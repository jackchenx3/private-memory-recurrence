MODES=('ACTIVE_C0','ACTIVE_C1','NOVEL_C0','NOVEL_C1','SHAM_C0','SHAM_C1')
LAWS=('ZERO','HALF','FULL');COSTS=('C0',);CONFIGS=('LOW0','LOW1','HIGH0','HIGH1');NEW=CONFIGS
RAW=('U0','U1','U','U40')+tuple('E'+str(i) for i in range(1,9))+('MLOSS',)
FREQ=('F0','F1','F','F40')+tuple('FE'+str(i) for i in range(1,9))+('D40',)
FBASE=('LOW_H','LOW_F','HIGH_H','HIGH_F');FCON=('LOW_MINUS_HIGH_H',);RABS=('LOW_POP','HIGH_POP');RCON=('LOW_MINUS_HIGH_POP',);CROSS=('LOW_H','HIGH_F','LOW_MINUS_HIGH_H');LPAIRS=(('HALF','ZERO'),('FULL','HALF'),('FULL','ZERO'))
def paired(rows):
 out={}
 for prefix in ('LOW','HIGH'):
  a,b=rows[prefix+'0'],rows[prefix+'1']
  for r in ('H','F'):
   for m in FREQ:out[prefix+'_'+r+'|'+m]=(a['frequency'][r][m]+b['frequency'][r][m])/2
  for m in RAW:out[prefix+'_POP|'+m]=(a['raw'][m]+b['raw'][m])/2
 return out

def derive(v):
 for g in LAWS:
  pre=g+'|C0|'
  for m in FREQ:v[pre+'LOW_MINUS_HIGH_H|'+m]=v[pre+'LOW_H|'+m]-v[pre+'HIGH_H|'+m]
  for m in RAW:v[pre+'LOW_MINUS_HIGH_POP|'+m]=v[pre+'LOW_POP|'+m]-v[pre+'HIGH_POP|'+m]
 for g,h in LPAIRS:
  for s in CROSS:
   for m in FREQ:v[g+'_MINUS_'+h+'|C0|'+s+'|'+m]=v[g+'|C0|'+s+'|'+m]-v[h+'|C0|'+s+'|'+m]
 assert len(v)==429

def structural(k):
 g,c,s,m=k.split('|');return m in ('F0','F1') if '_MINUS_' in g else s=='LOW_MINUS_HIGH_POP' and m=='U0'
def direction(k,ci):return 'structural_zero' if structural(k) else 'positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved'

def orientation(rows,i):
 out={}
 for pre in ('LOW','HIGH'):
  q=rows[pre+str(i)]
  for r in ('H','F'):
   for m in FREQ:out[pre+'_'+r+'|'+m]=q['frequency'][r][m]
  for m in RAW:out[pre+'_POP|'+m]=q['raw'][m]
 for m in FREQ:out['LOW_MINUS_HIGH_H|'+m]=out['LOW_H|'+m]-out['HIGH_H|'+m]
 for m in RAW:out['LOW_MINUS_HIGH_POP|'+m]=out['LOW_POP|'+m]-out['HIGH_POP|'+m]
 return out
