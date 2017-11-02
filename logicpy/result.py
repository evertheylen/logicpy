
from logicpy.data import Term, Variable, BasicTerm, has_occurence, replace
from logicpy.debug import NoDebugger

class ResultException(Exception):
    pass


class UnificationFail(ResultException):
    pass


class Uninstantiated(ResultException):
    pass


class Result:
    def __init__(self, it = None, var_cache = None):
        self.var_cache = var_cache or {}
        if it:
            self.identities = frozenset(it)
        else:
            self.identities = frozenset()
    
    # Act like a proper set ...............................
    
    # Binary operations
    # no __r*__ versions, PyPy doesn't know those
    for fname in ['__and__', '__xor__', '__sub__',
                  'intersection', 'difference', 'symmetric_difference', 'union']:
        def passthrough(self, other, f = getattr(frozenset, fname)):
            return type(self)(f(self.identities, other.identities if isinstance(other, Result) else other))
        locals()[fname] = passthrough
    
    def __or__(self, other):
        if isinstance(other, Result):
            # Often used, so let's write a faster version using var_cache
            overlap = self.var_cache.keys() & other.var_cache.keys()
            for var in overlap:
                if self.var_cache[var] != other.var_cache[var]:
                    return FailResult()
            
            total_var_cache = {**self.var_cache, **other.var_cache}
            total_identities = self.identities | other.identities
            return type(self)(total_identities, total_var_cache)
        else:
            return type(self)(self.identities | other)
    
    def __len__(self):
        return len(self.identities)
    
    def __iter__(self):
        return iter(self.identities)
    
    def __contains__(self, obj):
        return obj in self.identities
    
    
    # Representation and easy usage ......................
    
    def __str__(self):
        if len(self) == 0:
            return 'ok'
        return '{' + ', '.join(f"{L} = {R}" for L, R in self.identities) + '}'
    
    def easy_dict(self):
        return {L.name: R for L, R in self.identities if isinstance(L, Variable) and L.scope == 0}
    
    
    # Prolog additions ....................................
    
    def get_var(self, var):
        try:
            return self.var_cache[var]
        except KeyError:
            for A, B in self.identities:
                if A == var:
                    self.var_cache[var] = B
                    return B
        raise Uninstantiated(f"Uninstantiated: {var}")
    
    def mgu(self):
        return Result(Result.martelli_montanari(set(self.identities)))
    
    @staticmethod
    def martelli_montanari(E):
        from logicpy.structure import Structure
        
        if len(E) == 0:
            return E
        
        did_a_thing = True
        tried = set()
        
        while True:
            untried = E - tried
            if len(untried) == 0: break
            (A, B) = untried.pop()
            E.remove((A, B))
            did_a_thing = True  # Assume and unset later
             
            if not isinstance(A, Variable) and isinstance(B, Variable):
                # switch
                E.add((B, A))
            elif isinstance(A, BasicTerm) and isinstance(B, BasicTerm):
                # peel
                if A.name == B.name and len(A.children) == len(B.children):
                    E.update(zip(A.children, B.children))
                else:
                    raise UnificationFail(f"Conflict {A}, {B}")
            elif isinstance(A, Variable) and A != B:
                # substitute
                if has_occurence(B, A):
                    raise UnificationFail(f"Occurs check {A}, {B}")
                # While elegant, this is somewhat slow...
                replaced_E = {(replace(X, A, B), replace(Y, A, B)) for (X,Y) in E}
                if E == replaced_E:
                    did_a_thing = False
                else:
                    E = replaced_E
                E.add((A, B))  # Add it back
            elif (not isinstance(A, (Structure, Term))) and (not isinstance(B, (Structure, Term))):
                if A != B:
                    raise UnificationFail(f"Constant Conflict {A}, {B}")
            else:
                did_a_thing = False
            
            if did_a_thing:
                tried.clear()
            else:
                # Add it back
                E.add((A, B))
                tried.add((A, B))
        
        return E


class FailResult(Result):
    def mgu(self, dbg=NoDebugger()):
        dbg.output("Failure to unify was already detected")
        return None
