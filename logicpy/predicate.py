
from collections import namedtuple

from logicpy.structure import Structure, MultiArg
from logicpy.builtin import True_, Fail, and_, or_, PredicateCut
from logicpy.result import Result, UnificationFail
from logicpy.data import with_scope, Variable


class PredicateNotFound(Exception):
    pass



class Signature(namedtuple('_Signature', ('name', 'arity'))):
    def __str__(self):
        return f"{self.name}/{self.arity}"
    
    __repr__ = __str__


class Clause:
    def __init__(self, name, args, body, univ):
        self.univ = univ
        self.signature = Signature(name, len(args))
        self.args = args
        self.body = True_ if body is True else body
        if self.body and self.univ:
            self.univ.define(self)
    
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
        # /1 or higher clauses
        self.del_if_new()
        if not isinstance(args, tuple): args = (args,)
        return Clause(self.signature.name, args, body, self.univ)
    
    def __call__(self, *args):
        # /1 or higher call
        self.del_if_new()
        return PredicateCall(self.univ, Signature(self.signature.name, len(args)), args)
        
    def prove(self, result, dbg):
        # Act like a PredicateCall (/0 structure)
        predcall = PredicateCall(self.univ, self.signature, ())
        return predcall.prove(Result(), dbg.next())


class Predicate:
    def __init__(self, signature):
        self.signature = signature
        self.clauses = []
    
    def add_clause(self, clause):
        self.clauses.append(clause)
    
    def __str__(self):
        return str(self.signature)
    
    def __repr__(self):
        return ";  ".join(map(repr, clauses))


class PredicateCall(MultiArg):
    def __init__(self, univ, signature, args):
        self.univ = univ
        self.signature = signature
        super().__init__(*args)
    
    def __str__(self):
        return f"{self.signature.name}({', '.join(map(str, self.args))})"
    
    def __repr__(self):
        return f"{self.signature.name}({', '.join(map(repr, self.args))})"
    
    def with_scope(self, scope):
        return PredicateCall(self.univ, self.signature, [with_scope(a, scope) for a in self.args])
    
    def prove(self, result, dbg):
        dbg.prove(self, result)
        pred = self.univ.get_pred(self.signature)
        
        if pred is None:
            raise PredicateNotFound(f"Couldn't find predicate with signature {self.signature}")
        else:
            try:
                for i, clause in enumerate(pred.clauses):
                    scope = self.scope_id()
                    structure = clause.body.with_scope(scope)
                    
                    arg_res = Result((with_scope(a, scope), b) for a, b in zip(clause.args, self.args))
                    try:
                        total_res = (arg_res | result).mgu()
                        dbg.output(f"Unified arguments for clause {i}")
                    except UnificationFail as e:
                        dbg.output(f"Failed to unify arguments for clause {i}: {e}")
                        continue
                    
                    relevant_res = Result((a, b) for a, b in total_res if (a,b) in arg_res or (isinstance(a, Variable) and a.scope == scope))
                    
                    clause_dbg = dbg.next()
                    clause_dbg.prove(clause, relevant_res)
                    
                    for new_res in structure.prove(relevant_res, dbg or clause_dbg.from_next()):
                        try:
                            mgu = (new_res | result | arg_res).mgu()
                            clause_dbg.proven(clause, mgu)
                            yield mgu
                        except UnificationFail as e:
                            clause_dbg.output(f"Failed to unify resulting sets: {e}")
            except PredicateCut:
                pass  # Look at how easy that is ;)
