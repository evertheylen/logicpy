
def binary_compounder(name):
    def operation(self, other):
        return InfixCompound(name, (self, other))
    return operation


def unary_compounder(name):
    def operation(self):
        return PrefixCompound(name, (self,))
    return operation


class Term:
    def __init__(self, been_scoped=False):
        self.been_scoped = been_scoped
    
    def with_scope(self, scope):
        if self.been_scoped:
            return self
        else:
            return type(self)(been_scoped=True)
    
    # Some operand support
    __add__ = __radd__ = binary_compounder('+')
    __sub__ = __rsub__ = binary_compounder('-')
    __mul__ = __rmul__ = binary_compounder('*')
    __div__ = __rdiv__ = binary_compounder('/')
    __floordiv__ = __rfloordiv__ = binary_compounder('//')
    __mod__ = __rmod__ = binary_compounder('%')
    __matmul__ = __rmatmul__ = binary_compounder('@')
    __pow__ = __rpow__ = binary_compounder('**')
    
    __pos__ = unary_compounder('+')
    __neg__ = unary_compounder('-')
    
    
    # TODO: comparisons
    
    def __lshift__(self, other):
        "Replaces is in Prolog"
        from logicpy.builtin import Eval
        return Eval(self, other)
    
    def __rshift__(self, other):
        from logicpy.builtin import Eval
        return Eval(other, self)
    
    def __eq__(self, other):
        from logicpy.builtin import unify
        if self.been_scoped:
            return self.really_equal(other)
        else:
            return unify(self, other)


class NamedTerm(Term):
    TERM_TYPE = 'Term'
    
    def __init__(self, name, been_scoped=False):
        super().__init__(been_scoped)
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"
    
    def really_equal(self, other):
        return type(self) == type(other) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def has_occurence(self, var):
        return False  # by default
    
    def occurences(self, O):
        pass
    
    def replace(self, A, B):
        if self == A:
            return B
        else:
            return self
    
    def with_scope(self, scope):
        if self.been_scoped:
            return self
        else:
            return type(self)(self.name, been_scoped=True)


class BasicTerm(NamedTerm):
    pass


class Atom(BasicTerm):
    def __call__(self, *args):
        assert len(args) >= 1, "Creation of Compound needs at least 1 argument"
        return Compound(self.name, args)
    
    children = []


class Compound(BasicTerm):
    def __init__(self, name, children, been_scoped=False):
        super().__init__(name, been_scoped)
        self.children = tuple(children)
    
    def __str__(self):
        return f"{self.name}({', '.join(map(str, self.children))})"
    
    def __repr__(self):
        return f"Compound({self.name!r}, {self.children!r})"
    
    def really_equal(self, other):
        return self.name == other.name and self.children == other.children
    
    def __hash__(self):
        return hash((self.name, self.children))
    
    def has_occurence(self, var):
        return any(c.has_occurence(var) for c in self.children)
    
    def occurences(self, O):
        for c in self.children:
            c.occurences(O)
    
    def replace(self, A, B):
        new_children = tuple((B if c == A else c.replace(A, B)) for c in self.children)
        return Compound(self.name, new_children)
    
    def with_scope(self, scope):
        return Compound(self.name, tuple(c.with_scope(scope) for c in self.children), been_scoped=True)


class InfixCompound(Compound):
    def __str__(self):
        return '(' + f" {self.name} ".join(map(str, self.children)) + ')'


class PrefixCompound(Compound):
    def __str__(self):
        return self.name + " ".join(map(str, self.children))


class Variable(NamedTerm):
    def __init__(self, name, scope=None):
        super().__init__(name, scope is not None)
        self.name = name
        self.scope = scope
    
    def __repr__(self):
        if self.scope:
            return f"Variable({self.name!r}, {self.scope % 97})"
        else:
            return f"Variable({self.name!r})"
    
    def really_equal(self, other):
        return self.name == other.name and self.scope == other.scope
    
    def __hash__(self):
        return hash((self.name, self.scope))
    
    def has_occurence(self, var):
        return self == var
    
    def occurences(self, O):
        O.add(self)
    
    def with_scope(self, scope):
        return Variable(self.name, scope)

