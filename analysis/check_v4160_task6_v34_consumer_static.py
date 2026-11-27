"""Offline V34 -> task6 receive/parser and allocation-source composition.

Complete original operands/CFG, immutable paths and scalar/interval facts.
No target ISA/register/RAM/heap/queue model, provider, callback or MMIO runs.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_task5_v34_static as previous
import check_v4160_outer_id6_initializer_static as origin
import check_v4160_id6_leaf_return_static as leaf
import check_v4160_message_receive_static as receive

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
OUT=Path(__file__).with_name('v4160-task6-v34-consumer-static.json')
FIELDS={**previous.FIELDS,'xor':('rd','rs1','rs2'),'xori':('rd','rs1','imm')}
BRANCHES=previous.BRANCHES
PARTS=('handler', 'parser')
STARTS=((318450, 319918), (318602, 320070))
SIZES=(218, 226)
COUNTS=(76, 91)
HASHES=(('139cfa5373ff5db62200947565049d00e7422569d4b0001de5f38bb141f02bd3', 'e23e98f6676a46b5f2f35eb963aeaaa8ebfcdd5147831ec245b7006f544a5b3e'), ('f4438b2a870fb83e6a7573ddce8fdab6eb932ea998feadd1f0585ffa2be880af', '6b76ecf7cdece3bdfabd5641696a940a7255fb7dc1c081508bc6025107b771f1'))
TYPED_LOADS=({'handler': ((26, 4), (64, 4), (68, 4), (76, 4), (106, 4), (192, 4), (202, 4)), 'parser': ()}, {'handler': ((26, 4), (64, 4), (68, 4), (76, 4), (106, 4), (192, 4), (202, 4)), 'parser': ()})
LITERALS=(
{
'handler':'''
000 addi 2 2 -16
002 slli 15 11 16
006 store 2 9 4 4
008 store 2 1 12 4
00a store 2 8 8 4
00c store 2 18 0 4
00e srai 15 15 16
010 mv 9 11
012 bge 15 0 174
016 lui 18 536883200
01a load 10 18 788 1
01e auipc 1 536551424
022 jalr 1 1 1660
026 mv 8 10
028 beqz 10 122
02a load 14 10 0 1
02c addi 15 0 144
030 bne 14 15 116
034 load 14 10 1 1
036 li 15 19
038 bne 14 15 170
03c lui 13 536883200
040 load 16 10 2 1
044 load 10 13 507 1
048 lui 14 536883200
04c load 15 14 -94 1
050 addi 12 8 6
054 li 11 0
056 li 13 0
058 addi 14 14 -94
05c mv 17 10
05e bne 16 13 138
062 beqz 11 102
064 store 14 15 0 1
066 load 15 14 0 1
068 beqz 15 116
06a load 10 18 788 1
06e li 11 1
070 jal 1 275786
074 mv 10 8
076 jal 1 274874
07a lui 10 32768
07c xor 10 10 9
07e load 1 2 12 4
080 load 8 2 8 4
082 load 9 2 4 4
084 load 18 2 0 4
086 addi 2 2 16
088 jr 1
08a load 11 12 0 1
08c add 15 15 11
08e andi 11 15 255
092 andi 15 17 255
096 bgeu 11 10 158
09a andi 15 11 255
09e addi 13 13 1
0a0 andi 13 13 255
0a4 addi 12 12 2
0a6 li 11 1
0a8 jump 94
0aa jal 1 319918
0ac jump 116
0ae andi 15 11 1
0b2 li 10 0
0b4 beqz 15 126
0b6 jal 1 321994
0ba beqz 10 212
0bc lui 15 536883200
0c0 load 15 15 -94 1
0c4 beqz 15 212
0c6 lui 15 536883200
0ca load 10 15 788 1
0ce li 11 1
0d0 jal 1 275786
0d4 xori 10 9 1
0d8 jump 126
''',
'parser':'''
000 addi 2 2 -48
002 mv 11 10
004 store 2 8 40 4
006 store 2 9 36 4
008 load 8 10 2 2
00a mv 9 10
00c addi 10 2 24
00e store 2 1 44 4
010 jal 1 319184
014 load 11 2 28 4
016 bnez 11 36
018 bnez 10 126
01a li 11 1
01c mv 10 8
01e jal 1 317794
022 jump 206
024 load 15 2 24 2
026 li 14 5
028 bne 15 14 146
02c load 14 2 26 2
02e li 15 3
030 bgeu 15 14 126
034 addi 10 2 12
036 jal 1 319164
03a load 14 2 14 2
03c li 15 23
03e bgeu 15 14 84
042 load 11 2 13 1
044 lui 15 1507328
048 addi 15 15 1
04a addi 12 2 16
04c mv 10 8
04e store 2 15 16 4
050 jal 1 322870
054 load 15 2 14 2
056 load 14 2 26 2
058 addi 15 15 4
05a beq 14 15 100
05e mv 10 8
060 jal 1 317778
064 load 15 2 12 1
066 load 12 2 28 4
068 addi 11 2 12
06a andi 15 15 1
06c addi 12 12 4
06e mv 10 8
070 beqz 15 140
072 jal 1 319620
076 beqz 10 126
078 mv 10 8
07a jal 1 317778
07e load 10 9 8 4
080 beqz 10 26
082 auipc 1 536551424
086 jalr 1 1 -288
08a jump 26
08c jal 1 319316
090 jump 118
092 li 14 4
094 beq 15 14 166
098 addi 14 15 -6
09c slli 14 14 16
09e srli 14 14 16
0a0 li 13 1
0a2 bltu 13 14 216
0a6 li 14 12
0a8 addi 15 15 -4
0aa mul 15 15 14
0ae lui 14 536883200
0b2 addi 14 14 800
0b6 add 15 15 14
0b8 load 14 15 0 2
0ba beqz 14 126
0bc load 10 15 2 1
0be addi 12 2 24
0c0 mv 11 8
0c2 jal 1 320144
0c4 bnez 10 126
0c6 load 14 2 24 2
0c8 li 15 4
0ca bne 14 15 26
0ce load 1 2 44 4
0d0 load 8 2 40 4
0d2 load 9 2 36 4
0d4 addi 2 2 48
0d6 jr 1
0d8 addi 11 2 24
0da mv 10 8
0dc jal 1 320888
0de bnez 10 126
0e0 jump 206
'''
},
{
'handler':'''
000 addi 2 2 -16
002 slli 15 11 16
006 store 2 9 4 4
008 store 2 1 12 4
00a store 2 8 8 4
00c store 2 18 0 4
00e srai 15 15 16
010 mv 9 11
012 bge 15 0 174
016 lui 18 536883200
01a load 10 18 868 1
01e auipc 1 536551424
022 jalr 1 1 1508
026 mv 8 10
028 beqz 10 122
02a load 14 10 0 1
02c addi 15 0 144
030 bne 14 15 116
034 load 14 10 1 1
036 li 15 19
038 bne 14 15 170
03c lui 13 536883200
040 load 16 10 2 1
044 load 10 13 587 1
048 lui 14 536883200
04c load 15 14 -14 1
050 addi 12 8 6
054 li 11 0
056 li 13 0
058 addi 14 14 -14
05c mv 17 10
05e bne 16 13 138
062 beqz 11 102
064 store 14 15 0 1
066 load 15 14 0 1
068 beqz 15 116
06a load 10 18 868 1
06e li 11 1
070 jal 1 275926
074 mv 10 8
076 jal 1 275014
07a lui 10 32768
07c xor 10 10 9
07e load 1 2 12 4
080 load 8 2 8 4
082 load 9 2 4 4
084 load 18 2 0 4
086 addi 2 2 16
088 jr 1
08a load 11 12 0 1
08c add 15 15 11
08e andi 11 15 255
092 andi 15 17 255
096 bgeu 11 10 158
09a andi 15 11 255
09e addi 13 13 1
0a0 andi 13 13 255
0a4 addi 12 12 2
0a6 li 11 1
0a8 jump 94
0aa jal 1 320070
0ac jump 116
0ae andi 15 11 1
0b2 li 10 0
0b4 beqz 15 126
0b6 jal 1 322146
0ba beqz 10 212
0bc lui 15 536883200
0c0 load 15 15 -14 1
0c4 beqz 15 212
0c6 lui 15 536883200
0ca load 10 15 868 1
0ce li 11 1
0d0 jal 1 275926
0d4 xori 10 9 1
0d8 jump 126
''',
'parser':'''
000 addi 2 2 -48
002 mv 11 10
004 store 2 8 40 4
006 store 2 9 36 4
008 load 8 10 2 2
00a mv 9 10
00c addi 10 2 24
00e store 2 1 44 4
010 jal 1 319336
014 load 11 2 28 4
016 bnez 11 36
018 bnez 10 126
01a li 11 1
01c mv 10 8
01e jal 1 317946
022 jump 206
024 load 15 2 24 2
026 li 14 5
028 bne 15 14 146
02c load 14 2 26 2
02e li 15 3
030 bgeu 15 14 126
034 addi 10 2 12
036 jal 1 319316
03a load 14 2 14 2
03c li 15 23
03e bgeu 15 14 84
042 load 11 2 13 1
044 lui 15 1507328
048 addi 15 15 1
04a addi 12 2 16
04c mv 10 8
04e store 2 15 16 4
050 jal 1 323022
054 load 15 2 14 2
056 load 14 2 26 2
058 addi 15 15 4
05a beq 14 15 100
05e mv 10 8
060 jal 1 317930
064 load 15 2 12 1
066 load 12 2 28 4
068 addi 11 2 12
06a andi 15 15 1
06c addi 12 12 4
06e mv 10 8
070 beqz 15 140
072 jal 1 319772
076 beqz 10 126
078 mv 10 8
07a jal 1 317930
07e load 10 9 8 4
080 beqz 10 26
082 auipc 1 536551424
086 jalr 1 1 -440
08a jump 26
08c jal 1 319468
090 jump 118
092 li 14 4
094 beq 15 14 166
098 addi 14 15 -6
09c slli 14 14 16
09e srli 14 14 16
0a0 li 13 1
0a2 bltu 13 14 216
0a6 li 14 12
0a8 addi 15 15 -4
0aa mul 15 15 14
0ae lui 14 536883200
0b2 addi 14 14 880
0b6 add 15 15 14
0b8 load 14 15 0 2
0ba beqz 14 126
0bc load 10 15 2 1
0be addi 12 2 24
0c0 mv 11 8
0c2 jal 1 320296
0c4 bnez 10 126
0c6 load 14 2 24 2
0c8 li 15 4
0ca bne 14 15 26
0ce load 1 2 44 4
0d0 load 8 2 40 4
0d2 load 9 2 36 4
0d4 addi 2 2 48
0d6 jr 1
0d8 addi 11 2 24
0da mv 10 8
0dc jal 1 321040
0de bnez 10 126
0e0 jump 206
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
    for off,f3 in TYPED_LOADS[index][part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'task6 typed load encoding')
    n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'task6 complete boundaries '+part)
    for p,f in s.items():init.g(n,p,'task6 operand '+part+' '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'task6 complete identity '+part)
    e={};calls=[];returns=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'task6 ordinary RET');qs=[];returns.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':check(v['rd']==1,'task6 linked direct call');calls.append({'offset':p-pc,'target':v['target']})
        elif op=='jalr':
            check(v['rd']==v['rs1']==1 and n[p-4]['op']=='auipc' and n[p-4]['rd']==1,'task6 linked pair')
            calls.append({'offset':p-pc,'target':(p-4+n[p-4]['imm']+v['imm'])&0xfffffffe})
        check(all(q in n for q in qs),'task6 closed local CFG');e[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(e[p])
    check(seen==set(n),'task6 every local node reachable')
    check((len(calls),len(returns))==((6,1) if part=='handler' else (11,1)),'task6 complete call/return census')
    check(common.acyclic(e)==(part=='parser'),'task6 local cycle classification')
    if part=='handler':
        cut={p:list(qs) for p,qs in e.items()};cut[pc+0xa8].remove(pc+0x5e);check(common.acyclic(cut),'task6 only inline byte-count loop')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check(len(stores)==(5 if part=='handler' else 4),'task6 exact store census')
    if part=='parser':check(all(v['base']==2 for v in stores),'task6 parser local writes only own frame')
    return {'start':pc,'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'CFG':e,'calls':calls,'tails':[],
      'returns':returns,'stores':stores,'complete_local_body':True,'actual_progress_or_reachability_proved':False}


def witnesses(handler,parser):
    selected={
      'V34_unchanged_ff90':common.walk(handler,{0x12:0x16,0x28:0x2a,0x30:0x34,0x38:0xaa}),
      'receive_null':common.walk(handler,{0x12:0x16,0x28:0x7a}),
      'no_handled_event':common.walk(handler,{0x12:0xae,0xb4:0x7e}),
      'parser_payload_cleanup':common.walk(parser,{0x16:0x18,0x18:0x7e,0x80:0x82}),
      'parser_null_payload_cleanup':common.walk(parser,{0x16:0x18,0x18:0x7e,0x80:0x1a}),
      'parser_forward_type4_reply0':common.walk(parser,{0x16:0x24,0x28:0x92,0x94:0xa6,0xba:0xbc,0xc4:0xc6,0xca:0xce})}
    s=selected['V34_unchanged_ff90']
    check(s.index(0xaa)<s.index(0x74)<s.index(0x76)<s.index(0x7c) and 0x3c not in s,'task6 ff90 parser before outer message cleanup/XOR')
    check(0x76 not in selected['receive_null'],'task6 null receive skips message cleanup')
    s=selected['parser_payload_cleanup'];check(s.index(0x7e)<s.index(0x86)<s.index(0x1e),'task6 fresh original payload release then ID helper')
    check(0x86 not in selected['parser_null_payload_cleanup'] and 0x86 not in selected['parser_forward_type4_reply0'],'task6 conditional payload cleanup bypasses')
    paths=previous.allocation.previous.dag_paths(parser);cleanup=sum(0x86 in s for s in paths)
    check(cleanup>0 and cleanup<len(paths),'task6 parser direct release is conditional across full local DAG')
    return {'selected_syntactic_paths':selected,'parser_DAG_path_count':len(paths),'paths_with_direct_private_release':cleanup,
      'paths_without_direct_private_release':len(paths)-cleanup,'parser_paths_sha256':sha256(json.dumps(paths,separators=(',',':')).encode()).hexdigest(),
      'path_feasibility_callee_frame_outputs_or_ownership_proved':False}


def domains():
    for E in range(65536):
        signed=E if E<32768 else E-65536
        check((signed<0)==bool(E&0x8000),'task6 signed-half event priority')
        if E&0x8000:check((E^0x8000)==E-0x8000,'task6 message event XOR')
        elif E&1:check((E^1)==E-1,'task6 bit0 event XOR')
    for E in (0x18001,0xffff8000,0x80010001,0xffffffff):
        reply=E^0x8000 if E&0x8000 else E^1 if E&1 else 0
        check(reply&0xffff0000==E&0xffff0000,'task6 high reply bits retained on selected handled-bit paths')
    check(0x8000&0x8001 and (0x8001^0x8000)==1 and 0x10000&0x8001==0,'task6 priority and no-handled-bit distinction')
    for old in range(256):
        for part in range(256):check(((old+part)&255)==(old+part)%256,'task6 inline addition wraps before cap')
    for total in range(511):
        low=total&255
        for cap in range(256):check((cap if low>=cap else low)==min(low,cap),'task6 inline byte clamp')
    check(min((255+1)&255,255)==0 and min(255+1,255)==255,'task6 reject saturating-add substitution')
    for count in range(256):
        check(count<256,'task6 count loop cannot wrap before terminal equality')
        if count:check(6+2*(count-1)+1==2*count+5<=515,'task6 byte-stride footprint, not halfword loads')
    # Exact row geometry over every U16 ID and representative capacities;
    # arbitrary U8 capacities follow the same integer inequality.
    for capacity in (0,1,5,66,255):
        for identity in range(65536):
            offset=12*((identity-1)&65535)
            check((offset+12<=12*capacity)==(1<=identity<=capacity),'task6 V34 full-row bound')
    for capacity in range(256):
        check((12*capacity)&65535==12*capacity and (12*capacity+3)&~3==12*capacity,'task6 array request no truncation/round change')
        check(0<=12*capacity<=3060,'task6 getter capacity extent')
    q=(14&3)+(14>>2);check(q==5 and 12*q==60 and 60*q==300,'task6 record array differs resource pool')
    return {'event_halfword_cases':65536,'inline_add_cases':65536,'inline_cap_cases':511*256,'inline_count_cases':256,
      'full_ID_capacity_cases':65536*5,'capacities':[0,1,5,66,255],'getter_cases':256,
      'record_extent_rule':'allocated minimum12*g1;fill12*g2;g2<=g1 is sufficient fill-length bound onlywithvalidnonaliasallocatedpointer;consumer full-row bound1<=U16I<=g1',
      'retained_APP_source_case':{'byte21':14,'q':5,'record_array_bytes':60,'separate_resource_pool_bytes':300,'row_IDs':[1,5]},
      'counter_rule':'after each inline byte: min((previous_byte+U8[M+6+2*i])&255,capturedcap);not saturating addition',
      'actual_getter_retention_or_index_identity_or_memory_safety_proved':False}


def profile(image,data,hexraw,index,parent):
    bs={p:body(init.binding.take(data,STARTS[index][k],SIZES[k]),p,index) for k,p in enumerate(PARTS)}
    h,p=bs['handler'],bs['parser'];hp,pp=STARTS[index];hn={v['pc']-hp:v for v in h['instructions']};pn={v['pc']-pp:v for v in p['instructions']}
    event=common.previous.consumer.DETAILS[index][1];publicfree=common.dealloc.DETAILS[index][0]
    check([(c['offset'],c['target']) for c in h['calls']]==[(0x22,0x2000028c),(0x70,event),(0x76,publicfree),(0xaa,pp),(0xb6,0x4e9ca+152*index),(0xd0,event)],'task6 complete handler target census')
    targets=(0x4ded0,0x4d962,0x4debc,0x4ed36,0x4d952,0x4e084,0x4d952,0x20000110,0x4df54,0x4e290,0x4e578)
    expected=[(o,t if t==0x20000110 else t+152*index) for o,t in zip((0x10,0x1e,0x36,0x50,0x60,0x72,0x7a,0x86,0x8c,0xc2,0xdc),targets)]
    check([(c['offset'],c['target']) for c in p['calls']]==expected,'task6 complete parser target census')
    G=0x20003000;task=0x20003314+80*index;array=task+4;counter=0x20002fa2+80*index;cap=0x200031fb+80*index
    check(hn[0x1a]['imm']+G==hn[0x6a]['imm']+G==hn[0xca]['imm']+G==task,'task6 receive/repost uses same fresh task slot')
    check(hn[0x4c]['imm']+G==hn[0xc0]['imm']+G==counter and counter!=parent['roles']['credit_byte'],'task6 inline counter is distinct from V34 tag8001 credit')
    check(hn[0x44]['imm']+G==cap and hn[0x8a]['width']==1 and hn[0xa4]['imm']==2,'task6 inline cap and byte-at-stride2')
    check(hn[0x2c]['imm']==0x90 and hn[0x36]['imm']==19 and 0xff!=19,'task6 unchanged V34 statusFF routes general parser')
    check(pn[0x7e]['op']=='load' and pn[0x7e]['rd']==10 and pn[0x7e]['rs1']==9 and pn[0x7e]['imm']==8,'task6 parser fresh original M8 payload argument')
    check(pn[0x80]['target']==pp+0x1a and pn[0x8a]['target']==pp+0x1a,'task6 cleanup rejoins ID helper and returns')
    check(not any(v.get('rd')==10 for o,v in pn.items() if 0x7e<o<0x86),'task6 direct private release takes fresh original pointer unchanged')
    check(not any(v['op'] in ('load','store') and v.get('rs1')==8 for o,v in hn.items() if o>0x76),'task6 no local M dereference after public cleanup')
    # Original task/array producers are old complete contracts, not new bytes.
    ip=origin.STARTS[index][0];ib=origin.body(init.binding.take(data,ip,386),'initializer',index);inn={v['pc']-ip:v for v in ib['instructions']}
    rb=origin.body(init.binding.take(data,origin.STARTS[index][1],160),'resources',index)
    gp=0x4efd8+152*index;gb=leaf.body(init.binding.take(data,gp,10),'getter',index)
    check(inn[72]['rs2']==10 and inn[72]['imm']==12 and inn[98]['rd']==10 and inn[98]['imm']==12 and inn[108]['imm']+G==task,'task6 saved incoming registration ID publish')
    check(inn[276]['target']==inn[316]['target']==gp and inn[308]['imm']+G==array and inn[314]['rs1']==10,'task6 getter/array publication before null guard and fill')
    check(inn[288]['imm']+0x5000==0x4c06 and inn[280]['imm']==inn[320]['imm']==12,'task6 array tag and separate getter extents')
    role=origin.previous.role;entry,rs=role.specs('entry',index)
    check(rs[entry+8]['imm']+rs[entry+12]['imm']==hp and rs[entry+20]['target']==ip,'task6 outer handler registration differs internal callback')
    check(hp!=0x4d916+152*index,'task6 distinct internal callback address')
    check(parent['roles']['outgoing_task_byte']==task and parent['roles']['record_array_pointer']==array,'task6 V34 producer role joins')
    rn=receive.body(init.binding.take(data,receive.SOURCES[index][0],136),'receive',index)
    pubraw=init.binding.take(data,publicfree,78);check(sha256(pubraw).hexdigest()==common.dealloc.DETAILS[index][-2],'task6 exact public cleanup reuse')
    fn,_=common.previous.free_body(init.binding.take(data,common.previous.release.DETAILS[index][0],212),index)
    for o in (0x70,0xd0):check(hn[o-2]['op']=='li' and hn[o-2]['imm']==1,'task6 event repost mask1')
    _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
    for part,b in bs.items():
        check(sparse.captured(mem,b['start'],b['bytes'])==init.binding.take(data,b['start'],b['bytes']),'task6 original strict HEX backing')
        receipts.append({'part':part,'source':b['start'],'bytes':b['bytes'],'all_bytes_captured':True})
    return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,
      'CFG_certificates':{k:common.certificates(b) for k,b in bs.items()},'witnesses':witnesses(h,p),
      'roles':{'task_byte':task,'record_array_pointer':array,'inline_counter_byte':counter,'inline_cap_byte':cap},
      'origin_reuse':{'initializer_start':ip,'initializer_sha256':ib['sha256'],'resource_sha256':rb['sha256'],'getter_sha256':gb['sha256'],
        'task_publish_PC':ip+108,'array_publish_PC':ip+308,'registered_handler':hp,'internal_callback':0x4d916+152*index,'new_code_bytes_counted':0},
      'receive_cleanup_reuse':{'receive_target':0x2000028c,'receive_sha256':rn['sha256'],'public_message_cleanup':publicfree,'public_cleanup_sha256':sha256(pubraw).hexdigest(),'private_payload_cleanup':0x20000110},
      'binding_contract':'if prior selected registration6/count7/table/frame/state retained,entry6 ishandler;initializer reloadssaved incoming ID andpublisheslow8 toV34/receiver/repost taskslot. Reposting and matching fresh task do not prove actual dispatch/delivery',
      'array_contract':'core(12*g1,4c06),publisharrayresult before nullcheck/fill;nonnull then getterg2 andfill12*g2. g1/g2 freshU8 independently0..255;APPbyte21=14 givesq5 onlywithretention;12qrecordarray differs60qresourcepool',
      'handler_contract':['messageevent bit15 haspriority;freshsavedtask ->receive;null skipscleanup;nonnullM saved,byteM0!=90 skipsparser;byteM0=90,byteM1!=19 callsparser(M)',
        'all normalnonnull-message paths callpubliccleanup(originalM) after selectedparser/inlinepath,ignorecleanup scalarreply;returnfull entryE XOR8000,not maskedU16',
        'status19 inline:N=U8M2,cap=freshcapturedU8 capslot,counter=freshcapturedbyte;repeatN times U8[M6+2i],addmod256 thencapmin. N0 no counterstore;N>0 finalbyte store. Freshpostloopcounter!=0 ->event(freshtask,1)',
        'withoutbit15,bit0 ->pendingwrapper;nonzero reply andfreshcounter!=0 ->event(freshtask,1);returnfullE XOR1;neitherhandledbit ->0'],
      'parser_contract':['cacheU16M2 inS0,originalM inS1;calldecoder(SP24,M);freshSP28nonzero routesbyfreshhalfSP24;SP28zero+decoderreply0 callsIDhelper(ID,1) thenreturns;nonzero reply goescleanup',
        'multiple case callees andforwarders remain opaque;type4/6/7 use12-byte routing rowsG800/880,distinctfromV34recordarrayG792/872;forwarder reply0 canreturnwithoutdirectpayloadrelease',
        'cleanup:freshU32[originalM8] ->ifnonnull privatefree(pointer) unchanged,thenIDhelper(ID,1). Thisisoriginalmessagepointerfield,notdecoder outputSP28;no local M8clear or recursive release',
        'localstores onlyframe;11callees useassumed normalreturn/preservation edges,notcompletednestedclosure. Stacktuple outputs,case semantics andpayloadretention awaitcalleeproofs'],
      'lifetime_contract':'unchangedV34ff90 andconditionalacceptedqueue/taskbinding routegeneralparser thenouterpublicmessagecleanup. Someparserpaths attemptprivatepayloadrelease,othersdo not. V34 P+2 interiorpointer canbeacceptedonlyundercontainingheader/extent/ownershippremises. Neitherbranch certifies actualrelease,exclusiveforwardingorcompletepayloadlifetime',
      'premises':'matching captured candidate/conditionalISA/code andvalid source/frame/global/heap/message/accesses;normalcallee S/SP/RA/frame preservation;freshpointer/value identity requiresretention;no adverse alias/IRQ/DMA/reentry/unaccounted writers',
      'actual_installed_binding_dispatch_all_writers_or_payload_lifetime_proved':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage,hexes):
    parent=previous.derive(image,carriers,header,coverage,hexes)
    profiles=[profile(image,d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==888,'task6 new body byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==334,'task6 new body instruction census')
    return {'schema':'TSL9-task6-v34-consumer-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'complete_body_bytes':888,'complete_body_instructions':334,'C_reconstruction_coverage_changed':False,
      'remaining':['decoder132B and bounds-adjust56B contracts','parser case helpers/forwarders,pendingwrapper and payload handoff','actual task/provider binding,all writers and object/heap lifetime'],
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
    mutations=typed=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,STARTS[i][k],SIZES[k]);n=decode(raw,STARTS[i][k])
            for p,v in n.items():
                off=p-STARTS[i][k];z=v['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(bad,part,i)
                except RuntimeError:pass
                else:raise RuntimeError('task6 instruction mutation escaped')
                mutations+=1
            for off,f3 in TYPED_LOADS[i][part]:
                bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
                try:body(bad,part,i)
                except RuntimeError as ex:check('typed load encoding' in str(ex),'task6 exact load-type guard')
                else:raise RuntimeError('task6 signed load mutation escaped')
                typed+=1
    check((mutations,typed)==(334,14),'task6 mutation census');domains()
    print('PASS:334 instruction/14 typed-load mutations rejected;event/counter/record-extent scalar domains;selected consumer/cleanup paths')


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
    else:check(OUT.read_bytes()==raw,'task6 exact ledger replay')
    print('PASS:888B/334i complete task6 handler/parser;strict HEX;V34 task/array sources and conditional payload-cleanup joins;exact ledger')
    print('PASS:NO target execution/emulation;actual dispatch,case callees,forwarded payload lifetime and provider binding UNPROVED')


if __name__=='__main__':main()


