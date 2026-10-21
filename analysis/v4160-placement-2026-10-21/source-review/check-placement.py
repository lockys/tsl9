#!/usr/bin/env python3
"""Static source ownership/reference inventory. Never builds or executes firmware."""
import argparse
import collections
import hashlib
import importlib.util
import json
import re
from pathlib import Path

IMAGE = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
OBJECT = '646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97'
WITNESS = '66fbf4cf1d9731f5fcd4f71c66ec1c67fc4fd2487f710125ed6488cbde2e8420'
PARSER = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
LAYOUT = '651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b'
RANGES = [('reset_memory',0x186ba,0x186f8),('query',0x18834,0x188e2),
          ('fields',0x1973c,0x19764),('irq_init',0x9a42,0x9ad2),
          ('rcc_19124',0x19124,0x19142),('rcc_19142',0x19142,0x19160),
          ('rcc_19160',0x19160,0x1917e),('rcc_1917e',0x1917e,0x1919c)]

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def need(value,message):
    if not value:
        raise ValueError(message)

def validate_reference(actual,reference):
    need(actual==reference,'Bound full reference inventory unchanged')

def sx(x,bits):
    return x-(1<<bits) if x&(1<<(bits-1)) else x

def region(address):
    return next((name for name,start,end in RANGES if start<=address<end),None)

def direct(raw,pc):
    """Raw direct control targets only, not general execution semantics."""
    x=int.from_bytes(raw,'little')
    if len(raw)==4:
        if x&127==0x6f:
            imm=((x>>31)&1)*0x100000+((x>>21)&1023)*2+((x>>20)&1)*2048+((x>>12)&255)*4096
            return 'jal',(pc+sx(imm,21))&0xffffffff,(x>>7)&31
        if x&127==0x63 and (x>>12)&7 in (0,1,4,5,6,7):
            imm=((x>>31)&1)*4096+((x>>7)&1)*2048+((x>>25)&63)*32+((x>>8)&15)*2
            return 'branch',(pc+sx(imm,13))&0xffffffff,None
    elif len(raw)==2 and x&3==1:
        f=x>>13
        if f in (1,5):
            imm=((x>>12)&1)*2048+((x>>11)&1)*16+((x>>9)&3)*256+((x>>8)&1)*1024+((x>>7)&1)*64+((x>>6)&1)*128+((x>>3)&7)*2+((x>>2)&1)*32
            return 'c.jal' if f==1 else 'c.j',(pc+sx(imm,12))&0xffffffff,1 if f==1 else 0
        if f in (6,7):
            imm=((x>>12)&1)*256+((x>>10)&3)*8+((x>>5)&3)*64+((x>>3)&3)*2+((x>>2)&1)*32
            return 'c.branch',(pc+sx(imm,9))&0xffffffff,None
    return None

def analyze(firmware,object_path,witness_path,parser_path,layout_path=None):
    data=firmware.read_bytes()
    need(len(data)==76800 and sha(data)==IMAGE,'Exact ID2966 original image')
    need(sha(object_path.read_bytes())==OBJECT,'Exact 691-allocation/8280-RELA carrier')
    need(sha(witness_path.read_bytes())==WITNESS,'Exact source-layout numeric witness')
    need(sha(parser_path.read_bytes())==PARSER,'Reviewed read-only ELF parser')
    spec=importlib.util.spec_from_file_location('placement_elf',parser_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    obj=module.ELF(object_path);witness=module.ELF(witness_path)
    layout_path=layout_path or witness_path.parent.parent/'original-image-layout.ld'
    need(sha(layout_path.read_bytes())==LAYOUT,'Exact full 691-binding layout script')
    text=layout_path.read_text(encoding='utf-8')
    bindings=dict((n,int(v,16)) for n,v in re.findall(r'^\s*(\S+)\s+(0x[0-9a-f]+)(?:\s+\(NOLOAD\))?\s*:',text,re.M))
    sizes=dict((n,int(v)) for n,v in re.findall(r'ASSERT\(SIZEOF\(([^)]+)\)==(\d+)',text))
    allocations=sorted((s for s in witness.sections if s['flags']&2 and s['size']),key=lambda s:s['address'])
    need(len(allocations)==691 and len(obj.relocations)==8280,'Carrier allocation/RELA counts')
    need(len(bindings)==len(sizes)==691,'Full section address and SIZEOF bindings')
    need(all(bindings.get(s['name'])==s['address'] and sizes.get(s['name'])==s['size'] for s in allocations),'Every actual section matches full layout binding')
    cursor=0x8000
    for sec in allocations:
        if sec['type']==8:
            need(sec['name']=='.bss.tsl9v4160.ram' and sec['address']==0x20004000 and sec['size']==35160,'Known non-image RAM NOBITS owner')
            continue
        need(sec['address']==cursor,'Exact nonoverlapping section-backed image ownership')
        need(witness.data(sec)==data[cursor-0x8000:cursor-0x8000+sec['size']],'Witness section equals original bytes')
        need(sec['name'] in obj.byname and obj.byname[sec['name']]['size']==sec['size'],'Object/witness section identity')
        cursor+=sec['size']
    need(cursor==0x1ac00,'Complete original image coverage')
    def symbol_address(symbol):
        index=symbol['index']
        if index==0 and symbol['name']=='' and symbol['value']==0:return 0
        if index==0xfff1:return symbol['value']
        if 0<index<len(obj.sections):
            owner=obj.sections[index]['name']
            if owner in witness.byname:return witness.byname[owner]['address']+symbol['value']
        return None
    def source_address(owner,offset):
        return witness.byname[owner]['address']+offset if owner in witness.byname else None
    refs=[];unresolved=[]
    for rel in obj.relocations:
        address=symbol_address(rel['symbol'])
        if address is None:
            unresolved.append({'owner':rel['owner'],'offset':rel['offset'],'type':rel['type'],'symbol':rel['symbol']['name'],'addend':rel['addend']})
            continue
        target=(address+rel['addend'])&0xffffffff
        selected=region(target)
        if selected:
            category=('direct_control' if rel['type'] in (16,17,44,45) else
                      'pc_relative_low_anchor_not_runtime_entry' if rel['type'] in (24,25) else
                      'address_formation' if rel['type'] in (23,26) else
                      'absolute_32_word' if rel['type']==1 else 'arithmetic_expression_term')
            site=source_address(rel['owner'],rel['offset'])
            refs.append({'region':selected,'source':site,'source_owner':rel['owner'],'source_offset':rel['offset'],
                         'target':target,'type':rel['type'],'category':category,'symbol':rel['symbol']['name'],
                         'symbol_value':rel['symbol']['value'],'addend':rel['addend'],
                         'source_inside_same_selected_region':region(site)==selected if site is not None else False})
    definitions=[]
    for symbol in obj.symbols:
        address=symbol_address(symbol)
        if address is not None and region(address) and symbol['name']:
            definitions.append({'region':region(address),'address':address,'name':symbol['name'],'size':symbol['size'],'type':symbol['info']&15})
    decoded=[];indirect=[];instruction_total=0;outgoing=[];address_pairs=[]
    for sec in allocations:
        if not sec['flags']&4:continue
        raw=witness.data(sec);off=0
        while off<len(raw):
            size=4 if raw[off]&3==3 else 2
            need(off+size<=len(raw),'Known executable section ends on instruction boundary')
            need(size==2 or raw[off]&31!=31,'No unsupported long instruction in admitted code')
            code=raw[off:off+size];pc=sec['address']+off;instruction_total+=1
            d=direct(code,pc)
            if d and region(d[1]):
                decoded.append({'region':region(d[1]),'source':pc,'target':d[1],'kind':d[0],'rd':d[2],
                                'bytes':code.hex(),'source_owner':sec['name'],'source_inside_same_selected_region':region(pc)==region(d[1])})
            if d and region(pc) and region(d[1])!=region(pc):
                outgoing.append({'source':pc,'target':d[1],'kind':d[0],'rd':d[2],'source_region':region(pc)})
            x=int.from_bytes(code,'little')
            if size==4 and x&127 in (0x17,0x37) and (x>>7)&31 and off+size<len(raw):
                rd=(x>>7)&31;upper=((pc if x&127==0x17 else 0)+(x&0xfffff000))&0xffffffff
                pos=off+size;following_size=4 if raw[pos]&3==3 else 2
                if pos+following_size<=len(raw):
                    following=int.from_bytes(raw[pos:pos+following_size],'little');imm=None;kind=None
                    if following_size==4 and (following>>15)&31==rd and following&127 in (0x13,0x03,0x67):
                        if following&127!=0x13 or (following>>12)&7==0:
                            imm=sx(following>>20,12);kind='adjacent_addi' if following&127==0x13 else 'adjacent_memory_or_jalr'
                    elif following_size==2 and following&3==1 and following>>13==0 and (following>>7)&31==rd:
                        imm=sx(((following>>12)&1)*32+((following>>2)&31),6);kind='adjacent_c_addi'
                    if imm is not None and region((upper+imm)&0xfffffffe):
                        address_pairs.append({'source':pc,'following':pc+size,'target':(upper+imm)&0xffffffff,'kind':kind,'bytes':raw[off:pos+following_size].hex()})
            is_jalr=size==4 and x&127==0x67
            is_c_indirect=size==2 and x&3==2 and x>>13==4 and (x>>2)&31==0 and (x>>7)&31!=0
            if is_jalr or is_c_indirect:
                indirect.append({'source':pc,'source_owner':sec['name'],'bytes':code.hex(),
                                 'return_encoding':code.hex()=='8280'})
            off+=size
    candidates=[]
    for off in range(0,len(data)-1,2):
        size=4 if data[off]&3==3 else 2
        if off+size>len(data):continue
        d=direct(data[off:off+size],0x8000+off)
        if d and region(d[1]):
            candidates.append({'source':0x8000+off,'target':d[1],'kind':d[0],'rd':d[2],
                               'bytes':data[off:off+size].hex(),'admitted_instruction_boundary':any(x['source']==0x8000+off for x in decoded)})
    words=[]
    for off in range(len(data)-3):
        value=int.from_bytes(data[off:off+4],'little');target=value&0xfffffffe
        if region(target):
            address=0x8000+off
            owner=next(s for s in allocations if s['address']<=address<s['address']+s['size'])
            words.append({'region':region(target),'source':address,'value':value,'normalized_jalr_target':target,
                          'aligned32':address%4==0,'owner':owner['name'],'owner_executable':bool(owner['flags']&4),
                          'classification':'numeric window candidate, not established pointer'})
    ranges=[]
    for name,start,end in RANGES:
        owners=[{'name':s['name'],'start':s['address'],'end_exclusive':s['address']+s['size']} for s in allocations if s['address']<end and s['address']+s['size']>start]
        ranges.append({'name':name,'start':start,'end_exclusive':end,'bytes':end-start,
                       'sha256':sha(data[start-0x8000:end-0x8000]),'owners':owners})
    return {'schema':'TSL9-placement-static-source-inventory-v1','passed':True,'original_sha256':IMAGE,
            'object_sha256':OBJECT,'witness_sha256':WITNESS,'elf_parser_sha256':PARSER,
            'full_layout_sha256':LAYOUT,'full_layout_bindings':691,'full_layout_size_assertions':691,
            'allocations':691,'raw_RELA':8280,'RELA_type_counts':{str(k):v for k,v in collections.Counter(r['type'] for r in obj.relocations).items()},
            'source_image_file_backed_allocations':690,'RAM_NOBITS_allocations':1,'RAM_NOBITS_bytes':35160,
            'owned_ranges':ranges,'total_selected_original_bytes':sum(e-s for _,s,e in RANGES),
            'relocation_references':refs,'defined_symbols':definitions,'known_executable_instruction_count':instruction_total,
            'known_direct_references':decoded,'unrestricted_halfword_control_candidates':candidates,'raw_word_windows':words,
            'selected_outgoing_direct_references':outgoing,'adjacent_static_address_pairs':address_pairs,
            'reset_memory_fallthrough':{'entry_predecessor':0x186b6,'entry':0x186ba,'exit_conditional_branch':0x186ea,'continuation':0x186f8,'fallthrough_after':0x186f4},
            'known_indirect_transfers':{'count':len(indirect),'return_encoding_count':sum(x['return_encoding'] for x in indirect),
                                       'source_addresses':[x['source'] for x in indirect],
                                       'canonical_full_records_sha256':sha(json.dumps(indirect,sort_keys=True,separators=(',',':')).encode('utf-8'))},
            'unresolved_relocations':unresolved,
            'absence_of_additional_incoming_references_proved':False,'unknown_computed_targets_excluded':False,
            'padding_free_space_proved':False,'placement_plan_proved':False,'new_BIN_produced':False,
            'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False,'OTA_ready':False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--firmware',type=Path,required=True)
    p.add_argument('--object',type=Path,required=True)
    p.add_argument('--witness',type=Path,required=True)
    p.add_argument('--elf-parser',type=Path,required=True)
    p.add_argument('--layout',type=Path)
    p.add_argument('--reference',type=Path)
    a=p.parse_args()
    result=analyze(a.firmware,a.object,a.witness,a.elf_parser,a.layout)
    if a.reference:
        validate_reference(result,json.loads(a.reference.read_text(encoding='utf-8')))
        print(json.dumps({'passed':True,'owned_bytes':result['total_selected_original_bytes'],'allocations':691,'RELA':8280,
                          'relocation_references':len(result['relocation_references']),
                          'known_direct_references':len(result['known_direct_references']),
                          'raw_word_windows':len(result['raw_word_windows']),'placement_proved':False},sort_keys=True))
    else:
        print(json.dumps(result,indent=2))

if __name__=='__main__':main()
