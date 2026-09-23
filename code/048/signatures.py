import json

def canonical(q):return json.loads(json.dumps(q))
def prefix(r,n=2):return canonical(dict(initial_queries=r['initial_queries'],initial_raw_mismatches=r['initial_raw_mismatches'],populations=r['populations'][:n+1],raw_losses=r['raw_losses'][:n+1],penalized_losses=r['penalized_losses'][:n+1],frequencies=r['frequencies'][:n+1],steps=r['steps'][:n],ground_truth=r['ground_truth'][:n]))
def first(r):
 q=prefix(r,1)
 for s in q['steps']:s.pop('probe_access');s.pop('radius_probe',None)
 return q

def numeric(r):
 return dict(population_genotypes=[[p[0] for p in pop] for pop in r['populations']],initial_queries=r['initial_queries'],raw_losses=r['raw_losses'],penalized_losses=r['penalized_losses'],steps=[dict(candidate_genotypes=[p[0] for p in s['candidates']],raw=s['candidate_raw_mismatches'],pen=s['candidate_penalized_mismatches'],queries=s['query_records'],donors=s['donor_choices'],selected_indices=s['selected_indices']) for s in r['steps']])
