"""Compile the original-frame epilogue without executing target code."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent.parent
def compile_fragment(tool_dir, out, mode, reader):
    clang=Path(tool_dir)/('clang.exe' if (Path(tool_dir)/'clang.exe').is_file() else 'clang')
    if not clang.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid compiler or mode')
    obj=Path(out)/('ota-epilogue-'+mode+'.o')
    command=[str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32',
             '-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',
             str(ROOT/'src/native/receive/ota_epilogue_14098.inc'),'-o',str(obj)]
    p=subprocess.run(command,capture_output=True,text=True)
    if p.returncode:raise ValueError('Epilogue compile failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_epilogue']
    symbols=[x for x in elf.symbols if x['name']=='tsl9_ota_epilogue_14098']
    if (section['size']!=14 or section['type']!=1 or section['flags']&6!=6 or
        len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=14 or elf.relocations):
        raise ValueError('Unexpected epilogue object layout')
    return elf.data(section)

def compile_entry(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):
        raise ValueError('Invalid compiler, linker or mode')
    obj=Path(out)/('ota-entry-'+mode+'.o')
    cmd=[str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32',
         '-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',
         str(ROOT/'src/native/receive/ota_entry_14056.inc'),'-o',str(obj)]
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode:raise ValueError('Entry compile failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_entry']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_entry_14056']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x16,16,'.Lentry',0x38),(0x1a,16,'.Lentry',0x50),
              (0x22,16,'.Lentry',0x38),(0x26,16,'.Lentry',0x64),(0x34,16,'.Lentry',0x64),
              (0x3e,17,'tsl9_ota_entry_9c4a',0)]
    if (section['size']!=66 or section['type']!=1 or section['flags']&6!=6 or
        len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=66 or relocs!=expected):
        raise ValueError('Unexpected entry object or branch relocations')
    linked=Path(out)/('NOT-FLASHABLE-entry-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14056','-e','tsl9_ota_entry_14056',
                      '--defsym=tsl9_ota_entry_9c4a=0x9c4a',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Entry link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_entry']
    if placed['address']!=0x14056 or placed['size']!=66:
        raise ValueError('Unexpected linked entry placement')
    return result.data(placed)

def compile_more(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):
        raise ValueError('Invalid compiler, linker or mode')
    obj=Path(out)/('ota-more-'+mode+'.o')
    cmd=[str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32',
         '-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',
         str(ROOT/'src/native/receive/ota_more_140a6.inc'),'-o',str(obj)]
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatch continuation compile failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_more']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_more_140a6']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x04,16,'.Lmore',0x7c),(0x08,16,'.Lmore',0x36),(0x10,16,'.Lmore',-0x18),
              (0x26,16,'.Lmore',0x106),(0x2e,16,'.Lmore',0xbd8),(0x34,45,'.Lmore',0x108)]
    if (section['size']!=54 or section['type']!=1 or section['flags']&6!=6 or
        len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=54 or relocs!=expected):
        raise ValueError('Unexpected dispatch continuation or relocations')
    linked=Path(out)/('NOT-FLASHABLE-more-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x140a6','-e','tsl9_ota_more_140a6',
                      str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatch continuation link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_more']
    if placed['address']!=0x140a6 or placed['size']!=54:
        raise ValueError('Unexpected dispatch continuation placement')
    return result.data(placed)

def compile_dispatch80(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'):
        raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch80-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_141ac.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher80 compile failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch80']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_141ac']
    relocs = [(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected = [(0xe,44,'.Ld80',0x2a),(0x20,17,'tsl9_dispatch80_scheduler_9124',0),(0x28,45,'.Ld80',-0x4e)]
    if (section['size'] != 42 or section['type'] != 1 or section['flags'] & 6 != 6 or
        len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 42 or relocs != expected):
        raise ValueError('Unexpected dispatcher80 section or relocations: '+repr(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch80-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x141ac', '-e', 'tsl9_ota_dispatch_141ac', '--defsym=tsl9_dispatch80_scheduler_9124=0x9124', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher80 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch80']
    if placed['address'] != 0x141ac or placed['size'] != 42: raise ValueError('Unexpected dispatcher80 placement')
    return result.data(placed)

def compile_dispatch79(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'):
        raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch79-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14122.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher79 compile failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch79']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14122']
    relocs = [(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected = [(2,16,'.Ld79',-0x8a),(0x2a,16,'.Lnext79',0),(0x36,16,'.Lnext79',0),
                (0x40,45,'.Ld79',-8),(0x44,16,'.Lloop79',0),
                (0x4c,17,'tsl9_ota_code_13e0e',0),(0x52,17,'tsl9_ota_code_13dd4',0),
                (0x56,45,'.Ld79',-0x8a)]
    if (section['size'] != 88 or section['type'] != 1 or section['flags'] & 6 != 6 or
        len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 88 or relocs != expected):
        raise ValueError('Unexpected dispatcher79 section or relocations: '+repr(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch79-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14122', '-e', 'tsl9_ota_dispatch_14122', '--defsym=tsl9_ota_code_13e0e=0x13e0e', '--defsym=tsl9_ota_code_13dd4=0x13dd4', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher79 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch79']
    if placed['address'] != 0x14122 or placed['size'] != 88: raise ValueError('Unexpected dispatcher79 placement')
    return result.data(placed)

def compile_ae(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):
        raise ValueError('Invalid compiler, linker or mode')
    obj=Path(out)/('ota-ae-'+mode+'.o')
    cmd=[str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32',
         '-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',
         str(ROOT/'src/native/receive/ota_ae_140dc.inc'),'-o',str(obj)]
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode:raise ValueError('Command path compile failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_ae']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_ae_140dc']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    targets={'tsl9_ota_entry_92f2':0x92f2,'tsl9_callback_table_entry_90b0':0x90b0,
             'tsl9_queue_status_81aa':0x81aa,'tsl9_selector_notifications_provider_9ef0':0x9ef0,
             'tsl9_settings_state_inputs_provider_e20c':0xe20c,'tsl9_ota_external_13f66':0x13f66}
    expected=[(0x04,16,'.Lae',0x9e),(0x0c,16,'.Lae',-0x22),(0x16,17,'tsl9_ota_entry_92f2',0),
              (0x1a,44,'.Lae',-0x44),(0x24,17,'tsl9_callback_table_entry_90b0',0),
              (0x28,17,'tsl9_queue_status_81aa',0),(0x2c,44,'.Lae',0x38),
              (0x30,17,'tsl9_selector_notifications_provider_9ef0',0),
              (0x34,17,'tsl9_settings_state_inputs_provider_e20c',0),
              (0x40,17,'tsl9_ota_external_13f66',0),(0x44,45,'.Lae',-0x44)]
    if (section['size']!=70 or section['type']!=1 or section['flags']&6!=6 or
        len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=70 or relocs!=expected):
        raise ValueError('Unexpected command path or relocations')
    linked=Path(out)/('NOT-FLASHABLE-ae-'+mode+'.elf')
    cmd=[str(ld),'--no-relax','-Ttext=0x140dc','-e','tsl9_ota_ae_140dc']
    cmd += ['--defsym='+name+'='+hex(address) for name,address in targets.items()]
    p=subprocess.run([*cmd,str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Command path link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_ae']
    if placed['address']!=0x140dc or placed['size']!=70:
        raise ValueError('Unexpected command path placement')
    return result.data(placed)

def compile_ad(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):
        raise ValueError('Invalid compiler, linker or mode')
    obj=Path(out)/('ota-ad-'+mode+'.o')
    cmd=[str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32',
         '-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',
         str(ROOT/'src/native/receive/ota_ad_1417a.inc'),'-o',str(obj)]
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode:raise ValueError('Command path compile failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_ad']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_ad_1417a']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    targets={'tsl9_ota_entry_92f2':0x92f2,'tsl9_callback_table_entry_90b0':0x90b0,
             'tsl9_queue_status_81aa':0x81aa,'tsl9_selector_notifications_provider_9ef0':0x9ef0,
             'tsl9_secondary_message_dispatch_entry_1400c':0x1400c}
    expected=[(0x06,17,'tsl9_ota_entry_92f2',0),(0x0a,16,'.Lad',-0xe2),
              (0x16,17,'tsl9_callback_table_entry_90b0',0),(0x1a,17,'tsl9_queue_status_81aa',0),
              (0x1e,44,'.Lad',0x26),(0x22,17,'tsl9_selector_notifications_provider_9ef0',0),
              (0x2c,17,'tsl9_secondary_message_dispatch_entry_1400c',0),(0x30,45,'.Lad',-0xe2)]
    if (section['size']!=50 or section['type']!=1 or section['flags']&6!=6 or
        len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=50 or relocs!=expected):
        raise ValueError('Unexpected command path or relocations')
    linked=Path(out)/('NOT-FLASHABLE-ad-'+mode+'.elf')
    cmd=[str(ld),'--no-relax','-Ttext=0x1417a','-e','tsl9_ota_ad_1417a']
    cmd += ['--defsym='+name+'='+hex(address) for name,address in targets.items()]
    p=subprocess.run([*cmd,str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Command path link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_ad']
    if placed['address']!=0x1417a or placed['size']!=50:
        raise ValueError('Unexpected command path placement')
    return result.data(placed)

def compile_dispatch(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_141d6.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_141d6']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,16,'.Ldispatch',0x68),(8,16,'.Ldispatch',0x88),(0x10,16,'.Ldispatch',0x5a),(0x18,16,'.Ldispatch',0x68),(0x20,16,'.Ldispatch',0x68),(0x28,16,'.Ldispatch',0x904),(0x2c,16,'.Ldispatch',0x1f4),(0x34,16,'.Ldispatch',0x86a),(0x38,16,'.Ldispatch',0x1ac),(0x40,16,'.Ldispatch',0x7ec),(0x44,16,'.Ldispatch',0xb2),(0x4c,16,'.Ldispatch',-0x13e),(0x54,17,'tsl9_dispatch_provider_13ba6',0),(0x58,45,'.Ldispatch',-0x64)]
    if section['size']!=90 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=90 or relocs!=expected:raise ValueError('Unexpected dispatcher layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x141d6','-e','tsl9_ota_dispatch_141d6','--defsym=tsl9_dispatch_provider_13ba6=0x13ba6',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch']
    if placed['address']!=0x141d6 or placed['size']!=90:raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)

def compile_dispatch2(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch2-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14230.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch2']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14230']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0xa,16,'.Ldispatch2',-0x36),(0x10,17,'tsl9_dispatch2_queue_81aa',0),(0x16,44,'.Ldispatch2',-0x36),(0x28,17,'tsl9_dispatch2_scheduler_9124',0),(0x2c,45,'.Ldispatch2',-0x198),(0x32,16,'.Ldispatch2',0x4a),(0x3a,16,'.Ldispatch2',0xe),(0x48,45,'.Ldispatch2',0xa),(0x4e,16,'.Ldispatch2',0xe),(0x56,45,'.Ldispatch2',-0x3a)]
    if section['size']!=88 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=88 or relocs!=expected:raise ValueError('Unexpected dispatcher continuation layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch2-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14230','-e','tsl9_ota_dispatch_14230','--defsym=tsl9_dispatch2_queue_81aa=0x81aa','--defsym=tsl9_dispatch2_scheduler_9124=0x9124',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch2']
    if placed['address']!=0x14230 or placed['size']!=88:raise ValueError('Unexpected dispatcher continuation placement')
    return result.data(placed)

def compile_dispatch3(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch3-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14288.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher branch compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch3']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14288']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,16,'.Ldispatch3',0x774),(0xc,16,'.Ldispatch3',-0x1f0),(0x14,16,'.Ldispatch3',0x79c),(0x26,16,'.Ldispatch3',0x79c)]
    if section['size']!=56 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=56 or relocs!=expected:raise ValueError('Unexpected dispatcher branch layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch3-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14288','-e','tsl9_ota_dispatch_14288',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher branch link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch3']
    if placed['address']!=0x14288 or placed['size']!=56:raise ValueError('Unexpected dispatcher branch placement')
    return result.data(placed)

def compile_dispatch4(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch4-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_142c0.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher check compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch4']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_142c0']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(6,17,'tsl9_dispatch4_checker_92f2',0),(0x24,16,'.Ldispatch4',0x75e),(0x2a,16,'.Ldispatch4',0x1a),(0x38,16,'.Ldispatch4',0x764)]
    if section['size']!=60 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=60 or relocs!=expected:raise ValueError('Unexpected dispatcher check layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch4-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x142c0','-e','tsl9_ota_dispatch_142c0','--defsym=tsl9_dispatch4_checker_92f2=0x92f2',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher check link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch4']
    if placed['address']!=0x142c0 or placed['size']!=60:raise ValueError('Unexpected dispatcher check placement')
    return result.data(placed)

def compile_dispatch5(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch5-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_142fc.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher table-check compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch5']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_142fc']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x12,44,'.Ldispatch5',0x1e),(0x1a,17,'tsl9_dispatch5_ingress_9b02',0),(0x2c,44,'.Ldispatch5',0x32),(0x2e,17,'tsl9_dispatch5_callback_fa3c',0)]
    if section['size']!=50 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=50 or relocs!=expected:raise ValueError('Unexpected dispatcher table-check layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch5-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x142fc','-e','tsl9_ota_dispatch_142fc','--defsym=tsl9_dispatch5_ingress_9b02=0x9b02','--defsym=tsl9_dispatch5_callback_fa3c=0xfa3c',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher table-check link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch5']
    if placed['address']!=0x142fc or placed['size']!=50:raise ValueError('Unexpected dispatcher table-check placement')
    return result.data(placed)

def compile_dispatch6(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch6-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1432e.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher copy compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch6']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1432e']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x24,17,'tsl9_dispatch6_writer_13138',0),(0x38,17,'tsl9_dispatch6_scheduler_9124',0),(0x3e,17,'tsl9_dispatch6_entry_13dd4',0)]
    if section['size']!=66 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=66 or relocs!=expected:raise ValueError('Unexpected dispatcher copy layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch6-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x1432e','-e','tsl9_ota_dispatch_1432e','--defsym=tsl9_dispatch6_writer_13138=0x13138','--defsym=tsl9_dispatch6_scheduler_9124=0x9124','--defsym=tsl9_dispatch6_entry_13dd4=0x13dd4',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher copy link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch6']
    if placed['address']!=0x1432e or placed['size']!=66:raise ValueError('Unexpected dispatcher copy placement')
    return result.data(placed)

def compile_dispatch7(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch7-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14370.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher gate compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch7']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14370']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(8,16,'.Ldispatch7',-0x2d8),(0xc,17,'tsl9_dispatch7_inputs_e20c',0),(0x10,45,'.Ldispatch7',-0x2d8),(0x16,16,'.Ldispatch7',0x664),(0x1a,16,'.Ldispatch7',0x6e6),(0x22,16,'.Ldispatch7',0x67a),(0x2a,16,'.Ldispatch7',-0x2d8),(0x30,16,'.Ldispatch7',0x764)]
    if section['size']!=52 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=52 or relocs!=expected:raise ValueError('Unexpected dispatcher gate layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch7-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14370','-e','tsl9_ota_dispatch_14370','--defsym=tsl9_dispatch7_inputs_e20c=0xe20c',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher gate link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch7']
    if placed['address']!=0x14370 or placed['size']!=52:raise ValueError('Unexpected dispatcher gate placement')
    return result.data(placed)

def compile_dispatch8(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch8-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_143a4.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher ordinal compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch8']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_143a4']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x1a,16,'.Ldispatch8',0x6f2),(0x24,45,'.Ldispatch8',-0x28a),(0x2a,16,'.Ldispatch8',0x60c),(0x2e,16,'.Ldispatch8',0xd6),(0x36,16,'.Ldispatch8',0x154),(0x3a,16,'.Ldispatch8',0xa2),(0x42,16,'.Ldispatch8',-0x30c)]
    if section['size']!=70 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=70 or relocs!=expected:raise ValueError('Unexpected dispatcher ordinal layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch8-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x143a4','-e','tsl9_ota_dispatch_143a4',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher ordinal link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch8']
    if placed['address']!=0x143a4 or placed['size']!=70:raise ValueError('Unexpected dispatcher ordinal placement')
    return result.data(placed)

def compile_dispatch9(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch9-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_143ea.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-175 compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch9']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_143ea']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(2,16,'.Ldispatch9',-0x352),(0xe,17,'tsl9_dispatch9_table_90b0',0),(0x1e,17,'tsl9_dispatch9_helper_9334',0),(0x2a,16,'.Ldispatch9',0x54),(0x2e,17,'tsl9_dispatch9_notify_9ef0',0),(0x3e,44,'.Ldispatch9',0x4e),(0x4a,17,'tsl9_dispatch9_writer_13138',0),(0x50,17,'tsl9_dispatch9_status_820c',0),(0x5a,45,'.Ldispatch9',-0x2d0)]
    if section['size']!=92 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=92 or relocs!=expected:raise ValueError('Unexpected dispatcher command-175 layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch9-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x143ea','-e','tsl9_ota_dispatch_143ea','--defsym=tsl9_dispatch9_table_90b0=0x90b0','--defsym=tsl9_dispatch9_helper_9334=0x9334','--defsym=tsl9_dispatch9_notify_9ef0=0x9ef0','--defsym=tsl9_dispatch9_writer_13138=0x13138','--defsym=tsl9_dispatch9_status_820c=0x820c',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-175 link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch9']
    if placed['address']!=0x143ea or placed['size']!=92:raise ValueError('Unexpected dispatcher command-175 placement')
    return result.data(placed)

def compile_dispatch10(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch10-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14446.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-186 compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch10']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14446']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,16,'.Ldispatch10',0x746),(0xc,16,'.Ldispatch10',-0x3ae),(0x12,16,'.Ldispatch10',0x70a),(0x1a,16,'.Ldispatch10',0x6f4),(0x20,16,'.Ldispatch10',-0x3ae),(0x28,17,'tsl9_dispatch10_message_1264e',0),(0x2e,17,'tsl9_dispatch10_gap_136d0',0),(0x32,45,'.Ldispatch10',-0x3ae)]
    if section['size']!=52 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=52 or relocs!=expected:raise ValueError('Unexpected dispatcher command-186 layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch10-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14446','-e','tsl9_ota_dispatch_14446','--defsym=tsl9_dispatch10_message_1264e=0x1264e','--defsym=tsl9_dispatch10_gap_136d0=0x136d0',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-186 link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch10']
    if placed['address']!=0x14446 or placed['size']!=52:raise ValueError('Unexpected dispatcher command-186 placement')
    return result.data(placed)

def compile_dispatch11(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch11-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1447a.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-192 compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch11']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1447a']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,16,'.Ldispatch11',0x520),(8,16,'.Ldispatch11',0x48),(0x10,16,'.Ldispatch11',-0x3e2),(0x1a,16,'.Ldispatch11',0x36a),(0x1e,16,'.Ldispatch11',0x34c),(0x22,16,'.Ldispatch11',0x334),(0x28,16,'.Ldispatch11',-0x3e2),(0x30,17,'tsl9_dispatch11_provider_13ba6',0),(0x36,17,'tsl9_dispatch11_flow_12aa0',0),(0x3c,17,'tsl9_dispatch11_flow_12aa0',0),(0x42,17,'tsl9_dispatch11_flow_12aa0',0),(0x46,45,'.Ldispatch11',-0x3e2)]
    if section['size']!=72 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=72 or relocs!=expected:raise ValueError('Unexpected dispatcher command-192 layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch11-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x1447a','-e','tsl9_ota_dispatch_1447a','--defsym=tsl9_dispatch11_provider_13ba6=0x13ba6','--defsym=tsl9_dispatch11_flow_12aa0=0x12aa0',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-192 link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch11']
    if placed['address']!=0x1447a or placed['size']!=72:raise ValueError('Unexpected dispatcher command-192 placement')
    return result.data(placed)

def compile_dispatch12(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch12-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_144c2.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-240 compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch12']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_144c2']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,16,'.Ldispatch12',0x50),(0xc,16,'.Ldispatch12',-0x42a),(0x12,16,'.Ldispatch12',-0x42a),(0x1a,17,'tsl9_dispatch12_checker_92f2',0),(0x1e,16,'.Ldispatch12',-0x42a),(0x30,17,'tsl9_dispatch12_message_126a0',0),(0x34,45,'.Ldispatch12',-0x42a)]
    if section['size']!=54 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=54 or relocs!=expected:raise ValueError('Unexpected dispatcher command-240 layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch12-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x144c2','-e','tsl9_ota_dispatch_144c2','--defsym=tsl9_dispatch12_checker_92f2=0x92f2','--defsym=tsl9_dispatch12_message_126a0=0x126a0',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-240 link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch12']
    if placed['address']!=0x144c2 or placed['size']!=54:raise ValueError('Unexpected dispatcher command-240 placement')
    return result.data(placed)

def compile_dispatch13(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch13-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_144f8.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-176 compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch13']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_144f8']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(8,16,'.Ldispatch13',0x248),(0x10,17,'tsl9_dispatch13_provider_13ba6',0),(0x14,17,'tsl9_dispatch13_state_13c4e',0),(0x18,45,'.Ldispatch13',-0x460),(0x20,16,'.Ldispatch13',-0x460)]
    if section['size']!=54 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=54 or relocs!=expected:raise ValueError('Unexpected dispatcher command-176 layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch13-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x144f8','-e','tsl9_ota_dispatch_144f8','--defsym=tsl9_dispatch13_provider_13ba6=0x13ba6','--defsym=tsl9_dispatch13_state_13c4e=0x13c4e',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher command-176 link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch13']
    if placed['address']!=0x144f8 or placed['size']!=54:raise ValueError('Unexpected dispatcher command-176 placement')
    return result.data(placed)

def compile_dispatch14(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch14-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1452e.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher jump-table compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch14']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1452e']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,17,'tsl9_dispatch14_provider_13ba6',0),(0xa,17,'tsl9_dispatch14_field_12ad0',0),(0xe,45,'.Ldispatch14',-0x496),(0x14,17,'tsl9_dispatch14_provider_13ba6',0),(0x1a,45,'.Ldispatch14',0xa),(0x20,17,'tsl9_dispatch14_provider_13ba6',0)]
    if section['size']!=36 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=36 or relocs!=expected:raise ValueError('Unexpected dispatcher jump-table layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch14-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x1452e','-e','tsl9_ota_dispatch_1452e','--defsym=tsl9_dispatch14_provider_13ba6=0x13ba6','--defsym=tsl9_dispatch14_field_12ad0=0x12ad0',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher jump-table link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch14']
    if placed['address']!=0x1452e or placed['size']!=36:raise ValueError('Unexpected dispatcher jump-table placement')
    return result.data(placed)

def compile_dispatch15(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch15-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14552.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher case-2 compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch15']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14552']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(8,16,'.Ldispatch15',-0x4ba),(0x20,17,'tsl9_dispatch15_feature_82a8',0)]
    if section['size']!=36 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=36 or relocs!=expected:raise ValueError('Unexpected dispatcher case-2 layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch15-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14552','-e','tsl9_ota_dispatch_14552','--defsym=tsl9_dispatch15_feature_82a8=0x82a8',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher case-2 link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch15']
    if placed['address']!=0x14552 or placed['size']!=36:raise ValueError('Unexpected dispatcher case-2 placement')
    return result.data(placed)

def compile_dispatch16(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch16-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14576.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher halfword pack compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch16']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14576']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x26,17,'tsl9_dispatch16_feature_82a8',0)]
    if section['size']!=42 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=42 or relocs!=expected:raise ValueError('Unexpected dispatcher halfword pack layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch16-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14576','-e','tsl9_ota_dispatch_14576','--defsym=tsl9_dispatch16_feature_82a8=0x82a8',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher halfword pack link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch16']
    if placed['address']!=0x14576 or placed['size']!=42:raise ValueError('Unexpected dispatcher halfword pack placement')
    return result.data(placed)

def compile_dispatch17(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch17-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_145a0.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher word pack compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch17']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_145a0']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x42,17,'tsl9_dispatch17_feature_82a8',0)]
    if section['size']!=70 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=70 or relocs!=expected:raise ValueError('Unexpected dispatcher word pack layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch17-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x145a0','-e','tsl9_ota_dispatch_145a0','--defsym=tsl9_dispatch17_feature_82a8=0x82a8',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher word pack link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch17']
    if placed['address']!=0x145a0 or placed['size']!=70:raise ValueError('Unexpected dispatcher word pack placement')
    return result.data(placed)

def compile_dispatch18(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch18-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_145e6.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher mix compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch18']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_145e6']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x4c,17,'tsl9_dispatch18_feature_82a8',0)]
    if section['size']!=80 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=80 or relocs!=expected:raise ValueError('Unexpected dispatcher mix layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch18-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x145e6','-e','tsl9_ota_dispatch_145e6','--defsym=tsl9_dispatch18_feature_82a8=0x82a8',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher mix link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch18']
    if placed['address']!=0x145e6 or placed['size']!=80:raise ValueError('Unexpected dispatcher mix placement')
    return result.data(placed)

def compile_dispatch19(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch19-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14636.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher extra halfword compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch19']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14636']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x26,17,'tsl9_dispatch19_feature_82a8',0),(0x40,17,'tsl9_dispatch19_feature_82a8',0)]
    if section['size']!=68 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=68 or relocs!=expected:raise ValueError('Unexpected dispatcher extra halfword layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch19-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14636','-e','tsl9_ota_dispatch_14636','--defsym=tsl9_dispatch19_feature_82a8=0x82a8',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher extra halfword link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch19']
    if placed['address']!=0x14636 or placed['size']!=68:raise ValueError('Unexpected dispatcher extra halfword placement')
    return result.data(placed)

def compile_dispatch20(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch20-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1467a.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher compare-mask compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch20']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1467a']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(8,16,'.Ldispatch20',0x1c),(0x2e,17,'tsl9_dispatch20_leaf_d4ea',0)]
    if section['size']!=50 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=50 or relocs!=expected:raise ValueError('Unexpected dispatcher compare-mask layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch20-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x1467a','-e','tsl9_ota_dispatch_1467a','--defsym=tsl9_dispatch20_leaf_d4ea=0xd4ea',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher compare-mask link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch20']
    if placed['address']!=0x1467a or placed['size']!=50:raise ValueError('Unexpected dispatcher compare-mask placement')
    return result.data(placed)

def compile_dispatch21(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch21-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_146ac.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher mask-leaf compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch21']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_146ac']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x16,17,'tsl9_dispatch21_leaf_d472',0),(0x38,17,'tsl9_dispatch21_leaf_d322',0)]
    if section['size']!=60 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=60 or relocs!=expected:raise ValueError('Unexpected dispatcher mask-leaf layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch21-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x146ac','-e','tsl9_ota_dispatch_146ac','--defsym=tsl9_dispatch21_leaf_d472=0xd472','--defsym=tsl9_dispatch21_leaf_d322=0xd322',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher mask-leaf link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch21']
    if placed['address']!=0x146ac or placed['size']!=60:raise ValueError('Unexpected dispatcher mask-leaf placement')
    return result.data(placed)

def compile_dispatch22(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch22-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_146e8.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher extra-mask compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch22']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_146e8']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x14,17,'tsl9_dispatch22_leaf_d4e0',0),(0x2e,17,'tsl9_dispatch22_get_1008a',0)]
    if section['size']!=50 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=50 or relocs!=expected:raise ValueError('Unexpected dispatcher extra-mask layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch22-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x146e8','-e','tsl9_ota_dispatch_146e8','--defsym=tsl9_dispatch22_leaf_d4e0=0xd4e0','--defsym=tsl9_dispatch22_get_1008a=0x1008a',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher extra-mask link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch22']
    if placed['address']!=0x146e8 or placed['size']!=50:raise ValueError('Unexpected dispatcher extra-mask placement')
    return result.data(placed)

def compile_dispatch23(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch23-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1471a.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher filter-tail compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch23']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1471a']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x1e,17,'tsl9_dispatch23_filter_8a56',0),(0x22,45,'.Ldispatch23',-0x682)]
    if section['size']!=36 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=36 or relocs!=expected:raise ValueError('Unexpected dispatcher filter-tail layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch23-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x1471a','-e','tsl9_ota_dispatch_1471a','--defsym=tsl9_dispatch23_filter_8a56=0x8a56',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher filter-tail link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch23']
    if placed['address']!=0x1471a or placed['size']!=36:raise ValueError('Unexpected dispatcher filter-tail placement')
    return result.data(placed)

def compile_dispatch24(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch24-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1473e.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher table-cases compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch24']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1473e']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,17,'tsl9_dispatch24_provider_13ba6',0),(8,45,'.Ldispatch24',-0x6a6),(0xe,17,'tsl9_dispatch24_provider_13ba6',0),(0x1a,16,'.Ldispatch24',-0x6a6),(0x32,17,'tsl9_dispatch24_feature_82a8',0)]
    if section['size']!=54 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=54 or relocs!=expected:raise ValueError('Unexpected dispatcher table-cases layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch24-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x1473e','-e','tsl9_ota_dispatch_1473e','--defsym=tsl9_dispatch24_provider_13ba6=0x13ba6','--defsym=tsl9_dispatch24_feature_82a8=0x82a8',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher table-cases link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch24']
    if placed['address']!=0x1473e or placed['size']!=54:raise ValueError('Unexpected dispatcher table-cases placement')
    return result.data(placed)

def compile_dispatch25(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch25-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14774.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher three-halfword compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch25']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14774']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0x38,45,'.Ldispatch25',-0x3e)]
    if section['size']!=58 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=58 or relocs!=expected:raise ValueError('Unexpected dispatcher three-halfword layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch25-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14774','-e','tsl9_ota_dispatch_14774',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher three-halfword link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch25']
    if placed['address']!=0x14774 or placed['size']!=58:raise ValueError('Unexpected dispatcher three-halfword placement')
    return result.data(placed)


def compile_dispatch78(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch78-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14c78.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher78 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch78']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14c78']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0, 17, '.Ldispatch78', -0x1cfe), (4, 45, '.Ldispatch78', -0x7e), (10, 17, '.Ldispatch78', -0xe6a), (14, 17, '.Ldispatch78', -0xabc)]
    if section['size'] != 18 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 18 or relocs != expected: raise ValueError('Unexpected dispatcher78 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch78-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14c78', '-e', 'tsl9_ota_dispatch_14c78', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher78 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch78']
    if placed['address'] != 0x14c78 or placed['size'] != 18: raise ValueError('Unexpected dispatcher78 placement')
    return result.data(placed)


def compile_dispatch77(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch77-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14c50.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher77 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch77']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14c50']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0, 17, '.Ldispatch77', 0x2f42), (4, 44, '.Ldispatch77_zero', 0), (14, 16, '.Ldispatch77', -0xbb8), (22, 17, '.Ldispatch77', 0x2d3a), (26, 45, '.Ldispatch77', -0x298), (36, 17, '.Ldispatch77', -0xb36)]
    if section['size'] != 40 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 40 or relocs != expected: raise ValueError('Unexpected dispatcher77 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch77-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14c50', '-e', 'tsl9_ota_dispatch_14c50', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher77 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch77']
    if placed['address'] != 0x14c50 or placed['size'] != 40: raise ValueError('Unexpected dispatcher77 placement')
    return result.data(placed)


def compile_dispatch76(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch76-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14c32.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher76 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch76']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14c32']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(10, 17, '.Ldispatch76', -0xccc), (22, 17, '.Ldispatch76', -0x14f2), (26, 17, '.Ldispatch76', -0xb9a)]
    if section['size'] != 30 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 30 or relocs != expected: raise ValueError('Unexpected dispatcher76 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch76-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14c32', '-e', 'tsl9_ota_dispatch_14c32', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher76 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch76']
    if placed['address'] != 0x14c32 or placed['size'] != 30: raise ValueError('Unexpected dispatcher76 placement')
    return result.data(placed)


def compile_dispatch75(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch75-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14c28.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher75 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch75']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14c28']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(4, 17, '.Ldispatch75', -0xcaa), (8, 45, '.Ldispatch75', -0x2e)]
    if section['size'] != 10 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 10 or relocs != expected: raise ValueError('Unexpected dispatcher75 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch75-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14c28', '-e', 'tsl9_ota_dispatch_14c28', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher75 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch75']
    if placed['address'] != 0x14c28 or placed['size'] != 10: raise ValueError('Unexpected dispatcher75 placement')
    return result.data(placed)


def compile_dispatch74(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch74-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14c10.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher74 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch74']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14c10']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(18, 17, '.Ldispatch74', -0x1cc8), (22, 45, '.Ldispatch74', -0x16)]
    if section['size'] != 24 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 24 or relocs != expected: raise ValueError('Unexpected dispatcher74 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch74-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14c10', '-e', 'tsl9_ota_dispatch_14c10', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher74 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch74']
    if placed['address'] != 0x14c10 or placed['size'] != 24: raise ValueError('Unexpected dispatcher74 placement')
    return result.data(placed)


def compile_dispatch73(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch73-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14bf6.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher73 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch73']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14bf6']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0, 17, '.Ldispatch73', -0x1ba4), (20, 17, '.Ldispatch73', -0xbad2), (24, 45, '.Ldispatch73', -0x3a)]
    if section['size'] != 26 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 26 or relocs != expected: raise ValueError('Unexpected dispatcher73 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch73-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14bf6', '-e', 'tsl9_ota_dispatch_14bf6', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher73 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch73']
    if placed['address'] != 0x14bf6 or placed['size'] != 26: raise ValueError('Unexpected dispatcher73 placement')
    return result.data(placed)


def compile_dispatch72(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch72-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14be4.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher72 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch72']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14be4']
    if section['size'] != 18 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 18 or elf.relocations: raise ValueError('Unexpected dispatcher72 layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch72-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14be4', '-e', 'tsl9_ota_dispatch_14be4', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher72 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch72']
    if placed['address'] != 0x14be4 or placed['size'] != 18: raise ValueError('Unexpected dispatcher72 placement')
    return result.data(placed)


def compile_dispatch71(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch71-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14bda.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher71 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch71']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14bda']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    if section['size'] != 10 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 10 or relocs != [(8, 44, '.Ldispatch71', 0x36)]: raise ValueError('Unexpected dispatcher71 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch71-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14bda', '-e', 'tsl9_ota_dispatch_14bda', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher71 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch71']
    if placed['address'] != 0x14bda or placed['size'] != 10: raise ValueError('Unexpected dispatcher71 placement')
    return result.data(placed)


def compile_dispatch70(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch70-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14bc0.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher70 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch70']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14bc0']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0, 17, '.Ldispatch70', 0x2fd2), (4, 44, '.Ldispatch70', 0x72), (10, 16, '.Ldispatch70', -0xb28), (22, 16, '.Ldispatch70', 0x68)]
    if section['size'] != 26 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 26 or relocs != expected: raise ValueError('Unexpected dispatcher70 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch70-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14bc0', '-e', 'tsl9_ota_dispatch_14bc0', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher70 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch70']
    if placed['address'] != 0x14bc0 or placed['size'] != 26: raise ValueError('Unexpected dispatcher70 placement')
    return result.data(placed)


def compile_dispatch69(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch69-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14bb8.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher69 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch69']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14bb8']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0, 17, '.Ldispatch69', 0x2fda), (6, 45, '.Ldispatch69', 0x8a)]
    if section['size'] != 8 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 8 or relocs != expected: raise ValueError('Unexpected dispatcher69 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch69-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14bb8', '-e', 'tsl9_ota_dispatch_14bb8', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher69 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch69']
    if placed['address'] != 0x14bb8 or placed['size'] != 8: raise ValueError('Unexpected dispatcher69 placement')
    return result.data(placed)


def compile_dispatch68(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch68-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14b9c.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher68 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch68']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14b9c']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(2, 16, '.Ldispatch68', 0xb4), (8, 16, '.Ldispatch68', -0xb04), (12, 17, '.Ldispatch68', 0x2ff6), (20, 44, '.Ldispatch68', 0xdc), (22, 17, '.Ldispatch68', -0x1b18), (26, 45, '.Ldispatch68', 0x5e)]
    if section['size'] != 28 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 28 or relocs != expected: raise ValueError('Unexpected dispatcher68 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch68-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14b9c', '-e', 'tsl9_ota_dispatch_14b9c', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher68 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch68']
    if placed['address'] != 0x14b9c or placed['size'] != 28: raise ValueError('Unexpected dispatcher68 placement')
    return result.data(placed)


def compile_dispatch67(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch67-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14b8c.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher67 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch67']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14b8c']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(2, 16, '.Ldispatch67', -0xaf4), (10, 16, '.Ldispatch67', 0x34), (14, 44, '.Ldispatch67', 0x2c)]
    if section['size'] != 16 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 16 or relocs != expected: raise ValueError('Unexpected dispatcher67 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch67-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14b8c', '-e', 'tsl9_ota_dispatch_14b8c', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher67 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch67']
    if placed['address'] != 0x14b8c or placed['size'] != 16: raise ValueError('Unexpected dispatcher67 placement')
    return result.data(placed)


def compile_dispatch66(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch66-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14b64.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher66 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch66']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14b64']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0x14, 17, '.Ldispatch66', -0x1c7e), (0x1c, 17, '.Ldispatch66', -0x2516), (0x22, 17, '.Ldispatch66', -0x1494), (0x26, 45, '.Ldispatch66', -0x3e)]
    if section['size'] != 40 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 40 or relocs != expected: raise ValueError('Unexpected dispatcher66 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch66-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14b64', '-e', 'tsl9_ota_dispatch_14b64', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher66 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch66']
    if placed['address'] != 0x14b64 or placed['size'] != 40: raise ValueError('Unexpected dispatcher66 placement')
    return result.data(placed)


def compile_dispatch65(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch65-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14b50.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher65 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch65']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14b50']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(4, 16, '.Ldispatch65', -0xab8), (16, 16, '.Ldispatch65', -0x11c)]
    if section['size'] != 20 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 20 or relocs != expected: raise ValueError('Unexpected dispatcher65 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch65-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14b50', '-e', 'tsl9_ota_dispatch_14b50', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher65 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch65']
    if placed['address'] != 0x14b50 or placed['size'] != 20: raise ValueError('Unexpected dispatcher65 placement')
    return result.data(placed)


def compile_dispatch64(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch64-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14b3a.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher64 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch64']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14b3a']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0, 17, '.Ldispatch64', -0x24da), (14, 17, '.Ldispatch64', -0xca2), (18, 17, '.Ldispatch64', -0xaa2)]
    if section['size'] != 22 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 22 or relocs != expected: raise ValueError('Unexpected dispatcher64 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch64-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14b3a', '-e', 'tsl9_ota_dispatch_14b3a', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher64 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch64']
    if placed['address'] != 0x14b3a or placed['size'] != 22: raise ValueError('Unexpected dispatcher64 placement')
    return result.data(placed)


def compile_dispatch63(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch63-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14b1c.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher63 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch63']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14b1c']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0, 17, '.Ldispatch63', -0x1cc8), (6, 17, '.Ldispatch63', -0x14bc), (26, 17, '.Ldispatch63', -0x8c4)]
    if section['size'] != 30 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 30 or relocs != expected: raise ValueError('Unexpected dispatcher63 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch63-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14b1c', '-e', 'tsl9_ota_dispatch_14b1c', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher63 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch63']
    if placed['address'] != 0x14b1c or placed['size'] != 30: raise ValueError('Unexpected dispatcher63 placement')
    return result.data(placed)


def compile_dispatch62(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch62-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14b08.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher62 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch62']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14b08']
    if section['size'] != 20 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 20 or elf.relocations: raise ValueError('Unexpected dispatcher62 layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch62-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14b08', '-e', 'tsl9_ota_dispatch_14b08', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher62 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch62']
    if placed['address'] != 0x14b08 or placed['size'] != 20: raise ValueError('Unexpected dispatcher62 placement')
    return result.data(placed)


def compile_dispatch61(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch61-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14af4.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher61 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch61']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14af4']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(4, 16, '.Ldispatch61', -0xa5c), (16, 16, '.Ldispatch61', -0xc0)]
    if section['size'] != 20 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 20 or relocs != expected: raise ValueError('Unexpected dispatcher61 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch61-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14af4', '-e', 'tsl9_ota_dispatch_14af4', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher61 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch61']
    if placed['address'] != 0x14af4 or placed['size'] != 20: raise ValueError('Unexpected dispatcher61 placement')
    return result.data(placed)


def compile_dispatch60(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch60-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14ad4.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher60 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch60']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14ad4']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(2, 17, '.Ldispatch60', -0x710), (8, 16, '.Ldispatch60', 0x20), (18, 16, '.Ldispatch60', -0xa3c), (24, 17, '.Ldispatch60', -0x1474), (28, 17, '.Ldispatch60', -0xa3c)]
    if section['size'] != 32 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 32 or relocs != expected: raise ValueError('Unexpected dispatcher60 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch60-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14ad4', '-e', 'tsl9_ota_dispatch_14ad4', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher60 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch60']
    if placed['address'] != 0x14ad4 or placed['size'] != 32: raise ValueError('Unexpected dispatcher60 placement')
    return result.data(placed)


def compile_dispatch59(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch59-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14a9e.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher59 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch59']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14a9e']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(10, 17, '.Ldispatch59', -0x1966), (18, 17, '.Ldispatch59', -0xc90), (30, 17, '.Ldispatch59', -0xb38), (50, 17, '.Ldispatch59', -0x846)]
    if section['size'] != 54 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 54 or relocs != expected: raise ValueError('Unexpected dispatcher59 layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch59-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14a9e', '-e', 'tsl9_ota_dispatch_14a9e', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher59 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch59']
    if placed['address'] != 0x14a9e or placed['size'] != 54: raise ValueError('Unexpected dispatcher59 placement')
    return result.data(placed)


def compile_dispatch58(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch58-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14a96.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher58 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch58']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14a96']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    if section['size'] != 8 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 8 or relocs != [(4, 16, '.Ldispatch58', -0x6e0)]: raise ValueError('Unexpected dispatcher58 layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch58-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14a96', '-e', 'tsl9_ota_dispatch_14a96', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher58 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch58']
    if placed['address'] != 0x14a96 or placed['size'] != 8: raise ValueError('Unexpected dispatcher58 placement')
    return result.data(placed)


def compile_dispatch57(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch57-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14a6c.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher57 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch57']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14a6c']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(8, 17, '.Ldispatch57', -0xb948), (28, 17, '.Ldispatch57', -0xb948), (38, 17, '.Ldispatch57', -0x952)]
    if section['size'] != 42 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 42 or relocs != expected: raise ValueError('Unexpected dispatcher57 layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch57-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14a6c', '-e', 'tsl9_ota_dispatch_14a6c', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher57 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch57']
    if placed['address'] != 0x14a6c or placed['size'] != 42: raise ValueError('Unexpected dispatcher57 placement')
    return result.data(placed)


def compile_dispatch56(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch56-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14a56.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher56 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch56']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14a56']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(6, 17, '.Ldispatch56', -0xb764), (10, 16, '.Ldispatch56', -0x9be)]
    if section['size'] != 22 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 22 or relocs != expected: raise ValueError('Unexpected dispatcher56 layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch56-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14a56', '-e', 'tsl9_ota_dispatch_14a56', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher56 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch56']
    if placed['address'] != 0x14a56 or placed['size'] != 22: raise ValueError('Unexpected dispatcher56 placement')
    return result.data(placed)


def compile_dispatch55(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch55-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14a40.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher55 compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch55']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14a40']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(6, 17, '.Ldispatch55', -0xb74e), (10, 16, '.Ldispatch55', -0x9a8), (18, 17, '.Ldispatch55', -0x89c)]
    if section['size'] != 22 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 22 or relocs != expected: raise ValueError('Unexpected dispatcher55 layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch55-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14a40', '-e', 'tsl9_ota_dispatch_14a40', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher55 link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch55']
    if placed['address'] != 0x14a40 or placed['size'] != 22: raise ValueError('Unexpected dispatcher55 placement')
    return result.data(placed)


def compile_dispatch54(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch54-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14a24.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch54']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14a24']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(12, 17, '.Ldispatch54', -0xb536), (20, 17, '.Ldispatch54', -0xaa6), (24, 17, '.Ldispatch54', -0x98c)]
    if section['size'] != 28 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 28 or relocs != expected: raise ValueError('Unexpected dispatcher54 layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch54-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14a24', '-e', 'tsl9_ota_dispatch_14a24', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch54']
    if placed['address'] != 0x14a24 or placed['size'] != 28: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch53(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch53-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14a1e.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch53']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14a1e']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    if section['size'] != 6 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 6 or relocs != [(2, 17, '.Ldispatch53', -0x730)]: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch53-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14a1e', '-e', 'tsl9_ota_dispatch_14a1e', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch53']
    if placed['address'] != 0x14a1e or placed['size'] != 6: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch52(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch52-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_149fc.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch52']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_149fc']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(14, 16, '.Ldispatch52', 0x16), (18, 17, '.Ldispatch52', -0x9308), (30, 17, '.Ldispatch52', -0x8e2)]
    if section['size'] != 34 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 34 or relocs != expected: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch52-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x149fc', '-e', 'tsl9_ota_dispatch_149fc', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch52']
    if placed['address'] != 0x149fc or placed['size'] != 34: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch51(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch51-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_149ea.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch51']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_149ea']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(10, 17, '.Ldispatch51', 0x19c2), (14, 17, '.Ldispatch51', -0x952)]
    if section['size'] != 18 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 18 or relocs != expected: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch51-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x149ea', '-e', 'tsl9_ota_dispatch_149ea', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch51']
    if placed['address'] != 0x149ea or placed['size'] != 18: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch50(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch50-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_149d4.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch50']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_149d4']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(4, 44, '.Ldispatch50_zero', 0), (6, 17, '.Ldispatch50', -0xa370), (10, 17, '.Ldispatch50', -0x93c), (14, 17, '.Ldispatch50', -0xa32a), (18, 17, '.Ldispatch50', -0x93c)]
    if section['size'] != 22 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 22 or relocs != expected: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch50-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x149d4', '-e', 'tsl9_ota_dispatch_149d4', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch50']
    if placed['address'] != 0x149d4 or placed['size'] != 22: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch49(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch49-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_149c2.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch49']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_149c2']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(10, 17, '.Ldispatch49', 0x2982), (14, 17, '.Ldispatch49', -0x92a)]
    if section['size'] != 18 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 18 or relocs != expected: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch49-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x149c2', '-e', 'tsl9_ota_dispatch_149c2', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch49']
    if placed['address'] != 0x149c2 or placed['size'] != 18: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch48(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch48-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_149b0.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch48']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_149b0']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(4, 17, '.Ldispatch48', 0xc20), (14, 17, '.Ldispatch48', -0x896)]
    if section['size'] != 18 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 18 or relocs != expected: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch48-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x149b0', '-e', 'tsl9_ota_dispatch_149b0', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch48']
    if placed['address'] != 0x149b0 or placed['size'] != 18: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch47(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch47-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_1499a.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch47']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_1499a']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0, 45, '.Ldispatch47', 0x32e), (14, 17, '.Ldispatch47', -0xe4e), (18, 17, '.Ldispatch47', -0x902)]
    if section['size'] != 22 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 22 or relocs != expected: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch47-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x1499a', '-e', 'tsl9_ota_dispatch_1499a', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch47']
    if placed['address'] != 0x1499a or placed['size'] != 22: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch46(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch46-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14976.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch46']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14976']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(0, 17, '.Ldispatch46', -0x1f6e), (4, 45, '.Ldispatch46', -0x152), (10, 16, '.Ldispatch46', 0x14), (24, 16, '.Ldispatch46', -10), (34, 45, '.Ldispatch46', -10)]
    if section['size'] != 36 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 36 or relocs != expected: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch46-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14976', '-e', 'tsl9_ota_dispatch_14976', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch46']
    if placed['address'] != 0x14976 or placed['size'] != 36: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch45(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch45-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14974.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch45']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14974']
    if section['size'] != 2 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 2 or elf.relocations: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch45-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14974', '-e', 'tsl9_ota_dispatch_14974', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch45']
    if placed['address'] != 0x14974 or placed['size'] != 2: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch44(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch44-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14970.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch44']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14970']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    if section['size'] != 4 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 4 or relocs != [(0, 17, '.Ldispatch44', -0xc764)]: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch44-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14970', '-e', 'tsl9_ota_dispatch_14970', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch44']
    if placed['address'] != 0x14970 or placed['size'] != 4: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch43(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch43-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14968.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch43']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14968']
    if section['size'] != 8 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 8 or elf.relocations: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch43-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14968', '-e', 'tsl9_ota_dispatch_14968', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch43']
    if placed['address'] != 0x14968 or placed['size'] != 8: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch42(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'): raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch42-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14964.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch42']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14964']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    if section['size'] != 4 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 4 or relocs != [(0, 16, '.Ldispatch42', 24)]: raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch42-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14964', '-e', 'tsl9_ota_dispatch_14964', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch42']
    if placed['address'] != 0x14964 or placed['size'] != 4: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch41(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'):
        raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch41-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_1494c.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch41']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_1494c']
    if section['size'] != 24 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 24 or elf.relocations:
        raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch41-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x1494c', '-e', 'tsl9_ota_dispatch_1494c', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch41']
    if placed['address'] != 0x1494c or placed['size'] != 24: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch40(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'):
        raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch40-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14934.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch40']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14934']
    if section['size'] != 24 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 24 or elf.relocations:
        raise ValueError('Unexpected dispatcher layout or relocations')
    linked = Path(out)/('NOT-FLASHABLE-dispatch40-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14934', '-e', 'tsl9_ota_dispatch_14934', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch40']
    if placed['address'] != 0x14934 or placed['size'] != 24: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch39(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'):
        raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch39-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_14928.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch39']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_14928']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    expected = [(4, 17, 'tsl9_dispatch39_call_13ba6', 0), (8, 17, 'tsl9_dispatch39_call_1070a', 0)]
    if section['size'] != 12 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 12 or relocs != expected:
        raise ValueError('Unexpected dispatcher layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch39-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x14928', '-e', 'tsl9_ota_dispatch_14928', '--defsym=tsl9_dispatch39_call_13ba6=0x13ba6', '--defsym=tsl9_dispatch39_call_1070a=0x1070a', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch39']
    if placed['address'] != 0x14928 or placed['size'] != 12: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch38(tool_dir, out, mode, reader):
    directory = Path(tool_dir)
    clang = directory / ('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld = directory / ('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c', 'cpp'):
        raise ValueError('Invalid tool or mode')
    obj = Path(out)/('ota-dispatch38-'+mode+'.o')
    p = subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32', '-ffreestanding', '-Os', '-x', 'c' if mode == 'c' else 'c++', '-c', str(ROOT/'src/native/receive/ota_dispatch_1491a.inc'), '-o', str(obj)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher compilation failed: '+p.stderr[:1000])
    elf = reader(obj); section = elf.byname['.tsl9_ota_dispatch38']
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_ota_dispatch_1491a']
    relocs = [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    if section['size'] != 14 or section['type'] != 1 or section['flags'] & 6 != 6 or len(symbols) != 1 or symbols[0]['index'] != section['index'] or symbols[0]['size'] != 14 or relocs != [(10, 16, 'tsl9_dispatch38_return_14098', 0)]:
        raise ValueError('Unexpected dispatcher layout or relocations: '+str(relocs))
    linked = Path(out)/('NOT-FLASHABLE-dispatch38-'+mode+'.elf')
    p = subprocess.run([str(ld), '--no-relax', '-Ttext=0x1491a', '-e', 'tsl9_ota_dispatch_1491a', '--defsym=tsl9_dispatch38_return_14098=0x14098', str(obj), '-o', str(linked)], capture_output=True, text=True)
    if p.returncode: raise ValueError('Dispatcher link failed: '+p.stderr[:1000])
    result = reader(linked); placed = result.byname['.tsl9_ota_dispatch38']
    if placed['address'] != 0x1491a or placed['size'] != 14: raise ValueError('Unexpected dispatcher placement')
    return result.data(placed)


def compile_dispatch37(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch37-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_148fc.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch37']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_148fc']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    if section['size']!=30 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=30 or relocs!=[(4,16,'.Ldispatch37',-36),(28,45,'.Ldispatch37',-36)]:raise ValueError('Unexpected dispatcher continuation layout or relocations: '+str(relocs))
    linked=Path(out)/('NOT-FLASHABLE-dispatch37-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x148fc','-e','tsl9_ota_dispatch_148fc',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch37']
    if placed['address']!=0x148fc or placed['size']!=30:raise ValueError('Unexpected dispatcher continuation placement')
    return result.data(placed)


def compile_dispatch36(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch36-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_148de.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch36']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_148de']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,16,'.Ldispatch36',30),(28,45,'.Ldispatch36',-6)]
    if section['size']!=30 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=30 or relocs!=expected:raise ValueError('Unexpected dispatcher continuation layout or relocations: '+str(relocs))
    linked=Path(out)/('NOT-FLASHABLE-dispatch36-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x148de','-e','tsl9_ota_dispatch_148de',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch36']
    if placed['address']!=0x148de or placed['size']!=30:raise ValueError('Unexpected dispatcher continuation placement')
    return result.data(placed)


def compile_dispatch35(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch35-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_148b4.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch35']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_148b4']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(12,16,'.Ldispatch35',42),(40,45,'.Ldispatch35',-38)]
    if section['size']!=42 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=42 or relocs!=expected:raise ValueError('Unexpected dispatcher continuation layout or relocations: '+str(relocs))
    linked=Path(out)/('NOT-FLASHABLE-dispatch35-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x148b4','-e','tsl9_ota_dispatch_148b4',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch35']
    if placed['address']!=0x148b4 or placed['size']!=42:raise ValueError('Unexpected dispatcher continuation placement')
    return result.data(placed)


def compile_dispatch34(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch34-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1489a.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch34']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1489a']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0,17,'.Ldispatch34',-0x1ddc),(10,17,'.Ldispatch34',-0x1ddc),(20,17,'.Ldispatch34',-0x1ddc),(24,45,'.Ldispatch34',-0x76)]
    if section['size']!=26 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=26 or relocs!=expected:raise ValueError('Unexpected dispatcher continuation layout or relocations: '+str(relocs))
    linked=Path(out)/('NOT-FLASHABLE-dispatch34-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x1489a','-e','tsl9_ota_dispatch_1489a',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch34']
    if placed['address']!=0x1489a or placed['size']!=26:raise ValueError('Unexpected dispatcher continuation placement')
    return result.data(placed)


def compile_dispatch33(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch33-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1488e.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch33']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1488e']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    if section['size']!=12 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=12 or relocs!=[(0,16,'.Ldispatch33',0x26)]:raise ValueError('Unexpected dispatcher continuation layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch33-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x1488e','-e','tsl9_ota_dispatch_1488e',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch33']
    if placed['address']!=0x1488e or placed['size']!=12:raise ValueError('Unexpected dispatcher continuation placement')
    return result.data(placed)


def compile_dispatch32(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    if not clang.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch32-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1487e.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher loop setup compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch32']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1487e']
    if section['size']!=16 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=16 or elf.relocations:raise ValueError('Unexpected dispatcher loop setup layout or relocations')
    return elf.data(section)


def compile_dispatch31(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    if not clang.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch31-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14848.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch31']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14848']
    if section['size']!=54 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=54 or elf.relocations:raise ValueError('Unexpected dispatcher continuation layout or relocations')
    return elf.data(section)


def compile_dispatch30(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch30-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_1482e.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher cases compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch30']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_1482e']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(2,17,'tsl9_dispatch30_provider_12a6e',0),(8,45,'tsl9_dispatch30_continue_1481a',0),(12,17,'tsl9_dispatch30_provider_12a6e',0),(18,17,'tsl9_dispatch30_provider_12aa0',0),(24,45,'tsl9_dispatch30_continue_14820',0)]
    if section['size']!=26 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=26 or relocs!=expected:raise ValueError('Unexpected dispatcher cases layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch30-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x1482e','-e','tsl9_ota_dispatch_1482e','--defsym=tsl9_dispatch30_provider_12a6e=0x12a6e','--defsym=tsl9_dispatch30_provider_12aa0=0x12aa0','--defsym=tsl9_dispatch30_continue_1481a=0x1481a','--defsym=tsl9_dispatch30_continue_14820=0x14820',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher cases link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch30']
    if placed['address']!=0x1482e or placed['size']!=26:raise ValueError('Unexpected dispatcher cases placement')
    return result.data(placed)


def compile_dispatch29(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch29-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_14810.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch29']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_14810']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(0,44,'tsl9_dispatch29_case_14848',0),(4,17,'tsl9_dispatch29_provider_12a6e',0),(10,17,'tsl9_dispatch29_provider_12aa0',0),(16,17,'tsl9_dispatch29_provider_12aa0',0),(26,17,'tsl9_dispatch29_return_1411a',0)]
    if section['size']!=30 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=30 or relocs!=expected:raise ValueError('Unexpected dispatcher continuation layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch29-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14810','-e','tsl9_ota_dispatch_14810','--defsym=tsl9_dispatch29_case_14848=0x14848','--defsym=tsl9_dispatch29_provider_12a6e=0x12a6e','--defsym=tsl9_dispatch29_provider_12aa0=0x12aa0','--defsym=tsl9_dispatch29_return_1411a=0x1411a',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch29']
    if placed['address']!=0x14810 or placed['size']!=30:raise ValueError('Unexpected dispatcher continuation placement')
    return result.data(placed)


def compile_dispatch28(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch28-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_147f4.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch28']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_147f4']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,17,'tsl9_dispatch28_provider_13ba6',0),(8,17,'tsl9_dispatch28_feature_1070a',0),(18,16,'tsl9_dispatch28_case_1482e',0),(24,16,'tsl9_dispatch28_case_14838',0)]
    if section['size']!=28 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=28 or relocs!=expected:raise ValueError('Unexpected dispatcher continuation layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch28-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x147f4','-e','tsl9_ota_dispatch_147f4','--defsym=tsl9_dispatch28_provider_13ba6=0x13ba6','--defsym=tsl9_dispatch28_feature_1070a=0x1070a','--defsym=tsl9_dispatch28_case_1482e=0x1482e','--defsym=tsl9_dispatch28_case_14838=0x14838',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher continuation link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch28']
    if placed['address']!=0x147f4 or placed['size']!=28:raise ValueError('Unexpected dispatcher continuation placement')
    return result.data(placed)


def compile_dispatch27(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch27-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_147e4.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher guard compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch27']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_147e4']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,16,'tsl9_dispatch27_reject_1491a',0),(12,16,'tsl9_dispatch27_reject_1491a',0)]
    if section['size']!=16 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=16 or relocs!=expected:raise ValueError('Unexpected dispatcher guard layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch27-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x147e4','-e','tsl9_ota_dispatch_147e4','--defsym=tsl9_dispatch27_reject_1491a=0x1491a',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher guard link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch27']
    if placed['address']!=0x147e4 or placed['size']!=16:raise ValueError('Unexpected dispatcher guard placement')
    return result.data(placed)


def compile_dispatch26(tool_dir, out, mode, reader):
    directory=Path(tool_dir)
    clang=directory/('clang.exe' if (directory/'clang.exe').is_file() else 'clang')
    ld=directory/('ld.lld.exe' if (directory/'ld.lld.exe').is_file() else 'ld.lld')
    if not clang.is_file() or not ld.is_file() or mode not in ('c','cpp'):raise ValueError('Invalid tool or mode')
    obj=Path(out)/('ota-dispatch26-'+mode+'.o')
    p=subprocess.run([str(clang),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-Os','-x','c' if mode=='c' else 'c++','-c',str(ROOT/'src/native/receive/ota_dispatch_147ae.inc'),'-o',str(obj)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher two-cases compilation failed: '+p.stderr[:1000])
    elf=reader(obj);section=elf.byname['.tsl9_ota_dispatch26']
    symbols=[s for s in elf.symbols if s['name']=='tsl9_ota_dispatch_147ae']
    relocs=[(r['offset'],r['type'],r['symbol']['name'],r['addend']) for r in elf.relocations]
    expected=[(4,17,'tsl9_dispatch26_provider_13ba6',0),(10,17,'tsl9_dispatch26_status_820c',0),(16,17,'tsl9_dispatch26_feature_1074c',0),(20,17,'.Ldispatch26',-0x716),(28,17,'tsl9_dispatch26_provider_13ba6',0),(34,17,'tsl9_dispatch26_gap_12a6e',0),(40,17,'tsl9_dispatch26_gap_12a6e',0),(46,17,'tsl9_dispatch26_gap_12a6e',0),(50,17,'.Ldispatch26',-0x716)]
    if section['size']!=54 or section['type']!=1 or section['flags']&6!=6 or len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=54 or relocs!=expected:raise ValueError('Unexpected dispatcher two-cases layout or relocations')
    linked=Path(out)/('NOT-FLASHABLE-dispatch26-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x147ae','-e','tsl9_ota_dispatch_147ae','--defsym=tsl9_dispatch26_provider_13ba6=0x13ba6','--defsym=tsl9_dispatch26_status_820c=0x820c','--defsym=tsl9_dispatch26_feature_1074c=0x1074c','--defsym=tsl9_dispatch26_gap_12a6e=0x12a6e',str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Dispatcher two-cases link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_dispatch26']
    if placed['address']!=0x147ae or placed['size']!=54:raise ValueError('Unexpected dispatcher two-cases placement')
    return result.data(placed)
