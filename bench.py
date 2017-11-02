
from logicpy import *
from logicpy.core import *
from logicpy.builtin import *
from logicpy.predicate import *
from logicpy.data import *

import time

u, n = Universe().and_namespace()

n.fib[0, 1] = True
n.fib[1, 2] = True
n.fib[_.N, _.Res] = and_(
    _.N > 1,
    _.N1 << _.N - 1,
    _.N2 << _.N - 2,
    n.fib(_.N1, _.Res1),
    n.fib(_.N2, _.Res2),
    _.Res << _.Res1 + _.Res2)

fib = lambda x: {0: 1, 1: 2, 2: 3}.get(x) or fib(x-1) + fib(x-2)

for arg in range(8):
    check = fib(arg)
    
    try:
        start = time.time()
        res = u.simple_query(n.fib(arg, _.X))[0]['X']
        end = time.time()
        
        assert check == res, f"{check} != {res}"
        print(f"{arg}\t{end - start}")
    except Exception as e:
        print("\nFAIL --------------------------------------------------")
        print(e, "\n")
        print(u.simple_query(n.fib(arg, _.X), debug=True))
        break
    

