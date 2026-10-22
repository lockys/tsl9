#!/usr/bin/env python3
"""Independent ELF/JAL/image readback; never links, emits BIN, or executes code."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
SITE,CODE,ORIGIN=0x19896,0x1b000,0x8000
ENTRY='tsl9_adc_config_1892e'
BASE_SHA='3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee'
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ABI_SEAL='4ec2d4d6d851e7f4b27477ef336da273548889341c3476f4cc278fbcb31d248b'
TOOLS={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f','llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
def need(v,m):
    if not v:raise ValueError(m)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def sha(p):return digest(Path(p).read_bytes())
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def case(root,n):return next(p for p in(root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def locate(root,p):
    x=root/p
    if x.is_file():return x
    if p.startswith('apk-analysis/tsl9-'):
        n,tail=p[len('apk-analysis/tsl9-'):].split('/',1);return case(root,n)/tail
    return x
def module(p):
    s=importlib.util.spec_from_file_location('independent_link_'+p.parent.name+'_'+p.stem,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def abi(root):
    folder=case(root,'v4160-adc-caller-2026-10-22')/'abi-review';need(sha(folder/'seal.json')==ABI_SEAL,'Exact previous ABI seal')
    for n,pin in read(folder/'seal.json')['members'].items():need(sha(folder/n)==pin,'Closed immutable ABI member '+n)
    return module(folder/'review.py')
def stable(root):
    a=abi(root);result=a.stable(root)
    for rel,pin in read(HERE/'reference-pins.json')['sources'].items():need(sha(locate(root,rel))==pin,'Frozen integration source '+rel)
    return result
def source_audit(root,folder,record):
    src=case(root,'v4160-adc-caller-2026-10-22')/'integration';asm=(src/'call_site.s').read_text();link=(src/'caller.ld').read_text()
    need(asm.count('jal ra, '+ENTRY)==1 and '.option norelax' in asm and '.option norvc' in asm and not any(x in asm for x in('.incbin','.include','.word','.byte')),'Actual assembler source emits one real symbol JAL, no copied opcode/payload')
    need(link.count('PT_LOAD FLAGS(5)')==2 and '.caller 0x19896' in link and '.adc 0x1B000' in link and 'ENTRY('+ENTRY+')' in link and 'PROVIDE' not in link,'Actual linker source two precise RX owners and real C entry')
    tools=record['tools'];native=Path(record['native_folder'])/'native.o'
    expected=[('assemble-caller',[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac_zicsr_zifencei','-mabi=ilp32','-mno-relax','-x','assembler','-c',src/'call_site.s','-o',folder/'call_site.o']),('link-real-C',[tools['ld.lld'],'--gc-sections','--no-relax','-T',src/'caller.ld',folder/'call_site.o',native,'-Map='+str(folder/'linked.map'),'-o',folder/'linked.elf']),('complete-static-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'linked.elf'])]
    need([(x['label'],x['argv']) for x in record['commands']]==[(name,[str(x) for x in argv]) for name,argv in expected],'Independent exact real assembler/linker/static-disassembly recipes')
    return dict(actual_sources_read=True,one_symbolic_JAL=True,two_exact_RX_LOAD_script=True,no_numerical_provider=True)

class ELF:
    """Separate bounded struct reader for ELF32 little-endian RISC-V evidence."""
    def __init__(self,raw):
        self.raw=raw;need(len(raw)>=52 and raw[:7]==b'\x7fELF\x01\x01\x01','ELF32 little-endian header')
        self.kind,machine=struct.unpack_from('<HH',raw,16);need(machine==243,'RISC-V machine');self.entry,self.phoff,self.shoff,self.flags=struct.unpack_from('<4I',raw,24)
        eh,ps,pn,ss,sn,ns=struct.unpack_from('<6H',raw,40);need(eh==52 and ss==40 and sn>0 and self.shoff+sn*ss<=len(raw) and ns<sn,'Bounded section table')
        self.sections=[]
        for i in range(sn):
            at=self.shoff+i*ss;v=struct.unpack_from('<10I',raw,at);x=dict(zip(('name_offset','type','flags','address','offset','size','link','info','align','entry_size'),v));x.update(index=i,header_offset=at)
            need(x['type']==8 or x['offset']+x['size']<=len(raw),'Bounded section payload');self.sections.append(x)
        names=self.data(self.sections[ns])
        for x in self.sections:x['name']=self.string(names,x['name_offset'])
        self.byname={x['name']:x for x in self.sections};self.symbols=[];tables={}
        for x in self.sections:
            if x['type']!=2:continue
            need(x['entry_size']==16 and x['size']%16==0 and x['link']<sn,'Symbol table bounds');strings=self.data(self.sections[x['link']]);rows=[]
            for at in range(x['offset'],x['offset']+x['size'],16):
                n,val,size,info,other,index=struct.unpack_from('<IIIBBH',raw,at);rows.append(dict(name=self.string(strings,n),value=val,size=size,info=info,other=other,index=index))
            self.symbols.extend(rows);tables[x['index']]=rows
        self.relocations=[]
        for x in self.sections:
            if x['type'] not in(4,9):continue
            need(x['type']==4 and x['entry_size']==12 and x['size']%12==0 and x['link'] in tables and x['info']<sn,'Real RELA table bounds')
            for at in range(x['offset'],x['offset']+x['size'],12):
                off,info,addend=struct.unpack_from('<IIi',raw,at);need(info>>8<len(tables[x['link']]),'Real relocation symbol index');self.relocations.append(dict(owner=self.sections[x['info']]['name'],offset=off,type=info&255,addend=addend,symbol=tables[x['link']][info>>8]))
        self.programs=[]
        if pn:
            need(ps==32 and self.phoff+pn*ps<=len(raw),'Bounded program table')
            for i in range(pn):
                x=dict(zip(('type','offset','vaddr','paddr','filesz','memsz','flags','align'),struct.unpack_from('<8I',raw,self.phoff+i*ps)));x['header_offset']=self.phoff+i*ps;need(x['offset']+x['filesz']<=len(raw),'Bounded segment data');self.programs.append(x)
    @staticmethod
    def string(data,n):
        need(n<len(data),'Bounded string index');end=data.find(b'\0',n);need(end>=n,'Terminated string');return data[n:end].decode('utf8')
    def data(self,s):return self.raw[s['offset']:s['offset']+s['size']]
    def function(self,f):
        need(0<f['index']<len(self.sections),'Real function section');s=self.sections[f['index']];at=f['value']-(s['address'] if self.kind==2 else 0);need(0<=at and at+f['size']<=s['size'],'Whole function inside owner');return self.data(s)[at:at+f['size']]
def jal(raw,pc):
    need(len(raw)==4,'Exactly four actual caller bytes');w=int.from_bytes(raw,'little');need(w&127==0x6f,'Real JAL encoding');imm=((w>>31)&1)<<20|((w>>21)&1023)<<1|((w>>20)&1)<<11|((w>>12)&255)<<12
    if imm&(1<<20):imm-=1<<21
    return dict(rd=(w>>7)&31,displacement=imm,target=(pc+imm)&0xffffffff,link_value=(pc+4)&0xffffffff)
def caller_gate(raw):
    row=jal(raw,SITE);need(row==dict(rd=1,displacement=0x176a,target=CODE,link_value=0x1989a),'Actual RA-preserving JAL to linked C');return row
def linked_gate(raw,code):
    e=ELF(raw);need(e.kind==2 and e.flags==1 and e.entry==CODE and not e.relocations,'Actual fully linked RV32/RVC entry; no RELA')
    need(not any(x['index']==0 and x['name'] for x in e.symbols) and not any(x['index']==0xfff1 and x['info']>>4 for x in e.symbols),'No UND/ABS provider')
    alloc=[x for x in e.sections if x['flags']&2 and x['size']];need(len(alloc)==2 and {x['name'] for x in alloc}=={'.caller','.adc'} and all(x['type']==1 and x['flags']==6 for x in alloc),'Only two true executable allocations')
    need(not any(x['type']==8 and x['flags']&2 for x in e.sections),'No allocated NOBITS')
    a,b=e.byname['.caller'],e.byname['.adc'];need((a['address'],a['size'],b['address'],b['size'])==(SITE,4,CODE,110),'Exact independent caller/C section extents')
    caller_gate(e.data(a));funcs=[x for x in e.symbols if x['info']&15==2 and x['size']];need(len(funcs)==1 and funcs[0]['name']==ENTRY and funcs[0]['info']==18 and funcs[0]['other']==0 and funcs[0]['value']==CODE and funcs[0]['size']==110 and funcs[0]['index']==b['index'],'Only selected real C FUNC remains')
    need(e.function(funcs[0])==e.data(b)==code,'Actual linked selected function equals native bytes')
    loads=[x for x in e.programs if x['type']==1];need(len(loads)==2,'Exactly two actual LOADs')
    for p,s in zip(sorted(loads,key=lambda x:x['vaddr']),(a,b)):
        need(p['vaddr']==p['paddr']==s['address'] and p['offset']==s['offset'] and p['filesz']==p['memsz']==s['size'] and p['flags']==5,'Each RX LOAD owns exactly one section; no runtime hole/header/padding')
        need(p['align']>0 and p['align']&(p['align']-1)==0 and p['offset']%p['align']==p['vaddr']%p['align'],'Actual LOAD alignment congruence')
    return e,loads
def image_gate(raw,baseline,patch,code):
    at=SITE-ORIGIN;need(len(baseline)==77824 and ORIGIN+len(baseline)==CODE and len(raw)==78848,'Exact baseline boundary and one1024-byte append')
    need(raw[:at]==baseline[:at] and raw[at:at+4]==patch and raw[at+4:77824]==baseline[at+4:],'Entire preimage unchanged except actual four-byte caller')
    need(raw[77824:77934]==code and raw[77934:]==b'\xff'*914,'Exactly110 linked C bytes followed by914 non-code FF bytes')
def controls(elf,patch,image,baseline,code):
    out=[]
    variants=[]
    a=bytearray(patch);a[0]^=128;variants.append(('caller_RA_changed',bytes(a)))
    a=bytearray(patch);a[3]^=1;variants.append(('caller_target_changed',bytes(a)))
    for name,raw in variants:
        try:caller_gate(raw)
        except ValueError:out.append(dict(case=name,mutated_sha256=digest(raw),rejected=True));continue
        raise ValueError('Accepted raw caller control')
    adc=elf.byname['.adc'];load=next(x for x in elf.programs if x['type']==1 and x['vaddr']==CODE)
    for name,offset,value in(('section_size_changed',adc['header_offset']+20,112),('LOAD_hidden_mem_hole',load['header_offset']+20,114)):
        raw=bytearray(elf.raw);struct.pack_into('<I',raw,offset,value)
        try:linked_gate(bytes(raw),code)
        except ValueError:out.append(dict(case=name,offset=offset,mutated_sha256=digest(raw),rejected=True));continue
        raise ValueError('Accepted actual ELF extent control')
    for name,offset in(('inherited_preimage_changed',0),('native_payload_changed',77824),('noncode_tail_changed',78847)):
        raw=bytearray(image);raw[offset]^=1
        try:image_gate(bytes(raw),baseline,patch,code)
        except ValueError:out.append(dict(case=name,offset=offset,mutated_sha256=digest(raw),rejected=True));continue
        raise ValueError('Accepted actual image control')
    return out
def inspect(root,receipt):
    root=Path(root).resolve();receipt=Path(receipt).resolve();folder=receipt.parent;stable(root);record=read(receipt);a=abi(root);proof=a.replay(root,Path(record['abi_receipt']));need(proof['normal_caller_projection']['conditionally_supported'],'Sealed conditional normal caller proof')
    need(record['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt},'Actual immutable integration archive inventory')
    for p,pin in record['source_pins'].items():need(sha(p)==pin,'Every recorded integration input identity')
    for n,pin in TOOLS.items():need(sha(record['tools'][n])==pin,'Independent actual assembler/linker/disassembler hash')
    sources=source_audit(root,folder,record)
    for command in record['commands']:need(command['exit']==0 and sha(folder/command['log'])==command['sha256'],'Actual successful integration logs')
    need('--gc-sections' in record['commands'][1]['argv'] and '--no-relax' in record['commands'][1]['argv'],'Actual linker GC and no-relax flags')
    baseline=Path(record['baseline']).read_bytes();firmware=Path(record['firmware']).read_bytes();need(digest(baseline)==BASE_SHA and len(baseline)==77824 and digest(firmware)==FW_SHA and len(firmware)==76800,'Exact existing baseline and original firmware')
    at=SITE-ORIGIN;need(baseline[at:at+4]==firmware[at:at+4] and jal(firmware[at:at+4],SITE)['target']==0x1892e,'Original caller unchanged inside inherited baseline')
    native=ELF((Path(record['native_folder'])/'native.o').read_bytes());need(native.kind==1 and native.flags==1,'Actual source native ET_REL');funcs=[f for f in native.symbols if f['info']&15==2 and f['size']];need(len(funcs)==5,'All five native globals exist before GC');f=next(x for x in funcs if x['name']==ENTRY);code=native.function(f);need(len(code)==110 and digest(code)==proof['selected']['code_sha256'],'Real proved C machine bytes')
    obj=ELF((folder/'call_site.o').read_bytes());need(obj.kind==1 and obj.flags==1 and len(obj.relocations)==1,'One actual ET_REL caller relocation');r=obj.relocations[0]
    need(r['owner']=='.text.tsl9_adc_call_site' and r['offset']==0 and r['type']==17 and r['addend']==0 and r['symbol']['name']==ENTRY and r['symbol']['index']==0,'Real R_RISCV_JAL to actual undefined C symbol')
    need(jal(obj.data(obj.byname[r['owner']]),0)['rd']==1,'Assembler emitted true linked JAL register')
    e,loads=linked_gate((folder/'linked.elf').read_bytes(),code);patch=e.data(e.byname['.caller']);row=caller_gate(patch);old,src=a.contexts(root);raw_reader,(_,fields,llvm,ctx)=old.context(root);typed=src.context(root)[3](patch,SITE);need((typed['op'],typed['rd'],typed['target'])==('jal',row['rd'],row['target']),'Manual JAL fields agree with old independent typed decoder')
    rows=fields['rows'](code,0,ctx);a.kernel(rows);need(len(rows)==42,'All linked C raw operands match sealed genuine source profile')
    parsed=raw_reader.parse_sections((folder/'complete-static-disassembly.log').read_text(),llvm)
    for name,section in(('.caller',e.byname['.caller']),('.adc',e.byname['.adc'])):
        decoded=fields['rows'](e.data(section),section['address'],ctx);need([{k:v for k,v in x.items() if k!='offset'} for x in decoded]==parsed[name],'Every linked raw operand independently matches actual LLVM '+name)
    image=(folder/'NOT-FLASH-VALIDATED-adc-caller-bank.bin').read_bytes();image_gate(image,baseline,patch,code)
    removed=sorted({x['name'] for x in funcs}-{x['name'] for x in e.symbols if x['info']&15==2 and x['size']});need(len(removed)==4,'Four genuine unused functions actually removed after GC')
    return dict(passed=True,mode=record['mode'],actual_artifacts_read=True,actual_linked_ELF_read=True,candidate_BIN_read=True,integration_sources=sources,integration_receipt_sha256=sha(receipt),native_ABI_receipt_sha256=sha(record['abi_receipt']),candidate_bytes=len(image),candidate_sha256=digest(image),selected_function_bytes=110,selected_code_sha256=digest(code),caller_target=row['target'],caller_RA=row['link_value'],caller_patch_hex=patch.hex(),baseline_sha256=BASE_SHA,baseline_preserved_except_caller=True,changed_preimage_offsets=[i for i,(x,y) in enumerate(zip(baseline,image)) if x!=y],LOADs=loads,RELA=0,unused_globals_GCed=removed,noncode_FF_tail_bytes=914,raw_BIN_has_no_execute_permission_metadata=True,controls=controls(e,patch,image,baseline,code),normal_caller_projection=proof['normal_caller_projection'],inherited_OTA568_and_ROM_witness_limitations=True,inherited_physical_gates_false=True,full_image_provenance_proved=False,full_original_callee_ABI_proved=False,fault_async_IRQ_equivalence=False,Flash_NV_ownership_proved=False,installed_ROM_proved=False,hardware_OTA_proved=False,target_execution=False,ISA_emulation=False,linked=False,BIN_generated=False)
def replay(root,p):
    r=read(p);need(r['checker_sha256']==sha(HERE/'check.py'),'Exact independent checker source');result=inspect(root,Path(r['integration_receipt']));need(result==r['result'],'Actual independent readback equals review receipt');return result
def metadata(root):
    seal=read(HERE/'seal.json')
    for n,pin in seal['members'].items():need(sha(HERE/n)==pin,'Sealed integration-review member '+n)
    stable(root);data=read(HERE/'selected.json');need(set(data)=={'c','cpp'},'Two retained language results')
    for mode,r in data.items():need(r['mode']==mode and r['candidate_bytes']==78848 and r['selected_function_bytes']==110 and r['caller_target']==CODE and r['caller_RA']==SITE+4 and len(r['controls'])==7 and all(x['rejected'] for x in r['controls']) and not r['full_image_provenance_proved'] and not r['hardware_OTA_proved'],'Retained bounded actual candidate review')
    need(data['c']['candidate_sha256']==data['cpp']['candidate_sha256'],'Actual complete C/C++ candidate identity');need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Default Traditional Chinese README')
    return dict(passed=True,seal_sha256=sha(HERE/'seal.json'),sealed_members=len(seal['members']),metadata_only=True,actual_artifacts_read=False,retained_candidates=2,full_image_provenance_proved=False,inherited_physical_gates_false=True,target_execution=False,linked=False,BIN_generated=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--integration-receipt',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.integration_receipt is None and a.receipt is None,'Read-only replay');result=replay(root,a.replay)
    elif a.integration_receipt:
        need(a.receipt is not None and not a.receipt.exists(),'Create-only independent actual review');result=inspect(root,a.integration_receipt);write(a.receipt,dict(schema='TSL9-ADC-independent-integration-review-v1',checker_sha256=sha(HERE/'check.py'),integration_receipt=str(a.integration_receipt.resolve()),result=result))
    else:need(a.receipt is None,'Metadata only');result=metadata(root)
    print(json.dumps(result))
