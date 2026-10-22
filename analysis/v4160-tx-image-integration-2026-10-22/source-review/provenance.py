"""Independent source, exact recipe and include closure; never launch tools."""
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True

def context(R,root,firmware):
    oldcase=R.case(root,'v4160-reply-image-integration-2026-10-22')/'source-review'
    p=oldcase/'provenance.py';q=oldcase/'source-inputs.py'
    R.need(R.sha(p)=='fa11bf5313e15bc785a232ed0eebb3fc049a1c61f96f1d8b13a6beb2abb20468' and R.sha(q)=='bd7bb51ad0a59926bd73806720c4fd895017e13854b5506d5702fbf988268b3e','Immutable independent prior source/recipe helpers')
    P=R.load('thirteen_prior_source_recipes',p);S=R.load('thirteen_prior_source_inputs',q);old=root/'experiments/tsl9-v4160-reply-image-integration';c=S.context(root,old/'source-manifest.json','09bfe0613a88a395b048a397530f62e49b199e890c3d2fc04285ca44887915fe');model=root/'experiments/tsl9-v4160-tx-image-integration';ledger=R.read(model/'source-manifest.json')
    extra={n:R.sha(root/n) for n in ['experiments/tsl9-v4160-tx-register-abi/'+s for s in ('src/tx_native.c','src/tx_native.h','src/tx_io.h','adapter/valid_body.c','adapter/return_leaf.c')]+['experiments/tsl9-v4160-tx-image-integration/adapter/entry.S']}
    R.need(ledger['source_files']==dict(c['manifest']['source_files'],**extra) and len(ledger['source_files'])==85,'Exactly old79 + six explicit TX inputs; no fake source provider')
    for n,pin in ledger['source_files'].items():R.need(R.sha(root/n)==pin,'Actual current source pin '+n)
    txproducer=next(n for n in c['manifest']['source_units'] if n.endswith('/code_continuation_native.c'));txrow=dict(name=R.OWNER,global_alias=R.PUBLIC,bytes=280);c['generated_filters'][txproducer]=S.filtered(c['generated_filters'][txproducer],[txrow])
    units,E,bindings=P.profiles(root,firmware,c['manifest']);profile=R.case(root,'v4160-ota-tx-2026-10-22')/'implementation/verify_native.py';R.need(R.sha(profile)=='adeeaddea4c46d92dd4ce33a5beaa329779781a0611e97b965c1f023f5ef4eca','Immutable TX compiler profile');F=R.load('thirteen_independent_TX_profile',profile)
    return dict(P=P,S=S,old=c,model=model,ledger=ledger,units=units,E=E,bindings=bindings,TXflags=F.flags)

def recipes(R,root,folder,mode,tools,c):
    P=c['P'];m=c['old']['manifest'];old=P.expected_commands(root,folder,mode,m,tools,c['units']);position=next(i for i,r in enumerate(old) if r[0]=='merge-typed');out=old[:position];clang=str(tools['clang']);python=str(tools['python']);native=root/'experiments/tsl9-v4160-tx-register-abi'
    for label in ('valid_body','return_leaf'):
        for kind,action,suffix in [('object',['-c'],'.o'),('IR',['-S','-emit-llvm'],'.ll')]:
            dep=['-MD','-MF',str(folder/('tx-'+label+'.d')),'-MT','tx-'+label+'.o'] if kind=='object' else []
            out.append(('tx-'+label+'-'+kind,[clang,*c['TXflags'](mode),*dep,*action,str(native/'adapter'/(label+'.c')),'-o',str(folder/('tx-'+label+suffix))]))
    out.append(('tx-entry-object',[clang,'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-x','assembler','-c',str(c['model']/'adapter/entry.S'),'-o',str(folder/'tx-entry.o')]))
    driver=R.case(root,'v4160-tx-image-integration-2026-10-22')/'implementation/tx_order.py'
    out.append(('explicit-tx-frame-ordering',[python,'-B',str(driver),'--project-root',str(root),'--input',str(folder/'tx-valid_body.o'),'--output',str(folder/'tx-valid_body-ordered.o'),'--receipt',str(folder/'tx-frame-order.json')]))
    tail=old[position:];merge=tail[0][1];at=merge.index('-o');tail[0]=(tail[0][0],merge[:at]+[str(folder/n) for n in ('tx-entry.o','tx-valid_body-ordered.o','tx-return_leaf.o')]+merge[at:])
    # The old shared layout is immutable and remains an explicit actual command input.
    tail[-1]=(tail[-1][0],tail[-1][1][:-1]+[str(folder/'NOT-FLASH-VALIDATED-tx-integrated.bin')]);out+=tail
    R.need(len(out)==67 and len({n for n,a in out})==67,'Independent exact67 chronology');return out

def command_gate(R,commands,expected):
    R.need(len(commands)==67 and [(r['label'],r['argv']) for r in commands]==expected,'All67 exact command/source/profile/output associations and order')
    for row in commands:R.need(row['exit']!=0 if row['label']=='strict-final-link' else row['exit']==0,'Only strict missing-ROM link fails')

def inspect(R,root,firmware,folder,receipt):
    c=context(R,root,firmware);P=c['P'];m=c['old']['manifest'];r=receipt;mode=r['mode'];R.need(mode in ('c','cpp'),'Explicit language');tools={k:Path(v['path']).resolve(strict=True) for k,v in r['tools'].items()};R.need(set(tools)=={'clang','linker','objcopy','python'},'Four actual host tools')
    for k,p in tools.items():R.need(R.sha(p)==r['tools'][k]['sha256'],'Actual native build tool pin')
    expected=recipes(R,root,folder,mode,tools,c);command_gate(R,r['commands'],expected)
    R.need(set(r['artifacts'])=={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p!=folder/'verification.json'},'Complete actual artifact inventory, including every IR/dependency/log/control')
    for name,pin in r['artifacts'].items():
        p=(folder/name).resolve(strict=True);p.relative_to(folder);R.need(R.sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes'],'Actual pinned build artifact '+name)
    for row in r['commands']:R.need(R.sha(folder/row['log'])==row.get('sha256',row.get('log_sha256')),'Actual compile/link/order log')
    for original,data in c['old']['generated_filters'].items():R.need((folder/'filtered'/Path(original).name).read_bytes()==data,'Independent exact raw-owner source filter including TX with quarter')
    specs={}
    for n in m['source_units']:
        orig=root/n;stem='carrier-'+orig.stem;specs[stem+'.d']=(stem+'.o',folder/'filtered'/orig.name if n in c['old']['generated_filters'] else orig,None)
        e=c['E'](folder/(stem+'.o'));selected={x['name'] for x in m['selected_sections']}|{R.OWNER};R.need(not any(s['name'] in selected and s['size'] and s['flags']&2 for s in e.sections),'No original raw selected-body fallback')
    for u in c['units'](mode):
        label=u['label'];ad=folder/(label+'-adapter.h');R.need(ad.read_bytes()==P.adapter(u['rows']),'Exact prior typed source declaration/alias adapter');specs[label+'.d']=(label+'.o',u['source'],ad)
    for label in ('valid_body','return_leaf'):specs['tx-'+label+'.d']=('tx-'+label+'.o',root/'experiments/tsl9-v4160-tx-register-abi/adapter'/(label+'.c'),None)
    R.need(len(specs)==45 and {p.name for p in folder.glob('*.d')}==set(specs),'Exactly45 actual per-TU MD rules; raw ASM deliberately direct source')
    directory=Path((folder/'compiler-resource-dir.log').read_text().strip()).resolve(strict=True);headers={}
    for row in m['compiler_resource_header_inputs']:
        p=(directory/row['resource_relative']).resolve(strict=True);p.relative_to(directory);R.need(R.sha(p)==row['sha256'],'Actual compiler resource header');headers[p]=row['sha256']
    seen=set();generated=set();external=set();resource_rules=0
    for name,(target,primary,adapter) in specs.items():
        use=False
        for p in P.dependency((folder/name).read_text(),target,primary,adapter):
            if p.is_relative_to(folder):generated.add(p.relative_to(folder).as_posix())
            elif p.is_relative_to(root):
                n=p.relative_to(root).as_posix();R.need(n in c['ledger']['source_files'] and R.sha(p)==c['ledger']['source_files'][n],'Every actual project dependency belongs to exact source ledger');seen.add(n)
            else:R.need(p in headers and R.sha(p)==headers[p],'Only actual pinned compiler resource outside project');external.add(p);use=True
        resource_rules+=int(use)
    expectedseen=set(c['ledger']['source_files'])-set(c['old']['generated_filters'])-{'experiments/tsl9-v4160-tx-image-integration/adapter/entry.S','experiments/tsl9-v4160-tx-register-abi/src/tx_native.c'}
    expectedgenerated={'filtered/'+Path(n).name for n in c['old']['generated_filters']}|{u['label']+'-adapter.h' for u in c['units'](mode)}
    R.need(seen==expectedseen and len(seen)==78 and generated==expectedgenerated and len(generated)==14 and external==set(headers),'Exact measured78 project /14generated/resource closure, not all85 source pins compiled')
    canonical=c['bindings'](m);reply='.text.tsl9v4160.ota_handler_9b8e';marker='  KEEP(*('+reply+'))\n';canonical=canonical.replace(marker,marker+'  KEEP(*(.text.tsl9_ota_page_reply_9b8e))\n');marker='  KEEP(*('+R.OWNER+'))\n';canonical=canonical.replace(marker,marker+''.join('  KEEP(*('+n+'))\n' for n in ('.text.tsl9_tx_entry','.text.tsl9_tx_valid_body','.text.tsl9_tx_oversized_return')));R.need((folder/'canonical53.ld').read_bytes()==canonical.encode(),'Exact53 canonical relative bindings and truthful new provider section composition')
    R.need((folder/'NUMERIC-ROM-WITNESS-ONLY.ld').read_text()=='__tsl9v4160_rom_entry = 0x40000;\n','Numeric witness explicitly not ROM bytes')
    # Source/header/tool stability is independently checked against actual current files.
    for path,pin in r['input_stability_pins'].items():R.need(R.sha(Path(path))==pin,'Actual before/after input snapshot')
    required={str(root/n):pin for n,pin in c['ledger']['source_files'].items()};required.update({str(p):pin for p,pin in headers.items()})
    R.need(all(r['input_stability_pins'].get(n)==pin for n,pin in required.items()),'All project sources/direct ASM/resource headers explicitly in stability snapshot')
    base=folder.parent;generation=r['generation_invocation'];a=generation['argv'];language=a[a.index('--language')+1];R.need(language in (mode,'both'),'Outer generation language includes actual receipt mode')
    driver=R.case(root,'v4160-tx-image-integration-2026-10-22')/'implementation/prototype.py';expect=[str(tools['python']),'-B',str(driver),'--project-root',str(root),'--tool-dir',str(tools['clang'].parent),'--language',language,'--build-root',str(base),'--firmware',str(firmware)]
    R.need(a==expect and generation['exit']==0,'Exact outer source generator recipe, explicit reference-only firmware')
    preflight=r['preflight_query'];R.need(preflight['argv']==[str(tools['clang']),'-print-resource-dir'] and preflight['exit']==0,'Exact actual compiler resource preflight recipe')
    for row,name in ((generation,'fresh-generation.log'),(preflight,'preflight-resource-query.log')):
        p=Path(row['log']).resolve(strict=True);R.need(p==base/name and R.sha(p)==row['sha256'],'Contained actual outer host-driver/preflight log')
    R.need((base/'preflight-resource-query.log').read_bytes()==(folder/'compiler-resource-dir.log').read_bytes(),'Actual outer resource query matches per-language resource query')
    return dict(passed=True,actual_commands=67,LLVM_commands=64,explicit_Python_ABI_stages=3,compile_TUs=46,raw_TUs=34,typed_C_TUs=11,raw_assembler_TUs=1,actual_IR_units=11,actual_MD_rules=45,MD_project_inputs=78,direct_assembly_inputs=1,source_pins=85,generated_inputs=14,actual_resource_headers=len(headers),rules_using_resource_headers=resource_rules,all_source_pins_claimed_compiled=False,original_BIN_codegen_input=False,compiler_only=False)
