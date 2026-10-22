#!/usr/bin/env python3
"""Create-only static App/conditional-candidate views; no compiler/HOST run."""
import argparse,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def write(name,value):
    data=value if isinstance(value,bytes) else (json.dumps(value,indent=2)+'\n').encode('utf-8')
    with (HERE/name).open('xb') as f:f.write(data)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);p.add_argument('--object',required=True,type=Path);p.add_argument('--elf',required=True,type=Path);p.add_argument('--objdump',required=True,type=Path);p.add_argument('--r2',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve(strict=True)
    s=importlib.util.spec_from_file_location('bounded_callee_static_review',HERE/'review.py');R=importlib.util.module_from_spec(s);s.loader.exec_module(R)
    R.need(not (HERE/'seal.json').exists(),'Never alter a closed review');R.need(R.sha(a.firmware)==R.FW,'Original source identity');decode,E,parse=R.context(root)
    R.need(R.sha(a.elf)==R.read(HERE/'reference-pins.json')['actual_App_linked_ELF_sha256'],'Known actual full App witness identity')
    fw=a.firmware.read_bytes();app=fw[0x12ba:0x1334];obj=E(a.object);elf=E(a.elf)
    for name,body in (('.text.tsl9v4160.direct_closure_92ba',app[:56]),('.text.tsl9v4160.ota_handler_92f2',app[56:])):R.need(obj.data(obj.byname[name])==elf.data(elf.byname[name])==body,'App owner bytes equal actual original')
    R.need(R.sha(a.objdump)=='de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa','Pinned static LLVM tool')
    argv=[str(a.objdump.resolve()),'--mattr=+m,+a,+c,+zicsr','-d','--start-address=0x92ba','--stop-address=0x9334',str(a.elf.resolve())];run=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False);R.need(run.returncode==0,'Read-only LLVM App disassembly');ar=R.rows(app,0x92ba,decode);R.need(ar==parse(run.stdout.decode('utf-8')),'Every App operand independently agrees with LLVM text')
    candidates=R.candidate_inputs(root);copy=candidates[0]['body'];cr=R.rows(copy,0x20000332,decode);R.local_contract(ar,cr)
    folder=R.case(root,'wch-resident-candidate-2026-10-21');source=folder/'carrier'/R.read(HERE/'reference-pins.json')['candidate_files']['carrier']['segment']
    # -N prevents startup configuration; pDj formats static bytes only. Never issue ae/ESIL or stepping commands.
    rargv=[str(a.r2.resolve()),'-N','-q','-n','-a','riscv','-b','32','-m','0x1ffffd50','-c','pDj 58 @ 0x20000332;q',str(source)]
    view=subprocess.run(rargv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False);R.need(view.returncode==0,'Static candidate instruction display');rr=json.loads(view.stdout);sanitized=[{k:x[k] for k in ('addr','size','bytes','opcode')} for x in rr];R.need(len(sanitized)==18,'Bounded copy view18 rows')
    normal=[]
    for x in sanitized:
        if x['opcode']=='fence.i':
            R.need(x['bytes']=='0f100000','Actual canonical FENCE.I encoding');normal.append(decode(bytes.fromhex(x['bytes']),x['addr']))
        else:
            text=f"{x['addr']:x}: {' '.join(x['bytes'][i:i+2] for i in range(0,len(x['bytes']),2))}  {x['opcode']}\n";normal.extend(parse(text))
    R.need(normal==cr,'Every candidate raw operand equals independent static display; no ESIL used')
    write('app-llvm.txt',run.stdout.replace(b'\r\n',b'\n'));write('app-instructions.json',ar);write('copy-instructions.json',cr);write('candidate-static-display.json',sanitized)
    write('app-carrier.json',dict(source_object_sha256=R.sha(a.object),roles=R.capture_roles(obj)))
    write('capture.json',dict(schema='UID-callee-actual-static-capture-v1',App_bytes=len(app),App_rows=len(ar),App_linked_ELF_sha256=R.sha(a.elf),source_object_sha256=R.sha(a.object),LLVM=dict(argv=argv,exit=run.returncode,sha256=R.sha(a.objdump)),candidate_rows=len(cr),r2=dict(argv=rargv,exit=view.returncode,sha256=R.sha(a.r2),ESIL_executed=False),candidate_bodies_equal=True,compiler_or_HOST_run=False,target_execution=False,ISA_emulation=False,network=False,hardware=False))
    print(json.dumps(dict(passed=True,App_bytes=len(app),App_rows=len(ar),candidate_copy_bytes=len(copy),candidate_rows=len(cr))))
if __name__=='__main__':main()
