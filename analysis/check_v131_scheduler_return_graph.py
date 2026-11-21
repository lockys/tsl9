"""Check the local normal-return graph of the V1.31 reference scheduler.
Usage: python check_v131_scheduler_return_graph.py V131_CARRIER
Calls contribute only a fall-through edge on normal return. The graph permits
both outcomes of each branch; it proves neither termination nor feasibility.
Under Xwchc the two halfwords at 43860/43862 are stores, not transfers.
"""
from hashlib import sha256
from pathlib import Path
import sys


def check(ok, message):
    if not ok:
        raise ValueError(message)


def signed(v, bits):
    return v - ((v >> (bits - 1)) << bits)


def verify(blob):
    check(sha256(blob).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'carrier identity')
    pc, end = 0x43728, 0x43874
    graph, calls, returns = {}, [], []
    while pc < end:
        off = pc - 0x40000
        x = int.from_bytes(blob[off:off+2], 'little')
        n = 4 if x & 3 == 3 else 2
        edges = [pc+n]
        if n == 4:
            x = int.from_bytes(blob[off:off+4], 'little')
            op = x & 127
            if op == 0x63:
                d = (x>>31<<12) | ((x>>7&1)<<11) | ((x>>25&63)<<5) | ((x>>8&15)<<1)
                edges.append(pc+signed(d,13))
            elif op in (0x67, 0x6f):
                check((x>>7&31)==1, 'unexpected non-call transfer'); calls.append(pc)
            else:
                check(op in (3,15,19,23,35,51,55), 'unknown word opcode')
        elif x & 0xe003 == 0xa001:
            d = sum(((x>>i)&1)<<j for i,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)))
            edges = [pc+signed(d,12)]
        elif x & 0xc003 == 0xc001:
            d = sum(((x>>i)&1)<<j for i,j in zip((2,3,4,5,6,10,11,12),(5,1,2,6,7,3,4,8)))
            edges.append(pc+signed(d,9))
        elif x & 0xe003 == 0x2001:
            raise ValueError('unexpected compressed direct call')
        elif x & 0xe07f == 0x8002:
            if x == 0x8082:
                returns.append(pc); edges = []
            else:
                check(x & 0x1000 and x>>7&31, 'unexpected indirect jump'); calls.append(pc)
        graph[pc] = edges; pc += n
    check(pc==end and all(q in graph for es in graph.values() for q in es), 'edge outside local graph')
    check(returns==[0x437c8] and calls==[0x437a6,0x437ca,0x437ea,0x4380c,0x4382e,0x43842], 'transfer inventory')

    def reachable(start, omit=()):
        seen, todo = set(), [start]
        while todo:
            p = todo.pop()
            if p in seen or p in omit: continue
            seen.add(p); todo.extend(graph[p])
        return seen

    ret = returns[0]
    check(reachable(0x43728)==set(graph), 'disconnected code')
    for gate in (0x43732,0x43734,0x437b4,0x437b6,0x437c6):
        check(ret not in reachable(0x43728,[gate]), 'return bypass')
    check(ret not in reachable(0x43728,[0x437b2,0x4381c]), 'unclassified return')
    for start, status, other in ((0x43764,0x437b2,0x4381c),(0x437ae,0x437b2,0x4381c),(0x43834,0x437b2,0x4381c),(0x43812,0x4381c,0x437b2),(0x43846,0x4381c,0x437b2)):
        r = reachable(start); check(ret in r and status in r and other not in r, 'wrong return class')
    print(f'PASS: {len(graph)} instruction starts, 6 normal-return call edges, 5 classified path entries, 1 RET; no local return bypasses saved s0 reload')


if __name__ == '__main__':
    verify(Path(sys.argv[1]).read_bytes())
