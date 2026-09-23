import pathlib,json
P=pathlib.Path(__file__).resolve().parent
def assess(v):
 a='HALF|C0|F_BG_EFFECT|D40';b='HALF|C0|H_BG_EFFECT|D40';h='HALF|C0|F_BG_SWITCH|D40';f='HALF|C0|H_BG_SWITCH|D40';r='HALF_MINUS_ZERO|C0|F_BG_EFFECT|D40';positive=lambda k:v[k]['zero_classification']=='positive';negative=lambda k:v[k]['zero_classification']=='negative'
 return dict(primary_key=a,primary=v[a],primary_supported=positive(a),companion_key=b,companion=v[b],companion_supported=negative(b),resident_background_policy_advantage_supported=positive(a) and negative(b),absolute_H_introduction_key=h,absolute_H_introduction=v[h],absolute_H_introduction_supported=positive(h),absolute_F_introduction_key=f,absolute_F_introduction=v[f],absolute_F_introduction_supported=negative(f),regime_comparison_key=r,regime_comparison=v[r],regime_comparison_supported=positive(r),regime_changes_both_preparation_and_continuation=True,interval_scope='approximate pointwise',independent_cohort=False,equilibrium_invasion=False,storage_origin_test=False)
if __name__=='__main__':
 q=assess(json.loads((P/'summary.json').read_text())['values']);(P/'PRIMARY_ASSESSMENT.json').write_text(json.dumps(q,indent=2)+'\n');print(q)
