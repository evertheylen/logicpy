
from logicpy.predicate import Predicate, NoArgument
from logicpy.data import Variable, Atom


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
            self._predicates[sig] = Predicate(sig, self._predicates[sig].structure | clause.to_structure())
    
    def get_pred_body(self, sig):
        if sig in self._predicates:
            return self._predicates[sig].structure
        else:
            return Fail
    
    def query(self, struc):
        res = list(struc.prove({}))
        vars = set()
        struc.occurences(vars)
        return [{k: v for k, v in binding.items() if any(k.has_occurence(V) or v.has_occurence(V) for V in vars)}
                for bindings in res] 
    
    def ok(self, struc):
        for b in struc.prove({}):
            return True
        return False
    
    def __str__(self):
        return f"Universe with {len(self._predicates)} predicates:\n  "\
            + "\n  ".join(f"{k}: {v!r}" for k,v in self._predicates.items())


class Namespace:
    def __init__(self, univ):
        self.__dict__['_univ'] = univ
    
    def __getattr__(self, name):
        # getattr will cover the case of 'u.foo'
        # NoArgument covers the case of 'u.foo[bar]' and 'u.foo[bar] = quuz'
        return NoArgument(name, None, self._univ)
    
    def __setattr__(self, name, body):
        # setattr will cover the case of 'u.foo = bar'
        return NoArgument(name, body, self._univ)


class Underscore(NamedTerm):
    def __init__(self):
        super().__init__('_')
    
    def __getattr__(self, name):
        if name[0].isupper() or name[0] == '_':  # Variable
            return Variable(name)
        else:
            return Atom(name)  # Atom will create Compounds when needed
    

_ = Underscore()

