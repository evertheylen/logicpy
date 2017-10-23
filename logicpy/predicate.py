
from collections import namedtuple

from logicpy.structure import Structure, MultiArg
from logicpy.builtin import True_, and_, unify
from logicpy.data import Argument


class Signature(namedtuple('_Signature', ('name', 'arity'))):
    def __str__(self):
        return f"{self.name}/{self.arity}"
    
    __repr__ = __str__


class Clause:
    def __init__(self, name, args, body, univ):
        self.univ = univ
        self.signature = Signature(name, len(args))
        self.args = args
        for a in args: a.set_scope(self)
        self.body = True_ if body is True else body
        if self.body:
            self.body.set_scope(self)
            if self.univ:
                self.univ.define(self)
    
    def to_structure(self):
        return and_(*[unify(Argument(i, self.signature), arg) for i, arg in enumerate(self.args)], self.body)
    
    def __str__(self):
        return str(self.signature)
    
    def __repr__(self):
        return f"{self.signature.name}({', '.join(map(str, self.args))}) :- {self.body}"


class NoArgument(Clause, Structure):
    """ This class can be used in many ways. It is the biggest price we pay for not having
    our own parser. Here are examples of all usages:
    
      1) u.one = ...                --> /0 clause
      2) u.three[foo] = ...         --> /1 or higher clause
      3) u.foobar = u.five          --> usage of /0 clause
      4) u.foobar[A] = u.six(A)     --> usage of /1 or higher clause
    
    """
    
    def __init__(self, name, body, univ):
        # Protection against unwanted /0 base clauses
        self.am_i_new = Signature(name, 0) not in univ._predicates and body is not None
        Clause.__init__(self, name, (), body, univ)  # Covers 1 and 2 (/0 clauses)
    
    def del_if_new(self):
        if self.am_i_new:
            # Remove the /0 variant since we're actually defining another arity
            del self.univ._predicates[self.signature]
    
    def __setitem__(self, args, body):
        # Usecase 3: /1 or higher clauses
        self.del_if_new()
        if not isinstance(args, tuple): args = (args,)
        return Clause(self.signature.name, args, body, self.univ)
    
    def __call__(self, *args):
        # Usecase 6: /1 or higher call
        self.del_if_new()
        return PredicateCall(self.univ, Signature(self.signature.name, len(args)), args)
        
    def prove(self, bindings):
        # Usecase 5: act like a PredicateCall (/0 structure)
        # Luckily, we don't need weird inheritance tricks, since it's really pretty damn easy
        return self.univ.get_pred_body(self.signature).prove({})


class Predicate:
    def __init__(self, signature, structure):
        self.signature = signature
        self.structure = structure
    
    def __str__(self):
        return str(self.signature)
    
    def __repr__(self):
        return f"{self.signature.name}({', '.join(str(Argument(i, None)) for i in range(self.signature.arity))})"\
                    f" :- {self.structure}"


class PredicateCall(MultiArg):
    def __init__(self, univ, signature, args):
        self.univ = univ
        self.signature = signature
        super().__init__(*args)
    
    def __str__(self):
        return f"{self.signature.name}({', '.join(map(str, self.args))})"
    
    def prove(self, bindings):
        # TODO: limiting the bindings to only the pieces that are needed
        # will improve performance of unification (a lot?)
        body = self.univ.get_pred_body(self.signature)
        new_bindings = {**bindings, **{Argument(i, self.signature): a for i, a in enumerate(self.args)}}
        return body.prove(new_bindings)
    
