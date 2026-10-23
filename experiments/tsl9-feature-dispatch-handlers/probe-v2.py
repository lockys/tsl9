"""Create-only native compiler/static-byte trial. No target or host model runs."""
import argparse, hashlib, json, os, re, runpy, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROFILE=ROOT/'experiments/tsl9-record-program/spec.json'
FIRMWARE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
READER=ROOT/'experiments/tsl9-feature-dispatch-tree/elf_reader-v3.py'
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
READER_SHA='112e90f7a1786bd1e388718e80086ba937035364d926c89cd5875eba68ce543a'
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
    ends=starts[1:]+[0x153ba]
    need([f['name']for f in fs]==names,'All ordered genuine regions')
    controls=[];pc_pairs=[];nbytes=0;rows=[]
    for f,start,end in zip(fs,starts,ends):
        size=end-start;need(f['info']==18 and f['other']==0,'Strong visible FUNC')
        need(f['size']==size,f"{f['name']}: size {f['size']} expected {size}")
        s=e.sections[f['section']];need(s['flags']==6 and s['address']==0 and s['size']==size and f['value']==0,'Exact native region ownership')
        actual=e.data(s);original=fw[start-0x8000:end-0x8000];mask=bytearray(b'\xff'*size)
        for r in e.relocations:
            if r['section']!=s['index']:continue
            at=r['offset'];kind=r['type']
            if kind in (23,24):
                sym=e.symbols[r['symbol']]
                need(r['addend']==0 and start+at==(0x1534e if kind==23 else 0x15352),'Exact PC-relative pair sites')
                if kind==23:
                    need(sym['name']=='tsl9_feature_nested_table_1a6d4','Genuine table target')
                else:
                    need(sym['name'].startswith('.Lhandler_table') and sym['section']==s['index'] and sym['value']==at-4,'Matching HI20 anchor ownership')
                mask[at:at+4]=(0xfff if kind==23 else 0xfffff).to_bytes(4,'little')
                pc_pairs.append([hex(start+at),kind,sym['name']])
                continue
            need(kind in MASKS and r['addend']==0,'Known zero-addend control');width,bits=MASKS[kind]
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
    table=e.section('.rodata.tsl9_feature_nested_table')
    need(table['size']==32 and table['flags']==2 and table['align']==4 and e.data(table)==bytes(32),'Exact symbolic table carrier')
    targets=[0x15364,0x1536c,0x15370,0x15394,0x153b4,0x153b4,0x153b4,0x153b0]
    expected=sorted([(i*4,35,'tsl9_feature_handler_'+format(t,'x'),0)for i,t in enumerate(targets)]+[(i*4,39,'tsl9_feature_nested_table_1a6d4',0)for i in range(8)])
    actual=sorted((r['offset'],r['type'],e.symbols[r['symbol']]['name'],r['addend'])for r in e.relocations if r['section']==table['index'])
    need(actual==expected,'Genuine signed-relative target/table bindings')
    need(len(pc_pairs)==2 and len(controls)+18==len(e.relocations),'All code, PC and table relocations owned')
    return dict(bytes=nbytes,instructions=len(rows),FUNC=len(fs),RELA=len(controls),UND=sorted(s['name']for s in e.symbols if s['name']and s['section']==0),controls=controls,all_original_nonrelocation_bits_equal=True,machine_controls_resolved=False)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--trial',required=True);ap.add_argument('--source',default='src/handlers.v1.c');a=ap.parse_args()
    out=HERE/'build'/a.trial;need(out.parent==HERE/'build' and not out.exists(),'Create-only direct child trial')
    source=(HERE/a.source).resolve();need(source.is_relative_to(HERE/'src'),'Owned source')
    profile=json.loads(PROFILE.read_bytes());llvm=Path(os.environ['USERPROFILE'])/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin'
    for n,h in profile['tools'].items():need(sha(llvm/n)==h,'Pinned tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==profile['stdint_sha256'],'Pinned compiler header')
    need(sha(READER)==READER_SHA and sha(FIRMWARE)==FW_SHA,'Pinned local reader/firmware')
    E=runpy.run_path(str(READER))['ELF'];fw=FIRMWARE.read_bytes();inputs={str(p):sha(p)for p in [Path(__file__),source,PROFILE,READER,FIRMWARE,llvm.parent/'lib/clang/18/include/stdint.h']+[llvm/n for n in profile['tools']]};result=dict(schema='TSL9-feature-handlers-static-trial-v2',source=str(source.relative_to(ROOT)),inputs=inputs,modes={},target_executed=False,ISA_emulated=False,HOST_models_executed=False,firmware_ready=False)
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
