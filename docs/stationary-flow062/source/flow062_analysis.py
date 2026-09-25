"""Fixed exact analysis of saved study061kernels; no generation or solve."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
import argparse,datetime,gzip,hashlib,json,subprocess,time,traceback

BASE='651c4289b1ac34efb30d1a81560e88cd74b1609f'
TASK_SHA='4dab6fac94d6855db52cbe9b7c27f5d158031f19c8da420d580e74975ee0cb48'
PRIMARY='RECURRENCE_DECOMPOSITION|DIRECT_TARGET_LAW'
KEYS=('ACTIVE_ZERO|SELECTION_DRIFT','ACTIVE_HALF|SELECTION_DRIFT','HALF_MINUS_ZERO|SELECTION_DRIFT',PRIMARY,'RECURRENCE_DECOMPOSITION|STATE_OCCUPANCY','RECURRENCE_DECOMPOSITION|TOTAL')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def rat(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def unrat(x):return F(int(x['numerator']),int(x['denominator']))
def decimal(x,rounding=None):
 with localcontext() as ctx:
  ctx.prec=80
  if rounding is not None:ctx.rounding=rounding
  return str(Decimal(x.numerator)/Decimal(x.denominator))
def record(center,radius,units):
 lo,hi=center-radius,center+radius
 return dict(center=rat(center),radius=rat(radius),lower=rat(lo),upper=rat(hi),center_decimal=decimal(center),center_percentage_points=decimal(100*center),lower_percentage_points=decimal(100*lo,ROUND_FLOOR),upper_percentage_points=decimal(100*hi,ROUND_CEILING),units=units,sign='positive' if lo>0 else 'negative' if hi<0 else 'contains_zero',sign_certified=lo>0 or hi<0,uncertainty='Exact numerical enclosure from accepted total-variation bounds; not a statistical confidence interval')
def dot(p,q):return sum((a*b for a,b in zip(p,q)),F(0))
def span(x):return max(x)-min(x)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repository',type=Path,required=True);ap.add_argument('--task',type=Path,required=True);ap.add_argument('--fixture',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 start=time.monotonic();out=args.output;out.mkdir(parents=True,exist_ok=False)
 def save(name,value):
  if time.monotonic()-start>120:raise TimeoutError('Fixed two-minute analysis budget exceeded')
  data=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
  if name.endswith('.gz'):data=gzip.compress(data,compresslevel=6,mtime=0)
  if sum(p.stat().st_size for p in out.rglob('*') if p.is_file())+len(data)>8*1024*1024-16384:raise RuntimeError('Fixed8MiB output budget exceeded')
  with (out/name).open('xb') as f:f.write(data)
 try:
  assert sha(args.task)==TASK_SHA
  fixture=read(args.fixture);assert fixture['status']=='PASS' and fixture['exact_checks']==72 and fixture['study061_files_read']==0
  # Small sign/display fixtures, without touching any production quantity.
  for c,r,want in [(F(2),F(1),'positive'),(F(-2),F(1),'negative'),(F(0),F(1),'contains_zero')]:
   q=record(c,r,'constructed');assert q['sign']==want
   assert F(Decimal(q['lower_percentage_points']))<=100*(c-r) and F(Decimal(q['upper_percentage_points']))>=100*(c+r)
  manifest_text=subprocess.check_output(['git','show',BASE+':SHA256SUMS'],cwd=args.repository,text=True)
  manifest={name:h for h,name in (line.split('  ',1) for line in manifest_text.splitlines())}
  names=['results/061/'+folder+'/'+law+'.json.gz' for law in ('ACTIVE_ZERO','ACTIVE_HALF') for folder in ('matrices','vectors')]+['results/061/OUTCOMES.json','provenance/061_CERTIFICATES_CHECK.json']
  bindings={}
  for name in names:
   path=args.repository/name;actual=sha(path);assert actual==manifest[name],name;bindings[name]=actual
  assert read(args.repository/'provenance/061_CERTIFICATES_CHECK.json')['status']=='PASS'
  save('SOURCE_BINDINGS.json',dict(baseline_commit=BASE,files=bindings,task_sha256=TASK_SHA,prospective_fixture_sha256=sha(args.fixture),analysis_source_sha256=sha(Path(__file__)),scientific_code_imported=False))
  h=[F(((s>>2)&1)+((s>>5)&1),2) for s in range(256)];mu=F(1,16);beta=1-2*mu
  p={};d={};ph={};E={}
  for law in ('ZERO','HALF'):
   name='ACTIVE_'+law;m=read(args.repository/('results/061/matrices/'+name+'.json.gz'));v=read(args.repository/('results/061/vectors/'+name+'.json.gz'))
   A=m['numerators'];D=m['denominator'];assert D==377864847360 and len(A)==256 and all(len(row)==256 for row in A)
   k=list(map(int,v['k']));K=sum(k);assert v['status']=='COMPUTED' and len(k)==256 and K==int(v['certificate']['K']) and all(x>=0 for x in k)
   E[law]=unrat(v['certificate']['total_variation_bound']);assert v['certificate']['criterion_pass'] and E[law]>=0
   p[law]=[F(x,K) for x in k]
   ph[law]=[sum((n*reward for n,reward in zip(row,h)),F(0))/D for row in A]
   selected=[(x-mu)/beta for x in ph[law]];assert all(0<=x<=1 for x in selected)
   d[law]=[x-y for x,y in zip(selected,h)]
  sz=dot(p['ZERO'],d['ZERO']);sh=dot(p['HALF'],d['HALF'])
  f=[7*(a-b) for a,b in zip(d['HALF'],d['ZERO'])];g=[7*(a+b)/2 for a,b in zip(d['HALF'],d['ZERO'])]
  avg=[(a+b)/2 for a,b in zip(p['HALF'],p['ZERO'])];change=[a-b for a,b in zip(p['HALF'],p['ZERO'])]
  C=dot(avg,f);O=dot(change,g);T=C+O
  ez=E['ZERO']*span(d['ZERO']);eh=E['HALF']*span(d['HALF'])
  centers=[sz,sh,sh-sz,C,O,T];radii=[ez,eh,ez+eh,(E['HALF']+E['ZERO'])*span(f)/2,(E['HALF']+E['ZERO'])*span(g),7*(ez+eh)]
  records={key:record(value,radius,'H-frequency fraction per update before policy switching' if i<3 else 'stationary H-frequency fraction') for i,(key,value,radius) in enumerate(zip(KEYS,centers,radii))}
  save('DECOMPOSITION.json',records)
  rz=dot(p['ZERO'],[a-b for a,b in zip(ph['ZERO'],h)]);rh=dot(p['HALF'],[a-b for a,b in zip(ph['HALF'],h)])
  delta=dot(p['HALF'],h)-dot(p['ZERO'],h);correction=8*(rh-rz)
  assert T==7*(sh-sz) and T-delta==correction
  old=read(args.repository/'results/061/OUTCOMES.json')['ACTIVE_HALF_MINUS_ZERO|H']
  assert delta==unrat(old['center'])
  lo,hi=T-radii[-1],T+radii[-1];oldlo,oldhi=unrat(old['lower']),unrat(old['upper']);assert max(lo,oldlo)<=min(hi,oldhi)
  save('IDENTITIES.json',dict(status='PASS',symmetric_decomposition_exact=True,balance_residual_correction_exact=True,residual_projection_zero=rat(rz),residual_projection_half=rat(rh),residual_correction=rat(correction),residual_correction_decimal=decimal(correction),residual_correction_is_zero=correction==0,accepted061_center=rat(delta),accepted061_lower=old['lower'],accepted061_upper=old['upper'],total_enclosure_overlaps_accepted061=True,error_bounds={law:rat(q) for law,q in E.items()},reward_spans={name:rat(span(values)) for name,values in [('d_ZERO',d['ZERO']),('d_HALF',d['HALF']),('f_direct',f),('g_occupancy',g)]},formula='T - saved061Hcontrast = 8(r_HALF-r_ZERO); exact rational correction is retained'))
  rows=[]
  for s in range(256):
   rows.append(dict(state=s,h=rat(h[s]),pi_zero=rat(p['ZERO'][s]),pi_half=rat(p['HALF'][s]),next_h_zero=rat(ph['ZERO'][s]),next_h_half=rat(ph['HALF'][s]),drift_zero=rat(d['ZERO'][s]),drift_half=rat(d['HALF'][s]),direct_term=rat(avg[s]*f[s]),occupancy_term=rat(change[s]*g[s])))
  save('STATE_TERMS.json.gz',dict(source_bindings_sha256=sha(out/'SOURCE_BINDINGS.json'),states=rows,scope='Derived state terms, not regenerated transition rows'))
  save('EXECUTION.json',dict(status='COMPLETED_AUDIT_PENDING',started_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,records=6,state_term_rows=256,new_transition_rows=0,stationary_solves=0,population_paths=0,random_draws=0,primary=PRIMARY,primary_sign=records[PRIMARY]['sign'],prospective_fixture_checks_reused=72,sign_display_fixtures=3))
  print(json.dumps({k:dict(pp=q['center_percentage_points'],sign=q['sign'],radius=decimal(unrat(q['radius']))) for k,q in records.items()},indent=2))
 except BaseException as error:
  (out/'FAILURE.json').write_text(json.dumps(dict(error=str(error),traceback=traceback.format_exc(),automatic_retry=False),indent=2)+'\n');raise
if __name__=='__main__':main()
