import json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analysis import STARTS,LAWS,MODES,CROSS
P=pathlib.Path(__file__).resolve().parent;D=P/'figures';D.mkdir(exist_ok=True)
v=json.loads((P/'summary.json').read_text())['values'];t=json.loads((P/'TRAJECTORY_MEANS.json').read_text());events=json.loads((P/'TYPE_EVENT_COUNTS.json').read_text());diag=json.loads((P/'SELECTION_DIAGNOSTICS.json').read_text())
colors={'ACTIVE':'#1764ab','NOVEL':'#dc7b19','SHAM':'#777777'}
def finish(fig,name):
 fig.savefig(D/(name+'.png'),dpi=140);fig.savefig(D/(name+'.pdf'));plt.close(fig)
def point(ax,key,y,color='tab:blue'):
 q=v[key];lo,hi=q['ci95'];ax.plot([lo,hi],[y,y],color=color);ax.plot(q['mean'],y,'o',color=color)
for metric,label in [('frequency','Carrier frequency'),('raw_accuracy','Raw accuracy'),('penalized_accuracy','Penalized accuracy')]:
 fig,axes=plt.subplots(2,3,figsize=(16,9),constrained_layout=True)
 for i,a in enumerate(STARTS):
  for j,g in enumerate(LAWS):
   ax=axes[i,j]
   for p in MODES:ax.plot(range(41),t[a+'|'+g+'|'+p][metric],label=p,color=colors[p.split('_')[0]],linestyle='--' if p.endswith('C1') else '-')
   ax.set(title=a+' '+g,xlabel='Update',ylabel=label);ax.legend(fontsize=8)
 fig.suptitle('All192paths per arm; prepared initial states shared');finish(fig,'01_'+metric)
for metric in ('D40','U','U40'):
 fig,axes=plt.subplots(2,3,figsize=(16,9),constrained_layout=True)
 for i,a in enumerate(STARTS):
  for j,g in enumerate(LAWS):
   ax=axes[i,j]
   for y,p in enumerate(MODES):point(ax,a+'|'+g+'|'+p+'|'+metric,y,colors[p.split('_')[0]])
   ax.set_yticks(range(6),MODES);ax.axvline(0,color='.7');ax.set(title=a+' '+g,xlabel=metric+'; approximate pointwise95 interval')
 fig.suptitle('Absolute arm outcomes; carrier change and accuracy are distinct');finish(fig,'02_absolute_'+metric)
fig,axes=plt.subplots(3,3,figsize=(18,13),constrained_layout=True)
for i,a in enumerate(('BEST32','RACE32','RACE32_MINUS_BEST32')):
 for j,m in enumerate(('D40','U','U40')):
  ax=axes[i,j];labels=[]
  for g in LAWS:
   for pol in ('ACTIVE_C0-NOVEL_C0','ACTIVE_C0-SHAM_C0'):
    labels.append(g+' '+pol);point(ax,a+'|'+g+'|'+pol+'|'+m,len(labels)-1)
  ax.set_yticks(range(len(labels)),labels,fontsize=8);ax.axvline(0,color='.7');ax.set(title=a+' '+m,xlabel='Approximate pointwise95 interval')
fig.suptitle('Policy contrasts and direct selection moderation');finish(fig,'03_contrasts')
fig,axes=plt.subplots(2,3,figsize=(18,10),constrained_layout=True)
for i,a in enumerate(STARTS):
 for j,m in enumerate(('D40','U','U40')):
  ax=axes[i,j];labels=[]
  for g in ('HALF_MINUS_ZERO','FULL_MINUS_HALF','FULL_MINUS_ZERO'):
   for pol in ('ACTIVE_C0-NOVEL_C0','ACTIVE_C0-SHAM_C0'):
    labels.append(g+' '+pol);point(ax,a+'|'+g+'|'+pol+'|'+m,len(labels)-1)
  ax.set_yticks(range(len(labels)),labels,fontsize=8);ax.axvline(0,color='.7');ax.set(title=a+' '+m,xlabel='Direct law interaction; pointwise95')
fig.suptitle('Incremental recurrence is a separate test');finish(fig,'04_law_interactions')
fig,axes=plt.subplots(2,3,figsize=(16,9),constrained_layout=True)
for i,a in enumerate(STARTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j];left=[0]*6
  for state,color in [('extinct','#777777'),('fixed','#1764ab'),('polymorphic','#dc7b19')]:
   xs=[events[a+'|'+g+'|'+p].get('endpoint_'+state,0) for p in MODES];ax.barh(MODES,xs,left=left,label=state,color=color);left=[l+x for l,x in zip(left,xs)]
  ax.set(title=a+' '+g,xlabel='Paths /192');ax.legend(fontsize=8)
fig.suptitle('Every endpoint retained, including extinctions');finish(fig,'05_events')
fig,axes=plt.subplots(2,3,figsize=(16,9),constrained_layout=True)
for i,a in enumerate(STARTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j]
  for offset,key,color in [(-.2,'S_raw_negative','#1764ab'),(.2,'S_pen_negative','#dc7b19')]:ax.bar([k+offset for k in range(6)],[diag[a+'|'+g+'|'+p].get(key,0) for p in MODES],width=.4,label=key,color=color)
  ax.set_xticks(range(6),MODES,rotation=30,ha='right');ax.set(title=a+' '+g,ylabel='Updates /7680');ax.legend()
fig.suptitle('Negative selection improvement is valid under RACE32');finish(fig,'06_negative_selection')
