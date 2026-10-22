#!/usr/bin/env python3
"""Partial provider closure only: retained real objects -> ld.lld -r ET_REL."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import uuid
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
LD = 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'
PARSER = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
BASE = {'c':'85c674487c0bf2b0bbcbc3f0f5607d82dd07014acaf0634cfd45525ccdcdf456',
        'cpp':'e0407c603786c3b747f3a8646a142a1b0ea8c8e47921f5058a31f0577a1a2f4b'}
NATIVE = 'd75a75e0df88a7033632ad9f46c7c24bbd48357ecce4b29b5eb6c99effd7463d'
ROM = '__tsl9v4160_rom_entry'
ENTRY = 'tsl9_ota_handler_native_9c4a'
OLD = '__tsl9v4160_ota_code_9c4a'
NAMES = {'__tsl9v4160_ota_code_92f2','__tsl9v4160_call_9c0a','__tsl9v4160_call_9124',
         '__tsl9v4160_ota_code_13f66','__tsl9v4160_conditional_code_13e98',
         '__tsl9v4160_ota_code_9b8e','__tsl9v4160_ota_code_8e18',
         '__tsl9v4160_ota_code_9ee0','__tsl9v4160_captured_body_99e8'}

def H(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value, message):
    if not value: raise ValueError(message)
def read(path): return json.loads(path.read_bytes())
def parser_at(root):
    path = next(p for p in (root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py', root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py') if p.is_file())
    need(H(path) == PARSER, 'Pinned bounded ELF parser')
    return path
def undefined(e): return {s['name'] for s in e.symbols if s['index'] == 0 and s['name']}
def symbol(e, name):
    found = [s for s in e.symbols if s['name'] == name]
    need(len(found) == 1, 'One actual symbol '+name)
    return found[0]
def role(e, s):
    section = e.sections[s['index']]['name'] if 0 < s['index'] < len(e.sections) else s['index']
    return (s['name'], section, s['value'], s['size'], s['info'], s['other'])
def relocation(e, r, providers=None):
    s = r['symbol']
    return (r['owner'], r['offset'], r['type'], r['addend'], *(providers[s['name']] if providers and s['name'] in providers else role(e, s)))
def allocations(e):
    selected = [s for s in e.sections if s['flags']&2 and s['size']]
    need(len({s['name'] for s in selected})==len(selected), 'Unambiguous allocated section owners')
    return {s['name']:(s['type'],s['flags'],s['alignment'],s['size'],None if s['type']==8 else hashlib.sha256(e.data(s)).hexdigest()) for s in selected}
def receipt_input(path, receipt, name, expected):
    data = read(receipt)
    need(data['passed'] and data['mode'] in BASE, 'Successful existing input generation metadata')
    need(path.name == name and path.resolve().is_relative_to(receipt.parent.resolve()), 'Exact input artifact inside its retained generation')
    key = path.resolve().relative_to(receipt.parent.resolve()).as_posix()
    need(data['artifacts'][key] == dict(bytes=path.stat().st_size,sha256=H(path)) and H(path)==expected, 'Pinned real input object and its actual receipt artifact')
    return data['mode']
def checks(root, base, native, output):
    E = runpy.run_path(str(parser_at(root)))['ELF']; b,n,o = [E(p) for p in (base,native,output)]
    need(b.kind==n.kind==o.kind==1 and b.flags==n.flags==o.flags==1, 'Real RV32/RVC ET_REL inputs/output')
    need(undefined(b)=={ROM} and undefined(n)==NAMES and undefined(o)=={ROM}, 'Nine native UND bind; sole real ROM UND remains')
    providers = {}
    details = []
    for name in sorted(NAMES):
        before = symbol(b,name); after = symbol(o,name)
        need(0<before['index']<len(b.sections) and b.sections[before['index']]['flags']&2, 'Real allocated baseline provider '+name)
        need(role(b,before)==role(o,after), 'Provider role retained without ABS/alias '+name)
        providers[name]=role(b,before)
        details.append(dict(name=name,section=providers[name][1],value=before['value'],size=before['size'],info=before['info'],other=before['other']))
    ba,na,oa=allocations(b),allocations(n),allocations(o)
    need(len(ba)==691 and len(na)==1 and not(set(ba)&set(na)) and oa==dict(ba,**na), 'All real691+1 allocations retain bytes/type/flags/alignment/size; no padding/provider replacement')
    expected = Counter(relocation(b,r) for r in b.relocations)+Counter(relocation(n,r,providers) for r in n.relocations)
    need(Counter(relocation(o,r) for r in o.relocations)==expected, 'Complete relocation union; exactly nine symbolic provider-role resolutions')
    old = symbol(o,OLD); fresh = symbol(o,ENTRY)
    need(role(b,symbol(b,OLD))==role(o,old) and o.sections[old['index']]['size']==530, 'Original raw530 owner retained')
    need(fresh['info']==18 and fresh['other']==0 and fresh['size']==568 and fresh['value']==0 and o.sections[fresh['index']]['size']==568, 'Separate truthful new FUNC568 owner')
    need(o.function_bytes(fresh)==n.function_bytes(symbol(n,ENTRY)), 'Native bytes unchanged by partial link')
    incoming = [r for r in b.relocations if r['symbol']['index']==symbol(b,OLD)['index'] and r['owner']!=b.sections[symbol(b,OLD)['index']]['name']]
    need(incoming and all(r['symbol']['name']!=ENTRY for r in b.relocations), 'Original caller still refers to original handler; no reroute')
    return dict(base_allocations=len(ba),native_allocations=len(na),output_allocations=len(oa),base_relocations=len(b.relocations),native_relocations=len(n.relocations),output_relocations=len(o.relocations),providers=details,remaining_undefined=sorted(undefined(o)),original_handler_owner=o.sections[old['index']]['name'],original_handler_bytes=530,native_handler_owner=o.sections[fresh['index']]['name'],native_handler_bytes=568,original_handler_incoming_relocations=len(incoming),entry_rerouted=False,final_image=False,JAL_applied_or_range_checked=False,installed_ABI_proved=False)
def replay(root, receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=read(receipt)
    need(r['passed'] and r['mode'] in BASE, 'Actual partial-link generation')
    paths={k:Path(v) for k,v in r['paths'].items()}
    need(H(paths['ld'])==LD and r['source_pins']=={str(p):H(p) for p in [Path(__file__).resolve(),parser_at(root),Path(sys.executable).resolve()]}, 'Current exact runner/parser/runtime/tool identities')
    mode=receipt_input(paths['base'],paths['base_receipt'],'source-integrated.o',BASE[r['mode']])
    need(mode==receipt_input(paths['native'],paths['native_receipt'],'ota_handler.o',NATIVE)==r['mode'], 'Same language input receipts')
    need(r['input_pins']=={str(p):H(p) for k,p in paths.items() if k!='ld'}, 'Actual retained input receipt/object identities')
    need(r['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt}, 'Complete actual output/log inventory')
    argv=[str(paths['ld']),'--no-relax','-r',str(paths['base']),str(paths['native']),'-o',str(folder/'PROVIDER-CLOSURE-ONLY.o')]
    need(r['command']==dict(argv=argv,exit=0,log='partial-link.log',log_sha256=H(folder/'partial-link.log')), 'Exact sole ld.lld -r command and successful actual log')
    actual=checks(root,paths['base'],paths['native'],folder/'PROVIDER-CLOSURE-ONLY.o')
    need(actual==r['checks'], 'Read-only real partial provider closure replay')
    return dict(passed=True,receipt=str(receipt),sha256=H(receipt),mode=r['mode'],actual_partial_link_artifacts_read=True,provider_bindings=9,remaining_undefined=actual['remaining_undefined'],output_allocations=actual['output_allocations'],output_relocations=actual['output_relocations'],entry_rerouted=False,final_image=False,JAL_applied_or_range_checked=False,target_execution=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--replay',type=Path)
    for name in ('base-object','base-receipt','native-object','native-receipt','ld','build-root'):p.add_argument('--'+name,type=Path)
    a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(all(getattr(a,n) is None for n in ('base_object','base_receipt','native_object','native_receipt','ld','build_root')), 'Readonly replay rejects fresh options')
        print(json.dumps(replay(root,a.replay)));return
    need(all(getattr(a,n) is not None for n in ('base_object','base_receipt','native_object','native_receipt','ld')), 'Supply both real objects/receipts and pinned ld.lld explicitly')
    base,native,br,nr,ld=[x.resolve() for x in (a.base_object,a.native_object,a.base_receipt,a.native_receipt,a.ld)]
    mode=read(br)['mode'];need(mode in BASE and H(ld)==LD, 'Supported input mode and pinned local linker')
    receipt_input(base,br,'source-integrated.o',BASE[mode]);need(receipt_input(native,nr,'ota_handler.o',NATIVE)==mode,'Same mode')
    folder=a.build_root.resolve() if a.build_root else HERE/'build'/('partial-'+uuid.uuid4().hex)
    need(folder.is_relative_to(HERE/'build') and folder!=HERE/'build' and not folder.exists(), 'Create-only owned partial output')
    folder.mkdir(parents=True);paths=dict(base=base,native=native,base_receipt=br,native_receipt=nr,ld=ld)
    pins={str(v):H(v) for k,v in paths.items() if k!='ld'};source_pins={str(v):H(v) for v in [Path(__file__).resolve(),parser_at(root),Path(sys.executable).resolve()]}
    argv=[str(ld),'--no-relax','-r',str(base),str(native),'-o',str(folder/'PROVIDER-CLOSURE-ONLY.o')]
    done=subprocess.run(argv,cwd=folder,capture_output=True,timeout=120,env=dict(os.environ,TMP=str(folder),TEMP=str(folder)))
    log=folder/'partial-link.log';log.write_bytes(done.stdout+done.stderr)
    need(done.returncode==0,'Actual partial linker rejected: '+str(log))
    need(pins=={str(v):H(v) for k,v in paths.items() if k!='ld'} and H(ld)==LD and source_pins=={n:H(Path(n)) for n in source_pins}, 'Stable before/after actual inputs/tool/runner')
    r=dict(schema='TSL9-real-provider-partial-link-v1',passed=True,mode=mode,paths={k:str(v) for k,v in paths.items()},input_pins=pins,source_pins=source_pins,command=dict(argv=argv,exit=done.returncode,log=log.name,log_sha256=H(log)),checks=checks(root,base,native,folder/'PROVIDER-CLOSURE-ONLY.o'),artifacts={v.relative_to(folder).as_posix():dict(bytes=v.stat().st_size,sha256=H(v)) for v in folder.rglob('*') if v.is_file()},target_execution=False,final_image=False)
    receipt=folder/'verification.json';receipt.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(replay(root,receipt)))
if __name__=='__main__':main()
