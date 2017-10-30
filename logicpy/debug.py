
class NoDebugger:
    def prove(self, w, r):
        pass
    
    def output(self, text):
        pass
    
    def proven(self, w, r):
        pass
    
    def next(self):
        return self


def truncate(s, length):
    if len(s) <= length:
        return s
    else:
        return s[:length-3] + "..."


class Debugger:
    def __init__(self, level=1):
        self.level = level
    
    def prove(self, what, res):
        self.output(f"==> proving {type(what).__name__} ({truncate(str(what), 40)}) with {res}", -1)
        
    def proven(self, what, res):
        self.output(f"<== proven {type(what).__name__} ({truncate(str(what), 40)}) with {res}", -1)
    
    def output(self, text, relative_level=0):
        print(((self.level + relative_level) * "    ") + text)
        
    def next(self):
        return type(self)(self.level + 1)
