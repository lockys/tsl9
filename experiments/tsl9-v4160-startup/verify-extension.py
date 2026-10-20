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
    ap.add_argument('--spec',type=Path,default=ROOT/'evidence/core-flow-integration.json')
    ap.add_argument('--firmware',type=Path,default=ROOT.parents[1]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
    ap.add_argument('--baseline-receipt',type=Path)
    args=ap.parse_args();spec_path=args.spec.resolve();spec=json.loads(spec_path.read_text(encoding='utf-8'))
    need(spec['schema']=='ID2966-native-extension-spec-v1','Explicit reviewed extension spec')
    def local(name):
        p=(ROOT/name).resolve();need(p.is_relative_to(ROOT),'All source/tool entries stay in this project');return p
    raw=args.firmware.read_bytes();need(len(raw)==76800 and sha(raw)==spec['firmware_sha256']=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Pinned ID2966, no cross-version filling')
    work=ROOT/'build'/('extension-'+uuid.uuid4().hex);work.mkdir(parents=True,exist_ok=False)
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
    modules=[];new_sections={};new_symbols={};unknown={}
    for item in spec['modules']:
        plan_path=local(item['plan']);need(sha(plan_path.read_bytes())==item['plan_sha256'],'Pinned independently reviewed module plan')
        plan=json.loads(plan_path.read_text(encoding='utf-8'));need(plan['source_firmware_sha256']==sha(raw),'Module source digest')
        cfg_path=local(item['cfg_evidence'])
        need(sha(cfg_path.read_bytes())==item['cfg_sha256']==plan['CFG_review_sha256'],'Pinned independent local-CFG evidence')
        source=local(item['source']);header=local(item['header'])
        need(sha(source.read_bytes())==item['source_sha256'] and sha(header.read_bytes())==item['header_sha256'],'Pinned new source/header')
        sources.extend([plan_path,source,header,cfg_path]);modules.append((item,plan))
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
    need(all(n not in prior_real or base_witness.symbol[n]['value']==s['originalVA'] for n,s in unknown.items()),'New references agree with actual prior provider addresses')
    need(all(n not in new_symbols or new_symbols[n]['originalVA']==s['originalVA'] for n,s in unknown.items()),'New cross-module references agree with actual provider addresses')
    remaining=(prior_und|set(unknown))-set(new_symbols)-set(ram_views)-prior_real
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
    ram_script.write_text('SECTIONS { .bss.tsl9v4160.ram 0 : { KEEP(*(.bss.tsl9v4160.ram))\n'+''.join(n+' = __tsl9v4160_ram + '+hex(o)+';\n' for n,o in sorted(added_ram.items()))+'} }\n',encoding='utf-8')
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
    def inspect_module(elf,plan):
        sections={s['name']:s for s in plan['sections']}
        need(elf.kind==1 and {s['name'] for s in elf.sections if s['flags']&2 and s['size']}==set(sections),'Exact selected extension allocations')
        need({s['name'] for s in elf.symbols if s['name'] and s['index']==0}==set(plan['expected_undefined_symbols']),'Keep every true standalone dependency')
        for s in plan['defined_symbols']:
            v=elf.symbol[s['name']];need(v['index']==elf.byname[s['section']]['index'] and v['value']==s['originalVA']-sections[s['section']]['originalVA'] and v['type']==s['elf_type'] and v['size']==s['size'],'Real module symbol')
        expected={(r['section'],r['offset']):r for r in plan['relocations']}
        need(len(expected)==len(plan['relocations'])==len(elf.relocations),'Exact extension relocation sites')
        for r in elf.relocations:
            e=expected[(r['section'],r['offset'])];need(r['type']==e['type_number'] and normalized(elf,r)==e['target_originalVA']+e['addend'],'Exact extension relocation role')
            sym=elf.symbols[r['symbol_index']]
            if sym['index']==0:need(sym['name']==e['target'] and sym['name'] in plan['expected_undefined_symbols'],'Unresolved target name/role retained')
        for name,s in sections.items():
            b=raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']]
            need(len(b)==s['bytes'] and sha(b)==s['sha256'] and elf.byname[name]['data']==b,'Pinned extension original bytes')
            if s['kind']!='code':continue
            offset=0
            while offset<s['bytes']:
                half=struct.unpack_from('<H',b,offset)[0];width=4 if half&3==3 else 2
                need(offset+width<=s['bytes'],'No truncated native instruction')
                target=direct_target(s['originalVA']+offset,width,int.from_bytes(b[offset:offset+width],'little'))
                if target:
                    e=expected[(name,offset)];need((e['type_number'],e['target_originalVA'])==target,'Every original direct control transfer has a matching relocation')
                offset+=width
    counts=dict(code_bytes=sum(s['bytes'] for s in allocations.values() if s['kind']=='code'),RO_bytes=sum(s['bytes'] for s in allocations.values() if s['kind']!='code' and s['kind']!='RAM'),allocation_sections=len(allocations),relocations=baseline['modes']['c']['relocations']+sum(len(p['relocations']) for _,p in modules))
    need(all(counts[n]==v for n,v in spec['expected_counts'].items()),'Reviewed exact integration scope')
    modes={}
    for mode,language,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();commands=[];objects=[]
        for item,plan in modules:
            obj=folder/(item['name']+'.o')
            cmd,_=run([cc,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-stack-protector','-fno-builtin','-Wall','-Wextra','-Werror','-x',language,'-std='+std,'-c',local(item['source']),'-o',obj],folder,'compile-'+item['name']);commands.append(cmd)
            inspect_module(ELF(obj),plan);objects.append(obj)
        prior_path=Path(baseline['modes'][mode]['integrated_object']);need(sha(prior_path.read_bytes())==baseline['modes'][mode]['integrated_sha256'],'Actual prior object digest')
        prior=ELF(prior_path);integrated=folder/'native-extension.o'
        cmd,_=run([ld,'-r','--no-relax','-T',ram_script,prior_path,*objects,'-o',integrated],folder,'integrate-actual-providers');commands.append(cmd)
        merged=ELF(integrated);check_ram(merged);check_new_providers(merged)
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
        linked=ELF(witness);check_ram(linked);check_new_providers(linked,True)
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
        modes[mode]=dict(passed=True,commands=commands,integrated_object=str(integrated),integrated_sha256=sha(integrated.read_bytes()),numeric_witness_sha256=sha(witness.read_bytes()),undefined_symbols=sorted(remaining),RAM_views=ram_views,RAM_NOBITS_bytes=35160,strict_rejected=True,ABS_provider_countercase_rejected=True,**counts)
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256'] and modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256'],'C/C++ objects and witnesses byte-equal')
    need(source_hashes=={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources},'Source unchanged during verification')
    report=dict(schema='ID2966-native-extension-v1',extension_name=spec['name'],passed=True,firmware_sha256=sha(raw),source_files=source_hashes,tools={str(p):sha(p.read_bytes()) for p in [cc,ld]},baseline_receipt=str(baseline_path),baseline_receipt_sha256=sha(baseline_path.read_bytes()),allocations=allocations,new_providers=new_symbols,modes=modes,all_runtime_pointer_targets_proved=False,IRQ_ABI_proved=False,firmware_executed=False,emulation=False,network=False,hardware=False,target_ready=False,ota_verified=False,native_bin=False)
    receipt=work/'verification.json';receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,**counts,remaining_undefined=len(remaining),receipt=str(receipt),native_bin=False)))

if __name__=='__main__':main()
