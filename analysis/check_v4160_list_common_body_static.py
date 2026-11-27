"""Offline complete common body operands, SCC and bounded path certificates.

No target ISA, register/RAM machine, polling, copy/provider/callback, MMIO,
CSR or device is executed/emulated. Graph and bounded integer checks only.
"""
import argparse
import json
from collections import deque
from hashlib import sha256
from pathlib import Path
import check_v4160_list_outer_objects_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-list-common-body-static.json')
STARTS=(0x54c08,0x54cd2)
HASHES=('f6d82412d3e42c00b82df3014ab03bc2156ceafa401066a1667cb499df78e5ca','7b7d3b37bbed69f54e95d554b1e428cdf57f6aa1627c9c40de66f1290f890981')
FIELDS={'addi':('rd','rs1','imm'),'store':('rs1','rs2','imm','width'),'lui':('rd','imm'),'load':('rd','rs1','imm','width'),
 'bne':('rs1','rs2','target'),'beq':('rs1','rs2','target'),'bge':('rs1','rs2','target'),'mv':('rd','rs2'),'li':('rd','imm'),
 'jal':('rd','target'),'andi':('rd','rs1','imm'),'ori':('rd','rs1','imm'),'slli':('rd','rs1','imm'),'srli':('rd','rs1','imm'),
 'or':('rd','rs1','rs2'),'and':('rd','rs1','rs2'),'add':('rd','rs1','rs2'),'mul':('rd','rs1','rs2'),'div':('rd','rs1','rs2'),'divu':('rd','rs1','rs2'),
 'beqz':('rs1','target'),'bnez':('rs1','target'),'jump':('target',),'auipc':('rd','imm'),'jalr':('rd','rs1','imm'),'jr':('rs1',)}
BRANCHES={'bne','beq','bge','beqz','bnez'}
COPY_OFFSETS=(0xe6,0x31c,0x348,0x392,0x420,0x43c,0x47e)

LITERALS='''
000 addi 2 2 -32
002 store 2 20 8 4
004 lui 20 536883200
008 store 2 21 4 4
00a addi 21 20 952
00e load 15 21 168 4
012 store 2 1 28 4
014 store 2 8 24 4
016 store 2 9 20 4
018 store 2 18 16 4
01a store 2 19 12 4
01c bne 15 0 516
020 mv 8 10
022 li 10 2
024 jal 1 409306
028 lui 18 536883200
02c load 12 18 1340 4
030 addi 15 0 160
034 lui 19 536883200
038 store 12 15 100 4
03a load 15 19 1288 4
03e lui 11 3342336
042 addi 20 20 952
046 load 14 15 44 4
048 andi 14 14 -4
04a ori 14 14 1
04e store 15 14 44 4
050 load 14 15 0 4
052 andi 14 14 -385
056 store 15 14 0 4
058 load 14 15 0 4
05a andi 14 14 -385
05e ori 14 14 256
062 store 15 14 0 4
064 lui 14 536883200
068 load 14 14 1424 4
06c load 13 14 8 4
06e or 13 13 11
070 store 14 13 8 4
072 addi 13 0 90
076 store 12 13 80 4
078 load 13 14 44 4
07a andi 13 13 -3
07c store 14 13 44 4
07e load 14 8 10 1
080 andi 13 14 127
084 load 14 15 0 4
086 andi 14 14 -128
08a or 14 14 13
08c store 15 14 0 4
08e load 15 8 14 1
090 load 14 8 76 4
092 andi 15 15 15
094 store 8 15 16 1
096 store 14 15 0 1
098 li 14 7
09a load 9 8 76 4
09c bne 15 14 1020
0a0 li 15 1
0a2 store 9 0 3 1
0a6 store 9 15 2 1
0a8 load 14 8 95 1
0ac li 11 3
0ae bne 14 11 770
0b2 load 15 8 28 2
0b4 bne 15 0 534
0b8 load 15 8 84 4
0ba li 14 4
0bc andi 15 15 12
0be beq 15 14 534
0c2 li 14 12
0c4 bne 15 14 212
0c8 load 14 8 97 1
0cc load 15 8 127 1
0d0 beq 14 15 534
0d4 li 15 1
0d6 store 9 15 3 1
0d8 li 12 6
0da addi 11 8 54
0de addi 10 9 4
0e2 auipc 1 536522752
0e6 jalr 1 1 1608
0ea load 15 9 2 1
0ec addi 15 15 6
0ee andi 15 15 255
0f2 store 9 15 2 1
0f4 load 14 8 96 1
0f8 andi 14 14 64
0fc beqz 14 276
0fe load 14 9 3 1
100 ori 14 14 64
104 store 9 14 3 1
106 load 14 8 76 4
108 add 15 15 14
10a load 14 8 21 1
10c store 15 14 3 1
10e load 15 9 2 1
110 addi 15 15 1
112 store 9 15 2 1
114 store 20 0 124 1
118 load 13 9 2 1
11a load 15 8 94 1
11e andi 14 13 63
122 addi 14 14 1
124 slli 15 15 6
126 or 15 15 13
128 store 8 14 17 1
12a store 9 15 2 1
12c addi 15 0 -108
130 store 8 15 11 1
132 load 15 8 53 1
136 andi 15 15 1
138 bnez 15 324
13a load 14 8 52 1
13e li 15 2
140 bne 14 15 334
144 load 14 8 76 4
146 load 15 14 0 1
148 ori 15 15 64
14c store 14 15 0 1
14e load 15 8 76 4
150 load 11 8 17 1
152 lui 10 2181038080
156 addi 10 10 -1
158 store 15 11 1 1
15a load 13 18 1340 4
15e lui 9 536883200
162 load 15 13 4 4
164 ori 15 15 1
168 store 13 15 4 4
16a load 15 8 104 1
16e load 12 19 1288 4
172 andi 15 15 63
176 slli 14 15 25
17a load 15 12 44 4
17c and 15 15 10
17e or 15 15 14
180 store 12 15 44 4
182 lui 15 2391392256
186 addi 15 15 -298
18a store 12 15 8 4
18c lui 15 5591040
190 addi 15 15 1365
194 store 12 15 4 4
196 load 15 8 106 1
19a load 20 8 100 1
19e li 14 2
1a0 or 20 20 15
1a4 addi 15 9 1300
1a8 store 15 14 7 1
1aa store 15 0 3 1
1ae load 15 8 76 4
1b0 addi 9 9 1300
1b4 store 13 15 112 4
1b6 lui 15 536883200
1ba load 15 15 576 1
1be beq 15 0 1176
1c2 load 15 13 100 4
1c4 bnez 15 450
1c6 mv 10 20
1c8 store 9 0 2 1
1cc jal 1 408334
1d0 lui 10 348160
1d4 addi 10 10 1152
1d8 auipc 1 536526848
1dc jalr 1 1 -1622
1e0 load 15 19 1288 4
1e4 lui 13 8388608
1e8 load 14 15 0 4
1ea or 14 14 13
1ec store 15 14 0 4
1ee load 14 15 44 4
1f0 andi 14 14 -4
1f2 store 15 14 44 4
1f4 load 15 18 1340 4
1f8 store 9 0 5 1
1fc store 9 0 1 1
200 li 14 2
202 store 15 14 0 4
204 load 1 2 28 4
206 load 8 2 24 4
208 load 9 2 20 4
20a load 18 2 16 4
20c load 19 2 12 4
20e load 20 2 8 4
210 load 21 2 4 4
212 addi 2 2 32
214 jr 1
216 li 15 8
218 store 9 15 3 1
21a load 15 8 108 2
21e store 9 15 4 1
220 load 15 8 108 2
224 load 14 8 97 1
228 load 13 8 76 4
22a srli 15 15 8
22c slli 14 14 4
22e andi 15 15 15
230 or 15 15 14
232 store 13 15 5 1
234 load 13 9 2 1
236 li 14 1
238 addi 13 13 2
23a andi 13 13 255
23e store 9 13 2 1
240 load 15 20 124 1
244 load 12 18 1340 4
248 bne 14 15 680
24c load 14 8 100 1
250 li 15 2
252 bne 14 15 1014
256 load 14 8 106 1
25a addi 15 13 6
25e slli 15 15 3
260 beq 14 0 1006
264 addi 15 15 215
268 slli 15 15 1
26a store 8 15 116 2
26e load 15 8 116 2
272 load 14 8 24 1
274 li 11 30
276 addi 15 15 160
27a mul 15 15 14
27e li 10 2
280 store 20 10 124 1
284 lui 10 4096
286 store 12 10 8 4
288 addi 15 15 -80
28c slli 15 15 16
28e srli 15 15 16
290 addi 15 15 359
294 div 15 15 11
298 slli 14 15 16
29c mul 15 15 11
2a0 srli 14 14 16
2a2 slli 15 15 1
2a4 store 12 15 96 4
2a6 jump 712
2a8 load 14 12 96 4
2aa li 15 30
2ac srli 14 14 1
2ae divu 14 14 15
2b2 load 15 12 96 4
2b4 load 11 12 100 4
2b6 srli 15 15 1
2b8 andi 15 15 31
2ba add 15 15 11
2bc store 12 15 100 4
2be li 15 3
2c0 store 20 15 124 1
2c4 slli 14 14 16
2c6 srli 14 14 16
2c8 load 15 9 3 1
2ca ori 15 15 16
2ce store 9 15 3 1
2d0 load 15 8 76 4
2d2 add 13 13 15
2d4 load 15 8 98 1
2d8 ori 15 15 64
2dc store 13 15 3 1
2de load 13 9 2 1
2e0 load 15 8 76 4
2e2 add 15 15 13
2e4 store 15 14 4 1
2e6 load 13 9 2 1
2e8 load 15 8 76 4
2ea srli 14 14 8
2ec andi 14 14 31
2ee add 15 15 13
2f0 load 13 8 99 1
2f4 slli 13 13 5
2f6 or 14 14 13
2f8 store 15 14 5 1
2fa load 15 9 2 1
2fc addi 15 15 3
2fe store 9 15 2 1
300 jump 280
302 li 13 6
304 bne 14 13 920
308 load 14 8 28 2
30a bnez 14 920
30c store 9 15 3 1
30e addi 10 9 4
312 li 12 6
314 addi 11 8 54
318 auipc 1 536522752
31c jalr 1 1 1042
320 load 15 9 2 1
322 addi 10 9 10
326 addi 15 15 6
328 store 9 15 2 1
32a load 15 9 3 1
32c ori 15 15 2
330 store 9 15 3 1
332 load 15 8 53 1
336 andi 15 15 2
338 beqz 15 888
33a load 11 8 48 4
33c load 15 11 18 1
33e beqz 15 888
340 li 12 6
342 addi 11 11 20
344 auipc 1 536522752
348 jalr 1 1 998
34c load 14 8 76 4
34e load 15 14 0 1
350 ori 15 15 -128
354 store 14 15 0 1
356 load 15 9 2 1
358 addi 15 15 6
35a andi 15 15 255
35e store 9 15 2 1
360 load 14 8 96 1
364 andi 14 14 64
368 beq 14 0 276
36c load 13 9 3 1
36e load 14 8 76 4
370 ori 13 13 64
374 store 9 13 3 1
376 jump 264
378 load 15 8 61 1
37c beqz 15 904
37e load 14 8 76 4
380 load 15 14 0 1
382 ori 15 15 -128
386 store 14 15 0 1
388 li 12 6
38a addi 11 8 62
38e auipc 1 536522752
392 jalr 1 1 924
396 jump 854
398 li 15 8
39a store 9 15 3 1
39c load 15 8 108 2
3a0 store 9 15 4 1
3a2 load 15 8 108 2
3a6 load 14 8 97 1
3aa load 13 8 76 4
3ac srli 15 15 8
3ae slli 14 14 4
3b0 andi 15 15 15
3b2 or 15 15 14
3b4 store 13 15 5 1
3b6 load 13 9 2 1
3b8 li 14 1
3ba addi 13 13 2
3bc andi 13 13 255
3c0 store 9 13 2 1
3c2 load 15 20 124 1
3c6 load 12 18 1340 4
3ca beq 14 15 588
3ce load 14 12 96 4
3d0 li 15 30
3d2 srli 14 14 1
3d4 divu 14 14 15
3d8 load 15 12 96 4
3da load 10 12 100 4
3dc srli 15 15 1
3de andi 15 15 31
3e0 add 15 15 10
3e2 store 12 15 100 4
3e4 store 21 11 124 1
3e8 slli 14 14 16
3ea srli 14 14 16
3ec jump 712
3ee addi 15 15 74
3f2 slli 15 15 3
3f4 jump 618
3f6 addi 15 13 14
3fa jump 1010
3fc li 14 1
3fe bne 15 14 1156
402 li 15 12
404 store 8 15 17 1
406 load 15 8 53 1
40a andi 15 15 2
40c beqz 15 1122
40e load 11 8 48 4
410 load 15 11 18 1
412 beqz 15 1122
414 li 12 6
416 addi 11 11 20
418 addi 10 9 8
41c auipc 1 536522752
420 jalr 1 1 782
424 load 14 8 76 4
426 load 15 14 0 1
428 ori 15 15 -128
42c store 14 15 0 1
42e load 10 8 76 4
430 li 12 6
432 addi 11 8 54
436 addi 10 10 2
438 auipc 1 536522752
43c jalr 1 1 754
440 load 15 20 216 4
444 slli 14 15 17
448 bge 14 0 1116
44c load 15 8 14 1
44e andi 15 15 14
450 bnez 15 1116
452 load 14 8 76 4
454 load 15 14 0 1
456 ori 15 15 32
45a store 14 15 0 1
45c addi 15 0 -110
460 jump 304
462 load 15 8 61 1
466 beqz 15 1136
468 load 15 9 0 1
46a ori 15 15 -128
46e store 9 15 0 1
470 load 10 8 76 4
472 li 12 6
474 addi 11 8 62
478 addi 10 10 8
47a auipc 1 536522752
47e jalr 1 1 688
482 jump 1070
484 load 12 8 28 2
486 load 11 8 40 4
488 addi 10 9 8
48c addi 15 12 6
490 andi 15 15 63
494 store 8 15 17 1
496 jump 1146
498 lui 10 348160
49c li 11 0
49e addi 10 10 1152
4a2 jal 1 277288
4a6 load 12 8 17 1
4a8 load 8 2 24 4
4aa load 1 2 28 4
4ac load 9 2 20 4
4ae load 18 2 16 4
4b0 load 19 2 12 4
4b2 load 21 2 4 4
4b4 mv 11 20
4b6 load 20 2 8 4
4b8 li 10 0
4ba addi 2 2 32
4bc auipc 6 536530944
4c0 jalr 0 6 1526
'''
PROFILE1_PATCHES={
 0xa:{'imm': 1032},
 0x24:{'target': 409540},
 0x2c:{'imm': 1420},
 0x3a:{'imm': 1368},
 0x42:{'imm': 1032},
 0x68:{'imm': 1504},
 0xe6:{'imm': 1406},
 0x15a:{'imm': 1420},
 0x16e:{'imm': 1368},
 0x1a4:{'imm': 1380},
 0x1b0:{'imm': 1380},
 0x1ba:{'imm': 656},
 0x1cc:{'target': 408568},
 0x1d4:{'imm': 1374},
 0x1dc:{'imm': -1824},
 0x1e0:{'imm': 1368},
 0x1f4:{'imm': 1420},
 0x244:{'imm': 1420},
 0x31c:{'imm': 840},
 0x348:{'imm': 796},
 0x392:{'imm': 722},
 0x3c6:{'imm': 1420},
 0x420:{'imm': 580},
 0x43c:{'imm': 552},
 0x47e:{'imm': 486},
 0x49e:{'imm': 1374},
 0x4a2:{'target': 277428},
 0x4c0:{'imm': 1400},
}


def specs(index):
    pc=STARTS[index];out={}
    for line in LITERALS.splitlines():
        if not line:continue
        a,op,*args=line.split();o=int(a,16);values=[int(v,0) for v in args]
        check(len(values)==len(FIELDS[op]),'common literalfield count')
        d=dict(zip(FIELDS[op],values));d['op']=op
        if index:d.update(PROFILE1_PATCHES.get(o,{}))
        if op in BRANCHES|{'jump'}:d['target']+=pc
        out[pc+o]=d
    check(len(out)==443,'common literal443 census');return out


def sccs(edges):
    serial=0;ids={};low={};stack=[];active=set();groups=[]
    def visit(p):
        nonlocal serial
        ids[p]=low[p]=serial;serial+=1;stack.append(p);active.add(p)
        for q in edges[p]:
            if q not in ids:visit(q);low[p]=min(low[p],low[q])
            elif q in active:low[p]=min(low[p],ids[q])
        if low[p]==ids[p]:
            group=[]
            while True:
                q=stack.pop();active.remove(q);group.append(q)
                if q==p:break
            groups.append(sorted(group))
    for p in edges:
        if p not in ids:visit(p)
    return sorted(groups)


def body(raw,index):
    pc=STARTS[index];n=decode(raw,pc);s=specs(index)
    check(set(n)==set(s),'common boundaries')
    for p,f in s.items():init.g(n,p,'common operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(1220,443,HASHES[index]),'common identity')
    edges={};calls=[];tails=[];returns=[]
    for p,v in n.items():
        op=v['op'];q=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'common RA return');returns.append(p);q=[]
        elif op in BRANCHES:q.append(v['target'])
        elif op=='jump':q=[v['target']]
        elif op in ('jal','jalr'):
            if op=='jal':target=v['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==v['rs1'],'common adjacent PCpair');target=(p-4+a['imm']+v['imm'])&0xfffffffe
            row={'pc':p,'target':target}
            if v['rd']==0:tails.append(row);q=[]
            else:check(v['rd']==1,'common RA calllink');calls.append(row)
        check(all(x in n for x in q),'common closed localCFG');edges[p]=q
    groups=sccs(edges);cycles=[x for x in groups if len(x)>1 or x[0] in edges[x[0]]]
    check(cycles==[[pc+0x1c2,pc+0x1c4]],'common onlytwoinstruction pollingSCC')
    reachable=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in reachable:continue
        reachable.add(p);pending.extend(edges[p])
    check(reachable==set(n),'common allnodes locallyreachable')
    check(returns==[pc+0x214] and tails==[{'pc':pc+0x4c0,'target':0x200026ba+76*index}],'common distinct RET andprofiletail target')
    check(len(calls)==11 and [x['pc']-pc for x in calls if x['target']==0x20000332]==list(COPY_OFFSETS),'common seven copycallsites')
    check([(x['pc']-pc,x['target']) for x in calls if x['target']!=0x20000332]==[(0x24,0x63eda+234*index),(0x1cc,0x63b0e+234*index),(0x1dc,0x2000078a),(0x4a2,0x43b28+140*index)],'common othercalls census')
    stores=[{'pc':p,'base':v['rs1'],'offset':v['imm'],'source':v['rs2'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check(len(stores)==76 and sum(x['base']==2 for x in stores)==7,'common76stores including7frame')
    return {'start':pc,'end_exclusive':pc+1220,'bytes':1220,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'local_CFG':edges,
      'cyclic_SCCs':cycles,'calls':calls,'tail_cuts':tails,'returns':returns,'stores':stores,'complete_local_body':True,'termination_proved':False}


def certificates(b):
    pc=b['start'];e=b['local_CFG'];terminals={p for p,q in e.items() if not q}
    def path(start,goal):
        todo=deque([(start,[start])]);seen=set()
        while todo:
            p,seq=todo.popleft()
            if p==goal:return seq
            if p in seen:continue
            seen.add(p)
            for q in e[p]:todo.append((q,seq+[q]))
        return None
    def finish(p):
        choices=[x for q in sorted(terminals) if (x:=path(p,q)) is not None]
        check(bool(choices),'common everyselectednode hasexitpath');return min(choices,key=len)
    witnesses=[]
    for p,qs in e.items():
        prefix=path(pc,p);check(prefix is not None,'common edgeprefix')
        for q in qs:
            seq=prefix+[q]+finish(q)[1:];check(all(z in e[a] for a,z in zip(seq,seq[1:])),'common edgewitness isCFGwalk')
            witnesses.append([a-pc for a in seq])
    selected={}
    for x in (0x24,0xe6,0x1c2,0x1cc,0x1dc,0x214,0x26a,0x31c,0x348,0x392,0x420,0x43c,0x47e,0x484,0x4a2,0x4c0):
        seq=path(pc,pc+x)+finish(pc+x)[1:];selected['through_'+hex(x)]=[a-pc for a in seq]
    p=pc+0x1c2;seq=path(pc,p)+[p+2,p,p+2]+finish(p+2)[1:]
    check(all(z in e[a] for a,z in zip(seq,seq[1:])),'common onebackedge pluspossibleexit witness');selected['poll_backedge_then_exit']=[a-pc for a in seq]
    # Dominance handles the polling cycle; it is a graph fact, not execution.
    preds={p:set() for p in e}
    for p,qs in e.items():
        for q in qs:preds[q].add(p)
    dom={p:({pc} if p==pc else set(e)) for p in e};changed=True
    while changed:
        changed=False
        for p in e:
            if p==pc:continue
            value={p}|set.intersection(*(dom[q] for q in preds[p]))
            if value!=dom[p]:dom[p]=value;changed=True
    check({pc+0x19a,pc+0x1a0,pc+0x4b4}<dom[pc+0x4c0],'common tail S4flag definitions dominate')
    check(pc+0x15a in dom[pc+0x1c2],'common pollbase freshload dominates')
    # Exact busy path avoids saving N or calling a nested function.
    busy=[pc,pc+2,pc+4,pc+8,pc+0xa,pc+0xe,pc+0x12,pc+0x14,pc+0x16,pc+0x18,pc+0x1a,pc+0x1c,*range(pc+0x204,pc+0x216,2)]
    check(all(z in e[a] for a,z in zip(busy,busy[1:])) and busy[-1] in terminals,'common exactbusy path')
    selected['busy_nonzero_no_nested_call']=[a-pc for a in busy]
    return {'selected_walks':selected,'all_edge_witness_count':len(witnesses),'all_edge_witness_sha256':sha256(json.dumps(witnesses,separators=(',',':')).encode()).hexdigest(),
      'tail_dominating_S4_definitions':[0x19a,0x1a0,0x4b4],'poll_dominating_pointer_load':0x15a,
      'scope':'syntactic walks with optional polling exit; no branch-feasibility, finitepoll/callee/targetreturn proof'}


def domains():
    for a in range(256):
        for z in range(256):
            flags=a|z;check(0<=flags<=255,'common ORoftwobytes tailflags')
            packed=((a<<6)|z)&255;check(packed&63==z&63,'common packetbyte2 low6 identity')
    maxq=0
    for h in range(65536):
        q=(h+359)//30;maxq=max(maxq,q);check(0<=q<=2196 and q*60<=131760,'common finalpositiveDIV30 domain')
    check(maxq==2196,'common DIV30 max')
    for count in range(256):
        candidates=(16*(count+6)+430,64*(count+6)+592,8*(count+14))
        check(all(0<=x<65536 for x in candidates),'common timinghalfword encodedbranches fit16')
    check((65535+160)*255-80<2**32,'common timingproduct word nooverflow')
    return {'byte_pairs':65536,'tail_OR_byte_range':[0,255],'packet_low6_identity':True,'U16_plus359_div30_cases':65536,'quotient_max':maxq,'encoded60q_max':131760,
      'timing_halfword_branch_cases':768,'wordproduct_max_before_minus80':(65535+160)*255,
      'variable_copy_length_domain':[0,65535],'length_gate_or_validextent_proved':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        pc=STARTS[i];b=body(init.binding.take(data,pc,1220),i);cert=certificates(b);B=0x200033b8+80*i;n={v['pc']:v for v in b['instructions']}
        prior=previous.previous.body(init.binding.take(data,previous.previous.STARTS[i][1],60),'bit1',i)
        check(prior['tail_cuts'][0]['target']==hex(pc),'common bit1 tail joinscompletebody')
        reg=previous.reused_registrar(data,i);check(reg['start']==hex(b['calls'][-1]['target']),'common finalregistrar joinsknown22Bbody')
        check([p-pc for p,v in n.items() if v.get('rd')==20]==[4,0x42,0x19a,0x1a0,0x20e,0x4b6],'common exact S4writes andrestores')
        check([p-pc for p,v in n.items() if v.get('rd')==13 and 0x15a<=p-pc<0x1c6]==[0x15a],'common A3pollbase held withoutlocalredefinition')
        profiles.append({'label':pr['label'],'body':b,'CFG_certificates':cert,'reused_registrar':reg,
          'entry_contract':{'B':hex(B),'N':'originalA0 savedinS0 onlybusy0path; no localNnullguard','frame_bytes':32,'saved':['RA','S0','S1','S2','S3','S4','S5'],
            'busy':'freshU32[B168]!=0 ->frame-restoring RET withoutnestedcall/Ndereference; A0locallyretainedentryvalue',
            'busy0_first_call':{'target':hex(0x63eda+234*i),'A0':2},'minimum_fixed_N_extent':128,'minimum_B_extent':220,'callees_may_require_more':True},
          'pointed_globals':{'initial_D0':'freshU32['+hex(0x2000353c+80*i)+'];local D0+100=160,D0+80=90',
            'poll_D1':'freshU32[sameglobalslot] at+15a, not assumedidenticaltoD0; D1+4RMW,D1+112packetpointer beforepoll',
            'other_objects':[hex(0x20003508+80*i),hex(0x20003590+80*i)],'conditional_fixed_extents':{'D1':116,'other_objects':48},
            'classification':'pointer-valuedglobals/dynamicdereferences; physicalMMIO/board/RFidentity/extent unproved; no pointedobject nullguards'},
          'packet_sources':{'P_saved':'S1=freshU32[N76] at+9a; no nullguard','P_fresh':'laterloads ofN76 maydiffer; packetbyte2 freshat eachuse','Q':'freshU32[N48]; Q18dereferencedwithoutlocalnullguard onselectedpaths',
            'Q_copy_extent':26,'N40_pointer':'freshU32[N40] onvariablelengthpath; no null/lengthboundguard',
            'dynamic_packet_offsets':'somebyte storesusepacketbase+freshU8[packet2]+3/+4/+5; validity/capacity/alias/retention unproved'},
          'copy_callsites':[
            {'offset':0xe6,'args':['P_saved+4','N54',6]}, {'offset':0x31c,'args':['P_saved+4','N54',6]},
            {'offset':0x348,'args':['P_saved+10','freshQ+20',6],'guards':['N53bit1','freshU8[Q18]!=0'],'Q_null_guard':False},
            {'offset':0x392,'args':['P_saved+10','N62',6],'fallback':'Q-copyguardsfail; N61onlycontrolsheaderflag, notwhetherthiscopyisrequested'},
            {'offset':0x420,'args':['P_saved+8','freshQ+20',6],'guards':['N53bit1','freshU8[Q18]!=0'],'Q_null_guard':False},
            {'offset':0x43c,'args':['freshU32[N76]+2','N54',6]},
            {'offset':0x47e,'contracts':[{'path':'N61fallback','args':['freshU32[N76]+8','N62',6]},
              {'path':'mode_other_than1or7','args':['P_saved+8','freshU32[N40]','freshU16[N28]'],'length_range':[0,65535],'local_positive_or_capacity_guard':False}]}],
          'copy_limit':'alltargetRAM20000332; requestsonly, no providerexecution/nonretention/success/extentproof. Currentcallee mustpreserve liveN/Sregisters/SP/frame andrequiredobjects',
          'poll_contract':{'cycle_offsets':[0x1c2,0x1c4],'read':'freshU32[D1+100] intoA5','backedge':'A5!=0','exit':'A5==0','local_counter_or_call_or_backoff':False,
            'maximum_iterations_proved':False,'D1_lifetime_or_external_progress_proved':False},
          'gate_paths':{'source':hex(0x20003240+80*i),'fresh_nonzero':'poll, then63b0e/63bf8(flags), thenRAM2000078a(callbackliteral); pointedstores andframe-restoring RET',
            'fresh_zero':'skippoll, callmatchingregistrar(callbackliteral,0), thenrestoreframe andtailto'+hex(0x200026ba+76*i),
            'callback_literal':hex(0x55480+222*i),'ordinary_active_return':'inheritedRAM2000078a replyA0 afterrequiredreturn; notfixedsuccess'},
          'tail_contract':{'target':hex(0x200026ba+76*i),'A0':0,'A1':'S4beforeitsrestore = U8[N100] OR U8[N106], range0..255; not B address',
            'A2':'freshU8[N17] aftermatchingregistrar','frame_restored_before_tail':True,'original_RA_restored':True,'tail_function_body_or_return_proved':False,
            'matching_registrar_effect':'index0 storescallbackliteral to'+reg['table_base']+'; no invocation; preservesS4/S0/SP/RA/A0 locally, withnonaliasframe/N/table premises'},
          'lifetime_limit':'76directstores/69nonframe do notprove physicalfree/listunlink orretention; pointedwordRMW andcopy targets mayalias N/globals/frame unlessexcluded',
          'actual_installed_binding_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-list-common-body-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'scope':'complete1220B/443i commonbody perprofile;2440neworiginalbytes/886operandguards;alllocaledges witnessed/onepollSCC;priorcaller/registrar/outerproofs reused',
      'boundary':'static localbody/graph/arg contracts only; polling/callee/tailtermination, actualbinding andpointerlifetime unproved',
      'remaining':['constructorfunctionslot consumers/actualcallers','callback55480/5555e andRAMtail200026ba/20002706 sources/contracts','63b0e/63bf8,63eda/63fc4,actualcopy/provider/pollprogress','packetextent/lengthconstraints/writers/retention'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=walks=edges=0
    for i,data in enumerate(carriers):
        pc=STARTS[i];raw=init.binding.take(data,pc,1220);b=body(raw,i);c=certificates(b);walks+=len(c['selected_walks']);edges+=c['all_edge_witness_count']
        for p,v in decode(raw,pc).items():
            at=p-pc;z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
            try:body(buf,i)
            except RuntimeError as e:check(str(e).startswith('common operand '),'common specifiedmutation '+str(e))
            else:raise RuntimeError('common mutation escaped')
            mutations+=1
    check(mutations==886,'common mutationcensus');domains()
    print('PASS:886 operand mutations rejected;2440 new originalbytes;'+str(walks)+' selectedCFG walks;'+str(edges)+' edge witnesses;exactpoll SCC/domination/byte/U16 domains')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'common exactledger replay')
    print('PASS:complete commonbody/copyargs/flags/RETvsRAMtail;reused caller/registrar;exact ledger')
    print('PASS:NO target execution/emulation;poll/callee/tailtermination/provider/extent/retention UNPROVED')


if __name__=='__main__':main()
