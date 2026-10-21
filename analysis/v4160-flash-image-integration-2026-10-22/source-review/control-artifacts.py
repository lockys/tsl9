#!/usr/bin/env python3
"""Bounded actual file mutations; parse only, never launch original/rebuilt RV32."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def need(v,m):
    if not v:raise ValueError(m)
def run(root,firmware,receipt,output):
    g=load('independent_control_gate',HERE/'inspect-image.py');p=load('independent_dependency_gate',HERE/'provenance.py');c=g.retained_context(root,firmware,HERE/'source-constraints.json')
    folder=receipt.parent;paths=[folder/'source-integrated.o',folder/'ADDRESS-WITNESS-ONLY.elf',folder/'NOT-FLASH-VALIDATED-irq-and-flash.bin'];obj,elf=[c['E'](x) for x in paths[:2]]
    g.artifact_gate(obj,elf,paths[2],c);need(not output.exists(),'Create-only control directory');output.mkdir(parents=True)
    rows=[]
    def sh(raw,e,section,field,value):struct.pack_into('<I',raw,struct.unpack_from('<I',raw,32)[0]+section['index']*40+field,value)
    def sy(e,name):
        s=next(s for s in e.sections if s['type']==2);table=e.symbol_tables[s['index']];matches=[i for i,r in enumerate(table) if r['name']==name];need(len(matches)==1,'Unique symbol mutation');return s['offset']+matches[0]*16
    def re(e,predicate):
        for sec in e.sections:
            if sec['type']!=4:continue
            for index in range(sec['size']//12):
                off=sec['offset']+index*12;site,info,addend=struct.unpack_from('<IIi',e.raw,off);symbol=e.symbol_tables[sec['link']][info>>8]
                if predicate(e.sections[sec['info']]['name'],site,info&255,addend,symbol):return off
        raise ValueError('Required real relocation mutation site')
    native=next(x for x in c['selected'] if x['originalVA']==0x18ef2);entry=c['selected'][0]['global_alias'];binding=c['m']['section_relative_bindings'][0]['name']
    changes=[]
    raw=bytearray(obj.raw);s=obj.byname[next(iter(sorted(c['retained'])))];sh(raw,obj,s,8,s['flags']&~2);changes.append(('omitted_retained_allocation',0,raw))
    raw=bytearray(obj.raw);s=obj.byname[native['name']];raw[s['offset']:s['offset']+s['size']]=bytes.fromhex(next(x for x in c['new_manifest']['selected_sections'] if x['name']==native['name'])['original_bytes']);changes.append(('typed_program_replaced_by_raw_original',0,raw))
    raw=bytearray(obj.raw);at=re(obj,lambda owner,*unused:owner not in c['names']);struct.pack_into('<i',raw,at+8,struct.unpack_from('<i',raw,at+8)[0]+1);changes.append(('outside_RELA_signed_addend',0,raw))
    raw=bytearray(obj.raw);sec=next(s for s in obj.sections if s['type']==4 and s['size']>=24 and obj.sections[s['info']]['name'] not in c['names']);raw[sec['offset']+12:sec['offset']+24]=raw[sec['offset']:sec['offset']+12];changes.append(('outside_RELA_duplicate_preserves_count',0,raw))
    raw=bytearray(obj.raw);struct.pack_into('<H',raw,sy(obj,entry)+14,0xfff1);changes.append(('public_alias_ABS',0,raw))
    raw=bytearray(obj.raw);raw[sy(obj,entry)+12]=16;changes.append(('public_alias_NOTYPE',0,raw))
    raw=bytearray(obj.raw);at=re(obj,lambda owner,site,kind,addend,s:owner not in c['names'] and 0<s['index']<len(obj.sections) and obj.sections[s['index']]['name'] in c['names']);struct.pack_into('<i',raw,at+8,struct.unpack_from('<i',raw,at+8)[0]+2);changes.append(('external_entry_retargeted_to_interior',0,raw))
    raw=bytearray(obj.raw);at=sy(obj,binding);struct.pack_into('<I',raw,at+4,struct.unpack_from('<I',raw,at+4)[0]+2);changes.append(('canonical_relative_binding_offset',0,raw))
    raw=bytearray(elf.raw);sh(raw,elf,elf.byname[native['name']],20,94);changes.append(('program_owner_shortened_100_to94',1,raw))
    off=struct.unpack_from('<I',elf.raw,28)[0];stride,count=struct.unpack_from('<HH',elf.raw,42);ph=[off+i*stride for i in range(count) if struct.unpack_from('<I',elf.raw,off+i*stride)[0]==1];file_ph=next(at for at in ph if struct.unpack_from('<I',elf.raw,at+16)[0]);ram_ph=next(at for at in ph if not struct.unpack_from('<I',elf.raw,at+16)[0])
    for name,at,field,delta in [('LOAD_wrong_physical_address',file_ph,12,4),('LOAD_hidden_zero_tail',file_ph,20,4),('LOAD_RAM_memory_extent',ram_ph,20,4),('LOAD_wrong_permissions',file_ph,24,1)]:
        raw=bytearray(elf.raw);old=struct.unpack_from('<I',raw,at+field)[0];struct.pack_into('<I',raw,at+field,old^delta if field==24 else old+delta);changes.append((name,1,raw))
    raw=bytearray(paths[2].read_bytes());raw[0]^=1;changes.append(('BIN_outside_typed_byte',2,raw));changes.append(('BIN_truncated_tail',2,paths[2].read_bytes()[:-1]))
    for name,index,raw in changes:
        path=output/(name+('.o','.elf','.bin')[index]);path.write_bytes(raw);actual=list(paths);actual[index]=path
        try:g.artifact_gate(c['E'](actual[0]),c['E'](actual[1]),actual[2],c)
        except ValueError as error:reason=str(error)
        else:raise ValueError('Accepted independent actual file control '+name)
        rows.append({'case':name,'sha256':sha(path),'bytes':len(raw),'rejected':True,'reason':reason})
    r=json.loads(receipt.read_text(encoding='utf-8'));command=next(x for x in r['commands'] if x['label']=='typed-flash-program-object');argv=command['argv'];d=Path(argv[argv.index('-MF')+1]);text=d.read_text(encoding='utf-8');primary=Path(argv[argv.index('-c')+1]);p.dependency_rule(text,argv,primary)
    target,body=text.replace('\\\n','').replace('\\\r\n','').split(': ',1)
    for name,value in [('dependency_wrong_target','wrong.o: '+body),('dependency_missing_primary',target+': '+body.replace(primary.as_posix().replace(' ','\\ '),''))]:
        need(value!=text,'Actual changed dependency text')
        path=output/(name+'.d');path.write_bytes(value.encode('utf-8'))
        try:p.dependency_rule(value,argv,primary)
        except ValueError as error:reason=str(error)
        else:raise ValueError('Accepted independent dependency rule control '+name)
        rows.append({'case':name,'sha256':sha(path),'bytes':path.stat().st_size,'rejected':True,'reason':reason})
    result={'schema':'ID2966-independent-image-file-controls-v1','passed':True,'actual_file_controls':len(changes),'actual_dependency_text_controls':2,'rows':rows,'base_artifacts':{p.name:sha(p) for p in paths},'receipt_sha256':sha(receipt),'checker_sha256':sha(HERE/'inspect-image.py'),'target_execution':False,'emulation':False,'network':False}
    (output/'verification.json').write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'));return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--output-directory',type=Path,required=True);a=p.parse_args();output=a.output_directory.resolve();output.relative_to(HERE);r=run(a.project_root.resolve(),a.firmware.resolve(),a.receipt.resolve(),output);print(json.dumps({'passed':True,'controls':len(r['rows']),'report':str(output/'verification.json')}))
if __name__=='__main__':main()
