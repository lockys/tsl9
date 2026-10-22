"""Independent source/command/dependency readback for the frozen actual build."""
from pathlib import Path
import hashlib,json,re
H=Path(__file__).resolve().parent;R=H.parents[2]
MODEL=R/'experiments/tsl9-v4160-irq-image-integration'
RUNNER=H.parent/'integration/verify_image.py'
BUILD=MODEL/'build/source-integrated-99841ffbf5234f3a843228157e832782'
PLAN=R/'apk-analysis/tsl9-v4160-irq-callframe-2026-10-21/image-plan/verification.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def projection(raw,selected):
    lines=raw.splitlines(keepends=True);spans=[]
    decoded={i:json.loads(line.decode().strip()) for i,line in enumerate(lines) if line.decode().strip().startswith('"')}
    for row in selected:
        starts=[i for i,s in decoded.items() if s.startswith('.section '+row['name']+',')];need(len(starts)==1,'one original selected block')
        i=starts[0];ends=[j for j,s in decoded.items() if j>i and s=='.size '+row['global_alias']+','+str(row['bytes'])+'\n']
        need(len(ends)==1,'one exact original block size terminator');j=ends[0]
        need(all(not s.startswith('.section ') for k,s in decoded.items() if i<k<=j),'selected block is bounded')
        spans.append((i,j+1))
    removed={i for a,b in spans for i in range(a,b)}
    return b''.join(line for i,line in enumerate(lines) if i not in removed)
def adapter(rows):
    text='#include <stdint.h>\n#ifdef __cplusplus\nextern "C" {\n#endif\n'
    for r in rows:
        text+='uint32_t '+r['new_C_symbol']+'('+('void' if r['bytes']==144 else 'uint32_t mask,uint32_t enabled')+') __attribute__((section("'+r['name']+'"),used,noinline));\n'
        text+='extern __typeof__('+r['new_C_symbol']+') '+r['global_alias']+' __attribute__((alias("'+r['new_C_symbol']+'")));\n'
    return (text+'#ifdef __cplusplus\n}\n#endif\n').encode()
def script_check(path,m):
    allowed={b['name']:b for b in m['section_relative_bindings']};seen=set();sections=[];kept=[];sizes=[];owner=None;afterkeep=False
    for line in path.read_text().splitlines():
        s=line.strip()
        if not s or s in ['SECTIONS {','}'] or s.startswith('/*'):continue
        q=re.fullmatch(r'(\.[\w.]+) 0( \(NOLOAD\))? : \{',s)
        if q:
            owner=q[1];need(owner in m['allocations'],'canonical partial section');need(bool(q[2])==(m['allocations'][owner]['kind']=='RAM'),'RAM NOLOAD declaration');sections.append(owner);afterkeep=False;continue
        q=re.fullmatch(r'(\w+) = ([^;]+);',s)
        if q:
            name,expr=q.groups();need(name in allowed and name not in seen and not afterkeep,'only53 bindings beforeKEEP')
            b=allowed[name];need(b['role']['owner']==owner and b['expression']==expr,'binding proven owner/expression');seen.add(name);continue
        q=re.fullmatch(r'KEEP\(\*\(([^)]+)\)\)',s)
        if q:need(q[1]==owner,'KEEP own section');kept.append(owner);afterkeep=True;continue
        q=re.fullmatch(r'ASSERT\(SIZEOF\(([^)]+)\)==(\d+), "partial storage size"\)',s)
        if q:need(int(q[2])==m['allocations'][q[1]]['bytes'],'partial exact size');sizes.append(q[1]);continue
        raise ValueError('unsupported partial-link statement '+s)
    need(len(sections)==len(set(sections))==691 and set(sections)==set(m['allocations']) and kept==sections and sizes==sections and set(allowed)==seen,'complete691 sections/KEEP/assert and53 actual assignments')
def run():
    need(sha(RUNNER)=='b26410ae9a0d9dece3e5404fb311407dd7c3022a08a7d2fb8c8df7834496c854','frozen actual integration runner')
    need(sha(MODEL/'source-manifest.json')=='d952159ab2bf7c5294bc433510b88a7c19b23295ba11b0e7ab3d4a1ed39b1ce7','portable source manifest')
    m=read(MODEL/'source-manifest.json');p=read(PLAN)
    need(m['selected_sections']==p['selected_sections'] and m['section_relative_bindings']==p['section_relative_bindings'],'actual selected source/bindings match independent plan')
    need(m['source_units']==['experiments/tsl9-v4160-startup/'+u['path'] for u in p['transitive_source_units']],'34 actual baseline source units')
    need(sha(MODEL/'original-image-layout.ld')==m['layout_sha256']=='651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b','full original691 layout unchanged')
    pinned={str((R/n).resolve()):pin for n,pin in m['source_files'].items()}
    for name,pin in pinned.items():need(sha(Path(name))==pin,'actual original/typed source and header pin')
    results=[]
    for mode,pin in [('c','64f7e9f24a0cf1a9ac7fce09f4b5879f30ba9e55042f582509b3228d00a8a068'),('cpp','1d508a329b5360cb764c51c1b4f2964df288f9313b47bf7343d5cc78a6e316e9')]:
        folder=BUILD/mode;receipt=folder/'verification.json';need(sha(receipt)==pin,'actual final build receipt')
        r=read(receipt);need(r['runner_sha256']==sha(RUNNER) and r['source_files']==m['source_files'] and r['manifest_sha256']==sha(MODEL/'source-manifest.json'),'receipt actual runner/source closure')
        for name,row in r['artifacts'].items():
            path=(folder/name).resolve();need(path.is_relative_to(folder.resolve()) and path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'actual artifact/log readback')
        for t in r['tools'].values():need(sha(Path(t['path']))==t['sha256'],'actual local LLVM executable pin')
        generated={};groups={}
        for s in m['selected_sections']:groups.setdefault(s['producer'],[]).append(s)
        for name,rows in groups.items():
            original=R/name;filtered=folder/'filtered'/original.name
            need(filtered.read_bytes()==projection(original.read_bytes(),rows),'only exact old selected assembly blocks removed')
            generated[str(filtered.resolve())]=sha(filtered)
        for name,is_main in [('main',True),('helpers',False)]:
            ad=folder/(name+'-adapter.h');rows=[s for s in m['selected_sections'] if (s['bytes']==144)==is_main]
            need(ad.read_text(encoding='utf-8')==adapter(rows).decode(),'generated adapter declarations/true sameTU aliases; native newline convention')
            generated[str(ad.resolve())]=sha(ad)
        script_check(folder/'canonical53.ld',m)
        dpaths=list(folder.glob('*.d'));need(len(dpaths)==36,'36 actual compiler dependency rules')
        used=set();usedgenerated=set()
        for dep in dpaths:
            text=dep.read_text().replace('\\\n',' ');need(': ' in text,'Make dependency separator')
            tokens=text.split(': ',1)[1].split()
            for token in tokens:
                path=Path(token).resolve();key=str(path);need(key in pinned or key in generated,'no unpinned native source/header dependency')
                if key in pinned:need(sha(path)==pinned[key],'actual compiler dependency pin');used.add(key)
                else:need(sha(path)==generated[key],'actual generated dependency pin');usedgenerated.add(key)
        need(len(used)==71 and usedgenerated==set(generated),'71 actual native files/four generated inputs')
        commands=r['commands'];need(len(commands)==44,'44 actual compiler/link/export commands')
        labels={c['label']:c for c in commands};need(len(labels)==44,'unique actual command labels')
        for c in commands:
            need(sha(folder/c['log'])==c['log_sha256'],'command log provenance')
            argv=c['argv']
            if '-o' in argv:output=Path(argv[argv.index('-o')+1]).resolve()
            else:
                need(c['label']=='export-new-offline-image' and argv[1:3]==['-O','binary'],'only objcopy uses positional output')
                output=Path(argv[-1]).resolve()
            need(output.is_relative_to(folder.resolve()),'all outputs fresh build folder')
            for arg in argv:
                if arg.endswith('.o'):
                    q=Path(arg);q=q if q.is_absolute() else folder/q
                    need(q.resolve().is_relative_to(folder.resolve()),'no historical carrier object as build input')
        for name in m['source_units']:
            src=R/name;actual=folder/'filtered'/src.name if name in groups else src;c=labels['compile-'+src.stem];argv=c['argv']
            need(Path(argv[argv.index('-c')+1]).resolve()==actual.resolve(),'all34 compile true selected original source inputs')
            need('-MMD' in argv and '-ffreestanding' in argv and '-fno-builtin' in argv and '-march=rv32imac' in argv,'baseline source compile options')
            need(argv[argv.index('-x')+1]==('c' if mode=='c' else 'c++') and ('-std=c11' if mode=='c' else '-std=c++17') in argv,'actual baseline language')
        for unit,src in [('main','interrupt_callframe.c'),('helpers','rcc_helpers.c')]:
            for suffix in ['object','IR']:
                c=labels['typed-'+unit+'-'+suffix];argv=c['argv'];source=R/'experiments/tsl9-v4160-irq-callframe/src'/src
                need(str(source) in argv and '-include' in argv and Path(argv[argv.index('-include')+1]).resolve()==(folder/(unit+'-adapter.h')).resolve(),'typed core with only controlled adapter')
        strict=labels['strict-final-link'];log=(folder/strict['log']).read_text();need(strict['exit']!=0 and set(re.findall(r'undefined symbol: (\w+)',log))=={'__tsl9v4160_rom_entry'} and not (folder/'STRICT-MISSING-ROM.elf').exists(),'actual strict link sole missingROM')
        results.append(dict(mode=mode,receipt_sha256=pin,artifacts_checked=len(r['artifacts']),dependency_rules=36,pinned_native_dependencies=71,generated_inputs=generated,actual_commands=44,carrier_compile_TUs=34,typed_compile_TUs=2,partial_bindings=53,strict_ROM_rejection_confirmed=True))
    return dict(schema='TSL9-independent-source-integration-provenance-review-v1',passed=True,runner_sha256=sha(RUNNER),manifest_sha256=sha(MODEL/'source-manifest.json'),prepare_manifest_sha256=sha(MODEL/'prepare_manifest.py'),modes=results,
       limits=dict(no_fresh_compilation_by_reviewer=True,system_headers_excluded_by_MMD=True,target_execution=False,network=False,hardware=False,new_BIN_by_reviewer=False,asynchronous_equivalence=False,flashable=False))
if __name__=='__main__':
    r=run();out=H/'source-provenance.json'
    if out.exists():need(read(out)==r,'readonly source-provenance replay exact')
    else:out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,modes=2,actual_commands_per_mode=44,dependency_rules_per_mode=36,sha256=sha(out))))
