#!/usr/bin/env python3
"""Capture original static operands; no target execution or firmware generation."""
import argparse,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BODY='693eba9e21b786525b457b538d998a997a601ee46327621a2302ede1b2f274c5'
OWNER='.text.tsl9v4160.ota_handler_9c4a'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def context(root):
    old=case(root,'v4160-event-callback-2026-10-22')/'source-review/check-source.py'
    need(sha(old.parent/'seal.json')=='c9edde476232c0c0e018c08e54d2d9d9a9afa20839d5e19a53f5ffa752e0e1c5','Immutable original field-extension proof')
    for name,pin in json.loads((old.parent/'seal.json').read_bytes())['members'].items():need(sha(old.parent/name)==pin,'Immutable field extension member '+name)
    need(sha(old)=='3a4f54667035a5ed722d59befa24ba0366e832d1a300fed725f49cbce675f185','Pinned field reader entry')
    base,E=load('handler_prior_field_reader',old).context(root);extension=load('handler_OR_SP_fields',HERE/'raw.py')
    return lambda raw,pc:extension.decode(raw,pc,base),E
def rows(blob,decode):
    result=[];at=0
    while at<len(blob):
        r=decode(blob[at:],0x9c4a+at);need(r['bytes'] in (2,4) and at+r['bytes']<=len(blob),'Whole raw original instruction');result.append(r);at+=r['bytes']
    need(at==530,'Exact handler extent');return result
def role(e,s):return dict(name=s['name'],owner=e.sections[s['index']]['name'] if 0<s['index']<len(e.sections) else 'ABS' if s['index']==65521 else 'UND',offset=s['value'],bytes=s['size'],info=s['info'],other=s['other'])
def object_roles(e):
    owner=e.byname[OWNER];rs=[dict(owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend'],symbol=role(e,r['symbol'])) for r in e.relocations if r['owner']==OWNER or r['symbol']['index']==owner['index']]
    return dict(owner_metadata={k:owner[k] for k in ('name','type','flags','size','alignment')},owner_symbols=sorted([role(e,s) for s in e.symbols if s['index']==owner['index']],key=lambda r:json.dumps(r,sort_keys=True)),RELA=sorted(rs,key=lambda r:json.dumps(r,sort_keys=True)))
def write(name,value):
    data=value if isinstance(value,bytes) else (json.dumps(value,indent=2)+'\n').encode('utf-8')
    with (HERE/name).open('xb') as f:f.write(data)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);p.add_argument('--object',required=True,type=Path);p.add_argument('--elf',required=True,type=Path);p.add_argument('--objdump',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve(strict=True)
    need(not (HERE/'seal.json').exists(),'Never alter a closed source bundle');need(sha(a.firmware)==FW and a.firmware.stat().st_size==76800,'Exact original official firmware')
    decode,E=context(root);blob=a.firmware.read_bytes()[0x1c4a:0x1e5c];need(hashlib.sha256(blob).hexdigest()==BODY,'Original handler digest')
    e=E(a.object);linked=E(a.elf);need(e.kind==1 and linked.kind==2 and e.data(e.byname[OWNER])==linked.data(linked.byname[OWNER])==blob,'Actual original carrier and LLVM witness preserve every source byte')
    need(sha(a.objdump)=='de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa','Known static LLVM tool')
    argv=[str(a.objdump.resolve()),'--mattr=+m,+a,+c,+zicsr','-d','--start-address=0x9c4a','--stop-address=0x9e5c',str(a.elf.resolve())]
    run=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False);need(run.returncode==0,'Static LLVM capture success')
    parsed=load('handler_independent_LLVM_fields',HERE/'llvm_fields.py').parse(run.stdout.decode('utf-8'));actual=rows(blob,decode);need(actual==parsed,'Every raw operand/order equals independent LLVM text')
    write('llvm-disassembly.txt',run.stdout.replace(b'\r\n',b'\n'));write('instructions.json',actual);write('carrier-roles.json',dict(source_object_sha256=sha(a.object),roles=object_roles(e)))
    write('capture.json',dict(schema='ID2966-OTA-handler-original-static-capture-v1',firmware_sha256=FW,source_base=0x8000,entry=0x9c4a,end_exclusive=0x9e5c,bytes=len(blob),body_sha256=BODY,instructions=len(actual),argv=argv,exit=run.returncode,objdump_sha256=sha(a.objdump),source_object_sha256=sha(a.object),linked_ELF_sha256=sha(a.elf),static_only=True,target_execution=False,ISA_emulation=False))
    print(json.dumps(dict(passed=True,bytes=len(blob),instructions=len(actual))))
if __name__=='__main__':main()
