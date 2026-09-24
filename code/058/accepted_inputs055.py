import os,pathlib,json,time,hashlib,random,shutil
from io_utils import save,sha,File
from generators import local_masks,scouts,ties,labels
from accepted_survival_model import to_uniform
P=pathlib.Path(__file__).resolve().parent;SOURCE=P.parent/'independent_prepared_competition_v1'
COPIED=['streams.jsonl.gz','fresh_probe_masks.jsonl.gz','survival_streams.jsonl.gz','RESIDENT_STATES.jsonl.gz','RESIDENT_PROVENANCE.json','ZERO_TARGETS.json','HALF_TARGETS.json','FULL_TARGETS.json','SEEDS.json','SEED_ROSTER.json','SEED_COLLISION_CHECK.json','PRIOR_SEED_INVENTORY.json','TARGET_LAW_DRAWS.json']
def verify_inherited():
 for line in (P/'INHERITED_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);assert sha(P/n)==h
 for n,q in json.loads((P/'IMPLEMENTATION_MAP.json').read_text()).items():assert sha(P/n)==q['sha256']==sha(P/q['source'])
 return dict(accepted052_delivery_sha256=sha(SOURCE/'DELIVERY_SHA256SUMS'),accepted054_delivery_sha256=sha(P.parent/'full_density_frequency_boundary_v1/DELIVERY_SHA256SUMS'),full_deliveries_verified_in_preflight=True)
def seed(f,b,r):return int(hashlib.sha256(('ORG-POLICYPREP-055-r1|%s|%d|%d'%(f,b,r)).encode()).hexdigest()[:16],16)
def roster():
 coords=[(f,b,-1) for f in ('continuation_innovations','continuation_copy') for b in range(24)]+[(f,b,r) for f in ('transfer_local','transfer_scout','transfer_ties','transfer_labels','transfer_fresh','transfer_survival') for b in range(24) for r in range(8)]
 return [dict(family=f,block=b,replicate=r,seed=seed(f,b,r),namespace='ORG-POLICYPREP-055-r1|%s|%d|%d'%(f,b,r)) for f,b,r in coords]
def check_roster(rs,prior):
 ns=[q['seed'] for q in rs];assert rs==roster() and len(ns)==len(set(ns))==1200 and not set(ns)&set(prior)
def extend_targets(history,innovations,copy,law):
 assert len(history)==len(innovations)==len(copy)==40 and law in ('ZERO','HALF','FULL') and all(x in (0,1) for x in copy);ts=list(history)
 for z,c in zip(innovations,copy):ts.append(ts[-2] if law=='FULL' or law=='HALF' and c else z)
 return ts[40:]
def validate_freeze(name):
 q=json.loads(pathlib.Path(name).read_text());assert sha('SOURCE_SHA256SUMS')==q['source_manifest_sha256']
 for n,h in q['files'].items():assert sha(n)==h,n
 return q

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited();expected=json.loads(pathlib.Path('COPIED_INPUT_HASHES.json').read_text())
 for n in COPIED+['BOOTSTRAP_INDICES.json']:
  dst='reused052_'+n if n in COPIED else n;shutil.copyfile(str(SOURCE/n),dst);assert sha(dst)==sha(SOURCE/n)==expected[n]
 rs=json.loads(pathlib.Path('SEED_ROSTER.json').read_text());prior=json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers'];check_roster(rs,prior);save('SEED_COLLISION_CHECK.json',dict(status='PASS',unique_new=1200,prior_integer_inventory=len(prior),collision_count=0,checked_before_random_generation=True));save('SEEDS.json',rs);save('INPUT_REFERENCES.json',refs)
 originals={g:json.loads(pathlib.Path('reused052_'+g+'_TARGETS.json').read_text())['blocks'] for g in ('ZERO','HALF','FULL')};targets={g:[] for g in originals};lawdraws=[]
 for b in range(24):
  rng=random.Random(seed('continuation_innovations',b,-1));innov=[rng.getrandbits(32) for _ in range(40)];rng=random.Random(seed('continuation_copy',b,-1));copy=[rng.getrandbits(1) for _ in range(40)];lawdraws.append(dict(block=b,innovations=innov,copy_bits=copy,absolute_indices=list(range(40,80))))
  for g in targets:
   history=originals[g][b]['targets'];ts=extend_targets(history,innov,copy,g);targets[g].append(dict(block=b,targets=ts,preparation_terminal_targets=history[-2:],absolute_indices=list(range(40,80)),actual_changes=[ts[0]!=history[-1]]+[ts[i]!=ts[i-1] for i in range(1,40)],boundary_actual_change=ts[0]!=history[-1],law=g))
 save('TARGET_LAW_DRAWS.json',dict(blocks=lawdraws))
 for g,q in targets.items():save(g+'_TARGETS.json',dict(blocks=q))
 with File('streams.jsonl.gz','w') as out,File('fresh_probe_masks.jsonl.gz','w') as fo,File('survival_streams.jsonl.gz','w') as so:
  for b in range(24):
   for r in range(8):
    d={k:fun(random.Random(seed('transfer_'+k,b,r))) for k,fun in [('local',local_masks),('scout',scouts),('ties',ties),('labels',labels)]};out.write(dict(block=b,replicate=r,draws=d));fo.write(dict(block=b,replicate=r,fresh=scouts(random.Random(seed('transfer_fresh',b,r)))));rng=random.Random(seed('transfer_survival',b,r));ss=[]
    for _ in range(40):
     ks=[rng.getrandbits(52) for j in range(128)];ss.append(dict(k=ks,u=[to_uniform(k) for k in ks]))
    so.write(dict(block=b,replicate=r,survival=ss))
 save('INPUT_GENERATION.json',dict(seed_records=1200,innovation_getrandbits32=960,copy_getrandbits1=960,local_randrange32=7864320,scout_getrandbits32=245760,tie_random=983040,label_shuffle=192,fresh_getrandbits32=245760,survival_getrandbits52=983040,bootstrap_new_draws=0,preparation_new_draws=0,underlying_PRNG_word_count='not claimed: rejection sampling/shuffle implementation dependent',source_cohort_reused=True))
 files=['reused052_'+n for n in COPIED]+['BOOTSTRAP_INDICES.json','SEED_ROSTER.json','PRIOR_SEED_INVENTORY.json','SEEDS.json','SEED_COLLISION_CHECK.json','INPUT_REFERENCES.json','TARGET_LAW_DRAWS.json','ZERO_TARGETS.json','HALF_TARGETS.json','FULL_TARGETS.json','streams.jsonl.gz','fresh_probe_masks.jsonl.gz','survival_streams.jsonl.gz','INPUT_GENERATION.json'];hs={n:sha(n) for n in files};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hs.items()));save('INPUT_FREEZE.json',dict(stage='all reused/new exogenous inputs before first preparation',freeze_unix=time.time(),files=hs,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_manifest_sha256=sha('INPUT_SHA256SUMS')))
if __name__=='__main__':main()
