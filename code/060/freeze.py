"""Freeze source and prospective design before any production RNG or trajectory."""
import ast
from common import *
from prepare_design import source_check
from seed_design import verify_roster

def main():
 assert not (P/'SOURCE_SHA256SUMS').exists() and not (P/'INPUT_FREEZE.json').exists();assert read('TEST_STATUS.json')['status']=='PASS';verify_references();source_check();verify_roster(read('SEED_ROSTER.json'),read('PRIOR_SEED_INVENTORY.json')['integers'])
 fixed=('ASSIGNMENT.md','ASSIGNMENT_RECORD.json','SOURCE_INTERFACE.json','CONTINUATION_POLICY.md','README.md','IMPLEMENTATION_NOTES.md','config.json','METRIC_CATALOG.json','SEED_ROSTER.json','PRIOR_SEED_INVENTORY.json','PRIOR_SEED_AUTHENTICATION.json','IMPLEMENTATION_MAP.json','SOURCE_REFERENCES.json','SOURCE_SELECTION_CHECK.json','SELECTED_STATES.json','PREPARATION_TARGETS.json','TEST_STATUS.json','tests.log','job.sbatch')
 files=sorted(f for f in P.iterdir() if f.is_file() and (f.suffix=='.py' or f.name in fixed))
 for f in files:
  if f.suffix=='.py':ast.parse(f.read_text())
 save('DESIGN_FREEZE.json',dict(freeze_unix=time.time(),task_id='ORG-OBSERVATION-060',assignment_sha256=sha(P/'ASSIGNMENT.md'),selected_states_sha256=sha(P/'SELECTED_STATES.json'),source_selection_sha256=sha(P/'SOURCE_SELECTION_CHECK.json'),seed_roster_sha256=sha(P/'SEED_ROSTER.json'),metric_catalog_sha256=sha(P/'METRIC_CATALOG.json'),seed_records=1393,new_random_draws=0,new_scientific_paths=0,new_scientific_objective_calls=0))
 files.append(P/'DESIGN_FREEZE.json');(P/'SOURCE_SHA256SUMS').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in sorted(files)));print(json.dumps(dict(files=len(files),source_manifest_sha256=sha(P/'SOURCE_SHA256SUMS'))))
if __name__=='__main__':main()
