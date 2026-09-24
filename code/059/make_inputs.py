"""Generate new059 indexed transfer inputs inside the single allocation, before outcomes."""
import os,random
from common import *
from seed_design import seed,verify_roster
from generators import local_masks,scouts,ties,labels,bootstrap
from accepted_inputs055 import extend_targets
from accepted_survival_model import to_uniform

def main():
 assert os.environ.get('SLURM_JOB_ID') and not (P/'INPUT_FREEZE.json').exists();verify_manifest('SOURCE_SHA256SUMS');verify_references();verify_roster(read('SEED_ROSTER.json'),read('PRIOR_SEED_INVENTORY.json')['integers'])
 targets=[];draws=[]
 for b,history in enumerate(read('PREPARATION_TARGETS.json')):
  rng=random.Random(seed('continuation_innovations',b,-1));innov=[rng.getrandbits(32) for _ in range(40)];rng=random.Random(seed('continuation_copy',b,-1));copy=[rng.getrandbits(1) for _ in range(40)]
  ts=extend_targets(history['targets'],innov,copy,'HALF');draws.append(dict(block=b,innovations=innov,copy_bits=copy));targets.append(dict(block=b,targets=ts,preparation_terminal_targets=history['targets'][-2:],boundary_previous_target=history['targets'][-1],boundary_actual_change=ts[0]!=history['targets'][-1]))
 save('TARGET_TABLE.json',targets);save('TARGET_LAW_DRAWS.json',draws)
 with File(P/'streams.jsonl.gz','w') as out,File(P/'fresh_probe_masks.jsonl.gz','w') as fo,File(P/'survival_streams.jsonl.gz','w') as so:
  for b in range(24):
   for r in range(8):
    d={k:fn(random.Random(seed('transfer_'+k,b,r))) for k,fn in [('local',local_masks),('scout',scouts),('ties',ties),('labels',labels)]};out.write(dict(block=b,replicate=r,draws=d));fo.write(dict(block=b,replicate=r,fresh=scouts(random.Random(seed('transfer_fresh',b,r)))))
    rng=random.Random(seed('transfer_survival',b,r));ss=[]
    for _ in range(40):
     ks=[rng.getrandbits(52) for _ in range(128)];ss.append(dict(k=ks,u=[to_uniform(k) for k in ks]))
    so.write(dict(block=b,replicate=r,survival=ss))
 save('BOOTSTRAP_INDICES.json',bootstrap(random.Random(seed('bootstrap',-1,-1))));save('SEEDS.json',read('SEED_ROSTER.json'));save('SEED_COLLISION_CHECK.json',dict(status='PASS',new_unique=1201,prior_integers=len(read('PRIOR_SEED_INVENTORY.json')['integers']),collisions=0,before_trajectories=True))
 save('INPUT_GENERATION.json',dict(seed_records=1201,innovations_getrandbits32=960,copy_getrandbits1=960,local_randrange32=7864320,scout_getrandbits32=245760,tie_random=983040,label_shuffle=192,fresh_getrandbits32=245760,survival_getrandbits52=983040,bootstrap_randrange24=48000,old_transfer_inputs_used=False,preparation_draws=0,unused_absolute_index_prefix='constant zeros; not consumed',underlying_PRNG_word_count='not claimed'))
 freeze_stage('INPUT',['SELECTED_STATES.json','PREPARATION_TARGETS.json','TARGET_TABLE.json','TARGET_LAW_DRAWS.json','streams.jsonl.gz','fresh_probe_masks.jsonl.gz','survival_streams.jsonl.gz','BOOTSTRAP_INDICES.json','SEEDS.json','SEED_COLLISION_CHECK.json','INPUT_GENERATION.json'])
if __name__=='__main__':main()
