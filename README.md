
# Prolog implementation in Python

*Wanted: Better name*

While following the course ["Declarative Languages" at KULeuven](https://onderwijsaanbod.kuleuven.be/syllabi/e/H0N03AE.htm#activetab=doelstellingen_idm5137664) I got inspired to make a Prolog implementation in Python, while relying on Python's parser. This is the result:

```python
from logicpy import *
u, n = Universe().and_namespace()

n.parent[_.alice, _.bob] = True
n.parent[_.alice, _.charlie] = True
n.sibling[_.A, _.B] = n.parent(_.X, _.A) & n.parent(_.X, _.B) & (_.A != _.B)

u.simple_query(n.sibling(_.X, _.Y))
# returns [{'X': Atom('bob'), 'Y': Atom('charlie')},
#          {'X': Atom('charlie'), 'Y': Atom('bob')}]
```

There is also a kind of shell, which has some tricks so you can write your
queries more naturally. Use it through `u.interactive()`:

```
? parent(alice, Child)
{Child = bob};
{Child = charlie};
?
```

More examples can be found in the tests (`logicpy/tests.py`). There you will find more features:

  - **Evaluation of expressions (mainly math)**: I pulled a C++ for this and used the bitshift operators: `_.X << _.A * 2` will unify `X` with double of `A`, as long as `A` is instantiated.
  - **Cuts**: Just use `cut`
  - **Comparisons**: As you would expect.

## Why use it?

It has, obviously, perfect integration with Python. There are two main ways to integrate your functionality: 

  - As an 'evaluated' function: just use the `@evaluated` decorator (see the implementation of `max_` in `logicpy/builtin.py` for an example). Your code will be executed when we reach a `_.X << max_(...)`.
  - As a provable structure: subclass from `MonoArg` or `MultiArg` (or `Structure` if you really want), and implement the `prove(result, debugger)` method. Yield all results that you find ok.

## Why not use it?

I didn't add any metaprogramming, since this would logically be Python's job. There is no 'standard library'. There's still going to be a lot of bugs.

However, the biggest argument might be performance. It's pretty slow.

## How does it work?

  - Lots of generators for a Prolog-like runtime (works pretty well, see the backtracking implementation in `logicpy/builtin.py`!)
  - Some little hacky tricks to provide the interface (these are somewhat more brittle)
