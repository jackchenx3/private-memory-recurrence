"""Separate primary ranking, absolute spread, sham attribution and state moderation."""
import pathlib,json
P=pathlib.Path(__file__).resolve().parent
PRIMARY='RESIDENT40|RECUR|ACTIVE_C0-NOVEL_C0|D40';SPREAD='RESIDENT40|RECUR|ACTIVE_C0|D40';SHAM='RESIDENT40|RECUR|ACTIVE_C0-SHAM_C0|D40';STATE='RESIDENT40_MINUS_NAIVE|RECUR|ACTIVE_C0-NOVEL_C0|D40'
def assess(v):
 pos=lambda k:v[k]['zero_classification']=='positive'
 return dict(primary_key=PRIMARY,primary=v[PRIMARY],historical_advantage_supported=pos(PRIMARY),opposite_ranking_supported=v[PRIMARY]['zero_classification']=='negative',mean_spread_supported=pos(SPREAD),retrieval_attributed_spread_supported=pos(SPREAD) and pos(SHAM),absolute_spread=v[SPREAD],sham_contrast=v[SHAM],initial_state_moderation=v[STATE],moderation_scope='Total strategy contrast after prepared minus naive start; not a per-carrier coefficient or unique mediator',equilibrium_claim=False,coverage='All including primary approximate pointwise, not simultaneous',pooling=False)
def main():
 v=json.loads((P/'summary.json').read_text())['values'];r=assess(v);(P/'PRIMARY_ASSESSMENT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
