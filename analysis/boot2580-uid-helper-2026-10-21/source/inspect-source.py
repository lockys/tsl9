"""Portable, source-only BOOT ID2580 UID-helper operand/CFG check. No ISA execution."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[2]
BOOT_REL='exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
BOOT_SHA='650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
RETAINED_SHA='dc650ec657ccfaa6eed1cb6caacc93b608aa423b442794f04fa2241726e3b0ca'
SPAN_SHA='aeb3f1e819acd6c47f3aebd7fe001eed6df51aa6c1e8a994cf6de66a7c88d8d4'
ACCEPT_REL='apk-analysis/tsl9-v4160-ota-handoff-2026-10-21/boot-acceptance'
OLD_REL='apk-analysis/tsl9-ota-image-contract-2026-10-21/boot-contract'
PINS={ACCEPT_REL+'/identity.json':'710bd4a31fb338f0bc3d6a496c5ca70f3f35a3fa12c3c373b5070253d6bff731',ACCEPT_REL+'/final-audit.json':'d2b96075f8bc1e40439d97b87b8f5832acd7e8c7a404428f3ce5af378d42b9ac',OLD_REL+'/review.json':'45292413ff82b3efac75a069cf84293184ee3139cc719acb00c7f22d07465f4d',OLD_REL+'/seal.json':'1252de8f251635284f0c9cd1476baad228ea24e1f69da6d7ae65e1d86e94c79b'}
BASE,START,SPLIT,END=0x1000,0x1C4A,0x1C82,0x1CC4

def sha(b):return hashlib.sha256(b).hexdigest()
def encode(d):return (json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
def need(v,msg):
    if not v:raise ValueError(msg)
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def half(raw,pc):return int.from_bytes(raw[pc-BASE:pc-BASE+2],'little')
def word(raw,pc):return int.from_bytes(raw[pc-BASE:pc-BASE+4],'little')
def load(raw,pc):
    v=word(raw,pc);need(v&127==3,f'{pc:x}: LOAD opcode')
    return ((v>>7)&31,(v>>15)&31,sx(v>>20,12),(v>>12)&7)
def addi(raw,pc):
    v=word(raw,pc);need(v&0x707F==0x13,f'{pc:x}: ADDI opcode')
    return ((v>>7)&31,(v>>15)&31,sx(v>>20,12))
def c_lw(raw,pc):
    v=half(raw,pc);need(v&3==0 and v>>13==2,f'{pc:x}: C.LW opcode')
    return (8+((v>>2)&7),8+((v>>7)&7),(((v>>5)&1)<<6)|(((v>>10)&7)<<3)|(((v>>6)&1)<<2))
def c_stack(raw,pc,store):
    v=half(raw,pc);need(v&3==2 and v>>13==(6 if store else 2),f'{pc:x}: stack load/store')
    if store:return ((v>>2)&31,(((v>>7)&3)<<6)|(((v>>9)&15)<<2))
    return ((v>>7)&31,(((v>>2)&3)<<6)|(((v>>12)&1)<<5)|(((v>>4)&7)<<2))
def c_mv(raw,pc):
    v=half(raw,pc);need(v&3==2 and v>>12==8 and (v>>2)&31!=0,f'{pc:x}: C.MV opcode')
    return ((v>>7)&31,(v>>2)&31)
def c_li(raw,pc):
    v=half(raw,pc);need(v&3==1 and v>>13==2,f'{pc:x}: C.LI opcode')
    return ((v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6))
def direct(pc,n,v):
    if n==4 and v&127==0x63:
        im=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
        return ('branch',(pc+sx(im,13))&0xFFFFFFFF)
    if n==2 and v&3==1 and v>>13 in(1,5):
        im=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5)
        return ('call'if v>>13==1 else'jump',(pc+sx(im,12))&0xFFFFFFFF)
    return None

def semantic_gate(raw):
    for pc,v in {0x1C4A:0x1141,0x1C7E:0x0141,0x1C88:0x1101,0x1CB8:0x6105}.items():need(half(raw,pc)==v,f'{pc:x}: frame SP arithmetic')
    for pc,v in {0x1C4E:0x000404B7,0x1C56:0x1FFFF437}.items():need(word(raw,pc)==v,f'{pc:x}: nominal source/slot LUI')
    need(c_lw(raw,0x1C52)==(15,9,76),'1c52: first slot LW before remaining saves')
    need(load(raw,0x1C6E)==(6,9,76,2),'1c6e: fresh second slot LW via live S1')
    for pc,want in {0x1C5E:(11,8,2028),0x1C68:(11,8,2024),0x1C76:(10,18,8)}.items():need(addi(raw,pc)==want,f'{pc:x}: live copy argument')
    for pc,want in {0x1C62:(12,8),0x1C7C:(12,6),0x1C82:(15,14),0x1C94:(15,0),0x1C96:(13,14),0x1CB2:(10,0),0x1CBC:(10,1),0x1CC0:(10,1)}.items():need(c_li(raw,pc)==want,f'{pc:x}: count/result constant')
    for pc,want in {0x1C64:(18,10),0x1C8C:(8,10),0x1C8E:(10,2)}.items():need(c_mv(raw,pc)==want,f'{pc:x}: live pointer capture')
    for pc,st,want in [(0x1C4C,True,(9,4)),(0x1C54,True,(8,8)),(0x1C5A,True,(18,0)),(0x1C5C,True,(1,12)),(0x1C6C,False,(8,8)),(0x1C72,False,(1,12)),(0x1C74,False,(9,4)),(0x1C7A,False,(18,0)),(0x1C8A,True,(8,24)),(0x1C90,True,(1,28)),(0x1CB4,False,(1,28)),(0x1CB6,False,(8,24))]:need(c_stack(raw,pc,st)==want,f'{pc:x}: live stack register/offset')
    need(half(raw,0x1C66)==0x9782,'1c66: first copy C.JALR a5, link1c68')
    need(half(raw,0x1C80)==0x8302,'1c80: tail C.JR t1 without new link')
    for pc in(0x1CBA,0x1CC2):need(half(raw,pc)==0x8082,f'{pc:x}: RET through live RA')
    for pc,rs1,rs2,target in [(0x1C84,11,15,0x1CC0),(0x1CA8,12,14,0x1CBC),(0x1CAE,15,13,0x1C98)]:
        v=word(raw,pc);need(v&0x707F==0x1063 and(v>>15)&31==rs1 and(v>>20)&31==rs2 and direct(pc,4,v)==('branch',target),f'{pc:x}: strict BNE operands/target')
    need(direct(0x1C92,2,half(raw,0x1C92))==('call',0x1C4A),'1c92: internal builder call')
    need(direct(0x1CBE,2,half(raw,0x1CBE))==('jump',0x1CB4),'1cbe: mismatch common restore')
    for pc,want in {0x1C9C:(12,14,0,4),0x1CA4:(14,14,0,4)}.items():need(load(raw,pc)==want,f'{pc:x}: input-first / expected-second LBU')
    for pc,rs1 in [(0x1C98,8),(0x1CA0,2)]:
        v=word(raw,pc);need(v&0xFE00707F==0x33 and(v>>7)&31==14 and(v>>15)&31==rs1 and(v>>20)&31==15,f'{pc:x}: live base plus loop index')
    need(half(raw,0x1CAC)==0x0785,'1cac: index increment1')
    return True

def check_seal(path):
    d=json.loads(path.read_text(encoding='utf-8'));need(d.get('passed')is True,'prior seal not passed')
    for m in d['members']:
        b=(path.parent/m['path']).read_bytes();need(len(b)==m['bytes']and sha(b)==m['sha256'],f'sealed member changed:{m["path"]}')

def evt(pc,op,**kw):return {'pc':pc,'pc_hex':f'0x{pc:04X}','operation':op,**kw}

def contract(spans):
    return {'schema':'TSL9-BOOT2580-UID-helper-live-contract-v1','passed':True,'blocking_findings':[],
        'selected_source':{'catalog_ID':2580,'catalog_label':'V1.0.00','bytes':12288,'sha256':BOOT_SHA,'analysis_base':BASE,'spans':spans},
        'interface_limit':'Observed numeric-register and live-memory schema; no original C signature, ROM function identity, callee-save or physical memory ABI established.',
        'builder':{'entry':START,'bytes':SPLIT-START,'instructions':22,'entry_a0':'numeric output pointer','memory_and_call_order':[
            evt(0x1C4A,'SP = (SP-16) mod2^32'),evt(0x1C4C,'WRITE32',address='liveSP+4',value='liveS1'),evt(0x1C4E,'S1 = 0x40000'),
            evt(0x1C52,'READ32',address='liveS1+76',destination='a5',role='first loaded function pointer; only saveS1 completed at this point'),
            evt(0x1C54,'WRITE32',address='liveSP+8',value='liveS0'),evt(0x1C56,'S0 = 0x1FFFF000'),evt(0x1C5A,'WRITE32',address='liveSP+0',value='liveS2'),evt(0x1C5C,'WRITE32',address='liveSP+12',value='liveRA'),
            evt(0x1C5E,'a1 = (liveS0+2028) mod2^32'),evt(0x1C62,'a2 = 8'),evt(0x1C64,'S2 = live a0'),
            evt(0x1C66,'INDIRECT_CALL',target='a5 loaded at1C52',a0='then-current a0',a1='value assigned at1C5E',a2=8,link_RA=0x1C68),
            evt(0x1C68,'a1 = (liveS0+2024) mod2^32',role='source2 computed before restoring S0; nominal1FFFF7E8 only if relevant S0 preservation holds'),
            evt(0x1C6C,'READ32',address='liveSP+8',destination='s0'),evt(0x1C6E,'READ32',address='liveS1+76',destination='t1',role='fresh second pointer load before restoring S1; not reuse first loaded pointer'),
            evt(0x1C72,'READ32',address='liveSP+12',destination='ra',role='fresh saved return address'),evt(0x1C74,'READ32',address='liveSP+4',destination='s1'),
            evt(0x1C76,'a0 = (liveS2+8) mod2^32',role='destination2 computed before restoring S2'),evt(0x1C7A,'READ32',address='liveSP+0',destination='s2'),evt(0x1C7C,'a2 = 6'),evt(0x1C7E,'SP = (SP+16) mod2^32'),
            evt(0x1C80,'INDIRECT_TAIL',target='t1 loaded at1C6E',a0='value assigned at1C76',a1='value assigned at1C68',a2=6,link_register_written=False,possible_return_target='live RA freshly loaded at1C72')],
            'return_value':'Delegated tail target result; builder has no own RET or numeric success return.',
            'partial_frame_rule':'Do not save S0/S2/RA before the first slot load in a faithful event adapter. Each stack address uses then-current SP. A later read/call can HALT/TRANSFER; no successful unwinding is presumed.',
            'copy_ABI':'Counts8/6 and register values are observed requests. Whether either loaded target implements copying, preserves S0/S1/S2/SP, returns through expected RA, or faults is unresolved.'},
        'matcher':{'entry':SPLIT,'bytes':END-SPLIT,'instructions':26,'entry_a0':'numeric input pointer','entry_a1':'u32 request length; exact14 required here, not low8 masking',
            'length_reject':{'branch_pc':0x1C84,'target':0x1CC0,'return_result':1,'return_pc':0x1CC2,'frame_created':False,'body_memory_request_count':0,'builder_called':False},
            'normal_length_events':[
                evt(0x1C88,'SP = (SP-32) mod2^32'),evt(0x1C8A,'WRITE32',address='liveSP+24',value='liveS0'),evt(0x1C8C,'S0 = live a0',role='capture input numeric pointer'),evt(0x1C8E,'a0 = liveSP',role='builder destination'),evt(0x1C90,'WRITE32',address='liveSP+28',value='liveRA'),
                evt(0x1C92,'DIRECT_CALL',target=START,a0='value set fromSP at1C8E',link_RA=0x1C94,continuation_condition='builder delegated tail returns to expected numeric link; not automatic'),
                evt(0x1C94,'index a5 = 0'),evt(0x1C96,'limit a3 = 14'),evt(0x1C98,'a4 = (liveS0+index) mod2^32'),evt(0x1C9C,'READ8_UNSIGNED',address='a4 from1C98',destination='a2',role='request/input byte sampled first'),
                evt(0x1CA0,'a4 = (liveSP+index) mod2^32'),evt(0x1CA4,'READ8_UNSIGNED',address='a4 from1CA0',destination='a4',role='fresh expected byte after input read'),evt(0x1CA8,'if a2!=a4 jump1CBC',role='first mismatch exits; no later loop byte request'),evt(0x1CAC,'index = index+1'),evt(0x1CAE,'if index!=14 jump1C98'),evt(0x1CB2,'a0 = 0',role='all14 matched'),
                evt(0x1CB4,'READ32',address='liveSP+28',destination='ra'),evt(0x1CB6,'READ32',address='liveSP+24',destination='s0'),evt(0x1CB8,'SP = (SP+32) mod2^32'),evt(0x1CBA,'RET',target='liveRA freshly loaded at1CB4')],
            'first_mismatch_events':[evt(0x1CBC,'a0 = 1'),evt(0x1CBE,'jump common restore',target=0x1CB4)],
            'expected_buffer_is_live':True,'input_buffer_is_live':True,'zero_means_match':True,'nonreturn_or_unknown_memory_not_converted_to_mismatch':True,
            'retained_bounded_behavior':'At most14 paired LBU requests after normal builder return; each pair input first then expected current stack. No full-buffer snapshot or constant-time claim.'},
        'conditional_source_geometry':{'assumptions':['the relevant callee-saved source/destination registers retain their expected values','first loaded target normally returns to1C68','second tail target returns to the expected caller continuation','both target semantics copy exactly the requested bytes','source addresses remain stable/readable across both copies and are not changed by destination overlap or other effects','all address arithmetic and destination storage are valid in the modeled observation'],
            'copy1':{'source':0x1FFFF7EC,'bytes':8,'destination_offset':0},'copy2':{'source':0x1FFFF7E8,'bytes':6,'destination_offset':8},
            'output_source_addresses':[0x1FFFF7EC+i for i in range(8)]+[0x1FFFF7E8+i for i in range(6)],'requested_output_bytes':14,'distinct_source_byte_addresses':12,'tail2_equal_first2_under_assumptions':True,'tail_output_offsets':[12,13],'head_output_offsets':[0,1],'equal_source_addresses':[0x1FFFF7EC,0x1FFFF7ED],
            'actual_UID_values_read':False,'actual_UID_or_hardware_identity_recovered':False},
        'limits':{'source_only':True,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False,'UID_packet_created':False,'ROM_ABI_proved':False,'physical_memory_validated':False,'original_C_ABI_recovered':False,'provider_generated':False,'ROOT_modified':False,'D_modified':False}}

def run(boot,source_root,workspace,historical=False):
    raw=boot.read_bytes();need(len(raw)==12288 and sha(raw)==BOOT_SHA,'selected BOOT size/hash mismatch')
    need(int.from_bytes(raw[0x38:0x3C],'little')==BASE,'retained coordinate header mismatch')
    retained=(source_root/'retained-source.json').read_bytes();need(sha(retained)==RETAINED_SHA,'retained row hardpin mismatch')
    rows=json.loads(retained)['rows'];need(len(rows)==48,'expected48 instructions')
    if historical:
        for rel,pin in PINS.items():need(sha((workspace/rel).read_bytes())==pin,f'historical pin mismatch:{rel}')
        check_seal(workspace/ACCEPT_REL/'final-audit.json');check_seal(workspace/OLD_REL/'seal.json')
        old=json.loads((workspace/OLD_REL/'review.json').read_text(encoding='utf-8'))['source_instruction_rows']
        overlap=[r for r in old if SPLIT<=r['addr']<END]
        need(len(overlap)==26 and b''.join(bytes.fromhex(r['bytes'])for r in overlap)==raw[SPLIT-BASE:END-BASE],'historical matcher overlap')
    semantic_gate(raw);need(sha(raw[START-BASE:END-BASE])==SPAN_SHA,'122B span hash')
    starts={r['addr']for r in rows};cursor=START;ir=[];edges=[];terms=[];graph={}
    for r in rows:
        pc=r['addr'];n=r['size'];bs=raw[pc-BASE:pc-BASE+n];v=int.from_bytes(bs,'little');need(pc==cursor and bs.hex()==r['bytes'],'instruction row coverage/raw');need(n==(4 if v&3==3 else 2),'width');cursor+=n
        row={'pc':pc,'pc_hex':f'0x{pc:04X}','file_offset':pc-BASE,'width':n,'raw_hex':bs.hex(),'disassembly_from_prior':r['opcode']};d=direct(pc,n,v);succ=[]
        if d:
            kind,target=d;need(r.get('jump')==target,'raw target vs retained target')
            row['control']={'kind':kind,'target':target}
            if kind=='branch':row['control'].update({'rs1':(v>>15)&31,'rs2':(v>>20)&31,'condition':'NE'});succ=[target,pc+n]
            elif kind=='call':succ=[target,pc+n]
            else:succ=[target]
        elif pc==0x1C66:
            row['control']={'kind':'indirect-call','rs1':15,'link':0x1C68,'source_slot_load':0x1C52};succ=[pc+n];terms.append({'pc':pc,'kind':'delegated-indirect-call','target':'loaded a5','continuation':pc+n,'requires_explicit_return_to_link':True})
        elif pc==0x1C80:
            row['control']={'kind':'indirect-tail','rs1':6,'RA_source_load':0x1C72};terms.append({'pc':pc,'kind':'delegated-indirect-tail','target':'fresh loaded t1','possible_return_target':'then-live RA'})
        elif pc in(0x1CBA,0x1CC2):row['control']={'kind':'return','rs1':1};terms.append({'pc':pc,'kind':'return','target':'live RA'})
        else:
            need(not(n==4 and v&127 in(0x6F,0x67)),'unclassified32 control');need(not(n==2 and v&3==2 and v>>13==4 and(v>>2)&31==0),'unclassified16 indirect');succ=[pc+n]
        for t in succ:
            need(t in starts,'successor not instruction start');kind='local'
            if d and d[0]=='call':kind='internal-call-entry'if t==d[1]else'normal-return-to-link-required'
            if pc==0x1C66:kind='normal-return-to-link-required'
            edge={'source':pc,'target':t,'kind':kind}
            if d and d[0]=='branch':edge['branch_outcome']='taken'if t==d[1]else'not-taken'
            edges.append(edge)
        graph[pc]=succ;ir.append(row)
    need(cursor==END,'fullspan end');seen=set();todo=[SPLIT]
    while todo:
        pc=todo.pop()
        if pc in seen:continue
        seen.add(pc);todo.extend(graph[pc])
    need(seen==starts,'static graph incomplete')
    spans=[]
    for s,e,role in[(START,SPLIT,'loaded-copy builder'),(SPLIT,END,'UID byte comparator')]:
        b=raw[s-BASE:e-BASE];spans.append({'start':s,'end_exclusive':e,'file_offset':s-BASE,'bytes':len(b),'instructions':sum(s<=r['addr']<e for r in rows),'sha256':sha(b),'role':role})
    mutants=[]
    cases=[('builder_SP_frame',0x1C4A,1<<2),('first_slot_offset',0x1C52,1<<6),('source1_offset',0x1C5E,1<<20),('copy1_count8',0x1C62,1<<2),('first_copy_target_register',0x1C66,1<<7),('source2_live_S0',0x1C68,1<<15),('source2_offset',0x1C68,1<<20),('second_slot_fresh_base_S1',0x1C6E,1<<15),('second_slot_width',0x1C6E,1<<12),('saved_RA_offset',0x1C72,1<<4),('destination2_live_S2',0x1C76,1<<15),('copy2_count6',0x1C7C,1<<2),('tail_SP_increment',0x1C7E,1<<2),('tail_target_t1',0x1C80,1<<7),('exact_length14',0x1C82,1<<2),('length_BNE_to_BEQ',0x1C84,1<<12),('matcher_frame',0x1C88,1<<2),('builder_call_target',0x1C92,1<<3),('input_LBU_width',0x1C9C,2<<12),('expected_base_liveSP',0x1CA0,1<<15),('expected_LBU_width',0x1CA4,2<<12),('mismatch_BNE_to_BEQ',0x1CA8,1<<12),('success_result0',0x1CB2,1<<2),('badlength_result1',0x1CC0,1<<2)]
    for name,pc,xor in cases:
        n=4 if half(raw,pc)&3==3 else 2;mut=bytearray(raw);old=bytes(mut[pc-BASE:pc-BASE+n]);new=(int.from_bytes(old,'little')^xor).to_bytes(n,'little');mut[pc-BASE:pc-BASE+n]=new
        try:semantic_gate(mut)
        except ValueError as exc:mutants.append({'name':name,'pc':pc,'original_raw':old.hex(),'mutant_raw':new.hex(),'rejected':True,'error':str(exc)})
        else:raise ValueError('semantic mutation escaped:'+name)
    geometry=[0x1FFFF7EC+i for i in range(8)]+[0x1FFFF7E8+i for i in range(6)];need(len(geometry)==14 and len(set(geometry))==12 and geometry[:2]==geometry[-2:],'symbolic copy geometry')
    sm={'schema':'TSL9-BOOT2580-complete-UID-source-map-v1','passed':True,'selected_BOOT':{'relative_path':BOOT_REL,'bytes':len(raw),'sha256':BOOT_SHA,'analysis_base':BASE,'base_evidence':'header file0x38 LE32=0x1000; retained analysis coordinate, not physical observation'},'historical_input_hashes':PINS,'retained_source_sha256':RETAINED_SHA,'complete_span':{'start':START,'end_exclusive':END,'bytes':END-START,'sha256':SPAN_SHA},'source_spans':spans,'instructions':ir,'static_CFG':{'entry_roots':[START,SPLIT],'instruction_count':len(ir),'covered_bytes':END-START,'reachable_from_matcher_including_internal_call_entry_and_conditional_return_edges':len(seen),'uncovered_starts':sorted(starts-seen),'edges':edges,'indirect_and_return_boundaries':terms,'normal_return_edges_are_assumptions_not_execution':True,'no_ROM_target_traversed':True},'raw_semantic_mutants':mutants,'symbolic_geometry_only':True,'UID_values_read':False,'network':False,'target_execution':False,'ISA_emulation':False}
    return {'source-map.json':encode(sm),'contract.json':encode(contract(spans))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--firmware',type=Path);p.add_argument('--source-root',type=Path,default=HERE);p.add_argument('--workspace',type=Path,default=WORKSPACE);p.add_argument('--verify-historical',action='store_true');m=p.add_mutually_exclusive_group(required=True);m.add_argument('--check',action='store_true');m.add_argument('--write',action='store_true');a=p.parse_args();sr=a.source_root.resolve();w=a.workspace.resolve();boot=a.firmware.resolve()if a.firmware else w/BOOT_REL
    outputs=run(boot,sr,w,a.verify_historical)
    if a.write:
        need(sr==HERE and not(HERE/'final-audit.json').exists(),'write refused outside own unsealed package')
        for name,b in outputs.items():
            q=HERE/name;need(not q.exists()or q.read_bytes()==b,'nonidentical output exists:'+name)
            if not q.exists():q.write_bytes(b)
    else:
        for name,b in outputs.items():need((sr/name).read_bytes()==b,'byteexact replay mismatch:'+name)
        if(sr/'final-audit.json').exists():need(json.loads((sr/'final-audit.json').read_text()).get('sealed')is True,'not sealed');check_seal(sr/'final-audit.json')
    print(json.dumps({'passed':True,'mode':'readonly-byteexact'if a.check else'create-only','bytes':122,'instructions':48,'raw_mutation_rejections':24,'output_sha256':{n:sha(b)for n,b in outputs.items()},'network':False,'target_execution':False}))

if __name__=='__main__':main()
