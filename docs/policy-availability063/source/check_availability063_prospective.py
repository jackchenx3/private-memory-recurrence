"""Constructed exact fixtures only; no scientific input is accessed."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import json, datetime, hashlib

checks = 0
def check(value):
    global checks
    assert value
    checks += 1
alpha = F(31,256)
def fixture(beta, mix):
    matrix = [[1-alpha, alpha*mix, alpha*(1-mix)],
              [beta, (1-beta)*mix, (1-beta)*(1-mix)],
              [beta, (1-beta)*mix, (1-beta)*(1-mix)]]
    p = [beta/(alpha+beta), alpha*mix/(alpha+beta), alpha*(1-mix)/(alpha+beta)]
    check(all(sum(row)==1 and all(x>0 for x in row) for row in matrix))
    check(sum(p)==1 and all(sum(p[i]*matrix[i][j] for i in range(3))==p[j] for j in range(3)))
    b = p[0]; entry=alpha*b; exit=sum(p[i]*matrix[i][0] for i in (1,2))
    check(entry==exit)
    check(b/entry==1/alpha)
    check((1-b)/entry==1/beta)
    for delta in [F(-1,10000),F(0),F(1,10000)]:
        phat = [p[0]+delta,p[1]-delta,p[2]]
        error = abs(delta)
        check(all(x>0 for x in phat))
        fin=alpha*phat[0]; fout=sum(phat[i]*matrix[i][0] for i in (1,2))
        residual=sum(phat[i]*sum(matrix[i][j] for j in (1,2)) for i in range(3))-(1-phat[0])
        check(fin-fout==residual)
        f=lambda x:(1-x)/(alpha*x)
        lo,hi=f(phat[0]+error),f(phat[0]-error)
        check(lo<=1/beta<=hi)
        with localcontext() as ctx:
            ctx.prec=80; ctx.rounding=ROUND_FLOOR
            dlo=Decimal(lo.numerator)/Decimal(lo.denominator)
            ctx.rounding=ROUND_CEILING
            dhi=Decimal(hi.numerator)/Decimal(hi.denominator)
        check(F(dlo)<=lo<=hi<=F(dhi))
    return sum(p[i]*F(i,2) for i in range(3)), 1/beta

for beta in [F(1,8),F(1,4),F(1,2)]:
    for mix in [F(1,4),F(3,4)]: fixture(beta,mix)
h1,l1=fixture(alpha/2,F(9,10));h2,l2=fixture(alpha,F(1,10))
check(h2>h1 and l2<l1)
for a,b,c,d in [(F(4),F(3),F(2),F(1)),(F(3),F(4),F(2),F(1)),(F(5),F(1),F(2),F(3))]:
    check((a-b)-(c-d)==(a-c)-(b-d))
for lo,hi,want in [(F(1),F(2),'positive'),(F(-2),F(-1),'negative'),(F(0),F(0),'exact_zero'),(F(-1),F(1),'uncertified')]:
    got='positive' if lo>0 else 'negative' if hi<0 else 'exact_zero' if lo==hi==0 else 'uncertified'
    check(got==want)
R=Path(__file__).resolve().parents[1]
receipt=R/'outputs/coordination/tasks/ORG-AVAILABILITY-063-PROSPECTIVE_CHECK.json'
data={'status':'PASS','exact_checks':checks,'fixture_chains':8,
      'higher_frequency_shorter_availability_example':True,'study061_files_read':0,
      'new_production_values_seen':False,'stationary_solves':0,
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with receipt.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
print(json.dumps(data,indent=2))
