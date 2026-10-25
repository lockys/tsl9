"""Compile C and C++; compare actual RV32 objects, without target execution."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
X = Path(__file__).resolve().parent
R = X.parents[1]
S = json.loads((X/'spec-v1.json').read_text())
OUT = X/'build/v1'
OUT.mkdir(parents=True,exist_ok=True)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(R/S['source']) == S['source_sha256']
assert sha(R/S['firmware']) == S['firmware_sha256']
llvm = Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin'
assert sha(llvm/'clang.exe') == S['tools']['clang.exe']
assert sha(llvm.parent/'lib/clang/18/include/stdint.h') == S['stdint_sha256']
reader = R/'experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py'
assert sha(reader)=='a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a'
E = runpy.run_path(str(reader))['ELF']
shared=R/'experiments/tsl9-original-startup/build-v1.py'
assert sha(shared)=='1f6e3673c24a5d85c62d55ec8d8390b80225577010d81c8aba5c4b6750e208b5'
B=runpy.run_path(str(shared),run_name='offline_positive_control_library')
fw=(R/S['firmware']).read_bytes()
results=[]
for mode in ['c','cpp']:
    obj=OUT/(mode+'.o')
    command=[str(llvm/'clang.exe'),*S['flags'][mode],'-c',str(R/S['source']),'-o',str(obj)]
    p=subprocess.run(command,capture_output=True,timeout=60)
    if p.returncode:
        print(p.stderr.decode('utf-8',errors='replace')[:4000]); raise RuntimeError('Compiler failed: '+mode)
    e=E(obj)
    assert e.header[0]==1 and e.header[1]==243 and not e.program_headers
    symbols={s['name']:s for s in e.symbols if s['info']>>4}
    assert set(symbols)=={r['name'] for r in S['regions']}
    assert not any(s['section']==0 and s['name'] for s in e.symbols)
    expected=[];owned=set();instruction_count=0
    for region in S['regions']:
        symbol=symbols[region['name']];sec=e.sections[symbol['section']]
        assert symbol['info']==18 and symbol['size']==region['bytes'] and symbol['value']==0
        assert sec['flags']==6 and sec['type']==1 and sec['size']==region['bytes']
        assert sec['name']=='.text.'+region['name']
        owned.add(sec['index']);actual=bytearray(e.data(sec))
        original=fw[region['start']-0x8000:region['end']-0x8000]
        assert hashlib.sha256(original).hexdigest()==region['original_sha256']
        for edge in [x for x in S['controls'] if x['owner']==region['name']]:
            off,kind=edge['offset'],edge['type'];width,mask=B['MASKS'][kind]
            a=int.from_bytes(actual[off:off+width],'little');b=int.from_bytes(original[off:off+width],'little')
            assert a&mask==b&mask and a&(~mask&((1<<(width*8))-1))==0
            assert B['decode_control'](original[off:off+width],edge['PC'])==(kind,edge['target_PC'])
            actual[off:off+width]=(a|B['immediate'](kind,edge['target_PC']-edge['PC'])).to_bytes(width,'little')
            expected.append((sec['index'],off,kind,0,edge['target']))
        assert bytes(actual)==original, (mode,region['name'],'Original-coordinate byte mismatch')
        at=0
        while at<len(actual):
            at+=4 if actual[at]&3==3 else 2;instruction_count+=1
        assert at==len(actual)
    actual=[(x['section'],x['offset'],x['type'],x['addend'],e.symbols[x['symbol']]['name']) for x in e.relocations]
    assert sorted(actual)==sorted(expected)
    assert {s['index'] for s in e.sections if s['flags']&2 and s['size']}==owned
    assert instruction_count==41 and sum(r['bytes'] for r in S['regions'])==118
    # Parse the actual output using the independent retained review reader too.
    independent=R/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
    assert sha(independent)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
    comparison=runpy.run_path(str(R/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py'))['audit'](obj)
    results.append(dict(mode=mode,passed=True,object_sha256=sha(obj),code_bytes=118,instructions=41,
                        positive_FUNC=11,complete_original_bodies=3,typed_control_relocations=5,
                        compiler_undefined=0,independent_reader=comparison))
receipt=dict(passed=True,source_sha256=S['source_sha256'],results=results,
             curated_integration=False,formal_coverage_percent=89.03,target_executed=False,
             new_BIN=False,physical_ABI_verified=False,OTA_compatibility_verified=False)
(OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
