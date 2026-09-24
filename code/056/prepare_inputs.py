"""Deterministic target recursion on recorded tapes: no RNG, scoring or propagation."""
from common import *
from accepted_inputs055 import extend_targets
from analysis import *
def main():
 assert not (P/'SOURCE_SHA256SUMS').exists(),'Frozen payload cannot be rebuilt'
 targets={};draws=read('source055_TARGET_LAW_DRAWS.json')['blocks']
 for p in LAWS:
  histories=read('source055_reused052_'+p+'_TARGETS.json')['blocks']
  diagonal=read('source055_'+p+'_TARGETS.json')['blocks']
  for q in LAWS:
   data=[]
   for b in range(24):
    h=histories[b]['targets'];d=draws[b];ts=extend_targets(h,d['innovations'],d['copy_bits'],q)
    if p==q:assert ts==diagonal[b]['targets']
    data.append(dict(block=b,targets=ts,preparation_terminal_targets=h[-2:],boundary_previous_target=h[-1],boundary_actual_change=h[-1]!=ts[0]))
   targets['P_'+p+'_Q_'+q]=data
 save('TARGET_TABLE.json',targets)
 save('METRIC_CATALOG.json',dict(groups=GROUPS,endpoints=ENDPOINTS,keys=[g+'|'+k for g in GROUPS for k in ENDPOINTS],structural_zeros=STRUCTURAL_ZEROS,structural_reason='No algebraically forced zeros among D40,U,U40 or the specified factorial contrasts.',primary=PRIMARY,primary_prediction='positive',interaction_prediction=None,independent_units=24,continuations_per_block=8,bootstrap_rows=2000,quantiles='linear .025/.975',interval_scope='approximate pointwise',expected_descendants_scale=32,descriptive_descendant_scale_not_threshold=True))
 save('config.json',dict(read('contract.json'),source_directory='../majority_policy_preparation_v1',new_cells=['P_ZERO_Q_HALF','P_HALF_Q_ZERO'],reused_cells=['P_ZERO_Q_ZERO','P_HALF_Q_HALF'],unchanged_operators=True,new_candidate_evaluations=11796480,new_initial_evaluations=73728,new_states=94464,source_prepared_states=768,queries_per_path=5152,controller_model_calls=0,actual_credit_savings=None))
 save('INPUT_PREPARATION.json',dict(status='PASS',generated_target_cells=4,blocks_per_cell=24,targets_per_block=40,exact_diagonal_regeneration=True,new_random_draws=0,new_seeds=0,new_preparations=0,new_population_paths=0,new_objective_calls=0))
if __name__=='__main__':main()
