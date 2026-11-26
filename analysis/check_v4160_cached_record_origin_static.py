"""Row18 length/tag source, selected mode1 path and initialization intervals.

Two complete leaves plus explicitly bounded caller/prefix windows; not a full
mode dispatcher or writer census. Bytes/CFG/host algebra only, no target ISA,
provider, reset, copy, RAM, stack or MMIO execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_tagged_dispatch_static as previous
import check_v4160_app_jt0_call_chain_static as boot

init,sparse,check,take,decode=previous.init,previous.sparse,previous.check,previous.take,previous.decode
MASK=0xffffffff
OUT=Path(__file__).with_name('v4160-cached-record-origin-static.json')
DETAILS=(('getter',0x829e,10,3,0,'237f5833a80ead32ef214fce5c360966f882b57191ef5e76b99e9c855a243c5e'),
 ('row',0x82a8,42,16,0,'28d890ee09b7d7eb6f4565cd0829521eae728973a961d142a817c80901f94af0'),
 ('outer',0x14d2e,36,14,2,'7cccfae657ff1a3caa145a05f39f149fe74d8e87d3d5a1942ce3bfd62bcce1d2'),
 ('id819',0x14d5e,16,4,0,'e1c63a6f911dde7323193349b65177b884379167755980ce9b10cdd1e1492c7d'),
 ('id991',0x14ed8,12,3,0,'f2f2324e7622dc5d4b48689d5488e37addc9ce0adab43b1d76d27f4c35aa4df8'),
 ('id1025',0x14fa0,12,3,0,'ec9e402977bd50d78f254de8774a37654cb6acf8216275589a42d0eecccf88b6'),
 ('id1267',0x15002,12,3,0,'d4c7a12a92ec716d28096689090c8299b8e9dd8a881986552f670baee9ecde69'),
 ('id1657',0x15032,8,2,0,'b37c5400fcf2de5960ab35e7aedd0e50c4633d7c7b71affddafcfc7a1592c9ff'),
 ('case',0x152ba,22,9,0,'09c9b54ca6b7c18655ec21e63f4d55719da2901be8d25e8f3468b9ad58ab4f29'),
 ('init_prefix',0x12d92,46,16,2,'3a5b3696eb2953d42a84112ce85447053299252d05b152781dd7b89b0138abc4'))


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v=0,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v=0,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def mv(o,r,a):e(o,'mv',rd=r,rs2=a)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=t)
    if role=='getter':e(0,'auipc',rd=10,imm=0x20004000);load(4,10,10,-745,1);e(8,'jr',rs1=1)
    elif role=='row':
        e(0,'lui',rd=15,imm=0x40000);load(4,6,15,76);li(8,15,12);binary(10,'mul',11,11,15)
        e(14,'auipc',rd=15,imm=0x20004000);addi(18,15,15,-254);mv(22,14,12);li(24,12,12);binary(26,'add',15,15,11)
        e(28,'beqz',rs1=10,target=0x82cc);mv(30,11,15);mv(32,10,14);e(34,'jr',rs1=6)
        mv(36,11,14);mv(38,10,15);e(40,'jump',target=0x82ca)
    elif role=='outer':
        addi(0,2,2,-16);store(2,8,2,8);store(4,1,2,12);mv(6,8,10);e(8,'jal',rd=1,target=0x829e)
        li(12,15,6);branch(14,'bltu',15,10,0x1549a);e(18,'auipc',rd=14,imm=0x6000);addi(22,14,14,-1672)
        e(26,'slli',rd=10,rs1=10,imm=2);binary(28,'add',10,10,14);load(30,15,10);binary(32,'add',15,15,14);e(34,'jr',rs1=15)
    elif role=='id819':
        load(0,15,8,0,2);addi(4,14,0,819);branch(8,'beq',15,14,0x15176);branch(12,'bltu',14,15,0x14ed8)
    elif role in ('id991','id1025','id1267'):
        value,equal,above={'id991':(991,0x1525c,0x14fa0),'id1025':(1025,0x1527e,0x15002),
                           'id1267':(1267,0x152ae,0x15032)}[role]
        addi(0,14,0,value);branch(4,'beq',15,14,equal);branch(8,'bltu',14,15,above)
    elif role=='id1657':addi(0,14,0,1657);branch(4,'beq',15,14,0x152ba)
    elif role=='case':
        mv(0,12,8);li(2,10,0);li(4,11,18);e(6,'jal',rd=1,target=0x82a8);mv(10,10,8)
        load(12,8,2,8);load(14,1,2,12);addi(16,2,2,16);e(18,'jal',rd=0,target=0xc6a8)
    elif role=='init_prefix':
        addi(0,2,2,-48);store(2,8,2,40);e(4,'lui',rd=8,imm=0x40000);load(8,15,8,72);store(10,1,2,44)
        addi(12,12,0,384);li(16,11,0);e(18,'auipc',rd=10,imm=0x1fff9000);addi(22,10,10,660)
        e(26,'call_indirect',rd=1,rs1=15);load(28,15,8,72);addi(30,12,0,228);li(34,11,0)
        e(36,'auipc',rd=10,imm=0x1fff9000);addi(40,10,10,1026);e(44,'call_indirect',rd=1,rs1=15)
    else:raise RuntimeError('unknown cached-origin role')
    return s


def window(raw,role,pc,size,count,stores,digest):
    n=decode(raw,pc);expected=specs(role,pc);check(set(n)==set(expected),'origin complete window boundaries '+role)
    for p,f in expected.items():init.g(n,p,'origin '+role+' instruction '+hex(p-pc),**f)
    edges={};external=[];calls=[]
    for p,d in n.items():
        if d['op']=='jr':
            qs=[]
            if d['rs1']!=1:
                check((role,d['rs1']) in (('row',6),('outer',15)),'origin typed indirect exit')
                external.append({'pc':hex(p),'kind':'indirect tail','target':'captured T1 & ~1' if role=='row' else 'table word plus table base & ~1'})
        elif d['op']=='jump' or (d['op']=='jal' and d['rd']==0):qs=[d['target']]
        elif d['op'] in ('bltu','beq','beqz'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        for q in qs:
            if q not in n:external.append({'pc':hex(p),'target':hex(q),'kind':'bounded continuation' if q==pc+size else 'branch/tail outside window'})
        edges[p]=qs
        if d['op']=='call_indirect' or (d['op']=='jal' and d['rd']==1):calls.append({'pc':hex(p),
            'target':hex(d['target']) if 'target' in d else 'fresh A5 & ~1','link':hex(p+d['size']),'normal_return_proved':False})
    seen=set();active=set()
    def visit(p):
        if p not in n:return
        check(p not in active,'origin acyclic window '+role)
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'origin full window reachability '+role)
    actual=[d for d in n.values() if d['op']=='store']
    check((len(raw),len(n),len(actual),sha256(raw).hexdigest())==(size,count,stores,digest),'origin complete window identity '+role)
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,
        'complete_body':role in ('row','getter'),'instructions':list(n.values()),'stores':actual,'calls':calls,
        'external_edges':external,'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()}}


def sx(x,bits):return (x^(1<<(bits-1)))-(1<<(bits-1))


def adjacent_candidates(app,lo,hi):
    """Explicit raw syntactic domain; data/interior candidates are not CFG xrefs."""
    hits=[]
    for off in range(0,len(app)-5,2):
        w=int.from_bytes(app[off:off+4],'little');op=w&127;rd=w>>7&31
        if op not in (0x17,0x37) or rd==0:continue
        p=off+0x8000;upper=(w&0xfffff000)+(p if op==0x17 else 0)
        h=int.from_bytes(app[off+4:off+6],'little');v=int.from_bytes(app[off+4:off+8],'little');kind=None;width=0
        if h&3==3 and off+8<=len(app) and v>>15&31==rd:
            op2=v&127;f=v>>12&7
            if op2==0x13 and f==0:kind='ADDI';imm=sx(v>>20,12)
            elif op2==3 and f in (0,1,2,4,5):kind='load';imm=sx(v>>20,12);width={0:1,1:2,2:4,4:1,5:2}[f]
            elif op2==35 and f in (0,1,2):kind='store';imm=sx((v>>25<<5)|(v>>7&31),12);width=1<<f
        elif h&0xe003==0x0001 and h>>7&31==rd:
            kind='C.ADDI';imm=sx(((h>>12&1)<<5)|(h>>2&31),6)
        elif h&0xe003 in (0x4000,0xc000) and 8+(h>>7&7)==rd:
            kind='C.LW' if h&0xe003==0x4000 else 'C.SW';width=4
            imm=((h>>10&7)<<3)|((h>>6&1)<<2)|((h>>5&1)<<6)
        if kind is None:continue
        target=(upper+imm)&MASK
        if (lo<=target<hi) or (width and target<lo<target+width):
            hits.append({'upper_pc':hex(p),'next_pc':hex(p+4),'target':hex(target),'form':kind,'width':width})
    return hits


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    windows={r:window(take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in DETAILS}
    check(sum(w['bytes'] for w in windows.values())==216 and sum(len(w['instructions']) for w in windows.values())==73
          and sum(len(w['stores']) for w in windows.values())==4,'origin window census')
    nodes={r:{d['pc']:d for d in b['instructions']} for r,b in windows.items()}
    row=nodes['row'];base=(0x82b6+row[0x82b6]['imm']+row[0x82ba]['imm'])&MASK;obj=(base+18*12)&MASK
    check((base,obj,obj+12)==(0x2000c1b8,0x2000c290,0x2000c29c),'row18 object identity')
    getter=nodes['getter'];mode_addr=(0x829e+getter[0x829e]['imm']+getter[0x82a2]['imm'])&MASK
    outer=nodes['outer'];table=(0x14d40+outer[0x14d40]['imm']+outer[0x14d44]['imm'])&MASK
    table_raw=take(app,table,28);check(table_raw.hex()=='9aa6ffffa6a6ffff02adffff22adffff42adffff82adffffc2adffff','original seven-mode table')
    mode1=(table+int.from_bytes(table_raw[4:8],'little'))&MASK
    check((mode_addr,table,mode1)==(0x2000bfb5,0x1a6b8,0x14d5e),'mode1 getter/table join')
    path=(('id819',819,0x14ed8),('id991',991,0x14fa0),('id1025',1025,0x15002),('id1267',1267,0x15032))
    for role,value,target in path:
        ns=nodes[role];comp=next(d for d in ns.values() if d.get('rd')==14)
        check(comp['imm']==value and list(ns.values())[-1]['target']==target,'selected ID path join '+role)
    check(nodes['id1657'][0x15036]['target']==0x152ba and nodes['case'][0x152c0]['target']==0x82a8
          and nodes['case'][0x152cc]['target']==0xc6a8,'ID1657 case/cache/update joins')
    ns=nodes['init_prefix'];first=(0x12da4+ns[0x12da4]['imm']+ns[0x12da8]['imm'])&MASK
    second=(0x12db6+ns[0x12db6]['imm']+ns[0x12dba]['imm'])&MASK
    check((first,ns[0x12d9e]['imm'],second,ns[0x12db0]['imm'])==(0x2000c038,384,base,228),'two initialization request ranges')
    _,rp,rs,rn,rc,rh=boot.DETAILS[0];reset=boot.body(take(app,rp,rs),'reset',rp,rh,rn,rc)
    bn={d['pc']:d for d in reset['instructions']};gp=(0x186aa+bn[0x186aa]['imm']+bn[0x186ae]['imm'])&MASK
    zero_end=(0x186e2+bn[0x186e2]['imm']+bn[0x186e6]['imm'])&MASK
    check((gp,zero_end)==(0x20004000,0x2000c958) and gp+128<=obj<obj+12<=zero_end,'reset contains complete row18')
    source=(0x186ba+bn[0x186ba]['imm']+bn[0x186be]['imm'])&MASK
    config_word=take(app,source+84,4)
    check(source==0x1ab60 and config_word.hex()=='9cc20020' and int.from_bytes(config_word,'little')==obj+12,
          'reset GP+84 configuration pointer is adjacent to O, not O')
    hits=adjacent_candidates(app,obj,obj+12)
    check(hits==[{'upper_pc':'0xc78c','next_pc':'0xc790','target':'0x2000c290','form':'ADDI','width':0}], 'bounded adjacent object-address candidate census')
    literals={hex(a):[hex(0x8000+i) for i in range(0,len(app)-3,2) if app[i:i+4]==a.to_bytes(4,'little')] for a in (obj,obj+2,obj+11)}
    check(all(not v for v in literals.values()),'no raw aligned object-address words in APP domain')
    return {'schema':'TSL9-cached-record-origin-static-v1','profile':init.timer.PROFILE,
        'scope':'2 complete bodies52B/19instructions/0stores +8 bounded windows164B/54instructions/4stores; full prior reset reused',
        'windows':windows,'revalidated_reset':reset,'mode1_join':{'mode_byte':hex(mode_addr),'table':hex(table),'table_bytes':table_raw.hex(),
            'selected_target':hex(mode1),'selected_ID':1657,'full_mode1_dispatch_or_all_incoming_edges_proved':False},
        'cache_layout':{'base':hex(base),'row_bytes':12,'rows_in_fill_request':19,'selected_index':18,'object':hex(obj),
            'length':hex(obj+2),'tag':hex(obj+11),'next_config':hex(obj+12)},
        'row_wrapper':{'direction0':'tail captured fresh4004c(base+12*full_index,entry A2,12)',
            'direction_nonzero':'tail captured fresh4004c(entry A2,base+12*full_index,12)',
            'RV32_modular_index':True,'index_null_extent_guards':False,'no_frame_or_link_write':True},
        'ID1657_case':{'setup':'A2=P in S0,A0=0,A1=18; JAL82a8 at152c0, link152c4',
            'requested_copy':'12 bytes P..P+11 ->O..O+11; includes length+2 and tag+11',
            'field_guards_in_selected_case':[],'copy_scalar_tested':False,
            'normal_continuation':'A0=then-live S0(P), restore saved S0/RA/SP, tailC6a8(P), notC6a8(O)',
            'cached_fields':'only under actual reference copy/access/context/source preservation; not inferred from scalar reply',
            'source_ID_still1657_at_copy_time_proved':False},
        'initialization':{'reset_zero_interval':[hex(gp+128),hex(zero_end)],'row18_zero_store_addresses':[hex(obj+x) for x in (0,4,8)],
            'prefix_requests':[[hex(first),0,384],[hex(second),0,228]],
            'first_request_end':hex(first+384),'second_request_end':hex(second+228),
            'provider_calls':'fresh slot word each time; second base depends on first callee preserving S0; no actual fill or completion claim',
            'source_config_pointer':{'source':hex(source+84),'raw':config_word.hex(),'nominal_copy_destination':hex(gp+84),'value':hex(obj+12)},
            'reset_or_fill_values_retained_until_later_dispatch_proved':False},
        'bounded_scan':{'domain':'all halfword offsets; raw LUI/AUIPC followed immediately by standard ADDI/load/store or C.ADDI/C.LW/C.SW; matching start/overlap only',
            'instruction_boundary_or_execution_evidence':False,'object_candidates':hits,'raw_halfword_aligned_address_words':literals,
            'indirect_nonadjacent_bulk_alias_or_async_writers_excluded':False},
        'cached_consumption_bridge':{'earlier_case':'copyP->O then update/dispatch P, conditional on provider and live S0/frame',
            'later_handoff':'C776 copy7 into GP+220, explicit A0=O tailC6a8; cachedO length/tag not locally assigned by C6a8',
            'prior_state_stores':'only O+4..8; no direct O+2/O+11 store in C6a8',
            'tagged_accepted_cache_path':'if fields/context stay stable and ranges disjoint: nonzero O+2 gate then tagged L0<=8 ->L0 in1..8, tag1/2; L1=L0 still requires copy/provider/noninterference premises',
            'untagged_cache_path':'tag0 can enter record-copy path without local length cap; actual reachable source fields remain unproved',
            'all_byte_field_values_reachable_from_real_ingress_proved':False},
        'premises':['matching original bytes, conditional ISA and valid stack/object/table/provider access',
            'normal return, required S0/SP/RA/frame preservation and no adverse aliases/IRQ/other writers',
            'actual copy/fill binding and effects must be separately established; unknown sources not promoted to observed records',
            'reset/frame intervals are nominal host arithmetic, not hardware execution or exclusive object ownership'],
        'remaining_boundaries':['actual ID1657 ingress source/length/tag guards','other row/object writers and callback ordering',
            'actual copy/fill provider identity and pointer retention','concurrent field changes and object lifetime'],
        'prior_length_stability_boundary':parent['length_preservation'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    selected=[x for x in range(65536) if all(x!=k and x>k for k in (819,991,1025,1267)) and x==1657]
    check(selected==[1657],'selected unsigned ID path intersection')
    base=0x2000c1b8;obj=0x2000c290
    for index in range(19):
        start=base+12*index;check(start+12<=base+228,'all19 row request ranges')
        check((start<=obj+2<start+12)==(index==18) and (start<=obj+11<start+12)==(index==18),'length/tag exact row membership')
    for index in (18,0x40000012,0x80000012,0xc0000012):check((base+12*index)&MASK==obj,'full width row-index modular collision')
    check(base+19*12==obj+12,'index19 enters adjacent configuration interval')
    roles={r:(p,size,count,stores,h) for r,p,size,count,stores,h in DETAILS}
    cases=(('getter',4,1<<20),('row',4,1<<20),('row',8,4),('row',10,1<<20),('row',18,1<<20),
        ('row',28,0x80),('row',38,0x80),('outer',18,1<<12),('outer',30,4),('id819',4,1<<20),
        ('id991',8,0x1000),('id1025',0,1<<20),('id1267',8,0x1000),('id1657',4,0x1000),
        ('case',4,4),('case',10,0x80),('case',18,1<<21),('init_prefix',30,1<<20))
    for role,off,flip in cases:
        pc,size,count,stores,digest=roles[role];raw=bytearray(take(app,pc,size));w=decode(raw,pc)[pc+off]['size']
        raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:window(raw,role,pc,size,count,stores,digest)
        except RuntimeError as e:check(str(e)=='origin '+role+' instruction '+hex(off),'unexpected origin mutation guard '+str(e))
        else:raise RuntimeError('origin mutation escaped')
    print('PASS: 65536 ID path cases; 19 row intervals +4 full-width index aliases; 18 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(app);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'cached record origin exact ledger replay')
    print('PASS: complete bodies52B/19instructions +bounded windows164B/54instructions; ID1657->row18->O length/tag source joined')
    print('PASS: exact ledger bytes; reset/init intervals conditional; NO target execution or complete writer/ingress/provider-lifetime proof')


if __name__=='__main__':main()
