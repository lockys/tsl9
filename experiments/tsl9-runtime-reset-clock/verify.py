#!/usr/bin/env python3
"""Static reset/clock composition checks. No target execution or BIN generation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = 'experiments/tsl9-boot-clock-registers/verify.py'
PINS = {
    BASE:'096660430ae0aa0f44813192aa30c49c958b8180e4123249a5aa36eeab11a7a8',
    'experiments/tsl9-boot-clock-prefix/verify.py':'8befcde0b7afe9c890ad85207912e9fa2bc7ac9265334af090eff36cb65890bf',
    'analysis/boot2580-reset-resident-2026-10-22/check.py':'00c4b2812b7f50c7d6220430b70d82bdbdccff6a2bc9b4f58422477ab5b04e0d',
    'experiments/tsl9-runtime-reset-clock/src/reset_memory.c':'cd2d0975bdab14759f41f096ce89532535544f10373532b0adb5e2e5455ebaf1',
    'experiments/tsl9-runtime-reset-clock/src/reset_ports.c':'5419c3d669183107771f88231080e517458e757a63868f5971b2db7f14ed9ae8',
    'experiments/tsl9-runtime-reset-clock/src/reset_data.c':'02aad93670679ef0c8c472dc998e3d41963ba33d280a5ec6baa336a3173ed1ec',
    'experiments/tsl9-runtime-reset-clock/component.ld':'d37a24f82843d4e19a7f87dca15cac070e7b53327a781db4cfb9a4b66d752b9c',
    'experiments/tsl9-runtime-reset-clock/probe.py':'76755454ec4b52cccecd11f16c7f8884ca8020ec1bee6bd91b7d913c5a787d53',
}
RESET_SHA = '9507502c874a03e2c64a28b186a1f56aba9e85c9989dbf0cc053dabc4045bb4d'
DATA_SHA = 'd2f2eac71b3c4f04686d1179aebb430b70088394c46552914bec908c98558e0c'
IR_SHAS = {'c':'53432073f678df194b7cce7bd1d526dc4d93aadee72aebce977ba56cb634d09c',
           'cpp':'4da0bc90734b774d68ad287b7f7f9bffd5853bba00fc4af785bb9ac677ed97f4'}
CLOCK_SHA = '2d5529329f757de58bf85ae1d5671125836bc740b813d89df163cf5bbe7d48af'
CAPTURE = {'enabled':False,'paths':set(),'root':None}


def audit_open(event,args):
    if event=='open' and CAPTURE['enabled'] and isinstance(args[0],str):
        p = Path(args[0]).resolve()
        if p.is_relative_to(CAPTURE['root']) and p.is_file():
            CAPTURE['paths'].add(p)


sys.addaudithook(audit_open)


def need(ok,message):
    if not ok:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def digest(b):
    return hashlib.sha256(b).hexdigest()


def rows(blob,base,decode):
    result=[];at=0
    while at<len(blob):
        row=decode(blob[at:],base+at)
        need(row['bytes'] in (2,4) and at+row['bytes']<=len(blob),'Bounded complete instruction')
        result.append(row);at+=row['bytes']
    return result


def expect(by,pc,**fields):
    need(pc in by and all(by[pc].get(k)==v for k,v in fields.items()),'Operand/flow contract at '+hex(pc))


def pair(by,pc,rd):
    first,second=by[pc],by[pc+4]
    expect(by,pc,rd=rd)
    expect(by,pc+4,op='addi',rd=rd,rs1=rd)
    need(first['op'] in ('auipc','lui'),'Address producer pair')
    return ((pc if first['op']=='auipc' else 0)+first['immediate']+second['immediate'])&0xffffffff


def original(root,prior):
    CAPTURE.update(enabled=True,paths=set(),root=root)
    try:
        reader=runpy.run_path(str(root/'analysis/boot2580-reset-resident-2026-10-22/check.py'))
        decode=reader['decoder'](root)
        firmware=root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
        need(sha(firmware)==prior['RUNTIME_SHA'],'Exact original Runtime')
        image=firmware.read_bytes()
        reset=image[0x106aa:0x10734]
        need(len(image)==76800 and digest(reset)==RESET_SHA,'Original138B reset source')
        source=rows(reset,0x186aa,decode);by={r['PC']:r for r in source}
        need(len(source)==37 and pair(by,0x186aa,3)==0x20004000 and pair(by,0x186b2,2)==0x20010000,'Original GP/SP formation')
        need(pair(by,0x186ba,10)==0x1ab60 and pair(by,0x186e2,11)==0x2000c958,'Original initializer/BSS endpoints')
        expect(by,0x186c2,op='addi',rd=11,rs1=3,immediate=0)
        expect(by,0x186c6,op='addi',rd=12,rs1=3,immediate=128)
        expect(by,0x186de,op='addi',rd=10,rs1=3,immediate=128)
        expect(by,0x18720,op='jal',rd=1,target=0x1874a)
        need(pair(by,0x18724,5)==0x9008,'Original MEPC destination formation')
        expect(by,0x18730,op='jal',rd=0,target=0x40000)
        initializer=image[0x12b60:0x12be0]
        need(len(initializer)==128 and digest(initializer)==DATA_SHA,'Original complete initializer')
        need(image[0x10734:0x10738]==bytes.fromhex('73002030'),'Adjacent original MRET, not fallthrough')
        contract=prior['originals'](root,firmware.parent/'ID-2580-V1.0.00-decoded.bin',firmware)
    finally:
        CAPTURE['enabled']=False
    dependencies={str(p):sha(p) for p in sorted(CAPTURE['paths'])}
    return decode,reset,initializer,image,dict(original_reset_rows=source,clock_source_contract=contract,source_dependencies=dependencies)


def native_reset(blob,decode,source):
    need(len(blob)==138 and blob[:16]==source[:16],'Original GP/SP raw prefix,138B reset allocation')
    decoded=rows(blob,0x186aa,decode);by={r['PC']:r for r in decoded}
    need(len(decoded)==38,'Actual38-instruction reset')
    expect(by,0x186ba,op='jal',rd=0,target=0x186be)
    expect(by,0x186be,op='mv',rd=11,rs1=3)
    expect(by,0x186c0,op='addi',rd=12,rs1=3,immediate=128)
    expect(by,0x186c4,op='lui',rd=10,immediate=0x1b000)
    expect(by,0x186c6,op='addi',rd=10,rs1=10,immediate=-1184)
    need(0x1b000+by[0x186c6]['immediate']==0x1ab60,'Original initializer numeric address')
    expect(by,0x186de,op='addi',rd=10,rs1=3,immediate=128)
    need(pair(by,0x186e2,11)==0x2000c958,'Original BSS end')
    for lo,hi in [(0x186ca,0x186de),(0x186ea,0x18710),(0x18718,0x18724),(0x1872c,0x18734)]:
        need(blob[lo-0x186aa:hi-0x186aa]==source[lo-0x186aa:hi-0x186aa],'Exact original memory/CSR/transfer kernel '+hex(lo))
    expect(by,0x186ca,op='bgeu',rs1=11,rs2=12,target=0x186de)
    expect(by,0x186da,op='bltu',rs1=11,rs2=12,target=0x186ce)
    expect(by,0x186ea,op='bgeu',rs1=10,rs2=11,target=0x186f8)
    expect(by,0x186f4,op='bltu',rs1=10,rs2=11,target=0x186ee)
    need(pair(by,0x18710,5)==0x8038 and by[0x18718]['immediate']==3,'MTVEC base/OR bits')
    for pc,csr,op in [(0x186fa,0xbc0,'CSRRW_write'),(0x18700,0x804,'CSRRW_write'),
                      (0x1870c,0x300,'CSRRS_set_bits'),(0x1871c,0x305,'CSRRW_write'),(0x1872c,0x341,'CSRRW_write')]:
        expect(by,pc,op=op,CSR=csr,rd=0,rs1=5)
    expect(by,0x18720,op='jal',rd=1,target=0x1874a)
    need(pair(by,0x18724,5)==0x9008,'Normal MEPC9008')
    expect(by,0x18730,op='jal',rd=0,target=0x40000)
    need([r['PC'] for r in decoded if r['rd']==2]==[0x186b2,0x186b6],'No C frame, stack spill or SP change')
    need(all(r['rd'] in (None,0,1,2,3,5,10,11,12) for r in decoded),'Only original reset register bank')
    need(not any(r['op'] in ('ret','mret') for r in decoded),'No invented reset return/MRET')
    return dict(bytes=138,instructions=38,GP='0x20004000',SP='0x20010000',
                live_GP_PCs=['0x186be','0x186c0','0x186de'],memory_frame=False,
                clock_JAL_PC='0x18720',normal_clock_RA='0x18724',MEPC='0x9008',external_resident='0x40000',rows=decoded)


def ir_gate(ir,prefix,full_hash=True,mode='c'):
    body=prefix['normalized'](ir,'tsl9_runtime_reset_memory')
    need(body.count('"={x3},~{memory}"()')==3,'Three independent GP input ports')
    need('"={x5},~{memory}"()' in body and '%25 = phi i32 [ %8, %0 ], [ %17, %12 ]' in body,'Incoming T0 on skip; last copied word on loop exit')
    need(body.count('icmp ult i32')==4 and not re.search(r'\b(?:nuw|nsw|alloca)\b',body),'Unsigned guards, wrapping additions, no frame')
    for text in ['%4 = add i32 %3, 128','%27 = add i32 %26, 128',
                 '%19 = add i32 %14, 4','%21 = add i32 %13, 4','%37 = add i32 %35, 4',
                 'i32 109408, i32 %2, i32 %4, i32 %1','i32 %27, i32 536922456, i32 %7, i32 %25',
                 '"{x5},{x10},{x11},{x12},~{memory}"(i32 %32, i32 %41, i32 %30, i32 %31)']:
        need(text in body,'Reviewed pointer/port/SSA field: '+text)
    need(body.count('load volatile i32')==1 and body.count('store volatile i32')==2,'Only copy READ/STORE and zero STORE instructions')
    need('store volatile i32 %17, ptr %18' in body and 'store volatile i32 0, ptr %36' in body,'Copy read value and literal zero store')
    if full_hash:
        need(digest(body.encode())==IR_SHAS[mode],'Complete reviewed C/CPP IR including every empty port and branch edge')
    return dict(complete_body_sha256=IR_SHAS[mode],live_GP_reads=3,volatile_load_sites=1,volatile_store_sites=2,
                unsigned_compares=4,copy_skip_T0_preserved=True,zero_T0_preserved=True,empty_ports_have_no_machine_algorithm=True)


def negatives(blob,decode,source,ir,prefix):
    checks=[]
    # Real instruction fields changed in memory only; never compiled/executed.
    changes=[('SP',0x186b6,'immediate'),('entry-link',0x186ba,'rd'),('GP-source',0x186c0,'rs1'),
             ('copy-store',0x186d2,'rs2'),('copy-bound',0x186da,'rs2'),('zero-value',0x186ee,'rs2'),
             ('zero-guard-signed',0x186ea,'signed'),('mstatus-overwrite',0x1870c,'CSRform'),
             ('clock-link',0x18720,'rd'),('clock-target',0x18720,'jump'),
             ('MEPC',0x18728,'immediate'),('resident-link',0x18730,'rd')]
    for label,pc,field in changes:
        at=pc-0x186aa;changed=bytearray(blob);word=int.from_bytes(changed[at:at+4],'little')
        if field=='immediate':word^=1<<22
        elif field=='rd':word^=1<<7
        elif field=='rs1':word^=1<<15
        elif field=='rs2':word^=1<<20
        elif field=='signed':word^=1<<13
        elif field=='CSRform':word=(word&~(7<<12))|(1<<12)
        elif field=='jump':word^=1<<21
        changed[at:at+4]=word.to_bytes(4,'little')
        try:native_reset(bytes(changed),decode,source)
        except (ValueError,AssertionError,KeyError) as e:checks.append(dict(label=label,rejected_by=str(e),whole_image_hash_used=False))
        else:raise ValueError('Raw field mutant escaped: '+label)
    for label,old,new in [('GP-port','={x3},~{memory}','={x4},~{memory}'),
                          ('unsigned','icmp ult i32 %6, %7','icmp slt i32 %6, %7'),
                          ('skip-T0','%25 = phi i32 [ %8, %0 ]','%25 = phi i32 [ 0, %0 ]'),
                          ('copy-step','%19 = add i32 %14, 4','%19 = add i32 %14, 8')]:
        need(old in ir,'IR mutation anchor')
        try:ir_gate(ir.replace(old,new,1),prefix,False)
        except ValueError as e:checks.append(dict(label=label,rejected_by=str(e),whole_IR_hash_used=False))
        else:raise ValueError('IR mutant escaped: '+label)
    return checks


def inspect(root,folder,prior,prefix,source_result):
    decode,source,initializer,image,original_facts=source_result
    compile_record=json.loads((folder/'compile-receipt.json').read_bytes())
    need(compile_record['schema']=='TSL9-runtime-reset-clock-probe-v1' and compile_record['mode'] in ('c','cpp'),'Known compiler producer')
    tools={n:Path(p) for n,p in compile_record['tools'].items()}
    need(set(tools)==set(prior['TOOLS']) and all(sha(tools[n])==pin for n,pin in prior['TOOLS'].items()),'Exact admitted LLVM tools')
    probe=runpy.run_path(str(HERE/'probe.py'))
    sources=dict(memory=root/'src/native/startup/reset_memory.c',ports=root/'src/native/startup/reset_ports.c',
                 data=root/'src/native/startup/reset_data.c',clock=root/'src/native/clock/clock_init.c')
    stdint=tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
    origins=[HERE/'src'/sources[n].name for n in ('memory','ports','data')]
    expected_inputs={str(p):sha(p) for p in (HERE/'probe.py',root/BASE,HERE/'component.ld',stdint,*sources.values(),*origins,*tools.values())}
    need(compile_record['inputs']==expected_inputs and sha(stdint)==prior['STDINT_SHA'],'Exact sources/origins/header/tool input closure')
    need(all(p.read_bytes()==sources[n].read_bytes() for p,n in zip(origins,('memory','ports','data'))),'Curated startup sources equal origins')
    jobs=[]
    for unit,path in sources.items():
        common=[tools['clang'],*probe['flags'](prior,compile_record['mode'],unit)]
        jobs += [(unit+'-compile',[*common,'-c','-MD','-MF',folder/(unit+'.d'),'-MT',unit+'.o',path,'-o',folder/(unit+'.o')]),
                 (unit+'-IR',[*common,'-S','-emit-llvm',path,'-o',folder/(unit+'.ll')])]
        text=(folder/(unit+'.d')).read_text().replace('\\\n',' ')
        target,sep,tail=text.partition(':')
        deps={Path(re.sub(r'\\(.)',r'\1',t)).resolve() for t in re.findall(r'(?:\\.|[^\s])+',tail)}
        need(sep and target==unit+'.o' and deps==({path} if unit=='ports' else {path,stdint}),'Exact actual compiler MD closure: '+unit)
    elf_path=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
    jobs += [('link',[tools['ld.lld'],'--no-relax','-T',HERE/'component.ld',*[folder/(u+'.o') for u in sources],'-o',elf_path]),
             ('linked',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',elf_path]),
             ('memory-object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'memory.o'])]
    need(compile_record['commands']==[dict(label=k,argv=[str(x) for x in v],exit=0,log_sha256=sha(folder/(k+'.log'))) for k,v in jobs],'Complete successful compiler/link/disassembly recipes and logs')
    E=runpy.run_path(str(root/prior['PARSER']))['ELF'];elf=E(elf_path)
    need(elf.kind==2 and elf.flags==1 and not elf.relocations,'Actual linked RV32/RVC ELF without remaining relocations')
    und=[s['name'] for s in elf.symbols if s['name'] and s['index']==0 and s['info']>>4 in (1,2)]
    absolute=[s['name'] for s in elf.symbols if s['index']==0xfff1 and s['info']>>4 in (1,2)]
    need(not und and not absolute,'No unresolved ELF symbol or invented ABS provider')
    alloc=[s for s in elf.sections if s['size'] and s['flags']&2]
    need([(s['name'],s['address'],s['size'],s['flags'],s['type']) for s in alloc]==[
        ('.reset',0x186aa,138,6,1),('.clock',0x1874a,240,6,1),('.initializer',0x1ab60,128,2,1),
        ('.ram',0x20004000,35160,3,8),('.stack',0x2000fff0,16,3,8)],'Only declared real code/data/NOBITS allocations')
    funcs={s['name']:s for s in elf.symbols if s['info']&15==2 and s['size']}
    expected={'tsl9_runtime_reset_entry':(0x186aa,20),'tsl9_runtime_reset_memory':(0x186be,118),
              'tsl9_clock_prefix_entry':(0x1874a,16),'tsl9_clock_prefix_body':(0x1875a,220),'tsl9_clock_prefix_return':(0x18836,4)}
    need({n:(s['value'],s['size']) for n,s in funcs.items()}==expected and all(s['info']>>4==1 for s in funcs.values()),'Five genuine functions with fixed placements')
    need(struct.unpack_from('<I',elf.raw,24)[0]==0x186aa,'Actual ELF reset entry')
    native=elf.data(elf.byname['.reset']);contract=native_reset(native,decode,source)
    clock=elf.data(elf.byname['.clock'])
    need(digest(clock)==CLOCK_SHA,'Previously reviewed240B clock, same internal PC-relative jumps')
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
    need(len(got)==133,'38 reset plus95 clock instructions')
    # Object readback preserves every function's code, allowing only real linker patches.
    object_facts=[]
    role_functions={'memory':{'tsl9_runtime_reset_memory':118},'ports':{'tsl9_runtime_reset_entry':20},'data':{},
                    'clock':{'tsl9_clock_prefix_entry':16,'tsl9_clock_prefix_body':220,'tsl9_clock_prefix_return':4}}
    role_und={'memory':['tsl9_clock_prefix_entry'],'ports':['tsl9_runtime_reset_memory','tsl9_runtime_reset_ram','tsl9_runtime_reset_stack_top'],'data':[],'clock':[]}
    role_relocations={
        'memory':[('.text.tsl9_runtime_reset_memory',98,17,'tsl9_clock_prefix_entry',0)],
        'ports':[('.text.tsl9_runtime_reset_entry',0,23,'tsl9_runtime_reset_ram',0),
                 ('.text.tsl9_runtime_reset_entry',4,24,'.Lreset_gp',0),
                 ('.text.tsl9_runtime_reset_entry',8,23,'tsl9_runtime_reset_stack_top',0),
                 ('.text.tsl9_runtime_reset_entry',12,24,'.Lreset_sp',0),
                 ('.text.tsl9_runtime_reset_entry',16,17,'tsl9_runtime_reset_memory',0)],
        'data':[],
        'clock':[('.text.tsl9_clock_prefix_entry',12,17,'tsl9_clock_prefix_body',0),
                 ('.text.tsl9_clock_prefix_body',216,17,'tsl9_clock_prefix_return',0)]}
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
    need(overlap==bytes.fromhex('37170240 5c43') and clock[-6:]!=overlap,'Known six-byte original code overlap remains a blocker')
    checks=negatives(native,decode,source,ir,prefix)
    return dict(passed=True,mode=compile_record['mode'],reset=contract,memory_IR=ir_facts,
                linked_executable_bytes=378,linked_executable_instructions=133,objects=object_facts,
                negative_controls=checks,original=original_facts,
                normal_no_interference_projection=dict(GP='0x20004000',SP='0x20010000',A0='0x2000c958',A1='0x2000c958',RA='0x18724',T0='0x9008',MEPC='0x9008',
                    condition='original initializer reads/writes succeed, GP stable, no asynchronous interference, clock returns normally; A2-A5 follow the separate clock source contract'),
                ELF_link_closed=True,runtime_provider_closure=False,firmware_ready=False,
                blockers=['clock240B overlaps original [0x18834,0x1883a) code','vector8038/main9008/resident40000 not implemented in this ELF','changed GP-sample PCs, source setup order, AUIPC intermediates and clock instruction timing; full IRQ/fault equivalence unproved','physical RAM/stack/ROM/hardware and complete APP placement unproved'],
                target_execution=False,ISA_emulation=False,BIN_generated=False)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--tool-dir',type=Path)
    p.add_argument('--build-root',type=Path)
    p.add_argument('--replay',type=Path)
    p.add_argument('--require-firmware-ready',action='store_true')
    a=p.parse_args();root=a.project_root.resolve()
    need(HERE==root/'experiments/tsl9-runtime-reset-clock','Canonical model root')
    for name,pin in PINS.items():need(sha(root/name)==pin,'Reviewed source/dependency: '+name)
    prior=runpy.run_path(str(root/BASE));prefix=runpy.run_path(str(root/'experiments/tsl9-boot-clock-prefix/verify.py'))
    for name,pin in prior['SOURCE_PINS'].items():need(sha(root/name)==pin,'Clock reference source pin')
    if a.replay:
        record=json.loads(a.replay.read_bytes());folder=a.replay.resolve().parent
        need(record['schema']=='TSL9-runtime-reset-clock-static-v1' and record['verifier_sha256']==sha(Path(__file__)),'Unchanged replay verifier')
        need(record['artifacts']=={str(f):sha(f) for f in folder.iterdir() if f.is_file() and f.name!='verification.json'},'Complete actual artifact inventory')
        findings=inspect(root,folder,prior,prefix,original(root,prior));need(findings==record['findings'],'Replay findings exact')
        if a.require_firmware_ready:need(findings['firmware_ready'],'Firmware readiness rejected: '+ '; '.join(findings['blockers']))
        print(json.dumps(dict(replayed=True,mode=findings['mode'],negative_controls=len(findings['negative_controls']),firmware_ready=False)))
        return
    need(a.tool_dir and a.build_root and not a.build_root.exists(),'Existing tool directory and new owned build root required')
    subprocess.run([sys.executable,'-B',str(HERE/'probe.py'),'--project-root',str(root),'--tool-dir',str(a.tool_dir),'--build-root',str(a.build_root)],check=True,timeout=120)
    source=original(root,prior)
    for mode in ('c','cpp'):
        folder=a.build_root.resolve()/mode;findings=inspect(root,folder,prior,prefix,source)
        need(all(sha(Path(path))==pin for path,pin in source[-1]['source_dependencies'].items()),'Original parser/source dependency closure unchanged')
        record=dict(schema='TSL9-runtime-reset-clock-static-v1',verifier_sha256=sha(Path(__file__)),findings=findings,
                    artifacts={str(f):sha(f) for f in folder.iterdir() if f.is_file()})
        (folder/'verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(mode=mode,passed=True,reset_bytes=138,reset_instructions=38,negative_controls=len(findings['negative_controls']),firmware_ready=False,receipt=str(folder/'verification.json'))))
    if a.require_firmware_ready:raise ValueError('Firmware readiness rejected; see blockers in component receipts')


if __name__=='__main__':
    main()
