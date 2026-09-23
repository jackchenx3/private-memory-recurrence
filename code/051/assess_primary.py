import pathlib,json
P=pathlib.Path(__file__).resolve().parent
def assess(v):
 primary='HALF|C0|MIX_H_MINUS_F|D40';positive=lambda k:v[k]['zero_classification']=='positive'
 return dict(primary_key=primary,primary=v[primary],prospective_expectation='positive',expectation_supported=positive(primary),historical_absolute=v['HALF|C0|MIX_H|D40'],historical_mean_increase=positive('HALF|C0|MIX_H|D40'),fresh_absolute=v['HALF|C0|MIX_F|D40'],composition_moderation=v['HALF|C0|MIX_MINUS_ISO_RANK|D40'],incremental_recurrence=v['HALF_MINUS_ZERO|C0|MIX_H_MINUS_F|D40'],incremental_recurrence_supported=positive('HALF_MINUS_ZERO|C0|MIX_H_MINUS_F|D40'),interval_scope='approximate pointwise',total_composition_intervention=True,independent_replication=False)
if __name__=='__main__':
 q=assess(json.loads((P/'summary.json').read_text())['values']);(P/'PRIMARY_ASSESSMENT.json').write_text(json.dumps(q,indent=2)+'\n');print(q)
