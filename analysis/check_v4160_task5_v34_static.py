"""Offline complete V34 downstream and word-count copy contracts.

Pinned operands/CFG and immutable paths/scalar algebra. No target ISA,
mutable registers/RAM/heap/queue, provider, callback or MMIO execution.
"""
import argparse,json
from collections import Counter
from hashlib import sha256
from pathlib import Path
import check_v4160_task5_config_provenance_static as previous

allocation=previous.previous
init,sparse,check,decode=allocation.init,allocation.sparse,allocation.check,allocation.decode
common=allocation.common
OUT=Path(__file__).with_name('v4160-task5-v34-static.json')
FIELDS=allocation.FIELDS
BRANCHES=allocation.BRANCHES
PARTS=('v34', 'wordcopy')
STARTS=((340222, 536871788), (340390, 536871788))
SOURCES=((340222, 263644), (340390, 263708))
SIZES=((588, 48), (594, 48))
COUNTS=((207, 16), (209, 16))
HASHES=(('d0d1e180159e9e32fb0fdf6affc3b2f5d23e44ec1a419969d9108149bf07e784', '40be5d089663ab1aecad9bccbbcaea1d102e29773bce01a629626fe0565157f5'), ('abdb77cbad1ad0653e222ec2979f98e3e60a569f605f686dc7a296b27e9945a9', '40be5d089663ab1aecad9bccbbcaea1d102e29773bce01a629626fe0565157f5'))
TYPED_LOADS=({'v34': ((44, 4), (54, 4), (72, 5), (178, 4), (216, 4), (258, 2), (292, 2), (304, 2), (324, 4), (346, 2), (372, 2), (410, 2), (456, 2), (482, 4), (490, 2), (506, 2), (524, 2), (534, 2), (560, 2), (570, 2)), 'wordcopy': ((4, 2), (34, 2))}, {'v34': ((44, 4), (54, 4), (72, 5), (178, 4), (216, 4), (258, 2), (292, 2), (304, 2), (324, 4), (346, 2), (378, 2), (416, 2), (462, 2), (488, 4), (496, 2), (512, 2), (530, 2), (540, 2), (566, 2), (576, 2)), 'wordcopy': ((4, 2), (34, 2))})
LITERALS=(
{
'v34':'''
000 addi 2 2 -64
002 store 2 8 56 4
004 addi 8 10 -1
008 store 2 18 48 4
00a store 2 20 40 4
00c store 2 21 36 4
00e store 2 23 28 4
010 slli 8 8 16
012 store 2 1 60 4
014 store 2 9 52 4
016 store 2 19 44 4
018 store 2 22 32 4
01a li 23 2
01c mv 20 10
01e mv 18 12
020 mv 21 13
022 srli 8 8 16
024 bne 11 23 362
028 lui 23 536883200
02c load 15 23 -92 1
030 mv 22 23
032 li 9 2
034 beqz 15 112
036 load 19 13 1 1
03a load 15 13 0 1
03c li 9 4
03e slli 19 19 8
040 or 19 19 15
044 lui 15 536883200
048 load 15 15 508 2
04c addi 15 15 -3
04e bge 19 15 112
052 addi 15 12 -4
056 bne 19 15 240
05a li 10 12
05c store 2 11 12 4
05e auipc 1 536530944
062 jalr 1 1 218
066 mv 8 10
068 load 11 2 12 4
06a bnez 10 136
06c addi 9 0 255
070 load 1 2 60 4
072 load 8 2 56 4
074 mv 10 9
076 load 18 2 48 4
078 load 9 2 52 4
07a load 19 2 44 4
07c load 20 2 40 4
07e load 21 2 36 4
080 load 22 2 32 4
082 load 23 2 28 4
084 addi 2 2 64
086 jr 1
088 slli 18 18 16
08a srli 18 18 16
08e store 10 11 4 1
090 store 10 18 6 2
094 addi 15 0 -112
098 addi 18 18 5
09a lui 11 32768
09c store 10 15 0 2
09e store 10 20 2 2
0a2 addi 11 11 1
0a4 mv 10 18
0a6 auipc 1 536530944
0aa jalr 1 1 -356
0ae store 8 10 8 4
0b0 beqz 10 228
0b2 load 15 23 -92 1
0b6 addi 11 21 -2
0ba srli 12 18 2
0be addi 15 15 -1
0c0 store 23 15 -92 1
0c4 auipc 1 536530944
0c8 jalr 1 1 426
0cc load 15 8 8 4
0ce mv 11 8
0d0 addi 15 15 2
0d2 store 8 15 8 4
0d4 lui 15 536883200
0d8 load 10 15 788 1
0dc jal 1 274952
0e0 li 9 0
0e2 jump 112
0e4 mv 10 8
0e6 auipc 1 536530944
0ea jalr 1 1 -212
0ee jump 108
0f0 addi 15 12 -3
0f4 blt 19 15 108
0f8 li 15 12
0fa mul 8 8 15
0fe lui 9 536883200
102 load 15 9 792 4
106 add 15 15 8
108 load 14 15 10 1
10a beqz 14 280
10c load 10 15 0 4
10e beqz 10 280
110 auipc 1 536530944
114 jalr 1 1 -254
118 addi 10 19 4
11c lui 11 32768
11e slli 10 10 16
120 addi 11 11 1
122 srli 10 10 16
124 load 20 9 792 4
128 auipc 1 536530944
12c jalr 1 1 -486
130 load 15 9 792 4
134 add 20 20 8
136 store 20 10 0 4
13a add 15 15 8
13c load 10 15 0 4
13e beqz 10 108
140 li 14 1
142 store 15 14 10 1
144 load 15 22 -92 1
148 mv 12 18
14a mv 11 21
14c addi 15 15 -1
14e store 22 15 -92 1
152 auipc 1 536530944
156 jalr 1 1 226
15a load 15 9 792 4
15e add 8 8 15
160 store 8 18 6 2
164 store 8 19 4 2
168 jump 224
16a li 15 12
16c mul 8 8 15
170 lui 22 536883200
174 load 15 22 792 4
178 mv 19 22
17a add 15 15 8
17c load 14 15 6 2
17e load 10 15 0 4
180 beqz 14 550
182 load 15 15 4 2
184 add 13 14 12
188 addi 15 15 4
18a blt 15 13 550
18e add 10 10 14
190 mv 11 21
192 auipc 1 536530944
196 jalr 1 1 162
19a load 14 22 792 4
19e li 9 0
1a0 add 14 14 8
1a2 load 15 14 6 2
1a4 add 15 15 18
1a6 slli 15 15 16
1a8 srli 15 15 16
1aa store 14 15 6 2
1ac load 14 14 4 2
1ae addi 14 14 4
1b0 bne 15 14 112
1b4 li 10 12
1b6 auipc 1 536530944
1ba jalr 1 1 -126
1be mv 11 10
1c0 beqz 10 506
1c2 addi 15 0 -112
1c6 store 10 15 0 2
1c8 load 15 22 792 4
1cc store 10 23 4 1
1d0 store 10 20 2 2
1d4 add 15 15 8
1d6 load 14 15 6 2
1d8 load 15 15 0 4
1da store 10 14 6 2
1dc store 10 15 8 4
1de lui 15 536883200
1e2 load 10 15 788 1
1e6 jal 1 274952
1ea load 15 22 792 4
1ee add 8 8 15
1f0 store 8 0 6 2
1f4 store 8 0 10 1
1f8 jump 112
1fa load 15 22 792 4
1fe add 15 15 8
200 load 10 15 0 4
202 beqz 10 534
204 auipc 1 536530944
208 jalr 1 1 -498
20c load 15 22 792 4
210 add 15 15 8
212 store 15 0 0 4
216 load 15 19 792 4
21a add 8 8 15
21c store 8 0 6 2
220 store 8 0 10 1
224 jump 224
226 beqz 10 570
228 auipc 1 536530944
22c jalr 1 1 -534
230 load 15 19 792 4
234 add 15 15 8
236 store 15 0 0 4
23a load 15 19 792 4
23e li 9 1
240 add 8 8 15
242 store 8 0 6 2
246 store 8 0 10 1
24a jump 112
''',
'wordcopy':'''
000 lui 14 1073889280
004 load 15 14 524 4
008 store 14 0 524 4
00c fence.i 
010 beqz 10 22
012 beqz 11 22
014 bnez 12 32
016 lui 14 1073889280
01a store 14 15 524 4
01e jr 1
020 addi 11 11 4
022 load 14 11 -4 4
026 addi 10 10 4
028 addi 12 12 -1
02a store 10 14 -4 4
02e jump 20
'''
},
{
'v34':'''
000 addi 2 2 -64
002 store 2 8 56 4
004 addi 8 10 -1
008 store 2 18 48 4
00a store 2 20 40 4
00c store 2 21 36 4
00e store 2 23 28 4
010 slli 8 8 16
012 store 2 1 60 4
014 store 2 9 52 4
016 store 2 19 44 4
018 store 2 22 32 4
01a li 23 2
01c mv 20 10
01e mv 18 12
020 mv 21 13
022 srli 8 8 16
024 bne 11 23 362
028 lui 23 536883200
02c load 15 23 -12 1
030 mv 22 23
032 li 9 2
034 beqz 15 112
036 load 19 13 1 1
03a load 15 13 0 1
03c li 9 4
03e slli 19 19 8
040 or 19 19 15
044 lui 15 536883200
048 load 15 15 588 2
04c addi 15 15 -3
04e bge 19 15 112
052 addi 15 12 -4
056 bne 19 15 240
05a li 10 12
05c store 2 11 12 4
05e auipc 1 536530944
062 jalr 1 1 50
066 mv 8 10
068 load 11 2 12 4
06a bnez 10 136
06c addi 9 0 255
070 load 1 2 60 4
072 load 8 2 56 4
074 mv 10 9
076 load 18 2 48 4
078 load 9 2 52 4
07a load 19 2 44 4
07c load 20 2 40 4
07e load 21 2 36 4
080 load 22 2 32 4
082 load 23 2 28 4
084 addi 2 2 64
086 jr 1
088 slli 18 18 16
08a srli 18 18 16
08e store 10 11 4 1
090 store 10 18 6 2
094 addi 15 0 -112
098 addi 18 18 5
09a lui 11 32768
09c store 10 15 0 2
09e store 10 20 2 2
0a2 addi 11 11 1
0a4 mv 10 18
0a6 auipc 1 536530944
0aa jalr 1 1 -524
0ae store 8 10 8 4
0b0 beqz 10 228
0b2 load 15 23 -12 1
0b6 addi 11 21 -2
0ba srli 12 18 2
0be addi 15 15 -1
0c0 store 23 15 -12 1
0c4 auipc 1 536530944
0c8 jalr 1 1 258
0cc load 15 8 8 4
0ce mv 11 8
0d0 addi 15 15 2
0d2 store 8 15 8 4
0d4 lui 15 536883200
0d8 load 10 15 868 1
0dc jal 1 275092
0e0 li 9 0
0e2 jump 112
0e4 mv 10 8
0e6 auipc 1 536530944
0ea jalr 1 1 -380
0ee jump 108
0f0 addi 15 12 -3
0f4 blt 19 15 108
0f8 li 15 12
0fa mul 8 8 15
0fe lui 9 536883200
102 load 15 9 872 4
106 add 15 15 8
108 load 14 15 10 1
10a beqz 14 280
10c load 10 15 0 4
10e beqz 10 280
110 auipc 1 536530944
114 jalr 1 1 -422
118 addi 10 19 4
11c lui 11 32768
11e slli 10 10 16
120 addi 11 11 1
122 srli 10 10 16
124 load 20 9 872 4
128 auipc 1 536530944
12c jalr 1 1 -654
130 load 15 9 872 4
134 add 20 20 8
136 store 20 10 0 4
13a add 15 15 8
13c load 10 15 0 4
13e beqz 10 108
140 li 14 1
142 store 15 14 10 1
144 load 15 22 -12 1
148 mv 12 18
14a mv 11 21
14c addi 15 15 -1
14e store 22 15 -12 1
152 auipc 1 536530944
156 jalr 1 1 58
15a load 15 9 872 4
15e add 8 8 15
160 store 8 18 6 2
164 store 8 19 4 2
168 jump 224
16a li 15 1
16c bne 11 15 108
170 li 15 12
172 mul 8 8 15
176 lui 22 536883200
17a load 15 22 872 4
17e mv 19 22
180 add 15 15 8
182 load 14 15 6 2
184 load 10 15 0 4
186 beqz 14 556
188 load 15 15 4 2
18a add 13 14 12
18e addi 15 15 4
190 blt 15 13 556
194 add 10 10 14
196 mv 11 21
198 auipc 1 536530944
19c jalr 1 1 -12
1a0 load 14 22 872 4
1a4 li 9 0
1a6 add 14 14 8
1a8 load 15 14 6 2
1aa add 15 15 18
1ac slli 15 15 16
1ae srli 15 15 16
1b0 store 14 15 6 2
1b2 load 14 14 4 2
1b4 addi 14 14 4
1b6 bne 15 14 112
1ba li 10 12
1bc auipc 1 536530944
1c0 jalr 1 1 -300
1c4 mv 11 10
1c6 beqz 10 512
1c8 addi 15 0 -112
1cc store 10 15 0 2
1ce load 15 22 872 4
1d2 store 10 23 4 1
1d6 store 10 20 2 2
1da add 15 15 8
1dc load 14 15 6 2
1de load 15 15 0 4
1e0 store 10 14 6 2
1e2 store 10 15 8 4
1e4 lui 15 536883200
1e8 load 10 15 868 1
1ec jal 1 275092
1f0 load 15 22 872 4
1f4 add 8 8 15
1f6 store 8 0 6 2
1fa store 8 0 10 1
1fe jump 112
200 load 15 22 872 4
204 add 15 15 8
206 load 10 15 0 4
208 beqz 10 540
20a auipc 1 536530944
20e jalr 1 1 -672
212 load 15 22 872 4
216 add 15 15 8
218 store 15 0 0 4
21c load 15 19 872 4
220 add 8 8 15
222 store 8 0 6 2
226 store 8 0 10 1
22a jump 224
22c beqz 10 576
22e auipc 1 536530944
232 jalr 1 1 -708
236 load 15 19 872 4
23a add 15 15 8
23c store 15 0 0 4
240 load 15 19 872 4
244 li 9 1
246 add 8 8 15
248 store 8 0 6 2
24c store 8 0 10 1
250 jump 112
''',
'wordcopy':'''
000 lui 14 1073889280
004 load 15 14 524 4
008 store 14 0 524 4
00c fence.i 
010 beqz 10 22
012 beqz 11 22
014 bnez 12 32
016 lui 14 1073889280
01a store 14 15 524 4
01e jr 1
020 addi 11 11 4
022 load 14 11 -4 4
026 addi 10 10 4
028 addi 12 12 -1
02a store 10 14 -4 4
02e jump 20
'''
}
)

def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'task5 V34 literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=pc
        out[pc+int(off,16)]=f
    return out


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    if part=='wordcopy':check(raw[12:16]==bytes.fromhex('0f100000'),'V34 wordcopy fence bytes')
    for off,f3 in TYPED_LOADS[index][part]:
        check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'V34 typed load encoding')
    n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'V34 complete boundaries '+part)
    for p,f in s.items():init.g(n,p,'V34 operand '+part+' '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[index][k],COUNTS[index][k],HASHES[index][k]),'V34 complete identity '+part)
    e={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'V34 ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':check(v['rd']==1,'V34 linked call');calls.append({'offset':p-pc,'target':v['target']})
        elif op=='jalr':
            check(v['rd']==v['rs1']==1 and n[p-4]['op']=='auipc' and n[p-4]['rd']==1,'V34 linked pair')
            calls.append({'offset':p-pc,'target':(p-4+n[p-4]['imm']+v['imm'])&0xfffffffe})
        check(all(q in n for q in qs),'V34 closed CFG');e[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(e[p])
    check(seen==set(n),'V34 all nodes reachable')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(calls),len(rets))==((13,1) if part=='v34' else (0,1)),'V34 call/return census')
    check(common.acyclic(e)==(part=='v34'),'V34 cycle classification')
    if part=='wordcopy':
        cut={p:list(qs) for p,qs in e.items()};cut[pc+46].remove(pc+20);check(common.acyclic(cut),'V34 wordcopy sole loop')
        check(sorted({v['rd'] for v in n.values() if v.get('rd',0)})==[10,11,12,14,15],'V34 wordcopy GPR writes')
    return {'start':pc,'source':SOURCES[index][k],'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
      'CFG':e,'calls':calls,'tails':[],'returns':rets,'stores':stores,'complete_local_body':True,'actual_progress_proved':False}


def return_paths(b,index):
    pc=b['start'];n={v['pc']-pc:v for v in b['instructions']}
    paths=allocation.previous.dag_paths(b);categories=Counter();examples={}
    for seq in paths:
        common.previous.valid(b['CFG'],[pc+o for o in seq])
        check(seq[-1]==0x86 and 0x74 in seq,'V34 sole epilogue path')
        before=seq[:seq.index(0x74)];defs=[o for o in before if n[o].get('rd')==9]
        check(bool(defs),'V34 every local return defines S1')
        v=n[defs[-1]];check((v['op']=='li' or v['op']=='addi' and v['rs1']==0) and v['imm'] in (0,1,2,4,255),'V34 final local S1 is fixed status');reply=str(v['imm'])
        categories[reply]+=1;examples.setdefault(reply,seq)
    check(set(categories)=={'0','1','2','4','255'},'V34 complete conditional return classes')
    if index:
        # This path chooses both mode tests as unequal. Feasibility requires
        # entry mode not1/2; no register or memory state is executed here.
        rejected=[s for s in paths if 0x16c in s and 0x170 not in s]
        check(len(rejected)==1,'V34 exactly one unsupported-mode syntactic path')
        s=rejected[0];check(0x16a in s and 0x6c in s and 0x28 not in s,'V34 rejected mode loads255 then epilogue')
        check(not any(pc+o==pc+c['offset'] for o in s for c in b['calls']),'V34 rejected mode has no nested call')
        examples['V140_unsupported_mode_255']=s
    return {'syntactic_DAG_paths':len(paths),'return_class_path_counts':dict(sorted(categories.items())),
      'walks_sha256':sha256(json.dumps(paths,separators=(',',':')).encode()).hexdigest(),'examples':examples,
      'all_syntactic_paths_feasible_or_runtime_terminating_proved':False}


def domains():
    digest=sha256();shortfall=[];byte_lengths=0
    for length in range(65536):
        count=(length+5)>>2;copied=4*count;core_rounded=((length+8)&65535)&0xfffc
        check(copied==((length+2+3)//4)*4 and 2<=copied-length<=5,'V34 word/byte count identity')
        if core_rounded<copied:shortfall.append(length)
        if 4<=length<=255:
            check(copied<=core_rounded<=260 and count<=65,'V34 table0 byte-length size bound');byte_lengths+=1
        digest.update(count.to_bytes(2,'little')+copied.to_bytes(4,'little')+core_rounded.to_bytes(2,'little'))
    check(shortfall==list(range(65528,65536)) and byte_lengths==252,'V34 full U16 rounding classification')
    indices=[]
    for identity in range(65536):
        index=(identity-1)&65535;offset=12*index
        check(0<=offset<=786420 and offset%12==0,'V34 wrapped ID record offset')
        if identity in (0,1,2,65535):indices.append([identity,index,offset])
    for credit in range(256):
        check((((credit-1)&255)+1)&255==credit,'V34 credit decrement/release increment modulo inverse only')
    # All possible maxima are classified without enumerating a mutable payload.
    for maximum in range(65536):
        accepted=max(0,maximum-3)
        check(accepted==0 if maximum<=3 else accepted==maximum-3,'V34 signed max-3 header acceptance count')
        if maximum>=4:
            last=maximum-4;check(0<=last<=65531 and last+4<=65535,'V34 exact-match ordinary length domain')
    current=[]
    for length in range(4,252):
        header=length-4;check(header<251-3 and ((length+8)&65535)&0xfffc>=4*((length+5)>>2),'V34 retained config251 excludes size wrap')
        current.append(length)
    # Pointer translations and source extent; identities only, no byte copies.
    for sample in (0,1,2,0x20000000,0xfffffffe,0xffffffff):
        check((((sample+2)&0xffffffff)-2)&0xffffffff==sample,'V34 table0 plus2 minus2 pointer join')
    return {'length_U16_cases':65536,'length_vectors_sha256':digest.hexdigest(),'core_rounded_smaller_than_copy_lengths':shortfall,
      'table0_exact_match_length_cases':byte_lengths,'retained_config251_exact_match_lengths':[current[0],current[-1]],
      'ID_U16_cases':65536,'ID_offset_examples':indices,'credit_modulo_cases':256,'maximum_U16_cases':65536,
      'copy_formula':'N=(low16(L)+5)>>2;copied_bytes=4*N=roundup4(low16(L)+2);core_rounded=((low16(L)+8)&65535)&0xfffc',
      'current_call_domain':'table0 uses U8 length; exact match requires4<=L<=255. If fresh config max remains251, further L<=251. Neither premise is a universal V34 ABI',
      'actual_reachability_or_allocation_extent_or_ownership_proved':False}


def profile(data,hexraw,index):
    bs={p:body(init.binding.take(data,SOURCES[index][k],SIZES[index][k]),p,index) for k,p in enumerate(PARTS)}
    v,w=bs['v34'],bs['wordcopy'];pc=v['start'];n={x['pc']-pc:x for x in v['instructions']}
    sender=common.STARTS[index][2]
    expected=[(0x62,0x20000236),(0xaa,0x20000040),(0xc8,0x2000036c),(0xdc,sender),(0xea,0x20000110),
      (0x114,0x20000110),(0x12c,0x20000040),(0x156,0x20000332),(0x196+6*index,0x20000332),
      (0x1ba+6*index,0x20000236),(0x1e6+6*index,sender),(0x208+6*index,0x20000110),(0x22c+6*index,0x20000110)]
    check([(c['offset'],c['target']) for c in v['calls']]==expected,'V34 complete nested target census')
    check(n[0x74]['op']=='mv' and n[0x74]['rd']==10 and n[0x74]['rs2']==9 and n[0x78]['rd']==9,'V34 S1 reply precedes S1 restore')
    check(n[0x24]['rs1']==11 and n[0x24]['rs2']==23 and n[0x1a]['imm']==2,'V34 mode2 first branch')
    if index:
        check(n[0x16a]['imm']==1 and n[0x16c]['target']==pc+0x6c and n[0x16c]['op']=='bne','V34 version-specific reject loads255 before epilogue')
        encoded=bytes.fromhex(n[0x16c]['bytes']);check(encoded==bytes.fromhex('e390f5f0'),'V34 original reject branch bytes')
        word=int.from_bytes(encoded,'little');imm=((word>>31&1)<<12)|((word>>7&1)<<11)|((word>>25&63)<<5)|((word>>8&15)<<1)
        displacement=imm-8192 if imm&4096 else imm
        check(displacement==-256 and pc+0x16c+displacement==pc+0x6c,'V34 independent B-immediate sign/target algebra')
    G=0x20003000;credit=0x20002fa4+80*index;records=0x20003318+80*index;task=records-4;maximum=0x200031fc+80*index
    check(n[0x2c]['imm']+G==n[0xb2]['imm']+G==n[0xc0]['imm']+G==n[0x144]['imm']+G==n[0x14e]['imm']+G==credit,'V34 credit source/writer addresses')
    check(n[0x48]['imm']+G==maximum and n[0x102]['imm']+G==records and n[0xd8]['imm']+G==task,'V34 distinct max/record/task slots')
    check(n[0xb6]['imm']==-2 and n[0xba]['imm']==2 and n[0x98]['imm']==5,'V34 wordcopy source minus2 and word-count formation')
    check(n[0xd0]['imm']==2 and n[0xd2]['imm']==8 and n[0xcc]['imm']==8,'V34 fresh message pointer shifted2 after wordcopy')
    check(n[0x124]['rd']==20 and n[0x130]['rd']==15 and n[0x136]['rs1']==20 and n[0x13c]['rs1']==15,'V34 captures old array but tests fresh array after core')
    check(n[0x13e]['op']=='beqz' and n[0x13e]['rs1']==10,'V34 alternate test is reloaded record pointer')
    objects=allocation.previous.previous;ob=objects.body(init.binding.take(data,objects.STARTS[index][0],objects.SIZES[0]),'table0',index)
    adapter=objects.body(init.binding.take(data,objects.STARTS[index][2],4),'adapter',index)
    check(adapter['tails']==[{'offset':0,'target':pc,'new_link':False}],'V34 adapter full-body join')
    on={x['pc']-ob['start']:x for x in ob['instructions']}
    check(on[0xa]['op']=='lui' and on[0xa]['rd']==9 and on[0xa]['imm']==0x40024000,'V34 table0 control base source')
    check(on[0x60]['width']==on[0x62]['width']==1 and on[0x66]['imm']==2,'V34 table0 byte inputs and source+2 join')
    # Reuse every nested callee identity under its original contract.
    life=common.previous;closure=life.previous;core=closure.core
    core_n,_=closure.core_body(init.binding.take(data,core.DETAILS[index][0],208),index)
    free_n,_=life.free_body(init.binding.take(data,life.release.DETAILS[index][0],212),index)
    check(life.release.DETAILS[index][3]==credit,'V34 release special-tag counter is same byte')
    message=common.message;mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy']
    def src(target):return int(first['source'],16)+target-int(first['destination'],16)
    msgraw=init.binding.take(data,src(0x20000236),86)
    check(msgraw==message.MSG and sha256(msgraw).hexdigest()==message.MSG_SHA,'V34 message wrapper identity')
    mn=message.decode(msgraw,message.ENTRY)
    for p,f in message.message_specs().items():message.guard(mn,p,'V34 message wrapper operand',**f)
    sb=common.body(init.binding.take(data,sender,146),'sender',index)
    payload=previous.arithmetic.payload
    cb=payload.body(init.binding.take(data,src(0x20000332),58),'copy',0x20000332,58,18,3,init.binding.COPY_HASH)
    check(SOURCES[index][1]==src(0x2000036c) and 0x2000036c+48<=int(mapping['first_copy_end_exclusive'],16),'V34 complete wordcopy source mapping')
    check(not any(x.get('rd')==9 for x in free_n.values()) and not any(x.get('rd')==9 for x in cb['instructions']),'V34 reused private free/bytecopy S1 nonwrites')
    _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
    for p,b in bs.items():
        check(sparse.captured(mem,b['source'],b['bytes'])==init.binding.take(data,b['source'],b['bytes']),'V34 strict original HEX source')
        receipts.append({'part':p,'source':b['source'],'bytes':b['bytes'],'all_bytes_captured':True})
    return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,
      'CFG_certificates':{p:common.certificates(b) for p,b in bs.items()},'return_paths':return_paths(v,index),
      'roles':{'credit_byte':credit,'maximum_U16':maximum,'record_array_pointer':records,'outgoing_task_byte':task},
      'reused_bodies':{'core':{'source':core.DETAILS[index][0],'bytes':208},'private_release':{'source':life.release.DETAILS[index][0],'bytes':212},
        'message_allocator':{'source':src(0x20000236),'bytes':86,'sha256':message.MSG_SHA},'sender':{'start':sender,'bytes':146,'sha256':sb['sha256']},
        'bytecopy':{'source':src(0x20000332),'bytes':58,'sha256':cb['sha256']},'table0':{'start':ob['start'],'bytes':ob['bytes'],'sha256':ob['sha256']},'new_code_bytes_counted':0},
      'input_contract':'I=entryA0,mode=entryA1,L=entryA2 fullRV32,S=entryA3;offset12*((I-1)&65535),no key/tableextent/nullarray guard; table0 narrows I toU16,mode/length toU8,S=(sampled node4+2)mod32',
      'mode2_contract':['credit0 ->2 without payload reads;otherwise read two bytes atS before length checks;K=LE16(S),freshmaxM; signed K>=signed(M-3) ->4',
        'K==(L-4)mod32:allocate message12;null ->255;set half0ff90/half2low16I/byte4mode/half6low16L;core(low16L+5,8001);storeP inmessage8;directP0 ->release message attempt then255',
        'Pnonnull:freshcredit decrement mod256;wordcopy(P,S-2,(low16L+5)>>2);freshmessage8+=2;sender(freshtask,message);ignore sendreply,return0',
        'otherwise signed K<signed(L-3) ->255;else indexedrecord:optional oldpayload release ifbyte10 andword0 nonzero;core(low16(K+4),8001)',
        'capture arraybase before core,store result throughcaptured base but testrecord0throughfreshbase;that test isnot directly core reply unless identity holds',
        'fresh testedrecordptrnonnull:byte10=1;freshcredit--;bytecopy(ptr,S,L);freshrecord6=low16L,record4=K;return0;null testedrecordptr ->255'],
      'continuation_contract':['V131allmode!=2,V140mode1 only;loadrecord6cur andrecord0buffer;cur0 or signed(record4+4)<signed((cur+L)mod32) ->optionalrelease/clearrecord0,clearfreshrecord6/10,return1',
        'else bytecopy(buffer+cur,S,L);freshcur reloaded,SHlow16(freshcur+L);reply0;compare withfreshrecord4+4;different ->0 without sending',
        'equal ->allocate message12;nonnull:set headerff90/key/type2/freshrecord6/record0;send;ignore status;freshrecord6/10=0,record0 retained,return0',
        'completion messagealloc0:optionalrelease(freshrecord0),clearrecord0 if release branch taken;clearfreshrecord6/10;return0'],
      'wordcopy_contract':['control4002420c read/zero/FENCE.I precedes null/count guards;restore control on normal exit;no frame/calls/S-register/RA writes',
        'if D0 orS0 orN0:no data transfer,A0/A1/A2 unchanged;else N forwardLW/SW words,A0=D+4N,A1=S+4N mod32,A2=0',
        'no alignment/extent/overlap/wrap checks;not snapshot/memmove;normal control effects and no adverse aliases/interference remain premises'],
      'return_contract':'both profiles local classes0/1/2/4/255;V140 unsupported mode branches to+6c loading255 before epilogue+70. V131 all mode!=2 enterscontinuation;V140 onlymode1. Table0 pops only after reply0 with its separate freshhead/ownership premises;0 doesnotprove delivery',
      'ownership_boundary':'sender reply ignored;0 isnotdelivery/ownership proof. mode2 outgoing pointer isfreshmessage8+2,notadvancedcopyA0;continuation publishesexistingrecordpointer andretainsrecord0. Private release doesnotrecursivelyfreepayload orprove safe lateraccess',
      'premises':'matching conditional candidate code/ISA/source mapping;valid frames/control/globals/record/payload accesses andnormal callee preservation;freshreadidentity onlywithretention;no adverse alias/IRQ/DMA/reentry/unaccounted writers',
      'actual_installed_binding_or_delivery_or_payload_lifetime_proved':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage,hexes):
    previous.derive(image,carriers,header,coverage,hexes)
    profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))]
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==1278,'V34 byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==448,'V34 instruction census')
    return {'schema':'TSL9-task5-v34-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'complete_body_bytes':1278,'complete_body_instructions':448,'C_reconstruction_coverage_changed':False,
      'remaining':['record/task/credit writers and real index/length domains','downstream message consumption and payload release/lifetime','actual installed provider and hardware progress'],
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
    mutations=typed=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,SOURCES[i][k],SIZES[i][k]);n=decode(raw,STARTS[i][k])
            for p,v in n.items():
                off=p-STARTS[i][k];z=v['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(bad,part,i)
                except RuntimeError:pass
                else:raise RuntimeError('V34 instruction mutation escaped')
                mutations+=1
            for off,f3 in TYPED_LOADS[i][part]:
                bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
                try:body(bad,part,i)
                except RuntimeError as ex:check('typed load encoding' in str(ex),'V34 exact typed-load guard')
                else:raise RuntimeError('V34 load type mutation escaped')
                typed+=1
    raw=bytearray(init.binding.take(carriers[1],SOURCES[1][0],SIZES[1][0]));off=0x16c
    raw[off:off+4]=(int.from_bytes(raw[off:off+4],'little')^(1<<9)).to_bytes(4,'little')
    check(decode(raw,STARTS[1][0])[STARTS[1][0]+off]['target']==STARTS[1][0]+0x70,'V34 regression fixture targets epilogue skipping255')
    try:body(raw,'v34',1)
    except RuntimeError as ex:check('V34 operand' in str(ex),'V34 wrong epilogue target specific guard')
    else:raise RuntimeError('V34 wrong+70 target escaped')
    check((mutations,typed)==(448,44),'V34 mutation census');domains()
    print('PASS:448 instruction/44 typed-load + wrong-epilogue-target mutations rejected;65536 length/max/index cases;closed V34 DAG return paths')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
    ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    raw=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if args.write:
        with OUT.open('xb') as f:f.write(raw)
    else:check(OUT.read_bytes()==raw,'V34 exact ledger replay')
    print('PASS:1278B/448i complete V34+wordcopy;strict HEX backing;all nested targets joined;exact ledger')
    print('PASS:NO target execution/emulation;installed binding,delivery,postrelease/payload ownership UNPROVED')


if __name__=='__main__':main()


