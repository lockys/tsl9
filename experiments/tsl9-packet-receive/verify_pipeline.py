#!/usr/bin/env python3
"""Build/replay the bounded 494B partial composition; never run target code."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LINKER = HERE/'pipeline.ld'
OBJECT = 'PIPELINE-PACKET-OPEN.o'
PIPELINE_PIN = '16903753d56341a39e9edab06f9d14b2a12f9b42459dbb3fd009ec2b670e64a1'
LINKER_PIN = '81dc4e8f241c96fd3fd7304fc08736e451ff4e4ca61365dcc4dcf486f2eed574'
VERIFIERS = {
 'experiments/tsl9-register-providers/verify.py': '41d165f4d942f6d5e1612a578b7c2faaad9fefebfa01f00305d2751f113f266d',
 'experiments/tsl9-spi-transfer-leaf/verify_pipeline.py': '3d8db99c78b514b516cb6b43bf0401eee4ab8957e312944a84c9d74b4acadf3a',
 'experiments/tsl9-packet-receive/verify.py': '00d3e8542e80f1f9339547b18acb14d62b41d5c80cad5dcae28fa6dca7faf854',
 'experiments/tsl9-spi-transfer-leaf/verify.py': '8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8',
 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py': '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141',
}
SPI_RECEIPTS = {'c': '19d6cbbf7df2dec121dc58cec73f9a647077f245ff908b1eafc03fe26fb0c2b9',
 'cpp': '7d7a3c3e7aeeb2c858fdbb528e56c69b4a5cace6e66469ff0a05ce0432fc8014'}
PACKET_RECEIPTS = {'c': 'f30f1374e4cfebee84ad2c8e582126908a6f64e7f40942fcd509c1c28cb1ca0e',
 'cpp': 'b9a56045f6408ab5060a92248355a70ef96f7f628325a898fd33982fe3071e80'}
RING = 'tsl9_ring_insert_entry_12bc8'
SECTION_ROWS = [
 ('',0,0,0,0,0,0,0,0,0),
 ('.pipeline',1,6,0,52,494,0,0,2,0),
 ('.text',1,6,0,546,0,0,0,2,0),
 ('.rela.pipeline',4,64,0,548,276,5,1,4,12),
 ('.llvm_addrsig',1879002115,2147483648,0,824,19,0,0,1,0),
 ('.symtab',2,0,0,844,880,7,35,4,16),
 ('.shstrtab',3,0,0,1724,72,0,0,1,0),
 ('.strtab',3,0,0,1796,755,0,0,1,0)]


def need(value, why):
    if not value:
        raise ValueError(why)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    return sha(Path(path).read_bytes())


def portable(value, llvm):
    if isinstance(value, str):
        for path, token in [(llvm, '${LLVM_BIN}'), (llvm.parent/'lib/clang/18/include', '${CLANG_INCLUDE}'),
                            (ROOT, '${TSL9_ROOT}')]:
            value = value.replace(str(path), token).replace(path.as_posix(), token)
        return value.replace('${PROJECT_ROOT}', '${TSL9_ROOT}').replace('\\', '/')
    if isinstance(value, dict):
        return {portable(str(k), llvm): portable(v, llvm) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [portable(v, llvm) for v in value]
    return value


def resolve(value, llvm):
    for token, path in [('${PROJECT_ROOT}', ROOT), ('${TSL9_ROOT}', ROOT), ('${LLVM_BIN}', llvm),
                        ('${CLANG_INCLUDE}', llvm.parent/'lib/clang/18/include')]:
        value = value.replace(token, str(path))
    need('${' not in value, 'known portable input root')
    return Path(value).resolve()


def inventory(directory):
    need(directory.is_dir() and not directory.is_symlink(), 'actual evidence directory')
    entries = sorted(directory.iterdir())
    need(all(p.is_file() and not p.is_symlink() for p in entries), 'flat evidence inventory, no links/extra directories')
    return {p.name: digest(p) for p in entries}


def snapshots(paths):
    return {p: digest(p) for p in sorted(set(paths))}


def providers(language, llvm):
    """Replay all three frozen checkers at their actual producer paths."""
    for name, pin in VERIFIERS.items():
        need(digest(ROOT/name) == pin, 'frozen dependency checker/reader '+name)
    need(digest(LINKER) == LINKER_PIN, 'frozen new linker')
    rp = runpy.run_path(str(ROOT/'experiments/tsl9-register-providers/verify.py'))
    sp = runpy.run_path(str(ROOT/'experiments/tsl9-spi-transfer-leaf/verify_pipeline.py'))
    pk = runpy.run_path(str(HERE/'verify.py'))
    reader = sp['reader']()
    old_dir = ROOT/'experiments/tsl9-spi-transfer-leaf/build/pipeline-v1'/language
    spi_dir = ROOT/'experiments/tsl9-spi-transfer-leaf/build/probe-v7-symbolic'/language
    register_dir = ROOT/'experiments/tsl9-register-providers/build/verified-v3'/language
    packet_dir = HERE/'build/verified-v2'/language
    spi_receipt = ROOT/'experiments/tsl9-spi-transfer-leaf/build/pipeline-verified-v1'/language/'verification.json'
    packet_receipt = packet_dir/'verification.json'
    need(digest(spi_receipt) == SPI_RECEIPTS[language] and digest(packet_receipt) == PACKET_RECEIPTS[language],
         'published/frozen provider receipt pins')
    tools, header, old_reader, rx, co = rp['load'](ROOT, llvm)
    register_record = rp['replay'](ROOT, register_dir/'verification.json', tools, header, old_reader, rx, co)
    spi_record = sp['verify'](language, register_dir, spi_dir, old_dir, reader)
    spi_encoded = (json.dumps(spi_record, indent=2, ensure_ascii=True)+'\n').encode()
    need(spi_receipt.read_bytes() == spi_encoded, 'entire SPI pipeline receipt replay equality')
    packet_record, packet_encoded = pk['evaluate'](ROOT, llvm, packet_dir, language)
    need(packet_receipt.read_bytes() == packet_encoded.encode(), 'entire packet receipt replay equality')
    expected_inputs = {ROOT/n:pin for n,pin in VERIFIERS.items()}
    expected_inputs.update({LINKER:LINKER_PIN, spi_receipt:SPI_RECEIPTS[language],
                           packet_receipt:PACKET_RECEIPTS[language],
                           register_dir/'verification.json':sp['OLD_RECEIPTS'][language]})
    for table in [register_record['inputs_before'], spi_record['inputs_before']]:
        for name, pin in table.items():
            path = resolve(name, llvm); need(digest(path) == pin, 'transitive source/tool/header pin'); expected_inputs[path]=pin
    for item in packet_record['inputs']:
        path = resolve(item['path'], llvm); need(digest(path) == item['sha256'], 'packet source/tool/header pin'); expected_inputs[path]=item['sha256']
    dirs = [register_dir, spi_dir, old_dir, spi_receipt.parent, packet_dir]
    inventories = {str(d): inventory(d) for d in dirs}
    need(set(inventories[str(spi_receipt.parent)]) == {'verification.json'}, 'single SPI pipeline receipt artifact')
    pinned_inventories = {str(resolve(d,llvm)):v for d,v in spi_record['artifact_inventories_before'].items()}
    pinned_inventories[str(spi_receipt.parent)]={'verification.json':SPI_RECEIPTS[language]}
    pinned_inventories[str(packet_dir)]={Path(item['path']).name:item['sha256'] for item in packet_record['artifacts']}
    pinned_inventories[str(packet_dir)]['verification.json']=PACKET_RECEIPTS[language]
    need(inventories==pinned_inventories, 'complete inherited artifacts joined to replayed frozen receipt pins')
    for directory, values in pinned_inventories.items():
        expected_inputs.update({Path(directory)/name:pin for name,pin in values.items()})
    expected_inputs[Path(__file__).resolve()]=digest(__file__)
    before = snapshots(expected_inputs)
    need(before==expected_inputs, 'all replayed file pins joined to actual pre-link snapshot')
    records = [dict(component='register-providers', receipt=str(register_dir/'verification.json'),
                    receipt_sha256=digest(register_dir/'verification.json'), replayed=True,
                    controls=len(register_record['negative_controls']), commands=register_record['commands'],
                    compiler_dependencies=register_record['compiler_dependencies']),
               dict(component='SPI-pipeline', receipt=str(spi_receipt), receipt_sha256=digest(spi_receipt),
                    replayed=True, controls=len(spi_record['negative_controls']),
                    commands=spi_record['commands']+spi_record['SPI_producer_commands'],
                    compiler_dependencies=spi_record['compiler_dependencies']),
               dict(component='packet', receipt=str(packet_receipt), receipt_sha256=digest(packet_receipt),
                    replayed=True, controls=len(packet_record['negative_controls']), commands=packet_record['recipes'],
                    compiler_dependencies=packet_record['md_dependencies'])]
    return dict(ELF=pk['ELF'], reader=reader, spi=sp, packet=pk, old_dir=old_dir, packet_dir=packet_dir,
                old=pk['ELF'](old_dir/'PIPELINE-SPI-OPEN.o'), packet_object=pk['ELF'](packet_dir/'native.o'),
                inputs=before, inventories=inventories, replay_records=records)


def local_symbols(sp):
    # The partial linker reorders SECTION metadata but preserves all FILE/mapping records.
    old = sp['locals_expected']()
    rows = old[:17] + old[19:29]
    rows += [('',0,0,3,0,2), ('',0,0,3,0,4), ('packet_receive.v5.c',0,0,4,0,65521),
             ('$x.0',352,0,0,0,1), ('$x.1',366,0,0,0,1), ('$x.2',482,0,0,0,1),
             ('$d.4',0,0,0,0,65521), ('',0,0,3,0,1)]
    return rows


def contract(e, dep, full=True):
    sp, pk, old, packet = dep['spi'], dep['packet'], dep['old'], dep['packet_object']
    need(e.header == [1,243,1,0,0,2552,1,52,0,0,40,8,6] and not e.program_headers and len(e.raw)==2872,
         'complete RV32 RVC ET_REL header/file extent, no program segment')
    keys = ['name','type','flags','address','offset','size','link','info','align','entsize']
    need([tuple(s[k] for k in keys) for s in e.sections] == SECTION_ROWS,
         'exact section ownership/allocation/relocation metadata')
    need([s['index'] for s in e.sections] == list(range(8)) and
         [s['name_offset'] for s in e.sections] == [0,1,11,17,32,46,54,64], 'complete section/string indices')
    skeys = ['name','value','size','info','other','section']
    need([tuple(s[k] for k in skeys) for s in e.symbols[:35]] == local_symbols(sp), 'exact local FILE/SECTION/mapping metadata')
    names = sp['OLD_NAMES'] + dep['reader'].NAMES + pk['NAMES']
    starts = sp['OLD_STARTS'] + [280+x for x in dep['reader'].STARTS] + [352,366,482]
    sizes = sp['OLD_SIZES'] + dep['reader'].SIZES + [14,116,12]
    expected = {n:(v,z,18,0,1) for n,v,z in zip(names,starts,sizes)};expected[RING]=(0,0,16,0,0)
    actual = {s['name']:tuple(s[k] for k in skeys[1:]) for s in e.symbols[35:]}
    need(len(e.symbols)==55 and len(actual)==20 and actual==expected, '19 genuine FUNCs, sole ring UND, no ABS/weak/alias providers')
    ordered = sorted(zip(starts,sizes))
    need(ordered[0][0]==0 and all(a+z==b for (a,z),(b,_) in zip(ordered,ordered[1:])) and ordered[-1][0]+ordered[-1][1]==494,
         'exact function adjacency, no gaps/overlap')
    rels = [(r['offset'],r['type'],old.symbols[r['symbol']]['name'],0,1) for r in old.relocations]
    rels += [(352+r['offset']+(14 if packet.sections[r['section']]['name'].endswith('packet_receive_body') else 0),
              r['type'],packet.symbols[r['symbol']]['name'],0,1) for r in packet.relocations]
    actual_rels = [(r['offset'],r['type'],e.symbols[r['symbol']]['name'],r['addend'],r['section']) for r in e.relocations]
    need(actual_rels==rels and len(rels)==23, 'exact 23 relocation owner/type/addend/target records')
    external = [r['offset'] for r in e.relocations if e.symbols[r['symbol']]['section']==0]
    need(external==[478] and sum(e.symbols[r['symbol']]['section']==1 for r in e.relocations)==22,
         '22 actual defined target edges, sole ring UND call at478')
    code = e.data('.pipeline')
    controls = {}
    for at,kind,_,_,_ in rels:
        width = 2 if kind in (44,45) else 4
        if kind==17: word=0x6f if at==128 else 0xef
        elif at in (294,318): word=0xc301
        elif at in (336,348): word=0xe381
        elif at==350: word=0xa001
        elif at==440: word=0xe301
        elif at==458: word=0x00e6e063
        else: raise ValueError('known symbolic port')
        need(code[at:at+width]==word.to_bytes(width,'little'), 'typed zero-immediate JAL/RVC/B ports')
        controls.update({at+i:True for i in range(width)})
    need(code[:352]==old.data('.pipeline'), 'unchanged actual 352-byte SPI pipeline projection')
    packet_code=b''.join(packet.data('.text.'+n) for n in pk['NAMES'])
    need(code[352:]==packet_code, 'unchanged actual 142-byte packet native projection')
    firmware=(ROOT/pk['FIRMWARE']).read_bytes()
    selected,original=bytearray(),bytearray()
    for dest,va,size in sp['CHUNKS']+[(352,0x16a7c,142)]:
        part=firmware[va-0x8000:va-0x8000+size];need(len(part)==size,'original region extent')
        for i in range(size):
            if dest+i not in controls:selected.append(code[dest+i]);original.append(part[i])
    need(len(selected)==414 and selected==original, 'all 414 original noncontrol bytes')
    at=0;instructions=0
    while at<len(code):
        at+=4 if code[at]&3==3 else 2;instructions+=1
    need(at==494 and instructions==178, 'complete 494B/178 instruction boundaries')
    # Range contracts remain symbolic: the machine immediates above are still zero.
    for at,target,kind in [(440,482,44),(458,482,16)]:
        delta=target-at;need(delta%2==0 and -(256 if kind==44 else 4096)<=delta<(256 if kind==44 else 4096),'finish branch range')
    if full:need(sha(e.raw)==PIPELINE_PIN,'whole measured partial ELF pin')
    return dict(allocated_bytes=494,instructions=178,genuine_FUNCs=19,RELA_total=23,
                JAL_records=16,branch_records=7,defined_target_edges=22,UND_providers=[RING],UND_calls=[478],
                ABS_providers=[],local_ABS_metadata=12,original_noncontrol_bytes=414,
                original_noncontrol_sha256=sha(bytes(original)),preserved_input_projections=[352,142],
                machine_immediates_resolved=False,firmware_ready=False,sections=e.sections,symbols=e.symbols,relocations=e.relocations)


def negatives(e, dep):
    """Mutate raw ELF bytes and reparse; the whole-file hash gate is disabled."""
    tests=[]
    def add(name, at, fmt, value):
        b=bytearray(e.raw);struct.pack_into(fmt,b,at,value)
        try:contract(dep['ELF'](b),dep,full=False)
        except (ValueError,IndexError,KeyError) as exc:
            tests.append(dict(name=name,rejected=True,whole_hash_enabled=False,reason=str(exc)))
        else:raise ValueError('negative accepted '+name)
    symbols={s['name']:s for s in e.symbols if s['info']>>4}
    for name in [dep['packet']['NAMES'][0],dep['packet']['NAMES'][2],RING]:
        at=844+symbols[name]['index']*16
        add('ABS_'+name,at+14,'<H',65521)
        add('weak_'+name,at+12,'<B',34)
    at=844+symbols[dep['packet']['NAMES'][0]]['index']*16
    for suffix,off,fmt,val in [('UND',14,'<H',0),('wrongvalue',4,'<I',354),('wrongsize',8,'<I',16),('OBJECT',12,'<B',17),('hidden',13,'<B',2)]:
        add('packet_'+suffix,at+off,fmt,val)
    add('local_FUNC_alias',844+2*16+12,'<B',2)
    add('local_ABS_changed',844+4*16+4,'<I',2)
    add('ET_EXEC',16,'<H',2);add('wrong_ELF_flags',36,'<I',0)
    for name,section,off,val in [('pipelineRW',1,8,7),('pipelinealign',1,32,4),('pipelinesize',1,20,492),('extraALLOC',4,8,2),('RELAowner',3,28,2)]:
        add(name,2552+40*section+off,'<I',val)
    for index in [3,12,17,20,21,22]:
        at=548+12*index;add('RELAoffset_'+str(index),at,'<I',e.relocations[index]['offset']+2)
        add('RELAaddend_'+str(index),at+8,'<i',2)
        other=53 if e.relocations[index]['symbol']==54 else 54
        add('RELAtarget_'+str(index),at+4,'<I',(other<<8)|e.relocations[index]['type'])
    for name,pc,offset,xor in [('JALimm',22,1,16),('tailRA',128,0,128),('packetJALrd',386,0,128),
          ('RVCimm',440,0,4),('RVCreg',440,0,128),('BRANCHimm',458,0,128),('BRANCHreg',458,2,1),
          ('old_noncontrol',138,0,4),('packetDLC',450,0,4),('finishSP',490,0,4)]:
        position=52+pc+offset;add(name,position,'<B',e.raw[position]^xor)
    return tests


def recipes(llvm, out, dep):
    obj=out/OBJECT
    return [('combine',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(LINKER),
             str(dep['old_dir']/'PIPELINE-SPI-OPEN.o'),str(dep['packet_dir']/'native.o'),'-o',str(obj)]),
            ('object',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(obj)])]


def evaluate(language, llvm, out):
    dep=providers(language,llvm);before=dep['inputs'];before_inventory=inventory(out)
    need(set(before_inventory)=={OBJECT,'recipes.json','combine.log','object.log','verification.json'} or
         set(before_inventory)=={OBJECT,'recipes.json','combine.log','object.log'},'exact new artifact inventory')
    expected=[dict(label=n,argv=portable(a,llvm),returncode=0) for n,a in recipes(llvm,out,dep)]
    need(json.loads((out/'recipes.json').read_bytes())==expected,'exact actual new link/dump recipes')
    need(not (out/'combine.log').read_bytes(),'warning-free actual linker output')
    log=(out/'object.log').read_text();need(str(out/OBJECT) in log and all(n in log for n in [RING]+dep['packet']['NAMES']), 'dump binds actual linked object and symbols')
    e=dep['ELF'](out/OBJECT);facts=contract(e,dep);controls=negatives(e,dep)
    need(snapshots(before)==before,'all source/header/tool/receipt/native artifact inputs stable')
    need({d:inventory(Path(d)) for d in dep['inventories']}==dep['inventories'],'complete provider artifact inventories stable')
    after_inventory=inventory(out);need(before_inventory==after_inventory,'new artifacts unchanged while reading')
    artifacts={n:v for n,v in after_inventory.items() if n!='verification.json'}
    record=dict(schema='TSL9-packet-494B-open-pipeline-v1',language=language,firmware_ready=False,
                target_executed=False,ISA_emulated=False,inputs_before={str(k):v for k,v in before.items()},
                inputs_after={str(k):digest(k) for k in before},dependency_inventories=dep['inventories'],
                dependency_replays=dep['replay_records'],commands=expected,artifacts=artifacts,
                facts=facts,negative_controls=controls,limitations=[
                 'ET_REL symbol bindings do not resolve the 23 zero-immediate machine control ports.',
                 'The ring provider remains absent; its resident dependency and private ABI remain open.',
                 'Original full-image placement, interior/cold entries, IRQ/fault/alias context, physical memory and hardware remain unproved.',
                 'No target/ISA/MMIO execution, firmware BIN generation, OTA or flash validation.'])
    record=portable(record,llvm);encoded=(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
    need(not re.search(rb'(?i)[a-z]:[/\\]|/(?:users|home)/',encoded),'portable receipt contains no host path')
    return record,encoded


def main():
    p=argparse.ArgumentParser(description=__doc__);action=p.add_mutually_exclusive_group(required=True)
    action.add_argument('--out-dir',type=Path);action.add_argument('--replay',type=Path)
    p.add_argument('--language',choices=['c','cpp']);p.add_argument('--llvm-bin',type=Path,
       default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    p.add_argument('--require-firmware-ready',action='store_true');args=p.parse_args();llvm=args.llvm_bin.resolve()
    if args.replay:
        receipt=args.replay.resolve();out=receipt.parent;saved=json.loads(receipt.read_bytes());language=saved['language']
        need(args.language is None or args.language==language,'replay language')
    else:
        need(args.language is not None,'build language required');language=args.language;out=args.out_dir.resolve()
    need(out.is_relative_to(HERE/'build') and out.parent.name.startswith('pipeline-') and out.name==language,'owned pipeline language output')
    if not args.replay:
        need(not out.exists(),'fresh pipeline output only');dep=providers(language,llvm);before=dep['inputs'];out.mkdir(parents=True)
        actual=[]
        for label,argv in recipes(llvm,out,dep):
            child=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
            (out/(label+'.log')).write_bytes(child.stdout);actual.append(dict(label=label,argv=portable(argv,llvm),returncode=child.returncode))
            need(child.returncode==0,'actual native recipe failed '+label)
        (out/'recipes.json').write_bytes((json.dumps(actual,indent=2)+'\n').encode())
        need(snapshots(before)==before,'all inputs unchanged across actual link')
    record,encoded=evaluate(language,llvm,out)
    if args.replay:need(receipt.read_bytes()==encoded and saved==record,'entire canonical LF receipt replay equality')
    else:(out/'verification.json').write_bytes(encoded)
    print(json.dumps(dict(result='PASS',language=language,bytes=494,instructions=178,FUNCs=19,RELA=23,
                          defined_targets=22,UND_calls=1,noncontrol_bytes=414,controls=len(record['negative_controls']),
                          ELF_sha256=PIPELINE_PIN,receipt_sha256=sha(encoded),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: pending machine controls, missing ring provider, original layout/ABI and hardware unproved.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
