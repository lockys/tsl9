#!/usr/bin/env python3
"""All-field native profile review; never execute target instructions."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
NAME='tsl9_callback_native_8614'
SOURCE_SLOTS=[(1,44),(8,40),(9,36),(18,32),(19,28),(20,24),
              (21,20),(22,16),(23,12),(24,8),(25,4)]


def need(value,message):
    if not value:raise ValueError(message)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def H(raw):return hashlib.sha256(raw).hexdigest()


def contract(e,ctx,field,profile):
    need(e.kind in (1,2) and e.flags==1,'Actual RVC ET_REL or linked ELF')
    functions=[s for s in e.symbols if s['info']&15==2 and s['size']]
    need(len(functions)==1,'Exactly one real source FUNC; no helper substitution')
    symbol=functions[0]
    need(symbol['name']==NAME and symbol['info']==18 and symbol['other']==0 and
         0<symbol['index']<len(e.sections),'Actual allocated GLOBAL source function')
    section=e.sections[symbol['index']]
    allocated=[s for s in e.sections if s['flags']&2 and s['size']]
    expected=624 if profile=='fresh-GP624' else 656
    need(len(allocated)==1 and allocated[0]['index']==section['index'] and section['flags']==6 and
         section['type']==1 and symbol['size']==section['size']==expected and
         symbol['value']==(section['address'] if e.kind==2 else 0),
         'Complete measured source function owns exactly624/656 bytes, with no extra allocation/padding')
    need(not [s for s in e.symbols if s['name'] and s['index']==0] and not e.relocations,
         'Strictly resolved component with no hidden undefined/relocation provider')
    need(not any(s['name'] in ('.eh_frame','.debug_frame') and s['size'] for s in e.sections),
         'No unhandled unwind storage')
    rows=field['rows'](e.data(section),section['address'],ctx)
    need(len(rows)==(223 if profile=='fresh-GP624' else 240),'All actual instruction boundaries')
    need(not any(26 in (r['rd'],r['rs1'],r['rs2']) or 27 in (r['rd'],r['rs1'],r['rs2']) for r in rows),
         'No encoded S10/S11 read or write, not merely no symbol/disassembly spelling')
    need((rows[0]['op'],rows[0]['rd'],rows[0]['rs1'],rows[0]['immediate'])==('addi',2,2,-48),
         'Actual48B frame allocation')
    writesSP=[r for r in rows if r['rd']==2]
    need(len(writesSP)==2 and [(r['op'],r['rs1'],r['immediate']) for r in writesSP]==
         [('addi',2,-48),('addi',2,48)],'No alternate/hidden SP modification')
    stack=[r for r in rows if r['rs1']==2 and r['memory_width'] is not None]
    stores=[r for r in stack if r['op']=='sw'];loads=[r for r in stack if r['op']=='lw']
    need(len(stack)==22 and [(r['rs2'],r['immediate']) for r in stores]==SOURCE_SLOTS and
         [(r['rd'],r['immediate']) for r in loads]==SOURCE_SLOTS and
         all(r['memory_width']==32 for r in stack),'Eleven exact register/slot saves and fresh restores, no SP0 spill replacement')
    need(not any(r['rs1']==2 and r not in stack+writesSP for r in rows) and
         not any(r['rs2']==2 for r in rows),'No other syntactic SP-derived address/alias bridge')
    boundaries={r['PC'] for r in rows};calls=[];edges=[]
    for r in rows:
        if r['target'] is not None:
            need(r['target'] in boundaries,'Actual local CFG target is an instruction boundary')
            need(r['op']!='jal' or r['rd']==0,'No hidden direct function call')
            edges.append(dict(site=r['offset'],op=r['op'],target=r['target']-section['address']))
        if r['op']=='jalr':
            if r['rd']==1:
                need(r['rs1'] in (15,16) and r['PC']+r['bytes'] in boundaries,
                     'Real opaque A5/A6 call with valid local RA continuation')
                calls.append(dict(offset=r['offset'],target_register=r['rs1'],RA_offset=r['offset']+r['bytes']))
            else:
                need((r['rd'],r['rs1'],r['immediate'])==(0,1,0),'Only ordinary RET, no new tail transfer')
    need(len(calls)==15 and Counter(r['target_register'] for r in calls)==Counter({15:14,16:1}),
         'All fifteen actual opaque calls remain, not merged/out-of-line substitutes')
    gp=[r for r in rows if 3 in (r['rd'],r['rs1'],r['rs2'])]
    need(not any(r['rd']==3 for r in gp),'No actual GP overwrite by empty-output primitive')
    if profile=='fresh-GP624':
        wanted=[('lbu',10,3,None,148),('lbu',10,3,None,152),('add',10,3,14,None),
                ('addi',11,3,None,128),('addi',11,3,None,128),('lh',10,3,None,42)]
        need([(r['op'],r['rd'],r['rs1'],r['rs2'],r['immediate']) for r in gp]==wanted,
             'Six actual fresh GP-use fields; no cached snapshot substitute')
        at=rows.index(gp[2]);before=rows[at-1];after=rows[at+1]
        need((before['op'],before['rd'],before['rs1'],before['immediate'])==('slli',14,19,2) and
             (after['op'],after['rd'],after['rs1'],after['immediate'],after['memory_width'])==
             ('lhu',18,10,150,16),'Actual fresh GP plus lane*4 then connection LHU at150')
        first=rows.index(gp[3]);second=rows.index(gp[4]);attribute=rows.index(gp[5])
        next_calls=[next(i for i in range(start+1,len(rows)) if rows[i]['op']=='jalr' and rows[i]['rd']==1)
                    for start in (first,second)]
        need(any(r['op']=='jalr' and r['rd']==1 for r in rows[second:attribute]) and
             all(stop-start<=3 and not any(r['rd']==11 for r in rows[start+1:stop])
                 for start,stop in zip((first,second),next_calls)),
             'Fresh gate GP+128 and post-gate attribute GP+42 uses retain actual call frontiers')
    else:
        need(len(gp)==16 and all(r['op']=='mv' and r['rs1']==3 for r in gp),
             'Archived fixed-only656 still contains sixteen measured snapshots')
    return dict(symbol=symbol,owner=section,rows=rows,calls=calls,edges=edges,
                GP=gp,stack=stack,stores=stores,loads=loads)


def ir_contract(text,profile):
    calls=[line for line in text.splitlines() if 'asm sideeffect "jalr ra,a' in line]
    need(len(calls)==15,'All fifteen inline opaque primitives in actual IR')
    for line in calls:
        for reg in range(10,18):
            need('={x'+str(reg)+'}' in line and ',{x'+str(reg)+'}' in line,
                 'All eight raw argument read/write bindings retained')
        for reg in (1,5,6,7,28,29,30,31):
            need('~{x'+str(reg)+'}' in line,'Original honest caller clobber retained')
    if profile=='fresh-GP624':
        need(text.count('asm sideeffect "", "={x3},~{memory}"')==6 and 'asm sideeffect "mv $0,gp"' not in text,
             'Actual six fresh fixed-GP outputs, no entry/postcall GP snapshots')
    else:
        need(text.count('asm sideeffect "mv $0,gp"')==16,'Archived sixteen snapshot IR sites')
    for width in (8,16,32):
        need('load volatile i'+str(width) in text and 'store volatile i'+str(width) in text,
             'Actual typed volatile memory width '+str(width))
    return dict(opaque_calls=15,readwrite_argument_GPRs=list(range(10,18)),
                complete_original_scratch_residue_proved=False,
                GP_output_sites=6 if profile=='fresh-GP624' else 16)


def controls(e,ctx,field,profile):
    result=[];E=ctx['ELF'];facts=contract(e,ctx,field,profile);section=facts['owner']
    class Bytes:
        def __init__(self,raw):self.raw=raw
        def read_bytes(self):return self.raw
    def reject(name,raw):
        try:contract(E(Bytes(bytes(raw))),ctx,field,profile)
        except (ValueError,IndexError,StopIteration) as error:
            result.append(dict(name=name,rejected=True,reason=str(error),mutated_sha256=H(raw)));return
        raise ValueError('Actual malformed register/frame artifact admitted '+name)
    p=bytearray(e.raw);at=section['offset']+facts['loads'][1]['offset']
    h=int.from_bytes(p[at:at+2],'little');p[at:at+2]=((h&~(31<<7))|(26<<7)).to_bytes(2,'little')
    reject('restore_writes_reserved_S10',p)
    p=bytearray(e.raw);at=section['offset']+facts['stores'][0]['offset']
    h=int.from_bytes(p[at:at+2],'little');p[at:at+2]=(h&~((15<<9)|(3<<7))).to_bytes(2,'little')
    reject('RA_save_replaced_by_SP0_spill',p)
    p=bytearray(e.raw);at=section['offset']+facts['calls'][0]['offset']
    h=int.from_bytes(p[at:at+2],'little');p[at:at+2]=(h&~0x1000).to_bytes(2,'little')
    reject('opaque_call_does_not_link_RA',p)
    if profile=='fresh-GP624':
        p=bytearray(e.raw);at=section['offset']+facts['GP'][4]['offset'];w=struct.unpack_from('<I',p,at)[0]
        struct.pack_into('<I',p,at,(w&~(31<<15))|(9<<15));reject('postcopy_gate_uses_cached_S1_instead_of_live_GP',p)
    p=bytearray(e.raw);table=next(s for s in e.sections if s['type']==2)
    number=next(i for i,s in enumerate(e.symbol_tables[table['index']]) if s['name']==NAME)
    struct.pack_into('<I',p,table['offset']+number*16+8,632);reject('fabricated_FUNC632_extent',p)
    return result


def recipes(root,folder,profile):
    record=json.loads((folder/'probe.json').read_bytes());commands=record['commands'];mode=record['mode']
    need(mode in ('c','cpp') and record['profile_additions']==['-ffixed-x26','-ffixed-x27'],
         'Only the single declared register reservation profile')
    old=next(p for p in (root/'apk-analysis/tsl9-v4160-event-callback-2026-10-22/implementation/verify_native.py',
                        root/'analysis/v4160-event-callback-2026-10-22/implementation/verify_native.py') if p.is_file())
    need(sha(old)=='783918ed872b02c62321d1997bb4be2db08447f0f1d1def10a722c209f06fa8f',
         'Immutable base658 flags/layout definition')
    base=runpy.run_path(str(old));flags=base['flags'](mode)+['-ffixed-x26','-ffixed-x27']
    source=root/('experiments/tsl9-v4160-callback-registers/src' if profile=='fresh-GP624' else
                 'experiments/tsl9-v4160-event-callback/src')/'callback.c'
    cc=commands[0]['argv'][0];ld=commands[3]['argv'][0];objdump=commands[4]['argv'][0]
    expected=[('compiler-resource-dir',[cc,'-print-resource-dir']),
              ('native-object',[cc,*flags,'-c','-MD','-MF',folder/'callback.d','-MT','callback.o',source,'-o',folder/'callback.o']),
              ('native-IR',[cc,*flags,'-S','-emit-llvm',source,'-o',folder/'callback.ll']),
              ('strict-component-link',[ld,'-m','elf32lriscv','--no-relax','--build-id=none','-T',folder/'component.ld',
                                        folder/'callback.o','-o',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
              ('complete-static-disassembly',[objdump,'--mattr=+m,+a,+c,+zicsr','-d',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'])]
    need([(r['label'],r['argv']) for r in commands]==[(label,[str(x) for x in argv]) for label,argv in expected],
         'Exact observed source/flags/object/IR/strictlink/disassembly chronology')
    for command in commands:
        need(command['exit']==0 and sha(folder/command['log'])==command['sha256'],
             'Actual native tool log and successful exit')
    need((folder/'component.ld').read_bytes()==base['LAYOUT'].encode(),
         'Exact scratch-layout witness, not an original-placement claim')
    for name,pin in record['source_pins'].items():
        need(sha(Path(name))==pin,'Stable recorded source/tool/resource identity')
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h'
    text=(folder/'callback.d').read_text().replace('\\\n',' ').replace('\\\r\n',' ')
    target,_,tail=text.partition(':');need(target=='callback.o','Actual compiler MD target')
    actual={Path(re.sub(r'\\(.)',r'\1',token)).resolve() for token in re.findall(r'(?:\\.|[^\s])+',tail)}
    required={source,source.with_name('callback.h'),source.with_name('io.h'),resource}
    need(actual==required,'Exact actual three-source and compiler-resource dependency closure')
    return dict(mode=mode,commands=5,only_profile_additions=['-ffixed-x26','-ffixed-x27'],
                source_files=[dict(path=p.relative_to(root).as_posix(),sha256=sha(p)) for p in
                              (source,source.with_name('callback.h'),source.with_name('io.h'))],
                resource_sha256=sha(resource),actual_recipe_identity_passed=True,
                HOST_tests_rerun=False)


def inspect(root,folder):
    need(folder.is_relative_to(root),'Actual native folder inside explicit root')
    field=runpy.run_path(str(HERE/'fields.py'));ctx=field['context'](root);E=ctx['ELF']
    e=E(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf');o=E(folder/'callback.o')
    symbol=next(s for s in e.symbols if s['name']==NAME)
    profile='fresh-GP624' if symbol['size']==624 else 'fixed-only656'
    facts=contract(e,ctx,field,profile);unlinked=contract(o,ctx,field,profile)
    need(e.data(facts['owner'])==o.data(unlinked['owner']),'Actual linked bytes equal sole resolved compiler provider')
    text=runpy.run_path(str(HERE/'llvm.py'))['parse']((folder/'complete-static-disassembly.log').read_text())
    need([{k:v for k,v in r.items() if k!='offset'} for r in facts['rows']]==text,
         'Every actual raw instruction operand matches independent LLVM-text normalization')
    ir=ir_contract((folder/'callback.ll').read_text(),profile)
    baseline=json.loads((HERE/'baselines.json').read_bytes());old=baseline['sealed658']
    original_RAs=[p-0x8614+2 for p in (0x8640,0x865c,0x8666,0x86e0,0x8704,0x873c,0x87a2,
                   0x87ba,0x87c6,0x87d8,0x87f8,0x8812,0x882c,0x886a,0x8884)]
    return dict(schema='TSL9-callback-register-profile-independent-v1',actual_native_artifacts_read=True,
                profile=profile,actual_folder=folder.relative_to(root).as_posix(),
                allocated_bytes=facts['owner']['size'],instructions=len(facts['rows']),
                real_functions=[dict(name=NAME,bytes=symbol['size'],info=18,other=0)],
                code_sha256=H(e.data(facts['owner'])),ELF_sha256=sha(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'),
                object_sha256=sha(folder/'callback.o'),IR_sha256=sha(folder/'callback.ll'),
                baseline_bytes=old['bytes'],baseline_instructions=len(old['rows']),
                source_extent_bytes=632,mathematical_size_fits=symbol['size']<=632,
                unowned_original_tail_bytes=max(0,632-symbol['size']),whole632_storage_covered=False,
                frame_bytes=48,saves=facts['stores'],fresh_restores=facts['loads'],
                syntactic_stack_spill_substitution=False,S10_S11_encoded_uses=[],
                GP=facts['GP'],call_frontiers=facts['calls'],local_CFG=facts['edges'],
                all_memory_operands=[r for r in facts['rows'] if r['memory_width'] is not None],
                all_written_GPRs=sorted({r['rd'] for r in facts['rows'] if r['rd'] not in (None,0)}),
                original_call_RA_offsets=original_RAs,
                original_RA_offsets_preserved=sorted(r['RA_offset'] for r in facts['calls'])==sorted(original_RAs),
                IR_contract=ir,recipes=recipes(root,folder,profile),
                actual_artifact_countercases=controls(e,ctx,field,profile),
                HOST_suite_rerun=False,target_execution=False,ISA_emulation=False,
                original_full_ABI_admitted=False,placement_admitted=False,hardware_OTA_proved=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path)
    a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(a.folder is None and a.receipt is None,'Readonly actual replay')
        before=json.loads(a.replay.read_bytes());result=inspect(root,root/before['actual_folder'])
        need(result==before,'Exact independent actual artifact readback')
    else:
        need(a.folder is not None and a.receipt is not None and not a.receipt.exists(),'Explicit actual folder/create-only receipt')
        result=inspect(root,a.folder.resolve());a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(passed=True,actual_native_artifacts_read=True,profile=result['profile'],
                         bytes=result['allocated_bytes'],instructions=result['instructions'],
                         mathematical_size_fits=result['mathematical_size_fits'],
                         whole632_storage_covered=False,original_full_ABI_admitted=False,
                         placement_admitted=False,hardware_OTA_proved=False)))
