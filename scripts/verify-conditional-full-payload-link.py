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
EXPECTED = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
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
fragment_tools=runpy.run_path(str(ROOT/'scripts/source-ota-epilogue.py'))
compile_dispatch27=fragment_tools['compile_dispatch27']
compile_dispatch28=fragment_tools['compile_dispatch28']
compile_dispatch29=fragment_tools['compile_dispatch29']
compile_dispatch30=fragment_tools['compile_dispatch30']
compile_dispatch31=fragment_tools['compile_dispatch31']
compile_epilogue,compile_entry,compile_more,compile_ae,compile_ad,compile_dispatch,compile_dispatch2,compile_dispatch3,compile_dispatch4,compile_dispatch5,compile_dispatch6,compile_dispatch7,compile_dispatch8,compile_dispatch9,compile_dispatch10,compile_dispatch11,compile_dispatch12,compile_dispatch13,compile_dispatch14,compile_dispatch15,compile_dispatch16,compile_dispatch17,compile_dispatch18,compile_dispatch19,compile_dispatch20,compile_dispatch21,compile_dispatch22,compile_dispatch23,compile_dispatch24,compile_dispatch25,compile_dispatch26=fragment_tools['compile_fragment'],fragment_tools['compile_entry'],fragment_tools['compile_more'],fragment_tools['compile_ae'],fragment_tools['compile_ad'],fragment_tools['compile_dispatch'],fragment_tools['compile_dispatch2'],fragment_tools['compile_dispatch3'],fragment_tools['compile_dispatch4'],fragment_tools['compile_dispatch5'],fragment_tools['compile_dispatch6'],fragment_tools['compile_dispatch7'],fragment_tools['compile_dispatch8'],fragment_tools['compile_dispatch9'],fragment_tools['compile_dispatch10'],fragment_tools['compile_dispatch11'],fragment_tools['compile_dispatch12'],fragment_tools['compile_dispatch13'],fragment_tools['compile_dispatch14'],fragment_tools['compile_dispatch15'],fragment_tools['compile_dispatch16'],fragment_tools['compile_dispatch17'],fragment_tools['compile_dispatch18'],fragment_tools['compile_dispatch19'],fragment_tools['compile_dispatch20'],fragment_tools['compile_dispatch21'],fragment_tools['compile_dispatch22'],fragment_tools['compile_dispatch23'],fragment_tools['compile_dispatch24'],fragment_tools['compile_dispatch25'],fragment_tools['compile_dispatch26']
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
    dispatch79=fragment_tools['compile_dispatch79'](a.tool_dir,out,mode,reader)
    if dispatch79!=raw[0][0xcc:0x124]:raise ValueError('Compiled dispatcher 14122 differs from original bytes')
    ad=compile_ad(a.tool_dir,out,mode,reader)
    dispatch80=fragment_tools['compile_dispatch80'](a.tool_dir,out,mode,reader)
    if dispatch80!=raw[0][0x156:0x180]:raise ValueError('Compiled dispatcher 141ac differs from original bytes')
    dispatch=compile_dispatch(a.tool_dir,out,mode,reader)
    dispatch2=compile_dispatch2(a.tool_dir,out,mode,reader)
    dispatch3=compile_dispatch3(a.tool_dir,out,mode,reader)
    dispatch4=compile_dispatch4(a.tool_dir,out,mode,reader)
    dispatch5=compile_dispatch5(a.tool_dir,out,mode,reader)
    dispatch6=compile_dispatch6(a.tool_dir,out,mode,reader)
    dispatch7=compile_dispatch7(a.tool_dir,out,mode,reader)
    dispatch8=compile_dispatch8(a.tool_dir,out,mode,reader)
    dispatch9=compile_dispatch9(a.tool_dir,out,mode,reader)
    dispatch10=compile_dispatch10(a.tool_dir,out,mode,reader)
    dispatch11=compile_dispatch11(a.tool_dir,out,mode,reader)
    dispatch12=compile_dispatch12(a.tool_dir,out,mode,reader)
    dispatch13=compile_dispatch13(a.tool_dir,out,mode,reader)
    dispatch14=compile_dispatch14(a.tool_dir,out,mode,reader)
    dispatch15=compile_dispatch15(a.tool_dir,out,mode,reader)
    dispatch16=compile_dispatch16(a.tool_dir,out,mode,reader)
    dispatch17=compile_dispatch17(a.tool_dir,out,mode,reader)
    dispatch18=compile_dispatch18(a.tool_dir,out,mode,reader)
    dispatch19=compile_dispatch19(a.tool_dir,out,mode,reader)
    dispatch20=compile_dispatch20(a.tool_dir,out,mode,reader)
    dispatch21=compile_dispatch21(a.tool_dir,out,mode,reader)
    dispatch22=compile_dispatch22(a.tool_dir,out,mode,reader)
    dispatch23=compile_dispatch23(a.tool_dir,out,mode,reader)
    dispatch24=compile_dispatch24(a.tool_dir,out,mode,reader)
    dispatch25=compile_dispatch25(a.tool_dir,out,mode,reader)
    dispatch26=compile_dispatch26(a.tool_dir,out,mode,reader)
    # Each continuation is independently compiled and validated against its fixed
    # carrier interval before assembling the diagnostic byte provider.
    boundaries = [0x828,0x838,0x844,0x85e,0x888,0x8a6,0x8c4,0x8d2,0x8de,
                  0x8f6,0x90e,0x912,0x91a,0x91e,0x920,0x944,0x95a,0x96c,
                  0x97e,0x994,0x9a6,0x9c8,0x9ce,0x9ea,0xa00,0xa16,0xa40,
                  0xa48,0xa7e,0xa9e,0xab2,0xac6,0xae4,0xafa,0xb0e,0xb36,0xb46,0xb62,0xb6a,0xb84,0xb8e,0xba0,0xbba,0xbd2,0xbdc,0xbfa,0xc22,0xc34]
    later_dispatch = []
    for number, (start, end) in enumerate(zip(boundaries, boundaries[1:]), 32):
        compiled = fragment_tools[f'compile_dispatch{number}'](a.tool_dir,out,mode,reader)
        if compiled != raw[0][start:end]:
            raise ValueError(f'Compiled dispatcher {number} differs from original bytes')
        later_dispatch.append(compiled)
    dispatch31=compile_dispatch31(a.tool_dir,out,mode,reader)
    if dispatch31!=raw[0][0x7f2:0x828]:raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch30=compile_dispatch30(a.tool_dir,out,mode,reader)
    if dispatch30!=raw[0][0x7d8:0x7f2]:raise ValueError('Compiled dispatcher cases differ from original bytes')
    dispatch29=compile_dispatch29(a.tool_dir,out,mode,reader)
    if dispatch29!=raw[0][0x7ba:0x7d8]:raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch28=compile_dispatch28(a.tool_dir,out,mode,reader)
    if dispatch28!=raw[0][0x79e:0x7ba]:raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch27=compile_dispatch27(a.tool_dir,out,mode,reader)
    if dispatch27!=raw[0][0x78e:0x79e]:raise ValueError('Compiled dispatcher guard differs from original bytes')
    if dispatch26!=raw[0][0x758:0x78e]:raise ValueError('Compiled dispatcher two-cases differs from original bytes')
    if dispatch25!=raw[0][0x71e:0x758]:raise ValueError('Compiled dispatcher three-halfword differs from original bytes')
    if dispatch24!=raw[0][0x6e8:0x71e]:raise ValueError('Compiled dispatcher table-cases differs from original bytes')
    if dispatch23!=raw[0][0x6c4:0x6e8]:raise ValueError('Compiled dispatcher filter-tail differs from original bytes')
    if dispatch22!=raw[0][0x692:0x6c4]:raise ValueError('Compiled dispatcher extra-mask differs from original bytes')
    if dispatch21!=raw[0][0x656:0x692]:raise ValueError('Compiled dispatcher mask-leaf differs from original bytes')
    if dispatch20!=raw[0][0x624:0x656]:raise ValueError('Compiled dispatcher compare-mask differs from original bytes')
    if dispatch19!=raw[0][0x5e0:0x624]:raise ValueError('Compiled dispatcher extra halfword differs from original bytes')
    if dispatch18!=raw[0][0x590:0x5e0]:raise ValueError('Compiled dispatcher mix differs from original bytes')
    if dispatch17!=raw[0][0x54a:0x590]:raise ValueError('Compiled dispatcher word pack differs from original bytes')
    if dispatch16!=raw[0][0x520:0x54a]:raise ValueError('Compiled dispatcher halfword pack differs from original bytes')
    if dispatch15!=raw[0][0x4fc:0x520]:raise ValueError('Compiled dispatcher case-2 differs from original bytes')
    if dispatch14!=raw[0][0x4d8:0x4fc]:raise ValueError('Compiled dispatcher jump-table differs from original bytes')
    if dispatch13!=raw[0][0x4a2:0x4d8]:raise ValueError('Compiled dispatcher command-176 differs from original bytes')
    if dispatch12!=raw[0][0x46c:0x4a2]:raise ValueError('Compiled dispatcher command-240 differs from original bytes')
    if dispatch11!=raw[0][0x424:0x46c]:raise ValueError('Compiled dispatcher command-192 differs from original bytes')
    if dispatch10!=raw[0][0x3f0:0x424]:raise ValueError('Compiled dispatcher command-186 differs from original bytes')
    if dispatch9!=raw[0][0x394:0x3f0]:raise ValueError('Compiled dispatcher command-175 differs from original bytes')
    if dispatch8!=raw[0][0x34e:0x394]:raise ValueError('Compiled dispatcher ordinal differs from original bytes')
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
    code=entry+epilogue+more+ae+dispatch79+ad+dispatch80+dispatch+dispatch2+dispatch3+dispatch4+dispatch5+dispatch6+dispatch7+dispatch8+dispatch9+dispatch10+dispatch11+dispatch12+dispatch13+dispatch14+dispatch15+dispatch16+dispatch17+dispatch18+dispatch19+dispatch20+dispatch21+dispatch22+dispatch23+dispatch24+dispatch25+dispatch26+dispatch27+dispatch28+dispatch29+dispatch30+dispatch31+b''.join(later_dispatch)
    if code != raw[0]:
        raise ValueError('Reassembled dispatcher differs from carrier')
    defaults_input = reader(base/'base/source'/mode/'defaults-read-window/unit.o')
    literal = defaults_input.data(defaults_input.byname['.rodata.tsl9_defaults_read_window_1a69c'])
    if literal != raw[1]:
        raise ValueError('Compiled default literal differs from carrier')
    parts=[('.tsl9_full_code','ax','tsl9_incoming_external_14056',code)]
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
    insert=' .payload_code 0x14056 : SUBALIGN(1) { KEEP(*(.tsl9_full_code)) } :NONE\n'
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
    # The code provider is separate; defaults now belong to the registered aggregate.
    missing_code = out / ('MISSING-CODE-' + mode + '.elf')
    negative = subprocess.run([tool('ld.lld'), '--no-undefined', '--no-relax', '-T', str(ldfile),
                               str(aggregate), str(folder/'conditional-storage.o'), *flags,
                               '--defsym=tsl9_boot_resident_40000=0x40000', '-o', str(missing_code)],
                              capture_output=True, text=True)
    if (negative.returncode == 0 or missing_code.exists()
        or set(re.findall(r'undefined symbol: ([^\r\n]+)', negative.stderr)) != {'tsl9_incoming_external_14056'}):
        raise ValueError('Missing code provider control failed')
    # Remove the real defaults section before KEEP can select it, preserving its consumer.
    without_defaults = out / ('discard-defaults-' + mode + '.ld')
    without_defaults.write_text(ldfile.read_text(encoding='utf-8').replace('SECTIONS {\n',
        'SECTIONS {\n /DISCARD/ : { *(.rodata.tsl9_defaults_read_window_1a69c) }\n'), encoding='utf-8')
    missing_defaults = out / ('MISSING-DEFAULTS-' + mode + '.elf')
    negative = subprocess.run([tool('ld.lld'), '--no-undefined', '--no-relax', '-T', str(without_defaults),
                               str(aggregate), str(folder/'conditional-storage.o'), str(obj), *flags,
                               '--defsym=tsl9_boot_resident_40000=0x40000', '-o', str(missing_defaults)],
                              capture_output=True, text=True)
    if (negative.returncode == 0 or missing_defaults.exists() or 'discarded' not in negative.stderr
        or 'tsl9_settings_default_data_1a69c' not in negative.stderr):
        raise ValueError('Discarded defaults provider control failed: ' + negative.stderr[:600])
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
    defaults = symbols['tsl9_settings_default_data_1a69c']
    if defaults['index'] in (0, 0xfff1):
        raise ValueError('Defaults must be section-backed, not a numeric witness')
    defaults_section = elf.sections[defaults['index']]
    if ((defaults['value'], defaults['size'], defaults['info']) != (0x1a69c, 4, 17)
        or (defaults_section['address'], defaults_section['size'], defaults_section['type'], defaults_section['flags']) != (0x1a69c, 4, 1, 2)
        or elf.data(defaults_section) != raw[1]):
        raise ValueError('Registered defaults OBJECT or bytes changed')
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
                    'section_backed_new_symbols':1,'registered_defaults_section_backed':True,'negative_section_controls':2,
                    'conditional_data_aliases':3,'image_bytes':len(image)})
report = {'passed':True,'results':results,'opaque_original_bytes':3128,
                  'compiled_code_bytes_reassembled':len(raw[0]),
                  'opaque_data_bytes_selected':0, 'compiled_default_bytes_replacing_carrier':len(literal),
                  'direct_fragment_objects_linked':False,
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
                  'compiled_dispatch12_bytes_replacing_carrier':54,
                  'compiled_dispatch13_bytes_replacing_carrier':54,
                  'compiled_dispatch14_bytes_replacing_carrier':36,
                  'compiled_dispatch15_bytes_replacing_carrier':36,
                  'compiled_dispatch16_bytes_replacing_carrier':42,
                  'compiled_dispatch17_bytes_replacing_carrier':70,
                  'compiled_dispatch18_bytes_replacing_carrier':80,
                  'compiled_dispatch19_bytes_replacing_carrier':68,
                  'compiled_dispatch20_bytes_replacing_carrier':50,
                  'compiled_dispatch21_bytes_replacing_carrier':60,
                  'compiled_dispatch22_bytes_replacing_carrier':50,
                  'compiled_dispatch23_bytes_replacing_carrier':36,
                  'compiled_dispatch24_bytes_replacing_carrier':54,
                  'compiled_dispatch25_bytes_replacing_carrier':58,
                  'compiled_dispatch26_bytes_replacing_carrier':54,
                  'compiled_dispatch27_bytes_replacing_carrier':16,
                  'compiled_dispatch28_bytes_replacing_carrier':28,
                  'compiled_dispatch80_bytes_replacing_carrier':42,
                  'compiled_dispatch79_bytes_replacing_carrier':88,
                  'compiled_dispatch78_bytes_replacing_carrier':18,
                  'compiled_dispatch77_bytes_replacing_carrier':40,
                  'compiled_dispatch76_bytes_replacing_carrier':30,
                  'compiled_dispatch75_bytes_replacing_carrier':10,'compiled_dispatch74_bytes_replacing_carrier':24,'compiled_dispatch73_bytes_replacing_carrier':26,'compiled_dispatch72_bytes_replacing_carrier':18,'compiled_dispatch71_bytes_replacing_carrier':10,'compiled_dispatch70_bytes_replacing_carrier':26,'compiled_dispatch69_bytes_replacing_carrier':8,'compiled_dispatch68_bytes_replacing_carrier':28,'compiled_dispatch29_bytes_replacing_carrier':30,'compiled_dispatch30_bytes_replacing_carrier':26,'compiled_dispatch31_bytes_replacing_carrier':54,
                  'compiled_dispatch32_to_67_bytes_replacing_carrier':0xb46-0x828,
                  'original_semantics_recovered':False,'global_index_bounds_proved':False,
                  'ram_ownership_proved':False,'installed_rom_proved':False,'diagnostic_pt_load':0,
                  'target_executed':False,'hardware_validated':False,'flashable':False}
(out / "verification.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report))
