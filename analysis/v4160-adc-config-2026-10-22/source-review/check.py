"""Read-only static source contracts for original ADC cluster and callback closure."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FW = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PRIOR = 'e00c429d0db7e336243cfeeef830b1d91d559cf325cc433efa886dab737cadb9'
REFERENCE = {'rv_i-excerpt.txt':'a9307dfd76d8be41b708005c4160f72dba043cf560c335a67cb279dcab3dac11','rv_m-excerpt.txt':'55d91b0f584c058dd37c23c2b4011b227e9df6c4553c3e44bd347e056f8e1eb4','arg_lut-excerpt.txt':'8aaf78654b294f372bfce95dac25cba7eac83722413223eb94b7f80b32aec695'}
RANGES = {
 '1892e':(0x1892e,0x18986,37,'2f5e265070408a8fcbb4172fb5a1a4574baecd33ffc971eaafb5fc02d678653e'),
 '18986':(0x18986,0x18996,7,'1b0a6df26eca1dbb567293f57aaef784f3ece2541b357c34a7b9b0b73db968ac'),
 '18996':(0x18996,0x189ae,10,'109d29fa3c462fd901491a44a3194fb0c75304697c274141c30a71adf332c200'),
 '189ae':(0x189ae,0x18a66,64,'4ed751edae4e2951378a0bd2cc45f177132b3eddac354508e2a4d226cdc38172'),
 '18a66':(0x18a66,0x18a6e,4,'3742627de5a8d8a288a2a2a446c3a88b6056a8892352d99777783ea3467b5504'),
 '18a6e':(0x18a6e,0x18a8e,12,'16b62275fb19c8620b88718782fbb625e7cdfed61651f7c100323911aea2d177'),
 '18a8e':(0x18a8e,0x18a98,4,'54df366a01082d8608026cdcc1facff8db6e5c1447bb3b66237bd2ad55888349'),
 '18a98':(0x18a98,0x18ab0,10,'902658d8747cb4cefe949b5936b88f01ddf2327d1f4d67e8e48ab7cf77b86ff9'),
}
def read(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,s):
    if not v: raise ValueError(s)
def load(n,p):
    spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def case(root,n): return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def close(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact previous source seal')
    for n,h in read(folder/'seal.json')['members'].items(): need(sha(folder/n)==(h if isinstance(h,str) else h['sha256']),'Sealed member '+n)
def context(root):
    folder=case(root,'v4160-register-contract-2026-10-22')/'adc-review';close(folder,PRIOR)
    prior=load('adc_config_previous_contract',folder/'check.py');previous,C,base,E,old=prior.context(root)
    ref=HERE.parent/'instruction-reference'
    for n,h in REFERENCE.items(): need(sha(ref/n)==h,'Exact official encoding excerpt '+n)
    ext=load('adc_config_standard_fields',HERE/'raw.py')
    return prior,previous,C,lambda raw,pc:ext.decode(raw,pc,base),E,old
def exact(idx,pc,**fields):
    need(all(idx[pc][k]==v for k,v in fields.items()),'Source operand '+hex(pc)+' '+str(fields))
def cfg(rows,start):
    idx={x['PC']:x for x in rows};seen=set();active=set();exits=[]
    def visit(pc):
        need(pc in idx,'No branch outside actual bounded source')
        need(pc not in active,'No encoded leaf cycle')
        if pc in seen:return
        seen.add(pc);active.add(pc);x=idx[pc];op=x['op']
        if op=='jalr':
            need((x['rd'],x['rs1'],x['immediate'])==(0,1,0),'Only normal RA return');exits.append(pc);edges=[]
        elif op=='jal':need(x['rd']==0,'No hidden linked call');edges=[x['target']]
        elif op in ('beq','bne','bltu','bgeu'):edges=[x['target'],pc+x['bytes']]
        else:edges=[pc+x['bytes']]
        for edge in edges:visit(edge)
        active.remove(pc)
    visit(start);need(seen==set(idx),'Every retained row belongs to reachable entry CFG')
    return sorted(exits)
def gate(groups):
    allrows=[x for g in groups.values() for x in g];idx={x['PC']:x for x in allrows}
    protected=(1,2,3,4,8,9,*range(18,28))
    need(not any(x['rd'] in protected for x in allrows),'All cluster leaves have no RA/SP/S/GP/TP writes')
    exits={k:cfg(v,RANGES[k][0]) for k,v in groups.items()}
    access=[(x['PC'],x['op'],x['rs1'],x['immediate'],x['memory_width']) for x in groups['1892e'] if x['memory_width'] is not None]
    expected=[(0x1892e,'lw',10,4,32),(0x18938,'lw',11,24,32),(0x1893c,'lw',11,0,32),(0x18940,'lw',11,28,32),(0x18944,'lw',11,4,32),(0x1894c,'sw',10,4,32),(0x1894e,'lw',10,8,32),(0x18958,'lw',11,12,32),(0x1895c,'lw',11,16,32),(0x18960,'lw',11,8,32),(0x18968,'sw',10,8,32),(0x1896a,'lw',10,44,32),(0x18974,'lbu',11,20,8),(0x18982,'sw',10,44,32)]
    need(access==expected,'Exact14-effect source ordering and widths')
    for pc,rd,imm in [(0x18930,14,0xe0f10000),(0x18950,14,0xfff1f000),(0x1896c,14,0xff100000)]:exact(idx,pc,op='lui',rd=rd,immediate=imm)
    for pc,rd,imm in [(0x18934,14,-257),(0x18954,14,2045),(0x18970,14,-1),(0x18978,15,-1)]:exact(idx,pc,op='addi',rd=rd,rs1=rd,immediate=imm)
    for pc,rd,n in [(0x18946,13,8),(0x18962,13,1),(0x1897e,15,20)]:exact(idx,pc,op='slli',rd=rd,rs1=rd,immediate=n)
    exact(idx,0x1897a,op='andi',rd=15,rs1=15,immediate=255)
    for pc,rd,rs1,rs2 in [(0x1893a,14,14,15),(0x1895a,14,14,15),(0x18972,14,14,15)]:exact(idx,pc,op='and',rd=rd,rs1=rs1,rs2=rs2)
    for pc,rs2 in [(0x1893e,13),(0x18942,13),(0x18948,13),(0x1894a,14),(0x1895e,13),(0x18964,13),(0x18966,14),(0x18980,14)]:exact(idx,pc,op='or',rd=15,rs1=15,rs2=rs2)
    exact(idx,0x1898a,op='ori',rd=15,rs1=15,immediate=1);exact(idx,0x18992,op='andi',rd=15,rs1=15,immediate=-2)
    exact(idx,0x1899a,op='lui',rd=14,immediate=0x500000);exact(idx,0x189a4,op='lui',rd=14,immediate=0xffb00000);exact(idx,0x189a8,op='addi',rd=14,rs1=14,immediate=-1)
    exact(idx,0x189ae,op='addi',rd=15,rs1=0,immediate=9);exact(idx,0x189b0,op='bgeu',rs1=15,rs2=11,target=0x189fe)
    exact(idx,0x189b4,op='addi',rd=15,rs1=0,immediate=3);exact(idx,0x189b6,op='addi',rd=14,rs1=11,immediate=-10);exact(idx,0x189ba,op='mul',rd=14,rs1=14,rs2=15)
    exact(idx,0x189be,op='lw',rd=16,rs1=10,immediate=12,memory_width=32)
    exact(idx,0x189c2,op='addi',rd=15,rs1=0,immediate=7);exact(idx,0x189c4,op='sll',rd=15,rs1=15,rs2=14);exact(idx,0x189c8,op='xori',rd=15,rs1=15,immediate=-1)
    exact(idx,0x189cc,op='and',rd=15,rs1=15,rs2=16);exact(idx,0x189d0,op='sll',rd=13,rs1=13,rs2=14);exact(idx,0x189d4,op='or',rd=13,rs1=13,rs2=15);exact(idx,0x189d6,op='sw',rs1=10,rs2=13,immediate=12)
    exact(idx,0x189d8,op='addi',rd=15,rs1=0,immediate=6);exact(idx,0x189da,op='bltu',rs1=15,rs2=12,target=0x18a20)
    exact(idx,0x189de,op='addi',rd=15,rs1=0,immediate=5);exact(idx,0x189e0,op='addi',rd=12,rs1=12,immediate=-1);exact(idx,0x189e2,op='mul',rd=12,rs1=12,rs2=15)
    exact(idx,0x189e6,op='lw',rd=14,rs1=10,immediate=52);exact(idx,0x189e8,op='addi',rd=15,rs1=0,immediate=31);exact(idx,0x189ea,op='sll',rd=15,rs1=15,rs2=12)
    exact(idx,0x189ee,op='xori',rd=15,rs1=15,immediate=-1);exact(idx,0x189f2,op='and',rd=15,rs1=15,rs2=14);exact(idx,0x189f4,op='sll',rd=12,rs1=11,rs2=12);exact(idx,0x189f8,op='or',rd=12,rs1=12,rs2=15);exact(idx,0x189fa,op='sw',rs1=10,rs2=12,immediate=52)
    exact(idx,0x18a66,op='lw',rd=10,rs1=10,immediate=76,memory_width=32);exact(idx,0x18a68,op='slli',rd=10,rs1=10,immediate=16);exact(idx,0x18a6a,op='srli',rd=10,rs1=10,immediate=16)
    exact(idx,0x18a6e,op='lui',rd=15,immediate=0x40012000);exact(idx,0x18a72,op='addi',rd=15,rs1=15,immediate=1024);exact(idx,0x18a7a,op='lui',rd=13,immediate=0x800000);exact(idx,0x18a84,op='lui',rd=13,immediate=0xff800000)
    exact(idx,0x18a8e,op='lw',rd=10,rs1=10,immediate=0);exact(idx,0x18a90,op='and',rd=10,rs1=10,rs2=11);exact(idx,0x18a92,op='sltu',rd=10,rs1=0,rs2=10)
    exact(idx,0x18a9c,op='lui',rd=14,immediate=0x4000000);exact(idx,0x18aa6,op='lui',rd=14,immediate=0xfc000000)
    need([x['PC'] for x in allrows if x['rd']==16]==[0x189be,0x18a04],'Only A6 writers are channel-path fresh reads')
    return dict(source_bytes=386,source_rows=148,range_count=8,all_leaf_CFGs_acyclic=True,leaf_return_PCs=exits,
        no_leaf_RA_SP_S_GP_TP_writes=True,leaf_external_calls=0,config_source_accesses=14,
        config_masks=[0xe0f0feff,0xfff1f7fd,0xff0fffff],config_byte20_minus1_mask=255,config_byte20_shift=20,
        config_word_shifts_unmasked=True,unreviewed_direct_callback_targets=[],
        callback_A6_preserved=False,callback_A7_own_writes=False,callback_poll_timeout_encoded=False,
        callback_normal_return_unconditional=False,whole_MMIO_state_restored=False)
def caller_contract(caller):
    idx={x['PC']:x for x in caller}
    exact(idx,0x1987e,op='lui',rd=14,immediate=0xe0000);exact(idx,0x19882,op='sw',rs1=2,rs2=14,immediate=44)
    exact(idx,0x19884,op='addi',rd=11,rs1=2,immediate=32);exact(idx,0x19886,op='addi',rd=14,rs1=0,immediate=1);exact(idx,0x19888,op='mv',rd=10,rs1=9)
    exact(idx,0x1988a,op='sb',rs1=2,rs2=14,immediate=52)
    for pc,offset in [(0x1988e,32),(0x19890,36),(0x19892,40),(0x19894,48)]:exact(idx,pc,op='sw',rs1=2,rs2=0,immediate=offset)
    exact(idx,0x19896,op='jal',rd=1,target=0x1892e)
    for pc,reg,value in [(0x198b0,13,7),(0x198b2,12,1),(0x198b4,11,16),(0x198c8,11,2)]:exact(idx,pc,op='addi',rd=reg,rs1=0,immediate=value)
    exact(idx,0x198d6,op='beq',rs1=10,rs2=0,target=0x198c6)
    return dict(A0=0x40012400,A1='live callback SP+32',zeroed_config_bytes=32,
        config_words={'0':0,'4':0,'8':0,'12':0xe0000,'16':0,'24':0,'28':0},config_byte20=1,
        config_values_conditional_on_old_8520_zero_path=True,channel=16,sequence=1,sample=7,
        channel_write_offset=12,channel_shift=18,sequence_write_offset=52,sequence_shift=0,
        channel_RMW_mask=7<<18,sequence_RMW_mask=31,sequence_RMW_value=16,
        returned_A6_source_PC=0x189be,returned_A6='fresh READ32(0x4001240C) before channel write',
        callback_result='low16 of fresh READ32(0x4001244C)',poll_mask=2)
def post_config_liveness(root,groups,caller):
    before_A2_write=[x for x in caller if 0x1989a<=x['PC']<0x198b2]
    intermediate=before_A2_write+[x for k in ('18986','18a98','18a6e') for x in groups[k]]
    need(not any(r in (x['rs1'],x['rs2']) for r in (12,16,17) for x in intermediate),'No post-config read of A2/A6/A7 before bounded overwrites')
    exact({x['PC']:x for x in caller},0x198b2,op='addi',rd=12,rs1=0,immediate=1)
    need(not any(16 in (x['rs1'],x['rs2']) for x in groups['189ae'] if 0x189ae<=x['PC']<0x189be),'Actual channel16 path writes A6 before first read')
    before=read(case(root,'v4160-resident-native-2026-10-22')/'callback-review/ledger.json')['groups']
    dep=read(case(root,'v4160-register-contract-2026-10-22')/'adc-review/ledger.json')['groups']
    retained=[x for g in (*before.values(),*dep.values(),*groups.values()) for x in g]
    need(not any(x['rd']==17 or 17 in (x['rs1'],x['rs2']) for x in retained),'Original callback and every bounded dependency have no A7 read/write')
    idx={x['PC']:x for x in caller+[x for g in groups.values() for x in g]}
    exact(idx,0x1989a,op='addi',rd=11,rs1=0,immediate=1);exact(idx,0x1989c,op='mv',rd=10,rs1=9)
    exact(idx,0x18986,op='lw',rd=15,rs1=10,immediate=8)
    exact(idx,0x18aa0,op='or',rd=15,rs1=15,rs2=14)
    exact(idx,0x18a7e,op='or',rd=14,rs1=14,rs2=13)
    need(not any(14 in (x['rs1'],x['rs2']) for x in groups['18986']),'No intermediate read of A4 before18A9C overwrite')
    need(not any(13 in (x['rs1'],x['rs2']) for k in ('18986','18a98') for x in groups[k]),'No intermediate read of A3 before18A7A overwrite')
    need(not any(14 in (x['rs1'],x['rs2']) for x in groups['18a98'] if x['PC']<0x18a9c),'Actual enabled path overwrites A4 first')
    need(not any(13 in (x['rs1'],x['rs2']) for x in groups['18a6e'] if x['PC']<0x18a7a),'Actual enabled path overwrites A3 first')
    need(not any(x['rd'] in (5,7,28,29,30,31) or any(r in (x['rs1'],x['rs2']) for r in (5,7,28,29,30,31)) for x in retained),'All other T registers unread and preserved')
    need([x['PC'] for x in retained if x['rd']==6]==[0x8520] and [x['PC'] for x in retained if 6 in (x['rs1'],x['rs2'])]==[0x8524],'Only T1 source write15 and early count read')
    fill={x['PC']:x for x in before['fill_fast']};exact(fill,0x8520,op='addi',rd=6,rs1=0,immediate=15)
    return dict(A2_first_post_config_write_PC=0x198b2,A2_first_later_use_PC=0x189da,
        A6_first_post_config_write_PC=0x189be,A6_first_later_use_PC=0x189cc,
        intermediate_leaf_targets=[0x18986,0x18a98,0x18a6e],A2_A6_entry_clobbers_overwritten_for_this_caller=True,
        A0_first_post_config_write_PC=0x1989c,A1_first_post_config_write_PC=0x1989a,
        A3_first_post_config_write_PC=0x18a7a,A3_first_later_use_PC=0x18a7e,
        A4_first_post_config_write_PC=0x18a9c,A4_first_later_use_PC=0x18aa0,
        A5_first_post_config_write_PC=0x18986,A5_first_later_use_PC=0x1898a,
        A0_through_A6_entry_clobbers_overwritten_for_this_caller=True,
        original_A7_unread_and_preserved_to_normal_exit=True,new_A7_clobber_would_escape=True,
        original_T0_T2_T3_T4_T5_T6_unread_and_preserved_to_normal_exit=True,
        original_T1_only_write_PC=0x8520,original_T1_exit_value=15,
        any_new_T_clobber_requires_separate_exit_proof=True,
        relies_on_PSABI=False,no_async_register_observers_required=True,
        native102B_promotion_proved=False,full_native_ABI_proved=False)
def controls(blobs,groups,C,decode):
    out=[]
    for key,pc,field in [('1892e',0x18934,'immediate'),('1892e',0x18974,'immediate'),('1892e',0x18978,'immediate'),('1892e',0x1897e,'immediate'),('189ae',0x189b0,'target'),('18a8e',0x18a92,'rs1')]:
        old=next(x for x in groups[key] if x['PC']==pc);a=RANGES[key][0];found=None
        for bit in range(old['bytes']*8):
            raw=bytearray(blobs[key]);raw[pc-a+bit//8]^=1<<(bit%8)
            try:row=decode(raw[pc-a:],pc)
            except ValueError:continue
            keys=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if row[field]==old[field] or any(row[k]!=old[k] for k in keys if k!=field):continue
            found=(raw,bit,row);break
        need(found is not None,'Raw single-operand negative available');raw,bit,row=found;changed=dict(groups);changed[key]=C.rows(raw,a,decode)
        try:gate(changed)
        except ValueError as e:out.append(dict(PC=pc,field=field,bit=bit,original=old[field],mutated=row[field],raw_hex=row['raw_hex'],rejected=True,reason=str(e)));continue
        raise ValueError('Incorrect ADC operand admitted')
    return out
def inspect(root,firmware=None,image_elf=None):
    root=Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists():close(HERE,sha(HERE/'seal.json'))
    prior,previous,C,decode,E,old=context(root);prior.inspect(root)
    ledger=read(HERE/'ledger.json');groups=ledger['groups'];blobs={}
    for k,(a,z,n,h) in RANGES.items():
        blob=b''.join(bytes.fromhex(x['raw_hex']) for x in groups[k]);blobs[k]=blob
        need(len(blob)==z-a and len(groups[k])==n and hashlib.sha256(blob).hexdigest()==h,'Pinned complete source '+k)
        need(C.rows(blob,a,decode)==groups[k],'All raw operand fields '+k)
    facts=gate(groups);parse=load('ADC_retained_static_text_fields',HERE/'r2_fields.py').parse
    independent=[parse(x) for x in read(HERE/'r2-static.json')['tool_stdout']]
    need(independent==[x for g in groups.values() for x in g],'Every field independently crosschecked with retained static r2 text')
    caller=read(old/'ledger.json')['groups']['callback'];facts['caller']=caller_contract(caller)
    facts['post_config_register_liveness']=post_config_liveness(root,groups,caller)
    facts.update(conditional_whole_callback_SP_RA_S_GP_TP_preservation=True,
        minimum_stack_bytes_including_nested=144,config_word52_preservation_only_if_disjoint=True,
        config_word52_actual_value_proved=False,installed_identity_proved=False,
        conditional_callback_MMIO_write_word_addresses=[0x40012400+x for x in (4,8,12,16,20,24,28,32,36,40,44,48,52,56)]+[0x40021004,0x4002100c,0x40021018],
        RCC_reset_word_not_snapshotted_or_restored=True,RCC_reset_clear_mask=0x200,
        config52_preservation_scope='only this bounded normal-return callback, given disjoint word and no interference')
    result=dict(schema='TSL9-original-ADC-config-and-callback-closure-v1',passed=True,metadata_only=firmware is None,
        actual_original_firmware_read=False,actual_optional_ELF_read=False,raw_controls_replayed=False,facts=facts,
        premises=['old restricted8520 valid aligned32B zero path','valid nonwrapping144B stack interval','fixed MMIO accesses complete normally','stack/code/config-word52/MMIO write sets are disjoint','no asynchronous register/stack/code/config-word changes or register observers','poll returns nonzero on some finite read for normal return'],
        full_original_ABI_proved=False,whole_OTA_proved=False,physical_chip_identity_proved=False,
        config52_entire_initialization_lifetime_proved=False,new_BIN_generated=False,compiler_or_HOST_run=False,
        target_execution=False,ISA_or_ESIL_execution=False,network=False,hardware=False)
    need(image_elf is None or firmware is not None,'Optional ELF requires explicit original firmware')
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Actual official ID2966')
        raw=Path(firmware).read_bytes()
        for k,(a,z,_,_) in RANGES.items():need(C.rows(raw[a-0x8000:z-0x8000],a,decode)==groups[k],'Actual complete ADC source '+k)
        need(C.rows(raw[0x117f0:0x1195c],0x197f0,decode)==caller,'Actual complete callback source')
        prior_result=prior.inspect(root,firmware)
        need(prior_result['actual_original_firmware_read'],'Previously closed188E2 source reread')
        negatives=controls(blobs,groups,C,decode)
        result.update(actual_original_firmware_read=True,actual_new_source_bytes=386,actual_new_source_rows=148,
            actual_caller_bytes=364,prior_dependency_source_bytes=106,raw_controls_replayed=True,raw_controls=len(negatives),controls=negatives)
        if image_elf is not None:
            e=E(Path(image_elf).resolve(strict=True));need(e.kind==2,'Actual ELF32 executable')
            for k,(a,z,_,_) in RANGES.items():
                owners=[s for s in e.sections if s['flags']&6==6 and s['address']<=a and z<=s['address']+s['size']]
                need(len(owners)==1,'Unique actual executable source owner');owner=owners[0];at=a-owner['address']
                need(e.data(owner)[at:at+z-a]==blobs[k],'Optional original source subset '+k)
            result.update(actual_optional_ELF_read=True,actual_optional_ELF_sha256=sha(image_elf),whole_ELF_provenance_proved=False)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--firmware',type=Path);p.add_argument('--image-elf',type=Path);a=p.parse_args()
    print(json.dumps(inspect(a.project_root,a.firmware,a.image_elf)))
