"""Authenticate reused states and freeze prospective design without random generation."""
from common import *
from analysis import *
from seed_design import roster,verify_roster

def source_check():
 refs=read('SOURCE_REFERENCES.json');src=P.parent/'cross_environment_replication_v1'
 assert sha(src/'RESIDENT_STATES.jsonl.gz')==refs['prepared_source_sha256']=='df3e9529314c9fa43aad84ed5aed49a7ce945694939c64aa3c4ecf167023df47'
 assert sha(src/'DELIVERY_SHA256SUMS')=='406be53c487bce3160dce2f8d48099fb2787ecfe3a206d2e2e9f0ee44b0901ed'
 chosen=[dict(source_row_index=i,source_state=q) for i,q in enumerate(rows(src/'RESIDENT_STATES.jsonl.gz')) if q['geometry']=='HALF' and q['background']=='F']
 assert chosen==read('SELECTED_STATES.json') and len(chosen)==192 and len(states())==192
 assert sha(P.parent/refs['source_target_file'])==refs['source_target_sha256']
 assert read('PREPARATION_TARGETS.json')==json.loads((P.parent/refs['source_target_file']).read_text())['HALF']
 for q in chosen:
  st=q['source_state'];b=st['block'];assert st['last_two_preparation_targets']==read('PREPARATION_TARGETS.json')[b]['targets'][-2:]
  assert st['rebased_population']==[[x[0],x[1],i,x[3]] for i,x in enumerate(st['population'])]
  assert all(x[1]==2 for x in st['rebased_population'])
 return dict(status='PASS',selected=192,filter='geometry HALF and background F only',source=refs,scientific_paths_generated=0)

def main():
 assert not (P/'SOURCE_SHA256SUMS').exists();save('SOURCE_SELECTION_CHECK.json',source_check());verify_references();verify_roster(roster(),read('PRIOR_SEED_INVENTORY.json')['integers']);save('SEED_ROSTER.json',roster())
 save('METRIC_CATALOG.json',dict(keys=KEYS,groups=GROUPS,endpoints=ENDPOINTS,primary=PRIMARY,prediction='negative',structural_zeros=[],bootstrap_rows=2000,blocks=24,replicates_per_block=8,resolution_fraction=DELTA,intervals='exploratory approximate pointwise',raw_audit_block=0,raw_audit_paths=96))
 save('config.json',dict(task_id='ORG-OBSERVATION-060',revision=1,source='057 exact-observation HALF/F states',new_preparations=0,reused_preparations=192,blocks=24,replicates_per_block=8,population_size=32,bits=32,cost=0,updates=40,interfaces=['EXACT','NOISY'],laws=['ZERO','HALF'],configurations=CONFIGS,new_paths=2304,new_objective_calls=11870208,initial_queries=73728,candidate_queries=11796480,new_noise_uniforms=989184,seed_records=1393,bootstrap_rows=2000,estimates=81,primary=PRIMARY,resolution_fraction=DELTA,resources=dict(cpus=1,memory_GiB=4,minutes=15,partition='norm'),timeout_seconds=870,guard_bytes=3758096384,max_production_allocations=1,absolute_start=40,unused_fresh_prefix='40 constant-zero rows; never consumed',observation_error='EXACT:0;NOISY:2u-1, no clipping',survival='-log(open_uniform)*2.0**observed_score; order(key,tie,index)',cohort_pooling=False,independent_training_replication=False,main_figures=2))
 print('060 prospective design:192 authenticated states;1393 seeds;2304 paths;81 estimates;no draws or trajectories')
if __name__=='__main__':main()
