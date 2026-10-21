"""Independent actual source, dependency and ordered recipe readback; never execute."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import sys
sys.dont_write_bytecode=True

OLD_RUNNER='73d3fb0525d5f47c772632a2e397533d86fd3b58e2a26feeecfbd06ddac1bdb1'
REPLY_RUNNER='23b0dfe90a4cde21c8066c2fd318bfd9e19b32ebb758b83eb9f294dc3dae6ee3'
REPLY='.text.tsl9v4160.ota_handler_9b8e'
def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def case(root,name):return next(p for p in (root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def dependency(text,target,primary,adapter):
    text=text.replace('\\\r\n','').replace('\\\n','');left,right=text.split(': ',1);need(shlex.split(left,posix=True)==[target],'Own exact Make target')
    paths=[Path(token).resolve(strict=True) for token in shlex.split(right,posix=True)];need(paths and paths[0]==primary.resolve(),'Own actual primary source first')
    if adapter is not None:need(adapter.resolve() in paths,'Own forced-include adapter present')
    return paths
def profiles(root,firmware,manifest):
    path=case(root,'v4160-register-image-integration-2026-10-22')/'implementation/verify_image.py';need(sha(path)==OLD_RUNNER,'Immutable eight-provider compiler profiles');old=load('twelve_independent_prior_profiles',path);ctx=old.context(root,firmware)
    path=case(root,'v4160-ota-page-reply-2026-10-22')/'implementation/verify_native.py';need(sha(path)==REPLY_RUNNER,'Sealed standalone reply compiler profile');reply=load('twelve_independent_reply_profile',path)
    def units(mode):
        result=old.units(ctx,mode);result.append({'label':'reply','source':root/'experiments/tsl9-v4160-ota-page-reply/src/page_reply.c','flags':reply.flags(mode),'rows':[r for r in manifest['selected_sections'] if r['name']==REPLY]});need(len(result)==9,'Nine explicit typed source units');return result
    return units,ctx['ELF'],ctx['V'].bindings_source
def adapter(rows):
    out='#include <stdint.h>\n#ifdef __cplusplus\nextern "C" {\n#endif\n'
    for row in rows:
        address=row['originalVA'];name=row['new_C_symbol'];arguments='uint32_t a0,uint32_t a1,uint32_t a2' if address==0x9b8e else 'void' if address==0x9a42 else 'uint32_t a0,uint32_t a1' if row['family']=='IRQ' or address in (0x9c0a,0x18ef2) else 'uint32_t a0'
        out+='uint32_t '+name+'('+arguments+') __attribute__((section("'+row.get('typed_input_section',row['name'])+'"),used,noinline));\n'
        if address!=0x9b8e:out+='extern __typeof__('+name+') '+row['global_alias']+' __attribute__((alias("'+name+'")));\n'
    return (out+'#ifdef __cplusplus\n}\n#endif\n').encode('utf-8')
def expected_commands(root,folder,mode,m,tools,units):
    """Derive complete chronology independently; no command is launched."""
    clang,link,objcopy,python=(str(tools[k]) for k in ('clang','linker','objcopy','python'));result=[('compiler-resource-dir',[clang,'-print-resource-dir'])];filtered={row['producer'] for row in m['selected_sections']};raw=[]
    for name in m['source_units']:
        original=root/name;source=folder/'filtered'/original.name if name in filtered else original;out=folder/('carrier-'+original.stem+'.o');raw.append(str(out))
        result.append(('compile-'+original.stem,[clang,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-I',str(original.parent),'-MD','-MF',str(out.with_suffix('.d')),'-MT',out.name,'-c',str(source),'-o',str(out)]))
    result.append(('merge-raw-carriers',[link,'-r','--no-relax',*raw,'-o',str(folder/'raw-carriers.o')]));typed=[]
    for unit in units(mode):
        label=unit['label'];ad=folder/(label+'-adapter.h');out=folder/(label+'.o')
        for kind,action,suffix in [('object',['-c'],'.o'),('IR',['-S','-emit-llvm'],'.ll')]:
            deps=['-MD','-MF',str(out.with_suffix('.d')),'-MT',out.name] if kind=='object' else [];result.append(('typed-'+label+'-'+kind,[clang,*unit['flags'],'-include',str(ad),*deps,*action,str(unit['source']),'-o',str(folder/(label+suffix))]))
        if label=='reply':
            result.append(('explicit-reply-ordering',[python,'-B',str(root/'experiments/tsl9-v4160-reply-abi-order/order.py'),'--project-root',str(root),'--input',str(out),'--output',str(folder/'reply-ordered.o'),'--receipt',str(folder/'reply-order.json')]));typed.append(str(folder/'reply-ordered.o'))
        else:typed.append(str(out))
    model=root/'experiments/tsl9-v4160-reply-image-integration';layout=str(model/'original-image-layout.ld');numeric=str(folder/'NUMERIC-ROM-WITNESS-ONLY.ld');final=str(folder/'source-integrated.o')
    result += [('merge-typed',[link,'-r','--no-relax',*typed,'-o',str(folder/'typed-providers.o')]),('merge-source-integrated',[link,'-r','--no-relax','-T',str(folder/'canonical53.ld'),str(folder/'raw-carriers.o'),str(folder/'typed-providers.o'),'-o',str(folder/'pre-frame-integrated.o')]),('explicit-frame-scheduling',[python,'-B',str(root/'experiments/tsl9-v4160-frame-schedule/schedule.py'),'--project-root',str(root),'--input',str(folder/'pre-frame-integrated.o'),'--output',final,'--receipt',str(folder/'frame-scheduling.json')]),('strict-final-link',[link,'--no-relax','--error-limit=0','-T',layout,final,'-o',str(folder/'STRICT-MISSING-ROM.elf')]),('numeric-witness-final-link',[link,'--no-relax','-T',layout,'-T',numeric,final,'-o',str(folder/'ADDRESS-WITNESS-ONLY.elf')]),('export-new-offline-image',[objcopy,'-O','binary',str(folder/'ADDRESS-WITNESS-ONLY.elf'),str(folder/'NOT-FLASH-VALIDATED-reply-integrated.bin')])]
    need(len(result)==61 and len({label for label,argv in result})==61,'Exactly ordered61 recipes');return result
def commands_gate(commands,expected):
    need(len(commands)==len(expected)==61,'Actual61 commands')
    for row,(label,argv) in zip(commands,expected):
        need(row['label']==label and row['argv']==argv,'Exact chronological command/source/profile/output association: '+label)
        need(row['exit']!=0 if label=='strict-final-link' else row['exit']==0,'Only sole missing-ROM strict link rejects')
def inspect(root,folder,receipt,source,firmware):
    root=Path(root).resolve();folder=Path(folder).resolve();m=source['manifest'];r=receipt;need(r['mode'] in ('c','cpp') and r['source_files']==m['source_files'],'Claimed language and79 native source pins')
    for name,pin in r['artifacts'].items():
        p=(folder/name).resolve(strict=True);p.relative_to(folder);need(sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes'],'Actual source/compiler artifact '+name)
    tools={name:Path(row['path']).resolve(strict=True) for name,row in r['tools'].items()};need(set(tools)=={'clang','linker','objcopy','python'},'Four declared host tools')
    for name,path in tools.items():need(sha(path)==r['tools'][name]['sha256'],'Actual host tool identity')
    units,E,bindings=profiles(root,firmware,m);expected=expected_commands(root,folder,r['mode'],m,tools,units);commands_gate(r['commands'],expected)
    canonical=bindings(m);marker='  KEEP(*('+REPLY+'))\n';need(canonical.count(marker)==1,'One canonical zero-byte reply owner');canonical=canonical.replace(marker,marker+'  KEEP(*(.text.tsl9_ota_page_reply_9b8e))\n');need((folder/'canonical53.ld').read_bytes()==canonical.encode('utf-8'),'Exact canonical53 script plus explicit zero-boundary/native merge')
    need((folder/'NUMERIC-ROM-WITNESS-ONLY.ld').read_text(encoding='utf-8')=='/* Numeric address only: no ROM bytes/provider/runtime proof. */\n__tsl9v4160_rom_entry = 0x40000;\n','Exact address-only ROM witness source')
    for row in r['commands']:need(sha(folder/row['log'])==row['log_sha256'],'Actual source-only command log')
    for original,payload in source['generated_filters'].items():need((folder/'filtered'/Path(original).name).read_bytes()==payload,'Actual exact five source filter outputs')
    names={row['name'] for row in m['selected_sections']};specs={}
    for name in m['source_units']:
        original=root/name;primary=folder/'filtered'/original.name if name in source['generated_filters'] else original;stem='carrier-'+original.stem;specs[stem+'.d']=(stem+'.o',primary,None)
        e=E(folder/(stem+'.o'));need(not any(section['name'] in names and section['size'] and section['flags']&2 for section in e.sections),'No selected raw fallback in any carrier object')
    for unit in units(r['mode']):
        label=unit['label'];ad=folder/(label+'-adapter.h');need(ad.read_bytes()==adapter(unit['rows']),'Only owning typed section/function/alias adapter');specs[label+'.d']=(label+'.o',unit['source'],ad)
    raw=E(folder/'carrier-ota_handler_native.o');section=raw.byname[REPLY];need((section['type'],section['flags'],section['size'],section['alignment'])==(1,6,0,2),'Actual zero-byte AX reply boundary')
    role=lambda s:(s['name'],s['value'],s['size'],s['info'],s['other']);actual=sorted(role(s) for s in raw.symbols if s['name'] and s['index']==section['index']);need(actual==sorted([('__tsl9v4160_ota_code_9b8e',0,0,16,0),('.Lota_handler_00009b8e',0,0,0,0)]),'Original NOTYPE0 and local0 remain; no raw FUNC fabrication')
    resource_text=(folder/'compiler-resource-dir.log').read_text(encoding='utf-8').strip();need(len(resource_text.splitlines())==1,'Single actual compiler resource directory');directory=Path(resource_text).resolve(strict=True);headers={}
    for row in m['compiler_resource_header_inputs']:
        path=(directory/row['resource_relative']).resolve(strict=True);path.relative_to(directory);need(sha(path)==row['sha256'],'Actual resource-relative compiler header');headers[path]=row['sha256']
    seen=set();generated=set();external=set();resource_rules=0;need({p.name for p in folder.glob('*.d')}==set(specs) and len(specs)==43,'Exactly43 actual -MD rules')
    for name,(target,primary,ad) in specs.items():
        uses_resource=False
        for path in dependency((folder/name).read_text(encoding='utf-8'),target,primary,ad):
            if path.is_relative_to(folder):generated.add(path.relative_to(folder).as_posix())
            elif path.is_relative_to(root):
                relative=path.relative_to(root).as_posix();need(relative in m['source_files'] and sha(path)==m['source_files'][relative],'Every observed existing project input pinned');seen.add(relative)
            else:need(path in headers and sha(path)==headers[path],'Only observed pinned compiler resource inputs outside project');external.add(path);uses_resource=True
        resource_rules+=int(uses_resource)
    generated_expected={'filtered/'+Path(n).name for n in source['generated_filters']}|{unit['label']+'-adapter.h' for unit in units(r['mode'])}
    need(seen==set(m['source_files'])-set(source['generated_filters']) and len(seen)==74 and generated==generated_expected and len(generated)==14 and external==set(headers),'Measured74 existing/14generated/resource include closure')
    for name,pin in r['input_stability_pins'].items():need(sha(Path(name))==pin,'Actual source/proof/tool/header stability pin')
    need(all(str(path) in r['input_stability_pins'] and r['input_stability_pins'][str(path)]==pin for path,pin in headers.items()),'Actual compiler header included in before/after evidence')
    strict=(folder/'strict-final-link.log').read_text(encoding='utf-8');need(set(re.findall(r'undefined symbol: (\w+)',strict))=={'__tsl9v4160_rom_entry'} and not (folder/'STRICT-MISSING-ROM.elf').exists(),'Sole unknown-ROM strict failure actually recorded')
    return {'passed':True,'actual_commands':61,'ordered_ABI_stages':2,'actual_object_TUs':43,'raw_TUs':34,'typed_TUs':9,'actual_IR_units':9,'all_TUs_MD':True,'dependency_rules':43,'existing_project_inputs':74,'generated_inputs':14,'compiler_resource_headers':len(headers),'rules_observing_compiler_resource_headers':resource_rules,'resource_headers_actual_checked':True,'zero_byte_original_NOTYPE_boundary':True,'original_BIN_is_codegen_input':False,'target_execution':False}
