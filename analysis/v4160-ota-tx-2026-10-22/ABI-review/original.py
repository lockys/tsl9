#!/usr/bin/env python3
"""Independent original TX ownership, direct-call link fields and ABI frontiers."""
import argparse,hashlib,json,runpy,struct,sys
from pathlib import Path
sys.dont_write_bytecode=True
ENTRY=0x8a56
END=0x8b6e
OWNER='.text.tsl9v4160.code_continuation_8a56'
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BODY='3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b'
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
HELPER='4d7e1b4ffa5101347970a662390c4cb8ff6455161e47d6e68f2144a27b8ca7e1'
EXPECTED_INCOMING={0x8368:(2,1,0x836a,'fd25'),0x841c:(2,1,0x841e,'2d2d'),0x9be0:(4,1,0x9be4,'efe07fe7'),0x135a8:(4,1,0x135ac,'ef50efca'),0x13b30:(4,1,0x13b34,'ef407ff2'),0x13b80:(4,1,0x13b84,'ef407fed'),0x13c2e:(4,1,0x13c32,'ef409fe2'),0x13eac:(4,0,None,'6f40bfba'),0x14738:(4,1,0x1473c,'ef40efb1')}
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def H(b):return hashlib.sha256(b).hexdigest()
def case(root,slug):return next(p for p in (root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug) if p.is_dir())
def helpers(root):
    parser=case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py';helper=case(root,'v4160-flash-image-integration-2026-10-22')/'ABI-review/review.py';need(sha(parser)==PARSER and sha(helper)==HELPER,'Immutable bounded ELF/direct-link helpers');return runpy.run_path(str(parser))['ELF'],runpy.run_path(str(helper))
def indirect(body,pc):
    raw=body[pc-ENTRY:pc-ENTRY+2];h=int.from_bytes(raw,'little');need(len(raw)==2 and h&0xf07f in(0x8002,0x9002) and h&0x0f80,'Actual compressed JR/JALR');link=bool(h&0x1000);return dict(PC=pc,raw_hex=raw.hex(),bytes=2,rd=1 if link else 0,rs1=(h>>7)&31,return_PC=pc+2 if link else None)
def body_contract(body):
    need(len(body)==280,'Exact original TX extent280B');calls=[indirect(body,pc) for pc in (0x8a8e,0x8ab4,0x8aca,0x8b50,0x8b6c)];need([(r['rd'],r['rs1'],r['return_PC']) for r in calls]==[(1,15,0x8a90),(1,15,0x8ab6),(0,1,None),(0,6,None),(0,1,None)],'Two gate calls linkRA;failure/earlyRET andsuccessJRT1 do not link')
    def word(pc):return int.from_bytes(body[pc-ENTRY:pc-ENTRY+4],'little')
    need(word(0x8a56)==0x40f00793,'A5=1039 before unsigned length guard');w=word(0x8a5a);imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);imm=imm-8192 if imm&4096 else imm;need(w&127==0x63 and (w>>12)&7==6 and (w>>15)&31==15 and (w>>20)&31==13 and 0x8a5a+imm==0x8b6c,'Unsigned A5<A3 guard; full32 length and exactearlyRETtarget')
    for pc in (0x8a86,0x8aaa):
        w=word(pc);need(w&127==3 and (w>>12)&7==2 and (w>>7)&31==15 and (w>>15)&31==15 and w>>20==0x13c,'Fresh gate pointer32 read at literalROM+13C')
    w=word(0x8b36);need(w&127==0x23 and (w>>12)&7==1 and (w>>15)&31==15 and (w>>20)&31==0 and ((w>>25)<<5|((w>>7)&31))==4,'Successdescriptor SHzero width16 atoffset4')
    w=word(0x8b4a);need(w&127==3 and (w>>12)&7==4 and (w>>7)&31==10 and (w>>15)&31==12 and w>>20==0,'Terminal LBU A0 fromliveA2, not pointertruncation')
    return dict(bytes=280,indirect_transfers=calls,frame_bytes=32,ordered_saves=[dict(PC=pc,GPR=reg,slot=slot) for pc,reg,slot in [(0x8a60,8,24),(0x8a62,9,20),(0x8a64,18,16),(0x8a66,19,12),(0x8a68,1,28)]],early_unsigned_guard=dict(PC=0x8a5a,condition='1039 < unsigned entryA3',target=0x8b6c,before_frame=True,A0='unchanged entrycontext',A5=1039),unknown_gate_ABI=dict(slot_address=0x4013c,first_args=dict(A0='entrycontext',A1='liveGP+0x80',A2='entrypayload',A3='entrylength'),second_args=dict(A0='liveS2',A1='liveGP+0x80',A2='livepost-firstgate residue',A3='livepost-firstgate residue'),local_success_test='A0==1 only',callee_SP_S_GP_preservation_proved=False),framed_failure=dict(PC=0x8abe,A0='path-dependent entrycontext or gate result; no commonstatus',A2='set1 after secondgate even if it fails',fresh_stack_restore=True),success_tail=dict(PC=0x8b50,rd=0,target_GPR=6,ROM_slot=0x40050,A0='LBU(liveGP+0x94+4*liveLane)',A1=1,A2='liveGP+0x94+4*liveLane',A3='numeric SRAM2000B18C',A5=0x40000,RA='freshly restored callerRA',SP='liveSP+32',provider_signature_proved=False),post_gate_length_guard_still_bounds_arbitrary_liveS0=False,full32_counter_guard='low16(A1)<liveS0; addressing uses fullA1',allocation_copy_free_calls_visible=False,resident_ROM_behavior_proved=False,target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)
def incoming_contract(helper,code,offset,base):
    row=helper['direct_jump'](code,offset,base);need(row['site'] in EXPECTED_INCOMING,'Known actual original incoming site');n,rd,link,raw=EXPECTED_INCOMING[row['site']];need((row['bytes'],row['rd'],row['target'],row['link'],row['raw_hex'])==(n,rd,ENTRY,link,raw),'Actual incoming width/rd/target/RA/raw contract');return row
def inspect(root,firmware,folder=None):
    need(sha(firmware)==FW,'Exact official original firmware');full=firmware.read_bytes();body=full[ENTRY-0x8000:END-0x8000];need(H(body)==BODY,'Actual originalTX280 bytes');ELF,helper=helpers(root);incoming=[incoming_contract(helper,full,pc-0x8000,0x8000) for pc in sorted(EXPECTED_INCOMING)];back=helper['direct_jump'](body,0x114,ENTRY);need((back['bytes'],back['rd'],back['target'],back['link'])==(2,0,0x8b0a,None),'Local RVC loop backedge is actual no-linkCJ')
    result=dict(schema='TSL9-TX-original-independent-ABI-v1',passed=True,firmware_sha256=FW,body_sha256=BODY,body=body_contract(body),incoming=incoming,local_backedge=back,computed_or_encoded_interior_references_absent_proved=False,actual_archived_ELF_read=False)
    if folder:
        e=ELF(folder/'source-integrated.o');linked=ELF(folder/'ADDRESS-WITNESS-ONLY.elf');owner=e.byname[OWNER];need((owner['type'],owner['flags'],owner['size'],owner['alignment'])==(1,6,280,2),'Actual original AX280 align2 owner');role=[helper['role'](e,s) for s in e.symbols if s['index']==owner['index']];public=next(r for r in role if r['name']=='__tsl9v4160_call_8a56');need(public==dict(name=public['name'],owner=OWNER,offset=0,bytes=280,info=18,other=0),'Original canonical GLOBALFUNC280 role');need(linked.data(linked.byname[OWNER])==body,'Actual linked body equals original')
        owned=[helper['relocation'](e,r) for r in e.relocations if r['owner']==OWNER];external=[r for r in e.relocations if r['symbol']['index']==owner['index'] and r['owner']!=OWNER];need(len(owned)==11 and len(external)==9,'Eleven owned andnine external recorded references');need(sorted(r['type'] for r in owned)==[16]*8+[23,24,45],'Eight branches, PCRELHI/LO, localCJ');seen=[]
        for r in external:
            need(r['symbol']['value']==0 and r['addend']==0,'Recorded external reference to original entry0 only');s=linked.byname[r['owner']];jump=incoming_contract(helper,linked.data(s),r['offset'],s['address']);jump.update(owner=r['owner'],RELA_type=r['type']);seen.append(jump)
        need({x['site'] for x in seen}==set(EXPECTED_INCOMING),'Allnine actual physicalincoming sites');private=[r for r in role if r['name'].startswith('.L')];need(len(private)==8 and sorted(r['offset'] for r in private)==[64,104,118,120,128,180,252,278],'Eight exact original private boundaries')
        result.update(actual_archived_ELF_read=True,actual_folder=folder.resolve().relative_to(root).as_posix(),partial_sha256=H(e.raw),linked_sha256=H(linked.raw),owner=owner,owner_symbol_roles=role,owned_RELA=owned,actual_external_incoming=sorted(seen,key=lambda r:r['site']))
    controls=[]
    for site,mask in [(0x8368,0x8000),(0x135a8,0x80),(0x13eac,0x80)]:
        offset=site-0x8000;mutant=bytearray(full);n=EXPECTED_INCOMING[site][0];word=int.from_bytes(mutant[offset:offset+n],'little')^mask;mutant[offset:offset+n]=word.to_bytes(n,'little')
        original_row=helper['direct_jump'](full,offset,0x8000);mutated_row=helper['direct_jump'](bytes(mutant),offset,0x8000);need(original_row['bytes']==mutated_row['bytes'] and original_row['target']==mutated_row['target'] and original_row['rd']!=mutated_row['rd'],'Control changes actuallinkbehavior while retainingwidth/target')
        try:incoming_contract(helper,bytes(mutant),offset,0x8000)
        except ValueError as error:controls.append(dict(site=site,kind='actual original incoming instruction bytes',same_width_target=True,original_link_contract=original_row,mutated_link_contract=mutated_row,rejected=True,reason=str(error)));continue
        raise ValueError('Incoming link mutant admitted')
    result['actual_incoming_link_controls']=controls;return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--folder',type=Path);p.add_argument('--report',type=Path);a=p.parse_args();r=inspect(a.project_root.resolve(),a.firmware.resolve(),a.folder.resolve() if a.folder else None)
    if a.report:need(not a.report.exists(),'Create-only source ABI report');a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps(dict(passed=True,bytes=280,incoming=9,actual_archived_ELF_read=r['actual_archived_ELF_read'],target_execution=False)))
if __name__=='__main__':main()
