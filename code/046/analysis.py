MODES=('ACTIVE_C0','ACTIVE_C1','NOVEL_C0','NOVEL_C1','SHAM_C0','SHAM_C1');NEW=('NOVEL_C0','NOVEL_C1');OLD=('ACTIVE_C0','SHAM_C0','ACTIVE_C1','SHAM_C1');LAWS=('IID','RECUR')
RAW=('U0','U1','U','U40')+tuple('E'+str(i) for i in range(1,9))+('MLOSS',)
FREQ=('F0','F1','F','F40')+tuple('FE'+str(i) for i in range(1,9))+('D40',);MET=RAW+FREQ
PAIRS=(('ACTIVE_C0','NOVEL_C0'),('ACTIVE_C1','NOVEL_C1'),('ACTIVE_C0','SHAM_C0'),('ACTIVE_C1','SHAM_C1'),('NOVEL_C0','SHAM_C0'),('NOVEL_C1','SHAM_C1'),('NOVEL_C1','NOVEL_C0'));CROSS=('NOVEL_C0','NOVEL_C1','ACTIVE_C0-NOVEL_C0','ACTIVE_C1-NOVEL_C1');OLD_ACCESS=('ACTIVE_C0-SHAM_C0','ACTIVE_C1-SHAM_C1')
def derive(v):
 for g in LAWS:
  for a,b in PAIRS:
   for m in MET:v['RARE|'+g+'|'+a+'-'+b+'|'+m]=v['RARE|'+g+'|'+a+'|'+m]-v['RARE|'+g+'|'+b+'|'+m]
 for p in CROSS:
  for m in MET:v['RARE|RECUR_MINUS_IID|'+p+'|'+m]=v['RARE|RECUR|'+p+'|'+m]-v['RARE|IID|'+p+'|'+m]
 assert len(v)==780

def structural(k):
 a,g,p,m=k.split('|');assert a=='RARE'
 if g=='RECUR_MINUS_IID':return m in ('U0','U1','F0','F1')
 if '-' not in p:return False
 return m in ('U0','F0') or p in OLD_ACCESS and m in ('U1','F1')

def direction(k,ci):
 if structural(k):return 'structural_zero','design-implied zero'
 s='positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved';a,g,p,m=k.split('|');unit='raw mismatch' if m=='MLOSS' else 'carrier frequency change' if m=='D40' else 'carrier frequency' if m in FREQ else 'raw accuracy'
 return s,unit+('; recurrence-minus-IID difference' if g=='RECUR_MINUS_IID' else '; first minus second arm' if '-' in p else '; absolute')
