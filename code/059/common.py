import pathlib,json,hashlib,time
from io_utils import sha,File
P=pathlib.Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text())
def save(n,v):
 f=P/n;f.parent.mkdir(parents=True,exist_ok=True);t=f.with_name(f.name+'.tmp');t.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');t.replace(f)
def rows(f):
 with File(f,'r') as src:
  for row in src:yield row

def keyed(n):return {(q['block'],q['replicate']):q for q in rows(P/n)}
def states():return {(q['source_state']['block'],q['source_state']['replicate']):q for q in read('SELECTED_STATES.json')}
def verify_references():
 refs=read('SOURCE_REFERENCES.json');accepted={}
 for n,h in refs['accepted_delivery_manifests'].items():
  assert sha(P.parent/n)==h,n
  accepted.update({line.split('  ',1)[1]:line.split('  ',1)[0] for line in (P.parent/n).read_text().splitlines()})
 for n,q in read('IMPLEMENTATION_MAP.json').items():assert sha(P/n)==q['sha256']==sha(P/q['source'])==accepted[n],n
 assert refs['prepared_source_sha256']==accepted['RESIDENT_STATES.jsonl.gz']
 assert refs['source_target_sha256']==accepted['POLICY_TARGETS.json']
 assert sha(P/'SELECTED_STATES.json')==refs['selected_states_sha256'] and sha(P/'PREPARATION_TARGETS.json')==refs['selected_target_sha256']
 return len(read('IMPLEMENTATION_MAP.json'))
def verify_manifest(n):
 for line in (P/n).read_text().splitlines():h,f=line.split('  ',1);assert sha(P/f)==h,f

def freeze_stage(prefix,files):
 hs={n:sha(P/n) for n in files};(P/(prefix+'_SHA256SUMS')).write_text(''.join(h+'  '+n+'\n' for n,h in hs.items()));save(prefix+'_FREEZE.json',dict(freeze_unix=time.time(),files=hs,manifest_sha256=sha(P/(prefix+'_SHA256SUMS')),source_manifest_sha256=sha(P/'SOURCE_SHA256SUMS')))
def check_stage(prefix):
 q=read(prefix+'_FREEZE.json');assert q['source_manifest_sha256']==sha(P/'SOURCE_SHA256SUMS');verify_manifest(prefix+'_SHA256SUMS');return q

def checkpoint(stage,block,files,counts):
 save('checkpoints/'+stage+'-block%02d.json'%block,dict(stage=stage,last_complete_block=block,next_block=block+1,files={n:sha(P/n) for n in files},counts=counts,source_manifest_sha256=sha(P/'SOURCE_SHA256SUMS'),input_freeze_sha256=sha(P/'INPUT_FREEZE.json'),replacement_job_authorized=False))
