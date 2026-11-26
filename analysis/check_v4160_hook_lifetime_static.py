"""Candidate hook publication/consumption operands, CFG and conditional joins.

Read-only byte decoding and host predicate/address arithmetic only. No target
ISA, callback, RAM/frame, CSR, ECALL, MMIO or device execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_context_callback_frame_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-hook-lifetime-static.json')
DETAILS=((0x409fa,-264,'8b678d65194a574a288a1421f81f05d8b6fc16daea6420cc9fcda5d8252d0e56',
 'dc3baa9f4ffbd828b39dcc0e89440074819a0fc8c13af4167e0fbc5f2748f1f7'),
 (0x40a3a,-184,'f728ba41f5362d652b9663813fc00a39b14b6ecbb3c4fa5341653c3358565334',
 '1153522c8e921059766a62d59640fb216ffb05bfff0c0c751b38648a7eb4b591'))


def decode(raw,pc):
    n=previous.decode(raw,pc)
    for d in n.values():
        if d['op']=='load' and d['width']==1:
            w=int.from_bytes(bytes.fromhex(d['bytes']),'little')
            check(d['size']==4 and w&0x707f==0x4003,'hook exact unsigned byte encoding')
            d['signed']=False
    return n


def specs(role,pc,delta):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o):e(o,'lui',rd=15,imm=0x20003000)
    def load(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    if role=='setter':
        lui(0);store(4,10,15,delta);e(8,'beqz',rs1=10,target=pc+20)
        lui(10);e(14,'li',rd=14,imm=1);store(16,14,15,delta+4,1);e(20,'jr',rs1=1)
    elif role=='consumer':
        lui(0);load(4,14,15,delta);addi(8,2,2,-16);store(10,8,2,8);store(12,1,2,12)
        addi(14,8,15,delta);e(18,'beqz',rs1=14,target=pc+22);e(20,'call_indirect',rd=1,rs1=14)
        lui(22);e(26,'load',rd=15,rs1=15,imm=delta+4,width=1,signed=False)
        e(30,'andi',rd=15,rs1=15,imm=255);e(34,'bnez',rs1=15,target=pc+40);store(36,0,8,0)
        load(40,1,2,12);load(42,8,2,8);addi(44,2,2,16);e(46,'jr',rs1=1)
    else:raise RuntimeError('unknown hook role')
    return s


def body(raw,role,pc,delta,digest):
    n=decode(raw,pc);s=specs(role,pc,delta)
    check(set(n)==set(s),'hook whole body boundaries '+role)
    for p,f in s.items():init.g(n,p,'hook '+role+' operand '+hex(p-pc),**f)
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jr':qs=[]
        elif d['op'] in ('beqz','bnez'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'hook closed local body '+role)
        edges[p]=qs
        if d['op']=='call_indirect':calls.append({'pc':hex(p),'source':'initial fresh U32[hook_slot] in A4',
            'effective_target':'raw pointer & ~1','link':hex(p+d['size']),'normal_return_and_preservation_proved':False})
    seen=set()
    def visit(p):
        if p in seen:return
        seen.add(p)
        for q in edges[p]:visit(q)
    visit(pc);check(seen==set(n),'hook all local nodes reached '+role)
    size,count,stores=(22,7,2) if role=='setter' else (48,17,3)
    check((len(raw),len(n),sum(d['op']=='store' for d in n.values()),sha256(raw).hexdigest())==
          (size,count,stores,digest),'hook complete identity '+role)
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,
        'instructions':list(n.values()),'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'calls':calls,'terminal':{'pc':hex(pc+size-2),'kind':'ordinary RET'},'full_body':True}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,detail) in enumerate(zip(carriers,DETAILS)):
        source,delta,sh,ch=detail;p=parent['profiles'][i];dest=int(p['first_copy_destination'],16);src=int(p['first_copy_source'],16)
        end=int(p['first_copy_end'],16);runtime=source-src+dest;slot=0x20003000+delta;flag=slot+4
        check(runtime==0x2000078a and dest<=runtime and runtime+70<=end,'hook complete first-copy mapping')
        check(flag==int(p['flag_address'],16),'same callback and consumer flag')
        setter_raw=init.binding.take(data,source,22);consumer_raw=init.binding.take(data,source+22,48)
        setter=body(setter_raw,'setter',runtime,delta,sh);consumer=body(consumer_raw,'consumer',runtime+22,delta,ch)
        body(setter_raw,'setter',source,delta,sh);body(consumer_raw,'consumer',source+22,delta,ch)
        gateway=p['gateway'];check(gateway['calls'][0]['target']==consumer['start'],'gateway joins exact consumer entry')
        check(gateway['terminal_edges']==[{'pc':hex(int(gateway['start'],16)+4),'kind':'ecall'}],'gateway after normal return is ECALL')
        cb={d['pc']:d for d in p['callback']['instructions']};cp=int(p['callback']['start'],16)
        check(cb[cp+12]['op']=='store' and cb[cp+12]['rs2']==0 and cb[cp+12]['width']==1,'callback clears same flag before branch')
        check(int(p['startup_zero_request'][0],16)<=slot and flag+1<=int(p['startup_zero_request'][1],16),'zero request contains slot and flag')
        profiles.append({'label':p['label'],'first_copy_source':hex(src),'first_copy_destination':hex(dest),'first_copy_end':hex(end),
            'flash_setter':hex(source),'flash_consumer':hex(source+22),'setter':setter,'consumer':consumer,
            'hook_slot':hex(slot),'flag':hex(flag),'gateway':gateway['start'],'callback':p['callback']['start'],
            'callback_clear_pc':hex(cp+12),'startup_zero_request':p['startup_zero_request'],
            'installed_binding_copy_completion_and_preservation_proved':False})
    check(sum(x[r]['bytes'] for x in profiles for r in ('setter','consumer'))==140,'hook new byte census')
    return {'schema':'TSL9-hook-lifetime-static-v1','profile':parent['profile'],
        'scope':'2 complete setters44B/14instructions +2 complete consumers96B/34instructions; both FLASH and mapped RAM operands verified',
        'profiles':profiles,'parent_APP_body_hashes':{k:v['sha256'] for k,v in parent['APP'].items()},
        'publication_contract':{'raw_A0_zero':'SW0 hook_slot; branch to RET; no local flag write',
            'raw_A0_nonzero':'SW raw A0 hook_slot, then SB1 flag; no calls or local frame allocation',
            'no_null_alignment_lifetime_or_pointer_validation':True,'raw_pointer_bit0_is_stored':True},
        'consumption_contract':{'before_call':'one fresh LW hook_slot->A4; frame16 saves S0@8 and RA@12; S0=slot; rawzero skips JALR',
            'optional_call':'JALR uses original raw A4 & ~1; no explicit A0..A3 definitions before call; arguments otherwise unknown',
            'after_call_or_skip':'fresh LBU flag; AND255; ifzero SW0 via then-live S0; otherwise no local hook store',
            'no_pointer_reread_or_equality_check_before_clear':True,'no_local_flag_store':True,
            'scalar_return_is_not_defined_by_this_body':True,'SP_S0_saved_words_and_normal_hook_return_required':True},
        'conditional_join':{'callback_to_gateway':'prior callback SB0 flag precedes nonzero-branch direct callee/MRET; reaching gateway is conditional',
            'flag_zero_after_hook':'under valid mapping/access/preserved S0, clears slot even if hook replaced its contents',
            'flag_nonzero_after_hook':'body does not clear current slot; does not establish it still equals original pointer',
            'setter_nonzero_during_hook':'if same mapping/flag and completed setter with no intervening writes, fresh flag1 suppresses clear',
            'setter_zero_during_hook':'clears slot but leaves prior flag unchanged; no unconditional flag reset',
            'same_pointer_retention_or_payload_ownership_proved':False,
            'gateway_service_return':'ordinary return to gateway ECALL only if original RA/SP/saved words retained; no trap route established'},
        'premises':['actual installed candidate identity, completed code copy, correct GP/SP/context and valid instruction/data accesses',
            'unknown hook may write slot/flag/CSR/frame, reenter, not return, or invalidate saved registers/words; no global writer exclusion',
            'startup zero request is not proof of completed initialization or current pointer/flag values',
            'RAM word only records a pointer; no proof of referent allocation, lifetime, copy, payload or ABI contract'],
        'remaining':['setter callers and actual pointer provenance','additional flag writers and callback direct callees',
            'actual installed binding and gateway ECALL trap route','driver and broader frame/payload lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    for byte in range(256):
        check((byte&255==0)==(byte==0),'LBU/AND255 exact zero partition')
        check((((byte^128)-128)==0)==(byte==0),'LB callback and LBU consumer same zero partition')
    mutations={'setter':((0,1<<12),(4,1<<20),(8,4),(14,4),(16,1<<20)),
        'consumer':((4,1<<20),(14,1<<20),(18,4),(20,0x80),(26,1<<12),(30,1<<20),(34,4),(36,1<<15))}
    count=0
    for data,(source,delta,sh,ch) in zip(carriers,DETAILS):
        for role,p,size,h in (('setter',source,22,sh),('consumer',source+22,48,ch)):
            raw=init.binding.take(data,p,size)
            for off,flip in mutations[role]:
                b=bytearray(raw);n=previous.decode(raw,p)[p+off]['size'];b[off:off+n]=(int.from_bytes(b[off:off+n],'little')^flip).to_bytes(n,'little')
                try:body(b,role,p,delta,h)
                except RuntimeError as e:
                    check(str(e) in ('hook '+role+' operand '+hex(off),'hook exact unsigned byte encoding'),'specific hook mutation guard '+str(e))
                else:raise RuntimeError('hook mutation escaped')
                count+=1
    check(count==26,'hook mutation census')
    print('PASS: 256 LB/LBU zero partitions; 26 specified operand mutations rejected')


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
    else:check(OUT.read_bytes()==output,'hook lifetime exact ledger replay')
    print('PASS: complete candidate setters44B/14instructions and consumers96B/34instructions; FLASH/RAM mapping and callback flag/gateway joins')
    print('PASS: exact ledger; NO target execution; installed binding/hook preservation/lifetime/ECALL trap route UNPROVED')


if __name__=='__main__':main()
