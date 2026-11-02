#!/usr/bin/env python3
"""Test source-carried opaque sections in the conditional original-address link."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = '28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89'
p = argparse.ArgumentParser()
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
def tool(name):
    exe = a.tool_dir / (name + '.exe')
    result = exe if exe.is_file() else a.tool_dir / name
    if not result.is_file(): raise ValueError('LLVM tool missing: ' + name)
    return str(result)
def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Command failed: ' + result.stderr[:1000])
    return result.stdout
payload = json.loads((ROOT/'src/native/tx_candidate/full-image-payload.json').read_text(encoding='utf-8'))
items = payload['ranges']
if payload['schema'] != 'tsl9-v4160-opaque-payload-v1' or [(x['start'], x['end']) for x in items] != [(0x14056,0x14c8a),(0x1a69c,0x1a6a0)]:
    raise ValueError('Unexpected source payload range')
raw = [bytes.fromhex(x['hex']) for x in items]
if any(len(b) != i['end'] - i['start'] or hashlib.sha256(b).hexdigest() != i['sha256'] for b,i in zip(raw,items)):
    raise ValueError('Payload mismatch')
reader = runpy.run_path(str(ROOT/'src/native/tx_candidate/postpass/elf32.py'))['ELF']
out.mkdir(parents=True)
base = out/'ram'
facts = json.loads(run([sys.executable,'-B',str(ROOT/'scripts/verify-conditional-tx-storage.py'),'--tool-dir',str(a.tool_dir),'--out',str(base)]))
if not facts['passed'] or facts['ram_ownership_proved'] or facts['flashable']:
    raise ValueError('Unexpected conditional RAM baseline')
parts = [('.tsl9_full_code','ax','tsl9_incoming_external_14056',raw[0]),
         ('.tsl9_full_defaults','a','tsl9_settings_default_data_1a69c',raw[1])]
asm = []
for section,flags,name,data in parts:
    asm += ['.section '+section+',"' +flags+ '",@progbits', '.globl '+name, name+':']
    asm += ['.byte '+','.join(str(x) for x in data[i:i+32]) for i in range(0,len(data),32)]
    asm += ['.size '+name+', .-'+name]
source = out/'opaque-provider.s'
source.write_text('\n'.join(asm)+'\n',encoding='ascii')
aliases={'tsl9_input_state_decoders_static_data_1ab48':('tsl9_input_counter_read_window_1ab48',0,0x1ab48),
         'tsl9_record_field_transitions_static_data_1a078':('tsl9_grid_read_data_pool_19ed8',416,0x1a078),
         'tsl9_registered_callbacks_static_data_1a638':('tsl9_sequence_compare_read_window_1a638',0,0x1a638)}
results=[]
for mode in ('c','cpp'):
    folder=base/mode
    obj=out/('opaque-provider-'+mode+'.o')
    run([tool('clang'),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-c',str(source),'-o',str(obj)])
    local=reader(obj)
    if any(local.data(local.byname[section])!=data for section,_,_,data in parts):
        raise ValueError('Opaque object differs')
    layout=(folder/'conditional.ld').read_text(encoding='utf-8')
    insert=(' .payload_code 0x14056 : SUBALIGN(1) { KEEP(*(.tsl9_full_code)) } :NONE\n'
            ' .payload_defaults 0x1a69c : SUBALIGN(1) { KEEP(*(.tsl9_full_defaults)) } :NONE\n')
    if layout.count('SECTIONS {\n')!=1: raise ValueError('Unexpected layout')
    ldfile=out/('conditional-full-'+mode+'.ld')
    ldfile.write_text(layout.replace('SECTIONS {\n','SECTIONS {\n'+insert),encoding='utf-8')
    aggregate=base/'base/source'/('NOT-FLASHABLE-candidate-aliases-'+mode+'.o')
    flags=['--defsym='+n+'='+t+('+'+str(offset) if offset else '') for n,(t,offset,_) in aliases.items()]
    cmd=[tool('ld.lld'),'--no-undefined','--no-relax','-T',str(ldfile),str(aggregate),
         str(folder/'conditional-storage.o'),str(obj),*flags]
    strict=subprocess.run([*cmd,'-o',str(out/('STRICT-'+mode+'.elf'))],capture_output=True,text=True)
    missing=set(re.findall(r'undefined symbol: ([^\r\n]+)',strict.stderr))
    if strict.returncode==0 or missing!={'tsl9_boot_resident_40000'}:
        raise ValueError('Expected only resident ROM unresolved: '+str(sorted(missing)))
    for omitted in range(2):
        section,section_flags,name,data=parts[1-omitted]
        negative=['.section '+section+',"' +section_flags+ '",@progbits', '.globl '+name, name+':']
        negative += ['.byte '+','.join(str(x) for x in data[i:i+32]) for i in range(0,len(data),32)]
        negative += ['.size '+name+', .-'+name]
        negsrc=out/('negative-'+mode+'-'+str(omitted)+'.s')
        negsrc.write_text('\n'.join(negative)+'\n',encoding='ascii')
        negobj=out/('negative-'+mode+'-'+str(omitted)+'.o')
        run([tool('clang'),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-c',str(negsrc),'-o',str(negobj)])
        negcmd=[tool('ld.lld'),'--no-undefined','--no-relax','-T',str(ldfile),str(aggregate),
                str(folder/'conditional-storage.o'),str(negobj),*flags,
                '--defsym=tsl9_boot_resident_40000=0x40000','-o',str(out/('NEGATIVE-'+mode+'-'+str(omitted)+'.elf'))]
        neg=subprocess.run(negcmd,capture_output=True,text=True)
        negmissing=set(re.findall(r'undefined symbol: ([^\r\n]+)',neg.stderr))
        if neg.returncode==0 or negmissing!={parts[omitted][2]}:
            raise ValueError('Missing-section negative control failed')
    dest=out/('NOT-FLASHABLE-conditional-full-'+mode+'.elf')
    run([*cmd,'--defsym=tsl9_boot_resident_40000=0x40000','-o',str(dest)])
    elf=reader(dest); symbols={x['name']:x for x in elf.symbols if x['name']}
    for section,_,name,data in parts:
        owner=elf.byname['.payload_code' if section=='.tsl9_full_code' else '.payload_defaults']
        sym=symbols[name]
        if sym['index']!=owner['index'] or sym['value']!=owner['address'] or sym['size']!=len(data) or elf.data(owner)!=data:
            raise ValueError('Payload symbol lacks actual section backing')
    for name,(target,offset,address) in aliases.items():
        x,y=symbols[name],symbols[target]
        if x['index'] in (0,0xfff1) or x['index']!=y['index'] or x['value']!=y['value']+offset or x['value']!=address:
            raise ValueError('Conditional alias missing section backing')
    flash=sorted((s for s in elf.sections if s['flags']&2 and s['size'] and s['type']!=8),key=lambda s:s['address'])
    pos=0x8000; image=bytearray()
    for section in flash:
        if section['address']!=pos: raise ValueError('Image has gap or overlap')
        data=elf.data(section); image.extend(data);pos+=len(data)
    if pos!=0x1ac00 or len(image)!=76800 or hashlib.sha256(image).hexdigest()!=EXPECTED:
        raise ValueError('Full image differs from candidate')
    phoff=struct.unpack_from('<I',elf.raw,28)[0];phsize,phcount=struct.unpack_from('<HH',elf.raw,42)
    if any(struct.unpack_from('<I',elf.raw,phoff+i*phsize)[0]==1 for i in range(phcount)):
        raise ValueError('Diagnostic ELF unexpectedly loadable')
    binary=out/('NOT-FLASH-VALIDATED-conditional-link-'+mode+'.bin')
    binary.write_bytes(image)
    results.append({'mode':mode,'strict_undefined':['tsl9_boot_resident_40000'],
                    'section_backed_new_symbols':2,'negative_section_controls':2,
                    'conditional_data_aliases':3,'image_bytes':len(image)})
print(json.dumps({'passed':True,'results':results,'opaque_original_bytes':3128,
                  'original_semantics_recovered':False,'global_index_bounds_proved':False,
                  'ram_ownership_proved':False,'installed_rom_proved':False,'diagnostic_pt_load':0,
                  'target_executed':False,'hardware_validated':False,'flashable':False}))
