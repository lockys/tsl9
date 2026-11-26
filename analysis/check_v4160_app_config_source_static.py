"""Complete APP config constructor, wrapper and mode tail: bytes/CFG only.

Host constant algebra, no target ISA, memory, MMIO, callback or provider runner.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_config_arithmetic_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-app-config-source-static.json')
DETAILS=(('construct',0x19b56,126,43,'b5717eca817e1845094b27eca434f7827b15f3b331148c1ba0491eca9bf14940'),
 ('wrapper',0x19b16,64,22,'db9229526342b615e61627737672782a6620c99170d608bb956f9d10356884ab'),
 ('mode_tail',0x197b8,6,2,'781acefb45e65f1dbc986de7f9ae09da680c11d5d1416f460b706c9c5d1bede0'))
PRECALLS=((18,0x19142),(24,0x19076),(30,0x190c6),(36,0x1909e),(44,0x190da),
 (50,0x190e6),(54,0x19272),(58,0x19272),(64,0x19248),(68,0x19272),
 (74,0x19220),(78,0x19272),(82,0x197b8))


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    if role=='construct':
        addi(0,2,2,-32);li(2,11,1);lui(4,10,0x18000000);store(8,1,2,28)
        for o,v in ((10,0),(12,4),(14,8),(16,12)):store(o,0,2,v)
        for o,target in PRECALLS:e(o,'jal',rd=1,target=target)
        for o,v in ((22,1),(28,1),(34,0),(48,1),(62,1),(72,0)):li(o,10,v)
        addi(40,10,0,512);li(86,15,-1);store(88,15,2,4);lui(90,15,0x3e84000)
        addi(94,15,15,-384);store(98,15,2,8);e(100,'auipc',rd=15,imm=0xfffff000)
        addi(104,15,15,1548);store(108,15,2,0);lui(110,15,0x40000)
        load(114,15,15,116);e(116,'mv',rd=10,rs2=2);e(118,'call_indirect',rd=1,rs1=15)
        load(120,1,2,28);addi(122,2,2,32);e(124,'jr',rs1=1)
    elif role=='wrapper':
        addi(0,2,2,-16);store(2,9,2,4);lui(4,9,0x40000);load(8,15,9,128)
        store(12,1,2,12);store(14,8,2,8);e(16,'auipc',rd=10,imm=0)
        addi(20,10,10,-458);e(24,'call_indirect',rd=1,rs1=15);addi(26,8,3,388)
        store(30,10,8,0,1);e(34,'jal',rd=1,target=0x19b56);load(36,10,8,0,1)
        load(40,8,2,8);load(42,6,9,88);load(46,1,2,12);load(48,9,2,4)
        lui(50,12,0x2f000);addi(54,12,12,-512);lui(58,11,8192)
        addi(60,2,2,16);e(62,'jr',rs1=6)
    elif role=='mode_tail':li(0,10,3);e(2,'jal',rd=0,target=0x1929a)
    else:raise RuntimeError('unknown APP config role')
    return s


def body(raw,role):
    _,pc,size,count,digest=next(d for d in DETAILS if d[0]==role)
    if role=='wrapper':check(int.from_bytes(raw[36:40],'little')&0x707f==0x4003,'APP config wrapper unsigned byte encoding')
    n=decode(raw,pc);s=specs(role,pc);check(set(n)==set(s),'APP config complete boundaries '+role)
    for p,f in s.items():init.g(n,p,'APP config '+role+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'APP config complete identity '+role)
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op']
        if op=='jr':
            q=[]
            if d['rs1']!=1:tails.append({'pc':hex(p),'target':'fresh U32[then-live S1+88] & ~1','link_written':False})
        elif op=='jal' and d['rd']==0:
            q=[];tails.append({'pc':hex(p),'target':hex(d['target']),'link_written':False})
        else:q=[p+d['size']]
        check(all(v in n for v in q),'APP config local CFG no cuts '+role);edges[p]=q
        if op=='call_indirect' or op=='jal' and d['rd']==1:
            calls.append({'pc':hex(p),'link':hex(p+d['size']),
                'target':hex(d['target']) if op=='jal' else 'fresh U32[40074] & ~1' if role=='construct' else 'fresh U32[40080] & ~1',
                'normal_return_and_preservation_proved':False})
    check(len(calls)=={'construct':14,'wrapper':2,'mode_tail':0}[role],'APP config exact call count '+role)
    check(len(tails)==(role!='construct'),'APP config explicit terminal kind '+role)
    check(list(n)==sorted(n) and all(q==[p+n[p]['size']] for p,q in edges.items() if q),'APP config finite sequential local CFG '+role)
    stores=[d for d in n.values() if d['op']=='store']
    defs=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    if role=='construct':
        check([(d['pc']-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for d in stores]==
            [(8,2,1,28,4),(10,2,0,0,4),(12,2,0,4,4),(14,2,0,8,4),(16,2,0,12,4),(88,2,15,4,4),(98,2,15,8,4),(108,2,15,0,4)],'APP config exact frame/field stores')
        check(not any(d.get('rd')==10 for p,d in n.items() if p>=pc+120),'APP constructor forwards provider A0 locally')
        check(len([d for d in n.values() if d.get('rd')==2])==2,'APP constructor only frame SP definitions')
    if role=='wrapper':
        check(n[pc+36]['rd']==10 and n[pc+36]['rs1']==8 and n[pc+36]['imm']==0,'APP wrapper overwrites config return with fresh byte')
    return {'role':role,'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,
        'instructions':list(n.values()),'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'calls':calls,'external_tails':tails,'stores':stores,'local_encoded_GPR_definitions':defs,
        'complete_local_function_or_tail_wrapper':True,'transitive_callee_closure_proved':False}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={role:body(app[pc-0x8000:pc-0x8000+size],role) for role,pc,size,count,digest in DETAILS}
    construct=bodies['construct'];wrapper=bodies['wrapper'];mode=bodies['mode_tail']
    check(wrapper['calls'][1]['target']==construct['start'] and construct['calls'][-2]['target']==mode['start'],'APP constructor/wrapper/mode call joins')
    check(len(construct['calls'][:-1])==13 and sum(d['bytes'] for d in bodies.values())==196,'APP config source scope census')
    reader=(0x19bba+0xfffff000+1548)&0xffffffff
    check(reader==0x191c6 and 0x19b26-458==0x1995c,'APP config pointer constants')
    word=0x3e84000-384;check(word==0x03e83e80 and word&65535==16000 and word>>16==1000,'APP paired halfword construction')
    profiles=[]
    for i,data in enumerate(carriers):
        gate=previous.previous.DETAILS[i][0]
        check(init.binding.word(data,0x40074)&~1==gate,'APP config candidate slot target join')
        profile=parent['profiles'][i]
        check(profile['config_call']['target']==profile['arithmetic']['entry'],'APP config arithmetic evidence join')
        profiles.append({'label':profile['label'],'candidate40074_target':hex(gate),
            'arithmetic_entry':profile['arithmetic']['entry'],
            'conditional_h16000_output':22,'actual_installed_binding_proved':False})
    return {'schema':'TSL9-APP-config-source-static-v1','profile':parent['profile'],'APP_sha256':sha256(app).hexdigest(),
        'scope':'three complete APP local bodies196B/67instructions;13 pre-provider call sites are explicit unclosed callees',
        'bodies':bodies,'profiles':profiles,
        'initial_config':'after SP-=32 saveRA atSP+28; zero wordsSP+0,+4,+8,+12 before13 calls',
        'pre_calls':[{'pc':hex(0x19b56+o),'target':hex(t)} for o,t in PRECALLS],
        'pre_call_arguments':'19142 A0=18000000,A1=1;19076 A0=1;190c6 A0=1;1909e A0=0;190da A0=512;190e6 A0=1;19248 A0=1;19220 A0=0;19272 sites have then-live A0;197b8 forces A0=3 then tails1929a',
        'post_calls_config':'after last pre-call, local wordsrelative to then-live SP are +4=ffffffff,+8=03e83e80,+0=191c6; no further nested call before40074 request',
        'byte12_condition':'byte12..15 initiallyzero but not rewritten after13 calls; zero at final input needs same restored SP, intact bytes and no interfering writes',
        'final_provider_arguments':'fresh targetU32[40074]&~1; A0=then-live SP; no local null guard; A1/A2 not reestablished at this call',
        'conditional_config_gate_join':'with matching candidate, then-live SP nonzero, optional hook reload C matching that source, valid accesses, preserved input/required context and no interference, words0/4 and halfwords8/10 nonzero; ifinitialbyte12 surviveszero, state+21 gate bypassed',
        'conditional_arithmetic_join':'matching preserved copy and input halfword h16000 yields floor(7*h/5000)=22 only when fresh state+23 iszero and arithmetic branch completes; otherwise priorbyte may remain',
        'constructor_return':'provider A0 locally forwarded throughrestoreRA/SP/RET; no caller status test; wrapper next instruction freshloads U8[then-live S0] intoA0, discarding that result',
        'wrapper_source':'first call freshslot40080 with A0=1995c; afternormalreturn S0=then-liveGP+388 and store low8(A0); callconstructor; read freshbyte throughthen-live S0',
        'wrapper_tail':'fresh target from then-liveS1+88 (nominal40058 only ifS1 preserved40000); restoreRA/S0/S1/SP; tailJR T1 with A0=freshbyte,A1=8192,A2=192000; no local outcome/success test',
        'lifetime':'constructor16B config is inside its32Bframe; valid only duringactiveframe under required preservation; laterRA restore+SP release provides no copied-pointer lifetime guarantee; reader191c6 is code pointer, not stack address',
        'premises':['all pre-calls/slot calls must returnnormally and preserve needed SP/RA/frame, S0/S1/GP and mapping; no universal termination or ABI inferred',
            'config values afterpre-calls are relative to then-liveSP; linking earlierzero bytes to finalC needs SP identity acrosscalls',
            'optional hook may mutate saved input/global/config bytes beforegates; effective copy/pub/source equality requires previousnoalias/nointerference conditions',
            'numeric slot load and matching candidateword do not prove installedprovider or externalruntime paths'],
        'remaining':['13 pre-provider callees and1929a behavior/field writers','actual installed slot40074/40080/40058 bindings',
            'optional hook/registration effects, data/stack lifetime and other arithmetic domains'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    check(0x3e84000-384==16000+(1000<<16),'APP config word/halfword oracle')
    check((7*16000)//5000==22 and 0x2f000-512==192000,'APP config quotient/tail delay constants')
    count=0
    for role,pc,size,n,h in DETAILS:
        raw=app[pc-0x8000:pc-0x8000+size];nodes=decode(raw,pc)
        # Every instruction contributes an operand/control mutation.
        for p,d in nodes.items():
            at=p-pc;b=bytearray(raw);w=d['size'];flip=1<<20 if w==4 else 4
            b[at:at+w]=(int.from_bytes(b[at:at+w],'little')^flip).to_bytes(w,'little')
            try:body(b,role)
            except RuntimeError as e:check(str(e).startswith('APP config '+role+' operand '),'specific APP config mutation guard '+str(e))
            else:raise RuntimeError('APP config mutation escaped')
            count+=1
        if role=='wrapper':
            b=bytearray(raw);b[37]^=64
            try:body(b,role)
            except RuntimeError as e:check(str(e)=='APP config wrapper unsigned byte encoding','specific APP unsigned mutation guard')
            else:raise RuntimeError('APP config unsigned mutation escaped')
            count+=1
    check(count==68,'APP config mutation census')
    print('PASS: config paired-field/quotient/tail algebra; all67 instruction operand mutations and1 unsigned-byte mutation rejected')


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
    tests(app);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'APP config source exact ledger replay')
    print('PASS:3 complete APP bodies196B/67instructions; alloperands/CFG/callstails/fieldstore/frame/provider/arithmeticjoins; exact ledger')
    print('PASS: NO target execution; pre-callee/installedprovider/inputpreservation/lifetime UNPROVED')


if __name__=='__main__':main()
