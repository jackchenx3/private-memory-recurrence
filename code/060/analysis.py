"""Fixed81-estimate noise-by-recurrence catalog; separate ancestry and true accuracy."""
from accepted_analysis055 import RAW,FREQ,MODES
CELLS=('EXACT_Q_ZERO','EXACT_Q_HALF','NOISY_Q_ZERO','NOISY_Q_HALF')
COEFS={'EXACT_Q_ZERO':(1,0,0,0),'EXACT_Q_HALF':(0,1,0,0),'NOISY_Q_ZERO':(0,0,1,0),'NOISY_Q_HALF':(0,0,0,1),'EXACT_Q_HALF_MINUS_ZERO':(-1,1,0,0),'NOISY_Q_HALF_MINUS_ZERO':(0,0,-1,1),'NOISY_MINUS_EXACT_AT_Q_ZERO':(-1,0,1,0),'NOISY_MINUS_EXACT_AT_Q_HALF':(0,-1,0,1),'NOISE_BY_RECURRENCE':(1,-1,-1,1)}
GROUPS=tuple(COEFS)
ENDPOINTS=tuple(s+'|D40' for s in ('SWITCH','STAY','EFFECT'))+tuple(s+'_POP|'+m for m in ('U','U40') for s in ('SWITCH','STAY','EFFECT'))
KEYS=tuple(g+'|'+m for g in GROUPS for m in ENDPOINTS)
PRIMARY='NOISE_BY_RECURRENCE|EFFECT|D40'
CONFIGS=('STAY','SWITCH0','SWITCH1')
DELTA=1/32

def series(rec,labels):return dict(accuracy=rec['true_accuracies'],founder={str(i):[sum(q[2]==fid for q in pop)/32. for pop in rec['populations']] for i,fid in enumerate(labels[:2])},expression=rec['frequencies'])
def base(paths,placement=None):
 assert set(paths)==set(CONFIGS);out={};ids=(0,1) if placement is None else (placement,)
 for m in ('D40','U','U40'):
  x=[];y=[]
  for i in ids:
   switch,stay=paths['SWITCH'+str(i)],paths['STAY']
   if m=='D40':
    assert switch['founder'][str(i)][0]==stay['founder'][str(i)][0]==1/32
    x.append(switch['founder'][str(i)][40]-1/32);y.append(stay['founder'][str(i)][40]-1/32)
   elif m=='U':x.append(sum(switch['accuracy'][1:])/40);y.append(sum(stay['accuracy'][1:])/40)
   else:x.append(switch['accuracy'][40]);y.append(stay['accuracy'][40])
  a,b=sum(x)/len(ids),sum(y)/len(ids);suffix='' if m=='D40' else '_POP'
  for s,v in (('SWITCH',a),('STAY',b),('EFFECT',a-b)):out[s+suffix+'|'+m]=v
 assert set(out)==set(ENDPOINTS);return out

def combine(cells):
 assert set(cells)==set(CELLS)
 return {g+'|'+m:sum(c[j]*cells[cell][m] for j,cell in enumerate(CELLS)) for g,c in COEFS.items() for m in ENDPOINTS}
def positive_scale(ci):
 lo,hi=ci;return 'above_plus_one_descendant' if lo>DELTA else 'below_plus_one_descendant' if hi<DELTA else 'overlaps_plus_one_descendant'
def decisions(ci):
 lo,hi=ci;assert lo<=hi
 return dict(direction='supports_negative' if hi<0 else 'contradicts_negative' if lo>0 else 'unresolved',minus_one_descendant='below' if hi<-DELTA else 'above' if lo>-DELTA else 'overlaps',plus_one_descendant='below' if hi<DELTA else 'above' if lo>DELTA else 'overlaps',resolution_fraction=DELTA,not_equivalence_test=True)
def quantile(xs,p):
 ys=sorted(xs);x=(len(ys)-1)*p;i=int(x);return ys[i]+(ys[min(i+1,len(ys)-1)]-ys[i])*(x-i)
def interval(xs,indices):
 assert len(xs)==24;ds=[sum(xs[i] for i in row)/24 for row in indices]
 return sum(xs)/24,[quantile(ds,.025),quantile(ds,.975)]
