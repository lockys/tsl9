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
              (0x22,16,'.Lentry',0x38),(0x26,16,'.Lentry',0x64),(0x34,16,'.Lentry',0x64)]
    if (section['size']!=56 or section['type']!=1 or section['flags']&6!=6 or
        len(symbols)!=1 or symbols[0]['index']!=section['index'] or symbols[0]['size']!=56 or relocs!=expected):
        raise ValueError('Unexpected entry object or branch relocations')
    linked=Path(out)/('NOT-FLASHABLE-entry-'+mode+'.elf')
    p=subprocess.run([str(ld),'--no-relax','-Ttext=0x14056','-e','tsl9_ota_entry_14056',
                      str(obj),'-o',str(linked)],capture_output=True,text=True)
    if p.returncode:raise ValueError('Entry link failed: '+p.stderr[:1000])
    result=reader(linked);placed=result.byname['.tsl9_ota_entry']
    if placed['address']!=0x14056 or placed['size']!=56:
        raise ValueError('Unexpected linked entry placement')
    return result.data(placed)
