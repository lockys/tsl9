#!/usr/bin/env python3
"""Compare actual ELF32 objects with independent parsers; never execute their code."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'experiments/tsl9-original-RF-task-path/elf_reader-v6.py'
NEW=ROOT/'experiments/tsl9-resident-root-chain-callees/elf_reader-v7.py'
INDEPENDENT=ROOT/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbol(s,new=False):return tuple(s[k]for k in['name','value','size','info','other'])+(s['section'if new else'index'],)
def audit(path):
    need(sha(OLD)=='cf9500ec7898149f979042671fba4653ab24bc474c23c384d3e82cacd67ccda2','Frozen v6 reader unchanged')
    need(sha(INDEPENDENT)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Independent parser unchanged')
    expected=OLD.read_text(encoding='utf8').replace('Only section-count ceiling changes from retained v5: <2048 to <4096 for the measured2218-section RF task composition.','Only section-count ceiling changes from retained v6: <4096 to <8192 for the measured4147-section root-callee composition.').replace('0 < h[12] < 4096','0 < h[12] < 8192')
    need(NEW.read_text(encoding='utf8')==expected,'Only section ceiling and explanatory doc changed')
    A=runpy.run_path(str(NEW))['ELF'];B=runpy.run_path(str(INDEPENDENT))['ELF'];a,b=A(path),B(path)
    need(len(a.sections)==len(b.sections)and a.header[0]==b.kind==1 and a.header[6]==b.flags and not a.program_headers,'Actual RISC-V relocatable object')
    mapping={'align':'alignment','entsize':'entry_size'}
    for x,y in zip(a.sections,b.sections):
        for key in['name','type','flags','address','offset','size','link','info','align','entsize','index']:need(x[key]==y[mapping.get(key,key)],'Every actual section field agrees')
        if x['type']!=8:need(a.data(x)==b.data(y),'Every actual file-backed byte agrees')
    need([symbol(x,True)for x in a.symbols]==[symbol(x)for x in b.symbols],'Every symbol role/value/size/owner agrees')
    ar=Counter((a.sections[x['section']]['name'],x['offset'],x['type'],x['addend'],symbol(a.symbols[x['symbol']],True))for x in a.relocations)
    br=Counter((x['owner'],x['offset'],x['type'],x['addend'],symbol(x['symbol']))for x in b.relocations)
    need(ar==br,'Every typed relocation source/target role agrees')
    return dict(passed=True,sections=len(a.sections),symbols=len(a.symbols),relocations=len(a.relocations),object_sha256=sha(Path(path)),only_section_ceiling_and_doc_changed=True,all_actual_section_bytes_symbols_and_relocations_equal=True,target_executed=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--object',required=True,type=Path);args=p.parse_args();print(json.dumps(audit(args.object)))
