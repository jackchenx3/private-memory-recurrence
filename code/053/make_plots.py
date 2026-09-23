import pathlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from analysis import *
P=pathlib.Path(__file__).resolve().parent;D=P/'figures';D.mkdir(exist_ok=True);v=json.loads((P/'summary.json').read_text())['values'];tr=json.loads((P/'TRAJECTORY_MEANS.json').read_text());ev=json.loads((P/'TYPE_EVENT_COUNTS.json').read_text());jo=json.loads((P/'JOINT_ENDPOINT_COUNTS.json').read_text())
def finish(fig,n):fig.savefig(D/(n+'.png'),dpi=140);fig.savefig(D/(n+'.pdf'));plt.close(fig)
def avg(g,c,cfgs,key):return [sum(tr[g+'|'+c+'|'+cfg][key][i] for cfg in cfgs)/len(cfgs) for i in range(41)]
def qfreq(g,c):
 hh=[x/2 for x in avg(g,c,('HH',),'CARR')];ff=[x/2 for x in avg(g,c,('FF',),'CARR')];h=[(a+b)/2 for a,b in zip(avg(g,c,('MIX0',),'p0'),avg(g,c,('MIX1',),'p1'))];f=[(a+b)/2 for a,b in zip(avg(g,c,('MIX0',),'p1'),avg(g,c,('MIX1',),'p0'))];return dict(HH_AVG=hh,HF_H=h,HF_F=f,FF_AVG=ff)
for kind in ('founders','carriers','raw_accuracy','penalized_accuracy'):
 fig,axes=plt.subplots(2,3,figsize=(17,9),constrained_layout=True)
 for i,c in enumerate(COSTS):
  for j,g in enumerate(LAWS):
   ax=axes[i,j]
   if kind=='founders':series=qfreq(g,c)
   else:series={name:avg(g,c,cfgs,'CARR' if kind=='carriers' else kind) for name,cfgs in [('HH',('HH',)),('HF',('MIX0','MIX1')),('FF',('FF',))]}
   for label,ys in series.items():ax.plot(range(41),ys,label=label)
   ax.set(title=g+' '+c,xlabel='Update',ylabel=kind);ax.legend(fontsize=8)
 fig.suptitle('Fixed two-carrier density; founder frequency and collective accuracy are separate');finish(fig,'01_'+kind)
for name,series in [('02_common_competitor',('R_H','R_F','INTERACTION')),('03_absolute_founders',FBASE),('04_competitor_effects',('COMP_H','COMP_F','MIX_RANK'))]:
 fig,axes=plt.subplots(2,3,figsize=(18,9),constrained_layout=True)
 for i,c in enumerate(COSTS):
  for j,g in enumerate(LAWS):
   ax=axes[i,j]
   for y,s in enumerate(series):
    q=v[g+'|'+c+'|'+s+'|D40'];ax.plot(q['ci95'],[y,y],color='tab:blue');ax.plot(q['mean'],y,'o',color='tab:blue')
   ax.set_yticks(range(len(series)));ax.set_yticklabels(series);ax.axvline(0,color='gray',lw=1);ax.set(title=g+' '+c,xlabel='Frequency change; approximate pointwise 95% interval')
 fig.suptitle('No prescribed interaction sign; unresolved does not establish equivalence');finish(fig,name)
fig,axes=plt.subplots(2,3,figsize=(18,10),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j];labels=[]
  for s in RCON:
   for m in ('U','U40'):
    y=len(labels);q=v[g+'|'+c+'|'+s+'|'+m];color='tab:blue' if m=='U' else 'tab:orange';ax.plot(q['ci95'],[y,y],color=color);ax.plot(q['mean'],y,'o',color=color);labels.append(s+' '+m)
  ax.set_yticks(range(len(labels)));ax.set_yticklabels(labels,fontsize=8);ax.axvline(0,color='gray',lw=1);ax.set(title=g+' '+c,xlabel='Collective raw accuracy difference; pointwise 95%')
finish(fig,'05_population_contrasts')
fig,axes=plt.subplots(2,3,figsize=(18,10),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,s in enumerate(CROSS):
  ax=axes[i,j];labs=[]
  for y,(g,h) in enumerate(LPAIRS):
   law=g+'_MINUS_'+h;q=v[law+'|'+c+'|'+s+'|D40'];ax.plot(q['ci95'],[y,y],color='tab:blue');ax.plot(q['mean'],y,'o',color='tab:blue');labs.append(law)
  ax.set_yticks(range(3));ax.set_yticklabels(labs);ax.axvline(0,color='gray',lw=1);ax.set(title=s+' '+c,xlabel='Direct law contrast; pointwise 95%')
finish(fig,'06_law_interactions')
fig,axes=plt.subplots(2,3,figsize=(18,12),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j];labs=[]
  for cfg in CONFIGS:
   for role in ('p0','p1','CARR','R'):
    y=len(labs);e=ev[g+'|'+c+'|'+cfg+'|'+role];left=0
    for state,color in [('extinct','gray'),('fixed','tab:blue'),('polymorphic','tab:orange')]:
     n=e.get('endpoint_'+state,0);ax.barh(y,n,left=left,color=color,label=state if y==0 else None);left+=n
    labs.append(cfg+' '+role)
  ax.set_yticks(range(len(labs)));ax.set_yticklabels(labs,fontsize=8);ax.set_xlim(0,192);ax.set_xticks([0,48,96,144,192]);ax.set(title=g+' '+c,xlabel='Paths /192; founder, carriers and residents distinct');ax.legend(fontsize=7)
finish(fig,'07_fates')
fig,axes=plt.subplots(2,3,figsize=(17,9),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j]
  for y,cfg in enumerate(CONFIGS):
   left=0;e=jo[g+'|'+c+'|'+cfg]
   for name,color in [('both_absent','gray'),('p0only','tab:blue'),('p1only','tab:orange'),('both_present','tab:green')]:
    n=e.get(name,0);ax.barh(y,n,left=left,color=color,label=name if y==0 else None);left+=n
  ax.set_yticks(range(4));ax.set_yticklabels(CONFIGS);ax.set_xlim(0,192);ax.set_xticks([0,48,96,144,192]);ax.set(title=g+' '+c,xlabel='Joint founder endpoints; residents detailed separately');ax.legend(fontsize=7)
fig.suptitle('Policy fixation can retain both founders; it is not necessarily founder fixation');finish(fig,'08_joint_founders')
sg=json.loads((P/'ORIENTATION_SIGNS.json').read_text());paired_sg=json.loads((P/'INDIVIDUAL_SIGNS.json').read_text())
fig,axes=plt.subplots(2,3,figsize=(17,10),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j];labs=[]
  for s in ('R_H','R_F','INTERACTION'):
   for ori in ('p0','p1','paired'):
    y=len(labs);d=paired_sg[g+'|'+c+'|'+s+'|D40'] if ori=='paired' else sg[g+'|'+c+'|'+ori+'|'+s+'|D40'];left=0
    for sign,color in [('negative','indianred'),('zero','darkgray'),('positive','tab:blue')]:
     n=d.get(sign,0);ax.barh(y,n,left=left,color=color,label=sign if y==0 else None);left+=n
    labs.append(s+' '+ori)
  ax.set_yticks(range(len(labs)));ax.set_yticklabels(labs,fontsize=8);ax.set_xlim(0,192);ax.set_xticks([0,48,96,144,192]);ax.set(title=g+' '+c,xlabel='Signs /192; placements remain paired');ax.legend(fontsize=7)
finish(fig,'09_orientation_signs')
