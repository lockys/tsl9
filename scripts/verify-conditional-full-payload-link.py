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
fragment_tools=runpy.run_path(str(ROOT/'scripts/source-ota-epilogue.py'))
compile_epilogue,compile_entry,compile_more,compile_ae,compile_ad,compile_dispatch,compile_dispatch2,compile_dispatch3,compile_dispatch4,compile_dispatch5,compile_dispatch6=fragment_tools['compile_fragment'],fragment_tools['compile_entry'],fragment_tools['compile_more'],fragment_tools['compile_ae'],fragment_tools['compile_ad'],fragment_tools['compile_dispatch'],fragment_tools['compile_dispatch2'],fragment_tools['compile_dispatch3'],fragment_tools['compile_dispatch4'],fragment_tools['compile_dispatch5'],fragment_tools['compile_dispatch6']
aliases={'tsl9_input_state_decoders_static_data_1ab48':('tsl9_input_counter_read_window_1ab48',0,0x1ab48),
         'tsl9_record_field_transitions_static_data_1a078':('tsl9_grid_read_data_pool_19ed8',416,0x1a078),
         'tsl9_registered_callbacks_static_data_1a638':('tsl9_sequence_compare_read_window_1a638',0,0x1a638)}
results=[]
for mode in ('c','cpp'):
    folder=base/mode
    epilogue=compile_epilogue(a.tool_dir,out,mode,reader)
    entry=compile_entry(a.tool_dir,out,mode,reader)
    more=compile_more(a.tool_dir,out,mode,reader)
    ae=compile_ae(a.tool_dir,out,mode,reader)
    ad=compile_ad(a.tool_dir,out,mode,reader)
    dispatch=compile_dispatch(a.tool_dir,out,mode,reader)
    dispatch2=compile_dispatch2(a.tool_dir,out,mode,reader)
    dispatch3=compile_dispatch3(a.tool_dir,out,mode,reader)
    dispatch4=compile_dispatch4(a.tool_dir,out,mode,reader)
    dispatch5=compile_dispatch5(a.tool_dir,out,mode,reader)
    dispatch6=compile_dispatch6(a.tool_dir,out,mode,reader)
    dispatch11=fragment_tools['compile_dispatch11'](a.tool_dir,out,mode,reader)
    if dispatch11!=raw[0][0x424:0x46c]:raise ValueError('Compiled dispatcher command-192 differs from original bytes')
    dispatch10=fragment_tools['compile_dispatch10'](a.tool_dir,out,mode,reader)
    if dispatch10!=raw[0][0x3f0:0x424]:raise ValueError('Compiled dispatcher command-186 differs from original bytes')
    dispatch9=fragment_tools['compile_dispatch9'](a.tool_dir,out,mode,reader)
    if dispatch9!=raw[0][0x394:0x3f0]:raise ValueError('Compiled dispatcher command-175 differs from original bytes')
    dispatch8=fragment_tools['compile_dispatch8'](a.tool_dir,out,mode,reader)
    if dispatch8!=raw[0][0x34e:0x394]:raise ValueError('Compiled dispatcher ordinal differs from original bytes')
    dispatch7=fragment_tools['compile_dispatch7'](a.tool_dir,out,mode,reader)
    if dispatch7!=raw[0][0x31a:0x34e]:raise ValueError('Compiled dispatcher gate differs from original bytes')
    if dispatch6!=raw[0][0x2d8:0x31a]:raise ValueError('Compiled dispatcher copy differs from original bytes')
    if dispatch5!=raw[0][0x2a6:0x2d8]:raise ValueError('Compiled dispatcher table-check differs from original bytes')
    if dispatch4!=raw[0][0x26a:0x2a6]:raise ValueError('Compiled dispatcher check differs from original bytes')
    if dispatch3!=raw[0][0x232:0x26a]:raise ValueError('Compiled dispatcher branch differs from original bytes')
    if dispatch2!=raw[0][0x1da:0x232]:raise ValueError('Compiled dispatcher continuation differs from original bytes')
    if dispatch!=raw[0][0x180:0x1da]:raise ValueError('Compiled dispatcher differs from original bytes')
    if ad!=raw[0][0x124:0x156]:raise ValueError('Compiled command path differs from original bytes')
    if ae!=raw[0][0x86:0xcc]:raise ValueError('Compiled command path differs from original bytes')
    if more!=raw[0][0x50:0x86]:raise ValueError('Compiled dispatch continuation differs from original bytes')
    if entry!=raw[0][:0x42]:raise ValueError('Compiled entry differs from original bytes')
    if epilogue!=raw[0][0x42:0x50]:raise ValueError('Compiled epilogue differs from original bytes')
    code=entry+epilogue+more+ae+raw[0][0xcc:0x124]+ad+raw[0][0x156:0x180]+dispatch+dispatch2+dispatch3+dispatch4+dispatch5+dispatch6+dispatch7+dispatch8+dispatch9+dispatch10+dispatch11+raw[0][0x46c:]
    parts=[('.tsl9_full_code','ax','tsl9_incoming_external_14056',code),
           ('.tsl9_full_defaults','a','tsl9_settings_default_data_1a69c',raw[1])]
    asm=[]
    for section,section_flags,name,data in parts:
        asm += ['.section '+section+',"'+section_flags+ '",@progbits', '.globl '+name, name+':']
        asm += ['.byte '+','.join(str(x) for x in data[i:i+32]) for i in range(0,len(data),32)]
        asm += ['.size '+name+', .-'+name]
    source=out/('opaque-provider-'+mode+'.s')
    source.write_text('\n'.join(asm)+'\n',encoding='ascii')
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
    target=symbols['tsl9_ota_entry_9c4a']
    if (target['value']!=0x9c4a or target['index'] in (0,0xfff1) or target['size']==0 or
        elf.sections[target['index']]['flags']&6!=6):
        raise ValueError('OTA forwarding target lacks executable section backing')
    ae_targets={'tsl9_ota_entry_92f2':0x92f2,'tsl9_callback_table_entry_90b0':0x90b0,
                'tsl9_queue_status_81aa':0x81aa,'tsl9_selector_notifications_provider_9ef0':0x9ef0,
                'tsl9_settings_state_inputs_provider_e20c':0xe20c,'tsl9_ota_external_13f66':0x13f66}
    for name,address in ae_targets.items():
        target=symbols[name]
        if (target['value']!=address or target['index'] in (0,0xfff1) or target['size']==0 or
            elf.sections[target['index']]['flags']&6!=6):
            raise ValueError('Command path target lacks executable section backing: '+name)
    target=symbols['tsl9_callback_external_9124']
    if (target['value']!=0x9124 or target['index'] in (0,0xfff1) or target['size']==0 or
        elf.sections[target['index']]['flags']&6!=6):
        raise ValueError('Dispatcher continuation target lacks executable section backing')
    target=symbols['tsl9_events_13ba6']
    if (target['value']!=0x13ba6 or target['index'] in (0,0xfff1) or target['size']==0 or
        elf.sections[target['index']]['flags']&6!=6):
        raise ValueError('Dispatcher target lacks executable section backing')
    target=symbols['tsl9_secondary_message_dispatch_entry_1400c']
    if (target['value']!=0x1400c or target['index'] in (0,0xfff1) or target['size']==0 or
        elf.sections[target['index']]['flags']&6!=6):
        raise ValueError('Command path target lacks executable section backing')
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
                  'compiled_epilogue_bytes_replacing_carrier':14,
                  'compiled_entry_bytes_replacing_carrier':66,
                  'compiled_more_bytes_replacing_carrier':54,
                  'compiled_ae_bytes_replacing_carrier':70,
                  'compiled_ad_bytes_replacing_carrier':50,
                  'compiled_dispatch_bytes_replacing_carrier':90,
                  'compiled_dispatch2_bytes_replacing_carrier':88,
                  'compiled_dispatch3_bytes_replacing_carrier':56,
                  'compiled_dispatch4_bytes_replacing_carrier':60,
                  'compiled_dispatch5_bytes_replacing_carrier':50,
                  'compiled_dispatch6_bytes_replacing_carrier':66,
                  'compiled_dispatch7_bytes_replacing_carrier':52,
                  'compiled_dispatch8_bytes_replacing_carrier':70,
                  'compiled_dispatch9_bytes_replacing_carrier':92,
                  'compiled_dispatch10_bytes_replacing_carrier':52,
                  'compiled_dispatch11_bytes_replacing_carrier':72,
                  'original_semantics_recovered':False,'global_index_bounds_proved':False,
                  'ram_ownership_proved':False,'installed_rom_proved':False,'diagnostic_pt_load':0,
                  'target_executed':False,'hardware_validated':False,'flashable':False}))
