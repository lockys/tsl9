"""Original197F0 source CFG and small call dependencies, static fields only."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PRIOR='82ccc4a6dbd43fd467993291629fa62c6de3e8662b844f8fa43a90d821d47a0d'
CONT='b453913bfa81f02d097527cba2ee826b253dd43c7873be17d7881bb7b7b49ecc'
IRQ='4d6745033aae496576b9db2fb7467396fbfda5067713cf1451a34b949b414283'
RANGES={'callback':(0x197f0,0x1995c,130,'ee7d9a35ebc31a363cc5f6efca0ce21d341099694f34aa90185be94995d826a4'),
        'fill_fast':(0x8520,0x854a,17,'98688760c7a23d3f8b23f4b6cdbb0dd285fd8562ff5ba950b5fd46fee5a7ae2d'),
        'rcc_19124':(0x19124,0x19142,12,'ca3d4aef350f5c783ee6eeae7d25ba85b74055551058135024d07edf1804e864'),
        'rcc_1908c':(0x1908c,0x1909e,8,'8a1f8aa217067a65d4a6cfa6420d03b423019f47471c699a98afc65062a01b0a')}
CALLS=[(0x19814,0x8520),(0x1986e,0x19124),(0x19874,0x1908c),(0x1987a,0x188e2),(0x19896,0x1892e),(0x1989e,0x18986),(0x198a6,0x18a98),(0x198ac,0x18a6e),(0x198b8,0x189ae),(0x198c0,0x18996),(0x198ca,0x18a8e),(0x198dc,0x18a66),(0x198e6,0x188e2)]
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def closed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact previous source seal')
    for n,h in read(folder/'seal.json')['members'].items():need(sha(folder/n)==(h if isinstance(h,str) else h['sha256']),'Closed source member '+n)
def context(root):
    old=case(root,'v4160-allocator-callback-2026-10-22')/'callback-review';closed(old,PRIOR)
    continuation=case(root,'v4160-resident-memory-2026-10-22')/'continuation-review';closed(continuation,CONT)
    spec=importlib.util.spec_from_file_location('app_callback_original_reader',old/'check.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
    allocator=C.prior(root);R,_,_=allocator.references(root);_,E,_=R.context(root)
    audit=case(root,'v4160-interrupt-init-2026-10-21')/'source';need(sha(audit/'final-audit.json')==IRQ,'Unchanged original IRQ source audit')
    for item in read(audit/'final-audit.json')['files']:need(sha(audit/item['path'])==item['sha256'],'Prior IRQ source member')
    return C,C.decoder(root),E,continuation,audit
def gate(groups):
    b={r['PC']:r for r in groups['callback']};f={r['PC']:r for r in groups['fill_fast']};a={r['PC']:r for r in groups['rcc_19124']};z={r['PC']:r for r in groups['rcc_1908c']}
    def exact(index,pc,**fields):need(all(index[pc][k]==v for k,v in fields.items()),'Original callback source field '+hex(pc))
    for key,(start,end,count,_) in RANGES.items():need(len(groups[key])==count and sum(r['bytes'] for r in groups[key])==end-start,'Whole bounded instruction partition '+key)
    need([(r['PC'],r['target']) for r in groups['callback'] if r['op']=='jal' and r['rd']==1]==CALLS,'All13 direct callsites with exact targets and link form')
    need([(r['PC'],r['op'],r['target']) for r in groups['callback'] if r['target'] is not None and not(r['op']=='jal' and r['rd']==1)]==[(0x198d6,'beq',0x198c6)],'Only local loop branch, no hidden direct tail')
    exact(b,0x197f0,op='addi',rd=2,rs1=2,immediate=-128)
    saves=[(0x197fa,1,124),(0x197fc,9,116),(0x197fe,8,120),(0x19800,18,112),(0x19802,19,108),(0x19804,20,104),(0x19806,21,100),(0x19808,22,96),(0x1980a,23,92),(0x1980c,24,88),(0x1980e,25,84),(0x19810,26,80),(0x19812,27,76)]
    for pc,reg,offset in saves:exact(b,pc,op='sw',rs1=2,rs2=reg,immediate=offset,memory_width=32)
    restores=[(0x19920,1,124),(0x19928,9,116),(0x1992a,18,112),(0x19932,19,108),(0x19934,20,104),(0x1993c,21,100),(0x1993e,22,96),(0x19946,23,92),(0x1994e,8,120),(0x19950,24,88),(0x19952,25,84),(0x19954,26,80),(0x19956,27,76)]
    for pc,reg,offset in restores:exact(b,pc,op='lw',rd=reg,rs1=2,immediate=offset,memory_width=32)
    exact(b,0x19958,op='addi',rd=2,rs1=2,immediate=128);exact(b,0x1995a,op='jalr',rd=0,rs1=1,immediate=0)
    need([r['PC'] for r in groups['callback'] if r['op']=='jalr']==[0x1995a],'No indirect call in main, only terminalRET')
    exact(b,0x197f2,op='addi',rd=12,rs1=0,immediate=32);exact(b,0x197f6,op='addi',rd=11,rs1=0,immediate=0);exact(b,0x197f8,op='addi',rd=10,rs1=2,immediate=32)
    exact(b,0x1984e,op='addi',rd=11,rs1=0,immediate=1);exact(b,0x19850,op='addi',rd=10,rs1=0,immediate=512)
    exact(b,0x19824,op='lui',rd=15,immediate=0x40012000);exact(b,0x19828,op='addi',rd=9,rs1=15,immediate=1024);exact(b,0x19858,op='lui',rd=8,immediate=0x40012000)
    exact(b,0x19872,op='lui',rd=10,immediate=0xc000);exact(b,0x19878,op='mv',rd=10,rs1=9)
    exact(b,0x198c4,op='mv',rd=15,rs1=9);exact(b,0x198c6,op='mv',rd=10,rs1=15);exact(b,0x198c8,op='addi',rd=11,rs1=0,immediate=2)
    exact(b,0x198ce,op='lui',rd=15,immediate=0x40012000);exact(b,0x198d2,op='addi',rd=15,rs1=15,immediate=1024);exact(b,0x198d6,op='beq',rs1=10,rs2=0,target=0x198c6)
    exact(b,0x198e0,op='sw',rs1=2,rs2=10,immediate=28);exact(b,0x1991e,op='lw',rd=14,rs1=2,immediate=28);exact(b,0x19948,op='mv',rd=10,rs1=14)
    need(not any(r['rd'] in (3,4,16,17) for r in groups['callback']),'No explicit main GP/TP/A6/A7 writes; nested effects remain unproved')
    exact(f,0x8520,op='addi',rd=6,rs1=0,immediate=15);exact(f,0x8522,op='mv',rd=14,rs1=10);exact(f,0x8524,op='bgeu',rs1=6,rs2=12,target=0x854a)
    exact(f,0x8528,op='andi',rd=15,rs1=14,immediate=15);exact(f,0x852c,op='bne',rs1=15,rs2=0,target=0x85aa);exact(f,0x852e,op='bne',rs1=11,rs2=0,target=0x8598)
    exact(f,0x8530,op='andi',rd=13,rs1=12,immediate=-16);exact(f,0x8534,op='andi',rd=12,rs1=12,immediate=15);exact(f,0x8536,op='add',rd=13,rs1=13,rs2=14)
    for pc,offset in [(0x8538,0),(0x853a,4),(0x853c,8),(0x853e,12)]:exact(f,pc,op='sw',rs1=14,rs2=11,immediate=offset,memory_width=32)
    exact(f,0x8540,op='addi',rd=14,rs1=14,immediate=16);exact(f,0x8542,op='bltu',rs1=14,rs2=13,target=0x8538);exact(f,0x8546,op='bne',rs1=12,rs2=0,target=0x854a);exact(f,0x8548,op='jalr',rd=0,rs1=1,immediate=0)
    need(not any(r['rd'] in (1,2,3,4,8,9,*range(18,28)) or r['op']=='jal' or r['op']=='jalr' and r['rd']==1 for r in groups['fill_fast']),'Restricted8520 path has no hidden frame/S/GP write or nested call')
    exact(a,0x19124,op='beq',rs1=11,rs2=0,target=0x19132);exact(a,0x19126,op='lui',rd=14,immediate=0x40021000);exact(a,0x1912a,op='lw',rd=15,rs1=14,immediate=24);exact(a,0x1912c,op='or',rd=10,rs1=10,rs2=15);exact(a,0x1912e,op='sw',rs1=14,rs2=10,immediate=24)
    exact(z,0x1908c,op='lui',rd=13,immediate=0x40021000);exact(z,0x19090,op='lw',rd=15,rs1=13,immediate=4);exact(z,0x19092,op='lui',rd=14,immediate=0xffff4000);exact(z,0x19094,op='addi',rd=14,rs1=14,immediate=-1);exact(z,0x19096,op='and',rd=15,rs1=15,rs2=14);exact(z,0x19098,op='or',rd=10,rs1=10,rs2=15);exact(z,0x1909a,op='sw',rs1=13,rs2=10,immediate=4)
    for key in ('rcc_19124','rcc_1908c'):need(not any(r['rd'] in (1,2,3,4,8,9,*range(18,28)) or r['op']=='jal' or r['op']=='jalr' and r['rd']==1 for r in groups[key]),'Small RCC leaf has no nested call/S/GP/SP/RA writes')
    return dict(source_derived_range=[0x197f0,0x1995c],source_bytes=364,source_instructions=130,metadata_FUNC364_proved=False,direct_calls=13,unique_direct_targets=12,main_loop=[0x198c6,0x198d6],encoded_poll_timeout_present=False,normal_completion_proved=False,frame_bytes=128,saved_RA_and_S_words=13,first_unreviewed_dependency_site=0x1987a,first_unreviewed_dependency_target=0x188e2,restricted8520_premises=['entrySP16aligned','A0=liveSP+32 nonwrapping valid32B','A1=0 A2=32','normal memory completion, no code/stack alias or asynchronous changes'],restricted8520_write_SP_range=[32,63],other8520_paths_proved=False,config_word52_after_callback_proved=False)
def role(e):
    owner=e.byname['.text.tsl9v4160.conditional_runtime_197be']
    symbols=[{k:s[k] for k in ('name','value','size','info','other')} for s in e.symbols if s['name'] in ('__tsl9v4160_conditional_code_197f0','__tsl9v4160_address_197f0')]
    return dict(owner={k:owner[k] for k in ('name','type','flags','address','size','alignment')},entry_symbols=symbols)
def controls(blobs,groups,C,decode):
    out=[]
    for key,pc,field,label in [('callback',0x197f2,'immediate','initial zero count32'),('fill_fast',0x853e,'immediate','fourth fast-fill word'),('callback',0x198d6,'target','poll backedge'),('callback',0x19958,'immediate','normal frame pop128')]:
        start=RANGES[key][0];old=next(r for r in groups[key] if r['PC']==pc);found=None
        for bit in range(old['bytes']*8):
            raw=bytearray(blobs[key]);raw[pc-start+bit//8]^=1<<(bit%8)
            try:r=decode(raw[pc-start:],pc)
            except ValueError:continue
            keys=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if r[field]==old[field] or any(r[k]!=old[k] for k in keys if k!=field):continue
            found=(raw,bit);break
        need(found is not None,'Single-field byte control '+label);raw,bit=found;changed=dict(groups);changed[key]=C.rows(raw,start,decode)
        try:gate(changed)
        except ValueError:out.append(dict(case=label,PC=pc,field=field,bit=bit,rejected=True));continue
        raise ValueError('Accepted callback operand mutation')
    return out
def inspect(root,firmware=None,image_elf=None):
    root=Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists():closed(HERE,sha(HERE/'seal.json'))
    C,decode,E,continuation,audit=context(root);ledger=read(HERE/'ledger.json');groups=ledger['groups'];facts=gate(groups)
    for key,(_,_,_,pin) in RANGES.items():need(hashlib.sha256(b''.join(bytes.fromhex(r['raw_hex']) for r in groups[key])).hexdigest()==pin,'Pinned source bytes '+key)
    previous=read(continuation/'ledger.json');app=previous['App_callback_source_rows'];index={r['PC']:r for r in app};need((0x19a92+index[0x19a92]['immediate']+index[0x19a96]['immediate'])&0xffffffff==0x197f0 and index[0x19a9e]['immediate']==60,'Sealed original App config field44 source, semantic name remains inferred')
    result=dict(schema='TSL9-original-callback-CFG-v1',passed=True,metadata_only=firmware is None,actual_original_firmware_read=False,actual_callback_ELF_view_read=False,raw_controls_replayed=False,facts=facts,raw_config_field44_target=0x197f0,temperature_semantic_label_proved=False,all_nested_callee_effects_proved=False,whole_callback_SP_S_GP_preservation_proved=False,config_word52_after_callback_proved=False,installed_resident_identity_proved=False,whole_ELF_provenance_replayed=False,full_original_ABI_proved=False,whole_OTA_proved=False,new_BIN_generated=False,compiler_or_HOST_run=False,target_execution=False,ISA_emulation=False,network=False,hardware=False)
    need(image_elf is None or firmware is not None,'ELF view requires explicit original firmware')
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Actual official ID2966');raw=Path(firmware).read_bytes();blobs={}
        for key,(a,z,_,_) in RANGES.items():blobs[key]=raw[a-0x8000:z-0x8000];need(C.rows(blobs[key],a,decode)==groups[key],'Actual complete source fields '+key)
        need(C.rows(raw[0x11a8a:0x11ab4],0x19a8a,decode)==app,'Actual42B original config field44 source')
        retained=read(audit/'retained-instructions.json')['groups']['rcc_19124'];need(blobs['rcc_19124'].hex()==''.join(r['bytes'] for r in retained),'Same30B original IRQ helper, old94control matrix not rerun')
        nextrow=decode(raw[0x1195c:],0x1995c);need((nextrow['op'],nextrow['rd'],nextrow['rs1'],nextrow['immediate'])==('addi',2,2,-16),'Next source prologue corroborates CFG stop, not a FUNC-size oracle')
        negative=controls(blobs,groups,C,decode);result.update(actual_original_firmware_read=True,actual_source_bytes=454,actual_source_rows=167,actual_App_field44_bytes=42,raw_controls_replayed=True,raw_controls=len(negative),controls=negative)
        if image_elf is not None:
            e=E(Path(image_elf).resolve(strict=True));need(e.kind==2 and role(e)==ledger['ELF_role'],'Actual enclosing owner and NOTYPE/size0 roles')
            owner=e.byname[ledger['ELF_role']['owner']['name']];at=0x197f0-owner['address'];need(e.data(owner)[at:at+364]==blobs['callback'],'Actual callback code slice in enclosing548B section')
            result.update(actual_callback_ELF_view_read=True,actual_callback_ELF_sha256=sha(image_elf))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--image-elf',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.image_elf)))
