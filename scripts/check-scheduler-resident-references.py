#!/usr/bin/env python3
"""Read-only validation of retained reference data; never identifies installed ROM."""
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'analysis/scheduler-2026-10-23/resident-reference-association.json'

def need(ok,message):
    if not ok:
        raise ValueError(message)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    saved=json.loads(REPORT.read_bytes())
    header=ROOT/saved['header']
    need(sha(header)==saved['header_sha256'],'Exact retained historical header')
    mapping=[]
    for line_no,line in enumerate(header.read_bytes().decode('latin1').splitlines(),1):
        m=re.search(r'^#define\s+(\w+)\s+.*BLE_LIB_JT\((7|9|13|126)\)',line)
        if m:
            index=int(m.group(2))
            mapping.append(dict(line=line_no,macro=m.group(1),JT_index=index,
                                slot=0x40034+4*index,declaration=line))
    need(mapping==saved['mapping'],'Exact four ASCII macro declarations/indices')
    for candidate in saved['candidates']:
        mp=ROOT/candidate['source_map'];meta=json.loads(mp.read_bytes())
        need(sha(mp)==candidate['source_map_sha256'],'Retained complete source-map identity')
        source=(mp.parent/meta['source']['path']).resolve()
        need(source.is_relative_to(ROOT)and sha(source)==candidate['source_hex_sha256']==meta['source']['sha256'],'Retained primary HEX identity')
        actual=[];parts=[]
        for s in meta['segments']:
            p=(mp.parent/s['path']).resolve()
            need(p.is_relative_to(ROOT),'Owned local reference path')
            raw=p.read_bytes()
            need(len(raw)==s['bytes']and sha(p)==s['sha256'],'Exact sparse reference bytes')
            actual.append(dict(path=p.relative_to(ROOT).as_posix(),start=s['start'],
                               end=s['end_exclusive'],bytes=s['bytes'],sha256=s['sha256']))
            parts.append((s,raw))
        need(actual==candidate['segments'],'Complete retained sparse segment inventory')
        def read(address,width):
            rows=[b[address-s['start']:address-s['start']+width]for s,b in parts
                  if s['start']<=address and address+width<=s['end_exclusive']]
            need(len(rows)==1,'Single actual covered reference range')
            return rows[0]
        pointer=int.from_bytes(read(0x40034,4),'little')
        need(pointer==candidate['version_pointer'],'Actual reference version pointer')
        text=[]
        for i in range(80):
            byte=read(pointer+i,1)[0]
            if byte==0:
                break
            text.append(byte)
        need(bytes(text).decode('ascii')==candidate['version_ascii'],'Actual reference version bytes')
        words=[dict(slot=m['slot'],pointer=int.from_bytes(read(m['slot'],4),'little'))for m in mapping]
        need(words==candidate['table_words'],'Actual reference table pointer words')
    need(all(saved[k]is False for k in ['actual_installed_library_version_proved',
         'physical_MCU_identity_proved','ABI_or_runtime_behavior_proved',
         'candidate_addresses_bound_into_reconstruction','target_executed','ISA_emulated',
         'hardware_accessed','network','firmware_ready']),'Reference-only claim boundaries')
    print(json.dumps(dict(passed=True,reference_images=2,header_macros=4,
                          installed_ROM_identified=False,physical_MCU_proved=False,
                          no_candidate_provider_bound=True,target_executed=False)))
if __name__=='__main__':
    try:
        main()
    except (OSError,ValueError,KeyError)as error:
        print('FAIL: '+str(error),file=sys.stderr);sys.exit(1)
