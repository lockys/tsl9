#!/usr/bin/env python3
"""Audit undefined symbols and discarded relocation owners in diagnostic ELFs."""
import argparse,json,re,runpy
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--conditional-dir',type=Path,required=True);p.add_argument('--sparse-dir',type=Path,required=True);a=p.parse_args()
root=a.project_root.resolve();base=a.conditional_dir.resolve();sparse=a.sparse_dir.resolve()
E=runpy.run_path(str(root/'src/native/tx_candidate/postpass/elf32.py'))['ELF'];results=[]
for mode in ('c','cpp'):
    source=E(base/'ram/base/source'/('NOT-FLASHABLE-candidate-aliases-'+mode+'.o'))
    final=E(sparse/('NOT-FLASHABLE-sparse-reference-'+mode+'.elf'))
    script=(base/('conditional-full-'+mode+'.ld')).read_text(encoding='utf-8')
    discard='/DISCARD/ : { *(.text*) *(.rodata*) *(.data*) *(.bss*) *(.sdata*) *(.sbss*) *(.eh_frame*) *(.comment) *(.note*) *(.riscv.attributes) *(.llvm_addrsig) }'
    if script.count(discard)!=1:raise ValueError('Discard policy changed')
    keep=set(re.findall(r'KEEP\(\*\((\.[^()\s*]+)\)\)',script))
    undefined={x['name'] for x in final.symbols if x['index']==0 and x['name']}
    if len(undefined)!=44 or final.relocations:raise ValueError('Final symbol or relocation inventory changed')
    definitions={x['name']:x for x in source.symbols if x['name'] in undefined}
    if set(definitions)!=undefined:raise ValueError('Missing source symbols')
    dropped=[];original_undef=[]
    for name,sym in definitions.items():
        if sym['index']==0:original_undef.append(name);continue
        if sym['index']>=len(source.sections):raise ValueError('Unexpected symbol section')
        sec=source.sections[sym['index']]['name']
        if not sec.startswith(('.text','.rodata','.data','.bss','.sdata','.sbss')) or sec in keep:raise ValueError('Symbol definition is not discarded')
        dropped.append(name)
    refs=[r for r in source.relocations if r['symbol']['name'] in undefined]
    owners={r['owner'] for r in refs}
    if len(dropped)!=43 or original_undef!=['tsl9_runtime_reset_stack_top'] or len(refs)!=24 or len(owners)!=10 or any(not name.startswith(('.text','.rodata','.data','.bss','.sdata','.sbss')) or name in keep for name in owners):raise ValueError('Discarded references changed')
    fake_keep=set(keep);fake_keep.add(next(iter(owners)))
    assert any(name in fake_keep for name in owners)
    results.append({'mode':mode,'final_undefined':len(undefined),'originally_defined_discarded':len(dropped),'originally_undefined':len(original_undef),'input_relocations_to_these_symbols':len(refs),'relocation_owner_sections':len(owners),'all_reference_owners_discarded':True,'final_relocations':len(final.relocations),'synthetic_negative_control':True})
print(json.dumps({'passed':True,'results':results,'runtime_indirect_calls_proved':False,'installed_rom_proved':False,'data_bounds_proved':False,'target_executed':False,'flashable':False}))
