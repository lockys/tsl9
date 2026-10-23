#!/usr/bin/env python3
"""Actual peripheral-write composition: bounded ELF, raw operands and source closure."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-peripheral-dispatch-component'
SCHEMA = 'TSL9-peripheral-dispatch-component-v1'
BUILD_SCHEMA = 'TSL9-peripheral-dispatch-link-v1'
P = ["tsl9_dispatch_external_18ca4","tsl9_peripheral_selected_18cc6","tsl9_peripheral_metadata_18cec","tsl9_peripheral_finish_18d5a","tsl9_peripheral_select0_18d5e","tsl9_peripheral_select1_18d62","tsl9_peripheral_alternate_18d66"]
POFF = [0,34,72,182,186,190,194]
PSIZES = [34,38,110,4,4,4,18]
UND = sorted(['tsl9_queue_external_'+s for s in ('9454','9b36','12abe','14d2e')]+['tsl9_dispatch_external_16b7c'])
SECTION = '.peripheral_dispatch_component'
MASKS = {16:(4,0x01fff07f),17:(4,0x00000fff),44:(2,0xe383),45:(2,0xe003)}
OWN = ['build.py','check.py','component.ld','dependencies.json','README.md','readme.zh-TW.md','readme.en.md','verify.sh']


def need(ok,message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def load(path):
    return json.loads(Path(path).read_bytes())


def module(path,name):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def portable(value,root,llvm):
    if isinstance(value,str):
        value = value.replace('\\','/')
        for path,token in ((llvm.parent/'lib/clang/18/include','${CLANG_INCLUDE}'),(root,'${TSL9_ROOT}'),(llvm,'${LLVM_BIN}')):
            value = value.replace(str(path).replace('\\','/'),token)
        return value
    if isinstance(value,(list,tuple)):
        return [portable(x,root,llvm) for x in value]
    if isinstance(value,dict):
        return {portable(k,root,llvm):portable(v,root,llvm) for k,v in value.items()}
    return value

def restored(value,root,llvm):
    return Path(value.replace('${TSL9_ROOT}',str(root)).replace('${LLVM_BIN}',str(llvm))).resolve()


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()


def write_new(path,value):
    with path.open('xb') as stream:
        stream.write(encoded(value))


def dependencies(root):
    value = load(HERE/'dependencies.json')
    need(value['schema'] == 'TSL9-peripheral-dispatch-dependencies-v1' and all(sha(root/p) == h for p,h in value['pins'].items()), 'Pinned direct dependencies')
    return value


def previous(root):
    value = dependencies(root)
    result = module(root/value['previous_checker'],'record_previous_composition')
    result.metadata(root)
    return result


def reader(root):
    value = dependencies(root)
    return module(root/value['raw_reader'],'record_sealed_ELF_reader')


def inputs(root,llvm):
    direct = dependencies(root)
    result = portable(previous(root).inputs(root,llvm),root,llvm)
    peripheral = module(root/direct['peripheral_checker'],'peripheral_formal_input_closure')
    for key,value in portable(peripheral.inputs(llvm),root,llvm).items():
        h = value['sha256']
        need(key not in result or result[key] == h, 'Consistent new transitive input identity')
        result[key] = h
    paths = [HERE/p for p in OWN]+[HERE/'seal.json']+[root/p for p in direct['pins']]
    for path in paths:
        key = portable(str(path),root,llvm)
        value = sha(path)
        need(key not in result or result[key] == value, 'Consistent transitive input identity')
        result[key] = value
    return dict(sorted(result.items()))

def upstream(root,llvm,left,right,mode):
    direct = dependencies(root)
    need(left.name == right.name == mode and all(p.is_relative_to(root/'experiments') for p in (left,right)), 'Actual language-matched owned folders')
    old = previous(root).replay(root,llvm,left/'verification.json')
    need(old['schema'] == 'TSL9-record-dispatch-component-v1' and old['passed'] and old['result']['bytes'] == 950, 'Actual full formal950B previous composition')
    new = module(root/direct['peripheral_checker'],'peripheral_formal_native')
    fresh,text = new.evaluate(root,llvm,right,mode)
    need(load(right/'verification.json') == fresh and (right/'verification.json').read_bytes() == text.encode(), 'Fresh actual formal212B peripheral proof replay')
    return portable(dict(dispatch=dict(receipt=str(left/'verification.json'),sha256=sha(left/'verification.json'),
                              object_sha256=sha(left/'dispatch.o'),inputs=old['inputs'],whole_actual_proof_replayed=True),
                peripheral=dict(receipt=str(right/'verification.json'),sha256=sha(right/'verification.json'),
                            object_sha256=sha(right/'native.o'),inputs=fresh['inputs'],whole_actual_proof_replayed=True)),root,llvm)

def recipes(llvm,folder,left,right):
    return [('link',[llvm/'ld.lld.exe','-r','--no-relax','-T',HERE/'component.ld',left/'dispatch.o',right/'native.o','-o',folder/'dispatch.o']),
            ('dispatch',[llvm/'llvm-objdump.exe','--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',folder/'dispatch.o'])]

def body(e,function):
    s = e['sections'][function['section']]
    need(function['value'] >= 0 and function['value']+function['size'] <= s['size'], 'Complete genuine function storage')
    at = s['offset']+function['value']
    return e['raw'][at:at+function['size']]


def original_gate(root,code,relations):
    base = reader(root)
    fw = (root/base.FIRMWARE).read_bytes()
    need(digest(fw) == base.FW_SHA and len(fw) == 76800, 'Fresh official V4.1.60 identity')
    spans = [(0,314,0x12c58),(314,188,0x82d2),(502,6,0x81aa),(508,18,0x820c),(526,280,0x8a56),(806,102,0x12a08),(908,42,0x821e),(950,212,0x18ca4)]
    original = b''.join(fw[v-0x8000:v-0x8000+z] for _,z,v in spans)
    masks = bytearray(b'\xff'*1162)
    typed = []
    for offset,kind,target,addend in relations:
        need(kind in MASKS and addend == 0, 'Only genuine original control families/zero addends')
        width,mask = MASKS[kind]
        need(0 <= offset <= 1162-width and all(x == 255 for x in masks[offset:offset+width]), 'Complete non-overlapping control extent')
        masks[offset:offset+width] = mask.to_bytes(width,'little')
        at,size,va = next((a,z,v) for a,z,v in spans if a <= offset and offset+width <= a+z)
        pc = va+offset-at
        a,b = base.control(original,offset,kind,pc),base.control(code,offset,kind,pc)
        need({k:v for k,v in a.items() if k != 'target'} == {k:v for k,v in b.items() if k != 'target'}, 'Original control RD/RS/family/RA link retained')
        need(a['target'] == int(target.rsplit('_',1)[1],16), 'Symbol identity equals fresh original decoded destination')
        typed.append(dict(offset=offset,original_PC=pc,original_operand=a,target_symbol=target,pending_raw_target=b['target'],machine_operand_resolved=False))
    need(len(code) == len(original) == 1162 and all(not((a^b)&m) for a,b,m in zip(code,original,masks)), 'Every fresh original non-control bit retained')
    return dict(firmware_sha256=base.FW_SHA,spans=[dict(offset=a,bytes=z,original_VA=v) for a,z,v in spans],
                original_masked_sha256=digest(bytes(v&m for v,m in zip(original,masks))),typed_controls=typed,all_noncontrol_bits_equal=True)


def join(e,left,right,root):
    base = reader(root)
    old = sorted((s for s in left['symbols'] if s['info']&15 == 2),key=lambda s:s['value'])
    need(len(old) == 42 and sum(f['size'] for f in old) == 950, 'All genuine formal previous input bodies')
    names = [f['name'] for f in old]+P
    offsets = [f['value'] for f in old]+[950+x for x in POFF]
    sizes = [f['size'] for f in old]+PSIZES
    functions = [s for s in e['symbols'] if s['info']&15 == 2]
    need(len(functions) == 49 and {s['name'] for s in functions} == set(names), 'All49 genuine FUNCs including cold regions')
    globals_ = [s for s in e['symbols'] if s['info']>>4]
    need(all(s['info']>>4 == 1 and s['other'] == 0 and s['section'] != 0xfff1 for s in globals_), 'Strong visible definitions/references with zero global ABS')
    und = sorted(s['name'] for s in globals_ if s['section'] == 0)
    need(und == UND and all(s['value'] == s['size'] == 0 and s['info'] == 16 for s in globals_ if s['section'] == 0), 'Exactly five genuine zero-value strong UND')
    need({s['name'] for s in globals_} == set(names)|set(UND), 'No additional global objects/providers')
    sections = {s['name']:s for s in e['sections']}
    need(set(sections) == {'',SECTION,'.text','.rela'+SECTION,'.llvm_addrsig','.symtab','.shstrtab','.strtab'}, 'Complete actual section inventory')
    header = struct.unpack_from('<16sHHIIIIIHHHHHH',e['raw'])
    need(header[5] == 0 and header[12] == 8 and header[13] == sections['.shstrtab']['index'], 'No concealed program-header offset and exact section-table identity')
    need(all(s['address'] == 0 for s in e['sections']), 'Diagnostic VMA0 throughout')
    alloc = [s for s in e['sections'] if s['flags']&2 and s['size']]
    need([(s['name'],s['type'],s['flags'],s['address'],s['size'],s['align']) for s in alloc] == [(SECTION,1,6,0,1162,2)], 'Only1162B AX allocation, no hidden code/data')
    section = sections[SECTION]
    need((sections['.text']['size'],sections['.text']['flags'],sections['.text']['type']) == (0,6,1), 'Inherited text is empty')
    for name in ('.strtab','.shstrtab'):
        s = sections[name]
        need((s['type'],s['flags'],s['align'],s['entsize'],s['link'],s['info']) == (3,0,1,0,0,0), 'Exact string-table metadata')
    s = sections['.symtab']
    need((s['type'],s['flags'],s['align'],s['entsize'],s['link']) == (2,0,4,16,sections['.strtab']['index']), 'Exact symbol-table metadata')
    need(all((f['info']>>4 == 0) == (f['index'] < s['info']) for f in e['symbols']), 'Local/global symbol partition')
    s = sections['.rela'+SECTION]
    need((s['type'],s['flags'],s['align'],s['entsize'],s['link'],s['info']) == (4,64,4,12,sections['.symtab']['index'],section['index']), 'Exact RELA ownership metadata')
    addrsig = sections['.llvm_addrsig']
    size = sum(s['size'] for before in (left,right) for s in before['sections'] if s['name'] == '.llvm_addrsig')
    need((addrsig['type'],addrsig['flags'],addrsig['size']) == (0x6fff4c03,0x80000000,size), 'Actual input-derived nonallocated address-significance metadata')
    expected,relations = {},[]
    for before,group,bases in [(left,[f['name'] for f in old],{f['name']:f['value'] for f in old}),(right,P,dict(zip(P,[950+x for x in POFF])))]:
        starts = {}
        for f in before['symbols']:
            if f['name'] in group and f['info']&15 == 2:
                expected[f['name']] = body(before,f)
                start = bases[f['name']]-f['value']
                need(f['section'] not in starts or starts[f['section']] == start, 'Consistent genuine input section mapping')
                starts[f['section']] = start
        for r in before['relocations']:
            need(r['section'] in starts, 'Genuine input code relocation ownership')
            relations.append((starts[r['section']]+r['offset'],r['type'],r['target'],r['addend']))
    actual,facts = {},[]
    for name,offset,size in zip(names,offsets,sizes):
        f = next(s for s in functions if s['name'] == name)
        need((f['info'],f['other'],f['section'],f['value'],f['size']) == (18,0,section['index'],offset,size), 'Exact genuine FUNC definition '+name)
        actual[name] = body(e,f)
        facts.append(dict(name=name,offset=offset,bytes=size,sha256=digest(actual[name])))
    need(actual == expected, 'Every actual input body preserved byte for byte')
    rels = sorted((r['offset'],r['type'],r['target'],r['addend']) for r in e['relocations'])
    need(len(rels) == 57 and rels == sorted(relations), 'All57 pending RELA offsets/families/reindexed symbol identities/addends preserved')
    need(all(r['section'] == section['index'] for r in e['relocations']), 'All pending controls belong to actual code')
    bindings = []
    for name,offset,sites in [('tsl9_queue_external_12a08',806,[282]),('tsl9_queue_external_81aa',502,[300,814]),('tsl9_dispatch_external_821e',908,[832]),(P[0],950,[888])]:
        f = next(s for s in functions if s['name'] == name)
        seen = [r['offset'] for r in e['relocations'] if r['target'] == name]
        input_sites = [r['offset'] for r in left['relocations'] if r['target'] == name]
        need(f['value'] == offset and seen == sites and input_sites == sites, 'Actual input-derived provider callsite and genuine binding '+name)
        bindings.append(dict(symbol=name,definition_offset=offset,reference_offsets=seen,genuine_FUNC=True,
                             resolved_at_symbol_level=True,machine_control_resolved=False))
    code = b''.join(actual[n] for n in names)
    need(code == e['raw'][section['offset']:section['offset']+1162], 'No holes or unowned bytes')
    rows = base.count_instructions(code)
    need(len(rows) == 402, 'Full1162B stream contains402 instructions')
    return dict(bytes=1162,instructions=402,FUNCs=49,private_architectural_regions=46,ordinary_small_C_functions=3,
                functions=facts,code_sha256=digest(code),pending_RELA=57,strong_UND=und,global_ABS=[],
                symbol_bindings=bindings,relocations=[dict(offset=o,type=k,target=t,addend=a) for o,k,t,a in rels],
                original=original_gate(root,code,rels),VMA=0,all_machine_controls_resolved=False,
                ordinary_C_ABI_proved=False,original_placement_proved=False,
                upstream_native_typed_operand_claim='Non-relocated operands retained; original control destinations checked through genuine symbols; seven native branch immediates pending before nominal upstream link.',
                upstream_nominal_212B_original_equal=True),rows

def negatives(e,left,right,root):
    base = reader(root)
    rejected = []
    def reject(name,action):
        try: action()
        except (ValueError,IndexError,KeyError,StopIteration,struct.error): rejected.append(name)
        else: raise ValueError('Accepted actual in-memory regression '+name)
    def mutate(name,at,fmt,value):
        raw = bytearray(e['raw']); struct.pack_into(fmt,raw,at,value)
        reject(name,lambda:join(base.elf(bytes(raw)),left,right,root))
    section = next(s for s in e['sections'] if s['name'] == SECTION)
    symbols = {s['name']:s for s in e['symbols'] if s['name']}
    f = symbols[P[0]]
    mutate('writable_code',section['record']+8,'<I',7)
    mutate('program_header_offset',28,'<I',52)
    mutate('wrong_machine',18,'<H',40)
    mutate('false_load_entry',24,'<I',0x8000)
    for label,delta,fmt,value in [('fake_ABS_provider',14,'<H',0xfff1),('weak_provider',12,'<B',34),('wrong_provider_position',4,'<I',948),('lost_provider_body',8,'<I',32)]:
        mutate(label,f['record']+delta,fmt,value)
    mutate('lost_cold_alternate',symbols[P[-1]]['record']+8,'<I',16)
    mutate('wrong_cold_region',symbols[P[-2]]['record']+4,'<I',1138)
    mutate('nonzero_remaining_UND',symbols[UND[0]]['record']+4,'<I',2)
    for name in ('tsl9_queue_external_12a08','tsl9_queue_external_81aa','tsl9_dispatch_external_821e',P[0]):
        call = next(r for r in e['relocations'] if r['target'] == name)
        mutate('wrong_binding_'+name,call['record']+4,'<I',(symbols[UND[0]]['index']<<8)|call['type'])
    call = next(r for r in e['relocations'] if r['target'] == P[0])
    mutate('wrong_RELA_family',call['record']+4,'<I',(call['symbol']<<8)|16)
    mutate('wrong_RELA_offset',call['record'],'<I',call['offset']+2)
    mutate('nonzero_RELA_addend',call['record']+8,'<i',2)
    for name,offset,mask,width in [('provider_call_without_RA',888,128,4),('provider_first_read',950,4,2),('provider_A6_residue',1146,128,4),('prior_record_frame',806,4,2),('prior_predicate_byte',908,4,2)]:
        at = section['offset']+offset
        mutate(name,at,'<I' if width == 4 else '<H',int.from_bytes(e['raw'][at:at+width],'little')^mask)
    relasec = next(s for s in e['sections'] if s['name'] == '.rela'+SECTION)
    mutate('RELA_wrong_owner',relasec['record']+28,'<I',0)
    mutate('RELA_implicit_addend',relasec['record']+4,'<I',9)
    reject('unreported_trailing_bytes',lambda:join(base.elf(e['raw']+b'\0\0'),left,right,root))
    code = e['raw'][section['offset']:section['offset']+1162]
    relations = sorted((r['offset'],r['type'],r['target'],r['addend']) for r in e['relocations'])
    for name,offset,mask,width in [('typed_provider_JAL_link',888,128,4),('typed_provider_branch_source',956,8<<15,4),('typed_provider_CJ_family',1138,1<<13,2),('typed_provider_A6_load',1146,128,4),('typed_original_payload_read',1056,1<<20,4),('typed_original_predicate_byte',908,4,2)]:
        bad = bytearray(code)
        bad[offset:offset+width] = (int.from_bytes(bad[offset:offset+width],'little')^mask).to_bytes(width,'little')
        reject(name,lambda bad=bad:original_gate(root,bytes(bad),relations))
    bad = [(*r[:2],UND[0],r[3]) if r[0] == 888 else r for r in relations]
    reject('typed_actual_binding_destination',lambda:original_gate(root,code,bad))
    return rejected

def inspect(root,llvm,folder):
    need(root/MODEL == HERE and folder.is_relative_to(HERE/'build') and folder.name in ('c','cpp'), 'Actual owned portable mode folder')
    before = inputs(root,llvm)
    value = load(folder/'link-receipt.json')
    need(value['schema'] == BUILD_SCHEMA and value['mode'] == folder.name and value['inputs'] == before, 'Current fixed actual link receipt')
    left,right = (restored(value[k],root,llvm) for k in ('dispatch_folder','peripheral_folder'))
    proofs = upstream(root,llvm,left,right,value['mode'])
    expected = [dict(label=n,argv=portable([str(x) for x in args],root,llvm),exit=0,log_sha256=sha(folder/(n+'.log'))) for n,args in recipes(llvm,folder,left,right)]
    need(value['commands'] == expected, 'Exact two actual command recipes/exits/log hashes')
    files = ['dispatch.o','link.log','dispatch.log']
    need(value['artifacts'] == {n:sha(folder/n) for n in sorted(files)}, 'Complete actual artifacts/logs')
    need({p.name for p in folder.iterdir()}-{'verification.json'} == set(files)|{'link-receipt.json'}, 'Exact fresh output inventory')
    need(all(p.is_file() and not p.is_symlink() for p in folder.iterdir()) and (folder/'link.log').read_bytes() == b'', 'Ordinary files and empty successful linker diagnostics')
    base = reader(root)
    left_e,right_e,new_e = [base.elf(p.read_bytes()) for p in (left/'dispatch.o',right/'native.o',folder/'dispatch.o')]
    result,rows = join(new_e,left_e,right_e,root)
    readback = base.llvm_rows((folder/'dispatch.log').read_text(),rows)
    controls = negatives(new_e,left_e,right_e,root)
    need(before == inputs(root,llvm), 'Every source/tool/resource stable through review')
    result = dict(schema=SCHEMA,passed=True,mode=value['mode'],inputs=before,upstream=proofs,result=result,
                  actual_commands=value['commands'],artifacts={p.name:sha(p) for p in sorted(folder.iterdir()) if p.name != 'verification.json'},
                  full_LLVM_instruction_rows=readback,negative_controls=controls,new_compilation=False,
                  target_executed=False,ISA_emulated=False,HOST_execution=False,network=False,BIN_generated=False,
                  firmware_ready=False,installed_ROM_proved=False,physical_placement_proved=False)
    return json.loads(json.dumps(result))


def replay(root,llvm,receipt):
    value = inspect(root,llvm,receipt.parent)
    need(receipt.read_bytes() == encoded(value), 'Complete canonical read-only replay equals actual proof')
    return value


def metadata(root):
    previous(root)
    value = load(HERE/'seal.json')
    need(value['schema'] == 'TSL9-peripheral-dispatch-source-seal-v1' and value['files'] == {n:sha(HERE/n) for n in OWN}, 'Final authored source seal')
    need((HERE/'README.md').read_bytes() == (HERE/'readme.zh-TW.md').read_bytes(), 'Default TW byte identity')
    for name in OWN:
        b = (HERE/name).read_bytes()
        need(b'\r' not in b and b.endswith(b'\n') and not b.endswith(b'\n\n') and all(x.rstrip(b' \t') == x for x in b.splitlines()), 'LF/single EOF/whitespace '+name)
    return dict(passed=True,metadata_only=True,seal_sha256=sha(HERE/'seal.json'),firmware_ready=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,default=HERE.parents[1])
    p.add_argument('--llvm-bin',type=Path)
    g = p.add_mutually_exclusive_group()
    g.add_argument('--folder',type=Path)
    g.add_argument('--replay',type=Path)
    p.add_argument('--receipt',type=Path)
    p.add_argument('--require-firmware-ready',action='store_true')
    a = p.parse_args()
    root = a.project_root.resolve()
    need(root/MODEL == HERE, 'Exact portable experiment root')
    if a.folder or a.replay:
        need(a.llvm_bin is not None, 'Existing LLVM path required')
        llvm = a.llvm_bin.resolve()
        if a.replay:
            need(a.receipt is None, 'Replay is read-only')
            value = replay(root,llvm,a.replay.resolve())
        else:
            need(a.receipt is not None and a.receipt.resolve().parent == a.folder.resolve(), 'Create-only review receipt in owned folder')
            value = inspect(root,llvm,a.folder.resolve())
            write_new(a.receipt.resolve(),value)
    else:
        need(a.receipt is None, 'Receipt requires actual mode')
        value = metadata(root)
    result = value.get('result',{})
    print(json.dumps(dict(passed=True,mode=value.get('mode'),metadata_only=value.get('metadata_only',False),
                          bytes=result.get('bytes'),instructions=result.get('instructions'),FUNCs=result.get('FUNCs'),
                          pending_RELA=result.get('pending_RELA'),strong_UND=len(result.get('strong_UND',[])),
                          controls=len(value.get('negative_controls',[])),new_compilation=False,firmware_ready=False)))
    if a.require_firmware_ready:
        print('REJECTED: five providers, pending machine controls, resident identity/ABI and physical gates remain open.',file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration,struct.error) as error:
        print('FAIL: '+str(error),file=sys.stderr)
        sys.exit(1)
