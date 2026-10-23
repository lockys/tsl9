#!/usr/bin/env python3
"""Finite source/SSA/native proof for one RV32 predicate; never execute output."""
from __future__ import annotations
import argparse,hashlib,json,os,re,runpy,struct,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
NAME='tsl9_dispatch_external_821e'
LINKED='COMPONENT-ONLY-NOT-FIRMWARE.elf'
SOURCE=HERE/'src/predicate.v2.c'
SOURCE_PIN='ed2eb7f9337e5bc6394ea3838631eb768f2fdfc82e1fd9fbc17c9181f4a59669'
PROBE_PIN='5b18783d17976cfddba71fc3c0ccacb7744bd86e444e99442a4e4af7db15c78b'
LINKER_PIN='f76d45856e05279e551e9368f43331d2082e4703d61580eb3bf33d53fecd39f6'
READER=ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
READER_PIN='8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8'
FIRMWARE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FW_PIN='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CONTRACT=ROOT/'analysis/record-dispatch-2026-10-23/next-821e-contract.json'
CONTRACT_PIN='ed51619ac720d13d14f31b9ba1e3c8362104e0e6a7a1cce84ed26652dd3e0ade'
ORIGINAL_PIN='4af30f18b196e304a5b6d30bb167ee2a02c567c4ffcf4e36bb4f72e6204bcdcd'
TOOLS={'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f','llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
STDINT_PIN='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
IR_PINS={"c":"a63c5c6503519b025ba5568f2b626901da48a91eb145680847090a45d48a8663","cpp":"8f69a4c20ec2084d8d9434b5d0d82e4c839ff22c1623af26501a1f9fdbc2d96a"}
META={"native":{"header":[1,243,1,0,0,548,1,52,0,0,40,9,1],"program_headers":[],"sections":[{"name_offset":0,"type":0,"flags":0,"address":0,"offset":0,"size":0,"link":0,"info":0,"align":0,"entsize":0,"index":0,"name":""},{"name_offset":113,"type":3,"flags":0,"address":0,"offset":404,"size":144,"link":0,"info":0,"align":1,"entsize":0,"index":1,"name":".strtab"},{"name_offset":1,"type":1,"flags":6,"address":0,"offset":52,"size":0,"link":0,"info":0,"align":2,"entsize":0,"index":2,"name":".text"},{"name_offset":64,"type":1,"flags":6,"address":0,"offset":52,"size":42,"link":0,"info":0,"align":2,"entsize":0,"index":3,"name":".text.tsl9_dispatch_external_821e"},{"name_offset":7,"type":1,"flags":48,"address":0,"offset":94,"size":159,"link":0,"info":0,"align":1,"entsize":1,"index":4,"name":".comment"},{"name_offset":34,"type":1,"flags":0,"address":0,"offset":253,"size":0,"link":0,"info":0,"align":1,"entsize":0,"index":5,"name":".note.GNU-stack"},{"name_offset":16,"type":1879048195,"flags":0,"address":0,"offset":253,"size":52,"link":0,"info":0,"align":1,"entsize":0,"index":6,"name":".riscv.attributes"},{"name_offset":50,"type":1879002115,"flags":2147483648,"address":0,"offset":404,"size":0,"link":8,"info":0,"align":1,"entsize":0,"index":7,"name":".llvm_addrsig"},{"name_offset":121,"type":2,"flags":0,"address":0,"offset":308,"size":96,"link":1,"info":5,"align":4,"entsize":16,"index":8,"name":".symtab"}],"symbols":[{"index":0,"name":"","value":0,"size":0,"info":0,"other":0,"section":0},{"index":1,"name":"predicate.v2.c","value":0,"size":0,"info":4,"other":0,"section":65521},{"index":2,"name":"$x.0","value":0,"size":0,"info":0,"other":0,"section":3},{"index":3,"name":"$d.1","value":0,"size":0,"info":0,"other":0,"section":4},{"index":4,"name":"$d.2","value":0,"size":0,"info":0,"other":0,"section":6},{"index":5,"name":"tsl9_dispatch_external_821e","value":0,"size":42,"info":18,"other":0,"section":3}],"size":908,"sha256":"26d3ca185e03cf880f6dbc96e73c1820824b986b22521c4e83124c89ad2f2b1f"},"linked":{"header":[2,243,1,33310,52,764,1,52,32,4,40,6,4],"program_headers":[[6,52,32820,32820,128,128,4,4],[1,0,32768,32768,180,180,4,4096],[1,542,33310,33310,42,42,5,4096],[1685382481,0,0,0,0,0,6,0]],"sections":[{"name_offset":0,"type":0,"flags":0,"address":0,"offset":0,"size":0,"link":0,"info":0,"align":0,"entsize":0,"index":0,"name":""},{"name_offset":1,"type":1,"flags":6,"address":33310,"offset":542,"size":42,"link":0,"info":0,"align":2,"entsize":0,"index":1,"name":".predicate"},{"name_offset":12,"type":1,"flags":6,"address":33352,"offset":584,"size":0,"link":0,"info":0,"align":2,"entsize":0,"index":2,"name":".text"},{"name_offset":18,"type":2,"flags":0,"address":0,"offset":584,"size":80,"link":5,"info":4,"align":4,"entsize":16,"index":3,"name":".symtab"},{"name_offset":26,"type":3,"flags":0,"address":0,"offset":664,"size":44,"link":0,"info":0,"align":1,"entsize":0,"index":4,"name":".shstrtab"},{"name_offset":36,"type":3,"flags":0,"address":0,"offset":708,"size":54,"link":0,"info":0,"align":1,"entsize":0,"index":5,"name":".strtab"}],"symbols":[{"index":0,"name":"","value":0,"size":0,"info":0,"other":0,"section":0},{"index":1,"name":"predicate.v2.c","value":0,"size":0,"info":4,"other":0,"section":65521},{"index":2,"name":"$x.0","value":33310,"size":0,"info":0,"other":0,"section":1},{"index":3,"name":"$d.2","value":0,"size":0,"info":0,"other":0,"section":65521},{"index":4,"name":"tsl9_dispatch_external_821e","value":33310,"size":42,"info":18,"other":0,"section":1}],"size":1004,"sha256":"4b02f17b1832c9bbaf8a9a36fa6a4917f67c28129044762ff793c18d6d455abb"}}
EXPECTED=[('addi',15,3,84),('lw',15,15,0),('lbu',14,15,4),('li',15,0),('andi',14,8),('bnez',14,38),('li',14,2),('li',15,0),('bltu',14,10,38),('addi',15,3,192),('add',15,15,10),('lbu',15,15,1),('sltiu',15,15,3),('mv',10,15),('ret',1)]
def need(ok,message):
    if not ok:raise ValueError(message)
def digest(data):return hashlib.sha256(data).hexdigest()
def sha(p):return digest(Path(p).read_bytes())
def load_modules():
    need(sha(HERE/'probe.py')==PROBE_PIN and sha(READER)==READER_PIN,'frozen builder/ELF reader')
    return runpy.run_path(str(HERE/'probe.py'),run_name='predicate_builder'),runpy.run_path(str(READER),run_name='predicate_reader')['ELF']
probe,ELF=load_modules()
def portable(value,llvm):
    value=probe['portable'](value,llvm)
    if isinstance(value,dict):return {portable(k,llvm):portable(v,llvm) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [portable(v,llvm) for v in value]
    if isinstance(value,str):
        for p,t in [(str(Path(sys.executable).resolve()),'$'+'{PYTHON_EXECUTABLE}'),(str(Path(os.__file__).resolve().parent),'$'+'{PYTHON_STDLIB}')]:
            value=value.replace(p.replace('\\','/'),t)
    return value
def inventory(folder):
    need(folder.is_dir() and all(p.is_file() and not p.is_symlink() for p in folder.iterdir()),'ordinary complete output directory')
    return {p.name:sha(p) for p in folder.iterdir()}
def input_snapshot(llvm):
    expected={SOURCE:SOURCE_PIN,HERE/'probe.py':PROBE_PIN,HERE/'component.ld':LINKER_PIN,READER:READER_PIN,FIRMWARE:FW_PIN,CONTRACT:CONTRACT_PIN,llvm.parent/'lib/clang/18/include/stdint.h':STDINT_PIN}
    expected.update({llvm/n:p for n,p in TOOLS.items()})
    for p,pin in expected.items():need(sha(p)==pin,'actual pinned input '+p.name)
    # Pin the actual interpreter and local standard-library modules read by this
    # finite verifier, without embedding their user-profile paths in receipts.
    runtime=[Path(sys.executable).resolve(),Path(__file__).resolve()]
    for module in [argparse,hashlib,json,json.decoder,json.encoder,json.scanner,os,re,struct,subprocess,runpy]:
        p=getattr(module,'__file__',None)
        if p and Path(p).is_file():runtime.append(Path(p).resolve())
    runtime.extend([(Path(re.__file__).parent/n).resolve() for n in ('_parser.py','_compiler.py','_constants.py')])
    for p in runtime:expected[p]=sha(p)
    return {p:sha(p) for p in expected}
def sx(v,b):return v-(1<<b) if v&(1<<(b-1)) else v
def typed(code,full=True):
    need(len(code)==42,'exact42B code')
    at=0;rows=[]
    while at<len(code):
        half=int.from_bytes(code[at:at+2],'little');width=4 if half&3==3 else 2;w=int.from_bytes(code[at:at+width],'little')
        if width==4:
            op=w&127;f=(w>>12)&7;rd=(w>>7)&31;rs=(w>>15)&31;imm=sx(w>>20,12)
            if op==0x13 and f in (0,3):row=('addi' if f==0 else 'sltiu',rd,rs,imm)
            elif op==3 and f==4:row=('lbu',rd,rs,imm)
            elif op==0x63 and f==6:
                im=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
                row=('bltu',rs,(w>>20)&31,at+sx(im,13))
            else:raise ValueError('unsupported or extra32-bit instruction')
        elif half&3==0 and half>>13==2:
            im=((half>>10)&7)*8+((half>>6)&1)*4+((half>>5)&1)*64
            row=('lw',8+((half>>2)&7),8+((half>>7)&7),im)
        elif half&3==1 and half>>13==2:row=('li',(half>>7)&31,sx(((half>>12)&1)*32+((half>>2)&31),6))
        elif half&3==1 and half>>13==4 and (half>>10)&3==2:row=('andi',8+((half>>7)&7),sx(((half>>12)&1)*32+((half>>2)&31),6))
        elif half&3==1 and half>>13==7:
            im=(((half>>12)&1)<<8)|(((half>>10)&3)<<3)|(((half>>5)&3)<<6)|(((half>>3)&3)<<1)|(((half>>2)&1)<<5)
            row=('bnez',8+((half>>7)&7),at+sx(im,9))
        elif half&3==2 and half>>13==4:
            rd=(half>>7)&31;rs=(half>>2)&31
            if half==0x8082:row=('ret',1)
            elif rs and rd:row=('add',rd,rd,rs) if half&(1<<12) else ('mv',rd,rs)
            else:raise ValueError('extra compressed control/frame instruction')
        else:raise ValueError('unsupported compressed instruction')
        rows.append(dict(offset=at,width=width,fields=list(row)));at+=width
    need([tuple(r['fields']) for r in rows]==EXPECTED,'all15 typed operands/unsigned widths/targets/residues')
    need(at==42 and len(rows)==15,'complete instruction boundaries')
    if full:need(digest(code)==ORIGINAL_PIN,'whole original42-byte equality')
    return rows
def elf_contract(e,linked,full=True):
    m=META['linked' if linked else 'native']
    need(e.raw[:16]==b'\x7fELF\x01\x01\x01'+b'\0'*9,'exact ELF32 little-endian identity')
    need(e.header==m['header'] and e.program_headers==m['program_headers'] and len(e.raw)==m['size'],'exact ELF headers/program metadata/extent')
    need(e.sections==m['sections'] and e.symbols==m['symbols'] and not e.relocations,'exact sections/symbols/locals;0UND/ABSproviders/RELAs')
    f=next(s for s in e.symbols if s['name']==NAME);section=e.sections[f['section']]
    need(f['info']==18 and f['size']==42 and f['value']==(0x821e if linked else 0),'one genuine strong FUNC')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len(alloc)==1 and alloc[0]==section and section['size']==42 and section['type']==1 and section['flags']==6 and section['align']==2,'one42B AX allocation, no extra frame/data')
    rows=typed(e.data(section),full)
    if full:need(digest(e.raw)==m['sha256'],'complete actual ELF pin')
    return dict(sha256=digest(e.raw),header=e.header,program_headers=e.program_headers,sections=e.sections,symbols=e.symbols,typed_rows=rows,UND=[],global_ABS=[],RELA=[],allocated_bytes=42,functions=1)
def source_contract(text,full=True):
    need('uint32_t tsl9_dispatch_external_821e(uint32_t index)' in text,'full32 input source signature')
    need(all(x=='' for x in re.findall(r'__asm__ volatile\("([^"]*)"',text)),'all algorithm-free empty architecture ports')
    anchors=['result __asm__("a5") = live_gp() + 84u','*(volatile uint32_t *)(uintptr_t)result','*(volatile uint8_t *)(uintptr_t)(result + 4u)','result = 0;','condition &= 8u;','if (condition != 0)','condition = 2;','result = 0;','if (incoming > condition)','result = live_gp() + 192u;','result += incoming;','*(volatile uint8_t *)(uintptr_t)(result + 1u)','result = result < 3u ? 1u : 0u;','incoming = result;','return incoming;']
    pos=0
    for item in anchors:pos=text.index(item,pos)+len(item)
    need(text.count('volatile uint32_t')==1 and text.count('volatile uint8_t')==2,'only3 reads/no stores in C')
    if full:need(digest(text.encode())==SOURCE_PIN,'complete LF source pin')
    return dict(empty_architecture_ports_only=True,full32_unsigned_input=True,volatile_read_widths=[32,8,8],stores=[],GP_samples=2,raw_opcode_carrier=False)
def normalize_ir(text):
    return '\n'.join(s for s in text.splitlines() if not s.startswith('; ModuleID = ') and not s.startswith('source_filename = '))+'\n'
IR_ANCHORS=[
'%3 = tail call i32 asm sideeffect "", "={x3},~{memory}"()',
'%4 = add i32 %3, 84','%7 = load volatile i32, ptr %6','%9 = add i32 %8, 4','%11 = load volatile i8, ptr %10','%16 = and i32 %15, 8','%20 = icmp eq i32 %18, 0','br i1 %20, label %21, label %39',
'(i32 2, i32 %19)','(i32 %23, i32 0)','%25 = icmp ugt i32 %2, %23','br i1 %25, label %39, label %26',
'%27 = tail call i32 asm sideeffect "", "={x3},~{memory}"()','%28 = add i32 %27, 192','%30 = add i32 %29, %2','%32 = add i32 %31, 1','%34 = load volatile i8, ptr %33','%37 = icmp ult i32 %36, 3','%40 = phi i32 [ %19, %1 ], [ %24, %21 ], [ %38, %26 ]','%41 = phi i32 [ %18, %1 ], [ %23, %21 ], [ %23, %26 ]','ret i32 %42']
def ir_contract(text,language,full=True):
    norm=normalize_ir(text);body=norm[norm.index('define '):norm.index('\n}\n')+3]
    need(len(re.findall(r'^define ',norm,re.M))==1 and NAME in body and 'alloca ' not in body and 'store ' not in body,'single leaf IR/no stack/store')
    need(len(re.findall('load volatile i32',body))==1 and len(re.findall('load volatile i8',body))==2 and len(re.findall(re.escape('={x3}'),body))==2,'3 volatile loads/2 fresh physicalGP samples')
    pos=0
    anchors=[item.replace('tail call i32 asm sideeffect "", "={x3}', 'tail call noundef i32 asm sideeffect "", "={x3}') if language=='cpp' else item for item in IR_ANCHORS]
    for item in anchors:pos=body.index(item,pos)+len(item)
    need(all(x=='' for x in re.findall(r'asm sideeffect "([^"]*)"',body)),'IR ports have no executable algorithm strings')
    if full:need(digest(norm.encode())==IR_PINS[language],'complete per-language normalized SSA/CFG/metadata pin')
    return dict(normalization='Only producer ModuleID/source_filename lines omitted; LF',normalized_sha256=digest(norm.encode()),complete_normalized_IR=norm,complete_SSA_body=body,volatile_loads=[32,8,8],stores=[],GP_samples=2)
def controls(native,linked,ir,source,language):
    out=[]
    def trial(name,run,whole=False):
        try:run()
        except (ValueError,IndexError,KeyError,StopIteration,struct.error,UnicodeError) as error:out.append(dict(name=name,rejected=True,whole_hash_enabled=whole,reason=str(error)))
        else:raise ValueError('negative accepted '+name)
    for tag,e,is_linked in [('native',native,False),('linked',linked,True)]:
        section=e.section('.predicate' if is_linked else '.text.'+NAME);code=e.data(section)
        for row in typed(code):
            at=section['offset']+row['offset'];b=bytearray(e.raw);w=int.from_bytes(b[at:at+row['width']],'little');bit=2 if row['fields'][0]=='lw' else 7
            b[at:at+row['width']]=(w^(1<<bit)).to_bytes(row['width'],'little');trial(tag+'_typed_'+str(row['offset']),lambda b=b,flag=is_linked:elf_contract(ELF(b),flag,False))
        sym=next(s for s in e.symbols if s['name']==NAME);at=e.section('.symtab')['offset']+16*sym['index']
        for name,delta,fmt,val in [('UND',14,'<H',0),('ABS',14,'<H',65521),('weak',12,'<B',34),('size',8,'<I',40),('value',4,'<I',sym['value']+2)]:
            b=bytearray(e.raw);struct.pack_into(fmt,b,at+delta,val);trial(tag+'_'+name,lambda b=b,flag=is_linked:elf_contract(ELF(b),flag,False))
        for name,delta,val in [('write',8,7),('align',32,4),('data',4,8)]:
            b=bytearray(e.raw);struct.pack_into('<I',b,e.header[5]+40*section['index']+delta,val);trial(tag+'_section_'+name,lambda b=b,flag=is_linked:elf_contract(ELF(b),flag,False))
        b=bytearray(e.raw);padding=e.header[5]-1 if is_linked else e.section('.symtab')['offset']-1;b[padding]^=1;trial(tag+'_whole_file_padding',lambda b=b,flag=is_linked:elf_contract(ELF(b),flag,True),True)
    changes=[('configGP','%4 = add i32 %3, 84','%4 = add i32 %3, 85'),('configWidth','load volatile i32','load volatile i16'),('configOffset','%9 = add i32 %8, 4','%9 = add i32 %8, 5'),('mask','%16 = and i32 %15, 8','%16 = and i32 %15, 16'),('earlyCFG','br i1 %20, label %21, label %39','br i1 %20, label %39, label %21'),('signedIndex','icmp ugt i32 %2','icmp sgt i32 %2'),('staleGP','%28 = add i32 %27, 192','%28 = add i32 %3, 192'),('stateOffset','%32 = add i32 %31, 1','%32 = add i32 %31, 0'),('stateWidth','%34 = load volatile i8','%34 = load volatile i16'),('threshold','icmp ult i32 %36, 3','icmp ult i32 %36, 4'),('signedState','icmp ult i32 %36','icmp slt i32 %36'),('wrongPhi','[ %24, %21 ]','[ %19, %21 ]'),('wrongReturn','ret i32 %42','ret i32 %40')]
    for name,a,b in changes:
        need(a in ir,'actual IR mutation anchor');trial('IR_'+name,lambda text=ir.replace(a,b,1):ir_contract(text,language,False))
    for name,a,b in [('sourceMask','condition &= 8u','condition &= 16u'),('sourceState','result + 1u','result + 0u'),('sourceSigned','incoming > condition','(int32_t)incoming > (int32_t)condition'),('sourceASM','__asm__ volatile(""','__asm__ volatile(".byte 0"')]:
        need(a in source,'source mutation anchor');trial(name,lambda text=source.replace(a,b,1):source_contract(text,False))
    return out
def md_dependencies(folder,llvm):
    text=(folder/'native.d').read_text().replace('\\\n',' ').replace('\\\r\n',' ')
    target,rhs=text.split(': ',1);need(target.strip()=='native.o','exact dependency target')
    values=[Path(x.replace('\\ ',' ')).resolve() for x in re.findall(r'(?:\\ |\S)+',rhs)]
    need(values==[SOURCE.resolve(),(llvm.parent/'lib/clang/18/include/stdint.h').resolve()],'complete2 actual MD dependencies')
    return values
def evaluate(root,llvm,folder,language):
    need(Path(root).resolve()==ROOT and language in ('c','cpp'),'canonical root/language')
    before=input_snapshot(llvm);inv=inventory(folder);expected={'native.o','native.ll','native.d',LINKED,'compile.log','IR.log','object.log','link.log','linked.log','recipes.json'}
    need(set(inv) in (expected,expected|{'verification.json'}),'complete10artifact inventory')
    commands=[dict(label=n,argv=portable(argv,llvm),returncode=0) for n,argv in probe['recipes'](llvm,folder,language,SOURCE)]
    need(json.loads((folder/'recipes.json').read_bytes())==commands,'all5 actual exact recipes')
    need(all(not (folder/(n+'.log')).read_bytes() for n in ('compile','IR','link')),'empty actual compiler/IR/link diagnostics')
    for log,file in [('object.log','native.o'),('linked.log',LINKED)]:
        text=(folder/log).read_text();need(str(folder/file) in text and NAME in text,'reader log bound to actual artifact')
    firmware=FIRMWARE.read_bytes();original=firmware[0x21e:0x248];typed(original)
    contract=json.loads(CONTRACT.read_bytes());need(bytes.fromhex(''.join(r['bytes'] for r in contract['rows']))==original,'original retained evidence42B/15rows')
    source=SOURCE.read_text();source_facts=source_contract(source);ir=(folder/'native.ll').read_text()
    native=ELF(folder/'native.o');linked=ELF(folder/LINKED);elfs={'native.o':elf_contract(native,False),LINKED:elf_contract(linked,True)}
    ir_facts=ir_contract(ir,language);negative=controls(native,linked,ir,source,language);deps=md_dependencies(folder,llvm)
    need(before==input_snapshot(llvm) and inventory(folder)==inv,'all inputs/artifacts stable across read-only replay')
    record=dict(schema='TSL9-record-predicate-native-v1',language=language,source_sha256=SOURCE_PIN,original_VA=[0x821e,0x8248],firmware_ready=False,target_executed=False,ISA_emulated=False,compiler_profile_search=False,
        inputs=[dict(path=str(p),sha256=pin,size=p.stat().st_size) for p,pin in before.items()],input_snapshots_equal=True,
        commands=commands,MD_dependencies=[str(p) for p in deps],artifacts=[dict(path=str(folder/n),sha256=pin,size=(folder/n).stat().st_size) for n,pin in inv.items() if n!='verification.json'],
        source_contract=source_facts,IR=ir_facts,ELFs=elfs,negative_controls=negative,
        limitations=['Only one42B predicate is reconstructed; dynamic GP/memory/IRQ/fault/hardware behavior is not executed or proved.','C ports are RV32/profile-specific; ordinary HOST execution or a general compiler/ABI equivalence is not claimed.','Function eligibility, byte equality and nominal placement do not establish seat/DND/CAN semantics, a full image, delivery or flash compatibility.'])
    record=portable(record,llvm);encoded=json.dumps(record,sort_keys=True,indent=2,ensure_ascii=True)+'\n'
    need(not re.search(r'(?i)(?<![a-z0-9_])[a-z]:[/\\]|/(?:users|home)/',encoded),'portable LF receipt/no personal path')
    return record,encoded
def main():
    p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--out-dir',type=Path);mode.add_argument('--replay',type=Path);p.add_argument('--language',choices=['c','cpp']);p.add_argument('--llvm-bin',type=Path,default=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin');p.add_argument('--require-firmware-ready',action='store_true');a=p.parse_args();llvm=a.llvm_bin.resolve()
    if a.replay:
        receipt=a.replay.resolve();folder=receipt.parent;saved=json.loads(receipt.read_bytes());language=saved['language'];need(a.language in (None,language),'same replay language')
    else:need(a.language is not None,'explicit build language');language=a.language;folder=a.out_dir.resolve()
    need(folder.is_relative_to(HERE/'build') and folder.parent.name.startswith('verified-') and folder.name==language,'fresh owned formal build folder')
    if not a.replay:
        before=input_snapshot(llvm);need(not folder.exists(),'no overwrite');probe['build'](llvm,folder,language,SOURCE);need(before==input_snapshot(llvm),'complete inputs stable across native compile/link')
    record,text=evaluate(ROOT,llvm,folder,language)
    if a.replay:need(saved==record and receipt.read_bytes()==text.encode(),'complete canonical LF record/byte replay equality')
    else:(folder/'verification.json').write_bytes(text.encode())
    print(json.dumps(dict(result='PASS',language=language,bytes=42,instructions=15,FUNC=1,UND=0,RELA=0,controls=len(record['negative_controls']),inputs=len(record['inputs']),artifacts=len(record['artifacts']),recipes=len(record['commands']),receipt_sha256=digest(text.encode()),firmware_ready=False)))
    if a.require_firmware_ready:print('REJECTED: complete firmware/resident/memory/hardware/flashability remain unproved.',file=sys.stderr);return 1
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,IndexError,KeyError,StopIteration,struct.error,UnicodeError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
