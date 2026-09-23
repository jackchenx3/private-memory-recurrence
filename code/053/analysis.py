MODES=('ACTIVE_C0','ACTIVE_C1','NOVEL_C0','NOVEL_C1','SHAM_C0','SHAM_C1')
LAWS=('ZERO','HALF','FULL');COSTS=('C0','C1');CONFIGS=('HH','FF','MIX0','MIX1');NEW=('HH','FF')
RAW=('U0','U1','U','U40')+tuple('E'+str(i) for i in range(1,9))+('MLOSS',)
FREQ=('F0','F1','F','F40')+tuple('FE'+str(i) for i in range(1,9))+('D40',)
FBASE=('HH_AVG','HF_H','HF_F','FF_AVG');FCARR=('HH_CARR','HF_CARR','FF_CARR')
FCON=('R_H','R_F','COMP_H','COMP_F','INTERACTION','MIX_RANK');FABS=FBASE+FCARR
RABS=('HH_POP','HF_POP','FF_POP');RCON=('HH_MINUS_HF_POP','HH_MINUS_FF_POP','HF_MINUS_FF_POP');CROSS=('R_H','R_F','INTERACTION');LPAIRS=(('HALF','ZERO'),('FULL','HALF'),('FULL','ZERO'))

def paired(rows):
 out={}
 for m in FREQ:
  out['HH_AVG|'+m]=(rows['HH']['founders']['p0'][m]+rows['HH']['founders']['p1'][m])/2
  out['FF_AVG|'+m]=(rows['FF']['founders']['p0'][m]+rows['FF']['founders']['p1'][m])/2
  out['HF_H|'+m]=(rows['MIX0']['frequency']['H'][m]+rows['MIX1']['frequency']['H'][m])/2
  out['HF_F|'+m]=(rows['MIX0']['frequency']['F'][m]+rows['MIX1']['frequency']['F'][m])/2
 for m in RAW:
  out['HH_POP|'+m]=rows['HH']['raw'][m];out['FF_POP|'+m]=rows['FF']['raw'][m];out['HF_POP|'+m]=(rows['MIX0']['raw'][m]+rows['MIX1']['raw'][m])/2
 return out

def derive(v):
 for g in LAWS:
  for c in COSTS:
   pre=g+'|'+c+'|'
   for m in FREQ:
    get=lambda s:v[pre+s+'|'+m]
    for s,x in [('HH_CARR',2*get('HH_AVG')),('HF_CARR',get('HF_H')+get('HF_F')),('FF_CARR',2*get('FF_AVG')),('R_H',get('HH_AVG')-get('HF_F')),('R_F',get('HF_H')-get('FF_AVG')),('COMP_H',get('HH_AVG')-get('HF_H')),('COMP_F',get('HF_F')-get('FF_AVG')),('MIX_RANK',get('HF_H')-get('HF_F'))]:v[pre+s+'|'+m]=x
    v[pre+'INTERACTION|'+m]=get('R_H')-get('R_F');assert abs(get('INTERACTION')-(get('COMP_H')-get('COMP_F')))<1e-14;assert abs(get('INTERACTION')-((get('HH_CARR')+get('FF_CARR'))/2-get('HF_CARR')))<1e-14
   for s,a,b in [('HH_MINUS_HF_POP','HH_POP','HF_POP'),('HH_MINUS_FF_POP','HH_POP','FF_POP'),('HF_MINUS_FF_POP','HF_POP','FF_POP')]:
    for m in RAW:v[pre+s+'|'+m]=v[pre+a+'|'+m]-v[pre+b+'|'+m]
 for g,h in LPAIRS:
  for c in COSTS:
   for s in CROSS:
    for m in FREQ:v[g+'_MINUS_'+h+'|'+c+'|'+s+'|'+m]=v[g+'|'+c+'|'+s+'|'+m]-v[h+'|'+c+'|'+s+'|'+m]
 assert len(v)==1716

def structural(k):
 g,c,s,m=k.split('|')
 return m in ('F0','F1') if '_MINUS_' in g else s in FCON and m=='F0' or s in RCON and m=='U0'
def direction(k,ci):return 'structural_zero' if structural(k) else 'positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved'

def orientation(rows,i):
 other=1-i;k='p'+str(i);hh=rows['HH']['founders'][k];ff=rows['FF']['founders'][k];h=rows['MIX'+str(i)]['founders'][k];f=rows['MIX'+str(other)]['founders'][k];out={}
 for m in FREQ:
  vals={'HH_AVG':hh[m],'HF_H':h[m],'HF_F':f[m],'FF_AVG':ff[m],'R_H':hh[m]-f[m],'R_F':h[m]-ff[m],'COMP_H':hh[m]-h[m],'COMP_F':f[m]-ff[m],'MIX_RANK':h[m]-f[m]};vals['INTERACTION']=vals['R_H']-vals['R_F'];assert abs(vals['INTERACTION']-(vals['COMP_H']-vals['COMP_F']))<1e-14
  out.update({s+'|'+m:x for s,x in vals.items()})
 return out
