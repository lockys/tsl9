"""Bounded callback exit operands, frame fields and conditional CFG joins.

Original bytes plus host graph/bit arithmetic only; no target ISA, callback,
resident, RAM/frame, MMIO or device execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_ram_callback_loop_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-ram-callback-exits-static.json')
PARTS=(('threshold_exit',324,52,20),('completion_gate',390,18,6),('epilogue',834,20,10),('final_tail',898,80,28))
RESTORE=((8,24),(1,28),(9,20),(18,16),(19,12),(20,8),(21,4),(22,0))
HASHES=(
 ('e4e43cf20f8a3884e469f7f20bf648c3a6f633e97b9f8aacd29ee4c66f897ce3',
  '8a05e80bfddbe98b382fd36c4f532409af1b275d905df4fe709066e92fa05921',
  '149bca15f51bf26d0c77efd46862edf43633d1d725924f1ab1a7d734f7f3d42b',
  '48772c2662ad1ee8adaa484e39c07942af737faf45339e65b98923c4b2ab7327'),
 ('a9735c591e3abd8c12fb89c29f57ebb0876b611845aa8b194ed4dcdc841fc5a4',
  '4bb9b249b9a2a18575f7f8636401b9f80a03522ba8b66a72719065e084acfe10',
  '149bca15f51bf26d0c77efd46862edf43633d1d725924f1ab1a7d734f7f3d42b',
  '1e9a8347ea4f75442b43f6c21b5c659a8636cc71f71ae1cf46e7fe6578e996bc'))
# threshold helper, completion helper, pointer slot delta, tail source delta,
# tail linked-helper low, tail transfer low
PARAMS=((-1442,-1386,544,1260,-528,1072),(-1122,-1066,624,1340,-388,1212))


def specs(role,entry,params):
    low1,low2,slot,src,low3,low4=params;s={};pc=entry+next(o for r,o,size,n in PARTS if r==role)
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def move(o,r,a):e(o,'mv',rd=r,rs2=a)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def callpair(o,upper,low):e(o,'auipc',rd=1,imm=upper);e(o+4,'jalr',rd=1,rs1=1,imm=low)
    if role=='threshold_exit':
        li(0,11,8);move(2,10,8);callpair(4,0xe0056000,low1);store(12,10,8,43,1)
        lui(16,15,0x20003000);load(20,6,15,slot);e(24,'beq',rs1=6,rs2=0,target=entry+834)
        for j,(r,o) in enumerate(RESTORE):load(28+2*j,r,2,o)
        li(44,11,2);li(46,10,5);addi(48,2,2,32);e(50,'jr',rs1=6)
    elif role=='completion_gate':
        move(0,10,8);e(2,'jal',rd=1,target=entry+2076);move(4,10,8);callpair(6,0xe0056000,low2)
        e(14,'bne',rs1=10,rs2=0,target=entry+834)
    elif role=='epilogue':
        regs=((1,28),(8,24))+RESTORE[2:]
        for j,(r,o) in enumerate(regs):load(2*j,r,2,o)
        addi(16,2,2,32);e(18,'jr',rs1=1)
    elif role=='final_tail':
        load(0,15,9,12,1,mnemonic='qk.c.lbu');store(2,0,19,164);e(6,'beqz',rs1=15,target=pc+38)
        lui(8,15,0x20003000);load(12,10,15,src);callpair(16,0xe0043000,low3)
        lui(24,15,0xe000e000);lui(28,14,0x02000000);store(32,14,15,516);e(36,'jump',target=entry+834)
        load(38,15,8,41,1);li(42,11,1)
        for j,(r,o) in enumerate(RESTORE):load(44+2*j,r,2,o)
        e(60,'sll',rd=11,rs1=11,rs2=15);e(64,'slli',rd=11,rs1=11,imm=16);e(66,'srli',rd=11,rs1=11,imm=16)
        li(68,10,0);addi(70,2,2,32);e(72,'auipc',rd=6,imm=0xe0042000);e(76,'jalr',rd=0,rs1=6,imm=low4)
    else:raise RuntimeError('unknown callback exit role')
    return s


def window(raw,role,entry,params,digest):
    _,off,size,count=next(d for d in PARTS if d[0]==role)
    if role=='final_tail':check(int.from_bytes(raw[38:42],'little')&0x707f==0x4003,'exit unsigned byte encoding')
    n=decode(raw,entry+off);s=specs(role,entry,params);check(set(n)==set(s),'exit whole boundaries '+role)
    for p,f in s.items():init.g(n,p,'exit '+role+' operand '+hex(p-entry-off),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'exit full window identity '+role)
    edges={};calls=[];terminals=[]
    for p,d in n.items():
        tail_jalr=d['op']=='jalr' and d['rd']==0
        if d['op']=='jr' or tail_jalr:
            qs=[];terminals.append({'pc':hex(p),'kind':'ordinary RET' if d['op']=='jr' and d['rs1']==1 else 'tail transfer',
                'target':hex((p-4+n[p-4]['imm']+d['imm'])&0xfffffffe) if tail_jalr else 'restored RA & ~1' if d['rs1']==1 else 'fresh T1 & ~1',
                'new_link':False})
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beq','beqz','bne'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        edges[p]=qs
        if d['op']=='jal' or d['op']=='jalr' and not tail_jalr:
            target=hex(d['target']) if d['op']=='jal' else hex((p-4+n[p-4]['imm']+d['imm'])&0xfffffffe)
            calls.append({'pc':hex(p),'link':hex(p+d['size']),'target':target,'normal_return_and_preservation_proved':False})
    return {'start':hex(entry+off),'end_exclusive':hex(entry+off+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'conditional_CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},'calls':calls,'terminal_edges':terminals,'complete_function':False}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,p) in enumerate(zip(carriers,parent['profiles'])):
        source=int(p['flash_entry'],16);entry=int(p['mapped_entry'],16);bodies={}
        for j,(role,off,size,count) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size);bodies[role]=window(raw,role,entry,PARAMS[i],HASHES[i][j])
            window(raw,role,source,PARAMS[i],HASHES[i][j])
        check(bodies['threshold_exit']['calls'][0]['target']==('0x568f6','0x56a36')[i],'mapped threshold helper')
        check([x['target'] for x in bodies['completion_gate']['calls']]==['0x2000156c',('0x56972','0x56ab2')[i]],'mapped completion helpers')
        check(bodies['final_tail']['calls'][0]['target']==('0x43ed2','0x43f5e')[i],'mapped linked tail helper')
        check(bodies['final_tail']['terminal_edges'][0]['target']==('0x4354a','0x435d6')[i],'mapped unlinked final transfer')
        for role,at in (('threshold_exit',28),('epilogue',0),('final_tail',44)):
            start=int(bodies[role]['start'],16);ns={x['pc']:x for x in bodies[role]['instructions']}
            actual={(ns[start+at+2*j]['rd'],ns[start+at+2*j]['imm']) for j in range(8)}
            check(actual==set(previous.prefix.SAVED),'exact saved-frame restore field join '+role)
        edges={int(k,16):[int(q,16) for q in qs] for k,qs in p['combined_CFG'].items()}
        for b in bodies.values():
            for k,qs in b['conditional_CFG'].items():check(int(k,16) not in edges,'new exit window overlap');edges[int(k,16)]=[int(q,16) for q in qs]
        cuts={q for qs in edges.values() for q in qs if q not in edges};check(cuts=={entry+408},'only selected fallthrough cut remains')
        def reachable(root):
            seen=set()
            def visit(v):
                if v not in edges or v in seen:return
                seen.add(v)
                for q in edges[v]:visit(q)
            visit(root);return seen
        seen=reachable(entry);tailnodes={x['pc'] for x in bodies['final_tail']['instructions']}
        check(len(edges)==174 and len(seen)==146 and set(edges)-seen==tailnodes,'entry reachability separated from independent tail root')
        check(seen|reachable(entry+898)==set(edges),'two explicit roots cover selected graph')
        cycles=[c for c in previous.components(edges) if len(c)>1 or c[0] in edges[c[0]]]
        check(len(cycles)==1 and cycles[0]==[int(x,16) for x in p['cyclic_SCC_nodes']],'existing 41-node loop preserved')
        profiles.append({'label':p['label'],'flash_entry':hex(source),'mapped_entry':hex(entry),'bodies':bodies,
            'combined_CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},
            'cyclic_SCC_nodes':p['cyclic_SCC_nodes'],'only_continuation_cut':hex(entry+408),
            'entry_root_reachable_nodes':len(seen),'independent_final_tail_root':hex(entry+898),
            'independent_tail_reachable_from_entry_proved':False,
            'fresh_T1_slot':hex(0x20003000+PARAMS[i][2]),'final_tail_source_slot':hex(0x20003000+PARAMS[i][3]),
            'actual_frame_preservation_or_installed_binding_proved':False})
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==340,'exit new byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==128,'exit new instruction census')
    return {'schema':'TSL9-RAM-callback-exits-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'8 new bounded pieces340B/128instructions; selected combined1016B/348instructions, still not whole callback',
        'threshold_exit_contract':['A0=then-live S0,A1=8 ->unknown helper; SB low8(returnA0) to[then-live S0+43]',
            'fresh T1 word after helper; if rawT1zero ->ordinary epilogue with full A0/A1 unchanged',
            'if rawT1nonzero ->8 restored saved fields; A0=5,A1=2,SP+=32; JR T1&~1 without new link'],
        'completion_contract':'entry at local-call portion setsA0=S0 thenCALL; alternate entry skips that call; both setA0=then-live S0 and call second helper; nonzero ->epilogue, zero ->only selected cut',
        'epilogue_contract':'8 original saved fields ->registers; SP+=32; ordinary RET via restoredRA; A0/A1 unchanged locally',
        'independent_tail_contract':['fresh byte[S1+12] first; unconditionally SW0 to[then-live S3+164] before testing sampled byte',
            'nonzero: fresh source slot toA0; unknown linked helper; then encoded SW value02000000 to addressE000E204; jumpordinaryepilogue',
            'zero: fresh unsignedbyte b=[then-live S0+41] before restoringS0; restore8fields; A1=(1<<(b&31))&65535; A0=0;SP+=32; direct unlinked tail transfer'],
        'MMIO_operand_does_not_prove_hardware_effect':True,
        'premises':['actual installed candidate/mapping and conditional Xwchc ISA; valid stack/object/code/data accesses',
            'unknown callees normal-return and preserve required S0/S1/S3/SP/saved words; aliases, interrupt, reentry and other writers unproved',
            'restoring fields only recovers caller registers if frame words survived; a tail transfer does not prove downstream return or ABI',
            'independent final tail requires separate entry premise; missing middle body not silently connected; stores described as operands only'],
        'remaining':['only current-entry cut at41158/41198 and middle callback arithmetic/loops','independent tail actual incoming edges and called targets',
            'full config gates/copy semantics/registration order','installed provider, hardware behavior and frame/object lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    check(init.timer.encode('lbu',15,9,12)==0x24dc,'tail critical QK flag load')
    zeros=0
    for b in range(256):
        value=(1<<(b&31))&65535
        check((value==0)==bool(b&16),'RV32 shift low5 then low16 domain')
        if value==0:zeros+=1
        else:check(value==1<<(b&15),'nonzero mask position')
    check(zeros==128,'mask zero-value partition')
    changes=(((0,4),(8,1<<20),(12,1<<20),(20,1<<20),(24,1<<12),(50,4)),
        ((2,4),(6,1<<12),(10,1<<20),(14,1<<12)),((0,4),(16,4),(18,4)),
        ((0,4),(2,1<<20),(6,4),(12,1<<20),(32,1<<20),(60,1<<20),(76,1<<7)))
    count=0
    for i,(data,d) in enumerate(zip(carriers,previous.prefix.DETAILS)):
        source=d[0]
        for j,(role,off,size,n) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size)
            for at,flip in changes[j]:
                b=bytearray(raw);width=decode(raw,source+off)[source+off+at]['size'];b[at:at+width]=(int.from_bytes(b[at:at+width],'little')^flip).to_bytes(width,'little')
                try:window(b,role,source,PARAMS[i],HASHES[i][j])
                except RuntimeError as e:check(str(e)=='exit '+role+' operand '+hex(at),'specific exit mutation guard '+str(e))
                else:raise RuntimeError('callback exit mutation escaped')
                count+=1
    check(count==40,'exit mutation census')
    print('PASS: 256 RV32 mask cases; 3 exact eight-field restores/profile; 40 specified operand mutations rejected')


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
    else:check(OUT.read_bytes()==output,'callback exits exact ledger replay')
    print('PASS: new340B/128instructions; combined1016B/348instructions; one fallthrough cut, distinct RET/tails and separate final-tail root')
    print('PASS: exact ledger; NO target execution/MMIO; whole callback/preservation/installed binding UNPROVED')


if __name__=='__main__':main()
