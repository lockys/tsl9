"""Expand the small C fixture macro language without running a C preprocessor."""
import ast
import hashlib
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / 'v4160-18ef2-c-harness' / 'fixtures.h'
COUNTS = [201, 201, 201, 209]
PIN = 'dcbdeef30e9437e6f23b41f2f3b985f547e39b5f3447bee068e4df90b9786b5c'
HEADER_PIN = 'e02059b680d3bc53560240036ce3c607738d87f9a4c6e9d751524d5c39d72c47'
TOKEN = re.compile(r"'[^']*'|0x[0-9a-fA-F]+u?|[0-9]+u?|[A-Za-z_]\w*|\S")


def expand(tokens, macros, depth=0):
    if depth > 30:
        raise ValueError('recursive macro')
    out = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t not in macros:
            out.append(t)
            i += 1
            continue
        params, body = macros[t]
        i += 1
        if params is not None:
            if i >= len(tokens) or tokens[i] != '(':
                out.append(t)
                continue
            i += 1
            args, arg, level = [], [], 0
            while i < len(tokens):
                x = tokens[i]
                i += 1
                if x == ')' and level == 0:
                    args.append(arg)
                    break
                if x == ',' and level == 0:
                    args.append(arg)
                    arg = []
                    continue
                level += (x == '(') - (x == ')')
                arg.append(x)
            else:
                raise ValueError('unterminated arguments')
            if len(args) != len(params):
                raise ValueError('macro arity')
            substitutions = dict(zip(params, args))
            body = [y for x in body for y in substitutions.get(x, [x])]
        out.extend(expand(body, macros, depth + 1))
    return out


def number(tokens):
    expr = ''.join(re.sub(r'u$', '', t) for t in tokens)
    tree = ast.parse(expr, mode='eval')
    def calc(n):
        if isinstance(n, ast.Constant) and type(n.value) is int:
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in (ast.Add, ast.Mult, ast.BitOr, ast.BitAnd):
            a, b = calc(n.left), calc(n.right)
            return {ast.Add: lambda: a+b, ast.Mult: lambda: a*b,
                    ast.BitOr: lambda: a|b, ast.BitAnd: lambda: a&b}[type(n.op)]()
        raise ValueError('bad expression: ' + expr)
    return calc(tree.body) & 0xffffffff


def compact(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S).replace('\\\n', '')
    macros, traces, rows = {}, {}, []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.fullmatch(r'#define (\w+)(?:\(([^)]*)\))?\s*(.*)', line)
        if m:
            macros[m[1]] = (None if m[2] is None else m[2].split(','), TOKEN.findall(m[3]))
            continue
        m = re.fullmatch(r'#undef (\w+)', line)
        if m:
            del macros[m[1]]
            continue
        m = re.fullmatch(r'static const event (\w+)_events\[\] = \{ TRACE \};', line)
        if m:
            tokens = expand(['TRACE'], macros)
            s = ' '.join(tokens)
            pat = re.compile(r"\{ '([RW])' , \( uint32_t \) \( (.*?) \) , \( uint32_t \) \( (.*?) \) \} ,")
            events, pos = [], 0
            while pos < len(s):
                match = pat.match(s, pos)
                if not match:
                    raise ValueError('bad expanded event: ' + s[pos:pos+100])
                events.append((match[1], number(TOKEN.findall(match[2])), number(TOKEN.findall(match[3]))))
                pos = match.end()
                while pos < len(s) and s[pos] == ' ':
                    pos += 1
            traces[m[1]] = events
            continue
        m = re.fullmatch(r'ROW\((\w+),(0x[\da-f]+)u,(0x[\da-f]+)u,(0x[\da-f]+)u\),', line)
        if m:
            rows.append((m[1], *(int(v, 16) for v in m.groups()[1:])))
            continue
        if line in ('static const fixture fixtures[] = {', '};'):
            continue
        raise ValueError('unrecognised line: ' + line)
    return rows, traces


def original(text):
    event = re.compile(r"\s*\{ '([RW])', UINT32_C\(0x([0-9a-f]{8})\), UINT32_C\(0x([0-9a-f]{8})\) \},")
    pos = 0
    def take(pattern):
        nonlocal pos
        m = re.compile(pattern).match(text, pos)
        if not m:
            raise ValueError('bad original at ' + str(pos))
        pos = m.end()
        return m
    take(r'\s*/\* Fixed independently prepared bus scripts; values are not generated at runtime\. \*/')
    traces = {}
    for name in ('normal', 'wrap', 'alias', 'poll'):
        take(r'\s*static const event ' + name + r'_events\[\] = \{')
        events = []
        while True:
            m = event.match(text, pos)
            if not m:
                break
            pos = m.end()
            events.append((m[1], int(m[2], 16), int(m[3], 16)))
        traces[name] = events
        take(r'\s*\};')
    take(r'\s*static const fixture fixtures\[\] = \{')
    rows = []
    for name in traces:
        m = take(r'\s*\{ "' + name + r'", UINT32_C\(0x([0-9a-f]{8})\), UINT32_C\(0x([0-9a-f]{8})\), UINT32_C\(0x([0-9a-f]{8})\), ' + name + r'_events, sizeof ' + name + r'_events / sizeof ' + name + r'_events\[0\] \},')
        rows.append((name, *(int(v, 16) for v in m.groups())))
    take(r'\s*\};\s*\Z')
    return rows, traces


def digest(rows, traces):
    data = ''.join(f'{n} {a:08x} {s:08x} {d:08x}\n' +
                   ''.join(f'{k} {x:08x} {v:08x}\n' for k, x, v in traces[n])
                   for n, a, s, d in rows)
    return hashlib.sha256(data.encode('ascii')).hexdigest()


class Fixtures(unittest.TestCase):
    def test_traces(self):
        header = (HERE / 'fixtures.h').read_bytes()
        self.assertEqual(hashlib.sha256(header).hexdigest(), HEADER_PIN)
        rows, traces = compact(header.decode('utf-8'))
        self.assertEqual([r[0] for r in rows], ['normal', 'wrap', 'alias', 'poll'])
        self.assertEqual(set(traces), {r[0] for r in rows})
        self.assertEqual([len(traces[r[0]]) for r in rows], COUNTS)
        self.assertEqual(digest(rows, traces), PIN)
        if ORIGINAL.exists():
            oldrows, oldtraces = original(ORIGINAL.read_text(encoding='utf-8'))
            self.assertEqual(rows, oldrows)
            for name, *_ in rows:
                for i, (new, old) in enumerate(zip(traces[name], oldtraces[name])):
                    self.assertEqual(new, old, (name, i))
                self.assertEqual(len(traces[name]), len(oldtraces[name]))
            print('Compared all 812 events against original fixtures.h')
        else:
            print('Original absent; fixed complete-trace SHA256 and cardinalities verified')


if __name__ == '__main__':
    unittest.main()
