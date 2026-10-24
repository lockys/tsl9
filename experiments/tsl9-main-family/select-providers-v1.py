"""Select whole real provider sections; never synthesize an executable stub."""
import argparse,hashlib,json,runpy,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
N=runpy.run_path(str(HERE/'build-v1.py'))
S=N['S'];need=N['need'];sha=N['sha'];portable=N['portable'];encoded=N['encoded']
K=json.loads((HERE/'providers-v1.json').read_bytes())
def source(group,mode):return ROOT/group['input_pattern'].format(mode=mode)
def audit(path,group,selected):
    e=N['elf'](path);fw=(ROOT/S['firmware']).read_bytes()
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Real RISC-V ET_REL')
    gm={x['name']:x for x in e.symbols if x['info']>>4};owners=set()
    if selected:need(set(gm)=={x['name']for x in group['regions']},'Only whole genuine selected providers')
    for row in group['regions']:
        f=gm[row['name']];sec=e.sections[f['section']];owners.add(sec['index'])
        need(f['info']==18 and f['value']==0 and f['size']==row['bytes']and sec['name']=='.text.'+f['name']and sec['flags']==6 and sec['size']==f['size'],'Real complete function ownership')
        b=e.data(sec);original=fw[row['start']-0x8000:row['start']-0x8000+row['bytes']]
        need(b==original and hashlib.sha256(b).hexdigest()==row['original_sha256'],'Every selected original provider byte')
        need(not any(x['section']==sec['index']for x in e.relocations),'No hidden selected direct dependency')
    if selected:need({x['index']for x in e.sections if x['flags']&2 and x['size']}==owners and not e.relocations,'Every selected allocation and reference owned')
    return dict(passed=True,code_bytes=sum(x['bytes']for x in group['regions']),FUNC=len(group['regions']),RELA=0,UND=0,object_sha256=sha(path),all_original_bytes_equal=True)
def inputs(llvm):
    paths=[Path(__file__),HERE/'providers-v1.json',HERE/'build-v1.py',HERE/'spec-v1.json',ROOT/S['firmware'],ROOT/S['reader'],ROOT/K['source_curation_receipt'],llvm/'llvm-objcopy.exe']
    for group in K['groups']:
        paths.append(ROOT/group['source'])
        for mode in ['c','cpp']:paths.append(source(group,mode))
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    need(sha(llvm/'llvm-objcopy.exe')==S['tools']['llvm-objcopy.exe'],'Pinned selector')
    need(sha(ROOT/K['source_curation_receipt'])==K['source_curation_sha256'],'Pinned retained source provenance')
    for group in K['groups']:
        need(sha(ROOT/group['source'])==group['source_sha256'],'Unchanged real provider source')
        for mode in ['c','cpp']:
            need(sha(source(group,mode))==group['input_sha256'][mode],'Pinned complete compiler output')
            audit(source(group,mode),group,False)
    before=portable(inputs(llvm),llvm);out=(a.replay or a.output).resolve()
    need(out.parent==HERE/'build','Owned native output')
    if a.replay:
        saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==before,'All selection inputs unchanged')
        for mode in ['c','cpp']:
            need(saved['modes'][mode]['artifacts']==inventory(out/mode),'All retained selection outputs unchanged')
            for group in K['groups']:need(saved['modes'][mode]['results'][group['name']]==audit(out/mode/(group['name']+'.o'),group,True),'Actual selected output replay')
        print(json.dumps(dict(passed=True,mode='read-only-real-provider-selection',target_executed=False)));return
    need(not out.exists(),'Create-only native provider selection')
    report=dict(schema='TSL9-main-family-provider-selection-build-v1',inputs=before,modes={})
    for mode in ['c','cpp']:
        f=out/mode;f.mkdir(parents=True);results={};commands=[]
        for group in K['groups']:
            args=[str(llvm/'llvm-objcopy.exe'),'--strip-unneeded']+['--only-section=.text.'+x['name']for x in group['regions']]+[str(source(group,mode)),str(f/(group['name']+'.o'))]
            run=subprocess.run(args,cwd=ROOT,capture_output=True,timeout=60)
            (f/(group['name']+'.log')).write_bytes(run.stdout+run.stderr)
            need(run.returncode==0,'Actual whole-section extraction')
            commands.append(dict(argv=args,exit=run.returncode))
            results[group['name']]=audit(f/(group['name']+'.o'),group,True)
        report['modes'][mode]=dict(results=results,commands=commands,artifacts=inventory(f))
    need(before==portable(inputs(llvm),llvm),'All selector inputs unchanged')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))
    print(json.dumps(dict(passed=True,languages=['c','cpp'],whole_provider_functions=1,original_bytes=40,RELA=0,UND=0,target_executed=False)))
if __name__=='__main__':main()
