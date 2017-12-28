
from logicpy.predicate import Predicate, NoArgument
from logicpy.data import Variable, Atom, NamedTerm
from logicpy.builtin import Fail, unify, shell_builtins
from logicpy.result import Result
from logicpy.structure import Structure
from logicpy.debug import Debugger, NoDebugger
from logicpy.util.getch import getch


class Universe:
    def __init__(self):
        self._predicates = {}
        
    def namespace(self):
        return Namespace(self)
    
    def and_namespace(self):
        return self, self.namespace()
    
    def define(self, clause):
        sig = clause.signature
        pred = self._predicates.setdefault(sig, Predicate(sig))
        pred.add_clause(clause)
    
    def get_pred(self, sig):
        if sig in self._predicates:
            return self._predicates[sig]
        else:
            return None
    
    def query(self, struc, *, debug=False):
        struc = struc.with_scope(0)
        yield from struc.prove(Result(), Debugger() if debug else NoDebugger())
    
    def simple_query(self, struc, limit=None, **kwargs):
        q = self.query(struc, **kwargs)
        if limit is None:
            return [res.easy_dict() for res in q]
        else:
            return [next(q).easy_dict() for i in range(limit)]
    
    def ok(self, struc, **kwargs):
        for b in self.query(struc, **kwargs):
            return True
        return False
    
    def interactive(self):
        namespace = self.namespace()
        underscore = Underscore()
        
        import logicpy.builtin
        builtins = {k: getattr(logicpy.builtin, k) for k in shell_builtins}
        
        class InteractiveLocals:
            def __getitem__(glob, name):
                if name in builtins:
                    return builtins[name]
                elif name in namespace:
                    return getattr(namespace, name)
                else:
                    return getattr(underscore, name)
        
        shell_locals = InteractiveLocals()
        
        while True:
            try:
                inp = input("? ")
                struc = eval(inp, {}, shell_locals)
                #print(f">>> got {struc!r}")
                if hasattr(struc, 'prove'):
                    for res in self.query(struc):
                        print(res, end='', flush=True)
                        char = getch()
                        print(char)
                        if char in '\n.':
                            break
                        elif char == ';':
                            pass
                        else:
                            print(f"Press ';' for more solutions, '.' or Enter to stop")
                else:
                    print(f"Not a provable structure: {struc}")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def __str__(self):
        return f"Universe with {len(self._predicates)} predicates:\n  "\
            + "\n  ".join(f"{k}: {v!r}" for k,v in self._predicates.items())


class Namespace:
    def __init__(self, univ):
        self.__dict__['_univ'] = univ
        self.__dict__['_names'] = {sig.name for sig, pred in univ._predicates.items()}
    
    def __contains__(self, name):
        return name in self._names
    
    def __getattr__(self, name):
        # getattr will cover the case of 'u.foo'
        # NoArgument covers the case of 'u.foo[bar]' and 'u.foo[bar] = quuz'
        return NoArgument(name, None, self._univ)
    
    def __setattr__(self, name, body):
        # setattr will cover the case of 'u.foo = bar'
        return NoArgument(name, body, self._univ)


class Underscore(NamedTerm):
    def __init__(self, name='_', been_scoped=False):
        super().__init__(name, been_scoped)
    
    def with_scope(self, scope):
        # Just create a random variable
        return Variable("_", Structure.scope_id())
    
    def __getattr__(self, name):
        if name[0].isupper() or name[0] == '_':  # Variable
            return Variable(name)
        else:
            return Atom(name)  # Atom will create Compounds when needed

