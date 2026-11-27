"""Offline table0 requeue, object cleanup and node/payload lifetime contracts.

Original operands/CFG, immutable syntactic walks and scalar/interval algebra.
No target ISA, mutable object/heap/queue machine, callback or MMIO executes.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_task5_parser_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
OUT=Path(__file__).with_name('v4160-task5-object-static.json')
PARTS=('table0','cleanup','adapter')
STARTS=((0x5e40e,0x5774e,0x6a722),(0x5e556,0x5788e,0x6a906))
SOURCES=STARTS
SIZES=(162,252,4)
COUNTS=(60,78,1)
FIELDS={**previous.FIELDS,'ori':('rd','rs1','imm')}
BRANCHES=previous.BRANCHES
UNSIGNED={'table0':((0x84,2),),'cleanup':((0x22,1),(0x32,1),(0x42,1),(0x52,1),(0x74,2)),'adapter':()}
HASHES=(('77fb3acc5f6a0ecb6a81581e84898f36e58935d4fb3fb3d21c4aa09e10fe7598', '7cecc8f6c13eef9d412f0bd206097240164d84f2590e3c0a53d4214674e67d01', 'a42a0c80fe5978708bf75d01e41023f27bead8c8fcf3715e68bf9b44d504ee99'), ('e5ba29c15a0004fbc5d9994d81f70c21c4221fb74beabadad7b5230c98364776', '4763017b69417a4f2462b319ef9ecc47b7ea9c70d15a38c7698c22f83ef27586', '26d1665b1247749311f2de0cc230e92f55484e781d49772a3b2e360322157e3b'))
LITERALS=(
{
'table0':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 store 2 18 0 4
006 store 2 1 12 4
008 store 2 8 8 4
00a lui 9 1073889280
00e load 18 9 524 4
012 store 9 0 524 4
016 fence.i
01a jal 1 358474
01e bnez 10 50
020 store 9 18 524 4
024 li 10 2
026 load 1 2 12 4
028 load 8 2 8 4
02a load 9 2 4 4
02c load 18 2 0 4
02e addi 2 2 16
030 jr 1
032 load 15 10 288 4
036 store 10 0 26 1
03a mv 8 10
03c beqz 15 150
03e load 14 10 15 1
040 andi 14 14 1
042 bnez 14 94
044 load 10 8 8 2
046 li 12 0
048 addi 11 0 128
04c jal 1 385960
050 beqz 10 156
052 lui 15 1073889280
056 store 15 18 524 4
05a li 10 0
05c jump 38
05e load 13 15 4 4
060 load 12 15 12 1
062 load 11 15 8 1
064 load 10 10 8 2
066 addi 13 13 2
068 jal 1 436002
06c bnez 10 144
06e load 15 8 288 4
072 load 14 15 10 2
074 store 15 0 9 1
078 ori 14 14 -256
07c store 15 14 10 2
07e load 15 15 0 4
080 store 8 15 288 4
084 load 15 8 66 2
088 beqz 15 144
08a addi 15 15 -1
08c store 8 15 66 2
090 load 15 8 288 4
094 bnez 15 68
096 store 8 0 66 2
09a jump 82
09c li 15 1
09e store 8 15 26 1
0a0 jump 82
''',
'cleanup':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 store 2 1 12 4
006 mv 8 10
008 load 15 8 280 4
00c bnez 15 188
00e load 15 8 288 4
012 bnez 15 220
014 load 10 8 272 4
018 beqz 10 34
01a auipc 1 536514560
01e jalr 1 1 -1624
022 load 10 8 39 1
026 addi 15 0 255
02a beq 10 15 50
02e jal 1 277012
032 load 10 8 38 1
036 addi 15 0 255
03a beq 10 15 66
03e jal 1 277012
042 load 10 8 40 1
046 addi 15 0 255
04a beq 10 15 82
04e jal 1 277012
052 load 10 8 41 1
056 addi 15 0 255
05a beq 10 15 104
05e jal 1 277012
062 li 15 -1
064 store 8 15 41 1
068 load 10 8 8 2
06a jal 1 358986
06c lui 15 536883200
070 addi 15 15 952
074 load 14 15 180 2
078 bnez 14 180
07a lui 14 536883200
07e store 14 0 1260 4
082 lui 14 536883200
086 load 14 14 568 4
08a store 15 14 176 4
08e lui 15 536883200
092 load 15 15 500 4
096 beqz 15 180
098 lui 8 536883200
09c addi 8 8 412
0a0 load 10 8 32 4
0a2 beqz 10 180
0a4 auipc 1 536514560
0a8 jalr 1 1 -1762
0ac store 8 0 32 4
0b0 store 8 0 36 4
0b4 load 1 2 12 4
0b6 load 8 2 8 4
0b8 addi 2 2 16
0ba jr 1
0bc load 10 15 4 4
0be beqz 10 200
0c0 auipc 1 536514560
0c4 jalr 1 1 -1790
0c8 load 15 8 280 4
0cc load 14 15 10 2
0ce ori 14 14 -256
0d2 store 15 14 10 2
0d4 load 15 15 0 4
0d6 store 8 15 280 4
0da jump 8
0dc load 10 15 4 4
0de beqz 10 232
0e0 auipc 1 536514560
0e4 jalr 1 1 -1822
0e8 load 15 8 288 4
0ec load 14 15 10 2
0ee ori 14 14 -256
0f2 store 15 14 10 2
0f4 load 15 15 0 4
0f6 store 8 15 288 4
0fa jump 14
''',
'adapter':'''
000 jal 0 340222
'''
},
{
'table0':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 store 2 18 0 4
006 store 2 1 12 4
008 store 2 8 8 4
00a lui 9 1073889280
00e load 18 9 524 4
012 store 9 0 524 4
016 fence.i
01a jal 1 358794
01e bnez 10 50
020 store 9 18 524 4
024 li 10 2
026 load 1 2 12 4
028 load 8 2 8 4
02a load 9 2 4 4
02c load 18 2 0 4
02e addi 2 2 16
030 jr 1
032 load 15 10 288 4
036 store 10 0 26 1
03a mv 8 10
03c beqz 15 150
03e load 14 10 15 1
040 andi 14 14 1
042 bnez 14 94
044 load 10 8 8 2
046 li 12 0
048 addi 11 0 128
04c jal 1 386288
050 beqz 10 156
052 lui 15 1073889280
056 store 15 18 524 4
05a li 10 0
05c jump 38
05e load 13 15 4 4
060 load 12 15 12 1
062 load 11 15 8 1
064 load 10 10 8 2
066 addi 13 13 2
068 jal 1 436486
06c bnez 10 144
06e load 15 8 288 4
072 load 14 15 10 2
074 store 15 0 9 1
078 ori 14 14 -256
07c store 15 14 10 2
07e load 15 15 0 4
080 store 8 15 288 4
084 load 15 8 66 2
088 beqz 15 144
08a addi 15 15 -1
08c store 8 15 66 2
090 load 15 8 288 4
094 bnez 15 68
096 store 8 0 66 2
09a jump 82
09c li 15 1
09e store 8 15 26 1
0a0 jump 82
''',
'cleanup':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 store 2 1 12 4
006 mv 8 10
008 load 15 8 280 4
00c bnez 15 188
00e load 15 8 288 4
012 bnez 15 220
014 load 10 8 272 4
018 beqz 10 34
01a auipc 1 536514560
01e jalr 1 1 -1944
022 load 10 8 39 1
026 addi 15 0 255
02a beq 10 15 50
02e jal 1 277152
032 load 10 8 38 1
036 addi 15 0 255
03a beq 10 15 66
03e jal 1 277152
042 load 10 8 40 1
046 addi 15 0 255
04a beq 10 15 82
04e jal 1 277152
052 load 10 8 41 1
056 addi 15 0 255
05a beq 10 15 104
05e jal 1 277152
062 li 15 -1
064 store 8 15 41 1
068 load 10 8 8 2
06a jal 1 359306
06c lui 15 536883200
070 addi 15 15 1032
074 load 14 15 180 2
078 bnez 14 180
07a lui 14 536883200
07e store 14 0 1340 4
082 lui 14 536883200
086 load 14 14 648 4
08a store 15 14 176 4
08e lui 15 536883200
092 load 15 15 580 4
096 beqz 15 180
098 lui 8 536883200
09c addi 8 8 492
0a0 load 10 8 32 4
0a2 beqz 10 180
0a4 auipc 1 536510464
0a8 jalr 1 1 2014
0ac store 8 0 32 4
0b0 store 8 0 36 4
0b4 load 1 2 12 4
0b6 load 8 2 8 4
0b8 addi 2 2 16
0ba jr 1
0bc load 10 15 4 4
0be beqz 10 200
0c0 auipc 1 536510464
0c4 jalr 1 1 1986
0c8 load 15 8 280 4
0cc load 14 15 10 2
0ce ori 14 14 -256
0d2 store 15 14 10 2
0d4 load 15 15 0 4
0d6 store 8 15 280 4
0da jump 8
0dc load 10 15 4 4
0de beqz 10 232
0e0 auipc 1 536510464
0e4 jalr 1 1 1954
0e8 load 15 8 288 4
0ec load 14 15 10 2
0ee ori 14 14 -256
0f2 store 15 14 10 2
0f4 load 15 15 0 4
0f6 store 8 15 288 4
0fa jump 14
''',
'adapter':'''
000 jal 0 340390
'''
}
)


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'task5 object literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=pc
        out[pc+int(off,16)]=f
    return out


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    if part=='table0':check(raw[0x16:0x1a]==bytes.fromhex('0f100000'),'task5 object fence bytes')
    for off,width in UNSIGNED[part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f=={1:0x4003,2:0x5003}[width],'task5 object unsigned encoding')
    n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'task5 object complete boundaries '+part)
    for p,f in s.items():init.g(n,p,'task5 object operand '+part+' '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'task5 object original identity '+part)
    e={};calls=[];tails=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'task5 object ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':
            if v['rd']==0:tails.append({'offset':p-pc,'target':v['target'],'new_link':False});qs=[]
            else:check(v['rd']==1,'task5 object linked call');calls.append({'offset':p-pc,'target':v['target']})
        elif op=='jalr':
            check(v['rd']==v['rs1']==1 and n[p-4]['op']=='auipc' and n[p-4]['rd']==1,'task5 object pair call')
            calls.append({'offset':p-pc,'target':(p-4+n[p-4]['imm']+v['imm'])&0xfffffffe})
        check(all(q in n for q in qs),'task5 object closed CFG');e[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(e[p])
    check(seen==set(n),'task5 object all nodes reachable')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(calls),len(stores),len(rets),len(tails))==((3,14,1,0),(9,11,1,0),(0,0,0,1))[k],'task5 object census '+part)
    check(common.acyclic(e)==(part!='cleanup'),'task5 object cycle classification')
    if part=='cleanup':
        cut={p:list(qs) for p,qs in e.items()}
        for a,z in ((0xda,8),(0xfa,14)):cut[pc+a].remove(pc+z)
        check(common.acyclic(cut),'task5 object cleanup exactly two loop cuts')
        check([p-pc for p,v in n.items() if v.get('rd')==8]==[6,0x98,0x9c,0xb6],'task5 object S0 switches from object to fixed context')
    return {'start':pc,'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'CFG':e,'calls':calls,'tails':tails,
      'returns':rets,'stores':stores,'complete_local_body':True,'local_CFG_acyclic':common.acyclic(e),'actual_progress_proved':False}


def table0_paths(b):
    pc=b['start'];n={v['pc']-pc:v for v in b['instructions']};seqs=[]
    def visit(p,seq):
        check(p not in seq,'task5 table0 path DAG')
        seq=seq+[p]
        if not b['CFG'][p]:seqs.append([x-pc for x in seq]);return
        for q in b['CFG'][p]:visit(q,seq)
    visit(pc,[])
    check(len(seqs)==13,'task5 table0 complete syntactic path count')
    for seq in seqs:
        check(seq[-6:]==[0x26,0x28,0x2a,0x2c,0x2e,0x30],'task5 table0 complete restore/RET')
        a0defs=[o for o in seq if n[o].get('rd')==10]
        last=n[a0defs[-1]];check(last['op']=='li' and last['imm']==(2 if 0x24 in seq else 0),'task5 table0 normal reply')
        check(seq.count(0x4c)<=1 and seq.count(0x68)<=1,'task5 table0 at most one requeue and adapter call')
        check((0x9e in seq)==(0x50 in seq and 0x9c in seq),'task5 table0 flag1 iff builder zero branch')
        check(int(0x20 in seq)+int(0x56 in seq)==1,'task5 table0 captured control restored on each normal path')
        if 0x80 in seq:check(0x6e in seq and 0x74 in seq and 0x7c in seq,'task5 table0 pop only after fresh-head mutation')
    return {'all_syntactic_paths':seqs,'count':len(seqs),'all_paths_feasible_or_callchain_terminating_proved':False}


def cleanup_paths(b):
    pc=b['start'];out={};prefix=[0,2,4,6];finish=[0xb4,0xb6,0xb8,0xba]
    # Immutable concatenations of original CFG pieces, not mutable list/heap states.
    for n280 in range(3):
        for n288 in range(3):
            for free_payload in (False,True):
                for owner in (False,True):
                    for ids in range(16):
                        for global_case in ('count_nonzero','gate0','ctx32zero','ctx32nonnull'):
                            seq=prefix[:]
                            for _ in range(n280):seq.extend([8,0xc,0xbc,0xbe]+([0xc0,0xc4] if free_payload else [])+[0xc8,0xcc,0xce,0xd2,0xd4,0xd6,0xda])
                            seq.extend((8,0xc))
                            for _ in range(n288):seq.extend([0xe,0x12,0xdc,0xde]+([0xe0,0xe4] if free_payload else [])+[0xe8,0xec,0xee,0xf2,0xf4,0xf6,0xfa])
                            seq.extend((0xe,0x12,0x14,0x18))
                            if owner:seq.extend((0x1a,0x1e))
                            for j,(load,limit,branch,call) in enumerate(((0x22,0x26,0x2a,0x2e),(0x32,0x36,0x3a,0x3e),(0x42,0x46,0x4a,0x4e),(0x52,0x56,0x5a,0x5e))):
                                seq.extend((load,limit,branch))
                                if ids>>j&1:
                                    seq.append(call)
                                    if j==3:seq.extend((0x62,0x64))
                            seq.extend((0x68,0x6a,0x6c,0x70,0x74,0x78))
                            if global_case!='count_nonzero':
                                seq.extend((0x7a,0x7e,0x82,0x86,0x8a,0x8e,0x92,0x96))
                                if global_case!='gate0':
                                    seq.extend((0x98,0x9c,0xa0,0xa2))
                                    if global_case=='ctx32nonnull':seq.extend((0xa4,0xa8,0xac,0xb0))
                            seq.extend(finish);common.previous.valid(b['CFG'],[pc+o for o in seq])
                            key=f'{n280}:{n288}:payload{int(free_payload)}:owner{int(owner)}:ids{ids}:{global_case}'
                            out[key]=seq
    check(len(out)==2304,'task5 cleanup finite witness census')
    all_edges={(p-pc,q-pc) for p,qs in b['CFG'].items() for q in qs}
    covered={edge for seq in out.values() for edge in zip(seq,seq[1:])};check(covered==all_edges,'task5 cleanup every local edge witnessed')
    examples={key:out[key] for key in ('0:0:payload0:owner0:ids0:count_nonzero','1:1:payload1:owner1:ids15:ctx32nonnull','2:2:payload1:owner0:ids0:gate0','0:0:payload0:owner0:ids0:ctx32zero')}
    return {'immutable_CFG_walk_count':len(out),'each_list_length_vectors':[0,1,2],'all_local_edges_witnessed':True,
      'walks_sha256':sha256(json.dumps(out,separators=(',',':')).encode()).hexdigest(),'examples':examples,
      'real_list_finiteness_or_heap_release_success_proved':False}


def domains():
    for half in range(65536):
        marked=(half|0xffffff00)&65535
        check(marked==(half&255)|0xff00 and marked&255==half&255 and marked>>8==255,'task5 object node marker low-byte preservation')
        if half:check(0<=half-1<=65534,'task5 object nonzero count decrement')
    for flag in range(256):check(bool(flag&1)==(flag%2==1),'task5 object O15 bit0 predicate')
    return {'node_U16_marker_cases':65536,'O66_count_domain_cases':65536,'O15_byte_cases':256,
      'marker_store':'U16[P10] ->low8 unchanged,byteP11=255; distinct from message marker M-2',
      'count':'nonzero freshU16[O66] decremented only on local pop;freshhead0 later forcesO66=0',
      'actual_record_ownership_or_execution_proved':False}


def profile(image,data,hexraw,index,parent):
    bs={part:body(init.binding.take(data,STARTS[index][k],SIZES[k]),part,index) for k,part in enumerate(PARTS)}
    table0,cleanup,adapter=(bs[p] for p in PARTS);tp,cp,ap=STARTS[index];B=0x200033b8+80*index;C=0x2000319c+80*index
    tn={v['pc']-tp:v for v in table0['instructions']};cn={v['pc']-cp:v for v in cleanup['instructions']}
    check(parent['table']['entries'][0]['effective_target']==tp,'task5 table0 selected parser table join')
    lp=previous.lookup.STARTS[index][2];builder=0x5e3a8+328*index
    check(table0['calls']==[{'offset':0x1a,'target':lp},{'offset':0x4c,'target':builder},{'offset':0x68,'target':ap}],'task5 table0 complete callee joins')
    check(adapter['tails']==[{'offset':0,'target':0x530fe+168*index,'new_link':False}],'task5 V34 target')
    expected=[(0x1e,0x20000110),(0x2e,0x43a14+140*index),(0x3e,0x43a14+140*index),(0x4e,0x43a14+140*index),
      (0x5e,0x43a14+140*index),(0x6a,0x57a4a+320*index),(0xa8,0x20000110),(0xc4,0x20000110),(0xe4,0x20000110)]
    check([(v['offset'],v['target']) for v in cleanup['calls']]==expected,'task5 cleanup complete direct targets')
    check(tn[0x3e]['imm']==15 and tn[0x40]['imm']==1,'task5 table0 predicate O15 bit0')
    check(tn[0x60]['imm']==12 and tn[0x60]['width']==1 and tn[0x62]['imm']==8 and tn[0x62]['width']==1 and tn[0x66]['imm']==2,'task5 V34 byte fields/payload adjustment')
    check(tn[0x6e]['imm']==288 and tn[0x72]['rs1']==15 and not any(tn[o]['op'] in BRANCHES for o in (0x6e,0x72)),'task5 fresh post-adapter head lacks null guard')
    check(tn[0x74]['imm']==9 and tn[0x7c]['imm']==10 and tn[0x80]['imm']==288,'task5 table0 local pop fields')
    check(cn[0x6c]['imm']+cn[0x70]['imm']==B and cn[0x82]['imm']+cn[0x86]['imm']==C+156,'task5 cleanup global B/source roles')
    check(cn[0x7a]['imm']+cn[0x7e]['imm']==B+308 and cn[0x8e]['imm']+cn[0x92]['imm']==C+88,'task5 cleanup global zero/gate roles')
    check(cn[0x98]['imm']+cn[0x9c]['imm']==C and cn[0xa0]['imm']==cn[0xac]['imm']==32 and cn[0xb0]['imm']==36,'task5 cleanup fixed context pointer cleanup')
    check(not any(v['op'] in ('load','store') and v.get('rs1')==8 for o,v in cn.items() if 0x6a<o<0x98),'task5 no later original O dereference after57a4a call')
    # Revalidate exact private release; public SDK marker checks are not in this call chain.
    life=common.previous;fr=life.release;free_n,free_e=life.free_body(init.binding.take(data,fr.DETAILS[index][0],212),index)
    check(not any(v.get('rd') in (8,9,18) for v in free_n.values()),'task5 private free locally preserves object/context S registers')
    parser_n={v['pc']-parent['body']['start']:v for v in parent['body']['instructions']}
    check(parser_n[0xd4]['target']==cp and parser_n[0xd8]['target']==parent['body']['start']+0x2e,'task5 reason5 cleanup then forced parser0')
    after=[0xd8,0x2e,0x30,0x7a,0x7c,0x7e,0x80,0x82]
    check(not any(parser_n[o]['op'] in ('load','store') and parser_n[o].get('rs1')==8 for o in after),'task5 parser no O dereference aftercleanup')
    _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
    for part,b in bs.items():
        check(sparse.captured(mem,b['start'],b['bytes'])==init.binding.take(data,b['start'],b['bytes']),'task5 object strict HEX backing')
        receipts.append({'part':part,'start':b['start'],'bytes':b['bytes'],'all_bytes_captured':True})
    return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,
      'CFG_certificates':{p:common.certificates(b) for p,b in bs.items()},'table0_paths':table0_paths(table0),'cleanup_paths':cleanup_paths(cleanup),
      'reused_private_release':{'entry':fr.ENTRY,'source':fr.DETAILS[index][0],'bytes':212,'sha256':fr.DETAILS[index][-1]},
      'table0_contract':['lookup0 ->normalreturn2;lookupO ->sampleO288,then clearO26 andsaveO;all subsequent normal returns0 even builder/adapter failure',
        'initial sampledO288=0 ->SH0 O66;else freshO15 bit0=0 ->builder(freshU16 O8,128,0)',
        'bit0=1 ->V34(freshU16 O8,freshU8 P8,freshU8 P12,(freshU32 P4+2)mod32),P is initially sampled O288',
        'V34 reply0 ->fresh reloadP=O288,dereference without nullguard;sampleU16 P10 beforeSB0 P9,then OR/SH marksP11FF;advanceO288=P0;nonzeroO66 decrement',
        'then freshO288 nonzero ->builder once;zero ->SH0 O66;builderreply0 ->SB1 O26;buildernonzero ->no local flag1 store;no local recursion/loop',
        'controlword saved/cleared,FENCE.I,restored on every encoded normal return;physical critical-section meaning remains unproved'],
      'message_recurrence':'under retained task/ID/table bindings,successful distinct message allocation/append and later dispatch,table0 may enqueue another(128,0) before current handler frees M. That is a conditional cross-message recurrence,not a local infinite loop or progress proof;flag1 is not eventdelivery',
      'cleanup_contract':['drain O280 then O288;for each sampled node P,attempt privatefree(P4) ifnonnull;reload fresh head aftercall,mark freshP11FF,advance via freshP0;no direct node-P free',
        'afterboth heads0,nonnullO272 ->privatefree(pointer);no local O272 clear;fresh O39/O38/O40/O41 !=255 ->helper43a14/43aa0(ID);only O41 is locally written255 afteritscall',
        'call57a4a/57b8a(freshU16 O8);body/ownership effects unresolved;subsequent local code no longer dereferences originalO',
        'freshU16[B180]!=0 ->epilogue;else zeroB308,copyfreshC156toB176;freshwordC88==0 ->epilogue;nonzero is gate,not callback invocation',
        'gate!=0 ->S0=C;freshC32nonnull ->privatefree(C32),thenSW0 C32/C36;zeroC32 skipsfree/stores;C88notlocallycleared',
        'no fixed success return;A0then-live from lastcall or explicit C32load. Parser reason5 discards this value and forcesitsown0'],
      'separate_lifetimes':'object-node P11 is not message M-2;privatefree attempts are not public marker-checked free. P4/O272/C32 allocation provenance and containing-header/range/tag/account state must be established separately. Mark/pop is not freeingP;body norobject wipe/ownership conclusion follows',
      'fresh_head_premise':'post-adapter0/post-privatefree heads are reloaded before dereference;stability/nonnull/validity must hold acrosscalls. Correct original-node pop and finite-list ranking need same-head/next preservation;opaque callees could alterthem',
      'premises':'matching captured conditional ISA;valid aligned object>=292B,table0 node>=13B/cleanup node>=12B,frames,control/globals/privateheap;normal calls preserve needed S0/S1/S2/SP/RA/frame andfieldnonalias;no IRQ/DMA/reentry/unaccounted writers;payload pointer+2 validity belongs to opaque V34 target',
      'actual_provider_dispatch_progress_and_complete_lifetime_proved':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage,hexes):
    parent=previous.derive(image,carriers,header,coverage,hexes)
    profiles=[profile(image,d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==836,'task5 object byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==278,'task5 object instruction census')
    return {'schema':'TSL9-task5-object-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'complete_body_bytes':836,'complete_body_instructions':278,'C_reconstruction_coverage_changed':False,
      'remaining':['V34 target530fe/531a6 and helper43a14/57a4a effects','actual allocation sources for P4/O272/C32 and object/list writers','runtime task/provider binding,queue recurrence and physical progress'],
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
    mutations=unsigned=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,STARTS[i][k],SIZES[k]);n=decode(raw,STARTS[i][k])
            for p,v in n.items():
                off=p-STARTS[i][k];z=v['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(bad,part,i)
                except RuntimeError:pass
                else:raise RuntimeError('task5 object instruction mutation escaped')
                mutations+=1
            for off,width in UNSIGNED[part]:
                bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
                try:body(bad,part,i)
                except RuntimeError as ex:check('unsigned encoding' in str(ex),'task5 object specific signedness guard')
                else:raise RuntimeError('task5 object unsigned mutation escaped')
                unsigned+=1
    check((mutations,unsigned)==(278,12),'task5 object mutation census');domains()
    print('PASS:278 instruction and12 signedness mutations rejected;65536 marker/count +256 flag cases;26 table0 paths/4608 cleanup witnesses')


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
    else:check(OUT.read_bytes()==raw,'task5 object exact ledger replay')
    print('PASS:836B/278i complete table0/cleanup/adapter;strict HEX backing;message-vs-node/payload lifetime joins;exact ledger')
    print('PASS:NO target execution/emulation;actual providers,release provenance and progress UNPROVED')


if __name__=='__main__':main()
