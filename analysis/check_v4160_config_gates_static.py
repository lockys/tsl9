"""Complete candidate config gates: original bytes, CFG and host algebra only.

No target ISA, RAM/frame, callback, copy, resident, MMIO or device execution.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_second_selector_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-config-gates-static.json')
DETAILS=((0x43f46,220,492,564,480,924,0x6df1a,0x43d62,0x43b0a,
 '9aa8ba0cd9adc48d5f3fbfad68dc2ca6f2875fbd1e9c04c3283439cdbba8dc6a'),
 (0x43fd2,228,572,644,560,776,0x6e10a,0x43dee,0x43b96,
 '2e8dedeaeb6223cc57ec01b518faf261846305d7f925429bd01b80398283a893'))


def specs(pc,index):
    _,_,base,copied,slot,low,arith,hook,register,_=DETAILS[index]
    s={}
    # V140 inserts two instructions and reorders the saved S0 in its prologue.
    def address(o):return pc+o+(8 if index and o>=8 else 0)
    def e(o,op,**f):s[address(o)]=dict(op=op,**f)
    def branch(o,op,target,**f):e(o,op,target=address(target),**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def load(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    addi(0,2,2,-32)
    if index:
        s[pc+2]=dict(op='lui',rd=15,imm=0x20003000)
        s[pc+6]=dict(op='store',rs2=8,rs1=2,imm=24,width=4)
        s[pc+8]=dict(op='lui',rd=8,imm=0x20003000)
        s[pc+12]=dict(op='store',rs2=0,rs1=15,imm=660,width=4)
    else:store(2,8,2,24);lui(4,8,0x20003000)
    addi(8,15,8,base);load(12,15,15,48);store(14,1,2,28)
    e(16,'mv',rd=11,rs2=10);addi(18,8,8,base)
    branch(22,'beqz',30,rs1=15);store(24,10,2,12)
    e(26,'call_indirect',rd=1,rs1=15);load(28,11,2,12)
    branch(30,'beqz',160,rs1=11);load(32,15,11,0);e(34,'li',rd=10,imm=1)
    branch(36,'beqz',152,rs1=15);load(38,15,11,4);branch(40,'beqz',152,rs1=15)
    load(42,15,11,8,2);branch(44,'beqz',152,rs1=15)
    load(46,15,11,10,2);branch(48,'beqz',152,rs1=15)
    load(50,15,11,12,1);branch(52,'beqz',70,rs1=15)
    load(54,15,8,21,1);e(56,'andi',rd=14,rs1=15,imm=3)
    e(60,'srli',rd=15,rs1=15,imm=2);e(62,'add',rd=15,rs1=15,rs2=14)
    e(64,'li',rd=14,imm=2);branch(66,'blt',152,rs1=14,rs2=15)
    lui(70,10,0x20003000);e(74,'li',rd=12,imm=16);addi(76,10,10,copied)
    e(80,'auipc',rd=1,imm=0x1ffbc000);e(84,'jalr',rd=1,rs1=1,imm=low)
    lui(88,15,0x20003000);load(92,13,15,copied);lui(96,14,0x20003000);store(100,13,14,slot)
    load(104,14,8,23,1);branch(106,'bnez',140,rs1=14);addi(108,15,15,copied)
    load(112,10,15,8,2);addi(114,15,0,1400);lui(118,12,0xf4000)
    e(122,'mul',rd=10,rs1=10,rs2=15);addi(126,12,12,576)
    e(130,'li',rd=13,imm=0);e(132,'li',rd=11,imm=0)
    e(134,'jal',rd=1,target=arith);store(138,10,8,23,1)
    lui(140,10,0x44000);addi(144,10,10,hook-0x44000);e(148,'jal',rd=1,target=register)
    e(150,'li',rd=10,imm=0);load(152,1,2,28);load(154,8,2,24)
    addi(156,2,2,32);e(158,'jr',rs1=1)
    lui(160,15,0x20003000);addi(164,15,15,base-80);lui(168,14,0x20001000)
    store(172,0,15,28);addi(176,14,14,-1658);lui(180,15,0x20003000)
    store(184,14,15,copied);lui(188,14,0x328000);addi(192,15,15,copied)
    e(196,'li',rd=13,imm=-1);addi(198,14,14,-1518)
    store(202,13,15,4);store(204,14,15,8);store(206,0,15,12,1)
    lui(210,15,0x40024000);store(214,13,15,616);branch(218,'jump',88)
    return s,address


def body(raw,index):
    pc,size,base,copied,slot,low,arith,hook,register,digest=DETAILS[index]
    n=decode(raw,pc);s,a=specs(pc,index)
    check(set(n)==set(s),'config complete boundaries')
    for p,f in s.items():init.g(n,p,'config operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,76+2*index,digest),'config complete identity')
    # Explicit Xwchc widths/signs, independently distinguished from stock r2 FP aliases.
    for o,m in ((42,'qk.c.lhu'),(46,'qk.c.lhu'),(50,'qk.c.lbu'),(54,'qk.c.lbu'),
                (104,'qk.c.lbu'),(112,'qk.c.lhu'),(138,'qk.c.sb')):
        check(n[a(o)].get('mnemonic')==m,'config Xwchc width/sign')
    edges={};calls=[]
    for p,d in n.items():
        op=d['op']
        if op=='jr':q=[]
        elif op=='jump':q=[d['target']]
        elif op in ('beqz','bnez','blt'):q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'config CFG no cuts');edges[p]=q
        if op in ('call_indirect','jalr','jal'):
            target='fresh U32[base+48] & ~1' if op=='call_indirect' else hex(0x20000332) if op=='jalr' else hex(d['target'])
            calls.append({'pc':hex(p),'link':hex(p+d['size']),'target':target,'normal_return_and_preservation_proved':False})
    seen=set();active=set()
    def visit(p):
        check(p not in active,'config CFG cycle')
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'config full local reachability')
    check([p for p,q in edges.items() if not q]==[a(158)],'config sole RET')
    check(len(calls)==4 and (a(80)+0x1ffbc000+low)&0xfffffffe==0x20000332,'config four calls and copy target')
    check({(d['rs2'],d['imm']) for d in n.values() if d['op']=='store' and d['rs1']==2}=={(8,24),(1,28),(10,12)},'config frame saves')
    check({(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2}=={(8,24),(1,28),(11,12)},'config frame restores and argument reload')
    # Publication must be the fresh copied/default word, not an inferred copy result.
    check(n[a(92)]['imm']==copied and n[a(100)]['imm']==slot,'config fresh publication load/store')
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,
        'instructions':list(n.values()),'conditional_CFG':{hex(p):[hex(v) for v in q] for p,q in edges.items()},
        'calls':calls,'local_CFG_acyclic':True,'complete_function':True,
        'base':hex(0x20003000+base),'copied_config':hex(0x20003000+copied),
        'service_word':hex(0x20003000+slot),'optional_hook_word':hex(0x20003000+base+48),
        'default_clear_word':hex(0x20003000+base-52),
        'V140_unconditional_pre_hook_clear':hex(0x20003294) if index else None,
        'copy_call_arguments':{'A0':hex(0x20003000+copied),'A1':'then-live config pointer, reloaded from SP+12 after optional hook','A2':16},
        'arithmetic_call_arguments':{'A0':'1400 * fresh U16[copied_config+8]','A1':0,'A2':1000000,'A3':0},
        'registration_arguments':{'A0':hex(hook),'callee':hex(register)}}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    profiles=[]
    for i,data in enumerate(carriers):
        pc,size,*_=DETAILS[i]
        check(int.from_bytes(init.binding.take(data,0x40074,4),'little')==pc,'config candidate40074 entry')
        b=body(init.binding.take(data,pc,size),i)
        profiles.append({'label':init.binding.PROFILES[i][0],'config':b,
            'candidate_first_copy_source_for_20000332':hex((0x402b0,0x402f0)[i]+0x20000332-0x20000040),
            'actual_installed_binding_or_runtime_execution_proved':False})
    return {'schema':'TSL9-config-gates-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'two complete config functions448B/154instructions, including post-RET default branch',
        'optional_hook':'snapshot U32[base+48] before validation; if nonzero call with original A0 and reload config A1 from SP+12; callback return value ignored',
        'nonnull_gates':'in order U32[config+0], U32[config+4], U16[config+8], U16[config+10] must be nonzero; no buffer-length/pointer-range validation established',
        'mode_gate':'if U8[config+12] is nonzero, fresh b=U8[base+21] must satisfy (b&3)+(b>>2)<=2; exactly b in {0,1,2,4,5,8}; zero config+12 bypasses this gate',
        'gate_failure':'A0=1; sole epilogue; no local copy/publication/registration after failed gate, but optional hook and V140 initial clear may already have occurred',
        'accepted_nonnull':'request copy16 with config pointer; after conditional normal return reload U32[copied_config] and publish to service_word; copy semantics/contents/retention unproved',
        'null_config':'skip nonnull gates and copy; clear default_clear_word; write default word0=0x20000986, word4=0xffffffff, word8=0x00327a12, byte12=0; write0xffffffff to0x40024268; jump to same fresh publication',
        'default_partial_initialization':'writes bytes0..12 only; bytes13..15 not initialized locally; word8 encodes U16+8=31250 and U16+10=50 under little-endian ISA interpretation',
        'post_publication':'fresh U8[base+23] nonzero skips arithmetic; else call arithmetic with (1400*U16[copied+8],0,1000000,0), then store low8(A0) to base+23; helper meaning unproved',
        'normal_success_return':'call registration with profile-specific callback pointer; after normal return force A0=0 and restore RA/S0/SP; no provider-success or hardware-success claim',
        'premises':['matching installed candidate, valid instruction/data/frame accesses and preserved code/data mapping',
            'all nested calls must return normally and preserve SP/S0 plus live frame words needed later; gate return values need no inferred callee A0 preservation',
            'SP+12 argument reload proves local storage usage only; alias writes, interrupts and reentry may change it or source/global fields',
            'separate fresh field loads do not form a coherent snapshot; no actual path reachability, provider pointer retention or object lifetime established',
            'MMIO write instruction identified only; never performed or assigned hardware meaning'],
        'remaining':['arithmetic helper6df1a/6e10a','copy helper20000332 original body and preservation/retention contract',
            'APP full config construction and installed candidate provenance','registration/callback downstream effects and object lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    allowed={b for b in range(256) if (b&3)+(b>>2)<=2}
    check(allowed=={0,1,2,4,5,8},'byte gate exhaustive oracle')
    for v in range(65536):check(0<=1400*v<=91749000<2**32,'arithmetic product does not wrap')
    check(0x328000-1518==0x327a12 and (0x327a12&65535)==31250 and (0x327a12>>16)==50,'default field algebra')
    count=0
    for i,data in enumerate(carriers):
        pc,size,*_=DETAILS[i];raw=init.binding.take(data,pc,size);_,a=specs(pc,i)
        for off in (12,28,32,38,42,46,50,54,56,60,66,74,76,84,92,100,104,112,122,134,138,144,148,158,172,184,202,204,206,214,218):
            n=decode(raw,pc)[a(off)];at=a(off)-pc;b=bytearray(raw)
            # Keep the opcode family while changing a branch/operand bit.
            flip=1<<20 if n['size']==4 else 1<<2
            b[at:at+n['size']]=(int.from_bytes(b[at:at+n['size']],'little')^flip).to_bytes(n['size'],'little')
            try:body(b,i)
            except RuntimeError as e:check(str(e).startswith('config operand '),'specific config mutation guard '+str(e))
            else:raise RuntimeError('config mutation escaped')
            count+=1
    check(count==62,'config mutation census')
    print('PASS: all256 byte-gate values; all65536 product bounds; default-field algebra; 62 operand mutations rejected')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    ledger=derive(app,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'config gates exact ledger replay')
    print('PASS: two complete config functions448B/154instructions; full operands/acyclic CFG/four calls/frame/nullable-default joins')
    print('PASS: exact ledger; NO target execution; installed binding/copy semantics/MMIO effects/lifetime UNPROVED')


if __name__=='__main__':main()
