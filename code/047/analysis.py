MODES=('ACTIVE_C0','ACTIVE_C1','NOVEL_C0','NOVEL_C1','SHAM_C0','SHAM_C1');NEW=('NOVEL_C0','NOVEL_C1');OLD=('ACTIVE_C0','SHAM_C0','ACTIVE_C1','SHAM_C1');LAWS=('IID','RECUR')
RAW=('U0','U1','U','U40')+tuple('E'+str(i) for i in range(1,9))+('MLOSS',)
FREQ=('F0','F1','F','F40')+tuple('FE'+str(i) for i in range(1,9))+('D40',);MET=RAW+FREQ
PAIRS=(('ACTIVE_C0','NOVEL_C0'),('ACTIVE_C1','NOVEL_C1'),('ACTIVE_C0','SHAM_C0'),('ACTIVE_C1','SHAM_C1'),('NOVEL_C0','SHAM_C0'),('NOVEL_C1','SHAM_C1'),('NOVEL_C1','NOVEL_C0'));CROSS=('NOVEL_C0','NOVEL_C1','ACTIVE_C0-NOVEL_C0','ACTIVE_C1-NOVEL_C1');OLD_ACCESS=('ACTIVE_C0-SHAM_C0','ACTIVE_C1-SHAM_C1')
STARTS=('NAIVE','RESIDENT40');STATE_POL=('ACTIVE_C0','ACTIVE_C0-NOVEL_C0','ACTIVE_C0-SHAM_C0')
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
 assert len(v)==1716

def structural(k):
 a,g,p,m=k.split('|')
 if a=='RESIDENT40_MINUS_NAIVE':return m=='F0' or '-' in p and m=='U0' or p=='ACTIVE_C0-SHAM_C0' and m in ('U1','F1')
 assert a in STARTS
 if g=='RECUR_MINUS_IID':return m=='F0' or '-' in p and m=='U0'
 if '-' not in p:return False
 return m in ('U0','F0') or p in OLD_ACCESS and m in ('U1','F1')

def direction(k,ci):
 if structural(k):return 'structural_zero','design-implied zero'
 s='positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved';a,g,p,m=k.split('|');unit='raw mismatch' if m=='MLOSS' else 'carrier frequency change' if m=='D40' else 'carrier frequency' if m in FREQ else 'raw accuracy'
 return s,unit+('; prepared-minus-naive total effect' if a=='RESIDENT40_MINUS_NAIVE' else '; recurrence-minus-IID difference' if g=='RECUR_MINUS_IID' else '; first minus second arm' if '-' in p else '; absolute')
