"""Static source fields for original188E2 and its sole small nested19160 leaf. No execution."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FW = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PRIOR = '90d8fc14891295af29fb0821b503a97b72f9df217431394e3dd1344fa95e04af'
RANGES = {
    'entry_188e2': (0x188e2, 0x1892e, 25, '0149a0ddbea9fe8921c3b187b9af3ecf7c58bc88a5fa0eab292654a1bc625fe2'),
    'leaf_19160': (0x19160, 0x1917e, 12, 'a5541a42d8ec2844fcd1d2df5492c90e2b140ce22ae79b02f50e330277c31b60'),
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def need(ok, msg):
    if not ok: raise ValueError(msg)
def case(root, name):
    return next(p for p in (root/'analysis'/name, root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def closed(folder, pin):
    need(sha(folder/'seal.json') == pin, 'Exact previous source seal')
    for n, h in read(folder/'seal.json')['members'].items():
        need(sha(folder/n) == (h if isinstance(h, str) else h['sha256']), 'Closed source member '+n)
def context(root):
    old = case(root, 'v4160-resident-native-2026-10-22')/'callback-review'
    closed(old, PRIOR)
    spec = importlib.util.spec_from_file_location('adc_previous_original_source', old/'check.py')
    previous = importlib.util.module_from_spec(spec); spec.loader.exec_module(previous)
    C, decode, E, _, _ = previous.context(root)
    return previous, C, decode, E, old
def exact(rows, pc, **fields):
    row = rows[pc]
    need(all(row[k] == v for k, v in fields.items()), 'Source operand '+hex(pc)+' '+str(fields))
def gate(groups):
    a = {x['PC']: x for x in groups['entry_188e2']}
    z = {x['PC']: x for x in groups['leaf_19160']}
    exact(a, 0x188e2, op='addi', rd=2, rs1=2, immediate=-16)
    exact(a, 0x188e4, op='lui', rd=15, immediate=0x40012000)
    exact(a, 0x188e8, op='sw', rs1=2, rs2=1, immediate=12, memory_width=32)
    exact(a, 0x188ea, op='addi', rd=15, rs1=15, immediate=0x400)
    exact(a, 0x188ee, op='bne', rs1=10, rs2=15, target=0x1890a)
    for pc, value in ((0x188f2, 1), (0x188fc, 0), (0x18916, 1), (0x18920, 0)):
        exact(a, pc, op='addi', rd=11, rs1=0, immediate=value)
    for pc, mask in ((0x188f4, 0x200), (0x188fe, 0x200), (0x18918, 0x400), (0x18922, 0x400)):
        exact(a, pc, op='addi', rd=10, rs1=0, immediate=mask)
    for pc in (0x188f8, 0x1891c): exact(a, pc, op='jal', rd=1, target=0x19160)
    exact(a, 0x18902, op='lw', rd=1, rs1=2, immediate=12, memory_width=32)
    exact(a, 0x18904, op='addi', rd=2, rs1=2, immediate=16)
    exact(a, 0x18906, op='jal', rd=0, target=0x19160)
    exact(a, 0x1890a, op='lui', rd=15, immediate=0x40013000)
    exact(a, 0x1890e, op='addi', rd=15, rs1=15, immediate=-0x800)
    exact(a, 0x18912, op='bne', rs1=10, rs2=15, target=0x18928)
    exact(a, 0x18926, op='jal', rd=0, target=0x18902)
    exact(a, 0x18928, op='lw', rd=1, rs1=2, immediate=12, memory_width=32)
    exact(a, 0x1892a, op='addi', rd=2, rs1=2, immediate=16)
    exact(a, 0x1892c, op='jalr', rd=0, rs1=1, immediate=0)
    exact(z, 0x19160, op='beq', rs1=11, rs2=0, target=0x1916e)
    for pc, rd in ((0x19162, 14), (0x1916e, 15)):
        exact(z, pc, op='lui', rd=rd, immediate=0x40021000)
    for pc, rd, base in ((0x19166, 15, 14), (0x19172, 14, 15)):
        exact(z, pc, op='lw', rd=rd, rs1=base, immediate=12, memory_width=32)
    exact(z, 0x19168, op='or', rd=10, rs1=10, rs2=15)
    exact(z, 0x19174, op='xori', rd=10, rs1=10, immediate=-1)
    exact(z, 0x19178, op='and', rd=10, rs1=10, rs2=14)
    for pc, base in ((0x1916a, 14), (0x1917a, 15)):
        exact(z, pc, op='sw', rs1=base, rs2=10, immediate=12, memory_width=32)
    for pc in (0x1916c, 0x1917c): exact(z, pc, op='jalr', rd=0, rs1=1, immediate=0)
    protected = (3, 4, 8, 9, *range(18, 28))
    need(not any(x['rd'] in protected for group in groups.values() for x in group), 'No own S/GP/TP writes')
    need(not any(x['rd'] in (1, 2) or x['op']=='jal' or x['op']=='jalr' and x['rd'] != 0 for x in groups['leaf_19160']), 'Leaf no frame, RA write, or nested call')
    need([(x['PC'], x['rs1'], x['immediate']) for x in groups['entry_188e2'] if x['op']=='sw'] == [(0x188e8, 2, 12)], 'Only own store is saved RA')
    return dict(entry_range=[0x188e2, 0x1892e], entry_bytes=76, entry_rows=25,
        nested_range=[0x19160, 0x1917e], nested_bytes=30, nested_rows=12,
        no_encoded_loop=True, frame_bytes=16, saved_RA_offset=12,
        direct_call_sites=[0x188f8, 0x1891c], tail_dependency_site=0x18906,
        only_external_target=0x19160, own_S_GP_TP_writes=False,
        caller_constant=0x40012400, caller_mask=0x200,
        other_accepted_base=0x40012800, other_mask=0x400,
        two_fresh_read_modify_write_address=0x4002100c,
        first_effect='READ32|mask; WRITE32', second_effect='READ32&~mask; WRITE32',
        physical_peripheral_identity_proved=False, unconditional_hardware_reset_proved=False,
        whole_callback_preservation_proved=False, config_word52_lifetime_proved=False,
        next_unreviewed_call_site=0x19896, next_unreviewed_target=0x1892e)
def controls(blobs, groups, C, decode):
    out = []
    for key, pc, field in [('entry_188e2',0x188ee,'target'),('entry_188e2',0x188f4,'immediate'),('entry_188e2',0x18904,'immediate'),('leaf_19160',0x19166,'immediate'),('leaf_19160',0x1917a,'rs2')]:
        a = RANGES[key][0]; old = next(x for x in groups[key] if x['PC']==pc); found = None
        for bit in range(old['bytes']*8):
            raw = bytearray(blobs[key]); raw[pc-a+bit//8] ^= 1 << (bit%8)
            try: row = decode(raw[pc-a:], pc)
            except ValueError: continue
            keys = ('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if row[field] == old[field] or any(row[k] != old[k] for k in keys if k != field): continue
            found = raw, bit, row; break
        need(found is not None, 'Single-field byte control')
        raw, bit, row = found; changed = dict(groups); changed[key] = C.rows(raw, a, decode)
        try: gate(changed)
        except ValueError:
            out.append(dict(PC=pc, field=field, bit=bit, original=old[field], mutated=row[field], raw_hex=row['raw_hex'], rejected=True)); continue
        raise ValueError('Accepted incorrect ADC dependency operand')
    return out
def inspect(root, firmware=None, image_elf=None):
    root = Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists(): closed(HERE, sha(HERE/'seal.json'))
    previous, C, decode, E, old = context(root); ledger = read(HERE/'ledger.json'); groups = ledger['groups']
    blobs = {}
    for key, (a,z,n,pin) in RANGES.items():
        blob = b''.join(bytes.fromhex(x['raw_hex']) for x in groups[key]); blobs[key] = blob
        need(len(blob)==z-a and len(groups[key])==n and hashlib.sha256(blob).hexdigest()==pin, 'Pinned source range '+key)
        need(C.rows(blob,a,decode)==groups[key], 'All metadata raw fields '+key)
    facts = gate(groups)
    caller = read(old/'ledger.json')['groups']['callback']; idx = {x['PC']:x for x in caller}
    exact(idx, 0x19824, op='lui', rd=15, immediate=0x40012000)
    exact(idx, 0x19828, op='addi', rd=9, rs1=15, immediate=0x400)
    exact(idx, 0x19878, op='mv', rd=10, rs1=9)
    exact(idx, 0x1987a, op='jal', rd=1, target=0x188e2)
    need(not any(x['rd']==9 for x in caller if 0x1982c<=x['PC']<0x1987a), 'Caller own S1 remains')
    need(previous.gate(read(old/'ledger.json')['groups'])['first_unreviewed_dependency_target']==0x188e2, 'Previous frontier unchanged')
    result = dict(schema='TSL9-original-ADC-dependency-v1', passed=True, metadata_only=firmware is None,
        actual_original_firmware_read=False, actual_optional_ELF_read=False, raw_controls_replayed=False,
        facts=facts, normal_return_conditions=['valid nonaliasing16B stack frame','normal fresh MMIO accesses','no asynchronous register/stack changes','intact code'],
        full_original_ABI_proved=False, whole_OTA_proved=False, installed_identity_proved=False,
        new_BIN_generated=False, compiler_or_HOST_run=False, target_execution=False, ISA_emulation=False, network=False, hardware=False)
    need(image_elf is None or firmware is not None, 'Optional ELF requires explicit actual firmware')
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800, 'Actual official ID2966')
        raw = Path(firmware).read_bytes()
        for key,(a,z,_,_) in RANGES.items(): need(raw[a-0x8000:z-0x8000]==blobs[key], 'Actual complete source bytes '+key)
        need(C.rows(raw[0x117f0:0x1195c],0x197f0,decode)==caller, 'Actual caller source and preserved prior proofs')
        nextrow = decode(raw[0x1092e:], 0x1892e)
        need((nextrow['op'],nextrow['rd'],nextrow['rs1'],nextrow['immediate'])==('lw',15,10,4), 'Next entry read distinct from completed CFG')
        negative = controls(blobs,groups,C,decode)
        result.update(actual_original_firmware_read=True, actual_source_bytes=106, actual_source_rows=37,
            caller_bytes_reread=364, raw_controls_replayed=True, raw_controls=len(negative), controls=negative)
        if image_elf is not None:
            e = E(Path(image_elf).resolve(strict=True)); need(e.kind==2,'Actual ELF32 executable')
            for key,(a,z,_,_) in RANGES.items():
                owners=[s for s in e.sections if s['flags']&6==6 and s['address']<=a and z<=s['address']+s['size']]
                need(len(owners)==1,'Unique executable source owner '+key); owner=owners[0]; at=a-owner['address']
                need(e.data(owner)[at:at+z-a]==blobs[key],'Only requested source byte subset '+key)
                if key=='entry_188e2':
                    need(any(s['name']=='__tsl9v4160_conditional_code_188e2' and s['value']==a and s['size']==0 and s['info']&15==0 for s in e.symbols),'Conditional NOTYPE size0 entry, no function-size claim')
            result.update(actual_optional_ELF_read=True,actual_optional_ELF_sha256=sha(image_elf),whole_ELF_provenance_proved=False)
    return result
if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--firmware',type=Path); p.add_argument('--image-elf',type=Path); a=p.parse_args()
    print(json.dumps(inspect(a.project_root,a.firmware,a.image_elf)))
