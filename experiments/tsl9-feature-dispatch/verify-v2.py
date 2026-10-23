#!/usr/bin/env python3
"""V2 checks actual source artifacts with strict symbol roles; static data only."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B = runpy.run_path(str(HERE/'build-v2.py'))
S = B['S']
need,sha = B['need'],B['sha']
need(sha(ROOT/S['reader']) == S['reader_sha256'],'Frozen bounded ELF reader')
E = runpy.run_path(str(ROOT/S['reader']))['ELF']
DEFS = {n:(a,z) for u in S['units'] for n,a,z in u['definitions']}
TABLES = {t['name']:t for t in S['tables']}
MASKS = {16:(4,0x01fff07f),17:(4,0x00000fff),44:(2,0xe383),45:(2,0xe003),23:(4,0xfff),24:(4,0xfffff)}
EXTERNAL = sorted({r[3] for u in S['units'] for r in u['relocations']
                   if r[3] not in DEFS and r[3] not in TABLES and not r[3].startswith('.L')})


def functions(e):
    return [f for f in e.symbols if f['info']&15 == 2]


def canonical(e,names,tables):
    need(e.header[0] == 1 and e.header[3] == 0 and e.header[6] == 1 and not e.program_headers,'Diagnostic RV32 RVC ET_REL only')
    need(len(functions(e)) == len(names) and {f['name'] for f in functions(e)} == set(names),'Exact genuine FUNC inventory')
    need(all(f['info'] == 18 and f['other'] == 0 and f['size'] for f in functions(e)),'Strong visible nonempty FUNC')
    globals_ = [s for s in e.symbols if s['info']>>4 and s['name']]
    need(not any(s['section'] == 0xfff1 for s in globals_),'No global absolute symbol under any name')
    need(len({s['name'] for s in globals_}) == len(globals_),'Every global symbol name is unique')
    need(all(s['section'] == 0 or (s['info'] == 18 and s['name'] in names) or (s['info'] == 17 and s['name'] in tables) for s in globals_),'Every defined global has its genuine FUNC or OBJECT role')
    need({s['name'] for s in e.symbols if s['info']>>4 and s['section'] != 0} == set(names)|set(tables),'No extra global definitions or ABS providers')
    need(all((s['info'],s['other'],s['value'],s['size']) == (16,0,0,0) for s in e.symbols if s['name'] and s['section'] == 0),'Canonical true UND providers')


def body(e,f):
    s = e.sections[f['section']]
    at = f['value']-s['address']
    need(0 <= at <= s['size']-f['size'],'FUNC entirely inside owned section')
    return e.data(s)[at:at+f['size']]


def edges(e,f):
    sec = e.sections[f['section']]
    start = f['value']-sec['address']
    out = []
    for r in e.relocations:
        if r['section'] != sec['index'] or not start <= r['offset'] < start+f['size']:
            continue
        symbol = e.symbols[r['symbol']]
        target = symbol['name']
        if not symbol['info']>>4:
            owned = [v for v in functions(e) if v['section'] == symbol['section'] and v['value'] <= symbol['value'] < v['value']+v['size']]
            need(len(owned) == 1 and symbol['info'] == 0 and symbol['other'] == symbol['size'] == 0,'Local PC anchor belongs to one genuine FUNC')
            target = (target,owned[0]['name'],symbol['value']-owned[0]['value'])
        out.append((r['offset']-start,r['type'],target,r['addend']))
    return sorted(out,key=lambda x:(x[0],x[1]))


def target_va(name):
    if name in DEFS:
        return DEFS[name][0]
    if name in TABLES:
        return TABLES[name]['address']
    need(name in EXTERNAL and name.startswith('tsl9_feature_external_'),'Known actual direct-provider label')
    return int(name.rsplit('_',1)[1],16)


def sx(v,bits):
    return v-(1<<bits) if v&(1<<(bits-1)) else v


def encoded_control(word,kind,pc,target):
    delta = target-pc
    if kind == 17:
        need(delta%2 == 0 and -(1<<20) <= delta < (1<<20),'JAL displacement range')
        return (word&0xfff)|((delta>>20&1)<<31)|((delta>>1&1023)<<21)|((delta>>11&1)<<20)|((delta>>12&255)<<12)
    if kind == 16:
        need(delta%2 == 0 and -(1<<12) <= delta < (1<<12),'BRANCH displacement range')
        return (word&0x01fff07f)|((delta>>12&1)<<31)|((delta>>5&63)<<25)|((delta>>1&15)<<8)|((delta>>11&1)<<7)
    if kind == 44:
        need(delta%2 == 0 and -256 <= delta < 256,'RVC BRANCH displacement range')
        return (word&0xe383)|((delta>>8&1)<<12)|((delta>>3&3)<<10)|((delta>>6&3)<<5)|((delta>>1&3)<<3)|((delta>>5&1)<<2)
    need(kind == 45 and delta%2 == 0 and -2048 <= delta < 2048,'RVC JUMP displacement range')
    return (word&0xe003)|((delta>>11&1)<<12)|((delta>>4&1)<<11)|((delta>>8&3)<<9)|((delta>>10&1)<<8)|((delta>>6&1)<<7)|((delta>>7&1)<<6)|((delta>>1&7)<<3)|((delta>>5&1)<<2)


def table_gate(e,t,section_name):
    sec = e.section(section_name)
    symbols = [s for s in e.symbols if s['name'] == t['name']]
    need(len(symbols) == 1,'Unique strong table OBJECT')
    sym = symbols[0]
    need((sym['info'],sym['other'],sym['section'],sym['value'],sym['size']) == (17,0,sec['index'],0,t['bytes']),'Exact table OBJECT type/owner/size')
    need((sec['type'],sec['flags'],sec['address'],sec['size'],sec['align']) == (1,2,0,t['bytes'],4),'Exact read-only metadata allocation')
    need(e.data(sec) == bytes(t['bytes']),'Canonical symbolic data placeholders')
    actual = sorted((r['offset'],r['type'],e.symbols[r['symbol']]['name'],r['addend']) for r in e.relocations if r['section'] == sec['index'])
    names_by_va = {a:n for n,(a,z) in DEFS.items()}
    expected = sorted([(4*i,35,names_by_va[a],0) for i,a in enumerate(t['targets'])]+
                      [(4*i,39,t['name'],0) for i in range(len(t['targets']))])
    need(actual == expected,'Every genuine signed-relative table binding')
    relocated = b''.join(((a-t['address'])&0xffffffff).to_bytes(4,'little') for a in t['targets'])
    return sec,relocated


def native(raw,u,firmware):
    e = E(raw)
    defs = {n:(a,z) for n,a,z in u['definitions']}
    owned_tables = [t for t in S['tables'] if any(s['name'] == t['name'] and s['section'] != 0 for s in e.symbols)]
    canonical(e,defs,[t['name'] for t in owned_tables])
    actual = sorted([e.sections[r['section']]['name'],r['offset'],r['type'],e.symbols[r['symbol']]['name'],r['addend']] for r in e.relocations)
    need(actual == u['relocations'],'Complete exact typed relocation inventory')
    allocations = set()
    reencoded = {}
    for f in functions(e):
        address,size = defs[f['name']]
        sec = e.sections[f['section']]
        need((sec['type'],sec['flags'],sec['address'],sec['size'],sec['align'],sec['name'],f['value'],f['size']) ==
             (1,6,0,size,2,'.text.'+f['name'],0,size),'Exact native FUNC allocation/owner/extent')
        allocations.add(sec['index'])
        original = firmware[address-0x8000:address-0x8000+size]
        data = bytearray(body(e,f))
        mask = bytearray([255]*size)
        for at,kind,target,addend in edges(e,f):
            need(kind in MASKS and addend == 0,'Known original relocation type')
            width,bits = MASKS[kind]
            need(0 <= at <= size-width and all(v == 255 for v in mask[at:at+width]),'Disjoint complete relocation fields')
            word = int.from_bytes(data[at:at+width],'little')
            need(word&(~bits&((1<<(width*8))-1)) == 0,'Canonical zero symbolic instruction displacement')
            mask[at:at+width] = bits.to_bytes(width,'little')
            if kind not in (23,24):
                need(isinstance(target,str),'Direct control uses real provider/region')
                replacement = encoded_control(word,kind,address+at,target_va(target))
            elif kind == 23:
                need(isinstance(target,str) and target in TABLES,'HI20 uses real table OBJECT')
                replacement = (word&0xfff)|((((target_va(target)-(address+at)+0x800)>>12)&0xfffff)<<12)
            else:
                need(isinstance(target,tuple) and target[1] == f['name'] and target[2] == at-4,'LO12 uses same FUNC HI20 anchor')
                hi = next((v for v in edges(e,f) if v[0] == at-4 and v[1] == 23),None)
                need(hi is not None and isinstance(hi[2],str) and hi[2] in TABLES,'Genuine matching HI20/LO12 table pair')
                delta = target_va(hi[2])-(address+at-4)
                replacement = (word&0xfffff)|((delta&4095)<<20)
            data[at:at+width] = replacement.to_bytes(width,'little')
        need(all((a^b)&m == 0 for a,b,m in zip(body(e,f),original,mask)),'Every original nonrelocation bit')
        need(bytes(data) == original,'Data-only relocation encoding reproduces every original code byte')
        reencoded[f['name']] = bytes(data)
    for t in owned_tables:
        sec,data = table_gate(e,t,t['section'])
        allocations.add(sec['index'])
        need(data == firmware[t['address']-0x8000:t['address']-0x8000+t['bytes']],'Every original relative table word')
    need(allocations == {s['index'] for s in e.sections if s['flags']&2 and s['size']},'All and only proved code/table allocations')
    return e,reencoded


def linked(raw,natives,parent=None):
    e = E(raw)
    old = {} if parent is None else {f['name']:(parent,f) for f in functions(parent)}
    selected = {f['name']:(n,f) for n in natives.values() for f in functions(n)}
    need(not set(old)&set(selected),'No duplicate parent/dispatch providers')
    canonical(e,set(old)|set(selected),TABLES)
    allocations = set()
    if parent is None:
        sections = [('.getter',0x829e,0x82a8),('.dispatch',0x14d2e,0x154a6)]
        positions = {}
        for name,lo,hi in sections:
            sec = e.section(name)
            need((sec['type'],sec['flags'],sec['address'],sec['size'],sec['align']) == (1,6,0,hi-lo,2),'Exact diagnostic original-region code extent; VMA remains zero')
            allocations.add(sec['index'])
            for n,(address,size) in DEFS.items():
                if lo <= address < hi:
                    positions[n] = (sec['index'],address-lo)
    else:
        sec = e.section('.feature_graph')
        need((sec['type'],sec['flags'],sec['address'],sec['size'],sec['align']) == (1,6,0,5088,2),'Exact5088B diagnostic graph')
        need(e.data(sec)[:3166] == parent.data('.channel_graph'),'Unchanged genuine3166B parent prefix')
        allocations.add(sec['index'])
        positions = {n:(sec['index'],f['value']) for n,(p,f) in old.items()}
        at = 3166
        for n,(address,size) in sorted(DEFS.items(),key=lambda x:x[1][0]):
            positions[n] = (sec['index'],at)
            at += size
        need(at == 5088,'Actual1922B source extension')
    actual = {f['name']:f for f in functions(e)}
    for n,(source,f) in {**old,**selected}.items():
        a = actual[n]
        need((a['section'],a['value'],a['size']) == (*positions[n],f['size']),'Every actual source FUNC owner/value/size')
        need(body(e,a) == body(source,f) and edges(e,a) == edges(source,f),'Every genuine source body/typed edge retained')
    for i,t in enumerate(S['tables']):
        sec,data = table_gate(e,t,'.table_'+str(i))
        allocations.add(sec['index'])
    need(allocations == {s['index'] for s in e.sections if s['flags']&2 and s['size']},'No hidden linked allocations')
    need(len(e.relocations) == (242 if parent is None else 386),'Complete linked relocation inventory')
    need(sorted(s['name'] for s in e.symbols if s['name'] and s['section'] == 0) == EXTERNAL and len(EXTERNAL) == 70,'Exactly70 genuine direct-provider frontiers')
    return e


def parent_scope(llvm,mode,manifest,curation):
    raw = subprocess.check_output(['git','-C',str(ROOT),'show',S['prior_manifest_commit']+':src/source-manifest.json'])
    need(hashlib.sha256(raw).hexdigest() == S['prior_manifest_sha256'],'Frozen previously verified complete manifest')
    old = json.loads(raw)
    expected = json.loads(raw)
    expected['files'] += [u['file_entry'] for u in S['units']]
    expected['native_units'] += [u['unit_entry'] for u in S['units']]
    need(manifest == expected,'Only exact three source/compile metadata extensions')
    p = ROOT/S['previous_curation_root']/'verification.json'
    need(sha(p) == S['previous_curation_receipt_sha256'],'Unchanged original90-comparison receipt')
    previous = json.loads(p.read_bytes())
    need(curation['results'][:90] == previous['results'],'All prior90 source projections unchanged')
    need(all(curation['artifacts'][k] == v for k,v in previous['artifacts'].items()),'All541 prior artifact identities unchanged')
    need(sha(ROOT/S['parent_checker']) == S['parent_checker_sha256'],'Frozen prior checker')
    need(sha(ROOT/'experiments/tsl9-channel-route/proof-v2.json') == '0d229e3ef457b3445d7e8b2cd9d52a2a20ce8abba9c2b4e56a93e335392485fb','Frozen transitive parent proof data')
    P = runpy.run_path(str(ROOT/S['parent_checker']))
    folder = B['parent'](mode).parent
    measurement = json.loads((folder/'measurement.json').read_bytes())
    current = P['B']['portable'](P['B']['inputs'](llvm,mode),llvm)
    keys = [k for k in current if k.replace('\\','/').endswith('/src/source-manifest.json')]
    need(len(keys) == 1,'One explicitly scoped global manifest record')
    key = keys[0]
    need(measurement['inputs'][key] == dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),'Exact historical manifest input')
    current[key] = measurement['inputs'][key]
    need(current == measurement['inputs'],'All actual parent inputs except proven three-entry manifest extension unchanged')
    for name,facts in measurement['artifacts'].items():
        need(sha(folder/name) == facts['sha256'] and (folder/name).stat().st_size == facts['bytes'],'Actual frozen parent output')
    need(sha(B['parent'](mode)) == S['parent_object_sha256'],'Actual3166B parent identity')
    natives = {}
    fw = (ROOT/S['firmware']).read_bytes()
    for unit in P['S']['units']:
        oldpath = P['B']['obj'](unit,mode)
        fresh = ROOT/S['curation_root']/unit['name']/mode/'curated/unit.o'
        need(fresh.read_bytes() == oldpath.read_bytes(),'Fresh current source equals genuine parent source object')
        natives[unit['name']] = P['native'](fresh.read_bytes(),unit,fw)[0]
    P['nominal']((folder/'ORIGINAL-PC-COMPONENT-NOT-FIRMWARE.elf').read_bytes(),fw)
    parent = P['joined'](B['parent'](mode).read_bytes(),P['E'](P['B']['parent'](mode)),natives)
    need(P['indirects'](parent) == P['P2']['indirect_transfers'],'All19 existing indirect transfers unchanged')
    return parent




def verify(llvm,folder,mode,write):
    for key in ('firmware','reader','original_reader','curation_checker','parent_checker'):
        need(sha(ROOT/S[key]) == S[key+'_sha256'],'Frozen '+key)
    for name,pin in S['tools'].items():
        need(sha(llvm/name) == pin,'Pinned tool '+name)
    need(sha(ROOT/S['curation_root']/'verification.json') == S['curation_receipt_sha256'],'Frozen actual96-comparison receipt')
    C = runpy.run_path(str(ROOT/S['curation_checker']))
    manifest = C['metadata']()
    curation = json.loads((ROOT/S['curation_root']/'verification.json').read_bytes())
    with contextlib.redirect_stdout(io.StringIO()):
        C['audit'](ROOT/S['curation_root'],curation,manifest)
    measurement = json.loads((folder/'measurement.json').read_bytes())
    need(measurement['mode'] == mode and measurement['inputs'] == B['portable'](B['inputs'](llvm,mode),llvm),'Every current actual producer input')
    commands = [dict(label=n,argv=B['portable'](a,llvm),exit=0,log_sha256=sha(folder/(n+'.log'))) for n,a in B['recipes'](llvm,folder,mode)]
    need(commands == measurement['commands'],'Actual IR/link/read command/exit/log identity')
    expected_outputs = {u['name']+'.ll' for u in S['units']}|{n+'.log' for n,a in B['recipes'](llvm,folder,mode)}|{'UNRESOLVED-ORIGINAL-ADDRESS-DISPATCH.o','UNRESOLVED-FEATURE-GRAPH.o'}
    need(set(measurement['artifacts']) == expected_outputs,'Complete actual producer artifact inventory')
    for n,facts in measurement['artifacts'].items():
        need(sha(folder/n) == facts['sha256'] and (folder/n).stat().st_size == facts['bytes'],'Actual producer artifact')
    parent = parent_scope(llvm,mode,manifest,curation)
    fw = (ROOT/S['firmware']).read_bytes()
    natives = {}
    replay = {}
    for u in S['units']:
        p = B['obj'](u,mode)
        need(sha(p) == u['native_object_sha256'][mode],'Actual current source object identity')
        n,r = native(p.read_bytes(),u,fw)
        natives[u['name']] = n;replay.update(r)
    component = linked((folder/'UNRESOLVED-ORIGINAL-ADDRESS-DISPATCH.o').read_bytes(),natives)
    full = linked((folder/'UNRESOLVED-FEATURE-GRAPH.o').read_bytes(),natives,parent)
    historical = json.loads((folder/'verification.json').read_bytes())
    need(historical['checker_sha256'] == 'f644b7ce762ad42e925a766fcd9056d08da04eb2e13a0f7dfdbaffc919325c4b' and historical['negative_controls'] == 10173,'Frozen historical v1 result; not rerun or upgraded')
    need(sha(HERE/'verify.py') == historical['checker_sha256'],'Unchanged historical checker')
    report = dict(schema='TSL9-complete-feature-dispatch-static-verification-v2',passed=True,mode=mode,
        checker_sha256=sha(Path(__file__)),contract_sha256=sha(HERE/'spec-v2.json'),
        compiled_source_units=3,FUNC=210,code_bytes=1922,dispatch_body_bytes=1912,getter_bytes=10,table_bytes=60,
        code_instructions=669,direct_control_relocations=208,PC_relative_relocations=4,table_relocations=30,total_RELA=242,
        code_and_tables_equal_after_data_only_original_VA_relocation=True,no_absolute_provider_substitutes=True,
        provider_implementations_assumed=False,relocation_arithmetic_is_ISA_emulation=False,
        component_sha256=sha(folder/'UNRESOLVED-ORIGINAL-ADDRESS-DISPATCH.o'),
        component_ELF_VMA_zero=True,component_executable=False,component_UND=EXTERNAL,
        full_graph_code_bytes=5088,full_graph_table_bytes=60,full_graph_FUNC=401,full_graph_RELA=386,full_graph_UND=EXTERNAL,
        full_graph_sha256=sha(folder/'UNRESOLVED-FEATURE-GRAPH.o'),
        prior3166_code_bytes_unchanged=True,parent_revalidation='Scoped selected-source proof with exact three-entry manifest extension; not original global-receipt replay',
        curated_comparisons=96,curated_objects=192,prior90_facts_and541_artifacts_unchanged=True,
        new_negative_controls_executed=0,historical_v1_negative_controls=10173,historical_v1_no_ABS_gate_incomplete=True,
        independent_review_continuation_stopped=True,universal_semantic_proof=False,literal_callback_dependencies=S['literal_code_pointer_dependencies'],
        existing_parent_resident_sites=17,existing_parent_internal_computed_controls=2,new_relative_table_controls=2,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,network=False,hardware_accessed=False,
        full_firmware_proved=False,hardware_OTA_proved=False,firmware_BIN_generated=False,firmware_ready=False,
        limits=['All ET_REL VMA values are zero despite original-address contract/filename; do not execute.',
                'Data-only ELF relocation encoding does not supply70 external provider implementations.',
                '1069E callback and1083C delayed-registration frontier remain unresolved beyond direct UND.',
                'Reserved S0/frame/control/PC effects are explicit architecture ports, not a universal C ABI.',
                'Installed ROM, hardware/startup/IRQ/memory/clock/OTA remain unproved.',
                'Independent review continuation stopped by safety check; no rerouting or new malformed-case execution.',
                'V2 hardens actual global symbol uniqueness/roles/ABS checks. Historical v1 negative counts do not prove these new checks.'])
    out = folder/'verification-v2.json'
    if write:
        need(not out.exists(),'Create-only formal receipt')
        out.write_bytes(B['encoded'](report))
    elif out.exists():
        need(json.loads(out.read_bytes()) == report,'Exact read-only formal receipt replay')
    print(json.dumps({k:v for k,v in report.items() if k not in ('component_UND','full_graph_UND','literal_callback_dependencies','limits')}))
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--mode',choices=['c','cpp'],required=True)
    p.add_argument('--write',action='store_true')
    a = p.parse_args()
    verify(a.tool_dir.resolve(),a.folder.resolve(),a.mode,a.write)
