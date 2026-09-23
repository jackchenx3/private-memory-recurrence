import pathlib,json
P=pathlib.Path(__file__).resolve().parent
def assess(v):
 p='HALF|C0|R_H|D40';c='HALF|C0|R_F|D40';pos=lambda k:v[k]['zero_classification']=='positive'
 return dict(primary_key=p,primary=v[p],primary_supported=pos(p),companion_key=c,companion=v[c],companion_supported=pos(c),common_competitor_pattern_supported=pos(p) and pos(c),interaction=v['HALF|C0|INTERACTION|D40'],interaction_prescribed_sign=None,interval_scope='approximate pointwise',independent_cohort=False,fixed_initial_carrier_density=True)
if __name__=='__main__':
 q=assess(json.loads((P/'summary.json').read_text())['values']);(P/'PRIMARY_ASSESSMENT.json').write_text(json.dumps(q,indent=2)+'\n');print(q)
