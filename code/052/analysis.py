MODES=('ACTIVE_C0','ACTIVE_C1','NOVEL_C0','NOVEL_C1','SHAM_C0','SHAM_C1')
LAWS=('ZERO','HALF','FULL');COSTS=('C0','C1');CONFIGS=('MIX0','MIX1','H0','H1','F0','F1');NEW=CONFIGS
RAW=('U0','U1','U','U40')+tuple('E'+str(i) for i in range(1,9))+('MLOSS',)
FREQ=('F0','F1','F','F40')+tuple('FE'+str(i) for i in range(1,9))+('D40',)
FABS=('MIX_H','MIX_F','MIX_R','ISO_H','ISO_F');RABS=('MIX_POP','ISO_H_POP','ISO_F_POP')
FCON=('MIX_H_MINUS_F','ISO_H_MINUS_F','MIX_MINUS_ISO_H','MIX_MINUS_ISO_F','MIX_MINUS_ISO_RANK');RCON=('MIX_MINUS_ISO_H_POP','MIX_MINUS_ISO_F_POP','ISO_H_MINUS_F_POP');CROSS=('MIX_H_MINUS_F','ISO_H_MINUS_F','MIX_MINUS_ISO_RANK');LPAIRS=(('HALF','ZERO'),('FULL','HALF'),('FULL','ZERO'))

def paired(rows):
 out={}
 for series,configs,role in [('MIX_H',('MIX0','MIX1'),'H'),('MIX_F',('MIX0','MIX1'),'F'),('MIX_R',('MIX0','MIX1'),'R'),('ISO_H',('H0','H1'),'H'),('ISO_F',('F0','F1'),'F')]:
  for m in FREQ:out[series+'|'+m]=sum(rows[c]['frequency'][role][m] for c in configs)/2
 for series,configs in [('MIX_POP',('MIX0','MIX1')),('ISO_H_POP',('H0','H1')),('ISO_F_POP',('F0','F1'))]:
  for m in RAW:out[series+'|'+m]=sum(rows[c]['raw'][m] for c in configs)/2
 return out

def derive(v):
 for g in LAWS:
  for c in COSTS:
   pre=g+'|'+c+'|'
   for out,a,b,ms in [('MIX_H_MINUS_F','MIX_H','MIX_F',FREQ),('ISO_H_MINUS_F','ISO_H','ISO_F',FREQ),('MIX_MINUS_ISO_H','MIX_H','ISO_H',FREQ),('MIX_MINUS_ISO_F','MIX_F','ISO_F',FREQ),('MIX_MINUS_ISO_RANK','MIX_H_MINUS_F','ISO_H_MINUS_F',FREQ),('MIX_MINUS_ISO_H_POP','MIX_POP','ISO_H_POP',RAW),('MIX_MINUS_ISO_F_POP','MIX_POP','ISO_F_POP',RAW),('ISO_H_MINUS_F_POP','ISO_H_POP','ISO_F_POP',RAW)]:
    for m in ms:v[pre+out+'|'+m]=v[pre+a+'|'+m]-v[pre+b+'|'+m]
   for m in FREQ:assert abs(v[pre+'MIX_MINUS_ISO_RANK|'+m]-(v[pre+'MIX_MINUS_ISO_H|'+m]-v[pre+'MIX_MINUS_ISO_F|'+m]))<1e-14
 for g,h in LPAIRS:
  for c in COSTS:
   for s in CROSS:
    for m in FREQ:v[g+'_MINUS_'+h+'|'+c+'|'+s+'|'+m]=v[g+'|'+c+'|'+s+'|'+m]-v[h+'|'+c+'|'+s+'|'+m]
 assert len(v)==1482

def structural(k):
 g,c,s,m=k.split('|')
 if '_MINUS_' in g:return m in ('F0','F1')
 return s in FCON and m=='F0' or s in RCON and m=='U0'
def direction(k,ci):
 if structural(k):return 'structural_zero'
 return 'positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved'
