"""Plan-pinned native extension audit; host tools only, no RV32 execution."""
from pathlib import Path
import argparse,collections,hashlib,json,re,runpy,struct,subprocess,sys,uuid

ROOT=Path(__file__).resolve().parent
HOST=runpy.run_path(str(ROOT/'verify.py'))
FLOW=runpy.run_path(str(ROOT/'verify-dependencies.py'))
ELF=HOST['ELF'];need=HOST['need'];BIN=HOST['BIN'];direct_target=FLOW['direct_target']
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--spec',type=Path,default=ROOT/'evidence/table-cases-integration.json')
    ap.add_argument('--firmware',type=Path,default=ROOT.parents[1]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
    ap.add_argument('--baseline-receipt',type=Path)
    args=ap.parse_args();spec_path=args.spec.resolve();spec=json.loads(spec_path.read_text(encoding='utf-8'))
    need(spec['schema']=='ID2966-native-table-extension-spec-v1','Explicit reviewed extension spec')
    def local(name):
        p=(ROOT/name).resolve();need(p.is_relative_to(ROOT),'All source/tool entries stay in this project');return p
    raw=args.firmware.read_bytes();need(len(raw)==76800 and sha(raw)==spec['firmware_sha256']=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Pinned ID2966, no cross-version filling')
    work=ROOT/'build'/('table-extension-'+uuid.uuid4().hex);work.mkdir(parents=True,exist_ok=False)
    cc=BIN/'clang.exe';ld=BIN/'ld.lld.exe'
    def run(argv,folder,label,success=True):
        p=subprocess.run([str(x) for x in argv],cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90,check=False)
        (folder/(label+'.log')).write_bytes(p.stdout);need((p.returncode==0)==success,'Tool result '+label)
        return dict(argv=[str(x) for x in argv],exit=p.returncode,log_sha256=sha(p.stdout)),p.stdout
    if args.baseline_receipt:baseline_path=args.baseline_receipt.resolve()
    else:
        entry=local(spec['baseline_entry']);need(entry.suffix=='.py','Baseline is the declared local host verifier')
        _,output=run([sys.executable,'-X','utf8','-B',entry,'--firmware',args.firmware.resolve()],work,'baseline')
        baseline_path=Path(json.loads(output.decode('utf-8').strip().splitlines()[-1])['receipt'])
    baseline=json.loads(baseline_path.read_text(encoding='utf-8'))
    need(baseline['passed'] and baseline['schema']==spec['baseline_schema'] and baseline['firmware_sha256']==sha(raw),'Reviewed baseline/source identity')
    def check_chain(path,seen):
        path=path.resolve();need(path.is_relative_to(ROOT/'build') and path not in seen,'Retained receipt stays in this build tree, no cycle')
        seen.add(path);row=json.loads(path.read_text(encoding='utf-8'))
        need(row['passed'] and row['firmware_sha256']==sha(raw),'Every retained stage binds source')
        need(all(sha(local(n).read_bytes())==h for n,h in row['source_files'].items()),'Transitive baseline source drift')
        need(all(sha(Path(n).read_bytes())==h for n,h in row['tools'].items()),'Transitive tool drift')
        if 'baseline_receipt' in row:
            prior=Path(row['baseline_receipt']);need(sha(prior.read_bytes())==row['baseline_receipt_sha256'],'Retained baseline digest')
            check_chain(prior,seen)
    check_chain(baseline_path,set())
    sources=[Path(__file__).resolve(),ROOT/'verify.py',ROOT/'verify-dependencies.py',spec_path]
    modules=[];new_sections={};new_symbols={};unknown={};code_views={};cfg_docs={}
    for item in spec['modules']:
        plan_path=local(item['plan']);need(sha(plan_path.read_bytes())==item['plan_sha256'],'Pinned independently reviewed module plan')
        plan=json.loads(plan_path.read_text(encoding='utf-8'));need(plan['source_firmware_sha256']==sha(raw),'Module source digest')
        cfg_path=local(item['cfg_evidence'])
        need(sha(cfg_path.read_bytes())==item['cfg_sha256']==plan['CFG_review_sha256'],'Pinned independent local-CFG evidence')
        source=local(item['source']);header=local(item['header'])
        need(sha(source.read_bytes())==item['source_sha256'] and sha(header.read_bytes())==item['header_sha256'],'Pinned new source/header')
        sources.extend([plan_path,source,header,cfg_path]);modules.append((item,plan))
        cfg_docs[item['name']]=(item,json.loads(cfg_path.read_text(encoding='utf-8')))
        old_storage={**baseline['allocations'],**new_sections}
        for v in plan.get('existing_code_views',[]):
            need(v['name'] not in code_views and v['section'] in old_storage,'Unique view of already captured storage')
            storage=old_storage[v['section']]
            need(storage['kind']=='code' and v['elf_type']==0 and v['size']==0 and 0<=v['offset']<storage['bytes'],'Only NOTYPE0 view, never an implementation')
            need(v['originalVA']==storage['originalVA']+v['offset'],'Exact captured code address')
            owner,proof=cfg_docs[v['boundary_cfg_module']]
            need(owner['cfg_sha256']==v['boundary_cfg_sha256'] and proof['passed'],'Pinned old CFG instruction-boundary evidence')
            graph=next(g for g in proof['graphs'] if g['entry']==v['boundary_root_originalVA'])
            instruction=next(i for i in graph['instructions'] if i['va']==v['originalVA'])
            bits=bytes.fromhex(instruction['raw_hex'])
            need(instruction['raw_hex']==v['boundary_raw_hex'] and len(bits) in (2,4) and v['offset']+len(bits)<=storage['bytes'],'Actual old instruction start, not alignment alone')
            need(raw[v['originalVA']-0x8000:v['originalVA']-0x8000+len(bits)]==bits,'Boundary original bytes')
            code_views[v['name']]=v
        for section in plan['sections']:
            need(section['name'] not in new_sections and section['kind'] in ('code','RO','captured_view'),'Distinct observed code/data storage')
            new_sections[section['name']]=section
        for s in plan['defined_symbols']:
            need(s['name'] not in new_symbols and s['section'] in new_sections,'No new ABS or duplicate implementation')
            new_symbols[s['name']]=s
        for name,row in plan['expected_undefined_symbols'].items():
            need(name not in unknown or unknown[name]['originalVA']==row['originalVA'],'Consistent external address')
            unknown[name]=row
    source_hashes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources}
    need(set(new_symbols)==set(spec['required_providers']),'Exactly the selected entry providers')
    need(set(code_views)==set(spec.get('required_code_views',[])) and not(set(code_views)&set(new_symbols)),'Explicit noncolliding existing-code views')
    base_obj=ELF(Path(baseline['modes']['c']['integrated_object']))
    base_witness=ELF(baseline_path.parent/'c/ADDRESS-WITNESS-ONLY.elf')
    need(sha(base_obj.raw)==baseline['modes']['c']['integrated_sha256'] and sha(base_witness.raw)==baseline['modes']['c']['numeric_witness_sha256'],'Actual reviewed baseline artifacts')
    allocations=dict(baseline['allocations'])
    need(not(set(allocations)&set(new_sections)),'Never replace baseline storage')
    allocations.update({n:dict(s,flags=6 if s['kind']=='code' else 2) for n,s in new_sections.items()})
    ranges=sorted((s['originalVA'],s['originalVA']+s['bytes'],n) for n,s in allocations.items() if s['kind']!='RAM')
    need(all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:])),'All old/new bytes allocated once')
    ram_views=dict(baseline['modes']['c']['RAM_views'])
    observed_ram={n:s['originalVA']-0x20004000 for n,s in unknown.items() if s['role'].startswith('data_address') and 0x20004000<=s['originalVA']<0x2000c958}
    need(all(n not in ram_views or ram_views[n]==o for n,o in observed_ram.items()),'Consistent existing RAM address views')
    added_ram={n:o for n,o in observed_ram.items() if n not in ram_views}
    ram_views.update(added_ram)
    if 'expected_RAM_view_count' in spec:need(len(ram_views)==spec['expected_RAM_view_count'],'Exact reviewed address-only RAM view count')
    prior_und=set(baseline['modes']['c']['undefined_symbols'])
    prior_real={n for n,s in base_obj.symbol.items() if s['index'] not in (0,0xfff1) and base_obj.sections[s['index']]['flags']&2}
    need(not(set(code_views)&prior_real),'Never replace a real prior symbol with a view')
    need(all(n not in prior_real or base_witness.symbol[n]['value']==s['originalVA'] for n,s in unknown.items()),'New references agree with actual prior provider addresses')
    need(all(n in unknown and unknown[n]['originalVA']==v['originalVA'] and unknown[n]['role']=='existing_code_section_relative_view_no_storage' for n,v in code_views.items()),'Views resolve only their declared existing-code dependencies')
    need(all(n not in new_symbols or new_symbols[n]['originalVA']==s['originalVA'] for n,s in unknown.items()),'New cross-module references agree with actual provider addresses')
    remaining=(prior_und|set(unknown))-set(new_symbols)-set(ram_views)-set(code_views)-prior_real
    need(remaining==set(spec['expected_undefined_symbols']),'Explicit unresolved dependency frontier')
    addresses={n:base_witness.symbol[n]['value'] for n in prior_und}
    addresses.update({n:s['originalVA'] for n,s in unknown.items()})
    need(all(addresses[n]==a for n,a in spec['expected_undefined_symbols'].items()),'Original unresolved numeric addresses, not providers')
    layout=work/'original-address-layout.ld'
    text='OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for name,s in sorted(allocations.items(),key=lambda x:x[1]['originalVA']):
        text+=f' {name} {hex(s["originalVA"])}'+(' (NOLOAD)' if s['kind']=='RAM' else '')+f' : {{ KEEP(*({name})) }}\n ASSERT(SIZEOF({name})=={s["bytes"]}, "Original size changed")\n'
    layout.write_text(text+' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n',encoding='utf-8')
    ram_script=work/'actual-RAM-views.ld'
    partial='SECTIONS { .bss.tsl9v4160.ram 0 : { KEEP(*(.bss.tsl9v4160.ram))\n'+''.join(n+' = __tsl9v4160_ram + '+hex(o)+';\n' for n,o in sorted(added_ram.items()))+'}\n'
    grouped_views=collections.defaultdict(list)
    for n,v in sorted(code_views.items()):grouped_views[v['section']].append((n,v))
    for section,rows in sorted(grouped_views.items()):
        partial+=section+' 0 : {\n'+''.join(n+' = . + '+hex(v['offset'])+';\n' for n,v in rows)+'KEEP(*('+section+'))\n}\n'
    ram_script.write_text(partial+'}\n',encoding='utf-8')
    witness_script=work/'ADDRESS-WITNESS-ONLY.ld'
    witness_script.write_text('/* Only unresolved original numbers; NOT code/data implementations. */\n'+''.join(n+' = '+hex(addresses[n])+';\n' for n in sorted(remaining)),encoding='utf-8')
    def normalized(elf,r):
        sym=elf.symbols[r['symbol_index']]
        if sym['index']==0:
            if r['symbol_index']==0:return r['addend']
            need(sym['name'] in addresses or sym['name'] in new_symbols,'Known unresolved address role')
            return (addresses[sym['name']] if sym['name'] in addresses else new_symbols[sym['name']]['originalVA'])+r['addend']
        if sym['index']==0xfff1:return sym['value']+r['addend']
        name=elf.sections[sym['index']]['name'];need(name in allocations,'Actual allocated target section')
        return allocations[name]['originalVA']+sym['value']+r['addend']
    def check_ram(elf):
        ram=elf.symbol['__tsl9v4160_ram'];need(ram['index'] not in (0,0xfff1) and ram['size']==35160,'Single existing RAM provider')
        need(elf.sections[ram['index']]['type']==8 and elf.sections[ram['index']]['size']==35160,'No fabricated RAM values or extra storage')
        for name,offset in ram_views.items():
            v=elf.symbol[name];need(v['index']==ram['index'] and v['type']==0 and v['size']==0 and v['value']-ram['value']==offset,'Section-relative RAM view '+name)
    def check_new_providers(elf,linked=False):
        for name,s in new_symbols.items():
            v=elf.symbol[name];need(v['index']==elf.byname[s['section']]['index'] and v['type']==s['elf_type'] and v['size']==s['size'],'Actual extension provider '+name)
            need(v['value']==(s['originalVA'] if linked else s['originalVA']-new_sections[s['section']]['originalVA']),'Exact extension provider offset '+name)
    def check_code_views(elf,linked=False):
        for n,v in code_views.items():
            sym=elf.symbol[n]
            need(sym['index']==elf.byname[v['section']]['index'] and sym['type']==0 and sym['size']==0 and sym['bind']==1,'Actual section-relative old-code NOTYPE0 view '+n)
            need(sym['value']==(v['originalVA'] if linked else v['offset']),'View does not allocate or replace bytes '+n)
    def check_relative_providers(elf):
        records=collections.defaultdict(list)
        for row in elf.relocations:
            if row['type'] in (35,39):records[(row['section'],row['offset'])].append(row)
        for item,plan in modules:
            for e in plan.get('relative32_expressions',[]):
                rows=records[(e['section'],e['offset'])]
                need(len(rows)==2 and collections.Counter(r['type'] for r in rows)=={35:1,39:1},'Actual merged relative32 pair')
                for row in rows:
                    symbol=elf.symbols[row['symbol_index']]
                    need(symbol['index'] not in (0,0xfff1),'Relative32 operands require actual section-backed providers, never numeric substitutes')
                    section=elf.sections[symbol['index']]['name'];storage=allocations[section]
                    if row['type']==35:
                        need(storage['kind']=='code' and 0<=symbol['value']+row['addend']<storage['bytes'],'ADD target is within captured code storage')
                        need(normalized(elf,row)==e['target_originalVA']+e['target_addend'],'Exact captured target plus addend')
                    else:
                        need(section==e['section'] and normalized(elf,row)==e['base_originalVA']+e['base_addend'],'SUB base belongs to its actual table')
    def inspect_module(elf,plan):
        sections={s['name']:s for s in plan['sections']}
        need(elf.kind==1 and {s['name'] for s in elf.sections if s['flags']&2 and s['size']}==set(sections),'Exact selected extension allocations')
        need({s['name'] for s in elf.symbols if s['name'] and s['index']==0}==set(plan['expected_undefined_symbols']),'Keep every true standalone dependency')
        for s in plan['defined_symbols']:
            v=elf.symbol[s['name']];need(v['index']==elf.byname[s['section']]['index'] and v['value']==s['originalVA']-sections[s['section']]['originalVA'] and v['type']==s['elf_type'] and v['size']==s['size'],'Real module symbol')
        expected=collections.defaultdict(list)
        for e in plan['relocations']:expected[(e['section'],e['offset'])].append(e)
        wanted=collections.Counter((e['section'],e['offset'],e['type_number'],e['target_originalVA']+e['addend']) for e in plan['relocations'])
        actual=collections.Counter((r['section'],r['offset'],r['type'],normalized(elf,r)) for r in elf.relocations)
        need(actual==wanted,'Exact extension relocation semantic multiset, including same-site ADD/SUB')
        for r in elf.relocations:
            sym=elf.symbols[r['symbol_index']]
            if sym['index']==0:
                need(sym['name'] in plan['expected_undefined_symbols'] and any(e['target']==sym['name'] and e['type_number']==r['type'] and e['target_originalVA']+e['addend']==normalized(elf,r) for e in expected[(r['section'],r['offset'])]),'Unresolved target name/role retained')
        expressions={}
        for e in plan.get('relative32_expressions',[]):
            key=(e['section'],e['offset']);need(key not in expressions,'One expression per word, never duplicate providers')
            need(e['section'] in sections and sections[e['section']]['kind']=='RO' and e['offset']%4==0 and 0<=e['offset']<=sections[e['section']]['bytes']-4,'Bounded relative32 RO word')
            need(e['initial_u32']==0,'Canonical symbolic table has zero initial word, not copied encoded delta')
            rows=expected[key]
            need(len(rows)==2 and collections.Counter(x['type_number'] for x in rows)=={35:1,39:1},'Exactly one ADD32 and one SUB32 at this word')
            add=next(x for x in rows if x['type_number']==35);sub=next(x for x in rows if x['type_number']==39)
            need((add['target'],add['target_originalVA'],add['addend'])==(e['target_symbol'],e['target_originalVA'],e['target_addend']),'Exact ADD target/addend')
            need((sub['target'],sub['target_originalVA'],sub['addend'])==(e['base_symbol'],e['base_originalVA'],e['base_addend']),'Exact SUB base/addend')
            result=(e['initial_u32']+add['target_originalVA']+add['addend']-sub['target_originalVA']-sub['addend'])&0xffffffff
            pc=sections[e['section']]['originalVA']+e['offset'];original=struct.unpack_from('<I',raw,pc-0x8000)[0]
            need(result==e['original_u32']==original,'Relative32 expression equals original encoded word modulo 2^32')
            expressions[key]=e
        need({(r['section'],r['offset']) for r in plan['relocations'] if r['type_number'] in (35,39)}==set(expressions),'Every ADD/SUB word has a reviewed complete expression')
        for section in {name for name,offset in expressions}:
            need(sections[section]['bytes']%4==0 and {offset for name,offset in expressions if name==section}==set(range(0,sections[section]['bytes'],4)),'Every word of each captured relative table has its expression')
        for name,s in sections.items():
            b=raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']]
            need(len(b)==s['bytes'] and sha(b)==s['sha256'],'Pinned original code/data view')
            initial=bytearray(b)
            for (section,offset),e in expressions.items():
                if section==name:struct.pack_into('<I',initial,offset,e['initial_u32'])
            need(elf.byname[name]['data']==initial,'Exact unlinked bytes, with explicit relative32 initial words')
            if s['kind']!='code':continue
            offset=0
            while offset<s['bytes']:
                half=struct.unpack_from('<H',b,offset)[0];width=4 if half&3==3 else 2
                need(offset+width<=s['bytes'],'No truncated native instruction')
                target=direct_target(s['originalVA']+offset,width,int.from_bytes(b[offset:offset+width],'little'))
                if target:need(any((e['type_number'],e['target_originalVA']+e['addend'])==target for e in expected[(name,offset)]),'Every direct control transfer has exact provider-plus-addend relocation')
                offset+=width
    counts=dict(code_bytes=sum(s['bytes'] for s in allocations.values() if s['kind']=='code'),RO_bytes=sum(s['bytes'] for s in allocations.values() if s['kind']!='code' and s['kind']!='RAM'),allocation_sections=len(allocations),relocations=baseline['modes']['c']['relocations']+sum(len(p['relocations']) for _,p in modules))
    need(all(counts[n]==v for n,v in spec['expected_counts'].items()),'Reviewed exact integration scope')
    need(sum(len(p.get('relative32_expressions',[])) for _,p in modules)==spec['expected_relative32_expression_count'],'Exact independently reviewed relative32 scope')
    modes={}
    for mode,language,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();commands=[];objects=[];relative_countercases=[]
        for item,plan in modules:
            obj=folder/(item['name']+'.o')
            cmd,_=run([cc,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-stack-protector','-fno-builtin','-Wall','-Wextra','-Werror','-x',language,'-std='+std,'-c',local(item['source']),'-o',obj],folder,'compile-'+item['name']);commands.append(cmd)
            module_elf=ELF(obj);inspect_module(module_elf,plan);objects.append(obj)
            if plan.get('relative32_expressions'):
                e=plan['relative32_expressions'][0]
                bad=bytearray(module_elf.raw);section=module_elf.byname[e['section']]
                need(e['original_u32']!=e['initial_u32'],'Nontrivial actual encoded-delta countercase')
                struct.pack_into('<I',bad,section['offset']+e['offset'],e['original_u32'])
                counter=folder/(item['name']+'-COUNTERCASE-double-encoded.o');counter.write_bytes(bad)
                rejected=False;reason=''
                try:inspect_module(ELF(counter),plan)
                except AssertionError as error:rejected=True;reason=str(error)
                need(rejected,'Same module gate rejects actual raw-delta initial word')
                relative_countercases.append(dict(kind='raw_delta_initial_word',path=str(counter),sha256=sha(counter.read_bytes()),rejected=True,reason=reason))
                bad=bytearray(module_elf.raw);changed=False
                for table in module_elf.sections:
                    if table['type']!=4 or table['info']!=section['index']:continue
                    for offset in range(0,table['size'],12):
                        site,info=struct.unpack_from('<II',table['data'],offset)
                        if site==e['offset'] and info&255==39:
                            struct.pack_into('<I',bad,table['offset']+offset+4,(info&~255)|35);changed=True
                need(changed,'Actual SUB32 record selected')
                counter=folder/(item['name']+'-COUNTERCASE-SUB-to-ADD.o');counter.write_bytes(bad)
                rejected=False;reason=''
                try:inspect_module(ELF(counter),plan)
                except AssertionError as error:rejected=True;reason=str(error)
                need(rejected,'Same module gate rejects actual changed relocation multiset')
                relative_countercases.append(dict(kind='SUB32_changed_to_ADD32',path=str(counter),sha256=sha(counter.read_bytes()),rejected=True,reason=reason))
        prior_path=Path(baseline['modes'][mode]['integrated_object']);need(sha(prior_path.read_bytes())==baseline['modes'][mode]['integrated_sha256'],'Actual prior object digest')
        prior=ELF(prior_path);integrated=folder/'native-extension.o'
        cmd,_=run([ld,'-r','--no-relax','-T',ram_script,prior_path,*objects,'-o',integrated],folder,'integrate-actual-providers');commands.append(cmd)
        merged=ELF(integrated);check_ram(merged);check_new_providers(merged);check_code_views(merged);check_relative_providers(merged)
        need({s['name'] for s in merged.sections if s['flags']&2 and s['size']}==set(allocations),'No added code-view storage')
        need(len(merged.relocations)==counts['relocations'],'All old/new relocations retained')
        old=collections.Counter((r['section'],r['offset'],r['type'],normalized(prior,r)) for r in prior.relocations)
        current=collections.Counter((r['section'],r['offset'],r['type'],normalized(merged,r)) for r in merged.relocations)
        need(not(old-current),'Every prior semantic relocation preserved with multiplicity')
        for section in prior.sections:
            if section['flags']&2 and section['size']:
                now=merged.byname[section['name']];need(now['type']==section['type'] and now['size']==section['size'] and now['data']==section['data'],'All prior original storage preserved')
        for name,s in prior.symbol.items():
            # ELF local mapping symbols ($d.0, etc.) may repeat across objects;
            # a name-indexed table does not identify them uniquely. Their storage
            # and references are checked above; only external providers/views
            # have a unique exported-name identity here.
            if s['bind']==0 or s['index'] in (0,0xfff1) or not(prior.sections[s['index']]['flags']&2):continue
            now=merged.symbol[name];need(now['index']==merged.byname[prior.sections[s['index']]['name']]['index'] and (now['type'],now['size'],now['value'])==(s['type'],s['size'],s['value']),'Every prior real provider/view preserved')
        need({s['name'] for s in merged.symbols if s['name'] and s['index']==0}==remaining,'Explicit true dependency frontier')
        strict=folder/'strict-incomplete.elf'
        cmd,log=run([ld,'--no-relax','--error-limit=0','-T',layout,integrated,'-o',strict],folder,'strict-final-link',False);commands.append(cmd)
        need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',log.decode('utf-8','replace')))==remaining,'Strict unresolved dependencies are fatal, no ELF')
        witness=folder/'ADDRESS-WITNESS-ONLY.elf'
        cmd,_=run([ld,'--no-relax','-T',layout,'-T',witness_script,integrated,'-o',witness],folder,'numeric-address-witness');commands.append(cmd)
        linked=ELF(witness);check_ram(linked);check_new_providers(linked,True);check_code_views(linked,True)
        need({s['name'] for s in linked.sections if s['flags']&2 and s['size']}==set(allocations),'No hidden code/data/stack storage')
        for name,s in allocations.items():
            section=linked.byname[name];need(section['address']==s['originalVA'] and section['size']==s['bytes'],'Exact original allocation address/size')
            if s['kind']!='RAM':need(section['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'All allocated source bytes exact')
        # Genuine ELF mutation must be rejected by the same provider gate.
        bad=bytearray(merged.raw);chosen=sorted(new_symbols)[0];changed=False
        for table in merged.sections:
            if table['type']!=2:continue
            strings=merged.sections[table['link']]['data']
            for off in range(0,table['size'],16):
                at=struct.unpack_from('<I',table['data'],off)[0];name=strings[at:strings.index(0,at)].decode('ascii')
                if name==chosen:struct.pack_into('<H',bad,table['offset']+off+14,0xfff1);changed=True
        need(changed,'Actual provider countercase selected')
        counter=folder/'COUNTERCASE-ABS-provider.o';counter.write_bytes(bad);rejected=False
        try:check_new_providers(ELF(counter))
        except AssertionError:rejected=True
        need(rejected,'Same provider gate rejects actual ABS substitution')
        code_view_negative=None
        if code_views:
            chosen=sorted(code_views)[0];bad=bytearray(merged.raw);changed=False
            for table in merged.sections:
                if table['type']!=2:continue
                strings=merged.sections[table['link']]['data']
                for offset in range(0,table['size'],16):
                    at=struct.unpack_from('<I',table['data'],offset)[0]
                    if strings[at:strings.index(0,at)].decode('ascii')==chosen:
                        struct.pack_into('<H',bad,table['offset']+offset+14,0xfff1);changed=True
            need(changed,'Actual existing-code view selected')
            counter=folder/'COUNTERCASE-ABS-existing-code-view.o';counter.write_bytes(bad);rejected=False
            try:check_code_views(ELF(counter))
            except AssertionError:rejected=True
            need(rejected,'Same old-code view gate rejects actual ABS substitution')
            code_view_negative=dict(symbol=chosen,path=str(counter),sha256=sha(counter.read_bytes()),rejected=True)
        modes[mode]=dict(passed=True,commands=commands,integrated_object=str(integrated),integrated_sha256=sha(integrated.read_bytes()),numeric_witness_sha256=sha(witness.read_bytes()),undefined_symbols=sorted(remaining),RAM_views=ram_views,RAM_NOBITS_bytes=35160,strict_rejected=True,ABS_provider_countercase_rejected=True,relative32_actual_countercases=relative_countercases,existing_code_view_ABS_countercase=code_view_negative,**counts)
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256'] and modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256'],'C/C++ objects and witnesses byte-equal')
    need(source_hashes=={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources},'Source unchanged during verification')
    report=dict(schema='ID2966-native-table-extension-v1',extension_name=spec['name'],passed=True,firmware_sha256=sha(raw),source_files=source_hashes,tools={str(p):sha(p.read_bytes()) for p in [cc,ld]},baseline_receipt=str(baseline_path),baseline_receipt_sha256=sha(baseline_path.read_bytes()),allocations=allocations,new_providers=new_symbols,existing_code_views=code_views,relative32_expression_count=sum(len(p.get('relative32_expressions',[])) for _,p in modules),modes=modes,all_runtime_pointer_targets_proved=False,IRQ_ABI_proved=False,firmware_executed=False,emulation=False,network=False,hardware=False,target_ready=False,ota_verified=False,native_bin=False)
    receipt=work/'verification.json';receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,**counts,remaining_undefined=len(remaining),receipt=str(receipt),native_bin=False)))

if __name__=='__main__':main()
