#!/usr/bin/env python3
"""Stricter static proof over unchanged integration-v2 compiler artifacts."""
import argparse, contextlib, hashlib, io, json, os, runpy, struct, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
V=runpy.run_path(str(HERE/'verify.py'))
B=V['inspect'].__globals__['B']
need=B['need'];sha=B['sha']
old_nominal=B['nominal_contract']
S=V['S']

def nominal(raw):
    e,rows,transfers=old_nominal(raw)
    need(e.program_headers==S['nominal_LOADs'],'Exact complete PHDR inventory and LOAD extents')
    return e,rows,transfers

def artifacts(folder):
    # The new receipt is explicit proof output, not a producer artifact.
    excluded={'measurement.json','verification.json','verification-v2.json'}
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file() and p.name not in excluded}

# Configure only this fresh verifier instance; frozen sources are unchanged.
B['nominal_contract']=nominal
V['provenance'].__globals__['artifact_inventory']=artifacts

def receipts():
    paths=[B['T']['HERE']/'build/nominal-v1'/mode/'verification.json' for mode in ('c','cpp')]
    paths += [ROOT/'experiments/tsl9-peripheral-dispatch-component/build/component-v2'/mode/'verification.json' for mode in ('c','cpp')]
    paths += [ROOT/'build/curated-source/resident-copy-arch-20261023-v1/verification.json']
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}

def closure(llvm):
    return dict(producer=B['snapshot'](llvm),
        tagged_chain=B['T']['snapshot'](llvm),
        peripheral_composition=B['P'].inputs(ROOT,llvm),
        upstream_receipts=receipts(),
        current_proof={str(HERE/n):dict(bytes=(HERE/n).stat().st_size,sha256=sha(HERE/n)) for n in ('verify.py','verify-v2.py','proof-spec.json')})

def extra_controls(raw):
    e,rows,transfers=nominal(raw)
    offset=struct.unpack_from('<I',raw,28)[0];labels=[]
    rx=next(i for i,p in enumerate(e.program_headers) if p[0]==1 and p[6]&1)
    b=bytearray(raw)
    struct.pack_into('<I',b,offset+32*rx+16,e.program_headers[rx][4]+4)
    struct.pack_into('<I',b,offset+32*rx+20,e.program_headers[rx][5]+4)
    need(V['rejected'](lambda:nominal(bytes(b))),'Expanded RX extent rejected without whole-ELF hash')
    labels.append('expanded-RX-LOAD-rejected')
    i=next(i for i,p in enumerate(e.program_headers) if p[0]==0x6474e551)
    b=bytearray(raw);struct.pack_into('<8I',b,offset+32*i,1,0,0x20000000,0x20000000,52,52,5,4096)
    need(V['rejected'](lambda:nominal(bytes(b))),'Extra RX LOAD rejected without whole-ELF hash')
    labels.append('extra-RX-LOAD-rejected')
    return labels

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out-dir',required=True,type=Path);p.add_argument('--write',action='store_true');p.add_argument('--strict-firmware',action='store_true')
    p.add_argument('--llvm-bin',type=Path,default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    a=p.parse_args();out=a.out_dir.resolve();llvm=a.llvm_bin.resolve()
    need(out.is_relative_to(HERE/'build') and out!=HERE/'build','Owned integration evidence')
    before=closure(llvm)
    with contextlib.redirect_stdout(io.StringIO()):old_proofs=B['upstream'](llvm)
    results=[]
    for mode in ('c','cpp'):
        folder=out/mode;value=V['inspect'](folder,llvm,mode,old_proofs)
        value['schema']='TSL9-receive-transmit-static-integration-proof-v2'
        value['full_proof_input_groups']=before
        value['upstream_receipt_set']=receipts()
        value['proof_inputs'][str(HERE/'verify-v2.py')]=sha(HERE/'verify-v2.py')
        value['negative_controls']+=extra_controls((folder/'NOMINAL-SUBCOMPONENT-NOT-FIRMWARE.elf').read_bytes())
        value['nominal']['complete_PHDR_inventory_checked']=True
        need(len(value['negative_controls'])==1538,'All1538 bounded controls')
        need(value['nominal']['RX_LOAD_bytes']-value['nominal']['bytes']==value['nominal']['unproved_executable_gap_bytes']==66970,'Exact RX/gap projection')
        need(before==closure(llvm),'Complete transitive source/tool/receipt closure unchanged')
        data=B['encoded'](value,llvm);dest=folder/'verification-v2.json'
        if a.write:need(not dest.exists(),'Create-only stricter receipt');dest.write_bytes(data)
        else:need(dest.read_bytes()==data,'Complete v2 read-only replay equality')
        results.append(dict(language=mode,receipt_sha256=hashlib.sha256(data).hexdigest(),negative_controls=len(value['negative_controls']),input_groups={k:len(v) for k,v in before.items()}))
    print(json.dumps(dict(passed=True,results=results,full_bytes=1902,full_UND=4,nominal_bytes=1588,nominal_UND=0,firmware_ready=False)))
    return 1 if a.strict_firmware else 0
if __name__=='__main__':raise SystemExit(main())
