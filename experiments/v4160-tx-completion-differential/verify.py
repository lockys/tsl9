"""Compare the post-selection TX sequence through the boundary before JR T1."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import struct
import tempfile

from oracle import BASE, Slice, need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SIZE = 140000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corpus():
    serial = 0
    for base in (100, 4096):
        for bank in (0, 1):
            for n in (0, 1, 3, 4, 15, 31):
                for delta in (-1, 0, 4, 5, 16):
                    for stack in ('separate', 'checksum_RA', 'metadata_S0', 'tail_S0'):
                        for selector in ('normal_GP', 'metadata', 'tail', 'saved_RA'):
                            yield dict(base=base, bank=bank, n=n, delta=delta, stack=stack,
                                       selector=selector, command=(0,255,0x1234,0xffffffff)[serial%4])
                            serial += 1
    for bank in (0, 1):
        for n in (255,256,1039,1040,1050,1051,1052,65529,65530,65535):
            yield dict(base=100,bank=bank,n=n,delta=None,stack='separate',selector='normal_GP',command=0xffffffff)


def fixture(case, patterns, i):
    base, bank, n = case['base'], case['bank'], case['n']
    origin = BASE-base
    slot = BASE+1062*bank
    checksum = slot+11+n
    source = origin+70000 if case['delta'] is None else slot+6+case['delta']
    sp = {'separate': origin+139900, 'checksum_RA': (checksum&~3)-28,
          'metadata_S0': ((slot+2)&~3)-24, 'tail_S0': 0x40038}[case['stack']]
    address = {'normal_GP': 0x20004000+148+4*bank, 'metadata': slot+2,
               'tail': 0x40050, 'saved_RA': sp+28}[case['selector']]
    gp = address-148-4*bank
    r = [(j*0x1020304+0x112233)&0xffffffff for j in range(32)]
    r[0]=0; r[2]=sp; r[3]=gp; r[8]=n; r[9]=source; r[12]=bank; r[19]=case['command']
    r[16]=0xdeadbeef
    regions = [(origin,patterns[i%8]),(0x20004000,bytes((j*11+i)%256 for j in range(512))),
               (0x40000,bytes((j*17+i)%256 for j in range(128)))]
    return regions, r


def build(tools, folder, model, mode, optimization, name):
    unit = folder / (name + '.c')
    unit.write_text(model + '\n' + (HERE / 'wrapper.c').read_text('utf-8').replace('#include "model.c"', ''), encoding='utf-8')
    obj, dll = folder / (name + '.obj'), folder / (name + '.dll')
    args = [tools['clang'], '--target=x86_64-pc-windows-msvc', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', optimization, '-Wall', '-Wextra', '-Werror',
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17',
            '-c', unit, '-o', obj]
    if mode == 'cpp':
        args += ['-fno-exceptions', '-fno-rtti']
    for command in (args, [tools['ld.lld'], '-flavor', 'link', '/dll', '/noentry', '/nodefaultlib',
                           '/out:' + str(dll), obj]):
        result = subprocess.run([str(x) for x in command], capture_output=True, text=True, timeout=30)
        need(result.returncode == 0, 'host compiler/linker failed: ' + result.stderr[:600])
    return dll


def exercise(dll, oracle, patterns, cases, expect_failure=False):
    import _ctypes
    bytep, wordp = ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_uint32)
    lib=ctypes.CDLL(str(dll)); fn=lib.tx_run
    fn.argtypes=[bytep,ctypes.c_uint32,ctypes.c_uint32,bytep,bytep,wordp,wordp,ctypes.c_uint32,wordp,wordp]
    fn.restype=None
    capacity=2*65535+64
    events=(ctypes.c_uint32*(4*capacity))()
    try:
        for i,case in enumerate(cases):
            regions, initial = fixture(case,patterns,i)
            expected, registers, trace = oracle.run(regions,initial)
            buffers=[(ctypes.c_ubyte*len(data)).from_buffer_copy(data) for _,data in regions]
            r=(ctypes.c_uint32*32)(*initial); count=ctypes.c_uint32();fault=ctypes.c_uint32()
            fn(buffers[0],regions[0][0],SIZE,buffers[1],buffers[2],r,events,capacity,
               ctypes.byref(count),ctypes.byref(fault))
            need(fault.value==0,'valid fixture has no host mapping/trace fault')
            mem_equal=all(bytes(buf)==data for buf,(_,data) in zip(buffers,expected))
            reg_equal=list(r)==registers
            actual_trace=ctypes.string_at(ctypes.addressof(events),count.value*16)
            trace_equal=actual_trace==trace
            if expect_failure:
                if not mem_equal or not reg_equal:
                    return {'case':i,'fixture':case,'memory_equal':mem_equal,'registers_equal':reg_equal,
                            'trace_equal':trace_equal}
                continue
            need(mem_equal and reg_equal and trace_equal,'complete slice differential mismatch: '+str(case))
            n,bank=case['n'],case['bank'];sp=initial[2];selector=initial[3]+148+4*bank;slot=BASE+1062*bank
            suffix=[struct.unpack_from('<4I',trace,len(trace)-160+16*j) for j in range(10)]
            expected_suffix=[(2,slot+11+n,1,registers[14]),(1,sp+28,4,registers[1]),
                             (1,sp+20,4,registers[9]),(1,sp+16,4,registers[18]),(1,sp+12,4,registers[19]),
                             (2,slot+2,2,(n+6)&65535),(2,slot+4,2,0),(1,sp+24,4,registers[8]),
                             (1,0x40050,4,registers[6]),(1,selector,1,registers[10])]
            need(suffix==expected_suffix and count.value==2*n+14,'exact finish access sequence and count')
        need(not expect_failure,'compiled completion mutation accepted')
        return {'cases':len(cases),'all_32_registers_equal':True,'ordered_abstract_accesses_equal':True}
    finally:
        del fn
        _ctypes.FreeLibrary(lib._handle)


def worker(tool_dir):
    need(os.name == 'nt' and ctypes.sizeof(ctypes.c_void_p) == 8, 'Windows x64 host worker required')
    tools = {n: tool_dir / (n + '.exe') for n in ('clang', 'ld.lld')}
    expected_tools = {'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
                      'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
    for name, expected in expected_tools.items():
        need(sha(tools[name]) == expected, 'pinned tool: ' + name)
    inputs = {p.name: sha(p) for p in (HERE / 'model.c', HERE / 'wrapper.c', HERE / 'oracle.py', HERE / 'verify.py')}
    image = (ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
    need(len(image) == 76800 and hashlib.sha256(image).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'original image identity')
    oracle = Slice(image)
    patterns = [bytes((i * 37 + seed * 19) & 255 for i in range(SIZE)) for seed in range(8)]
    cases = list(corpus())
    model = (HERE / 'model.c').read_text('utf-8')
    profiles = {}
    with tempfile.TemporaryDirectory(prefix='tsl9-semantic-host-') as directory:
        folder = Path(directory)
        for mode in ('c', 'cpp'):
            for optimization in ('-O0', '-O2'):
                name = mode + optimization.replace('-', '_')
                dll = build(tools, folder, model, mode, optimization, name)
                profiles[name] = exercise(dll, oracle, patterns, cases)
        ra_read = 'r[1]=read_le(m,add32(sp,28),4);'
        s0_read = 'r[8]=read_le(m,add32(sp,24),4);'
        checksum = 'write_le(m,add32(add32(d,length),5),1,sum);'
        metadata = 'write_le(m,add32(r[15],2),2,r[8]);'
        mutants = {
            'checksum_offset': model.replace('add32(add32(d,length),5)','add32(add32(d,length),4)'),
            'metadata_length': model.replace('r[8]=add32(length,6)','r[8]=add32(length,5)'),
            'RA_prefetched_before_checksum': model.replace(ra_read,'r[1]=cached_ra;').replace(checksum,
                'uint32_t cached_ra=read_le(m,add32(sp,28),4);\n    '+checksum),
            'S0_prefetched_before_metadata': model.replace(s0_read,'r[8]=cached_s0;').replace(metadata,
                'uint32_t cached_s0=read_le(m,add32(sp,24),4);\n    '+metadata)}
        mutations = {}
        for name, text in mutants.items():
            dll = build(tools, folder, text, 'c', '-O2', name)
            mutations[name] = exercise(dll, oracle, patterns, cases, expect_failure=True)
    for name, expected in inputs.items():
        need(sha(HERE / name) == expected, 'inputs unchanged after host execution')
    return {'passed':True,'cases_per_profile':len(cases),'profiles':profiles,
            'compiled_mutations_rejected':mutations,'compared':['all_three_memory_regions','all_32_registers','ordered_abstract_memory_trace'],
            'actual_C_executed_on_host':True,'original_instructions_interpreted':True,
            'stop_before_JR_PC':'0x8b50','providers_executed':False,'device_executed':False,
            'global_RAM_ownership_proved':False,'bus_width_or_atomicity_equivalence_proved':False,
            'inputs_sha256':inputs,'tools_sha256':expected_tools}



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-dir', type=Path, required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.tool_dir)))
    else:
        command = [sys.executable] + (['-O'] if sys.flags.optimize else []) + ['-B', str(Path(__file__).resolve()), '--worker', '--tool-dir', str(args.tool_dir.resolve())]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        need(result.returncode == 0, 'bounded host worker failed: ' + result.stderr[-1500:])
        print(result.stdout.strip())
