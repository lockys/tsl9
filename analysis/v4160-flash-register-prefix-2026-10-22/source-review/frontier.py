#!/usr/bin/env python3
"""Compare encoded instruction frontiers as data; no CPU state or ISA interpreter."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

SOURCE_SEAL='67f43fd3bf0f8e94d316952ab931109e5069f06c6078152bf3c6995dad9b423d'
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PARSER_SHA='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
RANGES=[(0x9c0a,64),(0x18e90,8),(0x18e98,30),(0x18eb6,14),(0x18ec4,46),(0x18ef2,100)]
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def case(root,name):
    for p in (root/'apk-analysis'/('tsl9-'+name),root/'analysis'/name):
        if p.is_dir():return p
    raise ValueError('Missing source review '+name)
def source(root,firmware):
    source=case(root,'v4160-flash-native-2026-10-22')/'source';need(sha(source/'seal.json')==SOURCE_SEAL,'Original sealed Flash proof')
    for row in read(source/'seal.json')['members']:
        p=source/row['path'];need(sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],'Original proof member '+row['path'])
    raw=firmware.read_bytes();need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==FW_SHA,'Original raw ID2966 image')
    # Only immutable function definitions are admitted, not the old command-line,
    # module imports, disassembler subprocess or archive-writing paths.
    tree=ast.parse((source/'inspect.py').read_text(encoding='utf-8'));names={'sx','decode','instructions','facts'};defs=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name in names]
    need(len(defs)==4,'Exact four data-only decoder/shape-check definitions');space={'RANGES':RANGES,'require':need}
    exec(compile(ast.Module(body=defs,type_ignores=[]),str(source/'inspect.py'),'exec'),space)
    old=read(source/'source-proof.json');need(space['facts'](raw)==old['ledger'],'Fresh raw decode agrees with all99 sealed original rows')
    negatives=[]
    for row in old['raw_negatives']:
        mutant=bytearray(raw);pc=row['PC'];new=bytes.fromhex(row['after']);need(mutant[pc-0x8000:pc-0x8000+len(new)].hex()==row['before'],'Original raw negative before bytes');mutant[pc-0x8000:pc-0x8000+len(new)]=new
        try:space['facts'](mutant)
        except ValueError:negatives.append(row['name'])
        else:raise ValueError('Accepted old raw source control '+row['name'])
    need(len(negatives)==20,'All20 original raw shape controls rechecked')
    return space['decode'],old,raw,negatives
def rows(body,entry,decode):
    # The source decoder expects a base8000 carrier. This is a byte container,
    # not register state; no instruction is evaluated.
    raw=bytes(entry-0x8000)+body;pc=entry;result=[]
    while pc<entry+len(body):
        r=decode(raw,pc);need(pc+r['bytes']<=entry+len(body),'Exact last instruction extent');result.append(r);pc+=r['bytes']
    need(pc==entry+len(body),'Exact static instruction coverage');return result
def canonical(row):
    r={k:v for k,v in row.items() if k!='raw_hex'}
    # Deliberately narrow mathematical commutation: same destination, width,
    # opcode and unordered pair of sources. No constant/state evaluation.
    if r['op'] in ('add','and','or') and r['rs1'] is not None and r['rs2'] is not None:
        r['rs1'],r['rs2']=sorted((r['rs1'],r['rs2']))
    return r
def compare(original,body,entry,decode):
    a=rows(original,entry,decode);b=rows(body,entry,decode);aa={r['PC']:r for r in a};bb={r['PC']:r for r in b};difference=[]
    for pc in sorted(set(aa)|set(bb)):
        x=aa.get(pc);y=bb.get(pc)
        if x is None or y is None or canonical(x)!=canonical(y):difference.append({'PC':pc,'offset':pc-entry,'original':x,'candidate':y})
    return {'entry':entry,'bytes':len(body),'instruction_count':len(b),'original_instruction_count':len(a),'same_boundaries':set(aa)==set(bb),'exact_original_bytes':body==original,'same_decoded_instruction_frontiers_modulo_commutative_sources':not difference,'frontier_difference_count':len(difference),'frontier_differences':difference,'original_boundaries':[r['PC'] for r in a],'candidate_boundaries':[r['PC'] for r in b],'candidate_rows':b}
def parser(root):
    path=case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py';need(sha(path)==PARSER_SHA,'Immutable bounded ELF parser');spec=importlib.util.spec_from_file_location('prefix_ELF_data',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module.ELF
def elf(root,path):
    e=parser(root)(path);need(e.kind==2 and e.flags==1 and not e.relocations,'Linked RV32IMAC component with no unresolved relocations');return e
def component_bodies(root,path):
    e=elf(root,path);found={}
    for entry,size in RANGES:
        ss=[s for s in e.sections if s['flags']&2 and s['address']==entry and s['size']==size and s['flags']==6 and s['type']==1];need(len(ss)==1,'Unique exact executable original allocation '+hex(entry));s=ss[0]
        aliases=[x for x in e.symbols if x['index']==s['index'] and x['value']==entry and x['size']==size and x['info']==18 and x['other']==0];need(aliases,'Real section-owned original-size native function '+hex(entry));found[entry]=e.data(s)
    return found
def partial_objects(root,folder,bodies,decode,original_ledger):
    E=parser(root);names=['quarter','status','unlock','lock','erase','program'];results=[]
    for (entry,size),name,old in zip(RANGES,names,original_ledger):
        p=folder/(name+'.o');e=E(p);need(e.kind==1 and e.flags==1,'Actual integer RV32 partial object '+name)
        alloc=[s for s in e.sections if s['flags']&2 and s['size']];need(len(alloc)==1 and alloc[0]['size']==size and alloc[0]['flags']==6 and alloc[0]['type']==1,'One complete original-size function allocation '+name)
        s=alloc[0];public='tsl9_flash_'+name+'_'+format(entry,'x');functions=[x for x in e.symbols if x['info']&15==2 and x['size']]
        need(len(functions)==1 and functions[0]['name']==public and functions[0]['index']==s['index'] and functions[0]['value']==0 and functions[0]['size']==size and functions[0]['info']==18,'Actual readable C section-owned public provider '+name)
        raw=bytearray(e.data(s));linked=bytearray(bodies[entry]);expected={0x14:'unlock_18e98',0x1c:'status_18e90',0x22:'erase_18ec4',0x2a:'program_18ef2',0x2e:'lock_18eb6'} if name=='quarter' else {}
        need(len(e.relocations)==len(expected),'Only original five wrapper JAL relocations')
        for r in e.relocations:
            need(r['owner']==s['name'] and r['type']==17 and r['addend']==0 and r['offset'] in expected and r['symbol']['name']=='tsl9_flash_'+expected[r['offset']] and r['symbol']['index']==0,'Exact original wrapper direct-call role')
            for value in (raw,linked):
                at=r['offset'];w=int.from_bytes(value[at:at+4],'little');need(w&127==0x6f,'Actual JAL immediate normalization only');value[at:at+4]=(w&0xfff).to_bytes(4,'little')
        need(raw==linked,'Partial object bytes equal actual component bytes modulo exact JAL fields')
        und={x['name'] for x in e.symbols if not x['index'] and x['name']};need(und=={'tsl9_flash_'+x for x in expected.values()},'No hidden leaf/outliner dependencies')
        observed=sorted({r['rd'] for r in rows(bytes(raw),entry,decode) if r['rd'] not in (None,0)});need(observed==old['written_GPRs'],'Actual complete function GPR destination set matches source')
        results.append({'function':name,'object_sha256':sha(p),'bytes':size,'written_GPRs':observed,'JAL_relocations':len(e.relocations)})
    return results
