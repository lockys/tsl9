#!/usr/bin/env python3
"""Bounded actual ELF/operand join; no compilation, target or ISA execution."""
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
MODEL = 'experiments/tsl9-transport-dispatch-component'
SCHEMA = 'TSL9-transport-dispatch-component-v1'
BUILD_SCHEMA = 'TSL9-transport-dispatch-link-v1'
FIRMWARE = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FW_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
TOOLS = {'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
STDINT_SHA = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
T = ['tsl9_filter_external_8a56']+['tsl9_transport_'+s for s in ('frame_8a5e','first_8a7a','first_result_8a90',
     'second_8a96','second_result_8ab6','reject_8abe','select0_8acc','pack_8ace','test_8b0a','finish_8b14','copy_8b52','bare_return_8b6c')]
TOFF = [0,8,36,58,64,96,104,118,120,180,190,252,278]
TSIZES = [8,28,22,6,32,8,14,2,60,10,62,26,2]
UND = sorted('tsl9_queue_external_'+s for s in ('9454','9b36','12abe','12a08','14d2e'))
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
    if isinstance(value,(tuple,list)):
        return [portable(x,root,llvm) for x in value]
    if isinstance(value,dict):
        return {portable(k,root,llvm):portable(v,root,llvm) for k,v in value.items()}
    return value


def restored(text,root,llvm):
    return Path(text.replace('${TSL9_ROOT}',str(root)).replace('${LLVM_BIN}',str(llvm))).resolve()


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()


def write_new(path,value):
    with path.open('xb') as stream:
        stream.write(encoded(value))


def dependencies(root):
    value = load(HERE/'dependencies.json')
    need(value['schema'] == 'TSL9-transport-dispatch-dependencies-v1', 'Final dependency schema')
    need(all(sha(root/p) == pin for p,pin in value['pins'].items()), 'Every frozen source dependency hash')
    return value


def old_reader(root):
    spec = dependencies(root)
    return module(root/spec['dispatch_checker'],'transport_dispatch_previous_reader')


def inputs(root,llvm):
    spec = dependencies(root)
    need(sha(root/FIRMWARE) == FW_SHA and (root/FIRMWARE).stat().st_size == 76800, 'Full official V4.1.60 identity')
    need(all(sha(llvm/n) == pin for n,pin in TOOLS.items()), 'Existing LLVM tools including upstream compiler identities')
    stdint = llvm.parent/'lib/clang/18/include/stdint.h'
    need(sha(stdint) == STDINT_SHA, 'Actual transitive compiler resource')
    paths = [HERE/p for p in OWN]+[root/p for p in spec['pins']]+[root/FIRMWARE,stdint]+[llvm/n for n in TOOLS]
    return {portable(str(p),root,llvm):sha(p) for p in sorted(set(paths))}


def upstream(root,llvm,left,right,mode):
    spec = dependencies(root)
    need(left.name == right.name == mode and left.is_relative_to(root/'experiments') and right.is_relative_to(root/'experiments'), 'Actual language-matched input folders')
    actual = old_reader(root).replay(root,llvm,left/'verification.json')
    need(actual['schema'] == 'TSL9-queue-dispatch-component-v1' and actual['passed'] and actual['result']['bytes'] == 526, 'Genuine formal dispatch proof')
    new = module(root/spec['transport_checker'],'transport_dispatch_provider')
    fresh,text = new.evaluate(root,llvm,right,mode)
    need(load(right/'verification.json') == fresh and (right/'verification.json').read_bytes() == text.encode(), 'Actual formal transport proof freshly replayed')
    return dict(dispatch=dict(receipt=portable(str(left/'verification.json'),root,llvm),sha256=sha(left/'verification.json'),
                              object_sha256=sha(left/'dispatch.o'),inputs=actual['inputs'],whole_actual_proof_replayed=True),
                transport=dict(receipt=portable(str(right/'verification.json'),root,llvm),sha256=sha(right/'verification.json'),
                               object_sha256=sha(right/'native.o'),inputs=fresh['inputs'],whole_actual_proof_replayed=True))


def recipes(llvm,folder,left,right):
    return [('link',[llvm/'ld.lld.exe','-r','--no-relax','-T',HERE/'component.ld',left/'dispatch.o',right/'native.o','-o',folder/'dispatch.o']),
            ('dispatch',[llvm/'llvm-objdump.exe','--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',folder/'dispatch.o'])]


def body(e,function):
    s = e['sections'][function['section']]
    need(function['value'] >= 0 and function['value']+function['size'] <= s['size'], 'Complete genuine function storage')
    at = s['offset']+function['value']
    return e['raw'][at:at+function['size']]


def original_gate(root,code,relations):
    reader = old_reader(root)
    fw = (root/FIRMWARE).read_bytes()
    need(digest(fw) == FW_SHA and len(fw) == 76800, 'Fresh original full firmware')
    spans = [(0,314,0x12c58),(314,188,0x82d2),(502,6,0x81aa),(508,18,0x820c),(526,280,0x8a56)]
    original = b''.join(fw[va-0x8000:va-0x8000+size] for _,size,va in spans)
    masks = bytearray(b'\xff'*806)
    typed = []
    for off,kind,target,addend in relations:
        need(kind in MASKS and addend == 0, 'Original control families/zero addends')
        width,mask = MASKS[kind]
        need(0 <= off <= 806-width and all(m == 255 for m in masks[off:off+width]), 'Complete non-overlapping control extents')
        masks[off:off+width] = mask.to_bytes(width,'little')
        span = next((at,size,va) for at,size,va in spans if at <= off and off+width <= at+size)
        pc = span[2]+off-span[0]
        a,b = reader.control(original,off,kind,pc),reader.control(code,off,kind,pc)
        need({k:v for k,v in a.items() if k != 'target'} == {k:v for k,v in b.items() if k != 'target'}, 'Actual control RD/RS/family matches original')
        need(a['target'] == int(target.rsplit('_',1)[1],16), 'Actual symbolic identity equals original immediate target')
        typed.append(dict(offset=off,original_PC=pc,original_operand=a,target_symbol=target,pending_raw_target=b['target'],machine_operand_resolved=False))
    need(len(code) == len(original) == 806 and all(not((a^b)&m) for a,b,m in zip(code,original,masks)), 'Every original non-control bit retained')
    return dict(firmware_sha256=FW_SHA,spans=[dict(offset=a,bytes=z,original_VA=v) for a,z,v in spans],
                original_masked_sha256=digest(bytes(v&m for v,m in zip(original,masks))),typed_controls=typed,all_noncontrol_bits_equal=True)


def join(e,left,right,root):
    reader = old_reader(root)
    names,offsets,sizes = reader.NAMES+T,reader.OFFSETS+[526+x for x in TOFF],reader.SIZES+TSIZES
    functions = [s for s in e['symbols'] if s['info']&15 == 2]
    need(len(functions) == 32 and {s['name'] for s in functions} == set(names), 'All32 genuine FUNCs including cold/unused regions')
    globals_ = [s for s in e['symbols'] if s['info']>>4]
    need(all(s['info']>>4 == 1 and s['other'] == 0 and s['section'] != 0xfff1 for s in globals_), 'Strong visible definitions/references; no global ABS')
    und = sorted(s['name'] for s in globals_ if s['section'] == 0)
    need(und == UND and all(s['value'] == s['size'] == 0 and s['info'] == 16 for s in globals_ if s['section'] == 0), 'Exactly five zero-value genuine strong UND')
    need({s['name'] for s in globals_} == set(names)|set(UND), 'No additional global objects/providers')
    sections = {s['name']:s for s in e['sections']}
    need(set(sections) == {'','.transport_dispatch','.text','.rela.transport_dispatch','.llvm_addrsig','.symtab','.shstrtab','.strtab'}, 'Complete actual section inventory')
    alloc = [s for s in e['sections'] if s['flags']&2 and s['size']]
    need([(s['name'],s['type'],s['flags'],s['address'],s['size'],s['align']) for s in alloc] == [('.transport_dispatch',1,6,0,806,2)], 'Only806B AX code; no hidden allocation')
    sec = sections['.transport_dispatch']
    need((sections['.text']['size'],sections['.text']['flags'],sections['.text']['type']) == (0,6,1), 'Inherited text is empty')
    addr = sections['.llvm_addrsig']
    total = sum(s['size'] for prior in (left,right) for s in prior['sections'] if s['name'] == '.llvm_addrsig')
    need((addr['type'],addr['flags'],addr['size']) == (0x6fff4c03,0x80000000,total), 'Address-significance metadata derives from actual inputs')
    expected_codes,relations = {},[]
    for prior,group,bases in [(left,reader.NAMES,dict(zip(reader.NAMES,reader.OFFSETS))),(right,T,dict(zip(T,[526+x for x in TOFF])))]:
        starts = {}
        for s in prior['symbols']:
            if s['name'] in group and s['info']&15 == 2:
                expected_codes[s['name']] = body(prior,s)
                base = bases[s['name']]-s['value']
                need(s['section'] not in starts or starts[s['section']] == base, 'Consistent section mapping into new output')
                starts[s['section']] = base
        for r in prior['relocations']:
            need(r['section'] in starts, 'Only genuine input code relocation ownership')
            relations.append((starts[r['section']]+r['offset'],r['type'],r['target'],r['addend']))
    actual,facts = {},[]
    for name,offset,size in zip(names,offsets,sizes):
        f = next(s for s in functions if s['name'] == name)
        need((f['info'],f['other'],f['section'],f['value'],f['size']) == (18,0,sec['index'],offset,size), 'Exact genuine FUNC storage '+name)
        actual[name] = body(e,f)
        facts.append(dict(name=name,offset=offset,bytes=size,sha256=digest(actual[name])))
    need(actual == expected_codes, 'All actual input bodies preserved byte for byte')
    rels = sorted((r['offset'],r['type'],r['target'],r['addend']) for r in e['relocations'])
    need(len(rels) == 41 and rels == sorted(relations), 'All41 actual pending RELA offsets/families/symbols/addends preserved')
    need(all(r['section'] == sec['index'] for r in e['relocations']), 'Every output relocation belongs to actual code')
    provider = next(s for s in functions if s['name'] == T[0])
    sites = [r['offset'] for r in e['relocations'] if r['target'] == T[0]]
    need(provider['value'] == 526 and sites == [464], 'Original C.JAL now binds genuine transport FUNC at526')
    code = b''.join(actual[n] for n in names)
    need(code == e['raw'][sec['offset']:sec['offset']+806], 'No holes or unowned bytes')
    rows = reader.count_instructions(code)
    need(len(rows) == 280, 'Complete806B contains280 instructions')
    original = original_gate(root,code,rels)
    return dict(bytes=806,instructions=280,FUNCs=32,private_architectural_regions=30,ordinary_small_C_functions=2,
                functions=facts,code_sha256=digest(code),pending_RELA=41,strong_UND=und,global_ABS=[],
                symbol_binding=dict(symbol=T[0],definition_offset=526,reference_offsets=sites,genuine_FUNC=True,
                                    resolved_at_symbol_level=True,machine_control_resolved=False),
                relocations=[dict(offset=o,type=k,target=t,addend=a) for o,k,t,a in rels],original=original,VMA=0,
                all_machine_controls_resolved=False,ordinary_C_ABI_proved=False,original_placement_proved=False),rows


def negatives(e,left,right,root):
    reader = old_reader(root)
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
        reject(name,lambda:join(reader.elf(bytes(raw)),left,right,root))
    sec = next(s for s in e['sections'] if s['name'] == '.transport_dispatch')
    symbols = {s['name']:s for s in e['symbols'] if s['name']}
    provider = symbols[T[0]]
    mutate('writable_code',sec['record']+8,'<I',7)
    mutate('fake_ABS_transport',provider['record']+14,'<H',0xfff1)
    mutate('weak_transport',provider['record']+12,'<B',34)
    mutate('wrong_transport_position',provider['record']+4,'<I',524)
    mutate('lost_transport_bytes',symbols[T[8]]['record']+8,'<I',58)
    mutate('nonzero_remaining_UND',symbols[UND[0]]['record']+4,'<I',2)
    call = next(r for r in e['relocations'] if r['target'] == T[0])
    mutate('wrong_provider_binding',call['record']+4,'<I',(symbols[UND[0]]['index']<<8)|call['type'])
    mutate('wrong_RELA_family',call['record']+4,'<I',(call['symbol']<<8)|44)
    mutate('wrong_RELA_offset',call['record'],'<I',call['offset']+2)
    mutate('nonzero_RELA_addend',call['record']+8,'<i',2)
    at = sec['offset']+call['offset']
    mutate('C_JAL_to_tail_C_J',at,'<H',int.from_bytes(e['raw'][at:at+2],'little')^0x8000)
    for name,off,mask,width in [('transport_guard',526,1<<20,4),('frame32',534,4,2),('status_GP175',502,8<<20,4)]:
        at = sec['offset']+off
        mutate(name,at,'<I' if width == 4 else '<H',int.from_bytes(e['raw'][at:at+width],'little')^mask)
    reject('trailing_bytes',lambda:join(reader.elf(e['raw']+b'\0\0'),left,right,root))
    code = e['raw'][sec['offset']:sec['offset']+806]
    relations = sorted((r['offset'],r['type'],r['target'],r['addend']) for r in e['relocations'])
    for name,off,mask,width in [('typed_CJAL_link',call['offset'],0x8000,2),('typed_guard_rs1',530,1<<15,4),('typed_GP167',502,8<<20,4)]:
        bad = bytearray(code)
        bad[off:off+width] = (int.from_bytes(bad[off:off+width],'little')^mask).to_bytes(width,'little')
        reject(name,lambda bad=bad:original_gate(root,bytes(bad),relations))
    return rejected


def inspect(root,llvm,folder):
    need(root/MODEL == HERE and folder.is_relative_to(HERE/'build') and folder.name in ('c','cpp'), 'Owned portable mode folder')
    before = inputs(root,llvm)
    record = load(folder/'link-receipt.json')
    need(record['schema'] == BUILD_SCHEMA and record['mode'] == folder.name and record['inputs'] == before, 'Current frozen actual link receipt')
    left,right = (restored(record[k],root,llvm) for k in ('dispatch_folder','transport_folder'))
    proofs = upstream(root,llvm,left,right,record['mode'])
    commands = recipes(llvm,folder,left,right)
    expected = [dict(label=n,argv=portable([str(x) for x in argv],root,llvm),exit=0,log_sha256=sha(folder/(n+'.log'))) for n,argv in commands]
    need(record['commands'] == expected, 'Exact two actual command recipes/exits/log hashes')
    files = ['dispatch.o','link.log','dispatch.log']
    need(record['artifacts'] == {n:sha(folder/n) for n in sorted(files)}, 'Complete actual artifact hashes')
    need({p.name for p in folder.iterdir()}-{'verification.json'} == set(files)|{'link-receipt.json'}, 'Exact fresh output inventory')
    need(all(p.is_file() and not p.is_symlink() for p in folder.iterdir()), 'Ordinary actual output files only')
    need((folder/'link.log').read_bytes() == b'', 'Empty successful linker diagnostics')
    reader = old_reader(root)
    left_e,right_e,new_e = [reader.elf(p.read_bytes()) for p in (left/'dispatch.o',right/'native.o',folder/'dispatch.o')]
    result,rows = join(new_e,left_e,right_e,root)
    readback = reader.llvm_rows((folder/'dispatch.log').read_text(),rows)
    controls = negatives(new_e,left_e,right_e,root)
    need(before == inputs(root,llvm), 'All source/tool/resource inputs stable through actual review')
    result = dict(schema=SCHEMA,passed=True,mode=record['mode'],inputs=before,upstream=proofs,result=result,
                  actual_commands=record['commands'],artifacts={p.name:sha(p) for p in sorted(folder.iterdir()) if p.name != 'verification.json'},
                  negative_controls=controls,full_LLVM_instruction_rows=readback,new_compilation=False,
                  target_executed=False,ISA_emulated=False,HOST_execution=False,network=False,BIN_generated=False,
                  firmware_ready=False,installed_ROM_proved=False,physical_placement_proved=False)
    return json.loads(json.dumps(result))


def replay(root,llvm,receipt):
    result = inspect(root,llvm,receipt.parent)
    need(receipt.read_bytes() == encoded(result), 'Complete canonical read-only replay equals actual proof')
    return result


def metadata(root):
    dependencies(root)
    seal = load(HERE/'seal.json')
    need(seal['schema'] == 'TSL9-transport-dispatch-source-seal-v1' and seal['files'] == {p:sha(HERE/p) for p in OWN}, 'Final authored source seal')
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
            result = replay(root,llvm,a.replay.resolve())
        else:
            need(a.receipt is not None and a.receipt.resolve().parent == a.folder.resolve(), 'Create-only actual receipt in owned folder')
            result = inspect(root,llvm,a.folder.resolve())
            write_new(a.receipt.resolve(),result)
    else:
        need(a.receipt is None, 'Receipt requires actual mode')
        result = metadata(root)
    info = result.get('result',{})
    print(json.dumps(dict(passed=True,mode=result.get('mode'),metadata_only=result.get('metadata_only',False),
                          bytes=info.get('bytes'),instructions=info.get('instructions'),FUNCs=info.get('FUNCs'),
                          pending_RELA=info.get('pending_RELA'),strong_UND=len(info.get('strong_UND',[])),
                          controls=len(result.get('negative_controls',[])),new_compilation=False,firmware_ready=False)))
    if a.require_firmware_ready:
        print('REJECTED: five external providers, pending machine operands, resident identity and physical gates remain open.',file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration,struct.error) as error:
        print('FAIL: '+str(error),file=sys.stderr)
        sys.exit(1)
