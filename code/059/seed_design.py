import hashlib
PREFIX='ORG-PULSE-059-r1'
BLOCK_FAMILIES=('continuation_innovations','continuation_copy')
FAMILIES=tuple('transfer_'+k for k in ('local','scout','ties','labels','fresh','survival'))
def seed(f,b,r):return int(hashlib.sha256(('%s|%s|%d|%d'%(PREFIX,f,b,r)).encode()).hexdigest()[:16],16)
def roster():
 coords=[(f,b,-1) for f in BLOCK_FAMILIES for b in range(24)]+[(f,b,r) for f in FAMILIES for b in range(24) for r in range(8)]+[('bootstrap',-1,-1)]
 return [dict(family=f,block=b,replicate=r,seed=seed(f,b,r),namespace='%s|%s|%d|%d'%(PREFIX,f,b,r)) for f,b,r in coords]
def verify_roster(rs,prior):
 vals=[q['seed'] for q in rs];assert rs==roster() and len(vals)==len(set(vals))==1201 and not set(vals)&set(prior)
 return True
