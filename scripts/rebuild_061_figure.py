"""Rebuild figure18 solely from the saved exact stationary records."""
from pathlib import Path
from fractions import Fraction
import argparse,hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
KERNELS=('ACTIVE_ZERO','ACTIVE_HALF','NEUTRAL_ZERO','NEUTRAL_HALF')
def value(x):return float(Fraction(int(x['numerator']),int(x['denominator'])))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=ROOT/'_rebuilt/figures');args=ap.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    source=ROOT/'results/061/OUTCOMES.json';records=json.loads(source.read_text());bindings=[]
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(8.8,4.8));fig.subplots_adjust(left=.16,right=.985,top=.75,bottom=.27,wspace=.75)
    labels=['Active / ZERO','Active / HALF','Neutral / ZERO','Neutral / HALF']
    for ax,reward,title,limits in zip(axes,('H','U'),('A  H frequency','B  Population accuracy'),((49.90,50.64),(67.05,69.02))):
        for i,kernel in enumerate(KERNELS):
            key=kernel+'|'+reward;q=records[key];center,lo,hi=[100*value(q[k]) for k in ('center','lower','upper')]
            color='#146b83' if kernel.startswith('ACTIVE') else '#777777'
            ax.hlines(i,lo,hi,color=color,lw=2)
            ax.scatter(center,i,s=45,c=color,zorder=3)
            ax.annotate(f'{center:.6f}%',(center,i),xytext=(0,-18),textcoords='offset points',ha='center',fontsize=9,color=color)
            bindings.append({'figure':'18_stationary_policy','study':'061','key':key,'kind':'plotted_mean','center':q['center'],'lower':q['lower'],'upper':q['upper'],'scale':100})
        ax.set_yticks(range(4));ax.set_yticklabels(labels);ax.set_ylim(3.6,-.5);ax.set_xlim(*limits)
        ax.set_title(title,loc='left',pad=16);ax.set_xlabel('Percent (magnified axis)');ax.grid(axis='x',color='#dddddd',alpha=.7);ax.set_axisbelow(True)
        ax.spines[['right','top']].set_visible(False)
    axes[0].axvline(50,color='#aaaaaa',ls='--',lw=1,zorder=0)
    annotation_keys=('ACTIVE_HALF_MINUS_ZERO|H','ACTIVE_MINUS_NEUTRAL_ZERO|U','ACTIVE_MINUS_NEUTRAL_HALF|U')
    nums=[100*value(records[k]['center']) for k in annotation_keys]
    fig.text(.16,.10,f'Primary H: HALF - ZERO\n{nums[0]:+.6f} pp',color='#146b83',fontsize=10)
    fig.text(.59,.10,f'Active - neutral U:\nZERO {nums[1]:+.6f} pp; HALF {nums[2]:+.6f} pp',fontsize=9,va='baseline')
    fig.suptitle('Supplied memory in a separate two-individual / one-bit model',fontsize=12,y=.98)
    fig.text(.5,.91,'Exact saved kernels; symmetric policy switching at 1/16',ha='center',fontsize=9,color='#555555')
    fig.text(.5,.035,'Certified numerical enclosures are narrower than the markers. No statistical confidence intervals.',ha='center',fontsize=9,color='#555555')
    for key in annotation_keys:
        bindings.append({'figure':'18_stationary_policy','study':'061','key':key,'kind':'text_annotation','center':records[key]['center'],'scale':100})
    fig.savefig(args.output_dir/'18_stationary_policy.png',dpi=180,facecolor='white')
    fig.savefig(args.output_dir/'18_stationary_policy.pdf',metadata={'CreationDate':None,'ModDate':None});plt.close(fig)
    (args.output_dir/'FIGURE_061_DATA.json').write_text(json.dumps({'source':'results/061/OUTCOMES.json','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'uncertainty':'certified numerical enclosures','bindings':bindings},indent=2)+'\n')
    print(json.dumps({'figure':'18_stationary_policy','source_records':len(bindings),'numeric_bindings':27,'new_scientific_execution':False}))
if __name__=='__main__':main()
