"""Separate integer-weighted direct sums; imports no producer or model code."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import argparse,gzip,json,hashlib,time
F=Fraction

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repository',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();start=time.monotonic();checks=0
 def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
 def rational(q):return F(int(q['numerator']),int(q['denominator']))
 def expect(weights,numerators,den):return F(sum(w*x for w,x in zip(weights,numerators)),sum(weights)*den)
 sources=read(a.output/'SOURCE_BINDINGS.json')
 for name,digest in sources['files'].items():assert hashlib.sha256((a.repository/name).read_bytes()).hexdigest()==digest;checks+=1
 hh=[((s//4)%2)+((s//32)%2) for s in range(256)]
 weights={};nums={};den={};errors={};next_nums={};Ds={}
 for label in ('ZERO','HALF'):
  m=read(a.repository/('results/061/matrices/ACTIVE_'+label+'.json.gz'));v=read(a.repository/('results/061/vectors/ACTIVE_'+label+'.json.gz'));Ds[label]=m['denominator'];D=Ds[label]
  weights[label]=[int(x) for x in v['k']];errors[label]=rational(v['certificate']['total_variation_bound']);den[label]=14*D
  next_nums[label]=[sum(row[t]*hh[t] for t in range(256)) for row in m['numerators']]
  # Algebraically expanded numerator, distinct from the producer's Fraction matrix-reward route.
  nums[label]=[8*n-D-7*D*hh[s] for s,n in enumerate(next_nums[label])]
 cross={(w,r):expect(weights[w],nums[r],den[r]) for w in weights for r in nums}
 sz=cross['ZERO','ZERO'];sh=cross['HALF','HALF']
 direct=F(7,2)*(cross['HALF','HALF']-cross['HALF','ZERO']+cross['ZERO','HALF']-cross['ZERO','ZERO'])
 occupancy=F(7,2)*(cross['HALF','HALF']+cross['HALF','ZERO']-cross['ZERO','HALF']-cross['ZERO','ZERO'])
 dz=[F(n,den['ZERO']) for n in nums['ZERO']];dh=[F(n,den['HALF']) for n in nums['HALF']]
 zspan=max(dz)-min(dz);hspan=max(dh)-min(dh);fd=[7*(dh[i]-dz[i]) for i in range(256)];gd=[F(7,2)*(dh[i]+dz[i]) for i in range(256)]
 ez=errors['ZERO']*zspan;eh=errors['HALF']*hspan
 expected=[sz,sh,sh-sz,direct,occupancy,7*(sh-sz)]
 radii=[ez,eh,ez+eh,(errors['ZERO']+errors['HALF'])*(max(fd)-min(fd))/2,(errors['ZERO']+errors['HALF'])*(max(gd)-min(gd)),7*(ez+eh)]
 keys=('ACTIVE_ZERO|SELECTION_DRIFT','ACTIVE_HALF|SELECTION_DRIFT','HALF_MINUS_ZERO|SELECTION_DRIFT','RECURRENCE_DECOMPOSITION|DIRECT_TARGET_LAW','RECURRENCE_DECOMPOSITION|STATE_OCCUPANCY','RECURRENCE_DECOMPOSITION|TOTAL')
 q=read(a.output/'DECOMPOSITION.json');assert tuple(q)==keys;checks+=1
 for key,center,radius in zip(keys,expected,radii):
  v=q[key];lo,hi=center-radius,center+radius
  for field,value in [('center',center),('radius',radius),('lower',lo),('upper',hi)]:assert rational(v[field])==value;checks+=1
  assert v['sign']==('positive' if lo>0 else 'negative' if hi<0 else 'contains_zero');checks+=1
  assert v['sign_certified']==(lo>0 or hi<0);checks+=1
  assert F(Decimal(v['lower_percentage_points']))<=100*lo and F(Decimal(v['upper_percentage_points']))>=100*hi;checks+=1
 states=read(a.output/'STATE_TERMS.json.gz');assert len(states['states'])==256 and states['source_bindings_sha256']==hashlib.sha256((a.output/'SOURCE_BINDINGS.json').read_bytes()).hexdigest();checks+=1
 for s,row in enumerate(states['states']):
  pz=F(weights['ZERO'][s],sum(weights['ZERO']));ph=F(weights['HALF'][s],sum(weights['HALF']))
  vals=dict(h=F(hh[s],2),pi_zero=pz,pi_half=ph,next_h_zero=F(next_nums['ZERO'][s],2*Ds['ZERO']),next_h_half=F(next_nums['HALF'][s],2*Ds['HALF']),drift_zero=dz[s],drift_half=dh[s],direct_term=(pz+ph)*fd[s]/2,occupancy_term=(ph-pz)*gd[s])
  assert row['state']==s;checks+=1
  for field,value in vals.items():assert rational(row[field])==value;checks+=1
 residual={label:expect(weights[label],[n-Ds[label]*hh[s] for s,n in enumerate(next_nums[label])],2*Ds[label]) for label in weights}
 delta=expect(weights['HALF'],hh,2)-expect(weights['ZERO'],hh,2);correction=8*(residual['HALF']-residual['ZERO'])
 assert direct+occupancy==7*(sh-sz);checks+=1
 assert direct+occupancy-delta==correction;checks+=1
 identity=read(a.output/'IDENTITIES.json')
 for field,value in [('residual_projection_zero',residual['ZERO']),('residual_projection_half',residual['HALF']),('residual_correction',correction),('accepted061_center',delta)]:assert rational(identity[field])==value;checks+=1
 prior=read(a.repository/'results/061/OUTCOMES.json')['ACTIVE_HALF_MINUS_ZERO|H'];assert rational(prior['center'])==delta;checks+=1
 assert max(expected[-1]-radii[-1],rational(prior['lower']))<=min(expected[-1]+radii[-1],rational(prior['upper']));checks+=1
 assert identity['residual_correction_is_zero']==(correction==0);checks+=1
 result=dict(status='PASS',records=6,state_term_rows=256,exact_checks=checks,elapsed_seconds=time.monotonic()-start,producer_imports=0,scientific_operator_imports=0,transition_rows_reconstructed=0,stationary_solves=0,scope='Separately implemented integer-weighted direct sums, six centers/error radii, all derived state terms and exact identities; not an external reviewer or new empirical replication.')
 with (a.output/'AUDIT.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
if __name__=='__main__':main()
