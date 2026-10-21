"""Create-only historical evidence extraction; no compilation, execution or network.

Fresh builds consume source-manifest.json and original-image-layout.ld, and do not
need the historical build tree used by this one-time provenance extractor.
"""
from pathlib import Path
import hashlib,importlib.util,json,re
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def run():
    plan=R/'apk-analysis/tsl9-v4160-irq-callframe-2026-10-21/image-plan'
    seal=read(plan/'seal.json')
    for f in seal['files']:need(sha(plan/f['path'])==f['sha256'],'image-plan sealed member')
    d=read(plan/'verification.json');pins={x['path']:x['sha256'] for x in d['inputs']}
    base=R/'experiments/tsl9-v4160-startup/build/image-fidelity-999d8125159a4d80bd6df9153f267002'
    parser=R/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py'
    need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','parser')
    sp=importlib.util.spec_from_file_location('manifest_elf',parser);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
    for p in (base/'verification.json',base/'c/source-image-merged.o',base/'original-image-layout.ld'):
        need(sha(p)==pins[p.relative_to(R).as_posix()],'actual historical artifact pin')
    e=mod.ELF(base/'c/source-image-merged.o');alloc=read(base/'verification.json')['allocations']
    def role(s):return dict(name=s['name'],owner=e.sections[s['index']]['name'] if 0<s['index']<len(e.sections) else ('UND' if s['index']==0 else 'ABS'),offset=s['value'],bytes=s['size'],info=s['info'],other=s['other'])
    source={};units=[]
    def add(p):
        p=p.resolve();n=p.relative_to(R).as_posix()
        if n in source:return
        source[n]=sha(p)
        for name in re.findall(r'^\s*#include\s+"([^"]+)"',p.read_text(encoding='utf-8'),re.M):
            q=p.parent/name
            if name=='test_io.h' and not q.exists():continue # excluded HOST_TEST branch; native .d is checked
            add(q)
    for row in d['transitive_source_units']:
        p=R/'experiments/tsl9-v4160-startup'/row['path'];need(sha(p)==row['sha256'],'34 exact TUs');add(p);units.append(p.relative_to(R).as_posix())
    for n in ['interrupt_callframe.c','rcc_helpers.c']:add(R/'experiments/tsl9-v4160-irq-callframe/src'/n)
    result=dict(schema='TSL9-source-integrated-image-manifest-v1',plan_seal_sha256=sha(plan/'seal.json'),plan_verification_sha256=sha(plan/'verification.json'),
        original_image_sha256='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
        baseline_object_sha256=sha(base/'c/source-image-merged.o'),baseline_receipt_sha256=sha(base/'verification.json'),layout_sha256=sha(base/'original-image-layout.ld'),
        source_files=source,source_units=units,allocations=alloc,
        section_metadata={s['name']:{k:s[k] for k in ('type','flags','size','alignment','entry_size')} for s in e.sections if s['flags']&2 and s['size']},
        baseline_symbol_roles=[role(s) for s in e.symbols],selected_sections=d['selected_sections'],
        retained_RELA_count=d['retained_RELA_count'],retained_RELA_semantic_sha256=d['retained_RELA_semantic_sha256'],
        old_selected_RELA=d['old_selected_RELA'],external_incoming_RELA=d['external_incoming_RELA'],
        section_relative_bindings=d['section_relative_bindings'],expected_differences=d['probes'][0]['differences'])
    target=H/'source-manifest.json';data=(json.dumps(result,indent=2)+'\n').encode()
    if target.exists():need(read(target)==result,'immutable existing manifest')
    else:target.write_bytes(data)
    target=H/'original-image-layout.ld';data=(base/'original-image-layout.ld').read_bytes()
    if target.exists():need(target.read_bytes()==data,'immutable original691 layout')
    else:target.write_bytes(data)
    print(json.dumps(dict(passed=True,manifest_sha256=sha(H/'source-manifest.json'),source_units=len(units),source_files=len(source),allocations=len(alloc))))
if __name__=='__main__':run()
