
from logicpy.data import Term, Variable, BasicTerm, has_occurence, replace
from logicpy.debug import NoDebugger

class MartelliMontanariFail(Exception):
    pass


class Uninstantiated(Exception):
    pass


class Result:
    def __init__(self, it = None):
        self.var_cache = {}
        if it:
            self.identities = frozenset(it)
        else:
            self.identities = frozenset()
    
    # Act like a proper set ...............................
    
    # Binary operations
    # TODO: var_cache can be included in this to improve performance
    for fname in ['__and__', '__rand__', '__or__', '__ror__', '__xor__', '__rxor__', '__sub__', '__rsub__',
                  'intersection', 'difference', 'symmetric_difference', 'union']:
        def passthrough(self, other, f = getattr(frozenset, fname)):
            return Result(f(self.identities, other.identities if isinstance(other, Result) else other))
        locals()[fname] = passthrough
    
    def __len__(self):
        return len(self.identities)
    
    
    # Representation and easy usage ......................
    
    def __str__(self):
        if len(self) == 0:
            return 'ok'
        return '{' + ', '.join(f"{L} = {R}" for L, R in self.identities) + '}'
    
    def easy_dict(self):
        return {L.name: R for L, R in self.identities if isinstance(L, Variable) and L.scope == -1}
    
    
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
    
    def mgu(self, dbg=NoDebugger()):
        try:
            return Result(Result.martelli_montanari(set(self.identities)))
        except MartelliMontanariFail as e:
            dbg.output(f"MM failed: {e}")
            return None
    
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
            #print(f"unify {A!r}, {B!r}")
             
            if not isinstance(A, Variable) and isinstance(B, Variable):
                # switch
                E.add((B, A))
            elif isinstance(A, BasicTerm) and isinstance(B, BasicTerm):
                # peel
                if A.name == B.name and len(A.children) == len(B.children):
                    E.update(zip(A.children, B.children))
                else:
                    raise MartelliMontanariFail(f"Conflict {A}, {B}")
            elif isinstance(A, Variable) and A != B:
                # substitute
                if has_occurence(B, A):
                    raise MartelliMontanariFail(f"Occurs check {A}, {B}")
                # While elegant, this is somewhat slow...
                replaced_E = {(replace(X, A, B), replace(Y, A, B)) for (X,Y) in E}
                if E == replaced_E:
                    did_a_thing = False
                else:
                    E = replaced_E
                E.add((A, B))  # Add it back
            elif (not isinstance(A, (Structure, Term))) and (not isinstance(B, (Structure, Term))):
                if A != B:
                    raise MartelliMontanariFail(f"Constant Conflict {A}, {B}")
            else:
                did_a_thing = False
            
            if did_a_thing:
                tried.clear()
            else:
                # Add it back
                E.add((A, B))
                tried.add((A, B))
        
        return E
