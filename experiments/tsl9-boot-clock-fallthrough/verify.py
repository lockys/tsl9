#!/usr/bin/env python3
"""Static fall-through clock checks. No firmware output or target execution."""
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
SYMS=['tsl9_clock_prefix_entry','tsl9_clock_prefix_body']
IR_SHA='52f3769789eaa4631cc54e38d7bbf15d2ed62eaeaa6a488d4298e9d6c636cb26'
CODE_SHA='bd0eff746b615a1ee68e1a851ff5655424d1af31e3e8ddd443bbb86b61cb970d'
CAPTURE=dict(enabled=False,root=None,paths=set(),hashes={})


def need(ok,message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_open(event,args):
    if event=='open' and CAPTURE['enabled'] and isinstance(args[0],str):
        p=Path(args[0]).resolve()
        if p.is_relative_to(CAPTURE['root']) and not p.is_relative_to(HERE/'build') and p.is_file():
            CAPTURE['paths'].add(p)
            if p not in CAPTURE['hashes']:
                CAPTURE['enabled']=False
                try:
                    CAPTURE['hashes'][p]=sha(p)
                finally:
                    CAPTURE['enabled']=True


sys.addaudithook(audit_open)


def ir_gate(ir,old_ir,register_ir,prefix,prior,full_hash=True):
    prefix['ir_core'](old_ir,register_ir,prior)
    old=prefix['normalized'](old_ir,'tsl9_clock_prefix_body').splitlines()
    body=prefix['normalized'](ir,SYMS[1])
    lines=body.splitlines()
    need(lines[:3]==old[:3],'Exact live A4 sample and SP frame imports')
    need(lines[3:-2]==old[3:-2] and len(lines[3:-2])==85,
         'All 85 computational IR lines, operands, volatile operations and CFG edges unchanged')
    need(lines[-2:]==[r'tail call void asm sideeffect "addi sp, sp, 16\0Aret\0A", "~{memory}"()',
                      'unreachable'],'Only inline architectural SP+16 / original RA return')
    need('alloca ' not in body and '@llvm.lifetime' not in body,'No second frame')
    need(body.count('load volatile i32')==21 and body.count('store volatile i32')==20,
         'Same C volatile access inventory')
    if full_hash:
        need(hashlib.sha256(body.encode()).hexdigest()==IR_SHA,'Whole reviewed fall-through body IR')
    return dict(computational_IR_lines=85,full_SSA_CFG_equal=True,volatile_C_loads=21,
                volatile_C_stores=20,entry_first_load=True,second_frame=False,IR_sha256=IR_SHA)


def critical(codes,values,linked,old_codes):
    entry,body=codes
    need(len(entry)==12 and entry==old_codes[0][:12],
         'Exact original first-read-before-frame prefix; no entry branch/trap')
    need(len(body)==220 and body[-4:]==bytes.fromhex('41018280'),
         'Exact inline SP+16 / RET and reviewed C body extent')
    need(body[:-4]==old_codes[1][:-4],
         'Actual 216 computational native bytes equal compiled reviewed prefix C core')
    if linked:
        need(values==[0x1874a,0x18756] and values[1]==values[0]+len(entry),
             'Actual contiguous entry/body; no alignment, return, trap or veneer between them')
        need(values[1]+len(body)==0x18832 and values[1]+len(body)<=0x18834,
             'Actual extent stops before the next original function')
    return True


def inspect_elf(path,log,root,prior,prefix,old_codes,linked):
    E=runpy.run_path(str(root/prior['PARSER']))['ELF']
    classifier=runpy.run_path(str(root/prior['CLASSIFIER']))
    elf=E(path)
    need(elf.kind==(2 if linked else 1) and elf.flags==1,'RV32 RVC object or nominal linked component')
    fs={s['name']:s for s in elf.symbols if s['info']&15==2 and s['size']}
    need(set(fs)==set(SYMS),'Exactly two nonempty private-ABI FUNC symbols')
    ordered=[fs[n] for n in SYMS]
    need([f['size'] for f in ordered]==[12,220] and all(f['info']>>4==1 for f in ordered),
         'Exactly the reviewed global function sizes')
    undefined=[s['name'] for s in elf.symbols if s['name'] and s['index']==0 and s['info']>>4 in (1,2)]
    absolute=[s['name'] for s in elf.symbols if s['name'] and s['index']==0xfff1 and s['info']>>4 in (1,2)]
    need(not undefined and not absolute and not elf.relocations,'No providers, ABS symbols or relocations')
    allocated=[s for s in elf.sections if s['size'] and s['flags']&2]
    need(sum(s['size'] for s in allocated)==232 and
         all(s['flags']==6 and s['type']==1 and s['alignment']==2 for s in allocated),
         'Only 232 AX bytes, alignment2, no data/BSS/unwind/carrier/padding')
    codes=[elf.function_bytes(f) for f in ordered];values=[f['value'] for f in ordered]
    critical(codes,values,linked,old_codes)
    need(hashlib.sha256(b''.join(codes)).hexdigest()==CODE_SHA,
         'Independently reviewed complete232B native code anchor')
    if linked:
        need(len(allocated)==1 and allocated[0]['name']=='.clock' and allocated[0]['address']==0x1874a,
             'Single nominal clock section at original entry')
        need(struct.unpack_from('<I',elf.raw,24)[0]==0x1874a,'ELF entry is the architectural prefix')
        need(elf.data(allocated[0])==b''.join(codes),'Complete contiguous section with no hidden bytes')
    else:
        need(len(allocated)==2 and {s['name'] for s in allocated}=={'.text.'+n for n in SYMS}
             and values==[0,0],'Two own object sections, section-relative zero FUNC values')
    rows=prefix['read_rows'](elf,log,classifier)
    need(len(rows)==93 and sum(len(bytes.fromhex(r['raw'])) for r in rows)==232,
         'Complete 93-instruction LLVM/ELF byte readback')
    for function,code in zip(ordered,codes):
        selected=[r for r in rows if r['section']==elf.sections[function['index']]['name']
                  and function['value']<=r['address']<function['value']+function['size']]
        need(b''.join(bytes.fromhex(r['raw']) for r in selected)==code,
             'Complete nonoverlapping function instruction inventory')
    need([r['raw'] for r in rows if r['rd']==2]==['4111','4101'],
         'Only one frame decrement and increment; no extra prologue/spill')
    need(all(r['mnemonic'] not in ('call','tail','jal','jalr','j') for r in rows),
         'No link, jump, indirect helper or out-of-line return transfer')
    returns=[r for r in rows if r['mnemonic']=='ret']
    need(len(returns)==1 and returns[0]['address']==values[1]+218,
         'Only final original-RA return')
    stack=[(r['mnemonic'],r['operands']) for r in rows if '(sp)' in r['operands']]
    need(stack==[('sw','zero, 0x8(sp)'),('sw','zero, 0xc(sp)'),('sw','a5, 0xc(sp)'),
                 ('lw','a5, 0x8(sp)'),('sw','a5, 0x8(sp)'),('lw','a5, 0xc(sp)'),
                 ('lw','a5, 0x8(sp)'),('sw','a3, 0xc(sp)'),('lw','a4, 0xc(sp)')],
         'Only original live count/ready stack slots; no saved RA or reserved-slot access')
    return dict(file=path.name,linked=linked,bytes=232,instructions=93,UND=0,ABS=0,relocations=0,
                functions=[dict(name=f['name'],value=f['value'],bytes=f['size'],
                                sha256=hashlib.sha256(c).hexdigest()) for f,c in zip(ordered,codes)],
                own_written_GPRs=[2,12,13,14,15],SP_writes=2,stack_sites=len(stack),
                section_inventory=[{k:s[k] for k in ('name','type','flags','address','size','alignment')}
                                   for s in elf.sections],
                rows=rows),codes,values


def negatives(codes,values,old_codes,ir,old_ir,register_ir,prefix,prior):
    results=[]
    for label,index,at,raw in [
        ('first-read-RD',0,4,'9443'),('entry-frame-sign',0,10,'4101'),
        ('entry-extra-jump',0,12,'6f000000'),('entry-trap',0,10,'0290'),
        ('body-first-ORI-input',1,0,'93661700'),('first-store-offset',1,8,'14c6'),
        ('tail-frame-size',1,216,'2101'),('tail-return-register',1,218,'0285'),
        ('tail-cold-store',1,216,'02c6'),('body-extent-overrun',1,220,'0100'),
    ]:
        changed=list(codes);sample=bytearray(changed[index])
        if label=='body-first-ORI-input':
            word=int.from_bytes(sample[:4],'little')
            raw=((word&~(31<<15))|(15<<15)).to_bytes(4,'little').hex()
        sample[at:at+len(bytes.fromhex(raw))]=bytes.fromhex(raw);changed[index]=bytes(sample)
        try:
            critical(changed,values,True,old_codes)
        except ValueError as e:
            results.append(dict(label=label,rejected_by=str(e),whole_code_hash_used=False))
        else:
            raise ValueError('Native negative control escaped: '+label)
    for label,changed in [('entry-moved',[values[0]+2,values[1]]),
                          ('alignment-gap',[values[0],values[1]+2])]:
        try:
            critical(codes,changed,True,old_codes)
        except ValueError as e:
            results.append(dict(label=label,rejected_by=str(e),whole_code_hash_used=False))
        else:
            raise ValueError('Placement negative escaped: '+label)
    for label,old,new in [
        ('sample-port','={x14},={x2}','={x15},={x2}'),
        ('skip-W','%59 = phi i32 [ %31, %27 ]','%59 = phi i32 [ 0, %27 ]'),
        ('configured-A4','%59 = phi i32 [ %31, %27 ], [ 8, %53 ]','%59 = phi i32 [ %31, %27 ], [ 7, %53 ]'),
        ('poll-counter','icmp eq i32 %25, 4096','icmp eq i32 %25, 4095'),
        ('inline-SP-sign',r'addi sp, sp, 16\0Aret',r'addi sp, sp, -16\0Aret'),
        ('inline-return',r'16\0Aret\0A',r'16\0Ajr a0\0A'),
    ]:
        need(old in ir,'Actual mutation anchor: '+label)
        try:
            ir_gate(ir.replace(old,new,1),old_ir,register_ir,prefix,prior,False)
        except ValueError as e:
            results.append(dict(label=label,rejected_by=str(e),whole_IR_hash_used=False))
        else:
            raise ValueError('IR negative escaped: '+label)
    need(len(results)==18,'Complete negative-control inventory')
    return results


def inspect(root,folder,tool_dir):
    producer=runpy.run_path(str(HERE/'probe.py'))
    prior,tools,header=producer['load'](root,tool_dir)
    prefix=runpy.run_path(str(root/producer['PREFIX']/'verify.py'))
    actual=json.loads((folder/'compile-receipt.json').read_bytes())
    need(set(actual)=={'schema','mode','inputs','commands','target_execution','ISA_emulation','BIN_generated'}
         and all(actual[k] is False for k in ('target_execution','ISA_emulation','BIN_generated')),
         'Exact offline-only producer scope')
    need(actual['schema']=='TSL9-clock-fallthrough-probe-v1' and actual['mode'] in ('c','cpp'),
         'Known producer and language')
    need(actual['inputs']==producer['inputs'](root,prior,tools,header),'Exact compile input closure')
    recipes=producer['recipes'](root,folder,actual['mode'],prior,tools)
    commands=[dict(label=label,argv=[producer['portable'](x,root,tools,header) for x in argv],
                   exit=0,log_sha256=sha(folder/(label+'.log'))) for label,argv in recipes]
    need(actual['commands']==commands,'Exact compile/link/reference/disassembly commands and observed logs')
    expected={label+'.log' for label,_ in recipes}|{
        'native.o','prefix.o','COMPONENT-ONLY-NOT-FIRMWARE.elf','native.ll','prefix.ll','register.ll',
        'native.d','prefix.d','compile-receipt.json'}
    need(all(p.is_file() for p in folder.iterdir()),'No unaudited artifact subdirectories')
    need({p.name for p in folder.iterdir() if p.is_file() and p.name!='verification.json'}==expected,
         'Exact producer artifact inventory')
    for dep,source in [('native.d',HERE/'src/clock_fallthrough.c'),
                       ('prefix.d',root/producer['PREFIX']/'src/clock_prefix.c')]:
        text=(folder/dep).read_text().replace('\\\n',' ').partition(':')[2]
        dependencies={Path(re.sub(r'\\(.)',r'\1',x)).resolve() for x in re.findall(r'(?:\\.|[^\s])+',text)}
        need(dependencies=={source,header},'Complete actual source/header MD dependency set')
    ir=(folder/'native.ll').read_text();old_ir=(folder/'prefix.ll').read_text();register_ir=folder/'register.ll'
    core=ir_gate(ir,old_ir,register_ir,prefix,prior)
    _,old_codes,_=prefix['inspect_elf'](folder/'prefix.o',folder/'prefix-object.log',prior,root,False)
    facts=[]
    for linked,filename,log in [(False,'native.o','object.log'),(True,'COMPONENT-ONLY-NOT-FIRMWARE.elf','linked.log')]:
        fact,codes,values=inspect_elf(folder/filename,folder/log,root,prior,prefix,old_codes,linked)
        facts.append(fact)
    tests=negatives(codes,values,old_codes,ir,old_ir,register_ir,prefix,prior)
    return dict(passed=True,mode=actual['mode'],IR=core,ELFs=facts,negative_controls=tests,
                next_function_overlap_bytes=0,nominal_end='0x18832',
                residual_original_tail=dict(VA='[0x18832,0x18834)',raw='61bf',free_space=False,
                                            disposition_in_full_APP_unproved=True),
                full_original_ABI_proved=False,IRQ_fault_equivalence_proved=False,
                resident_and_physical_identity_proved=False,firmware_ready=False,
                target_execution=False,ISA_emulation=False,BIN_generated=False)


def main():
    verifier_started=sha(Path(__file__))
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--build-root',type=Path)
    p.add_argument('--replay',type=Path)
    p.add_argument('--require-firmware-ready',action='store_true')
    a=p.parse_args();root=a.project_root.resolve();tool_dir=a.tool_dir.resolve()
    need((a.build_root is None)!=(a.replay is None),'Choose a new build or read-only replay')
    if a.build_root:
        subprocess.run([sys.executable,'-B',str(HERE/'probe.py'),'--project-root',str(root),
                        '--tool-dir',str(tool_dir),'--build-root',str(a.build_root)],check=True,timeout=120)
        folders=[a.build_root.resolve()/n for n in ('c','cpp')]
    else:
        need(a.replay.name=='verification.json' and a.replay.resolve().is_relative_to(HERE/'build'),
             'Owned replay receipt')
        folders=[a.replay.resolve().parent]
    for folder in folders:
        need(folder.is_relative_to(HERE/'build'),'Owned candidate evidence')
        CAPTURE.update(enabled=True,root=root,paths=set(),hashes={})
        try:
            producer=runpy.run_path(str(HERE/'probe.py'));prior,_,_=producer['load'](root,tool_dir)
            boot=root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
            original=prior['originals'](root,boot,boot.parent/'ID-2966-V4.1.60-decoded.bin')
            raw=(boot.parent/'ID-2966-V4.1.60-decoded.bin').read_bytes()
            need(raw[0x1082c:0x10834]==bytes.fromhex('4101828002c661bf'),
                 'Actual original SP/RET/cold-store/cold-jump tail')
            findings=inspect(root,folder,tool_dir)
            edge_reader=runpy.run_path(str(HERE/'source_edges.py'))
            findings['bounded_original_incoming_scan']=edge_reader['inspect'](root)
        finally:
            CAPTURE['enabled']=False
        dependencies={path.relative_to(root).as_posix():sha(path) for path in sorted(CAPTURE['paths'])}
        need(all(sha(path)==pin for path,pin in CAPTURE['hashes'].items()),
             'All actual project evidence readers stable before and after analysis')
        need(sha(Path(__file__))==verifier_started,'Verifier source unchanged throughout analysis')
        artifacts={path.name:sha(path) for path in sorted(folder.iterdir()) if path.is_file() and path.name!='verification.json'}
        record=dict(schema='TSL9-clock-fallthrough-static-v1',verifier_sha256=sha(Path(__file__)),
                    original=original,source_evidence_dependencies=dependencies,findings=findings,artifacts=artifacts)
        if a.replay:
            saved=json.loads(a.replay.read_bytes())
            need(saved==record,'Complete current-source, original-image, artifact and finding replay equality')
        else:
            (folder/'verification.json').write_bytes((json.dumps(record,indent=2)+'\n').encode('utf-8'))
        print(json.dumps(dict(mode=findings['mode'],passed=True,bytes=232,instructions=93,
                              negative_controls=len(findings['negative_controls']),
                              next_function_overlap_bytes=0,firmware_ready=False,
                              target_execution=False,BIN_generated=False)))
        if a.require_firmware_ready:
            need(findings['firmware_ready'],'Full APP, cold-tail, IRQ/fault, resident and physical closure unproved')


if __name__=='__main__':
    main()
