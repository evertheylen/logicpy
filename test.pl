
test(foo(X), Y) :- test(X, Y).
test(bar, bar).

sum(zero, X, X).
sum(next(X), Y, Z) :- sum(X, next(Y), Z).


four(next(next(next(next(zero))))).
two(next(next(zero))).
