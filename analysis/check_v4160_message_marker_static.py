"""Conditional message-header -> APP descriptor -> callback ownership edges.

Static bytes/operands and host algebra only. Calls are opaque boundaries;
no target instruction, allocator, provider, synthetic heap or MMIO executes.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_allocator_static as release

timer,outer,binding = release.timer,release.outer,release.binding
ROOT,LIB,MASK = release.ROOT,release.LIB,0xffffffff
ENTRY,CORE,LENGTH = 0x20000236,0x20000040,86
OUT = Path(__file__).with_name('v4160-message-marker-static.json')
MSG = bytes.fromhex('411126c24ac0b744024006c622c403a9c42023a604200f10000009e923a62421b240224492440249410182802a842105bd654205c18d4181c93b11c9fd572320050042a17ca123a624212105d1bf23a624210145f1b7')
MSG_SHA = 'dd02b794304fe9ae8b45e6cc3a888820393e679d5d3870a95a2a021fc0070faa'
APP_BODIES = (
 (0x13660,0x136d0,'101aa514b5384a875ac5d0aed78902d5b371c24317897dff9643d090b5089392'),
 (0x136d0,0x13740,'27451c9e0ed74db53f6a1b5c627ef1dd69adb646727695f2d322d2708db5d16a'),
 (0x13740,0x137c0,'d07d4c09659a93ad967d73787a5735d8eadfad01f2bafc932ea0542ee06de6d9'),
 (0x13f36,0x13f66,'4eb573901c294659d125c03c49154ec9d5ce89cb6c4775e58df5572097667ed9'))
check,sx = timer.check,timer.sx


def decode(raw,start):
    nodes,off = {},0
    while off < len(raw):
        h = int.from_bytes(raw[off:off+2],'little'); size = 2 if h&3!=3 else 4
        check(off+size<=len(raw),'message partial instruction')
        pc,chunk = start+off,raw[off:off+size]
        w = int.from_bytes(chunk,'little')
        d = {'pc':pc,'bytes':chunk.hex(),'size':size}
        def emit(op,**f): d.update(op=op,**f)
        if size == 4 and w&127 == 0x17: emit('auipc',rd=w>>7&31,imm=w&0xfffff000)
        elif size == 4 and w&127 == 0x6f:
            v = (w>>31)<<20|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
            emit('jal',rd=w>>7&31,target=(pc+sx(v,21))&MASK)
        elif size == 2:
            q,f,r,b = h&3,h>>13,h>>7&31,h>>2&31
            if q==2 and f==6:
                emit('store',rs1=2,rs2=b,width=4,imm=(h>>9&15)<<2|(h>>7&3)<<6)
            elif q==2 and f==2 and r:
                emit('load',rd=r,rs1=2,width=4,imm=(h>>12&1)<<5|(h>>4&7)<<2|(h>>2&3)<<6)
            elif q==2 and f==4 and h&0x1000 and not b and r: emit('call_indirect',rd=1,rs1=r)
            elif q==1 and f==1: emit('jal',rd=1,target=outer.cjal(chunk,0,pc))
            elif q==1 and f==3 and r==2:
                imm=(h>>12&1)<<9|(h>>6&1)<<4|(h>>5&1)<<6|(h>>3&3)<<7|(h>>2&1)<<5
                emit('addi',rd=2,rs1=2,imm=sx(imm,10))
            elif q==1 and f==4 and not h&0x1000 and h>>10&3==3 and h>>5&3==2:
                r = 8+(h>>7&7)
                emit('or',rd=r,rs1=r,rs2=8+(h>>2&7))
        if 'op' not in d: d = release.decode(chunk,pc)[pc]
        nodes[pc] = d; off += size
    return nodes


def guard(nodes,p,message,**fields):
    check(p in nodes and all(nodes[p].get(k)==v for k,v in fields.items()),message)


def message_specs():
    rows = [
      (0,'addi',dict(rd=2,rs1=2,imm=-16)),(2,'store',dict(rs2=9,rs1=2,imm=4,width=4)),
      (4,'store',dict(rs2=18,rs1=2,imm=0,width=4)),(6,'lui',dict(rd=9,imm=0x40024000)),
      (10,'store',dict(rs2=1,rs1=2,imm=12,width=4)),(12,'store',dict(rs2=8,rs1=2,imm=8,width=4)),
      (14,'load',dict(rd=18,rs1=9,imm=524,width=4)),(18,'store',dict(rs2=0,rs1=9,imm=524,width=4)),
      (22,'fence.i',{}),(26,'bnez',dict(rs1=10,target=ENTRY+44)),
      (28,'store',dict(rs2=18,rs1=9,imm=524,width=4)),
      (32,'load',dict(rd=1,rs1=2,imm=12,width=4)),(34,'load',dict(rd=8,rs1=2,imm=8,width=4)),
      (36,'load',dict(rd=9,rs1=2,imm=4,width=4)),(38,'load',dict(rd=18,rs1=2,imm=0,width=4)),
      (40,'addi',dict(rd=2,rs1=2,imm=16)),(42,'jr',dict(rs1=1)),
      (44,'mv',dict(rd=8,rs2=10)),(46,'addi',dict(rd=10,rs1=10,imm=8)),
      (48,'lui',dict(rd=11,imm=0xf000)),(50,'slli',dict(rd=10,rs1=10,imm=16)),
      (52,'or',dict(rd=11,rs1=11,rs2=8)),(54,'srli',dict(rd=10,rs1=10,imm=16)),
      (56,'jal',dict(rd=1,target=CORE)),(58,'beqz',dict(rs1=10,target=ENTRY+78)),
      (60,'li',dict(rd=15,imm=-1)),(62,'store',dict(rs2=0,rs1=10,imm=0,width=4)),
      (66,'store',dict(rs2=8,rs1=10,imm=4,width=2,mnemonic='qk.c.sh')),
      (68,'store',dict(rs2=15,rs1=10,imm=6,width=1,mnemonic='qk.c.sb')),
      (70,'store',dict(rs2=18,rs1=9,imm=524,width=4)),
      (74,'addi',dict(rd=10,rs1=10,imm=8)),(76,'jump',dict(target=ENTRY+32)),
      (78,'store',dict(rs2=18,rs1=9,imm=524,width=4)),(82,'li',dict(rd=10,imm=0)),
      (84,'jump',dict(target=ENTRY+32))]
    return {ENTRY+off:dict(op=op,**f) for off,op,f in rows}


def app_contract(app):
    bodies,all_nodes = [],{}
    for lo,hi,digest in APP_BODIES:
        raw = app[lo-binding.BASE:hi-binding.BASE]
        check(len(raw)==hi-lo,'descriptor APP range')
        nodes = decode(raw,lo); all_nodes.update(nodes)
        bodies.append({'start':hex(lo),'end_exclusive':hex(hi),'bytes':len(raw),
            'sha256':sha256(raw).hexdigest(),'expected_sha256':digest,'instructions':list(nodes.values())})
    n = all_nodes
    builders = []
    for start,call,tag,source,save,reg,fail,tail,branch,ret in (
      (0x13660,0x13672,0xab,96,0x13688,0x136ac,0x136b6,0x136c4,0x13674,0x136c6),
      (0x136d0,0x136e2,0xba,88,0x136f8,0x1371c,0x13726,0x13734,0x136e4,0x13736),
      (0x13740,0x13756,0xb9,None,0x13768,0x1379c,0x137a6,0x137b4,0x13758,0x137b6)):
        guard(n,start,'builder allocation slot base',op='lui',rd=15,imm=0x40000)
        guard(n,start+4,'builder allocation slot',op='load',rd=15,rs1=15,imm=112,width=4)
        guard(n,start+16,'builder allocation length',op='li',rd=10,imm=12)
        guard(n,call,'builder allocation call',op='call_indirect',rd=1,rs1=15)
        guard(n,branch,'builder allocation null branch',op='beqz',rs1=10,target=ret)
        tagpc = call+4 if start!=0x13740 else 0x1375c
        guard(n,tagpc,'builder descriptor marker value',op='addi',rd=15,rs1=0,imm=tag-256)
        guard(n,tagpc+4,'builder descriptor marker offset',op='store',rs1=10,rs2=15,imm=2,width=1)
        guard(n,save,'builder saved descriptor',op='mv',rd=8,rs2=10)
        idpc = save-4
        guard(n,idpc,'builder identifier store',op='store',rs1=10,rs2=9,imm=0,width=2)
        lengthpc = 0x1377a if start==0x13740 else save+4
        guard(n,lengthpc,'builder descriptor size value',op='addi',rd=15,rs1=0,imm=256)
        guard(n,lengthpc+4,'builder descriptor size offset',op='store',rs1=8 if start==0x13740 else 10,rs2=15,imm=8,width=2)
        if source is not None:
            guard(n,save-10,'builder source GP offset',op='addi',rd=15,rs1=3,imm=source)
            guard(n,save-6,'builder source word',op='load',rd=15,rs1=15,imm=0,width=4)
            guard(n,save+2,'builder source store',op='store',rs1=10,rs2=15,imm=4,width=4)
        guard(n,reg-12,'builder descriptor argument',op='mv',rd=13,rs2=8)
        guard(n,reg-10,'builder registration flag',op='li',rd=11,imm=0)
        a,b=n[reg-8],n[reg-4]
        check(a['op']=='auipc' and a['rd']==10 and b['op']=='addi' and b['rd']==10 and b['rs1']==10 and
              ((reg-8+a['imm']+b['imm'])&MASK)==0x13f36,'builder callback key')
        guard(n,reg,'builder registration call',op='jal',rd=1,target=0x9124)
        guard(n,reg+4,'builder registration result branch',op='beqz',rs1=10,target=ret)
        guard(n,fail-4,'builder failure deallocate base',op='lui',rd=15,imm=0x40000)
        guard(n,fail,'builder failure deallocate pointer',op='mv',rd=10,rs2=8)
        guard(n,tail-6,'builder failure deallocate slot',op='load',rd=6,rs1=15,imm=104,width=4)
        guard(n,tail,'builder failure deallocate tail',op='jr',rs1=6)
        builders.append({'entry':hex(start),'allocate_call':hex(call),'request':12,'allocate_slot':'0x40070',
            'descriptor_marker_offset':2,'descriptor_marker':tag,'source_GP_offset':source,
            'register_call':hex(reg),'register_key':'0x13f36','register_flag':0,
            'register_payload':'D returned by slot40070, held in S0','failure_free_slot':'0x40068',
            'provider_return_and_saved_frame_preservation_assumed':True})
    for pc,imm in ((0x1376c,104),(0x13772,100)):
        guard(n,pc,'third builder selected GP offset',op='addi',rd=15,rs1=3,imm=imm)
    guard(n,0x13770,'third builder source selector',op='bnez',rs1=11,target=0x13776)
    guard(n,0x13776,'third builder source word',op='load',rd=15,rs1=15,imm=0,width=4)
    guard(n,0x13778,'third builder source store',op='store',rs1=8,rs2=15,imm=4,width=4)
    for pc,target in ((0x13694,0x135e6),(0x13704,0x135e6),(0x13784,0x135e6)):
        guard(n,pc,'builder delay helper call',op='jal',rd=1,target=target)
    for pc,reg,imm,width in ((0x13f40,13,8,2),(0x13f44,12,4,4),(0x13f46,11,2,1),(0x13f4a,10,0,2)):
        guard(n,pc,'callback descriptor read',op='load',rd=reg,rs1=10,imm=imm,width=width)
    guard(n,0x13f36,'callback null branch',op='beqz',rs1=10,target=0x13f64)
    guard(n,0x13f3e,'callback saved descriptor',op='mv',rd=8,rs2=10)
    guard(n,0x13f4e,'callback transfer call',op='jal',rd=1,target=0x13e98)
    guard(n,0x13f52,'callback free base',op='lui',rd=15,imm=0x40000)
    guard(n,0x13f56,'callback original pointer to free',op='mv',rd=10,rs2=8)
    guard(n,0x13f5c,'callback free slot',op='load',rd=6,rs1=15,imm=104,width=4)
    guard(n,0x13f62,'callback free tail',op='jr',rs1=6)
    return bodies,builders


def derive(app,carriers,header):
    matches = {}
    for name,index in ((b'tmos_msg_allocate',15),(b'tmos_msg_send',12)):
        m = re.search(rb'^#define\s+'+name+rb'\s+[^\r\n]*BLE_LIB_JT\(\s*(\d+)\s*\)',header,re.M)
        check(m is not None and int(m[1])==index,'message header JT identity')
        matches[name.decode()] = {'JT':index,'slot':hex(0x40034+4*index)}
    bodies,builders = app_contract(app)
    profiles = []
    for data,(label,_,_,_,_),src in zip(carriers,binding.PROFILES,(0x404a6,0x404e6)):
        check(binding.word(data,0x40070)==ENTRY,'message allocation entry slot')
        mapping = binding.profile(data,label)
        first = {k:int(v,16) for k,v in mapping['first_copy'].items()}
        check(first['destination']<=CORE<=ENTRY and ENTRY+LENGTH<=int(mapping['first_copy_end_exclusive'],16) and
              first['source']+ENTRY-first['destination']==src,'message complete first-copy source mapping')
        raw = binding.take(data,src,LENGTH); nodes=decode(raw,ENTRY); specs=message_specs()
        check(nodes.keys()==specs.keys(),'message instruction boundaries')
        for pc,fields in specs.items(): guard(nodes,pc,'message instruction '+hex(pc-ENTRY),**fields)
        check(raw==MSG,'message full body template')
        check(not any(d.get('rd')==12 for d in nodes.values()),'message A2 not written')
        profiles.append({'label':label,'slot':'0x40070','target':hex(ENTRY),'load_image_source':hex(src),
            'bytes':LENGTH,'sha256':sha256(raw).hexdigest(),'expected_sha256':MSG_SHA,
            'instructions':list(nodes.values()),'core_call':{'pc':hex(ENTRY+56),'target':hex(CORE),
                'link':hex(ENTRY+58),'conditional_source':hex(first['source']+CORE-first['destination']),
                'A0':'(full_input_L + 8) & 0xffff','A1':'0xf000 | full_input_L','A2':'not written by wrapper',
                'body_or_fallback_contract_proved':False},
            'nonnull_core_suffix_stores':['U32[P+0]=0','U16[P+4]=live_S0','U8[P+6]=255'],
            'return_nonnull_core':'D=(P+8)&0xffffffff; D may wrap to zero',
            'marker_relation':'((D-2)&0xffffffff)==((P+6)&0xffffffff)',
            'installed_binding_proved':False,'code_frame_header_nonalias_proved':False,
            'normal_core_live_S0_S1_S2_SP_and_frame_preservation_assumed':True})
    return {'schema':'TSL9-message-marker-static-v1','profile':timer.PROFILE,
        'scope':'Static bytes/operands and conditional data-flow boundaries, no target ISA/heap/MMIO execution',
        'installed_binding_proved':False,'header_JT':matches,'profiles':profiles,
        'APP_bodies':bodies,'APP_builders':builders,
        'descriptor_plus2_equals_allocator_minus2':False,
        'conditional_APP_request12_core_arguments':{'A0':20,'A1':'0xf00c','header_U16_length':12},
        'callback_execution_or_single_free_proved':False,
        'required_premises':['matching installed profile and final code bytes','normal opaque-call returns with live context and saved frame intact',
            'valid stable accesses and code/frame/header/descriptor nonalias','same D delivered by scheduler with no ownership-changing intervention']}


def tests(app,carriers,header):
    wraps = []
    for length in range(1,65536):
        arg=(length+8)&65535
        check(arg==(length+8 if length<65528 else length-65528),'message U16 request algebra')
        if arg<8: wraps.append(length)
    check(wraps==list(range(65528,65536)),'message eight wrapped typed requests')
    for p in (1,0x1000,0xfffffff0,0xfffffff8,0xfffffffc,0xffffffff):
        d=(p+8)&MASK
        check((d-2)&MASK==(p+6)&MASK,'message modulo marker relation')
    check((0xfffffff8+8)&MASK==0,'message nonnull P can wrap return to zero')
    cases=(
      ('carrier',0x404a6+68,'7ca1','5ca1','message instruction 0x44'),
      ('carrier',0x404a6+66,'42a1','62a1','message instruction 0x42'),
      ('carrier',0x404a6+74,'2105','3105','message instruction 0x4a'),
      ('app',0x13664,'bc5b','bc57','builder allocation slot'),
      ('app',0x13670,'3145','3545','builder allocation length'),
      ('app',0x1367a,'2301f500','a301f500','builder descriptor marker offset'),
      ('app',0x136a0,'a286','a686','builder descriptor argument'),
      ('app',0x13f46,'83452500','83456500','callback descriptor read'))
    for kind,pc,before,after,message in cases:
        a,cs=bytearray(app),[bytearray(c) for c in carriers]
        data,off=(a,pc-binding.BASE) if kind=='app' else (cs[0],pc-LIB)
        old,new=bytes.fromhex(before),bytes.fromhex(after)
        check(data[off:off+len(old)]==old,'message mutation pin')
        data[off:off+len(new)]=new
        try: derive(a,cs,header)
        except RuntimeError as error: check(str(error)==message,'unexpected marker mutation guard: '+str(error))
        else: raise RuntimeError('message marker mutation escaped')
    print('PASS: 65535 typed nonzero lengths; 8 wrapping request sizes; 6 pointer identities; 8 specified raw mutations')


def main():
    p=argparse.ArgumentParser(); p.add_argument('--write',action='store_true',help='Create ledger exclusively')
    options=p.parse_args()
    app,header=binding.APP.read_bytes(),outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,n,digest in binding.PROFILES:
        raw=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==n and sha256(raw).hexdigest()==digest,'candidate identity '+label); carriers.append(raw)
    sources,vectors=timer.source_contract()
    ledger=derive(app,carriers,header); ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    for b in ledger['APP_bodies']+ledger['profiles']: check(b['sha256']==b['expected_sha256'],'message complete body identity')
    tests(app,carriers,header)
    output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    if options.write:
        with OUT.open('xb') as f: f.write(output)
    else: check(OUT.read_bytes()==output,'message marker ledger exact replay')
    print('PASS: 2 complete message wrappers (172 bytes), 3 APP builders + callback (400 bytes); marker/descriptor/free-pointer edges')
    print('PASS: ledger exact replay; installed/core/payload lifetime UNPROVED; NO ISA/provider/MMIO execution')


if __name__=='__main__': main()
