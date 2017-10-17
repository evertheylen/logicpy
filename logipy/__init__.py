
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
#   u.parent[_.alice, _.bob]
#   u.parent[_.alice, _.charlie]
#   u.sibling[X, Y] = u.parent(P, X) & u.parent(_.P, _.Y)


# Management stuff
# ----------------

class Universe:
    def __init__(self):
        self._predicates = {}
        
    def namespace(self):
        return Namespace(self)
    
    def and_namespace(self):
        return self, self.namespace()
    
    def define(self, clause):
        sig = clause.signature
        if sig not in self._predicates:
            self._predicates[sig] = Predicate(sig, clause.to_structure())
        else:
            print(sig)
            print(self._predicates)
            print(self._predicates[sig])
            print(self._predicates[sig].structure)
            self._predicates[sig] = Predicate(sig, self._predicates[sig].structure | clause.to_structure())
    
    def query(self, pred):
        pass
    
    def __str__(self):
        s = f"Universe with {len(self._predicates)} predicates:\n"
        s += "\n".join(f"  {k}:\n{v}" for k,v in self._predicates.items())
        return s


class Namespace:
    def __init__(self, univ):
        self.__dict__['_univ'] = univ
    
    def __getattr__(self, name):
        # getattr will cover the case of 'u.foo'
        # NoArgument covers the case of 'u.foo[bar]' and 'u.foo[bar] = quuz'
        return NoArgument(name, True, self._univ)
    
    def __setattr__(self, name, body):
        # setattr will cover the case of 'u.foo = bar'
        return NoArgument(name, body, self._univ)


class Underscore:
    def __getattr__(self, name):
        if name[0].isupper() or name[0] == '_':  # Variable
            return Variable(name)
        else:
            return Atom(name)  # Atom will create Compounds when needed


_ = Underscore()




# Basic abstractions
# ==================

# Meaning
# -------

class Structure:
    # builtin operators, see below
    
    def __and__(self, other):
        return and_(self, other)
    
    def __or__(self, other):
        return or_(self, other)
    
    def __eq__(self, other):
        return unify(self, other)


class Signature(namedtuple('_Signature', ('name', 'arity'))):
    def __str__(self):
        return f"{self.name}/{self.arity}"
    
    __repr__ = __str__


class Clause:
    def __init__(self, name, args, body, univ):
        self.univ = univ
        self.signature = Signature(name, len(args))
        self.args = args
        self.body = body
        if self.univ:
            self.univ.define(self)
    
    def to_structure(self):
        return and_(*(unify(Argument(i), arg) for i, arg in enumerate(self.args)), self.body)
    
    def __str__(self):
        return str(self.signature)
    
    def __repr__(self):
        return f"{self.signature.name}({', '.join(map(str, self.args))}) :- {self.body}"


class NoArgument(Clause):
    """ This class can be used in many ways. It is the biggest price we pay for not having
    our own parser. Here are examples of all six usages:
    
      1) u.one                      --> just a simple /0 base clause
      2) u.two = u.foobar           --> still a /0 clause, this time non-base
      3) u.three[foo]               --> /1 or higher base clause
      4) u.four[foo] = barr         --> /1 or higher non-base clause
      5) u.foo(X) = u.five          --> using as a /0 structure
      6) u.foo(X) = u.six(X)        --> using as a /1 structure
    
    The difference between 1 and 2 is made by Namespace. 3 and 4 are handled by __getitem__
    and __setitem__ respectively. Note that in 3 or 4, we're *also* using this class as
    1 and 2, but we don't want to redefine /0 base clauses everytime.
    
    5 and 6 are the most difficult
    """
    
    def __init__(self, name, body, univ):
        # Protection against too many /0 base clauses
        self.am_i_new = Signature(name, 0) not in univ._predicates
        Clause.__init__(self, name, (), body, univ)  # Covers 1 and 2
    
    def __getitem__(self, args):
        "Usecase 3"
        return self.__setitem__(args, True)
    
    def __setitem__(self, args, body):
        "Usecase 4"
        if self.am_i_new:
            # Remove the /0 variant since we're actually defining another arity
            del self.univ._predicates[self.signature]
        return Clause(self.signature.name, args, body, self.univ)

    def __call__(self, *args):
        "Usecase 6"
        return PredicateCall(self.univ._predicates[Signature(self.signature.name, len(args))])
        
    # TODO: act like a PredicateCall in case 5
    
    
class Predicate:
    def __init__(self, signature, structure):
        self.signature = signature
        self.structure = structure
    
    def __str__(self):
        return str(self.signature)
    
    def __repr__(self):
        return f"{self.signature.name}({', '.join(str(Argument(i)) for i in range(self.signature.arity))}"\
                    f":- {self.structure})"


class PredicateCall(Structure):
    def __init__(self, pred, args):
        self.pred = pred
        self.args = args
    
    def __str__(self):
        return f"{self.pred.signature.name}({', '.join(map(str, self.args))})"



# Builtin structures
# ------------------

class MultiArg(Structure):
    def __init__(self, *args):
        self.args = args
    
    def __str__(self):
        return f" {self.op} ".join(self.args)
    

class and_(MultiArg):
    op = '&'
    
    def __and__(self, other):
        self.args = self.args + (other,)


class or_(MultiArg):
    op = '|'
    
    def __or__(self, other):
        self.args = self.args + (other,)


class unify(Structure):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __str__(self):
        return f"{self.left} == {self.right}"


# Terms, variables, basically data
# --------------------------------


class Term:
    pass


class NamedTerm(Term):
    TERM_TYPE = 'Term'
    
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"
    
    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)


class Atom(NamedTerm):
    def __call__(self, *args):
        assert len(args) >= 1, "Creation of Compound needs at least 1 argument"
        return Compound(self.name, args)


class Compound(NamedTerm):
    def __init__(self, name, children):
        super().__init__(name)
        self.children = tuple(children)
    
    def __str__(self):
        return f"{self.name}({', '.join(map(str, self.children))})"
    
    def __repr__(self):
        return f"Compound({self.name!r}, {self.children!r})"
    
    def __eq__(self, other):
        return super().__eq__(other) and self.children == other.children
    
    def __hash__(self):
        return hash((self.name, self.children))
    

class Variable(NamedTerm):
    pass


class Argument(Variable):
    def __init__(self, num):
        self.num = num
        
    @property
    def name(self):
        return f"${self.num}"
    
    def __eq__(self, other):
        return type(self) == type(other) and self.num == other.num
    
    def __hash__(self):
        return hash((Argument, self.num))


class Constant(Term):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return repr(self.value)

