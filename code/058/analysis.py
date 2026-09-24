"""Prospectively fixed paired114-statistic catalog; no cross-objective utility grid."""
from accepted_analysis055 import MODES,RAW,FREQ,CONFIGS
OBJECTIVES=('HAM','TRAP4')
LAWS=('ZERO','HALF')
SERIES=tuple(bg+'_BG_'+s for bg in ('F','H') for s in ('SWITCH','STAY','EFFECT'))
ENDPOINTS=tuple(s+'|D40' for s in SERIES)+tuple(s+'_POP|'+m for s in SERIES for m in ('U','U40'))
CELLS=tuple(o+'|Q_'+q for o in OBJECTIVES for q in LAWS)
GROUPS=tuple(o+'|Q_'+q for o in OBJECTIVES for q in ('ZERO','HALF','HALF_MINUS_ZERO'))
CROSS='TRAP4_MINUS_HAM|Q_HALF_MINUS_ZERO'
KEYS=tuple(g+'|'+k for g in GROUPS for k in ENDPOINTS)+tuple(CROSS+'|'+s+'|D40' for s in SERIES)
PRIMARY='TRAP4|Q_HALF_MINUS_ZERO|F_BG_EFFECT|D40'
STRUCTURAL_ZEROS=()
DELTA=1/32
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
 for o in OBJECTIVES:
  for k in ENDPOINTS:out[o+'|Q_HALF_MINUS_ZERO|'+k]=cells[o+'|Q_HALF'][k]-cells[o+'|Q_ZERO'][k]
 for s in SERIES:
  k=s+'|D40';out[CROSS+'|'+k]=out['TRAP4|Q_HALF_MINUS_ZERO|'+k]-out['HAM|Q_HALF_MINUS_ZERO|'+k]
 assert set(out)==set(KEYS) and len(out)==114
 return out

def decisions(ci):
 lo,hi=ci;assert lo<=hi
 return dict(direction='supports_positive' if lo>0 else 'contradicts_positive' if hi<0 else 'unresolved',benchmark='supports_exceeding_one_expected_descendant' if lo>DELTA else 'does_not_support_at_least_one_expected_descendant' if hi<DELTA else 'unresolved',benchmark_fraction=DELTA)
def orientation(rows,i):
 out={};fid='p'+str(i)
 for bg in ('F','H'):
  a,b=rows[bg+'_SWITCH'+str(i)],rows[bg+'_STAY']
  for suffix,ms in [('',('D40',)),('_POP',('U','U40'))]:
   for m in ms:
    x,y=(a['founders'][fid][m],b['founders'][fid][m]) if not suffix else (a['raw'][m],b['raw'][m])
    for s,v in [('SWITCH',x),('STAY',y),('EFFECT',x-y)]:out[bg+'_BG_'+s+suffix+'|'+m]=v
 return out
