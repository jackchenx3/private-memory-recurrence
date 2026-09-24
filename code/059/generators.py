def local_masks(rng):
 out=[]
 for g in range(40):
  row=[]
  for i in range(32):
   mask=0
   for bit in range(32):
    if rng.randrange(32)==0:mask|=1<<bit
   row.append(mask)
  out.append(row)
 return out

def scouts(rng):return [[rng.getrandbits(32) for i in range(32)] for g in range(40)]
def ties(rng):return [[rng.random() for j in range(128)] for g in range(40)]
def labels(rng):a=list(range(32));rng.shuffle(a);return a
def bootstrap(rng):return [[rng.randrange(24) for b in range(24)] for r in range(2000)]

def build_targets(pair,innovations,copy,law):
 assert law in ('ZERO','HALF','FULL') and len(pair)==2 and len(innovations)==len(copy)==38 and all(c in (0,1) for c in copy)
 ts=list(pair)
 for j,z in enumerate(innovations):ts.append(ts[-2] if law=='FULL' or law=='HALF' and copy[j] else z)
 return ts

