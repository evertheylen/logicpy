
from collections import defaultdict, OrderedDict, namedtuple

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


# Basic abstractions
# ==================

# Meaning
# -------

# Builtin structures
# ------------------




# Terms, variables, basically data
# --------------------------------


# The Underscore
# --------------

class Underscore(NamedTerm):
    def __init__(self):
        super().__init__('_')
    
    def __getattr__(self, name):
        if name[0].isupper() or name[0] == '_':  # Variable
            return Variable(name)
        else:
            return Atom(name)  # Atom will create Compounds when needed
    

_ = Underscore()

