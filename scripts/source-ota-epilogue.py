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
