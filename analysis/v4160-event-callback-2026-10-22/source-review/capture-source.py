"""Create-only local LLVM text/reference capture; static tool invocation only."""
import argparse,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OWNER='.text.tsl9v4160.callback_8614'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--llvm-objdump',required=True,type=Path);p.add_argument('--carrier',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve();fw=a.firmware.resolve();carrier=a.carrier.resolve();tool=a.llvm_objdump.resolve()
    assert sha(fw)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
    blob=fw.read_bytes()[0x614:0x88c];assert len(blob)==632 and hashlib.sha256(blob).hexdigest()=='3e21432057f673abea404541e0745937d894448b492478b5fed5775e91b398bf'
    E=load('callback_capture_elf',case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py').ELF;e=E(carrier);assert e.data(e.byname[OWNER])==blob
    cmd=[str(tool),'--disassemble','--section='+OWNER,str(carrier)];x=subprocess.run(cmd,capture_output=True,timeout=30,check=True);rows=load('callback_independent_llvm',HERE/'llvm_fields.py').parse(x.stdout.decode('utf-8'));assert b''.join(bytes.fromhex(r['raw_hex']) for r in rows)==blob
    base=load('callback_immutable_base',case(root,'v4160-ota-tx-2026-10-22')/'source-review/raw.py').decode;raw=load('callback_raw_extensions',HERE/'raw.py');actual=[];at=0
    while at<len(blob):r=raw.decode(blob[at:],0x8614+at,base);actual.append(r);at+=r['bytes']
    assert actual==rows,'Independent raw-bit fields equal normalized LLVM operands'
    for name,data in [('llvm-disassembly.txt',x.stdout),('instructions.json',(json.dumps(rows,indent=2)+'\n').encode()),('capture.json',(json.dumps(dict(argv=cmd,exit=x.returncode,carrier_sha256=sha(carrier),tool_sha256=sha(tool),firmware_sha256=sha(fw),slice_sha256=hashlib.sha256(blob).hexdigest(),instructions=len(rows),static_only=True),indent=2)+'\n').encode())]:
        with (HERE/name).open('xb') as f:f.write(data)
    print(json.dumps(dict(passed=True,bytes=len(blob),instructions=len(rows),branch_instructions=sum(r['target'] is not None for r in rows),memory_instructions=sum(r['memory_width'] is not None for r in rows),opaque_calls=sum(r['op']=='jalr' and r['rd']==1 for r in rows))))
if __name__=='__main__':main()
