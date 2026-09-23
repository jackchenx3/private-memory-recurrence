import pathlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analysis import MODES,LAWS
from matplotlib.ticker import MaxNLocator
ABUNDANCES=('NAIVE','RESIDENT40');ACCESS=('ACTIVE_C0-RADIUS_C0','ACTIVE_C1-RADIUS_C1')
P=pathlib.Path(__file__).resolve().parent;D=P/'plots';D.mkdir(exist_ok=True);V=json.loads((P/'summary.json').read_text())['values'];T=json.loads((P/'TRAJECTORY_MEANS.json').read_text());GROUPS=[a+'|'+g for a in ABUNDANCES for g in LAWS]
def finish(fig,name):
 for ax in fig.axes:
  if ax.get_xlabel()!='':ax.xaxis.set_major_locator(MaxNLocator(4))
 for ext in ('png','svg'):fig.savefig(D/(name+'.'+ext),dpi=170,bbox_inches='tight')
 plt.close(fig)
def point(ax,k,y):
 q=V[k];ax.errorbar(q['mean'],y,xerr=[[q['mean']-q['ci95'][0]],[q['ci95'][1]-q['mean']]],fmt='o',capsize=3)
fig,axes=plt.subplots(4,3,figsize=(19,17),constrained_layout=True)
for row,g in enumerate(GROUPS):
 for col,key in enumerate(('frequency','raw_accuracy','penalized_accuracy')):
  ax=axes[row,col]
  for pol in MODES:ax.plot(range(41),T[g+'|'+pol][key],label=pol)
  ax.set_title(g+' '+key);ax.set_xlabel('Update');ax.legend(fontsize=8)
  if key=='frequency':ax.axhline(1/32,color='.6',ls=':')
fig.suptitle('Finite resident preparation versus naive starts; all paths retained');finish(fig,'01_trajectories')
keys=['RESIDENT40|RECUR|ACTIVE_C0-RADIUS_C0|D40','RESIDENT40|RECUR|ACTIVE_C0|D40','RESIDENT40|RECUR|RADIUS_C0|D40','RESIDENT40|RECUR|RADIUS_C0-SHAM_C0|D40','RESIDENT40|RECUR|RADIUS_C0-NOVEL_C0|D40','NAIVE|RECUR|ACTIVE_C0-RADIUS_C0|D40','RESIDENT40_MINUS_NAIVE|RECUR|ACTIVE_C0-RADIUS_C0|D40','RESIDENT40|IID|ACTIVE_C0-RADIUS_C0|D40','RESIDENT40|RECUR|RADIUS_C1|D40'];fig,ax=plt.subplots(figsize=(18,9),constrained_layout=True)
for i,k in enumerate(keys):point(ax,k,i)
ax.set_yticks(range(len(keys)),keys);ax.axvline(0,color='.6');ax.set_xlabel('Carrier change or retrieval contrast');ax.set_title('Direction restriction: primary and separate absolute changes; approximate pointwise intervals');finish(fig,'02_primary')
fig,axes=plt.subplots(4,3,figsize=(18,17),constrained_layout=True)
for row,g in enumerate(GROUPS):
 for col,m in enumerate(('D40','U','U40')):
  ax=axes[row,col]
  for i,pol in enumerate(MODES):point(ax,g+'|'+pol+'|'+m,i)
  ax.set_yticks(range(8),MODES);ax.set_title(g+' '+m);ax.axvline(0,color='.7');ax.set_xlabel('Carrier change' if m=='D40' else 'Raw accuracy')
fig.suptitle('Absolute changes and raw performance; zero-width bootstrap is not impossibility');finish(fig,'03_absolute')
fig,axes=plt.subplots(4,3,figsize=(18,17),constrained_layout=True)
for row,g in enumerate(GROUPS):
 for col,m in enumerate(('D40','U','U40')):
  ax=axes[row,col]
  for i,pol in enumerate(ACCESS):point(ax,g+'|'+pol+'|'+m,i)
  ax.set_yticks(range(2),['Cost 0','Cost 1']);ax.set_ylim(-.4,1.4);ax.set_title(g+' '+m);ax.axvline(0,color='.7');ax.set_xlabel('Historical minus radius')
fig.suptitle('Historical minus radius probes; approximate pointwise intervals');finish(fig,'04_retrieval_contrasts')
fig,axes=plt.subplots(4,2,figsize=(16,17),constrained_layout=True)
for row,g in enumerate(GROUPS):
 for col,prefix in enumerate(('E','FE')):
  ax=axes[row,col]
  for pol in MODES:
   q=[V[g+'|'+pol+'|'+prefix+str(i)] for i in range(1,9)];ax.plot(range(1,9),[x['mean'] for x in q],marker='o',label=pol);ax.fill_between(range(1,9),[x['ci95'][0] for x in q],[x['ci95'][1] for x in q],alpha=.12)
  ax.set_title(g+(' raw accuracy' if prefix=='E' else ' carrier frequency'));ax.set_xticks(range(1,9));ax.set_xlabel('Five-update window');ax.legend(fontsize=8)
  if prefix=='FE':ax.axhline(1/32,color='.6',ls=':')
fig.suptitle('All fixed windows; no survivor-conditioned summaries');finish(fig,'05_windows')
E=json.loads((P/'TYPE_EVENT_COUNTS.json').read_text());fig,axes=plt.subplots(2,2,figsize=(16,10),constrained_layout=True)
for ax,g in zip(axes.flat,GROUPS):
 bottom=[0]*8
 for event in ('extinct','polymorphic','fixed'):
  ys=[E[g+'|'+pol].get('endpoint_'+event,0) for pol in MODES];ax.bar(MODES,ys,bottom=bottom,label=event);bottom=[x+y for x,y in zip(bottom,ys)]
 ax.set_ylim(0,200);ax.set_title(g);ax.set_ylabel('All 192 paths');ax.legend();ax.tick_params(axis='x',labelrotation=20)
fig.suptitle('Endpoint states: extinction, polymorphism and fixation are separate');finish(fig,'06_endpoint_events')
B=json.loads((P/'RARE_BLOCK_EVENTS.json').read_text());fig,ax=plt.subplots(figsize=(18,17),constrained_layout=True);ks=sorted(B)
ax.barh(ks,[B[k]['event_blocks'] for k in ks]);ax.set_xlim(0,40);ax.set_xlabel('Blocks with any endpoint survivor (of 24 independent blocks)')
for i,k in enumerate(ks):
 q=B[k];label='zero-event upper95 = %.4f (block probability)'%q['upper95'] if q['zero_event_bound_applicable'] else 'zero-event bound inapplicable';ax.text(q['event_blocks']+.2,i,label,va='center',fontsize=8)
ax.set_title('Eight continuations per block; never 192 independent lineages');finish(fig,'07_block_events')
C=json.loads((P/'FRESH_PROBE_COUNTS.json').read_text())['per_update'];fig,axes=plt.subplots(2,2,figsize=(16,10),constrained_layout=True)
for ax,g in zip(axes.flat,GROUPS):
 for pol in ('NOVEL_C0','NOVEL_C1'):
  q=C[g+'|'+pol];ax.plot(range(1,41),[r['carrier_fresh_probe_uses']/(192*32) for r in q],label=pol)
 ax.set_title(g+' fraction of recipient slots using fresh probe');ax.set_xlabel('Update');ax.set_ylabel('All 192 paths ×32 slots');ax.legend()
fig.suptitle('Unused noncarrier slots and extinct states remain in denominator');finish(fig,'08_fresh_probe_use')

fig,axes=plt.subplots(2,3,figsize=(17,9),constrained_layout=True)
for row,g in enumerate(LAWS):
 for col,m in enumerate(('D40','U','U40')):
  ax=axes[row,col]
  for i,pol in enumerate(('ACTIVE_C0-RADIUS_C0','ACTIVE_C1-RADIUS_C1')):point(ax,'RESIDENT40_MINUS_NAIVE|'+g+'|'+pol+'|'+m,i)
  ax.set_yticks(range(2),['Cost 0','Cost 1']);ax.set_ylim(-.4,1.4);ax.axvline(0,color='.6');ax.set_title(g+' '+m);ax.set_xlabel('Prepared minus naive: total effect')
fig.suptitle('Direct initial-state moderation; approximate pointwise intervals');finish(fig,'09_state_moderation')

C=json.loads((P/'RADIUS_PROBE_COUNTS.json').read_text())['per_update'];fig,axes=plt.subplots(4,2,figsize=(16,17),constrained_layout=True)
for row,g in enumerate(GROUPS):
 for pol in ('RADIUS_C0','RADIUS_C1'):
  q=C[g+'|'+pol];axes[row,0].plot(range(1,41),[r.get('used',0)/(192*32) for r in q],label=pol)
  axes[row,1].plot(range(1,41),[sum(d*r.get('all_slots_distance_'+str(d),0) for d in range(33))/(192*32) for r in q],label=pol)
 for col,lab in enumerate(('Fraction of all slots reading cache distance','Distance averaged over all slots (unused = 0)')):
  ax=axes[row,col];ax.set_title(g);ax.set_xlabel('Update');ax.set_ylabel(lab);ax.legend()
fig.suptitle('Own-state distance and use; extinct and unused slots remain in denominator');finish(fig,'10_radius_use_distance')
