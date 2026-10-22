"""Actual fresh whole-image prototype; generated code never reads original BIN.

Provisional diagnostic producer, deliberately separate from future strict admission.
"""
import argparse,collections,hashlib,json,os,runpy,subprocess,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-tx-image-integration'
TX='.text.tsl9v4160.code_continuation_8a56'
IMAGE='NOT-FLASH-VALIDATED-tx-integrated.bin'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
def case(root,slug):return next(p for p in(root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def load(root):
    old=case(root,'v4160-reply-image-integration-2026-10-22')/'implementation/verify_image.py';need(sha(old)=='540b2cf1627ebd603760b673738437691c416225ae389dfc36c1de8ecdc8e215','sealed twelve-owner producer')
    return runpy.run_path(str(old))
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--language',choices=['c','cpp','both'],default='c');p.add_argument('--build-root',type=Path);p.add_argument('--firmware',type=Path);a=p.parse_args();root=a.project_root.resolve();model=root/MODEL;P=load(root);ctx=P['context'](root,a.firmware);V=ctx['V'];E=ctx['ELF'];m=ctx['manifest'];oldtx=next(s for s in m['baseline_symbol_roles'] if s['name']=='__tsl9v4160_call_8a56');need(oldtx['owner']==TX and oldtx['bytes']==280 and oldtx['info']==18,'actual original global FUNC280 owner')
    TXC=case(root,'v4160-ota-tx-2026-10-22')/'implementation/verify_native.py';need(sha(TXC)=='253b5fb067d5f5c90e517e2df4593381ef807dfbdd6143de2526c97a84744525','sealed native flags');T=runpy.run_path(str(TXC));tools={k:V.resolve_tool(None,a.tool_dir,n) for k,n in [('clang','clang'),('linker','ld.lld'),('objcopy','llvm-objcopy')]};tools['python']=Path(sys.executable).resolve();firmware,original=P['original_image'](root,ctx,a.firmware);base=a.build_root.resolve() if a.build_root else model/'build'/('prototype-'+uuid.uuid4().hex);need(not base.exists() and base.is_relative_to(model/'build'),'new owned build root');base.mkdir(parents=True);results=[]
    for mode in ('c','cpp') if a.language=='both' else(a.language,):
        folder=base/mode;folder.mkdir();tmp=folder/'compiler-temp';tmp.mkdir();env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp));commands=[];inputs={str(root/n):v for n,v in m['source_files'].items()};inputs[str(model/'adapter/entry.S')]=sha(model/'adapter/entry.S');inputs[str(Path(__file__).resolve())]=sha(Path(__file__).resolve())
        def run(label,argv,fail=False):
            r=subprocess.run([str(x) for x in argv],cwd=folder,capture_output=True,env=env,timeout=180);log=folder/(label+'.log');log.write_bytes(r.stdout+r.stderr);commands.append(dict(label=label,argv=[str(x) for x in argv],exit=r.returncode,log=log.name,sha256=sha(log),TMP=str(tmp),TEMP=str(tmp)));need(r.returncode!=0 if fail else r.returncode==0,'actual '+label+' failed: '+str(log));return r
        resource=Path(run('compiler-resource-dir',[tools['clang'],'-print-resource-dir']).stdout.decode().strip())/'include/stdint.h';inputs[str(resource)]=sha(resource);filtered=folder/'filtered';filtered.mkdir();groups=collections.defaultdict(dict)
        for r in m['selected_sections']:groups[r['producer']][r['name']]=r
        txsrc=next(n for n in m['source_units'] if n.endswith('/code_continuation_native.c'));groups[txsrc][TX]=dict(name=TX,global_alias='__tsl9v4160_call_8a56',bytes=280);rawobjects=[];filters=[]
        for name in m['source_units']:
            original_source=root/name;src=original_source
            if name in groups:
                src=filtered/original_source.name;payload=P['filtered_source'](ctx,original_source.read_bytes(),groups[name]);src.write_bytes(payload);filters.append(dict(source=name,sha256=sha(src),removed_sections=sorted(groups[name])))
            out=folder/('carrier-'+src.stem+'.o');run('compile-'+src.stem,[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-I',original_source.parent,'-MD','-MF',out.with_suffix('.d'),'-MT',out.name,'-c',src,'-o',out]);rawobjects.append(out)
        run('merge-raw-carriers',[tools['linker'],'-r','--no-relax',*rawobjects,'-o',folder/'raw-carriers.o']);typed=[]
        for u in P['units'](ctx,mode):
            label=u['label'];ad=folder/(label+'-adapter.h');ad.write_bytes(P['adapter'](u['rows']).encode());out=folder/(label+'.o')
            for kind,action,dest in [('object',['-c'],out),('IR',['-S','-emit-llvm'],folder/(label+'.ll'))]:
                deps=['-MD','-MF',out.with_suffix('.d'),'-MT',out.name] if kind=='object' else [];run('typed-'+label+'-'+kind,[tools['clang'],*u['flags'],'-include',ad,*deps,*action,u['source'],'-o',dest])
            if label=='reply':run('explicit-reply-ordering',[tools['python'],'-B',ctx['reply']['ordering'],'--project-root',root,'--input',out,'--output',folder/'reply-ordered.o','--receipt',folder/'reply-order.json']);out=folder/'reply-ordered.o'
            typed.append(out)
        frozen=root/'experiments/tsl9-v4160-tx-register-abi'
        for label in ('valid_body','return_leaf'):
            src=frozen/'adapter'/(label+'.c');inputs[str(src)]=sha(src)
            for kind,action,suffix in [('object',['-c'],'.o'),('IR',['-S','-emit-llvm'],'.ll')]:
                deps=['-MD','-MF',folder/('tx-'+label+'.d'),'-MT','tx-'+label+'.o'] if kind=='object' else [];run('tx-'+label+'-'+kind,[tools['clang'],*T['flags'](mode),*deps,*action,src,'-o',folder/('tx-'+label+suffix)])
        run('tx-entry-object',[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-x','assembler','-c',model/'adapter/entry.S','-o',folder/'tx-entry.o'])
        order=Path(__file__).with_name('tx_order.py');run('explicit-tx-frame-ordering',[tools['python'],'-B',order,'--project-root',root,'--input',folder/'tx-valid_body.o','--output',folder/'tx-valid_body-ordered.o','--receipt',folder/'tx-frame-order.json']);typed += [folder/'tx-entry.o',folder/'tx-valid_body-ordered.o',folder/'tx-return_leaf.o']
        run('merge-typed',[tools['linker'],'-r','--no-relax',*typed,'-o',folder/'typed-providers.o'])
        script=P['bindings_source'](ctx);needle='  KEEP(*('+TX+'))\n';need(script.count(needle)==1,'canonical TX output section');script=script.replace(needle,needle+''.join('  KEEP(*('+n+'))\n' for n in('.text.tsl9_tx_entry','.text.tsl9_tx_valid_body','.text.tsl9_tx_oversized_return')));(folder/'canonical53.ld').write_bytes(script.encode());run('merge-source-integrated',[tools['linker'],'-r','--no-relax','-T',folder/'canonical53.ld',folder/'raw-carriers.o',folder/'typed-providers.o','-o',folder/'pre-frame-integrated.o'])
        run('explicit-frame-scheduling',[tools['python'],'-B',ctx['scheduler'],'--project-root',root,'--input',folder/'pre-frame-integrated.o','--output',folder/'source-integrated.o','--receipt',folder/'frame-scheduling.json'])
        layout=root/'experiments/tsl9-v4160-reply-image-integration/original-image-layout.ld';strict=folder/'STRICT-MISSING-ROM.elf';run('strict-final-link',[tools['linker'],'--no-relax','--error-limit=0','-T',layout,folder/'source-integrated.o','-o',strict],True);need(not strict.exists() and set(__import__('re').findall(r'undefined symbol: (\w+)',(folder/'strict-final-link.log').read_text()))=={P['ROM']},'strict sole missing ROM provider')
        witness=folder/'NUMERIC-ROM-WITNESS-ONLY.ld';witness.write_bytes((P['ROM']+' = 0x40000;\n').encode());run('numeric-witness-final-link',[tools['linker'],'--no-relax','-T',layout,'-T',witness,folder/'source-integrated.o','-o',folder/'ADDRESS-WITNESS-ONLY.elf']);run('export-new-offline-image',[tools['objcopy'],'-O','binary',folder/'ADDRESS-WITNESS-ONLY.elf',folder/IMAGE]);image=(folder/IMAGE).read_bytes();e=E(folder/'source-integrated.o');l=E(folder/'ADDRESS-WITNESS-ONLY.elf');need(len(image)==76800,'actual complete image extent');diff=[dict(VA=i+0x8000,old=x,new=y) for i,(x,y) in enumerate(zip(original,image)) if x!=y];need(all(0x8a56<=r['VA']<0x8b6e for r in diff),'all image differences within TX280 only')
        selected={r['name'] for r in m['selected_sections']}|{TX};outside=[V.relocation(e,r) for r in e.relocations if r['owner'] not in selected];owned=[V.relocation(e,r) for r in e.relocations if r['owner'] in selected];need(set(V.alloc(e))==set(m['allocations']),'all691 allocation owner names retained');need(e.data(e.byname[TX])==b''.join(E(p).data(next(s for s in E(p).sections if s['flags']&2 and s['size'])) for p in typed[-3:]),'actual TX partial payload concatenates newly compiled/ordered three providers')
        for n,proof in m['retained_storage'].items():
            if n!=TX:need(hashlib.sha256(V.data(e,e.byname[n])).hexdigest()==proof['sha256'],'every retained partial-storage byte '+n)
        need(all(sha(Path(n))==pin for n,pin in inputs.items()),'stable source/resource inputs');result=dict(schema='TSL9-TX-whole-image-prototype-v1',passed=True,mode=mode,commands=commands,source_pins=inputs,filters=filters,allocation_count=len(V.alloc(e)),retained_storage_count=len(m['retained_storage'])-1,RELA=len(e.relocations),outside_RELA=len(outside),owned_RELA=len(owned),actual_FUNC_roles=[V.role(e,s) for s in e.symbols if s['info']&15==2 and s['index']==e.byname[TX]['index']],TX_linked_hex=l.data(l.byname[TX]).hex(),image=dict(bytes=len(image),sha256=sha(folder/IMAGE),differences=diff,outside_TX_identical=True),strict_missing_ROM_rejected=True,compiler_only=False,target_execution=False,whole_original_ABI_admitted=False,hardware=False,OTA_ready=False,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()});write(folder/'prototype.json',result);results.append(dict(mode=mode,receipt=str(folder/'prototype.json'),sha256=sha(folder/'prototype.json'),image=str(folder/IMAGE),image_sha256=sha(folder/IMAGE),RELA=result['RELA'],differences=len(diff)))
    write(base/'results.json',dict(results=results));print(json.dumps(dict(passed=True,results=results,whole_original_ABI_admitted=False,hardware=False)))
if __name__=='__main__':main()
