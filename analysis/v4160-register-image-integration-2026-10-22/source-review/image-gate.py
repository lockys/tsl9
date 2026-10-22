"""Independent data-only source image context; reuse the immutable prior ELF gate."""
from pathlib import Path
import hashlib
import importlib.util
import json

MODEL='experiments/tsl9-v4160-register-image-integration'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def case(root,name):
    return next(p for p in (root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def context(root,firmware,manifest_sha):
    oldcase=case(root,'v4160-flash-image-integration-2026-10-22')/'source-review';need(sha(oldcase/'seal.json')=='2555cdd38cead5ee55288f3342b4a3db5cc54dd3c42ffca0e28529e3ad5d3f57','Closed independent original-role/reference review');oldseal=read(oldcase/'seal.json')
    for name in ('inspect-image.py','source-constraints.json'):
        need(sha(oldcase/name)==oldseal['members'][name]['sha256'],'Immutable independent role/ELF gate '+name)
    G=module('immutable_source_image_gate',oldcase/'inspect-image.py');q=read(oldcase/'source-constraints.json');m=read(root/'experiments/tsl9-v4160-irq-image-integration/source-manifest.json');need(sha(root/'experiments/tsl9-v4160-irq-image-integration/source-manifest.json')==q['original_manifest_sha256'],'Original691-section source layout')
    previous_path=root/'experiments/tsl9-v4160-flash-image-integration/source-manifest.json';need(sha(previous_path)=='8463f01466e180f4a70127413939469d5124a85cdeab5d0f0e90d438c765c3d9','Prior compiler body ledger');previous=read(previous_path)
    prefix=case(root,'v4160-flash-register-prefix-2026-10-22')/'source-review';need(sha(prefix/'seal.json')=='09e0a9433b6b72f20ab4b35c45762c6d30e8917c689940e9ae315e2ea4de80e1','Closed independent actual current Flash component review');pin=read(prefix/'seal.json')['members']['final-C-review.json']['sha256'];need(sha(prefix/'final-C-review.json')==pin,'Actual component row ledger');flash={r['entry']:bytes.fromhex(''.join(x['raw_hex'] for x in r['candidate_rows'])) for r in read(prefix/'final-C-review.json')['candidate_results']}
    path=root/MODEL/'source-manifest.json';need(sha(path)==manifest_sha,'Reviewed new source/scheduling ledger');n=read(path);raw=firmware.read_bytes();need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==q['original_firmware_sha256'],'Original ID2966 raw bytes as validation reference')
    need(n['allocations']==m['allocations'] and n['section_metadata']==m['section_metadata'] and n['section_relative_bindings']==m['section_relative_bindings'],'All691 original allocations and53 relative bindings')
    names={r['name'] for r in q['selected']};need(len(n['selected_sections'])==11 and {r['name'] for r in n['selected_sections']}==names,'Exact original11 typed owners');retained=set(m['allocations'])-names;hashes={k:r['sha256'] for k,r in n['retained_storage'].items()};need(set(hashes)==retained and G.digest(hashes)==q['retained_raw_hashes_digest'],'Exact680 independently anchored retained storage hashes')
    need(len(n['source_files'])==76 and len(n['source_units'])==34,'Exact native source inventory')
    for name,pin in n['source_files'].items():need(sha(root/name)==pin,'Current native project input '+name)
    for name,pin in n['frame_schedule_source_files'].items():need(sha(root/name)==pin,'Current explicit scheduling pipeline input '+name)
    need(n['frame_schedule_source_files']['experiments/tsl9-v4160-frame-schedule/schedule.py']=='dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d' and n['frame_schedule_source_files']['experiments/tsl9-v4160-frame-schedule/frame-policy.json']=='2af7789f91ceabca11fc29eb264991b96f40664555cdfe08964284f1470a694d','Exact reviewed scheduler and policy')
    native={};compiler={}
    for row in n['selected_sections']:
        name=row['name'];source=next(x for x in q['selected'] if x['name']==name);need(all(row[k]==v for k,v in source.items()) and row['new_C_symbol']==q['public'][name],'Original extent/owner/provider role')
        start=row['originalVA']-0x8000;body=raw[start:start+row['bytes']];need(row['original_bytes']==row['native_linked_bytes']==body.hex(),'Scheduled linked native bytes equal actual original allocation')
        before=flash[row['originalVA']] if row['family']=='Flash' else bytes.fromhex(next(x for x in previous['selected_sections'] if x['name']==name)['native_linked_bytes']);need(row['compiler_linked_bytes']==before.hex(),'Compiler-only body anchored to actual sealed previous/current native evidence')
        rels=[r for r in q['new_owned'] if r['owner']==name];need(hashlib.sha256(G.canonical_code(before,rels)).hexdigest()==row['compiler_native_object_sha256'] and hashlib.sha256(G.canonical_code(body,rels)).hexdigest()==row['native_object_sha256'],'Separate pre/post partial body hashes derived only by declared JAL normalization');native[name]=body;compiler[name]=before
    need(n['expected_differences']==[],'No expected original image differences')
    for r in q['filters']:
        selected=[x for x in q['selected'] if x['producer']==r['path']];need(hashlib.sha256(G.filter_intervals((root/r['path']).read_bytes(),selected)).hexdigest()==r['sha256'],'Independent raw source interval filtering')
    parser=case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py';need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Bounded immutable ELF parser')
    return {'G':G,'E':module('new_image_ELF_data',parser).ELF,'m':m,'new_manifest':n,'selected':q['selected'],'names':names,'retained':retained,'retained_hashes':hashes,'outside_sha256':q['outside_RELA_sha256'],'incoming':q['incoming'],'new_owned':q['new_owned'],'public':q['public'],'native':native,'compiler_native':compiler,'expected':raw,'original_bytes':raw,'expected_named_semantic_sha256':q['expected_named_semantic_sha256'],'filters':q['filters'],'original_baseline_archives_replayed':False}
