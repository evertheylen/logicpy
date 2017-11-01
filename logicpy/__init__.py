
# Prolog:
#   parent(alice, bob).
#   parent(alice, charlie).
#   sibling(X, Y) :- parent(P, X), parent(P, Y).

# LogiPy:
#   from logipy import Universe, _
#   # terms: _.foo, Term('FOOOOBAR')
#   #   --> upcasted to Atom/Compound
#   # vars:  _.Bar, _._bar, Variable('quuz')
#   # unbound var: _
#  
#   
#   universe = Universe()
#   u = universe.definer()
#   u.parent[_.alice, _.bob] = True
#   u.parent[_.alice, _.charlie] = True
#   u.sibling[X, Y] = u.parent(P, X) & u.parent(_.P, _.Y)

from .core import Universe, Underscore
from .builtin import *

_ = Underscore()

__all__ = ('_', 'Universe', 'True_', 'Fail', 'and_', 'or_', 'max_', 'min_', 'abs_', 'evaluated')
