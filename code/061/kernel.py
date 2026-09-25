"""Literal exact256-state mathematical kernel, independent of the32-bit simulator."""
import itertools,math
L=1441440
D=377864847360
KERNELS=('ACTIVE_ZERO','ACTIVE_HALF','NEUTRAL_ZERO','NEUTRAL_HALF')
AUDIT_ROWS=(0,36,85,113,142,170,219,255)
PAIRS=tuple(itertools.product((0,1),repeat=2))

def decode(s):
 assert type(s)==int and 0<=s<256
 return tuple((s>>j)&1 for j in range(8))
def encode(bits):
 assert len(bits)==8 and all(x in (0,1) for x in bits)
 return sum(x<<j for j,x in enumerate(bits))
def target_num(a,e,law):
 assert law in ('ZERO','HALF');return 2 if law=='ZERO' else 3 if a==e else 1

def candidates(s,e,u,scout,local,mode):
 assert mode in ('ACTIVE','NEUTRAL');g0,c0,h0,g1,c1,h1,a,b=decode(s);gs=(g0,g1);cs=(c0,c1);hs=(h0,h1)
 probes=tuple(cs[i] if mode=='ACTIVE' and hs[i] else u[i] for i in range(2))
 donor=tuple(e if e in (gs[i],probes[i],scout[i]) else 1-e for i in range(2))
 child=tuple(donor[i]^local[i] for i in range(2))
 parent=(s&7,(s>>3)&7)
 def born(i,x):return x+2*gs[i]+4*hs[i]
 return parent+tuple(born(i,probes[i]) for i in range(2))+tuple(born(i,scout[i]) for i in range(2))+tuple(born(i,child[i]) for i in range(2))

def row(s,name):
 mode,law=name.split('_');assert name in KERNELS;bits=decode(s);a,b=bits[6:];out=[0]*256
 for e in (0,1):
  target=target_num(a,e,law);tail=64*b+128*e
  for u in PAIRS:
   for scout in PAIRS:
    for local in PAIRS:
     local_num=(3 if local[0]==0 else 1)*(3 if local[1]==0 else 1);pool=candidates(s,e,u,scout,local,mode);weights=[2 if p&1==e else 1 for p in pool];W=sum(weights)
     for j in range(8):
      factor=target*local_num*weights[j]*(L//(W*(W-weights[j])))
      for k in range(8):
       if k==j:continue
       mass=factor*weights[k];base=pool[j]+8*pool[k]+tail
       # Exact expansion of four independent policy-flip outcomes; no slot aggregation.
       out[base]+=225*mass;out[base^4]+=15*mass;out[base^32]+=15*mass;out[base^36]+=mass
 assert sum(out)==D and all(type(x)==int and 0<=x<=D for x in out)
 return out

def matrix(name):return [row(s,name) for s in range(256)]

def support_checks(A):
 n=len(A);edges=[[j for j,v in enumerate(row) if v] for row in A];reverse=[[i for i in range(n) if A[i][j]] for j in range(n)]
 def reach(graph):
  seen={0};pending=[0]
  while pending:
   i=pending.pop()
   for j in graph[i]:
    if j not in seen:seen.add(j);pending.append(j)
  return seen
 assert len(reach(edges))==len(reach(reverse))==n,'Support is not strongly connected'
 distance={0:0};pending=[0]
 for i in pending:
  for j in edges[i]:
   if j not in distance:distance[j]=distance[i]+1;pending.append(j)
 period=0
 for i in range(n):
  for j in edges[i]:period=math.gcd(period,abs(distance[i]+1-distance[j]))
 assert period==1,'Aperiodicity contradicts the specified constructive argument'
 return dict(strongly_connected_classes=1,period=period,positive_entries=sum(len(x) for x in edges),positive_diagonal=sum(A[i][i]>0 for i in range(n)))

def check_matrix(A,name):
 assert len(A)==256 and all(len(r)==256 and sum(r)==D and all(type(x)==int and 0<=x<=D for x in r) for r in A)
 for i in range(256):
  for j in range(256):
   assert A[i][j]==A[i^219][j^219],('global_bit_symmetry',name,i,j)
   if name.startswith('NEUTRAL'):assert A[i][j]==A[i^36][j^36],('neutral_label_symmetry',name,i,j)
 return dict(status='PASS',normalization='integer row sums exactly D',global_complement_entries=65536,neutral_label_entries=65536 if name.startswith('NEUTRAL') else 0,support=support_checks(A))
