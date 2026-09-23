import pathlib,json
P=pathlib.Path(__file__).resolve().parent
def assess(v):
 primary='RACE32|HALF|ACTIVE_C0-NOVEL_C0|D40';direct='RACE32|HALF_MINUS_ZERO|ACTIVE_C0-NOVEL_C0|D40';absolute='RACE32|HALF|ACTIVE_C0|D40';sham='RACE32|HALF|ACTIVE_C0-SHAM_C0|D40'
 positive=lambda k:v[k]['zero_classification']=='positive'
 return dict(selection_moderation=v['RACE32_MINUS_BEST32|HALF|ACTIVE_C0-NOVEL_C0|D40'],primary_key=primary,primary=v[primary],prospective_expectation='positive',expectation_supported=positive(primary),opposite_supported=v[primary]['zero_classification']=='negative',incremental_lag_two_attribution=v[direct],incremental_attribution_supported=positive(direct),absolute_change=v[absolute],mean_spread_supported=positive(absolute),sham_contrast=v[sham],retrieval_attributed_mean_increase=positive(absolute) and positive(sham),coverage='all intervals approximate pointwise including primary',independent_replication=False,monotonicity_claim=False)
if __name__=='__main__':
 q=assess(json.loads((P/'summary.json').read_text())['values']);(P/'PRIMARY_ASSESSMENT.json').write_text(json.dumps(q,indent=2)+'\n');print(q)
