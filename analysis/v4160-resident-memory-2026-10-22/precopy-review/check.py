"""Complete candidate pre-copy comparison leaf, only static operand data."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PRIOR='d460886bab54b1a9d4ac288de09b38b2b1874aa806b07e5c049eaa6abe2bc401'
FILL='50a30704b4e5806ee29a9d1c3af83f3330aaee28e06af8b5580a2be840d66c17'
BODY='39eff00fe85a0bdea780df359a1f1d1356681a168097a60b7b805faac6303581'
def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def case(root,name):return next(p for p in (root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def closed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact source proof seal')
    seal=read(folder/'seal.json')
    for n,h in seal['members'].items():need(sha(folder/n)==(h if isinstance(h,str) else h['sha256']),'Immutable source member '+n)
    for n,h in seal.get('external_inputs',{}).items():
        p=root_path(folder,n)
        need(sha(p)==h,'Immutable external source '+n)
def root_path(folder,name):
    # Published cases and W cases have the same root depth.
    root=folder.parents[2];p=root/name
    if name.startswith('analysis/') and not p.is_file():p=root/('apk-analysis/tsl9-'+name[len('analysis/'):])
    return p
def context(root):
    scope=case(root,'v4160-allocator-callback-2026-10-22')/'callback-review';closed(scope,PRIOR)
    fill=case(root,'v4160-config-lifetime-2026-10-22')/'memset-review';closed(fill,FILL)
    spec=importlib.util.spec_from_file_location('precopy_prior_callback',scope/'check.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
    return C,read(scope/'ledger.json'),read(fill/'source-ledger.json')
def gate_leaf(rows):
    b=0x200004bc;index={r['PC']:r for r in rows}
    def exact(off,**fields):need(all(index[b+off][k]==v for k,v in fields.items()),'Complete pre-copy leaf field '+hex(b+off))
    need(len(rows)==19 and sum(r['bytes'] for r in rows)==62,'Complete62B/19rows, not merely the firstRET')
    exact(0,op='lui',rd=14,immediate=0x40024000);exact(4,op='lw',rd=15,rs1=14,immediate=0x20c,memory_width=32)
    exact(8,op='sw',rs1=14,rs2=0,immediate=0x20c,memory_width=32);exact(12,op='fence.i')
    exact(16,op='beq',rs1=10,rs2=0,target=b+24);exact(18,op='add',rd=14,rs1=10,rs2=12)
    exact(22,op='bne',rs1=12,rs2=0,target=b+36)
    for off in (24,50):exact(off,op='lui',rd=14,immediate=0x40024000)
    for off in (28,54):exact(off,op='sw',rs1=14,rs2=15,immediate=0x20c,memory_width=32)
    exact(32,op='addi',rd=10,rs1=0,immediate=0);exact(58,op='addi',rd=10,rs1=0,immediate=1)
    for off in (34,60):exact(off,op='jalr',rd=0,rs1=1,immediate=0)
    exact(36,op='addi',rd=10,rs1=10,immediate=1);exact(38,op='lbu',rd=13,rs1=10,immediate=-1,memory_width=8)
    exact(42,op='bne',rs1=13,rs2=11,target=b+24);exact(46,op='bne',rs1=10,rs2=14,target=b+36)
    need({r['rd'] for r in rows if r['rd'] not in (None,0)}=={10,13,14,15},'Only A0/A3/A4/A5 explicitly written')
    need(not any(r['op'] in ('jal','jalr') and r['rd']==1 for r in rows),'No nested callee/opaque control transfer')
    need(all(r['target'] is None or r['target'] in index for r in rows),'All direct targets remain inside the complete leaf')
    need([(r['op'],r['rs1'],r['rs2'],r['immediate']) for r in rows if r['op'] in ('sb','sh','sw')]==[('sw',14,0,524),('sw',14,15,524),('sw',14,15,524)],'Only MMIO writes; no config/stack byte stores')
    return True
def caller_gate(record,C):
    C.gate(record);rows=record['init_prefix'];b=rows[0]['PC'];index={r['PC']-b:r for r in rows}
    def exact(off,**fields):need(all(index[off][k]==v for k,v in fields.items()),'Original candidate caller argument/control '+hex(b+off))
    exact(0x1a,op='addi',rd=12,rs1=0,immediate=6);exact(0x1c,op='mv',rd=9,rs1=10)
    exact(0x1e,op='addi',rd=11,rs1=0,immediate=255);exact(0x22,op='addi',rd=10,rs1=10,immediate=24)
    need(C.target(index[0x28],index[0x2c])==0x200004bc,'Actual caller numeric target200004BC')
    exact(0x30,op='addi',rd=14,rs1=0,immediate=1);exact(0x32,op='addi',rd=15,rs1=0,immediate=3)
    exact(0x34,op='beq',rs1=10,rs2=14,target=b+0xd2)
    exact(0x38,op='lw',rd=15,rs1=9,immediate=8,memory_width=32);exact(0x3a,op='beq',rs1=15,rs2=0,target=b+0x46)
    exact(0x3c,op='lw',rd=14,rs1=9,immediate=56,memory_width=32);exact(0x3e,op='addi',rd=15,rs1=0,immediate=6)
    exact(0x40,op='beq',rs1=14,rs2=0,target=b+0xd2);exact(0x42,op='lw',rd=14,rs1=9,immediate=60,memory_width=32)
    exact(0x44,op='beq',rs1=14,rs2=0,target=b+0xd2)
    need(not any(r['rd'] in (2,9) or r['op'] in ('sb','sh','sw') for r in rows if b+0x30<=r['PC']<b+0x46),'Accepted local NV guards do not mutate SP/S1/config')
    return True
def inputs(root,refs):
    C,old,fill=context(root);decode=C.decoder(root);allocator=C.prior(root);maps=allocator.inputs(root,refs);source=C.candidate_data(root,refs);out=[]
    for item,mapping,original in zip(source,maps,old['candidates']):
        need(item['candidate']==mapping['candidate']==original['candidate'],'Exact two-version source associations')
        flash=mapping['mapped_core_flash']+0x200004bc-0x20000040;offset=flash-0x40000;blob=item['segment'][offset:offset+62]
        need(hashlib.sha256(blob).hexdigest()==BODY,'Actual complete candidate leaf identity')
        prefix=C.rows(item['init_prefix_bytes'],item['slot400A4'],decode);need(prefix==original['init_prefix'],'Actual114B caller fields agree with sealed ledger')
        fill_record=next(x for x in fill['candidates'] if x['candidate']==item['candidate']);fill_at=fill_record['mapped_flash']-0x40000
        need(hashlib.sha256(item['segment'][fill_at:fill_at+46]).hexdigest()==fill_record['body_sha256'],'Actual later fill body matches existing preservation proof')
        caller_gate(original,C);body=C.rows(blob,0x200004bc,decode);gate_leaf(body)
        out.append(dict(candidate=item['candidate'],mapped_flash=flash,RAM_entry=0x200004bc,bytes=62,body_sha256=BODY,rows=body,caller_prefix_sha256=hashlib.sha256(item['init_prefix_bytes']).hexdigest(),caller_config_record=original,blob=blob,prefix_bytes=item['init_prefix_bytes']))
    return C,decode,out
def controls(item,C,decode):
    result=[]
    for pc,field,label in [(0x200004cc,'rs1','null input branch'),(0x200004e6,'rs2','full32 A1 comparison'),(0x200004f6,'immediate','successful match result1')]:
        old=next(r for r in item['rows'] if r['PC']==pc);offset=pc-0x200004bc;found=None
        for bit in range(old['bytes']*8):
            raw=bytearray(item['blob']);raw[offset+bit//8]^=1<<(bit%8)
            try:r=decode(raw[offset:],pc)
            except ValueError:continue
            keys=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if r[field]==old[field] or any(r[k]!=old[k] for k in keys if k!=field):continue
            found=(raw,bit);break
        need(found is not None,'One-field byte control '+label);raw,bit=found
        try:gate_leaf(C.rows(raw,0x200004bc,decode))
        except ValueError:result.append(dict(case=label,PC=pc,field=field,bit=bit,rejected=True));continue
        raise ValueError('Accepted pre-copy operand mutation')
    raw=bytearray(item['prefix_bytes']);raw[0x1e+2]^=0x10;changed=dict(item['caller_config_record']);changed['init_prefix']=C.rows(raw,changed['slot400A4'],decode)
    try:caller_gate(changed,C)
    except ValueError:result.append(dict(case='caller expected byte255',PC=changed['slot400A4']+0x1e,field='immediate',bit=20,rejected=True))
    else:raise ValueError('Accepted caller comparison-value mutation')
    return result
def inspect(root,firmware=None,candidate_root=None):
    root=Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists():closed(HERE,sha(HERE/'seal.json'))
    C,old,_=context(root);ledger=read(HERE/'ledger.json');need(len(ledger['candidates'])==2,'Both SDK references retained')
    for item in ledger['candidates']:
        gate_leaf(item['rows']);need(hashlib.sha256(b''.join(bytes.fromhex(r['raw_hex']) for r in item['rows'])).hexdigest()==BODY,'Retained62B byte closure')
        caller_gate(next(r for r in old['candidates'] if r['candidate']==item['candidate']),C)
    need((firmware is None)==(candidate_root is None),'Use both --firmware and --candidate-root, or neither')
    result=dict(schema='TSL9-complete-precopy-leaf-review-v1',passed=True,metadata_only=firmware is None,actual_original_firmware_read=False,actual_candidate_leaf_bodies_read=0,actual_caller_prefixes_read=0,actual_existing_fill_bodies_rechecked=0,raw_controls_replayed=False,candidate_leaf_bytes=62,candidate_leaf_instructions=19,explicit_GPR_destinations=[10,13,14,15],candidate_leaf_nested_calls=0,normal_return_values=[0,1],null_or_zero_length_return=0,first_full_A1_byte_mismatch_return=0,nonnull_nonzero_all_bytes_equal_full_A1_return=1,entry_A1_truncated=False,entry_A2_truncated=False,payload_byte_writes=False,full_A1_vs_LBU_comparison_confirmed=True,conditional_local_S1_SP_and_config52_preservation_confirmed=True,installed_resident_identity_proved=False,App_branch_reachability_proved=False,callback_lifetime_or_live_zero_proved=False,full_original_ABI_proved=False,complete_initializer_continuation_proved=False,new_provider_or_BIN_generated=False,compiler_or_HOST_run=False,target_execution=False,ISA_emulation=False,network=False,hardware=False)
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Actual original official ID2966')
        app=read(case(root,'v4160-allocator-callback-2026-10-22')/'config-review/source-ledger.json')
        need(Path(firmware).read_bytes()[0x119e2:0x11b16]==bytes.fromhex(app['body_raw_hex']),'Actual original308B App configuration source agrees with sealed caller context')
        C,decode,data=inputs(root,candidate_root);negative=[]
        for actual,expected in zip(data,ledger['candidates']):
            need({k:v for k,v in actual.items() if k not in ('caller_config_record','blob','prefix_bytes')}==expected,'All actual bounded raw/source associations');negative+=controls(actual,C,decode)
        result.update(actual_original_firmware_read=True,actual_candidate_leaf_bodies_read=2,actual_caller_prefixes_read=2,actual_existing_fill_bodies_rechecked=2,raw_controls_replayed=True,raw_controls=len(negative),controls=negative)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--candidate-root',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.candidate_root)))
