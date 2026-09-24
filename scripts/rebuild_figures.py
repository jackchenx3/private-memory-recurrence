"""Plot manuscript figures from published summaries, without fitting or simulation."""
from pathlib import Path
import argparse,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,default=ROOT/'_rebuilt/figures')
args=parser.parse_args();OUT=args.output_dir;OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,
                     'axes.labelsize':10,'svg.hashsalt':'private-memory-v1'})
DATA={s.name:json.loads((s/'summary.json').read_text())['values'] for s in (ROOT/'results').iterdir() if s.is_dir()}
records=[]
COLORS=['#176b8c','#b95340','#5b8061','#6f5c8c']

def panel(ax,series,labels,title,xlabel='Frequency-change contrast (pp)',offset=0):
    for i,(study,key) in enumerate(series):
        v=DATA[study][key];m,lo,hi=np.asarray([v['mean'],*v['ci95']])*100
        ax.errorbar(m,i+offset,xerr=[[m-lo],[hi-m]],fmt='o',ms=5,capsize=3,color=COLORS[0])
        records.append(dict(figure=current,study=study,key=key,mean_pp=m,ci95_pp=[lo,hi]))
    ax.set_yticks(range(len(labels)),labels);ax.set_ylim(len(labels)-.5,-.6)
    ax.axvline(0,color='#687682',lw=.8,ls='--');ax.grid(axis='x',alpha=.18)
    ax.set_title(title,loc='left',fontweight='bold',pad=12);ax.set_xlabel(xlabel)
    ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)

def save(fig,name):
    fig.tight_layout(pad=1.6,w_pad=2.8,h_pad=2.5)
    for ext in ['png','svg','pdf']:
        kw={'metadata':{'CreationDate':None,'ModDate':None}} if ext=='pdf' else {}
        fig.savefig(OUT/(name+'.'+ext),dpi=220,bbox_inches='tight',**kw)
    plt.close(fig)

current='01_replication';fig,axes=plt.subplots(1,2,figsize=(8.6,3.5))
for ax,s,title in zip(axes,['045','046'],['A  Original cohort','B  Independent cohort']):
    panel(ax,[(s,'RARE|'+g+'|ACTIVE_C0-NOVEL_C0|D40') for g in ['RECUR','IID','RECUR_MINUS_IID']],['Recurrent','Independent','Interaction'],title)
save(fig,current)

current='02_preparation_direction';fig,axes=plt.subplots(2,1,figsize=(8.6,5.8))
panel(axes[0],[('047',p+'|RECUR|ACTIVE_C0-NOVEL_C0|D40') for p in ['NAIVE','RESIDENT40','RESIDENT40_MINUS_NAIVE']],['Naive','Prepared','Prepared minus naive'],'A  Recurrent historical-minus-fresh effect')
panel(axes[1],[('048','NAIVE|RECUR|ACTIVE_C0-RADIUS_C0|D40'),('048','RESIDENT40|RECUR|ACTIVE_C0-RADIUS_C0|D40'),('048','RESIDENT40|IID|ACTIVE_C0-RADIUS_C0|D40')],['Naive, recurrent','Prepared, recurrent','Prepared, independent'],'B  Historical-minus-distance-control effect')
save(fig,current)

current='03_endpoint_fates';fig,ax=plt.subplots(figsize=(8.6,4.5))
fates=json.loads((ROOT/'provenance/MANUSCRIPT_STATISTICS.json').read_text())['fate_records'][:7]
left=np.zeros(len(fates))
for key,label,color in [('endpoint_extinct','Extinct','#c9d0d7'),('endpoint_polymorphic','Polymorphic','#d9953b'),('endpoint_fixed','Fixed','#176b8c')]:
    a=np.asarray([r['counts'].get(key,0) for r in fates]);ax.barh(range(len(fates)),a,left=left,color=color,label=label)
    left+=a
assert np.all(left==192)
ax.set_yticks(range(len(fates)),[r['label'].replace('Independent ·','Independent:').replace('Prepared ·','Prepared:') for r in fates]);ax.invert_yaxis();ax.set_xlim(0,192);ax.set_xlabel('Paths (24 blocks × 8 continuations)');ax.legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,-.16));ax.spines[['top','right']].set_visible(False)
records.append(dict(figure=current,endpoint_fates=fates));save(fig,current)

current='04_endpoint_disagreement';fig,axes=plt.subplots(1,2,figsize=(8.6,3.3))
for ax,s,prefix,title in [(axes[0],'047','RESIDENT40|IID|ACTIVE_C0-SHAM_C0|','A  Prepared independent\nhistorical minus sham'),(axes[1],'048','NAIVE|RECUR|RADIUS_C0-NOVEL_C0|','B  Naive recurrent\ndistance control minus fresh')]:
    panel(ax,[(s,prefix+m) for m in ['D40','U40']],['Founder change','Terminal accuracy'],title,'Contrast (pp; different endpoints)')
save(fig,current)

current='05_intermittent';fig,axes=plt.subplots(1,2,figsize=(8.6,3.8))
panel(axes[0],[('049','RESIDENT40|'+g+'|ACTIVE_C0-NOVEL_C0|D40') for g in ['ZERO','HALF','FULL','HALF_MINUS_ZERO']],['Renewed','Partial recurrence','Full recurrence','Partial minus renewed'],'A  Carrier transmission')
panel(axes[1],[('049','RESIDENT40|HALF|ACTIVE_C0-NOVEL_C0|'+m) for m in ['U','U40']],['Mean accuracy','Terminal accuracy'],'B  Partial recurrence','Accuracy contrast (pp)')
save(fig,current)

current='06_probabilistic_survival';fig,axes=plt.subplots(2,1,figsize=(8.6,6.3))
series=[];labels=[]
for op,name in [('BEST32','Deterministic'),('RACE32','Probabilistic')]:
    for g,lab in [('ZERO','renewed'),('HALF','partial'),('FULL','full')]:series.append(('050',op+'|'+g+'|ACTIVE_C0-NOVEL_C0|D40'));labels.append(name+', '+lab)
panel(axes[0],series,labels,'A  Historical-minus-fresh transmission')
panel(axes[1],[('050',op+'|HALF|ACTIVE_C0-NOVEL_C0|'+m) for op in ['BEST32','RACE32'] for m in ['U','U40']],['Deterministic mean','Deterministic terminal','Probabilistic mean','Probabilistic terminal'],'B  Partial recurrence','Accuracy contrast (pp)')
save(fig,current)

current='07_direct_competition';fig,axes=plt.subplots(2,1,figsize=(8.6,6.3))
panel(axes[0],[('051',g+'|C0|'+c+'|D40') for c in ['ISO_H_MINUS_F','MIX_H_MINUS_F'] for g in ['ZERO','HALF','FULL']],['Separate, renewed','Separate, partial','Separate, full','Mixed, renewed','Mixed, partial','Mixed, full'],'A  Historical-minus-fresh ranking')
panel(axes[1],[('051','HALF|C0|'+c+'|D40') for c in ['MIX_H_MINUS_F','MIX_H','MIX_F','MIX_MINUS_ISO_RANK']],['Mixed H minus F','Mixed H absolute','Mixed F absolute','Mixed minus separate ranking'],'B  Distinct partial-recurrence outcomes')
save(fig,current)

current='08_independent_preparation';fig,axes=plt.subplots(1,2,figsize=(8.6,3.6))
for ax,s,title in zip(axes,['051','052'],['A  Earlier prepared cohort','B  Independent preparation']):
    panel(ax,[(s,'HALF|C0|MIX_H_MINUS_F|D40'),(s,'HALF|C0|MIX_H|D40'),(s,'HALF_MINUS_ZERO|C0|MIX_H_MINUS_F|D40')],['H minus F','H absolute','Recurrence interaction'],title)
save(fig,current)

current='09_common_competitor';fig,axes=plt.subplots(3,1,figsize=(8.6,6.7),sharex=True)
for ax,g,title in zip(axes,['ZERO','HALF','FULL'],['A  Renewed targets','B  Partial recurrence','C  Full recurrence']):
    panel(ax,[('053',g+'|C0|'+k+'|D40') for k in ['R_H','R_F','INTERACTION']],['Against H','Against F','Difference'],title)
save(fig,current)

current='10_frequency_boundary';fig,axes=plt.subplots(1,2,figsize=(8.6,3.7))
for ax,key,title in [(axes[0],'LOW_H','A  Rare H among 31 F'),(axes[1],'HIGH_F','B  Rare F among 31 H')]:
    panel(ax,[('054',g+'|C0|'+key+'|D40') for g in ['ZERO','HALF','FULL']],['Renewed','Partial recurrence','Full recurrence'],title,'Absolute founder change (pp)')
save(fig,current)

current='11_policy_preparation';fig,axes=plt.subplots(2,2,figsize=(8.6,7.3))
for ax,key,title in [(axes[0,0],'F_BG_EFFECT','A  F-to-H matched effect'),(axes[0,1],'H_BG_EFFECT','B  H-to-F matched effect')]:
    panel(ax,[('055',g+'|C0|'+key+'|D40') for g in ['ZERO','HALF','FULL']],['Renewed','Partial recurrence','Full recurrence'],title,'Founder effect (pp)')
panel(axes[1,0],[('055','HALF|C0|'+k+'|D40') for k in ['F_BG_SWITCH','H_BG_SWITCH']],['Introduced H','Introduced F'],'C  Partial recurrence','Absolute founder change (pp)')
panel(axes[1,1],[('055','HALF|C0|'+k+'|'+m) for k in ['F_BG_EFFECT_POP','H_BG_EFFECT_POP'] for m in ['U','U40']],['F-to-H mean','F-to-H terminal','H-to-F mean','H-to-F terminal'],'D  Partial recurrence','Accuracy effect (pp)')
save(fig,current)
(OUT/'FIGURE_DATA.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(dict(figures=11,numerical_records=len(records),output_dir=str(OUT),new_simulations=0),indent=2))

# Add accepted crossed-environment figures without running population paths.
import subprocess,sys
subprocess.run([sys.executable,str(ROOT/"scripts/rebuild_extension_figures.py"),"--output-dir",str(OUT)],check=True)
records += json.loads((OUT/"EXTENSION_FIGURE_DATA.json").read_text())
(OUT/"FIGURE_DATA.json").write_text(json.dumps(records,indent=2)+"\n")
print(json.dumps(dict(figures=13,numerical_records=len(records),new_simulations=0)))
