#!/usr/bin/env python3
"""Read-only static proof of both integrations; --write creates new receipts."""
import argparse, contextlib, hashlib, io, json, os, re, runpy, struct, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
B=runpy.run_path(str(HERE/'build-v2.py'))
E=B['E']
S=json.loads((HERE/'proof-spec.json').read_bytes())
for n,h in S['pins'].items():B['need'](B['sha'](HERE/n)==h,'Frozen integration source '+n)
need=B['need'];sha=B['sha'];portable=B['portable']

def readback(text,expected):
    got=[]
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)',line)
        if m:got.append([int(m.group(1),16),bytes.fromhex(m.group(2)).hex()])
    need(got==expected,'Every complete LLVM address/byte row')
    return got

def artifact_inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.iterdir())
            if p.is_file() and p.name not in ('measurement.json','verification.json')}
def provenance(folder,llvm,mode,record):
    need(record['schema']=='TSL9-receive-transmit-integration-measurement-v1' and record['mode']==mode,'Actual producer schema and mode')
    need(record['inputs']==portable(B['snapshot'](llvm),llvm),'Complete current producer input set')
    expected=[]
    for label,argv in B['recipes'](folder,llvm,mode):
        expected.append(dict(label=label,argv=argv,exit=0,consumed=B['consumed'](label,folder,llvm),log_sha256=sha(folder/(label+'.log'))))
    need(record['actual_commands']==portable(expected,llvm) and B['load'](folder/'commands.json')==portable(expected,llvm),'All28 exact command labels/argv/exits/consumed bytes/logs')
    names=set()
    for u in B['SPEC']['units']:
        n=u['name'];names.update(n+s for s in ('.o','.d','.ll','-compile.log','-IR.log'))
        md=(folder/(n+'.d')).read_text(encoding='utf8').replace('\\\n',' ').replace('\\\r\n',' ').replace('\\ ','\x01').replace('\\','/')
        prefix=str(folder/(n+'.o')).replace('\\','/')
        need(md.startswith(prefix+':'),'Actual MD object target')
        deps=[x.replace('\x01',' ') for x in md[len(prefix)+1:].strip().split()]
        need(deps==[str(ROOT/u['curated_unit']).replace('\\','/'),str(llvm.parent/'lib/clang/18/include/stdint.h').replace('\\','/')],'Exact source/header dependency closure')
    names.update(['UNRESOLVED-FULL-COMPONENT.o','NOMINAL-SUBCOMPONENT-NOT-FIRMWARE.elf','commands.json','full-link.log','full-read.log','nominal-link.log','nominal-read.log'])
    need(set(artifact_inventory(folder))==names and len(names)==67,'Exact67 producer artifacts without hidden files')
    need(record['artifacts']==artifact_inventory(folder),'Actual complete artifact hashes/sizes')
    return expected

def projections(folder,full):
    e=E(full);fs={s['name']:s for s in B['funcs'](e)};got=[];names=set()
    full_rels=[[r['offset'],r['type'],e.symbols[r['symbol']]['name'],r['addend']] for r in e.relocations]
    for u in B['SPEC']['units']:
        obj=E(folder/(u['name']+'.o'));source_fs=B['funcs'](obj);section_owners={}
        need(source_fs and obj.header[0]==1,'Actual source relocatable object')
        for s in source_fs:
            need(s['name'] in fs and s['name'] not in names and s['info']>>4==1,'Each actual source owns unique strong genuine function')
            names.add(s['name']);dest=fs[s['name']]
            body=obj.data(obj.sections[s['section']])[s['value']:s['value']+s['size']]
            need(body==e.data('.full')[dest['value']:dest['value']+dest['size']],'Full partial component consumes every exact compiled body')
            section_owners[s['section']]=s
        for r in obj.relocations:
            s=section_owners[r['section']];owner=fs[s['name']]
            got.append([owner['value']+r['offset']-s['value'],r['type'],obj.symbols[r['symbol']]['name'],r['addend']])
    need(names==set(B['DEFS']) and sorted(got)==sorted(full_rels),'All107 compiled definitions and97 unchanged genuine source edges')

def rejected(fn):
    try:fn()
    except (ValueError,KeyError,IndexError,struct.error):return True
    return False

def negatives(full,nominal):
    fe,frows,_=B['full_contract'](full);ne,nrows,_=B['nominal_contract'](nominal);labels=[]
    def test(name,fn):need(rejected(fn),'Mutation escaped '+name);labels.append(name)
    for raw,e,rs,kind,fn in [(full,fe,frows,'full',B['full_contract']),(nominal,ne,nrows,'nominal',B['nominal_contract'])]:
        for addr,h in rs:
            sec=next(s for s in e.sections if s['flags']&2 and s['address']<=addr<s['address']+s['size'])
            b=bytearray(raw);b[sec['offset']+addr-sec['address']]^=1
            test(kind+'-instruction-'+hex(addr),lambda x=bytes(b),f=fn:f(x))
        symsec=next(s for s in e.sections if s['type']==2)
        for i,s in enumerate(e.symbols):
            if s['info']&15!=2 or not s['size']:continue
            b=bytearray(raw);b[symsec['offset']+16*i+12]=(s['info']&15)|0x20
            test(kind+'-weak-'+s['name'],lambda x=bytes(b),f=fn:f(x))
    for sec in fe.sections:
        if sec['type']!=4:continue
        for at in range(0,sec['size'],12):
            b=bytearray(full);b[sec['offset']+at+8]^=2
            test('full-relocation-addend-'+str(at),lambda x=bytes(b):B['full_contract'](x))
    symsec=next(s for s in fe.sections if s['type']==2)
    for i,s in enumerate(fe.symbols):
        if not s['name'] or s['section']!=0:continue
        b=bytearray(full);b[symsec['offset']+16*i+12]=(s['info']&15)|0x20
        test('full-weak-UND-'+s['name'],lambda x=bytes(b):B['full_contract'](x))
    b=bytearray(nominal);struct.pack_into('<I',b,24,0x8000)
    test('nominal-wrong-entry',lambda:B['nominal_contract'](bytes(b)))
    for n,va,z in B['SPANS']:
        b=bytearray(nominal);sec=ne.section(n);struct.pack_into('<I',b,ne.header[5]+40*sec['index']+8,7)
        test('nominal-writable-'+n,lambda x=bytes(b):B['nominal_contract'](x))
    phoff=struct.unpack_from('<I',nominal,28)[0]
    for i,p in enumerate(ne.program_headers):
        if p[0]!=1:continue
        for label,offset,value in [('writable',24,p[6]|2),('bad-alignment',28,3)]:
            b=bytearray(nominal);struct.pack_into('<I',b,phoff+i*32+offset,value)
            test('nominal-LOAD-'+str(i)+'-'+label,lambda x=bytes(b):B['nominal_contract'](x))
    need(len(labels)==1536,'All1536 bounded metadata/instruction controls')
    return labels

def inspect(folder,llvm,mode,upstream):
    record=B['load'](folder/'measurement.json');recipes=provenance(folder,llvm,mode,record)
    need(record['upstream']==upstream,'Same actual recursive source proofs')
    full=(folder/'UNRESOLVED-FULL-COMPONENT.o').read_bytes();nominal=(folder/'NOMINAL-SUBCOMPONENT-NOT-FIRMWARE.elf').read_bytes()
    for n in S['ELF_sha256']:need(sha(folder/n)==S['ELF_sha256'][n],'Complete frozen ELF metadata')
    fe,fr,typed=B['full_contract'](full);ne,nr,transfers=B['nominal_contract'](nominal)
    projections(folder,full)
    readback((folder/'full-read.log').read_text(encoding='utf8'),fr)
    readback((folder/'nominal-read.log').read_text(encoding='utf8'),nr)
    controls=negatives(full,nominal)
    return dict(schema='TSL9-receive-transmit-static-integration-proof-v1',passed=True,mode=mode,
        full=dict(bytes=1902,instructions=662,FUNC=107,RELA=97,UND=sorted(B['MISSING']),VMA=0,whole_nonrelocation_bits_equal_original=True,typed_controls=typed,ELF_sha256=sha(folder/'UNRESOLVED-FULL-COMPONENT.o')),
        nominal=dict(bytes=1588,instructions=555,FUNC=97,RELA=0,UND=0,whole_original_code_projection_equal=True,spans=B['SPANS'],direct_transfers=transfers,
            RX_LOAD_bytes=sum(p[4] for p in ne.program_headers if p[0]==1 and p[6]&1),unproved_executable_gap_bytes=66970,
            ELF_sha256=sha(folder/'NOMINAL-SUBCOMPONENT-NOT-FIRMWARE.elf')),
        full_LLVM_rows=dict(full=fr,nominal=nr),actual_commands=recipes,inputs=B['snapshot'](llvm),upstream=upstream,
        proof_inputs={str(HERE/n):sha(HERE/n) for n in ('verify.py','proof-spec.json')},
        producer_receipt_sha256=sha(folder/'measurement.json'),artifacts=artifact_inventory(folder),
        negative_controls=controls,ordinary_C_ABI_proved=False,installed_resident_identity_proved=False,
        target_executed=False,ISA_emulated=False,HOST_models_executed=False,hardware_OTA_proved=False,
        full_firmware_proved=False,BIN_generated=False,firmware_ready=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out-dir',required=True,type=Path);p.add_argument('--write',action='store_true')
    p.add_argument('--strict-firmware',action='store_true');p.add_argument('--llvm-bin',type=Path,default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    a=p.parse_args();out=a.out_dir.resolve();llvm=a.llvm_bin.resolve();need(out.is_relative_to(HERE/'build') and out!=HERE/'build','Owned result')
    with contextlib.redirect_stdout(io.StringIO()):proofs=B['upstream'](llvm)
    before=B['snapshot'](llvm);results=[]
    for mode in ('c','cpp'):
        folder=out/mode;value=inspect(folder,llvm,mode,proofs);data=B['encoded'](value,llvm);dest=folder/'verification.json'
        if a.write:need(not dest.exists(),'Create-only formal receipt');dest.write_bytes(data)
        else:need(dest.read_bytes()==data,'Complete read-only formal replay')
        results.append(dict(language=mode,receipt_sha256=hashlib.sha256(data).hexdigest(),negative_controls=len(value['negative_controls'])))
    need(before==B['snapshot'](llvm),'All producer source/tool inputs unchanged')
    print(json.dumps(dict(passed=True,results=results,full_bytes=1902,full_UND=4,nominal_bytes=1588,nominal_UND=0,firmware_ready=False)))
    return 1 if a.strict_firmware else 0
if __name__=='__main__':raise SystemExit(main())
