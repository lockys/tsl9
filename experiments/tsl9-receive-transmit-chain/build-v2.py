#!/usr/bin/env python3
"""Compile selected src units and link real components; never execute outputs."""
import argparse, hashlib, importlib.util, json, os, re, runpy, struct, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SPEC=json.loads((HERE/'spec.json').read_bytes())
for name,h in SPEC['pins'].items():
    if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input '+name)
C=runpy.run_path(str(ROOT/'scripts/verify-curated-source.py'))
T=runpy.run_path(str(ROOT/'experiments/tsl9-tagged-native-chain/check.py'))
E=T['E']
FW=ROOT/T['U']['FIRMWARE']
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SPANS=[('.flag',0x81aa,6),('.helpers',0x820c,60),('.filter',0x82d2,188),
       ('.fill',0x8520,168),('.transport_frame',0x8a56,280),('.dispatch',0x12a08,102),
       ('.spi',0x16896,326),('.tagged',0x16b7c,246),('.peripheral',0x18ca4,212)]
DEFS={n:(va,z) for n,va,z in SPEC['definitions']}
MISSING=SPEC['missing_providers']
MASK={16:(4,0x01fff07f),17:(4,0x00000fff),44:(2,0xe383),45:(2,0xe003)}
def need(v,msg):
    if not v:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def portable(v,llvm):return T['portable'](v,llvm)
def encoded(v,llvm):return (json.dumps(portable(v,llvm),indent=2)+'\n').encode()
def module(path):
    s=importlib.util.spec_from_file_location('peripheral_frozen_composition',path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
P=module(ROOT/'experiments/tsl9-peripheral-dispatch-component/check.py')

def original():
    b=FW.read_bytes();need(len(b)==76800 and digest(b)==FW_SHA,'Original image identity');return b
def rows(b,base):
    at=0;out=[]
    while at<len(b):
        need(at+2<=len(b),'Instruction boundary');w=int.from_bytes(b[at:at+2],'little')
        z=4 if w&3==3 else 2;need(at+z<=len(b),'Complete instruction extent')
        out.append([base+at,b[at:at+z].hex()]);at+=z
    return out
def sx(n,b):return n-(1<<b) if n&(1<<(b-1)) else n
def target(b,pc,kind):
    w=int.from_bytes(b,'little')
    if kind==17:
        need(len(b)==4 and w&127==0x6f,'JAL type')
        im=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        return (pc+sx(im,21))&0xffffffff
    if kind==16:
        need(len(b)==4 and w&127==0x63 and (w>>12)&7 in (0,1,4,5,6,7),'BRANCH type')
        im=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        return (pc+sx(im,13))&0xffffffff
    if kind==44:
        need(len(b)==2 and w&3==1 and w>>13 in (6,7),'Compressed BRANCH type')
        im=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
        return (pc+sx(im,9))&0xffffffff
    need(kind==45 and len(b)==2 and w&3==1 and w>>13 in (1,5),'Compressed jump type')
    im=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
    return (pc+sx(im,12))&0xffffffff

def funcs(e):
    return sorted([s for s in e.symbols if s['info']&15==2 and s['size']],key=lambda s:(s['section'],s['value']))
def common(e,nominal):
    fs=funcs(e);wanted={n:v for n,v in DEFS.items() if not nominal or not (0x12c58<=v[0]<0x12d92)}
    need(len(fs)==len(wanted) and {s['name'] for s in fs}==set(wanted),'Complete genuine function inventory')
    need(all(s['info']>>4==1 and s['size']==wanted[s['name']][1] and s['section'] not in (0,0xfff1) for s in fs),'Strong real function sizes')
    need(not [s for s in e.symbols if s['info']>>4 and s['section']==0xfff1],'No absolute global stand-in')
    und=sorted(s['name'] for s in e.symbols if s['name'] and s['section']==0)
    need(und==([] if nominal else sorted(MISSING)),'Exact genuine unresolved frontier')
    need(all(s['info']>>4==1 for s in e.symbols if s['name'] and s['section']==0),'Strong unresolved declarations')
    return fs

def full_contract(raw):
    e=E(raw);fw=original();fs=common(e,False);sec=e.section('.full')
    need(e.header[0]==1 and sec['flags']==6 and sec['address']==0 and sec['size']==1902 and sec['align']==2,'Owned1902B diagnostic ET_REL')
    need([(s['name'],s['size']) for s in e.sections if s['flags']&2 and s['size']]==[('.full',1902)],'No extra allocations')
    need(len(e.relocations)==97,'All97 actual pending edges retained')
    code=e.data('.full');mask=bytearray(b'\xff'*1902);typed=[]
    for r in e.relocations:
        need(r['section']==sec['index'] and r['type'] in MASK and r['addend']==0,'Actual typed .full relocation')
        off=r['offset'];width,bits=MASK[r['type']]
        owner=next((s for s in fs if s['value']<=off and off+width<=s['value']+s['size']),None)
        need(owner is not None and all(v==255 for v in mask[off:off+width]),'Owned nonoverlapping edge')
        va=DEFS[owner['name']][0]+off-owner['value']
        ref=fw[va-0x8000:va-0x8000+width];actual=code[off:off+width]
        dest=e.symbols[r['symbol']]['name'];expected=(DEFS.get(dest) or (MISSING.get(dest),0))[0]
        need(expected is not None and target(ref,va,r['type'])==expected,'Original target equals actual named provider')
        target(actual,va,r['type'])
        mask[off:off+width]=bits.to_bytes(width,'little')
        typed.append([off,va,r['type'],dest,expected])
    cursor=0;allrows=[]
    for s in fs:
        need(s['section']==sec['index'] and s['value']==cursor,'Every code byte owned without gaps')
        va,z=DEFS[s['name']];ref=fw[va-0x8000:va-0x8000+z];actual=code[cursor:cursor+z]
        need(all(not((a^b)&m) for a,b,m in zip(actual,ref,mask[cursor:cursor+z])),'All original nonrelocation bits')
        allrows+=rows(actual,cursor);cursor+=z
    need(cursor==1902 and len(allrows)==662,'Full1902B662i projection')
    return e,allrows,typed

def nominal_contract(raw):
    e=E(raw);fw=original();fs=common(e,True)
    need(e.header[0]==2 and e.header[3]==0x82d2 and not e.relocations,'Original-PC EXEC entry, no pending relocation')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need([s['name'] for s in alloc]==[n for n,va,z in SPANS],'Exactly9code spans')
    allrows=[];loads=[p for p in e.program_headers if p[0]==1]
    need(loads and all(p[6] in (4,5) and p[2]==p[3] and p[4]==p[5] and p[7]==4096 and p[1]%p[7]==p[2]%p[7] for p in loads),'Read-only executable congruent file-backed LOADs')
    for n,va,z in SPANS:
        s=e.section(n);b=e.data(n)
        need(s['address']==va and s['size']==z and s['flags']==6 and s['align']==2,'Exact original section shape')
        need(b==fw[va-0x8000:va-0x8000+z],'Whole original code projection')
        cover=[p for p in loads if p[2]<=va and va+z<=p[2]+p[4]]
        need(len(cover)==1 and cover[0][6]==5 and cover[0][1]+va-cover[0][2]==s['offset'],'Mapped actual code file bytes')
        allrows+=rows(b,va)
    need(len(allrows)==555,'All555 complete instruction rows')
    for s in fs:
        va,z=DEFS[s['name']]
        need(s['value']==va and any(n==e.sections[s['section']]['name'] and base<=va and va+z<=base+size for n,base,size in SPANS),'Every97 strong definition original PC/extent')
    # Direct destinations must be instruction boundaries inside the proved spans.
    boundaries={a for a,b in allrows};transfers=[]
    for pc,h in allrows:
        b=bytes.fromhex(h);w=int.from_bytes(b,'little');kind=None
        if len(b)==4 and w&127 in (0x6f,0x63):kind=17 if w&127==0x6f else 16
        elif len(b)==2 and w&3==1 and w>>13 in (1,5,6,7):kind=45 if w>>13 in (1,5) else 44
        if kind:
            dest=target(b,pc,kind);need(dest in boundaries,'Every static transfer targets proved instruction')
            transfers.append([pc,kind,dest])
    return e,allrows,transfers

def upstream(llvm):
    prev=sys.argv;sys.argv=[str(T['HERE']/'check.py'),'--out-dir',str(T['HERE']/'build/nominal-v1'),'--llvm-bin',str(llvm)]
    try:need(T['main']()==0,'Existing740B proof actual read-only replay')
    finally:sys.argv=prev
    proofs={}
    for mode in ('c','cpp'):
        path=ROOT/'experiments/tsl9-peripheral-dispatch-component/build/component-v2'/mode/'verification.json'
        P.replay(ROOT,llvm,path);proofs['peripheral-'+mode]=sha(path)
    receipt=ROOT/'build/curated-source/resident-copy-arch-20261023-v1/verification.json'
    record=load(receipt);need(len(C['audit'](receipt.parent,record,C['metadata']()))==76,'Current selected-source comparison proof')
    proofs['curated-source']=sha(receipt)
    return proofs

def snapshot(llvm):
    paths=set(Path(p) for p in C['inputs'](C['metadata']()))
    paths.update([Path(__file__),HERE/'spec.json',HERE/'nominal.ld',HERE/'full.ld',FW])
    paths.update(llvm/n for n in ('clang.exe','ld.lld.exe','llvm-objdump.exe'))
    paths.add(llvm.parent/'lib/clang/18/include/stdint.h')
    need(sha(llvm/'clang.exe')=='047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','Pinned compiler')
    need(sha(llvm/'ld.lld.exe')=='fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f','Pinned linker')
    need(sha(llvm/'llvm-objdump.exe')=='de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa','Pinned readback')
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(paths)}

def recipes(folder,llvm,mode):
    out=[]
    for u in SPEC['units']:
        n=u['name'];source=ROOT/u['curated_unit'];flags=C['flags'](u,mode)
        if n=='queue-small-providers':flags += ['-Dtsl9_queue_status_81aa=tsl9_queue_external_81aa','-Dtsl9_queue_clear_820c=tsl9_queue_external_820c']
        out += [(n+'-compile',[str(llvm/'clang.exe')]+flags+['-MD','-MF',str(folder/(n+'.d')),'-MT',str(folder/(n+'.o')),'-c',str(source),'-o',str(folder/(n+'.o'))]),
                (n+'-IR',[str(llvm/'clang.exe')]+flags+['-S','-emit-llvm',str(source),'-o',str(folder/(n+'.ll'))])]
    out += [('full-link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'full.ld')]+[str(folder/(u['name']+'.o')) for u in SPEC['units']]+['-o',str(folder/'UNRESOLVED-FULL-COMPONENT.o')]),
            ('full-read',[str(llvm/'llvm-objdump.exe'),'-d','-r','-h','-t',str(folder/'UNRESOLVED-FULL-COMPONENT.o')]),
            ('nominal-link',[str(llvm/'ld.lld.exe'),'--no-relax','-T',str(HERE/'nominal.ld')]+[str(folder/(u['name']+'.o')) for u in SPEC['units'] if u['name']!='queue-consumer']+['-o',str(folder/'NOMINAL-SUBCOMPONENT-NOT-FIRMWARE.elf')]),
            ('nominal-read',[str(llvm/'llvm-objdump.exe'),'-d','-r','-h','-t',str(folder/'NOMINAL-SUBCOMPONENT-NOT-FIRMWARE.elf')])]
    return out

def consumed(label,folder,llvm):
    exe='ld.lld.exe' if label.endswith('-link') else 'llvm-objdump.exe' if label.endswith('-read') else 'clang.exe'
    paths=[llvm/exe]
    if label.endswith('-link'):
        nominal=label.startswith('nominal');paths += [HERE/('nominal.ld' if nominal else 'full.ld')]
        paths += [folder/(u['name']+'.o') for u in SPEC['units'] if not nominal or u['name']!='queue-consumer']
    elif label.endswith('-read'):paths += [folder/('UNRESOLVED-FULL-COMPONENT.o' if label.startswith('full') else 'NOMINAL-SUBCOMPONENT-NOT-FIRMWARE.elf')]
    else:
        unit=next(u for u in SPEC['units'] if label==u['name']+'-compile' or label==u['name']+'-IR')
        paths += [ROOT/unit['curated_unit'],llvm.parent/'lib/clang/18/include/stdint.h']
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out-dir',required=True,type=Path);p.add_argument('--build',action='store_true')
    p.add_argument('--llvm-bin',type=Path,default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    a=p.parse_args();out=a.out_dir.resolve();llvm=a.llvm_bin.resolve()
    need(out.is_relative_to(HERE/'build') and out!=HERE/'build','Owned output')
    before=snapshot(llvm);proofs=upstream(llvm)
    if a.build:need(not out.exists(),'New create-only build directory')
    results={}
    for mode in ('c','cpp'):
        folder=out/mode
        if a.build:
            folder.mkdir(parents=True);actual=[]
            for label,argv in recipes(folder,llvm,mode):
                used=consumed(label,folder,llvm);child=subprocess.run(argv,cwd=ROOT,capture_output=True)
                (folder/(label+'.log')).write_bytes(child.stdout+child.stderr)
                actual.append(dict(label=label,argv=argv,exit=child.returncode,consumed=used,log_sha256=sha(folder/(label+'.log'))))
                (folder/'commands.json').write_bytes(encoded(actual,llvm))
                need(child.returncode==0,'Actual command failed '+label)
        full=full_contract((folder/'UNRESOLVED-FULL-COMPONENT.o').read_bytes())
        nominal=nominal_contract((folder/'NOMINAL-SUBCOMPONENT-NOT-FIRMWARE.elf').read_bytes())
        need(before==snapshot(llvm),'Source and tools unchanged')
        result=dict(schema='TSL9-receive-transmit-integration-measurement-v1',mode=mode,inputs=before,upstream=proofs,
            full=dict(bytes=1902,instructions=len(full[1]),FUNC=107,RELA=97,UND=sorted(MISSING),ELF_sha256=sha(folder/'UNRESOLVED-FULL-COMPONENT.o')),
            nominal=dict(bytes=1588,instructions=len(nominal[1]),FUNC=97,UND=0,RELA=0,ELF_sha256=sha(folder/'NOMINAL-SUBCOMPONENT-NOT-FIRMWARE.elf')),
            artifacts={f.name:dict(bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(folder.iterdir()) if f.is_file() and f.name!='measurement.json'},
            actual_commands=load(folder/'commands.json'),target_executed=False,ISA_emulated=False,HOST_models_executed=False,firmware_ready=False)
        data=encoded(result,llvm);dest=folder/'measurement.json'
        if a.build:need(not dest.exists(),'Create-only measurement');dest.write_bytes(data)
        else:need(dest.read_bytes()==data,'Full read-only measurement equality')
        results[mode]=dict(full=result['full'],nominal=result['nominal'],commands=len(result['actual_commands']))
    print(json.dumps(dict(passed=True,results=results,firmware_ready=False)))
if __name__=='__main__':main()
