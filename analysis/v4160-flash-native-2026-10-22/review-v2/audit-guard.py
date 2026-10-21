#!/usr/bin/env python3
"""Bounded guard-only probe: actual executable headers; RV32 spawn intercepted."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import struct
import subprocess
import sys

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',required=True,type=Path)
    parser.add_argument('--host-executable',required=True,type=Path)
    parser.add_argument('--rv32-component',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    a=parser.parse_args();project=a.project_root.resolve(strict=True)
    here=Path(__file__).resolve().parent;case=here.parent
    output=a.output.resolve();output.relative_to(here);need(not output.exists(),'Create-only own audit result')
    path=project/'experiments/tsl9-v4160-flash-native/verify_host.py';before=sha(path)
    spec=importlib.util.spec_from_file_location('independent_final_host_guard',path)
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    tree=ast.parse(path.read_text(encoding='utf-8'))
    execute=next(f for f in tree.body if isinstance(f,ast.FunctionDef) and f.name=='execute')
    calls=[c for c in ast.walk(execute) if isinstance(c,ast.Call)]
    guard_lines=[c.lineno for c in calls if isinstance(c.func,ast.Name) and c.func.id=='host_executable']
    spawn_lines=[c.lineno for c in calls if isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Name) and c.func.value.id=='subprocess' and c.func.attr=='run']
    need(len(spawn_lines)==1 and min(guard_lines)<spawn_lines[0]<max(guard_lines),'Guard before launch and stable header afterward')
    launch_sites=[]
    for f in tree.body:
        if not isinstance(f,ast.FunctionDef):continue
        for c in ast.walk(f):
            if isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='execute' and c.args and isinstance(c.args[0],ast.List):
                need(any(k.arg=='host_test' and isinstance(k.value,ast.Constant) and k.value.value is True for k in c.keywords),'Every direct test executable launch opts into guard')
                launch_sites.append({'function':f.name,'line':c.lineno})
    need({s['function'] for s in launch_sites}=={'verify','controls'} and len(launch_sites)==2,'One positive and the six-iteration mutant launch site')
    host=a.host_executable.resolve(strict=True);rv=a.rv32_component.resolve(strict=True)
    pins={str(p):sha(p) for p in (host,rv,Path(sys.executable),path)}
    data=host.read_bytes();need(data[:2]==b'MZ','Actual current Windows host fixture')
    pe=struct.unpack_from('<I',data,60)[0]
    need(data[pe:pe+4]==b'PE\0\0','Independent PE signature')
    machine=struct.unpack_from('<H',data,pe+4)[0];width=64 if struct.unpack_from('<H',data,pe+24)[0]==0x20b else 32
    admitted=runner.host_executable(host)
    need(admitted['format']=='PE' and admitted['machine']==machine and admitted['bits']==width and admitted['sha256']==sha(host),'Actual PE admission agrees with independent header read')
    architecture=next(f for f in tree.body if isinstance(f,ast.FunctionDef) and f.name=='host_architecture')
    need(not architecture.args.args,'Host architecture has no candidate artifact parameter')
    attributes=[n for n in ast.walk(architecture) if isinstance(n,ast.Attribute)]
    need(any(isinstance(n.value,ast.Name) and n.value.id=='sys' and n.attr=='executable' for n in attributes),'Host architecture reads current interpreter')
    pydata=Path(sys.executable).read_bytes();need(pydata[:2]==b'MZ','Actual interpreter is PE on this Windows run')
    pyoff=struct.unpack_from('<I',pydata,60)[0]
    pymachine=struct.unpack_from('<H',pydata,pyoff+4)[0]
    need(pymachine==machine and runner.host_architecture()=={0x8664:'x86_64',0xaa64:'arm64',0x14c:'x86'}[pymachine],'Architecture agrees with independently read current Python header')
    old_machine=platform.machine
    try:
        platform.machine=lambda:''
        fallback=runner.host_executable(host)
        need(fallback==admitted,'Empty platform.machine does not alter interpreter-derived admission')
    finally:platform.machine=old_machine
    need(width==struct.calcsize('P')*8,'Accepted host width matches this Python process')
    raw=rv.read_bytes();need(raw[:4]==b'\x7fELF' and raw[4]==1 and raw[5]==1 and int.from_bytes(raw[18:20],'little')==243,'Actual RV32 component ELF, independent read')
    original_run=runner.subprocess.run;spawn_calls=[]
    def forbidden(*args,**kwargs):
        spawn_calls.append(args);raise AssertionError('A target launch was attempted')
    try:
        runner.subprocess.run=forbidden
        try:runner.execute([rv],here,'MUST-NOT-EXIST',{},host_test=True)
        except ValueError as error:
            rejection=str(error);need('RISC-V' in rejection,'Explicit RV32 machine rejection')
        else:raise ValueError('RV32 artifact admitted')
    finally:runner.subprocess.run=original_run
    need(not spawn_calls and not (here/'MUST-NOT-EXIST.log').exists(),'RV32 rejected before any subprocess/log path')
    # This command runs only the old Python hash checker, never its archived tests.
    oldcheck=subprocess.run([sys.executable,'-B',case/'review/check-review.py','--project-root',project],capture_output=True,timeout=30)
    oldtext=(oldcheck.stdout+oldcheck.stderr).decode('utf-8',errors='replace')
    need(oldcheck.returncode!=0 and 'Reviewed model/helper input experiments/tsl9-v4160-flash-native/verify_host.py' in oldtext,'Old checker intentionally rejects the changed runner pin')
    need(all(sha(Path(n))==v for n,v in pins.items()) and sha(path)==before,'All actually read artifacts and final runner unchanged')
    result={'schema':'ID2966-independent-host-guard-audit-v2','passed':True,'runner_sha256':before,'input_pins':pins,'python_host_width':struct.calcsize('P')*8,'host_architecture_from_current_python_only':True,'actual_host_PE':admitted,'empty_platform_machine_admission':fallback,'actual_RV32_ELF':{'sha256':sha(rv),'bytes':len(raw),'machine':243,'bits':32},'RV32_execute_guard_rejection':rejection,'RV32_subprocess_calls':0,'guard_order_lines':{'guard':guard_lines,'spawn':spawn_lines},'guarded_test_launch_sites':launch_sites,'old_checker_rejected_new_runner':True,'old_checker_exit':oldcheck.returncode,'old_checker_output_sha256':hashlib.sha256(oldcheck.stdout+oldcheck.stderr).hexdigest(),'target_execution':False,'ISA_emulation':False,'hardware':False,'network':False}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'passed':True,'receipt':str(output),'sha256':sha(output),'target_execution':False}))
if __name__=='__main__':main()
