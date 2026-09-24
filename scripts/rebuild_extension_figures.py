"""Rebuild the two added comparison figures from accepted, unpooled estimates."""
from pathlib import Path
import json, argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,default=ROOT/'_rebuilt/figures')
OUT=parser.parse_args().output_dir;OUT.mkdir(parents=True,exist_ok=True)
records=[]
v={s:json.loads((ROOT/'results'/s/'ESTIMATES.json').read_text()) for s in ('056','057')}
colors={'056':'#22627c','057':'#bd642d'}
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False})
founder=[('F-to-H: future effect\nafter ZERO preparation','Q_HALF_MINUS_ZERO_AT_P_ZERO|F_BG_EFFECT|D40'),
         ('F-to-H: future effect\nafter HALF preparation','Q_HALF_MINUS_ZERO_AT_P_HALF|F_BG_EFFECT|D40'),
         ('F-to-H: preparation-by-future\ninteraction','INTERACTION|F_BG_EFFECT|D40'),
         ('H-to-F: preparation-by-future\ninteraction','INTERACTION|H_BG_EFFECT|D40')]
fig,ax=plt.subplots(figsize=(8.6,6.2),layout='constrained')
for study,shift in [('056',-.12),('057',.12)]:
    for i,(label,key) in enumerate(founder):
        r=v[study][key];y=i+shift
        records.append(dict(figure='12_crossed_founder_effects',study=study,key=key,mean_pp=r['mean']*100,ci95_pp=[x*100 for x in r['ci95']]))
        ax.plot([100*x for x in r['ci95']],[y,y],color=colors[study],lw=2)
        ax.plot(r['mean']*100,y,'o',color=colors[study],label=('056: reused cohort' if study=='056' else '057: new cohort') if i==0 else None)
ax.set_yticks(range(4),[x[0] for x in founder]);ax.invert_yaxis();ax.axvline(0,color='#8b959b',lw=1)
ax.set_xlabel('Founder effect (percentage points)')
ax.set_title('Future recurrence and preparation\nSeparate cohorts; pointwise 95% intervals',loc='left',fontsize=13,fontweight='bold')
ax.legend(loc='lower right',fontsize=10)
fig.savefig(OUT/'12_crossed_founder_effects.png',dpi=180);plt.close(fig)
fig,axes=plt.subplots(2,1,figsize=(8.6,8.8),layout='constrained')
pop=[('HALF/HALF: F-to-H','P_HALF_Q_HALF','F'),('HALF/HALF: H-to-F','P_HALF_Q_HALF','H'),
     ('Future effect after HALF: F-to-H','Q_HALF_MINUS_ZERO_AT_P_HALF','F'),
     ('Future effect after HALF: H-to-F','Q_HALF_MINUS_ZERO_AT_P_HALF','H')]
for ax,metric,title in zip(axes,['U','U40'],['Mean population accuracy','Terminal population accuracy']):
    for study,shift in [('056',-.12),('057',.12)]:
        for i,(label,g,bg) in enumerate(pop):
            key=g+'|'+bg+'_BG_EFFECT_POP|'+metric
            r=v[study][key];y=i+shift
            records.append(dict(figure='13_crossed_population_effects',study=study,key=key,mean_pp=r['mean']*100,ci95_pp=[x*100 for x in r['ci95']]))
            ax.plot([100*x for x in r['ci95']],[y,y],color=colors[study],lw=2)
            ax.plot(r['mean']*100,y,'o',color=colors[study],label=study if i==0 else None)
    ax.set_yticks(range(4),[x[0] for x in pop]);ax.invert_yaxis();ax.axvline(0,color='#8b959b',lw=1)
    ax.set_title(title,loc='left',fontsize=14,fontweight='bold');ax.set_xlabel('Accuracy percentage points')
    ax.legend(loc='lower right',fontsize=9)
fig.savefig(OUT/'13_crossed_population_effects.png',dpi=180);plt.close(fig)
print('Rebuilt two comparison figures; no simulation or random draws.')

(OUT/'EXTENSION_FIGURE_DATA.json').write_text(json.dumps(records,indent=2)+'\n')
