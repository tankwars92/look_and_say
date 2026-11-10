from itertools import groupby


def _decay(s):
    return ''.join(str(len(list(g))) + k for k, g in groupby(s))


def _stable(c, y, depth=90, cap=64):
    p = y
    whole = True
    for _ in range(depth):
        if p[0] == c:
            return False
        if not whole:
            j = len(p) - 1
            while j > 0 and p[j - 1] == p[-1]:
                j -= 1
            p = p[:j]
        p = _decay(p)
        if len(p) > cap:
            p = p[:cap]
            whole = False
    return True


def _split(s):
    cuts = [0] + [i for i in range(1, len(s)) if s[i - 1] != s[i] and _stable(s[i - 1], s[i:])] + [len(s)]
    return [s[a:b] for a, b in zip(cuts, cuts[1:])]


def _build():
    sigma = {}
    stack = ['1']
    while stack:
        a = stack.pop()
        if a not in sigma:
            sigma[a] = _split(_decay(a))
            stack.extend(sigma[a])
    atoms = list(sigma)
    index = {a: i for i, a in enumerate(atoms)}
    return atoms, [tuple(index[p] for p in sigma[a]) for a in atoms]


ATOMS, CHILDREN = _build()
_N = len(ATOMS)
_EDGES = sum(map(len, CHILDREN))
_STR = [[a.encode() for a in ATOMS]]
_LEN = [[len(a) for a in ATOMS]]
_SHORT = 24
_UNIT = 400


def verify():
    for a, ch in zip(ATOMS, CHILDREN):
        if _decay(a) != ''.join(ATOMS[c] for c in ch):
            return False
    pairs = set()
    for ch in CHILDREN:
        pairs.update(zip(ch, ch[1:]))
    todo = list(pairs)
    while todo:
        x, y = todo.pop()
        z = (CHILDREN[x][-1], CHILDREN[y][0])
        if z not in pairs:
            pairs.add(z)
            todo.append(z)
    return all(ATOMS[x][-1] != ATOMS[y][0] for x, y in pairs)


def _lens(d):
    while len(_LEN) <= d:
        prev = _LEN[-1]
        _LEN.append([sum([prev[c] for c in ch]) for ch in CHILDREN])
    return _LEN


def _strings(d):
    while len(_STR) <= d:
        prev = _STR[-1]
        _STR.append([b''.join([prev[c] for c in ch]) for ch in CHILDREN])
    return _STR[d]


def _choose(t):
    lens = _lens(t)
    have = len(_STR) - 1
    cum = [0]
    for d in range(1, t + 1):
        cum.append(cum[-1] + sum(lens[d]) + _UNIT * _EDGES)
    cnt = [0] * _N
    cnt[0] = 1
    best = None
    for m in range(t + 1):
        d = t - m
        cost = (cum[d] - cum[have] if d > have else 0) + _UNIT * sum(cnt)
        if best is None or cost < best[0]:
            best = (cost, m)
        elif _UNIT * sum(cnt) > best[0]:
            break
        nxt = [0] * _N
        for x, v in enumerate(cnt):
            if v:
                for c in CHILDREN[x]:
                    nxt[c] += v
        cnt = nxt
    return best[1]


def term_bytes(n):
    t = n - 1
    m = _choose(t)
    w = [0]
    for _ in range(m):
        w = [c for x in w for c in CHILDREN[x]]
    s = _strings(t - m)
    return b''.join([s[x] for x in w])


def term(n):
    return term_bytes(n).decode()


def digit(n, k):
    t = n - 1
    lens = _lens(t)
    if not 0 <= k < lens[t][0]:
        raise IndexError(k)
    x = 0
    while t:
        row = lens[t - 1]
        for c in CHILDREN[x]:
            l = row[c]
            if k < l:
                x = c
                break
            k -= l
        t -= 1
    return ATOMS[x][k]


def digits(n, start, count):
    t = n - 1
    lens = _lens(t)
    end = min(start + count, lens[t][0])
    out = []
    stack = [(0, t, start, end)]
    while stack:
        x, d, lo, hi = stack.pop()
        if d <= _SHORT:
            out.append(_strings(d)[x][lo:hi])
            continue
        row = lens[d - 1]
        off = 0
        new = []
        for c in CHILDREN[x]:
            l = row[c]
            a = max(lo - off, 0)
            b = min(hi - off, l)
            if a < b:
                new.append((c, d - 1, a, b))
            off += l
            if off >= hi:
                break
        stack.extend(reversed(new))
    return b''.join(out).decode()


def _bm(s, p):
    C, B, L, m, b = [1], [1], 0, 1, 1
    for n in range(len(s)):
        d = s[n]
        for i in range(1, L + 1):
            d = (d + C[i] * s[n - i]) % p
        if d == 0:
            m += 1
            continue
        coef = d * pow(b, -1, p) % p
        T = C[:]
        C = C + [0] * (len(B) + m - len(C))
        for i, v in enumerate(B):
            C[i + m] = (C[i + m] - coef * v) % p
        if 2 * L <= n:
            L, B, b, m = n + 1 - L, T, d, 1
        else:
            m += 1
    C = C + [0] * (L + 1 - len(C))
    return [-(c if c <= p // 2 else c - p) for c in C[1:L + 1]]


_PRIME = (1 << 61) - 1
_TERMS = 420


def _count_rows():
    rows = [[(a.count('1'), a.count('2'), a.count('3')) for a in ATOMS]]
    for _ in range(_TERMS - 1):
        prev = rows[-1]
        rows.append([tuple(sum(prev[c][j] for c in ch) for j in range(3)) for ch in CHILDREN])
    return rows


def _sequences():
    rows = _count_rows()
    return {
        'length': [sum(rows[d][0]) for d in range(_TERMS)],
        1: [rows[d][0][0] for d in range(_TERMS)],
        2: [rows[d][0][1] for d in range(_TERMS)],
        3: [rows[d][0][2] for d in range(_TERMS)],
    }


_SEQ = _sequences()
_REC = {key: _bm(seq, _PRIME) for key, seq in _SEQ.items()}


def recurrence_holds(key):
    q, seq = _REC[key], _SEQ[key]
    r = len(q)
    return all(seq[n] == sum(q[i] * seq[n - 1 - i] for i in range(r)) for n in range(r, _TERMS))


def _pack(a, nb):
    pos = b''.join([max(x, 0).to_bytes(nb, 'little') for x in a])
    neg = b''.join([max(-x, 0).to_bytes(nb, 'little') for x in a])
    return int.from_bytes(pos, 'little') - int.from_bytes(neg, 'little')


def _unpack(v, nb, count):
    shift = int.from_bytes((b'\x00' * (nb - 1) + b'\x80') * count, 'little')
    raw = (v + shift).to_bytes(nb * count, 'little')
    half = 1 << (8 * nb - 1)
    return [int.from_bytes(raw[i * nb:(i + 1) * nb], 'little') - half for i in range(count)]


def _mulmod(a, b, q):
    r = len(q)
    bits = max(x.bit_length() for x in a) + max(x.bit_length() for x in b) + r.bit_length() + 2
    nb = bits // 8 + 1
    prod = _unpack(_pack(a, nb) * _pack(b, nb), nb, 2 * r - 1)
    for k in range(2 * r - 2, r - 1, -1):
        v = prod[k]
        if v:
            for i in range(r):
                prod[k - 1 - i] += q[i] * v
    return prod[:r]


def _linear(key, n):
    seq, q = _SEQ[key], _REC[key]
    r = len(q)
    if n < _TERMS:
        return seq[n]
    base = [0] * r
    base[1] = 1
    res = [0] * r
    res[0] = 1
    e = n
    while e:
        if e & 1:
            res = _mulmod(res, base, q)
        e >>= 1
        if e:
            base = _mulmod(base, base, q)
    return sum(c * seq[i] for i, c in enumerate(res))


def length(n):
    return _linear('length', n - 1)


def counts(n):
    return tuple(_linear(j, n - 1) for j in (1, 2, 3))
