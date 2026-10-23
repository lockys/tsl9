#!/usr/bin/env python3
"""Create-only C/C++ LLVM static trials. Never run emitted code or a model."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = json.loads((HERE/'spec.json').read_bytes())


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)+'\n').encode()


def facts(raw, firmware):
    E = runpy.run_path(str(ROOT/S['reader']))['ELF']
    e = E(raw)
    expected = {n:(a,z) for n,a,z in S['definitions']}
    fs = [f for f in e.symbols if f['info'] & 15 == 2]
    need(e.header[0] == 1 and e.header[6] == 1 and not e.program_headers, 'RV32 RVC unresolved ET_REL only')
    need({f['name'] for f in fs} == set(expected) and len(fs) == len(expected), 'Exact twenty-one C-owned architectural regions')
    need(not [f for f in e.symbols if f['section'] == 0xfff1 and f['info'] >> 4], 'No global ABS substitutes')
    sections = {}
    for f in fs:
        address,size = expected[f['name']]
        sec=e.sections[f['section']]
        need((f['value'],f['size'],f['info'],f['other']) == (0,size,18,0), 'Strong exact-size FUNC '+f['name'])
        need((sec['name'],sec['type'],sec['flags'],sec['size'],sec['align']) == ('.text.'+f['name'],1,6,size,2), 'Complete owned FUNC section '+f['name'])
        sections[sec['index']] = (f,address)
    table=e.section('.rodata.'+S['table'][0])
    need((table['type'],table['flags'],table['size'],table['align']) == (1,2,28,4), 'True relative table data allocation')
    ts=[f for f in e.symbols if f['name'] == S['table'][0]]
    need(len(ts) == 1 and (ts[0]['section'],ts[0]['value'],ts[0]['size'],ts[0]['info'],ts[0]['other']) == (table['index'],0,28,17,0), 'Strong OBJECT table owner')
    need({x['index'] for x in e.sections if x['flags']&2 and x['size']} == set(sections)|{table['index']}, 'Only294 code bytes and28 table bytes allocated')
    rows=json.loads((ROOT/S['listing']).read_bytes())
    selected={r['addr']:r for r in rows if any(a<=r['addr']<b for a,b in S['spans'][:2])}
    control={pc:r for pc,r in selected.items() if r['type'] in ('call','cjmp','jmp')}
    actual=[]; pc_ports=[]; datarels=[]
    keep={16:(4,0x01fff07f),17:(4,0x00000fff),23:(4,0x00000fff),24:(4,0x000fffff)}
    for secid,(f,address) in sections.items():
        data=bytearray(e.data(e.sections[secid])); original=bytearray(firmware[address-0x8000:address-0x8000+f['size']])
        for rel in [r for r in e.relocations if r['section'] == secid]:
            at,kind=rel['offset'],rel['type']; sym=e.symbols[rel['symbol']]
            need(kind in keep and rel['addend'] == 0 and 0<=at<=len(data)-4, 'Typed in-owner relocation with zero addend')
            width,mask=keep[kind]
            a=int.from_bytes(data[at:at+width],'little'); b=int.from_bytes(original[at:at+width],'little')
            need(a & mask == b & mask, 'Relocation instruction family/registers '+hex(address+at))
            data[at:at+width]=(a&mask).to_bytes(width,'little'); original[at:at+width]=(b&mask).to_bytes(width,'little')
            if kind in (16,17):
                pc=address+at
                need(pc in control, 'No invented control relocation')
                row=control[pc]
                target=expected[sym['name']][0] if sym['name'] in expected else int(sym['name'].rsplit('_',1)[1],16)
                need(target == row['jump'] and kind == (16 if row['type']=='cjmp' else 17), 'Genuine target and control type '+hex(pc))
                actual.append(dict(owner=f['name'],offset=at,PC=pc,type=kind,target=sym['name'],original_target=target))
            else:
                pc_ports.append((address+at,kind,sym['name'],sym['section'],sym['value']))
        need(data == original, 'Every nonrelocated original byte '+f['name'])
    need({x['PC'] for x in actual} == set(control) and len(actual) == len(control), 'Complete exact direct-control relocation inventory')
    need(len(pc_ports)==2 and pc_ports[0][:3] == (0x14d40,23,S['table'][0]) and pc_ports[1][0:2] == (0x14d44,24), 'Symbolic table HI20/LO12 ports')
    anchor=e.symbols[next(r['symbol'] for r in e.relocations if r['section'] in sections and sections[r['section']][1]+r['offset']==0x14d44)]
    need(anchor['section']==next(i for i,x in sections.items() if x[1]==0x14d40) and anchor['value']==0, 'LO12 points to genuine same-owner AUIPC anchor')
    data=bytearray(e.data(table))
    for i,target in enumerate(S['table_targets']):
        rels=[r for r in e.relocations if r['section']==table['index'] and r['offset']==4*i]
        need(len(rels)==2 and [(r['type'],e.symbols[r['symbol']]['name'],r['addend']) for r in rels] == [(35,target,0),(39,S['table'][0],0)], 'Every table entry has true ADD32/SUB32 target/base')
        need(data[4*i:4*i+4] == bytes(4), 'Zero symbolic table placeholder')
        target_va=expected[target][0] if target in expected else int(target.rsplit('_',1)[1],16)
        data[4*i:4*i+4]=((target_va-S['table'][1])&0xffffffff).to_bytes(4,'little')
        datarels.extend([dict(offset=r['offset'],type=r['type'],symbol=e.symbols[r['symbol']]['name']) for r in rels])
    need(data == firmware[S['table'][1]-0x8000:S['table'][1]-0x8000+28], 'All seven relative table entries match original data')
    need(len(e.relocations) == len(actual)+len(pc_ports)+len(datarels), 'No hidden relocation records')
    und=sorted(s['name'] for s in e.symbols if s['name'] and s['section']==0)
    return dict(code_bytes=294,table_bytes=28,FUNC=21,direct_controls=sorted(actual,key=lambda r:r['PC']),PC_relative_ports=pc_ports,data_relocations=datarels,RELA=len(e.relocations),UND=und,
                verification='Original-byte/static typed-relocation comparison only; no linked provider or execution claim')


def build(source, output, llvm):
    need(source.is_relative_to(HERE/'src') and source.is_file(), 'Source in bounded experiment')
    need(output.is_relative_to(HERE/'build') and not output.exists(), 'Create-only static trial')
    for k in ('firmware','listing','reader','profile_source'):
        need(sha(ROOT/S[k]) == S[k+'_sha256'], 'Pinned '+k)
    for n,pin in S['tools'].items():
        need(sha(llvm/n)==pin,'Pinned existing tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned stdint')
    C=runpy.run_path(str(ROOT/S['profile_source']))
    output.mkdir(parents=True)
    (output/'source.snapshot.c').write_bytes(source.read_bytes())
    (output/'spec.snapshot.json').write_bytes((HERE/'spec.json').read_bytes())
    fw=(ROOT/S['firmware']).read_bytes(); all_pass=True
    for mode in ('c','cpp'):
        folder=output/mode; folder.mkdir()
        flags=C['flags']({'profile':S['profile']},mode)
        cmds=[('compile',[str(llvm/'clang.exe'),*flags,'-c','-MD','-MF',str(folder/'unit.d'),'-MT','unit.o',str(source),'-o',str(folder/'unit.o')]),
              ('IR',[str(llvm/'clang.exe'),*flags,'-S','-emit-llvm',str(source),'-o',str(folder/'unit.ll')]),
              ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(folder/'unit.o')])]
        record=dict(schema='TSL9-outer-static-trial-v1',mode=mode,source=str(source.relative_to(ROOT)),source_sha256=sha(source),builder_sha256=sha(Path(__file__)),spec_sha256=sha(HERE/'spec.json'),profile=S['profile'],flags=flags,commands=[],passed=False,
                    target_executed=False,HOST_model_executed=False,ISA_emulated=False,network=False,hardware_accessed=False,firmware_ready=False)
        for label,argv in cmds:
            if label=='read' and not (folder/'unit.o').exists(): continue
            proc=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (folder/(label+'.log')).write_bytes(proc.stdout)
            record['commands'].append(dict(label=label,argv=argv,exit=proc.returncode,log_sha256=hashlib.sha256(proc.stdout).hexdigest()))
        try:
            need(all(x['exit']==0 for x in record['commands']) and len(record['commands'])==3,'Actual compiler/IR/reader commands passed')
            record['facts']=facts((folder/'unit.o').read_bytes(),fw)
            ir=(folder/'unit.ll').read_text(encoding='utf8')
            names=re.findall(r'^define\b[^\n]*@([A-Za-z0-9_]+)\(',ir,re.M)
            need(set(names)=={d[0] for d in S['definitions']},'All C regions retained in LLVM IR')
            record['passed']=True
        except Exception as err:
            record['failure']=type(err).__name__+': '+str(err); all_pass=False
        record['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.iterdir() if p.is_file()}
        (folder/'receipt.json').write_bytes(encoded(record))
        print(json.dumps({k:record[k] for k in ('mode','passed')}|{'failure':record.get('failure'),'object_sha256':sha(folder/'unit.o') if (folder/'unit.o').exists() else None}))
    need(all_pass,'One or more static trials failed; all original logs/artifacts retained')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--tool-dir',type=Path,default=Path(os.environ['USERPROFILE'])/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    a=parser.parse_args()
    build(a.source.resolve(),a.output.resolve(),a.tool_dir.resolve())
