#!/usr/bin/env python3
"""Actual five-source C/C++ nominal link. Three code spans, never an OTA image."""
import argparse,hashlib,json,re,runpy,struct,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FILL=ROOT/'experiments/tsl9-fill-provider'
TAG=ROOT/'experiments/tsl9-tagged-dispatch'
WRITE=ROOT/'experiments/tsl9-spi-write-providers'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
F=runpy.run_path(str(FILL/'verify.py'))
T=runpy.run_path(str(TAG/'verify.py'))
N=runpy.run_path(str(WRITE/'nominal.py'))
U=N['U'];W=N['V'];E=N['E']
D=runpy.run_path(str(FILL/'decode.py'))['decode']
SOURCE={
 'fill':FILL/'src/fill.v2.c',
 'tagged':TAG/'src/tagged_dispatch.v1.c',
 'write':WRITE/'src/spi_write.v1.c',
 'read':ROOT/'experiments/tsl9-register-read/src/register_read.c',
 'spi':ROOT/U['SOURCE'],
}
READ_PIN='5d0dfffde0adf21490e9108fbb95920595a851d67ac95b376549e20be3989846'
SPANS=[('.fill',0x8520,168),('.transport',0x16896,326),('.tagged',0x16b7c,246)]
def portable(v,llvm):return U['portable'](v,ROOT,llvm)
def encode(v,llvm):return (json.dumps(portable(v,llvm),indent=2)+'\n').encode()
def decoded(code,base):D.__globals__['BASE']=base;return D(code)
def snapshot(llvm):
    paths=set(N['paths'](llvm));paths.update([Path(__file__).resolve(),HERE/'component.ld',FILL/'verify.py',FILL/'spec.json',TAG/'verify.py',TAG/'spec.json',SOURCE['read']])
    for mod in (F,T):paths.update(ROOT/n for n in mod['S']['pins'])
    for folder in [FILL/'build/verified-v1',TAG/'build/verified-v2',WRITE/'build/nominal-v3']:
        paths.update(p for p in folder.rglob('*') if p.is_file())
    need(sha(SOURCE['read'])==READ_PIN,'Frozen genuine register-read source')
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(paths)}
def replay_cli(module,folder,llvm):
    prev=sys.argv;sys.argv=[str(Path(module['__file__'])),'--out-dir',str(folder),'--llvm-bin',str(llvm)]
    try:need(module['main']()==0,'Actual recursive original-proof replay')
    finally:sys.argv=prev
def upstream(llvm):
    replay_cli(F,FILL/'build/verified-v1',llvm)
    replay_cli(T,TAG/'build/verified-v2',llvm)
    replay_cli(N,WRITE/'build/nominal-v3',llvm)
    return dict(fill={m:sha(FILL/'build/verified-v1'/m/'verification.json') for m in ('c','cpp')},
        tagged={m:sha(TAG/'build/verified-v2'/m/'verification.json') for m in ('c','cpp')},
        SPI_write_nominal={m:sha(WRITE/'build/nominal-v3'/m/'verification.json') for m in ('c','cpp')})
def flags(name,mode):
    if name=='fill':return F['P']['flags'](mode)
    if name=='spi':return U['flags'](mode)
    return T['P']['flags'](mode)
def recipes(folder,llvm,mode):
    out=[]
    for name,source in SOURCE.items():
        out += [(name+'-compile',[str(llvm/'clang.exe')]+flags(name,mode)+['-MD','-MF',str(folder/(name+'.d')),'-MT',str(folder/(name+'.o')),'-c',str(source),'-o',str(folder/(name+'.o'))]),
                (name+'-IR',[str(llvm/'clang.exe')]+flags(name,mode)+['-S','-emit-llvm',str(source),'-o',str(folder/(name+'.ll'))])]
    out += [('link',[str(llvm/'ld.lld.exe'),'--no-relax','-T',str(HERE/'component.ld')]+[str(folder/(n+'.o')) for n in SOURCE]+['-o',str(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf')]),
            ('read',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf')])]
    return out
def consumed(label,folder):
    if label=='link':paths=[HERE/'component.ld']+[folder/(n+'.o') for n in SOURCE]
    elif label=='read':paths=[folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf']
    else:paths=[SOURCE[label.split('-')[0]]]
    return {str(p):sha(p) for p in paths}
def definitions():
    defs=[[n,0x8520+off,size,'.fill'] for n,off,size in F['S']['regions']]
    defs += [[n,0x16896+off,size,'.transport'] for n,off,size in zip(U['NAMES'],U['STARTS'],U['SIZES'])]
    defs += [[n,0x168de+off,size,'.transport'] for n,off,size in W['S']['regions']]
    defs += [['tsl9_register_read_entry_16994',0x16994,4,'.transport'],['tsl9_register_read_body',0x16998,68,'.transport']]
    defs += [[n,0x16b7c+off,size,'.tagged'] for n,off,size in T['S']['regions']]
    return defs
def linked(raw):
    e=E(raw);fw=(ROOT/U['FIRMWARE']).read_bytes()
    need(hashlib.sha256(fw).hexdigest()==F['S']['firmware_sha256'],'Fresh actual official image')
    need(e.header[0]==2 and e.header[3]==0x16b7c,'Nominal EXEC/entry')
    allocated=[s for s in e.sections if s['size'] and s['flags']&2]
    need([s['name'] for s in allocated]==[s[0] for s in SPANS],'Exactly three owned code spans')
    loads=[p for p in e.program_headers if p[0]==1];need(loads and all(not(p[6]&2) for p in loads),'No writable LOAD')
    allrows=[];calls=[]
    for name,base,size in SPANS:
        sec=e.section(name);code=e.data(name)
        need(sec['address']==base and len(code)==size and sec['flags']==6 and sec['align']==2,'Exact original AX span')
        need(code==fw[base-0x8000:base-0x8000+size],'Every code byte equals corresponding original span')
        cover=[p for p in loads if p[2]<=base and p[2]+p[4]>=base+size]
        need(len(cover)==1 and cover[0][6]==5 and cover[0][1]+base-cover[0][2]==sec['offset'],'File-backed executable mapping')
        rows=decoded(code,base);allrows += [[base+r[0],r[1],r[2:]] for r in rows]
        calls += [[base+r[0],r[-1]] for r in rows if r[2]=='JAL']
    need(len(allrows)==260 and sum(s[2] for s in SPANS)==740,'Complete740B260i code projection')
    actual=sorted([s for s in e.symbols if s['info']&15==2 and s['size']],key=lambda s:s['value'])
    expected=definitions();need([[s['name'],s['value'],s['size'],e.sections[s['section']]['name']] for s in actual]==expected,'All58 genuine definitions at original PCs')
    need(all(s['info']>>4==1 for s in actual),'Strong actual FUNCs')
    need(not e.relocations and not [s for s in e.symbols if s['section']==0 and s['name']],'Zero pending control/UND')
    need(not [s for s in e.symbols if s['section']==0xfff1 and s['info']>>4],'No global ABS stand-in')
    call_targets={0x8520,0x16896,0x168de,0x1693e,0x16994}
    need(len(calls)==15 and all(t in call_targets for at,t in calls),'All15 direct calls resolve to genuine providers')
    # Computed fill transfers target original SB instructions/RET. This is
    # static bounded arithmetic from decoded entry/remainder guards, not ISA execution.
    fillrows={r[0]:r[2] for r in allrows if 0x8520<=r[0]<0x85c8}
    need(fillrows[0x8550]==['AUIPC',5,0] and fillrows[0x85ae]==['AUIPC',5,0],'Original PC ports')
    tail=[(0x8550+4*(15-n)+10)&~1 for n in range(16)]
    prefix=[(0x85ae+4*m-88)&~1 for m in range(1,16)]
    need(tail==[0x8596-4*n for n in range(16)] and prefix==[0x8556+4*m for m in range(1,16)],'All31 computed target expressions')
    need(all(fillrows[t][0]=='SB8' for t in prefix) and all(fillrows[t][0] in ('SB8','RET') for t in tail),'Computed targets are actual table instruction boundaries')
    return e,allrows,dict(tail_targets=tail,prefix_targets=prefix,alignment_link_RA='0x85BA',resident_0x4004C_target_known=False)
def readback(text,e):
    actual=[]
    for l in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)',l)
        if m:actual.append([int(m.group(1),16),bytes.fromhex(m.group(2)).hex()])
    expected=[]
    for name,base,size in SPANS:
        code=e.data(name);expected += [[base+r[0],code[r[0]:r[0]+r[1]].hex()] for r in decoded(code,base)]
    need(actual==expected,'All260 LLVM instruction addresses/bytes')
    return actual
def evaluate(folder,llvm,mode):
    raw=(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf').read_bytes();e,rows,controls=linked(raw)
    fullread=readback((folder/'read.log').read_text(),e)
    actual=load(folder/'recipes.json');expected=[dict(label=l,argv=a,returncode=0,consumed_inputs=consumed(l,folder)) for l,a in recipes(folder,llvm,mode)]
    need(actual==portable(expected,llvm),'All12 actual compile/IR/link/read recipes with consumed hashes')
    for name,source in SOURCE.items():
        md=(folder/(name+'.d')).read_text().replace('\\\n',' ').replace('\\\r\n',' ').replace('\\ ','\x01').replace('\\','/')
        target=str(folder/(name+'.o')).replace('\\','/');need(md.startswith(target+':'),'Actual MD object target')
        deps=[x.replace('\x01',' ') for x in md[len(target)+1:].strip().split()]
        need(deps==[str(source).replace('\\','/'),str(llvm.parent/'lib/clang/18/include/stdint.h').replace('\\','/')],'Exact two-file source/header closure')
    need(sha(folder/'fill.o')==F['S']['ELF_sha256']['native'] and sha(folder/'tagged.o')==T['S']['ELF_sha256']['native'] and sha(folder/'write.o')==W['S']['ELF_sha256']['native'],'Newly compiled native providers equal actual formal originals')
    U['elf_contract'](E(folder/'spi.o'),True);U['ir_contract']((folder/'spi.ll').read_text(),mode)
    F['ir_contract']((folder/'fill.ll').read_text(),mode);T['ir_contract']((folder/'tagged.ll').read_text(),mode);W['ir_contract']((folder/'write.ll').read_text(),mode)
    negatives=[]
    def rejects(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError,struct.error):negatives.append(label);return
        raise ValueError('Changed input accepted: '+label)
    for addr,width,fields in rows:
        sec=next(s for s in e.sections if s['flags']&2 and s['address']<=addr<s['address']+s['size']);b=bytearray(raw);b[sec['offset']+addr-sec['address']]^=0x80
        rejects('instruction-'+hex(addr),lambda x=bytes(b):linked(x))
    b=bytearray(raw);struct.pack_into('<I',b,24,0x8000);rejects('wrong-entry',lambda:linked(bytes(b)))
    for name,base,size in SPANS:
        b=bytearray(raw);sec=e.section(name);struct.pack_into('<I',b,e.header[5]+sec['index']*40+8,7);rejects('writable-'+name,lambda x=bytes(b):linked(x))
    return dict(schema='TSL9-tagged-native-three-span-proof-v1',passed=True,language=mode,bytes=740,instructions=260,FUNC=58,strong_UND=0,pending_RELA=0,global_ABS=0,
        spans=SPANS,whole_original_code_projection_equal=True,ELF_sha256=sha(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'),
        full_ELF_metadata=dict(header=e.header,program_headers=e.program_headers,sections=e.sections,symbols=e.symbols,relocations=e.relocations),
        actual_recipes=actual,full_LLVM_address_byte_rows=fullread,computed_control_contract=controls,negative_controls=negatives,
        artifacts={p.name:sha(p) for p in sorted(folder.iterdir()) if p.is_file() and p.name!='verification.json'},
        target_executed=False,ISA_emulated=False,HOST_models_executed=False,physical_placement_proved=False,
        resident_ABI_proved=False,IRQ_interleavings_proved=False,whole_image_proved=False,hardware_tested=False,BIN_generated=False,firmware_ready=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out-dir',required=True,type=Path);p.add_argument('--build',action='store_true');p.add_argument('--strict-firmware',action='store_true');p.add_argument('--llvm-bin',type=Path,default=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin');a=p.parse_args();out=a.out_dir.resolve();llvm=a.llvm_bin.resolve();need(out.is_relative_to(HERE/'build') and out!=HERE/'build','Owned bounded output')
    before=snapshot(llvm);proofs=upstream(llvm)
    if a.build:need(not out.exists(),'Create-only original proof')
    results=[]
    for mode in ('c','cpp'):
        folder=out/mode
        if a.build:
            folder.mkdir(parents=True);actual=[]
            for label,argv in recipes(folder,llvm,mode):
                used=consumed(label,folder);child=subprocess.run(argv,cwd=ROOT,capture_output=True);(folder/(label+'.log')).write_bytes(child.stdout+child.stderr);actual.append(dict(label=label,argv=argv,returncode=child.returncode,consumed_inputs=used));need(child.returncode==0,'Actual command failed: '+label)
            (folder/'recipes.json').write_bytes(encode(actual,llvm))
        value=evaluate(folder,llvm,mode);value['inputs']=before;value['upstream']=proofs;need(snapshot(llvm)==before,'All declared recursive input snapshots unchanged')
        data=encode(value,llvm);dest=folder/'verification.json'
        if a.build:need(not dest.exists(),'New original receipt');dest.write_bytes(data)
        else:need(dest.read_bytes()==data,'Exact original receipt read-only replay')
        results.append(dict(language=mode,receipt_sha256=hashlib.sha256(data).hexdigest(),ELF_sha256=value['ELF_sha256'],negative_controls=len(value['negative_controls'])))
    print(json.dumps(dict(passed=True,results=results,bytes=740,instructions=260,FUNC=58,pending_RELA=0,strong_UND=0,resident_target_known=False,firmware_ready=False)))
    return 1 if a.strict_firmware else 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,struct.error) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
