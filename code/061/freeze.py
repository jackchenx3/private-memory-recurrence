"""Prospective source/config/state-index freeze; no production kernel or solve."""
import ast
from common import *

def main():
 assert not (P/'SOURCE_SHA256SUMS').exists() and not (P/'PRODUCTION_STARTED.json').exists();assert read('TEST_STATUS.json')['status']=='PASS';verify_references()
 fixed=('ASSIGNMENT.md','DESIGN_CHECK.json','STATE_INDEX.json','config.json','OUTCOME_CATALOG.json','DEPENDENCY_HASHES.json','README.md','IMPLEMENTATION_NOTES.md','CONTINUATION_POLICY.md','TEST_STATUS.json','tests.log','job.sbatch')
 files=sorted(f for f in P.iterdir() if f.is_file() and (f.suffix=='.py' or f.name in fixed))
 for f in files:
  if f.suffix=='.py':ast.parse(f.read_text())
 save('DESIGN_FREEZE.json',dict(task_id='ORG-STATIONARY-061',revision=1,freeze_unix=time.time(),assignment_sha256=sha(P/'ASSIGNMENT.md'),state_index_sha256=sha(P/'STATE_INDEX.json'),catalog_sha256=sha(P/'OUTCOME_CATALOG.json'),production_matrices=0,production_stationary_vectors=0,allowed_audit_rows_checked=32,simulation_paths=0,random_draws=0))
 files.append(P/'DESIGN_FREEZE.json');manifest('SOURCE_SHA256SUMS',[f.name for f in files]);print(json.dumps(dict(files=len(files),source_manifest_sha256=sha(P/'SOURCE_SHA256SUMS'))))
if __name__=='__main__':main()
