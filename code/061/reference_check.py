"""Standalone independent reconstruction; imports no producer kernel/solver/outcome code.
The supervisor may run this checker or implement its own. A producer execution of
this script is not itself a claim that supervisor review has occurred.
"""
import itertools,json,gzip,pathlib,math,sys
from fractions import Fraction
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
ROWS=(0,36,85,113,142,170,219,255)
NAMES=('ACTIVE_ZERO','ACTIVE_HALF','NEUTRAL_ZERO','NEUTRAL_HALF')
DENOMINATOR=377864847360

def reference_row(state,name):
 g=[state%2,(state//8)%2];cache=[(state//2)%2,(state//16)%2];policy=[(state//4)%2,(state//32)%2];history=(state//64)%2;current=(state//128)%2;answer=[0]*256
 for target in range(2):
  target_weight=2 if name.endswith('ZERO') else 3 if target==history else 1
  for draws in itertools.product((0,1),repeat=6):
   probes=[cache[i] if name.startswith('ACTIVE') and policy[i] else draws[i] for i in range(2)];scouts=draws[2:4];flips=draws[4:6]
   options=[(g[i],cache[i],policy[i]) for i in range(2)]
   options.extend((probes[i],g[i],policy[i]) for i in range(2));options.extend((scouts[i],g[i],policy[i]) for i in range(2))
   for i in range(2):
    donor=min((g[i],probes[i],scouts[i]),key=lambda value:int(value!=target));options.append((donor^flips[i],g[i],policy[i]))
   weights=[1+int(o[0]==target) for o in options];total=sum(weights);local_weight=(1 if flips[0] else 3)*(1 if flips[1] else 3)
   for first in range(8):
    for second in range(8):
     if first==second:continue
     div=4*16*16*256*total*(total-weights[first]);assert DENOMINATOR%div==0
     multiplier=target_weight*local_weight*weights[first]*weights[second]*(DENOMINATOR//div)
     for m0,m1 in itertools.product((0,1),repeat=2):
      x,y=options[first],options[second];destination=x[0]+2*x[1]+4*(x[2]^m0)+8*y[0]+16*y[1]+32*(y[2]^m1)+64*current+128*target
      answer[destination]+=multiplier*(1 if m0 else 15)*(1 if m1 else 15)
 return answer

def fraction(q):return Fraction(int(q['numerator']),int(q['denominator']))
def encode_fraction(q):return dict(numerator=str(q.numerator),denominator=str(q.denominator))
def load(path):
 if path.suffix=='.gz':
  with gzip.open(str(path),'rt') as f:return json.load(f)
 return json.loads(path.read_text())
def independent_certificate(A,k,D):
 K=sum(k);assert min(k)>=0 and K>0
 residual=sum(abs(sum(A[i][j]*k[i] for i in range(len(k)))-D*k[j]) for j in range(len(k)));r=Fraction(residual,K*D);bound=min(Fraction(1),r*3774873600)
 return K,residual,r,bound

def main(directory):
 root=pathlib.Path(directory);numbers={};row_checks=0;certs=[];unavailable=[];audited={}
 for name in NAMES:
  data=load(root/'matrices'/(name+'.json.gz'));A=data['numerators'];assert data['denominator']==DENOMINATOR and len(A)==256
  assert all(len(r)==256 and all(type(x)==int and x>=0 for x in r) and sum(r)==DENOMINATOR for r in A)
  for i in range(256):
   for j in range(256):
    assert A[i][j]==A[i^219][j^219]
    if name.startswith('NEUTRAL'):assert A[i][j]==A[i^36][j^36]
  audited[name]={}
  for i in ROWS:
   expected=reference_row(i,name);assert expected==A[i],(name,i);audited[name][str(i)]=expected;row_checks+=1
  v=load(root/'vectors'/(name+'.json.gz'))
  if v['status']=='REJECTED':unavailable.append(name);continue
  assert v['solution']['precision_digits']==80 and v['solution']['grid_digits']==60
  k=[int(x) for x in v['k']];assert len(k)==256;K,R,r,E=independent_certificate(A,k,DENOMINATOR);c=v['certificate'];assert str(K)==c['K'] and str(R)==c['R'] and fraction(c['residual'])==r and fraction(c['total_variation_bound'])==E and c['criterion_pass']==(r<=Fraction(1,10**30));assert fraction(c['alpha'])==Fraction(1,3774873600) and fraction(c['criterion'])==Fraction(1,10**30)
  # Verify the saved fixed-grid rounding, without solving stationarity again.
  with localcontext() as ctx:
   ctx.prec=80
   from decimal import ROUND_HALF_EVEN
   xs=[Decimal(x) for x in v['solution']['normalized_decimal']];assert all(x>=0 for x in xs)
   assert [int((x*(Decimal(10)**60)).to_integral_value(rounding=ROUND_HALF_EVEN)) for x in xs]==k
  certs.append(dict(kernel=name,criterion_pass=c['criterion_pass'],R=str(R)))
  for reward in ('H','U'):
   numerator=0
   for s,x in enumerate(k):
    g0=s%2;g1=(s//8)%2;h0=(s//4)%2;h1=(s//32)%2;b=(s//128)%2
    twice=h0+h1 if reward=='H' else int(g0==b)+int(g1==b);numerator+=x*twice
   center=Fraction(numerator,2*K);numbers[name+'|'+reward]=(center,E,c['criterion_pass'])
   if name.startswith('NEUTRAL') and reward=='H':assert center-E<=Fraction(1,2)<=center+E
 expected={}
 for key,(center,E,ok) in numbers.items():expected[key]=(center,E,max(Fraction(0),center-E),min(Fraction(1),center+E),ok)
 contrasts=[('ACTIVE_HALF_MINUS_ZERO|H','ACTIVE_HALF|H','ACTIVE_ZERO|H'),('ACTIVE_ZERO_MINUS_HALF_SHARE|H','ACTIVE_ZERO|H',None),('ACTIVE_HALF_MINUS_HALF_SHARE|H','ACTIVE_HALF|H',None),('ACTIVE_HALF_MINUS_ZERO|U','ACTIVE_HALF|U','ACTIVE_ZERO|U'),('ACTIVE_MINUS_NEUTRAL_ZERO|U','ACTIVE_ZERO|U','NEUTRAL_ZERO|U'),('ACTIVE_MINUS_NEUTRAL_HALF|U','ACTIVE_HALF|U','NEUTRAL_HALF|U')]
 for key,a,b in contrasts:
  if a not in numbers or b is not None and b not in numbers:continue
  x,E,ok=numbers[a];y,F,other=(Fraction(1,2),Fraction(0),True) if b is None else numbers[b];center=x-y;radius=E+F;expected[key]=(center,radius,center-radius,center+radius,ok and other)
 saved=load(root/'OUTCOMES.json');assert set(saved)=={name+'|'+reward for name in NAMES for reward in ('H','U')}|{q[0] for q in contrasts}
 for key,q in saved.items():
  if key not in expected:assert q['status']=='UNAVAILABLE';continue
  center,radius,lo,hi,ok=expected[key]
  for field,x in [('center',center),('radius',radius),('lower',lo),('upper',hi)]:assert fraction(q[field])==x,(key,field)
  assert Fraction(Decimal(q['lower_decimal']))<=lo and Fraction(Decimal(q['upper_decimal']))>=hi
  assert Fraction(Decimal(q['lower_percentage_points']))<=lo*100 and Fraction(Decimal(q['upper_percentage_points']))>=hi*100
  assert q['status']==('CERTIFIED' if ok else 'NUMERICAL_CRITERION_FAILED')
  assert q['sign']==('uncertified' if not ok else 'positive' if lo>0 else 'negative' if hi<0 else 'contains_zero')
 result=dict(status='PASS' if not unavailable else 'PARTIAL_REJECTED_VECTORS',audit_rows=row_checks,audit_numerators=row_checks*256,certificates=certs,rejected_vectors=unavailable,outcomes_checked=len(expected),stationary_solves=0,new_kernel_rows=row_checks,method='Standalone implementation; no producer kernel/solver/outcome imports')
 (root/'INDEPENDENT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
 with gzip.open(str(root/'AUDITED_ROWS.json.gz'),'wt') as f:json.dump(audited,f,separators=(',',':'))
 print(json.dumps(result))
if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parent)
