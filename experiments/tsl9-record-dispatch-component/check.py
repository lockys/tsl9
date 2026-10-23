#!/usr/bin/env python3
"""Actual record-dispatch composition: bounded ELF, raw operands and source closure."""
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
MODEL = 'experiments/tsl9-record-dispatch-component'
SCHEMA = 'TSL9-record-dispatch-component-v1'
BUILD_SCHEMA = 'TSL9-record-dispatch-link-v1'
R = ['tsl9_queue_external_12a08']+['tsl9_dispatch_'+s for s in ('status_12a14','ID_12a16','query_12a20','tag_12a28',
     'copy_12a2e','peripheral_12a50','finish_12a5e','tagged_12a66')]
ROFF = [0,12,14,24,32,38,72,86,94]
RSIZES = [12,2,10,8,6,34,14,8,8]
STATUS = 'tsl9_queue_external_81aa'
PREDICATE = 'tsl9_dispatch_external_821e'
UND = sorted(['tsl9_queue_external_'+s for s in ('9454','9b36','12abe','14d2e')]+
             ['tsl9_dispatch_external_'+s for s in ('18ca4','16b7c')])
SECTION = '.record_dispatch_component'
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
        return value.replace(str(root).replace('\\','/'),'${TSL9_ROOT}').replace(str(root),'${TSL9_ROOT}').replace(str(llvm).replace('\\','/'),'${LLVM_BIN}').replace(str(llvm),'${LLVM_BIN}')
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
    need(value['schema'] == 'TSL9-record-dispatch-dependencies-v1' and all(sha(root/p) == h for p,h in value['pins'].items()), 'Pinned direct dependencies')
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
    result = previous(root).inputs(root,llvm)
    paths = [HERE/p for p in OWN]+[root/p for p in direct['pins']]
    for path in paths:
        key = portable(str(path),root,llvm)
        value = sha(path)
        need(key not in result or result[key] == value, 'Consistent transitive input identity')
        result[key] = value
    return dict(sorted(result.items()))


def upstream(root,llvm,left,right,predicate,mode):
    direct = dependencies(root)
    need(left.name == right.name == predicate.name == mode and all(p.is_relative_to(root/'experiments') for p in (left,right,predicate)), 'Actual language-matched owned folders')
    old = previous(root).replay(root,llvm,left/'verification.json')
    need(old['schema'] == 'TSL9-transport-dispatch-component-v1' and old['passed'] and old['result']['bytes'] == 806, 'Actual formal806B previous composition')
    new = module(root/direct['record_checker'],'record_formal_native')
    fresh,text = new.evaluate(root,llvm,right,mode)
    need(load(right/'verification.json') == fresh and (right/'verification.json').read_bytes() == text.encode(), 'Fresh actual formal record proof replay')
    predicate_checker = module(root/direct['predicate_checker'],'record_predicate_formal')
    predicate_facts,predicate_text = predicate_checker.evaluate(root,llvm,predicate,mode)
    need(load(predicate/'verification.json') == predicate_facts and (predicate/'verification.json').read_bytes() == predicate_text.encode(), 'Fresh actual formal predicate proof replay')
    return dict(dispatch=dict(receipt=portable(str(left/'verification.json'),root,llvm),sha256=sha(left/'verification.json'),
                              object_sha256=sha(left/'dispatch.o'),inputs=old['inputs'],whole_actual_proof_replayed=True),
                record=dict(receipt=portable(str(right/'verification.json'),root,llvm),sha256=sha(right/'verification.json'),
                            object_sha256=sha(right/'native.o'),inputs=fresh['inputs'],whole_actual_proof_replayed=True),
                predicate=dict(receipt=portable(str(predicate/'verification.json'),root,llvm),sha256=sha(predicate/'verification.json'),
                               object_sha256=sha(predicate/'native.o'),inputs=predicate_facts['inputs'],whole_actual_proof_replayed=True))


def recipes(llvm,folder,left,right,predicate):
    return [('link',[llvm/'ld.lld.exe','-r','--no-relax','-T',HERE/'component.ld',left/'dispatch.o',right/'native.o',predicate/'native.o','-o',folder/'dispatch.o']),
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
    spans = [(0,314,0x12c58),(314,188,0x82d2),(502,6,0x81aa),(508,18,0x820c),(526,280,0x8a56),(806,102,0x12a08),(908,42,0x821e)]
    original = b''.join(fw[v-0x8000:v-0x8000+z] for _,z,v in spans)
    masks = bytearray(b'\xff'*950)
    typed = []
    for offset,kind,target,addend in relations:
        need(kind in MASKS and addend == 0, 'Only genuine original control families/zero addends')
        width,mask = MASKS[kind]
        need(0 <= offset <= 950-width and all(x == 255 for x in masks[offset:offset+width]), 'Complete non-overlapping control extent')
        masks[offset:offset+width] = mask.to_bytes(width,'little')
        at,size,va = next((a,z,v) for a,z,v in spans if a <= offset and offset+width <= a+z)
        pc = va+offset-at
        a,b = base.control(original,offset,kind,pc),base.control(code,offset,kind,pc)
        need({k:v for k,v in a.items() if k != 'target'} == {k:v for k,v in b.items() if k != 'target'}, 'Original control RD/RS/family/RA link retained')
        need(a['target'] == int(target.rsplit('_',1)[1],16), 'Symbol identity equals fresh original decoded destination')
        typed.append(dict(offset=offset,original_PC=pc,original_operand=a,target_symbol=target,pending_raw_target=b['target'],machine_operand_resolved=False))
    need(len(code) == len(original) == 950 and all(not((a^b)&m) for a,b,m in zip(code,original,masks)), 'Every fresh original non-control bit retained')
    return dict(firmware_sha256=base.FW_SHA,spans=[dict(offset=a,bytes=z,original_VA=v) for a,z,v in spans],
                original_masked_sha256=digest(bytes(v&m for v,m in zip(original,masks))),typed_controls=typed,all_noncontrol_bits_equal=True)


def join(e,left,right,predicate,root):
    prior,base = previous(root),reader(root)
    old_names,old_offsets,old_sizes = base.NAMES+prior.T,base.OFFSETS+[526+x for x in prior.TOFF],base.SIZES+prior.TSIZES
    names,offsets,sizes = old_names+R+[PREDICATE],old_offsets+[806+x for x in ROFF]+[908],old_sizes+RSIZES+[42]
    functions = [s for s in e['symbols'] if s['info']&15 == 2]
    need(len(functions) == 42 and {s['name'] for s in functions} == set(names), 'All42 genuine FUNCs including cold/unused regions')
    globals_ = [s for s in e['symbols'] if s['info']>>4]
    need(all(s['info']>>4 == 1 and s['other'] == 0 and s['section'] != 0xfff1 for s in globals_), 'Strong visible definitions/references with zero global ABS')
    und = sorted(s['name'] for s in globals_ if s['section'] == 0)
    need(und == UND and all(s['value'] == s['size'] == 0 and s['info'] == 16 for s in globals_ if s['section'] == 0), 'Exactly six genuine zero-value strong UND')
    need({s['name'] for s in globals_} == set(names)|set(UND), 'No additional global objects/providers')
    sections = {s['name']:s for s in e['sections']}
    need(set(sections) == {'',SECTION,'.text','.rela'+SECTION,'.llvm_addrsig','.symtab','.shstrtab','.strtab'}, 'Complete actual section inventory')
    alloc = [s for s in e['sections'] if s['flags']&2 and s['size']]
    need([(s['name'],s['type'],s['flags'],s['address'],s['size'],s['align']) for s in alloc] == [(SECTION,1,6,0,950,2)], 'Only950B AX allocation, no hidden code/data')
    section = sections[SECTION]
    need((sections['.text']['size'],sections['.text']['flags'],sections['.text']['type']) == (0,6,1), 'Inherited text is empty')
    addrsig = sections['.llvm_addrsig']
    size = sum(s['size'] for before in (left,right,predicate) for s in before['sections'] if s['name'] == '.llvm_addrsig')
    need((addrsig['type'],addrsig['flags'],addrsig['size']) == (0x6fff4c03,0x80000000,size), 'Actual input-derived nonallocated address-significance metadata')
    expected,relations = {},[]
    for before,group,bases in [(left,old_names,dict(zip(old_names,old_offsets))),(right,R,dict(zip(R,[806+x for x in ROFF]))),(predicate,[PREDICATE],{PREDICATE:908})]:
        starts = {}
        for f in before['symbols']:
            if f['name'] in group and f['info']&15 == 2:
                expected[f['name']] = body(before,f)
                start = bases[f['name']]-f['value']
                need(f['section'] not in starts or starts[f['section']] == start, 'Consistent input section mapping')
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
    need(actual == expected, 'Every actual input function body preserved byte for byte')
    rels = sorted((r['offset'],r['type'],r['target'],r['addend']) for r in e['relocations'])
    need(len(rels) == 50 and rels == sorted(relations), 'All50 pending RELA offsets/families/symbols/addends preserved')
    need(all(r['section'] == section['index'] for r in e['relocations']), 'All pending controls belong to actual code')
    bindings = []
    for name,offset,sites in [(R[0],806,[282]),(STATUS,502,[300,814]),(PREDICATE,908,[832])]:
        f = next(s for s in functions if s['name'] == name)
        seen = [r['offset'] for r in e['relocations'] if r['target'] == name]
        need(f['value'] == offset and seen == sites, 'Genuine source/provider symbol binding '+name)
        bindings.append(dict(symbol=name,definition_offset=offset,reference_offsets=seen,genuine_FUNC=True,
                             resolved_at_symbol_level=True,machine_control_resolved=False))
    code = b''.join(actual[n] for n in names)
    need(code == e['raw'][section['offset']:section['offset']+950], 'No holes or unowned bytes')
    rows = base.count_instructions(code)
    need(len(rows) == 330, 'Full950B stream contains330 instructions')
    return dict(bytes=950,instructions=330,FUNCs=42,private_architectural_regions=39,ordinary_small_C_functions=3,
                functions=facts,code_sha256=digest(code),pending_RELA=50,strong_UND=und,global_ABS=[],
                symbol_bindings=bindings,relocations=[dict(offset=o,type=k,target=t,addend=a) for o,k,t,a in rels],
                original=original_gate(root,code,rels),VMA=0,all_machine_controls_resolved=False,
                ordinary_C_ABI_proved=False,original_placement_proved=False),rows


def negatives(e,left,right,predicate,root):
    base = reader(root)
    rejected = []
    def reject(name,action):
        try:
            action()
        except (ValueError,IndexError,KeyError,StopIteration,struct.error):
            rejected.append(name)
        else:
            raise ValueError('Accepted actual in-memory regression '+name)
    def mutate(name,at,fmt,value):
        raw = bytearray(e['raw'])
        struct.pack_into(fmt,raw,at,value)
        reject(name,lambda:join(base.elf(bytes(raw)),left,right,predicate,root))
    section = next(s for s in e['sections'] if s['name'] == SECTION)
    symbols = {s['name']:s for s in e['symbols'] if s['name']}
    f = symbols[R[0]]
    mutate('writable_code',section['record']+8,'<I',7)
    mutate('fake_ABS_record_provider',f['record']+14,'<H',0xfff1)
    mutate('weak_record_provider',f['record']+12,'<B',34)
    mutate('wrong_record_position',f['record']+4,'<I',804)
    mutate('lost_record_copy_bytes',symbols[R[5]]['record']+8,'<I',32)
    mutate('fake_ABS_predicate',symbols[PREDICATE]['record']+14,'<H',0xfff1)
    mutate('wrong_predicate_position',symbols[PREDICATE]['record']+4,'<I',906)
    mutate('lost_predicate_bytes',symbols[PREDICATE]['record']+8,'<I',40)
    mutate('nonzero_remaining_UND',symbols[UND[0]]['record']+4,'<I',2)
    for name in (R[0],STATUS,PREDICATE):
        call = next(r for r in e['relocations'] if r['target'] == name and (name != STATUS or r['offset'] >= 806))
        mutate('wrong_binding_'+name,call['record']+4,'<I',(symbols[UND[0]]['index']<<8)|call['type'])
    call = next(r for r in e['relocations'] if r['target'] == R[0])
    mutate('wrong_RELA_family',call['record']+4,'<I',(call['symbol']<<8)|16)
    mutate('wrong_RELA_offset',call['record'],'<I',call['offset']+2)
    mutate('nonzero_RELA_addend',call['record']+8,'<i',2)
    at = section['offset']+call['offset']
    mutate('record_call_without_RA',at,'<I',int.from_bytes(e['raw'][at:at+4],'little')&~0xf80)
    for name,offset,mask,width in [('record_frame',806,4,2),('record_copy_byte',844,4,2),('retained_GP175',502,8<<20,4)]:
        at = section['offset']+offset
        mutate(name,at,'<I' if width == 4 else '<H',int.from_bytes(e['raw'][at:at+width],'little')^mask)
    reject('unreported_trailing_bytes',lambda:join(base.elf(e['raw']+b'\0\0'),left,right,predicate,root))
    code = e['raw'][section['offset']:section['offset']+950]
    relations = sorted((r['offset'],r['type'],r['target'],r['addend']) for r in e['relocations'])
    for name,offset,mask,width in [('typed_record_JAL_link',282,128,4),('typed_status_JAL_link',814,128,4),('typed_predicate_JAL_link',832,128,4),('typed_GP167',502,8<<20,4),('full_original_predicate_byte',908,4,2)]:
        bad = bytearray(code)
        bad[offset:offset+width] = (int.from_bytes(bad[offset:offset+width],'little')^mask).to_bytes(width,'little')
        reject(name,lambda bad=bad:original_gate(root,bytes(bad),relations))
    return rejected


def inspect(root,llvm,folder):
    need(root/MODEL == HERE and folder.is_relative_to(HERE/'build') and folder.name in ('c','cpp'), 'Actual owned portable mode folder')
    before = inputs(root,llvm)
    value = load(folder/'link-receipt.json')
    need(value['schema'] == BUILD_SCHEMA and value['mode'] == folder.name and value['inputs'] == before, 'Current fixed actual link receipt')
    left,right,predicate = (restored(value[k],root,llvm) for k in ('dispatch_folder','record_folder','predicate_folder'))
    proofs = upstream(root,llvm,left,right,predicate,value['mode'])
    expected = [dict(label=n,argv=portable([str(x) for x in args],root,llvm),exit=0,log_sha256=sha(folder/(n+'.log'))) for n,args in recipes(llvm,folder,left,right,predicate)]
    need(value['commands'] == expected, 'Exact two actual command recipes/exits/log hashes')
    files = ['dispatch.o','link.log','dispatch.log']
    need(value['artifacts'] == {n:sha(folder/n) for n in sorted(files)}, 'Complete actual artifacts/logs')
    need({p.name for p in folder.iterdir()}-{'verification.json'} == set(files)|{'link-receipt.json'}, 'Exact fresh output inventory')
    need(all(p.is_file() and not p.is_symlink() for p in folder.iterdir()) and (folder/'link.log').read_bytes() == b'', 'Ordinary files and empty successful linker diagnostics')
    base = reader(root)
    left_e,right_e,predicate_e,new_e = [base.elf(p.read_bytes()) for p in (left/'dispatch.o',right/'native.o',predicate/'native.o',folder/'dispatch.o')]
    result,rows = join(new_e,left_e,right_e,predicate_e,root)
    readback = base.llvm_rows((folder/'dispatch.log').read_text(),rows)
    controls = negatives(new_e,left_e,right_e,predicate_e,root)
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
    need(value['schema'] == 'TSL9-record-dispatch-source-seal-v1' and value['files'] == {n:sha(HERE/n) for n in OWN}, 'Final authored source seal')
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
        print('REJECTED: six providers, pending machine controls, resident identity/ABI and physical gates remain open.',file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration,struct.error) as error:
        print('FAIL: '+str(error),file=sys.stderr)
        sys.exit(1)
