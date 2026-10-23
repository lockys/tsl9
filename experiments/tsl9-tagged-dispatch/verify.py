#!/usr/bin/env python3
"""Finite offline native proof. No target execution; strict firmware gate stays shut."""
import argparse,copy,hashlib,json,re,runpy,struct,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=0x16b7c

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def pin(path):return sha(Path(path).read_bytes())
def load(path):return json.loads(Path(path).read_bytes())
def frozen():
    spec=load(HERE/'spec.json')
    for name,h in spec['pins'].items():need(pin(ROOT/name)==h,'Frozen input '+name)
    return spec,runpy.run_path(str(HERE/'probe.py')),runpy.run_path(str(ROOT/spec['reader']))['ELF'],runpy.run_path(str(HERE/'decode.py'))['decode']
S,P,ELF,decode=frozen()
portable=runpy.run_path(str(ROOT/S['reader']))['portable']

def original():
    fw=(ROOT/S['firmware']).read_bytes()
    need(len(fw)==76800 and sha(fw)==S['firmware_sha256'],'Official input image identity')
    code=fw[0xeb7c:0xec72]
    need(sha(code)==S['span_sha256'],'Original246B candidate')
    window=load(ROOT/S['evidence'])
    need(bytes.fromhex(''.join(r['bytes'] for r in window['rows']))[:246]==code,'Retained rows equal actual original')
    rows=decode(code);need(rows==S['typed_rows'],'All86 original typed rows')
    return code,rows

def regions(e,partial):
    fs=sorted([s for s in e.symbols if s['info']&15==2 and s['size']],key=lambda s:(s['section'],s['value']))
    facts=[];code=b'';starts={}
    for s in fs:
        need(s['section'] not in (0,0xfff1),'Genuine function body')
        start=len(code);starts[s['section']]=0 if partial else start
        facts.append([s['name'],start,s['size']])
        code+=e.data(e.sections[s['section']])[s['value']:s['value']+s['size']]
    need(facts==S['regions'],'Exactly15 ordered private regions with original offsets/extents')
    rels=[[starts[r['section']]+r['offset'],r['type'],e.symbols[r['symbol']]['name'],r['addend']] for r in e.relocations]
    need(rels==S['relocations'],'All11 genuine pending control relocations and targets')
    und=sorted(s['name'] for s in e.symbols if s['section']==0 and s['name'])
    need(und==sorted(S['undefined']) and all((s['info']>>4)==1 for s in e.symbols if s['section']==0 and s['name']),'Four strong unresolved providers')
    need(not [s for s in e.symbols if s['section']==0xfff1 and s['info']>>4],'No fabricated global absolute provider')
    if partial:need(code==e.data('.tagged_dispatch'),'No gaps or unowned linked bytes')
    return code,rels

def typed_contract(code,rels):
    rows=decode(code);expected=copy.deepcopy(S['typed_rows'])
    by={r[0]:r for r in rows}
    for off,kind,target,addend in rels:
        need(addend==0,'No shifted provider')
        expected[next(i for i,r in enumerate(expected) if r[0]==off)][-1]=BASE+off
        row=by[off];need((kind==17 and row[2:4]==['JAL',1]) or (kind==16 and row[2] in ('BLTU','BNE')) or (kind==44 and row[2]=='BNEZ') or (kind==45 and row[2]=='J'),'Relocation opcode/link-register contract')
    need(rows==expected,'All86 widths, signed/unsigned fields, operands and pending-control encodings')
    need(by[124]==[124,2,'JALR',1,15,0],'Fresh indirect call links RA=0x16BFA')
    need(by[232][2:5]==['BNE',9,19],'Busy loop compares then-live S1!=S3')
    need(by[228]==[228,2,'RET',1] and by[244]==[244,2,'RET',1],'Two genuine returns')
    return rows

def object_contract(raw,partial,whole=True):
    e=ELF(raw);code,rels=regions(e,partial);typed_contract(code,rels)
    if whole:need(sha(raw)==S['ELF_sha256']['partial' if partial else 'native'],'Complete frozen ELF metadata/sections/symbols/tail')
    return e,code

def ir_contract(text,mode,whole=True):
    # Scalar SSA, volatile memory and original architecture ports are separate
    # witnesses. This does not claim ordinary C ABI or whole-program semantics.
    functions=re.findall(r'^define .*?@(\w+)\(\).*?\{\n(.*?)^\}',text,re.M|re.S)
    need([n for n,b in functions]==[r[0] for r in S['regions']],'IR private-region order')
    scalars={n:[re.sub(r'%\d+','%v',l.strip()) for l in b.splitlines() if re.match(r'\s*%\d+ = (?:add |and |shl |lshr |icmp |zext |load volatile |inttoptr )',l)] for n,b in functions}
    need(scalars==S['IR_scalars'][mode],'C-owned scalar SSA and two volatile word loads')
    need('alloca ' not in text and ' call ' not in re.sub(r'.*asm sideeffect.*','',text),'No compiler stack frame or ordinary hidden call')
    for anchor in S['IR_ports']:need(anchor in text,'Then-live architecture port '+anchor)
    canonical='\n'.join(l for l in text.splitlines() if not l.startswith(('; ModuleID','source_filename')))+'\n'
    if whole:need(sha(canonical.encode())==S['IR_sha256'][mode],'Complete path-independent IR')
    return scalars

def recipes(folder,llvm,mode):
    source=HERE/'src/tagged_dispatch.v1.c';common=P['flags'](mode)
    return [
      ('compile',[str(llvm/'clang.exe')]+common+['-MD','-MF',str(folder/'native.d'),'-MT',str(folder/'native.o'),'-c',str(source),'-o',str(folder/'native.o')]),
      ('IR',[str(llvm/'clang.exe')]+common+['-S','-emit-llvm',str(source),'-o',str(folder/'native.ll')]),
      ('object',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(folder/'native.o')]),
      ('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'component.ld'),str(folder/'native.o'),'-o',str(folder/'partial.o')]),
      ('partial',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(folder/'partial.o')])]

def verify(folder,llvm,mode):
    code,rows=original();raw=(folder/'native.o').read_bytes();part=(folder/'partial.o').read_bytes()
    native,actual=object_contract(raw,False);linked,linkedcode=object_contract(part,True)
    need(actual==linkedcode,'Partial link retains native bytes and all11 pending edges')
    masks=bytearray(b'\xff'*246)
    for off,kind,target,addend in S['relocations']:
        n,mask={16:(4,0x01fff07f),17:(4,0xfff),44:(2,0xe383),45:(2,0xe003)}[kind];masks[off:off+n]=mask.to_bytes(n,'little')
    need(all(not((a^b)&m) for a,b,m in zip(actual,code,masks)),'Every nonrelocation bit equals original')
    need(actual!=code,'Diagnostic VMA0 is not original-address linked firmware')
    ir=(folder/'native.ll').read_text();scalars=ir_contract(ir,mode)
    md=(folder/'native.d').read_text().replace('\\\n','').replace('\\','/')
    deps=md.split(': ',1)[1].split()
    need(deps==[str(HERE/'src/tagged_dispatch.v1.c').replace('\\','/'),str(llvm.parent/'lib/clang/18/include/stdint.h').replace('\\','/')],'Actual MD closure: source and pinned compiler stdint only')
    actual_recipes=load(folder/'recipes.json')
    expected=[dict(label=l,argv=a,returncode=0) for l,a in recipes(folder,llvm,mode)]
    need(actual_recipes==portable(expected,ROOT,llvm),'Five actual successful pinned compiler/IR/reader/linker recipes')
    measurement=load(folder.parent/'measurement.json');m=measurement['modes'][mode]
    need(m['all_recipes_succeeded'] and m['ELF_sha256']==sha(raw) and m['partial_ELF_sha256']==sha(part),'Producer measurement matches actual ELF')
    for a in m['artifacts']:
        path=folder/Path(a['path'].replace('\\','/')).name
        need(path.stat().st_size==a['size'] and pin(path)==a['sha256'],'All measured artifacts unchanged')
    # Controlled corruptions use parser/typed checks with the complete ELF/IR
    # hash check disabled; passing solely because a digest changed is excluded.
    negatives=[]
    def rejects(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError,struct.error,UnicodeError):negatives.append(label);return
        raise ValueError('Negative unexpectedly accepted: '+label)
    starts={s['section']:s for s in native.symbols if s['info']&15==2 and s['size']}
    for row in rows:
        off=row[0];region=next(s for s in S['regions'] if s[1]<=off<s[1]+s[2])
        sym=next(s for s in native.symbols if s['name']==region[0]);pos=native.sections[sym['section']]['offset']+sym['value']+off-region[1]
        changed=bytearray(raw);changed[pos]^=0x80
        rejects('instruction-'+str(off),lambda b=bytes(changed):object_contract(b,False,False))
    for i,rel in enumerate(native.relocations):
        section=next(s for s in native.sections if s['type']==4 and s['info']==rel['section'])
        peers=[r for r in native.relocations if r['section']==rel['section']];entry=peers.index(rel)
        changed=bytearray(raw);at=section['offset']+entry*12+8;changed[at]^=2
        rejects('relocation-addend-'+str(i),lambda b=bytes(changed):object_contract(b,False,False))
    for anchor in S['IR_ports']:
        rejects('IR-port-'+str(len(negatives)),lambda t=ir.replace(anchor,'CORRUPT'+anchor[1:]):ir_contract(t,mode,False))
    # Alter C-owned scalar semantics with full IR hash checking disabled.
    for old,new in [('add i32 %13, -1','add i32 %13, -2'),('and i32 %21, 255','and i32 %21, 127'),('lshr i32 %6, 3','lshr i32 %6, 4'),('shl i32 %15, 5','shl i32 %15, 4'),('load volatile i32','load i32')]:
        need(old in ir,'Negative scalar anchor present')
        rejects('IR-scalar-'+str(len(negatives)),lambda t=ir.replace(old,new,1):ir_contract(t,mode,False))
    artifacts=[dict(path=str(p),bytes=p.stat().st_size,sha256=pin(p)) for p in sorted(folder.iterdir()) if p.is_file() and p.name!='verification.json']
    return dict(schema='TSL9-tagged-dispatch-offline-proof-v1',passed=True,language=mode,
        bytes=246,instructions=86,private_regions=15,pending_relocations=11,strong_undefined=4,global_ABS=0,
        nonrelocation_bits_equal_original=True,whole_bytes_equal_original=False,source_owned_scalar_SSA=scalars,
        negative_controls=negatives,negative_controls_complete_hash_disabled=True,
        real_compile_and_link_recipes=5,artifacts=artifacts,
        function_extent_globally_confirmed=False,ordinary_C_ABI_proved=False,resident_0x4004C_target_known=False,
        target_executed=False,ISA_emulated=False,hardware_tested=False,firmware_ready=False)

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--out-dir',required=True,type=Path);a.add_argument('--build',action='store_true');a.add_argument('--strict-firmware',action='store_true');a.add_argument('--llvm-bin',type=Path,default=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin');args=a.parse_args()
    out=args.out_dir.resolve();llvm=args.llvm_bin.resolve();need(out.is_relative_to(HERE/'build') and out!=HERE/'build','Owned bounded evidence folder')
    paths=[HERE/'spec.json',Path(__file__).resolve()]+[ROOT/n for n in S['pins']]+[llvm/n for n in S['tools']]+[llvm.parent/'lib/clang/18/include/stdint.h']
    for n,h in S['tools'].items():need(pin(llvm/n)==h,'Pinned actual tool')
    need(pin(paths[-1])==S['stdint_sha256'],'Pinned compiler stdint')
    before={str(p):dict(sha256=pin(p),bytes=p.stat().st_size) for p in paths}
    if args.build:
        need(not out.exists(),'Create-only evidence, never rewrite old receipts')
        saved=sys.argv;sys.argv=[str(HERE/'probe.py'),'--version','1','--out-dir',str(out),'--llvm-bin',str(llvm)]
        try:need(P['main']()==0,'Actual finite C/C++ build')
        finally:sys.argv=saved
    results=[]
    for mode in ('c','cpp'):
        result=verify(out/mode,llvm,mode);result['inputs']=before
        data=(json.dumps(portable(result,ROOT,llvm),indent=2)+'\n').encode();dest=out/mode/'verification.json'
        if args.build:need(not dest.exists(),'Create-only original verification');dest.write_bytes(data)
        else:need(dest.read_bytes()==data,'Exact read-only original-receipt replay')
        results.append(dict(language=mode,passed=True,verification_sha256=sha(data),negative_controls=len(result['negative_controls'])))
    need(before=={str(p):dict(sha256=pin(p),bytes=p.stat().st_size) for p in paths},'All proof inputs unchanged')
    print(json.dumps(dict(passed=True,results=results,firmware_ready=False)))
    return 1 if args.strict_firmware else 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
