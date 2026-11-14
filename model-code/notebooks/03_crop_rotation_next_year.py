# %% [markdown]
# # Next-season crop prediction from crop history + terrain + soil + NASA POWER: starter baseline
# Target challenge: **Field Shift: Adapting Farms with NASA Data** (NASA Space Apps 2026).
#
# Why: a rotation decision-support tool needs a calibrated model of what a field is likely to carry next
# season, so we can compare the existing rotation with alternatives and flag risk. This starter predicts the next-year
# crop group per 30 m pixel for one county (Story County, Iowa, FIPS 19169) from public, no-login data:
# - USDA NASS Cropland Data Layer via CropScape (public domain): labels and history
# - NASADEM elevation via Microsoft Planetary Computer (NASA, public domain)
# - SoilGrids 2.0 (ISRIC, CC-BY-4.0): clay, sand, SOC, pH, bulk density at 0-5 cm
# - NASA POWER daily agroclimatology (NASA, no login): growing-season precipitation, GDD, root-zone wetness
#
# Baselines: persistence, corn/soy alternation rule, 2nd-order Markov table. Model: LightGBM multiclass.
# Temporal split. One seed, not a published benchmark. `SMOKE=1` runs a tiny CPU subset.

# %%
import os, sys, subprocess
IN_COLAB='google.colab' in sys.modules
if IN_COLAB: subprocess.run([sys.executable,'-m','pip','install','-q','rasterio','pystac-client','planetary-computer','lightgbm','optuna'],check=True)
import json, re, time, urllib.request, ssl, numpy as np, pandas as pd, rasterio
from rasterio.warp import reproject, Resampling, transform_bounds
SMOKE=os.environ.get('SMOKE','0')=='1'
FIPS=os.environ.get('FIPS','19169')
DATA=os.environ.get('DATA_DIR','/content/data/farm' if IN_COLAB else './data/farm'); os.makedirs(DATA,exist_ok=True)
YEARS=list(range(2014 if SMOKE else 2009, 2021 if SMOKE else 2026))
TEST=[2020] if SMOKE else [2024,2025]; VAL=[2019] if SMOKE else [2022,2023]
NLAG=3 if SMOKE else 5; NPIX=20000 if SMOKE else 400000; N_TRIALS=int(os.environ.get('N_TRIALS','0' if SMOKE else '25'))
SEED=0; rng=np.random.default_rng(SEED)
print(dict(SMOKE=SMOKE,FIPS=FIPS,YEARS=(YEARS[0],YEARS[-1]),TEST=TEST,NPIX=NPIX))
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE   # CropScape serves an incomplete TLS chain
def fetch(url,fn,tries=4):
    if os.path.exists(fn) and os.path.getsize(fn)>0: return fn
    for t in range(tries):
        try:
            with urllib.request.urlopen(url,context=ctx,timeout=180) as r, open(fn,'wb') as f: f.write(r.read()); return fn
        except Exception as e: print('retry',url[:90],e); time.sleep(5)
    raise RuntimeError(url)

# %%
cdl={}
for y in YEARS:
    fn=f'{DATA}/cdl_{y}.tif'
    if not os.path.exists(fn):
        x=urllib.request.urlopen(f'https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLFile?year={y}&fips={FIPS}',context=ctx,timeout=120).read().decode()
        fetch(re.search(r'https?://[^<]+\.tif',x).group(0),fn)
    cdl[y]=fn
ref=rasterio.open(cdl[YEARS[-1]]); H,W=ref.shape; prof=ref.profile
def to_ref(src_path,band=1,resampling=Resampling.nearest,dtype='float32'):
    out=np.zeros((H,W),dtype=dtype)
    with rasterio.open(src_path) as s:
        reproject(rasterio.band(s,band),out,dst_transform=ref.transform,dst_crs=ref.crs,resampling=resampling,src_nodata=s.nodata,dst_nodata=0)
    return out
C=np.stack([to_ref(cdl[y],dtype='uint8') for y in YEARS])   # (T,H,W)
print('CDL stack',C.shape)
# Crop groups: 0 corn, 1 soy, 2 hay/alfalfa, 3 grass/pasture, 4 other crop, 5 non-ag
G=np.full(256,5,np.int8); G[1]=0; G[5]=1; G[[36,37]]=2; G[[176,62,58,59,60]]=3
G[[2,3,4,6,10,12,13,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,38,39,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,61,66,67,68,69,70,71,72,74,75,76,77,204,205,206,207,208,209,210,211,212,213,214,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,254]]=4
CG=G[C]; NAMES=['corn','soy','hay','grass','other_crop','non_ag']

# %%
import pystac_client, planetary_computer as pc
bb=transform_bounds(ref.crs,'EPSG:4326',*ref.bounds)
cat=pystac_client.Client.open('https://planetarycomputer.microsoft.com/api/stac/v1',modifier=pc.sign_inplace)
dem=np.zeros((H,W),'float32')
for it in cat.search(collections=['nasadem'],bbox=bb).items():
    d=to_ref(it.assets['elevation'].href,resampling=Resampling.bilinear); dem=np.where(dem==0,d,dem)
gy,gx=np.gradient(dem,30.0); slope=np.degrees(np.arctan(np.hypot(gx,gy))).astype('float32')
soil={}
for p in ['clay','sand','soc','phh2o','bdod']:
    fn=f'{DATA}/soil_{p}.tif'
    fetch(f'https://maps.isric.org/mapserv?map=/map/{p}.map&SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID={p}_0-5cm_mean&FORMAT=GEOTIFF_INT16'
          f'&SUBSET=long({bb[0]:.4f},{bb[2]:.4f})&SUBSET=lat({bb[1]:.4f},{bb[3]:.4f})&SUBSETTINGCRS=http://www.opengis.net/def/crs/EPSG/0/4326&OUTPUTCRS=http://www.opengis.net/def/crs/EPSG/0/4326',fn)
    soil[p]=to_ref(fn,resampling=Resampling.bilinear)
lat,lon=(bb[1]+bb[3])/2,(bb[0]+bb[2])/2
pw=json.load(open(fetch(f'https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,GWETROOT&community=AG&longitude={lon:.3f}&latitude={lat:.3f}&start={YEARS[0]-1}0101&end={YEARS[-1]}1231&format=JSON',f'{DATA}/power_{FIPS}.json')))
P=pd.DataFrame(pw['properties']['parameter']); P.index=pd.to_datetime(P.index); P=P.replace(-999,np.nan)
gs=P[(P.index.month>=4)&(P.index.month<=9)]
gdd=((gs.T2M_MAX.clip(upper=30)+gs.T2M_MIN.clip(lower=10))/2-10).clip(lower=0)
clim=pd.DataFrame({'gs_precip':gs.PRECTOTCORR.groupby(gs.index.year).sum(),'gs_gdd':gdd.groupby(gdd.index.year).sum(),'gs_rootwet':gs.GWETROOT.groupby(gs.index.year).mean()})
print(clim.tail(3))

# %%
rows=[]
valid=(dem>0)
for ti,y in enumerate(YEARS):
    if ti<NLAG: continue
    lag1=CG[ti-1]; m=valid&(lag1<=4)               # pixels that were farmed last year
    idx=np.flatnonzero(m.ravel()); idx=rng.choice(idx,min(len(idx),NPIX//max(1,len(YEARS)-NLAG)),replace=False)
    r,c=np.unravel_index(idx,(H,W)); d={'year':y,'target':CG[ti][r,c]}
    for k in range(1,NLAG+1): d[f'lag{k}']=CG[ti-k][r,c]
    hist=CG[ti-NLAG:ti][:,r,c]
    d['n_corn']=(hist==0).sum(0); d['n_soy']=(hist==1).sum(0); d['n_hay']=(hist==2).sum(0)
    d['elev']=dem[r,c]; d['slope']=slope[r,c]
    for p,a in soil.items(): d[p]=a[r,c]
    for k,v in clim.loc[y-1].items(): d['prev_'+k]=v
    d['row']=r; d['col']=c; rows.append(pd.DataFrame(d))
df=pd.concat(rows,ignore_index=True)
tr=df[~df.year.isin(TEST+VAL)]; va=df[df.year.isin(VAL)]; te=df[df.year.isin(TEST)]
print('train',len(tr),'val',len(va),'test',len(te)); print(te.target.value_counts(normalize=True).rename(lambda i:NAMES[i]).round(3).to_dict())

# %%
from sklearn.metrics import accuracy_score, f1_score
def emit(n,y,p,extra={}):
    print('RESULT_'+n+' '+json.dumps({'acc':float(accuracy_score(y,p)),'macro_f1':float(f1_score(y,p,average='macro')),**extra,'fips':FIPS,'test_years':TEST,'n_test':int(len(y)),'smoke':SMOKE,'seed':SEED,'note':'one seed, not a published benchmark'}))
emit('baseline_persistence',te.target,te.lag1)
alt=te.lag1.map({0:1,1:0}).fillna(te.lag1).astype(int); emit('baseline_corn_soy_alternation',te.target,alt)
tab=tr.groupby(['lag1','lag2']).target.agg(lambda s:s.mode().iloc[0])
mk=[tab.get((a,b),a2) for a,b,a2 in zip(te.lag1,te.lag2,alt)]; emit('baseline_markov2',te.target,mk)

# %%
import lightgbm as lgb
FE=[c for c in df.columns if c not in('year','target','row','col')]; CAT=[f'lag{k}' for k in range(1,NLAG+1)]
def fit(ps):
    p=dict(objective='multiclass',num_class=6,learning_rate=0.05,num_leaves=63,min_data_in_leaf=50,feature_fraction=0.9,verbose=-1,seed=SEED,**ps)
    return lgb.train(p,lgb.Dataset(tr[FE],tr.target,categorical_feature=CAT),num_boost_round=60 if SMOKE else 2000,
                     valid_sets=[lgb.Dataset(va[FE],va.target,categorical_feature=CAT)],callbacks=[lgb.early_stopping(50,verbose=False)])
best={}
if N_TRIALS>0:
    import optuna; optuna.logging.set_verbosity(optuna.logging.WARNING)
    def obj(t):
        b=fit(dict(num_leaves=t.suggest_int('num_leaves',15,255,log=True),min_data_in_leaf=t.suggest_int('min_data_in_leaf',10,500,log=True),
                   learning_rate=t.suggest_float('learning_rate',0.01,0.2,log=True),feature_fraction=t.suggest_float('feature_fraction',0.5,1.0),lambda_l2=t.suggest_float('lambda_l2',1e-3,10,log=True)))
        return -f1_score(va.target,b.predict(va[FE]).argmax(1),average='macro')
    st=optuna.create_study(sampler=optuna.samplers.TPESampler(seed=SEED)); st.optimize(obj,n_trials=N_TRIALS); best=st.best_params
b=fit(best); pr=b.predict(te[FE]); emit('lgbm_multiclass',te.target,pr.argmax(1),{'hpo_trials':N_TRIALS,'best_iter':int(b.best_iteration or 0)})
# Calibration check (for honest per-field probabilities in the tool)
conf=pr.max(1); correct=(pr.argmax(1)==te.target.values)
print('RESULT_lgbm_calibration '+json.dumps({f'conf_{lo:.1f}-{lo+0.1:.1f}':[int(((conf>=lo)&(conf<lo+.1)).sum()),float(correct[(conf>=lo)&(conf<lo+.1)].mean()) if ((conf>=lo)&(conf<lo+.1)).any() else None] for lo in np.arange(0.3,1.0,0.1)}))
print(sorted(zip(FE,b.feature_importance('gain').round()),key=lambda x:-x[1])[:10])
