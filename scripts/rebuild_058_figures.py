"""Readable manuscript figures from saved 058 estimates; no trajectories or RNG."""
from pathlib import Path
import argparse, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,default=R/'_rebuilt/figures')
out=parser.parse_args().output_dir;out.mkdir(parents=True,exist_ok=True)
v=json.loads((R/'results/058/ESTIMATES.json').read_text());records=[]
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def draw(ax,key,y,color,figure):
    q=v[key];ax.plot([100*x for x in q['ci95']],[y,y],color=color,lw=1.5);ax.plot(q['mean']*100,y,'o',color=color,ms=4)
    records.append(dict(figure=figure,study='058',key=key,mean_pp=q['mean']*100,ci95_pp=[x*100 for x in q['ci95']]))
groups=['HAM|Q_ZERO','HAM|Q_HALF','TRAP4|Q_ZERO','TRAP4|Q_HALF','HAM|Q_HALF_MINUS_ZERO','TRAP4|Q_HALF_MINUS_ZERO','TRAP4_MINUS_HAM|Q_HALF_MINUS_ZERO']
labels=['HAM: ZERO','HAM: HALF','TRAP4: ZERO','TRAP4: HALF','HAM: future effect','TRAP4: future effect','TRAP4 - HAM: future effect']
name='14_interacting_objective_founders'
fig,axes=plt.subplots(1,2,figsize=(8,4.8),sharey=True,layout='constrained')
for ax,bg in zip(axes,('F','H')):
    for i,g in enumerate(groups):draw(ax,g+'|'+bg+'_BG_EFFECT|D40',i,'#bb642c' if g.startswith('TRAP4') else '#246783',name)
    ax.axvline(0,color='#8b959b',lw=.8);ax.set_yticks(range(7));ax.set_title('F-to-H substitution' if bg=='F' else 'H-to-F substitution',fontsize=11);ax.tick_params(labelsize=9)
axes[0].set_yticklabels(labels,fontsize=9);axes[0].invert_yaxis()
axes[0].plot([3.125,3.125],[4.72,5.28],color='black',lw=2)
axes[0].set_xticks([0,10,20,30]);axes[1].set_xticks([-10,-5,0,5])
fig.supxlabel('Matched founder effect (percentage points); pointwise 95% intervals',fontsize=10)
for ext in ('png','pdf'):fig.savefig(out/(name+'.'+ext),dpi=180)
plt.close(fig)
name='15_interacting_objective_population'
fig,axes=plt.subplots(2,2,figsize=(8,6),layout='constrained')
for row,obj in enumerate(('HAM','TRAP4')):
    for col,metric in enumerate(('U','U40')):
        ax=axes[row,col]
        for i,(q,bg) in enumerate((q,bg) for q in ('ZERO','HALF') for bg in ('F','H')):
            for kind,dy,color in [('SWITCH',-.12,'#bb642c'),('STAY',.12,'#246783')]:
                draw(ax,obj+'|Q_'+q+'|'+bg+'_BG_'+kind+'_POP|'+metric,i+dy,color,name)
        ax.set_yticks(range(4));ax.set_yticklabels(['ZERO F-to-H','ZERO H-to-F','HALF F-to-H','HALF H-to-F'],fontsize=9);ax.invert_yaxis();ax.tick_params(axis='x',labelsize=9)
        ax.set_title(obj+(': mean utility' if metric=='U' else ': terminal utility'),fontsize=11)
        if row==0 and col==1:
            for label,color in [('Switch','#bb642c'),('Stay','#246783')]:ax.plot([],[],'o-',color=color,label=label,ms=4)
            ax.legend(loc='upper right',fontsize=9)
fig.supxlabel('Own-objective utility (%); pointwise 95% intervals',fontsize=10)
for ext in ('png','pdf'):fig.savefig(out/(name+'.'+ext),dpi=180)
plt.close(fig)
(out/'FIGURE_058_DATA.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(dict(figures=2,source_bound_statistics=len(records),new_scientific_paths=0)))
