"""Complete original callback operands/CFG closure under normal-call-return.

Offline decoding and host integer identities only. No target ISA, callbacks,
RAM/frame, copy, resident, MMIO, FENCE.I or device execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_ram_callback_middle_static as previous
import check_v4160_loaded_hook_sources_static as loaded

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-ram-callback-closure-static.json')
MASK=0xffffffff
PARTS=(('arithmetic',610,140,41),('selection',750,34,11),('footer',784,50,18),('alternative',870,16,5),('bypass',886,12,4))
NEW_HASHES=(('b08e153793b7893e0bff7fe144e3f7c1358e31bd14106c77c6d73a5a8368a187',
 'a30ec389b16e7f527d10509328bc7f6b354ee27988fdad20eb7a98a1d5df03a1'),
 ('ac68f017c76b76326f79c5ad5216fc25aef558c142d775f68630f6197b63a0af',
 '7389c4bc671d771930d5405366aca5451520e90013014d2deb53cc19233f7a83'))
WHOLE_HASHES=('b353bc4b279cf6f978caa0b230d7959a5376661d62929c6b77004863849bc0e5',
 '957eb61b592d6c4481b4bff30bcb6c7e9bcf1638f54a418e43f4acde383b1990')
PARAMS=((515,-212,-240,-268,-348,1340,1300),(595,284,256,228,-114,1420,1380))


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=4 if h&3==3 else 2
        check(off+size<=len(raw),'closure whole instruction');chunk=raw[off:off+size];w=int.from_bytes(chunk,'little');p=pc+off
        if size==4 and w&0xfe00707f==0x02003033:
            d=dict(pc=p,size=4,bytes=chunk.hex(),op='mulhu',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        else:d=previous.decode(chunk,p)[p]
        n[p]=d;off+=size
    return n


def specs(role,entry,index,setter):
    g,l1,l2,l3,l4,ptr,state=PARAMS[index];pc=entry+next(o for r,o,size,n in PARTS if r==role)
    ld=loaded.DETAILS[index]
    if role=='selection':return loaded.specs('flow',pc,(ld[3],entry+870,entry+886,setter))
    if role=='alternative':return loaded.specs(role,pc,(ld[4],entry+776))
    if role=='bypass':return loaded.specs(role,pc,(ld[5],entry+784))
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v,w=4,**f):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**f)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def move(o,r,a):e(o,'mv',rd=r,rs2=a)
    def callpair(o,upper,low):e(o,'auipc',rd=1,imm=upper);e(o+4,'jalr',rd=1,rs1=1,imm=low)
    if role=='arithmetic':
        load(0,21,9,8,2);load(4,15,8,134,2);lui(8,18,999424);addi(12,14,18,575);binary(16,'mul',15,15,21)
        addi(20,18,18,576);binary(24,'add',15,15,14);binary(26,'divu',15,15,18);lui(30,14,0x20003000)
        load(34,14,14,g,1);binary(38,'add',15,15,14);e(40,'bltu',rs1=15,rs2=10,target=entry+898)
        binary(44,'mulhu',11,10,18);load(48,20,8,34,2);move(52,12,21);e(54,'li',rd=13,imm=0)
        binary(56,'mul',10,10,18);callpair(60,0xe006d000,l1);binary(68,'add',22,20,10)
        binary(72,'mul',10,20,21);lui(76,12,999424);addi(80,12,12,576);e(84,'li',rd=13,imm=0);e(86,'li',rd=11,imm=0)
        callpair(88,0xe006d000,l2);e(96,'beqz',rs1=10,target=pc+130);binary(98,'mulhu',15,10,18)
        move(102,12,21);e(104,'li',rd=13,imm=0);binary(106,'mul',11,18,11);binary(110,'mul',10,18,10)
        binary(114,'add',11,11,15);callpair(116,0xe006d000,l3);binary(124,'sub',10,20,10)
        store(128,10,8,34,2,mnemonic='qk.c.sh');e(130,'li',rd=10,imm=13);callpair(132,0xe0063000,l4)
    elif role=='footer':
        lui(0,13,0x20003000);load(4,12,13,ptr);lui(8,15,0x20003000);addi(12,15,15,state)
        e(16,'li',rd=14,imm=5);store(18,14,15,7,1,mnemonic='qk.c.sb');load(20,14,12,12)
        lui(22,15,0xffffe000);addi(24,15,15,-1);binary(26,'and',15,15,14);store(28,15,12,12)
        e(30,'fence.i');load(34,15,13,ptr);lui(38,13,8192);e(40,'slli',rd=22,rs1=22,imm=1)
        store(42,13,15,8);store(44,22,15,100);store(48,14,15,12)
    else:raise RuntimeError('unknown closure role')
    return s


def graph(n):
    edges={};calls=[];terminals=[]
    for p,d in n.items():
        tail=d['op']=='jalr' and d['rd']==0
        if d['op']=='jr' or tail:
            qs=[];terminals.append({'pc':hex(p),'kind':'ordinary RET' if d['op']=='jr' and d['rs1']==1 else 'tail transfer','new_link':False})
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beq','bne','beqz','bnez','bltu','blt'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        edges[p]=qs
        if d['op'] in ('jal','jalr','call_indirect') and not tail:
            target=hex(d['target']) if d['op']=='jal' else 'fresh register target & ~1' if d['op']=='call_indirect' else hex((p-4+n[p-4]['imm']+d['imm'])&0xfffffffe)
            calls.append({'pc':hex(p),'link':hex(p+d['size']),'target':target,'normal_return_and_preservation_proved':False})
    return edges,calls,terminals


def window(raw,role,entry,index,setter,digest):
    _,off,size,count=next(d for d in PARTS if d[0]==role)
    if role=='arithmetic':
        check(all(int.from_bytes(raw[o:o+4],'little')&0xfe00707f==0x02003033 for o in (44,98)),'closure exact MULHU opcode fields')
        check(all(int.from_bytes(raw[o:o+4],'little')&0x707f==0x5003 for o in (0,4,48)),'closure unsigned halfword fields')
    if role=='footer':check(raw[30:34]==bytes.fromhex('0f100000'),'closure exact FENCE.I encoding')
    n=decode(raw,entry+off);s=specs(role,entry,index,setter);check(set(n)==set(s),'closure whole boundaries '+role)
    for p,f in s.items():init.g(n,p,'closure '+role+' operand '+hex(p-entry-off),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'closure window identity '+role)
    edges,calls,terminals=graph(n)
    return {'start':hex(entry+off),'end_exclusive':hex(entry+off+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'calls':calls,'terminal_edges':terminals,
        'reused_loaded_source_spec':role in ('selection','alternative','bypass')}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,p) in enumerate(zip(carriers,parent['profiles'])):
        source=int(p['flash_entry'],16);entry=int(p['mapped_entry'],16);lh=loaded.DETAILS[i][-1]
        hashes=(NEW_HASHES[i][0],lh[0],NEW_HASHES[i][1],lh[1],lh[2]);bodies={}
        setter_source=(0x409fa,0x40a3a)[i]
        for j,(role,off,size,count) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size);bodies[role]=window(raw,role,entry,i,0x2000078a,hashes[j])
            window(raw,role,source,i,setter_source,hashes[j])
        raw=init.binding.take(data,source,978);n=decode(raw,entry)
        check(len(n)==321 and sha256(raw).hexdigest()==WHOLE_HASHES[i],'complete callback original identity')
        merged={int(k,16):[int(q,16) for q in qs] for k,qs in p['combined_CFG'].items()}
        for b in bodies.values():
            for k,qs in b['conditional_CFG'].items():check(int(k,16) not in merged,'closure fragments overlap');merged[int(k,16)]=[int(q,16) for q in qs]
        edges,calls,terminals=graph(n);check(edges==merged and set(n)==set(merged),'whole decoder matches all pinned fragment CFGs')
        check(not {q for qs in edges.values() for q in qs if q not in n},'complete local CFG has no cuts')
        check(sum(d['size'] for d in n.values())==978 and max(n)+n[max(n)]['size']==entry+978,'complete byte interval coverage')
        seen=set()
        def visit(v):
            if v in seen:return
            seen.add(v)
            for q in edges[v]:visit(q)
        visit(entry);check(seen==set(n),'all complete callback nodes locally reachable')
        cycles=[c for c in previous.previous.previous.components(edges) if len(c)>1 or c[0] in edges[c[0]]]
        check(cycles==[[int(x,16) for x in c] for c in p['cyclic_SCC_nodes']],'exact 3/41-node SCCs unchanged')
        check([t['pc'] for t in terminals]==[hex(entry+374),hex(entry+852),hex(entry+974)],'three exact terminal instructions')
        ar=bodies['arithmetic']['calls'];check([c['target'] for c in ar]==[('0x6df1a','0x6e10a')[i]]*3+[('0x63eda','0x63fc4')[i]],'closure mapped helper targets')
        mulhu=[d for d in n.values() if d['op']=='mulhu'];check([(x['rd'],x['rs1'],x['rs2']) for x in mulhu]==[(11,10,18),(15,10,18)],'two exact MULHU forms')
        profiles.append({'label':p['label'],'flash_start':hex(source),'flash_end_exclusive':hex(source+978),
            'mapped_start':hex(entry),'mapped_end_exclusive':hex(entry+978),'whole_bytes':978,'whole_instructions':321,
            'whole_sha256':WHOLE_HASHES[i],'closing_fragments':bodies,'whole_CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},
            'calls':calls,'terminal_edges':terminals,'cyclic_SCC_nodes':p['cyclic_SCC_nodes'],'unresolved_local_cuts':[],
            'fresh_global_byte_source':hex(0x20003000+PARAMS[i][0]),'footer_pointer_source_word':hex(0x20003000+PARAMS[i][5]),
            'footer_byte5_destination':hex(0x20003000+PARAMS[i][6]+7),
            'callee_effects_actual_binding_runtime_reachability_or_termination_proved':False})
    return {'schema':'TSL9-RAM-callback-closure-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'2 complete original callback bodies1956B/642instructions; final gaps504B/158instructions comprise newly pinned380B/118instructions +reused124B/40instructions',
        'closure_means':'original byte interval, operands and conditional-normal-return local CFG are closed; transitive callees/runtime behavior are not closed',
        'MULHU_contract':['unsigned high32(x*y); together with MUL low32 yields exact unsigned word pair',
            'before first helper pair(A1:A0)=incomingDifference*1000000, A2=fresh factor,A3=0; no local factor-zero guard',
            'second helper receives low32(then-live S4*S5),A1=0,A2=1000000,A3=0',
            'only returnedA0 from second helper controls third helper; on nonzero path form returned(A1:A0)*then-live S2 modulo2^64',
            'after third helper low16(then-live S4-returnA0) ->field34; no helper semantic or return ABI proof'],
        'threshold_contract':'wrapping-million Q<=4294 plus fresh U8 global <=255 gives threshold<=4549; unsigned threshold<incomingA0 ->finaltail; continuing nonzero-difference path has1<=incomingA0<=4549',
        'footer_contract':['fresh P1 from pointer-source word; writebyte5 to nominal state+7; fresh V=U32[P1+12]; SW(V&ffffdfff)->[P1+12]',
            'FENCE.I original operand, not executed or treated as synchronization/identity proof',
            'fresh P2 from same pointer-source word; write2000hex->[P2+8]; low32(S6<<1)->[P2+100]; originalunmaskedV->[P2+12]',
            'P1=P2 and finalfield12-cleared properties are unproved'],
        'premises':['actual installed candidate/mapping and valid conditional Xwchc ISA/code/object/frame accesses',
            'all calls must return normally with required registers/saved words/data preserved for local CFG fallthroughs to occur',
            'fresh source values may differ, aliases/interrupts/reentry/writers remain unknown; no hardware or FENCE.I effect inferred',
            'word-pair arithmetic does not identify callee division/copy/ownership ABI; raw pointer validity and referent lifetime unknown'],
        'remaining':['transitive local helpers and arithmetic word-pair service','complete config gates/copy semantics and actual binding',
            'object/global producers and practical field bounds','hardware effects, registration order, termination and frame/payload lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    def limbs(x,y):
        a,b=x&65535,x>>16;c,d=y&65535,y>>16;t=a*c
        mid=(t>>16)+(b*c&65535)+(a*d&65535)
        return ((b*d+(b*c>>16)+(a*d>>16)+(mid>>16))&MASK,(t&65535)|((mid&65535)<<16))
    values=(0,1,65535,65536,0x7fffffff,0x80000000,MASK);pairs=[(x,y) for x in values for y in values]
    state=0x4160
    for _ in range(4096):
        state=(1664525*state+1013904223)&MASK;x=state;state=(1664525*state+1013904223)&MASK;pairs.append((x,state))
    for x,y in pairs:
        hi,lo=limbs(x,y);check((hi<<32)|lo==x*y,'unsigned high/low limb oracle')
    for delta in range(1,4550):
        hi,lo=limbs(delta,1000000);check((hi<<32)|lo==delta*1000000 and hi<=1,'bounded first MULHU pair')
    for lo,hi,factor in ((MASK,MASK,1000000),(0,1,MASK),(0x80000000,7,123),(1,0,0)):
        high=((factor*hi)&MASK)+((factor*lo)>>32);low=factor*lo&MASK
        check(((high&MASK)<<32)|low==((((hi<<32)|lo)*factor)&((1<<64)-1)),'second word-pair product modulo64')
    check(init.timer.encode('sh',10,8,34)==0xb02a,'final field34 QK truncating store')
    changes=(((0,1<<14),(34,1<<20),(40,1<<12),(44,1<<12),(44,1<<15),(64,1<<20),(98,1<<15),(128,4),(130,4)),
        ((4,4),(8,1<<12)),((4,1<<20),(18,4),(28,4),(30,1<<20),(34,1<<20),(48,4)),((10,1<<20),(14,4)),((0,4),(6,1<<20)))
    count=0
    for i,(data,d) in enumerate(zip(carriers,previous.previous.previous.prefix.DETAILS)):
        source=d[0];lh=loaded.DETAILS[i][-1];hashes=(NEW_HASHES[i][0],lh[0],NEW_HASHES[i][1],lh[1],lh[2])
        for j,(role,off,size,n) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size)
            for at,flip in changes[j]:
                b=bytearray(raw);width=decode(raw,source+off)[source+off+at]['size'];b[at:at+width]=(int.from_bytes(b[at:at+width],'little')^flip).to_bytes(width,'little')
                try:window(b,role,source,i,(0x409fa,0x40a3a)[i],hashes[j])
                except RuntimeError as e:check(str(e) in ('closure '+role+' operand '+hex(at),'closure exact MULHU opcode fields','closure unsigned halfword fields','closure exact FENCE.I encoding'),'specific closure mutation guard '+str(e))
                else:raise RuntimeError('closure mutation escaped')
                count+=1
    check(count==42,'closure mutation census')
    print('PASS: 4145 host unsigned-limb products +4549 bounded products; word-pair algebra; 42 specified operand mutations rejected')


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
    else:check(OUT.read_bytes()==output,'complete callback exact ledger replay')
    print('PASS: each callback978B/321instructions, whole hashes and all operands/byte coverage; no local cuts; 3/41-node SCCs and 3 terminals')
    print('PASS: exact ledger; NO target execution; callee semantics/MMIO/FENCE effects/termination/installed binding UNPROVED')


if __name__=='__main__':main()
