"""Separate integer-sum check of study063; does not import its producer."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
import argparse,gzip,hashlib,json,time

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repository',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    start=time.monotonic();n=0
    def check(ok):
        nonlocal n
        assert ok
        n+=1
    def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
    def q(x):return None if x is None else Fraction(int(x['numerator']),int(x['denominator']))
    def ds(x,mode=None):
        with localcontext() as c:
            c.prec=80
            if mode:c.rounding=mode
            return str(Decimal(x.numerator)/Decimal(x.denominator))
    bindings=load(a.output/'SOURCE_BINDINGS.json')
    for name,h in bindings['files'].items():check(hashlib.sha256((a.repository/name).read_bytes()).hexdigest()==h)
    saved=load(a.output/'OUTCOMES.json');flux=load(a.output/'FLUX_CERTIFICATES.json')
    is_absent=[not ((s>>2)&1) and not ((s>>5)&1) for s in range(256)]
    bstates=[i for i,flag in enumerate(is_absent) if flag];astates=[i for i,flag in enumerate(is_absent) if not flag]
    check(len(bstates)==64 and len(astates)==192)
    check(flux['absent_states']==bstates and flux['present_states']==astates)
    check(q(flux['alpha'])==Fraction(31,256) and q(flux['exact_mean_absent_spell'])==Fraction(256,31))
    expected={};primitive=[]
    for law in ['ACTIVE_ZERO','ACTIVE_HALF','NEUTRAL_ZERO','NEUTRAL_HALF']:
        matrix=load(a.repository/f'results/061/matrices/{law}.json.gz');vector=load(a.repository/f'results/061/vectors/{law}.json.gz')
        rows=matrix['numerators'];den=matrix['denominator'];weights=[int(x) for x in vector['k']];total=sum(weights)
        mass=sum(x for x,flag in zip(weights,is_absent) if flag)
        next_a=[sum(x for x,flag in zip(row,is_absent) if not flag) for row in rows]
        detail=flux['kernels'][law]
        check(detail['matrix_denominator']==den)
        for s in bstates:
            check(256*next_a[s]==31*den)
            check(detail['absent_to_present_numerators'][str(s)]==next_a[s])
        b=Fraction(mass,total);e=q(vector['certificate']['total_variation_bound'])
        lo=max(Fraction(0),b-e);hi=min(Fraction(1),b+e)
        expected[law+'|ABSENT_MASS']=(b,lo,hi)
        def duration(x):return Fraction(256*(x.denominator-x.numerator),31*x.numerator) if x>0 else None
        triple=(duration(b),duration(hi),duration(lo));primitive.append(triple)
        expected[law+'|PRESENT_SPELL']=triple
        incoming=Fraction(sum(weights[i]*next_a[i] for i in bstates),total*den)
        outgoing=Fraction(sum(weights[i]*(sum(rows[i])-next_a[i]) for i in astates),total*den)
        projection=Fraction(sum(weights[i]*next_a[i] for i in range(256))-(total-mass)*den,total*den)
        check(incoming-outgoing==projection)
        for field,want in [('event_mass_center',b),('accepted_total_variation_bound',e),('entry_flux_center',incoming),('exit_flux_center',outgoing),('residual_projection',projection)]:check(q(detail[field])==want)
        check(detail['residual_is_zero']==(projection==0) and detail['flux_identity_exact'])
        check(detail['strict_event_mass_enclosure']==(0<lo<=hi<1))
        check(detail['residual_decimal']==ds(projection))
    # Columns are ACTIVE_ZERO, ACTIVE_HALF, NEUTRAL_ZERO, NEUTRAL_HALF.
    rows=[('ACTIVE_HALF_MINUS_ZERO',[-1,1,0,0]),('NEUTRAL_HALF_MINUS_ZERO',[0,0,-1,1]),
          ('ACTIVE_MINUS_NEUTRAL_ZERO',[1,0,-1,0]),('ACTIVE_MINUS_NEUTRAL_HALF',[0,1,0,-1]),
          ('RECURRENCE_BY_EXPRESSION',[-1,1,1,-1])]
    for label,coeff in rows:
        values=[]
        for which in range(3):
            terms=[]
            for i,c in enumerate(coeff):
                if not c:continue
                index=which if which==0 or c>0 else (2 if which==1 else 1)
                terms.append(None if primitive[i][index] is None else c*primitive[i][index])
            values.append(sum(terms,Fraction(0)) if all(x is not None for x in terms) else None)
        expected[label+'|PRESENT_SPELL']=tuple(values)
    check(set(expected)==set(saved) and len(saved)==13)
    for name,(center,lower,upper) in expected.items():
        actual=saved[name]
        for field,want in [('center',center),('lower',lower),('upper',upper)]:check(q(actual[field])==want)
        finite=all(x is not None for x in (center,lower,upper));check(actual['finite_enclosure']==finite)
        certifiable=finite
        if name.endswith('|PRESENT_SPELL') and name.split('|')[0] in flux['kernels']:
            certifiable=certifiable and flux['kernels'][name.split('|')[0]]['strict_event_mass_enclosure']
        sign=('positive' if lower>0 else 'negative' if upper<0 else 'exact_zero' if lower==upper==0 else 'uncertified') if certifiable else 'uncertified'
        check(actual['sign']==sign and actual['sign_certified']==(sign!='uncertified'))
        for field,val,mode in [('center_decimal',center,None),('lower_decimal',lower,ROUND_FLOOR),('upper_decimal',upper,ROUND_CEILING)]:
            check(actual[field]==(ds(val,mode) if val is not None else None))
        if finite:
            check(Fraction(Decimal(actual['lower_decimal']))<=lower<=center<=upper<=Fraction(Decimal(actual['upper_decimal'])))
        if name.endswith('|ABSENT_MASS'):
            for field,val,mode in [('center_percentage_points',center,None),('lower_percentage_points',lower,ROUND_FLOOR),('upper_percentage_points',upper,ROUND_CEILING)]:check(actual[field]==ds(100*val,mode))
    v=lambda label:expected[label+'|PRESENT_SPELL'][0]
    if all(v(label) is not None for label,_ in rows):
        check(v('RECURRENCE_BY_EXPRESSION')==v('ACTIVE_HALF_MINUS_ZERO')-v('NEUTRAL_HALF_MINUS_ZERO'))
        check(v('RECURRENCE_BY_EXPRESSION')==v('ACTIVE_MINUS_NEUTRAL_HALF')-v('ACTIVE_MINUS_NEUTRAL_ZERO'))
    check(flux['absent_row_sums_checked']==256 and flux['contrast_centers_identity_exact'])
    receipt={'status':'PASS','records':13,'exact_checks':n,'saved_absent_row_sums_checked':256,
             'elapsed_seconds':time.monotonic()-start,'producer_imports':0,'scientific_operator_imports':0,
             'new_transition_rows':0,'stationary_solves':0,'hitting_time_solves':0,'population_paths':0,
             'scope':'Separate integer-sum implementation of event probabilities,duration bounds,13records,256saved row sums and exact flux corrections;not external review or empirical replication.'}
    with (a.output/'AUDIT.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
