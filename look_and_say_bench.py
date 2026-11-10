import re
import sys
import time
from itertools import groupby


def groupby_terms(n):
    s = '1'
    for _ in range(n - 1):
        s = ''.join([str(len(list(g))) + k for k, g in groupby(s)])
    return s


_RUN = re.compile(r'(.)\1*')


def regex_terms(n):
    s = '1'
    for _ in range(n - 1):
        s = _RUN.sub(lambda m: str(len(m.group())) + m.group(1), s)
    return s


def element_terms(n, children, atoms):
    w = [0]
    for _ in range(n - 1):
        w = [c for x in w for c in children[x]]
    return ''.join([atoms[x] for x in w])


def clock(f, *a):
    t = time.perf_counter()
    r = f(*a)
    return time.perf_counter() - t, r


if __name__ == '__main__':
    n = int(sys.argv[1])
    which = sys.argv[2]
    if which == 'ours':
        t0 = time.perf_counter()
        import look_and_say as L
        ti = time.perf_counter() - t0
        t1, r = clock(L.term_bytes, n)
        t2, _ = clock(L.term_bytes, n)
        t3, _ = clock(L.term, n)
        print('ours n=%d len=%d import=%.3f cold=%.4f warm=%.4f warm_str=%.4f' % (n, len(r), ti, t1, t2, t3))
    elif which == 'element':
        import look_and_say as L
        t1, r = clock(element_terms, n, L.CHILDREN, L.ATOMS)
        print('element n=%d len=%d %.4f' % (n, len(r), t1))
    elif which == 'regex':
        t1, r = clock(regex_terms, n)
        print('regex n=%d len=%d %.4f' % (n, len(r), t1))
    else:
        t1, r = clock(groupby_terms, n)
        print('groupby n=%d len=%d %.4f' % (n, len(r), t1))
