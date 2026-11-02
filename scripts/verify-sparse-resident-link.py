#!/usr/bin/env python3
"""Link a pinned sparse reference resident for offline evidence only."""
import argparse,hashlib,json,re,runpy,struct,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--conditional-dir',type=Path,required=True);p.add_argument('--reference-dir',type=Path,required=True);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
root=a.project_root.resolve();base=a.conditional_dir.resolve();ref=a.reference_dir.resolve();out=a.out.resolve()
if out.exists() or out==root or root in out.parents:raise ValueError('Output must be a new directory outside project')
def sha(data):return hashlib.sha256(data).hexdigest()
manifest=(ref/'source-map.json').read_bytes()
if sha(manifest)!='96ff0490ccd196ee97655a80ed44ea2b1ceee53b84ca3bad8f8f74525031c0ba':raise ValueError('Reference map changed')
m=json.loads(manifest);segments=m['segments']
if not m['passed'] or len(segments)!=17:raise ValueError('Reference segments changed')
for x in segments:
    path=(ref/x['path']).resolve()
    if path.parent!=ref or path.suffix!='.bin' or x['end_exclusive']-x['start']!=x['bytes'] or sha(path.read_bytes())!=x['sha256']:raise ValueError('Invalid reference segment')
if segments[0]['start']!=0x40000 or segments[0]['end_exclusive']!=0x6ea66 or segments[-1]['end_exclusive']!=0x6eb2c:raise ValueError('Reference extents changed')
if any(x['end_exclusive']>y['start'] for x,y in zip(segments,segments[1:])):raise ValueError('Reference overlaps')
def tool(name):
    exe=a.tool_dir/(name+'.exe')
    return exe if exe.is_file() else a.tool_dir/name
def run(*args):
    q=subprocess.run(list(map(str,args)),capture_output=True,text=True)
    if q.returncode:raise ValueError('Tool failure: '+q.stderr[:1000])
reader=runpy.run_path(str(root/'src/native/tx_candidate/postpass/elf32.py'))['ELF']
out.mkdir(parents=True)
lines=[]
for i,s in enumerate(segments):
    lines+=['.section .reference_'+str(i)+',"'+('ax' if i==0 else 'a')+'",@progbits']
    if i==0:lines+=['.globl tsl9_boot_resident_40000','.type tsl9_boot_resident_40000,@function','tsl9_boot_resident_40000:']
    lines+=['.incbin '+json.dumps((ref/s['path']).as_posix())]
    if i==0:lines+=['.size tsl9_boot_resident_40000,4']
src=out/'reference.s';src.write_text('\n'.join(lines)+'\n',encoding='ascii')
obj=out/'reference.o';run(tool('clang'),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-c',src,'-o',obj)
shortsrc=out/'entry-only.s'
shortsrc.write_text('.section .reference_0,"ax",@progbits\n.globl tsl9_boot_resident_40000\n.type tsl9_boot_resident_40000,@function\ntsl9_boot_resident_40000:\n.incbin '+json.dumps((ref/segments[0]['path']).as_posix())+',0,4\n.size tsl9_boot_resident_40000,4\n',encoding='ascii')
shortobj=out/'entry-only.o'
run(tool('clang'),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-c',shortsrc,'-o',shortobj)
aliases=['--defsym=tsl9_input_state_decoders_static_data_1ab48=tsl9_input_counter_read_window_1ab48','--defsym=tsl9_record_field_transitions_static_data_1a078=tsl9_grid_read_data_pool_19ed8+416','--defsym=tsl9_registered_callbacks_static_data_1a638=tsl9_sequence_compare_read_window_1a638']
results=[]
for mode in ('c','cpp'):
    layout=(base/('conditional-full-'+mode+'.ld')).read_text(encoding='utf-8')
    if layout.count('SECTIONS {\n')!=1:raise ValueError('Layout changed')
    additions=''.join(' .reference_'+str(i)+' '+hex(s['start'])+' : SUBALIGN(1) { KEEP(*(.reference_'+str(i)+')) } :NONE\n' for i,s in enumerate(segments))
    ld=out/(mode+'.ld');ld.write_text(layout.replace('SECTIONS {\n','SECTIONS {\n'+additions),encoding='utf-8')
    inputs=[base/'ram/base/source'/('NOT-FLASHABLE-candidate-aliases-'+mode+'.o'),base/'ram'/mode/'conditional-storage.o',base/('opaque-provider-'+mode+'.o')]
    common=[tool('ld.lld'),'--no-undefined','--no-relax','-T',ld,*inputs,*aliases]
    absent=out/('NO-RESIDENT-'+mode+'.elf')
    rejected=subprocess.run(list(map(str,[*common,'-o',absent])),capture_output=True,text=True)
    errors=set(re.findall(r'undefined symbol: ([^\r\n]+)',rejected.stderr))
    if rejected.returncode==0 or errors!={'tsl9_boot_resident_40000'} or absent.exists():raise ValueError('Missing resident negative control failed')
    short=out/('NOT-FLASHABLE-entry-only-'+mode+'.elf')
    run(*common,shortobj,'-o',short)
    shortelf=reader(short);shortsec=shortelf.byname['.reference_0']
    if shortsec['address']!=0x40000 or shortsec['size']!=4 or shortelf.data(shortsec)!=(ref/segments[0]['path']).read_bytes()[:4]:raise ValueError('Entry-only counterexample changed')
    if any('.reference_'+str(i) in shortelf.byname for i in range(1,len(segments))):raise ValueError('Entry-only counterexample unexpectedly includes more reference sections')
    shortsyms={s['name']:s for s in shortelf.symbols if s['name']}
    if shortsyms['tsl9_boot_resident_40000']['index']!=shortsec['index']:raise ValueError('Entry-only symbol is not section backed')
    phoff=struct.unpack_from('<I',shortelf.raw,28)[0];phsize,phcount=struct.unpack_from('<HH',shortelf.raw,42)
    if any(struct.unpack_from('<I',shortelf.raw,phoff+i*phsize)[0]==1 for i in range(phcount)):raise ValueError('Entry-only diagnostic unexpectedly loadable')
    dest=out/('NOT-FLASHABLE-sparse-reference-'+mode+'.elf')
    run(*common,obj,'-o',dest)
    e=reader(dest);syms={s['name']:s for s in e.symbols if s['name']};entry=syms['tsl9_boot_resident_40000']
    for i,s in enumerate(segments):
        sec=e.byname['.reference_'+str(i)]
        if sec['address']!=s['start'] or e.data(sec)!=(ref/s['path']).read_bytes():raise ValueError('Reference section mismatch')
    if entry['value']!=0x40000 or entry['index']!=e.byname['.reference_0']['index']:raise ValueError('Entry is not section backed')
    image=bytearray();pos=0x8000
    for sec in sorted((s for s in e.sections if s['flags']&2 and s['size'] and s['type']!=8 and 0x8000<=s['address']<0x1ac00),key=lambda s:s['address']):
        if sec['address']!=pos:raise ValueError('APP section gap')
        image.extend(e.data(sec));pos+=sec['size']
    if pos!=0x1ac00 or sha(image)!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('APP image changed')
    phoff=struct.unpack_from('<I',e.raw,28)[0];size,count=struct.unpack_from('<HH',e.raw,42)
    if any(struct.unpack_from('<I',e.raw,phoff+i*size)[0]==1 for i in range(count)):raise ValueError('Diagnostic unexpectedly loadable')
    undefined=[s['name'] for s in e.symbols if s['index']==0 and s['name']]
    if 'tsl9_boot_resident_40000' in undefined:raise ValueError('Resident entry remains undefined')
    results.append({'mode':mode,'strict_link_succeeded':True,'reference_sections':len(segments),'undefined_symbol_table_entries':len(undefined),'app_image_matches':True,'pt_load':0,'missing_provider_rejected':True,'entry_only_four_byte_link_succeeded':True})
missing=[x for x in range(0x6eaa4,0x6eb30) if not any(s['start']<=x<s['end_exclusive'] for s in segments)]
if missing!=list(range(0x6eb2c,0x6eb30)):raise ValueError('Startup source coverage changed')
print(json.dumps({'passed':True,'results':results,'startup_source_missing_bytes':len(missing),'installed_rom_proved':False,'ram_ownership_proved':False,'global_index_bounds_proved':False,'target_executed':False,'hardware_validated':False,'flashable':False}))
