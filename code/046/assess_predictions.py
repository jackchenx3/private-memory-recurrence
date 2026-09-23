"""Evaluate frozen pointwise directional predictions; no new inference or fitting."""
import json,pathlib
P=pathlib.Path(__file__).resolve().parent

def assess(values,spec):
 rows=[]
 for pred in spec['predictions']:
  q=values[pred['key']];observed=q['zero_classification'];status='supported' if observed==pred['expected'] else 'opposed' if observed in ('positive','negative') else 'unresolved';rows.append(dict(pred,assessment=status,observed=q))
 states=[r['assessment'] for r in rows];overall='full_three_part_pattern_reproduced' if all(s=='supported' for s in states) else 'not_reproduced' if 'opposed' in states or 'supported' not in states else 'partially_supported_full_pattern_not_reproduced'
 spread=values['RARE|RECUR|ACTIVE_C0|D40'];sham=values['RARE|RECUR|ACTIVE_C0-SHAM_C0|D40'];return dict(overall=overall,predictions=rows,mean_spread_supported=spread['zero_classification']=='positive',sham_attribution_supported=sham['zero_classification']=='positive',retrieval_attributed_spread_supported=spread['zero_classification']=='positive' and sham['zero_classification']=='positive',absolute_spread=spread,sham_contrast=sham,coverage='Separate approximate pointwise intervals, not simultaneous coverage',pooling=False,endpoint_substitution=False)

def main():
 values=json.loads((P/'summary.json').read_text())['values'];spec=json.loads((P/'FROZEN_PREDICTIONS.json').read_text());result=assess(values,spec);(P/'PREDICTION_ASSESSMENT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
