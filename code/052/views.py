from model import utilities

def view(row):
 r=row['record'];cfg=row['configuration']
 if isinstance(r['frequencies'],dict):return r['frequencies'],r['utilities']
 role=cfg[0];f=r['frequencies'];freq={'R':[1-x for x in f],'H':f if role=='H' else [0.]*41,'F':f if role=='F' else [0.]*41};return freq,utilities(r['raw_losses'],freq)
def prefix(rec):
 import json
 return json.dumps({k:rec[k][:n] for k,n in [('initial_queries',32),('initial_raw_mismatches',32),('populations',3),('raw_losses',3),('penalized_losses',3),('steps',2),('ground_truth',2)]},sort_keys=True,separators=(',',':'))
