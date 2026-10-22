"""Bounded static reply consumer review. No execution, linking, or code generation."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RANGES={'packet':(0x13e98,0x13eb4),'allocate_copy_TX_free':(0x13b4c,0x13ba6),
        'small':(0x13f66,0x13f7e),'page':(0x9b8e,0x9c0a),'TX_original':(0x8a56,0x8b6e)}
PRIOR='v4160-ota-handler-compact-2026-10-22'
SEAL='5b915632290d82c30545fa9ec517fc96bb67d706abf71f592e53354c3a622a8c'

def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def case(root,name):return next(p for p in (root/'apk-analysis'/('tsl9-'+name),root/'analysis'/name) if p.is_dir())
def pins(root):
    for key,pin in read(HERE/'reference-pins.json').items():
        scope,name=key.split('/',1);p=case(root,scope)/name
        need(sha(p)==pin,'Immutable reference '+key)
def closed():
    p=HERE/'seal.json'
    if p.exists():
        for name,pin in read(p)['members'].items():
            target=(HERE/name).resolve();need(target.is_relative_to(HERE) and sha(target)==pin,'Closed reply review member '+name)
def context(root):
    prior=case(root,PRIOR)/'callee-review'
    m=runpy.run_path(str(prior/'review.py'));m['closed'](prior,SEAL)
    decode,E,_=m['context'](root)
    return m,decode,E
def rows(blob,start,decode):
    out=[];at=0
    while at<len(blob):
        row=decode(blob[at:],start+at);need(row['bytes'] in (2,4) and at+row['bytes']<=len(blob),'Whole static instruction')
        out.append(row);at+=row['bytes']
    return out
def validate(blob,start,decode,expected):
    actual=rows(blob,start,decode);need(actual==expected,'Exact retained raw operands');return actual
def facts(groups):
    b={r['PC']:r for g in groups.values() for r in g}
    def exact(pc,**fields):
        need(all(b[pc][k]==v for k,v in fields.items()),'Source frontier '+hex(pc))
    exact(0x13e9c,op='mv',rd=15,rs1=12);exact(0x13e9e,op='mv',rd=14,rs1=13)
    exact(0x13ea0,op='beq',rs1=12,rs2=0,target=0x13ea4)
    exact(0x13ea2,op='bne',rs1=13,rs2=0,target=0x13eb0)
    exact(0x13eac,op='jal',rd=0,target=0x8a56);exact(0x13eb0,op='jal',rd=0,target=0x13b4c)
    exact(0x13b54,op='lw',rd=15,rs1=9,immediate=0x70,memory_width=32)
    exact(0x13b60,op='mv',rd=10,rs1=13)
    exact(0x13b64,op='sw',rs1=2,rs2=12,immediate=12,memory_width=32)
    exact(0x13b66,op='sw',rs1=2,rs2=13,immediate=8,memory_width=32)
    exact(0x13b68,op='jalr',rd=1,rs1=15)
    need(not any(r['rd']==12 for r in groups['allocate_copy_TX_free'] if r['PC']<0x13b68),'Allocator sees entry A2 pointer')
    exact(0x13b6a,op='beq',rs1=10,rs2=0,target=0x13b98)
    exact(0x13b6e,op='lw',rd=15,rs1=9,immediate=0x4c,memory_width=32)
    exact(0x13b70,op='lw',rd=11,rs1=2,immediate=12,memory_width=32)
    exact(0x13b72,op='mv',rd=12,rs1=13);exact(0x13b76,op='jalr',rd=1,rs1=15)
    exact(0x13b7c,op='mv',rd=12,rs1=8);exact(0x13b80,op='jal',rd=1,target=0x8a56)
    exact(0x13b88,op='lw',rd=6,rs1=9,immediate=0x68,memory_width=32)
    exact(0x13b96,op='jalr',rd=0,rs1=6)
    exact(0x13f68,op='sb',rs1=2,rs2=12,immediate=15,memory_width=8)
    exact(0x13f6e,op='addi',rd=12,rs1=2,immediate=15)
    exact(0x13f74,op='jal',rd=1,target=0x13b4c)
    exact(0x9bd4,op='jalr',rd=1,rs1=15);exact(0x9be0,op='jal',rd=1,target=0x8a56)
    exact(0x8b56,op='lbu',rd=10,rs1=10,immediate=0,memory_width=8)
    exact(0x8b62,op='sb',rs1=16,rs2=10,immediate=5,memory_width=8)
    return dict(packet_wrapper_bytes=28,allocation_wrapper_bytes=90,small_bytes=24,page_bytes=124,
        original_pointer_escapes_to_allocator_A2=True,pointer_reloaded_from_live_SP12_into_copy_A1=True,
        length_reloaded_from_live_SP8=True,copy_target_fresh_live_S1_plus_4C=True,
        TX_uses_postcopy_live_S0_buffer=True,numeric_pointer_globally_unobserved_proved=False)
def controls(groups,decode,prior):
    choices=[('packet',0x13ea2,'rs1','packet length branch'),('allocate_copy_TX_free',0x13b64,'immediate','saved source slot'),
             ('allocate_copy_TX_free',0x13b6e,'immediate','fresh copy slot'),('allocate_copy_TX_free',0x13b70,'rd','source pointer argument'),
             ('TX_original',0x8b56,'rd','payload byte feeds store')]
    out=[]
    for name,pc,field,label in choices:
        expected=groups[name];blob=bytes.fromhex(''.join(r['raw_hex'] for r in expected));start=RANGES[name][0]
        out+=prior['controls'](blob,start,decode,expected,[(pc,field,label)])
    return out
def inspect(root,firmware=None,folder=None,image_elf=None,candidate_root=None):
    root=Path(root).resolve(strict=True);closed();pins(root);prior,decode,E=context(root);ledger=read(HERE/'source-ledger.json');groups=ledger['rows']
    for n,(start,end) in RANGES.items():
        blob=bytes.fromhex(''.join(r['raw_hex'] for r in groups[n]));need(len(blob)==end-start,'Exact bounded extent '+n)
        validate(blob,start,decode,groups[n])
    result=dict(schema='TSL9-reply-pointer-consumer-review-v1',passed=True,metadata_only=not any((firmware,folder,image_elf,candidate_root)),
        actual_original_firmware_read=False,actual_native_artifacts_read=False,actual_image_ELF_read=False,
        actual_candidate_sources_read=False,retained_instruction_rows=sum(map(len,groups.values())),facts=facts(groups),
        raw_operand_controls=controls(groups,decode,prior),installed_identity_proved=False,full_ABI_admitted=False,
        original_or_candidate_execution=False,HOST_or_compiler_run=False,ISA_emulation=False,network=False,hardware_OTA_proved=False)
    if firmware:
        firmware=Path(firmware).resolve(strict=True);need(sha(firmware)==FW,'Exact original official ID2966 firmware')
        fw=firmware.read_bytes();need(len(fw)==76800,'Official76800 bytes')
        for n,(start,end) in RANGES.items():validate(fw[start-0x8000:end-0x8000],start,decode,groups[n])
        result['actual_original_firmware_read']=True;result['firmware_sha256']=FW
    if image_elf:
        image_elf=Path(image_elf).resolve(strict=True);e=E(image_elf);need(e.kind==2,'Actual linked address witness')
        for n,(start,end) in RANGES.items():
            if n=='TX_original':continue
            owners=[s for s in e.sections if s['flags']&2 and s['type']!=8 and s['address']<=start and end<=s['address']+s['size']]
            need(len(owners)==1,'Unique allocated consumer owner '+n);s=owners[0]
            validate(e.data(s)[start-s['address']:end-s['address']],start,decode,groups[n])
        result['actual_image_ELF_read']=True;result['image_ELF_sha256']=sha(image_elf)
        result['image_scope']='Four unchanged App consumers only; rebuilt TX bytes are not asserted identical to original'
    if folder:
        folder=Path(folder).resolve(strict=True);native=runpy.run_path(str(case(root,PRIOR)/'ABI-review/native.py'))['inspect'](root,folder)
        result['actual_native_artifacts_read']=True;result['actual_native_folder']=str(folder)
        result['native_projection']=dict(object_sha256=native['actual_artifacts']['ota_handler.o']['sha256'],
            bytes=native['measured']['bytes'],frame=native['measured']['frame_bytes'],response=native['response_IR'],frame_contents=native['frame_contents'])
    if candidate_root:
        candidates=prior['candidate_inputs'](root,candidate_root)
        expected=read(case(root,PRIOR)/'callee-review/copy-instructions.json')
        for item in candidates:validate(item['body'],0x20000332,decode,expected)
        result['actual_candidate_sources_read']=True;result['candidate_sources']=[{k:v for k,v in item.items() if k!='body'} for item in candidates]
    return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path)
    for n in ('firmware','folder','image-elf','candidate-root','receipt','replay'):p.add_argument('--'+n,type=Path)
    a=p.parse_args();root=a.project_root.resolve(strict=True)
    if a.replay:
        need(not a.receipt and not any((a.firmware,a.folder,a.image_elf,a.candidate_root)),'Replay uses recorded explicit references')
        record=read(a.replay);inputs=record['inputs'];got=inspect(root,**{k:Path(v) if v else None for k,v in inputs.items()})
        need(got==record['result'],'Read-only exact actual/metadata replay');print(json.dumps(got));return
    result=inspect(root,a.firmware,a.folder,a.image_elf,a.candidate_root)
    if a.receipt:
        receipt=a.receipt.resolve();need(not receipt.exists(),'Create-only receipt');receipt.parent.mkdir(parents=True,exist_ok=True)
        inputs={n:str(getattr(a,n).resolve()) if getattr(a,n) else None for n in ('firmware','folder','image_elf','candidate_root')}
        with receipt.open('xb') as f:f.write((json.dumps(dict(inputs=inputs,result=result),indent=2)+'\n').encode())
    print(json.dumps(result))
if __name__=='__main__':main()
