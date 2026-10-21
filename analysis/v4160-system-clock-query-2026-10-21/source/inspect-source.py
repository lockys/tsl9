"""Source-only ID2966 clock query/derived-output contract, with no target execution."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[2]
FW_REL='exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RETAINED_SHA='0aa4f2f2e0828453e5aa4f6aac3e3b2a7a95559820ef1173281dcad26f3901b0'
BASE=0x8000
RANGES={'query18834':(0x18834,0x188E2),'derive1973c':(0x1973C,0x19764),'conditional_reset_initializer_mapping':(0x186AA,0x186DE)}

def sha(b):return hashlib.sha256(b).hexdigest()
def enc(d):return(json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
def need(v,msg):
    if not v:raise ValueError(msg)
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def half(b,p):return int.from_bytes(b[p-BASE:p-BASE+2],'little')
def word(b,p):return int.from_bytes(b[p-BASE:p-BASE+4],'little')
def load(b,p):
    v=word(b,p);need(v&127==3,f'{p:x}: LOAD opcode');return((v>>7)&31,(v>>15)&31,sx(v>>20,12),(v>>12)&7)
def store(b,p):
    v=word(b,p);need(v&127==0x23,f'{p:x}: STORE opcode');return((v>>20)&31,(v>>15)&31,sx(((v>>25)<<5)|((v>>7)&31),12),(v>>12)&7)
def addi(b,p):
    v=word(b,p);need(v&0x707F==0x13,f'{p:x}: ADDI opcode');return((v>>7)&31,(v>>15)&31,sx(v>>20,12))
def c_mem(b,p):
    v=half(b,p);need(v&3==0 and v>>13==2,f'{p:x}: C.LW');return(8+((v>>2)&7),8+((v>>7)&7),(((v>>5)&1)<<6)|(((v>>10)&7)<<3)|(((v>>6)&1)<<2))
def c_addi(b,p):
    v=half(b,p);need(v&3==1 and v>>13==0,f'{p:x}: C.ADDI');return((v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6))
def c_li(b,p):
    v=half(b,p);need(v&3==1 and v>>13==2,f'{p:x}: C.LI');return((v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6))
def pair(b,hi,lo,rd,auipc=False):
    h=word(b,hi);need(h&127==(0x17 if auipc else 0x37)and(h>>7)&31==rd,f'{hi:x}: own HI')
    need(addi(b,lo)[:2]==(rd,rd),f'{lo:x}: own LOW');return((hi if auipc else 0)+(h&0xFFFFF000)+addi(b,lo)[2])&0xFFFFFFFF
def direct(p,n,v):
    if n==4 and v&127==0x63:
        im=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1);return('branch',(p+sx(im,13))&0xFFFFFFFF)
    if n==2 and v&3==1 and v>>13==5:
        im=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5);return('jump',(p+sx(im,12))&0xFFFFFFFF)
    if n==2 and v&3==1 and v>>13 in(6,7):
        im=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5);return('branch',(p+sx(im,9))&0xFFFFFFFF)
    return None
def branch(b,p,rs1,rs2,f3,target):
    v=word(b,p);need(v&0x707F==(f3<<12|0x63)and(v>>15)&31==rs1 and(v>>20)&31==rs2 and direct(p,4,v)==('branch',target),f'{p:x}: branch condition/register/target')
def r_op(b,p,rd,rs1,rs2,f3,f7):
    v=word(b,p);need(v&127==0x33 and(v>>7)&31==rd and(v>>15)&31==rs1 and(v>>20)&31==rs2 and(v>>12)&7==f3 and v>>25==f7,f'{p:x}: arithmetic opcode/operands')

def gate(b):
    need(word(b,0x18834)==0x40021737 and word(b,0x18854)==0x400217B7,'query MMIO base LUI')
    for p,x in{0x18838:(15,14,4),0x18858:(15,15,4),0x18882:(15,14,4),0x18884:(14,14,4),0x188B4:(14,13,4),0x188CE:(14,13,4),0x1886C:(15,15,0),0x19740:(15,15,0)}.items():need(c_mem(b,p)==x,f'{p:x}: fresh READ32 register/offset')
    need(c_li(b,0x1883A)==(13,4)and half(b,0x1883C)==0x8BB1,'select mask12/compare4')
    branch(b,0x1883E,15,13,0,0x18878);need(c_li(b,0x18842)==(13,8),'select compare8');branch(b,0x18844,15,13,0,0x18882)
    for hi,lo,rd,val in[(0x18848,0x1884C,15,8000000),(0x18878,0x1887C,15,32000000),(0x188A6,0x188AA,14,8000000),(0x188C0,0x188C4,14,16000000),(0x188D8,0x188DC,14,4000000),(0x19742,0x19746,14,8000000)]:need(pair(b,hi,lo,rd)==val,f'{hi:x}: literal base constant')
    for p in(0x18850,0x18872):need(store(b,p)==(15,3,108,2),f'{p:x}: provisional/final WRITE32 liveGP+108')
    need(addi(b,0x1885A)==(14,3,64),'table base liveGP+64')
    need(half(b,0x1885E)==0x8391 and half(b,0x18860)==0x8BBD and half(b,0x18862)==0x97BA,'fresh prescaler index shift/mask/address')
    need(load(b,0x18864)==(14,15,0,4),'table unsigned READ8')
    for p in(0x18868,0x1973C):need(addi(b,p)==(15,3,108),f'{p:x}: fresh clock address liveGP+108')
    r_op(b,0x1886E,15,15,14,5,0)
    for p in(0x18876,0x19762):need(half(b,p)==0x8082,f'{p:x}: RET liveRA')
    need(half(b,0x18886)==0x66C1 and half(b,0x18888)==0x83C9 and half(b,0x1888A)==0x8BBD and half(b,0x1888C)==0x8F75,'PLL field extraction/mask65536')
    need(c_addi(b,0x1888E)==(15,2)and c_li(b,0x18890)==(13,17),'multiplier field+2/compare17')
    branch(b,0x18892,15,13,1,0x18898);need(c_li(b,0x18896)==(15,18),'raw17 multiplier replacement18')
    for p,rs1,f3,t in[(0x18898,14,7,0x188B0),(0x188A4,14,6,0x188D8)]:
        v=half(b,p);need(v&3==1 and v>>13==f3 and 8+((v>>7)&7)==rs1 and direct(p,2,v)==('branch',t),f'{p:x}: compressed branch')
    need(word(b,0x1889A)==0x40024737 and load(b,0x1889E)==(14,14,-2048,2),'special READ32 address40023800, signed displacement')
    need(half(b,0x188A2)==0x8B41,'special bit4 mask16')
    need(word(b,0x188B0)==0x400216B7 and word(b,0x188B6)==0x00C00637 and half(b,0x188BA)==0x8F71,'external config base/maskC00000')
    branch(b,0x188BC,14,12,1,0x188CE)
    r_op(b,0x188C8,15,15,14,0,1)
    need(word(b,0x188D0)==0x00E71693,'SLLI14 low32 before SIGNED BGEZ')
    branch(b,0x188D4,13,0,5,0x188A6)
    for p,t in[(0x18880,0x18850),(0x188AE,0x188C8),(0x188CC,0x18850),(0x188E0,0x188C8)]:need(direct(p,2,half(b,p))==('jump',t),f'{p:x}: local join')
    r_op(b,0x1974A,15,15,14,5,1)
    need(word(b,0x1974E)==0x0FF7F793,'derived unsigned quotient AND255')
    need(store(b,0x19752)==(15,3,382,0),'derived WRITE8 liveGP+17E')
    need(addi(b,0x19756)==(14,0,1000),'derived multiplier1000')
    r_op(b,0x1975A,15,15,14,0,1)
    need(store(b,0x1975E)==(15,3,380,1),'derived WRITE16 liveGP+17C')
    need(pair(b,0x186AA,0x186AE,3,True)==0x20004000 and pair(b,0x186BA,0x186BE,10,True)==0x1AB60,'conditional reset GP/source mapping')
    need(addi(b,0x186C2)==(11,3,0)and addi(b,0x186C6)==(12,3,128),'conditional initializer dest/end')
    branch(b,0x186CA,11,12,7,0x186DE);branch(b,0x186DA,11,12,6,0x186CE)
    need(load(b,0x186CE)==(5,10,0,2)and store(b,0x186D2)==(5,11,0,2),'conditional reset word copy order')
    need(c_addi(b,0x186D6)==(10,4)and c_addi(b,0x186D8)==(11,4),'conditional reset word increments')
    return True

def ev(p,op,**kw):return{'pc':p,'pc_hex':f'0x{p:X}','operation':op,**kw}

def make_contract(spans,table):
    return{'schema':'ID2966-system-clock-and-derived-output-live-contract-v1','passed':True,'blocking_findings':[],'firmware':{'catalog_ID':2966,'version':'V4.1.60','sha256':FW_SHA,'bytes':76800,'analysis_base':BASE},'source_spans':spans,
        'API_requirements':{'memory_primitives':['READ32','READ8_UNSIGNED','WRITE32','WRITE8','WRITE16'],'context':'numeric u32 GPRs including liveGP/liveRA/A0; evaluate each source address/branch from current register state; no original C prototype claimed','unknown_or_nonreturn':'unknown reads/branch decisions, HALT and TRANSFER must not be silently replaced with zero, a default branch or a normal return','leaf_register_effects':'Both bodies contain no call and no SP operation, do not explicitly assign GP/RA/A0/A1, and RET uses then-live RA. Other A2/A3/A4/A5 fields are changed by source operations; old argument/status ABI is unproved.','no_observation_snapshot':'Repeated MMIO reads, GP-relative addresses and the output-word read are distinct live requests.'},
        'query18834':{'entry':0x18834,'end_exclusive':0x188E2,'bytes':174,'instructions':58,'no_calls':True,'no_DIV_instruction':True,'selection_order':[ev(0x18838,'READ32',address='liveA4+4 after LUI40021000',nominal_address=0x40021004,destination='a5',role='select config sample'),ev(0x1883C,'a5=a5&12'),ev(0x1883E,'if selected bits==4 go literal32000000',target=0x18878),ev(0x18844,'else if selected bits==8 go PLL path',target=0x18882),ev(0x18848,'else provisional=8000000',role='both selector0 and selector12 use this default')],
            'PLL_path':{'ordered_prefix':[ev(0x18882,'READ32',address='then-liveA4+4',nominal_address=0x40021004,destination='a5',role='fresh multiplier config'),ev(0x18884,'READ32',address='then-liveA4+4 before A4 overwritten',nominal_address=0x40021004,destination='a4',role='separate fresh source config'),ev(0x18888,'a5=logical_right(a5,18)'),ev(0x1888A,'a5=a5&15'),ev(0x1888C,'a4=a4&0x10000'),ev(0x1888E,'a5=(a5+2) mod2^32'),ev(0x18892,'if multiplier!=17 skip replacement'),ev(0x18896,'a5=18',condition='old value17'),ev(0x18898,'if sampled source flag!=0 external-config path else special-word path')],
                'multiplier_formula':'(((cfg_multiplier>>18)&15)+2), except17 becomes18','multiplier_values':list(range(2,17))+[18],
                'source_flag_zero_path':[ev(0x1889E,'READ32',address='A4 LUI40024000 -2048',nominal_address=0x40023800,destination='a4'),ev(0x188A2,'a4=a4&16'),ev(0x188A4,'if bit4==0 choose4000000 else8000000')],
                'source_flag_nonzero_path':[ev(0x188B4,'READ32',address='liveA3+4 after LUI40021000',nominal_address=0x40021004,destination='a4'),ev(0x188BA,'a4=a4&0x00C00000'),ev(0x188BC,'if masked value==0x00C00000 choose16000000; else another fresh read'),ev(0x188CE,'READ32',address='then-liveA3+4',nominal_address=0x40021004,destination='a4'),ev(0x188D0,'a3=(a4<<14) mod2^32'),ev(0x188D4,'SIGNED int32(a3)>=0 chooses8000000, negative chooses4000000',role='not unsigned comparison; low32 wrap before sign test, equivalent to testing sampled bit17 when normal register flow holds')],
                'join':ev(0x188C8,'a5=low32(a5*a4)',role='MUL, not DIV; base is4000000/8000000/16000000'), 'known_numeric_bound_only':'With the literal branches/fields and no external GPR mutation, largest product16000000*18=288000000 fits u32; retain actual low32 MUL semantics.'},
            'common_live_suffix':[ev(0x18850,'WRITE32',address='then-liveGP+108 mod2^32',value='provisional a5',role='first output store occurs before prescaler MMIO/table/word reads'),ev(0x18858,'READ32',address='a5+4 after fresh LUI40021000',nominal_address=0x40021004,destination='a5',role='fresh prescaler config'),ev(0x1885A,'a4=(then-liveGP+64) mod2^32'),ev(0x1885E,'a5=logical_right(a5,4)'),ev(0x18860,'a5=a5&15'),ev(0x18862,'a5=(table_base+a5) mod2^32'),ev(0x18864,'READ8_UNSIGNED',address='computed table address',destination='a4',role='live table byte; zero-extend8, not an embedded constant'),ev(0x18868,'a5=(then-liveGP+108) mod2^32'),ev(0x1886C,'READ32',address='a5 from18868',destination='a5',role='fresh scalar read, not cached provisional value'),ev(0x1886E,'a5=logical_right(a5,a4&31)',role='RV32 SRL uses low5 shift bits; not arithmetic-right or unmasked C shift'),ev(0x18872,'WRITE32',address='then-liveGP+108 mod2^32',value='shifted fresh scalar'),ev(0x18876,'RET',target='then-liveRA',a0='not assigned by this body')],
            'scalar_name_scope':'GP+108 word is the clock scalar described by the task as SystemCoreClock; original symbol/C-object identity and physical frequency units are not proved.',
            'GP_address_formation':'18850 provisional store, 1885A table base, 18868 scalar address and18872 final store each use GP then current at that point. Do not pin one GP for the whole function.',
            'table_index_range':[0,15],'table_shift_value_range_from_live_READ8':[0,255],'effective_shift_range':[0,31],
            'memory_request_bounds_under_normal_fixed_control':{'selector0_or4_or12':6,'PLL_source_zero':9,'PLL_source_nonzero_mask_equal':9,'PLL_source_nonzero_mask_not_equal':10,'includes_table_scalar_reads_and_two_writes':True},'hardware_clock_source_chip_or_SDK_identity_proved':False},
        'derive1973c':{'entry':0x1973C,'end_exclusive':0x19764,'bytes':40,'instructions':11,'ordered_effects':[ev(0x1973C,'a5=(then-liveGP+108) mod2^32'),ev(0x19740,'READ32',address='a5 from1973C',destination='a5',role='fresh clock scalar after unrelated9A42 may have changed GP/global'),ev(0x19742,'a4=8000000 via literal LUI/ADDI',low_pc=0x19746),ev(0x1974A,'a5=DIVU32(a5,8000000)',role='unsigned, not signed; divisor is nonzero literal'),ev(0x1974E,'a5=a5&255'),ev(0x19752,'WRITE8',address='then-liveGP+382 mod2^32',value='low8 a5'),ev(0x19756,'a4=1000'),ev(0x1975A,'a5=low32(a5*a4)',role='uses held masked quotient, does not reload the byte written at19752'),ev(0x1975E,'WRITE16',address='then-liveGP+380 mod2^32',value='low16 a5'),ev(0x19762,'RET',target='then-liveRA',a0='not assigned by body')],
            'formula_if_no_unaccounted_GPR_change':{'q8':'(uint32(fresh_clock)/8000000)&255','byte':'q8','halfword':'(q8*1000)&65535'},'quotient_not_signed':True,'GP_may_differ_between_read_byte_store_halfword_store':True,'tick_frequency_MHz_or_other_output_units_proved':False},
        'caller_boundary':{'init_call18834':{'pc':0x9254,'return_link':0x9258},'intervening_unknown_provider':{'pc':0x9258,'target':0x9A42,'may_change_GP_global_or_context':True},'init_call1973c':{'pc':0x925C,'return_link':0x9260},'do_not_feed_cached_query_value_into_derived_call':True,'source_caller_order_previously_verified_not_expanded_here':True},
        'conditional_initializer_table':table,
        'limits':{'source_only':True,'original_C_ABI_or_prototypes_recovered':False,'physical_RAM_MMIO_clock_or_chip_identity_validated':False,'live_prescaler_table_observed':False,'implicit_GP_stability_assumed':False,'provider_generated':False,'ROOT_modified':False,'D_modified':False,'network':False,'target_execution':False,'ISA_emulation':False,'hardware':False}}

def historical_check(w,r):
    for rel,pin in r['historical_input_hashes'].items():need(sha((w/rel).read_bytes())==pin,'historical file drift:'+rel)
    p=w/'apk-analysis/tsl9-v4160-core-flow-2026-10-20/initialization-review'
    for name,group in[('18834','query18834'),('1973c','derive1973c')]:
        old=json.loads((p/f'entry-{name}.json').read_text(encoding='utf-8'))['instructions'];need([(x['addr'],x['size'],x['bytes'])for x in r['groups'][group]]==[(x['VA'],x['size'],x['bytes'])for x in old],'historical raw equality')
def verify_seal(path):
    d=json.loads(path.read_text(encoding='utf-8'));need(d.get('passed')is True,'seal not passed')
    for m in d['members']:
        b=(path.parent/m['path']).read_bytes();need(len(b)==m['bytes']and sha(b)==m['sha256'],'seal member drift:'+m['path'])

def run(firmware,sr,w,historical=False):
    b=firmware.read_bytes();need(len(b)==76800 and sha(b)==FW_SHA,'ID2966 firmware size/hash')
    rb=(sr/'retained-source.json').read_bytes();need(sha(rb)==RETAINED_SHA,'retained source hardpin');r=json.loads(rb)
    if historical:historical_check(w,r)
    gate(b);spans=[];mainrows=[];aux=[]
    for name,(start,end)in RANGES.items():
        cur=start;rs=r['groups'][name]
        for x in rs:
            p=x['addr'];n=x['size'];need(p==cur and b[p-BASE:p-BASE+n].hex()==x['bytes'],'raw row/coverage:'+name);need(n==(4 if half(b,p)&3==3 else 2),'width');cur+=n
            (aux if name.startswith('conditional')else mainrows).append({**x,'body':name})
        need(cur==end,'exact range end');spans.append({'role':name,'start':start,'end_exclusive':end,'file_offset':start-BASE,'bytes':end-start,'instructions':len(rs),'sha256':sha(b[start-BASE:end-BASE])})
    need(len(mainrows)==69 and sum(x['size']for x in mainrows)==214,'complete214B/69 bound')
    table=dict(r['conditional_initializer']);init=b[0x1AB60-BASE:0x1ABE0-BASE];tb=b[0x1ABA0-BASE:0x1ABB0-BASE];need(sha(init)==table['sha256']and tb.hex()==table['table_hex']and sha(tb)==table['table_sha256'],'conditional initializer/table source hash')
    table.update({'table_numeric_bytes':list(tb),'mapping_condition':'Original reset128B copy from1AB60 toGP20004000 completes normally and table bytes remain unchanged until query reads. Resident/IRQ/9A42 or other writers may invalidate this; no live RAM capture.','function_still_must_READ8_live_table':True,'whole_original_C_array_identity_proved':False})
    starts={x['addr']for x in mainrows};graph={};edges=[];inst=[];terms=[]
    for x in sorted(mainrows,key=lambda z:z['addr']):
        p=x['addr'];n=x['size'];v=int.from_bytes(bytes.fromhex(x['bytes']),'little');d=direct(p,n,v);succ=[];ir={'pc':p,'file_offset':p-BASE,'width':n,'raw_hex':x['bytes'],'disassembly':x['opcode'],'body':x['body']}
        if d:
            need(x.get('jump')==d[1],'direct decoded target');ir['control']={'kind':d[0],'target':d[1]};succ=[d[1],p+n]if d[0]=='branch'else[d[1]]
            if d[0]=='branch'and n==4:ir['control'].update({'rs1':(v>>15)&31,'rs2':(v>>20)&31,'funct3':(v>>12)&7})
        elif p in(0x18876,0x19762):ir['control']={'kind':'return','target':'liveRA'};terms.append(p)
        else:need(not(n==4 and v&127 in(0x67,0x6F,0x63,0x73)),'unclassified control');succ=[p+n]
        for t in succ:
            need(t in starts,'uncovered successor/outside frontier');e={'source':p,'target':t}
            if d and d[0]=='branch':e['branch_outcome']='taken'if t==d[1]else'not-taken'
            edges.append(e)
        graph[p]=succ;inst.append(ir)
    seen=set();todo=[0x18834,0x1973C]
    while todo:
        p=todo.pop()
        if p in seen:continue
        seen.add(p);todo.extend(graph[p])
    need(seen==starts,'fullCFG node coverage')
    mutations=[];cases=[('MMIO_initial_base',0x18834,1<<12),('MMIO_first_offset',0x18838,1<<6),('selector_mask12',0x1883C,1<<2),('first_selector_BEQ',0x1883E,1<<12),('second_selector_value8',0x18842,1<<2),('default8000000',0x1884C,1<<20),('provisional_store_GPoffset',0x18850,1<<7),('prescaler_fresh_READ32',0x18858,1<<6),('table_GPoffset64',0x1885A,1<<20),('prescaler_shift4',0x1885E,1<<2),('prescaler_mask15',0x18860,1<<2),('table_unsigned_LBU',0x18864,4<<12),('scalar_fresh_GPoffset',0x18868,1<<20),('scalar_fresh_READ32',0x1886C,1<<2),('final_SRL_to_SRA',0x1886E,1<<30),('final_store_width',0x18872,1<<12),('literal32000000',0x1887C,1<<20),('PLL_first_read_destination',0x18882,1<<2),('PLL_second_read_base',0x18884,1<<7),('PLL_multiplier_shift18',0x18888,1<<2),('PLL_multiplier_mask15',0x1888A,1<<2),('PLL_multiplier_add2',0x1888E,1<<2),('PLL_replace_compare17',0x18890,1<<2),('PLL_replace18',0x18896,1<<2),('PLL_source_branch',0x18898,1<<13),('special_signed_displacement',0x1889E,1<<31),('special_bit4_mask',0x188A2,1<<2),('special_branch_direction',0x188A4,1<<13),('external_predivide_mask',0x188B6,1<<12),('external_mask_compare',0x188BC,1<<12),('literal16000000',0x188C4,1<<20),('PLL_MUL_operation',0x188C8,1<<12),('external_fresh_read_base',0x188CE,1<<7),('SLLI14_wrap_amount',0x188D0,1<<20),('BGEZ_signed_to_unsigned',0x188D4,2<<12),('literal4000000',0x188DC,1<<20),('derived_fresh_GPoffset',0x1973C,1<<20),('derived_fresh_READ32',0x19740,1<<2),('derived_DIVU_to_DIV',0x1974A,1<<12),('derived_AND255',0x1974E,1<<20),('derived_SB_width',0x19752,1<<12),('derived_SB_offset',0x19752,1<<7),('derived_multiplier1000',0x19756,1<<20),('derived_MUL_operation',0x1975A,1<<12),('derived_SH_width',0x1975E,1<<12),('derived_SH_offset',0x1975E,1<<7),('reset_table_GP_mapping',0x186AE,1<<20),('reset_initializer_source',0x186BE,1<<20),('reset_initializer_extent',0x186C6,1<<20),('RET_liveRA_register',0x18876,1<<7)]
    for name,p,xor in cases:
        n=4 if half(b,p)&3==3 else 2;old=b[p-BASE:p-BASE+n];new=(int.from_bytes(old,'little')^xor).to_bytes(n,'little');mut=bytearray(b);mut[p-BASE:p-BASE+n]=new
        try:gate(mut)
        except ValueError as exc:mutations.append({'name':name,'pc':p,'original_raw':old.hex(),'mutant_raw':new.hex(),'rejected':True,'error':str(exc)})
        else:raise ValueError('raw mutation escaped:'+name)
    numeric=[]
    for clock in(0,7999999,8000000,2040000000,2048000000,0x80000000,0xFFFFFFFF):
        q=(clock//8000000)&255;numeric.append({'u32_clock':clock,'DIVU_quotient':clock//8000000,'q8':q,'WRITE8':q,'WRITE16':(q*1000)&65535})
    sm={'schema':'ID2966-system-clock-and-derived-output-source-map-v1','passed':True,'firmware':{'relative_path':FW_REL,'bytes':len(b),'sha256':FW_SHA,'analysis_base':BASE},'retained_source_sha256':RETAINED_SHA,'historical_input_hashes':r['historical_input_hashes'],'fresh_historical_equality':r['historical_row_equality'],'source_spans':spans,'instructions':inst,'auxiliary_reset_rows':aux,'CFG':{'entry_roots':[0x18834,0x1973C],'target_bytes':214,'target_instructions':69,'conditionally_reached_starts':len(seen),'uncovered_starts':sorted(starts-seen),'edges':edges,'return_sites':terms,'external_calls':[],'unresolved_control_frontier':[],'endpoints_derived_from_actual_reachable_RET_and_jumps_not_next_symbol':True,'aux_reset_is_mapping_context_not_complete_reset_CFG':True},'conditional_initializer_table':table,'arithmetic_examples_not_target_execution':numeric,'raw_operand_mutations':mutations,'chip_or_SDK_identity_assumed':False,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False}
    return{'source-map.json':enc(sm),'contract.json':enc(make_contract(spans,table))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--firmware',type=Path);p.add_argument('--source-root',type=Path,default=HERE);p.add_argument('--workspace',type=Path,default=WORKSPACE);p.add_argument('--verify-historical',action='store_true');g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args();w=a.workspace.resolve();sr=a.source_root.resolve();fw=a.firmware.resolve()if a.firmware else w/FW_REL;out=run(fw,sr,w,a.verify_historical)
    if a.write:
        need(sr==HERE and not(HERE/'final-audit.json').exists(),'write restricted to own unsealed source scope')
        for n,b in out.items():
            q=HERE/n;need(not q.exists()or q.read_bytes()==b,'nonidentical output:'+n)
            if not q.exists():q.write_bytes(b)
    else:
        for n,b in out.items():need((sr/n).read_bytes()==b,'readonly byteexact mismatch:'+n)
        if(sr/'final-audit.json').exists():need(json.loads((sr/'final-audit.json').read_text(encoding='utf-8')).get('sealed')is True,'not sealed');verify_seal(sr/'final-audit.json')
    report=json.loads(out['source-map.json']);print(json.dumps({'passed':True,'mode':'readonly-byteexact'if a.check else'create-only','target_bytes':214,'target_instructions':69,'raw_operand_mutation_rejections':len(report['raw_operand_mutations']),'output_sha256':{n:sha(b)for n,b in out.items()},'target_execution':False,'network':False}))

if __name__=='__main__':main()
