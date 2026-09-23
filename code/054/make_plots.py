import pathlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analysis import LAWS,CONFIGS,FBASE,FCON,CROSS,LPAIRS
P=pathlib.Path(__file__).resolve().parent;D=P/'figures';D.mkdir(exist_ok=True);v=json.loads((P/'summary.json').read_text())['values'];tr=json.loads((P/'TRAJECTORY_MEANS.json').read_text())
def finish(fig,n):fig.savefig(D/(n+'.png'),dpi=140);fig.savefig(D/(n+'.pdf'));plt.close(fig)
def avg(g,pre,key):return [(a+b)/2 for a,b in zip(tr[g+'|C0|'+pre+'0'][key],tr[g+'|C0|'+pre+'1'][key])]
fig,axes=plt.subplots(1,3,figsize=(17,5),constrained_layout=True)
for ax,g in zip(axes,LAWS):
 for pre in ('LOW','HIGH'):
  for r in ('H','F'):ax.plot(range(41),avg(g,pre,r),label=pre+'_'+r)
 ax.set(title=g,xlabel='Update',ylabel='Policy frequency',ylim=(-.03,1.03));ax.legend(fontsize=8)
fig.suptitle('All 32 individuals retrieve; placements paired, finite initial compositions');finish(fig,'01_policy_frequencies')
fig,axes=plt.subplots(1,3,figsize=(17,5),constrained_layout=True)
for ax,g in zip(axes,LAWS):
 for pre in ('LOW','HIGH'):ax.plot(range(41),avg(g,pre,'raw_accuracy'),label=pre)
 ax.set(title=g,xlabel='Update',ylabel='Collective raw accuracy');ax.legend()
fig.suptitle('Cost 0: raw and penalized accuracy coincide');finish(fig,'02_population_accuracy')
fig,axes=plt.subplots(1,3,figsize=(17,6),constrained_layout=True)
for ax,g in zip(axes,LAWS):
 ss=FBASE+FCON
 for i,s in enumerate(ss):
  q=v[g+'|C0|'+s+'|D40'];ax.plot(q['ci95'],[i,i],color='tab:blue');ax.plot(q['mean'],i,'o',color='tab:blue')
 ax.set_yticks(range(len(ss)));ax.set_yticklabels(ss);ax.axvline(0,color='gray',lw=1);ax.set(title=g,xlabel='Frequency change; approximate pointwise 95%')
fig.suptitle('LOW_MINUS_HIGH_H change differs from its final-frequency contrast');finish(fig,'03_frequency_changes')
fig,axes=plt.subplots(1,3,figsize=(16,4),constrained_layout=True)
for ax,g in zip(axes,LAWS):
 for i,m in enumerate(('U','U40')):
  q=v[g+'|C0|LOW_MINUS_HIGH_POP|'+m];ax.plot(q['ci95'],[i,i],color='tab:blue');ax.plot(q['mean'],i,'o',color='tab:blue')
 ax.set_yticks([0,1]);ax.set_yticklabels(['Mean U','Terminal U40']);ax.axvline(0,color='gray',lw=1);ax.set(title=g,xlabel='LOW minus HIGH raw accuracy; pointwise 95%')
finish(fig,'04_population_contrasts')
fig,axes=plt.subplots(1,3,figsize=(18,5),constrained_layout=True)
for ax,s in zip(axes,CROSS):
 labels=[]
 for i,(g,h) in enumerate(LPAIRS):
  law=g+'_MINUS_'+h;q=v[law+'|C0|'+s+'|D40'];ax.plot(q['ci95'],[i,i],color='tab:blue');ax.plot(q['mean'],i,'o',color='tab:blue');labels.append(law)
 ax.set_yticks(range(3));ax.set_yticklabels(labels);ax.axvline(0,color='gray',lw=1);ax.set(title=s,xlabel='Direct law difference; pointwise 95%')
finish(fig,'05_law_contrasts')
ev=json.loads((P/'TYPE_EVENT_COUNTS.json').read_text());jo=json.loads((P/'JOINT_ENDPOINT_COUNTS.json').read_text());sg=json.loads((P/'ORIENTATION_SIGNS.json').read_text());paired=json.loads((P/'INDIVIDUAL_SIGNS.json').read_text())
for kind in ('fates','joint','signs'):
 fig,axes=plt.subplots(1,3,figsize=(18,7 if kind=='fates' else 5),constrained_layout=True)
 for ax,g in zip(axes,LAWS):
  labels=[]
  if kind=='fates':
   for cfg in CONFIGS:
    for role in ('H','F','RARE'):
     q=ev[g+'|C0|'+cfg+'|'+role];y=len(labels);left=0
     for state,color in [('extinct','gray'),('fixed','tab:blue'),('polymorphic','tab:orange')]:
      n=q.get('endpoint_'+state,0);ax.barh(y,n,left=left,color=color,label=state if y==0 else None);left+=n
     labels.append(cfg+' '+role)
  elif kind=='joint':
   for cfg in CONFIGS:
    q=jo[g+'|C0|'+cfg];y=len(labels);left=0
    for state,color in [('H_only','tab:blue'),('F_only','tab:orange'),('both_present','tab:green')]:
     n=q.get(state,0);ax.barh(y,n,left=left,color=color,label=state if y==0 else None);left+=n
    labels.append(cfg)
  else:
   for s in ('LOW_H','HIGH_F','LOW_MINUS_HIGH_H'):
    for ori in ('p0','p1','paired'):
     q=paired[g+'|C0|'+s+'|D40'] if ori=='paired' else sg[g+'|C0|'+ori+'|'+s+'|D40'];y=len(labels);left=0
     for sign,color in [('negative','indianred'),('zero','darkgray'),('positive','tab:blue')]:
      n=q.get(sign,0);ax.barh(y,n,left=left,color=color,label=sign if y==0 else None);left+=n
     labels.append(s+' '+ori)
  ax.set_yticks(range(len(labels)));ax.set_yticklabels(labels,fontsize=8);ax.set_xlim(0,192);ax.set_xticks([0,48,96,144,192]);ax.set_ylim(-.65,len(labels)-.5+max(1.,len(labels)*.16));ax.legend(loc='upper center',ncol=3,fontsize=8,frameon=False);ax.set(title=g,xlabel='Continuations /192; orientations remain paired')
 fig.suptitle('Finite policy outcomes; majority fixation need not be single-founder fixation');finish(fig,{'fates':'06_fates','joint':'07_joint_policies','signs':'08_orientation_signs'}[kind])
