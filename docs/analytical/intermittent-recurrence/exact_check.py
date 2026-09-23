from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
# Exhaustive finite-state probability calculations, not sampled populations.
M=4;n=2;length=6;records=[];checks=0
for q in [F(0),F(1,2),F(1)]:
 adjacent=[{} for _ in range(length-1)];lagtwo=[{} for _ in range(length-2)];total=F(0)
 for ts in product(range(M),repeat=length):
  p=F(1,M*M)
  for i in range(2,length):p*=q*int(ts[i]==ts[i-2])+(1-q)/M
  total+=p
  for i,t in enumerate(adjacent):key=ts[i:i+2];t[key]=t.get(key,F(0))+p
  for i,t in enumerate(lagtwo):key=(ts[i],ts[i+2]);t[key]=t.get(key,F(0))+p
 assert total==1;checks+=1
 for table in adjacent:
  for a,b in product(range(M),repeat=2):assert table[a,b]==F(1,M*M);checks+=1
 for table in lagtwo:
  for a,b in product(range(M),repeat=2):assert table[a,b]==(q*int(a==b)+(1-q)/M)/M;checks+=1
  mean=sum(p*bin(a^b).count('1') for (a,b),p in table.items());assert mean==F(n,2)*(1-q);checks+=1
 records.append(dict(copy_probability=str(q),probability_mass=str(total),target_sequences_enumerated=M**length,adjacent_expected_hamming=str(F(n,2)),lag_two_expected_hamming=str(F(n,2)*(1-q)),lag_two_exact_return_probability=str(q+(1-q)/M)))
result=dict(status='PASS',scope='Exact two-bit six-time target-law enumeration; no population paths, Monte Carlo, pseudorandom values or policy outcomes.',checks=checks,probability_cases=3,target_sequences_per_case=M**length,records=records,general_n32={'adjacent_mean_distance':'16 for every q','lag_two_mean_distance':'16*(1-q)','lag_two_exact_return_probability':'q+(1-q)/2^32'},scientific_population_paths=0,random_values_generated=0)
Path(__file__).with_name('RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
