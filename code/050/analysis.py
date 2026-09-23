MODES=('ACTIVE_C0','ACTIVE_C1','NOVEL_C0','NOVEL_C1','SHAM_C0','SHAM_C1');NEW=MODES;STARTS=('BEST32','RACE32');LAWS=('ZERO','HALF','FULL')
RAW=('U0','U1','U','U40')+tuple('E'+str(i) for i in range(1,9))+('MLOSS',)
FREQ=('F0','F1','F','F40')+tuple('FE'+str(i) for i in range(1,9))+('D40',);MET=RAW+FREQ

PAIRS=(('ACTIVE_C0','NOVEL_C0'),('ACTIVE_C1','NOVEL_C1'),('ACTIVE_C0','SHAM_C0'),('ACTIVE_C1','SHAM_C1'),('NOVEL_C0','SHAM_C0'),('NOVEL_C1','SHAM_C1'))
CROSS=('ACTIVE_C0-NOVEL_C0','ACTIVE_C1-NOVEL_C1','ACTIVE_C0-SHAM_C0','ACTIVE_C1-SHAM_C1')
LAW_PAIRS=(('HALF','ZERO'),('FULL','HALF'),('FULL','ZERO'))

def derive(v):
 for a in STARTS:
  for g in LAWS:
   for x,y in PAIRS:
    for m in MET:v[a+'|'+g+'|'+x+'-'+y+'|'+m]=v[a+'|'+g+'|'+x+'|'+m]-v[a+'|'+g+'|'+y+'|'+m]
  for g,h in LAW_PAIRS:
   for pol in CROSS:
    for m in MET:v[a+'|'+g+'_MINUS_'+h+'|'+pol+'|'+m]=v[a+'|'+g+'|'+pol+'|'+m]-v[a+'|'+h+'|'+pol+'|'+m]
 for g in LAWS:
  for pol in CROSS:
   for m in MET:v['RACE32_MINUS_BEST32|'+g+'|'+pol+'|'+m]=v['RACE32|'+g+'|'+pol+'|'+m]-v['BEST32|'+g+'|'+pol+'|'+m]
 assert len(v)==2808

def structural(k):
 a,g,p,m=k.split('|')
 if a=='RACE32_MINUS_BEST32':return m in ('U0','F0') or 'SHAM' in p and m in ('U1','F1')
 assert a in STARTS
 if '_MINUS_' in g:return m in ('U0','U1','F0','F1')
 if '-' not in p:return False
 return m in ('U0','F0') or p.startswith('ACTIVE') and 'SHAM' in p and m in ('U1','F1')

def direction(k,ci):
 if structural(k):return 'structural_zero','design-implied zero'
 s='positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved';a,g,p,m=k.split('|');unit='raw mismatch' if m=='MLOSS' else 'carrier frequency change' if m=='D40' else 'carrier frequency' if m in FREQ else 'raw accuracy'
 return s,unit+('; RACE32-minus-BEST32 total policy contrast' if a=='RACE32_MINUS_BEST32' else '; direct law difference' if '_MINUS_' in g else '; first minus second arm' if '-' in p else '; absolute')
