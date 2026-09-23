import os,pathlib,json,time,shutil
from io_utils import save,sha
P=pathlib.Path(__file__).resolve().parent;SOURCE=P.parent/'probabilistic_private_memory_v1'
def verify_inherited():
 for line in (P/'INHERITED_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);assert sha(P/n)==h
 files={}
 for source in (SOURCE,P.parent/'intermittent_private_memory_v1',P.parent/'prepared_resident_introduction_v1',P.parent/'independent_rare_memory_novelty_v1',P.parent/'single_carrier_fresh_probe_v1',P.parent/'single_carrier_introduction_v1',P.parent/'private_memory_competition_v1'):
  for manifest in ('SOURCE_SHA256SUMS','INPUT_SHA256SUMS','RESULT_SHA256SUMS','DELIVERY_SHA256SUMS'):
   for line in (source/manifest).read_text().splitlines():h,n=line.split(None,1);assert sha(source/n)==h;files['../'+source.name+'/'+n]=h
 for n,q in json.loads((P/'IMPLEMENTATION_MAP.json').read_text()).items():assert sha(P/n)==q['sha256']==sha(P/q['source'])
 return files





COPIED=['streams.jsonl.gz','fresh_probe_masks.jsonl.gz','BOOTSTRAP_INDICES.json','RESIDENT_STATES.jsonl.gz','RESIDENT_PROVENANCE.json','TARGET_LAW_DRAWS.json','ZERO_TARGETS.json','HALF_TARGETS.json','FULL_TARGETS.json','survival_streams.jsonl.gz','SEEDS.json','SEED_ROSTER.json','SEED_COLLISION_CHECK.json','PRIOR_SEED_INVENTORY.json']
def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited()
 expected=json.loads(pathlib.Path('COPIED_INPUT_HASHES.json').read_text())
 for n in COPIED:shutil.copyfile(str(SOURCE/n),n);assert sha(n)==sha(SOURCE/n)==expected[n]
 save('INPUT_REFERENCES.json',dict(files=refs,old_control_paths=2304,controls_rerun=0,source_resident_states=192,seed_files_are_reused050_provenance=True,nested_FULL_reuse=True))
 save('INPUT_GENERATION.json',dict(new_seeds=0,new_random_draws=0,old_paths_reused=2304,copied_seed_roster_records=192,copied_survival_uniforms=983040,all_inputs_reused_from050=True))
 files=COPIED+['INPUT_REFERENCES.json','INPUT_GENERATION.json'];hashes={n:sha(n) for n in files};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()));save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),files=hashes,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_manifest_sha256=sha('INPUT_SHA256SUMS')))
if __name__=='__main__':main()
