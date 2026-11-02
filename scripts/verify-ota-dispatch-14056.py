#!/usr/bin/env python3
"""Check the bounded dispatcher model against the source-carried instructions."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser()
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
out.mkdir(parents=True)
build = out / 'candidate'
proc = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build-v4160-source-candidate.py'),
                       '--tool-dir', str(a.tool_dir), '--out', str(build)], capture_output=True, text=True)
if proc.returncode:
    raise ValueError('Candidate build failed: ' + proc.stderr[:1000])
facts = json.loads(proc.stdout)
if not facts['passed'] or facts['hardware_validated'] or facts['flashable_proved']:
    raise ValueError('Unexpected candidate build')
def tool(name):
    exe = a.tool_dir / (name + '.exe')
    return exe if exe.is_file() else a.tool_dir / name
expected = {0x14062:'li a5, 0x55', 0x1406c:'beq a1, a5, 0x1408e',
            0x14070:'bltu a5, a1, 0x140a6', 0x14074:'li a5, 0x45',
            0x14078:'beq a1, a5, 0x1408e', 0x1407c:'bltu a1, a5, 0x140ba',
            0x14080:'addi a5, a1, -0x52', 0x14084:'andi a5, a5, 0xff',
            0x14088:'li a4, 0x1', 0x1408a:'bltu a4, a5, 0x140ba',
            0x14094:'jal 0x9c4a', 0x140a6:'li a5, 0xa8',
            0x140aa:'beq a1, a5, 0x14122', 0x140ae:'bltu a5, a1, 0x140dc',
            0x140b2:'li a5, 0x57', 0x140b6:'beq a1, a5, 0x1408e'}
js = '''const fs=require("fs");
WebAssembly.instantiate(fs.readFileSync(process.argv[1])).then(({instance})=>{
 const f=instance.exports.tsl9_ota_dispatch_14056;
 for(let n=0;n<256;n++){
  const expected=[0x45,0x52,0x53,0x55,0x57].includes(n)?1:0;
  if(f(n)!==expected) throw Error("classification mismatch at "+n);
 }
 process.stdout.write("256 matched");
}).catch(e=>{console.error(e.message);process.exit(1)});'''
results = []
for mode in ('c', 'cpp'):
    obj = build / ('opaque-' + mode + '.o')
    cmd = [str(tool('llvm-objdump')), '-D', '--mattr=+m,+a,+c', '--adjust-vma=0x14056',
           '--section=.tsl9_payload_0', '--start-address=0xc', '--stop-address=0x64', str(obj)]
    text = subprocess.check_output(cmd, text=True)
    decoded = {}
    for line in text.splitlines():
        m = re.match(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+(.*?)\s*$', line)
        if m:
            insn = re.sub(r'\s+', ' ', re.sub(r'\s*<[^>]*>', '', m[2])).strip()
            decoded[int(m[1], 16)] = insn
    if any(decoded.get(pc) != instruction for pc, instruction in expected.items()):
        raise ValueError('Dispatcher instructions changed')
    wasm = out / ('model-' + mode + '.wasm')
    cmd = [str(tool('clang')), '--target=wasm32', '-nostdlib', '-Wl,--no-entry',
           '-Wl,--export=tsl9_ota_dispatch_14056', '-x', 'c' if mode == 'c' else 'c++',
           str(ROOT / 'src/native/receive/ota_dispatch_14056.inc'), '-o', str(wasm)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode:
        raise ValueError('Model compilation failed: ' + proc.stderr[:1000])
    proc = subprocess.run(['node', '-e', js, str(wasm)], capture_output=True, text=True)
    if proc.returncode or proc.stdout != '256 matched':
        raise ValueError('Model test failed: ' + proc.stderr[:1000])
    results.append({'mode': mode, 'inputs_tested': 256, 'instruction_checks': len(expected)})
print(json.dumps({'passed': True, 'results': results, 'target_executed': False,
                  'candidate_image_changed': False, 'model_integrated_into_image': False,
                  'hardware_validated': False}))
