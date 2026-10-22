#!/usr/bin/env python3
"""Metadata default; explicit BOOT/Runtime files enable bounded static proof."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
BOOT='650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
RUNTIME='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BODY='44702abb50c4489f378bb1036d8cf949817301e2e07d8af8434f7d6e119438d5'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,name):return next(p for p in (root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def prior(root):
    folder=case(root,'boot2580-command-adapter-2026-10-21')/'source';audit=folder/'final-audit.json';need(sha(audit)=='e906c1a4bd695e613a0f6a3601b7be23812295e1d9fc8cf0d6c0ed41473d4d60','Pinned immutable original BOOT source audit')
    for m in read(audit)['members']:
        p=folder/m['path'];need(p.stat().st_size==m['bytes'] and sha(p)==m['sha256'],'Immutable original BOOT source member '+m['path'])
    return folder
def context(root):
    folder=case(root,'v4160-ota-handler-2026-10-22')/'source-review';need(sha(folder/'seal.json')=='7e32146e97e26f74eefa36fa8d8eab4d558dd1deae37e88bef8ccc4d8b059615','Pinned independent raw-field decoder proof')
    for n,pin in read(folder/'seal.json')['members'].items():need(sha(folder/n)==pin,'Immutable decoder member '+n)
    return load('bounded_BOOT_raw_fields',folder/'capture-source.py').context(root)[0]
def rows(raw,decode):
    result=[];pc=0x21be
    while pc<0x235c:
        r=decode(raw[pc-0x1000:],pc);need(pc+r['bytes']<=0x235c,'Whole BOOT source instruction');result.append(r);pc+=r['bytes']
    need(len(result)==144,'Entire original BOOT144 instructions');return result
def tuple_fields(r):return [r[k] for k in ('PC','op','rd','rs1','rs2','immediate','target','memory_width')]
def gate(actual):
    expected=read(HERE/'evidence.json');by={r['PC']:r for r in actual}
    need([tuple_fields(by[r[0]]) for r in expected['guard_operand_rows']]==expected['guard_operand_rows'],'Exact original low/high load, byte assembly, bases/shifts/unsigned guard operands')
    for pc,target,rd in [(0x2272,0x20e6,1),(0x22ac,0x1c82,1),(0x22da,0x1c82,1),(0x22f0,0x250e,1),(0x22f4,0x2184,1),(0x233a,0x1afa,1),(0x234e,0x1afa,1),(0x22c6,0x2aba,0),(0x230e,0x2aa0,0)]:need((by[pc]['op'],by[pc]['target'],by[pc]['rd'])==('jal',target,rd),'Every original bounded external call/tail role')
    need((by[0x225e]['op'],by[0x225e]['rd'],by[0x225e]['rs1'])==('jalr',1,15),'Optional alignment copy uses loaded target A5')
    need((by[0x2282]['op'],by[0x2282]['rd'],by[0x2282]['rs1'])==('lw',12,13) and (by[0x2288]['op'],by[0x2288]['rd'],by[0x2288]['rs1'])==('lw',13,13),'Ordered Flash32 then liveRAM32 results')
    need((by[0x228a]['op'],by[0x228a]['rs1'],by[0x228a]['rs2'],by[0x228a]['target'])==('bne',12,13,0x21e2),'Mismatch silently reaches epilogue')
    need((by[0x226e]['op'],by[0x226e]['rd'],by[0x226e]['rs1'],by[0x226e]['immediate'])==('addi',18,18,256),'Quarter offset increment occurs before call')
    need((by[0x2260]['rd'],by[0x2260]['immediate'],by[0x2262]['rd'],by[0x2262]['immediate'])==(18,0,20,1024) and (by[0x2274]['op'],by[0x2274]['rs1'],by[0x2274]['rs2'],by[0x2274]['target'])==('bne',18,20,0x2266),'Four-quarter source loop only under appropriate live-register/return conditions')
    need((by[0x2208]['op'],by[0x2208]['rd'],by[0x2208]['immediate'])==('addi',15,1026) and by[0x220c]['target']==0x21e2,'Full W length1026 gate')
    need((by[0x2202]['op'],by[0x2202]['rs1'],by[0x2202]['immediate'])==('lbu',3,139) and (by[0x231e]['op'],by[0x231e]['rs1'],by[0x231e]['immediate'])==('lbu',3,139),'W/E use current liveGP active byte')
    need((by[0x2294]['rd'],by[0x2294]['immediate'],by[0x2296]['rd'],by[0x2296]['immediate'])==(13,0,12,0),'Successful W requests empty reply')
    for pc,rd,value in [(0x2298,11,87),(0x2328,12,200),(0x2340,12,400),(0x2352,13,0),(0x2354,12,0),(0x2356,11,69)]:need((by[pc]['op'],by[pc]['rd'],by[pc]['immediate'])==('addi',rd,value),'Exact selected W/E reply and schedule scalar arguments')
    for hi_pc,target in [(0x232e,0x192c),(0x2346,0x20e2)]:
        hi,lo=by[hi_pc],by[hi_pc+4];need(hi['op']=='auipc' and lo['op']=='addi' and hi['rd']==lo['rd']==lo['rs1']==10 and (hi_pc+hi['immediate']+lo['immediate'])&0xffffffff==target,'Original scheduled callback PC-relative operands')
    need((by[0x2336]['op'],by[0x2336]['rs1'],by[0x2336]['rs2'],by[0x2336]['immediate'])==('sb',3,0,139),'E clears live active before scheduling')
    E=[r for r in actual if r['PC']>=0x231e]
    need([(r['PC'],r['target']) for r in E if r['op']=='jal' and r['rd']==1]==[(0x233a,0x1afa),(0x234e,0x1afa)] and [r['PC'] for r in E if r['op'].startswith('l') and r['memory_width'] is not None]==[0x231e],'Selected E has active read and two scheduler calls, no UID/length/payload/completion read')
    return True
def controls(raw,actual,decode):
    result=[];by={r['PC']:r for r in actual}
    for pc,field,label in [(0x2208,'immediate','W full-length1026'),(0x2236,'immediate','1024-byte destination stride'),(0x2238,'immediate','upper bound high constant'),(0x2240,'rs1','unsigned limit operand'),(0x2282,'rd','Flash-first read result')]:
        old=by[pc];found=None
        for bit in range(old['bytes']*8):
            b=bytearray(raw);b[pc-0x1000+bit//8]^=1<<(bit%8)
            try:r=decode(b[pc-0x1000:],pc)
            except ValueError:continue
            if r[field] is None or r[field]==old[field] or any(r[k]!=old[k] for k in ('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width') if k!=field):continue
            found=(bytes(b),r,bit);break
        need(found is not None,'Actual single-field raw counterexample '+label);b,r,bit=found
        try:gate(rows(b,decode))
        except ValueError:result.append(dict(case=label,PC=pc,field=field,bit=bit,original=old[field],mutated=r[field],rejected=True));continue
        raise ValueError('Accepted BOOT guard/readback mutation')
    return result
def arithmetic():
    # Mathematical guard expression from separately verified operands, not a CPU interpreter.
    page_bytes=1<<10;base=(0x20000+32)*page_bytes;limit=0x18000-256;accepted_max=limit//page_bytes
    need(base==0x08008000 and accepted_max==95 and 65535*page_bytes<0x100000000,'Unsigned u16 page arithmetic has no address-domain ambiguity')
    samples=[]
    for p in (0,74,75,95,96,65535):
        destination=(base+p*page_bytes)&0xffffffff;offset=(destination+0xf7ff8000)&0xffffffff
        need(offset==p*page_bytes,'Wrapped subtract-base identity for the u16 domain');samples.append(dict(page=p,guard_accepts=offset<=limit,destination=destination,end_exclusive=destination+page_bytes))
    return dict(page_bytes=page_bytes,numeric_accepted_pages=[0,95],numeric_page_count=96,initial_target_base=base,last_page_start=base+95*page_bytes,numeric_target_end_exclusive=base+96*page_bytes,maximum_target_span_bytes=96*page_bytes,current_runtime_base=0x8000,current_runtime_bytes=76800,current_runtime_pages=75,current_runtime_end_exclusive=0x1ac00,extra_numeric_page_numbers=[75,95],extra_numeric_pages=21,extra_numeric_interval_low=[0x1ac00,0x20000],extra_numeric_interval_flash_alias=[0x0801ac00,0x08020000],extra_numeric_bytes=21504,samples=samples,storage_free_proved=False,physical_Flash_capacity_proved=False)
def inspect(root,boot=None,firmware=None):
    root=Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists():
        for n,pin in read(HERE/'seal.json')['members'].items():need(sha(HERE/n)==pin,'Immutable bounded BOOT review '+n)
    folder=prior(root);evidence=read(HERE/'evidence.json');need(evidence['BOOT_sha256']==BOOT and evidence['BOOT_body_sha256']==BODY and (evidence['body_bytes'],evidence['body_instructions'],len(evidence['guard_operand_rows']))==(414,144,18),'Pinned bounded source metadata, not an actual file read')
    facts=arithmetic();result=dict(schema='ID2580-BOOT-numeric-layout-review-v1',passed=True,metadata_only=boot is None,source_evidence_metadata_checked=True,actual_BOOT_read=False,actual_Runtime_read=False,raw_operand_controls_replayed=False,numeric=facts,installed_BOOT_identity_proved=False,storage_free_proved=False,NV_metadata_ownership_proved=False,physical_Flash_capacity_proved=False,whole_image_CRC_or_signature_acceptance_proved=False,whole_OTA_compatibility_proved=False,new_BIN_generated=False,compiler_or_HOST_run=False,target_execution=False,ISA_emulation=False,network=False,hardware=False)
    need((boot is None)==(firmware is None),'Provide both --boot and --firmware, or neither')
    if boot:
        boot=Path(boot).resolve(strict=True);firmware=Path(firmware).resolve(strict=True);need(sha(boot)==BOOT and boot.stat().st_size==12288,'Exact supplied BOOT ID2580');need(sha(firmware)==RUNTIME and firmware.stat().st_size==76800,'Exact supplied original Runtime ID2966')
        raw=boot.read_bytes();decode=context(root);actual=rows(raw,decode);need(hashlib.sha256(raw[0x11be:0x135c]).hexdigest()==BODY,'Actual original414-byte command body')
        retained=[r for r in read(folder/'retained-source.json')['rows'] if 0x21be<=r['addr']<0x235c];need(len(retained)==144 and [(r['PC'],r['bytes'],r['raw_hex']) for r in actual]==[(r['addr'],r['size'],r['bytes']) for r in retained],'All144 raw bytes/order agree with independently retained static source')
        gate(actual);negative=controls(raw,actual,decode);jump=[decode(raw[pc-0x1000:],pc) for pc in (0x20e2,0x20e4)];need((jump[0]['op'],jump[0]['rd'],jump[0]['immediate'])==('lui',6,0x8000) and (jump[1]['op'],jump[1]['rd'],jump[1]['rs1'])==('jalr',0,6),'Four-byte scheduled callback is a numeric jump8000, not execution evidence')
        result.update(actual_BOOT_read=True,actual_Runtime_read=True,BOOT_file_extent=dict(base=0x1000,bytes=len(raw),end_exclusive=0x4000),Runtime_file_extent=dict(base=0x8000,bytes=firmware.stat().st_size,end_exclusive=0x8000+firmware.stat().st_size),selected_body_bytes=414,selected_body_instructions=144,scheduled_handoff_bytes=4,scheduled_handoff_numeric_target=0x8000,raw_operand_controls_replayed=True,raw_operand_controls=len(negative),controls=negative,actual_boot_body_operands_rechecked=True)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--boot',type=Path);p.add_argument('--firmware',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.boot,a.firmware)))
