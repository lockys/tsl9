"""Independent static ELF component review; no link, code execution or BIN output."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
READER='b89e4ed72983183fc1606c13aa0be918fd84ac4a18cf90befaf2059cc0942fbd'
SOURCE='c29430e22451a71a2acbcf0afea199f4b6053d09309597eb4082a52fbafa677a'
NATIVE='b30c679bd1e15a7a59be59b4ed723a6f98f78cc022e93e314e4c59f85c7aa09f'
NATIVE_RECEIPTS={'c':'58df66d33aa1a9b2d34736a2a1727c66778aa5f1170d977e2bdceb3bbbcbd944','cpp':'6169f4213e1cdc2f4fff1eea1ab47c51735c0a551afc52b3fe7ab0edda1c2486'}
TOOLS={'ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f','llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
SIZES={'tsl9_flash_status_18e90':8,'tsl9_flash_unlock_18e98':30,'tsl9_flash_lock_18eb6':14,'tsl9_flash_erase_18ec4':46,'tsl9_flash_program_18ef2':100,'tsl9_flash_quarter_9c0a':64,'tsl9_delay_19764':60,'tsl9_nv_write_callback_197be':72}
RELOCS=[('tsl9_flash_quarter_9c0a',20,17,'tsl9_flash_unlock_18e98'),('tsl9_flash_quarter_9c0a',28,17,'tsl9_flash_status_18e90'),('tsl9_flash_quarter_9c0a',34,17,'tsl9_flash_erase_18ec4'),('tsl9_flash_quarter_9c0a',42,17,'tsl9_flash_program_18ef2'),('tsl9_flash_quarter_9c0a',46,17,'tsl9_flash_lock_18eb6'),('tsl9_nv_write_callback_197be',12,19,'tsl9_flash_unlock_18e98'),('tsl9_nv_write_callback_197be',22,19,'tsl9_flash_erase_18ec4'),('tsl9_nv_write_callback_197be',34,19,'tsl9_flash_program_18ef2'),('tsl9_nv_write_callback_197be',42,19,'tsl9_flash_lock_18eb6'),('tsl9_nv_write_callback_197be',52,19,'tsl9_delay_19764')]

def need(v,m):
    if not v:raise ValueError(m)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())

def locate(root,rel):
    p=root/rel
    if p.is_file():return p
    if rel.startswith('apk-analysis/tsl9-'):
        name,tail=rel[len('apk-analysis/tsl9-'):].split('/',1);return case(root,name)/tail
    return p

def stable(root):
    p=case(root,'v4160-adc-caller-2026-10-22')/'integration-review/check.py'
    need(sha(p)==READER,'Pinned separate generic ELF reader')
    source=case(root,'v4160-nv-write-2026-10-22')/'source-review'
    need(sha(source/'seal.json')==SOURCE,'Frozen original source proof')
    for n,h in read(source/'seal.json')['members'].items():need(sha(source/n)==h,'Original proof member '+n)
    if (HERE/'reference-pins.json').exists():
        for rel,pin in read(HERE/'reference-pins.json')['sources'].items():need(sha(locate(root,rel))==pin,'Frozen genuine component source '+rel)
    return runpy.run_path(str(p))['ELF']

def functions(e):
    fs=[x for x in e.symbols if x['info']&15==2 and x['size']]
    need(len(fs)==8 and {x['name']:x['size'] for x in fs}==SIZES,'All eight genuine complete functions')
    need(all(x['info']==18 and x['other']==0 and 0<x['index']<len(e.sections) for x in fs),'Real global FUNC section providers')
    return {x['name']:x for x in fs}

def ABS_metadata(x):
    return x['index']==0xfff1 and (x['info']&15==4 or (x['info']==0 and x['value']==x['size']==0 and re.fullmatch(r'\$d\.\d+',x['name']) is not None))

def widths(raw):
    out=[];at=0
    while at<len(raw):
        need(at+2<=len(raw),'Whole instruction halfword');w=int.from_bytes(raw[at:at+2],'little');n=4 if w&3==3 else 2
        need(n==2 or w&31!=31,'No long instruction format');need(at+n<=len(raw),'Whole source instruction extent')
        out.append(dict(offset=at,bytes=n,raw_hex=raw[at:at+n].hex()));at+=n
    return out

def signed(v,bits):return v-(1<<bits) if v&(1<<(bits-1)) else v

def jal(raw,pc):
    need(len(raw)==4,'Four-byte JAL');w=int.from_bytes(raw,'little');need(w&127==0x6f and (w>>7)&31==1,'Actual JAL with rd RA')
    imm=((w>>31)&1)<<20|((w>>21)&1023)<<1|((w>>20)&1)<<11|((w>>12)&255)<<12
    return (pc+signed(imm,21))&0xffffffff

def callpair(raw,pc):
    need(len(raw)==8,'Eight-byte CALL_PLT pair');a,b=struct.unpack('<II',raw)
    need(a&0xfff==0x97 and b&0xfffff==0x80e7,'Actual AUIPC RA + JALR RA,RA pair')
    return ((pc+signed(a&0xfffff000,32)+signed(b>>20,12))&0xffffffff)&0xfffffffe

def object_gate(raw,ELF):
    e=ELF(raw);need(e.kind==1 and e.flags==1,'Actual input RV32/RVC ET_REL');fs=functions(e)
    need(not any(x['name'] and x['index']==0 for x in e.symbols),'Input has no named UND')
    need(not any(x['name'] and x['index']==0xfff1 and not ABS_metadata(x) for x in e.symbols),'Input has no ABS provider; local FILE/mapping metadata exempt')
    actual=[]
    for r in e.relocations:
        owner=next((n for n,f in fs.items() if e.sections[f['index']]['name']==r['owner']),None)
        need(owner is not None and r['addend']==0 and r['symbol']['name'] in fs and r['symbol']['index']==fs[r['symbol']['name']]['index'],'Real internal relocation provider')
        actual.append((owner,r['offset']-fs[owner]['value'],r['type'],r['symbol']['name']))
    need(sorted(actual)==sorted(RELOCS),'Five actual JAL and five actual CALL_PLT relocations')
    need(sum(len(widths(e.function(f))) for f in fs.values())==148,'All 148 input instructions')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len(alloc)==8 and all(s['type']==1 and s['flags']==6 for s in alloc),'Only eight complete input executable allocations')
    need(all(f['value']==0 and e.sections[f['index']]['size']==f['size'] for f in fs.values()),'Every original executable section exactly one complete function')
    return e,fs

def linked_gate(raw,obj,fs,ELF):
    e=ELF(raw);need(e.kind==2 and e.flags==1 and not e.relocations,'Fully linked RV32/RVC ET_EXEC without remaining RELA')
    need(not any(x['type'] in (4,9) for x in e.sections),'No remaining relocation section')
    out=functions(e);need(not any(x['name'] and x['index']==0 for x in e.symbols),'No named UND')
    need(not any(x['name'] and x['index']==0xfff1 and not ABS_metadata(x) for x in e.symbols),'No ABS provider; local FILE/mapping metadata exempt')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len(alloc)==1,'Exactly one component allocation');s=alloc[0]
    need((s['name'],s['type'],s['flags'],s['address'],s['size'])==('.text',1,6,0,394),'Nonphysical .text VMA zero and exact394-byte extent')
    need(not any(s['type']==8 and s['flags']&2 for s in e.sections),'No allocated NOBITS')
    need(e.entry==out['tsl9_nv_write_callback_197be']['value'],'Real selected function entry, not fabricated address')
    ordered=sorted(out.values(),key=lambda f:f['value']);cursor=0
    for f in ordered:
        need(f['index']==s['index'] and f['value']==cursor,'All function bytes contiguous with no gaps/overlap');cursor+=f['size']
    need(cursor==394,'All eight functions retained without GC')
    loads=[p for p in e.programs if p['type']==1];need(len(loads)==1,'One exact RX LOAD');p=loads[0]
    need(p['vaddr']==p['paddr']==0 and p['offset']==s['offset'] and p['filesz']==p['memsz']==394 and p['flags']==5,'RX LOAD contains exactly component bytes, no headers/holes')
    need(p['align']>0 and p['align']&(p['align']-1)==0 and p['offset']%p['align']==0,'LOAD alignment congruence')
    attrs=e.byname['.riscv.attributes'];other=[q for q in e.programs if q['type']!=1]
    need(len(e.programs)==2 and len(other)==1 and attrs['flags']==0 and attrs['type']==0x70000003,'Only nonallocated RISC-V attributes metadata beyond RX LOAD')
    q=other[0]
    need(q['type']==0x70000003 and q['offset']==attrs['offset'] and q['filesz']==q['memsz']==attrs['size']==64 and q['vaddr']==q['paddr']==0 and q['flags']==4 and q['align']==1,'Exact read-only attribute metadata header; no hidden loadable extent')
    allowed={n:bytearray(f['size']) for n,f in fs.items()};calls=[]
    for owner,off,kind,target in RELOCS:
        old=obj.function(fs[owner]);new=e.function(out[owner]);pc=out[owner]['value']+off;dest=out[target]['value'];n=4 if kind==17 else 8
        need(off+n<=len(old),'Whole original call relocation')
        if kind==17:
            need(jal(old[off:off+4],off)==off,'Original JAL placeholder immediate zero');observed=jal(new[off:off+4],pc);masks=[0xfffff000]
        else:
            need(callpair(old[off:off+8],off)==off,'Original CALL_PLT placeholder immediate zero');observed=callpair(new[off:off+8],pc);masks=[0xfffff000,0xfff00000]
        need(observed==dest,'Actual relocated call resolves to genuine provider '+target)
        for i,mask in enumerate(masks):allowed[owner][off+4*i:off+4*i+4]=mask.to_bytes(4,'little')
        calls.append(dict(owner=owner,offset=off,PC=pc,type=kind,bytes=n,target_symbol=target,target=dest,linked_raw_hex=new[off:off+n].hex()))
    preservation=[]
    for n,f in fs.items():
        a=obj.function(f);b=e.function(out[n]);need(len(a)==len(b),'Unchanged complete function size')
        need(all(((x^y)&(~m&255))==0 for x,y,m in zip(a,b,allowed[n])),'All bytes outside actual relocation immediate fields unchanged: '+n)
        preservation.append(dict(name=n,bytes=len(a),instructions=len(widths(a)),input_sha256=digest(a),linked_sha256=digest(b),changed_byte_offsets=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y],editable_immediate_bits=sum(m.bit_count() for m in allowed[n])))
    need(sum(len(widths(e.function(f))) for f in out.values())==148,'All148 linked instruction widths retained')
    reachable={'tsl9_nv_write_callback_197be'}
    while True:
        expanded=reachable|{target for owner,off,kind,target in RELOCS if owner in reachable}
        if expanded==reachable:break
        reachable=expanded
    return e,dict(functions=8,function_bytes=394,instructions=148,UND=0,RELA=0,ABS_providers=0,local_FILE_ABS_metadata=sum(x['index']==0xfff1 and x['info']&15==4 for x in e.symbols),local_mapping_ABS_metadata=sum(x['index']==0xfff1 and x['info']==0 and ABS_metadata(x) for x in e.symbols),calls=calls,preservation=preservation,LOADs=loads,attribute_metadata_header=q,retained_unused_functions=sorted(set(SIZES)-reachable),no_GC=True,no_relaxation=True,immediate_editable_bits=260)

def llvm_rows(text):
    rows={};name=None
    for line in text.splitlines():
        head=re.match(r'^\s*[0-9a-fA-F]+ <([^>+]+)>:$',line)
        if head:name=head.group(1);rows[name]=[];continue
        m=re.match(r'^\s*([0-9a-fA-F]+):\s+((?:[0-9a-fA-F]{2}\s+){2,4})\s*\S',line)
        if m and name in SIZES:rows[name].append(dict(PC=int(m.group(1),16),raw_hex=''.join(m.group(2).split())))
    return rows

def controls(raw,obj,fs,ELF):
    e=ELF(raw);f=functions(e);sec=e.sections[f['tsl9_nv_write_callback_197be']['index']];base=sec['offset']
    variants=[]
    # Change only a real linked CALL_PLT immediate bit, not a copied mock record.
    b=bytearray(raw);b[base+f['tsl9_nv_write_callback_197be']['value']+12+7]^=1;variants.append(('wrong_real_call_target',b))
    b=bytearray(raw);struct.pack_into('<I',b,sec['header_offset']+20,396);variants.append(('wrong_section_size',b))
    load=next(p for p in e.programs if p['type']==1)
    b=bytearray(raw);struct.pack_into('<I',b,load['header_offset']+20,396);variants.append(('hidden_LOAD_memory_hole',b))
    b=bytearray(raw);struct.pack_into('<I',b,load['header_offset']+24,7);variants.append(('writable_LOAD',b))
    # Find actual symbol row using its string index and definition, then alter it.
    symtab=next(s for s in e.sections if s['type']==2);target=f['tsl9_flash_unlock_18e98'];at=None
    for q in range(symtab['offset'],symtab['offset']+symtab['size'],16):
        if struct.unpack_from('<IIIBBH',raw,q)[1:]==(target['value'],target['size'],target['info'],target['other'],target['index']):at=q;break
    need(at is not None,'Actual provider symbol row')
    b=bytearray(raw);struct.pack_into('<H',b,at+14,0xfff1);variants.append(('fake_ABS_provider',b))
    b=bytearray(raw);struct.pack_into('<I',b,at+8,target['size']+2);variants.append(('wrong_function_size',b))
    b=bytearray(raw);status=f['tsl9_flash_status_18e90'];b[base+status['value']]^=0x80;variants.append(('unused_function_byte_changed',b))
    out=[]
    for name,b in variants:
        try:linked_gate(bytes(b),obj,fs,ELF)
        except ValueError as error:out.append(dict(case=name,rejected=True,mutated_sha256=digest(b),reason=str(error)));continue
        raise ValueError('Accepted malformed real ELF control '+name)
    return out

def inspect(root,receipt):
    root=Path(root).resolve(strict=True);receipt=Path(receipt).resolve(strict=True);folder=receipt.parent
    ELF=stable(root);record=read(receipt);mode=record['mode'];need(mode in NATIVE_RECEIPTS,'Retained language mode')
    native=Path(record['native_folder']);need(sha(native/'native.o')==NATIVE,'Exact frozen genuine C/C++ object bytes')
    original_record=read(native/'verification.json')
    need(original_record['schema']=='TSL9-real-NV-write-timer-C-v1' and original_record['mode']==mode,'Actual native source receipt language/schema')
    need(original_record['artifacts']=={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in native.iterdir() if p.is_file() and p.name!='verification.json'},'Actual native complete archive identities')
    for path,pin in original_record['source_pins'].items():need(sha(path)==pin,'Native recorded source/tool identity '+str(Path(path).name))
    for x in original_record['commands']:need(x['exit']==0 and sha(native/x['log'])==x['log_sha256'],'Native successful source build logs')
    need(record['schema']=='TSL9-offline-NV-write-component-v1','Explicit component receipt schema')
    inventory={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.iterdir() if p.is_file() and p!=receipt}
    need(record['artifacts']==inventory and set(inventory)=={'actual-component-link.log','complete-static-disassembly.log','linked.elf'},'Complete code-only component inventory; no BIN')
    for path,pin in record['source_pins'].items():need(sha(path)==pin,'Actual recorded source/tool identity '+str(Path(path).name))
    need(set(record['tools'])==set(TOOLS),'Only actual linker/static-disassembler tools')
    for name,pin in TOOLS.items():need(sha(record['tools'][name])==pin,'Pinned actual LLVM tool '+name)
    component=case(root,'v4160-nv-write-2026-10-22')/'component';script=component/'component.ld'
    need(script.read_text().replace('\r\n','\n')=='OUTPUT_ARCH(riscv)\nENTRY(tsl9_nv_write_callback_197be)\nPHDRS { code PT_LOAD FLAGS(5); }\nSECTIONS {\n  .text 0 : { *(.text.*) } :code\n  /DISCARD/ : { *(.comment) }\n}\n','Exact nonphysical code-only linker script without providers/GC')
    expected=[('actual-component-link',[record['tools']['ld.lld'],'--no-relax','-T',script,native/'native.o','-o',folder/'linked.elf']),('complete-static-disassembly',[record['tools']['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'linked.elf'])]
    need([(x['label'],x['argv']) for x in record['commands']]==[(label,[str(v) for v in argv]) for label,argv in expected],'Independent exact actual link/no-relax/no-GC recipe')
    for x in record['commands']:need(x['exit']==0 and sha(folder/x['log'])==x['log_sha256'],'Successful actual link/disassembly log identity')
    obj,fs=object_gate((native/'native.o').read_bytes(),ELF);linked,facts=linked_gate((folder/'linked.elf').read_bytes(),obj,fs,ELF)
    original_log=llvm_rows((native/'complete-static-disassembly.log').read_text())
    linked_log=llvm_rows((folder/'complete-static-disassembly.log').read_text())
    need(set(original_log)==set(linked_log)==set(SIZES),'Both static logs cover exactly eight complete functions')
    for name,f in fs.items():
        need(original_log[name]==[dict(PC=x['offset'],raw_hex=x['raw_hex']) for x in widths(obj.function(f))],'Every original instruction agrees with actual LLVM raw log '+name)
        g=functions(linked)[name]
        need(linked_log[name]==[dict(PC=g['value']+x['offset'],raw_hex=x['raw_hex']) for x in widths(linked.function(g))],'Every linked instruction agrees with actual LLVM raw log '+name)
    negatives=controls(linked.raw,obj,fs,ELF)
    return dict(schema='TSL9-independent-NV-component-static-v1',passed=True,metadata_only=False,actual_artifacts_read=True,
      mode=mode,component_receipt_sha256=sha(receipt),native_receipt_sha256=sha(native/'verification.json'),input_object_sha256=NATIVE,
      functions=8,function_bytes=394,instructions=148,UND=0,RELA=0,ABS_providers=0,input_JAL=5,input_CALL_PLT=5,
      linked_ELF_sha256=sha(folder/'linked.elf'),text_sha256=digest(linked.data(linked.byname['.text'])),
      actual_input_and_linked_function_bytes_read=788,actual_input_and_linked_instruction_rows=296,
      facts=facts,controls=negatives,producer_verdict_used=False,all_unused_real_functions_retained=True,
      component_VMA_is_physical=False,full_original_ABI_proved=False,normal_caller_replacement_proved=False,
      fault_async_IRQ_equivalence=False,installed_ROM_proved=False,hardware=False,hardware_OTA_proved=False,
      target_execution=False,ISA_emulation=False,linked_by_checker=False,BIN_generated=False,rebuilt_flashable_BIN=False)

def metadata(root):
    stable(root)
    if (HERE/'seal.json').exists():
        for n,h in read(HERE/'seal.json')['members'].items():need(sha(HERE/n)==h,'Sealed component-review member '+n)
    selected=read(HERE/'selected.json');need(set(selected)=={'c','cpp'},'Two sealed language reviews')
    for mode,r in selected.items():
        need(r['mode']==mode and r['passed'] and r['facts']['functions']==8 and r['facts']['function_bytes']==394 and r['facts']['instructions']==148 and len(r['facts']['calls'])==10 and len(r['controls'])==7 and all(x['rejected'] for x in r['controls']),'Bounded retained actual review counters')
        need(r['facts']['UND']==r['facts']['RELA']==r['facts']['ABS_providers']==0 and not r['full_original_ABI_proved'] and not r['hardware'],'Preserved provider and physical limits')
    need(selected['c']['text_sha256']==selected['cpp']['text_sha256'],'Retained actual C/C++ code equality')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Default Traditional Chinese parity')
    return dict(passed=True,metadata_only=True,actual_artifacts_read=False,retained_modes=2,functions=8,function_bytes=394,instructions=148,retained_text_sha256=selected['c']['text_sha256'],UND=0,RELA=0,ABS_providers=0,full_original_ABI_proved=False,hardware=False,target_execution=False,BIN_generated=False)

def replay(root,receipt):
    r=read(receipt);need(r['checker_sha256']==sha(HERE/'check.py'),'Exact independent review checker')
    result=inspect(root,Path(r['component_receipt']));need(result==r['result'],'Read-only independent actual ELF replay');return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--component-receipt',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.component_receipt is None and a.receipt is None,'Read-only replay');result=replay(root,a.replay)
    elif a.component_receipt:
        need(a.receipt is not None and not a.receipt.exists(),'Create-only review receipt');result=inspect(root,a.component_receipt);write(a.receipt,dict(schema='TSL9-independent-NV-component-review-v1',checker_sha256=sha(HERE/'check.py'),component_receipt=str(a.component_receipt.resolve()),result=result))
    else:need(a.receipt is None,'Metadata mode');result=metadata(root)
    print(json.dumps(result))
