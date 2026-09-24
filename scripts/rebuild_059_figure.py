from pathlib import Path
import argparse,json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];e=json.loads((R/'results/059/ESTIMATES.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,default=R/'_rebuilt/figures');OUT=parser.parse_args().output_dir;OUT.mkdir(parents=True,exist_ok=True)
fig,axes=plt.subplots(2,1,figsize=(6.6,6.8),constrained_layout=True)
groups=['PULSE_MINUS_STAY','CONT_MINUS_STAY','PULSE_MINUS_CONT'];labels=['Pulse minus unchanged H','Continuous F minus unchanged H','Pulse minus continuous F'];bindings=[]
for ax,m,title in zip(axes,['U40','D40'],['Terminal population accuracy','Terminal founder representation']):
 for i,g in enumerate(groups):
  key=g+'|'+m;q=e[key];lo,hi=[100*x for x in q['ci95']];mean=100*q['mean'];color='#a34e16' if m=='U40' and i==0 else '#16688e'
  ax.plot([lo,hi],[i,i],color=color,lw=2);ax.plot(mean,i,'o',color=color,ms=5);bindings.append(dict(study='059',figure='16_transient_pulse',key=key,mean_pp=mean,ci95_pp=[lo,hi]))
 ax.axvline(0,color='gray',lw=.8);ax.set_yticks(range(3),labels,fontsize=8.5);ax.invert_yaxis();ax.set_title(title,fontsize=11);ax.set_xlabel('Percentage points; pointwise 95% intervals',fontsize=9);ax.tick_params(axis='x',labelsize=9)
 if m=='U40':
  ax.plot([100/1024]*2,[-.2,.2],color='black',lw=1.8);ax.text(.98,.03,'Black tick: one expected matching bit',transform=ax.transAxes,ha='right',fontsize=8);ax.set_ylim(2.5,-.5)
fig.savefig(OUT/'16_transient_pulse.png',dpi=180);fig.savefig(OUT/'16_transient_pulse.pdf');plt.close(fig)
(OUT/'FIGURE_059_DATA.json').write_text(json.dumps(bindings,indent=2)+'\n')
print(json.dumps(dict(status='PASS',figure_bindings=len(bindings))))
