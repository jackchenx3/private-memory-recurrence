"""Frozen 056 catalog: paired effects before 24-block resampling; no timepoint grid."""
from accepted_analysis055 import MODES,RAW,FREQ,CONFIGS
LAWS=('ZERO','HALF')
SERIES=tuple(bg+'_BG_'+s for bg in ('F','H') for s in ('SWITCH','STAY','EFFECT'))
ENDPOINTS=tuple(s+'|D40' for s in SERIES)+tuple(s+'_POP|'+m for s in SERIES for m in ('U','U40'))
CELLS=tuple('P_'+p+'_Q_'+q for p in LAWS for q in LAWS)
GROUPS=CELLS+tuple('Q_HALF_MINUS_ZERO_AT_P_'+p for p in LAWS)+tuple('P_HALF_MINUS_ZERO_AT_Q_'+q for q in LAWS)+('INTERACTION',)
PRIMARY='Q_HALF_MINUS_ZERO_AT_P_HALF|F_BG_EFFECT|D40'
STRUCTURAL_ZEROS=()  # No F0 or U0 endpoints are included; no algebraic zero in this catalog.
def base_estimands(rows):
 out={}
 for bg in ('F','H'):
  a,b,stay=rows[bg+'_SWITCH0'],rows[bg+'_SWITCH1'],rows[bg+'_STAY']
  for suffix,metrics in [('',('D40',)),('_POP',('U','U40'))]:
   for m in metrics:
    x=(a['founders']['p0'][m]+b['founders']['p1'][m])/2 if not suffix else (a['raw'][m]+b['raw'][m])/2
    y=(stay['founders']['p0'][m]+stay['founders']['p1'][m])/2 if not suffix else stay['raw'][m]
    for kind,value in [('SWITCH',x),('STAY',y),('EFFECT',x-y)]:out[bg+'_BG_'+kind+suffix+'|'+m]=value
 assert set(out)==set(ENDPOINTS)
 return out

def combine(cells):
 assert set(cells)==set(CELLS)
 out={g+'|'+k:v for g,row in cells.items() for k,v in row.items()}
 for p in LAWS:
  for k in ENDPOINTS:out['Q_HALF_MINUS_ZERO_AT_P_'+p+'|'+k]=cells['P_'+p+'_Q_HALF'][k]-cells['P_'+p+'_Q_ZERO'][k]
 for q in LAWS:
  for k in ENDPOINTS:out['P_HALF_MINUS_ZERO_AT_Q_'+q+'|'+k]=cells['P_HALF_Q_'+q][k]-cells['P_ZERO_Q_'+q][k]
 for k in ENDPOINTS:out['INTERACTION|'+k]=out['Q_HALF_MINUS_ZERO_AT_P_HALF|'+k]-out['Q_HALF_MINUS_ZERO_AT_P_ZERO|'+k]
 assert len(out)==162
 return out

def orientation(rows,i):
 out={};fid='p'+str(i)
 for bg in ('F','H'):
  a,b=rows[bg+'_SWITCH'+str(i)],rows[bg+'_STAY']
  for suffix,ms in [('',('D40',)),('_POP',('U','U40'))]:
   for m in ms:
    x,y=(a['founders'][fid][m],b['founders'][fid][m]) if not suffix else (a['raw'][m],b['raw'][m])
    for s,v in [('SWITCH',x),('STAY',y),('EFFECT',x-y)]:out[bg+'_BG_'+s+suffix+'|'+m]=v
 return out
