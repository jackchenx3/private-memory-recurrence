"""Prospective state index and fixed catalog only, no production kernel or vector."""
from common import *
from kernel import decode,L,D,KERNELS,AUDIT_ROWS
from outcomes import KEYS,PRIMARY

def main():
 assert not (P/'SOURCE_SHA256SUMS').exists();brief=read('DESIGN_CHECK.json');assert brief['D']==D and brief['L']==L and brief['outcome_keys']==list(KEYS)
 save('STATE_INDEX.json',dict(encoding='g0+2*c0+4*h0+8*g1+16*c1+32*h1+64*a+128*b',states=[dict(id=i,g0=decode(i)[0],c0=decode(i)[1],h0=decode(i)[2],g1=decode(i)[3],c1=decode(i)[4],h1=decode(i)[5],a=decode(i)[6],b=decode(i)[7]) for i in range(256)]))
 save('config.json',dict(task_id='ORG-STATIONARY-061',revision=1,task_sha256=sha(P/'ASSIGNMENT.md'),kernels=KERNELS,states=256,population_size=2,bits=1,local_flip_probability='1/4',policy_flip_probability='1/16',recurrence=['0','1/2'],candidate_slots=8,L=L,D=D,branches_per_row=28672,branches_per_kernel=7340032,literal_branches_total=29360128,transition_numerators=262144,stationary_entries=1024,decimal_precision=80,rounding_grid_digits=60,rounding='ties_to_even',residual_criterion='1/10^30',two_step_entry_lower_bound='1/966367641600',alpha='1/3774873600',outcomes=14,primary=PRIMARY,audit_rows=AUDIT_ROWS,audit_numerators=8192,resources=dict(cpus=1,memory_GiB=4,minutes=30,partition='norm'),timeout_seconds=1770,max_production_allocations=1,delivery_budget_bytes=64*1024*1024,simulation_paths=0,seeds=0,bootstrap_rows=0,main_figures=1))
 save('OUTCOME_CATALOG.json',dict(keys=KEYS,primary=PRIMARY,prediction='positive',uncertainty='numerical certification; no statistical intervals'))
 print('256state index and14keys fixed; no production matrix, vector or contrast computed')
if __name__=='__main__':main()
