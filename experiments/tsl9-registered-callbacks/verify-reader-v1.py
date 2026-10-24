#!/usr/bin/env python3
"""Positive comparison of two local parsers on measured callback objects; no target execution."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, runpy

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'experiments/tsl9-feature-dispatch-tree/elf_reader-v3.py'
NEW=ROOT/'experiments/tsl9-feature-dispatch-tree/elf_reader-v4.py'
INDEPENDENT=ROOT/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encode(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
def symbol(s,new=False):return tuple(s[k]for k in ['name','value','size','info','other'])+(s['section'if new else'index'],)

def proof():
    need(sha(OLD)=='112e90f7a1786bd1e388718e80086ba937035364d926c89cd5875eba68ce543a','Frozen v3 reader remains unchanged')
    need(sha(INDEPENDENT)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Independent curation parser remains unchanged')
    expected=OLD.read_text('utf-8').replace('Only section-count ceiling changes: <64 to <512 for 96 tree regions.','Only section-count ceiling changes from retained v3: <512 to <1024 for the measured613-section callback object.').replace('0 < h[12] < 512','0 < h[12] < 1024')
    need(NEW.read_text('utf-8')==expected,'Only the count ceiling and explanatory doc changed')
    A=runpy.run_path(str(NEW))['ELF'];B=runpy.run_path(str(INDEPENDENT))['ELF']
    record=json.loads((HERE/'build/native-v2/measurement.json').read_bytes());facts={}
    for mode in ('c','cpp'):
        path=HERE/'build/native-v2'/mode/'unit.o';a,b=A(path),B(path)
        need(sha(path)==record['modes'][mode]['result']['native_object_sha256'],'Actual accepted native object')
        need(len(a.sections)==len(b.sections)==613 and a.header[0]==b.kind==1 and a.header[6]==b.flags,'Measured actual613-section ELF32 object')
        mapping={'align':'alignment','entsize':'entry_size'}
        for x,y in zip(a.sections,b.sections):
            for key in ['name','type','flags','address','offset','size','link','info','align','entsize','index']:
                need(x[key]==y[mapping.get(key,key)],'Every actual section field agrees')
            if x['type']!=8:need(a.data(x)==b.data(y),'Every actual file-backed section byte agrees')
        need([symbol(x,True)for x in a.symbols]==[symbol(x)for x in b.symbols],'Every symbol role/value/size/owner agrees')
        ar=Counter((a.sections[x['section']]['name'],x['offset'],x['type'],x['addend'],symbol(a.symbols[x['symbol']],True))for x in a.relocations)
        br=Counter((x['owner'],x['offset'],x['type'],x['addend'],symbol(x['symbol']))for x in b.relocations)
        need(ar==br and len(a.relocations)==300,'All300 typed relocation source/target roles agree')
        facts[mode]=dict(passed=True,sections=613,symbols=len(a.symbols),relocations=300,object_sha256=sha(path))
    need(facts['c']==facts['cpp'],'Both language artifacts are identical')
    paths=[Path(__file__),OLD,NEW,INDEPENDENT,HERE/'build/native-v2/measurement.json']+[HERE/'build/native-v2'/mode/'unit.o'for mode in('c','cpp')]
    return dict(passed=True,inputs={p.relative_to(ROOT).as_posix():sha(p)for p in paths},languages=facts,
                retained_reader_unchanged=True,independent_parser_unchanged=True,only_section_ceiling_and_doc_changed=True,
                original_section_limit_exclusive=512,new_section_limit_exclusive=1024,actual_sections=613,
                all_actual_section_bytes_symbols_and_relocations_equal=True,
                target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,negative_cases_executed=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path);a=p.parse_args();result=proof()
    out=(a.output or a.replay).resolve();need(out.parent==HERE/'build','Owned proof path')
    if a.replay:need(json.loads(out.read_bytes())==result,'Exact positive parser comparison replay')
    else:need(not out.exists(),'Create-only proof');out.write_bytes(encode(result))
    print(json.dumps({k:v for k,v in result.items()if k not in ('inputs','languages')}))
