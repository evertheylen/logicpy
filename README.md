
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

It has, obviously, perfect integration with Python. There are three main ways to integrate your functionality, which are best described using their return value.

### My function doesn't return anything useful, it only performs some work.

Use the `@runnable` decorator. Arguments given to your function will be evaluated. Used as a predicate, it will *always* succeed. Example:

    @runnable
    def add_article(title, text):
        requests.post(".../article/add", {'title': title, 'text': text})
    
    # Can be used as:
    n.generate_intro[_.Name] = add_article("Intro " + _.Name, "Hello, I am " + _.Name + ", happy to be here.")


### My function returns a Boolean

Use the `@provable` decorator. This works almost exactly like `@runnable`, but depending on the truthiness of the return value it will succeed or fail.


### My function returns some valuable result

Use the `@evaluated` decorator. Again, the arguments itself are evaluated. Example:

    @evaluated
    def max_(x, y):
        return max(x, y)
    
    # Can be used as:
    Y << max_(X+5, 8)

    
### Want more control? (Debugging, multiple results, ...)
  
Apart from those techniques, you can also subclass from `MonoArg` or `MultiArg` (or `Structure` if you really want), and implement the `prove(result, debugger)` method. Yield all results that you find ok. This gives you the most control, but requires more knowledge about the inner workings of this library.


## Why not use it?

I didn't add any metaprogramming, since this would logically be Python's job. There is no 'standard library'. There are still going to be a lot of bugs. This project contains more lines of Python than the total amount of lines of Prolog I have written in my life, so some things might behave unexpectedly (but I wouldn't know currently). It's more of a proof-of-concept.

However, the biggest disadvantage might be performance. It's pretty slow.


## How does it work?

  - Lots of generators for a Prolog-like runtime (works pretty well, see the backtracking implementation in `logicpy/builtin.py`!)
  - Some little hacky tricks to provide the interface (these are somewhat more brittle)

  
## License?

This project is licensed under the MIT License.
