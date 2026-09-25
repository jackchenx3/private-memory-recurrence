"""Fixed saved-kernel analysis: no kernel generation, solves, or trajectories."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import argparse, datetime, gzip, hashlib, json, subprocess, time, traceback

BASE='651c4289b1ac34efb30d1a81560e88cd74b1609f'
TASK_SHA='878dfc33373b9d8ca5734b86c3d81d75315650bc711323c685e20cdcf52f2103'
LAWS=('ACTIVE_ZERO','ACTIVE_HALF','NEUTRAL_ZERO','NEUTRAL_HALF')
PRIMARY='RECURRENCE_BY_EXPRESSION|PRESENT_SPELL'
ALPHA=F(31,256)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def rat(x):return None if x is None else {'numerator':str(x.numerator),'denominator':str(x.denominator)}
def unrat(x):return F(int(x['numerator']),int(x['denominator']))
def dec(x,rounding=None):
    if x is None:return None
    with localcontext() as ctx:
        ctx.prec=80
        if rounding is not None:ctx.rounding=rounding
        return str(Decimal(x.numerator)/Decimal(x.denominator))
def record(c,lo,hi,units,certifiable=True):
    finite=all(x is not None for x in (c,lo,hi))
    if finite:assert lo<=c<=hi
    sign=('positive' if lo>0 else 'negative' if hi<0 else 'exact_zero' if lo==hi==0 else 'uncertified') if finite and certifiable else 'uncertified'
    q={'center':rat(c),'lower':rat(lo),'upper':rat(hi),'center_decimal':dec(c),
       'lower_decimal':dec(lo,ROUND_FLOOR),'upper_decimal':dec(hi,ROUND_CEILING),
       'units':units,'sign':sign,'finite_enclosure':finite,'sign_certified':sign!='uncertified',
       'uncertainty':'Numerical enclosure from accepted total-variation bounds; not a confidence interval.'}
    if units=='stationary probability fraction':
        q.update(center_percentage_points=dec(100*c),lower_percentage_points=dec(100*lo,ROUND_FLOOR),upper_percentage_points=dec(100*hi,ROUND_CEILING))
    if not finite:q['limitation']='Null lower/upper means negative/positive infinity respectively; null center is unavailable. Strict event-mass certification failed.'
    return q

def main():
    ap=argparse.ArgumentParser()
    for name in ('repository','task','fixture','output'):ap.add_argument('--'+name,type=Path,required=True)
    a=ap.parse_args();start=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    out=a.output;out.mkdir(parents=True,exist_ok=False)
    def save(name,value):
        data=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
        if time.monotonic()-start>120:raise TimeoutError('Fixed two-minute analysis budget exceeded')
        if sum(p.stat().st_size for p in out.rglob('*') if p.is_file())+len(data)>8*1024*1024-16384:raise RuntimeError('Fixed8MiB output budget exceeded')
        with (out/name).open('xb') as f:f.write(data)
    try:
        assert sha(a.task)==TASK_SHA
        fixture=read(a.fixture)
        assert fixture['status']=='PASS' and fixture['exact_checks']==144 and fixture['study061_files_read']==0
        manifest={name:h for h,name in (line.split('  ',1) for line in subprocess.check_output(['git','show',BASE+':SHA256SUMS'],cwd=a.repository,text=True).splitlines())}
        names=['results/061/'+folder+'/'+law+'.json.gz' for law in LAWS for folder in ('matrices','vectors')]+['provenance/061_CERTIFICATES_CHECK.json']
        bindings={}
        for name in names:
            actual=sha(a.repository/name);assert actual==manifest[name],name;bindings[name]=actual
        assert read(a.repository/'provenance/061_CERTIFICATES_CHECK.json')['status']=='PASS'
        save('SOURCE_BINDINGS.json',{'baseline_commit':BASE,'files':bindings,'task_sha256':TASK_SHA,
             'prospective_fixture_sha256':sha(a.fixture),'analysis_source_sha256':sha(Path(__file__)),
             'scientific_code_imported':False})
        absent=[s for s in range(256) if (s & 36)==0];present=[s for s in range(256) if (s & 36)!=0]
        assert len(absent)==64 and len(present)==192
        outcomes={};triples={};diagnostics={};nchecks=0
        for law in LAWS:
            m=read(a.repository/('results/061/matrices/'+law+'.json.gz'))
            v=read(a.repository/('results/061/vectors/'+law+'.json.gz'))
            A=m['numerators'];D=m['denominator'];k=list(map(int,v['k']));K=sum(k)
            assert len(A)==len(k)==256 and all(len(row)==256 for row in A)
            assert v['status']=='COMPUTED' and v['certificate']['criterion_pass'] and K==int(v['certificate']['K']) and min(k)>=0
            E=unrat(v['certificate']['total_variation_bound']);assert E>=0
            into_present=[sum(row[j] for j in present) for row in A]
            b_rows={str(s):into_present[s] for s in absent}
            for value in b_rows.values():assert F(value,D)==ALPHA;nchecks+=1
            b=F(sum(k[s] for s in absent),K);lo=max(F(0),b-E);hi=min(F(1),b+E)
            assert 0<=lo<=b<=hi<=1
            outcomes[law+'|ABSENT_MASS']=record(b,lo,hi,'stationary probability fraction')
            length=lambda x:(1-x)/(ALPHA*x) if x>0 else None
            L=length(b);lower=length(hi);upper=length(lo)
            finite_strict=0<lo<=hi<1
            outcomes[law+'|PRESENT_SPELL']=record(L,lower,upper,'updates per entry-sampled H-present spell',finite_strict)
            triples[law]=(L,lower,upper)
            incoming=ALPHA*b
            outgoing=sum((F(k[s],K)*F(sum(A[s][j] for j in absent),D) for s in present),F(0))
            residual=sum((F(k[s]*into_present[s],K*D) for s in range(256)),F(0))-(1-b)
            assert incoming-outgoing==residual
            diagnostics[law]={'absent_to_present_numerators':b_rows,'matrix_denominator':D,
                'event_mass_center':rat(b),'accepted_total_variation_bound':rat(E),
                'entry_flux_center':rat(incoming),'exit_flux_center':rat(outgoing),
                'residual_projection':rat(residual),'residual_decimal':dec(residual),
                'residual_is_zero':residual==0,'flux_identity_exact':True,
                'strict_event_mass_enclosure':finite_strict}
        coeffs={
            'ACTIVE_HALF_MINUS_ZERO|PRESENT_SPELL':{'ACTIVE_HALF':1,'ACTIVE_ZERO':-1},
            'NEUTRAL_HALF_MINUS_ZERO|PRESENT_SPELL':{'NEUTRAL_HALF':1,'NEUTRAL_ZERO':-1},
            'ACTIVE_MINUS_NEUTRAL_ZERO|PRESENT_SPELL':{'ACTIVE_ZERO':1,'NEUTRAL_ZERO':-1},
            'ACTIVE_MINUS_NEUTRAL_HALF|PRESENT_SPELL':{'ACTIVE_HALF':1,'NEUTRAL_HALF':-1},
            PRIMARY:{'ACTIVE_HALF':1,'ACTIVE_ZERO':-1,'NEUTRAL_HALF':-1,'NEUTRAL_ZERO':1}}
        for key,weights in coeffs.items():
            values=[]
            for field in range(3):
                terms=[sign*triples[law][field if sign>0 or field==0 else 3-field]
                       if triples[law][field if sign>0 or field==0 else 3-field] is not None else None
                       for law,sign in weights.items()]
                values.append(sum(terms,F(0)) if all(x is not None for x in terms) else None)
            outcomes[key]=record(*values,'difference in mean H-present spell duration, updates')
        assert len(outcomes)==13 and nchecks==256
        if all(q['center'] is not None for q in outcomes.values()):
            value=lambda name:unrat(outcomes[name+'|PRESENT_SPELL']['center'])
            assert value('RECURRENCE_BY_EXPRESSION')==value('ACTIVE_HALF_MINUS_ZERO')-value('NEUTRAL_HALF_MINUS_ZERO')==value('ACTIVE_MINUS_NEUTRAL_HALF')-value('ACTIVE_MINUS_NEUTRAL_ZERO')
        save('OUTCOMES.json',outcomes)
        save('FLUX_CERTIFICATES.json',{'alpha':rat(ALPHA),'exact_mean_absent_spell':rat(1/ALPHA),
             'absent_states':absent,'present_states':present,'absent_row_sums_checked':nchecks,
             'kernels':diagnostics,'contrast_centers_identity_exact':True,
             'no_assumption_of_geometric_or_independent_present_spells':True})
        save('EXECUTION.json',{'status':'COMPLETED_AUDIT_PENDING','started_at_utc':started,
             'finished_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'elapsed_seconds':time.monotonic()-start,'mathematical_records':13,
             'new_transition_rows':0,'stationary_solves':0,'hitting_time_solves':0,'population_paths':0,
             'random_draws':0,'primary':PRIMARY,'primary_sign':outcomes[PRIMARY]['sign'],
             'prospective_fixture_checks_reused':144})
        print(json.dumps({k:{'center':q['center_decimal'],'sign':q['sign']} for k,q in outcomes.items()},indent=2))
    except BaseException as error:
        (out/'FAILURE.json').write_text(json.dumps({'error':str(error),'traceback':traceback.format_exc(),'automatic_retry':False},indent=2)+'\n');raise
if __name__=='__main__':main()
