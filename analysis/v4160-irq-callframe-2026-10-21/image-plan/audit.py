"""Read-only carrier/source integration plan; never link or generate an image."""
from pathlib import Path
import hashlib,importlib.util,json,re,collections
H=Path(__file__).resolve().parent;R=H.parents[2];S=R/'experiments/tsl9-v4160-startup'
BASE='experiments/tsl9-v4160-startup/build/image-fidelity-999d8125159a4d80bd6df9153f267002/'
PARSER='apk-analysis/tsl9-v4160-reset-memory-2026-10-21/compiler-review/elf32.py'
sp=importlib.util.spec_from_file_location('bounded',R/PARSER);E=importlib.util.module_from_spec(sp);sp.loader.exec_module(E)
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
NAMES={'.text.tsl9v4160.init_9a42':(0x9a42,144,'__tsl9v4160_call_9a42','tsl9_rebuild_interrupt_registers_9a42'),**{'.text.tsl9v4160.frontier_'+a:(int(a,16),30,'__tsl9v4160_call_'+a,'tsl9_rebuild_rcc_registers_'+a) for a in ['19124','19142','19160','1917e']}}
def role(e,s):return dict(name=s['name'],owner=e.sections[s['index']]['name'] if s['index'] not in (0,0xfff1) else ('UND' if not s['index'] else 'ABS'),offset=s['value'],bytes=s['size'],info=s['info'],other=s['other'])
def relocation(e,r):return dict(owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend'],symbol=role(e,r['symbol']))
def source_labels(path):
    text=path.read_text();asm=''.join(json.loads(x.strip()) for x in text.splitlines() if x.strip().startswith('"'))
    blocks={}
    for block in re.split(r'(?=^\.section )',asm,flags=re.M):
        if not block.startswith('.section '):continue
        name=block.split(',',1)[0].split(' ',1)[1]
        if name not in NAMES:continue
        start=NAMES[name][0];labels=[]
        for label in re.findall(r'^([\w.$]+):$',block,re.M):
            match=re.fullmatch(r'\.L(?:init|frontier)_([0-9a-f]+)',label)
            labels.append(dict(name=label,offset=int(match[1],16)-start if match else 0,kind='instruction' if match else 'entry'))
        blocks[name]=dict(producer=path.relative_to(R).as_posix(),labels=labels,assembly_sha256=hashlib.sha256(block.encode()).hexdigest())
    return blocks
def run():
    refs=[PARSER,'exports/v4160-image-fidelity-stage.json',BASE+'verification.json',BASE+'c/source-image-merged.o',BASE+'c/ADDRESS-WITNESS-ONLY.elf',BASE+'original-image-layout.ld',
      'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
      'experiments/tsl9-v4160-startup/verify-image-fidelity.py','experiments/tsl9-v4160-startup/verify-extension.py',
      'experiments/tsl9-v4160-startup/src/initialization_native.c','experiments/tsl9-v4160-startup/src/frontier_native.c',
      'apk-analysis/tsl9-v4160-core-flow-2026-10-20/initialization-review/generate-native.py',
      'apk-analysis/tsl9-v4160-frontier-2026-10-20/native/generate-frontier.py','scripts/stage-v4160-frontier.py','scripts/stage-v4160-image-fidelity.py',
      'experiments/tsl9-v4160-irq-callframe/src/interrupt_callframe.c','experiments/tsl9-v4160-irq-callframe/src/callframe_io.h','experiments/tsl9-v4160-irq-callframe/src/rcc_helpers.c',
      'experiments/tsl9-v4160-irq-native/src/native_io.h','experiments/tsl9-v4160-interrupt-registers/src/interrupt_registers.h']
    stage=json.loads((R/refs[1]).read_text());need(stage['integrated_sha256']==sha(R/refs[3])=='646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97','authoritative carrier pin')
    need(stage['receipt_sha256']==sha(R/refs[2])=='2e6585594c1b02de058e2fbb5838f591a5915efed7bc461b9083e99a2e97b8bd','authoritative full receipt')
    need(sha(R/refs[5])=='651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b','full691 layout pin')
    receipt=json.loads((R/refs[2]).read_text());alloc=receipt['allocations'];e=E.ELF(R/refs[3]);linked=E.ELF(R/refs[4]);original=(R/refs[6]).read_bytes()
    need(hashlib.sha256(original).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','original pin')
    allalloc=[s for s in e.sections if s['flags']&2 and s['size']];need(len(allalloc)==691 and len(e.relocations)==8280,'carrier691/8280')
    und=[role(e,s) for s in e.symbols if s['name'] and s['index']==0];need([s['name'] for s in und]==['__tsl9v4160_rom_entry'],'sole true ROM UND')
    sections=[];indices={e.byname[n]['index'] for n in NAMES}
    labels=source_labels(S/'src/initialization_native.c')|source_labels(S/'src/frontier_native.c');need(set(labels)==set(NAMES),'two actual producers cover five')
    layout=(R/refs[5]).read_text();need(layout.count('ASSERT(SIZEOF(')==691,'all691 size assertions')
    for name,(va,size,alias,public) in NAMES.items():
        q=e.byname[name];need(q['size']==size and q['alignment']==2 and q['type']==1 and q['flags']==6,'selected original storage role')
        need(e.data(q)==original[va-0x8000:va-0x8000+size] and linked.byname[name]['address']==va,'selected storage bytes and original VAs')
        syms=[role(e,s) for s in e.symbols if s['index']==q['index']]
        need(any(s['name']==alias and s['offset']==0 and s['bytes']==size and s['info']==18 for s in syms),'actual original global FUNC alias')
        need(re.search(re.escape(name)+r' '+hex(va)+r' :',layout) is not None and 'ASSERT(SIZEOF('+name+')=='+str(size) in layout,'exact original section binding')
        sections.append(dict(name=name,originalVA=va,bytes=size,global_alias=alias,new_C_symbol=public,symbol_roles=syms,**labels[name]))
    need(sum(len(x['symbol_roles']) for x in sections)==19,'19 actual selected symbol records')
    need(sum(sum(l['kind']=='instruction' for l in x['labels']) for x in sections)==94,'all94 original source labels')
    outgoing=[relocation(e,r) for r in e.relocations if r['owner'] in NAMES]
    incoming=[relocation(e,r) for r in e.relocations if r['owner'] not in NAMES and r['symbol']['index'] in indices]
    retained=[relocation(e,r) for r in e.relocations if r['owner'] not in NAMES]
    retained_global_roles=[role(e,s) for s in e.symbols if s['name'] and s['info']>>4 in (1,2) and s['index'] not in indices]
    need(len(outgoing)==10 and collections.Counter(r['type'] for r in outgoing)=={17:6,44:4},'old six calls/four branch RELA')
    need(len(incoming)==8 and all(r['type']==17 and r['addend']==0 and r['symbol']['offset']==0 for r in incoming),'eight external entry JAL bindings')
    need(len(retained)==8270,'all8270 outside-owned RELA retained')
    retainedsections=[dict(name=q['name'],type=q['type'],flags=q['flags'],alignment=q['alignment'],bytes=q['size'],sha256=hashlib.sha256(e.data(q) if q['type']!=8 else b'').hexdigest()) for q in allalloc if q['name'] not in NAMES]
    need(len(retainedsections)==686,'686 retained allocations')
    chain=[];source_union={};p=R/refs[2]
    while True:
        d=json.loads(p.read_text());chain.append(dict(path=p.relative_to(R).as_posix(),sha256=sha(p)))
        for n,h in d.get('source_files',{}).items():
            n=n.replace('\\','/');need(n not in source_union or source_union[n]==h,'consistent inherited producer pins');source_union[n]=h
        if not d.get('baseline_receipt'):break
        p=Path(d['baseline_receipt']);need(p.resolve().is_relative_to(S.resolve()) and len(chain)<40,'bounded original receipt chain')
    units=sorted(n for n in source_union if n.endswith(('.c','.S')));need(len(units)==34 and len(chain)==13,'actual34unit/13receipt lineage')
    for n,h in source_union.items():need(sha(S/n)==h,'all inherited source pins current')
    unit_inventory=[];declarations=[]
    for n in units:
        text=(S/n).read_text();asm=''.join(json.loads(x.strip()) for x in text.splitlines() if x.strip().startswith('"'))
        an=re.findall(r'^\.(?:section|pushsection)\s+([^,\s]+)',asm,re.M)
        cn=re.findall(r'section\("([^"]+)"\)',text)
        mn=['.rodata.tsl9v4160.finite_data_'+v for v in re.findall(r'^ORIGINAL_RO\((\w+)\)',text,re.M)]
        names=an+cn+mn;declarations+=names
        unit_inventory.append(dict(path=n,sha256=source_union[n],assembly_sections=an,C_attribute_sections=cn,finite_macro_sections=mn,sections=len(names)))
    need(len(declarations)==len(set(declarations))==691 and set(declarations)==set(alloc),'34units declare exact691 allocations once each')
    ranges=sorted((s['originalVA'],s['originalVA']+s['bytes']) for s in alloc.values() if s['kind']!='RAM')
    need(len(ranges)==690 and ranges[0][0]==0x8000 and ranges[-1][1]==0x1ac00 and all(a[1]==b[0] for a,b in zip(ranges,ranges[1:])),'690 source extents no gaps/overlaps')
    need(sum(b-a for a,b in ranges)==76800,'all76800 bytes section-backed before filtering')
    binding_paths=[]
    for c in chain:
        for name in ['actual-RAM-views.ld','real-RAM-view.ld']:
            p=(R/c['path']).parent/name
            if p.is_file():binding_paths.append(p)
    binding_paths += [S/'layout'/n for n in ['vector-ram-views.ld','callback-address-bindings.ld','retained-data-addresses.ld']]
    bindings=[];allnamed={s['name']:s for s in e.symbols if s['name']}
    for path in binding_paths:
        refs.append(path.relative_to(R).as_posix());owner=None
        for lineno,line in enumerate(path.read_text().splitlines(),1):
            section=re.search(r'(\.[\w.]+)\s+0(?:\s+\(NOLOAD\))?\s*:\s*\{',line)
            if section:owner=section[1]
            match=re.match(r'\s*(\w+)\s*=\s*([^;]+);',line)
            if not match:continue
            name,expr=match.groups();sym=allnamed[name];actual=role(e,sym)
            need(actual['owner']==owner and actual['info']==16 and actual['bytes']==0 and actual['other']==0,'actual section-relative zero-size global NOTYPE binding')
            if expr.startswith('__tsl9v4160_ram + '):expected=int(expr.split('+')[1].strip(),0)
            else:
                need(expr.startswith('. + '),'only source-proven relative-label expression');expected=int(expr.split('+')[1].strip(),0)
            need(actual['offset']==expected,'binding exact owner-relative offset')
            bindings.append(dict(name=name,script=path.relative_to(R).as_posix(),line=lineno,expression=expr,role=actual))
    need(len(binding_paths)==7 and len(bindings)==len({b['name'] for b in bindings})==53,'exact7scripts53distinctbindings')
    probes=[]
    for mode,folder in [('c','probe-c2143004802448d0b154369ba6e22de7-c'),('cpp','probe-483f607c01574e199941d1f5070265ef-cpp')]:
        base='experiments/tsl9-v4160-irq-callframe/build/'+folder+'/'
        refs += [base+n for n in ['probe.json','main.o','helpers.o','COMPONENT-ONLY-NOT-FIRMWARE.elf']]
        elf=E.ELF(R/(base+'COMPONENT-ONLY-NOT-FIRMWARE.elf'));main=E.ELF(R/(base+'main.o'));helper=E.ELF(R/(base+'helpers.o'))
        diffs=[]
        for name,(va,size,alias,public) in NAMES.items():
            f=next(s for s in elf.symbols if s['name']==public);data=elf.function_bytes(f);need(f['value']==va and len(data)==size,'five fixed native probe extents')
            diffs += [dict(address=va+i,original=original[va-0x8000+i],native=b) for i,b in enumerate(data) if b!=original[va-0x8000+i]]
        need([x['address'] for x in diffs]==list(range(0x9a44,0x9a4c)),'exact8prologue byte differences')
        need(len(main.relocations)==6 and all(r['type']==17 and r['addend']==0 for r in main.relocations),'six native main JAL relocations')
        need(not helper.relocations,'compiled helper branches already resolved')
        need([r['offset'] for r in main.relocations]==[0x1c,0x28,0x32,0x3c,0x46,0x50],'same six call relocation offsets')
        probes.append(dict(mode=mode,differences=diffs,main_RELA=[relocation(main,r) for r in main.relocations],helper_RELA=[],native_allocations=[dict(name=s['name'],bytes=s['size']) for obj in [main,helper] for s in obj.sections if s['flags']&2 and s['size']]))
    return dict(schema='TSL9-IRQ-callframe-image-integration-plan-v1',passed=True,inputs=[dict(path=n,sha256=sha(R/n)) for n in refs],
       selected_sections=sections,old_selected_RELA=outgoing,external_incoming_RELA=incoming,sole_UND=und,
       retained_allocations=retainedsections,retained_global_symbol_roles=retained_global_roles,retained_RELA_count=8270,retained_RELA_semantic_sha256=digest(sorted(retained,key=lambda x:json.dumps(x,sort_keys=True))),
       receipt_lineage=chain,transitive_source_units=unit_inventory,section_relative_bindings=bindings,source_storage_coverage=dict(allocation_declarations=691,unique_declarations=691,file_backed_extents=690,original_bytes=76800,gaps=0,overlaps=0),
       baseline_compile_profile=['--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x c -std=c11 OR -x c++ -std=c++17','-c'],probes=probes,
       expected_new_RELA=8276,discharged_original_helper_branch_RELA=4,
       expected_difference_bytes=8,expected_difference_range=[0x9a44,0x9a4c],
       limits=dict(plan_only=True,new_merged_object_created=False,new_ELF_linked=False,new_BIN_created=False,whole_image_difference_verified=False,source_files_modified=False,originals_overwritten=False,ISA_execution=False,hardware=False,network=False,computed_interior_entries_excluded=False,flashable=False))
if __name__=='__main__':
    result=run();p=H/'verification.json'
    if p.exists():need(json.loads(p.read_text())==result,'readonly replay exact')
    else:p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,selected=5,retained=686,old_RELA=8280,retained_RELA=8270,new_expected_RELA=8276,incoming=8,source_labels=94,probe_difference_bytes=8,verification_sha256=sha(p))))
