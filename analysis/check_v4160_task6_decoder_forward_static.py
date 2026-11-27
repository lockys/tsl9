"""Offline decoder/bounds-adjust/type-validator/tuple-forwarding contracts.

Original complete operands/CFGs, immutable paths, scalar and interval algebra.
No target ISA, mutable registers/RAM/heap/queue, provider or MMIO is run.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_task6_v34_consumer_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
OUT=Path(__file__).with_name('v4160-task6-decoder-forward-static.json')
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
PARTS=('decoder', 'typevalidator', 'boundsadjust', 'forwarder')
STARTS=((319184, 316832, 536871396, 320144), (319336, 316984, 536871396, 320296))
SOURCES=((319184, 316832, 263252, 320144), (319336, 316984, 263316, 320296))
SIZES=(132, 48, 56, 94)
COUNTS=(52, 17, 17, 39)
HASHES=(('c0269e7b81b71fb928f50bc0fb8ce0b4bcb9b703e41be90141d5f098ac3790ab', '75bd7ae1702c45ae2891ce375be3a09d70059deb26891c38303f635212e879be', '0de67b30b05144f0f11d0f8a526aadb9b276cf6a52fb91554ec35b4d7738572f', '7f91af819b1f854da1d0870f126b5239cd45ab04e03aee06100b1e7a078650b4'), ('3de7ba27669e9805ab3b884be117c007b8fbe206aee622eaf1a2fd5e75734bf8', '02149d4b08d66a2c893c6537fa9bbc8e56e4bd60d611d4ab15d243320abc9bb1', 'a00ed5538f4ae03e92eae6b1be8ca946760ef394f96ec44b9632fdacb94c1454', 'fb2532dd989c234f88fe40743932c22ca6ea6ef310f339115ac74ab7ed3abbec'))
TYPED_LOADS=({'decoder': ((78, 2),), 'typevalidator': ((4, 4), (12, 2)), 'boundsadjust': ((8, 2), (12, 2)), 'forwarder': ()}, {'decoder': ((78, 2),), 'typevalidator': ((4, 4), (12, 2)), 'boundsadjust': ((8, 2), (12, 2)), 'forwarder': ()})
LITERALS=(
{
'decoder':'''
000 store 10 0 4 4
004 load 14 11 4 1
006 li 15 2
008 beq 14 15 16
00c li 10 1
00e jr 1
010 load 13 11 6 2
012 li 14 3
014 bgeu 14 13 12
018 load 15 11 8 4
01a addi 2 2 -32
01c store 2 1 28 4
01e store 2 8 24 4
020 store 2 9 20 4
022 store 2 18 16 4
024 store 2 19 12 4
026 load 9 15 1 1
028 load 12 15 0 1
02a slli 9 9 8
02c or 9 9 12
02e addi 12 9 4
032 bne 12 13 116
036 load 8 15 3 1
038 load 15 15 2 1
03a mv 19 11
03c slli 8 8 8
03e or 8 8 15
040 addi 15 8 -4
044 slli 15 15 16
046 srli 15 15 16
048 mv 18 10
04a bltu 14 15 108
04e load 10 19 8 4
052 store 18 9 2 2
056 store 18 8 0 2
05a li 11 -4
05c auipc 1 536551424
060 jalr 1 1 696
064 store 18 10 4 4
068 li 10 0
06a jump 118
06c mv 10 8
06e jal 1 316832
072 bnez 10 78
074 li 10 1
076 load 1 2 28 4
078 load 8 2 24 4
07a load 9 2 20 4
07c load 18 2 16 4
07e load 19 2 12 4
080 addi 2 2 32
082 jr 1
''',
'typevalidator':'''
000 lui 15 536883200
004 load 11 15 -96 1
008 lui 15 536883200
00c load 14 15 -104 4
010 li 15 0
012 bne 11 15 28
016 li 13 0
018 mv 10 13
01a jr 1
01c load 12 14 2 2
01e mv 13 14
020 beqz 12 38
022 beq 12 10 24
026 addi 15 15 1
028 andi 15 15 255
02c addi 14 14 16
02e jump 18
''',
'boundsadjust':'''
000 lui 15 536883200
004 lui 13 536883200
008 load 15 15 404 4
00c load 12 13 396 4
010 mv 14 10
012 sub 11 10 11
016 bne 12 15 30
01a mv 10 14
01c jump 54
01e addi 13 15 8
022 load 15 15 0 4
024 bltu 14 13 22
028 bgeu 14 15 22
02c mv 10 11
02e bltu 11 13 22
032 bgeu 11 15 22
036 jr 1
''',
'forwarder':'''
000 addi 2 2 -32
002 store 2 18 16 4
004 mv 18 10
006 li 10 12
008 store 2 9 20 4
00a store 2 1 28 4
00c store 2 8 24 4
00e store 2 11 12 4
010 mv 9 12
012 auipc 1 536551424
016 jalr 1 1 -108
01a beqz 10 90
01c load 11 2 12 4
01e addi 15 0 160
022 store 10 15 0 2
024 store 10 11 2 2
026 mv 8 10
028 li 12 8
02a addi 10 10 4
02c beqz 9 78
02e mv 11 9
030 auipc 1 536551424
034 jalr 1 1 114
038 mv 11 8
03a mv 10 18
03c jal 1 274952
040 li 10 0
042 load 1 2 28 4
044 load 8 2 24 4
046 load 9 2 20 4
048 load 18 2 16 4
04a addi 2 2 32
04c jr 1
04e li 11 0
050 auipc 1 536551424
054 jalr 1 1 188
058 jump 56
05a li 10 1
05c jump 66
'''
},
{
'decoder':'''
000 store 10 0 4 4
004 load 14 11 4 1
006 li 15 2
008 beq 14 15 16
00c li 10 1
00e jr 1
010 load 13 11 6 2
012 li 14 3
014 bgeu 14 13 12
018 load 15 11 8 4
01a addi 2 2 -32
01c store 2 1 28 4
01e store 2 8 24 4
020 store 2 9 20 4
022 store 2 18 16 4
024 store 2 19 12 4
026 load 9 15 1 1
028 load 12 15 0 1
02a slli 9 9 8
02c or 9 9 12
02e addi 12 9 4
032 bne 12 13 116
036 load 8 15 3 1
038 load 15 15 2 1
03a mv 19 11
03c slli 8 8 8
03e or 8 8 15
040 addi 15 8 -4
044 slli 15 15 16
046 srli 15 15 16
048 mv 18 10
04a bltu 14 15 108
04e load 10 19 8 4
052 store 18 9 2 2
056 store 18 8 0 2
05a li 11 -4
05c auipc 1 536551424
060 jalr 1 1 544
064 store 18 10 4 4
068 li 10 0
06a jump 118
06c mv 10 8
06e jal 1 316984
072 bnez 10 78
074 li 10 1
076 load 1 2 28 4
078 load 8 2 24 4
07a load 9 2 20 4
07c load 18 2 16 4
07e load 19 2 12 4
080 addi 2 2 32
082 jr 1
''',
'typevalidator':'''
000 lui 15 536883200
004 load 11 15 -16 1
008 lui 15 536883200
00c load 14 15 -24 4
010 li 15 0
012 bne 11 15 28
016 li 13 0
018 mv 10 13
01a jr 1
01c load 12 14 2 2
01e mv 13 14
020 beqz 12 38
022 beq 12 10 24
026 addi 15 15 1
028 andi 15 15 255
02c addi 14 14 16
02e jump 18
''',
'boundsadjust':'''
000 lui 15 536883200
004 lui 13 536883200
008 load 15 15 484 4
00c load 12 13 476 4
010 mv 14 10
012 sub 11 10 11
016 bne 12 15 30
01a mv 10 14
01c jump 54
01e addi 13 15 8
022 load 15 15 0 4
024 bltu 14 13 22
028 bgeu 14 15 22
02c mv 10 11
02e bltu 11 13 22
032 bgeu 11 15 22
036 jr 1
''',
'forwarder':'''
000 addi 2 2 -32
002 store 2 18 16 4
004 mv 18 10
006 li 10 12
008 store 2 9 20 4
00a store 2 1 28 4
00c store 2 8 24 4
00e store 2 11 12 4
010 mv 9 12
012 auipc 1 536551424
016 jalr 1 1 -260
01a beqz 10 90
01c load 11 2 12 4
01e addi 15 0 160
022 store 10 15 0 2
024 store 10 11 2 2
026 mv 8 10
028 li 12 8
02a addi 10 10 4
02c beqz 9 78
02e mv 11 9
030 auipc 1 536551424
034 jalr 1 1 -38
038 mv 11 8
03a mv 10 18
03c jal 1 275092
040 li 10 0
042 load 1 2 28 4
044 load 8 2 24 4
046 load 9 2 20 4
048 load 18 2 16 4
04a addi 2 2 32
04c jr 1
04e li 11 0
050 auipc 1 536551424
054 jalr 1 1 36
058 jump 56
05a li 10 1
05c jump 66
'''
}
)

def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'decoder-forward literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=pc
        out[pc+int(off,16)]=f
    return out


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    for off,f3 in TYPED_LOADS[index][part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'decoder-forward typed load encoding')
    n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'decoder-forward complete boundaries '+part)
    for p,f in s.items():init.g(n,p,'decoder-forward operand '+part+' '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'decoder-forward complete identity '+part)
    e={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'decoder-forward ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':check(v['rd']==1,'decoder-forward linked direct call');calls.append({'offset':p-pc,'target':v['target']})
        elif op=='jalr':
            check(v['rd']==v['rs1']==1 and n[p-4]['op']=='auipc' and n[p-4]['rd']==1,'decoder-forward linked call pair')
            calls.append({'offset':p-pc,'target':(p-4+n[p-4]['imm']+v['imm'])&0xfffffffe})
        check(all(q in n for q in qs),'decoder-forward closed local CFG');e[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(e[p])
    check(seen==set(n),'decoder-forward all local nodes reachable')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(calls),len(rets),len(stores))==((2,2,9),(0,1,0),(0,1,0),(4,1,7))[k],'decoder-forward complete call/return/store census')
    cyclic=part in ('typevalidator','boundsadjust');check(common.acyclic(e)!=cyclic,'decoder-forward cycle classification')
    if cyclic:
        cuts=((0x2e,0x12),) if part=='typevalidator' else tuple((a,0x16) for a in (0x24,0x28,0x2e,0x32))
        cut={p:list(qs) for p,qs in e.items()}
        for a,z in cuts:check(pc+z in cut[pc+a],'decoder-forward loop edge');cut[pc+a].remove(pc+z)
        check(common.acyclic(cut),'decoder-forward all cycles cut')
        check(not any(v.get('rd') in (1,2,8,9,18,19) for v in n.values()),'decoder-forward readonly leaves keep S/SP/RA')
    return {'start':pc,'source':SOURCES[index][k],'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
      'CFG':e,'calls':calls,'tails':[],'returns':rets,'stores':stores,'complete_local_body':True,'actual_progress_or_ownership_proved':False}


def witnesses(bs):
    d,f,b=(bs[k] for k in ('decoder','forwarder','boundsadjust'));dp=d['start'];fp=f['start'];bp=b['start']
    dn={v['pc']-dp:v for v in d['instructions']};fn={v['pc']-fp:v for v in f['instructions']}
    paths={p:previous.previous.allocation.previous.dag_paths(bs[p]) for p in ('decoder','forwarder')}
    replies={p:{'0':0,'1':0} for p in paths}
    for part,groups in paths.items():
        n=dn if part=='decoder' else fn
        for seq in groups:
            defs=[o for o in seq if n[o].get('rd')==10];last=n[defs[-1]]
            check(last['op']=='li' and last['imm'] in (0,1),'decoder-forward fixed normal reply')
            code=last['imm'];replies[part][str(code)]+=1
            if part=='decoder':
                check(0 in seq and (0x64 in seq)==(code==0),'decoder-forward output pointer assigned only normal success')
                check((0x52 in seq)==(code==0) and (0x56 in seq)==(code==0),'decoder-forward halfwords untouched on rejected paths')
                if code==0:check(seq.index(0x4e)<seq.index(0x52)<seq.index(0x60)<seq.index(0x64),'decoder-forward fresh originalM8 before output writes and adjust')
            else:
                check((0x3c in seq)==(code==0),'decoder-forward send attempted only nonnull newmessage path')
                if code==0:check((0x34 in seq)!=(0x54 in seq),'decoder-forward copy8 orfill8 exclusively')
    prefix=[0,4,8,12,16,18,22];restore=[26,28,54]
    rows=[30,34,36,40,44,46,50,54]
    walks={'empty_or_exhausted':prefix+restore,'both_pointers_inside':prefix+rows,
      'original_below':prefix+[30,34,36,22]+restore,
      'original_at_or_above_next':prefix+[30,34,36,40,22]+restore,
      'adjusted_below':prefix+[30,34,36,40,44,46,22]+restore,
      'adjusted_at_or_above_next':prefix+[30,34,36,40,44,46,50,22]+restore}
    for name,seq in walks.items():
        common.previous.valid(b['CFG'],[bp+o for o in seq]);check(seq[-1]==54,'decoder-forward bounds witness ordinary return')
        if name.startswith('adjusted_'):check(seq.index(44)<seq.index(26),'decoder-forward failed adjusted value overwritten by original before return')
    return {'DAG_paths':paths,'normal_reply_path_counts':replies,'bounds_immutable_walks':walks,
      'all_syntactic_paths_feasible_or_heap_traversal_terminating_proved':False}


def domains():
    direct=[]
    for code in range(65536):
        ok=((code-4)&65535)<=3
        check(ok==(4<=code<=7),'decoder-forward direct type range')
        if ok:direct.append(code)
    check(direct==[4,5,6,7],'decoder-forward exactly four bypass types')
    for size in range(65536):
        total=size+4;possible=total<=65535
        check(possible==(size<=65531),'decoder-forward header-size equality representable domain')
        if possible:check(total>3,'decoder-forward successful decoded message length lower bound')
    # Pointer interval and subtraction identities only, never a heap machine.
    vectors=[]
    for pointer in (0,1,2,4,0x20005002,0xfffffffb,0xfffffffc,0xfffffffe,0xffffffff):
        for delta in (0,4,0xfffffffc):
            candidate=(pointer-delta)&0xffffffff
            if delta==0xfffffffc:check(candidate==(pointer+4)&0xffffffff,'decoder-forward negative delta is forward4')
            vectors.append([pointer,delta,candidate])
    cases=0
    for lower in range(17):
        for upper in range(lower+1,33):
            for original in range(37):
                candidate=original+4
                both=lower<=original<upper and lower<=candidate<upper
                check(both==(lower<=original and candidate<upper),'decoder-forward nonwrapping plus4 interval reduction')
                cases+=1
    geometry=[]
    for length in range(4,256):
        decoded=length-4;copied=4*((length+5)>>2);rounded=((length+8)&65535)&0xfffc
        check(6+decoded==length+2<=copied<=rounded and 6<rounded,'decoder-forward retained V34 byte-length geometry')
        geometry.append([length,decoded,copied,rounded])
    # Tuple in parser's live48B frame versus decoder/forwarder32B child frames.
    tuple_bytes=set(range(24,32));parent_saves=set(range(36,48));child_saves=set(range(-20,0))
    check(tuple_bytes.isdisjoint(parent_saves|child_saves),'decoder-forward nested frame/tuple intervals disjoint')
    check(set(range(4,12))==set(range(4,4+8)) and 4+4==8,'decoder-forward tupleword4 maps newmessageword8')
    return {'type_U16_cases':65536,'direct_types':direct,'size_U16_cases':65536,'size_success_domain':[0,65531],
      'pointer_vectors':vectors,'nonwrapping_interval_cases':cases,'V34_byte_length_geometry_cases':len(geometry),
      'V34_geometry_sha256':sha256(json.dumps(geometry,separators=(',',':')).encode()).hexdigest(),
      'conditional_V34_layout':'messageM8=P+2;decodedpointer=P+6 onlyif freshM8retained andsameheaderchecksaccept. Bodylen=L-4;[P+6,P+L+2) fitscopiedextent forcurrentbyteL4..255,notuniversalU16ABI',
      'tuple_offsets':{'code_U16':0,'decoded_length_U16':2,'pointer_word':4,'bytes':8},
      'unconditional_base_capacity_reachability_or_ownership_proved':False}


def profile(image,data,hexraw,index,parent):
    bs={p:body(init.binding.take(data,SOURCES[index][k],SIZES[k]),p,index) for k,p in enumerate(PARTS)}
    d,t,b,f=(bs[k] for k in PARTS);dp,tp,bp,fp=STARTS[index]
    dn={v['pc']-dp:v for v in d['instructions']};tn={v['pc']-tp:v for v in t['instructions']};bn={v['pc']-bp:v for v in b['instructions']};fn={v['pc']-fp:v for v in f['instructions']}
    check(d['calls']==[{'offset':0x60,'target':bp},{'offset':0x6e,'target':tp}],'decoder-forward exact decoder leaf joins')
    sender=common.STARTS[index][2]
    check(f['calls']==[{'offset':0x16,'target':0x20000236},{'offset':0x34,'target':0x20000332},{'offset':0x3c,'target':sender},{'offset':0x54,'target':0x2000039c}],'decoder-forward complete forwarder callees')
    check(dn[0]['rs1']==10 and dn[0]['rs2']==0 and dn[0]['imm']==4 and dn[0]['width']==4,'decoder-forward first output pointer clear')
    check(dn[0x18]['imm']==dn[0x4e]['imm']==8 and dn[0x18]['rs1']==11 and dn[0x4e]['rs1']==19,'decoder-forward sampled versus fresh original payload reads')
    check(dn[0x5a]['imm']==-4 and bn[0x12]['op']=='sub' and bn[0x12]['rs1']==10 and bn[0x12]['rs2']==11,'decoder-forward adjustment sign and operand order')
    check(dn[0x52]['imm']==2 and dn[0x56]['imm']==0 and dn[0x64]['imm']==4,'decoder-forward tuple field mapping')
    check(fn[0x1e]['imm']==0xa0 and fn[0x22]['imm']==0 and fn[0x24]['imm']==2 and fn[0x28]['imm']==8 and fn[0x2a]['imm']==4,'decoder-forward typeA0/header/copy8 mapping')
    check(fn[0x38]['rs2']==8 and fn[0x3a]['rs2']==18 and fn[0x40]['imm']==0,'decoder-forward sender ignored then force0')
    G=0x20003000;count=0x20002fa0+80*index;array=0x20002f98+80*index
    check(G+tn[4]['imm']==count and G+tn[12]['imm']==array,'decoder-forward validator uses distinct16-byte array source')
    check(array!=parent['roles']['record_array_pointer'] and count!=parent['roles']['inline_counter_byte'],'decoder-forward validator storage distinct from prior arrays/counters')
    ip=previous.origin.STARTS[index][0];ib=previous.origin.body(init.binding.take(data,ip,386),'initializer',index);inn={v['pc']-ip:v for v in ib['instructions']}
    check(G+inn[138]['imm']==count and G+inn[146]['imm']==array and inn[228]['rs1']==8 and inn[240]['rs1']==18,'decoder-forward initializer validator-array source join')
    check(inn[218]['imm']+0x5000==0x4c05 and inn[230]['imm']==4,'decoder-forward validator allocation16*count tag4c05')
    first=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy']
    def src(target):return int(first['source'],16)+target-int(first['destination'],16)
    check(src(bp)==SOURCES[index][2] and bp+56<=int(init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy_end_exclusive'],16),'decoder-forward captured complete RAM bounds source')
    core=common.previous.previous.core
    check(bn[8]['imm']+G==core.DETAILS[index][1] and bn[12]['imm']+G==core.DETAILS[index][3],'decoder-forward bounds uses same small-head/sentinel slots')
    payload=previous.previous.previous.arithmetic.payload
    cb=payload.body(init.binding.take(data,src(0x20000332),58),'copy',0x20000332,58,18,3,init.binding.COPY_HASH)
    fill=previous.previous.allocation.source.fill_contract(init.binding.take(data,src(0x2000039c),46))
    sb=common.body(init.binding.take(data,sender,146),'sender',index)
    msgraw=init.binding.take(data,src(0x20000236),86);check(msgraw==common.message.MSG and sha256(msgraw).hexdigest()==common.message.MSG_SHA,'decoder-forward old message allocation wrapper')
    parser=parent['bodies']['parser'];pn={v['pc']-parser['start']:v for v in parser['instructions']}
    check(next(c['target'] for c in parser['calls'] if c['offset']==0x10)==dp and next(c['target'] for c in parser['calls'] if c['offset']==0xc2)==fp,'decoder-forward caller complete joins')
    check(pn[0xc]['imm']==24 and pn[0x14]['imm']==28 and pn[0x18]['target']==parser['start']+0x7e,'decoder-forward failure tuple0/reply1 joins caller cleanup')
    check(pn[0xbe]['imm']==24 and pn[0xc0]['rs2']==8 and pn[0xbc]['width']==1,'decoder-forward source tuple/task/ID call mapping')
    _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
    for part,bb in bs.items():
        check(sparse.captured(mem,bb['source'],bb['bytes'])==init.binding.take(data,bb['source'],bb['bytes']),'decoder-forward original strict HEX backing')
        receipts.append({'part':part,'source':bb['source'],'bytes':bb['bytes'],'all_bytes_captured':True})
    return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,
      'CFG_certificates':{p:common.certificates(bb) for p,bb in bs.items()},'witnesses':witnesses(bs),
      'roles':{'validation_count_U8':count,'validation_16byte_array_pointer':array,'bounds_head_slot':G+bn[8]['imm'],'bounds_sentinel_slot':G+bn[12]['imm']},
      'reused_bodies':{'message_allocator':{'source':src(0x20000236),'bytes':86,'sha256':common.message.MSG_SHA},
        'bytecopy':{'source':src(0x20000332),'bytes':58,'sha256':cb['sha256']},'fill':{'source':src(0x2000039c),'bytes':46,'sha256':fill['sha256']},
        'sender':{'start':sender,'bytes':146,'sha256':sb['sha256']},'initializer':{'start':ip,'bytes':386,'sha256':ib['sha256']},'new_code_bytes_counted':0},
      'decoder_contract':['first SW0[out4] before message validation;requiresU8M4=2 andU16M6>3;no out/message/payload null or extent guards',
        'sampleP0=M8;LE16(P0[0..1])=K;requireK+4==sampledU16M6;LE16(P0[2..3])=code;directcode4..7 bypassvalidator,othercodes require validator(code) nonzero',
        'success reloadsfreshP1=M8 BEFOREwritingout2=K,out0=code;calladjust(P1,-4);store replyout4;return0 regardlessadjusted/original/zero pointer',
        'rejected paths return1,out4 remainszero;out0/2 not locallywritten. Underdisjointoutput/frame/message/payload/heap andclosedreadonlycallees/noexternalwriters, localwrites do notchangeM8;actualfreshidentity remainsconditional'],
      'validator_contract':['capturecountU8 andbaseword;scan atmostcount0..255 rowsstride16,readfreshU16[row2];nonzerotag==fullinputcode returnsrow,otherwise0 aftercount',
        'zero tags nevermatch;no pointer/null/extent guards;no stores/calls/frame/S/SP/RA writes. A matchingrowataddress0 wouldstillbezero reply;actualnonnullallocation/framecontext needed',
        '16-byte validator array comes from initializer tag4c05/countslot2fa0;distinctfromV34recordarray tag4c06/12-byte rows33318'],
      'bounds_contract':['candidate=(original-entrydelta)mod32;decoder deltafffffffC meansoriginal+4',
        'walk freshnext headers fromcapturedhead untilcapturedsentinel;returncandidate onlyif original ANDcandidate each satisfyunsigned H+8<=pointer<next inonesampledheader;otherwise onnormalexhaustion returnoriginal',
        'no stores/calls/frame/retag/free/copy;doesnotcheck blocktag/allocatedstate/remaininglength/exactbase/ownership;no universal listtermination ornonwrappingheader proof'],
      'forwarder_contract':['entryA0=task,entryA1=ID,entryA2=tuplepointer;allocate12B message;null ->1',
        'nonnullQ:U16Q0=00A0,U16Q2=low16ID;tuplepointer nonzero ->bytecopy(Q4,tuple,8),elsefill(Q4,0,8)',
        'sender(savedtask,Q);ignore senderreply;return0. Outputtupleword4 mapsQ8;copiespointerVALUE,doesnotdirectlysavecallerstacktupleaddress. Valid source/destination/copy/normalreturn premises remain',
        'no payloadbody copy/referencecount/release/ack. Newmessage typeA0 differsoriginalff90;senderrejection/cleanup doesnotprove tuplepayload acceptedorfreed'],
      'caller_join':['decoderfailure1+out4zero routesparent toconditionalprivatefree(freshoriginalM8),thenIDhelper;outerhandler maylaterpubliccleanuporiginalM onlyafterparser normalreturn',
        'successfulforwarder0 canmakeparent skipprivatepayloadcleanup;failure1 routescleanup. Tuplepointer mayP+6 whileoriginalM8 remainsP+2;neither is anunconditionalexactbase or ownershipcertificate',
        'otherparsercasehelpers,forwardedmessageconsumer andpendingwrapper stillunclosed;no completepayloadlifetime or actualdelivery claim'],
      'premises':'matching conditionalcandidateISA/source/code;valid normalmemory/control/frame/heap accesses;disjoint liveframes/output/message/source/heap/code asrequired;no adversealias/IRQ/DMA/reentry/writers;normalcalleeprogress andrequiredstate preservation',
      'actual_installed_binding_message_delivery_or_payload_ownership_proved':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage,hexes):
    parent=previous.derive(image,carriers,header,coverage,hexes)
    profiles=[profile(image,d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==660,'decoder-forward byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==250,'decoder-forward instruction census')
    return {'schema':'TSL9-task6-decoder-forward-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'complete_body_bytes':660,'complete_body_instructions':250,'C_reconstruction_coverage_changed':False,
      'remaining':['parser othercasehelpers andforwardedtypeA0 consumer/payloadrelease','dynamicvalidator rowwriters andactualheap/list/pointerretention','actualinstalledprovider,dispatch andobjectlifetime'],
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
    mutations=typed=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);n=decode(raw,STARTS[i][k])
            for p,v in n.items():
                off=p-STARTS[i][k];z=v['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(bad,part,i)
                except RuntimeError:pass
                else:raise RuntimeError('decoder-forward instruction mutation escaped')
                mutations+=1
            for off,f3 in TYPED_LOADS[i][part]:
                bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
                try:body(bad,part,i)
                except RuntimeError as ex:check('typed load encoding' in str(ex),'decoder-forward exact load-type guard')
                else:raise RuntimeError('decoder-forward load-type mutation escaped')
                typed+=1
        raw=bytearray(init.binding.take(data,SOURCES[i][2],56));raw[18:22]=(int.from_bytes(raw[18:22],'little')^(1<<30)).to_bytes(4,'little')
        check(decode(raw,STARTS[i][2])[STARTS[i][2]+18]['op']=='add','decoder-forward wrong-sign regression fixture')
        try:body(raw,'boundsadjust',i)
        except RuntimeError as ex:check('operand boundsadjust' in str(ex),'decoder-forward exact SUB-versus-ADD guard')
        else:raise RuntimeError('decoder-forward wrong-sign mutation escaped')
    check((mutations,typed)==(250,10),'decoder-forward mutation census');domains()
    print('PASS:250 instruction/10 typed-load/2 wrong-sign mutations rejected;type/length/pointer/frame domains;decoder/forwarder DAG paths')


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
    else:check(OUT.read_bytes()==raw,'decoder-forward exact ledger replay')
    print('PASS:660B/250i complete decoder/typevalidator/boundsadjust/forwarder;strict HEX;pointer-minus-delta and tuple8 joins;exact ledger')
    print('PASS:NO target execution/emulation;actual binding,delivery,heap ownership andforwardedpayload lifetime UNPROVED')


if __name__=='__main__':main()


