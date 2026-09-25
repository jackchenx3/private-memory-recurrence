"""Exactly14 fixed rational centers/enclosures; numerical rather than sampling error."""
from fractions import Fraction
from decimal import ROUND_FLOOR,ROUND_CEILING
from numerics import rational,from_rational,decimal_string
KERNELS=('ACTIVE_ZERO','ACTIVE_HALF','NEUTRAL_ZERO','NEUTRAL_HALF')
PRIMARY='ACTIVE_HALF_MINUS_ZERO|H'
CONTRASTS=(('ACTIVE_HALF_MINUS_ZERO|H','ACTIVE_HALF|H','ACTIVE_ZERO|H'),('ACTIVE_ZERO_MINUS_HALF_SHARE|H','ACTIVE_ZERO|H',None),('ACTIVE_HALF_MINUS_HALF_SHARE|H','ACTIVE_HALF|H',None),('ACTIVE_HALF_MINUS_ZERO|U','ACTIVE_HALF|U','ACTIVE_ZERO|U'),('ACTIVE_MINUS_NEUTRAL_ZERO|U','ACTIVE_ZERO|U','NEUTRAL_ZERO|U'),('ACTIVE_MINUS_NEUTRAL_HALF|U','ACTIVE_HALF|U','NEUTRAL_HALF|U'))
KEYS=tuple(k+'|'+r for k in KERNELS for r in ('H','U'))+tuple(q[0] for q in CONTRASTS)

def reward_twice(s,kind):
 if kind=='H':return ((s>>2)&1)+((s>>5)&1)
 assert kind=='U';b=(s>>7)&1;return 2-((s&1)^b)-(((s>>3)&1)^b)

def make_record(center,radius,certified,primitive=False):
 lo,hi=center-radius,center+radius
 if primitive:lo=max(Fraction(0),lo);hi=min(Fraction(1),hi)
 return dict(status='CERTIFIED' if certified else 'NUMERICAL_CRITERION_FAILED',center=rational(center),radius=rational(radius),lower=rational(lo),upper=rational(hi),center_decimal=decimal_string(center),lower_decimal=decimal_string(lo,ROUND_FLOOR),upper_decimal=decimal_string(hi,ROUND_CEILING),center_percentage_points=decimal_string(center*100),lower_percentage_points=decimal_string(lo*100,ROUND_FLOOR),upper_percentage_points=decimal_string(hi*100,ROUND_CEILING),sign='uncertified' if not certified else 'positive' if lo>0 else 'negative' if hi<0 else 'contains_zero')

def calculate(vectors):
 out={};numeric={}
 for name in KERNELS:
  v=vectors[name]
  for kind in ('H','U'):
   key=name+'|'+kind
   if v['status']=='REJECTED':out[key]=dict(status='UNAVAILABLE',reason=v['reason'],sign='uncertified');continue
   k=[int(x) for x in v['k']];K=int(v['certificate']['K']);assert sum(k)==K;center=Fraction(sum(x*reward_twice(s,kind) for s,x in enumerate(k)),2*K);radius=from_rational(v['certificate']['total_variation_bound']);passed=v['certificate']['criterion_pass'];numeric[key]=(center,radius,passed);out[key]=make_record(center,radius,passed,True)
 for key,a,b in CONTRASTS:
  if a not in numeric or b is not None and b not in numeric:out[key]=dict(status='UNAVAILABLE',reason='Component stationary vector rejected',sign='uncertified');continue
  x,E,passed=numeric[a];y,F,other=(Fraction(1,2),Fraction(0),True) if b is None else numeric[b];out[key]=make_record(x-y,E+F,passed and other)
 assert tuple(out)==KEYS
 return out

def assess(records):
 primary=records[PRIMARY]
 return dict(primary=PRIMARY,prediction='positive',decision='supports_positive' if primary['sign']=='positive' else 'contradicts_positive' if primary['sign']=='negative' else 'sign_uncertified',uncertainty='exact residual-based numerical error enclosure; not a confidence interval',primary_record=primary)
