"""Figure17 from seven saved contrasts; no scientific draws or trajectories."""
from pathlib import Path
import argparse,json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=R/'_rebuilt/figures');OUT=p.parse_args().output_dir;OUT.mkdir(parents=True,exist_ok=True)
e=json.loads((R/'results/060/ESTIMATES.json').read_text());records=[]
fig,axes=plt.subplots(2,1,figsize=(6.8,6.2),constrained_layout=True)
upper=[('EXACT_Q_HALF_MINUS_ZERO|EFFECT|D40','Exact: HALF minus ZERO'),('NOISY_Q_HALF_MINUS_ZERO|EFFECT|D40','Noisy: HALF minus ZERO'),('NOISE_BY_RECURRENCE|EFFECT|D40','Noise interaction (primary)')]
lower=[('NOISY_MINUS_EXACT_AT_Q_'+law+'|'+kind+'_POP|U',law+': '+label) for law in ['ZERO','HALF'] for kind,label in [('SWITCH','H introduction'),('STAY','all F')]]
for ax,items,title,xlabel in [(axes[0],upper,'Founder recurrence effects and their change','Founder percentage points'),(axes[1],lower,'Noise lowers absolute mean true accuracy','Accuracy percentage points: noisy minus exact')]:
 for i,(key,label) in enumerate(items):
  q=e[key];m=q['mean']*100;ci=[x*100 for x in q['ci95']];color='#ad5420' if 'NOISE_BY_RECURRENCE' in key else '#176b8c';ax.plot(ci,[i,i],color=color,lw=2);ax.plot(m,i,'o',color=color,ms=5);records.append(dict(study='060',figure='17_measurement_error',key=key,mean_pp=m,ci95_pp=ci))
 ax.axvline(0,color='#777777',lw=.8);ax.set_yticks(range(len(items)),[q[1] for q in items],fontsize=8.5);ax.invert_yaxis();ax.set_title(title,fontsize=11);ax.set_xlabel(xlabel+'\nExploratory pointwise 95% intervals',fontsize=9);ax.tick_params(axis='x',labelsize=9)
axes[0].set_ylim(2.65,-.5)
for x in [-3.125,3.125]:axes[0].plot([x,x],[1.83,2.17],color='black',lw=1.8)
axes[0].text(.99,.02,'Black ticks: +/- one expected descendant',ha='right',transform=axes[0].transAxes,fontsize=7.5)
for ext in ['png','pdf']:fig.savefig(OUT/('17_measurement_error.'+ext),dpi=180)
plt.close(fig);(OUT/'FIGURE_060_DATA.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(dict(figures=1,estimate_bindings=len(records),numeric_bindings=3*len(records),new_simulations=0)))
