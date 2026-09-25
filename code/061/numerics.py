"""Fixed80-digit solve, ties-even60-place grid, exact arbitrary-integer residual."""
from decimal import Decimal,localcontext,ROUND_HALF_EVEN,ROUND_FLOOR,ROUND_CEILING
from fractions import Fraction
PRECISION=80
GRID_DIGITS=60
ALPHA=Fraction(1,3774873600)
CRITERION=Fraction(1,10**30)

def rational(x):
 x=Fraction(x);return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def from_rational(q):return Fraction(int(q['numerator']),int(q['denominator']))
def decimal_string(x,rounding=ROUND_HALF_EVEN):
 x=Fraction(x)
 with localcontext() as ctx:
  ctx.prec=80;ctx.rounding=rounding
  return str(Decimal(x.numerator)/Decimal(x.denominator))

def solve(A,D):
 n=len(A);assert n>0 and all(len(r)==n and sum(r)==D for r in A)
 with localcontext() as ctx:
  ctx.prec=PRECISION;ctx.rounding=ROUND_HALF_EVEN
  # The first n-1 transposed stationary equations, followed by sum(x)=1.
  M=[[Decimal(A[j][i]-(D if i==j else 0)) for j in range(n)]+[Decimal(0)] for i in range(n-1)]+[[Decimal(1)]*n+[Decimal(1)]]
  pivots=[]
  for c in range(n):
   pivot=max(range(c,n),key=lambda r:(abs(M[r][c]),-r));assert M[pivot][c]!=0,'Singular fixed stationary system';pivots.append(pivot);M[c],M[pivot]=M[pivot],M[c]
   for i in range(c+1,n):
    if M[i][c]==0:continue
    factor=M[i][c]/M[c][c];M[i][c]=Decimal(0)
    for j in range(c+1,n+1):M[i][j]-=factor*M[c][j]
  x=[Decimal(0)]*n
  for i in range(n-1,-1,-1):x[i]=(M[i][n]-sum((M[i][j]*x[j] for j in range(i+1,n)),Decimal(0)))/M[i][i]
  total=sum(x,Decimal(0));assert total>0,'Nonpositive Decimal normalization';x=[v/total for v in x]
  # Preserve diagnostics even if a component is rejected by the caller.
  return dict(precision_digits=80,grid_digits=60,normalized_decimal=[str(v) for v in x],pivots=pivots)

def rounded_weights(solution):
 assert solution['precision_digits']==80 and solution['grid_digits']==60
 with localcontext() as ctx:
  ctx.prec=80;ctx.rounding=ROUND_HALF_EVEN;x=[Decimal(v) for v in solution['normalized_decimal']]
  if any(v<0 for v in x):raise ValueError('Negative computed component; rejected without clipping')
  scale=Decimal(10)**60;k=[int((v*scale).to_integral_value(rounding=ROUND_HALF_EVEN)) for v in x]
  if min(k)<0 or sum(k)<=0:raise ValueError('Negative rounded component or zero total; rejected')
  return k

def certify(A,D,k,alpha=ALPHA):
 assert len(A)==len(k) and all(type(v)==int and v>=0 for v in k);K=sum(k);assert K>0 and alpha>0
 R=sum(abs(sum(k[i]*A[i][j] for i in range(len(k)))-k[j]*D) for j in range(len(k)));r=Fraction(R,K*D);E=min(Fraction(1),r/alpha)
 return dict(K=str(K),R=str(R),residual=rational(r),alpha=rational(alpha),total_variation_bound=rational(E),criterion=rational(CRITERION),criterion_pass=r<=CRITERION,arithmetic='Python arbitrary-precision integers and reduced rational fractions; no64-bit matrix square')
