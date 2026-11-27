"""Offline threshold -> four-byte message -> queue publication certificates.

Pinned original operands, CFGs and immutable scalar/interval equations only.
No target ISA, mutable register/RAM/heap/list model, callback or MMIO execution.
"""
import argparse,json
from collections import deque,Counter
from hashlib import sha256
from pathlib import Path
import check_v4160_record_node_lifecycle_static as previous
import check_v4160_generator_static as operands
import check_v4160_message_marker_static as message
import check_v4160_cancel_provider_static as dealloc
import check_v4160_ram_callback_exits_static as exits
import check_v4160_ram_callback_prefix_static as prefix

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-threshold-message-static.json')
PARTS=('threshold','builder','sender','append')
STARTS=((0x568f6,0x5e3a8,0x43208,0x2000021c),(0x56a36,0x5e4f0,0x43294,0x2000021c))
SOURCES=((0x568f6,0x5e3a8,0x43208,0x4048c),(0x56a36,0x5e4f0,0x43294,0x404cc))
SIZES=(124,102,146,26)
COUNTS=(42,39,50,10)
FIELDS=operands.FIELDS
BRANCHES=operands.BRANCHES
HASHES=(('6bd9e582ecc17962ea0a1339777024639447653b11cad0396144e665c45a4cf4', '9b3ba752484ec0ef908448e2a5dcbc6ff46c9f8e404bc550bfe9e6ad67d11771', '3dc33c9ac54b0e89b7875c45a22610e31d7d2e53429cb3c1fea306cfb2038166', '2c2441db8c74ab2d96f18c9f6f4198cd9657a18cf85d9a02fa4232cb321fe2e8'), ('0f3fd0f2bdd3de9913f672a229116317b7c141c2799fdde992c45d88d4df9ff0', '0e27449a0b30db78463e2f70a97b2a3f1c50494a6b0c9d66a4e24b4198e786be', '8c93604b40d30365a3732f40e90ecbcbd8d868f0c6f27fa92bd3ecd9b5813757', '2c2441db8c74ab2d96f18c9f6f4198cd9657a18cf85d9a02fa4232cb321fe2e8'))
LITERALS=(
{
'threshold':'''
000 lui 15 536883200
004 addi 15 15 952
008 load 14 15 168 4
00c addi 2 2 -16
00e store 2 8 8 4
010 store 2 9 4 4
012 store 2 1 12 4
014 mv 8 10
016 mv 9 11
018 bne 14 10 32
01c store 15 0 168 4
020 load 15 8 288 4
024 beqz 15 50
026 load 10 8 8 2
028 li 12 0
02a addi 11 0 128
02e jal 1 385960
032 load 15 8 68 2
036 beqz 15 68
038 load 10 8 8 2
03a li 12 19
03c addi 11 0 129
040 jal 1 385960
044 load 10 8 8 2
046 li 12 5
048 addi 11 0 129
04c jal 1 385960
050 lui 15 536883200
054 addi 15 15 1300
058 load 14 15 7 1
05a store 8 0 10 1
05e store 8 0 16 1
062 store 8 9 84 1
066 li 13 5
068 bne 13 14 112
06c store 15 0 7 1
070 load 1 2 12 4
072 load 8 2 8 4
074 load 9 2 4 4
076 li 10 0
078 addi 2 2 16
07a jr 1
''',
'builder':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 9 20 4
006 store 2 18 16 4
008 store 2 1 28 4
00a lui 8 1073889280
00e store 2 11 12 4
010 store 2 12 8 4
012 load 9 8 524 4
016 mv 18 10
018 store 8 0 524 4
01c fence.i
020 li 10 4
022 auipc 1 536485888
026 jalr 1 1 -404
02a beqz 10 84
02c load 11 2 12 4
02e load 12 2 8 4
030 store 10 18 2 2
034 store 10 11 0 1
036 store 10 12 1 1
038 store 8 9 524 4
03c lui 15 536883200
040 load 8 2 24 4
042 load 1 2 28 4
044 load 9 2 20 4
046 load 18 2 16 4
048 mv 11 10
04a load 10 15 415 1
04e addi 2 2 32
050 jal 0 274952
054 store 8 9 524 4
058 load 1 2 28 4
05a load 8 2 24 4
05c load 9 2 20 4
05e load 18 2 16 4
060 li 10 4
062 addi 2 2 32
064 jr 1
''',
'sender':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 store 2 18 0 4
006 lui 9 1073889280
00a store 2 1 12 4
00c store 2 8 8 4
00e load 18 9 524 4
012 store 9 0 524 4
016 fence.i
01a bnez 11 36
01c store 9 18 524 4
020 li 10 5
022 jump 70
024 lui 15 536883200
028 load 15 15 413 1
02c mv 8 10
02e mv 10 11
030 bgeu 8 15 58
034 li 15 2
036 bltu 15 8 82
03a jal 1 274874
03c lui 15 1073889280
040 store 15 18 524 4
044 li 10 3
046 load 1 2 12 4
048 load 8 2 8 4
04a load 9 2 4 4
04c load 18 2 0 4
04e addi 2 2 16
050 jr 1
052 load 15 11 -8 4
056 bnez 15 100
058 load 14 11 -2 1
05c addi 15 0 255
060 beq 14 15 112
064 jal 1 274874
066 lui 15 1073889280
06a store 15 18 524 4
06e jump 32
070 lui 10 536883200
074 store 11 8 -2 1
078 addi 10 10 408
07c auipc 1 536596480
080 jalr 1 1 -104
084 lui 11 32768
086 mv 10 8
088 jal 1 275786
08a li 10 0
08c store 9 18 524 4
090 jump 70
''',
'append':'''
000 store 11 0 -8 4
004 load 15 10 0 4
006 bnez 15 14
008 store 10 11 0 4
00a jr 1
00c mv 15 14
00e load 14 15 -8 4
012 bnez 14 12
014 store 15 11 -8 4
018 jr 1
'''
},
{
'threshold':'''
000 lui 15 536883200
004 addi 15 15 1032
008 load 14 15 168 4
00c addi 2 2 -16
00e store 2 8 8 4
010 store 2 9 4 4
012 store 2 1 12 4
014 mv 8 10
016 mv 9 11
018 bne 14 10 32
01c store 15 0 168 4
020 load 15 8 288 4
024 beqz 15 50
026 load 10 8 8 2
028 li 12 0
02a addi 11 0 128
02e jal 1 386288
032 load 15 8 68 2
036 beqz 15 68
038 load 10 8 8 2
03a li 12 19
03c addi 11 0 129
040 jal 1 386288
044 load 10 8 8 2
046 li 12 5
048 addi 11 0 129
04c jal 1 386288
050 lui 15 536883200
054 addi 15 15 1380
058 load 14 15 7 1
05a store 8 0 10 1
05e store 8 0 16 1
062 store 8 9 84 1
066 li 13 5
068 bne 13 14 112
06c store 15 0 7 1
070 load 1 2 12 4
072 load 8 2 8 4
074 load 9 2 4 4
076 li 10 0
078 addi 2 2 16
07a jr 1
''',
'builder':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 9 20 4
006 store 2 18 16 4
008 store 2 1 28 4
00a lui 8 1073889280
00e store 2 11 12 4
010 store 2 12 8 4
012 load 9 8 524 4
016 mv 18 10
018 store 8 0 524 4
01c fence.i
020 li 10 4
022 auipc 1 536485888
026 jalr 1 1 -732
02a beqz 10 84
02c load 11 2 12 4
02e load 12 2 8 4
030 store 10 18 2 2
034 store 10 11 0 1
036 store 10 12 1 1
038 store 8 9 524 4
03c lui 15 536883200
040 load 8 2 24 4
042 load 1 2 28 4
044 load 9 2 20 4
046 load 18 2 16 4
048 mv 11 10
04a load 10 15 495 1
04e addi 2 2 32
050 jal 0 275092
054 store 8 9 524 4
058 load 1 2 28 4
05a load 8 2 24 4
05c load 9 2 20 4
05e load 18 2 16 4
060 li 10 4
062 addi 2 2 32
064 jr 1
''',
'sender':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 store 2 18 0 4
006 lui 9 1073889280
00a store 2 1 12 4
00c store 2 8 8 4
00e load 18 9 524 4
012 store 9 0 524 4
016 fence.i
01a bnez 11 36
01c store 9 18 524 4
020 li 10 5
022 jump 70
024 lui 15 536883200
028 load 15 15 493 1
02c mv 8 10
02e mv 10 11
030 bgeu 8 15 58
034 li 15 2
036 bltu 15 8 82
03a jal 1 275014
03c lui 15 1073889280
040 store 15 18 524 4
044 li 10 3
046 load 1 2 12 4
048 load 8 2 8 4
04a load 9 2 4 4
04c load 18 2 0 4
04e addi 2 2 16
050 jr 1
052 load 15 11 -8 4
056 bnez 15 100
058 load 14 11 -2 1
05c addi 15 0 255
060 beq 14 15 112
064 jal 1 275014
066 lui 15 1073889280
06a store 15 18 524 4
06e jump 32
070 lui 10 536883200
074 store 11 8 -2 1
078 addi 10 10 488
07c auipc 1 536596480
080 jalr 1 1 -244
084 lui 11 32768
086 mv 10 8
088 jal 1 275926
08a li 10 0
08c store 9 18 524 4
090 jump 70
''',
'append':'''
000 store 11 0 -8 4
004 load 15 10 0 4
006 bnez 15 14
008 store 10 11 0 4
00a jr 1
00c mv 15 14
00e load 14 15 -8 4
012 bnez 14 12
014 store 15 11 -8 4
018 jr 1
'''
}
)


def specs(part,index):
    k=PARTS.index(part);pc=STARTS[index][k];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'threshold-message literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=pc
        out[pc+int(off,16)]=f
    return out


def acyclic(edges):
    degree=Counter({p:0 for p in edges})
    for qs in edges.values():
        for q in qs:degree[q]+=1
    pending=[p for p,z in degree.items() if not z];count=0
    while pending:
        p=pending.pop();count+=1
        for q in edges[p]:
            degree[q]-=1
            if not degree[q]:pending.append(q)
    return count==len(edges)


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    for off,mask in {'threshold':((0x32,0x5003),),'builder':((0x4a,0x4003),),
                     'sender':((0x28,0x4003),(0x58,0x4003)),'append':()}[part]:
        check(int.from_bytes(raw[off:off+4],'little')&0x707f==mask,'threshold-message unsigned encoding '+part)
    if part in ('builder','sender'):
        off=0x1c if part=='builder' else 0x16
        check(raw[off:off+4]==bytes.fromhex('0f100000'),'threshold-message fence bytes')
    n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'threshold-message boundaries '+part)
    for p,f in s.items():init.g(n,p,'threshold-message operand '+part+' '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'threshold-message identity '+part)
    edges={};calls=[];tails=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'threshold-message ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':
            check(v['rd'] in (0,1),'threshold-message link register')
            if v['rd']==0:tails.append({'offset':p-pc,'target':v['target'],'new_link':False});qs=[]
            else:calls.append({'offset':p-pc,'target':v['target']})
        elif op=='jalr':
            check(v['rd']==v['rs1']==1 and n[p-4]['op']=='auipc' and n[p-4]['rd']==1,'threshold-message call pair')
            calls.append({'offset':p-pc,'target':(p-4+n[p-4]['imm']+v['imm'])&0xfffffffe})
        check(all(q in n for q in qs),'threshold-message closed local CFG');edges[p]=qs
    reachable=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in reachable:continue
        reachable.add(p);pending.extend(edges[p])
    check(reachable==set(n),'threshold-message all nodes reachable')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(calls),len(stores),len(rets),len(tails))==((3,8,1,0),(1,12,1,1),(4,10,1,0),(0,3,2,0))[k],'threshold-message census '+part)
    check(acyclic(edges)==(part!='append'),'threshold-message cycle census')
    if part=='append':
        cut={p:list(qs) for p,qs in edges.items()};cut[pc+0x12].remove(pc+0xc)
        check(acyclic(cut),'threshold-message append only loop cut')
        check(sorted({v['rd'] for v in n.values() if v.get('rd',0)})==[14,15],'threshold-message append keeps S/SP/RA')
    return {'start':pc,'source':SOURCES[index][k],'bytes':len(raw),'sha256':sha256(raw).hexdigest(),
      'instructions':list(n.values()),'CFG':edges,'calls':calls,'tails':tails,'returns':rets,'stores':stores,
      'complete_local_body':True,'local_CFG_acyclic':acyclic(edges),'actual_progress_proved':False}


def certificates(b):
    pc=b['start'];e=b['CFG'];terminals=set(b['returns'])|{pc+t['offset'] for t in b['tails']}
    def path(a,ends):
        pending=deque([(a,[a])]);seen=set()
        while pending:
            p,s=pending.popleft()
            if p in ends:return s
            if p in seen:continue
            seen.add(p);pending.extend((q,s+[q]) for q in e[p])
        raise RuntimeError('threshold-message no syntactic witness')
    walks=[]
    for p,qs in e.items():
        for q in qs:
            seq=path(pc,{p})+[q]+path(q,terminals)[1:]
            previous.valid(e,seq);check(seq[0]==pc and seq[-1] in terminals,'threshold-message complete edge witness')
            walks.append([x-pc for x in seq])
    return {'syntactic_edge_witness_count':len(walks),'edge_witness_sha256':sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),
      'all_local_edges_witnessed':True,'all_paths_feasible_or_callchain_terminating_proved':False}


def walk(b,choices):
    pc=b['start'];seq=previous.until(b['CFG'],pc,{pc+a:pc+z for a,z in choices.items()})
    previous.valid(b['CFG'],seq);return [p-pc for p in seq]


def domains():
    admitted=0
    for count in range(256):
        for task in range(256):
            ok=task>2 and task<count
            check(ok==(3<=task<=count-1),'threshold-message admission equivalence')
            if ok:
                admitted+=1;check(3<=task<=254 and task!=255,'threshold-message accepted owner differs from FF')
    check(admitted==31878,'threshold-message exact task/count domain')
    digest=sha256()
    for identity in range(65536):
        for code,reason in ((128,0),(129,19),(129,5)):
            payload=bytes((code,reason,identity&255,identity>>8))
            check(len(payload)==4 and int.from_bytes(payload[2:4],'little')==identity,'threshold-message payload packing')
            digest.update(payload)
    # Header H; allocator Q=H+8, visible message M=Q+8, with 4 visible bytes.
    check(4+8==12 and 12&0xfffc==12 and 0xf000|4==0xf004,'threshold-message allocation request')
    check(8+8+4==20 and (8+6)-(8+8)==-2,'threshold-message marker/extent equations')
    hidden_written=set(range(0,4))|{4,5,6}
    check(7 not in hidden_written and set(range(8,12)).isdisjoint(hidden_written),'threshold-message hidden byte7 uninitialized')
    return {'task_count_pairs':65536,'admitted_task_count_pairs':admitted,'admitted_tasks':[3,254],
      'payload_cases':65536*3,'payload_sha256_identity_then_code_order':digest.hexdigest(),
      'body_layout':'M0=code,M1=reason,M2..3=littleendian low16 sampled O8',
      'message_size':4,'private_core_request_bytes':12,'private_core_tag':0xf004,
      'relative_to_private_header_H':{'core_payload_Q':8,'visible_message_M':16,'end_exclusive':20},
      'hidden_prefix_byte7_initialized':False,'actual_input_reachability_proved':False}


def profile(data,index):
    bs={p:body(init.binding.take(data,SOURCES[index][k],SIZES[k]),p,index) for k,p in enumerate(PARTS)}
    ns={p:{v['pc']-b['start']:v for v in b['instructions']} for p,b in bs.items()}
    t,u,s,a=(ns[p] for p in PARTS);tp,bp,sp,ap=STARTS[index]
    T=0x20003220+80*index;C=0x2000319c+80*index;global_B=0x200033b8+80*index;status=0x2000351b+80*index
    check([c['target'] for c in bs['threshold']['calls']]==[bp]*3,'threshold-message three builder joins')
    check(bs['builder']['calls']==[{'offset':0x26,'target':message.ENTRY}] and bs['builder']['tails']==[{'offset':0x50,'target':sp,'new_link':False}],'threshold-message builder joins')
    freepc,_,countbase,_,freehash,_=dealloc.DETAILS[index]
    eventpc=previous.consumer.DETAILS[index][1]
    check([c['target'] for c in bs['sender']['calls']]==[freepc,freepc,ap,eventpc],'threshold-message sender complete call joins')
    check(C==countbase and 0x20003000+s[0x28]['imm']==C+1 and 0x20003000+s[0x78]['imm']==C-4 and 0x20003000+u[0x4a]['imm']==C+3,'threshold-message distinct global roles')
    check(t[0]['imm']+t[4]['imm']==global_B and t[0x50]['imm']+t[0x54]['imm']+t[0x58]['imm']==status,'threshold-message threshold globals')
    threshold_paths={}
    for flags in range(16):
        choices={0x18:0x1c if flags&1 else 0x20,0x24:0x26 if flags&2 else 0x32,
                 0x36:0x38 if flags&4 else 0x44,0x68:0x6c if flags&8 else 0x70}
        seq=walk(bs['threshold'],choices);threshold_paths[str(flags)]=seq
        actual=[o for o in seq if o in (0x2e,0x40,0x4c)]
        check(actual==([0x2e] if flags&2 else [])+([0x40] if flags&4 else [])+[0x4c],'threshold-message selected call order')
        check(seq[-4:]==[0x74,0x76,0x78,0x7a],'threshold-message final forced zero')
    check([o for o,v in t.items() if v.get('rd')==10][-1]==0x76 and t[0x76]['imm']==0,'threshold-message no downstream A0 overwrite')
    check([o for o,v in t.items() if v.get('rd')==11]==[0x2a,0x3c,0x48],'threshold-message A1 not restored or forced8')
    sender_choices={'null':{0x1a:0x1c},'task_ge_count':{0x1a:0x24,0x30:0x3a},
      'task_le2':{0x1a:0x24,0x30:0x34,0x36:0x3a},
      'next_nonzero':{0x1a:0x24,0x30:0x34,0x36:0x52,0x56:0x64},
      'marker_notFF':{0x1a:0x24,0x30:0x34,0x36:0x52,0x56:0x58,0x60:0x64},
      'accepted':{0x1a:0x24,0x30:0x34,0x36:0x52,0x56:0x58,0x60:0x70}}
    sender_paths={name:walk(bs['sender'],choices) for name,choices in sender_choices.items()}
    for name,seq in sender_paths.items():
        last=[s[o]['imm'] for o in seq if s[o]['op']=='li' and s[o]['rd']==10][-1]
        check(last==(0 if name=='accepted' else 3 if name.startswith('task_') else 5),'threshold-message selected sender replies')
        check(seq[-1]==0x50,'threshold-message sender RET')
    accepted=sender_paths['accepted']
    check(accepted.index(0x74)<accepted.index(0x80)<accepted.index(0x88)<accepted.index(0x8a),'threshold-message queue then event then forced0')
    check(not any(s[o]['op'] in BRANCHES for o in accepted[accepted.index(0x88)+1:]),'threshold-message event reply ignored')
    builder_paths={name:walk(bs['builder'],{0x2a:z}) for name,z in (('allocation0',0x54),('allocation_nonzero',0x2c))}
    check(builder_paths['allocation0'][-3:]==[0x60,0x62,0x64] and builder_paths['allocation_nonzero'][-1]==0x50,'threshold-message builder failRET versus success tail')
    append_empty=walk(bs['append'],{6:8});append_one=walk(bs['append'],{6:14,18:20})
    append_two=[0,4,6,14,18,12,14,18,20,24]
    previous.valid(bs['append']['CFG'],[ap+o for o in append_two])
    check(append_empty==[0,4,6,8,10] and append_one==[0,4,6,14,18,20,24],'threshold-message empty/nonempty publication witnesses')
    # Guard the existing allocation, public deallocation and event bodies again.
    msgraw=init.binding.take(data,0x404a6+64*index,message.LENGTH)
    check(msgraw==message.MSG and sha256(msgraw).hexdigest()==message.MSG_SHA,'threshold-message allocator identity')
    mn=message.decode(msgraw,message.ENTRY)
    for p,f in message.message_specs().items():message.guard(mn,p,'threshold-message allocator operands',**f)
    core=previous.previous.core;corebytes=init.binding.take(data,core.DETAILS[index][0],208)
    previous.previous.core_body(corebytes,index)
    freeraw=init.binding.take(data,freepc,len(dealloc.FREE))
    check(sha256(freeraw).hexdigest()==freehash and dealloc.normalized(freeraw,((62,8),))==dealloc.normalized(dealloc.FREE,((62,8),)),'threshold-message public deallocator identity')
    check(dealloc.auipc_call(freeraw,62,freepc+62)==0x20000110,'threshold-message private deallocator target')
    fn=decode(freeraw,freepc)
    free_call_walk=[0,2,4,6,10,12,16,20,24,42,46,50,62,66]
    check(fn[freepc+24]['target']==freepc+42 and fn[freepc+50]['target']==freepc+62,'threshold-message marker-approved deallocator branch')
    check(not any(fn[freepc+o].get('rd')==10 for o in free_call_walk),'threshold-message exact M forwarded unchanged')
    check(16-8==8 and 16!=8,'threshold-message interior pointer does not equal core payload')
    event=previous.consumer.event_body(init.binding.take(data,eventpc,64),eventpc,C,previous.consumer.DETAILS[index][3])
    # Bind mapped outer call + store43 + fresh T + ordinary and unlinked exits.
    src=prefix.DETAILS[index][0];entry=0x20000d50
    check(src-(0x402b0+64*index)+0x20000040==entry,'threshold-message mapped callback coordinate')
    outer=exits.window(init.binding.take(data,src+324,52),'threshold_exit',entry,exits.PARAMS[index],exits.HASHES[index][0])
    epilogue=exits.window(init.binding.take(data,src+834,20),'epilogue',entry,exits.PARAMS[index],exits.HASHES[index][2])
    check(outer['calls'][0]['target']==hex(tp) and T==0x20003000+exits.PARAMS[index][2],'threshold-message mapped helper/T join')
    on={v['pc']-(entry+324):v for v in outer['instructions']}
    check(on[12]['rs2']==10 and on[12]['imm']==43 and on[20]['rd']==6,'threshold-message store reply before fresh T')
    return {'label':init.binding.PROFILES[index][0],'bodies':bs,'CFG_certificates':{p:certificates(b) for p,b in bs.items()},
      'threshold_syntactic_branch_walks':threshold_paths,'builder_walks':builder_paths,'sender_walks':sender_paths,
      'append_walks':{'empty':append_empty,'one_prior':append_one,'two_prior':append_two},
      'deallocator_markerFF_call_walk':free_call_walk,'deallocator_private_A0':'entry M unchanged; M is not core payload Q=M-8',
      'globals':{'threshold_owner':global_B+168,'status_byte':status,'task_count_byte':C+1,'builder_task_byte':C+3,'message_head':C-4,'fresh_failure_slot':T},
      'reused_bodies':{'allocator':{'entry':message.ENTRY,'bytes':message.LENGTH,'sha256':message.MSG_SHA},
        'core':{'entry':core.ENTRY,'bytes':208,'sha256':sha256(corebytes).hexdigest()},
        'deallocator':{'entry':freepc,'bytes':len(freeraw),'sha256':freehash},
        'event':{k:event[k] for k in ('start','bytes','sha256')},'outer_threshold_exit':outer,'outer_epilogue':epilogue},
      'threshold_contract':['sampled global_B168==entryO ->clear before calls; O288 is a word guard, not a dereferenced pointer',
        'O288 nonzero ->builder(freshU16[O8],128,0); freshU16[O68] nonzero ->builder(freshU16[O8],129,19); always builder(freshU16[O8],129,5)',
        'normal return: O10=0,O16=0,O84=low8 entryA1; sampled status5 ->clear; A0 forced0 regardless nested replies; A1 not restored'],
      'builder_contract':['request visible length4; allocator0 ->A0=4 RET; nonzero M ->write all four body bytes; restore frame then unlinked tail sender(freshU8[C+3],M)',
        'allocator Q=H+8 owns12 bytes; hidden Q0..3=0,Q4..5=4,Q6=FF,Q7 unspecified; visible M=Q+8=H+16',
        'A2 ambient reason remains at allocator entry; if core fallback slot nonzero, optional callback may see (1,000cf004,ambient A2); private callback retention remains opaque'],
      'sender_contract':['nonnull M and full task>2 and task<freshU8[C+1], U32[M-8]==0 and U8[M-2]==255 required',
        'accepted: write low8task to M-2; append(C-4,M); event(task,8000); force0 despite event reply; queued heap message retained globally',
        'null ->5; invalid task ->attempt dealloc then3; bad header ->attempt dealloc then5; dealloc marker rejection means attempted cleanup does not imply actual free',
        'public deallocator forwards M unchanged, not M-8, to private release20000110; M=H+16 is interior to the original allocation, so original-block release/ownership inverse is not established',
        'append first clears M-8 then walks/publishes; finite valid list and distinct owned M required; no bound, duplicate detection or delivery proof'],
      'outer_join':['under normal nested returns and preserved S/frame/object/RA, helper0 ->outer O43=0; entryA1=8 ->O84=8 only if later stores/aliases do not overwrite it',
        'fresh T==0 ->ordinary restored-frame RET with A0=0; A1 then-live, not forced8; fresh T!=0 ->restore frame,unlinked JR(T&~1),A0=5,A1=2; final return opaque',
        'T zero at callback entry does not prove fresh T zero after allocation/cleanup/queue/event/object stores; valid nonalias and no external writers required'],
      'preservation_premises':'valid aligned objects >=292 bytes and stack/control/heap/header/message/list/global separation; nominal GP/QK semantics; nested normal return, S/SP/RA and saved-frame integrity; no IRQ/DMA/reentry/other-writer interference; fresh snapshots need not equal earlier reads',
      'physical_critical_section/actual_binding/complete_message_consumption/lifetimes_proved':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage):
    previous.derive(image,carriers,header,coverage)
    dealloc.derive(image,carriers,header)
    profiles=[profile(data,i) for i,data in enumerate(carriers)]
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==796,'threshold-message full byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==282,'threshold-message full instruction census')
    return {'schema':'TSL9-threshold-message-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'new_complete_body_bytes':796,'new_complete_body_instructions':282,'C_reconstruction_coverage_changed':False,
      'remaining':['actual installed provider/dispatch mapping','message dequeue/consume/free lifetime','all alias/writer effects needed for unconditional T retention'],
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
    mutations=0;unsigned=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);ns=decode(raw,STARTS[i][k])
            for p,v in ns.items():
                off=p-STARTS[i][k];z=v['size'];bad=bytearray(raw)
                bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(bad,part,i)
                except RuntimeError:pass
                else:raise RuntimeError('threshold-message mutation escaped '+part+' '+hex(off))
                mutations+=1
            for off in {'threshold':(0x32,),'builder':(0x4a,),'sender':(0x28,0x58),'append':()}[part]:
                bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
                try:body(bad,part,i)
                except RuntimeError as ex:check('unsigned encoding' in str(ex),'threshold-message specific signedness guard')
                else:raise RuntimeError('threshold-message signedness mutation escaped')
                unsigned+=1
    check((mutations,unsigned)==(282,8),'threshold-message mutation census');domains()
    print('PASS:282 instruction mutations and8 unsigned-to-signed variants rejected;65536 task/count and196608 payload cases')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(carriers);output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if args.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'threshold-message exact ledger replay')
    print('PASS:8 complete candidate bodies796B/282i;threshold->builder->sender->append/event and outer return joins;exact ledger')
    print('PASS:NO target execution/emulation;actual provider,whole lifetime and physical critical-section effects UNPROVED')


if __name__=='__main__':main()
