import pathlib,json,gzip
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analysis import *
P=pathlib.Path(__file__).resolve().parent;D=P/'figures';D.mkdir(exist_ok=True);v=json.loads((P/'summary.json').read_text())['values'];tr=json.loads((P/'TRAJECTORY_MEANS.json').read_text())
def finish(fig,n):fig.savefig(D/(n+'.png'),dpi=140);fig.savefig(D/(n+'.pdf'));plt.close(fig)
def avg(g,bg,switch,key):
 if not switch:return tr[g+'|C0|'+bg+'_STAY'][key]
 return [(a+b)/2 for a,b in zip(tr[g+'|C0|'+bg+'_SWITCH0'][key],tr[g+'|C0|'+bg+'_SWITCH1'][key])]
fig,axes=plt.subplots(1,3,figsize=(17,5),constrained_layout=True)
for ax,g in zip(axes,LAWS):
 for bg in BACKGROUNDS:
  a=tr[g+'|C0|'+bg+'_SWITCH0']['p0'];b=tr[g+'|C0|'+bg+'_SWITCH1']['p1'];stay=tr[g+'|C0|'+bg+'_STAY'];ax.plot(range(41),[(x+y)/2 for x,y in zip(a,b)],label=bg+'_BG_SWITCH');ax.plot(range(41),[(x+y)/2 for x,y in zip(stay['p0'],stay['p1'])],label=bg+'_BG_STAY',ls='--')
 ax.set(title=g,xlabel='Transfer update (absolute time 40–79)',ylabel='Focal founder frequency');ax.legend(fontsize=8)
fig.suptitle('Substitution and same-founder unchanged-policy controls; caches retained');finish(fig,'01_focal_trajectories')
fig,axes=plt.subplots(1,3,figsize=(17,5),constrained_layout=True)
for ax,g in zip(axes,LAWS):
 for bg in BACKGROUNDS:
  for sw in (True,False):ax.plot(range(41),avg(g,bg,sw,'raw_accuracy'),label=bg+('_SWITCH' if sw else '_STAY'),ls='-' if sw else '--')
 ax.set(title=g,xlabel='Transfer update',ylabel='Collective raw accuracy');ax.legend(fontsize=8)
fig.suptitle('Initial accuracy uses the first continuation target; cost 0');finish(fig,'02_population_accuracy')
for name,series,metrics in [('03_focal_changes',FBASE+FCON,('D40',)),('04_population_effects',RCON,('U','U40'))]:
 fig,axes=plt.subplots(1,3,figsize=(18,6),constrained_layout=True)
 for ax,g in zip(axes,LAWS):
  labs=[]
  for s in series:
   for m in metrics:
    q=v[g+'|C0|'+s+'|'+m];i=len(labs);ax.plot(q['ci95'],[i,i],color='tab:blue');ax.plot(q['mean'],i,'o',color='tab:blue');labs.append(s+' '+m)
  ax.set_yticks(range(len(labs)));ax.set_yticklabels(labs,fontsize=8);ax.axvline(0,color='gray',lw=1);ax.set(title=g,xlabel='Difference/change; approximate pointwise 95%')
 finish(fig,name)
fig,axes=plt.subplots(2,2,figsize=(14,9),constrained_layout=True)
for ax,s in zip(axes.flat,CROSS):
 labs=[]
 for i,(g,h) in enumerate(LPAIRS):
  law=g+'_MINUS_'+h;q=v[law+'|C0|'+s+'|D40'];ax.plot(q['ci95'],[i,i],color='tab:blue');ax.plot(q['mean'],i,'o',color='tab:blue');labs.append(law)
 ax.set_yticks(range(3));ax.set_yticklabels(labs);ax.axvline(0,color='gray',lw=1);ax.set(title=s,xlabel='Direct law difference; pointwise 95%')
fig.suptitle('Regimes change both preparation and continuation');finish(fig,'05_regime_contrasts')
ev=json.loads((P/'TYPE_EVENT_COUNTS.json').read_text());jo=json.loads((P/'JOINT_ENDPOINT_COUNTS.json').read_text());sg=json.loads((P/'ORIENTATION_SIGNS.json').read_text());psg=json.loads((P/'INDIVIDUAL_SIGNS.json').read_text())
for kind in ('switch_fates','stay_fates','switch_joint','stay_joint','signs'):
 fig,axes=plt.subplots(1,3,figsize=(18,7 if kind in ('switch_fates','signs') else 5),constrained_layout=True)
 for ax,g in zip(axes,LAWS):
  labs=[];items=[]
  if 'fates' in kind:
   configs=[s for s in CONFIGS if ('SWITCH' in s)==kind.startswith('switch')]
   for cfg in configs:
    for r in (('H','F','RARE') if kind.startswith('switch') else ('p0','p1')):items.append((cfg+' '+r,ev[g+'|C0|'+cfg+'|'+r]))
   states=[('endpoint_extinct','gray'),('endpoint_fixed','tab:blue'),('endpoint_polymorphic','tab:orange')]
  elif 'joint' in kind:
   configs=[s for s in CONFIGS if ('SWITCH' in s)==kind.startswith('switch')];items=[(cfg,jo[g+'|C0|'+cfg]) for cfg in configs];states=[('H_only','tab:blue'),('F_only','tab:orange'),('both_present','tab:green')] if kind.startswith('switch') else [('neither','gray'),('p0only','tab:blue'),('p1only','tab:orange'),('both_present','tab:green')]
  else:
   for s in CROSS:
    for ori in ('p0','p1','paired'):items.append((s+' '+ori,psg[g+'|C0|'+s+'|D40'] if ori=='paired' else sg[g+'|C0|'+ori+'|'+s+'|D40']))
   states=[('negative','indianred'),('zero','darkgray'),('positive','tab:blue')]
  for label,q in items:
   i=len(labs);left=0
   for state,color in states:n=q.get(state,0);ax.barh(i,n,left=left,color=color,label=state.replace('endpoint_','') if i==0 else None);left+=n
   labs.append(label)
  ax.set_yticks(range(len(labs)));ax.set_yticklabels(labs,fontsize=8);ax.set_xlim(0,192);ax.set_xticks([0,48,96,144,192]);ax.set_ylim(-.65,len(labs)-.5+max(1.,len(labs)*.18));ax.legend(loc='upper center',ncol=len(states),fontsize=7,frameon=False);ax.set(title=g,xlabel='Continuations /192; placements paired')
 fig.suptitle('Founder transmission differs from policy fixation; all losses retained');finish(fig,{'switch_fates':'06_switch_fates','stay_fates':'07_stay_fates','switch_joint':'08_switch_joint','stay_joint':'09_stay_joint','signs':'10_orientation_signs'}[kind])
pre={g+'|'+bg:[0.]*41 for g in LAWS for bg in BACKGROUNDS}
with gzip.open(P/'PREPARATION_DESCRIPTIONS.jsonl.gz','rt') as src:
 for line in src:
  q=json.loads(line);key=q['geometry']+'|'+q['background']
  for i,x in enumerate(q['raw_accuracy']):pre[key][i]+=x/192
fig,axes=plt.subplots(1,3,figsize=(17,5),constrained_layout=True)
for ax,g in zip(axes,LAWS):
 for bg in BACKGROUNDS:ax.plot(range(41),pre[g+'|'+bg],label='all '+bg)
 ax.set(title=g,xlabel='Preparation update (absolute time 0–39)',ylabel='Collective raw accuracy');ax.legend()
fig.suptitle('New finite resident preparation; all 1,152 endpoints retained');finish(fig,'11_preparation_accuracy')
