"""Offline candidate task5 parser, dispatch table and message-lifetime joins.

Original operands, immutable CFG witnesses and scalar/interval certificates.
No target ISA, mutable message/list/heap/register machine, provider or MMIO runs.
"""
import argparse,json
from collections import Counter
from hashlib import sha256
from pathlib import Path
import check_v4160_app_task_1995c_static as previous
import check_v4160_list_setup_handler_static as handler
import check_v4160_constructor_consumer_tail_static as lookup

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
OUT=Path(__file__).with_name('v4160-task5-parser-static.json')
PARTS=('parser',)
STARTS=((0x5e230,),(0x5e378,))
SOURCES=STARTS
SIZES=(376,)
COUNTS=(130,)
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
UNSIGNED=((0x9c,2),(0xc4,1),(0xc8,1),(0xe8,1),(0xee,1),(0x10a,2),(0x10e,2),(0x112,1),(0x118,1),(0x12c,2),(0x14e,1),(0x166,1))
TABLES=(0x6e5ec,0x6e7dc)
VENEER_OFFSETS=(0,4,8,20,24,28,32)
HASHES=(('1faeef42b3e6bb70121591fba11430f4c10598ccfa9283780636b186e2d2f855',), ('887a8c59e74582db8da02dc81b0bedc8e1fd1cb898595196494696eb06d4ae0c',))
LITERALS=(
{
'parser':'''
000 addi 2 2 -16
002 store 2 1 12 4
004 store 2 8 8 4
006 load 14 10 0 1
008 addi 15 0 128
00c bne 14 15 50
010 load 14 10 1 1
012 addi 13 0 44
016 li 15 1
018 bltu 13 14 122
01c lui 15 450560
020 slli 14 14 2
022 addi 15 15 1516
026 add 15 15 14
028 load 15 15 0 4
02a load 10 10 2 2
02c call_indirect 1 15
02e li 15 0
030 jump 122
032 addi 13 0 129
036 li 15 1
038 bne 14 13 122
03c load 14 10 1 1
03e li 13 19
040 beq 14 13 290
044 bltu 13 14 104
048 li 13 8
04a beq 14 13 222
04e li 13 12
050 beq 14 13 256
054 li 13 5
056 bne 14 13 122
05a load 10 10 2 2
05c jal 1 358474
060 mv 8 10
062 bnez 10 150
064 li 15 2
066 jump 122
068 addi 13 0 48
06c beq 14 13 344
070 bltu 13 14 132
074 li 13 26
076 beq 14 13 324
07a load 1 2 12 4
07c load 8 2 8 4
07e mv 10 15
080 addi 2 2 16
082 jr 1
084 addi 15 0 87
088 beq 14 15 368
08c addi 15 14 -255
090 sltu 15 0 15
094 jump 122
096 load 15 10 280 4
09a beqz 15 196
09c load 12 10 68 2
0a0 addi 12 12 1
0a2 slli 12 12 16
0a4 srli 12 12 16
0a6 load 15 15 0 4
0a8 addi 14 12 1
0ac slli 14 14 16
0ae srli 14 14 16
0b0 bnez 15 218
0b2 store 8 12 68 2
0b6 beqz 12 196
0b8 load 11 8 8 2
0ba li 10 1
0bc jal 1 435988
0c0 store 8 0 68 2
0c4 load 10 8 43 1
0c8 load 12 8 84 1
0cc load 11 8 8 2
0ce jal 1 435968
0d2 mv 10 8
0d4 jal 1 358222
0d8 jump 46
0da mv 12 14
0dc jump 166
0de load 10 10 2 2
0e0 jal 1 358474
0e4 mv 8 10
0e6 beqz 10 100
0e8 load 12 10 76 1
0ec load 11 10 8 2
0ee load 10 10 43 1
0f2 sltu 12 0 12
0f6 jal 1 435972
0fa store 8 0 43 1
0fe jump 46
100 load 10 10 2 2
102 jal 1 358474
106 mv 8 10
108 beqz 10 100
10a load 14 10 82 2
10e load 13 10 80 2
112 load 12 10 79 1
116 load 11 10 8 2
118 load 10 10 43 1
11c jal 1 435976
120 jump 250
122 load 10 10 2 2
124 jal 1 358474
128 mv 8 10
12a beqz 10 100
12c load 12 10 68 2
130 beqz 12 318
132 load 11 10 8 2
134 li 10 1
136 jal 1 435988
13a store 8 0 68 2
13e store 8 0 49 1
142 jump 46
144 load 10 10 2 2
146 jal 1 358474
14a beq 10 0 100
14e load 10 10 43 1
152 jal 1 435992
156 jump 46
158 load 10 10 2 2
15a jal 1 358474
15e mv 8 10
160 beq 10 0 100
164 load 11 10 8 2
166 load 10 10 43 1
16a jal 1 435996
16e jump 250
170 load 10 10 2 2
172 jal 1 436000
176 jump 46
'''
},
{
'parser':'''
000 addi 2 2 -16
002 store 2 1 12 4
004 store 2 8 8 4
006 load 14 10 0 1
008 addi 15 0 128
00c bne 14 15 50
010 load 14 10 1 1
012 addi 13 0 44
016 li 15 1
018 bltu 13 14 122
01c lui 15 450560
020 slli 14 14 2
022 addi 15 15 2012
026 add 15 15 14
028 load 15 15 0 4
02a load 10 10 2 2
02c call_indirect 1 15
02e li 15 0
030 jump 122
032 addi 13 0 129
036 li 15 1
038 bne 14 13 122
03c load 14 10 1 1
03e li 13 19
040 beq 14 13 290
044 bltu 13 14 104
048 li 13 8
04a beq 14 13 222
04e li 13 12
050 beq 14 13 256
054 li 13 5
056 bne 14 13 122
05a load 10 10 2 2
05c jal 1 358794
060 mv 8 10
062 bnez 10 150
064 li 15 2
066 jump 122
068 addi 13 0 48
06c beq 14 13 344
070 bltu 13 14 132
074 li 13 26
076 beq 14 13 324
07a load 1 2 12 4
07c load 8 2 8 4
07e mv 10 15
080 addi 2 2 16
082 jr 1
084 addi 15 0 87
088 beq 14 15 368
08c addi 15 14 -255
090 sltu 15 0 15
094 jump 122
096 load 15 10 280 4
09a beqz 15 196
09c load 12 10 68 2
0a0 addi 12 12 1
0a2 slli 12 12 16
0a4 srli 12 12 16
0a6 load 15 15 0 4
0a8 addi 14 12 1
0ac slli 14 14 16
0ae srli 14 14 16
0b0 bnez 15 218
0b2 store 8 12 68 2
0b6 beqz 12 196
0b8 load 11 8 8 2
0ba li 10 1
0bc jal 1 436472
0c0 store 8 0 68 2
0c4 load 10 8 43 1
0c8 load 12 8 84 1
0cc load 11 8 8 2
0ce jal 1 436452
0d2 mv 10 8
0d4 jal 1 358542
0d8 jump 46
0da mv 12 14
0dc jump 166
0de load 10 10 2 2
0e0 jal 1 358794
0e4 mv 8 10
0e6 beqz 10 100
0e8 load 12 10 76 1
0ec load 11 10 8 2
0ee load 10 10 43 1
0f2 sltu 12 0 12
0f6 jal 1 436456
0fa store 8 0 43 1
0fe jump 46
100 load 10 10 2 2
102 jal 1 358794
106 mv 8 10
108 beqz 10 100
10a load 14 10 82 2
10e load 13 10 80 2
112 load 12 10 79 1
116 load 11 10 8 2
118 load 10 10 43 1
11c jal 1 436460
120 jump 250
122 load 10 10 2 2
124 jal 1 358794
128 mv 8 10
12a beqz 10 100
12c load 12 10 68 2
130 beqz 12 318
132 load 11 10 8 2
134 li 10 1
136 jal 1 436472
13a store 8 0 68 2
13e store 8 0 49 1
142 jump 46
144 load 10 10 2 2
146 jal 1 358794
14a beq 10 0 100
14e load 10 10 43 1
152 jal 1 436476
156 jump 46
158 load 10 10 2 2
15a jal 1 358794
15e mv 8 10
160 beq 10 0 100
164 load 11 10 8 2
166 load 10 10 43 1
16a jal 1 436480
16e jump 250
170 load 10 10 2 2
172 jal 1 436484
176 jump 46
'''
}
)
TABLE_TARGETS=((386062, 383660, 383588, 385254, 385208, 385164, 385106, 385062, 385512, 385516, 384024, 385520, 385000, 385524, 384966, 385528, 384902, 384886, 384832, 385532, 384800, 385536, 385540, 385544, 384706, 383592, 383612, 385548, 385552, 385556, 385560, 385564, 384610, 384492, 385568, 385572, 385576, 385580, 384392, 385504, 385508, 383794, 385406, 385308, 383616), (386390, 383988, 383916, 385582, 385536, 385492, 385434, 385390, 385840, 385844, 384352, 385848, 385328, 385852, 385294, 385856, 385230, 385214, 385160, 385860, 385128, 385864, 385868, 385872, 385034, 383920, 383940, 385876, 385880, 385884, 385888, 385892, 384938, 384820, 385896, 385900, 385904, 385908, 384720, 385832, 385836, 384122, 385734, 385636, 383944))
TABLE_HASHES=('977de44a84dc5f3aff95df573f31dc505341aa30f9eb6bae11c00d11cbb607f2', '6b9ee11871a88de640130f2b9355fc20dc4b501b90495bbf653cdebbd0bc7a80')
VENEER_TARGETS=((339638, 339706, 339780, 340158, 340028, 340088, None), (339806, 339874, 339948, 340326, 340196, 340256, None))
VENEER_HASHES=(('4f490ced7b72c0894d85a10777b818e4b82f77636f28af4636280fb5405076fa', '1a4ed6c30b101e53155b1296cd4ff242f15e28b565b1e25759baf1cbfacce65b', 'd6197210b256285082594c55233c4a345ce7ba632d3eb7f37513280412dc52f5', '84593a177e41a0f09945e70de06c22fda7bd46d2c1fa4b53200bef6c47dcd42f', 'd4aa4305bb954103e98daeafdfad85fbb6914319713eef255aea1f5676e4db7b', 'ecf25702806101346dc7c0c62790645cca6d01e29c47ec971a11767c5101232a', '7529d4e6ceb037815e2664a7277abb404b02f0bf9ddbf5c11658f52448221cba'), ('43f25a2186ec8237ff88540b9de2e8e73a9d8176e20a4e880c835c61f5280767', '6b064a4944af74e08c557dc5e2e74bba9e0afe80fa6336057a8a4855e20faaf5', '53c3ea574ff4bf6cee6e488b3989bc36f5354cfea6cb9210332855ddf7e15909', '17bca4344c5bb3733f4da9f105131c40e51c63fdb7bc7f02a2cc67456ec66c3c', 'db37e27a200e30d20d0bd3cf19f8495330e573c6ba1fca276d94d4d077eb13a9', '833d43af2f0fce37d1a707728bfacdc537495c7c3c3cb4ed64e69d753f0f41f4', '7529d4e6ceb037815e2664a7277abb404b02f0bf9ddbf5c11658f52448221cba'))


def specs(index):
    pc=STARTS[index][0];out={}
    for line in LITERALS[index]['parser'].splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'task5 parser literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=pc
        out[pc+int(off,16)]=f
    return out


def body(raw,index):
    pc=STARTS[index][0]
    for off,width in UNSIGNED:
        check(int.from_bytes(raw[off:off+4],'little')&0x707f=={1:0x4003,2:0x5003}[width],'task5 parser unsigned encoding')
    n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'task5 parser complete boundaries')
    for p,f in s.items():init.g(n,p,'task5 parser operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(376,130,HASHES[index][0]),'task5 parser original identity')
    edges={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'task5 parser ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':
            check(v['rd']==1,'task5 parser direct linked call');calls.append({'offset':p-pc,'target':v['target']})
        elif op=='call_indirect':
            check(v['rd']==1 and v['rs1']==15 and p==pc+0x2c,'task5 parser table-call register')
            calls.append({'offset':p-pc,'target':'fresh word from table[reason] & ~1','null_guard':False})
        check(all(q in n for q in qs),'task5 parser closed CFG');edges[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(edges[p])
    check(seen==set(n),'task5 parser all nodes reachable')
    cut={p:list(qs) for p,qs in edges.items()};cut[pc+0xdc].remove(pc+0xa6)
    check(not common.acyclic(edges) and common.acyclic(cut),'task5 parser sole list-loop backedge')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check([(v['offset'],v['base'],v['imm'],v['bytes']) for v in stores]==[(2,2,12,4),(4,2,8,4),(0xb2,8,68,2),(0xc0,8,68,2),(0xfa,8,43,1),(0x13a,8,68,2),(0x13e,8,49,1)],'task5 parser exact store census')
    check(len(calls)==16 and rets==[pc+0x82],'task5 parser call/return census')
    message_loads=[(p-pc,v['imm'],v['width']) for p,v in n.items() if v['op']=='load' and v['rs1']==10 and p<pc+0x96]
    check(message_loads==[(6,0,1),(0x10,1,1),(0x2a,2,2),(0x3c,1,1),(0x5a,2,2)],'task5 parser initial message extent')
    return {'start':pc,'bytes':376,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'CFG':edges,'calls':calls,'tails':[],
      'returns':rets,'stores':stores,'complete_local_body':True,'local_CFG_acyclic':False,'actual_list_or_callchain_termination_proved':False}


def table(raw,index):
    check(len(raw)==180,'task5 table exact extent')
    values=tuple(int.from_bytes(raw[j:j+4],'little') for j in range(0,180,4))
    check(values==TABLE_TARGETS[index],'task5 table exact word operands')
    check(sha256(raw).hexdigest()==TABLE_HASHES[index],'task5 table original identity')
    check(all(v and not v&1 for v in values),'task5 table captured entries nonzero/even')
    return {'start':TABLES[index],'bytes':180,'sha256':TABLE_HASHES[index],'entries':[{'reason':j,'raw_pointer':v,'effective_target':v&~1} for j,v in enumerate(values)],
      'index_bound':44,'each_callee_body_or_effects_proved':False,'actual_runtime_table_preserved_proved':False}


def veneer(raw,index,k):
    off=VENEER_OFFSETS[k];pc=0x6a700+484*index+off;size=2 if off==32 else 4;n=decode(raw,pc)
    check(len(raw)==size and len(n)==1,'task5 veneer complete instruction')
    if off==32:init.g(n,pc,'task5 reason87 RET veneer',op='jr',rs1=1)
    else:init.g(n,pc,'task5 unlinked veneer operand',op='jal',rd=0,target=VENEER_TARGETS[index][k])
    check(sha256(raw).hexdigest()==VENEER_HASHES[index][k],'task5 veneer exact identity')
    return {'start':pc,'bytes':size,'sha256':sha256(raw).hexdigest(),'instruction':n[pc],
      'target':VENEER_TARGETS[index][k],'new_link':False,'callee_body_or_physical_effects_proved':False}


def veneers(data,index):
    return [veneer(init.binding.take(data,0x6a700+484*index+off,2 if off==32 else 4),index,k) for k,off in enumerate(VENEER_OFFSETS)]


def selected(b,code,reason,found=True,head=False,count=False):
    c={0xc:0x10 if code==128 else 0x32,0x18:0x1c if reason<=44 else 0x7a,
       0x38:0x3c if code==129 else 0x7a,0x40:0x122 if reason==19 else 0x44,
       0x44:0x68 if reason>19 else 0x48,0x4a:0xde if reason==8 else 0x4e,
       0x50:0x100 if reason==12 else 0x54,0x56:0x5a if reason==5 else 0x7a,
       0x6c:0x158 if reason==48 else 0x70,0x70:0x84 if reason>48 else 0x74,
       0x76:0x144 if reason==26 else 0x7a,0x88:0x170 if reason==87 else 0x8c,
       0x62:0x96 if found else 0x64,0xe6:0xe8 if found else 0x64,
       0x108:0x10a if found else 0x64,0x12a:0x12c if found else 0x64,
       0x14a:0x14e if found else 0x64,0x160:0x164 if found else 0x64,
       0x9a:0x9c if head else 0xc4,0xb0:0xb2,0xb6:0xb8 if count else 0xc4,
       0x130:0x132 if count else 0x13e}
    return common.walk(b,c)


def certificates(b):
    pc=b['start'];n={v['pc']-pc:v for v in b['instructions']};cases={}
    for code,reason in ((128,0),(128,44),(128,45),(129,0),(129,5),(129,8),(129,12),(129,19),(129,26),(129,27),(129,48),(129,87),(129,255),(129,254),(127,0)):
        for found in (False,True):
            for head,count in ((False,False),(True,False),(True,True)):
                name=f'{code}:{reason}:found{int(found)}:head{int(head)}:count{int(count)}'
                seq=selected(b,code,reason,found,head,count)
                check(seq[-5:]==[0x7a,0x7c,0x7e,0x80,0x82],'task5 parser shared epilogue')
                defs=[o for o in seq if n[o].get('rd')==15]
                last=n[defs[-1]]
                if last['op']=='li':status=last['imm']
                else:
                    check(last['op']=='sltu' and defs[-1]==0x90,'task5 parser last status definition')
                    status=int(reason!=255)
                expected=0 if code==128 and reason<=44 else (0 if reason in (87,255) else (0 if found else 2) if reason in (5,8,12,19,26,48) else 1) if code==129 else 1
                check(status==expected,'task5 parser selected normal status')
                cases[name]=seq
    base=selected(b,129,5,True,True,True)
    at=base.index(0xa6);cycle=[0xa6,0xa8,0xac,0xae,0xb0,0xda,0xdc]
    loop=base[:at]+cycle+base[at:]
    common.previous.valid(b['CFG'],[pc+o for o in loop]);cases['129:5:one_extra_next_link']=loop
    e={(p-pc,q-pc) for p,qs in b['CFG'].items() for q in qs};covered={edge for seq in cases.values() for edge in zip(seq,seq[1:])}
    check(covered==e,'task5 parser selected witnesses cover all local edges')
    return {'selected_syntactic_walks':cases,'all_local_edges_witnessed':True,'all_paths_feasible_or_terminating_proved':False}


def domains():
    kinds=Counter()
    for code in range(256):
        for reason in range(256):
            name='type128_table' if code==128 and reason<=44 else 'lookup' if code==129 and reason in (5,8,12,19,26,48) else 'type129_no_lookup_success' if code==129 and reason in (87,255) else 'unsupported'
            kinds[name]+=1
    check(dict(kinds)=={'unsupported':65483,'type128_table':45,'lookup':6,'type129_no_lookup_success':2},'task5 parser complete code/reason domain')
    for old in range(65536):
        for length in (1,2,65535,65536,65537):
            value=(old+length)&65535
            check(((old+1+(length-1))&65535)==value,'task5 parser count formula')
            check((value!=0)==((old+length)%65536!=0),'task5 parser wrap affects V20 branch')
    check(((65535+1)&65535)==0 and ((0+65536)&65535)==0,'task5 parser V20 call skipped at wrapped0')
    for v in range(256):check(((v^128)<=1)==(v in (128,129)),'task5 handler exact type filter')
    return {'code_reason_pairs':65536,'branch_family_counts':dict(kinds),'counter_U16_cases':65536,'positive_length_vectors':[1,2,65535,65536,65537],
      'reason5_nonempty_formula':'(oldU16[O68]+finite list length) mod65536; final nonzero ->V20 call then clear68; wrapped0 skipsV20',
      'reason5_empty_list':'no local read/increment/store O68; proceeds to notify/reset regardless of old68; nested sideeffects still opaque',
      'real_message_reachability_or_list_length_proved':False}


def profile(image,data,hexraw,index,parent):
    pc=STARTS[index][0];b=body(init.binding.take(data,pc,376),index);n={v['pc']-pc:v for v in b['instructions']}
    t=table(init.binding.take(data,TABLES[index],180),index);vs=veneers(data,index)
    check(n[0x1c]['imm']+n[0x22]['imm']==TABLES[index] and n[0x20]['imm']==2 and n[0x2a]['imm']==2,'task5 parser bounded table address/key join')
    check(n[0xa0]['rd']==12 and n[0xa0]['rs1']==12 and n[0xa0]['imm']==1 and n[0xa8]['rd']==14 and n[0xa8]['rs1']==12 and n[0xa8]['imm']==1,'task5 list count initial/next increment')
    check(n[0xa2]['imm']==n[0xa4]['imm']==n[0xac]['imm']==n[0xae]['imm']==16 and n[0xda]['rd']==12 and n[0xda]['rs2']==14,'task5 list count low16 carry-back')
    empty=selected(b,129,5,True,False,False)
    check(not any(o in empty for o in (0x9c,0xb2,0xbc,0xc0)),'task5 empty list has no local68 access/V20 call')
    lpc=lookup.STARTS[index][2];lb=lookup.body(init.binding.take(data,lpc,24),'lookup',index)
    check([c['target'] for c in b['calls'] if c.get('target')==lpc]==[lpc]*6,'task5 parser six lookup calls')
    expected=[('table',0x2c),(lpc,0x5c),(vs[3]['start'],0xbc),(vs[0]['start'],0xce),(0x5774e+320*index,0xd4),
      (lpc,0xe0),(vs[1]['start'],0xf6),(lpc,0x102),(vs[2]['start'],0x11c),(lpc,0x124),(vs[3]['start'],0x136),
      (lpc,0x146),(vs[4]['start'],0x152),(lpc,0x15a),(vs[5]['start'],0x16a),(vs[6]['start'],0x172)]
    check([(c['target'] if isinstance(c['target'],int) else 'table',c['offset']) for c in b['calls']]==expected,'task5 parser complete direct target joins')
    hp=handler.STARTS[index];hb=handler.body(init.binding.take(data,hp,258),index);hn={v['pc']-hp:v for v in hb['instructions']}
    check(hn[44]['target']==pc and hn[48]['rd']==10 and hn[48]['rs2']==9 and hn[50]['target']==common.dealloc.DETAILS[index][0],'task5 handler parser then original M cleanup')
    # Strict original HEX provenance: no absent byte receives a fill value.
    _,memory=sparse.inspect(hexraw,sparse.parser());ranges=[(pc,376),(TABLES[index],180)]+[(v['start'],v['bytes']) for v in vs]
    receipts=[]
    for a,z in ranges:
        check(sparse.captured(memory,a,z)==init.binding.take(data,a,z),'task5 captured HEX/candidate range equality')
        receipts.append({'start':a,'bytes':z,'all_bytes_captured_in_original_HEX':True})
    message_offsets=[(v['imm'],v['width']) for o,v in n.items() if v['op']=='load' and v['rs1']==10 and (o in (6,0x10,0x2a,0x3c,0x5a,0xde,0x100,0x122,0x144,0x158,0x170))]
    check(all(o>=0 and o+z<=4 for o,z in message_offsets),'task5 all original message field reads within4 bytes')
    return {'label':init.binding.PROFILES[index][0],'body':b,'table':t,'veneers':vs,'HEX_capture_receipts':receipts,
      'CFG_certificates':certificates(b),'reused_lookup':{k:lb[k] for k in ('start','bytes','sha256')},
      'reused_registered_handler':{k:hb[k] for k in ('start','bytes','sha256')},
      'conditional_task_binding':parent['conditional_distinct_routing'],
      'lookup_contract':'first list object with freshU16[O8]==full requestedID,head20003454/34a4,nextO0; zero if finite no-match; duplicates/order/extent/termination and actual objects remain conditional',
      'message_scope':'all message reads are M0:type,M1:reason,U16[M2]:ID; minimum4B valid readable message, no local null/length check; other loads follow lookup objects/list nodes',
      'status_contract':'normal return0:handled calls or reason255;1:unsupported type/reason;2:lookup0 for reasons5/8/12/19/26/48; nested scalar replies otherwise ignored, not delivery or physical success',
      'reason5':'lookup O; if freshO280!=0, count oldO68+finite list length mod65536,SH count; nonzero count ->veneer(1,freshO8,count),thenSH0 toO68. EmptyO280 skips68 work. Then veneer(freshO43,freshO8,freshO84),reset5774e/5788e(O),return0',
      'reason8':'lookup O; veneer(freshO43,freshO8,bool(freshO76)); then SB0 toO43;return0',
      'reason12':'lookup O; veneer(freshO43,freshO8,freshU8O79,freshU16O80,freshU16O82);thenSB0 toO43;return0',
      'reason19':'lookup O; freshO68 nonzero ->veneer(1,freshO8,freshO68),thenSH0 toO68;alwaysSB0 toO49;return0',
      'reason26':'lookup O;veneer(freshO43),no local object clear;return0',
      'reason48':'lookup O;veneer(freshO43,freshO8),thenSB0 toO43;return0',
      'reason87_255':'87 passesU16[M2] to two-byte RET veneer,thenforces0;255 returns0 without lookup/veneer or ID read',
      'type128':'reason<=44 ->fresh table[reason] call withA0=U16[M2],no null target guard;thenforces0 regardless scalar;larger reason1. Individual45 callees remain opaque',
      'lifetime_join':'registered handler saves M inS1,calls parser only type128/129,then attempts publicfree(originalM) for every nonnulltype; parser return scalar ignored. Calls must return/preserve required S1/SP/RA/frame; no global actual callback delivery/lifetime proof',
      'threshold_join':'if prior accepted same-task messages survive queue/receive/handler and fields stay stable, (128,0)->table0, (129,19)->reason19, (129,5)->reason5. Key-only lookup does not prove returnedO is original threshold object; require first-match identity/uniqueness and retention',
      'preservation_premises':'matching captured candidates/conditional ISA and runtime table; valid aligned frame/message4B/object>=284B/list-node words; normal nested calls and needed S0/S1/SP/RA/frame preservation; adversealias/IRQ/DMA/reentry/writers excluded; fresh object fields not equated without evidence',
      'target_execution_or_emulation':False,'actual_installed_binding_or_complete_payload_lifetime_proved':False}


def derive(image,carriers,header,coverage,hexes):
    parent=previous.derive(image,carriers,header,coverage)
    profiles=[profile(image,d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
    check(sum(p['body']['bytes'] for p in profiles)==752 and sum(len(p['body']['instructions']) for p in profiles)==260,'task5 full parser census')
    check(sum(v['bytes'] for p in profiles for v in p['veneers'])==52 and sum(p['table']['bytes'] for p in profiles)==360,'task5 table/veneer census')
    return {'schema':'TSL9-task5-parser-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'complete_parser_bytes':752,'complete_parser_instructions':260,'additional_veneer_bytes':52,'additional_veneer_instructions':14,'dispatch_table_bytes':360,
      'C_reconstruction_coverage_changed':False,'remaining':['type128 table0 andother45 target bodies','reason-specific veneer target/reset effects andfield writers','actual installed task5 dispatch/key identity and payload retention'],
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
    mutations=unsigned=words=veneer_mutations=0
    for i,data in enumerate(carriers):
        pc=STARTS[i][0];raw=init.binding.take(data,pc,376)
        for p,v in decode(raw,pc).items():
            off=p-pc;z=v['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
            try:body(bad,i)
            except RuntimeError:pass
            else:raise RuntimeError('task5 parser mutation escaped')
            mutations+=1
        for off,width in UNSIGNED:
            bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
            try:body(bad,i)
            except RuntimeError as ex:check('unsigned encoding' in str(ex),'task5 specific unsigned guard')
            else:raise RuntimeError('task5 signedness escaped')
            unsigned+=1
        tab=init.binding.take(data,TABLES[i],180)
        for off in range(0,180,4):
            bad=bytearray(tab);bad[off]^=1
            try:table(bad,i)
            except RuntimeError as ex:check('word operands' in str(ex),'task5 exact table word guard')
            else:raise RuntimeError('task5 table mutation escaped')
            words+=1
        for k,off in enumerate(VENEER_OFFSETS):
            size=2 if off==32 else 4;raw=init.binding.take(data,0x6a700+484*i+off,size)
            bad=(int.from_bytes(raw,'little')^(4 if size==2 else 1<<20)).to_bytes(size,'little')
            try:veneer(bad,i,k)
            except RuntimeError:pass
            else:raise RuntimeError('task5 veneer mutation escaped')
            veneer_mutations+=1
    check((mutations,unsigned,words,veneer_mutations)==(260,24,90,14),'task5 mutation census');domains()
    print('PASS:260 parser+14 veneer instructions,24 signedness and90 table-word mutations rejected;65536 type/reason and U16 counter domains')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
    ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    raw=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if args.write:
        with OUT.open('xb') as f:f.write(raw)
    else:check(OUT.read_bytes()==raw,'task5 parser exact ledger replay')
    print('PASS:752B/260i complete parsers +52B/14i veneers +360B tables;all local edges witnessed;strict original HEX backing;exact ledger')
    print('PASS:NO target execution/emulation;actual task/provider binding,callee effects and full lifetime UNPROVED')


if __name__=='__main__':main()
