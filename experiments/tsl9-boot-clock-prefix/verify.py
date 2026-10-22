#!/usr/bin/env python3
"""Build or replay static clock-prefix evidence; no target execution support."""
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
BASE_SHA = '096660430ae0aa0f44813192aa30c49c958b8180e4123249a5aa36eeab11a7a8'
SYMS = ['tsl9_clock_prefix_entry','tsl9_clock_prefix_body','tsl9_clock_prefix_return']
PREFIX = bytes.fromhex('b7170240 9843 b706fff8 4111')
IR_SHA = 'f464d446ad5fb931a0cc87c605c1fbe7104deb98708b88acc05baf2646b15eef'
LINKED_SHA = '2d5529329f757de58bf85ae1d5671125836bc740b813d89df163cf5bbe7d48af'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def normalized(ir, symbol):
    match = re.search(r'define[^\n]*@'+symbol+r'\([^)]*\)[^{]*\{(.*?)\n\}',ir,re.S)
    need(match, 'Defined actual IR body')
    lines = []
    for raw in match[1].splitlines():
        line = raw.split(';',1)[0].strip()
        if line:
            line = re.sub(r', ![A-Za-z.]+ !\d+','',line)
            lines.append(re.sub(r' #\d+\b','',line))
    return '\n'.join(lines)+'\n'


def ir_core(ir, reference, prior, whole_hash=True):
    body = normalized(ir,SYMS[1])
    lines = body.splitlines()
    need(lines[:3] == [
        '%1 = tail call { i32, ptr } asm sideeffect "", "={x14},={x2},~{memory}"()',
        '%2 = extractvalue { i32, ptr } %1, 0',
        '%3 = extractvalue { i32, ptr } %1, 1'], 'A4 sample/SP frame live-in ports')
    need(lines[-2:] == ['tail call void asm sideeffect "j tsl9_clock_prefix_return\\0A", "~{memory}"()',
                          'unreachable'], 'Only no-link architectural return transfer')
    need('alloca ' not in body and '@llvm.lifetime' not in body,
         'C body has no frame allocation or lifetime helpers')
    prior['ir_gate'](reference)
    baseline = prior['normalized_ir'](reference.read_text(encoding='utf-8')).splitlines()
    need(baseline[:4] == [
        '%1 = alloca %struct.clock_frame, align 4',
        'call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %1)',
        'call void asm sideeffect "", "=*m,~{memory}"(ptr nonnull elementtype(%struct.clock_frame) %1)',
        '%2 = load volatile i32, ptr inttoptr (i32 1073876992 to ptr), align 4096'],
         'Reviewed reference allocation and first sample')
    def number(n):
        return 1 if n == 3 else n-1 if n >= 4 else n
    converted = []
    for line in lines[3:-2]:
        line = re.sub(r'%(\d+)',lambda m:'%'+str(number(int(m[1]))),line)
        line = re.sub(r'^(\d+):',lambda m:str(number(int(m[1])))+':',line)
        # A tail marker on this EMPTY fixed-register port adds no machine call.
        if 'asm sideeffect "", "{x12},{x13},{x14},{x15},~{memory}"' in line:
            line = line.removeprefix('tail ')
        converted.append(line)
    need(converted == baseline[4:-2] and len(converted) == 85,
         'All 85 computational IR lines/SSA operands/CFG edges equal reviewed C core')
    need(body.count('load volatile i32') == 21 and body.count('store volatile i32') == 20,
         'C IR 21 loads/20 stores; the remaining first load belongs to entry')
    if whole_hash:
        need(hashlib.sha256(body.encode()).hexdigest() == IR_SHA, 'Whole reviewed private C body IR')
    return dict(core_lines=85,core_SSA_and_CFG_equal=True,volatile_C_loads=21,volatile_C_stores=20,
                initial_read_in_architectural_entry=True,no_second_sample=True,second_frame=False,
                empty_port_tail_marker_only_normalization=True)


def read_rows(elf, log, classifier):
    rows,section = [],None
    for line in log.read_text(encoding='utf-8').splitlines():
        header = re.match(r'Disassembly of section (.+):',line)
        if header:
            section = header[1]
        m = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)',line)
        if not m:
            continue
        at,raw = int(m[1],16),bytes.fromhex(m[2])
        need(section in elf.byname and len(raw) in (2,4), 'Actual instruction inside known section')
        owner = elf.byname[section]
        offset = at-owner['address']
        need(raw == elf.data(owner)[offset:offset+len(raw)] and m[3] not in ('<unknown>','.word','.2byte'),
             'LLVM instruction bytes equal ELF bytes')
        rd,kind,known = classifier['decode16' if len(raw)==2 else 'decode32'](int.from_bytes(raw,'little'))
        need(known and rd in (None,0,2,12,13,14,15), 'Only SP/A2-A5 own writes')
        rows.append(dict(section=section,address=at,raw=raw.hex(),rd=rd,kind=kind,
                         mnemonic=m[3],operands=m[4]))
    return rows


def jump(raw, at, target):
    need(len(raw)==4, 'Direct transfer is JAL32')
    word = int.from_bytes(raw,'little')
    need(word&127 == 0x6f and (word>>7)&31 == 0, 'No-link JAL x0; RA unchanged')
    imm = ((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1)
    if imm&0x100000:
        imm -= 0x200000
    need(at+imm == target, 'Actual direct transfer reaches declared function')


def critical(codes, values, linked):
    entry,body,finish = codes
    need(entry[:12] == PREFIX and len(entry)==16, 'Original four-instruction first-read-before-frame prefix')
    need(body[:10] == bytes.fromhex('936617003716024014c2'),
         'Body ORI consumes A4 sample and first SW uses that result; no resample')
    need(finish == bytes.fromhex('41018280'), 'Single SP+16 and original RA return')
    need(body[-12:-4] == bytes.fromhex('37060200b7160240'), 'Common exit commits original A2/A3')
    if linked:
        jump(entry[12:], values[0]+12, values[1])
        jump(body[-4:], values[1]+len(body)-4, values[2])
    return True


def inspect_elf(path, log, prior, root, linked):
    E = runpy.run_path(str(root/prior['PARSER']))['ELF']
    decoder = runpy.run_path(str(root/prior['CLASSIFIER']))
    elf = E(path)
    need(elf.kind == (2 if linked else 1) and elf.flags==1, 'RV32 RVC object or component')
    functions = {s['name']:s for s in elf.symbols if s['info']&15==2 and s['size']}
    need(set(functions)==set(SYMS), 'Exactly entry, genuine C body, architectural return')
    fs = [functions[n] for n in SYMS]
    need([s['size'] for s in fs]==[16,220,4] and all(s['info']>>4==1 for s in fs), 'Measured three global function sizes')
    undefined = [s['name'] for s in elf.symbols if s['name'] and s['index']==0 and s['info']>>4 in (1,2)]
    absolute = [s['name'] for s in elf.symbols if s['index']==0xfff1 and s['info']>>4 in (1,2)]
    need(not undefined and not absolute, 'No unresolved/global ABS provider')
    alloc = [s for s in elf.sections if s['size'] and s['flags']&2]
    need(sum(s['size'] for s in alloc)==240 and all(s['flags']==6 and s['type']==1 for s in alloc),
         'Only 240 AX bytes; no allocated data, NOBITS, unwind, carriers or padding')
    codes = [elf.function_bytes(s) for s in fs]
    values = [s['value'] for s in fs]
    critical(codes,values,linked)
    if linked:
        need(not elf.relocations and len(alloc)==1 and alloc[0]['name']=='.text', 'All internal relocations resolved')
        need(values == [0,16,236] and struct.unpack_from('<I',elf.raw,24)[0]==0, 'Nonphysical zero VMA entry and contiguous functions')
        need(hashlib.sha256(elf.data(alloc[0])).hexdigest()==LINKED_SHA,'Reviewed complete linked code')
    else:
        need(len(alloc)==3 and {s['name'] for s in alloc}=={'.text.'+n for n in SYMS}, 'Only three declared object sections')
        rel = [(x['owner'],x['offset'],x['type'],x['symbol']['name'],x['addend']) for x in elf.relocations]
        need(rel == [('.text.'+SYMS[0],12,17,SYMS[1],0),('.text.'+SYMS[1],216,17,SYMS[2],0)],
             'Exactly two internal R_RISCV_JAL no-relax relocations')
    rows = read_rows(elf,log,decoder)
    need(len(rows)==95 and sum(len(bytes.fromhex(r['raw'])) for r in rows)==240,'Complete 95-instruction readback')
    for f,code in zip(fs,codes):
        selected = [r for r in rows if r['section']==elf.sections[f['index']]['name']
                    and f['value']<=r['address']<f['value']+f['size']]
        need(b''.join(bytes.fromhex(r['raw']) for r in selected)==code,'No omitted, overlapping or extra executable instructions')
        sp = [r for r in selected if r['rd']==2]
        expected_sp = ['4111'] if f['name']==SYMS[0] else ['4101'] if f['name']==SYMS[2] else []
        need([r['raw'] for r in sp]==expected_sp,'One frame decrement/increment; no body SP writes')
    need(all(r['mnemonic'] not in ('call','tail','jal','jalr') for r in rows), 'No extra link, indirect transfer or compiler helpers')
    stack = [r for r in rows if '(sp)' in r['operands']]
    need([(r['mnemonic'],r['operands']) for r in stack] == [
        ('sw','zero, 0x8(sp)'),('sw','zero, 0xc(sp)'),('sw','a5, 0xc(sp)'),('lw','a5, 0x8(sp)'),
        ('sw','a5, 0x8(sp)'),('lw','a5, 0xc(sp)'),('lw','a5, 0x8(sp)'),('sw','a3, 0xc(sp)'),('lw','a4, 0xc(sp)')],
         'Only original live count/ready slots; no spill/RA save/reserved-word access')
    return dict(ELF=path.name,linked=linked,functions=[dict(name=f['name'],bytes=f['size'],value=f['value'],
                    sha256=hashlib.sha256(c).hexdigest()) for f,c in zip(fs,codes)],bytes=240,instructions=95,
                UND=undefined,ABS=absolute,relocations=len(elf.relocations),own_written_GPRs=[2,12,13,14,15],
                SP_write_count=2,stack_sites=len(stack),first_read_precedes_frame=True,rows=rows),codes,values


def negatives(codes,values,ir,reference,prior):
    results = []
    for label,which,at,raw in [
        ('first-read-RD',0,4,'9443'),('prefix-frame-sign',0,10,'4101'),
        ('first-ORI-input',1,0,'93661700'),('first-store-offset',1,8,'14c6'),
        ('entry-link-RA',0,12,'ef004000'),('entry-target',0,12,'6f000000'),
        ('body-link-RA',1,216,'ef004000'),('return-frame-size',2,0,'2101'),
    ]:
        changed = [bytes(c) for c in codes]
        sample = bytearray(changed[which])
        if label=='first-ORI-input':
            # ORI's rs1 A4 -> A5, preserving all remaining fields.
            word = int.from_bytes(sample[:4],'little')
            raw = ((word&~(31<<15))|(15<<15)).to_bytes(4,'little').hex()
        sample[at:at+len(bytes.fromhex(raw))] = bytes.fromhex(raw)
        changed[which] = bytes(sample)
        try:
            critical(changed,values,True)
        except ValueError as e:
            results.append(dict(label=label,rejected_by=str(e),whole_code_hash_used=False))
        else:
            raise ValueError('Mutation escaped critical gate: '+label)
    for label,old,new in [
        ('sample-port','={x14},={x2}','={x15},={x2}'),
        ('skip-W','%59 = phi i32 [ %31, %27 ]','%59 = phi i32 [ 0, %27 ]'),
        ('configured-A4','%59 = phi i32 [ %31, %27 ], [ 8, %53 ]','%59 = phi i32 [ %31, %27 ], [ 7, %53 ]'),
        ('poll-counter','icmp eq i32 %25, 4096','icmp eq i32 %25, 4095'),
    ]:
        need(old in ir, 'Mutation source anchor')
        changed = ir.replace(old,new,1)
        try:
            ir_core(changed,reference,prior,False)
        except ValueError as e:
            results.append(dict(label=label,rejected_by=str(e),whole_IR_hash_used=False))
        else:
            raise ValueError('Mutation escaped IR gate: '+label)
    return results


def inspect(root,folder,prior):
    compile_record = json.loads((folder/'compile-receipt.json').read_bytes())
    need(compile_record['schema']=='TSL9-clock-prefix-probe-v1' and compile_record['mode'] in ('c','cpp'), 'Known producer')
    tools = {n:Path(x) for n,x in compile_record['tools'].items()}
    need(set(tools)==set(prior['TOOLS']) and all(sha(tools[n])==pin for n,pin in prior['TOOLS'].items()),
         'Exact existing LLVM tool identities')
    stdint = tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
    expected_inputs = {str(x):sha(x) for x in (HERE/'probe.py',root/BASE,HERE/'src/clock_prefix.c',
                       HERE/'component.ld',stdint,*tools.values(),*(root/n for n in prior['SOURCE_PINS']))}
    need(compile_record['inputs']==expected_inputs and sha(stdint)==prior['STDINT_SHA'],
         'Complete producer source, baseline, header and tool input closure')
    for p,pin in compile_record['inputs'].items():
        need(sha(Path(p))==pin,'Unchanged actual compile input: '+p)
    source = HERE/'src/clock_prefix.c'
    common = [tools['clang'],*prior['flags'](compile_record['mode'])]
    commands = [
        ('compile',[*common,'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',folder/'native.o']),
        ('IR',[*common,'-S','-emit-llvm',source,'-o',folder/'native.ll']),
        ('reference-IR',[*common,'-S','-emit-llvm',root/'experiments/tsl9-boot-clock-registers/src/clock_registers.c','-o',folder/'reference.ll']),
        ('link',[tools['ld.lld'],'--no-relax','-T',HERE/'component.ld',folder/'native.o','-o',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
        ('object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'native.o']),
        ('linked',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
    ]
    need(compile_record['commands']==[dict(label=label,argv=[str(x) for x in argv],exit=0,
         log_sha256=sha(folder/(label+'.log'))) for label,argv in commands],
         'Exact observed compile, reference IR, link and disassembly commands')
    for cmd in compile_record['commands']:
        need(cmd['exit']==0 and cmd['log_sha256']==sha(folder/(cmd['label']+'.log')), 'Successful observed command/log')
    dep = (folder/'native.d').read_text().replace('\\\n',' ').partition(':')[2]
    dependencies = {Path(re.sub(r'\\(.)',r'\1',x)).resolve() for x in re.findall(r'(?:\\.|[^\s])+',dep)}
    need(dependencies=={HERE/'src/clock_prefix.c',stdint},'Complete compiler source/header closure')
    ir = (folder/'native.ll').read_text(encoding='utf-8')
    core = ir_core(ir,folder/'reference.ll',prior)
    artifacts,codes,values = [],None,None
    for linked,fn,log in [(False,'native.o','object.log'),(True,'COMPONENT-ONLY-NOT-FIRMWARE.elf','linked.log')]:
        fact,codes,values = inspect_elf(folder/fn,folder/log,prior,root,linked)
        artifacts.append(fact)
    tests = negatives(codes,values,ir,folder/'reference.ll',prior)
    return dict(passed=True,mode=compile_record['mode'],IR=core,ELFs=artifacts,negative_controls=tests,
                complete_return_register_ABI_proved=False,IRQ_fault_equivalence_proved=False,
                original_hardware_identity_proved=False,target_execution=False,BIN_generated=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--tool-dir',type=Path)
    p.add_argument('--build-root',type=Path)
    p.add_argument('--replay',type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    need(HERE==root/'experiments/tsl9-boot-clock-prefix' and sha(root/BASE)==BASE_SHA,'Canonical model and reviewed baseline')
    prior = runpy.run_path(str(root/BASE))
    for name,pin in prior['SOURCE_PINS'].items():
        need(sha(root/name)==pin,'Reviewed baseline dependency: '+name)
    if a.replay:
        saved = json.loads(a.replay.read_bytes())
        need(saved['schema']=='TSL9-clock-prefix-static-v1','Known replay format')
        need(saved['verifier_sha256']==sha(Path(__file__)),'Unchanged replay verifier')
        boot = root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
        need(saved['original']==prior['originals'](root,boot,boot.parent/'ID-2966-V4.1.60-decoded.bin'),
             'Actual original images and complete source exit contract replay')
        expected_artifacts = {str(f):sha(f) for f in a.replay.resolve().parent.iterdir()
                              if f.is_file() and f.name!='verification.json'}
        need(saved['artifact_hashes']==expected_artifacts,'Complete unchanged replay artifact inventory')
        for path,pin in saved['artifact_hashes'].items():
            need(sha(Path(path))==pin,'Unchanged evidence artifact')
        actual = inspect(root,a.replay.resolve().parent,prior)
        need(actual==saved['findings'],'Replay findings identical')
        print(json.dumps(dict(replayed=True,mode=actual['mode'],ELFs=2,negative_controls=len(actual['negative_controls']))))
        return
    need(a.tool_dir and a.build_root and not a.build_root.exists(),'New build root and existing tool directory required')
    subprocess.run([sys.executable,'-B',str(HERE/'probe.py'),'--project-root',str(root),
                    '--tool-dir',str(a.tool_dir),'--build-root',str(a.build_root)],check=True,timeout=120)
    boot = root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
    runtime = boot.parent/'ID-2966-V4.1.60-decoded.bin'
    original = prior['originals'](root,boot,runtime)
    for mode in ('c','cpp'):
        folder = a.build_root.resolve()/mode
        findings = inspect(root,folder,prior)
        record = dict(schema='TSL9-clock-prefix-static-v1',verifier_sha256=sha(Path(__file__)),
                      original=original,findings=findings,
                      artifact_hashes={str(f):sha(f) for f in folder.iterdir() if f.is_file()})
        (folder/'verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(mode=mode,passed=True,bytes=240,instructions=95,
                              negative_controls=len(findings['negative_controls']),receipt=str(folder/'verification.json'))))


if __name__=='__main__':
    main()
