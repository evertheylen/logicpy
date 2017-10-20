
foo(X, Y) :- bar(X), quuz(bla(Y)).
bar(A) :- quuz(bla(A)).
quuz(bla(B)) :- B = kaas; B = hesp.
