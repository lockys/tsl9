"""Source-only static contract for selected BOOT ID2580. Never executes RV32."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
BOOT_REL = 'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
BOOT_SHA = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
RETAINED_SHA = 'e21edb56e71a3c724a886919e6493fd415bd75c14ef81ac7f1645b8e5729f713'
BASE, START, END = 0x1000, 0x21BE, 0x235C
OLD_REL = 'apk-analysis/tsl9-ota-image-contract-2026-10-21/boot-contract'
ACCEPT_REL = 'apk-analysis/tsl9-v4160-ota-handoff-2026-10-21/boot-acceptance'
PINS = {
    OLD_REL+'/seal.json': '1252de8f251635284f0c9cd1476baad228ea24e1f69da6d7ae65e1d86e94c79b',
    OLD_REL+'/review.json': '45292413ff82b3efac75a069cf84293184ee3139cc719acb00c7f22d07465f4d',
    ACCEPT_REL+'/final-audit.json': 'd2b96075f8bc1e40439d97b87b8f5832acd7e8c7a404428f3ce5af378d42b9ac',
    ACCEPT_REL+'/facts.json': 'af0d7d352758bf3f2a83080f30ffd20fed2293aef71d83f350781b64888aa8e2',
    ACCEPT_REL+'/source-map.json': '77c9a864635bceb85f4ab283013ed8e8634a69dd566d0dff2dd23bc15f463d8b',
    ACCEPT_REL+'/response-wrappers.json': '11ae81d8300309f95b31d6e9187a0abb7fb56abdf23eace9c541a630bb58dea6',
}

def sha(b): return hashlib.sha256(b).hexdigest()
def encoded(d): return (json.dumps(d, indent=2, ensure_ascii=False)+'\n').encode('utf-8')
def require(v, msg):
    if not v: raise ValueError(msg)
def sx(v, n): return v-(1<<n) if v&(1<<(n-1)) else v

def direct(pc, width, v):
    """Decode only direct control fields, without CPU state or instruction execution."""
    if width == 4:
        op=v&127
        if op == 0x6F:
            im=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
            return ('call' if (v>>7)&31 == 1 else 'jump', (pc+sx(im,21))&0xFFFFFFFF)
        if op == 0x63:
            im=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
            return ('branch', (pc+sx(im,13))&0xFFFFFFFF)
    else:
        q=v&3; f=(v>>13)&7
        if q == 1 and f in (1,5):
            im=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5)
            return ('call' if f == 1 else 'jump', (pc+sx(im,12))&0xFFFFFFFF)
        if q == 1 and f in (6,7):
            im=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5)
            return ('branch', (pc+sx(im,9))&0xFFFFFFFF)
    return None

def h(raw, pc): return int.from_bytes(raw[pc-BASE:pc-BASE+2],'little')
def word(raw, pc): return int.from_bytes(raw[pc-BASE:pc-BASE+4],'little')
def load(raw, pc):
    v=word(raw,pc); require(v&127 == 3, f'{pc:x}: load opcode')
    return ((v>>7)&31, (v>>15)&31, sx(v>>20,12), (v>>12)&7)
def store(raw, pc):
    v=word(raw,pc); require(v&127 == 0x23, f'{pc:x}: store opcode')
    return ((v>>20)&31, (v>>15)&31, sx(((v>>25)<<5)|((v>>7)&31),12), (v>>12)&7)
def addi(raw, pc):
    v=word(raw,pc); require(v&0x707F == 0x13, f'{pc:x}: ADDI opcode')
    return ((v>>7)&31, (v>>15)&31, sx(v>>20,12))
def c_lw(raw,pc):
    v=h(raw,pc); require(v&3 == 0 and v>>13 == 2, f'{pc:x}: C.LW opcode')
    off=(((v>>5)&1)<<6)|(((v>>10)&7)<<3)|(((v>>6)&1)<<2)
    return (8+((v>>2)&7), 8+((v>>7)&7), off)
def c_stack(raw,pc,is_store):
    v=h(raw,pc)
    require(v&3 == 2 and v>>13 == (6 if is_store else 2), f'{pc:x}: stack operation')
    if is_store: return ((v>>2)&31, (((v>>7)&3)<<6)|(((v>>9)&15)<<2))
    return ((v>>7)&31, (((v>>2)&3)<<6)|(((v>>12)&1)<<5)|(((v>>4)&7)<<2))

def semantic_gate(raw):
    """Raw operand gates; deliberately independent of the source hash gate."""
    for pc, wanted in {0x2202:(15,3,139,4),0x2210:(15,12,1,4),0x2214:(8,12,0,4),0x22E2:(15,12,0,4),0x231E:(15,3,139,4)}.items():
        require(load(raw,pc)==wanted,f'{pc:x}: live load register/width/offset')
    for pc,wanted in {0x22A8:(0,3,139,0),0x22EC:(15,3,139,0),0x2312:(0,3,139,0),0x2318:(15,12,0,0),0x2336:(0,3,139,0)}.items():
        require(store(raw,pc)==wanted,f'{pc:x}: live store register/width/offset')
    for pc,wanted in {0x2208:(15,0,1026),0x2244:(11,12,2),0x2258:(12,0,1024),0x2262:(20,0,1024),0x226E:(18,18,256),0x227A:(14,0,1024),0x2298:(11,0,87),0x22A4:(10,12,1),0x22CA:(11,13,-1),0x22CE:(10,12,1),0x22C0:(11,0,85),0x22FA:(11,0,83),0x2328:(12,0,200),0x2340:(12,0,400),0x2356:(11,0,69)}.items():
        require(addi(raw,pc)==wanted,f'{pc:x}: argument/increment ADDI')
    require(c_lw(raw,0x2256)==(15,15,76),'2256: loaded function pointer slot')
    require(h(raw,0x225E)==0x9782,'225e: C.JALR loaded a5 with RA link')
    require(c_lw(raw,0x2282)==(12,13,0),'2282: Flash first LW')
    require(c_lw(raw,0x2288)==(13,13,0),'2288: live source second LW')
    for pc,st,wanted in [(0x22D6,True,(13,12)),(0x22D8,True,(12,8)),(0x22DC,False,(12,8)),(0x22DE,False,(13,12)),(0x22F6,False,(12,8)),(0x22F8,False,(13,12))]:
        require(c_stack(raw,pc,st)==wanted,f'{pc:x}: live SP save/reload')
    for pc,target,kind in [(0x220C,0x21E2,'branch'),(0x2240,0x21E2,'branch'),(0x2272,0x20E6,'call'),(0x2274,0x2266,'branch'),(0x228A,0x21E2,'branch'),(0x2290,0x227E,'branch'),(0x22AC,0x1C82,'call'),(0x22DA,0x1C82,'call'),(0x22F0,0x250E,'call'),(0x22F4,0x2184,'call'),(0x22C6,0x2ABA,'jump'),(0x230E,0x2AA0,'jump'),(0x233A,0x1AFA,'call'),(0x234E,0x1AFA,'call')]:
        width=4 if h(raw,pc)&3 == 3 else 2
        require(direct(pc,width,int.from_bytes(raw[pc-BASE:pc-BASE+width],'little'))==(kind,target),f'{pc:x}: direct control target')
    require((word(raw,0x2240)>>12)&7 == 6,'2240: unsigned BLTU guard')
    for pc in (0x22AE,0x22E0):
        require((h(raw,pc)>>13)&7 == 7, f'{pc:x}: UID nonzero failure branch')
    for pc,expected in {0x2294:0x4681,0x2296:0x4601,0x22BE:0x4601,0x22F2:0x4509,0x2326:0x4681,0x232C:0x4581,0x233E:0x4681,0x2344:0x4581,0x2352:0x4681,0x2354:0x4601}.items():
        require(h(raw,pc)==expected,f'{pc:x}: compressed argument constant')
    require(word(raw,0x22A0)==0x0FF6F593 and word(raw,0x22D2)==0x0FF5F593,'UID length is uint8(n-1)')
    require(word(raw,0x232E)==0xFFFFF517 and addi(raw,0x2332)==(10,10,1534),'scheduler callback192c')
    require(word(raw,0x2346)==0x00000517 and addi(raw,0x234A)==(10,10,-612),'scheduler callback20e2')
    return True

def verify_seal(path):
    seal=json.loads(path.read_text(encoding='utf-8')); require(seal.get('passed') is True, 'prior seal not passed')
    for member in seal['members']:
        p=path.parent/member['path']; b=p.read_bytes()
        require(len(b)==member['bytes'] and sha(b)==member['sha256'], f'prior sealed member drift: {p.name}')

def event(pc, op, **kwargs): return {'pc':pc,'pc_hex':f'0x{pc:04X}','operation':op,**kwargs}

def make_contract(body_hash, input_hashes):
    return {
        'schema':'TSL9-BOOT-ID2580-command-source-contract-v1','passed':True,'blocking_findings':[],
        'selected_boot':{'catalog_ID':2580,'catalog_version_label':'V1.0.00','bytes':12288,'sha256':BOOT_SHA,'analysis_base':BASE,'body':{'start':START,'end_exclusive':END,'bytes':414,'sha256':body_hash}},
        'inputs':input_hashes,
        'entry_register_schema':{'a0':'numeric context saved in s1 at21D0','a1':'command numeric u32','a2':'numeric payload address u32','a3':'length numeric u32','gp':'live numeric GP; active byte at (gp+139) mod2^32','sp':'live numeric SP, after prologue SP=entrySP-48 modulo2^32'},
        'schema_limit':'Observed register/memory schema for a synthetic adapter, not an original C signature or proof of callee-save, SP, GP, memory, ROM or hardware ABI.',
        'frame':{'prologue':[START,0x21CC],'frame_bytes':48,'saved_register_offsets':{'ra':44,'s0':40,'s1':36,'s2':32,'s3':28,'s4':24},'body_stack_slots':{'payload':8,'length':12},'live_stack_rule':'S stores use then-current SP; each reload after delegated calls uses then-current SP, not an automatic host snapshot. No physical stack memory proof.'},
        'command_dispatch':{'S':83,'U':85,'W':87,'E':69,'R':{'value':82,'local_case':False,'effect':'falls to local restore/RET21E2; no page-read case in this body'},'other':'restore/RET21E2'},
        'common_delegation_rule':'Each call can RETURN normally, HALT or TRANSFER through the synthetic backend. Only RETURN reaches its following instruction. Ignored numeric retval does not turn a nonreturn into a return. Register preservation is an explicit adapter assumption, not established runtime ABI.',
        'commands':{
            'W':{
                'entry':0x2202,'guards':[event(0x2202,'READ8',address='liveGP+139'),event(0x2206,'return if active==0'),event(0x220C,'return if length!=1026')],
                'page_reads':[event(0x2210,'READ8',address='payload+1 mod2^32',role='low byte sampled first'),event(0x2214,'READ8',address='payload+0',role='high byte sampled second')],
                'page_formula':{'page':'(second_byte<<8)|first_byte','destination':'((0x20020+page)<<10) mod2^32','alias_base':0x08008000,'offset':'(destination+0xF7FF8000) mod2^32','unsigned_limit':0x17F00,'reject_pc':0x2240,'accepted_u16_pages':[0,95],'runtime75_page_fit':[0,74],'fit_is_hardware_or_version_proof':False},
                'source_alignment':{'source':'payload+2 mod2^32','misalignment':'source&3','aligned_source':'source-misalignment mod2^32','unaligned_only':[event(0x2256,'READ32',address=0x4004C,role='load pointer, not a direct function target'),event(0x225E,'INDIRECT_CALL',target='loaded a5',a0='aligned_source',a1='source',a2=1024)],'overlap_copy_semantics_unknown':True},
                'program_calls':{'site':0x2272,'delegated_target':0x20E6,'offsets':[0,256,512,768],'a0':'destination+offset mod2^32','a1':'aligned_source+offset mod2^32','increment_before_call_pc':0x226E,'increment':256,'numeric_return_value_ignored':True,'all_four_require_normal_returns':True},
                'readback':{'offsets':{'first':0,'last':1020,'step':4},'events':[event(0x2282,'READ32',address='destination+offset',role='Flash first'),event(0x2288,'READ32',address='aligned_source+offset',role='live source second, after Flash callback effects'),event(0x228A,'return silently if unequal')],'source_is_live':True,'snapshot_source_not_equivalent':True,'mismatch_does_not_clear_active_locally':True},
                'success_tail':{'site':0x230E,'target':0x2AA0,'a0':'saved context s1','a1':87,'a2':0,'a3':0},
                'not_proved_in_body':['page receipt bitmap','whole-image digest','firmware version compatibility','physical write completion','full APP startup compatibility']},
            'U':{'entry':0x229E,'events':[event(0x22A8,'WRITE8',address='liveGP+139',value=0,role='before UID call, even on later failure'),event(0x22AC,'DIRECT_CALL',target=0x1C82,a0='payload+1 mod2^32',a1='uint8(length-1)'),event(0x22AE,'return if raw UID result!=0'),event(0x22C6,'TAIL_CALL',target=0x2ABA,a0='saved context s1',a1=85,a2=0)],'mode_not_read_locally':True,'does_not_start_W_session':True,'UID_is_delegated':True},
            'S':{'entry':0x22CA,'events':[event(0x22D6,'WRITE32',address='liveSP+12',value='length'),event(0x22D8,'WRITE32',address='liveSP+8',value='payload numeric address'),event(0x22DA,'DIRECT_CALL',target=0x1C82,a0='payload+1 mod2^32',a1='uint8(length-1)'),event(0x22DC,'READ32',address='liveSP+8',role='fresh payload before UID-result branch'),event(0x22DE,'READ32',address='liveSP+12',role='fresh length before UID-result branch'),event(0x22E0,'fail if raw UID result!=0'),event(0x22E2,'READ8',address='fresh payload address',role='fresh mode after UID'),event(0x22E8,'fail if mode!=1'),event(0x22EC,'WRITE8',address='liveGP+139',value=1),event(0x22F0,'DIRECT_CALL',target=0x250E,role='delegated cancellation; normal return needed'),event(0x22F4,'DIRECT_CALL',target=0x2184,a0=2,role='metadata selector; numeric retval ignored, nonreturn preserved'),event(0x22F6,'READ32',address='liveSP+8',role='fresh payload after cancellation and metadata'),event(0x22F8,'READ32',address='liveSP+12',role='fresh length after cancellation and metadata'),event(0x230E,'TAIL_CALL',target=0x2AA0,a0='saved context s1',a1=83,a2='fresh payload',a3='fresh length')],
                'failure_events':[event(0x2312,'WRITE8',address='liveGP+139',value=0),event(0x2318,'WRITE8',address='payload freshly loaded at22DC',value=255),event(0x231C,'jump to S response arguments',target=0x22FA)],
                'length_gate':'Delegated1C82 sees uint8(n-1); not a local strict n15 guard. Raw result0 means match.',
                'metadata_return_test_between_22F4_and_22F6':False,'echo_is_original_snapshot':False},
            'E':{'entry':0x231E,'events':[event(0x231E,'READ8',address='liveGP+139'),event(0x2322,'return if active==0'),event(0x2326,'overwrite a3',value=0),event(0x2328,'overwrite incoming payload register a2',value=200),event(0x2336,'WRITE8',address='liveGP+139',value=0),event(0x233A,'DIRECT_CALL',target=0x1AFA,a0=0x192C,a1=0,a2=200,a3=0),event(0x234E,'DIRECT_CALL',target=0x1AFA,a0=0x20E2,a1=0,a2=400,a3=0),event(0x230E,'TAIL_CALL',target=0x2AA0,a0='saved context s1',a1=69,a2=0,a3=0)],'local_UID_call':False,'local_length_guard':False,'incoming_payload_read':False,'local_mode_guard':False,'scheduling_or_callback_execution_proved':False}
        },
        'delegated_boundaries':[
            {'target':0x1C82,'callsites':[0x22AC,0x22DA],'role':'UID comparator; raw0 match, nonzero fail; uint8 length passed; no UID values or packets created'},
            {'target_expression':'READ32(0x4004C)','callsites':[0x225E],'role':'opaque loaded copy pointer, 1024-byte request; source/destination overlap and actual ABI open'},
            {'target':0x20E6,'callsites':[0x2272],'role':'program256 request, four iterations; Flash/CSR/status implementation delegated'},
            {'target':0x250E,'callsites':[0x22F0],'role':'cancellation boundary'},
            {'target':0x2184,'callsites':[0x22F4],'role':'selector2 metadata request; return ignored only when normal return occurs; persistence/Flash implementation delegated'},
            {'target':0x1AFA,'callsites':[0x233A,0x234E],'role':'schedule-like request boundary; no timer/IRQ execution proved'},
            {'target':0x2ABA,'tailsites':[0x22C6],'role':'three explicit args context/U/status0; wrapper creates one-byte response'},
            {'target':0x2AA0,'tailsites':[0x230E],'role':'four explicit args context/cmd/pointer/n; no automatic one-byte substitution for zero ptr/n'}],
        'limits':{'source_only':True,'all_control_paths_conditioned_on_delegated_normal_return_or_explicit_terminal':True,'original_C_ABI_recovered':False,'original_RAM_or_GP_SP_validated':False,'physical_BOOT_version_matched':False,'target_executed':False,'ISA_emulation':False,'network':False,'hardware':False,'real_UID_packet_created':False,'provider_generated':False,'ROOT_modified':False,'D_modified':False,'flashable':False}
    }

def run(root, boot, source_root=HERE, verify_historical=False):
    inputs=dict(PINS)
    if verify_historical:
        for rel,pin in PINS.items():
            b=(root/rel).read_bytes(); require(sha(b)==pin,f'pinned source drift: {rel}')
        verify_seal(root/OLD_REL/'seal.json'); verify_seal(root/ACCEPT_REL/'final-audit.json')
    retained_raw=(source_root/'retained-source.json').read_bytes()
    require(sha(retained_raw)==RETAINED_SHA,'retained selected-row source pin mismatch')
    inputs['retained-source.json']=RETAINED_SHA
    retained=json.loads(retained_raw)
    raw=boot.read_bytes(); require(len(raw)==12288 and sha(raw)==BOOT_SHA,'selected BOOT size/hash mismatch')
    require(int.from_bytes(raw[0x38:0x3C],'little')==BASE,'base header mismatch')
    oldrows=retained['rows']; rows=[r for r in oldrows if START<=r['addr']<END]
    dependency_rows=oldrows
    require(len(rows)==144,'expected144 source instruction rows')
    cursor=START; instr=[]; graph={}; edges=[]; calls=[]; terms=[]
    starts={r['addr'] for r in rows}
    semantic_gate(raw)
    for row in rows:
        pc=row['addr']; n=row['size']; bs=raw[pc-BASE:pc-BASE+n]
        require(pc==cursor and bs.hex()==row['bytes'],f'exact source row at{pc:x}')
        require(n==(4 if int.from_bytes(bs[:2],'little')&3==3 else 2),'instruction width mismatch')
        cursor+=n; v=int.from_bytes(bs,'little'); d=direct(pc,n,v); succ=[]
        ir={'pc':pc,'pc_hex':f'0x{pc:04X}','file_offset':pc-BASE,'width':n,'raw_hex':bs.hex(),'disassembly_from_prior':row['opcode']}
        if d:
            kind,target=d
            if 'jump' in row: require(row['jump']==target,f'prior direct target mismatch{pc:x}')
            if kind=='call':
                require(target not in starts,'unexpected internal call in boundedbody')
                calls.append({'pc':pc,'kind':'direct','target':target,'continuation':pc+n,'continuation_requires_normal_return':True}); succ=[pc+n]
                edges.append({'source':pc,'target':target,'kind':'delegated-call','inside_body':False})
            elif kind=='branch': succ=[target,pc+n]
            elif target in starts: succ=[target]
            else:
                terms.append({'pc':pc,'kind':'delegated-tail','target':target})
                edges.append({'source':pc,'target':target,'kind':'delegated-tail','inside_body':False})
            ir['decoded_control']={'kind':kind,'target':target}
            if kind=='branch':
                if n==4:
                    ir['decoded_control'].update({'rs1':(v>>15)&31,'rs2':(v>>20)&31,'condition':{0:'EQ',1:'NE',4:'LT_SIGNED',5:'GE_SIGNED',6:'LT_UNSIGNED',7:'GE_UNSIGNED'}[(v>>12)&7]})
                else:
                    ir['decoded_control'].update({'rs1':8+((v>>7)&7),'rs2':0,'condition':'EQ' if v>>13==6 else 'NE'})
        elif n==2 and v==0x9782:
            require(pc==0x225E,'unexpected indirectcall'); calls.append({'pc':pc,'kind':'indirect','target':'a5 loaded at2256 from nominal4004C','continuation':pc+n,'continuation_requires_normal_return':True});succ=[pc+n]
            ir['decoded_control']={'kind':'indirect-call','rs1':15,'link_register':1}
        elif n==2 and v==0x8082:
            require(pc==0x21F0,'unexpected return'); terms.append({'pc':pc,'kind':'return','rs1':1});ir['decoded_control']={'kind':'return','rs1':1}
        else:
            require(not(n==4 and v&127==0x67),'unclassified JALR');
            require(not(n==2 and v&3==2 and v>>13==4 and (v>>2)&31==0),'unclassified compressed indirect')
            succ=[pc+n]
        for target in succ:
            require(target in starts,f'noninstruction internal successor{pc:x}->{target:x}')
            edge={'source':pc,'target':target,'kind':'normal-return-continuation' if d and d[0]=='call' or pc==0x225E else 'local','inside_body':True}
            if d and d[0]=='branch':edge['branch_outcome']='taken' if target==d[1] else 'not-taken'
            edges.append(edge)
        graph[pc]=succ; instr.append(ir)
    require(cursor==END,'noncovering source interval')
    seen=set(); todo=[START]
    while todo:
        pc=todo.pop()
        if pc in seen: continue
        seen.add(pc);todo.extend(graph[pc])
    require(seen==starts,'boundedCFG instruction coverage incomplete')
    require(len(calls)==8 and len(terms)==3,'call/terminal cardinality mismatch')
    body=raw[START-BASE:END-BASE]; bodyhash=sha(body)
    spans=[]
    for start,end,role in [(START,END,'complete selected command body'),(0x1C82,0x1CC4,'delegated UID helper bounded reference'),(0x20E6,0x2126,'delegated program256 wrapper bounded reference'),(0x2184,0x21BE,'delegated metadata helper bounded reference'),(0x2AA0,0x2AD0,'delegated response wrappers bounded reference')]:
        bs=raw[start-BASE:end-BASE]
        # The pre-existing sealed disassembly must cover every chosen dependency byte too.
        sr=sorted([r for r in dependency_rows if start<=r['addr']<end],key=lambda r:r['addr']); require(sum(r['size'] for r in sr)==end-start,'dependency source span coverage')
        require(b''.join(bytes.fromhex(r['bytes']) for r in sr)==bs,'dependency source bytes drift')
        spans.append({'start':start,'end_exclusive':end,'file_offset':start-BASE,'bytes':len(bs),'sha256':sha(bs),'role':role})
    mutants=[]
    for name,pc,delta in [('active_offset139_to138',0x2202,1<<20),('page_first_lowoffset1_to0',0x2210,1<<20),('page_second_highoffset0_to1',0x2214,1<<20),('W_length1026_to1027',0x2208,1<<20),('copy1024_to1025',0x2258,1<<20),('copy_slot4C_to48',0x2256,1<<6),('quarter_increment256_to257',0x226E,1<<20),('unsigned_page_guard_to_signed',0x2240,2<<12),('Flash_LW_destination_register',0x2282,1<<2),('source_LW_base_register',0x2288,1<<7),('UID_failure_BNEZ_to_BEQZ',0x22E0,1<<13),('S_saved_pointer_offset',0x22D8,1<<9),('S_fresh_pointer_offset_after_UID',0x22DC,1<<4),('S_fresh_length_offset_after_metadata',0x22F8,1<<4),('S_metadata_selector2_to3',0x22F2,1<<2),('E_length_clobber0_to1',0x2326,1<<2),('E_delay200_to201',0x2328,1<<20),('E_active_store_offset139_to138',0x2336,1<<7)]:
        n=4 if h(raw,pc)&3==3 else 2; changed=bytearray(raw); before=bytes(changed[pc-BASE:pc-BASE+n]); after=(int.from_bytes(before,'little')^delta).to_bytes(n,'little'); changed[pc-BASE:pc-BASE+n]=after
        try: semantic_gate(changed)
        except ValueError as exc: mutants.append({'name':name,'pc':pc,'original_raw':before.hex(),'mutant_raw':after.hex(),'rejected':True,'gate_error':str(exc)})
        else: raise ValueError(f'raw semantic mutation escaped: {name}')
    # Exhaustive arithmetic, not execution of the original ISA.
    pages=[p for p in range(65536) if (((((0x20020+p)<<10)&0xFFFFFFFF)+0xF7FF8000)&0xFFFFFFFF)<=0x17F00]
    require(pages==list(range(96)),'page arithmetic domain')
    source_map={'schema':'TSL9-BOOT-ID2580-complete-command-source-map-v1','passed':True,'selected_boot_relative_path':BOOT_REL,'selected_boot_bytes':len(raw),'selected_boot_sha256':BOOT_SHA,'analysis_base':BASE,'base_evidence':{'header_file_offset':0x38,'LE32':BASE,'scope':'retained source coordinate; physical load not measured'},'inputs':inputs,'source_spans':spans,'instructions':instr,'cfg':{'entry':START,'end_exclusive':END,'instruction_count':len(instr),'covered_bytes':len(body),'reachable_instruction_count_under_normal_return_edges':len(seen),'uncovered_instruction_starts':sorted(starts-seen),'edges':edges,'calls':calls,'terminals':terms,'external_callees_not_traversed':True,'coverage_is_static_control_graph_not_execution':True},'raw_semantic_mutations':mutants,'arithmetic_check':{'u16_candidates':65536,'accepted_count':len(pages),'accepted_first':pages[0],'accepted_last':pages[-1]},'network':False,'target_executed':False,'ISA_emulation':False,'real_UID_packet_created':False}
    contract=make_contract(bodyhash,inputs)
    return {'source-map.json':encoded(source_map),'contract.json':encoded(contract)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace',type=Path,default=WORKSPACE,help='explicit existing evidence workspace; no filesystem search')
    p.add_argument('--firmware','--boot',dest='boot',type=Path,help='exact selected BOOT; size and SHA256 strictly verified')
    p.add_argument('--source-root',type=Path,default=HERE,help='this self-contained source evidence package; no historical tree needed')
    p.add_argument('--verify-historical',action='store_true',help='also read/recheck original sealed historical chains below --workspace')
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true')
    a=p.parse_args();root=a.workspace.resolve();boot=a.boot.resolve() if a.boot else root/BOOT_REL;source_root=a.source_root.resolve()
    outputs=run(root,boot,source_root,a.verify_historical)
    if a.write:
        require(source_root==HERE,'write is restricted to this checker own directory')
        require(not(HERE/'final-audit.json').exists(),'sealed output: write refused')
        for name,bs in outputs.items():
            path=HERE/name; require(not path.exists() or path.read_bytes()==bs,f'nonidentical output already exists: {name}')
            if not path.exists():path.write_bytes(bs)
    else:
        for name,bs in outputs.items():require((source_root/name).read_bytes()==bs,f'readonly replay mismatch: {name}')
        if (source_root/'final-audit.json').exists():
            require(json.loads((source_root/'final-audit.json').read_text(encoding='utf-8')).get('sealed') is True,'final seal missing sealed:true')
            verify_seal(source_root/'final-audit.json')
    print(json.dumps({'passed':True,'mode':'readonly-byteexact' if a.check else 'create-only','body_bytes':414,'instructions':144,'raw_mutation_rejections':18,'output_sha256':{k:sha(v) for k,v in outputs.items()},'network':False,'target_executed':False}))

if __name__=='__main__': main()
