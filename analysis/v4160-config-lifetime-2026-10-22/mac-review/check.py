"""Original six-byte helper footprint and caller continuation; pure static operands."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ALLOC='e039ece24d70ee9c3b78a64d6d3b58b052ed3e08161a70aa89bd20ef9089999e'
CONFIG='dcb6a0e3aa98e46d26cfccbb965427ac80894b511a256e35758982e50a3db23d'
HELPER='5ea71cc5060b528919272111556388a084fe65e49474efa62683825e4df2eedf'
CALLER='747ccb507745f07b46289b7fb200480c46f79ff63e399ce44e72042ac4ca421c'
RANGES={'helper':(0x18f56,0x18f88),'caller':(0x19aac,0x19aee)}
def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def case(root,name):return next(p for p in (root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def closed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact sealed evidence dependency')
    for n,h in read(folder/'seal.json')['members'].items():need(sha(folder/n)==(h if isinstance(h,str) else h['sha256']),'Immutable evidence '+n)
def context(root):
    folder=case(root,'v4160-ota-source-wiring-2026-10-22')/'allocator-review';closed(folder,ALLOC)
    closed(case(root,'v4160-allocator-callback-2026-10-22')/'config-review',CONFIG)
    spec=importlib.util.spec_from_file_location('mac_prior_allocator',folder/'check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    R,_,_=m.references(root);_,E,_=R.context(root);return m.decoder(root),E
def rows(data,start,decode):
    out=[];offset=0
    while offset<len(data):
        r=decode(data[offset:],start+offset);need(offset+r['bytes']<=len(data),'Whole static source row');out.append(r);offset+=r['bytes']
    return out
def gate(groups):
    helper=groups['helper'];caller=groups['caller'];h={r['PC']:r for r in helper};c={r['PC']:r for r in caller}
    def exact(index,pc,**fields):need(all(index[pc][k]==v for k,v in fields.items()),'Original helper/caller field '+hex(pc))
    need(len(helper)==14 and sum(r['bytes'] for r in helper)==50,'Complete50B helper')
    exact(h,0x18f56,op='lui',rd=14,immediate=0x1ffff000)
    exact(h,0x18f5a,op='lw',rd=15,rs1=14,immediate=0x7e8,memory_width=32)
    exact(h,0x18f78,op='lw',rd=15,rs1=14,immediate=0x7ec,memory_width=32)
    expected=[(0x18f62,15,0),(0x18f66,13,1),(0x18f70,13,2),(0x18f74,15,3),(0x18f7c,15,4),(0x18f82,15,5)]
    need([(r['PC'],r['rs2'],r['immediate']) for r in helper if r['op']=='sb']==expected,'Exactly six ordered destination bytes')
    need(all(r['rs1']==10 and r['memory_width']==8 for r in helper if r['op']=='sb'),'All writes use unchanged fullA0 base and byte width')
    need([r['op'] for r in helper if r['memory_width'] is not None]==['lw','sb','sb','sb','sb','lw','sb','sb'],'First source word then four bytes, fresh second source then two bytes')
    for pc,rd,rs1,shift in [(0x18f5e,13,15,8),(0x18f6a,13,15,16),(0x18f6e,15,15,24),(0x18f80,15,15,8)]:exact(h,pc,op='srli',rd=rd,rs1=rs1,immediate=shift)
    exact(h,0x18f86,op='jalr',rd=0,rs1=1,immediate=0)
    need({r['rd'] for r in helper if r['rd'] not in (None,0)}=={13,14,15},'Only A3/A4/A5 explicitly written; no SP/S/GP/A0/RA writes')
    need(not any(r['target'] is not None or r['op']=='jal' or r['op']=='jalr' and r['rd']==1 for r in helper),'No internal branches/nested call/opaque callee')
    need(len(caller)==24 and sum(r['bytes'] for r in caller)==66,'Bounded caller continuation66B')
    exact(c,0x19aac,op='addi',rd=10,rs1=2,immediate=8)
    exact(c,0x19ab4,op='jal',rd=1,target=0x18f56)
    exact(c,0x19ab8,op='addi',rd=14,rs1=2,immediate=16)
    exact(c,0x19aba,op='addi',rd=15,rs1=0,immediate=0);exact(c,0x19abc,op='addi',rd=13,rs1=0,immediate=6)
    exact(c,0x19abe,op='addi',rd=12,rs1=2,immediate=8);exact(c,0x19ac0,op='add',rd=12,rs1=12,rs2=15)
    exact(c,0x19ac2,op='lbu',rd=12,rs1=12,immediate=0,memory_width=8)
    exact(c,0x19ac6,op='addi',rd=15,rs1=15,immediate=1);exact(c,0x19ac8,op='addi',rd=14,rs1=14,immediate=1)
    exact(c,0x19aca,op='sb',rs1=14,rs2=12,immediate=23,memory_width=8)
    exact(c,0x19ace,op='bne',rs1=15,rs2=13,target=0x19abe)
    need([(r['PC'],r['op'],r['rs1'],r['rs2'],r['immediate'],r['memory_width']) for r in caller if r['op'] in ('sb','sh','sw')]==[(0x19aae,'sh',2,14,48,16),(0x19ab2,'sw',2,15,64,32),(0x19aca,'sb',14,12,23,8)],'All stores in the66B caller slice; SP48..49/SP64..67 and six config bytes only')
    exact(c,0x19ae0,op='jal',rd=0,target=0x19ae0)
    exact(c,0x19ae2,op='lui',rd=15,immediate=0x40000);exact(c,0x19ae6,op='lw',rd=15,rs1=15,immediate=0xa4,memory_width=32)
    exact(c,0x19aea,op='addi',rd=10,rs1=2,immediate=16);exact(c,0x19aec,op='jalr',rd=1,rs1=15,immediate=0)
    need(not any(r['rd'] in (2,3,8,9,18,19,20,21,22,23,24,25,26,27) for r in caller),'No caller SP/GP/S writes in this bounded continuation')
    need([(r['PC'],r['op']) for r in caller if r['op']=='jal' and r['rd']==1 or r['op']=='jalr' and r['rd']==1]==[(0x19ab4,'jal'),(0x19aec,'jalr')],'No intervening opaque call before BLE-init boundary')
    # Closed-form address arithmetic from the verified six-iteration loop.
    helper_offsets=list(range(8,14));copy_offsets=[16+(i+1)+23 for i in range(6)]
    need(copy_offsets==list(range(40,46)) and not(set(helper_offsets+copy_offsets)&set(range(68,72))),'Numeric byte footprints disjoint from config+52/SP68..71')
    return dict(helper_bytes=50,helper_instructions=14,helper_explicit_GPR_writes=[13,14,15],nested_calls=0,helper_destination_byte_offsets=[0,5],caller_helper_write_SP_offsets=[8,13],caller_copy_write_SP_offsets=[40,45],caller_other_store_SP_byte_ranges=[[48,49],[64,67]],config_MAC_field_byte_offsets=[24,29],staCB_SP_byte_offsets=[68,71],helper_or_copy_explicitly_writes_staCB=False,entire_caller_slice_explicitly_writes_staCB=False,helper_explicitly_writes_SP_or_S0=False,raw_return_link=0x19ab8,prior_opaque_call_effects_resolved=False)
def controls(raw,start,decode,groups,key,selections):
    out=[];index={r['PC']:r for r in groups[key]}
    for pc,field,label in selections:
        before=index[pc];found=None
        for bit in range(before['bytes']*8):
            data=bytearray(raw);data[pc-start+bit//8]^=1<<(bit%8)
            try:after=decode(data[pc-start:],pc)
            except ValueError:continue
            fields=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if after[field]==before[field] or any(after[k]!=before[k] for k in fields if k!=field):continue
            found=(data,after,bit);break
        need(found is not None,'Actual field countercase '+label);data,after,bit=found;mutated=dict(groups);mutated[key]=rows(data,start,decode)
        try:gate(mutated)
        except ValueError:out.append(dict(case=label,PC=pc,field=field,bit=bit,rejected=True));continue
        raise ValueError('Accepted footprint/control mutation')
    return out
def inspect(root,firmware=None,image_elf=None):
    root=Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists():closed(HERE,sha(HERE/'seal.json'))
    old=case(root,'v4160-ota-source-wiring-2026-10-22')/'allocator-review';closed(old,ALLOC);closed(case(root,'v4160-allocator-callback-2026-10-22')/'config-review',CONFIG)
    ledger=read(HERE/'ledger.json');groups=ledger['groups'];facts=gate(groups)
    for key,pin in [('helper',HELPER),('caller',CALLER)]:need(hashlib.sha256(b''.join(bytes.fromhex(r['raw_hex']) for r in groups[key])).hexdigest()==pin,'Retained bounded byte closure')
    need(image_elf is None or firmware is not None,'ELF view requires explicit firmware')
    result=dict(schema='TSL9-six-byte-helper-footprint-v1',passed=True,metadata_only=firmware is None,actual_original_firmware_read=False,actual_helper_ELF_view_read=False,raw_controls_replayed=False,facts=facts,helper_local_footprint_obligation_resolved=True,whole_config_zero_lifetime_proved=False,earlier_resident_callee_effects_proved=False,hardware_MAC_or_UID_value_read=False,whole_ELF_provenance_replayed=False,full_original_ABI_proved=False,whole_OTA_proved=False,new_BIN_generated=False,compiler_or_HOST_run=False,target_execution=False,ISA_emulation=False,hardware=False,network=False)
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Actual official ID2966');data=Path(firmware).read_bytes();decode,E=context(root);negative=[]
        for key,(a,z) in RANGES.items():need(rows(data[a-0x8000:z-0x8000],a,decode)==groups[key],'All actual bounded raw fields '+key)
        negative+=controls(data[0x10f56:0x10f88],0x18f56,decode,groups,'helper',[(0x18f82,'immediate','sixth byte destination'),(0x18f86,'rs1','raw RA return')])
        negative+=controls(data[0x11aac:0x11aee],0x19aac,decode,groups,'caller',[(0x19aac,'immediate','caller SP+8 pointer'),(0x19aca,'immediate','config+24 destination')])
        result.update(actual_original_firmware_read=True,raw_controls_replayed=True,raw_controls=len(negative),controls=negative)
        if image_elf is not None:
            e=E(Path(image_elf).resolve(strict=True));owner=e.byname[ledger['helper_ELF_role']['owner']['name']];role={k:owner[k] for k in ('name','type','flags','address','size','alignment')}
            symbols=[{k:s[k] for k in ('name','value','size','info','other')} for s in e.symbols if s['name']=='__tsl9v4160_call_18f56']
            need(e.kind==2 and role==ledger['helper_ELF_role']['owner'] and symbols==ledger['helper_ELF_role']['canonical_symbols'] and e.data(owner)==data[0x10f56:0x10f88],'Actual helper-only ELF bytes/role/extent, not whole build provenance')
            result.update(actual_helper_ELF_view_read=True,actual_helper_ELF_sha256=sha(image_elf))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--image-elf',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.image_elf)))
