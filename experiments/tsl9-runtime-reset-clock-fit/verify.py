#!/usr/bin/env python3
"""Strict offline reset/caller +232B clock composition evidence; no firmware BIN."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
CAPTURE=dict(enabled=False,root=None,hashes={})


def need(ok,message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def audit_open(event,args):
    if event=='open' and CAPTURE['enabled'] and isinstance(args[0],str):
        path=Path(args[0]).resolve()
        if path.is_relative_to(CAPTURE['root']) and not path.is_relative_to(HERE/'build') and path.is_file():
            if path not in CAPTURE['hashes']:
                CAPTURE['enabled']=False
                try:
                    CAPTURE['hashes'][path]=sha(path)
                finally:
                    CAPTURE['enabled']=True


sys.addaudithook(audit_open)


def inspect(root,folder,tool_dir):
    producer=runpy.run_path(str(HERE/'probe.py'))
    prior,tools,header,parent,shared,flag_owner=producer['load'](root,tool_dir)
    prefix=runpy.run_path(str(root/'experiments/tsl9-boot-clock-prefix/verify.py'))
    fall=runpy.run_path(str(root/producer['FALL']/'verify.py'))
    native_reset,ir_gate,negatives=(parent[k] for k in ('native_reset','ir_gate','negatives'))
    decode,source,initializer,image,original_facts=parent['original'](root,prior)
    # Keep frozen readers untouched. New receipts use repository-relative keys;
    # existing local receipts remain immutable records of their original run.
    original_facts={**original_facts,'source_dependencies':{
        Path(name).resolve().relative_to(root).as_posix():pin
        for name,pin in original_facts['source_dependencies'].items()}}
    compile_record=json.loads((folder/'compile-receipt.json').read_bytes())
    need(set(compile_record)=={'schema','mode','clock_source','inputs','commands','target_execution','ISA_emulation','BIN_generated'}
         and all(compile_record[k] is False for k in ('target_execution','ISA_emulation','BIN_generated')),
         'Exact offline producer scope')
    need(compile_record['schema']=='TSL9-runtime-reset-clock-fit-probe-v1'
         and compile_record['mode'] in ('c','cpp'),'Known compiler producer')
    policy=compile_record['clock_source']
    sources=producer['sources'](root,policy)
    expected_inputs=producer['inputs'](root,policy,prior,tools,header,parent,shared)
    need(compile_record['inputs']==expected_inputs,'Exact sources/origins/header/tool/reader input closure')
    jobs=producer['recipes'](root,folder,compile_record['mode'],policy,prior,tools,flag_owner)
    for unit,path in {**sources,'prefix':root/'experiments/tsl9-boot-clock-prefix/src/clock_prefix.c'}.items():
        text=(folder/(unit+'.d')).read_text().replace('\\\n',' ')
        target,sep,tail=text.partition(':')
        deps={Path(re.sub(r'\\(.)',r'\1',t)).resolve() for t in re.findall(r'(?:\\.|[^\s])+',tail)}
        need(sep and target==unit+'.o' and deps==({path} if unit=='ports' else {path,header}),
             'Exact actual compiler MD closure: '+unit)
    need(compile_record['commands']==[
        dict(label=k,argv=[shared['portable'](x,root,tools,header) for x in v],exit=0,
             log_sha256=sha(folder/(k+'.log'))) for k,v in jobs],
         'Complete successful compiler/link/reference/disassembly recipes and logs')
    expected={label+'.log' for label,_ in jobs}|{
        *[unit+suffix for unit in (*sources,'prefix') for suffix in ('.o','.d')],
        *[unit+'.ll' for unit in (*sources,'prefix','register')],
        'COMPONENT-ONLY-NOT-FIRMWARE.elf','compile-receipt.json'}
    need(all(p.is_file() for p in folder.iterdir()) and
         {p.name for p in folder.iterdir() if p.name!='verification.json'}==expected,
         'Exact complete build artifact inventory; no extra files or directories')
    elf_path=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
    E=runpy.run_path(str(root/prior['PARSER']))['ELF'];elf=E(elf_path)
    need(elf.kind==2 and elf.flags==1 and not elf.relocations,'Actual linked RV32/RVC ELF without remaining relocations')
    und=[s['name'] for s in elf.symbols if s['name'] and s['index']==0 and s['info']>>4 in (1,2)]
    absolute=[s['name'] for s in elf.symbols if s['index']==0xfff1 and s['info']>>4 in (1,2)]
    need(not und and not absolute,'No unresolved ELF symbol or invented ABS provider')
    alloc=[s for s in elf.sections if s['size'] and s['flags']&2]
    need([(s['name'],s['address'],s['size'],s['flags'],s['type']) for s in alloc]==[
        ('.reset',0x186aa,138,6,1),('.clock',0x1874a,232,6,1),('.initializer',0x1ab60,128,2,1),
        ('.ram',0x20004000,35160,3,8),('.stack',0x2000fff0,16,3,8)],'Only declared real code/data/NOBITS allocations')
    funcs={s['name']:s for s in elf.symbols if s['info']&15==2 and s['size']}
    expected={'tsl9_runtime_reset_entry':(0x186aa,20),'tsl9_runtime_reset_memory':(0x186be,118),
              'tsl9_clock_prefix_entry':(0x1874a,12),'tsl9_clock_prefix_body':(0x18756,220)}
    need({n:(s['value'],s['size']) for n,s in funcs.items()}==expected and all(s['info']>>4==1 for s in funcs.values()),'Four genuine functions with fixed placements')
    need(struct.unpack_from('<I',elf.raw,24)[0]==0x186aa,'Actual ELF reset entry')
    native=elf.data(elf.byname['.reset']);contract=native_reset(native,decode,source)
    clock=elf.data(elf.byname['.clock'])
    need(digest(clock)==fall['CODE_SHA'],'Independently reviewed232B clock bytes in actual composition')
    clock_functions=[funcs[n] for n in fall['SYMS']]
    need(elf.function_bytes(clock_functions[0])+elf.function_bytes(clock_functions[1])==clock,
         'Actual clock section equals two adjacent real functions')
    _,old_codes,_=prefix['inspect_elf'](folder/'prefix.o',folder/'prefix-object.log',prior,root,False)
    clock_object,_,_=fall['inspect_elf'](folder/'clock.o',folder/'clock-object.log',root,prior,prefix,old_codes,False)
    clock_IR=(folder/'clock.ll').read_text()
    old_IR=(folder/'prefix.ll').read_text();register_IR=folder/'register.ll'
    clock_IR_facts=fall['ir_gate'](clock_IR,old_IR,register_IR,prefix,prior)
    clock_codes=[elf.function_bytes(f) for f in clock_functions]
    clock_values=[f['value'] for f in clock_functions]
    fall['critical'](clock_codes,clock_values,True,old_codes)
    clock_tests=fall['negatives'](clock_codes,clock_values,old_codes,clock_IR,old_IR,register_IR,prefix,prior)
    edges=runpy.run_path(str(root/producer['FALL']/'source_edges.py'))['inspect'](root)
    need(elf.data(elf.byname['.initializer'])==initializer,'All128 initializer bytes equal original source')
    ir=(folder/'memory.ll').read_text(encoding='utf-8');ir_facts=ir_gate(ir,prefix,mode=compile_record['mode'])
    # Every LLVM AX instruction must read back to the same ELF bytes.
    got={};section=None
    for line in (folder/'linked.log').read_text().splitlines():
        h=re.match(r'Disassembly of section (.+):',line)
        if h:section=h[1]
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)',line)
        if not m:continue
        pc=int(m[1],16);raw=bytes.fromhex(m[2]);need(section in ('.reset','.clock') and m[3]!='<unknown>','Only reviewed executable disassembly')
        key=(section,pc);need(key not in got,'No duplicate LLVM row');got[key]=raw
    for name in ('.reset','.clock'):
        s=elf.byname[name];at=s['address'];out=b''
        while at<s['address']+s['size']:
            need((name,at) in got,'Complete LLVM byte coverage');b=got[(name,at)];out+=b;at+=len(b)
        need(out==elf.data(s),'Whole actual LLVM/ELF byte equality')
    need(len(got)==131,'38 reset plus93 clock instructions')
    # Object readback preserves every function's code, allowing only real linker patches.
    object_facts=[]
    role_functions={'memory':{'tsl9_runtime_reset_memory':118},'ports':{'tsl9_runtime_reset_entry':20},'data':{},
                    'clock':{'tsl9_clock_prefix_entry':12,'tsl9_clock_prefix_body':220}}
    role_und={'memory':['tsl9_clock_prefix_entry'],'ports':['tsl9_runtime_reset_memory','tsl9_runtime_reset_ram','tsl9_runtime_reset_stack_top'],'data':[],'clock':[]}
    role_relocations={
        'memory':[('.text.tsl9_runtime_reset_memory',98,17,'tsl9_clock_prefix_entry',0)],
        'ports':[('.text.tsl9_runtime_reset_entry',0,23,'tsl9_runtime_reset_ram',0),
                 ('.text.tsl9_runtime_reset_entry',4,24,'.Lreset_gp',0),
                 ('.text.tsl9_runtime_reset_entry',8,23,'tsl9_runtime_reset_stack_top',0),
                 ('.text.tsl9_runtime_reset_entry',12,24,'.Lreset_sp',0),
                 ('.text.tsl9_runtime_reset_entry',16,17,'tsl9_runtime_reset_memory',0)],
        'data':[],
        'clock':[]}
    for unit in sources:
        obj=E(folder/(unit+'.o'));need(obj.kind==1 and obj.flags==1,'Actual object kind')
        sym=[s for s in obj.symbols if s['info']&15==2 and s['size']]
        need({s['name']:s['size'] for s in sym}==role_functions[unit] and all(s['info']>>4==1 and s['value']==0
             and obj.sections[s['index']]['name']=='.text.'+s['name'] for s in sym),'Exact genuine object function inventory/zero section-relative offsets: '+unit)
        actual_und=sorted(s['name'] for s in obj.symbols if s['name'] and s['index']==0 and s['info']>>4 in (1,2))
        need(actual_und==role_und[unit] and not any(s['index']==0xfff1 and s['info']>>4 in (1,2) for s in obj.symbols),'Exact object UND/no ABS provider roles: '+unit)
        rel=[(x['owner'],x['offset'],x['type'],x['symbol']['name'],x['addend']) for x in obj.relocations]
        need(rel==role_relocations[unit],'Exact semantic relocation roles: '+unit)
        actual_alloc=[(s['name'],s['size'],s['flags'],s['type']) for s in obj.sections if s['size'] and s['flags']&2]
        expected_alloc=[('.text.'+n,size,6,1) for n,size in role_functions[unit].items()]
        if unit=='data':
            expected_alloc=[('.rodata.tsl9_reset_initializer',128,2,1),('.bss.tsl9_reset_ram',35160,3,8),('.bss.tsl9_reset_stack',16,3,8)]
            need(obj.data(obj.byname['.rodata.tsl9_reset_initializer'])==initializer,'Actual data object original initializer bytes')
        need(sorted(actual_alloc)==sorted(expected_alloc),'Complete object section/data/NOBITS inventory: '+unit)
        need(all(s['alignment']==(16 if s['name']=='.bss.tsl9_reset_stack' else 4 if unit=='data' else 2)
             for s in obj.sections if s['size'] and s['flags']&2),'Exact object allocation alignments')
        defined={s['name'] for s in obj.symbols if s['name'] and s['index'] not in (0,0xfff1) and s['info']>>4==1}
        need(defined==(set(role_functions[unit]) if unit!='data' else {'tsl9_runtime_reset_initializer','tsl9_runtime_reset_ram','tsl9_runtime_reset_stack'}),
             'Only genuine declared global definitions')
        for f in sym:
            need(f['name'] in funcs,'Object function is a real final definition')
            original_bytes=bytearray(obj.function_bytes(f));linked_bytes=elf.function_bytes(funcs[f['name']])
            patches={x['offset'] for x in obj.relocations if x['owner']==obj.sections[f['index']]['name']}
            for at in patches:original_bytes[at:at+4]=linked_bytes[at:at+4]
            need(bytes(original_bytes)==linked_bytes,'Only actual relocation sites differ from object code')
        object_facts.append(dict(unit=unit,functions=[f['name'] for f in sym],relocations=len(obj.relocations)))
    overlap=image[0x10834:0x1083a]
    need(overlap==bytes.fromhex('37170240 5c43') and
         elf.byname['.clock']['address']+elf.byname['.clock']['size']==0x18832,
         'Candidate extent is before the unchanged original next-function boundary')
    need(image[0x10830:0x10834]==bytes.fromhex('02c661bf') and clock[-2:]==bytes.fromhex('8280'),
         'New RET replaces original cold SW; residual cold J is not padding')
    checks=negatives(native,decode,source,ir,prefix)
    return dict(passed=True,mode=compile_record['mode'],reset=contract,memory_IR=ir_facts,
                linked_executable_bytes=370,linked_executable_instructions=131,objects=object_facts,
                negative_controls=checks,clock_negative_controls=clock_tests,clock_IR=clock_IR_facts,
                clock_object=clock_object,clock_source=policy,original=original_facts,
                next_function_overlap_bytes=0,residual_original_tail=dict(VA='[0x18832,0x18834)',raw='61bf',free_space=False),
                bounded_original_incoming_scan=edges,actual_ELFs=6,
                normal_no_interference_projection=dict(GP='0x20004000',SP='0x20010000',A0='0x2000c958',A1='0x2000c958',RA='0x18724',T0='0x9008',MEPC='0x9008',
                    condition='original initializer reads/writes succeed, GP stable, no asynchronous interference, clock returns normally; A2-A5 follow the separate clock source contract'),
                ELF_link_closed=True,runtime_provider_closure=False,firmware_ready=False,
                blockers=['residual original cold jump18832..18834 and indirect/resident/BOOT/IRQ incoming behavior unproved','vector8038/main9008/resident40000 not implemented in this ELF','changed GP-sample PCs, source setup order, AUIPC intermediates and clock instruction timing; full IRQ/fault equivalence unproved','physical RAM/stack/ROM/hardware and complete APP placement unproved'],
                target_execution=False,ISA_emulation=False,BIN_generated=False)

def main():
    started=sha(Path(__file__))
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--build-root',type=Path)
    p.add_argument('--clock-source',choices=('origin','curated'))
    p.add_argument('--replay',type=Path)
    p.add_argument('--require-firmware-ready',action='store_true')
    a=p.parse_args();root=a.project_root.resolve();tool_dir=a.tool_dir.resolve()
    need((a.build_root is None)!=(a.replay is None),'Choose fresh build or read-only replay')
    if a.build_root:
        policy=a.clock_source or 'curated'
        subprocess.run([sys.executable,'-B',str(HERE/'probe.py'),'--project-root',str(root),
                        '--tool-dir',str(tool_dir),'--build-root',str(a.build_root),
                        '--clock-source',policy],check=True,timeout=120)
        folders=[a.build_root.resolve()/n for n in ('c','cpp')]
    else:
        need(a.clock_source is None and a.replay.name=='verification.json' and
             a.replay.resolve().is_relative_to(HERE/'build'),'Owned replay with recorded source policy')
        folders=[a.replay.resolve().parent]
    for folder in folders:
        need(folder.is_relative_to(HERE/'build'),'Owned diagnostic artifacts')
        CAPTURE.update(enabled=True,root=root,hashes={})
        try:
            findings=inspect(root,folder,tool_dir)
        finally:
            CAPTURE['enabled']=False
        need(all(sha(path)==pin for path,pin in CAPTURE['hashes'].items()),
             'All actual project readers/inputs stable before and after analysis')
        need(sha(Path(__file__))==started,'Unchanged verifier throughout analysis')
        dependencies={path.relative_to(root).as_posix():pin for path,pin in sorted(CAPTURE['hashes'].items())}
        artifacts={path.name:sha(path) for path in sorted(folder.iterdir()) if path.name!='verification.json'}
        record=dict(schema='TSL9-runtime-reset-clock-fit-static-v1',verifier_sha256=started,
                    source_evidence_dependencies=dependencies,findings=findings,artifacts=artifacts)
        if a.replay:
            need(json.loads(a.replay.read_bytes())==record,'Exact full original/source/artifact/finding replay')
        else:
            (folder/'verification.json').write_bytes((json.dumps(record,indent=2)+'\n').encode())
        print(json.dumps(dict(mode=findings['mode'],clock_source=findings['clock_source'],passed=True,
                              reset_bytes=138,clock_bytes=232,executable_bytes=370,instructions=131,
                              reset_negative_controls=len(findings['negative_controls']),
                              clock_negative_controls=len(findings['clock_negative_controls']),
                              firmware_ready=False,target_execution=False,BIN_generated=False)))
        if a.require_firmware_ready:
            need(findings['firmware_ready'],'Full APP, cold-tail, IRQ/fault, resident and physical closure unproved')


if __name__=='__main__':
    main()
