"""Dispatch only: exact accepted045 fresh and accepted044 rare old policies."""
from accepted_rare_model import initial,sequence as private_sequence
from accepted_fresh_model import sequence as fresh_sequence,Policy,Evaluator,step
from analysis import MODES

def sequence(targets,draws,mode,fresh):
 assert mode in MODES
 return fresh_sequence(targets,draws,mode,fresh) if mode.startswith('NOVEL') else private_sequence(targets,draws,mode)
