"""Offline code4 routing and complete task8 typeA0 consumer contracts.

Original operand/CFG, immutable paths and host scalar/interval equations only.
No target ISA, register/RAM/heap/queue model, callbacks or MMIO executes.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_task6_decoder_forward_static as previous
import check_v4160_id8_initialization_static as route8
import check_v4160_id9_vector_dispatch_static as route9

init,sparse,check=previous.init,previous.sparse,previous.check
common=previous.common
v34=previous.previous.previous
OUT=Path(__file__).with_name('v4160-task8-typea0-static.json')
FIELDS={**previous.FIELDS,'call_indirect':('rd','rs1')}
BRANCHES=previous.BRANCHES
def decode(raw,pc):
 out={};off=0
 while off<len(raw):
  z=2 if int.from_bytes(raw[off:off+2],'little')&3!=3 else 4;chunk=raw[off:off+z];check(len(chunk)==z,'task8 complete instruction');w=int.from_bytes(chunk,'little');p=pc+off
  if z==4 and w&0xfe00707f==0x4033:d=dict(pc=p,bytes=chunk.hex(),size=4,op='xor',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
  else:d=previous.decode(chunk,p)[p]
  out[p]=d;off+=z
 return out


PARTS=('handler', 'decoder')
STARTS=((305160, 280222), (305312, 280370))
SIZES=(312, 140)
COUNTS=(111, 56)
HASHES=(('e035daca2b9ceac4912133f3831b4a941ac722a39e28f934a161308d2b98cbac', 'f6af339e5d52c8f1a7c7e6669e765247cc67a29c31e99e1aabf849cf52452928'), ('87750b1d1e9ad294686a7e608f511cfe2cf5a6df96d2256f2a499804ee755ede', '060768024df2abf96e206fe55c7f5307e4c61265fa8a680e30c30cee5484f278'))
TYPED_LOADS=({'handler': ((26, 4), (68, 4), (102, 2), (164, 4), (232, 2), (238, 4), (270, 2), (290, 4), (296, 4)), 'decoder': ((16, 2), (24, 4), (52, 5))}, {'handler': ((26, 4), (68, 4), (102, 2), (164, 4), (232, 2), (238, 4), (270, 2), (290, 4), (296, 4)), 'decoder': ((16, 2), (24, 4), (52, 5))})
LITERALS=(
{
'handler':'''
000 addi 2 2 -48
002 slli 15 11 16
006 store 2 18 32 4
008 store 2 1 44 4
00a store 2 8 40 4
00c store 2 9 36 4
00e srai 15 15 16
010 li 18 0
012 bge 15 0 200
016 lui 15 536883200
01a load 10 15 941 1
01e mv 18 11
020 auipc 1 536567808
024 jalr 1 1 -1436
028 mv 8 10
02a beqz 10 194
02c load 14 10 0 1
02e addi 15 0 160
032 bne 14 15 188
036 li 15 1
038 addi 11 2 20
03a store 2 15 11 1
03c jal 1 280222
040 mv 9 10
042 bnez 10 122
044 load 15 2 22 1
048 li 14 28
04a bgeu 14 15 214
04e addi 14 15 -31
052 andi 14 14 255
056 addi 13 0 32
05a bgeu 13 14 228
05e andi 15 15 1
060 beqz 15 266
062 lui 15 536883200
066 load 15 15 -148 4
06a li 9 6
06c beqz 15 122
06e load 10 8 2 2
070 addi 12 2 11
074 addi 11 2 20
076 call_indirect 1 15
078 mv 9 10
07a load 15 2 11 1
07c beqz 15 138
07e load 10 8 8 4
080 beqz 10 138
082 auipc 1 536567808
086 jalr 1 1 -1914
08a bnez 9 174
08c load 14 2 20 4
08e lui 15 16777216
092 addi 15 15 -256
096 and 14 14 15
098 lui 15 1179648
09c addi 15 15 256
0a0 beq 14 15 188
0a4 load 14 2 22 1
0a8 li 15 27
0aa bne 14 15 188
0ae load 10 8 2 2
0b0 li 11 1
0b2 jal 1 317794
0b6 li 15 19
0b8 beq 9 15 200
0bc mv 10 8
0be jal 1 274874
0c2 lui 15 32768
0c4 xor 18 18 15
0c8 load 1 2 44 4
0ca load 8 2 40 4
0cc mv 10 18
0ce load 9 2 36 4
0d0 load 18 2 32 4
0d2 addi 2 2 48
0d4 jr 1
0d6 lui 14 338690048
0da addi 14 14 1
0dc srl 14 14 15
0e0 andi 14 14 1
0e2 beqz 14 94
0e4 lui 14 536883200
0e8 load 14 14 -144 4
0ec beqz 14 122
0ee load 14 2 21 1
0f2 bnez 14 122
0f4 store 2 15 12 1
0f6 li 15 6
0f8 store 2 15 16 1
0fc load 10 8 2 2
0fe addi 11 2 12
100 store 2 0 14 2
104 jal 1 280780
108 jump 122
10a lui 15 536883200
10e load 15 15 -144 4
112 beqz 15 308
114 load 10 8 2 2
116 addi 12 2 11
11a addi 11 2 20
11c call_indirect 1 15
11e beqz 10 122
120 mv 9 10
122 load 15 2 21 1
126 bnez 15 122
128 load 15 2 22 1
12c store 2 9 16 1
130 store 2 15 12 1
132 jump 252
134 li 9 6
136 jump 290
''',
'decoder':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 load 8 10 6 2
006 store 2 1 28 4
008 store 2 9 20 4
00a store 2 18 16 4
00c store 2 19 12 4
00e beqz 8 136
010 load 19 10 8 4
014 mv 9 11
016 mv 16 10
018 load 18 19 0 1
01c li 15 0
01e slli 14 18 24
022 srai 14 14 24
024 bge 14 0 78
028 li 15 12
02a li 10 1
02c bgeu 15 8 122
030 addi 8 8 -12
032 slli 8 8 16
034 load 10 16 2 2
038 srli 8 8 16
03a add 14 19 8
03e mv 13 8
040 mv 12 19
042 li 11 1
044 jal 1 328032
048 sltu 15 0 10
04c addi 15 15 1
04e addi 8 8 -1
050 srli 10 18 6
054 slli 8 8 16
056 andi 10 10 1
058 andi 18 18 63
05c srli 8 8 16
05e store 9 15 0 1
060 store 9 10 1 1
062 store 9 18 2 1
066 store 9 8 4 2
068 li 14 0
06a beqz 8 112
06c addi 14 19 1
070 store 9 14 8 4
072 li 14 2
074 beq 15 14 122
078 li 10 0
07a load 1 2 28 4
07c load 8 2 24 4
07e load 9 2 20 4
080 load 18 2 16 4
082 load 19 2 12 4
084 addi 2 2 32
086 jr 1
088 li 10 1
08a jump 122
'''
},
{
'handler':'''
000 addi 2 2 -48
002 slli 15 11 16
006 store 2 18 32 4
008 store 2 1 44 4
00a store 2 8 40 4
00c store 2 9 36 4
00e srai 15 15 16
010 li 18 0
012 bge 15 0 200
016 lui 15 536883200
01a load 10 15 1021 1
01e mv 18 11
020 auipc 1 536567808
024 jalr 1 1 -1588
028 mv 8 10
02a beqz 10 194
02c load 14 10 0 1
02e addi 15 0 160
032 bne 14 15 188
036 li 15 1
038 addi 11 2 20
03a store 2 15 11 1
03c jal 1 280370
040 mv 9 10
042 bnez 10 122
044 load 15 2 22 1
048 li 14 28
04a bgeu 14 15 214
04e addi 14 15 -31
052 andi 14 14 255
056 addi 13 0 32
05a bgeu 13 14 228
05e andi 15 15 1
060 beqz 15 266
062 lui 15 536883200
066 load 15 15 -68 4
06a li 9 6
06c beqz 15 122
06e load 10 8 2 2
070 addi 12 2 11
074 addi 11 2 20
076 call_indirect 1 15
078 mv 9 10
07a load 15 2 11 1
07c beqz 15 138
07e load 10 8 8 4
080 beqz 10 138
082 auipc 1 536563712
086 jalr 1 1 2030
08a bnez 9 174
08c load 14 2 20 4
08e lui 15 16777216
092 addi 15 15 -256
096 and 14 14 15
098 lui 15 1179648
09c addi 15 15 256
0a0 beq 14 15 188
0a4 load 14 2 22 1
0a8 li 15 27
0aa bne 14 15 188
0ae load 10 8 2 2
0b0 li 11 1
0b2 jal 1 317946
0b6 li 15 19
0b8 beq 9 15 200
0bc mv 10 8
0be jal 1 275014
0c2 lui 15 32768
0c4 xor 18 18 15
0c8 load 1 2 44 4
0ca load 8 2 40 4
0cc mv 10 18
0ce load 9 2 36 4
0d0 load 18 2 32 4
0d2 addi 2 2 48
0d4 jr 1
0d6 lui 14 338690048
0da addi 14 14 1
0dc srl 14 14 15
0e0 andi 14 14 1
0e2 beqz 14 94
0e4 lui 14 536883200
0e8 load 14 14 -64 4
0ec beqz 14 122
0ee load 14 2 21 1
0f2 bnez 14 122
0f4 store 2 15 12 1
0f6 li 15 6
0f8 store 2 15 16 1
0fc load 10 8 2 2
0fe addi 11 2 12
100 store 2 0 14 2
104 jal 1 280928
108 jump 122
10a lui 15 536883200
10e load 15 15 -64 4
112 beqz 15 308
114 load 10 8 2 2
116 addi 12 2 11
11a addi 11 2 20
11c call_indirect 1 15
11e beqz 10 122
120 mv 9 10
122 load 15 2 21 1
126 bnez 15 122
128 load 15 2 22 1
12c store 2 9 16 1
130 store 2 15 12 1
132 jump 252
134 li 9 6
136 jump 290
''',
'decoder':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 load 8 10 6 2
006 store 2 1 28 4
008 store 2 9 20 4
00a store 2 18 16 4
00c store 2 19 12 4
00e beqz 8 136
010 load 19 10 8 4
014 mv 9 11
016 mv 16 10
018 load 18 19 0 1
01c li 15 0
01e slli 14 18 24
022 srai 14 14 24
024 bge 14 0 78
028 li 15 12
02a li 10 1
02c bgeu 15 8 122
030 addi 8 8 -12
032 slli 8 8 16
034 load 10 16 2 2
038 srli 8 8 16
03a add 14 19 8
03e mv 13 8
040 mv 12 19
042 li 11 1
044 jal 1 328186
048 sltu 15 0 10
04c addi 15 15 1
04e addi 8 8 -1
050 srli 10 18 6
054 slli 8 8 16
056 andi 10 10 1
058 andi 18 18 63
05c srli 8 8 16
05e store 9 15 0 1
060 store 9 10 1 1
062 store 9 18 2 1
066 store 9 8 4 2
068 li 14 0
06a beqz 8 112
06c addi 14 19 1
070 store 9 14 8 4
072 li 14 2
074 beq 15 14 122
078 li 10 0
07a load 1 2 28 4
07c load 8 2 24 4
07e load 9 2 20 4
080 load 18 2 16 4
082 load 19 2 12 4
084 addi 2 2 32
086 jr 1
088 li 10 1
08a jump 122
'''
}
)

def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'task8 literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=pc
        out[pc+int(off,16)]=f
    return out


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    for off,f3 in TYPED_LOADS[index][part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'task8 typed load encoding')
    n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'task8 complete boundaries '+part)
    for p,f in s.items():init.g(n,p,'task8 operand '+part+' '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'task8 complete identity '+part)
    e={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'task8 ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':check(v['rd']==1,'task8 linked direct call');calls.append({'offset':p-pc,'target':v['target']})
        elif op=='jalr':
            check(v['rd']==v['rs1']==1 and n[p-4]['op']=='auipc' and n[p-4]['rd']==1,'task8 linked pair')
            calls.append({'offset':p-pc,'target':(p-4+n[p-4]['imm']+v['imm'])&0xfffffffe})
        elif op=='call_indirect':
            check(v['rd']==1 and v['rs1']==15,'task8 linked callback');calls.append({'offset':p-pc,'target':'then-live X15 & ~1','indirect':True})
        check(all(q in n for q in qs),'task8 closed local CFG');e[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(e[p])
    check(seen==set(n) and common.acyclic(e),'task8 complete local DAG')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(calls),len(rets),len(stores))==((8,1,10) if part=='handler' else (1,1,10)),'task8 exact call/return/store census')
    if part=='handler':check(all(v['base']==2 for v in stores),'task8 handler own-frame stores only')
    return {'start':pc,'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'CFG':e,'calls':calls,'tails':[],
      'returns':rets,'stores':stores,'complete_local_body':True,'actual_call_progress_or_ownership_proved':False}


def witnesses(handler,decoder):
    common_entry={0x12:0x16,0x2a:0x2c,0x32:0x36}
    callback={**common_entry,0x42:0x44,0x4a:0x4e,0x5a:0x5e,0x60:0x62,0x6c:0x6e}
    selected={
      'no_bit15':common.walk(handler,{0x12:0xc8}),
      'receive_null':common.walk(handler,{0x12:0x16,0x2a:0xc2}),
      'other_message_type':common.walk(handler,{0x12:0x16,0x2a:0x2c,0x32:0xbc}),
      'decoder_failure_flag1_payloadnonnull':common.walk(handler,{**common_entry,0x42:0x7a,0x7c:0x7e,0x80:0x82,0x8a:0xae,0xb8:0xbc}),
      'callback_status19_flag0':common.walk(handler,{**callback,0x7c:0x8a,0x8a:0xae,0xb8:0xc8}),
      'callback_status19_flag1':common.walk(handler,{**callback,0x7c:0x7e,0x80:0x82,0x8a:0xae,0xb8:0xc8})}
    check(0xbe not in selected['callback_status19_flag0'] and 0xc4 not in selected['callback_status19_flag0'],'task8 status19 skips message cleanup and event XOR')
    check(0x86 not in selected['callback_status19_flag0'] and 0x86 in selected['callback_status19_flag1'],'task8 callback releaseflag controls private payload cleanup independently')
    check(0x76 in selected['callback_status19_flag0'] and 0x78 in selected['callback_status19_flag0'],'task8 selected status19 witness captures callback reply')
    check(0x44 not in selected['decoder_failure_flag1_payloadnonnull'],'task8 failure skips uninitialized tuple interpretation')
    s=selected['decoder_failure_flag1_payloadnonnull'];check(s.index(0x86)<s.index(0xb2)<s.index(0xbe)<s.index(0xc4),'task8 failure cleanup and normal event return order')
    hs=v34.allocation.previous.dag_paths(handler)
    ds=v34.allocation.previous.dag_paths(decoder)
    dn={v['pc']-decoder['start']:v for v in decoder['instructions']}
    for seq in ds:
        last=dn[[o for o in seq if dn[o].get('rd')==10][-1]]
        check(last['op']=='li' and last['imm'] in (0,1) or last['op']=='andi' and last['imm']==1,'task8 decoder normal replies bounded0/1')
        writes=[o for o in seq if dn[o]['op']=='store' and dn[o]['rs1']==9]
        check(writes==[0x5e,0x60,0x62,0x66,0x70] if writes else 0x2a in seq or 0x88 in seq,'task8 decoder all-or-no local output fields')
    return {'selected_handler_paths':selected,'handler_syntactic_DAG_paths':len(hs),'decoder_syntactic_DAG_paths':len(ds),
      'handler_paths_with_private_payload_call':sum(0x86 in s for s in hs),'handler_paths_with_public_message_call':sum(0xbe in s for s in hs),
      'path_hashes':{'handler':sha256(json.dumps(hs,separators=(',',':')).encode()).hexdigest(),'decoder':sha256(json.dumps(ds,separators=(',',':')).encode()).hexdigest()},
      'path_feasibility_callback_outputs_or_ownership_proved':False}


def domains():
    for low in range(65536):
        signed=low if low<32768 else low-65536
        check((signed<0)==bool(low&0x8000),'task8 event signed low-half test')
        if low&0x8000:check((low^0x8000)==low-0x8000,'task8 ordinary message return clears selected bit')
    for E in (0x8001,0x18000,0xffff8001):check(E!=E^0x8000 and ((E^0x8000)&0xffff0000)==E&0xffff0000,'task8 unchanged versus XOR full32 replies')
    for length in range(65536):
        if length:
            check(0<=length-1<=65534,'task8 nonextended body length')
        if length>12:
            check((length-12-1)&65535==length-13 and 1+(length-13)==length-12,'task8 extended strips one prefix plus12 trailing bytes')
    for byte in range(256):
        flag=byte>>6&1;opcode=byte&63
        check(0<=opcode<=63 and flag in (0,1),'task8 decoded byte fields')
        for reply_nonzero in (False,True):
            status=1+int(reply_nonzero)
            reply=flag if status==2 else 0
            check(reply in (0,1) and (reply==1)==(reply_nonzero and flag==1),'task8 helper result is not forwarded as decoder reply')
    mask=0x14300001;special_low=[i for i in range(29) if mask>>i&1]
    check(special_low==[0,20,21,26,28],'task8 fixed opcode bitmask members')
    for opcode in range(64):
        special=(opcode<=28 and bool(mask>>opcode&1)) or ((opcode-31)&255)<=32
        check(special==(opcode in set(special_low)|set(range(31,64))),'task8 initial opcode range classification')
    for code in range(4,8):
        offset=12*(code-4);check(0<=offset and offset+3<=48,'task8 actual constant-code route writes inside48B')
    sample=0x10004;d=(sample-4)&0xffffffff
    check((d&65535)<=3 and 12*d!=12*(d&65535),'task8 generic selector truncation cannot justify48B table bound')
    writes={0,1,2,4,5,8,9,10,11};check(set(range(12))-writes=={3,6,7},'task8 decoder output partial initialization')
    protected=set(range(32,48));outputs={11}|set(range(20,32))
    child=set(range(-20,0));check(not protected&outputs and not child&outputs,'task8 saved frame excludes borrowed flag/tuple and child saves')
    return {'event_U16_cases':65536,'length_U16_cases':65536,'first_byte_helper_reply_cases':512,'decoded_opcode_cases':64,
      'bitmask_opcodes':special_low,'additional_special_opcodes':[31,63],'output_bytes_written':sorted(writes),'output_bytes_not_written':[3,6,7],
      'normal_reply_rule':'no bit15 ->0; ordinary message paths ->fullE XOR8000; status19 afterIDhelper ->fullE withmessagecleanup skipped',
      'decoder_rule':'L0 ->1,no output;nonextendedL>0 ->bodyL-1/status0/reply0;extendedL<=12 ->1,no output;extendedL>12 ->bodyL-13,status1+(auxreply!=0),reply=(bit6 ifstatus2 else0)',
      'actual_route_publication_callback_status_or_payload_extent_proved':False}


def profile(image,data,hexraw,index,parent):
    bs={p:body(init.binding.take(data,STARTS[index][k],SIZES[k]),p,index) for k,p in enumerate(PARTS)}
    h,d=bs['handler'],bs['decoder'];hp,dp=STARTS[index];hn={v['pc']-hp:v for v in h['instructions']};dn={v['pc']-dp:v for v in d['instructions']}
    public=common.dealloc.DETAILS[index][0];idhelper=0x4d962+152*index;report=0x448cc+148*index;aux=(0x50160,0x501fa)[index]
    check(h['calls']==[{'offset':0x24,'target':0x2000028c},{'offset':0x3c,'target':dp},{'offset':0x76,'target':'then-live X15 & ~1','indirect':True},
      {'offset':0x86,'target':0x20000110},{'offset':0xb2,'target':idhelper},{'offset':0xbe,'target':public},
      {'offset':0x104,'target':report},{'offset':0x11c,'target':'then-live X15 & ~1','indirect':True}],'task8 complete call census')
    check(d['calls']==[{'offset':0x44,'target':aux}],'task8 decoder auxiliary target, version-specific delta')
    check(hn[0x3a]['rs1']==2 and hn[0x3a]['imm']==11 and hn[0x36]['imm']==1,'task8 initializes releaseflag before decoder')
    check(hn[0x7a]['imm']==11 and hn[0x7e]['imm']==8 and hn[0x7e]['rd']==10 and hn[0x7e]['rs1']==8,'task8 fresh flag/originalM8 private release')
    check(hn[0x70]['imm']==hn[0x116]['imm']==11 and hn[0x74]['imm']==hn[0x11a]['imm']==20,'task8 callbacks borrow flag and tuple pointers')
    check(hn[0xb6]['imm']==19 and hn[0xb8]['target']==hp+0xc8 and hn[0xc4]['op']=='xor','task8 status19 skips both cleanup and XOR')
    check(dn[4]['imm']==6 and dn[0x10]['imm']==8 and dn[0x18]['rs1']==19,'task8 captured length then payload byte')
    check(dn[0x30]['imm']==-12 and dn[0x4e]['imm']==-1 and dn[0x6c]['imm']==1,'task8 body suffix/prefix arithmetic')
    check(dn[0x48]['op']=='sltu' and dn[0x48]['rs1']==0 and dn[0x48]['rs2']==10 and dn[0x4c]['imm']==1,'task8 status from auxiliary zero/nonzero')
    check(dn[0x56]['imm']==1 and dn[0x58]['imm']==63 and dn[0x74]['target']==dp+0x7a,'task8 decoder bit6/opcode/status2 return selection')
    G=0x20003000;task=G+941+80*index;odd=G-148+80*index;other=G-144+80*index
    check(hn[0x1a]['imm']+G==task and hn[0x66]['imm']+G==odd and hn[0xe8]['imm']+G==hn[0x10e]['imm']+G==other,'task8 distinct task and callback source slots')
    # Existing initializer and selector source proofs; no new coverage here.
    ib=route8.body(init.binding.take(data,route8.STARTS[index][0],50),'initializer',index);ip=route8.STARTS[index][0];inn={v['pc']-ip:v for v in ib['instructions']}
    selector=route8.previous;sp=selector.STARTS[index][5];sb=selector.body(init.binding.take(data,sp,44),'selector',index);sn={v['pc']-sp:v for v in sb['instructions']}
    check(inn[28]['imm']==4 and inn[34]['imm']+G==task and inn[38]['target']==sp,'task8 initializer constantcode4 and saved task source')
    check(inn[4]['rs2']==10 and inn[4]['imm']==12 and inn[10]['rd']==10 and inn[10]['imm']==12,'task8 saved incoming ID for source publication')
    check(sn[32]['imm']==2 and sn[34]['imm']==0 and sn[32]['width']==1 and sn[34]['width']==2,'task8 selector task byte before gate halfword')
    check(sn[18]['rs1']==15 and sn[8]['rd']==13 and sn[18]['rs1']!=sn[8]['rd'],'task8 generic selector index uses full delta not low16 guard')
    entry,rs=route8.role.specs('entry',index)
    check(rs[entry+40]['imm']+rs[entry+44]['imm']==hp and rs[entry+52]['target']==ip,'task8 correct registered handler address')
    i9p=route9.STARTS[index][0];i9=route9.body(init.binding.take(data,i9p,42),'initializer',index);i9n={v['pc']-i9p:v for v in i9['instructions']}
    check(any(v['op']=='li' and v.get('rd')==11 and v.get('imm')==6 for v in i9n.values()),'task8 separate known code6 route source')
    # Full parent proofs already establish code4/6/7 lookup and tuple8 copy.
    forward=parent['bodies']['forwarder'];check(forward['start']==0x4e290+152*index,'task8 parent typeA0 forwarder join')
    fn={v['pc']-forward['start']:v for v in forward['instructions']};check(fn[0x1e]['imm']==0xa0,'task8 parent message type matches consumer')
    recv=previous.previous.receive;rb=recv.body(init.binding.take(data,recv.SOURCES[index][0],136),'receive',index)
    pubraw=init.binding.take(data,public,78);check(sha256(pubraw).hexdigest()==common.dealloc.DETAILS[index][-2],'task8 public message cleanup reuse')
    free,_=common.previous.free_body(init.binding.take(data,common.previous.release.DETAILS[index][0],212),index)
    _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
    for part,b in bs.items():
        check(sparse.captured(mem,b['start'],b['bytes'])==init.binding.take(data,b['start'],b['bytes']),'task8 original strict HEX backing')
        receipts.append({'part':part,'source':b['start'],'bytes':b['bytes'],'all_bytes_captured':True})
    return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,'CFG_certificates':{k:common.certificates(b) for k,b in bs.items()},
      'witnesses':witnesses(h,d),'roles':{'task8_byte':task,'odd_callback_word':odd,'other_callback_word':other,'routing_base':G+800+80*index},
      'route_sources':{'initializer_start':ip,'initializer_sha256':ib['sha256'],'selector_start':sp,'selector_sha256':sb['sha256'],
        'code4_selected_task':8,'code4_handler':hp,'code6_selected_task':9,'code6_handler':(0x502b4,0x5034e)[index],
        'code7_zero_gate_only_if_initial_clear_retained_except_known_writers':True,'new_code_bytes_counted':0},
      'cleanup_reuse':{'receive_sha256':rb['sha256'],'public_cleanup':public,'public_cleanup_sha256':sha256(pubraw).hexdigest(),'private_payload_cleanup':0x20000110},
      'handler_contract':['no bit15 ->0;bit15 savesfullE andreceivesfreshsavedtask8byte;null ->E XOR8000;nonnulltype!=A0 ->publiccleanuporiginalM thenE XOR8000',
        'typeA0:initializeSP11releaseflag1;decoder(M,SP20);capturedecoderreplyS1. Nonzero reply skips tuple interpretation;0 classifiesfreshopcodebyteSP22/flagSP21',
        'twoindirectcallbacks fromfreshodd/otherword get(freshU16M2,SP20,&SP11);normalreturnmaychangeborrowedtuple/releaseflag;replysavedS1 oncorrespondingpaths',
        'commonrelease:if freshU8SP11 andfreshoriginalM8nonnull ->privatefree(originalM8),unchangedpointer. Zero releaseflag suppressesprivatecall',
        'statusnonzero or selectedopcode/prefix causesIDhelper(ID,1);if savedstatus19 then skippublicmessagecleanup ANDskip eventXOR,returnfullE. Otherpaths publiccleanuporiginalM thenE XOR8000',
        'reporthelper/callback/IDhelper semantics andprogressremainopaque;borrowedSP11/SP20retention andpostreleaseaccessnotclosed'],
      'decoder_contract':['captureU16M6 L;L0 ->1 withoutoutputwrites. Otherwise samplepayloadP=M8,readfirstbyteb,no payloadnull/extentguard',
        'bit7clear ->bodylenL-1,status0. bit7set+L<=12 ->1 withoutoutputwrites;bit7set+L>12 callsaux(freshU16M2,1,P,L-12,P+L-12),thenstatus1+(reply!=0),bodylenL-13',
        'writeoutbyte0status,byte1bit6,byte2low6opcode,U16out4bodylen,wordout8=(P+1 ifbodylen!=0 else0). Bytes3/6/7 untouched;originalM8notlocallychanged',
        'return0 unlessstatus2,inwhichcase returnbit6;earlyrejections1. Auxiliarynonzero isnot forwarded numericreply. Source/extent/auxeffects andnormalcallee preservationstillpremises'],
      'routing_contract':'selectedconstantcode4->retainedrow0gate4/task8->matchingregisteredhandler;code6->task9isdistinctnextconsumer. Selector tests low16delta butusesfull32delta forindex;48Browbound onlyforactualconstantcodes4..7;publicationtaskbyteprecedesgate,notatomicmatchedsnapshot',
      'ownership_boundary':'originalM8mayP+6 fromprecedingforwarder;decoderbodypointermayP+7,butprivatecleanupusesfreshoriginalM8. Callbackcanchangeflag andstatus19canretainmessagewithoutclearingeventafterpayloadattempt. No actualfree,delivery,exclusiveownership orsafe retainedmessage proof',
      'premises':'matchingconditionalcandidateISA/code/task/provider/queue/dispatch;validmemory/frame/global/heap/source/copyaccesses;normalcallee S/SP/RA andsaved-frame preservation,allowexplicitborrowedflag/tupleoutputs;no adversealias/IRQ/DMA/reentry/unaccountedwriters;freshidentityseparatelyretained',
      'actual_binding_delivery_callback_retention_or_payload_lifetime_proved':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage,hexes):
    parent=previous.derive(image,carriers,header,coverage,hexes)
    profiles=[profile(image,d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==904,'task8 byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==334,'task8 instruction census')
    return {'schema':'TSL9-task8-typeA0-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'standard_XOR_encoding':{'mask':0xfe00707f,'match':0x4033,'fields':{'rd_lsb':7,'rs1_lsb':15,'rs2_lsb':20},'original_word':'3349f900','target_execution':False},
      'complete_body_bytes':904,'complete_body_instructions':334,'C_reconstruction_coverage_changed':False,
      'remaining':['two callback bindings/releaseflag retention,status19 lifetime','auxiliary/report/IDhelper nestedcontracts andtask9 consumer','actualinstalledprovider,otherwriters andpayloadownership'],
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
                else:raise RuntimeError('task8 instruction mutation escaped')
                mutations+=1
            for off,f3 in TYPED_LOADS[i][part]:
                bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
                try:body(bad,part,i)
                except RuntimeError as ex:check('typed load encoding' in str(ex),'task8 exact load-type guard')
                else:raise RuntimeError('task8 typed load mutation escaped')
                typed+=1
        bad=bytearray(init.binding.take(data,STARTS[i][0],312));off=0xc4;bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<13)).to_bytes(4,'little')
        check(decode(bad,STARTS[i][0])[STARTS[i][0]+off]['op']=='or','task8 wrong OR fixture')
        try:body(bad,'handler',i)
        except RuntimeError as ex:check('task8 operand' in str(ex),'task8 exact XOR-versus-OR guard')
        else:raise RuntimeError('task8 wrong event operation escaped')
    for rd in range(32):
        for a in range(32):
            for b in range(32):
                word=0x4033|(rd<<7)|(a<<15)|(b<<20);v=decode(word.to_bytes(4,'little'),0x1000)[0x1000]
                check((v['op'],v['rd'],v['rs1'],v['rs2'])==('xor',rd,a,b),'task8 standard XOR register-field decode vector')
    check((mutations,typed)==(334,24),'task8 mutation census');domains()
    print('PASS:334 instruction/24 typed-load/2 wrong-event-operation mutations rejected;32768 XOR decode vectors;event/length/opcode/frame domains')


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
    else:check(OUT.read_bytes()==raw,'task8 exact ledger replay')
    print('PASS:904B/334i complete task8 typeA0 handler/decoder;strict HEX;code4 routing andconditionalcleanup/status19 joins;exact ledger')
    print('PASS:NO target execution/emulation;callbackoutputs,auxiliaryeffects,actualbinding andpayload/message ownership UNPROVED')


if __name__=='__main__':main()


