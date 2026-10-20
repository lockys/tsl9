"""Inspect candidate ELF/BIN statically; never executes target instructions."""
from pathlib import Path
import argparse, hashlib, json, struct

def require(ok, why):
    if not ok:
        raise AssertionError(why)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

class ELF32:
    def __init__(self, path):
        self.raw = Path(path).read_bytes()
        b = self.raw
        require(len(b) >= 52 and b[:7] == b'\x7fELF\x01\x01\x01', 'ELF32 LE header')
        h = struct.unpack_from('<16sHHIIIIIHHHHHH', b)
        _, self.kind, self.machine, version, self.entry, phoff, shoff, self.flags, ehsize, phsize, phnum, shsize, shnum, shstr = h
        require(self.kind in (1,2) and self.machine == 243 and version == 1 and ehsize == 52, 'RISC-V ELF ABI')
        require(shsize == 40 and shnum > 0 and shstr < shnum and shoff+40*shnum <= len(b), 'Section table bounds')
        headers = [struct.unpack_from('<10I', b, shoff+40*i) for i in range(shnum)]
        def payload(s):
            require(s[4]+s[5] <= len(b), 'Section file bounds')
            return b[s[4]:s[4]+s[5]]
        def string(buf, off):
            require(off < len(buf), 'String offset')
            end = buf.find(b'\0', off)
            require(end >= 0, 'Terminated string')
            return buf[off:end].decode('utf-8')
        names = payload(headers[shstr])
        self.sections = []
        for i,s in enumerate(headers):
            if s[1] != 8:
                payload(s)
            self.sections.append(dict(index=i,name=string(names,s[0]),type=s[1],flags=s[2],va=s[3],
                                      offset=s[4],bytes=s[5],link=s[6],info=s[7],align=s[8],entsize=s[9]))
        self.names = {s['name']:s for s in self.sections}
        self.symbols = []
        for s in headers:
            if s[1] != 2:
                continue
            require(s[9] == 16 and s[5] % 16 == 0 and s[6] < shnum, 'Symbol table shape')
            strings, table = payload(headers[s[6]]), payload(s)
            for off in range(0,len(table),16):
                n,v,size,info,other,ndx = struct.unpack_from('<IIIBBH',table,off)
                self.symbols.append(dict(name=string(strings,n),value=v,bytes=size,binding=info>>4,
                                         type=info&15,visibility=other&3,index=ndx))
        require((phnum == 0 or phsize == 32) and phoff+phnum*phsize <= len(b), 'Program header bounds')
        self.segments = []
        for i in range(phnum):
            ty,off,va,pa,fs,ms,fl,al = struct.unpack_from('<8I',b,phoff+32*i)
            require(off+fs <= len(b) and fs <= ms, 'Program file/memory extent')
            self.segments.append(dict(type=ty,offset=off,va=va,pa=pa,file_bytes=fs,memory_bytes=ms,flags=fl,align=al))

    def symbol(self,name):
        rows = [s for s in self.symbols if s['name'] == name]
        require(len(rows) == 1, 'Unique symbol '+name)
        return rows[0]

    def allocated(self):
        return [s for s in self.sections if s['flags'] & 2 and s['bytes']]

def audit(receipt):
    receipt = Path(receipt).resolve()
    p = read(receipt)
    require(p['schema'] == 'CH32V208-conditional-candidate-producer-v1' and
            p['compile_exit'] == p['link_exit'] == p['objcopy_exit'] == 0, 'Real native tools succeeded')
    for name,digest in p['sources'].items():
        require(sha(name) == digest, 'Candidate build source identity')
    for name,row in p['outputs'].items():
        require(Path(row['path']).stat().st_size == row['bytes'] and sha(row['path']) == row['sha256'], 'Output identity '+name)
    require(sha(p['plan']) == p['plan_sha256'], 'Actual plan identity')
    plan = read(p['plan'])
    original = Path(plan['runtime']['path']).read_bytes()
    require(len(original) == 76800 and hashlib.sha256(original).hexdigest() == plan['runtime']['sha256'], 'Original carrier identity')
    for n,digest in plan['generated_sha256'].items():
        require(sha(receipt.parent/n) == digest, 'Generated source/layout identity')
    for name in ('compiler','linker','objcopy'):
        require(sha(plan[name]) == plan['tool_sha256'][name], 'Native tool identity '+name)
    old = plan['retained_producer']
    require(sha(old['path']) == old['sha256'] and sha(old['audit']) == old['audit_sha256'] and
            sha(old['strict_log']) == old['strict_log_sha256'] and old['strict_exit'] != 0,
            'Old strict failure preserved')
    oldp = read(old['path'])
    for name,digest in oldp['sources'].items():
        require(sha(name) == digest, 'Core source still matches native producer')
    baseline = read(oldp['baseline_receipt'])
    require(sha(oldp['baseline_receipt']) == oldp['baseline_receipt_sha256'], 'Baseline receipt identity')
    for name,digest in baseline['source_sha256'].items():
        require(sha(name) == digest, 'Retained legacy source unchanged')
    require(sha(plan['core_object']['path']) == plan['core_object']['sha256'], 'Core object identity')
    elf = ELF32(p['outputs']['tsl9-ch32v208-candidate.elf']['path'])
    require(elf.kind == 2 and elf.entry == 0x8000, 'ET_EXEC with candidate Runtime entry')
    require(not any(s['index'] == 0 and s['name'] and s['binding'] in (1,2) for s in elf.symbols), 'Strict: no remaining UND')
    require(not any(s['type'] in (4,9) and s['bytes'] for s in elf.sections), 'No unapplied runtime relocations')
    expected = {s['section']:s for s in plan['mapped_sections']+plan['carrier_gaps']}
    expected[plan['ram']['section']] = plan['ram']
    require(set(expected) == {s['name'] for s in elf.allocated()}, 'Exact allocated section set')
    flash = []
    for section in elf.allocated():
        e = expected[section['name']]
        require(section['va'] == e['va'] and section['bytes'] == e['bytes'], 'Fixed original VMA and section size')
        if section['name'] == plan['ram']['section']:
            require(section['type'] == 8 and section['flags'] == 3, 'RAM is writable NOBITS, not BIN bytes')
        else:
            require(section['type'] == 1, 'Flash section has real bytes')
            flash.append(section)
    previous = 0x8000
    for s in sorted(flash,key=lambda s:s['va']):
        require(s['va'] == previous, 'No implicit Flash gap fill or overlap')
        previous += s['bytes']
        raw = elf.raw[s['offset']:s['offset']+s['bytes']]
        expected_raw = original[s['va']-0x8000:s['va']-0x8000+s['bytes']]
        if raw != expected_raw:
            positions = [s['va']+i for i,(a,b) in enumerate(zip(raw,expected_raw)) if a != b]
            raise AssertionError('Final linked bytes differ: '+s['name']+' count='+str(len(positions))+' first_VAs='+str(positions[:12]))
    require(previous == 0x1ac00, 'Exact candidate Runtime endpoint; no missing-tail padding')
    loads = [s for s in elf.segments if s['type'] == 1]
    # LLD emits a standard non-load RISC-V attributes program header. It must
    # describe only the non-allocated ABI metadata, never extra Runtime bytes.
    metadata = [s for s in elf.segments if s['type'] != 1]
    attr = elf.names['.riscv.attributes']
    require(len(loads) == 2 and len(metadata) == 1, 'Only Flash/RAM loads and one ABI metadata header')
    a = metadata[0]
    require(a['type'] == 0x70000003 and a['offset'] == attr['offset'] and
            a['file_bytes'] == a['memory_bytes'] == attr['bytes'] and
            a['va'] == a['pa'] == 0 and a['flags'] == 4 and a['align'] == 1 and
            attr['flags'] == 0, 'Non-load RISC-V attributes metadata only')
    f = next(s for s in loads if s['va'] == 0x8000)
    r = next(s for s in loads if s['va'] == 0x20004000)
    require(f['pa'] == 0x8000 and f['file_bytes'] == f['memory_bytes'] == 76800 and f['flags'] == 5,
            'Candidate Flash LMA/VMA and file extent')
    require(r['pa'] == 0x20004000 and r['file_bytes'] == 0 and r['memory_bytes'] == 35152 and r['flags'] == 6,
            'RAM LOAD is memory-only')
    for row in plan['external_address_assumptions']:
        s = elf.symbol(row['name'])
        require(s['value'] == row['value'] and s['bytes'] == 0 and s['type'] == 0 and s['index'] == 0xfff1,
                'Explicit external address-only symbol')
    require(elf.symbol('__tsl9_data_load')['value'] == 0x1a7e0 and
            elf.symbol('__tsl9_data_start')['value'] == 0x20004000 and
            elf.symbol('__tsl9_bss_end')['value'] == 0x2000c950 and
            elf.symbol('__tsl9_stack_top')['value'] == 0x20010000, 'Original initializer and numeric reset expectations')
    binary = Path(p['outputs']['tsl9-ch32v208-candidate.bin']['path'])
    require(binary.read_bytes() == original, 'Final objcopy BIN byte-exact with retained Runtime')
    return dict(schema='CH32V208-conditional-candidate-audit-v1', passed=True, mode=plan['mode'],
        elf_type='ET_EXEC', machine='RISC-V', entry=elf.entry, flash_base=0x8000, bytes=76800,
        sha256=sha(binary), mapped_C_Cpp_code_bytes=71762, mapped_C_Cpp_RO_bytes=4685,
        retained_unreconstructed_carrier_bytes=353, carrier_ranges=25, source_external_bytes_supplied=0,
        allocated_sections=len(elf.allocated()), flash_sections=len(flash), unapplied_relocations=0, undefined_symbols=0,
        address_assumptions=plan['external_address_assumptions'], byte_exact_original_Runtime=True,
        physical_ROM_or_full_table_provider_proved=False, physical_layout_proved=False,
        original_strict_failure_preserved=True, target_ready=False, ota_verified=False, goal_complete=False,
        target_executed=False, emulation=False, hardware=False, network=False)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--receipt',required=True); a=p.parse_args()
    print(json.dumps(audit(a.receipt),separators=(',',':')))
