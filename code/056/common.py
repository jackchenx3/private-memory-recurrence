import pathlib,json,gzip,hashlib,time
P=pathlib.Path(__file__).resolve().parent
SOURCE=P.parent/'majority_policy_preparation_v1'
def read(n):return json.loads((P/n).read_text())
def save(n,v):
 f=P/n;f.parent.mkdir(parents=True,exist_ok=True);t=f.with_name(f.name+'.tmp');t.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');t.replace(f)
from io_utils import sha as sha, File
def rows(f):
 with File(f,'r') as src:
  for row in src:yield row
def keyed(n):return {(q['block'],q['replicate']):q for q in rows(P/('source055_'+n))}
def states():return {(q['block'],q['replicate'],q['geometry'],q['background']):q for q in rows(P/'source055_RESIDENT_STATES.jsonl.gz') if q['geometry'] in ('ZERO','HALF')}
def verify_references():
 refs=read('SOURCE_REFERENCES.json');assert sha(SOURCE/'DELIVERY_SHA256SUMS')==refs['delivery_manifest_sha256']
 for n,h in refs['files'].items():assert sha(SOURCE/n)==h,n
 for n,q in read('IMPLEMENTATION_MAP.json').items():assert sha(P/n)==q['sha256']==sha(P/q['source']),n
 return len(refs['files'])
def verify_manifest(name):
 for line in (P/name).read_text().splitlines():
  h,n=line.split('  ',1);assert sha(P/n)==h,n
