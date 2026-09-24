"""Generate all independent058 exogenous tapes inside allocation before any trajectory."""
import os,random
from common import *
from seed_design import seed,verify_roster
from generators import local_masks,scouts,ties,labels,bootstrap,build_targets
from accepted_inputs055 import extend_targets
from accepted_survival_model import to_uniform

def main():
 assert os.environ.get('SLURM_JOB_ID') and not (P/'INPUT_FREEZE.json').exists()
 verify_manifest('SOURCE_SHA256SUMS');verify_references();rs=read('SEED_ROSTER.json');prior=read('PRIOR_SEED_INVENTORY.json')['integers'];verify_roster(rs,prior)
 save('SEED_COLLISION_CHECK.json',dict(status='PASS',unique_new=3193,prior_integers=len(prior),collisions=0,before_random_generation=True));save('SEEDS.json',rs)
 histories={'HALF':[]};targets={};initial=[];lawdraws=[];cdraws=[]
 for b in range(24):
  rng=random.Random(seed('target_pair',b,-1));pair=[rng.getrandbits(32) for _ in range(2)];rng=random.Random(seed('policy_innovations',b,-1));innov=[rng.getrandbits(32) for _ in range(38)];rng=random.Random(seed('policy_copy',b,-1));bits=[rng.getrandbits(1) for _ in range(38)]
  rng=random.Random(seed('continuation_innovations',b,-1));ci=[rng.getrandbits(32) for _ in range(40)];rng=random.Random(seed('continuation_copy',b,-1));cc=[rng.getrandbits(1) for _ in range(40)]
  initial.append(dict(block=b,targets=pair*20));lawdraws.append(dict(block=b,first_pair=pair,innovations=innov,copy_bits=bits));cdraws.append(dict(block=b,innovations=ci,copy_bits=cc))
  for p in histories:
   hs=build_targets(pair,innov,bits,p);histories[p].append(dict(block=b,targets=hs))
   for q in ('ZERO','HALF'):
    ts=extend_targets(hs,ci,cc,q);targets.setdefault('Q_'+q,[]).append(dict(block=b,targets=ts,preparation_terminal_targets=hs[-2:],boundary_previous_target=hs[-1],boundary_actual_change=hs[-1]!=ts[0]))
 save('INITIAL_TARGETS.json',dict(blocks=initial));save('POLICY_TARGETS.json',histories);save('POLICY_TARGET_DRAWS.json',dict(blocks=lawdraws));save('CONTINUATION_TARGET_DRAWS.json',dict(blocks=cdraws));save('TARGET_TABLE.json',targets)
 for stage in ('initial','policy','continuation'):
  stem='' if stage=='continuation' else stage+'_'
  with File(P/(stem+'streams.jsonl.gz'),'w') as out:
   for b in range(24):
    for r in range(8):
     d={k:fn(random.Random(seed(stage+'_'+k,b,r))) for k,fn in [('local',local_masks),('scout',scouts),('ties',ties),('labels',labels)]};out.write(dict(block=b,replicate=r,draws=d))
  if stage!='initial':
   with File(P/(stem+'fresh_probe_masks.jsonl.gz'),'w') as fo,File(P/(stem+'survival_streams.jsonl.gz'),'w') as so:
    for b in range(24):
     for r in range(8):
      fo.write(dict(block=b,replicate=r,fresh=scouts(random.Random(seed(stage+'_fresh',b,r)))));rng=random.Random(seed(stage+'_survival',b,r));ss=[]
      for _ in range(40):
       ks=[rng.getrandbits(52) for _ in range(128)];ss.append(dict(k=ks,u=[to_uniform(k) for k in ks]))
      so.write(dict(block=b,replicate=r,survival=ss))
 save('BOOTSTRAP_INDICES.json',bootstrap(random.Random(seed('bootstrap',-1,-1))))
 counts={s:dict(local_randrange32=7864320,scout_getrandbits32=245760,tie_random=983040,label_shuffle=192) for s in ('initial','policy','continuation')}
 for s in ('policy','continuation'):counts[s].update(fresh_getrandbits32=245760,survival_getrandbits52=983040)
 save('INPUT_GENERATION.json',dict(seed_records=3193,target_pair_getrandbits32=48,policy_innovations_getrandbits32=912,policy_copy_getrandbits1=912,continuation_innovations_getrandbits32=960,continuation_copy_getrandbits1=960,stage_draws=counts,bootstrap_randrange24=48000,initial_survival_or_fresh_draws=0,old_inputs_used=False,underlying_PRNG_word_count='Not claimed; API-level calls only.'))
 names=['SEEDS.json','SEED_COLLISION_CHECK.json','INITIAL_TARGETS.json','POLICY_TARGETS.json','POLICY_TARGET_DRAWS.json','CONTINUATION_TARGET_DRAWS.json','TARGET_TABLE.json','BOOTSTRAP_INDICES.json','INPUT_GENERATION.json','initial_streams.jsonl.gz','policy_streams.jsonl.gz','policy_fresh_probe_masks.jsonl.gz','policy_survival_streams.jsonl.gz','streams.jsonl.gz','fresh_probe_masks.jsonl.gz','survival_streams.jsonl.gz'];freeze_stage('INPUT',names)
if __name__=='__main__':main()
