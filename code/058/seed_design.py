"""Namespace enumeration and hashing only; safe before RNG generation."""
import hashlib
PREFIX='ORG-LANDSCAPE-058-r1'
BLOCK_FAMILIES=('target_pair','policy_innovations','policy_copy','continuation_innovations','continuation_copy')
INITIAL_FAMILIES=tuple('initial_'+s for s in ('local','scout','ties','labels'))
POLICY_FAMILIES=tuple('policy_'+s for s in ('local','scout','ties','labels','fresh','survival'))
CONTINUATION_FAMILIES=tuple('continuation_'+s for s in ('local','scout','ties','labels','fresh','survival'))
def seed(f,b,r):return int(hashlib.sha256(('%s|%s|%d|%d'%(PREFIX,f,b,r)).encode()).hexdigest()[:16],16)
def roster():
 coords=[(f,b,-1) for f in BLOCK_FAMILIES for b in range(24)]+[(f,b,r) for f in INITIAL_FAMILIES+POLICY_FAMILIES+CONTINUATION_FAMILIES for b in range(24) for r in range(8)]+[('bootstrap',-1,-1)]
 return [dict(family=f,block=b,replicate=r,seed=seed(f,b,r),namespace='%s|%s|%d|%d'%(PREFIX,f,b,r)) for f,b,r in coords]
def verify_roster(rs,prior):
 vals=[q['seed'] for q in rs];assert rs==roster() and len(vals)==len(set(vals))==3193 and not set(vals)&set(prior)
 return True
