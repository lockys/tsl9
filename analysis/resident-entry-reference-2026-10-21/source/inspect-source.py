"""Portable static V1.31 entry/init/seed contract. No RV32 execution or ISA emulation."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[2]
CARRIER_REL='apk-analysis/tsl9-wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
CARRIER_SHA='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
RETAINED_SHA='3d993d42d5d5c7defeb839f7e31e2cda5e69ae1e84e72f26f81a996a4d107434'
BASE=0x40000
OLD='apk-analysis/tsl9-v4160-entry-irq-contract-2026-10-21/resident-handoff'
CAR='apk-analysis/tsl9-wch-resident-candidate-2026-10-21/carrier-dec2023'
PINS={CAR+'/final-audit.json':'3e1b0273334d42b7fc249f457b0c42cb639e2233c70de13fa7dc0e482d8e83a0',CAR+'/source-map.json':'96ff0490ccd196ee97655a80ed44ea2b1ceee53b84ca3bad8f8f74525031c0ba',OLD+'/final-audit.json':'60dd822cd584afaefbdb609d72bda7b3fad63f4ecf16aa5c9d97c7d3197fc0c1',OLD+'/historical-entry.json':'0f7b39f0b1644a965cec22537c372a6cea9df3a94e5fd1fd1938035a3b900d22',OLD+'/historical-initializer.json':'2e5d337a5837bdc1c81c70ced4da3c89e41f10cab806fb4bd9bad89c934752a4',OLD+'/historical-seed.json':'84f379fa3df94706af148a6197f2ef6357031a967884132d2f17dcdeed2100aa'}

def sha(b):return hashlib.sha256(b).hexdigest()
def enc(d):return(json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
def need(v,msg):
    if not v:raise ValueError(msg)
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def half(b,p):return int.from_bytes(b[p-BASE:p-BASE+2],'little')
def word(b,p):return int.from_bytes(b[p-BASE:p-BASE+4],'little')
def load(b,p):
    v=word(b,p);need(v&127==3,f'{p:x}: LOAD');return((v>>7)&31,(v>>15)&31,sx(v>>20,12),(v>>12)&7)
def store(b,p):
    v=word(b,p);need(v&127==0x23,f'{p:x}: STORE');return((v>>20)&31,(v>>15)&31,sx(((v>>25)<<5)|((v>>7)&31),12),(v>>12)&7)
def pair(b,hi,lo,rd,auipc=False,jalr_rd=None):
    h=word(b,hi);l=word(b,lo);need(h&127==(0x17 if auipc else 0x37)and(h>>7)&31==rd,f'{hi:x}: HI opcode/register')
    need(l&0x707F==(0x67 if jalr_rd is not None else 0x13)and(l>>15)&31==rd and(l>>7)&31==(jalr_rd if jalr_rd is not None else rd),f'{lo:x}: own LOW opcode/rs1/rd')
    val=((hi if auipc else 0)+(h&0xFFFFF000)+sx(l>>20,12))&0xFFFFFFFF
    return val&~1 if jalr_rd is not None else val
def c_addi(b,p):
    v=half(b,p);need(v&3==1 and v>>13==0,f'{p:x}: C.ADDI');return((v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6))
def c_stack(b,p,st):
    v=half(b,p);need(v&3==2 and v>>13==(6 if st else 2),f'{p:x}: SP load/store')
    if st:return((v>>2)&31,(((v>>7)&3)<<6)|(((v>>9)&15)<<2))
    return((v>>7)&31,(((v>>2)&3)<<6)|(((v>>12)&1)<<5)|(((v>>4)&7)<<2))
def c_lw(b,p):
    v=half(b,p);need(v&3==0 and v>>13==2,f'{p:x}: C.LW');return(8+((v>>2)&7),8+((v>>7)&7),(((v>>5)&1)<<6)|(((v>>10)&7)<<3)|(((v>>6)&1)<<2))
def c_sw(b,p):
    v=half(b,p);need(v&3==0 and v>>13==6,f'{p:x}: C.SW');return(8+((v>>2)&7),8+((v>>7)&7),(((v>>5)&1)<<6)|(((v>>10)&7)<<3)|(((v>>6)&1)<<2))
def direct(pc,n,v):
    if n==4 and v&127==0x6F:
        im=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1);return('call'if(v>>7)&31==1 else'jump',(pc+sx(im,21))&0xFFFFFFFF)
    if n==4 and v&127==0x63:
        im=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1);return('branch',(pc+sx(im,13))&0xFFFFFFFF)
    if n==2 and v&3==1 and v>>13 in(1,5):
        im=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5)
        return('call'if v>>13==1 else'jump',(pc+sx(im,12))&0xFFFFFFFF)
    return None
def branch(b,p,rs1,rs2,f3,target):
    v=word(b,p);need(v&0x707F==(f3<<12|0x63)and(v>>15)&31==rs1 and(v>>20)&31==rs2 and direct(p,4,v)==('branch',target),f'{p:x}: unsigned branch operands/target')

def gate(b):
    need(direct(BASE,4,word(b,BASE))==('jump',0x6DE7E),'40000: entry jump')
    gp=pair(b,0x6DE7E,0x6DE82,3,True);sp=pair(b,0x6DE86,0x6DE8A,2,True);need((gp,sp)==(0x20004000,0x20010000),'entry GP/SP')
    seed=[pair(b,0x6DE8E,0x6DE92,10,True),pair(b,0x6DE96,0x6DE9A,11,True),pair(b,0x6DE9E,0x6DEA2,12,True)];need(seed==[0x40280,0x20000010,0x20000040],'entry seed args')
    branch(b,0x6DEA6,11,12,7,0x6DEBE);branch(b,0x6DEB6,11,12,6,0x6DEAA)
    need(load(b,0x6DEAA)==(5,10,0,2),'seed READ32 first')
    need(store(b,0x6DEAE)==(5,11,0,2),'seed WRITE32 second')
    need(c_addi(b,0x6DEB2)==(10,4)and c_addi(b,0x6DEB4)==(11,4),'seed increments after write')
    need(direct(0x6DEBA,4,word(b,0x6DEBA))==('call',0x6DE0C),'entry initializer JAL/link')
    need(word(b,0x6DEBE)==0x30200073,'terminal MRET')
    need(c_addi(b,0x6DE0C)==(2,-16),'initializer liveSP frame')
    need(c_stack(b,0x6DE12,True)==(1,12),'initializer savedRA write')
    ptrs=[pair(b,0x6DE0E,0x6DE18,14),pair(b,0x6DE1E,0x6DE22,14),pair(b,0x6DE28,0x6DE2C,14)]
    need(ptrs==[0x200007D0,0x2000251C,0x20002E34],'lowRAM pointer values')
    need(word(b,0x6DE14)==0x200007B7,'lowRAM base LUI a5')
    for p,offset in[(0x6DE1C,0),(0x6DE26,4),(0x6DE3C,8)]:need(c_sw(b,p)==(14,15,offset),f'{p:x}: lowRAM WRITE32')
    first=[pair(b,0x6DE38,0x6DE46,10),pair(b,0x6DE34,0x6DE42,11),pair(b,0x6DE30,0x6DE3E,12)];need(first==[0x402B0,0x20000040,0x20002E70],'first copy args')
    second=[pair(b,0x6DE5A,0x6DE66,10),pair(b,0x6DE56,0x6DE62,11),pair(b,0x6DE52,0x6DE5E,12)];need(second==[0x6EAA4,0x20002E70,0x20002EF8],'second copy args')
    need(pair(b,0x6DE4A,0x6DE4E,1,True,1)==0x20000010 and pair(b,0x6DE6A,0x6DE6E,1,True,1)==0x20000010,'two RAM copy calls/linkRA')
    need(c_stack(b,0x6DE72,False)==(1,12),'fresh savedRA read after calls')
    need(c_addi(b,0x6DE74)==(2,16),'liveSP increment after RA load')
    need(pair(b,0x6DE76,0x6DE7A,6,True,0)==0x20000022,'tail to RAM zero helper without new link')
    branch(b,0x40280,12,11,7,0x40286);need(half(b,0x40284)==0x8082,'word helper RET')
    need(c_lw(b,0x40286)==(15,10,0),'word READ32')
    need(c_addi(b,0x40288)==(11,4)and c_addi(b,0x4028A)==(10,4),'word increments before write')
    need(store(b,0x4028C)==(15,11,-4,2),'word WRITE32 at advanced-a1 minus4')
    need(direct(0x40290,2,half(b,0x40290))==('jump',0x40280),'word loop')
    z=[pair(b,0x40292,0x4029A,15),pair(b,0x40296,0x4029E,14)];need(z==[0x20002EF8,0x20003614],'zero helper fixed bounds')
    branch(b,0x402A2,14,15,7,0x402A8);need(half(b,0x402A6)==0x8082,'zero RET')
    need(store(b,0x402A8)==(0,15,0,2),'zero WRITE32')
    need(c_addi(b,0x402AC)==(15,4)and direct(0x402AE,2,half(b,0x402AE))==('jump',0x402A2),'zero increment/loop')
    return {'GP':gp,'SP':sp,'seed':seed,'first':first,'second':second,'zero':z,'lowRAM_values':ptrs}

def verify_seal(path):
    d=json.loads(path.read_text(encoding='utf-8'));need(d.get('passed')is True,'seal not passed')
    for m in d['members']:
        b=(path.parent/m['path']).read_bytes();need(len(b)==m['bytes']and sha(b)==m['sha256'],'sealed member drift:'+m['path'])
def ev(pc,op,**kw):return{'source_pc':pc,'source_pc_hex':f'0x{pc:X}','operation':op,**kw}

def make_contract(v,spans,stop):
    return{'schema':'WCH-V1.31-reference-entry-ordered-contract-v1','passed':True,'blocking_findings':[],'reference_candidate_only':True,'carrier_sha256':CARRIER_SHA,'source_spans':spans,
        'entry':{'header_jump':{'pc':BASE,'raw':'6fd0f267','target':0x6DE7E},'ordered_effects':[
            ev(0x6DE7E,'GP=(PC+AUIPCupper+ADDIimm) mod2^32',low_pc=0x6DE82,value=v['GP']),ev(0x6DE86,'SP=(PC+AUIPCupper+ADDIimm) mod2^32',low_pc=0x6DE8A,value=v['SP']),ev(0x6DE8E,'set a0 seed source',low_pc=0x6DE92,value=v['seed'][0]),ev(0x6DE96,'set a1 seed destination',low_pc=0x6DE9A,value=v['seed'][1]),ev(0x6DE9E,'set a2 seed end-exclusive',low_pc=0x6DEA2,value=v['seed'][2]),
            ev(0x6DEA6,'if unsigned a1>=a2 skip seed AND initializer to MRET',target=0x6DEBE),ev(0x6DEAA,'READ32',address='live a0',destination='t0'),ev(0x6DEAE,'WRITE32',address='live a1',value='t0 sampled by prior read'),ev(0x6DEB2,'a0=(a0+4) mod2^32'),ev(0x6DEB4,'a1=(a1+4) mod2^32'),ev(0x6DEB6,'if unsigned a1<a2 repeat seed loop',target=0x6DEAA),ev(0x6DEBA,'DIRECT_CALL',target=0x6DE0C,link_RA=0x6DEBE,continuation='only if initializer/zero chain returns to expected link'),ev(0x6DEBE,'MRET',raw='73002030',target='machine return context; not saved RA')],
            'fixed_seed_shape':{'source':[0x40280,0x402B0],'destination':[0x20000010,0x20000040],'bytes':48,'words':12,'read_then_write_then_source_increment_then_destination_increment':True,'normal_initial_guard_false':True,'post_loop_registers_if_normal':{'a0':0x402B0,'a1':0x20000040,'a2':0x20000040}}},
        'initializer':{'entry':0x6DE0C,'ordered_effects':[
            ev(0x6DE0C,'SP=(liveSP-16) mod2^32'),ev(0x6DE0E,'a4=0x20000000'),ev(0x6DE12,'WRITE32',address='liveSP+12 mod2^32',value='live RA',role='save occurs after frame subtraction/LUI and before RAM calls'),ev(0x6DE14,'a5=0x20000000'),ev(0x6DE18,'a4=a4+2000'),ev(0x6DE1C,'WRITE32',address='live a5+0',value=0x200007D0),ev(0x6DE26,'WRITE32',address='live a5+4',value=0x2000251C),ev(0x6DE3C,'WRITE32',address='live a5+8',value=0x20002E34),
            ev(0x6DE4E,'INDIRECT_CALL_RAM_CODE',target=0x20000010,a0=0x402B0,a1=0x20000040,a2=0x20002E70,link_RA=0x6DE52,normal_return_to_link_required=True),ev(0x6DE6E,'INDIRECT_CALL_RAM_CODE',target=0x20000010,a0=0x6EAA4,a1=0x20002E70,a2=0x20002EF8,link_RA=0x6DE72,normal_return_to_link_required=True),
            ev(0x6DE72,'READ32',address='then-liveSP+12 mod2^32',destination='ra',role='fresh read; not a cached entry RA'),ev(0x6DE74,'SP=(then-liveSP+16) mod2^32'),ev(0x6DE7A,'INDIRECT_TAIL_RAM_CODE',target=0x20000022,link_written=False,return_RA='value freshly loaded at6DE72')],
            'live_context':'RAM callees are not assumed to preserve SP/GP or stack contents. Later events use returned live state. If exact seed instructions are still installed and normally interpreted without interleaving, neither helper explicitly accesses SP/GP; that conditional source fact does not prove actual ABI preservation.',
            'default_frame_geometry_only':{'entry_SP':0x20010000,'frame_SP':0x2000FFF0,'save_and_expected_fresh_read_address':0x2000FFFC,'nominal_saved_RA':0x6DEBE,'normal_final_SP_if_context_unchanged':0x20010000,'memory_accessibility_or_saved_value_stability_proved':False},'numeric_call_return_value_tested':False,'HALT_TRANSFER_or_other_return_target_never_forced_to_continuation':True},
        'RAM_instruction_admission':{'seed_source_capture':[0x40280,0x402B0],'expected_RAM_capture':[0x20000010,0x20000040],'word_helper':{'source':[0x40280,0x40292],'RAM':[0x20000010,0x20000022],'bytes':18,'instructions':7},'zero_helper':{'source':[0x40292,0x402B0],'RAM':[0x20000022,0x20000040],'bytes':30,'instructions':9},
            'required_conditions':['all12 seed READ32/WRITE32 requests complete with the expected bytes','instruction fetch sees those written bytes at the numeric RAM targets','RAM is executable and ISA/privilege decode matches the standard fields used here','no alias, IRQ, DMA or later write replaces the instructions or required register context','memory and control returns complete as required; a numeric target alone is not a provider'],
            'embedded_seed_does_not_prove_installed_RAM':True,'provider_generated':False,'default_run_RAM_is_delegated':True},
        'word_copy_helper':{'entry_source':0x40280,'conditional_RAM_entry':0x20000010,'ordered_iteration':[
            ev(0x40280,'if unsigned a2>=a1 copy one word; else RET',copy_target=0x40286),ev(0x40284,'RET',target='live RA'),ev(0x40286,'READ32',address='live a0',destination='a5'),ev(0x40288,'a1=(a1+4) mod2^32'),ev(0x4028A,'a0=(a0+4) mod2^32'),ev(0x4028C,'WRITE32',address='(live a1-4) mod2^32',value='a5 from preceding read'),ev(0x40290,'jump unsigned guard',target=0x40280)],
            'inclusive_last_word':True,'generic_wrap_alignment_or_memory_validity_proved':False,'fixed_calls':[{'call_pc':0x6DE4E,'source':[0x402B0,0x430E4],'destination':[0x20000040,0x20002E74],'last_word_inclusive':0x20002E70,'words':2957,'bytes':11828,'all_requested_source_captured':True,'post_registers_if_normal':{'a0':0x430E4,'a1':0x20002E74,'a2':0x20002E70}},{'call_pc':0x6DE6E,'source':[0x6EAA4,0x6EB30],'destination':[0x20002E70,0x20002EFC],'last_word_inclusive':0x20002EF8,'words':35,'bytes':140,'captured_prefix_words':34,'captured_prefix_bytes':136,'all_requested_source_captured':False,'post_registers_if_all_reads_normal':{'a0':0x6EB30,'a1':0x20002EFC,'a2':0x20002EF8}}]},
        'zero_helper':{'entry_source':0x40292,'conditional_RAM_entry':0x20000022,'own_constant_bounds':{'start':0x20002EF8,'last_word_inclusive':0x20003614,'end_exclusive':0x20003618,'words':456,'bytes':1824},'ordered_effects':[ev(0x40292,'a5=0x20003000'),ev(0x40296,'a4=0x20003000'),ev(0x4029A,'a5=(a5-264) mod2^32',nominal_value=0x20002EF8),ev(0x4029E,'a4=(a4+1556) mod2^32',nominal_value=0x20003614),ev(0x402A2,'if unsigned a4>=a5 write; else RET',write_target=0x402A8),ev(0x402A6,'RET',target='live RA freshly restored by initializer, if unchanged'),ev(0x402A8,'WRITE32',address='live a5',value=0),ev(0x402AC,'a5=(a5+4) mod2^32'),ev(0x402AE,'jump guard',target=0x402A2)],'not_a_caller_length_parameter':True,'does_not_assign_a0_a1_a2_SP_GP':True,'post_registers_if_normal':{'a4':0x20003614,'a5':0x20003618}},
        'strict_captured_provider_stop':stop,
        'MRET_and_context':{'source_pc':0x6DEBE,'raw':'73002030','bounded_explicit_CSR_read_or_write_instructions':[],'bounded_MEPC_MTVEC_write_sites':[],'no_bounded_MEPC_write_is_not_global_or_IRQ_preservation':True,'MRET_is_not_RET_to_restored_RA':True,'source_has_no_original_APP_handoff_target_constant':True,'requires_valid_machine_return_state_and_no_unaccounted_trap':True,'MSTATUS_vendor_CSR_and_physical_IRQ_semantics_proved':False},
        'C_reconstruction_boundaries':{'can_implement':'fixed entry register setup, ordered seed requests, lowRAM writes, delegated RAM calls/tail, literal word/zero reference providers under explicit fetch/ABI/memory conditions, fresh stack restore and MRET observation','must_keep_unknown':['installed resident identity','installed RAM instruction bytes/fetch validity','effects of delegated RAM code on live SP/GP/RA','unbacked last READ32 and physical source contents','IRQ/trap/alias behavior and CSR return context','original C signature/ABI and successful startup'], 'capture_only_provider_must_stop_before_zero_RA_reload_and_MRET':True},
        'limits':{'reference_candidate_only':True,'source_only':True,'original_TSL9_resident_identity_proved':False,'startup_completed_proved':False,'holes_filled':False,'provider_generated':False,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False,'ROOT_modified':False,'D_modified':False}}

def run(carrier,sr,w,historical=False):
    b=carrier.read_bytes();need(len(b)==191078 and sha(b)==CARRIER_SHA,'V1.31 main carrier hash/length')
    rb=(sr/'retained-source.json').read_bytes();need(sha(rb)==RETAINED_SHA,'retained source hardpin');r=json.loads(rb)
    if historical:
        for rel,pin in PINS.items():need(sha((w/rel).read_bytes())==pin,'historical pin drift:'+rel)
        verify_seal(w/CAR/'final-audit.json');verify_seal(w/OLD/'final-audit.json')
    vals=gate(b);spans=[];rows=[]
    for role,rs in r['groups'].items():
        cur=rs[0]['addr'];start=cur
        for row in rs:
            p=row['addr'];n=row['size'];raw=b[p-BASE:p-BASE+n];need(p==cur and raw.hex()==row['bytes'],'raw row/coverage:'+role);need(n==(4 if int.from_bytes(raw[:2],'little')&3==3 else 2),'instruction width');cur+=n;rows.append({**row,'role':role})
        spans.append({'role':role,'start':start,'end_exclusive':cur,'file_offset':start-BASE,'bytes':cur-start,'instructions':len(rs),'sha256':sha(b[start-BASE:cur-BASE])})
    need(len(rows)==67 and sum(x['size']for x in rows)==234,'retained full bounds')
    marker=r['version_markers'][0];mb=b[marker['address']-BASE:marker['address']-BASE+marker['bytes']];need(sha(mb)==marker['sha256']and mb.rstrip(b'\0')==b'CH32V20x_BLE_LIB_V1.31','actual V1.31 marker')
    starts={x['addr']for x in rows};edges=[];inst=[];graph={};terms=[]
    special={0x6DE4E:(0x20000010,0x40280,0x6DE52),0x6DE6E:(0x20000010,0x40280,0x6DE72),0x6DE7A:(0x20000022,0x40292,None)}
    for row in sorted(rows,key=lambda x:x['addr']):
        p=row['addr'];n=row['size'];v=int.from_bytes(bytes.fromhex(row['bytes']),'little');d=direct(p,n,v);succ=[];item={'pc':p,'file_offset':p-BASE,'width':n,'raw_hex':row['bytes'],'disassembly':row['opcode'],'role':row['role']}
        if row['role']=='seed_helpers':item['conditional_RAM_pc']=0x20000010+p-0x40280
        if d:
            need(row.get('jump')==d[1],'direct target mismatch');item['control']={'kind':d[0],'target':d[1]}
            if d[0]=='branch':item['control'].update({'rs1':(v>>15)&31,'rs2':(v>>20)&31,'funct3':(v>>12)&7});succ=[d[1],p+n]
            elif d[0]=='call':succ=[d[1],p+n]
            else:succ=[d[1]]
        elif p in special:
            target,source,cont=special[p];item['control']={'kind':'conditional-RAM-call'if cont else'conditional-RAM-tail','numeric_RAM_target':target,'conditional_source_entry':source,'normal_return_to_link_required':cont};succ=[source]+([cont]if cont else[])
        elif p in(0x40284,0x402A6):item['control']={'kind':'return','target':'liveRA'};terms.append({'pc':p,'kind':'return','target':'liveRA'})
        elif p==0x6DEBE:item['control']={'kind':'MRET','target':'machine return context'};terms.append({'pc':p,'kind':'MRET','target':'machine return context'})
        else:
            need(not(n==4 and v&127 in(0x67,0x6F,0x73)),'unclassified control/system');succ=[p+n]
        for target in succ:
            need(target in starts,'uncovered CFG target');edge={'source':p,'target':target,'kind':'local'}
            if p in special:edge['kind']='conditional-RAM-source-entry'if target==special[p][1]else'normal-return-to-expected-link'
            elif d and d[0]=='call':edge['kind']='direct-call-entry'if target==d[1]else'normal-return-to-expected-link'
            elif d and d[0]=='branch':edge['branch_outcome']='taken'if target==d[1]else'not-taken'
            edges.append(edge)
        graph[p]=succ;inst.append(item)
    seen=set();todo=[BASE]
    while todo:
        p=todo.pop()
        if p in seen:continue
        seen.add(p);todo.extend(graph[p])
    need(seen==starts,'bounded conditional sourceCFG not fully covered')
    explicitcsr=[x['pc']for x in inst if x['width']==4 and int.from_bytes(bytes.fromhex(x['raw_hex']),'little')&127==0x73 and x['pc']!=0x6DEBE];need(not explicitcsr,'unexpected bounded CSR instruction')
    sec=vals['second'];secbytes=sec[2]-sec[1]+4;lo,hi=sec[0],sec[0]+secbytes;covered=[(max(lo,x['start']),min(hi,x['end_exclusive']))for x in r['captured_segment_ledger']if x['start']<hi and lo<x['end_exclusive']];need(covered==[(0x6EAA4,0x6EB2C)],'second captured source coverage');cap=sum(e-s for s,e in covered);need(cap%4==0,'captured word prefix')
    stop={'scope':'strict captured-only source provider under the fixed normal entry/init/reference-helper path','call_pc':0x6DE6E,'read_instruction_source_pc':0x40286,'conditional_RAM_instruction_pc':0x20000016,'read_address':sec[0]+cap,'width':4,'zero_based_word_index':cap//4,'requested_word_count':secbytes//4,'captured_prefix_words':cap//4,'captured_prefix_bytes':cap,'pending_destination':sec[1]+cap,'inclusive_last_destination_word':sec[2],'read_precedes_increments_and_write':True,'no_increment_no_write_until_READ_returns':True,'unbacked_range':[0x6EB2C,0x6EB30],'source_missing_is_not_physical_unmapped_or_fault_proof':True,'strict_provider_action':'stop/HALT with missing-source evidence; do not fabricate zero/FF or automatically continue','zero_loop_reached':False,'fresh_RA_reload_reached':False,'MRET_reached':False,'explicit_unknown_external_memory_backend_is_separate_unproved_contract':True}
    mutations=[];cases=[('header_entry_target',BASE,1<<21),('GP_value',0x6DE82,1<<20),('SP_value',0x6DE8A,1<<20),('seed_source',0x6DE92,1<<20),('seed_destination',0x6DE9A,1<<20),('seed_end',0x6DEA2,1<<20),('entry_guard_unsigned',0x6DEA6,1<<12),('entry_READ32_width',0x6DEAA,1<<12),('entry_WRITE32_value',0x6DEAE,1<<20),('seed_source_increment',0x6DEB2,1<<2),('seed_dest_increment',0x6DEB4,1<<2),('seed_loop_comparison',0x6DEB6,1<<12),('init_frame_SP',0x6DE0C,1<<2),('saved_RA_offset',0x6DE12,1<<9),('RAM0_pointer_value',0x6DE18,1<<20),('RAM4_pointer_value',0x6DE22,1<<20),('RAM8_pointer_value',0x6DE2C,1<<20),('first_copy_source',0x6DE46,1<<20),('first_copy_destination',0x6DE42,1<<20),('first_copy_lastword',0x6DE3E,1<<20),('RAM_copy_call_link',0x6DE4E,1<<7),('second_copy_source',0x6DE66,1<<20),('second_copy_lastword',0x6DE5E,1<<20),('fresh_RA_restore_offset',0x6DE72,1<<4),('SP_restore_increment',0x6DE74,1<<2),('zero_tail_writes_link',0x6DE7A,1<<7),('word_inclusive_comparison',0x40280,1<<12),('word_READ32_destination_register',0x40286,1<<2),('word_preincrement',0x40288,1<<2),('word_STORE_offset',0x4028C,1<<7),('zero_start',0x4029A,1<<20),('zero_lastword',0x4029E,1<<20),('zero_inclusive_comparison',0x402A2,1<<12),('zero_STORE_value',0x402A8,1<<20),('MRET_word',0x6DEBE,1<<20)]
    for name,p,xor in cases:
        n=4 if half(b,p)&3==3 else 2;old=b[p-BASE:p-BASE+n];new=(int.from_bytes(old,'little')^xor).to_bytes(n,'little');mut=bytearray(b);mut[p-BASE:p-BASE+n]=new
        try:gate(mut)
        except ValueError as exc:mutations.append({'name':name,'pc':p,'original_raw':old.hex(),'mutant_raw':new.hex(),'rejected':True,'error':str(exc)})
        else:raise ValueError('raw semantic mutation escaped:'+name)
    sm={'schema':'WCH-V1.31-entry-init-seed-source-map-v1','passed':True,'reference_candidate_only':True,'carrier':{'relative_path':CARRIER_REL,'bytes':len(b),'sha256':CARRIER_SHA,'retained_range':[BASE,BASE+len(b)]},'retained_source_sha256':RETAINED_SHA,'historical_input_hashes':PINS,'public_source_provenance':r['historical_carrier_source'],'version_marker':marker,'source_spans':spans,'instructions':inst,'CFG':{'entry':BASE,'source_instruction_count_including_header':len(inst),'body_instruction_count_excluding_header':len(inst)-1,'source_bytes_including_header':sum(x['width']for x in inst),'body_bytes_excluding_header':sum(x['width']for x in inst)-4,'covered_starts':len(seen),'uncovered_starts':sorted(starts-seen),'edges':edges,'terminals':terms,'RAM_edges_require_matching_written_instruction_bytes':True,'normal_return_edges_are_assumptions_not_execution':True},'captured_source_stop':stop,'raw_operand_mutations':mutations,'standard_RV32_fields_only':True,'XWCHC_or_V1_40_constants_used':False,'target_execution':False,'ISA_emulation':False,'network':False}
    return{'source-map.json':enc(sm),'contract.json':enc(make_contract(vals,spans,stop))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--carrier',type=Path);p.add_argument('--source-root',type=Path,default=HERE);p.add_argument('--workspace',type=Path,default=WORKSPACE);p.add_argument('--verify-historical',action='store_true');g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args();w=a.workspace.resolve();sr=a.source_root.resolve();car=a.carrier.resolve()if a.carrier else w/CARRIER_REL;out=run(car,sr,w,a.verify_historical)
    if a.write:
        need(sr==HERE and not(HERE/'final-audit.json').exists(),'write limited to own unsealed scope')
        for n,b in out.items():
            q=HERE/n;need(not q.exists()or q.read_bytes()==b,'nonidentical output exists:'+n)
            if not q.exists():q.write_bytes(b)
    else:
        for n,b in out.items():need((sr/n).read_bytes()==b,'readonly byteexact mismatch:'+n)
        if(sr/'final-audit.json').exists():need(json.loads((sr/'final-audit.json').read_text()).get('sealed')is True,'not sealed');verify_seal(sr/'final-audit.json')
    print(json.dumps({'passed':True,'mode':'readonly-byteexact'if a.check else'create-only','reference_candidate_only':True,'body_bytes':230,'body_instructions':66,'header_bytes':4,'raw_operand_mutation_rejections':35,'output_sha256':{n:sha(b)for n,b in out.items()},'target_execution':False,'network':False}))

if __name__=='__main__':main()
