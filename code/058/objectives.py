"""Fixed integer objectives; no fitted scales or outcome-dependent parameters."""
from accepted_model import Evaluator as BaseEvaluator
OBJECTIVES=('HAM','TRAP4')
TRAP=(1,2,3,4,0)
NIBBLE_LOSS=tuple(TRAP[4-bin(i).count("1")] for i in range(16))
def loss(x,t,objective):
 assert type(x)==int and type(t)==int and 0<=x<2**32 and 0<=t<2**32
 z=x^t
 if objective=='HAM':return bin(z).count("1")
 if objective=='TRAP4':return sum(NIBBLE_LOSS[(z>>(4*j))&15] for j in range(8))
 raise ValueError(objective)
class Evaluator(BaseEvaluator):
 def __init__(self,objective):
  assert objective in OBJECTIVES
  super().__init__();self.objective=objective
 def score(self,record,index):
  value=loss(record[0],self.target,self.objective)
  self.records.append(dict(candidate_index=index,genotype=record[0],raw_mismatch=value,objective=self.objective))
  self.calls+=1
  return value
SCHEMA={'raw_mismatch':'Selected objective integer raw loss, not necessarily Hamming mismatch.', 'raw_mismatches':'Selected objective losses; applies also to initial/candidate/penalized and donor fields.', 'raw_accuracies':'Normalized objective utility 1-mean(raw_loss)/32. TRAP4 is not matching-bit accuracy.'}
def annotate(record,objective):
 record['objective']=objective;record['score_schema']=SCHEMA
 return record
