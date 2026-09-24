"""Freeze only prospective code/inputs and test evidence; never include mutable status."""
import ast
from common import *
def main():
 assert not (P/'SOURCE_SHA256SUMS').exists();assert read('TEST_STATUS.json')['status']=='PASS';verify_references()
 files=sorted(f for f in P.iterdir() if f.is_file() and (f.suffix=='.py' or f.name in ('ASSIGNMENT.md','contract.json','RESUME_056.json','config.json','METRIC_CATALOG.json','TARGET_TABLE.json','INPUT_PREPARATION.json','SOURCE_REFERENCES.json','IMPLEMENTATION_MAP.json','TEST_STATUS.json','tests.log','tests-initial-failed.log','common-initial-failed.py.txt','PRESUBMISSION_REPAIR.json','RECORDED_COMPATIBILITY_CHECK.json','README.md','job.sbatch') or f.name.startswith('source055_')))
 for f in files:
  if f.suffix=='.py':ast.parse(f.read_text())
 inputs=[f for f in files if f.name.startswith('source055_')]+[P/'TARGET_TABLE.json',P/'METRIC_CATALOG.json',P/'SOURCE_REFERENCES.json']
 (P/'INPUT_SHA256SUMS').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in inputs));save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),input_manifest_sha256=sha(P/'INPUT_SHA256SUMS'),source055_delivery_sha256=read('SOURCE_REFERENCES.json')['delivery_manifest_sha256'],new_draws=0,new_paths_at_freeze=0,new_preparations=0,source_raw_references_authenticated=True))
 files+=[P/'INPUT_SHA256SUMS',P/'INPUT_FREEZE.json'];(P/'SOURCE_SHA256SUMS').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in sorted(files)));print(json.dumps(dict(files=len(files),source_manifest_sha256=sha(P/'SOURCE_SHA256SUMS'))))
if __name__=='__main__':main()
