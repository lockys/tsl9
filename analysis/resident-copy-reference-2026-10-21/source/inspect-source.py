"""Static V1.31 reference-only resident copy contract; never executes the candidate ISA."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[2]
CARRIER_REL='apk-analysis/tsl9-wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
CARRIER_SHA='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
RETAINED_SHA='9dc8ec6d725cfd0d93896bdf132863a0cfad7ee9aad255ac2a494ee17dc8c832'
HELPER_SHA='558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36'
BASE=0x40000
START,END,RAM=0x405A2,0x405DC,0x20000332
CARRIER_DIR='apk-analysis/tsl9-wch-resident-candidate-2026-10-21/carrier-dec2023'
HANDOFF_DIR='apk-analysis/tsl9-v4160-entry-irq-contract-2026-10-21/resident-handoff'
HISTORY={CARRIER_DIR+'/final-audit.json':'3e1b0273334d42b7fc249f457b0c42cb639e2233c70de13fa7dc0e482d8e83a0',CARRIER_DIR+'/source-map.json':'96ff0490ccd196ee97655a80ed44ea2b1ceee53b84ca3bad8f8f74525031c0ba',HANDOFF_DIR+'/final-audit.json':'60dd822cd584afaefbdb609d72bda7b3fad63f4ecf16aa5c9d97c7d3197fc0c1',HANDOFF_DIR+'/contract.json':'5afab00af7e8fe9f0a61e18ee9c97df1220d20e01fabdca73fb7a0cb5ab70bdb'}

def sha(b):return hashlib.sha256(b).hexdigest()
def enc(d):return(json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
def need(v,msg):
    if not v:raise ValueError(msg)
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def half(b,pc):return int.from_bytes(b[pc-BASE:pc-BASE+2],'little')
def word(b,pc):return int.from_bytes(b[pc-BASE:pc-BASE+4],'little')
def load(b,pc):
    v=word(b,pc);need(v&127==3,f'{pc:x}: LOAD opcode');return((v>>7)&31,(v>>15)&31,sx(v>>20,12),(v>>12)&7)
def store(b,pc):
    v=word(b,pc);need(v&127==0x23,f'{pc:x}: STORE opcode');return((v>>20)&31,(v>>15)&31,sx(((v>>25)<<5)|((v>>7)&31),12),(v>>12)&7)
def lui(b,pc,rd):
    v=word(b,pc);need(v&127==0x37 and(v>>7)&31==rd,f'{pc:x}: LUI register/opcode');return v&0xFFFFF000
def addi(b,pc):
    v=word(b,pc);need(v&0x707F==0x13,f'{pc:x}: ADDI opcode');return((v>>7)&31,(v>>15)&31,sx(v>>20,12))
def pair(b,hi,lo,rd,auipc=False,jalr=False):
    v=word(b,hi);need(v&127==(0x17 if auipc else 0x37)and(v>>7)&31==rd,f'{hi:x}: pair HI')
    low=word(b,lo);need(low&0x707F==(0x67 if jalr else 0x13)and(low>>15)&31==rd and(low>>7)&31==rd,f'{lo:x}: pair LOW')
    value=((hi if auipc else 0)+(v&0xFFFFF000)+sx(low>>20,12))&0xFFFFFFFF
    return value&~1 if jalr else value
def direct(pc,n,v):
    if n==4 and v&127==0x6F:
        im=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
        return('call'if(v>>7)&31==1 else'jump',(pc+sx(im,21))&0xFFFFFFFF)
    if n==4 and v&127==0x63:
        im=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1);return('branch',(pc+sx(im,13))&0xFFFFFFFF)
    if n==2 and v&3==1 and v>>13 in(1,5):
        im=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5)
        return('call'if v>>13==1 else'jump',(pc+sx(im,12))&0xFFFFFFFF)
    if n==2 and v&3==1 and v>>13 in(6,7):
        im=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5);return('branch',(pc+sx(im,9))&0xFFFFFFFF)
    return None
def c_li(b,pc):
    v=half(b,pc);need(v&3==1 and v>>13==2,f'{pc:x}: C.LI');return((v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6))
def c_addi(b,pc):
    v=half(b,pc);need(v&3==1 and v>>13==0,f'{pc:x}: C.ADDI');return((v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6))

def gate(b):
    need(word(b,0x4004C)==RAM,'4004c: slot target must be20000332, not ROM4004c')
    need(direct(BASE,4,word(b,BASE))==('jump',0x6DE7E),'40000: entry jump')
    need(pair(b,0x6DE8E,0x6DE92,10,True)==0x40280,'entry seed source')
    need(pair(b,0x6DE96,0x6DE9A,11,True)==0x20000010,'entry seed destination')
    need(pair(b,0x6DE9E,0x6DEA2,12,True)==0x20000040,'entry seed end-exclusive')
    # The word helper's actual BGEU is inclusive on last-word address.
    v=word(b,0x40280);need(v&0x707F==0x7063 and(v>>15)&31==12 and(v>>20)&31==11 and direct(0x40280,4,v)==('branch',0x40286),'40280: inclusive BGEU last,current')
    need(half(b,0x40284)==0x8082 and half(b,0x40286)==0x411C,'seed RET/LW')
    need(c_addi(b,0x40288)==(11,4)and c_addi(b,0x4028A)==(10,4),'seed word increments')
    need(store(b,0x4028C)==(15,11,-4,2),'seed word store after increment')
    need(direct(0x40290,2,half(b,0x40290))==('jump',0x40280),'seed helper local loop')
    src=pair(b,0x6DE38,0x6DE46,10);dest=pair(b,0x6DE34,0x6DE42,11);last=pair(b,0x6DE30,0x6DE3E,12)
    need((src,dest,last)==(0x402B0,0x20000040,0x20002E70),'first copy exact loader arguments')
    need(pair(b,0x6DE4A,0x6DE4E,1,True,True)==0x20000010,'first copy calls seed helper in RAM')
    src2=pair(b,0x6DE5A,0x6DE66,10);dest2=pair(b,0x6DE56,0x6DE62,11);last2=pair(b,0x6DE52,0x6DE5E,12)
    need((src2,dest2,last2)==(0x6EAA4,0x20002E70,0x20002EF8),'second copy exact loader arguments')
    need(pair(b,0x6DE6A,0x6DE6E,1,True,True)==0x20000010,'second copy calls seed helper in RAM')
    for pc in(0x405A2,0x405BA):need(lui(b,pc,15)==0x40024000,f'{pc:x}: MMIO address high')
    need(load(b,0x405A6)==(14,15,524,2),'405a6: initial READ32 literal4002420c')
    need(store(b,0x405AA)==(0,15,524,2),'405aa: WRITE32 zero before pointer guards')
    need(word(b,0x405AE)==0x0000100F,'405ae: FENCE.I not ordinary FENCE')
    for pc,rs1,f3,target in[(0x405B2,10,6,0x405BA),(0x405B4,11,6,0x405BA),(0x405B8,12,7,0x405C4)]:
        v=half(b,pc);need(v&3==1 and v>>13==f3 and 8+((v>>7)&7)==rs1 and direct(pc,2,v)==('branch',target),f'{pc:x}: pointer/count guard')
    need(c_li(b,0x405B6)==(15,0),'405b6: index0')
    need(store(b,0x405BE)==(14,15,524,2),'405be: restore saved word')
    need(half(b,0x405C2)==0x8082,'405c2: RET through live RA')
    for pc,rs1 in[(0x405C4,11),(0x405CC,10)]:
        v=word(b,pc);need(v&0xFE00707F==0x33 and(v>>7)&31==13 and(v>>15)&31==rs1 and(v>>20)&31==15,f'{pc:x}: address base plus old index')
    need(load(b,0x405C8)==(16,13,0,4),'405c8: source LBU unsigned')
    need(c_addi(b,0x405D0)==(15,1),'405d0: index increment before store')
    need(store(b,0x405D2)==(16,13,0,0),'405d2: destination SB')
    v=word(b,0x405D6);need(v&0x707F==0x1063 and(v>>15)&31==12 and(v>>20)&31==15 and direct(0x405D6,4,v)==('branch',0x405C4),'405d6: count/index BNE')
    need(direct(0x405DA,2,half(b,0x405DA))==('jump',0x405BA),'405da: common restore')
    return {'seed_source':0x40280,'seed_destination':0x20000010,'seed_bytes':48,'source':src,'destination':dest,'last_word':last,'bytes':last-dest+4,'source2':src2,'destination2':dest2,'last_word2':last2,'bytes2':last2-dest2+4,'slot':RAM,'mapped_helper_source':src+(RAM-dest)}

def verify_seal(path):
    d=json.loads(path.read_text(encoding='utf-8'));need(d.get('passed')is True,'historical seal not passed')
    for m in d['members']:
        b=(path.parent/m['path']).read_bytes();need(len(b)==m['bytes']and sha(b)==m['sha256'],f'seal member drift:{m["path"]}')

def event(pc,op,**kw):return {'source_pc':pc,'conditional_RAM_pc':RAM+pc-START,'operation':op,**kw}

def run(carrier,sr,w,historical=False):
    b=carrier.read_bytes();need(len(b)==191078 and sha(b)==CARRIER_SHA,'historical V1.31 carrier hash/length')
    rb=(sr/'retained-source.json').read_bytes();need(sha(rb)==RETAINED_SHA,'retained source hardpin');ret=json.loads(rb)
    if historical:
        for rel,pin in HISTORY.items():need(sha((w/rel).read_bytes())==pin,'historical pin drift:'+rel)
        verify_seal(w/CARRIER_DIR/'final-audit.json');verify_seal(w/HANDOFF_DIR/'final-audit.json')
    mapping=gate(b);need(mapping['mapped_helper_source']==START and mapping['bytes']==11828,'exact helper mapping')
    need(mapping['destination']<=RAM and RAM+(END-START)<=mapping['destination']+mapping['bytes'],'helper fully inside first copy')
    marker=ret['version_markers'][0];ma=marker['address'];mb=b[ma-BASE:ma-BASE+marker['bytes']];need(sha(mb)==marker['sha256']and mb.rstrip(b'\0')==b'CH32V20x_BLE_LIB_V1.31','actual candidate V1.31 marker')
    allspans=[];allrows={}
    for name,rs in ret['groups'].items():
        cur=rs[0]['addr'];first=cur
        for r in rs:
            pc=r['addr'];n=r['size'];v=bytes.fromhex(r['bytes']);need(pc==cur and b[pc-BASE:pc-BASE+n]==v,'retained row raw/coverage:'+name);need(n==(4 if int.from_bytes(v[:2],'little')&3==3 else 2),'width');cur+=n
        allrows[name]=rs;allspans.append({'role':name,'start':first,'end_exclusive':cur,'file_offset':first-BASE,'bytes':cur-first,'instructions':len(rs),'sha256':sha(b[first-BASE:cur-BASE])})
    rows=allrows['helper'];need(len(rows)==18 and sha(b[START-BASE:END-BASE])==HELPER_SHA,'helper exact source')
    starts={r['addr']for r in rows};ir=[];edges=[];graph={}
    for r in rows:
        pc=r['addr'];n=r['size'];v=int.from_bytes(bytes.fromhex(r['bytes']),'little');d=direct(pc,n,v);succ=[]
        item={'source_pc':pc,'conditional_RAM_pc':RAM+pc-START,'carrier_file_offset':pc-BASE,'width':n,'raw_hex':r['bytes'],'disassembly':r['opcode']}
        if d:
            need(r.get('jump')==d[1],'decoded target drift');need(d[0]!='call','unexpected helper call')
            item['control']={'kind':d[0],'source_target':d[1],'conditional_RAM_target':RAM+d[1]-START}
            if d[0]=='branch':succ=[d[1],pc+n]
            else:succ=[d[1]]
        elif pc==0x405C2:item['control']={'kind':'return','target':'liveRA'}
        else:succ=[pc+n]
        for target in succ:
            need(target in starts,'unresolved/outside helper CFG successor');e={'source':pc,'target':target,'RAM_source':RAM+pc-START,'RAM_target':RAM+target-START}
            if d and d[0]=='branch':e['branch_outcome']='taken'if target==d[1]else'not-taken'
            edges.append(e)
        graph[pc]=succ;ir.append(item)
    seen=set();todo=[START]
    while todo:
        pc=todo.pop()
        if pc in seen:continue
        seen.add(pc);todo.extend(graph[pc])
    need(seen==starts,'helper CFG incomplete')
    ledger=ret['captured_segment_ledger'];lo=mapping['source2'];hi=lo+mapping['bytes2'];covered=[(max(lo,s['start']),min(hi,s['end_exclusive']))for s in ledger if s['start']<hi and lo<s['end_exclusive']];need(covered==[(0x6EAA4,0x6EB2C)],'inherited captured source ledger');missing=[{'start':0x6EB2C,'end_exclusive':0x6EB30,'bytes':4}]
    mutations=[]
    cases=[('MMIO_read_offset',0x405A6,1<<20),('zero_write_value',0x405AA,1<<20),('FENCE_I_to_FENCE',0x405AE,1<<12),('destination_BEQZ_to_BNEZ',0x405B2,1<<13),('source_BEQZ_to_BNEZ',0x405B4,1<<13),('count_BNEZ_to_BEQZ',0x405B8,1<<13),('index_initial0',0x405B6,1<<2),('source_address_base',0x405C4,1<<15),('unsigned_LBU_to_LB',0x405C8,4<<12),('destination_address_base',0x405CC,1<<15),('increment1_to0',0x405D0,1<<2),('byte_store_to_halfword',0x405D2,1<<12),('loop_BNE_to_BEQ',0x405D6,1<<12),('restore_MMIO_high',0x405BA,1<<12),('restore_MMIO_offset',0x405BE,1<<7),('restore_word_register',0x405BE,1<<20),('RET_register',0x405C2,1<<7),('slot_RAM_address',0x4004C,1<<1),('first_copy_source',0x6DE46,1<<20),('first_copy_destination',0x6DE42,1<<20),('first_copy_lastword',0x6DE3E,1<<20),('inclusive_BGEU_to_BLTU',0x40280,1<<12),('word_copy_store_offset',0x4028C,1<<7)]
    for name,pc,xor in cases:
        n=4 if pc==0x4004C or half(b,pc)&3==3 else 2;old=b[pc-BASE:pc-BASE+n];new=(int.from_bytes(old,'little')^xor).to_bytes(n,'little');mut=bytearray(b);mut[pc-BASE:pc-BASE+n]=new
        try:gate(mut)
        except ValueError as exc:mutations.append({'name':name,'source_pc':pc,'original_raw':old.hex(),'mutant_raw':new.hex(),'rejected':True,'gate_error':str(exc)})
        else:raise ValueError('raw mutation escaped:'+name)
    sm={'schema':'WCH-V1.31-reference-copy-source-map-v1','passed':True,'reference_candidate_only':True,'source_carrier':{'relative_path':CARRIER_REL,'bytes':len(b),'sha256':CARRIER_SHA,'retained_segment':[BASE,BASE+len(b)]},'retained_source_sha256':RETAINED_SHA,'historical_input_hashes':HISTORY,'public_source_provenance':ret['historical_carrier_source'],'version_marker':marker,'source_spans':allspans,'loader_rows':{k:v for k,v in allrows.items()if k!='helper'},'helper_instructions':ir,'helper_CFG':{'entry_source':START,'entry_conditional_RAM':RAM,'end_exclusive_source':END,'end_exclusive_conditional_RAM':RAM+END-START,'bytes':END-START,'instructions':len(rows),'reachable_instruction_count':len(seen),'edges':edges,'return_sites':[0x405C2],'external_calls':[],'unknown_indirect_calls':[],'unresolved_control_frontier':[],'endpoint_derived_from_reachable_returns_and_branches_not_next_symbol':True},'raw_operand_mutations':mutations,'decoding_profile':'standard RV32I/C field decoding plus literal FENCE.I; no RC_WCH/XWCHC profile selected, no physical ISA claim','target_execution':False,'ISA_emulation':False,'network':False}
    facts={'schema':'WCH-V1.31-reference-copy-live-contract-v1','passed':True,'blocking_findings':[],'reference_candidate_only':True,'selected_carrier_sha256':CARRIER_SHA,'version':'CH32V20x_BLE_LIB_V1.31','slot':{'address':0x4004C,'raw_LE32':'32030020','value':RAM,'value_is_RAM_not_carrier_ROM_text':True,'installed_slot_value_proved':False},
        'conditional_mapping':{'seed':{'source':mapping['seed_source'],'destination':mapping['seed_destination'],'bytes':48,'contains_word_copy_helper18B':True},'first_copy':{'source':mapping['source'],'destination':mapping['destination'],'last_destination_word_inclusive':mapping['last_word'],'width':4,'bytes':mapping['bytes'],'words':mapping['bytes']//4,'all_source_bytes_captured_in_main_segment':True},'mapped_copy_helper':{'RAM_entry':RAM,'source_entry':START,'source_end_exclusive':END,'bytes':END-START,'sha256':HELPER_SHA,'mapping_formula':'source402B0 + (RAMaddress-20000040)','slot_inside_first_destination_range':True},'assumptions':['entry seed copy and the relevant prefix of first word copy execute normally','the seed word-copy instructions are interpreted with the decoded standard RV32 fields','source reads and RAM writes are valid, stable and preserve the requested bytes','no interrupt/alias/other memory modification replaces copied instructions','actual installed resident/ISA may differ from this public candidate'],
            'startup_completed_proved':False,'resident_ABI_or_original_TSL9_identity_proved':False},
        'numeric_register_interface':{'a0':'u32 destination address; body never assigns a0','a1':'u32 source address; body never assigns a1','a2':'u32 byte count; body never assigns a2','a4':'holds initial MMIO word until restore in this local body','a5':'MMIO base, then index, then restore MMIO base','a6':'zero-extended source byte','a3':'computed source/destination address','SP_GP':'not referenced or assigned by this58B body','RA':'RET through then-live RA; no call/link inside body','original_C_signature_proved':False},
        'ordered_effects':[
            event(0x405A6,'READ32',address=0x4002420C,destination='a4',role='saved word; hardware register role unknown'),event(0x405AA,'WRITE32',address=0x4002420C,value=0),event(0x405AE,'FENCE.I',role='observed instruction; hardware effects/faults delegated'),event(0x405B2,'if destination==0 goto restore'),event(0x405B4,'if source==0 goto restore'),event(0x405B6,'index=0'),event(0x405B8,'if count!=0 enter byte loop else restore'),
            event(0x405C4,'source_address=(source+old_index) mod2^32'),event(0x405C8,'READ8_UNSIGNED',address='computed source_address',destination='a6'),event(0x405CC,'destination_address=(destination+old_index) mod2^32'),event(0x405D0,'index=(index+1) mod2^32',role='before destination write'),event(0x405D2,'WRITE8',address='already computed destination_address',value='low8 of a6'),event(0x405D6,'if count!=index repeat loop'),event(0x405DA,'jump common restore'),event(0x405BA,'a5=0x40024000'),event(0x405BE,'WRITE32',address=0x4002420C,value='a4 saved by first read'),event(0x405C2,'RET',target='liveRA',a0='unchanged numeric destination')],
        'behavioral_boundaries':{'zero_destination_source_or_count':'still performs MMIO read, zero write, FENCE.I and restore, but no source/destination byte requests','nonnull_nonzero_count':'forward byte loop for u32 count; source read precedes destination write each iteration; no snapshot or backward-copy selection','overlap':'forward live reads can observe earlier writes; not a memmove contract','return_value':'a0 is unchanged destination, not a success/failure boolean','fault_or_transfer':'every request/observation can stop before subsequent events; no automatic finally/restore on HALT or TRANSFER','restore_fence':'no second FENCE.I between restore store and RET','MMIO_hardware_identity':'unproved; retain literal4002420C, not a guessed peripheral name','large_count_or_pointer_wrap':'u32 arithmetic shape only, valid memory and feasible completion not proved'},
        'inherited_startup_gap':{'second_copy_source':lo,'requested_bytes':mapping['bytes2'],'captured_intersection_bytes':sum(e-s for s,e in covered),'missing_source':missing,'RAM_destination':mapping['destination2'],'last_word_inclusive':mapping['last_word2'],'later_zero_does_not_prove_missing_source_read_can_complete':True,'ledger_sha256':RETAINED_SHA,'copy_RAM_mapping_is_not_startup_completion':True},
        'limits':{'original_TSL9_resident_identity_proved':False,'BOOT_4004C_runtime_value_proved':False,'ROM_ABI_proved':False,'physical_RAM_MMIO_or_ISA_validated':False,'provider_generated':False,'reference_ROM_injected':False,'holes_filled':False,'ROOT_modified':False,'D_modified':False,'network':False,'target_execution':False,'ISA_emulation':False,'hardware':False,'real_UID_or_packet_created':False}}
    return{'source-map.json':enc(sm),'contract.json':enc(facts)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--carrier',type=Path);p.add_argument('--source-root',type=Path,default=HERE);p.add_argument('--workspace',type=Path,default=WORKSPACE);p.add_argument('--verify-historical',action='store_true');g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args();w=a.workspace.resolve();sr=a.source_root.resolve();car=a.carrier.resolve()if a.carrier else w/CARRIER_REL;out=run(car,sr,w,a.verify_historical)
    if a.write:
        need(sr==HERE and not(HERE/'final-audit.json').exists(),'write restricted to own unsealed package')
        for n,b in out.items():
            q=HERE/n;need(not q.exists()or q.read_bytes()==b,'nonidentical output:'+n)
            if not q.exists():q.write_bytes(b)
    else:
        for n,b in out.items():need((sr/n).read_bytes()==b,'readonly byteexact mismatch:'+n)
        if(sr/'final-audit.json').exists():need(json.loads((sr/'final-audit.json').read_text()).get('sealed')is True,'final not sealed');verify_seal(sr/'final-audit.json')
    print(json.dumps({'passed':True,'mode':'readonly-byteexact'if a.check else'create-only','reference_candidate_only':True,'helper_bytes':58,'helper_instructions':18,'raw_operand_mutation_rejections':23,'output_sha256':{n:sha(b)for n,b in out.items()},'target_execution':False,'network':False}))

if __name__=='__main__':main()
