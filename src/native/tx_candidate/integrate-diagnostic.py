#!/usr/bin/env python3
"""Integrate compiled TX into a bounded source-derived diagnostic ELF; no firmware BIN."""
import argparse, hashlib, json, re, runpy, struct, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--project-root', type=Path, default=HERE.parents[2])
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
root = a.project_root.resolve(); out = a.out.resolve()
if out.exists() or out == HERE or HERE in out.parents: raise SystemExit('Output must be a new path outside source tree')
obj = root/'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/split-C-payload.o'
layout = root/'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/original-layout.ld'
obj_cpp = root/'experiments/tsl9-original-layout/build/event-word-table-data-v1/cpp/split-C-payload.o'
layout_cpp = root/'experiments/tsl9-original-layout/build/event-word-table-data-v1/cpp/original-layout.ld'
parser = root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
for path, expected in ((obj, 'fbfc95442f35275192e698c0252a1540922f342f06562b42817603fda42c6965'), (layout, '2cab1617adbd580ef4d3347fb8bf06359e858bfb5a002ae75aae0027e0c502a9'), (parser, '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141')):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected: raise SystemExit('Pinned diagnostic input changed')
if hashlib.sha256(obj_cpp.read_bytes()).digest()!=hashlib.sha256(obj.read_bytes()).digest() or hashlib.sha256(layout_cpp.read_bytes()).digest()!=hashlib.sha256(layout.read_bytes()).digest():
    raise SystemExit('C and C++ diagnostic inputs differ')
if a.candidate.stat().st_size != 76800: raise SystemExit('Unexpected candidate size')
ELF = runpy.run_path(str(parser))['ELF']; source = ELF(obj)
sec = source.byname['.original_code_span_00008520']; lo=0x8a56-0x8520; hi=0x8b6e-0x8520
if source.kind != 1 or sec['size'] != 47926: raise SystemExit('Unexpected source section')
inner = {id(s) for s in source.symbols if s['index']==sec['index'] and lo < s['value'] < hi}
incoming = []
for rel in source.relocations:
    inside = rel['owner']==sec['name'] and lo <= rel['offset'] < hi
    if not inside and id(rel['symbol']) in inner: raise SystemExit('External relocation references old TX interior')
    if not inside and rel['symbol']['index']==sec['index'] and rel['symbol']['value']+rel['addend']==lo: incoming.append(rel)
if len(incoming)!=8: raise SystemExit('Unexpected incoming entry references')
out.mkdir(parents=True)
subprocess.run([sys.executable,'-B',str(HERE/'verify-linked.py'),'--project-root',str(root),'--tool-dir',str(a.tool_dir),'--candidate',str(a.candidate),'--out',str(out/'tx')],check=True,capture_output=True,text=True)
tx=(out/'tx/NOT-FLASHABLE-TX-ONLY-c.bin').read_bytes()
if len(tx)!=280 or hashlib.sha256(tx).hexdigest()!='8b129d84cbd65062315ec8197f7cbabb0eae7a4dfec4dca5bf39861851a525b9': raise SystemExit('Unexpected compiled TX')
raw=bytearray(source.raw);raw[sec['offset']+lo:sec['offset']+hi]=tx
allowed_changes=set(range(sec['offset']+lo,sec['offset']+hi))
relsections=[x for x in source.sections if x['type']==4 and x['info']==sec['index']]
if len(relsections)!=1: raise SystemExit('Unexpected code relocation sections')
relsec=relsections[0];sites=[]
for offset in range(relsec['offset'],relsec['offset']+relsec['size'],12):
    site,info,addend=struct.unpack_from('<IIi',raw,offset)
    if lo <= site < hi:
        sites.append(0x8520+site);struct.pack_into('<Ii',raw,offset+4,0,0);allowed_changes.update(range(offset+4,offset+12))
if sites != [0x8a5a,0x8a76,0x8a7e,0x8a92,0x8a9a,0x8aa2,0x8aba,0x8b10,0x8b6a]: raise SystemExit('Unexpected old TX relocation sites')
symtabs=[s for s in source.sections if s['type']==2]
if len(symtabs)!=1: raise SystemExit('Unexpected symbol tables')
symtab=symtabs[0]; masked=0
for i,s in enumerate(source.symbol_tables[symtab['index']]):
    if s['index']==sec['index'] and lo<s['value']<hi:
        at=symtab['offset']+16*i
        struct.pack_into('<I',raw,at,0)       # No stale internal symbol name.
        struct.pack_into('<I',raw,at+8,0)     # No stale function size.
        raw[at+12] &= 0xf0                   # Preserve binding; discard old type.
        allowed_changes.update(range(at,at+4));allowed_changes.update(range(at+8,at+13))
        masked+=1
if masked!=24: raise SystemExit('Unexpected old TX interior symbol count')
if any(i not in allowed_changes for i,(before,after) in enumerate(zip(source.raw,raw)) if before!=after):raise SystemExit('Unexpected object change')
replacement=out/'NOT-FLASHABLE-source-with-TX.o';replacement.write_bytes(raw)
patched=ELF(replacement)
if patched.data(patched.byname[sec['name']])[:lo] != source.data(sec)[:lo] or patched.data(patched.byname[sec['name']])[hi:] != source.data(sec)[hi:]: raise SystemExit('Non-TX code changed')
if any(s['name'] for s in patched.symbols if s['index']==sec['index'] and lo<s['value']<hi):raise SystemExit('Stale TX interior symbol names remain')
if any(rel['type']!=0 for rel in patched.relocations if rel['owner']==sec['name'] and lo<=rel['offset']<hi):raise SystemExit('Old TX relocations remain active')
ld=a.tool_dir/('ld.lld.exe' if (a.tool_dir/'ld.lld.exe').is_file() else 'ld.lld')
cmd=[str(ld),'--no-undefined','--no-relax','-T',str(layout),str(replacement)]
strict=subprocess.run([*cmd,'-o',str(out/'STRICT-UNRESOLVED.elf')],capture_output=True,text=True)
names={'tsl9_boot_resident_40000':0x40000,'tsl9_incoming_external_14056':0x14056,'tsl9_input_state_decoders_static_data_1ab48':0x1ab48,'tsl9_record_field_transitions_static_data_1a078':0x1a078,'tsl9_registered_callbacks_static_data_1a638':0x1a638,'tsl9_settings_default_data_1a69c':0x1a69c}
missing=set(re.findall(r'undefined symbol: ([^\r\n]+)',strict.stderr))
if strict.returncode==0 or missing!=set(names):raise SystemExit('Strict link did not report exactly six missing providers')
diagnostic=out/'NOT-FLASHABLE-ORIGINAL-LAYOUT.elf'
result=subprocess.run([*cmd,*['--defsym='+k+'='+hex(v) for k,v in names.items()],'-o',str(diagnostic)],capture_output=True,text=True)
if result.returncode: raise SystemExit('Diagnostic witness link failed: '+result.stderr[:1000])
elf=ELF(diagnostic)
if elf.kind!=2: raise SystemExit('Not diagnostic ET_EXEC')
phoff=struct.unpack_from('<I',elf.raw,28)[0];phsize,phcount=struct.unpack_from('<HH',elf.raw,42)
if any(struct.unpack_from('<I',elf.raw,phoff+i*phsize)[0]==1 for i in range(phcount)):raise SystemExit('Unexpected loadable segment')
excluded=((0x14056,0x14c8a),(0x1a69c,0x1a6a0));sections=[s for s in elf.sections if s['flags']&2 and s['size']]
if len(sections)!=40 or sum(s['size'] for s in sections)!=73538:raise SystemExit('Unexpected diagnostic extent')
count=0
with a.candidate.open('rb') as stream:
    for s in sections:
        start=s['address'];end=start+s['size']
        if s['type']!=1 or not 0x8000<=start<end<=0x1ac00 or any(not(end<=lo or start>=hi) for lo,hi in excluded):raise SystemExit('Rejected section or excluded window')
        stream.seek(start-0x8000);expected=stream.read(s['size'])
        if len(expected)!=s['size'] or expected!=elf.data(s):raise SystemExit('Candidate mismatch in allowed diagnostic section '+s['name'])
        count+=len(expected)
print(json.dumps({'passed':True,'source_tx_integrated':True,'checked_candidate_bytes':count,'old_tx_relocations_disabled':len(sites),'stale_interior_symbols_masked':masked,'external_entry_references':len(incoming),'strict_link_undefined':len(names),'diagnostic_pt_load':0,'complete_firmware':False,'flashable':False,'excluded_read':False}))
