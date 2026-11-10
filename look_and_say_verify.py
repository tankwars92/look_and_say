import random
from itertools import groupby
import look_and_say as L


def naive_terms(count):
    s = '1'
    out = [s]
    for _ in range(count - 1):
        s = ''.join(str(len(list(g))) + k for k, g in groupby(s))
        out.append(s)
    return out


ref = naive_terms(46)
assert L.verify()
assert all(L.recurrence_holds(k) for k in L._REC)
for n in range(1, 47):
    assert L.term(n) == ref[n - 1], n
    assert L.length(n) == len(ref[n - 1]), n
    assert L.counts(n) == tuple(ref[n - 1].count(c) for c in '123'), n
print('terms, lengths, counts n<=46: ok')
for n in (12, 25, 40, 46):
    s = ref[n - 1]
    assert all(L.digit(n, k) == s[k] for k in range(0, len(s), 1 if len(s) < 5000 else 7))
    for _ in range(300):
        a = random.randrange(len(s))
        c = random.randrange(1, 400)
        assert L.digits(n, a, c) == s[a:a + c]
print('digit, digits n<=46: ok')
s = naive_terms(62)[-1]
assert L.term(62) == s and L.length(62) == len(s)
assert L.counts(62) == tuple(s.count(c) for c in '123')
for _ in range(2000):
    k = random.randrange(len(s))
    assert L.digit(62, k) == s[k]
    a = random.randrange(len(s))
    assert L.digits(62, a, 300) == s[a:a + 300]
print('n=62 (len %d): ok' % len(s))
t = L.term(66)
assert len(t) == L.length(66)
assert tuple(t.count(c) for c in '123') == L.counts(66)
assert all(L.digit(66, k) == t[k] for k in random.sample(range(len(t)), 3000))
print('n=66 (len %d): ok' % len(t))
big = 3000
n1, n2 = L.length(big), L.length(big + 1)
rows = L._lens(big)
assert rows[big - 1][0] == n1 and rows[big][0] == n2
assert sum(L.counts(big)) == n1
assert L.length(10**5) == sum(L.counts(10**5))
for n in (200, 421, 1000, 2999):
    assert L.length(n) == L._lens(n - 1)[n - 1][0], n
print('length via recurrence = DP for large n: ok')
x = L.digits(3000, 10**300, 60)
y = ''.join(L.digit(3000, 10**300 + i) for i in range(60))
assert x == y
print('digits n=3000 position 10^300:', x)
