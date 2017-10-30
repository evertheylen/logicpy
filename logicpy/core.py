
from logicpy.predicate import Predicate, NoArgument
from logicpy.data import Variable, Atom, NamedTerm
from logicpy.builtin import Fail, unify
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
        if sig not in self._predicates:
            self._predicates[sig] = Predicate(sig, clause.to_structure())
        else:
            self._predicates[sig] = Predicate(sig, self._predicates[sig].structure | clause.to_structure())
    
    def get_pred_body(self, sig):
        if sig in self._predicates:
            return self._predicates[sig].structure
        else:
            return Fail
    
    def query(self, struc, *, debug=False):
        for res in struc.prove(Result(), Debugger() if debug else NoDebugger()):
            res = res.mgu()
            if res is not None:
                yield res
    
    def simple_query(self, struc, **kwargs):
        return [res.easy_dict() for res in self.query(struc, **kwargs)]
    
    def interactive(self):
        namespace = self.namespace()
        underscore = Underscore()
        
        class InteractiveLocals:
            def __getitem__(glob, name):
                if name in namespace:
                    return getattr(namespace, name)
                else:
                    return getattr(underscore, name)
        
        shell_locals = InteractiveLocals()
        
        while True:
            try:
                inp = input("? ")
                struc = eval(inp, {}, shell_locals)
                if hasattr(struc, 'prove'):
                    for res in struc.prove(Result()):
                        print(res)
                        char = getch()
                        if char in '\n.':
                            break
                        elif char == ';':
                            continue
                        else:
                            print(f"Unknown action '{char}'")
                else:
                    print(f"Not a provable structure: {struc}")
            except EOFError:
                break
            except Exception as e:
                print("Error: {e}")
    
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
    def __init__(self):
        super().__init__('_')
    
    def __getattr__(self, name):
        if name[0].isupper() or name[0] == '_':  # Variable
            return Variable(name)
        else:
            return Atom(name)  # Atom will create Compounds when needed

