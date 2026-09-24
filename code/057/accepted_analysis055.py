MODES=('ACTIVE_C0','ACTIVE_C1','NOVEL_C0','NOVEL_C1','SHAM_C0','SHAM_C1')
LAWS=('ZERO','HALF','FULL');COSTS=('C0',);BACKGROUNDS=('F','H');CONFIGS=('F_STAY','F_SWITCH0','F_SWITCH1','H_STAY','H_SWITCH0','H_SWITCH1');NEW=CONFIGS
RAW=('U0','U1','U','U40')+tuple('E'+str(i) for i in range(1,9))+('MLOSS',)
FREQ=('F0','F1','F','F40')+tuple('FE'+str(i) for i in range(1,9))+('D40',)
FBASE=('F_BG_SWITCH','F_BG_STAY','H_BG_SWITCH','H_BG_STAY');FCON=('F_BG_EFFECT','H_BG_EFFECT');RABS=tuple(s+'_POP' for s in FBASE);RCON=tuple(s+'_POP' for s in FCON);CROSS=('F_BG_SWITCH','H_BG_SWITCH','F_BG_EFFECT','H_BG_EFFECT');LPAIRS=(('HALF','ZERO'),('FULL','HALF'),('FULL','ZERO'))
def paired(rows):
 out={}
 for bg in BACKGROUNDS:
  stay=rows[bg+'_STAY'];a,b=rows[bg+'_SWITCH0'],rows[bg+'_SWITCH1']
  for m in FREQ:out[bg+'_BG_SWITCH|'+m]=(a['founders']['p0'][m]+b['founders']['p1'][m])/2;out[bg+'_BG_STAY|'+m]=(stay['founders']['p0'][m]+stay['founders']['p1'][m])/2
  for m in RAW:out[bg+'_BG_SWITCH_POP|'+m]=(a['raw'][m]+b['raw'][m])/2;out[bg+'_BG_STAY_POP|'+m]=stay['raw'][m]
 return out

def derive(v):
 for g in LAWS:
  pre=g+'|C0|'
  for bg in BACKGROUNDS:
   for m in FREQ:v[pre+bg+'_BG_EFFECT|'+m]=v[pre+bg+'_BG_SWITCH|'+m]-v[pre+bg+'_BG_STAY|'+m]
   for m in RAW:v[pre+bg+'_BG_EFFECT_POP|'+m]=v[pre+bg+'_BG_SWITCH_POP|'+m]-v[pre+bg+'_BG_STAY_POP|'+m]
 for g,h in LPAIRS:
  for s in CROSS:
   for m in FREQ:v[g+'_MINUS_'+h+'|C0|'+s+'|'+m]=v[g+'|C0|'+s+'|'+m]-v[h+'|C0|'+s+'|'+m]
 assert len(v)==624

def structural(k):
 g,c,s,m=k.split('|');return m=='F0' if '_MINUS_' in g else s in FCON and m=='F0' or s in RCON and m=='U0'
def direction(k,ci):return 'structural_zero' if structural(k) else 'positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved'

def orientation(rows,i):
 out={};fid='p'+str(i)
 for bg in BACKGROUNDS:
  switch=rows[bg+'_SWITCH'+str(i)];stay=rows[bg+'_STAY']
  for m in FREQ:
   a,b=switch['founders'][fid][m],stay['founders'][fid][m]
   for s,x in [('SWITCH',a),('STAY',b),('EFFECT',a-b)]:out[bg+'_BG_'+s+'|'+m]=x
  for m in RAW:
   a,b=switch['raw'][m],stay['raw'][m]
   for s,x in [('SWITCH',a),('STAY',b),('EFFECT',a-b)]:out[bg+'_BG_'+s+'_POP|'+m]=x
 return out
