#!/usr/bin/env python3
"""Compile/read a finite RV32 component; never execute target instructions."""
import argparse,hashlib,json,re,runpy,struct,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SPEC=HERE/'spec.json'
NAME='tsl9_dispatch_external_18ca4'
LINKED='COMPONENT-ONLY-NOT-FIRMWARE.elf'
def need(ok,message):
    if not ok: raise ValueError(message)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b): return hashlib.sha256(b).hexdigest()
def load(p): return json.loads(Path(p).read_bytes())
def modules():
    spec=load(SPEC)
    for p,pin in spec['pins'].items(): need(sha(ROOT/p)==pin,'Frozen input '+Path(p).name)
    return spec,runpy.run_path(str(HERE/'probe.py'),run_name='peripheral_builder'),runpy.run_path(str(ROOT/spec['reader']),run_name='peripheral_reader')['ELF']
S,P,ELF=modules()
NAMES=S['names']
OFFSETS=S['offsets']
SIZES=S['sizes']
EDGES=S['edges']
def portable(v,llvm): return P['portable'](v,llvm)
def inputs(llvm):
    paths=[SPEC,Path(__file__).resolve()]+[ROOT/p for p in S['pins']]+[llvm/n for n in S['tools']]+[llvm.parent/'lib/clang/18/include/stdint.h']
    for n,h in S['tools'].items(): need(sha(llvm/n)==h,'Actual compiler/linker/reader identity')
    need(sha(paths[-1])==S['stdint_sha256'],'Exact compiler stdint resource')
    return {str(p):dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths}
def sx(v,b): return v-(1<<b) if v&(1<<(b-1)) else v
def decode(code,base):
    rows=[];at=0
    while at<len(code):
        half=int.from_bytes(code[at:at+2],'little');width=4 if half&3==3 else 2
        need(at+width<=len(code),'Complete instruction')
        w=int.from_bytes(code[at:at+width],'little')
        if width==4:
            op=w&127;f=(w>>12)&7;rd=(w>>7)&31;rs=(w>>15)&31;rs2=(w>>20)&31
            if op==3 and f in (2,4): fields=['LW' if f==2 else 'LBU',rd,rs,sx(w>>20,12)]
            elif op==0x23 and f in (0,2): fields=['SB' if f==0 else 'SW',rs2,rs,sx(((w>>25)<<5)|((w>>7)&31),12)]
            elif op==0x13 and f==1 and w>>25==0: fields=['SLLI',rd,rs,rs2]
            elif op==0x13 and f==6: fields=['ORI',rd,rs,sx(w>>20,12)]
            elif op==0x33 and f==6 and w>>25==0: fields=['OR',rd,rs,rs2]
            elif op==0x63 and f in (4,5):
                im=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
                fields=['BLT' if f==4 else 'BGE',rs,rs2,base+at+sx(im,13)]
            else: raise ValueError('Unexpected32-bit opcode/funct/register family')
        else:
            q=w&3;f=w>>13;rd=(w>>7)&31;rs2=(w>>2)&31;rp=8+((w>>7)&7)
            if q==0 and f==2:
                im=((w>>10)&7)*8+((w>>6)&1)*4+((w>>5)&1)*64
                fields=['LW',8+((w>>2)&7),rp,im]
            elif q==1 and f==2: fields=['LI',rd,sx(((w>>12)&1)*32+((w>>2)&31),6)]
            elif q==1 and f==4 and (w>>10)&3==2: fields=['ANDI',rp,rp,sx(((w>>12)&1)*32+((w>>2)&31),6)]
            elif q==1 and f==4 and (w>>10)&3==3 and not w&(1<<12) and (w>>5)&3==2: fields=['OR',rp,rp,8+((w>>2)&7)]
            elif q==2 and f==0 and not w&(1<<12): fields=['SLLI',rd,rd,(w>>2)&31]
            elif w==0x8082: fields=['RET',1]
            elif q==2 and f==4 and rd and rs2: fields=['ADD',rd,rd,rs2] if w&(1<<12) else ['MV',rd,rs2]
            elif q==1 and f==7:
                im=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
                fields=['BNEZ',rp,base+at+sx(im,9)]
            elif q==1 and f==5:
                im=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
                fields=['J',base+at+sx(im,12)]
            else: raise ValueError('Unexpected compressed opcode/family')
        rows.append(dict(offset=at,width=width,fields=fields));at+=width
    return rows
def original():
    fw=(ROOT/S['firmware']).read_bytes()
    need(digest(fw)==S['firmware_sha256'] and len(fw)==76800,'Actual official firmware')
    code=fw[0x10ca4:0x10d78];need(digest(code)==S['span_sha256'],'Exact original212B')
    evidence=load(ROOT/S['evidence'])
    need(bytes.fromhex(''.join(x['bytes'] for x in evidence['rows']))==code,'All72 retained raw rows equal fresh original')
    rows=decode(code,0x18ca4);need(len(rows)==72,'Complete72instruction original')
    return code,rows
def metadata(e):
    return dict(header=list(e.header),program_headers=e.program_headers,sections=e.sections,symbols=e.symbols,relocations=e.relocations)
def elf_contract(e,linked,whole=True):
    which='linked' if linked else 'native'
    need(metadata(e)==S['ELF_metadata'][which],'Complete ELF headers/sections/symbols/RELA ownership')
    need(not any(x['info']>>4 and x['section'] in (0,65521) for x in e.symbols),'No global UND/ABS provider')
    expected,allrows=original();actual=[]
    if linked:
        code=e.data(e.section('.peripheral_write'));actual=decode(code,0x18ca4)
        need(actual==allrows,'All linked72 typed widths/operands/targets')
        need(code==expected,'Every original212 byte equal after nominal link')
    else:
        need(len(e.relocations)==7,'Seven actual private symbolic edges')
        for name,offset,size in zip(NAMES,OFFSETS,SIZES):
            s=e.section('.text.'+name);code=e.data(s);need(len(code)==size,'Whole genuine region size')
            rows=decode(code,0x18ca4+offset);truth=decode(expected[offset:offset+size],0x18ca4+offset)
            edges=[x for x in EDGES if x['owner']==name]
            for a,b in zip(rows,truth):
                need(a['offset']==b['offset'] and a['width']==b['width'],'Original instruction boundaries')
                edge=next((x for x in edges if x['offset']==a['offset']),None)
                if edge:
                    need(a['fields'][:-1]==b['fields'][:-1],'Pending edge family/RD/RS retained')
                    need(b['fields'][-1]==0x18ca4+OFFSETS[NAMES.index(edge['target'])],'Symbol target is genuine original destination')
                else: need(a==b,'All native noncontrol typed operations')
            need(len(rows)==len(truth),'No missing/extra native instruction')
            actual.extend(rows)
    if whole: need(digest(e.raw)==S['ELF_sha256'][which],'Whole actual ELF byte identity')
    return dict(sha256=digest(e.raw),bytes=212,instructions=len(actual),FUNCs=7,UND=0,global_ABS=0,RELA=len(e.relocations),all_original_typed_operands_equal=True,all_original_bytes_equal=linked,private_regions=True,physical_installation_proved=False)
def ir_contract(text,mode,full=True):
    norm='\n'.join(x for x in text.splitlines() if not x.startswith('; ModuleID') and not x.startswith('source_filename'))+'\n'
    need(re.findall(r'^define .*?@(\w+)\(',text,re.M)==NAMES,'Seven genuine IR regions')
    need('alloca ' not in text and ' phi ' not in text,'No compiler frame or invented inter-region phi')
    need(len(re.findall(r'load volatile ',text))==22 and len(re.findall(r'store volatile ',text))==8,'All22 loads/eight stores emitted from C')
    need(not any('call ' in x and 'asm sideeffect' not in x for x in text.splitlines()),'No hidden call provider')
    need([x.strip() for x in norm.splitlines() if re.search(r'load volatile|store volatile|= (?:add|shl|and|or) |^define |^  unreachable',x)]==S['IR_scalar_SSA'],'Complete selected C scalar SSA/volatile order')
    for x in S['IR_port_anchors']: need(x in text,'Physical register/control port identity')
    if full: need(digest(norm.encode())==S['IR_sha256'][mode],'Complete normalized IR including all ports/metadata')
    return dict(normalized_sha256=digest(norm.encode()),normalization='Only ModuleID/source_filename lines removed',complete_scalar_SSA=S['IR_scalar_SSA'],volatile_loads=22,volatile_stores=8,ordinary_C_ABI_proved=False,inter_region_CFG='Native typed edges, not ordinary C calls')
def md(text,llvm):
    text=text.replace('\\\n',' ').replace('\\\r\n',' ');target,rhs=text.split(': ',1)
    need(target.strip()=='native.o','Exact MD target')
    paths=[Path(x.replace('\\ ',' ')).resolve() for x in re.findall(r'(?:\\ |\S)+',rhs)]
    need(paths==[(HERE/'src/peripheral_write.v2.c').resolve(),(llvm.parent/'lib/clang/18/include/stdint.h').resolve()],'Complete two actual MD inputs')
    return paths
def source_contract(text,full=True):
    need(len(re.findall(r'^REGION void ',text,re.M))==7 and text.count('__builtin_unreachable();')==7,'Only seven private source regions')
    need(all(x not in text for x in ('.byte','.word','.2byte','.4byte','.incbin','memcpy','return a0;')),'No opcode/data carrier or unverified helper')
    for x in S['source_anchors']: need(x in text,'Original source read/write/arithmetic/port order anchor')
    operations=[x.strip() for x in text.splitlines() if re.match(r'\s*(?:a[0-6]\s*(?:=|\+=|<<=|&=|\|=)|(?:WORD|BYTE)\(.*=)',x)]
    need(operations==S['source_operation_lines'],'Complete ordered C scalar/volatile operations')
    if full: need(digest(text.encode())==S['pins'][S['source']],'Exact selected C source')
    return dict(C_arithmetic_and_volatile_memory=True,explicit_symbolic_edges=7,return_ports=1,private_regions=7,ordinary_C_ABI_proved=False)
def negatives(native,linked,ir,source,mode,llvm,md_text):
    out=[]
    def reject(name,fn,whole=False):
        try: fn()
        except (ValueError,IndexError,KeyError,StopIteration,struct.error,UnicodeError) as e: out.append(dict(name=name,rejected=True,whole_ELF_hash_enabled=whole,reason=str(e)))
        else: raise ValueError('Negative accepted '+name)
    for tag,e,islinked in [('native',native,False),('linked',linked,True)]:
        sections=[e.section('.peripheral_write')] if islinked else [e.section('.text.'+n) for n in NAMES]
        for section in sections:
            for row in decode(e.data(section),section['address']):
                fields=row['fields'];bit=15 if row['width']==4 and fields[0] in ('BLT','BGE') else 13 if fields[0]=='J' else 7
                at=section['offset']+row['offset'];raw=bytearray(e.raw);w=int.from_bytes(raw[at:at+row['width']],'little');raw[at:at+row['width']]=(w^(1<<bit)).to_bytes(row['width'],'little')
                reject(tag+'_'+section['name']+'_operand_'+str(row['offset']),lambda raw=raw,f=islinked:elf_contract(ELF(raw),f,False))
        f=next(s for s in e.symbols if s['name']==NAME);at=e.section('.symtab')['offset']+16*f['index']
        for label,delta,fmt,val in [('ABS',14,'<H',65521),('UND',14,'<H',0),('weak',12,'<B',34),('size',8,'<I',32),('value',4,'<I',f['value']+2)]:
            raw=bytearray(e.raw);struct.pack_into(fmt,raw,at+delta,val);reject(tag+'_'+label,lambda raw=raw,flag=islinked:elf_contract(ELF(raw),flag,False))
        raw=e.raw+b'\0';reject(tag+'_whole_file_tail',lambda raw=raw,flag=islinked:elf_contract(ELF(raw),flag,True),True)
    for i,rel in enumerate(native.relocations):
        section=next(s for s in native.sections if s['type']==4 and s['info']==rel['section'])
        ordinal=sum(x['section']==rel['section'] for x in native.relocations[:i])
        at=section['offset']+ordinal*12
        for label,delta,fmt,value in [('offset',0,'<I',rel['offset']+2),('type',4,'<I',(rel['symbol']<<8)|17),('addend',8,'<i',2)]:
            raw=bytearray(native.raw);struct.pack_into(fmt,raw,at+delta,value);reject('RELA_'+str(i)+'_'+label,lambda raw=raw:elf_contract(ELF(raw),False,False))
    for label,a,b in S['IR_mutations']:
        need(a in ir,'Actual IR control anchor');reject('IR_'+label,lambda text=ir.replace(a,b,1):ir_contract(text,mode,False))
    for label,a,b in S['source_mutations']:
        need(a in source,'Actual source mutation anchor');reject('source_'+label,lambda text=source.replace(a,b,1):source_contract(text,False))
    reject('MD_extra',lambda:md(md_text+' extra.h',llvm))
    return out
def evaluate(root,llvm,folder,mode):
    need(Path(root).resolve()==ROOT and mode in ('c','cpp'),'Canonical root/language')
    before=inputs(llvm);files={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
    expected={'native.o','native.ll','native.d',LINKED,'compile.log','IR.log','object.log','link.log','linked.log','recipes.json'}
    need(set(files) in (expected,expected|{'verification.json'}),'Complete actual output inventory')
    need(all(p.is_file() and not p.is_symlink() for p in folder.iterdir()),'Ordinary retained files only')
    commands=[dict(label=n,argv=portable(argv,llvm),returncode=0) for n,argv in P['recipes'](llvm,folder,mode,HERE/'src/peripheral_write.v2.c')]
    need(load(folder/'recipes.json')==commands,'All five actual command recipes')
    need(all((folder/(x+'.log')).read_bytes()==b'' for x in ('compile','IR','link')),'Successful actual compile/IR/link diagnostics')
    for log,file in [('object.log','native.o'),('linked.log',LINKED)]:
        text=(folder/log).read_text();need(str(folder/file) in text and all(n in text for n in NAMES),'Actual complete LLVM artifact readback')
    source=(HERE/'src/peripheral_write.v2.c').read_text();ir=(folder/'native.ll').read_text();mdtext=(folder/'native.d').read_text()
    native,linked=ELF(folder/'native.o'),ELF(folder/LINKED)
    facts=dict(native=elf_contract(native,False),linked=elf_contract(linked,True))
    sourcefacts=source_contract(source);irfacts=ir_contract(ir,mode);deps=md(mdtext,llvm);controls=negatives(native,linked,ir,source,mode,llvm,mdtext)
    need(before==inputs(llvm) and files=={p.name:sha(p) for p in folder.iterdir() if p.is_file()},'All inputs/artifacts stable across read-only check')
    record=portable(dict(schema='TSL9-peripheral-write-native-v1',language=mode,inputs=before,source=sourcefacts,IR=irfacts,ELFs=facts,commands=commands,MD_dependencies=deps,
        artifacts={n:dict(sha256=h,bytes=(folder/n).stat().st_size) for n,h in files.items() if n!='verification.json'},negative_controls=controls,
        original_span=[0x18ca4,0x18d78],firmware_ready=False,target_executed=False,ISA_emulated=False,physical_placement_proved=False,
        limitations=['Seven private architectural regions, not independent ordinary C ABI.','Exact nominal original212B/72i is a bounded static component proof; trusted Python standard-library runtime is not a hermetic input closure.','Physical chip/MMIO identity, aliases/asynchronous memory, caller ABI, full ROM/startup/IRQ and BLE OTA remain unproved.']),llvm)
    text=json.dumps(record,sort_keys=True,indent=2,ensure_ascii=True)+'\n'
    need(not re.search(r'(?i)(?<![a-z0-9_])[a-z]:[/\\\\]|/(?:users|home)/',text),'No public personal paths')
    return record,text
def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--out-dir',type=Path);g.add_argument('--replay',type=Path)
    p.add_argument('--language',choices=('c','cpp'));p.add_argument('--llvm-bin',type=Path,default=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin');p.add_argument('--require-firmware-ready',action='store_true');a=p.parse_args();llvm=a.llvm_bin.resolve()
    folder=(a.replay.parent if a.replay else a.out_dir).resolve();mode=load(a.replay)['language'] if a.replay else a.language
    need(mode in ('c','cpp') and folder.is_relative_to(HERE/'build') and folder.parent.name.startswith('verified-') and folder.name==mode,'Owned formal build folder/language')
    if not a.replay:
        before=inputs(llvm);need(not folder.exists(),'Create-only output');P['build'](llvm,folder,mode,HERE/'src/peripheral_write.v2.c');need(before==inputs(llvm),'Inputs stable across compilation')
    record,text=evaluate(ROOT,llvm,folder,mode)
    if a.replay: need(a.replay.read_bytes()==text.encode(),'Complete canonical read-only replay equality')
    else: (folder/'verification.json').write_bytes(text.encode())
    print(json.dumps(dict(result='PASS',language=mode,bytes=212,instructions=72,FUNCs=7,native_RELA=7,linked_RELA=0,original_code_equal=True,controls=len(record['negative_controls']),inputs=len(record['inputs']),receipt_sha256=digest(text.encode()),firmware_ready=False)))
    if a.require_firmware_ready:
        print('REJECTED: complete image, placement, original hardware/ABI/IRQ/ROM and OTA remain unproved.',file=sys.stderr);return 1
    return 0
if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError,OSError,IndexError,KeyError,StopIteration,struct.error,UnicodeError) as e: print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
