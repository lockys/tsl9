"""Independent ET_REL/operand/IR/MD audit. Never links or executes target code."""
import collections
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE=Path(__file__).resolve().parent
MODEL='experiments/tsl9-v4160-ota-handler-compact/src/'
OLD='apk-analysis/tsl9-v4160-callback-registers-2026-10-22/ABI-review/'
SOURCE='apk-analysis/tsl9-v4160-ota-handler-2026-10-22/source-review/'
PINS={OLD+'fields.py':'373d78c75feb58fcbf621d924733249786c8243197f8eef4e0a52e33e304b413',
      OLD+'llvm.py':'c52cc458441eab2038ff4bb5064666ec87af3b2345f5c8b99cf9fdcc0ffb0fd5',
      SOURCE+'carrier-roles.json':'cf1e2034779d0223504f7eebb287bd3c4b81281dfc52611e4906099844d78cf1',
      SOURCE+'instructions.json':'c7fea72fc7a928117cc198117ca1119e6afe222a39d03b5e884b730309b8d43f',
      SOURCE+'contracts.json':'83a87f68eb9d7aa0528ff68ed57cd8a14103509f869924b77b1f0c42b55ab118',
      SOURCE+'raw.py':'2d63d9f450413447794116100f538acc0f3a9e33a1f69102875ff8132b6c092f',
      'apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py':'fc3005e95419c73ab82a4554d3f0af5b3174b1a95736d52d656cefc5678289ab'}
DIRECT={'__tsl9v4160_ota_code_92f2':4,'__tsl9v4160_call_9c0a':1,
        '__tsl9v4160_call_9124':4,'__tsl9v4160_ota_code_13f66':1,
        '__tsl9v4160_conditional_code_13e98':1,'__tsl9v4160_ota_code_9b8e':1}
ADDRESSES={'__tsl9v4160_ota_code_8e18':2,'__tsl9v4160_ota_code_9ee0':1,
           '__tsl9v4160_captured_body_99e8':1}
NAME='tsl9_ota_handler_native_9c4a'


def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def locate(root,relative):
    p=root/relative
    if not p.is_file() and relative.startswith('apk-analysis/tsl9-'):
        p=root/relative.replace('apk-analysis/tsl9-','analysis/',1)
    need(p.is_file(),'Pinned helper/evidence '+relative);return p


def context(root):
    modules={}
    for relative,pin in PINS.items():
        path=locate(root,relative);need(sha(path)==pin,'Immutable source/decoder '+relative)
        if path.suffix=='.py':modules[path.name]=runpy.run_path(str(path))
    fields=modules['fields.py'];ctx=fields['context'](root);previous=ctx['extension'];extension=modules['raw.py']['decode']
    ctx['extension']=lambda raw,pc,base:extension(raw,pc,lambda b,p:previous(b,p,base))
    return fields,modules['llvm.py'],ctx


def machine(rows,relocations,size):
    bypc={r['PC']:r for r in rows};first=rows[0]
    need(first['op']=='addi' and first['rd']==first['rs1']==2 and first['immediate']<0,
         'Actual entry subtracts a concrete stack frame')
    frame=-first['immediate'];need(frame%16==0,'Actual stack frame alignment')
    need(not [r for r in rows if r['rd']==3],'No generated GP writes')
    stacks=[r for r in rows if r['rs1']==2 and r['op'] in ('lw','sw','sb','lbu')]
    for row in stacks:
        need(0<=row['immediate'] and row['immediate']+row['memory_width']//8<=frame,
             'Every SP memory operand lies inside the measured frame')
    direct=collections.Counter();addresses=collections.Counter();resolved=[]
    for relocation in relocations:
        need(relocation['addend']==0 and relocation['offset'] in bypc,'Actual zero-addend instruction relocation')
        row=bypc[relocation['offset']];name=relocation['symbol']['name'];kind=relocation['type']
        need(relocation['symbol']['index']==0 and relocation['symbol']['info']==16
             and relocation['symbol']['value']==0 and relocation['symbol']['size']==0,
             'Every external symbol stays an honest UND/NOTYPE0, never a numeric/fake provider')
        if kind==17:
            need(name in DIRECT and row['op']=='jal' and row['rd']==1 and row['bytes']==4,
                 'True direct-call JAL relocation writes RA')
            direct[name]+=1
        elif kind in (26,27):
            need(name in ADDRESSES and row['op']==('lui' if kind==26 else 'addi'),
                 'Real unresolved callback address HI20/LO12_I instruction role')
            addresses[(name,kind)]+=1
        else:raise ValueError('Unexpected relocation/provider role')
        resolved.append(dict(offset=row['PC'],type=kind,name=name,rd=row['rd'],rs1=row['rs1']))
    need(dict(direct)==DIRECT,'All actual direct call occurrences belong to the six expected callees')
    need(dict(addresses)=={(n,t):v for n,v in ADDRESSES.items() for t in (26,27)},
         'All four actual callback materializations have paired real external HI/LO references')
    callsites={r['offset'] for r in relocations if r['type']==17}
    for row in rows:
        if row['target'] is not None and row['PC'] not in callsites:
            need(row['target'] in bypc,'Local control transfer targets an actual instruction start')
    indirect=[r for r in rows if r['op']=='jalr' and r['rd']==1]
    need(len(indirect)==1 and indirect[0]['rs1']==15,'Only the actual alignment-copy call is indirect')
    prior=[r for r in rows if r['PC']<indirect[0]['PC'] and r['rd']==15]
    pointer=prior[-1];need(pointer['op']=='lw' and pointer['memory_width']==32 and pointer['immediate']==0x4c,
                           'Actual indirect target is the fresh32-bit slot4C load')
    need(any(r['op']=='jalr' and r['rd']==0 and r['rs1']==1 for r in rows),'Actual normal return exists')
    return dict(bytes=size,instructions=len(rows),frame_bytes=frame,
                SP_memory_operands=[{k:r[k] for k in ('PC','op','rd','rs2','immediate','memory_width')} for r in stacks],
                direct_call_occurrences=sum(direct.values()),indirect_call_occurrences=1,
                direct_call_counts=dict(sorted(direct.items())),callback_address_materializations=4,
                relocation_fields=resolved,GP_reads=sum(r['rs1']==3 or r['rs2']==3 for r in rows),GP_writes=0,
                mathematical_original530_fit=size<=530,original_frame_bytes=48,
                original_frame_equal=frame==48,original_whole_ABI_admitted=False)


def negative_controls(raw,rows,relocations,fields,ctx):
    base=rows[0]['PC'];size=len(raw);out={}
    def reject(label,body,relas):
        try:machine(fields['rows'](body,base,ctx),relas,size)
        except ValueError:out[label]=True;return
        raise ValueError('Unrejected actual native counterexample '+label)
    changed=bytearray(raw);changed[1]^=0x10
    reject('entry_SP_subtract_changed_to_add',bytes(changed),relocations)
    site=next(r['offset'] for r in relocations if r['type']==17)
    changed=bytearray(raw);changed[site]^=0x80
    reject('direct_JAL_link_register_removed',bytes(changed),relocations)
    row=next(r for r in rows if r['rs1']==3 and r['rd'] not in (None,0) and r['bytes']==4)
    changed=bytearray(raw);word=int.from_bytes(changed[row['PC']:row['PC']+4],'little')
    word^=(row['rd']^3)<<7;changed[row['PC']:row['PC']+4]=word.to_bytes(4,'little')
    reject('actual_GP_read_changed_to_GP_write',bytes(changed),relocations)
    return out


def dependencies(root,folder,record,core):
    mode=record['mode'];need(mode in ('c','cpp'),'Actual native language')
    source=root/MODEL/'ota_handler.c';obj=folder/'ota_handler.o';ir=folder/'ota_handler.ll'
    commands=record['commands'];need(len(commands)==4,'Four actual ET_REL-only native recipes')
    flags=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz',
           '-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector',
           '-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections',
           '-fdata-sections','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++',
           '-std=c11' if mode=='c' else '-std=c++17']+(['-fno-exceptions'] if mode=='cpp' else [])
    compiler=commands[0]['argv'][0];disassembler=commands[3]['argv'][0]
    need(sha(Path(compiler))=='047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6'
         and sha(Path(disassembler))=='de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
         'Actual selected compiler and disassembler binary identities')
    expected=[[compiler,'-print-resource-dir'],
              [compiler,*flags,'-c','-MD','-MF',str(folder/'ota_handler.d'),'-MT','ota_handler.o',str(source),'-o',str(obj)],
              [compiler,*flags,'-S','-emit-llvm',str(source),'-o',str(ir)],
              [disassembler,'--mattr=+m,+a,+c,+zicsr','-d','-r',str(obj)]]
    for command,argv in zip(commands,expected):
        need(command['argv']==argv and command['exit']==0,'Exact actual source/profile/native recipe')
        need(sha(folder/command['log'])==command['sha256'],'Actual native tool output log')
    pins=record['source_pins']
    for name in ('ota_handler.c','ota_handler.h','io.h'):
        path=root/MODEL/name;need(sha(path)==core[name] and pins[str(path)]==core[name],
                                'Current source equals native generation source '+name)
    for path,pin in pins.items():need(sha(Path(path))==pin,'Actual pinned source/tool/resource remains unchanged')
    for name in ('ota_handler.o','ota_handler.ll','ota_handler.d','complete-static-disassembly.log'):
        path=folder/name;need(record['artifacts'][name]==dict(bytes=path.stat().st_size,sha256=sha(path)),
                             'Actual probe binds observed native artifact '+name)
    dep=(folder/'ota_handler.d').read_text().replace('\\\n','')
    target,sep,rest=dep.partition(': ');need(sep and target=='ota_handler.o','Actual MD target object')
    paths={Path(token.replace('\\ ',' ')).resolve() for token in re.findall(r'(?:\\.|[^\s])+',rest)}
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h'
    wanted={root/MODEL/name for name in ('ota_handler.c','ota_handler.h','io.h')}|{resource}
    need(paths==wanted,'Exactly three actual project dependencies and the observed compiler stdint resource')
    return dict(mode=mode,actual_recipes=4,actual_MD_project_inputs=3,actual_MD_resource_inputs=1,
                all_actual_source_tool_resource_hashes_checked=True,native_compiler_invoked_by_review=False)


def inspect(root,folder):
    root=Path(root).resolve();folder=Path(folder).resolve()
    need(folder.is_relative_to(root),'Explicit actual native folder in selected project')
    fields,llvm,ctx=context(root);E=ctx['ELF'];p=folder/'ota_handler.o';e=E(p)
    core=json.loads((HERE/'core-pins.json').read_bytes())
    record=json.loads((folder/'verification.json').read_bytes())
    need(record['schema']=='TSL9-readable-OTA-handler-native-formal-v1','Actual frozen formal native schema')
    deps=dependencies(root,folder,record,core)
    need(e.kind==1 and e.flags==1,'Actual RV32/RVC ET_REL; no executable/witness provider substituted')
    funcs=[s for s in e.symbols if s['info']&15==2 and s['index'] not in (0,65521)]
    need(len(funcs)==1 and funcs[0]['name']==NAME and funcs[0]['info']==18 and funcs[0]['other']==0,
         'Exactly one honest GLOBAL FUNC with its actual compiler size')
    f=funcs[0];sec=e.sections[f['index']];raw=e.function_bytes(f)
    need(f['value']==0 and f['size']==sec['size'] and sec['type']==1 and sec['flags']==6 and sec['alignment']==2,
         'Real function owns the complete AX source allocation')
    need([s for s in e.sections if s['flags']&2 and s['size']]==[sec],
         'No extra allocated helper/data/unwind/padding storage')
    undefined=[s for s in e.symbols if s['index']==0 and s['name']]
    need({s['name'] for s in undefined}==set(DIRECT)|set(ADDRESSES) and len(undefined)==9,
         'Exactly six direct-callee plus three callback-address true UND obligations')
    absolute=[s for s in e.symbols if s['index']==65521]
    need(absolute==[dict(name='ota_handler.c',value=0,size=0,info=4,other=0,index=65521)],
         'Only actual nonprovider STT_FILE metadata may be absolute; no numeric ABS provider')
    rows=fields['rows'](raw,0,ctx)
    textrows=llvm['parse']((folder/'complete-static-disassembly.log').read_text())
    need([{k:v for k,v in r.items() if k!='offset'} for r in rows]==textrows,
         'Every actual native raw byte/operand agrees with independent LLVM text fields')
    need(all(r['owner']==sec['name'] for r in e.relocations),'Every native relocation belongs to the true function')
    measured=machine(rows,e.relocations,len(raw));controls=negative_controls(raw,rows,e.relocations,fields,ctx)
    source_delta=runpy.run_path(str(HERE/'source_delta.py'))['inspect'](root)
    loop_module=runpy.run_path(str(HERE/'loop.py'))
    quarter_loop=loop_module['quarter'](rows,e.relocations)
    frame_contents=loop_module['frame_contents'](rows)
    loop_controls=loop_module['controls'](raw,rows,e.relocations,fields,ctx)
    text=(folder/'ota_handler.ll').read_text();calls=collections.Counter(re.findall(r'asm sideeffect "jal ra,([^" ]+)"',text))
    need(dict(calls)==DIRECT and text.count('asm sideeffect "jalr ra,a5,0"')==1,
         'Independent LLVM IR contains the same six true direct-callee identities and indirect copy')
    need(len(re.findall(r'^define ',text,re.M))==1 and 'define dso_local i32 @'+NAME+'(' in text,
         'Actual one-function IR native interface; no invented linked provider')
    response=loop_module['response_ir'](text)
    roles=json.loads(locate(root,SOURCE+'carrier-roles.json').read_bytes())['roles']
    oldowner=roles['owner_metadata']['name'];owned=[r for r in roles['RELA'] if r['owner']==oldowner]
    need(len(owned)==51 and len(roles['RELA'])==52 and roles['owner_metadata']['size']==530,
         'Original530/51owned+oneincoming role baseline is retained independently')
    incoming=[r for r in roles['RELA'] if r['owner']!=oldowner]
    actual={name:dict(bytes=(folder/name).stat().st_size,sha256=sha(folder/name)) for name in
            ('ota_handler.o','ota_handler.ll','ota_handler.d','verification.json','complete-static-disassembly.log')}
    return dict(schema='TSL9-OTA-handler-compact-independent-native-v1',passed=True,actual_native_artifacts_read=True,
                actual_folder=folder.relative_to(root).as_posix(),inputs=dict(core=core,source_helpers=PINS,
                checker=sha(HERE/'native.py')),actual_artifacts=actual,dependencies=deps,measured=measured,
                source_delta=source_delta,quarter_loop=quarter_loop,response_IR=response,frame_contents=frame_contents,
                new_helper_pins={n:sha(HERE/n) for n in ('source_delta.py','loop.py')},
                original=dict(bytes=530,instructions=169,frame_bytes=48,owned_RELA=51,recorded_incoming=incoming),
                original_private_role_discharge_complete=False,opaque_raw8_prefix_proved=False,
                normal_native_abi_condition='Conventional callee preservation only; HOST live named-state mutations are not physical-native proof',
                focused_raw_controls=controls,loop_operand_controls=loop_controls,
                actual_providers_linked=False,strict_dependency_closure_proved=False,
                full_original_ABI_admitted=False,original_placement_admitted=False,
                BIN_created=False,HOST_tests_rerun=False,target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)
