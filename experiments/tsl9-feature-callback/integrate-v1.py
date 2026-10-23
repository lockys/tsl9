#!/usr/bin/env python3
"""Genuine partial-link integration; compile products are inspected, never run."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v3.json').read_bytes())
K=json.loads((HERE/'integration-v1.json').read_bytes())
B=runpy.run_path(str(HERE/'build-v3.py'))
need=B['need'];sha=B['sha'];encoded=B['encoded'];portable=B['portable']

def parent(mode):
    return ROOT/K['previous_graph']/mode/'UNRESOLVED-FEATURE-GRAPH.o'

def native(mode):
    return ROOT/Path(K['curation']).parent/'feature-callback'/mode/'curated/unit.o'

def inputs(llvm):
    paths=[Path(__file__),HERE/'integration-v1.json',HERE/'joined-v1.ld',HERE/'spec-v3.json',
           HERE/'build-v3.py',ROOT/S['source'],ROOT/K['new_file_entry']['destination'],
           ROOT/S['firmware'],ROOT/S['reader'],ROOT/S['curation_checker'],
           ROOT/'src/source-manifest.json',ROOT/K['curation'],ROOT/K['previous_curation'],
           ROOT/K['standalone_receipt'],ROOT/'experiments/tsl9-feature-dispatch/verify-v2.py',
           llvm.parent/'lib/clang/18/include/stdint.h']
    for mode in ('c','cpp'):
        paths += [parent(mode),parent(mode).parent/'measurement.json',parent(mode).parent/'verification-v2.json',
                  native(mode),native(mode).parent/'unit.d',native(mode).parent/'compile.log',
                  (ROOT/K['standalone_receipt']).parent/mode/'native.o']
    paths += [llvm/n for n in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}

def expand(value,llvm):
    for name,p in [('CLANG_RESOURCE',llvm.parent/'lib/clang/18'),('LLVM_BIN',llvm),('PROJECT_ROOT',ROOT)]:
        value=value.replace('$'+'{'+name+'}',str(p))
    return Path(value)

def source_proof(llvm):
    for k in ('firmware','reader','curation_checker','source'):
        need(sha(ROOT/S[k])==S[k+'_sha256'],'Pinned '+k)
    for n,pin in S['tools'].items():
        need(sha(llvm/n)==pin,'Pinned local tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned header')
    need(sha(ROOT/K['curation'])==K['curation_sha256'],'Actual current98 receipt')
    need(sha(ROOT/K['previous_curation'])==K['previous_curation_sha256'],'Frozen prior96 receipt')
    need(sha(ROOT/K['standalone_receipt'])==K['standalone_receipt_sha256'],'Actual native trial receipt')
    need(sha(ROOT/'experiments/tsl9-feature-dispatch/verify-v2.py')==K['parent_checker_sha256'],'Frozen parent checker')
    raw=subprocess.check_output(['git','show',K['base_commit']+':src/source-manifest.json'],cwd=ROOT)
    need(hashlib.sha256(raw).hexdigest()==K['previous_manifest_sha256'],'Pinned original Git manifest')
    old=json.loads(raw);current=json.loads((ROOT/'src/source-manifest.json').read_bytes())
    old['files'].append(K['new_file_entry']);old['native_units'].append(K['new_unit_entry'])
    need(old==current,'Exact one-file one-unit manifest extension')
    previous=json.loads((ROOT/K['previous_curation']).read_bytes())
    curated=json.loads((ROOT/K['curation']).read_bytes())
    need(curated['results'][:96]==previous['results'] and len(curated['results'])==98,'All prior96 comparison facts unchanged')
    need(len(previous['artifacts'])==577 and all(curated['artifacts'].get(k)==v for k,v in previous['artifacts'].items()),'All prior577 artifact records unchanged')
    p=subprocess.run([sys.executable,'-B',str(ROOT/S['curation_checker']),'--replay',str(ROOT/K['curation'])],
                     cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    need(p.returncode==0,'Current complete source replay')
    replay=json.loads(p.stdout);need(replay['passed']and replay['comparisons']==98,'Actual98 read-only audit')
    standalone=json.loads((ROOT/K['standalone_receipt']).read_bytes())
    for mode in ('c','cpp'):
        need(sha(parent(mode))==K['previous_graph_sha256'],'Pinned genuine parent graph')
        need(sha(parent(mode).parent/'verification-v2.json')==K['parent_v2_receipts'][mode],'Frozen parent normal-artifact proof')
        record=json.loads((parent(mode).parent/'measurement.json').read_bytes())
        for key,pin in record['inputs'].items():
            path=expand(key,llvm)
            if path==ROOT/'src/source-manifest.json':
                need(pin['sha256']==K['previous_manifest_sha256'],'Only proven global-manifest extension')
                continue
            need(path.is_file()and path.stat().st_size==pin['bytes']and sha(path)==pin['sha256'],'Frozen parent producer input unchanged')
        need(sha(native(mode))==K['curated_native_object_sha256'],'Pinned actual curated object')
        original=(ROOT/K['standalone_receipt']).parent/mode/'native.o'
        need(sha(original)==K['native_object_sha256'],'Pinned actual standalone object')
        E=runpy.run_path(str(ROOT/S['reader']))['ELF'];original_elf=E(original);curated_elf=E(native(mode))
        need({s['name']for s in original_elf.sections}=={s['name']for s in curated_elf.sections},'Complete same section inventory')
        need(all(original_elf.data(sec)==curated_elf.data(curated_elf.section(sec['name']))
                 for sec in original_elf.sections if sec['name'] and sec['name']not in('.strtab','.symtab')),'All non-symbol carrier bytes equal')
        need([s for s in original_elf.symbols if s['info']&15!=4]==
             [s for s in curated_elf.symbols if s['info']&15!=4],'All non-FILE parsed symbols equal')
        need([s['name']for s in original_elf.symbols if s['info']&15==4]==['callback.v3.c']and
             [s['name']for s in curated_elf.symbols if s['info']&15==4]==['feature_callback.c'],'Only known local FILE identity differs')
        prior_result=standalone['modes'][mode]['result']
        need(B['audit_object'](native(mode))==dict(prior_result,native_object_sha256=K['curated_native_object_sha256']),'Current native314B audit with explicit object carrier hash')
    return dict(passed=True,current_comparisons=98,current_objects=196,source_C_H_files=75,native_units=49,
                prior96_comparisons_and577_artifacts_unchanged=True,
                standalone_curated_complete_projection_equal_except_local_FILE_identity=True,
                parent_source_scope='Exact one-file and one-unit manifest extension; all other parent producer inputs unchanged',
                original_parent_whole_manifest_replay_claimed=False,negative_cases_executed=0)

def globals_by_name(e):
    items=[s for s in e.symbols if s['info']>>4]
    need(len({s['name']for s in items})==len(items),'Unique genuine global names')
    need(all(s['section']!=0xfff1 for s in items),'No absolute providers')
    return {s['name']:s for s in items}

def relocs(e,transform):
    return Counter((transform(e.sections[r['section']]['name'],r['offset']),
                    r['type'],e.symbols[r['symbol']]['name'],r['addend'])for r in e.relocations)

def audit_graph(path,mode):
    E=runpy.run_path(str(ROOT/S['reader']))['ELF']
    p=E(parent(mode));n=E(native(mode));e=E(path)
    need(e.header[0]==1 and not e.program_headers,'Unresolved ET_REL without loading headers')
    pm=globals_by_name(p);nm=globals_by_name(n);em=globals_by_name(e)
    need('tsl9_queue_clear_820c'in pm and pm['tsl9_queue_clear_820c']['info']==18,'Real existing shared820C provider')
    need(set(em)==set(pm)|set(nm),'Complete genuine global-symbol inventory')
    offsets={};at=K['old_graph_code_bytes'];pieces=[]
    for region in S['regions']:
        fn=nm[region['name']];offsets['.text.'+region['name']]=at
        pieces.append(n.data(n.sections[fn['section']]));at+=region['bytes']
    need(at==K['total_code_bytes'],'Exact new graph extent')
    allowed={'.feature_graph':(6,at),'.table_0':(2,28),'.table_1':(2,32)}
    need({s['name']for s in e.sections if s['flags']&2 and s['size']}==set(allowed),'All actual allocated sections')
    for name,(flags,size)in allowed.items():
        sec=e.section(name);need(sec['flags']==flags and sec['size']==size and sec['address']==0,'Exact allocation and zero VMA')
    need(e.data('.feature_graph')==p.data('.feature_graph')+b''.join(pieces),'Parent prefix and all new code bytes unchanged by partial link')
    need(all(e.data(name)==p.data(name)for name in ('.table_0','.table_1')),'All60 original relative-table carrier bytes unchanged')
    for name,actual in em.items():
        originals=[s for s in (pm.get(name),nm.get(name))if s and s['section']]
        if originals:
            need(len(originals)==1,'Single true definition')
            original=originals[0];from_new=name in nm and nm[name]['section']>0
            owner=(n if from_new else p).sections[original['section']]['name']
            target='.feature_graph'if from_new else owner
            value=offsets[owner]+original['value']if from_new else original['value']
            need(actual['info']==original['info'] and actual['other']==original['other'] and
                 actual['size']==original['size'] and e.sections[actual['section']]['name']==target and
                 actual['value']==value,'Exact genuine definition '+name)
        else:
            need(actual['info']==16 and actual['section']==0 and actual['value']==0,'Explicit unresolved provider '+name)
    wanted=relocs(p,lambda s,o:(s,o))
    wanted.update(relocs(n,lambda s,o:('.feature_graph',offsets[s]+o)))
    need(relocs(e,lambda s,o:(s,o))==wanted,'Every parent and new typed relocation preserved with true owners')
    need(len(e.relocations)==412,'Complete386+26 relocation count')
    undefined=sorted(name for name,sym in em.items()if sym['section']==0)
    resolved=sorted(name for name,sym in pm.items()if sym['section']==0 and name in nm and nm[name]['section']>0)
    return dict(passed=True,mode=mode,code_bytes=5402,table_bytes=60,FUNC=sum(s['info']==18 for s in em.values()),
                RELA=len(e.relocations),UND=undefined,resolved_parent_direct_UND=resolved,
                new_code_bytes=314,new_code_instructions=109,new_native_regions=31,
                previous5088_code_bytes_and60_table_bytes_unchanged=True,
                graph_sha256=sha(path),ELF_VMA_zero=True,executable=False,
                all_new_native_code_original_VA_equal=True,normal_artifacts_only=True,
                independent_safety_stopped_review_retried=False,negative_cases_executed=0,
                target_executed=False,ISA_emulated=False,HOST_model_executed=False,
                hardware_accessed=False,network=False,firmware_BIN_generated=False,firmware_ready=False)

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve();proof=source_proof(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained output')
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['source_proof']==proof,'All actual retained provenance')
        for mode in ('c','cpp'):
            need(saved['modes'][mode]['artifacts']==inventory(out/mode),'Full retained output inventory')
            need(saved['modes'][mode]['result']==audit_graph(out/mode/'UNRESOLVED-CALLBACK-GRAPH.o',mode),'Normal graph replay equality')
        print(json.dumps(dict(passed=True,languages=['c','cpp'],mode='read-only-normal-graph-replay',source_proof=proof)))
        return
    out=a.output.resolve();need(out.parent==HERE/'build' and not out.exists(),'Create-only direct child output')
    report=dict(schema='TSL9-callback-partial-link-v1',inputs=before,source_proof=proof,modes={})
    for mode in ('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[]
        output=f/'UNRESOLVED-CALLBACK-GRAPH.o'
        recipes=[('joined-link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v1.ld'),
                                 str(parent(mode)),str(native(mode)),'-o',str(output)]),
                 ('joined-read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(output)])]
        for label,argv in recipes:
            result=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (f/(label+'.log')).write_bytes(result.stdout);commands.append(dict(label=label,argv=argv,exit=result.returncode))
            need(result.returncode==0,'Actual '+label+' failed; original log retained')
        audit=audit_graph(output,mode)
        (f/'verification.json').write_bytes(encoded(audit))
        report['modes'][mode]=dict(result=audit,commands=commands,artifacts=inventory(f))
        print(json.dumps({k:v for k,v in audit.items()if k!='UND'}|dict(UND_count=len(audit['UND']))))
    need(before==portable(inputs(llvm),llvm),'Inputs unchanged during real partial link')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))

if __name__=='__main__':
    try:
        main()
    except (ValueError,OSError) as e:
        print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
