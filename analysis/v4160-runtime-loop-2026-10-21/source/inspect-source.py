"""ID2966 V4.1.60 main/init/loop/dispatcher source-only static contract."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[2]
FIRMWARE_REL='exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FIRMWARE_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RETAINED_SHA='95e33f2e2bb76f13d959b16c753351c01ae02ce6619028d97b63965aef11d880'
BASE=0x8000
INIT_CALLS=[(0x9254,0x18834),(0x9258,0x9A42),(0x925C,0x1973C),(0x9260,0x9F4C),(0x9264,0x131C2),(0x9268,0x8E88),(0x926A,0x9B4E),(0x926E,0x9958),(0x9270,0x9F12),(0x9274,0x12D92),(0x9278,0x14C8A),(0x927C,0x154A6),(0x9280,0x17040),(0x9284,0x173A2)]
RANGES={'main':(0x9008,18),'init':(0x9250,64),'loop':(0x8180,42),'dispatcher':(0x901A,96)}

def sha(b):return hashlib.sha256(b).hexdigest()
def enc(d):return(json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
def need(v,msg):
    if not v:raise ValueError(msg)
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def half(b,p):return int.from_bytes(b[p-BASE:p-BASE+2],'little')
def word(b,p):return int.from_bytes(b[p-BASE:p-BASE+4],'little')
def c_addi(b,p):
    v=half(b,p);need(v&3==1 and v>>13==0,f'{p:x}: C.ADDI');return((v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6))
def c_li(b,p):
    v=half(b,p);need(v&3==1 and v>>13==2,f'{p:x}: C.LI');return((v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6))
def c_stack(b,p,st):
    v=half(b,p);need(v&3==2 and v>>13==(6 if st else 2),f'{p:x}: SP load/store')
    if st:return((v>>2)&31,(((v>>7)&3)<<6)|(((v>>9)&15)<<2))
    return((v>>7)&31,(((v>>2)&3)<<6)|(((v>>12)&1)<<5)|(((v>>4)&7)<<2))
def c_mem(b,p,st=False):
    v=half(b,p);need(v&3==0 and v>>13==(6 if st else 2),f'{p:x}: C.LW/SW');return(8+((v>>2)&7),8+((v>>7)&7),(((v>>5)&1)<<6)|(((v>>10)&7)<<3)|(((v>>6)&1)<<2))
def load(b,p):
    v=word(b,p);need(v&127==3,f'{p:x}: LOAD');return((v>>7)&31,(v>>15)&31,sx(v>>20,12),(v>>12)&7)
def store(b,p):
    v=word(b,p);need(v&127==0x23,f'{p:x}: STORE');return((v>>20)&31,(v>>15)&31,sx(((v>>25)<<5)|((v>>7)&31),12),(v>>12)&7)
def addi(b,p):
    v=word(b,p);need(v&0x707F==0x13,f'{p:x}: ADDI');return((v>>7)&31,(v>>15)&31,sx(v>>20,12))
def direct(p,n,v):
    if n==4 and v&127==0x6F:
        im=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1);return('call'if(v>>7)&31==1 else'jump',(p+sx(im,21))&0xFFFFFFFF)
    if n==4 and v&127==0x63:
        im=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1);return('branch',(p+sx(im,13))&0xFFFFFFFF)
    if n==2 and v&3==1 and v>>13 in(1,5):
        im=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5)
        return('call'if v>>13==1 else'jump',(p+sx(im,12))&0xFFFFFFFF)
    if n==2 and v&3==1 and v>>13 in(6,7):
        im=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5);return('branch',(p+sx(im,9))&0xFFFFFFFF)
    return None
def control(b,p,kind,target):
    n=4 if half(b,p)&3==3 else 2;need(direct(p,n,int.from_bytes(b[p-BASE:p-BASE+n],'little'))==(kind,target),f'{p:x}: direct {kind} target')

def gate(b):
    for p,want in[(0x9008,(2,-16)),(0x9016,(2,16)),(0x9250,(2,-16)),(0x928A,(2,16)),(0x8180,(2,-16)),(0x901A,(2,-16)),(0x906C,(2,16)),(0x9070,(8,1))]:need(c_addi(b,p)==want,f'{p:x}: frame/index arithmetic')
    for p,st,want in[(0x900A,True,(1,12)),(0x9012,False,(1,12)),(0x9252,True,(1,12)),(0x9288,False,(1,12)),(0x8182,True,(8,8)),(0x8186,True,(9,4)),(0x8188,True,(18,0)),(0x818A,True,(1,12)),(0x901C,True,(8,8)),(0x901E,True,(1,12)),(0x9020,True,(9,4)),(0x9066,False,(1,12)),(0x9068,False,(8,8)),(0x906A,False,(9,4))]:need(c_stack(b,p,st)==want,f'{p:x}: live stack register/offset')
    for p in(0x9018,0x906E):need(half(b,p)==0x8082,f'{p:x}: RET through live RA')
    need(c_li(b,0x9014)==(10,0),'9014: main0 only after loop return')
    control(b,0x900C,'call',0x9250);control(b,0x900E,'call',0x8180)
    for p,t in INIT_CALLS:control(b,p,'call',t)
    control(b,0x928C,'jump',0x17BF6)
    need(half(b,0x8184)==0x642D,'8184: S0 LUI before remaining saves')
    need(word(b,0x818C)==0x20000937 and word(b,0x8190)==0x400034B7,'loop S2/S1 LUI')
    need(addi(b,0x8194)==(8,8,-1366),'8194: nominal S0 AAAA')
    need(load(b,0x8198)==(15,18,0,2),'8198: fresh pointer from live S2')
    need(half(b,0x819C)==0x9782,'819c: unguarded loaded A5 call')
    control(b,0x819E,'call',0x17002);control(b,0x81A2,'call',0x12C58)
    need(c_mem(b,0x81A6,True)==(8,9,0),'81a6: live S0→live S1 WRITE32')
    control(b,0x81A8,'jump',0x8198)
    for p,want in[(0x9022,(8,0)),(0x9024,(14,15)),(0x902E,(15,12)),(0x905A,(10,1)),(0x9076,(10,0))]:need(c_li(b,p)==want,f'{p:x}: dispatcher constant')
    need(word(b,0x9026)==0x4085D7B3 and half(b,0x902A)==0x8B85,'9026/2a: arithmetic shift inputA1 byS0, AND1')
    need(word(b,0x9030)==0x02F40733,'9030: MUL stride12')
    need(word(b,0x9034)==0x20003797 and addi(b,0x9038)==(15,15,-556),'9034: own PCREL registry base')
    need(half(b,0x903C)==0x84AE and half(b,0x903E)==0x97BA,'903c: save full A1 in S1 then add record offset')
    need(c_mem(b,0x9040)==(13,15,4),'9040: callback pointer first')
    need(load(b,0x9044)==(14,15,0,4),'9044: mode byte BEFORE argument')
    need(c_mem(b,0x9048)==(10,15,8),'9048: argument after mode byte')
    need(word(b,0x904A)==0x0FF77713,'904a: mode ANDI255 after argument')
    need(store(b,0x9050)==(0,15,4,2)and store(b,0x9054)==(0,15,8,2),'mode0 clears callback then argument BEFORE call')
    need(half(b,0x9058)==0x9682,'9058: loaded A3 call/link905a')
    need(word(b,0x905C)==0x00851533 and half(b,0x9060)==0x8D25,'return uses THEN-LIVE S0/S1')
    need(half(b,0x9062)==0x0542 and half(b,0x9064)==0x8141,'return low16 truncation')
    for p,target,funct3,reg in[(0x902C,0x9070,6,15),(0x9042,0x905A,6,13),(0x904E,0x9058,7,14)]:
        v=half(b,p);need(v&3==1 and v>>13==funct3 and 8+((v>>7)&7)==reg,f'{p:x}: compressed branch register/condition');control(b,p,'branch',target)
    v=word(b,0x9072);need(v&0x707F==0x1063 and(v>>15)&31==8 and(v>>20)&31==14,'9072: compare scan index to15');control(b,0x9072,'branch',0x9026);control(b,0x9078,'jump',0x9066)
    base=(0x9034+(word(b,0x9034)&0xFFFFF000)+sx(word(b,0x9038)>>20,12))&0xFFFFFFFF
    need(base==0x2000BE08,'registry PC-relative numeric base')
    return base

def ev(p,op,**kw):return{'pc':p,'pc_hex':f'0x{p:X}','operation':op,**kw}

def make_contract(base,spans):
    return{'schema':'ID2966-runtime-loop-live-contract-v1','passed':True,'blocking_findings':[],'source_firmware':{'catalog_ID':2966,'version':'V4.1.60','bytes':76800,'sha256':FIRMWARE_SHA,'analysis_base':BASE},'source_spans':spans,'interface_limit':'Synthetic numeric/live-state C reconstruction contract from raw source; no original C prototype or ABI recovery.',
        'common_call_rule':'Calls carry then-live argument registers and numeric link RA. Only an explicit return to the expected link permits continuation. HALT/TRANSFER or unknown callee effects are preserved. No automatic SP/GP/callee-saved register or stack restoration is inferred.',
        'main':{'entry':0x9008,'ordered_effects':[ev(0x9008,'SP=(liveSP-16) mod2^32'),ev(0x900A,'WRITE32',address='liveSP+12',value='liveRA'),ev(0x900C,'DIRECT_CALL',target=0x9250,link_RA=0x900E,args='then-live a0..a7'),ev(0x900E,'DIRECT_CALL',target=0x8180,link_RA=0x9012,args='then-live a0..a7 after initializer/tail'),ev(0x9012,'READ32',address='then-liveSP+12',destination='ra',condition='only if loop call returns; not established by the selected loop body'),ev(0x9014,'a0=0',condition='only after preceding continuation'),ev(0x9016,'SP=(then-liveSP+16) mod2^32'),ev(0x9018,'RET',target='freshly loaded liveRA')], 'normally_returning_loop_provider_proved':False,'local_loop_has_no_RET':True,'source_present_post_loop_suffix_is_not_a_normal_loop_exit':True},
        'initializer':{'entry':0x9250,'ordered_effects':[ev(0x9250,'SP=(liveSP-16) mod2^32'),ev(0x9252,'WRITE32',address='liveSP+12',value='liveRA')]+[ev(p,'DIRECT_CALL',target=t,link_RA=p+(4 if p not in(0x9268,0x926E)else 2),args='then-live a0..a7; no local argument assignment between calls')for p,t in INIT_CALLS]+[ev(0x9288,'READ32',address='then-liveSP+12',destination='ra',role='fresh, after14 normal calls'),ev(0x928A,'SP=(then-liveSP+16) mod2^32'),ev(0x928C,'DIRECT_TAIL',target=0x17BF6,link_written=False,return_RA='freshly loaded at9288',args='then-live a0..a7')], 'direct_callee_count':14,'numeric_return_values_tested_locally':False,'arguments_and_statuses_not_reset_between_calls':True,'tail_implementation_delegated':True},
        'loop':{'entry':0x8180,'prologue_order':[ev(0x8180,'SP=(liveSP-16) mod2^32'),ev(0x8182,'WRITE32',address='liveSP+8',value='old liveS0'),ev(0x8184,'S0=0xB000'),ev(0x8186,'WRITE32',address='liveSP+4',value='liveS1'),ev(0x8188,'WRITE32',address='liveSP+0',value='liveS2'),ev(0x818A,'WRITE32',address='liveSP+12',value='liveRA'),ev(0x818C,'S2=0x20000000'),ev(0x8190,'S1=0x40003000'),ev(0x8194,'S0=(S0-1366) mod2^32',nominal_value=0xAAAA)],'iteration_order':[ev(0x8198,'READ32',address='then-liveS2+0',destination='a5',role='fresh on EVERY iteration'),ev(0x819C,'INDIRECT_CALL',target='loaded a5, even if zero',link_RA=0x819E,args='then-live argument registers'),ev(0x819E,'DIRECT_CALL',target=0x17002,link_RA=0x81A2,args='then-live argument registers'),ev(0x81A2,'DIRECT_CALL',target=0x12C58,link_RA=0x81A6,args='then-live argument registers'),ev(0x81A6,'WRITE32',address='then-liveS1+0',value='then-liveS0',nominal_address_if_preserved=0x40003000,nominal_value_if_preserved=0xAAAA),ev(0x81A8,'UNCONDITIONAL_BACKEDGE',target=0x8198)],'pointer_is_not_cached':True,'local_null_pointer_guard':False,'local_restore_or_RET':False,'frame_is_not_unwound_on_observation_budget':True,'body_is_perpetual_if_all_operations_return_normally':True,'host_budget_is_not_an_original_HALT_instruction':True,'MMIO_hardware_role_proved':False,'S0_S1_S2_preservation_after_callbacks_proved':False},
        'dispatcher':{'entry':0x901A,'entry_a1':'full u32 input; not truncated before selection/callback','prologue':[ev(0x901A,'SP=(liveSP-16) mod2^32'),ev(0x901C,'WRITE32',address='liveSP+8',value='liveS0'),ev(0x901E,'WRITE32',address='liveSP+12',value='liveRA'),ev(0x9020,'WRITE32',address='liveSP+4',value='liveS1'),ev(0x9022,'S0=0'),ev(0x9024,'a4=15')],
            'selection':{'low_bit_indices':list(range(15)),'selected_index':'least index0..14 whose input a1 bit is1','raw_operations':[ev(0x9026,'a5=ASR32(a1,S0&31)'),ev(0x902A,'a5=a5&1'),ev(0x902C,'if a5==0 go increment',target=0x9070),ev(0x9070,'S0=(S0+1) mod2^32'),ev(0x9072,'if S0!=15 repeat scan',target=0x9026)],'no_low15_bit_path':[ev(0x9076,'a0=0'),ev(0x9078,'jump restore',target=0x9066)],'bits15_to31_do_not_select_a_record':True},
            'selected_record':{'PCREL_pair':[0x9034,0x9038],'base':base,'base_formula':'0x9034+0x20003000-556 modulo2^32; not a liveGP lookup','stride':12,'index_range':[0,14],'whole_original_C_object_or_physical_RAM_validity_proved':False,'ordered_effects':[ev(0x902E,'a5=12'),ev(0x9030,'a4=(S0*a5) mod2^32'),ev(0x9034,'compute PC-relative base',low_pc=0x9038,value=base),ev(0x903C,'S1=full32 live a1'),ev(0x903E,'a5=(base+record_offset) mod2^32'),ev(0x9040,'READ32',address='a5+4',destination='a3',role='callback pointer FIRST'),ev(0x9042,'if a3==0 skip mode/arg/clear/call',target=0x905A),ev(0x9044,'READ8_UNSIGNED',address='a5+0',destination='a4',role='mode byte BEFORE arg read'),ev(0x9048,'READ32',address='a5+8',destination='a0',role='argument AFTER sampled mode byte'),ev(0x904A,'a4=a4&255',role='mask sampled mode only after argument read'),ev(0x904E,'if a4!=0 call without clearing',target=0x9058),ev(0x9050,'WRITE32',address='a5+4',value=0),ev(0x9054,'WRITE32',address='a5+8',value=0),ev(0x9058,'INDIRECT_CALL',target='a3 loaded at9040',link_RA=0x905A,a0='argument loaded at9048',a1='full original u32 input still in a1 before this call',mode='a4 low8; no new mode read',target_and_argument_not_refetched_after_clears=True)],'correct_read_order':'pointer READ32, mode LBU, argument READ32, mode ANDI, optional clears, call','callback_zero_path_has_no_mode_arg_read_or_clear':True,'mode0_clears_only_for_nonzero_callback':True},
            'return_and_restore':[ev(0x905A,'a0=1'),ev(0x905C,'a0=(a0 << (then-liveS0&31)) mod2^32'),ev(0x9060,'a0=a0 XOR then-liveS1'),ev(0x9062,'a0=(a0<<16) mod2^32'),ev(0x9064,'a0=a0 logical-right16',role='low16 zero-extended'),ev(0x9066,'READ32',address='then-liveSP+12',destination='ra'),ev(0x9068,'READ32',address='then-liveSP+8',destination='s0'),ev(0x906A,'READ32',address='then-liveSP+4',destination='s1'),ev(0x906C,'SP=(then-liveSP+16) mod2^32'),ev(0x906E,'RET',target='freshly loaded liveRA')],
            'callback_numeric_return_value_ignored':True,'result_computed_before_S0_S1_restore':True,'removes_selected_bit_only_if_expected_S0_S1_preserved':True,'actual_post_callback_formula':'low16(liveS1 XOR (1u << (liveS0&31)))','original_C_ABI_callee_save_or_lifetime_proved':False,'no_low15_selection_returns0_even_if_higher_input_bits_set':True},
        'limits':{'source_only':True,'original_C_prototypes_or_ABI_recovered':False,'cross_version_dispatcher_ABI_assumed':False,'physical_RAM_MMIO_or_resident_validated':False,'callback_target_lifetime_or_return_proved':False,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False,'provider_generated':False,'ROOT_modified':False,'D_modified':False}}

def historical_check(w,retained):
    for rel,pin in retained['historical_input_hashes'].items():need(sha((w/rel).read_bytes())==pin,'historical file drift:'+rel)
    e=w/'experiments/tsl9-v4160-startup/evidence';groups=retained['groups'];m=json.loads((e/'main-plan.json').read_text());need(''.join(x['bytes']for x in groups['main'])==m['source_hex'],'main plan raw')
    core=json.loads((e/'core-flow-cfg.json').read_text());disp=json.loads((e/'conditional-dispatcher-cfg.json').read_text())
    for name,entry in [('loop',0x8180),('init',0x9250)]:
        old=next(g['instructions']for g in core['graphs']if g['entry']==entry);need([(x['addr'],x['size'],x['bytes'])for x in groups[name]]==[(x['va'],x['bytes'],x['raw_hex'])for x in old],'core prior row equality')
    need([(x['addr'],x['size'],x['bytes'])for x in groups['dispatcher']]==[(x['va'],x['bytes'],x['raw_hex'])for x in disp['instructions']],'dispatcher prior row equality')

def verify_seal(path):
    d=json.loads(path.read_text(encoding='utf-8'));need(d.get('passed')is True,'seal not passed')
    for m in d['members']:
        b=(path.parent/m['path']).read_bytes();need(len(b)==m['bytes']and sha(b)==m['sha256'],'seal member drift:'+m['path'])

def run(firmware,sr,w,historical=False):
    b=firmware.read_bytes();need(len(b)==76800 and sha(b)==FIRMWARE_SHA,'selected ID2966 hash/length');need(word(b,BASE+0x38)==BASE,'header analysis coordinate')
    rb=(sr/'retained-source.json').read_bytes();need(sha(rb)==RETAINED_SHA,'retained row hardpin');ret=json.loads(rb)
    if historical:historical_check(w,ret)
    base=gate(b);rows=[];spans=[]
    for name,(start,size)in RANGES.items():
        rs=ret['groups'][name];cur=start
        for r in rs:
            p=r['addr'];n=r['size'];need(p==cur and b[p-BASE:p-BASE+n].hex()==r['bytes'],'raw row/coverage:'+name);need(n==(4 if half(b,p)&3==3 else 2),'width');cur+=n;rows.append({**r,'body':name})
        need(cur==start+size,'range end:'+name);spans.append({'role':name,'start':start,'end_exclusive':cur,'file_offset':start-BASE,'bytes':size,'instructions':len(rs),'sha256':sha(b[start-BASE:cur-BASE])})
    need(len(rows)==80 and sum(r['size']for r in rows)==220,'complete220B/80 instruction bounds')
    starts={r['addr']for r in rows};graph={};edges=[];instructions=[];calls=[];terminals=[]
    for r in sorted(rows,key=lambda x:x['addr']):
        p=r['addr'];n=r['size'];v=int.from_bytes(bytes.fromhex(r['bytes']),'little');d=direct(p,n,v);succ=[];item={'pc':p,'file_offset':p-BASE,'width':n,'raw_hex':r['bytes'],'disassembly':r['opcode'],'body':r['body']}
        if d:
            kind,t=d;need(r.get('jump')==t,'decoded target mismatch');item['control']={'kind':kind,'target':t}
            if kind=='call':
                calls.append({'pc':p,'kind':'direct','target':t,'link_RA':p+n,'argument_registers':'then-live a0..a7'});succ=([t]if t in starts else[])+[p+n]
                if t not in starts:edges.append({'source':p,'target':t,'kind':'delegated-direct-call','inside_selected_source':False})
            elif kind=='branch':succ=[t,p+n]
            elif t in starts:succ=[t]
            else:terminals.append({'pc':p,'kind':'delegated-tail','target':t});edges.append({'source':p,'target':t,'kind':'delegated-tail','inside_selected_source':False})
        elif p in(0x819C,0x9058):
            reg=15 if p==0x819C else 13;item['control']={'kind':'indirect-call','rs1':reg,'link_RA':p+n};calls.append({'pc':p,'kind':'indirect','target_register':reg,'link_RA':p+n});succ=[p+n]
        elif p in(0x9018,0x906E):item['control']={'kind':'return','target':'liveRA'};terminals.append({'pc':p,'kind':'return','target':'liveRA'})
        else:
            need(not(n==4 and v&127 in(0x67,0x6F,0x63,0x73)),'unclassified32control');need(not(n==2 and v&3==2 and v>>13==4 and(v>>2)&31==0),'unclassified16indirect');succ=[p+n]
        for t in succ:
            need(t in starts,'uncovered internal successor');edge={'source':p,'target':t,'kind':'local','inside_selected_source':True}
            if d and d[0]=='call':edge['kind']='selected-direct-call-entry'if t==d[1]else('unproved-loop-return-only'if p==0x900E else'normal-return-to-link-required')
            elif p in(0x819C,0x9058):edge['kind']='normal-return-to-link-required'
            elif d and d[0]=='branch':edge['branch_outcome']='taken'if t==d[1]else'not-taken'
            edges.append(edge)
        graph[p]=succ;instructions.append(item)
    seen=set();todo=[0x9008,0x901A]
    while todo:
        p=todo.pop()
        if p in seen:continue
        seen.add(p);todo.extend(graph[p])
    need(seen==starts,'conditional sourceCFG not fully covered')
    mutants=[];cases=[('main_savedRA_offset',0x900A,1<<9),('main_init_target',0x900C,1<<3),('main_loop_target',0x900E,1<<21),('main_freshRA_offset',0x9012,1<<4),('main_return0',0x9014,1<<2),('init_savedRA_offset',0x9252,1<<9),('init_first_target',0x9254,1<<21),('init_freshRA_offset',0x9288,1<<4),('init_SP_restore',0x928A,1<<2),('init_tail_becomes_call',0x928C,1<<7),('loop_saveS0_offset',0x8182,1<<9),('loop_S0_high',0x8184,1<<2),('loop_saveS1_offset',0x8186,1<<9),('loop_saveS2_offset',0x8188,1<<9),('loop_saveRA_offset',0x818A,1<<9),('loop_S2_base',0x818C,1<<12),('loop_S1_base',0x8190,1<<12),('loop_AAAA_low',0x8194,1<<20),('loop_live_pointer_base',0x8198,1<<15),('loop_pointer_width',0x8198,1<<12),('loop_indirect_target',0x819C,1<<7),('loop_direct_target',0x819E,1<<21),('loop_write_value_register',0x81A6,1<<2),('loop_write_base_register',0x81A6,1<<7),('loop_backedge',0x81A8,1<<3),('dispatcher_save_order_RA_offset',0x901E,1<<9),('scan_limit15',0x9024,1<<2),('scan_uses_A1',0x9026,1<<15),('record_stride12',0x902E,1<<2),('registry_PC_low',0x9038,1<<20),('save_full_input_S1',0x903C,1<<2),('callback_pointer_field',0x9040,1<<6),('mode_LBU_field',0x9044,1<<20),('argument_field8',0x9048,1<<6),('mode_mask255',0x904A,1<<20),('mode_branch_direction',0x904E,1<<13),('clear_callback_offset',0x9050,1<<7),('clear_argument_offset',0x9054,1<<7),('callback_target_A3',0x9058,1<<7),('postcall_live_shift_S0',0x905C,1<<20),('postcall_live_XOR_S1',0x9060,1<<2),('low16_truncation',0x9062,1<<2),('dispatcher_freshRA_offset',0x9066,1<<4),('dispatcher_freshS0_offset',0x9068,1<<4),('dispatcher_scan_backedge',0x9072,1<<8)]
    for name,p,xor in cases:
        n=4 if half(b,p)&3==3 else 2;old=b[p-BASE:p-BASE+n];new=(int.from_bytes(old,'little')^xor).to_bytes(n,'little');mut=bytearray(b);mut[p-BASE:p-BASE+n]=new
        try:gate(mut)
        except ValueError as exc:mutants.append({'name':name,'pc':p,'original_raw':old.hex(),'mutant_raw':new.hex(),'rejected':True,'error':str(exc)})
        else:raise ValueError('raw mutation escaped:'+name)
    need(len([c for c in calls if c['kind']=='direct'])==18 and len([c for c in calls if c['kind']=='indirect'])==2,'callsite counts')
    # Pure bit/interval arithmetic from the observed finite scan, not target execution.
    bit_cases=[{'input':m,'selected_index':next((i for i in range(15)if(m>>i)&1),None)}for m in(0,0x8000,0x80000000,0x80008004,0xFFFF,0xFFFFFFFF)]
    for x in bit_cases:x['result_if_expected_S0_S1_preserved']=0 if x['selected_index']is None else(x['input']^(1<<x['selected_index']))&0xFFFF
    sm={'schema':'ID2966-runtime-loop-source-map-v1','passed':True,'firmware':{'relative_path':FIRMWARE_REL,'bytes':len(b),'sha256':FIRMWARE_SHA,'analysis_base':BASE,'header_file_offset_0x38_LE32':BASE,'physical_load_not_measured':True},'retained_source_sha256':RETAINED_SHA,'historical_input_hashes':ret['historical_input_hashes'],'fresh_vs_historical':ret['historical_equivalence'],'source_spans':spans,'instructions':instructions,'CFG':{'entry_roots':[0x9008,0x901A],'instructions':len(instructions),'bytes':220,'conditionally_covered_starts':len(seen),'uncovered_starts':sorted(starts-seen),'edges':edges,'calls':calls,'terminals':terminals,'main_900E_return_edge_is_not_established_by_loop_source':True,'loop_contains_no_RET_or_restore':True,'normal_return_edges_do_not_prove_callee_ABI':True,'external_callees_not_traversed':True},'synthetic_bit_geometry_cases':bit_cases,'raw_operand_mutations':mutants,'network':False,'target_execution':False,'ISA_emulation':False,'hardware':False}
    return{'source-map.json':enc(sm),'contract.json':enc(make_contract(base,spans))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--firmware',type=Path);p.add_argument('--source-root',type=Path,default=HERE);p.add_argument('--workspace',type=Path,default=WORKSPACE);p.add_argument('--verify-historical',action='store_true');g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args();w=a.workspace.resolve();sr=a.source_root.resolve();fw=a.firmware.resolve()if a.firmware else w/FIRMWARE_REL;out=run(fw,sr,w,a.verify_historical)
    if a.write:
        need(sr==HERE and not(HERE/'final-audit.json').exists(),'write restricted to own unsealed package')
        for n,b in out.items():
            q=HERE/n;need(not q.exists()or q.read_bytes()==b,'nonidentical output exists:'+n)
            if not q.exists():q.write_bytes(b)
    else:
        for n,b in out.items():need((sr/n).read_bytes()==b,'readonly byteexact mismatch:'+n)
        if(sr/'final-audit.json').exists():need(json.loads((sr/'final-audit.json').read_text()).get('sealed')is True,'not sealed');verify_seal(sr/'final-audit.json')
    print(json.dumps({'passed':True,'mode':'readonly-byteexact'if a.check else'create-only','bytes':220,'instructions':80,'raw_operand_mutation_rejections':45,'output_sha256':{n:sha(b)for n,b in out.items()},'target_execution':False,'network':False}))

if __name__=='__main__':main()
