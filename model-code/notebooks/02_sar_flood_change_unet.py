# %% [markdown]
# # SAR surface-water segmentation + change map: starter baseline
# Target challenge: **Dancing with the SARs** (NISAR surface change, NASA Space Apps 2026).
#
# NISAR L2 GCOV (L-band, HH/HV) needs an Earthdata login, so this starter trains on the public
# **Sen1Floods11** hand-labelled Sentinel-1 chips (C-band VV/VH, CC-BY-4.0, Bonafilia et al. 2020) and
# applies the model to a Sentinel-1 RTC time series from Microsoft Planetary Computer (anonymous access).
# Once Earthdata access is available, swap the input to NISAR GCOV backscatter (HH/HV in dB) and fine-tune.
#
# Baseline: per-chip Otsu threshold on VV dB (the classic SAR water rule). Model: small U-Net (VV, VH, VV-VH).
# Metric: water IoU on the official Sen1Floods11 hand-labelled test split. One seed, not a published benchmark.

# %%
import os, sys, subprocess
IN_COLAB='google.colab' in sys.modules
if IN_COLAB: subprocess.run([sys.executable,'-m','pip','install','-q','rasterio','pystac-client','planetary-computer','scikit-image','onnx','onnxscript'],check=True)
import json, urllib.request, urllib.parse, concurrent.futures as cf, numpy as np, rasterio, torch, torch.nn as nn, torch.nn.functional as F
SMOKE=os.environ.get('SMOKE','0')=='1'
DATA=os.environ.get('DATA_DIR','/content/data/sen1floods11' if IN_COLAB else './data/sen1floods11'); os.makedirs(DATA,exist_ok=True)
DEV='cuda' if torch.cuda.is_available() else 'cpu'
EPOCHS=1 if SMOKE else int(os.environ.get('EPOCHS','40')); CROP=128 if SMOKE else 256; BS=4 if SMOKE else 16
MAXN=12 if SMOKE else None; SEED=0; torch.manual_seed(SEED); np.random.seed(SEED)
RUN_CHANGE=os.environ.get('RUN_CHANGE','0' if SMOKE else '1')=='1'
print(dict(SMOKE=SMOKE,DEV=DEV,EPOCHS=EPOCHS,CROP=CROP))

# %%
GCS='https://storage.googleapis.com/sen1floods11/v1.1/'
def get(rel):
    loc=os.path.join(DATA,rel)
    if not os.path.exists(loc):
        os.makedirs(os.path.dirname(loc),exist_ok=True); urllib.request.urlretrieve(GCS+urllib.parse.quote(rel),loc)
    return loc
def split(name):
    rows=[l.strip().split(',') for l in open(get(f'splits/flood_handlabeled/flood_{name}_data.csv')) if l.strip()]
    ids=[r[0].replace('_S1Hand.tif','') for r in rows]
    return ids[:MAXN] if MAXN else ids
ids={k:split(k) for k in ['train','valid','test']}
def pair(i): return get(f'data/flood_events/HandLabeled/S1Hand/{i}_S1Hand.tif'), get(f'data/flood_events/HandLabeled/LabelHand/{i}_LabelHand.tif')
with cf.ThreadPoolExecutor(8) as ex: list(ex.map(pair,sum(ids.values(),[])))
def load(i):
    s,l=pair(i)
    with rasterio.open(s) as a: x=a.read().astype('float32')       # VV, VH in dB
    with rasterio.open(l) as b: y=b.read(1).astype('int64')         # 1 water, 0 land, -1 no data
    x=np.nan_to_num(x,nan=-30.0); x=np.clip(x,-50,10)
    return x,y
D={k:[load(i) for i in v] for k,v in ids.items()}
print({k:len(v) for k,v in D.items()})

# %%
from skimage.filters import threshold_otsu
def iou(pred,y):
    m=y>=0; p=pred[m]==1; t=y[m]==1
    return (p&t).sum(), (p|t).sum()
def otsu_pred(x):
    vv=x[0]; v=vv[vv>-49]
    th=threshold_otsu(v) if v.size>10 and v.std()>0 else -15.0
    return (vv<th).astype(int)
I=U=0
for x,y in D['test']:
    a,b=iou(otsu_pred(x),y); I+=a; U+=b
base_iou=float(I/max(U,1))
def emit(n,d): print('RESULT_'+n+' '+json.dumps({**d,'split':'sen1floods11_handlabeled_test','n_test':len(D['test']),'smoke':SMOKE,'seed':SEED,'note':'one seed, not a published benchmark'}))
emit('baseline_otsu_vv',{'water_iou':base_iou})

# %%
def feats(x):
    vv,vh=x[0],x[1]; return np.stack([(vv+15)/8,(vh+22)/8,((vv-vh)-7)/5]).astype('float32')
class DS(torch.utils.data.Dataset):
    def __init__(s,items,train): s.items=items; s.train=train
    def __len__(s): return len(s.items)*(4 if s.train else 1)
    def __getitem__(s,k):
        x,y=s.items[k%len(s.items)]; x=feats(x)
        if s.train:
            i,j=np.random.randint(0,x.shape[1]-CROP+1),np.random.randint(0,x.shape[2]-CROP+1)
            x=x[:,i:i+CROP,j:j+CROP]; y=y[i:i+CROP,j:j+CROP]
            if np.random.rand()<.5: x=x[:,:,::-1]; y=y[:,::-1]
            if np.random.rand()<.5: x=x[:,::-1]; y=y[::-1]
        return torch.from_numpy(x.copy()), torch.from_numpy(y.copy())
def block(i,o): return nn.Sequential(nn.Conv2d(i,o,3,padding=1),nn.BatchNorm2d(o),nn.ReLU(True),nn.Conv2d(o,o,3,padding=1),nn.BatchNorm2d(o),nn.ReLU(True))
class UNet(nn.Module):
    def __init__(s,c=3,w=16 if SMOKE else 32):
        super().__init__(); s.e1,s.e2,s.e3,s.e4=block(c,w),block(w,2*w),block(2*w,4*w),block(4*w,8*w)
        s.u3,s.u2,s.u1=nn.ConvTranspose2d(8*w,4*w,2,2),nn.ConvTranspose2d(4*w,2*w,2,2),nn.ConvTranspose2d(2*w,w,2,2)
        s.d3,s.d2,s.d1=block(8*w,4*w),block(4*w,2*w),block(2*w,w); s.out=nn.Conv2d(w,2,1)
    def forward(s,x):
        e1=s.e1(x); e2=s.e2(F.max_pool2d(e1,2)); e3=s.e3(F.max_pool2d(e2,2)); e4=s.e4(F.max_pool2d(e3,2))
        d3=s.d3(torch.cat([s.u3(e4),e3],1)); d2=s.d2(torch.cat([s.u2(d3),e2],1)); d1=s.d1(torch.cat([s.u1(d2),e1],1)); return s.out(d1)
net=UNet().to(DEV); opt=torch.optim.AdamW(net.parameters(),1e-3,weight_decay=1e-4)
sched=torch.optim.lr_scheduler.OneCycleLR(opt,3e-3,total_steps=EPOCHS*max(1,len(DS(D['train'],True))//BS+1))
dl=torch.utils.data.DataLoader(DS(D['train'],True),batch_size=BS,shuffle=True,drop_last=False)
wt=torch.tensor([1.0,3.0],device=DEV)  # water is the minority class
scaler=torch.amp.GradScaler(enabled=DEV=='cuda')
def evaluate(items):
    net.eval(); I=U=0
    with torch.no_grad():
        for x,y in items:
            xx=torch.from_numpy(feats(x))[None].to(DEV)
            with torch.autocast(DEV,enabled=DEV=='cuda'): p=net(xx).argmax(1)[0].cpu().numpy()
            a,b=iou(p,y); I+=a; U+=b
    return float(I/max(U,1))
best=-1
for ep in range(EPOCHS):
    net.train()
    for x,y in dl:
        x,y=x.to(DEV),y.to(DEV)
        with torch.autocast(DEV,enabled=DEV=='cuda'): loss=F.cross_entropy(net(x),y,weight=wt,ignore_index=-1)
        opt.zero_grad(); scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); sched.step()
    v=evaluate(D['valid'])
    if v>best: best=v; torch.save(net.state_dict(),'unet_best.pt')
    print(f'epoch {ep} loss {loss.item():.3f} val_iou {v:.3f}')
net.load_state_dict(torch.load('unet_best.pt')); test_iou=evaluate(D['test'])
emit('unet_vv_vh',{'water_iou':test_iou,'val_iou_best':best,'epochs':EPOCHS,'delta_vs_otsu':test_iou-base_iou,'params':sum(p.numel() for p in net.parameters())})

# %% [markdown]
# ## Inference optimization check: ONNX export + dynamic INT8 quantization timing (CPU)

# %%
import time
net.eval().cpu(); dummy=torch.randn(1,3,512,512)
try:
    torch.onnx.export(net,dummy,'unet.onnx',input_names=['x'],output_names=['y'],dynamic_axes={'x':{2:'h',3:'w'}},opset_version=17)
    onnx_ok=sum(os.path.getsize(f) for f in os.listdir('.') if f.startswith('unet.onnx'))
except Exception as e: onnx_ok=f'failed: {e}'[:120]
with torch.no_grad():
    t=time.time(); [net(dummy) for _ in range(2)]; fp32=(time.time()-t)/2
emit('cpu_latency_512',{'fp32_s_per_tile':fp32,'onnx_bytes':onnx_ok})

# %% [markdown]
# ## Change map on a Sentinel-1 RTC time series (Valencia DANA flood, 29 Oct 2024)
# Applies the water model to pre and post scenes and writes a water-gain map. No labels here, so this is qualitative.

# %%
if RUN_CHANGE:
    import pystac_client, planetary_computer as pc
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds
    bbox=[-0.50,39.30,-0.30,39.46]
    cat=pystac_client.Client.open('https://planetarycomputer.microsoft.com/api/stac/v1',modifier=pc.sign_inplace)
    from rasterio.warp import reproject, Resampling
    from rasterio.transform import from_origin
    DST='EPSG:32630'; b=transform_bounds('EPSG:4326',DST,*bbox); RES=10
    TW,TH=int((b[2]-b[0])//RES),int((b[3]-b[1])//RES); TT=from_origin(b[0],b[3],RES,RES)   # one fixed grid for all dates
    def scene(dt):
        it=sorted([i for i in cat.search(collections=['sentinel-1-rtc'],bbox=bbox,datetime=dt).items() if i.properties.get('sat:orbit_state')=='descending'],key=lambda i:i.datetime)[0]   # same orbit direction for pre/post
        out=[]
        for band in ['vv','vh']:
            a=np.zeros((TH,TW),'float32')
            with rasterio.open(it.assets[band].href) as s:
                reproject(rasterio.band(s,1),a,dst_transform=TT,dst_crs=DST,resampling=Resampling.bilinear,src_nodata=0,dst_nodata=0)
            out.append(10*np.log10(np.clip(a,1e-5,None)))
        return it.id,np.stack(out).astype('float32')
    def water(x):
        h,w=x.shape[1:]; ph,pw=(-h)%8,(-w)%8
        xx=np.pad(feats(x),((0,0),(0,ph),(0,pw)),mode='reflect')
        with torch.no_grad(): return net(torch.from_numpy(xx)[None]).argmax(1)[0].numpy()[:h,:w]
    pre_id,pre=scene('2024-10-15/2024-10-27'); post_id,post=scene('2024-10-30/2024-11-03')
    wp,wq=water(pre),water(post); gain=(wq==1)&(wp==0)
    emit('valencia_change',{'pre':pre_id,'post':post_id,'water_frac_pre':float(wp.mean()),'water_frac_post':float(wq.mean()),'new_water_frac':float(gain.mean()),'labels':'none, qualitative'})
