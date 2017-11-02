
class NoDebugger:
    def prove(self, w, r):
        pass
    
    def output(self, text):
        pass
    
    def proven(self, w, r):
        pass
    
    def next(self):
        return self
    
    def from_next(self):
        return self
    
    def __bool__(self):
        return True


def truncate(s, length):
    if len(s) <= length:
        return s
    else:
        return s[:length-3] + "..."


class Debugger:
    def __init__(self, level=0, return_level=-1):
        self.level = level
        self.return_level = return_level
    
    def prove(self, what, res):
        padding = "   " * self.level
        print(padding + f"-> {type(what).__name__} {what} with\t {res}")
        
    def proven(self, what, res):
        padding = "   " * (self.return_level + 1)
        arrow = "---" * (self.level - self.return_level)
        arrow = "<" + arrow[1:-1] + " "
        print(padding + arrow + f"{type(what).__name__} {what} with\t {res}")
    
    def output(self, text):
        print(((self.level+1) * "   ") + text)
        
    def next(self):
        return type(self)(self.level + 1, self.return_level)
    
    def from_next(self):
        return type(self)(self.level + 1, self.level)
    
    def __bool__(self):
        # For `dbg or` tricks
        return False
    
