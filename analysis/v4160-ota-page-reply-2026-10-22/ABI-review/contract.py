"""Bounded raw ABI obligations for original9B8E; no instruction execution or provider ABI invention."""
from pathlib import Path
import hashlib,json,struct
SHA=lambda b:hashlib.sha256(b).hexdigest()
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PROTOCOL_SHA='9a66b861219b9d0b2307f5968bd5e44081e40ccb48600ca397713485145d0564'


def need(v,why):
    if not v:raise ValueError(why)


def c_indirect(raw,pc):
    word=int.from_bytes(raw,'little');need(len(raw)==2 and word&0xf07f in (0x8002,0x9002),'actual compressed JR/JALR with zero rs2');reg=(word>>7)&31;need(reg!=0,'nonzero indirect source register');link=bool(word&0x1000)
    return dict(PC=pc,bytes=2,raw_hex=raw.hex(),source_GPR=reg,destination_GPR=1 if link else 0,return_address=pc+2 if link else None,target='live GPR with bit0 cleared')


def direct_jal(raw,pc):
    word=int.from_bytes(raw,'little');need(len(raw)==4 and word&127==0x6f,'actual four-byte JAL');rd=(word>>7)&31;imm=((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1);delta=imm-(1<<21) if imm&(1<<20) else imm
    return dict(PC=pc,bytes=4,raw_hex=raw.hex(),destination_GPR=rd,target=pc+delta,return_address=pc+4 if rd else None)


def source_contract(root,firmware=None):
    case=root/'apk-analysis/tsl9-v4160-ota-route-2026-10-21/protocol-review/review.json'
    if not case.is_file():case=root/'analysis/v4160-ota-route-2026-10-21/protocol-review/review.json'
    need(SHA(case.read_bytes())==PROTOCOL_SHA,'sealed original protocol/raw context');source=json.loads(case.read_bytes());window=next(x for x in source['raw_r2_contexts'] if x['start']==0x9b8e);need(window['end_exclusive']==0x9c0a and len(window['instructions'])==50,'original124B/50instruction window')
    path=firmware or root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin';full=path.read_bytes();need(SHA(full)==FW_SHA,'pinned original firmware source');body=full[0x9b8e-0x8000:0x9c0a-0x8000];need(SHA(body)==window['sha256'],'actual original body bytes')
    def at(pc,n):return body[pc-0x9b8e:pc-0x9b8e+n]
    calls=[c_indirect(at(pc,2),pc) for pc in (0x9bae,0x9bd4,0x9bf8,0x9c08)];calls.insert(2,direct_jal(at(0x9be0,4),0x9be0))
    need([(x['destination_GPR'],x.get('source_GPR'),x['return_address']) for x in calls]==[(1,15,0x9bb0),(1,15,0x9bd6),(1,None,0x9be4),(0,6,None),(0,1,None)],'allocator/copy linkRA, TX linkRA, freeJRT1 and nullRETRA');need(calls[2]['target']==0x8a56,'actual direct TX target')
    loads=[]
    for pc,rd,offset in [(0x9b96,15,0x70),(0x9bc2,15,0x4c),(0x9be8,6,0x68)]:
        word=int.from_bytes(at(pc,4),'little');need(word&127==3 and (word>>12)&7==2 and (word>>7)&31==rd and (word>>15)&31==18 and word>>20==offset,'fresh liveS2 ROM pointer load');loads.append(dict(PC=pc,destination_GPR=rd,base_GPR=18,offset=offset,nominal_address=0x40000+offset,fixed_address_unconditionally_proved=False))
    return dict(schema='TSL9-page-reply-original-ABI-obligations-v1',source_firmware_sha256=FW_SHA,source_context_sha256=PROTOCOL_SHA,body_sha256=SHA(body),entry=0x9b8e,bytes=124,instructions=50,calls=calls,live_pointer_loads=loads,frame_bytes=32,original_save_order=[dict(GPR=18,slot=16,PC=0x9b90),dict(GPR=9,slot=20,PC=0x9b9a),dict(GPR=19,slot=12,PC=0x9b9c),dict(GPR=20,slot=8,PC=0x9b9e),dict(GPR=1,slot=28,PC=0x9ba0),dict(GPR=8,slot=24,PC=0x9ba2)],input_index_GPR=12,input_index_width=32,header_store_low16_only=True,source_arithmetic_uses_live_full32_index=True,allocator_entry=dict(A0='1026',A1='entry command',A2='full entry index',A5='live allocator target',other_caller_saved='entry residues except local assignments'),copy_entry=dict(A0='live allocation+2',A1='((0x20004+liveS1)<<10) modulo2^32',A2='1024',A5='fresh live copy target',other_caller_saved='allocator-dependent residues'),free_tail=dict(A0_assignment_PC=0x9be4,A0='liveS0 before its fresh restore',fresh_S0_restore_PC=0x9be6,target_load_PC=0x9be8,target_GPR=6,remaining_restore_PCs=[0x9bec,0x9bee,0x9bf0,0x9bf2,0x9bf4],SP_restore_PC=0x9bf6,jump_PC=0x9bf8,new_RA_created=False,provider_returns_into_local_continuation=False,eventual_caller_return_and_GPRs='provider-defined'),null_path=dict(entry=0x9bfa,A0=0,other_caller_saved='allocator-defined, not normalized',fresh_restore_order=[1,8,9,18,19,20],SP_restore=32,terminal_PC=0x9c08,terminal='JR restoredRA'),resident_ABI_verified=False,ordinary_C_provider_SP_callee_saved_obligations='conditional only; no arbitrary liveSP/S-register clobber equivalence',old_frame_word_permutation_applies=False,target_execution=False,ISA_emulation=False,hardware=False,network=False)
