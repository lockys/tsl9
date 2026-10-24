"""Compose six genuine RF units at original relative offsets; inspect ET_REL only."""
import argparse,hashlib,json,runpy,subprocess,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
K=json.loads((HERE/'rf-original-v1.json').read_bytes())
S=json.loads((HERE/'spec-v1.json').read_bytes())
N=runpy.run_path(str(HERE/'build-v1.py'))
B=N['B']
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(x):return (json.dumps(x,ensure_ascii=True,sort_keys=True,indent=2)+'\n').encode()
def key(p,llvm):
    for base,token in [(ROOT,'PROJECT_ROOT'),(llvm,'LLVM_BIN')]:
        if p.is_relative_to(base):return '$'+'{'+token+'}/'+p.relative_to(base).as_posix()
    raise ValueError('Unexpected RF-layout input location')
def prepared(mode):
    rows=[];controls=[];objects=[];paths=[];proofs={}
    for u in K['units']:
        spec=ROOT/u['spec'];builder=ROOT/u['builder'];p=ROOT/u['objects'][mode]
        need(sha(spec)==u['spec_sha256']and sha(builder)==u['builder_sha256']and sha(p)==u['object_sha256'][mode],'Pinned actual RF unit')
        d=json.loads(spec.read_bytes())
        for field in ['source','curated_source','source_deriver','reference_candidate']:
            pin=d['source_sha256']if field=='curated_source'else d[field+'_sha256']
            need(sha(ROOT/d[field])==pin,'Original/curated RF unit source identity')
            paths.append(ROOT/d[field])
        module=runpy.run_path(str(builder));proofs[u['key']]=module['audit_object'](p)
        rows+=d['regions'];controls+=d['controls'];objects.append(p);paths.extend([spec,builder,p])
    rows.sort(key=lambda x:x['start'])
    need(len(rows)==103 and rows[0]['start']==K['range_start']and rows[-1]['end']==K['range_end']and
         all(a['end']==b['start']for a,b in zip(rows,rows[1:])),'Exactly contiguous original RF instruction coverage')
    need(sum(x['bytes']for x in rows)==1550 and len(controls)==56,'Whole RF code/reference coverage')
    return rows,controls,objects,paths,proofs
def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def inputs(llvm):
    paths=[Path(__file__),HERE/'rf-original-v1.json',HERE/'rf-original-v1.ld',HERE/'spec-v1.json',HERE/'build-v1.py',
           ROOT/S['firmware'],ROOT/S['reader'],ROOT/S['curation_checker'],ROOT/K['curation'],llvm/'ld.lld.exe']
    for mode in ['c','cpp']:paths+=prepared(mode)[3]
    return {key(p,llvm):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}
def audit(path,mode):
    rows,controls,objects,_,proofs=prepared(mode)
    e=N['elf'](path);base=K['range_start'];sec=e.section('.rf_code')
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonexecutable RISC-V ET_REL without PH')
    need(sec['address']==0 and sec['size']==1550 and sec['flags']==6 and sec['type']==1,'Actual VMA-zero RF section andoriginal relative extent')
    need({s['index']for s in e.sections if s['flags']&2 and s['size']}=={sec['index']},'Only original RF code allocation')
    gs=[s for s in e.symbols if s['info']>>4];gm={s['name']:s for s in gs}
    expected={r['name']for r in rows}|set(K['aliases'])|set(K['external_original_PCs'])
    need(len(gs)==len(gm)and set(gm)==expected and all(s['section']!=0xfff1 for s in gs),'Exact genuine globals;no ABS providers')
    for r in rows:
        f=gm[r['name']]
        need(f['info']==18 and f['other']==0 and f['size']==r['bytes']and f['section']==sec['index']and
             f['value']==r['start']-base,'Every real region at its original relative offset')
    for name,target in K['aliases'].items():
        a=gm[name];b=gm[target]
        need(a['info']==18 and a['other']==0 and a['size']==0 and a['section']==b['section']and a['value']==b['value'],
             'Five aliases own real matching bodies')
    und=sorted(name for name,f in gm.items()if not f['section'])
    need(und==sorted(K['external_original_PCs'])and all(gm[n]['info']==16 and gm[n]['value']==0 for n in und),'Three honest external provider gaps')
    wanted=Counter((x['PC']-base,x['type'],0,x['target'])for x in controls)
    actual=Counter((r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name'])for r in e.relocations)
    need(wanted==actual and len(e.relocations)==56 and all(r['section']==sec['index']for r in e.relocations),'All owned typed reference roles')
    raw=e.data(sec);fw=(ROOT/S['firmware']).read_bytes();original=fw[base-0x8000:K['range_end']-0x8000]
    normalized=bytearray(raw);internal=external=0
    for edge in controls:
        off=edge['PC']-base;kind=edge['type'];width,mask=B['MASKS'][kind]
        a=int.from_bytes(raw[off:off+width],'little');b=int.from_bytes(original[off:off+width],'little')
        need(a&mask==b&mask and a&(~mask&((1<<(8*width))-1))==0,'Original control opcode/register bits')
        f=gm[edge['target']]
        if f['section']:
            target=base+f['value'];internal+=1
        else:target=K['external_original_PCs'][edge['target']];external+=1
        need(target==edge['target_PC']and B['decode_control'](original[off:off+width],edge['PC'])==(kind,target),
             'Original encoded edge target andactual internal symbol offset')
        normalized[off:off+width]=(a|B['immediate'](kind,target-edge['PC'])).to_bytes(width,'little')
    need(bytes(normalized)==original,'Every1550 RF code byte after data-only original-VA encoding')
    at=count=0
    while at<len(raw):
        width=4 if raw[at]&3==3 else 2
        need(at+width<=len(raw),'Whole native RF instruction');at+=width;count+=1
    need(count==538,'All538 original RF instructions')
    # Decode isolated adjacent AUIPC/ADDI words as address data;no register/ISA execution.
    literal=[];by_pc={r['start']:r for r in rows};off=0
    while off<len(original):
        width=4 if original[off]&3==3 else 2
        if width==4 and off+8<=len(original):
            a=int.from_bytes(original[off:off+4],'little');b=int.from_bytes(original[off+4:off+8],'little')
            if a&0x7f==0x17 and b&0x707f==0x13 and (a>>7&31)==(b>>7&31)==(b>>15&31):
                hi=a&0xfffff000;hi=hi-0x100000000 if hi&0x80000000 else hi
                lo=b>>20;lo=lo-4096 if lo&0x800 else lo
                pc=base+off;target=(pc+hi+lo)&0xffffffff
                if base<=target<K['range_end']:
                    need(target in by_pc,'Original local literal points at real region')
                    need(raw[off:off+8]==original[off:off+8],'Actual native literal words unchanged')
                    owner=by_pc[target]['name'];native_pc=sec['address']+off;native_target=(native_pc+hi+lo)&0xffffffff
                    need(native_target==sec['address']+gm[owner]['value'],'Actual native relative literal owns real target')
                    literal.append(dict(original_AUIPC_PC=pc,original_ADDI_PC=pc+4,original_target=target,native_AUIPC_PC=native_pc,native_target=native_target,owner=owner))
        off+=width
    need({0x17476,0x174ee}.issubset({x['original_target']for x in literal}),'Corrected constructor literals correspond toactual relative layout')
    return dict(passed=True,mode=mode,ELF_type='ET_REL',program_headers=0,original_address_origin=base,native_section_VMA=sec['address'],
        code_bytes=1550,original_instructions=538,real_FUNC_regions=103,true_entry_aliases=5,RELA=56,
        internal_reference_sites_owned=internal,external_reference_sites_unbound=external,UND=und,
        original_VA_encoded_bytes_equal=True,compiled_unit_original_byte_audits=proofs,
        local_literal_address_correspondence=literal,original_relative_offsets_verified=True,absolute_original_VMA_placement_proved=False,
        final_image_or_hardware_placement_proved=False,external_provider_placement_proved=False,
        readonly_table1AAE8_included=False,installed_ROM_ABI_or_IRQ_proved=False,
        component_sha256=sha(path),target_executed=False,HOST_model_executed=False,ISA_emulated=False,
        hardware_accessed=False,network=False,firmware_BIN_generated=False,firmware_ready=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    need(sha(ROOT/S['firmware'])==S['firmware_sha256']and sha(ROOT/S['reader'])==S['reader_sha256'],'Original firmware/parser')
    need(sha(llvm/'ld.lld.exe')==S['tools']['ld.lld.exe']and sha(ROOT/K['curation'])==K['curation_sha256'],'Pinned linker/current source proof')
    before=inputs(llvm);out=(a.replay or a.output).resolve();need(out.parent==HERE/'build','Owned original RF output')
    if a.replay:
        saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==before,'Every original-RF input unchanged')
        for m in ['c','cpp']:
            need(saved['modes'][m]['artifacts']==inventory(out/m)and saved['modes'][m]['result']==audit(out/m/'UNRESOLVED-RF-RELATIVE-LAYOUT.o',m),'Actual original-RF replay')
        print(json.dumps(dict(passed=True,languages=['c','cpp'],original_RF_bytes=1550,relative_layout_only=True,target_executed=False)));return
    need(not out.exists(),'Create-only original RF output')
    report=dict(schema='TSL9-original-address-RF-native-proof-v1',inputs=before,modes={})
    for m in ['c','cpp']:
        folder=out/m;folder.mkdir(parents=True);output=folder/'UNRESOLVED-RF-RELATIVE-LAYOUT.o'
        argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'rf-original-v1.ld')]+[str(p)for p in prepared(m)[2]]+['-o',str(output)]
        result=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120)
        (folder/'link.log').write_bytes(result.stdout+result.stderr);need(result.returncode==0,'Native RF composition failed;local log retained')
        facts=audit(output,m);(folder/'verification.json').write_bytes(encoded(facts))
        report['modes'][m]=dict(result=facts,artifacts=inventory(folder))
        print(json.dumps({k:v for k,v in facts.items()if k not in ['compiled_unit_original_byte_audits','local_literal_address_correspondence']}|dict(literal_sites=len(facts['local_literal_address_correspondence']))))
    need(before==inputs(llvm),'Original RF inputs unchanged')
    (out/'measurement.json').write_bytes(encoded(report))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,OSError,AssertionError,subprocess.SubprocessError)as e:
        print(json.dumps(dict(passed=False,error_label=str(e)if isinstance(e,ValueError)else'Local RF proof failure;values withheld')));raise SystemExit(1)
