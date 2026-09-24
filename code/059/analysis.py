"""Fixed36-estimate pulse catalog; founder IDs are independent of expressed policy."""
from accepted_analysis055 import RAW,FREQ,MODES
ENDPOINTS=('U1','U_LATE','U40','U_ALL','D1','D40')
ARMS=('STAY','PULSE','CONT')
CONFIGS=('STAY','PULSE0','PULSE1','CONT0','CONT1')
CONTRASTS={'PULSE_MINUS_STAY':('PULSE','STAY'),'CONT_MINUS_STAY':('CONT','STAY'),'PULSE_MINUS_CONT':('PULSE','CONT')}
GROUPS=ARMS+tuple(CONTRASTS)
KEYS=tuple(g+'|'+m for g in GROUPS for m in ENDPOINTS)
PRIMARY='PULSE_MINUS_STAY|U40'
DELTA=1/1024
STRUCTURAL_ZEROS=('PULSE_MINUS_CONT|U1','PULSE_MINUS_CONT|D1')

def lineage_series(rec,labels):return {str(i):[sum(q[2]==fid for q in pop)/32. for pop in rec['populations']] for i,fid in enumerate(labels[:2])}
def endpoints(accuracy,founder):
 assert len(accuracy)==len(founder)==41 and founder[0]==1/32
 return dict(U1=accuracy[1],U_LATE=sum(accuracy[2:])/39,U40=accuracy[40],U_ALL=sum(accuracy[1:])/40,D1=founder[1]-1/32,D40=founder[40]-1/32)
def summarize(paths):
 assert set(paths)==set(CONFIGS);base={}
 for arm in ARMS:
  pair=[endpoints(paths['STAY']['accuracy'],paths['STAY']['founder'][str(i)]) if arm=='STAY' else endpoints(paths[arm+str(i)]['accuracy'],paths[arm+str(i)]['founder'][str(i)]) for i in (0,1)]
  base[arm]={m:(pair[0][m]+pair[1][m])/2 for m in ENDPOINTS}
 out={g+'|'+m:v for g,row in base.items() for m,v in row.items()}
 for g,(a,b) in CONTRASTS.items():
  for m in ENDPOINTS:out[g+'|'+m]=base[a][m]-base[b][m]
 assert set(out)==set(KEYS) and all(out[k]==0 for k in STRUCTURAL_ZEROS)
 return out

def decisions(ci):
 lo,hi=ci;assert lo<=hi
 return dict(direction='supports_positive' if lo>0 else 'contradicts_positive' if hi<0 else 'unresolved',benchmark='above_one_matching_bit' if lo>DELTA else 'below_one_matching_bit' if hi<DELTA else 'overlaps_one_matching_bit',resolution_fraction=DELTA,resolution_percentage_points=100*DELTA)
def quantile(xs,p):
 ys=sorted(xs);x=(len(ys)-1)*p;i=int(x);return ys[i]+(ys[min(i+1,len(ys)-1)]-ys[i])*(x-i)
def interval(xs,indices):
 assert len(xs)==24
 bs=[sum(xs[i] for i in row)/24 for row in indices]
 return sum(xs)/24,[quantile(bs,.025),quantile(bs,.975)]
