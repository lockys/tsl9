"""Bounded setter callers, flag writer tail, and a direct prefix-to-tail edge.

Original operands, conditional CFG and host address/bit arithmetic only.
No target ISA, RAM/frame, callback, resident, CSR or hardware execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_hook_lifetime_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
decode=previous.previous.decode
OUT=Path(__file__).with_name('v4160-hook-callers-flag-static.json')
SAVED=[(1,60),(8,56),(9,52)]+[(r,48-4*(r-18)) for r in range(18,28)]
CALLERS=(
 ((0x416b8,0x20001000,-688,'608d542c8b53053a2354dfc7d350f1aa6533d03a0e5afaa9c9e6a0b849c31fba'),
  (0x4202a,0x5d000,-1612,'ac5fdd8985930bb743d8dd009ac180d98c6e554f10ff6cd73743495a9f734205'),
  (0x4249e,0x63000,-1756,'ef886d38272e7964ef5495e424710d5240edd51f70644f3db9382b68d48fcf55'),
  (0x424c8,0x63000,-1756,'cbf70d845cc713f7b4998d5de47dc15a3b79b785d6c98645049d36fb73a7393f')),
 ((0x416f8,0x20001000,-688,'608d542c8b53053a2354dfc7d350f1aa6533d03a0e5afaa9c9e6a0b849c31fba'),
  (0x4206a,0x5d000,-1284,'9b3bfd6d90406097bb0447d9ac418d8116ca6880868c23ff4ba766de4149297d'),
  (0x4252a,0x63000,-1522,'d40a9695eb53a36dc6d272fcf1ed07c08f8bc3d20a98b4665ad9230c66f860ba'),
  (0x42554,0x63000,-1522,'aa03eed59a19bc6a4e617ee702c09cbb257de50b9c4d81fdeee5fa961b5b13a8')))
DETAILS=(
 (0x42044,0x42268,1300,1340,-260,0x60734,82,
  '1c3961b3cade9bc2e006e8ec4ca9baa2941f4fcc9eb16b72961dfd7bb76d5ac3',
  '706c380eb91490005bbac643de5c0662caeb464bc77ffd4c7cc8063fad1f8dda',
  '34dd79c2f04f6ec92f2bd529a3d5e8cfa7ad8a4a8766cac43f7399cef2a58607'),
 (0x42084,0x422a8,1380,1420,-180,0x6081e,-152,
  'eae58cb358223e1db1bae83d15eb946ad5fa149c3c388e931378c319e2c62121',
  '2293c2a96b42af339e31532e3300b5483ae8f9e9edf62b477a0f8e3b9b70af1a',
  '2c075c73f7d940e784464d5a955d927e420f52a43b09bece59d9c3bccb8fd7bb'))
PAIR_SITES=((0x54de0,0x56868,0x57ea4,0x5cef4,0x5cf06,0x5cfa8,0x5d6da,0x5d82e,
 0x6030a,0x60738,0x6081c,0x62c5a,0x62c6c,0x62d84,0x62d90,0x632ee,0x63302,0x64534,0x64962,0x64e8e,0x65102,0x65508,0x67b56),
 (0x54eaa,0x569a8,0x57fe4,0x5d03c,0x5d04e,0x5d0f0,0x5d822,0x5d976,
 0x603f4,0x60822,0x60906,0x62d44,0x62d56,0x62e6e,0x62e7a,0x633d8,0x633ec,0x6461e,0x64a4c,0x64f78,0x651ec,0x655f2,0x67c94))


def direct_edges(raw,base,target):
    # The reused raw immediate scanner uses fixed base8000. Translate both
    # its comparison target and output PCs; do not mix carrier/APP addresses.
    delta=base-0x8000
    return [hex(int(p,16)+delta) for p in previous.previous.raw_edges(raw,target-delta)]


def pairs(raw,base,target):
    hits=[]
    for off in range(0,len(raw)-7,2):
        a=int.from_bytes(raw[off:off+4],'little');b=int.from_bytes(raw[off+4:off+8],'little')
        if a&127==0x17 and a>>7&31!=0 and b&0x707f==0x67 and a>>7&31==b>>15&31:
            upper=(a&0xfffff000);upper=(upper^0x80000000)-0x80000000
            low=((b>>20)^2048)-2048
            if (base+off+upper+low)&0xfffffffe==target:hits.append(hex(base+off))
    return hits


def specs(role,pc,args):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v):e(o,'load',rd=r,rs1=b,imm=v,width=4)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    if role=='constant_call':
        upper,low,target=args;e(0,'lui',rd=10,imm=upper);addi(4,10,10,low);e(8,'jal',rd=1,target=target)
    elif role=='clear_tail':
        low=args;e(0,'li',rd=10,imm=0);addi(2,2,2,32);e(4,'auipc',rd=6,imm=0x1ffa0000);e(8,'jalr',rd=0,rs1=6,imm=low)
    elif role=='prefix':
        state_delta,tail=args;addi(0,2,2,-64);store(2,8,2,56);e(4,'lui',rd=8,imm=0x20003000)
        addi(8,15,8,state_delta);load(12,15,15,24);store(14,1,2,60)
        for j,(r,off) in enumerate(SAVED[2:]):store(16+2*j,r,2,off)
        e(38,'slli',rd=14,rs1=15,imm=16);e(42,'bge',rs1=14,rs2=0,target=tail)
    elif role=='writer_tail':
        pointer_delta,flag_delta=args;e(0,'lui',rd=15,imm=0x20003000);load(4,15,15,pointer_delta);load(8,15,15,108)
        e(10,'beqz',rs1=15,target=pc+22);e(12,'lui',rd=15,imm=0x20003000);e(16,'li',rd=14,imm=1)
        store(18,14,15,flag_delta,1)
        for j,(r,off) in enumerate(SAVED):load(22+2*j,r,2,off)
        addi(48,2,2,64);e(50,'jr',rs1=1)
    else:raise RuntimeError('unknown hook caller role')
    return s


def window(raw,role,pc,args,digest):
    n=decode(raw,pc);s=specs(role,pc,args);check(set(n)==set(s),'hook caller boundaries '+role)
    for p,f in s.items():init.g(n,p,'hook caller '+role+' operand '+hex(p-pc),**f)
    count={'constant_call':3,'clear_tail':4,'prefix':19,'writer_tail':22}[role]
    size={'constant_call':12,'clear_tail':12,'prefix':46,'writer_tail':52}[role]
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'hook caller full window hash '+role)
    edges={};external=[]
    for p,d in n.items():
        if d['op']=='jr' or role=='clear_tail' and p==pc+8:qs=[]
        elif d['op'] in ('bge','beqz'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        for q in qs:
            if q not in n:
                check((role in ('prefix','constant_call') and q==pc+size) or (role=='prefix' and q==args[1]),'hook caller explicit cut')
                external.append(hex(q))
        edges[p]=qs
    seen=set()
    def visit(p):
        if p in seen or p not in n:return
        seen.add(p)
        for q in edges[p]:visit(q)
    visit(pc);check(seen==set(n),'hook caller window reachability')
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'cuts':external,
        'complete_containing_function':False,'kind':role}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,d) in enumerate(zip(carriers,DETAILS)):
        pre,tail,state_delta,ptr_delta,flag_delta,zpc,zlow,ph,th,zh=d;p=parent['profiles'][i]
        shift=int(p['first_copy_destination'],16)-int(p['first_copy_source'],16);end=int(p['first_copy_end'],16)
        setter=int(p['setter']['start'],16);setter_source=int(p['flash_setter'],16);flag=0x20003000+flag_delta
        check(flag==int(p['flag'],16),'writer same callback/consumer flag')
        pro=window(init.binding.take(data,pre,46),'prefix',pre+shift,(state_delta,tail+shift),ph)
        suffix=window(init.binding.take(data,tail,52),'writer_tail',tail+shift,(ptr_delta,flag_delta),th)
        window(init.binding.take(data,pre,46),'prefix',pre,(state_delta,tail),ph)
        window(init.binding.take(data,tail,52),'writer_tail',tail,(ptr_delta,flag_delta),th)
        check((pro['start'],suffix['start'])==('0x20001dd4','0x20001ff8') and tail+shift+52<=end,'prefix and tail mapped bounds')
        pn={x['pc']:x for x in pro['instructions']};tn={x['pc']:x for x in suffix['instructions']}
        for r,off in SAVED:
            ss=[x for x in pn.values() if x['op']=='store' and x['rs2']==r and x['rs1']==2 and x['imm']==off]
            ll=[x for x in tn.values() if x['op']=='load' and x['rd']==r and x['rs1']==2 and x['imm']==off]
            check(len(ss)==len(ll)==1,'exact prefix tail saved-register field join')
        callers=[]
        for source,upper,low,h in CALLERS[i]:
            raw=init.binding.take(data,source,12);w=window(raw,'constant_call',source+shift,(upper,low,setter),h)
            window(raw,'constant_call',source,(upper,low,setter_source),h)
            check(source+shift+12<=end,'caller inside complete first copy')
            value=(upper+low)&0xffffffff;check(value!=0,'constant setter arg nonzero')
            callers.append({'flash_source':hex(source),'window':w,'A0':hex(value),'publishes_to':p['hook_slot'],
                'sets_flag_to_one_if_reached':True,'reached_at_runtime_proved':False})
        zr=init.binding.take(data,zpc,12);zero=window(zr,'clear_tail',zpc,zlow,zh)
        check((zpc+4+0x1ffa0000+zlow)&0xfffffffe==setter,'zero argument tail target')
        direct=direct_edges(data,0x40000,setter_source)
        expected=[(0x412cc,0x416c0,0x42032,0x424a6,0x424d0),(0x4130c,0x41700,0x42072,0x42532,0x4255c)][i]
        check(direct==[hex(x) for x in expected],'raw direct setter candidate census')
        adjacent=pairs(data,0x40000,setter);check(adjacent==[hex(x) for x in PAIR_SITES[i]],'raw adjacent setter candidate census')
        check(int(p['first_copy_destination'],16)<=0x20000d50<end,'RAM argument inside first-copy code range')
        profiles.append({'label':p['label'],'mapping_shift':hex(shift),'setter':p['setter']['start'],'hook_slot':p['hook_slot'],'flag':hex(flag),
            'constant_callers':callers,'zero_argument_tail':zero,'zero_tail_target':hex(setter),
            'prefix':pro,'writer_tail':suffix,'prefix_flash':hex(pre),'writer_tail_flash':hex(tail),
            'state_word':hex(0x20003000+state_delta+24),'pointer_source_word':hex(0x20003000+ptr_delta),
            'RAM_argument_flash_source':hex(0x20000d50-shift),
            'raw_only_candidates':{'JAL_CJ_CJAL_to_source_setter':direct,'adjacent_AUIPC_JALR_to_RAM_setter':adjacent,
                'instruction_boundaries_reachability_other_indirect_callers_not_proved':True}})
    app_scans={'raw_JAL_CJ_CJAL':direct_edges(app,0x8000,0x2000078a),'adjacent_AUIPC_JALR':pairs(app,0x8000,0x2000078a)}
    check(app_scans=={'raw_JAL_CJ_CJAL':[],'adjacent_AUIPC_JALR':[]},'APP selected raw setter scan')
    check(sum(len(w['instructions']) for p in profiles for w in [p['prefix'],p['writer_tail'],p['zero_argument_tail']]+[c['window'] for c in p['constant_callers']])==114,'bounded instruction census')
    return {'schema':'TSL9-hook-callers-flag-static-v1','profile':parent['profile'],'profiles':profiles,'APP_raw_scan':app_scans,
        'scope':'14 bounded windows316B/114instructions; not 14 complete functions; FLASH/RAM coordinate checks for copied windows',
        'writer_contract':{'prefix':'SP-=64; save RA/S0..S11; read state word; SLLI16; BGE signedzero -> writer_tail',
            'prefix_branch_condition':'loaded state bit15 is zero; higher input bits discarded by 32-bit SLLI16',
            'other_prefix_edge':'fallthrough leaves validated prefix; intervening function body not covered',
            'tail':'fresh pointer=U32[pointer_source_word]; fresh field=U32[pointer+108]; if field!=0 SB1 flag; else leave flag unchanged',
            'no_pointer_null_guard_before_field_load':True,'tail_has_no_hook_slot_store_or_flag_reset':True,
            'return':'13 wordloads RA/S0..S11; SP+=64; ordinary RET, conditional on valid saved frame',
            'prefix_to_tail_edge_has_no_intermediate_call':True,'entire_containing_function_proved':False},
        'caller_contract':{'constant_windows':'each has uninterrupted LUI A0/ADDI A0/JAL setter; argument and callee identities differ',
            'zero_tail':'LI A0=0; SP+=32; AUIPC T1/JALR X0 setter; existing RA retained, no local link; parent epilogue unproved',
            'if_zero_tail_reached':'prior setter clears hook slot and does not reset flag',
            'all_runtime_registration_order_or_hook_execution_proved':False},
        'premises':['actual installed resident equals candidate; mapped bytes complete and preserved; valid target ISA and instruction/data accesses',
            'bounded windows reached with valid stack/context; no adverse alias, interrupt, reentry or other writer',
            'pointer-source word and loaded object identity/lifetime/validity unknown; +108 is an operand, not a proved C struct type',
            'raw halfword scans include data or mid-instruction false candidates and omit non-adjacent/indirect constructions'],
        'remaining':['loaded-argument caller and other raw candidates need instruction context','actual constant callback bodies and their downstream effects',
            'pointer-source writer/field108 origin and whole middle function','installed binding, ECALL route and object/frame preservation'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    for x in range(65536):
        shifted=(x<<16)&0xffffffff;signed=(shifted^0x80000000)-0x80000000
        check((signed>=0)==(x&0x8000==0),'SLLI16 BGE bit15 partition')
    count=0
    for i,(data,d) in enumerate(zip(carriers,DETAILS)):
        pre,tail,state,ptr,flag,zpc,zlow,ph,th,zh=d
        cases=[('prefix',pre,46,(state,tail),ph,((0,0x10),(14,4),(38,1<<20),(42,1<<12))),
            ('writer_tail',tail,52,(ptr,flag),th,((4,1<<20),(8,4),(18,1<<20),(22,4))),
            ('clear_tail',zpc,12,zlow,zh,((0,4),(4,1<<12),(8,1<<20)))]
        cases += [('constant_call',pc,12,(u,l,previous.DETAILS[i][0]),h,((0,1<<12),(4,1<<20),(8,1<<20))) for pc,u,l,h in CALLERS[i]]
        for role,pc,size,args,h,changes in cases:
            raw=init.binding.take(data,pc,size)
            for off,flip in changes:
                b=bytearray(raw);n=decode(raw,pc)[pc+off]['size'];b[off:off+n]=(int.from_bytes(b[off:off+n],'little')^flip).to_bytes(n,'little')
                try:window(b,role,pc,args,h)
                except RuntimeError as e:check(str(e)=='hook caller '+role+' operand '+hex(off),'specific hook caller mutation guard '+str(e))
                else:raise RuntimeError('hook caller mutation escaped')
                count+=1
    check(count==46,'mutation census')
    print('PASS: 65536 bit15 branch cases; 13 saved-register field joins per profile; 46 specified raw mutations rejected')


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
    else:check(OUT.read_bytes()==output,'hook callers flag exact ledger replay')
    print('PASS: 14 bounded windows316B/114instructions; constant/zero arguments, first-copy and prefix-to-flag-tail joins')
    print('PASS: exact ledger and raw candidate census; NO target execution; installed binding/object lifetime/ECALL route UNPROVED')


if __name__=='__main__':main()
