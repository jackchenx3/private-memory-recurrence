"""Constructed fixtures and only the32 prospectively selected production rows."""
import unittest,math,itertools,ast,time
from fractions import Fraction
from decimal import Decimal
from common import *
from kernel import decode,encode,candidates,target_num,row,L,D,KERNELS,AUDIT_ROWS,support_checks
from numerics import solve,rounded_weights,certify,from_rational,ALPHA,CRITERION
from outcomes import calculate,KEYS,PRIMARY,reward_twice,assess
from reference_check import reference_row,independent_certificate

class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows={}
  for name in KERNELS:
   for state in AUDIT_ROWS:cls.rows[name,state]=row(state,name)
 def test_all_state_encodings(self):
  for s in range(256):self.assertEqual(encode(decode(s)),s)
  self.assertEqual(decode(255),(1,)*8);self.assertEqual(decode(36),(0,0,1,0,0,1,0,0))
 def test_denominator_and_literal_counts(self):
  value=1
  for W in range(8,17):
   for w in (1,2):den=W*(W-w);value=value*den//math.gcd(value,den);self.assertEqual(L%den,0)
  self.assertEqual(value,L);self.assertEqual(D,4*16*16*256*L);self.assertEqual(D.bit_length(),39);self.assertEqual(2*4*4*4*56*4,28672);self.assertEqual(28672*256*4,29360128)
  self.assertEqual(Fraction(1,983040)**2,Fraction(1,966367641600));self.assertEqual(256*Fraction(1,966367641600),ALPHA)
 def test_targets_and_joint_weights(self):
  for a in (0,1):
   self.assertEqual([target_num(a,e,'ZERO') for e in (0,1)],[2,2]);self.assertEqual(target_num(a,a,'HALF'),3);self.assertEqual(target_num(a,1-a,'HALF'),1)
  local=[(3 if x==0 else 1)*(3 if y==0 else 1) for x,y in itertools.product((0,1),repeat=2)];policy=[(15 if x==0 else 1)*(15 if y==0 else 1) for x,y in itertools.product((0,1),repeat=2)]
  self.assertEqual(local,[9,3,3,1]);self.assertEqual(policy,[225,15,15,1]);self.assertEqual(sum(local),16);self.assertEqual(sum(policy),256)
 def test_duplicate_slots_cache_and_donors(self):
  pool=candidates(0,0,(0,0),(0,0),(0,0),'ACTIVE');self.assertEqual(len(pool),8);self.assertEqual(pool,(0,)*8)
  s=encode((1,0,1,0,1,0,1,0));pool=candidates(s,0,(1,1),(1,0),(0,1),'ACTIVE');self.assertEqual(pool[:2],(5,2))
  for i in (0,1):
   g,c,h=decode(s)[3*i:3*i+3]
   for group in (1,2,3):record=pool[2*group+i];self.assertEqual((record>>1)&1,g);self.assertEqual((record>>2)&1,h)
  for e in (0,1):
   for proposals in itertools.product((0,1),repeat=3):
    tied=[x for x in proposals if int(x!=e)==min(int(v!=e) for v in proposals)];self.assertEqual(len(set(tied)),1)
 def test_policy_flips_and_survivor_order(self):
  first,second=5,2;b,e=1,0;base=first+8*second+64*b+128*e
  for m0,m1 in itertools.product((0,1),repeat=2):
   final=base^(4*m0)^(32*m1);bits=decode(final);self.assertEqual(bits[:2],(1,0));self.assertEqual(bits[3:5],(0,1));self.assertEqual(bits[2],1^m0);self.assertEqual(bits[5],m1);self.assertEqual(bits[6:],(b,e))
  self.assertNotEqual(first+8*second,second+8*first)
 def test_sequential_selection_all_weight_patterns(self):
  for weights in itertools.product((1,2),repeat=8):
   W=sum(weights);p=sum((Fraction(weights[j]*weights[k],W*(W-weights[j])) for j in range(8) for k in range(8) if j!=k),Fraction(0));self.assertEqual(p,1)
 def test32_rows_literal_independent_reconstruction(self):
  for (name,s),produced in self.rows.items():self.assertEqual(produced,reference_row(s,name),(name,s));self.assertEqual(sum(produced),D)
 def test_prespecified_row_symmetries(self):
  for (name,s),values in self.rows.items():
   for j,x in enumerate(values):
    self.assertEqual(x,self.rows[name,s^219][j^219])
    if name.startswith('NEUTRAL'):self.assertEqual(x,self.rows[name,s^36][j^36])
 def test_small_chain_fixed_solver_and_certificate(self):
  A=[[3,1],[2,2]];solution=solve(A,4);self.assertEqual(solution['precision_digits'],80);k=rounded_weights(solution);cert=certify(A,4,k,Fraction(1,2));self.assertTrue(cert['criterion_pass']);center=Fraction(k[0],sum(k));E=from_rational(cert['total_variation_bound']);self.assertLessEqual(abs(center-Fraction(2,3)),E)
  K,R,r,bound=independent_certificate(A,k,4);self.assertEqual(str(R),cert['R']);self.assertEqual(from_rational(cert['residual']),r)
  for i in range(101):
   cert=certify(A,4,[i,100-i],Fraction(1,2));center=Fraction(i,100);self.assertLessEqual(abs(center-Fraction(2,3)),from_rational(cert['total_variation_bound']))
  self.assertEqual(support_checks(A)['period'],1)
 def test_rounding_rejection_and_fixed_grid(self):
  s=dict(precision_digits=80,grid_digits=60,normalized_decimal=['0.0000000000000000000000000000000000000000000000000000000000005','0.0000000000000000000000000000000000000000000000000000000000015','1'])
  self.assertEqual(rounded_weights(s)[:2],[0,2]);s['normalized_decimal']=['-1e-90','1']
  with self.assertRaises(ValueError):rounded_weights(s)
  s['normalized_decimal']=['0','0']
  with self.assertRaises(ValueError):rounded_weights(s)
  self.assertFalse(certify([[3,1],[2,2]],4,[1,1],Fraction(1,2))['criterion_pass'])
 def test14_catalog_rewards_contrasts_and_outward_enclosures(self):
  # Supplied synthetic vectors; no production stationary solve or kernel.
  vectors={}
  for i,name in enumerate(KERNELS):
   k=[1]*256;k[36]+=i;K=sum(k)
   vectors[name]=dict(status='COMPUTED',k=[str(v) for v in k],certificate=dict(K=str(K),total_variation_bound={'numerator':'1','denominator':str(10**50)},criterion_pass=True))
  out=calculate(vectors);self.assertEqual(tuple(out),KEYS);self.assertEqual(len(out),14);self.assertEqual(list(KEYS),read('DESIGN_CHECK.json')['outcome_keys'])
  for key,v in out.items():
   self.assertLessEqual(Fraction(Decimal(v['lower_decimal'])),from_rational(v['lower']));self.assertGreaterEqual(Fraction(Decimal(v['upper_decimal'])),from_rational(v['upper']))
  self.assertEqual(from_rational(out[PRIMARY]['center']),from_rational(out['ACTIVE_HALF|H']['center'])-from_rational(out['ACTIVE_ZERO|H']['center']));self.assertEqual(from_rational(out['ACTIVE_ZERO_MINUS_HALF_SHARE|H']['center']),from_rational(out['ACTIVE_ZERO|H']['center'])-Fraction(1,2));self.assertEqual(assess(out)['decision'],'supports_positive')
  for s in range(256):
   bits=decode(s);self.assertEqual(reward_twice(s,'H'),bits[2]+bits[5]);self.assertEqual(reward_twice(s,'U'),2-(bits[0]^bits[7])-(bits[3]^bits[7]))
  vectors['ACTIVE_HALF']['certificate']['criterion_pass']=False;self.assertEqual(assess(calculate(vectors))['decision'],'sign_uncertified')
 def test_dependencies_and_python36_syntax(self):
  self.assertEqual(verify_references(),2)
  for f in P.glob('*.py'):ast.parse(f.read_text(),filename=f.name,feature_version=(3,6))
if __name__=='__main__':
 start=time.time();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));save('TEST_STATUS.json',dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),elapsed_seconds=time.time()-start,production_matrices=0,production_stationary_vectors=0,prespecified_rows_checked=32,independent_row_numerators=8192,constructed_two_state_vectors=101,simulation_paths=0,random_draws=0));raise SystemExit(0 if result.wasSuccessful() else 1)
