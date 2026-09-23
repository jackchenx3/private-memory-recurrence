import pathlib,json
P=pathlib.Path(__file__).resolve().parent
def assess(v):
 a='HALF|C0|LOW_H|D40';b='HALF|C0|HIGH_F|D40';c='HALF_MINUS_ZERO|C0|LOW_H|D40';pa=v[a]['zero_classification']=='positive';pb=v[b]['zero_classification']=='negative'
 return dict(primary_key=a,primary=v[a],primary_supported=pa,companion_key=b,companion=v[b],companion_supported=pb,two_boundary_H_advantage_supported=pa and pb,incremental_recurrence_key=c,incremental_recurrence=v[c],incremental_recurrence_supported=v[c]['zero_classification']=='positive',initial_frequency_difference=v['HALF|C0|LOW_MINUS_HIGH_H|D40'],difference_prescribed_sign=None,interval_scope='approximate pointwise',independent_cohort=False,equilibrium_invasion=False)
if __name__=='__main__':
 q=assess(json.loads((P/'summary.json').read_text())['values']);(P/'PRIMARY_ASSESSMENT.json').write_text(json.dumps(q,indent=2)+'\n');print(q)
