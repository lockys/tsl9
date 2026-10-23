"""Create-only native compiler/static-byte trial. No target or host model runs."""
import argparse, hashlib, json, os, re, runpy, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROFILE=ROOT/'experiments/tsl9-record-program/spec.json'
FIRMWARE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
READER=HERE/'elf_reader.py'
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
READER_SHA='4a7697a2f84c7327e7f36b56c7deb4f1b34ea49c1b248ffa517610bcc823ff50'
MASKS={16:(4,0x01fff07f),17:(4,0x00000fff),44:(2,0xe383),45:(2,0xe003)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def target(b,pc,k):
    v=int.from_bytes(b,'little')
    if k==17:
        need(v&127==0x6f,'JAL family');i=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1);return(pc+sx(i,21))&0xffffffff
    if k==16:
        need(v&127==0x63,'BRANCH family');i=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1);return(pc+sx(i,13))&0xffffffff
    if k==44:
        need(v&0xe003 in (0xc001,0xe001),'RVC branch family');i=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5);return(pc+sx(i,9))&0xffffffff
    need(k==45 and v&0xe003 in (0x2001,0xa001),'RVC jump family');i=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5);return(pc+sx(i,12))&0xffffffff
def inspect(E,p,fw,source):
    e=E(p);fs=sorted([s for s in e.symbols if s['info']&15==2],key=lambda s:s['section'])
    names=re.findall(r'(?:REGION|FRAME) void (tsl9_\w+)\(void\)',source.read_text())
    starts=[int(n.rsplit('_',1)[1],16) for n in names]
    ends=starts[1:]+[0x1505c]
    need([f['name']for f in fs]==names,'All ordered genuine regions')
    controls=[];nbytes=0;rows=[]
    for f,start,end in zip(fs,starts,ends):
        size=end-start;need(f['info']==18 and f['other']==0,'Strong visible FUNC')
        need(f['size']==size,f"{f['name']}: size {f['size']} expected {size}")
        s=e.sections[f['section']];need(s['flags']==6 and s['address']==0 and s['size']==size and f['value']==0,'Exact native region ownership')
        actual=e.data(s);original=fw[start-0x8000:end-0x8000];mask=bytearray(b'\xff'*size)
        for r in e.relocations:
            if r['section']!=s['index']:continue
            at=r['offset'];kind=r['type'];need(kind in MASKS and r['addend']==0,'Known zero-addend control');width,bits=MASKS[kind]
            need(0<=at<=size-width and all(x==255 for x in mask[at:at+width]),'Disjoint control extent')
            sym=e.symbols[r['symbol']]['name'];dest=int(sym.rsplit('_',1)[1],16)
            need(target(original[at:at+width],start+at,kind)==dest,'Exact original control target')
            mask[at:at+width]=bits.to_bytes(width,'little');controls.append([hex(start+at),kind,sym])
        bad=[i for i,(a,b,m)in enumerate(zip(actual,original,mask))if(a^b)&m]
        need(not bad,f"{f['name']}: nonrelocation byte mismatch {bad[:8]} actual={actual.hex()} original={original.hex()}")
        at=0
        while at<size:
            z=4 if int.from_bytes(actual[at:at+2],'little')&3==3 else 2;need(at+z<=size,'Complete instruction');rows.append([start+at,z]);at+=z
        nbytes+=size
    need(len(controls)==len(e.relocations),'All relocations owned')
    return dict(bytes=nbytes,instructions=len(rows),FUNC=len(fs),RELA=len(controls),UND=sorted(s['name']for s in e.symbols if s['name']and s['section']==0),controls=controls,all_original_nonrelocation_bits_equal=True,machine_controls_resolved=False)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--trial',required=True);ap.add_argument('--source',default='src/tree.v1.c');a=ap.parse_args()
    out=HERE/'build'/a.trial;need(out.parent==HERE/'build' and not out.exists(),'Create-only direct child trial')
    source=(HERE/a.source).resolve();need(source.is_relative_to(HERE/'src'),'Owned source')
    profile=json.loads(PROFILE.read_bytes());llvm=Path(os.environ['USERPROFILE'])/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin'
    for n,h in profile['tools'].items():need(sha(llvm/n)==h,'Pinned tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==profile['stdint_sha256'],'Pinned compiler header')
    need(sha(READER)==READER_SHA and sha(FIRMWARE)==FW_SHA,'Pinned local reader/firmware')
    E=runpy.run_path(str(READER))['ELF'];fw=FIRMWARE.read_bytes();inputs={str(p):sha(p)for p in [Path(__file__),source,PROFILE,READER,FIRMWARE,llvm.parent/'lib/clang/18/include/stdint.h']+[llvm/n for n in profile['tools']]};result=dict(schema='TSL9-feature-tree-static-trial-v2',source=str(source.relative_to(ROOT)),inputs=inputs,modes={},target_executed=False,ISA_emulated=False,HOST_models_executed=False,firmware_ready=False)
    for mode in ('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[];entry={}
        recipes=[('compile',[str(llvm/'clang.exe')]+profile['flags'][mode]+['-MD','-MF',str(f/'native.d'),'-MT','native.o','-c',str(source),'-o',str(f/'native.o')]),('IR',[str(llvm/'clang.exe')]+profile['flags'][mode]+['-S','-emit-llvm',str(source),'-o',str(f/'native.ll')]),('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(f/'native.o')])]
        try:
            for label,argv in recipes:
                c=subprocess.run(argv,cwd=ROOT,capture_output=True);(f/(label+'.log')).write_bytes(c.stdout+c.stderr);commands.append(dict(label=label,argv=argv,exit=c.returncode));need(c.returncode==0,'Compiler/read failure '+label)
            entry.update(inspect(E,f/'native.o',fw,source));entry['passed']=True
        except (ValueError,KeyError,IndexError)as ex:entry.update(passed=False,error=str(ex))
        entry['commands']=commands;entry['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(f.iterdir())if p.is_file()};result['modes'][mode]=entry
        print(json.dumps(dict(mode=mode,**{k:v for k,v in entry.items()if k not in ['commands','artifacts','controls']})))
    need(inputs=={p:sha(p)for p in inputs},'Frozen inputs unchanged')
    (out/'trial.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    return 0 if all(x['passed']for x in result['modes'].values())else 1
if __name__=='__main__':raise SystemExit(main())
