"""Independent static native review. Matches admitted instruction sequences; no ISA execution."""
from pathlib import Path
import argparse, hashlib, json, re, runpy, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=HERE.parent/'source'
PARSER=ROOT/'apk-analysis/tsl9-v4160-reset-memory-2026-10-21/compiler-review/elf32.py'
SHA=lambda b:hashlib.sha256(b).hexdigest()
NAMES={'quarter':(0x9c0a,64),'status':(0x18e90,8),'unlock':(0x18e98,30),'lock':(0x18eb6,14),'erase':(0x18ec4,46),'program':(0x18ef2,100)}
SOURCE_PINS={'flash_native.c':'a937b855436127a16300ea62ee5a0b44fe09ab0c0e19a0395ee15bcc34025494','flash_native.h':'b26fe2050e88708e7d18257841f5682ac49fcd4b402aac42ffc5aaae649dd7bd','native_io.h':'77a46db44e17958027dd01caa6c730fcd4172bce14d56d774876e909b56d3503'}
# Each line describes actual admitted encodings, not a simulation or a generated expected result.
PATTERNS={
'quarter':'''addi 2 2 -32
sw 2 1 28
sw 2 8 24
sw 2 9 20
mv 9 10
sw 2 11 12
addi 8 0 136
csrc 0 8 2048
jal 1 tsl9_flash_unlock_18e98
addi 10 0 49
jal 1 tsl9_flash_status_18e90
mv 10 9
jal 1 tsl9_flash_erase_18ec4
lw 11 2 12
mv 10 9
jal 1 tsl9_flash_program_18ef2
jal 1 tsl9_flash_lock_18eb6
csrs 0 8 2048
lw 1 2 28
lw 8 2 24
lw 9 2 20
addi 2 2 32
ret 1''',
'status':'''lui 15 1073881088
sw 15 10 12
ret 1''',
'unlock':'''lui 15 1073881088
lui 13 1164378112
addi 13 13 291
sw 15 13 4
lui 14 3455029248
addi 14 14 -1621
sw 15 14 4
sw 15 13 36
sw 15 14 36
ret 1''',
'lock':'''lui 14 1073881088
lw 15 14 16
lui 13 32768
or 15 15 13
sw 14 15 16
ret 1''',
'erase':'''lui 15 1073881088
lw 14 15 16
andi 10 10 -256
lui 13 131072
or 13 13 14
sw 15 13 16
sw 15 10 20
lw 13 15 16
ori 13 13 64
sw 15 13 16
lw 13 15 12
andi 13 13 1
bne 13 0 28
lw 14 15 16
lui 13 4294836224
addi 13 13 -1
and 14 14 13
sw 15 14 16
ret 1''',
'program':'''lui 14 1073881088
lw 12 14 16
lui 13 65536
or 12 12 13
sw 14 12 16
lw 12 14 12
andi 12 12 1
bne 12 0 12
lw 12 14 12
andi 12 12 2
bne 12 0 18
andi 10 10 -256
addi 12 0 256
addi 15 0 0
add 13 15 11
lw 16 13 0
add 13 15 10
sw 13 16 0
lw 13 14 12
andi 13 13 2
bne 13 0 50
addi 15 15 4
bne 15 12 34
lw 13 14 16
lui 15 2097152
or 13 13 15
sw 14 13 16
lui 15 1073881088
lw 13 15 12
andi 13 13 1
bne 13 0 76
lw 14 15 16
lui 13 4294901760
addi 13 13 -1
and 14 14 13
sw 15 14 16
ret 1'''}
EXPECTED_RD={'quarter':{1,2,8,9,10,11},'status':{15},'unlock':{13,14,15},'lock':{13,14,15},'erase':{10,13,14,15},'program':{10,12,13,14,15,16}}
IR_COUNTS={'quarter':(1,1),'status':(0,1),'unlock':(0,4),'lock':(1,1),'erase':(4,4),'program':(8,4)}


def need(v,why):
    if not v: raise ValueError(why)


def tool_digest(path,observed_tools=None):
    if observed_tools is not None:
        observed=observed_tools[str(path)]
        before=observed['before_sha256'];after=observed['after_sha256']
        need(before==after and re.fullmatch('[0-9a-f]{64}',before) is not None,'actual before/after tool identity')
        if path.is_file():need(SHA(path.read_bytes())==before,'present explicit tool identity')
        return before
    # The actual tool bytes were observed once; retained-artifact replay need not install Windows tools.
    pins=json.loads((HERE/'tool-pins.json').read_bytes())['tools']
    basename=str(path).replace('\\','/').rsplit('/',1)[-1]
    expected=pins[basename]['sha256']
    if path.is_file():need(SHA(path.read_bytes())==expected,'current local tool matches observed byte pin')
    return expected


def pinned_helpers(project_root=None,parser_path=None):
    need(SHA((SOURCE/'seal.json').read_bytes())=='67f43fd3bf0f8e94d316952ab931109e5069f06c6078152bf3c6995dad9b423d','original source seal')
    seal=json.loads((SOURCE/'seal.json').read_bytes())
    for row in seal['members']: need(SHA((SOURCE/row['path']).read_bytes())==row['sha256'],'original source member '+row['path'])
    root=Path(project_root).resolve() if project_root else ROOT
    parser=Path(parser_path).resolve() if parser_path else root/PARSER.relative_to(ROOT)
    need(SHA(parser.read_bytes())=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','ELF parser')
    return runpy.run_path(str(SOURCE/'inspect.py'))['decode'],runpy.run_path(str(parser))['ELF']


def raw_rows(body,decode):
    pc=0;out=[]
    while pc<len(body):
        row=decode(body,pc+0x8000);row['offset']=pc
        if row['target'] is not None:row['target']-=0x8000
        out.append(row);pc+=row['bytes']
    need(pc==len(body),'whole native instruction coverage')
    return out


def native_contract(name,body,relocations,decode):
    rows=raw_rows(body,decode);refs={r['offset']:r for r in relocations};lines=[]
    for r in rows:
        op=r['op'];d=r['rd'];s=r['rs1'];t=r['rs2'];imm=r['immediate']
        if op=='jal':
            need(name=='quarter' and r['offset'] in refs and refs[r['offset']]['type']==17 and refs[r['offset']]['addend']==0,'admitted call relocation')
            line=f"jal {d} {refs[r['offset']]['symbol']['name']}"
        elif op=='bne':line=f"bne {s} {t} {r['target']}"
        elif op=='sw':line=f"sw {s} {t} {imm}"
        elif op=='ret':line=f'ret {s}'
        elif op in ('mv',):line=f'{op} {d} {s}'
        elif op=='lui':line=f'{op} {d} {imm}'
        elif op in ('add','or','and'):line=f'{op} {d} {s} {t}'
        else:line=f'{op} {d} {s} {imm}'
        lines.append(line)
    expected=PATTERNS[name].splitlines()
    need(lines==expected,'complete native semantic pattern '+name)
    need({r['rd'] for r in rows if r['rd'] not in (None,0)}==EXPECTED_RD[name],'actual destination set '+name)
    need(len(refs)==(5 if name=='quarter' else 0),'no hidden relocations '+name)
    boundaries={r['offset'] for r in rows}
    for r in rows:
        if r['op']=='bne':need(r['target'] in boundaries,'native branch boundary')
    return rows


def ir_contract(name,ir):
    counts=(ir.count('load volatile i32'),ir.count('store volatile i32'))
    need(counts==IR_COUNTS[name],'volatile IR width/count '+name)
    need(not re.search(r'(load|store) volatile i(?:8|16|64)\b',ir),'only word-width volatile accesses')
    if name=='quarter':
        need('i64 20' in ir and 'csrc 0x800' in ir and 'csrs 0x800' in ir and 'li $0,136' in ir,'frame and CSR IR')
    if name=='program':
        need('i32 256' in ir and 'add i32' in ir and 'i32 -65537' in ir and '2097152' in ir,'program IR commitments')
        need('={x10},{x11},{x12},{x13},{x14},{x15},{x16},{x10},~{memory}' in ir,'normal output fixed GPR bridge')
    return counts


def linked_review(path,folder,decode,ELF,project_root=None):
    root=Path(project_root).resolve() if project_root else ROOT
    e=ELF(path);need(e.kind==2,'linked executable ELF');rows=[];owners=set()
    need(not any(s['name'] for s in e.symbols if s['index']==0),'linked no undefined symbol')
    for name,(address,limit) in NAMES.items():
        symbolname='tsl9_flash_'+name+'_'+format(address,'x')
        syms=[s for s in e.symbols if s['name']==symbolname];need(len(syms)==1,'linked function identity')
        s=syms[0];need(s['value']==address and s['info']&15==2,'original entry address')
        owner=e.sections[s['index']];owners.add(owner['index'])
        need(owner['address']==address and owner['size']==s['size'] and owner['flags']==6,'dedicated bounded code owner')
        o=ELF(folder/(name+'.o'));os=next(s for s in o.symbols if s['name']==symbolname);body=e.function_bytes(s);expected=bytearray(o.function_bytes(os))
        calls=[]
        if name=='quarter':
            for r in o.relocations:
                target=next(v for k,(v,_) in NAMES.items() if r['symbol']['name']=='tsl9_flash_'+k+'_'+format(v,'x'))
                site=address+r['offset'];delta=target-site
                need(delta%2==0 and -(1<<20)<=delta<(1<<20),'JAL target representable')
                d=delta&0x1fffff
                word=0xef|((d>>20)&1)<<31|((d>>1)&1023)<<21|((d>>11)&1)<<20|((d>>12)&255)<<12
                expected[r['offset']:r['offset']+4]=word.to_bytes(4,'little')
                calls.append(dict(site=site,target=target))
        need(body==expected,'actual linked bytes equal objects plus exact five JAL fixups')
        actual=raw_rows(body,decode)
        linkedcalls=[dict(site=address+r['offset'],target=address+r['target']) for r in actual if r['op']=='jal']
        need(linkedcalls==calls,'actual linked JAL encoded targets')
        rows.append(dict(name=name,address=address,bytes=len(body),limit=limit,section=owner['name'],body_sha256=SHA(body),calls=calls))
    allocated={s['index'] for s in e.sections if s['flags']&2 and s['size']}
    need(allocated==owners,'no unreviewed allocated section in component ELF')
    need(not e.relocations,'component linker consumed every relocation')
    return dict(path=path.relative_to(root).as_posix(),sha256=SHA(path.read_bytes()),functions=rows,allocated_sections=len(owners),normal_component_layout_admitted=True,full_original_image=False,remaining_program_tail_ownership_proved=False)


def review(folder,linked=None,project_root=None,parser_path=None,observed_tools=None,source_dir=None,firmware_path=None):
    """Explicit context only relocates inputs/tool observations; all code/ABI gates stay fixed."""
    root=Path(project_root).resolve() if project_root else ROOT
    folder=folder.resolve();decode,ELF=pinned_helpers(root,parser_path);functions=[]
    native_source=Path(source_dir).resolve() if source_dir else root/'experiments/tsl9-v4160-flash-native/src'
    firmware=Path(firmware_path).resolve() if firmware_path else root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    for n,digest in SOURCE_PINS.items():need(SHA((native_source/n).read_bytes())==digest,'frozen native source '+n)
    producer=json.loads((folder/'probe.json').read_bytes());need({n:producer['source'][n] for n in SOURCE_PINS}==SOURCE_PINS,'actual producer native core snapshot')
    profile=[]
    allowed={'quarter':{1,2,8,9,10,11,12,13,14,15,16},'status':{10,15},'unlock':{10,13,14,15},'lock':{10,13,14,15},'erase':{10,13,14,15},'program':{10,11,12,13,14,15,16}}
    for row in producer['functions']:
        need(row['compiled'],'actual compiler success')
        compiler_commands=[c for c in row['commands'] if '-c' in c['argv'] or '-emit-llvm' in c['argv']]
        need(len(compiler_commands)==2,'actual object and IR commands')
        for command in row['commands']:
            need(command['exit']==0 and SHA((folder/command['log']).read_bytes())==command['log_sha256'],'actual command exit and log binding')
        for command in compiler_commands:
            argv=command['argv']
            for flag in ('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-enable-machine-outliner=never','-mno-relax','-fno-unwind-tables','-fno-asynchronous-unwind-tables'):need(flag in argv,'actual bounded native profile '+flag)
            fixed={int(s[9:]) for s in argv if s.startswith('-ffixed-x')}
            need(fixed==set(range(1,32))-allowed[row['name']],'actual fixed register profile')
        tool=Path(compiler_commands[0]['argv'][0])
        profile.append(dict(name=row['name'],compiler_sha256=tool_digest(tool,observed_tools),allocatable_GPRs=sorted(allowed[row['name']]),actual_commands=compiler_commands))
    for name,(address,limit) in NAMES.items():
        path=folder/(name+'.o');e=ELF(path);symname='tsl9_flash_'+name+'_'+format(address,'x')
        symbols=[s for s in e.symbols if s['info']&15==2 and s['index'] and s['size']]
        need(len(symbols)==1 and symbols[0]['name']==symname,'one actual compiled function '+name);symbol=symbols[0]
        body=e.function_bytes(symbol);rows=native_contract(name,body,e.relocations,decode)
        allocated=[s for s in e.sections if s['flags']&2 and s['size']]
        need(len(allocated)==1 and allocated[0]['index']==symbol['index'] and allocated[0]['size']==len(body) and allocated[0]['flags']==6,'one bounded executable allocation '+name)
        writable=[s['name'] for s in e.sections if s['flags']&3==3 and s['size']]
        need(not writable,'no hidden writable allocation '+name)
        und=sorted(s['name'] for s in e.symbols if s['index']==0 and s['name'])
        expected_und=sorted('tsl9_flash_'+n+'_'+format(a,'x') for n,(a,_) in NAMES.items() if n!='quarter') if name=='quarter' else []
        need(und==expected_und,'defined/undefined ABI surface '+name)
        irpath=folder/(name+'.ll');ir=irpath.read_text(encoding='utf-8')
        counts=ir_contract(name,ir)
        original_raw=firmware.read_bytes()
        need(SHA(original_raw)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','actual original firmware')
        original=original_raw[address-0x8000:address-0x8000+limit]
        functions.append(dict(name=name,address=address,bytes=len(body),original_bytes=limit,fits=len(body)<=limit,byte_identical_to_original=len(body)==limit and body==original,encoded_GPR_destinations=sorted(EXPECTED_RD[name]),object_sha256=SHA(path.read_bytes()),IR_sha256=SHA(irpath.read_bytes()),IR_volatile_load_store_counts=counts,object_RELA=e.relocations,rows=rows,normal_boundary_contract_admitted=True,pointwise_equivalence=False))
    # These are actual changed instruction bytes, rejected by pattern before object hash comparison.
    mutants=[('quarter',0x0a,'2ec8','source-slot16'),('quarter',0x10,'73200480','CSRset-before-calls'),('quarter',0x0c,'13040008','CSRmask128'),('quarter',0x36,'e240','wrong-RA-slot'),('status',4,'28c7','status-notA0'),('unlock',0x0c,'d8c3','key-order'),('lock',6,'c166','lockbit16'),('erase',6,'137505f8','alignment128'),('erase',0x1e,'898a','erasepollbit1'),('program',0x1c,'13060020','copy512'),('program',0x26,'03980600','source-halfword'),('program',0x2e,'23900601','destination-halfword'),('program',0x38,'8907','stride2'),('program',0x3a,'e394c7fc','loop-wrong-target'),('program',0x4e,'898a','finalpollbit1')]
    negatives=[]
    for name,off,h,label in mutants:
        e=ELF(folder/(name+'.o'));s=next(s for s in e.symbols if s['name']=='tsl9_flash_'+name+'_'+format(NAMES[name][0],'x'));body=bytearray(e.function_bytes(s));new=bytes.fromhex(h);before=body[off:off+len(new)].hex();need(before!=h,'actual machine negative');body[off:off+len(new)]=new
        try:native_contract(name,body,e.relocations,decode)
        except ValueError as ex:negatives.append(dict(name=label,function=name,offset=off,before=before,after=h,rejected=True,reason=str(ex)))
        else:raise ValueError('accepted raw machine mutant '+label)
    ir_negatives=[]
    for name,before,after,label in [('program','load volatile i32','load i32','nonvolatile-source-observation'),('program','{x16},{x10}','{x17},{x10}','wrong-lastword-register'),('quarter','li $0,136','li $0,128','wrong-CSR-mask')]:
        text=(folder/(name+'.ll')).read_text();need(before in text,'actual IR mutation input');mutant=text.replace(before,after,1)
        try:ir_contract(name,mutant)
        except ValueError as ex:ir_negatives.append(dict(name=label,function=name,rejected=True,reason=str(ex),compiled=False))
        else:raise ValueError('accepted IR transcript mutant '+label)
    layout=linked_review(linked.resolve(),folder,decode,ELF,root) if linked else None
    if linked:
        commands=producer['link_commands'];need(len(commands)==2,'actual link and disassembly commands')
        for command in commands:need(command['exit']==0 and SHA((folder/command['log']).read_bytes())==command['log_sha256'],'actual link command/log binding')
        argv=commands[0]['argv'];need('--no-relax' in argv and '--no-undefined' in argv,'strict actual component linker flags')
        layout['actual_commands']=commands;layout['linker_sha256']=tool_digest(Path(argv[0]),observed_tools);layout['link_script_sha256']=SHA((folder/'original-entry-component.ld').read_bytes())
    return dict(schema='ID2966-flash-independent-native-review-v1',passed=True,build_root=folder.relative_to(root).as_posix(),source_pins=SOURCE_PINS,source_seal_sha256=SHA((SOURCE/'seal.json').read_bytes()),actual_profile=profile,producer_receipt_sha256=SHA((folder/'probe.json').read_bytes()),functions=functions,component_link=layout,all_six_normal_boundaries_admitted=True,all_six_fit=all(x['fits'] for x in functions),raw_machine_negatives=negatives,IR_transcript_negatives=ir_negatives,original_stack_source_slot=12,compiled_stack_source_slot=12,original_frame_store_order=['S0@24','S1@20','RA@28','A1@12'],compiled_frame_store_order=['RA@28','S0@24','S1@20','A1@12'],exact_frame_prefix_equivalence=False,program_A0_alignment_original_PC=0x18efa,program_A0_alignment_compiled_offset=0x18,program_A0_alignment_moved_after_initial_polls=True,program_loop_words=64,program_unused_original_tail_bytes=6,full_image_integration=False,pointwise_async_equivalence=False,nonreturn_physical_GPR_prefix_equivalence=False,hardware_success=False,target_execution=False,emulation=False,network=False,new_BIN=False)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--build-root',type=Path,required=True);ap.add_argument('--linked-elf',type=Path);ap.add_argument('--report',type=Path,required=True);ap.add_argument('--check',action='store_true')
    ap.add_argument('--project-root',type=Path);ap.add_argument('--parser-path',type=Path);ap.add_argument('--source-dir',type=Path);ap.add_argument('--firmware-path',type=Path);ap.add_argument('--observed-tools',type=Path);a=ap.parse_args()
    observed=json.loads(a.observed_tools.read_bytes()) if a.observed_tools else None
    report=review(a.build_root,a.linked_elf,project_root=a.project_root,parser_path=a.parser_path,observed_tools=observed,source_dir=a.source_dir,firmware_path=a.firmware_path);payload=(json.dumps(report,indent=2)+'\n').encode('utf-8')
    if a.check:need(a.report.read_bytes()==payload,'exact readonly replay')
    else:need(a.report.resolve().is_relative_to(HERE),'own review output only');a.report.write_bytes(payload)
    print(json.dumps(dict(passed=True,functions=len(report['functions']),all_fit=report['all_six_fit'],machine_negatives=len(report['raw_machine_negatives']),full_image=False)))
