import os,pathlib,json,time,shutil
from io_utils import save,sha
P=pathlib.Path(__file__).resolve().parent;SOURCE=P.parent/'independent_prepared_competition_v1'
COPIED=['streams.jsonl.gz','fresh_probe_masks.jsonl.gz','BOOTSTRAP_INDICES.json','RESIDENT_STATES.jsonl.gz','RESIDENT_PROVENANCE.json','TARGET_LAW_DRAWS.json','ZERO_TARGETS.json','HALF_TARGETS.json','FULL_TARGETS.json','survival_streams.jsonl.gz','SEEDS.json','SEED_ROSTER.json','SEED_COLLISION_CHECK.json','PRIOR_SEED_INVENTORY.json','PREPARATION_TARGETS.json']
def verify_inherited():
 for line in (P/'INHERITED_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);assert sha(P/n)==h
 for n,q in json.loads((P/'IMPLEMENTATION_MAP.json').read_text()).items():assert sha(P/n)==q['sha256']==sha(P/q['source'])
 change=json.loads((P/'MODEL_CHANGE.json').read_text());original=(P/'accepted_transfer_model.py').read_text();assert (P/'model.py').read_text()==original.replace("assign={'HH'","assign={"+change['mapping_addition']+"'HH'")
 return dict(accepted052_delivery_sha256=sha(SOURCE/'DELIVERY_SHA256SUMS'),accepted053_delivery_sha256=sha(P.parent/'matched_competitor_policy_v1/DELIVERY_SHA256SUMS'),full_deliveries_verified_in_preflight=True)

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited();expected=json.loads(pathlib.Path('COPIED_INPUT_HASHES.json').read_text())
 for n in COPIED:shutil.copyfile(str(SOURCE/n),n);assert sha(n)==sha(SOURCE/n)==expected[n]
 save('INPUT_REFERENCES.json',dict(provenance=refs,reused_prepared_states=192,old_paths_used=0,old_paths_rerun=0,new_preparation_calls=0));save('INPUT_GENERATION.json',dict(new_seeds=0,new_random_draws=0,reused_seed_roster_records=1993,all_inputs_reused_from052=True,seed_files_are_historical_provenance=True))
 names=COPIED+['INPUT_REFERENCES.json','INPUT_GENERATION.json'];hs={n:sha(n) for n in names};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hs.items()));save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),files=hs,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_manifest_sha256=sha('INPUT_SHA256SUMS')))
if __name__=='__main__':main()
