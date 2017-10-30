

class Term:
    def set_scope(self, scope):
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
    
    def has_occurence(self, var):
        return False  # by default
    
    def occurences(self, O):
        pass
    
    def replace(self, A, B):
        if self == A:
            return B
        else:
            return self


class BasicTerm(NamedTerm):
    pass

class Atom(BasicTerm):
    def __call__(self, *args):
        assert len(args) >= 1, "Creation of Compound needs at least 1 argument"
        return Compound(self.name, args)
    
    children = []


class Compound(BasicTerm):
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
    
    def has_occurence(self, var):
        return any(c.has_occurence(var) for c in self.children)
    
    def occurences(self, O):
        for c in self.children:
            c.occurences(O)
    
    def replace(self, A, B):
        new_children = tuple((B if c == A else c.replace(A, B)) for c in self.children)
        return Compound(self.name, new_children)
    
    def set_scope(self, scope):
        for c in self.children:
            c.set_scope(scope)


class Variable(NamedTerm):
    def __init__(self, name, scope=None):
        self.name = name
        self.scope = scope
    
    def __repr__(self):
        return f"Variable({self.name!r}, {id(self.scope)})"
    
    def __eq__(self, other):
        # Variables are scoped!
        return super().__eq__(other) and self.scope == other.scope
    
    def __hash__(self):
        return hash((self.name, self.scope))
    
    def has_occurence(self, var):
        return self == var
    
    def occurences(self, O):
        O.add(self)
    
    def set_scope(self, scope):
        self.scope = scope


class Argument(Variable):
    def __init__(self, num, scope):
        self.num = num
        self.scope = scope  # scope is always needed for arguments!
        
    @property
    def name(self):
        return f"${self.num}"
    
    def __eq__(self, other):
        return type(self) == type(other) and self.num == other.num and self.scope == other.scope
    
    def __hash__(self):
        return hash((self.num, self.scope))


class Constant(Term):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return repr(self.value)


