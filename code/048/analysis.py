OLD=('ACTIVE_C0','ACTIVE_C1','NOVEL_C0','NOVEL_C1','SHAM_C0','SHAM_C1');NEW=('RADIUS_C0','RADIUS_C1');MODES=OLD+NEW;LAWS=('IID','RECUR');STARTS=('NAIVE','RESIDENT40')
RAW=('U0','U1','U','U40')+tuple('E'+str(i) for i in range(1,9))+('MLOSS',)
FREQ=('F0','F1','F','F40')+tuple('FE'+str(i) for i in range(1,9))+('D40',);MET=RAW+FREQ

PAIRS=tuple((a+'_C'+str(c),b+'_C'+str(c)) for a,b in (('ACTIVE','RADIUS'),('RADIUS','NOVEL'),('RADIUS','SHAM')) for c in (0,1))
CROSS=STATE_POL=('ACTIVE_C0-RADIUS_C0','ACTIVE_C1-RADIUS_C1')
def derive(v):
 for start in STARTS:
  for g in LAWS:
   for a,b in PAIRS:
    for m in MET:v[start+'|'+g+'|'+a+'-'+b+'|'+m]=v[start+'|'+g+'|'+a+'|'+m]-v[start+'|'+g+'|'+b+'|'+m]
  for p in CROSS:
   for m in MET:v[start+'|RECUR_MINUS_IID|'+p+'|'+m]=v[start+'|RECUR|'+p+'|'+m]-v[start+'|IID|'+p+'|'+m]
 for g in LAWS:
  for p in STATE_POL:
   for m in MET:v['RESIDENT40_MINUS_NAIVE|'+g+'|'+p+'|'+m]=v['RESIDENT40|'+g+'|'+p+'|'+m]-v['NAIVE|'+g+'|'+p+'|'+m]
 assert len(v)==1664

def structural(k):
 a,g,p,m=k.split('|')
 if a=='RESIDENT40_MINUS_NAIVE' or g=='RECUR_MINUS_IID':return m in ('U0','U1','F0','F1')
 if '-' not in p:return False
 return m in ('U0','F0') or 'NOVEL' not in p and m in ('U1','F1')
def direction(k,ci):
 if structural(k):return 'structural_zero','design-implied zero'
 s='positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved';a,g,p,m=k.split('|');unit='raw mismatch' if m=='MLOSS' else 'carrier frequency change' if m=='D40' else 'carrier frequency' if m in FREQ else 'raw accuracy'
 return s,unit+('; prepared-minus-naive total effect' if a=='RESIDENT40_MINUS_NAIVE' else '; recurrence-minus-IID difference' if g=='RECUR_MINUS_IID' else '; first minus second arm' if '-' in p else '; absolute')
