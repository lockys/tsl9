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
