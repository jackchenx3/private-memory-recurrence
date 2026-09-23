import pathlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from analysis import *
P=pathlib.Path(__file__).resolve().parent;D=P/'figures';D.mkdir(exist_ok=True);v=json.loads((P/'summary.json').read_text())['values'];tr=json.loads((P/'TRAJECTORY_MEANS.json').read_text());ev=json.loads((P/'TYPE_EVENT_COUNTS.json').read_text());jo=json.loads((P/'JOINT_ENDPOINT_COUNTS.json').read_text())
def finish(fig,name):fig.savefig(D/(name+'.png'),dpi=140);fig.savefig(D/(name+'.pdf'));plt.close(fig)
def average(g,c,cfgs,key):return [sum(tr[g+'|'+c+'|'+cfg][key][i] for cfg in cfgs)/len(cfgs) for i in range(41)]
def point(ax,k,y,color='tab:blue'):
 q=v[k];ax.plot(q['ci95'],[y,y],color=color);ax.plot(q['mean'],y,'o',color=color)
for metric in ('frequency','resident','raw_accuracy','penalized_accuracy'):
 fig,axes=plt.subplots(2,3,figsize=(17,9),constrained_layout=True)
 for i,c in enumerate(COSTS):
  for j,g in enumerate(LAWS):
   ax=axes[i,j]
   if metric=='frequency':series=[('MIX H',('MIX0','MIX1'),'H'),('MIX F',('MIX0','MIX1'),'F'),('ISO H',('H0','H1'),'H'),('ISO F',('F0','F1'),'F')]
   elif metric=='resident':series=[('MIX R',('MIX0','MIX1'),'R'),('ISO H residents',('H0','H1'),'R'),('ISO F residents',('F0','F1'),'R')]
   else:series=[('MIX POP',('MIX0','MIX1'),metric),('ISO H POP',('H0','H1'),metric),('ISO F POP',('F0','F1'),metric)]
   for label,cfgs,key in series:ax.plot(range(41),average(g,c,cfgs,key),label=label)
   ax.set(title=g+' '+c,xlabel='Update',ylabel=metric);ax.legend(fontsize=8)
 fig.suptitle('Mean trajectories:192 paired continuations; each isolated series is a separate population');finish(fig,'01_'+metric)
for name,series,metric in [('02_ranking',('MIX_H_MINUS_F','ISO_H_MINUS_F','MIX_MINUS_ISO_RANK'),'D40'),('03_absolute_changes',FABS,'D40')]:
 fig,axes=plt.subplots(2,3,figsize=(17,9),constrained_layout=True)
 for i,c in enumerate(COSTS):
  for j,g in enumerate(LAWS):
   ax=axes[i,j]
   for y,s in enumerate(series):point(ax,g+'|'+c+'|'+s+'|'+metric,y)
   ax.set_yticks(range(len(series)),series);ax.axvline(0,color='.7');ax.xaxis.set_major_locator(MaxNLocator(4));ax.set(title=g+' '+c,xlabel='Frequency change; approximate pointwise95 interval')
 fig.suptitle('Direct ranking, absolute increase and composition moderation are separate');finish(fig,name)
fig,axes=plt.subplots(2,3,figsize=(18,10),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j];labels=[]
  for s in RCON:
   for metric in ('U','U40'):labels.append(s+' '+metric);point(ax,g+'|'+c+'|'+s+'|'+metric,len(labels)-1,'tab:blue' if metric=='U' else 'tab:orange')
  ax.set_yticks(range(len(labels)),labels,fontsize=8);ax.axvline(0,color='.7');ax.xaxis.set_major_locator(MaxNLocator(4));ax.set(title=g+' '+c,xlabel='Raw population accuracy difference; pointwise95')
fig.suptitle('One mixed-population accuracy, compared with separate isolated populations');finish(fig,'04_population_contrasts')
fig,axes=plt.subplots(2,3,figsize=(18,10),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,s in enumerate(CROSS):
  ax=axes[i,j];labels=[]
  for g,h in LPAIRS:
   label=g+'_MINUS_'+h;labels.append(label);point(ax,label+'|'+c+'|'+s+'|D40',len(labels)-1)
  ax.set_yticks(range(3),labels);ax.axvline(0,color='.7');ax.xaxis.set_major_locator(MaxNLocator(4));ax.set(title=s+' '+c,xlabel='Direct recurrence effect on ranking; pointwise95')
fig.suptitle('Recurrence interactions use paired differences');finish(fig,'05_law_interactions')
fig,axes=plt.subplots(2,3,figsize=(17,10),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j];groups=[(cfg,r) for cfg in CONFIGS for r in (('H','F') if cfg.startswith('MIX') else (cfg[0],))];labels=[cfg+' '+r for cfg,r in groups];left=[0]*8
  for state,color in [('extinct','#777777'),('fixed','#1764ab'),('polymorphic','#dc7b19')]:
   xs=[ev[g+'|'+c+'|'+cfg+'|'+r].get('endpoint_'+state,0) for cfg,r in groups];ax.barh(labels,xs,left=left,color=color,label=state);left=[a+b for a,b in zip(left,xs)]
  ax.set_xlim(0,192);ax.set_xticks([0,48,96,144,192]);ax.set_ylim(-.5,10);ax.legend(fontsize=8);ax.set(title=g+' '+c,xlabel='Introduced carrier paths /192; each placement retained')
fig.suptitle('Every introduced-carrier fate; absence is not conditioned away');finish(fig,'06_carrier_fates')
fig,axes=plt.subplots(2,3,figsize=(17,9),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j];left=[0,0]
  for state in ('both_absent','Honly','Fonly','both_present'):
   xs=[jo[g+'|'+c+'|MIX'+str(ori)].get(state,0) for ori in (0,1)];ax.barh(['MIX0','MIX1'],xs,left=left,label=state);left=[a+b for a,b in zip(left,xs)]
  ax.set_xlim(0,192);ax.set_xticks([0,48,96,144,192]);ax.set_ylim(-.5,2.5);ax.legend(fontsize=8);ax.set(title=g+' '+c,xlabel='Mixed paths /192; full fixation detailed in tables')
fig.suptitle('Joint carrier endpoints; co-occurrence at40 is not stable coexistence');finish(fig,'07_joint_endpoints')
signs=json.loads((P/'ORIENTATION_SIGNS.json').read_text());paired_signs=json.loads((P/'INDIVIDUAL_SIGNS.json').read_text());fig,axes=plt.subplots(2,3,figsize=(17,9),constrained_layout=True)
for i,c in enumerate(COSTS):
 for j,g in enumerate(LAWS):
  ax=axes[i,j];cs=[signs[g+'|'+c+'|MIX'+str(ori)+'|MIX_H_MINUS_F|D40'] for ori in (0,1)]+[paired_signs[g+'|'+c+'|MIX_H_MINUS_F|D40']];left=[0]*3
  for s,color in [('negative','#b44b45'),('zero','#aaaaaa'),('positive','#1764ab')]:
   xs=[q.get(s,0) for q in cs];ax.barh(['MIX0','MIX1','paired'],xs,left=left,label=s,color=color);left=[a+b for a,b in zip(left,xs)]
  ax.set_xlim(0,192);ax.set_xticks([0,48,96,144,192]);ax.set_ylim(-.5,4);ax.legend(fontsize=8);ax.set(title=g+' '+c,xlabel='H-minus-F path signs /192; orientations are paired')
fig.suptitle('No failed founder placement is hidden by averaging');finish(fig,'08_orientation_signs')
