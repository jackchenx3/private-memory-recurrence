import os,pathlib,json,time,hashlib,random
from io_utils import save,sha,File
from generators import local_masks,scouts,ties,labels,bootstrap,build_targets
from accepted_survival_model import to_uniform
P=pathlib.Path(__file__).resolve().parent;SOURCE=P.parent/'direct_private_memory_competition_v1'
def verify_inherited():
 for line in (P/'INHERITED_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);assert sha(P/n)==h
 for n,q in json.loads((P/'IMPLEMENTATION_MAP.json').read_text()).items():assert sha(P/n)==q['sha256']==sha(P/q['source'])
 # Full accepted051 content is authenticated by submit_hpc.sh once before allocation.
 return dict(accepted051_delivery_sha256=sha(SOURCE/'DELIVERY_SHA256SUMS'),old_population_inputs_used=False)
def seed(f,b,r):return int(hashlib.sha256(('ORG-PREPREP-052-r1|%s|%d|%d'%(f,b,r)).encode()).hexdigest()[:16],16)
def roster():
 coords=[(f,b,-1) for f in ('target_pair','innovations','copy') for b in range(24)]+[(f,b,r) for f in ('prep_local','prep_scout','prep_ties','prep_labels','transfer_local','transfer_scout','transfer_ties','transfer_labels','transfer_fresh','transfer_survival') for b in range(24) for r in range(8)]+[('bootstrap',-1,-1)]
 return [dict(family=f,block=b,replicate=r,seed=seed(f,b,r),namespace='ORG-PREPREP-052-r1|%s|%d|%d'%(f,b,r)) for f,b,r in coords]
def check_roster(rs,prior):
 ns=[r['seed'] for r in rs];assert rs==roster() and len(ns)==len(set(ns))==1993 and not set(ns)&set(prior)
def validate_freeze(name):
 q=json.loads(pathlib.Path(name).read_text());assert sha('SOURCE_SHA256SUMS')==q['source_manifest_sha256']
 for n,h in q['files'].items():assert sha(n)==h,n
 return q

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited();rs=json.loads(pathlib.Path('SEED_ROSTER.json').read_text());prior=json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers'];check_roster(rs,prior)
 save('SEED_COLLISION_CHECK.json',dict(status='PASS',unique_new=1993,prior_integer_inventory=len(prior),collision_count=0,checked_before_random_generation=True));save('SEEDS.json',rs);save('INPUT_REFERENCES.json',refs);targets={g:[] for g in ('ZERO','HALF','FULL')};preps=[];lawdraws=[]
 for b in range(24):
  rng=random.Random(seed('target_pair',b,-1));pair=[rng.getrandbits(32) for _ in range(2)];rng=random.Random(seed('innovations',b,-1));innov=[rng.getrandbits(32) for _ in range(38)];rng=random.Random(seed('copy',b,-1));copy=[rng.getrandbits(1) for _ in range(38)];preps.append(dict(block=b,targets=pair*20,last_target=pair[1]));lawdraws.append(dict(block=b,first_pair=pair,innovations=innov,copy_bits=copy,indices=list(range(2,40))))
  for g in targets:
   ts=build_targets(pair,innov,copy,g);targets[g].append(dict(block=b,targets=ts,actual_changes=[False]+[ts[j]!=ts[j-1] for j in range(1,40)],boundary_change_from_preparation=pair[0]!=pair[1],last_preparation_target=pair[1],first_actual_change_convention='initial evaluated state uses A; boundary B-to-A recorded separately',distinct_targets=len(set(ts)),law=g))
 save('PREPARATION_TARGETS.json',dict(blocks=preps));save('TARGET_LAW_DRAWS.json',dict(blocks=lawdraws))
 for g,rows in targets.items():save(g+'_TARGETS.json',dict(blocks=rows))
 with File('prep_streams.jsonl.gz','w') as prep,File('streams.jsonl.gz','w') as transfer,File('fresh_probe_masks.jsonl.gz','w') as fresh,File('survival_streams.jsonl.gz','w') as survival:
  for b in range(24):
   for r in range(8):
    for stage,out in [('prep',prep),('transfer',transfer)]:
     q={k:fun(random.Random(seed(stage+'_'+k,b,r))) for k,fun in [('local',local_masks),('scout',scouts),('ties',ties),('labels',labels)]};out.write(dict(block=b,replicate=r,draws=q))
    fresh.write(dict(block=b,replicate=r,fresh=scouts(random.Random(seed('transfer_fresh',b,r)))))
    rng=random.Random(seed('transfer_survival',b,r));rows=[]
    for _ in range(40):
     ks=[rng.getrandbits(52) for _ in range(128)];rows.append(dict(k=ks,u=[to_uniform(k) for k in ks]))
    survival.write(dict(block=b,replicate=r,survival=rows))
 save('BOOTSTRAP_INDICES.json',bootstrap(random.Random(seed('bootstrap',-1,-1))))
 save('INPUT_GENERATION.json',dict(seed_records=1993,target_pair_getrandbits32=48,innovation_getrandbits32=912,copy_getrandbits1=912,preparation=dict(local_randrange32=7864320,scout_getrandbits32=245760,tie_random=983040,label_shuffle=192),transfer=dict(local_randrange32=7864320,scout_getrandbits32=245760,tie_random=983040,label_shuffle=192,fresh_getrandbits32=245760,survival_getrandbits52=983040),bootstrap_randrange24=48000,underlying_PRNG_word_count='not claimed: rejection sampling/shuffle implementation dependent',old_inputs_used=False,preparation_fresh_or_survival_draws=0))
 files=['SEED_ROSTER.json','PRIOR_SEED_INVENTORY.json','SEEDS.json','SEED_COLLISION_CHECK.json','INPUT_REFERENCES.json','PREPARATION_TARGETS.json','TARGET_LAW_DRAWS.json','ZERO_TARGETS.json','HALF_TARGETS.json','FULL_TARGETS.json','prep_streams.jsonl.gz','streams.jsonl.gz','fresh_probe_masks.jsonl.gz','survival_streams.jsonl.gz','BOOTSTRAP_INDICES.json','INPUT_GENERATION.json'];hashes={n:sha(n) for n in files};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()));save('INPUT_FREEZE.json',dict(stage='all exogenous inputs before preparation',freeze_unix=time.time(),files=hashes,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_manifest_sha256=sha('INPUT_SHA256SUMS')))
if __name__=='__main__':main()
