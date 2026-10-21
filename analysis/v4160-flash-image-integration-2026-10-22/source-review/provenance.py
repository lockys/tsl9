"""Read actual compilation provenance and MMD rules; never launch a command."""
from pathlib import Path
import hashlib
import json
import re
import shlex

def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dependency_rule(text,argv,primary):
    text=text.replace('\\\r\n','').replace('\\\n','');target,body=text.split(': ',1)
    need(shlex.split(target,posix=True)==[argv[argv.index('-MT')+1]] and argv[argv.index('-MT')+1]==Path(argv[argv.index('-o')+1]).name,'Dependency target matches its actual object command')
    dependencies={Path(x).resolve(strict=True) for x in shlex.split(body,posix=True)}
    need(primary.resolve() in dependencies,'Each MMD rule contains its own primary source')
    if '-include' in argv:need(Path(argv[argv.index('-include')+1]).resolve() in dependencies,'Each typed MMD rule contains its own injected adapter')
    return dependencies
def inspect(root,folder,r,c):
    root=Path(root).resolve();folder=Path(folder).resolve()
    manifest=c['new_manifest'];module_root=Path(__file__).resolve().parent
    need(r['passed'] and r['mode'] in ('c','cpp') and r['source_files']==manifest['source_files'],'Actual source receipt and all76 input pins')
    need(r['runner_sha256']==sha(module_root.parent/'implementation/verify_image.py'),'Receipt uses current producer runner')
    for name,pin in r['artifacts'].items():
        p=(folder/name).resolve(strict=True);p.relative_to(folder.resolve());need(sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes'],'Actual artifact/log/dependency hash '+name)
    tools={k:Path(v['path']).resolve(strict=True) for k,v in r['tools'].items()};need(set(tools)=={'clang','linker','objcopy'},'Exactly declared LLVM host tools')
    for key,p in tools.items():need(sha(p)==r['tools'][key]['sha256'],'Actual host tool fingerprint')
    for name,pin in r['input_stability_pins'].items():need(sha(Path(name))==pin,'Actual current source/proof/tool snapshot')
    commands=r['commands'];need(len(commands)==56 and len({x['label'] for x in commands})==56,'All56 unique actual compile/IR/link/export commands')
    by={x['label']:x for x in commands};compiles=[x for x in commands if '-c' in x['argv']];need(len(compiles)==42,'Exactly42 native object compilation commands')
    typed=['main','helpers','flash-quarter','flash-status','flash-unlock','flash-lock','flash-erase','flash-program']
    wanted={'compile-'+Path(n).stem for n in manifest['source_units']}|{'typed-'+label+'-'+kind for label in typed for kind in ('object','IR')}|{'merge-raw-carriers','merge-typed','merge-source-integrated','strict-final-link','numeric-witness-final-link','export-new-offline-image'}
    need(set(by)==wanted,'Exact34 carrier/eight typed/two final-link recipes')
    for row in commands:
        need(Path(row['argv'][0]).resolve()==tools['clang' if row['label'].startswith(('compile-','typed-')) else 'objcopy' if row['label']=='export-new-offline-image' else 'linker'],'Actual command tool matches stage')
        need(sha(folder/row['log'])==row['log_sha256'],'Actual command output log')
        need(row['exit']!=0 if row['label']=='strict-final-link' else row['exit']==0,'Only missing-ROM strict link fails')
    filtered={x['producer'] for x in c['selected']};generated_expected={'filtered/'+Path(x).name for x in filtered}|{label+'-adapter.h' for label in typed}
    source_by_label={}
    for name in manifest['source_units']:
        original=root/name;path=folder/'filtered'/original.name if name in filtered else original;label='compile-'+original.stem
        source_by_label[label]=path
        need(Path(by[label]['argv'][by[label]['argv'].index('-c')+1]).resolve()==path.resolve(),'Each raw command compiles its exact source interval')
        e=c['E'](folder/('carrier-'+original.stem+'.o'))
        need(not set(c['names'])&set(s['name'] for s in e.sections if s['flags']&2 and s['size']),'No selected raw fallback survives in any of34 carrier objects')
    for label in typed:
        expected=root/('experiments/tsl9-v4160-irq-callframe/src/'+('interrupt_callframe.c' if label=='main' else 'rcc_helpers.c')) if label in ('main','helpers') else root/'experiments/tsl9-v4160-flash-entry-order/src/flash_native.c'
        for kind in ('object','IR'):
            command=by['typed-'+label+'-'+kind];argv=command['argv'];action='-c' if kind=='object' else '-emit-llvm';source=Path(argv[argv.index(action)+1])
            need(source.resolve()==expected.resolve(),'Typed object/IR comes from exact readable C source')
            need(Path(argv[argv.index('-include')+1]).resolve()==(folder/(label+'-adapter.h')).resolve(),'Each typed source receives its own adapter')
        source_by_label['typed-'+label+'-object']=expected
    seen=set();generated=set();rules=set()
    for command in compiles:
        argv=command['argv'];need('-MMD' in argv and '-MF' in argv and '-MT' in argv,'EveryactualTU emits project-only dependencies')
        d=Path(argv[argv.index('-MF')+1]).resolve();need(d.parent==folder.resolve() and d not in rules,'Distinct actual dependency file per TU');rules.add(d)
        dependencies=dependency_rule(d.read_text(encoding='utf-8'),argv,source_by_label[command['label']])
        for p in dependencies:
            p.relative_to(root)
            if p.is_relative_to(folder.resolve()):generated.add(p.relative_to(folder).as_posix())
            else:
                name=p.relative_to(root).as_posix();need(name in manifest['source_files'] and sha(p)==manifest['source_files'][name],'Each observed non-system project input is pinned');seen.add(name)
    need(set(folder.glob('*.d'))==rules and len(rules)==42,'Exactly42 actual rule files, no unused substitute')
    need(seen==set(manifest['source_files'])-filtered and len(seen)==72 and generated==generated_expected and len(generated)==12,'Exact72 existing and12 generated observed project inputs')
    own=__import__('importlib.util',fromlist=['spec_from_file_location']);spec=own.spec_from_file_location('independent_filter_check',module_root/'inspect-image.py');gate=own.module_from_spec(spec);spec.loader.exec_module(gate)
    for x in c['filters']:
        source=root/x['path'];actual=folder/'filtered'/source.name;rows=[r for r in c['selected'] if r['producer']==x['path']]
        need(actual.read_bytes()==gate.filter_intervals(source.read_bytes(),rows),'Actual four compiler inputs remove only selected quoted blocks')
    link=str(tools['linker']);model=root/'experiments/tsl9-v4160-flash-image-integration';layout=str(model/'original-image-layout.ld');rom=folder/'NUMERIC-ROM-WITNESS-ONLY.ld'
    need(rom.read_text(encoding='utf-8')=='/* Numeric address only: no ROM bytes/provider/runtime proof. */\n__tsl9v4160_rom_entry = 0x40000;\n','Explicit address-only ROM witness script')
    recipes={
      'merge-raw-carriers':[link,'-r','--no-relax',*[str(folder/('carrier-'+Path(n).stem+'.o')) for n in manifest['source_units']],'-o',str(folder/'raw-carriers.o')],
      'merge-typed':[link,'-r','--no-relax',*[str(folder/(label+'.o')) for label in typed],'-o',str(folder/'typed-providers.o')],
      'merge-source-integrated':[link,'-r','--no-relax','-T',str(folder/'canonical53.ld'),str(folder/'raw-carriers.o'),str(folder/'typed-providers.o'),'-o',str(folder/'source-integrated.o')],
      'strict-final-link':[link,'--no-relax','--error-limit=0','-T',layout,str(folder/'source-integrated.o'),'-o',str(folder/'STRICT-MISSING-ROM.elf')],
      'numeric-witness-final-link':[link,'--no-relax','-T',layout,'-T',str(rom),str(folder/'source-integrated.o'),'-o',str(folder/'ADDRESS-WITNESS-ONLY.elf')],
      'export-new-offline-image':[str(tools['objcopy']),'-O','binary',str(folder/'ADDRESS-WITNESS-ONLY.elf'),str(folder/'NOT-FLASH-VALIDATED-irq-and-flash.bin')]}
    for label,expected in recipes.items():need(by[label]['argv']==expected,'Exact source-object-only link/export recipe, no prebuilt BIN input')
    log=(folder/'strict-final-link.log').read_text(encoding='utf-8');need(set(re.findall(r'undefined symbol: (\w+)',log))=={'__tsl9v4160_rom_entry'} and not (folder/'STRICT-MISSING-ROM.elf').exists(),'Strict missing-ROM failure remains real and inspectable')
    return {'actual_commands':56,'actual_object_TUs':42,'raw_TUs':34,'typed_TUs':8,'dependency_rules':42,'each_rule_target_and_primary_source_bound':True,'observed_existing_project_files':72,'observed_generated_files':12,'compiler_resource_headers_included':False,'strict_ROM_provider_link_passed':False,'target_execution':False}
