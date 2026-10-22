#!/usr/bin/env python3
"""Actual raw-compiler to ordered-object to linked-component review."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PINS={'review.py':'57da439732bbfed651f6b7d82fd46762db3dbe1920e7555ddae5430ff62cd6b0',
      'frame.py':'8b8c9e3bee89287a1e41c394e5fe7a1ed7a8624f0bf80def7dc55c05fce2557d',
      'fields.py':'373d78c75feb58fcbf621d924733249786c8243197f8eef4e0a52e33e304b413',
      'llvm.py':'c52cc458441eab2038ff4bb5064666ec87af3b2345f5c8b99cf9fdcc0ffb0fd5'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)


def inspect(root,pre,folder):
    need(pre.is_relative_to(root) and folder.is_relative_to(root),'Explicit actual project folders')
    modules={}
    for name,pin in PINS.items():
        need(sha(HERE/name)==pin,'Frozen independent static gate '+name)
        modules[name]=runpy.run_path(str(HERE/name))
    source=modules['review.py']['inspect'](root,pre)
    need(source['profile']=='fresh-GP624','Only selected624 fresh-GP source variant is schedulable')
    scheduling=modules['frame.py']['audit'](root,pre/'callback.o',folder/'callback-ordered.o',folder/'frame-order.json')
    field=modules['fields.py'];ctx=field['context'](root);E=ctx['ELF']
    raw=E(pre/'COMPONENT-ONLY-NOT-FIRMWARE.elf');linked=E(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf')
    ordered=E(folder/'callback-ordered.o');function=next(s for s in raw.symbols if s['name']==modules['review.py']['NAME'])
    section=raw.sections[function['index']];payload=raw.data(section)
    expected=bytearray(raw.raw);start=section['offset']
    expected[start+2:start+6]=payload[4:6]+payload[2:4]
    need(linked.raw==bytes(expected),'Every linked ELF byte/metadata/LOAD unchanged except actual two-save permutation')
    need(raw.sections==linked.sections and raw.symbols==linked.symbols and raw.relocations==linked.relocations,
         'All linked allocation/symbol/relocation roles unchanged')
    objfunction=next(s for s in ordered.symbols if s['name']==function['name'])
    need(ordered.function_bytes(objfunction)==linked.function_bytes(function),
         'Actual linked code equals exact ordered source provider')
    rows=field['rows'](linked.data(linked.byname[section['name']]),section['address'],ctx)
    text=modules['llvm.py']['parse']((folder/'complete-static-disassembly.log').read_text())
    need([{k:v for k,v in r.items() if k!='offset'} for r in rows]==text,
         'All223 scheduled linked raw fields agree independently with LLVM operands')
    need([(r['rs2'],r['immediate']) for r in rows[1:12]]==
         [(8,40),(1,44),*modules['review.py']['SOURCE_SLOTS'][2:]],
         'Original relative eleven-save memory projection restored')
    need((folder/'component.ld').read_bytes()==(pre/'component.ld').read_bytes(),
         'Same actual component scratch layout; no invented original placement')
    actual={}
    for prefix,base,names in (
        ('pre',pre,('callback.o','callback.ll','probe.json','COMPONENT-ONLY-NOT-FIRMWARE.elf')),
        ('ordered',folder,('callback-ordered.o','frame-order.json','COMPONENT-ONLY-NOT-FIRMWARE.elf',
                           'component.ld','complete-static-disassembly.log'))):
        for name in names:actual[prefix+'/'+name]=dict(bytes=(base/name).stat().st_size,sha256=sha(base/name))
    producer=folder/'verification.json'
    return dict(schema='TSL9-callback-independent-ordered-profile-v1',actual_native_artifacts_read=True,
                actual_pre=pre.relative_to(root).as_posix(),actual_folder=folder.relative_to(root).as_posix(),
                source=source,scheduling=scheduling,actual_artifacts=actual,
                producer_receipt_sha256=sha(producer) if producer.exists() else None,
                ordered_ELF_sha256=sha(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'),
                allocated_bytes=624,instructions=223,mathematical_size_fits=True,
                whole632_storage_covered=False,unowned_original_tail_bytes=8,
                original_relative_save_order_matched=True,whole_original_prefix_equal=False,
                original_full_ABI_admitted=False,placement_admitted=False,
                HOST_suite_rerun=False,target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--pre',type=Path);p.add_argument('--folder',type=Path)
    p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(a.pre is None and a.folder is None and a.receipt is None,'Readonly actual ordered replay')
        old=json.loads(a.replay.read_bytes());result=inspect(root,root/old['actual_pre'],root/old['actual_folder'])
        need(result==old,'Exact actual ordered independent artifact replay')
    else:
        need(a.pre is not None and a.folder is not None and a.receipt is not None and not a.receipt.exists(),
             'Explicit actual pre/ordered folders and create-only receipt')
        result=inspect(root,a.pre.resolve(),a.folder.resolve());a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(passed=True,actual_native_artifacts_read=True,actual_ordered_artifacts_replayed=True,
                         bytes=624,instructions=223,relative_save_order_matched=True,
                         whole632_storage_covered=False,original_full_ABI_admitted=False,
                         placement_admitted=False,hardware_OTA_proved=False)))
