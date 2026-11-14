# %% [markdown]
# # MODIS to VIIRS active-fire harmonization: starter baseline
# Target challenge: **Harmonization of MODIS and VIIRS Hot Spots** (NASA Space Apps 2026).
#
# What it does: downloads public FIRMS country archives (no key, no login), grids hotspots to cell x month,
# learns a MODIS to VIIRS-equivalent count mapping on the 2012+ overlap, and tests on held-out recent years.
# This lets us back-cast a VIIRS-consistent calendar to 2000-2011.
#
# Baselines: (1) one global VIIRS/MODIS ratio, (2) per-calendar-month ratio. Model: LightGBM (Poisson).
# Results are one seed, not a published benchmark. Set `SMOKE=1` for a tiny CPU run.
# Data: NASA FIRMS (LANCE/MODAPS) https://firms.modaps.eosdis.nasa.gov/ . NASA data, no restriction on use; cite FIRMS.

# %%
import os, sys, subprocess
IN_COLAB = 'google.colab' in sys.modules
if IN_COLAB:
    subprocess.run([sys.executable,'-m','pip','install','-q','lightgbm','optuna','pyarrow'],check=True)
import json, time, urllib.request, numpy as np, pandas as pd
SMOKE = os.environ.get('SMOKE','0')=='1'
COUNTRY = os.environ.get('COUNTRY','Canada')       # FIRMS country file name, e.g. Canada, Argentina, Brazil, Australia
YEARS_MODIS = list(range(2012 if SMOKE else 2000, 2016 if SMOKE else 2026))
YEARS_VIIRS = list(range(2012, 2016 if SMOKE else 2026))
CELL = 0.25                                       # grid cell in degrees
TEST_YEARS = [2015] if SMOKE else [2022,2023,2024,2025]
N_TRIALS = int(os.environ.get('N_TRIALS', '0' if SMOKE else '30'))
DATA = os.environ.get('DATA_DIR','/content/data/firms' if IN_COLAB else './data/firms'); os.makedirs(DATA,exist_ok=True)
SEED=0; np.random.seed(SEED)
print(dict(SMOKE=SMOKE,COUNTRY=COUNTRY,TEST_YEARS=TEST_YEARS,N_TRIALS=N_TRIALS))

# %%
def fetch(sensor, year):
    fn=f"{DATA}/{sensor}_{year}_{COUNTRY}.csv"
    if not os.path.exists(fn):
        u=f"https://firms.modaps.eosdis.nasa.gov/data/country/{sensor}/{year}/{sensor}_{year}_{COUNTRY}.csv"
        for t in range(4):
            try: urllib.request.urlretrieve(u,fn); break
            except Exception as e: print('retry',u,e); time.sleep(5)
    return fn
usecols_m=['latitude','longitude','brightness','acq_date','satellite','confidence','frp','daynight','type']
usecols_v=['latitude','longitude','bright_ti4','acq_date','confidence','frp','daynight','type']
M=pd.concat([pd.read_csv(fetch('modis',y),usecols=usecols_m) for y in YEARS_MODIS])
V=pd.concat([pd.read_csv(fetch('viirs-snpp',y),usecols=usecols_v) for y in YEARS_VIIRS])
if SMOKE:
    M=M.sample(min(len(M),60000),random_state=SEED); V=V.sample(min(len(V),200000),random_state=SEED)
# Keep vegetation fires only (type 0 = presumed vegetation fire); drop low-confidence
M=M[(M.type==0)&(M.confidence>=30)]; V=V[(V.type==0)&(V.confidence!='l')]
print('MODIS',len(M),'VIIRS',len(V))

# %%
def grid(df, prefix, extra):
    d=df.copy(); d['t']=pd.to_datetime(d.acq_date).dt.to_period('M')
    d['gy']=np.floor(d.latitude/CELL).astype(int); d['gx']=np.floor(d.longitude/CELL).astype(int)
    d['night']=(d.daynight=='N').astype(int)
    agg=dict(n=('frp','size'),frp_sum=('frp','sum'),frp_med=('frp','median'),night_frac=('night','mean'),**extra)
    g=d.groupby(['gy','gx','t']).agg(**agg).reset_index()
    return g.rename(columns={c:f'{prefix}_{c}' for c in g.columns if c not in('gy','gx','t')})
M['aqua']=(M.satellite=='A').astype(int)
gm=grid(M,'m',dict(bright=('brightness','mean'),aqua_frac=('aqua','mean')))
gv=grid(V,'v',dict(bright=('bright_ti4','mean')))
df=gm.merge(gv[['gy','gx','t','v_n']],on=['gy','gx','t'],how='outer')
df=df[df.t.dt.year>=2012].fillna({c:0 for c in df.columns if c.startswith(('m_','v_'))})
df['year']=df.t.dt.year; df['month']=df.t.dt.month
df['lat']=(df.gy+0.5)*CELL; df['lon']=(df.gx+0.5)*CELL
df['msin']=np.sin(2*np.pi*df.month/12); df['mcos']=np.cos(2*np.pi*df.month/12)
train=df[~df.year.isin(TEST_YEARS)].copy(); test=df[df.year.isin(TEST_YEARS)].copy()
# Cell-level history features computed on TRAIN only (no leakage)
h=train.groupby(['gy','gx']).agg(cell_m=('m_n','sum'),cell_v=('v_n','sum'),cell_months=('m_n','size')).reset_index()
h['cell_ratio']=(h.cell_v+1)/(h.cell_m+1)
train=train.merge(h,on=['gy','gx'],how='left'); test=test.merge(h,on=['gy','gx'],how='left').fillna({'cell_m':0,'cell_v':0,'cell_months':0,'cell_ratio':np.nan})
print('cell-months train',len(train),'test',len(test))

# %%
from scipy.stats import spearmanr
def metrics(y,p):
    y=np.asarray(y,float); p=np.clip(np.asarray(p,float),0,None)
    return dict(rmse_log1p=float(np.sqrt(np.mean((np.log1p(y)-np.log1p(p))**2))), mae=float(np.mean(np.abs(y-p))),
                spearman=float(spearmanr(y,p).correlation), total_bias_pct=float(100*(p.sum()-y.sum())/max(y.sum(),1)))
def emit(name, d):
    print('RESULT_'+name+' '+json.dumps({**d,'country':COUNTRY,'test_years':TEST_YEARS,'smoke':SMOKE,'seed':SEED,'note':'one seed, not a published benchmark'}))
r_global=train.v_n.sum()/max(train.m_n.sum(),1)
base1=test.m_n*r_global
mr=train.groupby('month').apply(lambda g:g.v_n.sum()/max(g.m_n.sum(),1)); base2=test.m_n*test.month.map(mr).fillna(r_global)
m_b1=metrics(test.v_n,base1); m_b2=metrics(test.v_n,base2)
emit('baseline_global_ratio',{**m_b1,'ratio':float(r_global)}); emit('baseline_month_ratio',m_b2)

# %%
import lightgbm as lgb
FEATS=['m_n','m_frp_sum','m_frp_med','m_night_frac','m_bright','m_aqua_frac','lat','lon','msin','mcos','month','cell_m','cell_v','cell_months','cell_ratio']
# validation = last train year, for early stopping and HPO
vy=train.year.max(); tr=train[train.year<vy]; va=train[train.year==vy]
def fit(params, Xtr, ytr, Xva, yva, rounds=2000):
    p=dict(objective='poisson',learning_rate=0.05,num_leaves=31,min_data_in_leaf=20,feature_fraction=0.9,bagging_fraction=0.9,bagging_freq=1,verbose=-1,seed=SEED,**params)
    return lgb.train(p,lgb.Dataset(Xtr,ytr),num_boost_round=50 if SMOKE else rounds,valid_sets=[lgb.Dataset(Xva,yva)],callbacks=[lgb.early_stopping(50,verbose=False)])
best_params={}
if N_TRIALS>0:
    import optuna; optuna.logging.set_verbosity(optuna.logging.WARNING)
    def obj(trial):
        ps=dict(num_leaves=trial.suggest_int('num_leaves',8,128,log=True),min_data_in_leaf=trial.suggest_int('min_data_in_leaf',5,200,log=True),
                learning_rate=trial.suggest_float('learning_rate',0.01,0.2,log=True),feature_fraction=trial.suggest_float('feature_fraction',0.5,1.0),
                lambda_l2=trial.suggest_float('lambda_l2',1e-3,10,log=True))
        b=fit(ps,tr[FEATS],tr.v_n,va[FEATS],va.v_n); return metrics(va.v_n,b.predict(va[FEATS]))['rmse_log1p']
    st=optuna.create_study(direction='minimize',sampler=optuna.samplers.TPESampler(seed=SEED)); st.optimize(obj,n_trials=N_TRIALS)
    best_params=st.best_params; print('best',best_params)
bst=fit(best_params,tr[FEATS],tr.v_n,va[FEATS],va.v_n)
pred=bst.predict(test[FEATS]); m_gbm=metrics(test.v_n,pred)
emit('lgbm_poisson',{**m_gbm,'hpo_trials':N_TRIALS,'best_iter':int(bst.best_iteration or 0),
     'delta_rmse_log1p_vs_month_ratio':m_gbm['rmse_log1p']-m_b2['rmse_log1p']})
imp=sorted(zip(FEATS,bst.feature_importance('gain')),key=lambda x:-x[1])[:8]; print('top features',imp)

# %% [markdown]
# ## Burning-activity calendar (harmonized)
# Back-cast VIIRS-equivalent monthly counts for 2000-2011 from MODIS with the fitted model, splice with observed VIIRS 2012+.

# %%
allm=gm.copy(); allm['year']=allm.t.dt.year; allm['month']=allm.t.dt.month
allm['lat']=(allm.gy+0.5)*CELL; allm['lon']=(allm.gx+0.5)*CELL; allm['msin']=np.sin(2*np.pi*allm.month/12); allm['mcos']=np.cos(2*np.pi*allm.month/12)
allm=allm.merge(h,on=['gy','gx'],how='left').fillna({'cell_m':0,'cell_v':0,'cell_months':0})
allm['v_equiv']=bst.predict(allm[FEATS])
pre=allm[allm.year<2012].groupby(['year','month']).v_equiv.sum()
post=gv.assign(year=gv.t.dt.year,month=gv.t.dt.month).groupby(['year','month']).v_n.sum()
cal=pd.concat([pre,post]).unstack('month').fillna(0).round(0)
print(cal.tail(8))
os.makedirs('outputs',exist_ok=True); cal.to_csv(f'outputs/harmonized_calendar_{COUNTRY}.csv')
emit('calendar_written',{'rows':int(cal.shape[0]),'path':f'outputs/harmonized_calendar_{COUNTRY}.csv'})
