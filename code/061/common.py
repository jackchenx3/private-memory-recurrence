import pathlib,json,hashlib,time,gzip
from io_utils import sha
P=pathlib.Path(__file__).resolve().parent

def read(n):
 f=P/n
 if f.suffix=='.gz':
  with gzip.open(str(f),'rt') as src:return json.load(src)
 return json.loads(f.read_text())
def save(n,value):
 f=P/n;f.parent.mkdir(parents=True,exist_ok=True);tmp=f.with_name(f.name+'.tmp')
 if f.suffix=='.gz':
  with gzip.open(str(tmp),'wt',compresslevel=6) as out:json.dump(value,out,separators=(',',':'),allow_nan=False)
 else:tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
 tmp.replace(f)
def verify_manifest(n):
 for line in (P/n).read_text().splitlines():h,f=line.split('  ',1);assert sha(P/f)==h,f

def verify_references():
 for n,q in read('DEPENDENCY_HASHES.json').items():assert sha(P/n)==q['sha256']==sha(P/q['source']),n
 return 2

def manifest(n,names):
 names=sorted(names);(P/n).write_text(''.join(sha(P/f)+'  '+f+'\n' for f in names))
def package_bytes():return sum(f.stat().st_size for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts)
