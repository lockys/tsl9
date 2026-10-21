#!/usr/bin/env python3
"""Bounded malformed-actual-ELF and receipt controls for the separate ABI tool."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import struct
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,value):
    need(not path.exists(),'Create-only audit evidence');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value)
def module(path):
    s=importlib.util.spec_from_file_location('reply_independent_native',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def audit(root,folder,work):
    root=root.resolve();folder=folder.resolve();work=work.resolve();need(work.is_relative_to(root) and not work.exists(),'New explicit in-project audit folder');work.mkdir(parents=True)
    tool=root/'experiments/tsl9-v4160-reply-abi-order/order.py';api=runpy.run_path(str(tool));before_tool=sha(tool);policy=tool.with_name('order-policy.json');policy_hash=sha(policy);ELF,decoder,rule=api['context'](root);source=folder/'page_reply.o';e=ELF(source);section=e.byname[rule['section']];start=section['offset'];shoff=struct.unpack_from('<I',e.raw,32)[0]
    native=module(HERE/'native.py');output=work/'ordered.o';receipt=work/'order-receipt.json';positive=api['transform'](root,source,output,receipt);need(api['replay'](root,receipt)==positive,'Actual explicit ABI receipt replay');independent=native.review(root,folder,output)
    mutations=[]
    def reject(name,payload):
        inp=work/(name+'.o');out=work/(name+'-output.o');rec=work/(name+'-receipt.json');write(inp,payload)
        try:api['transform'](root,inp,out,rec)
        except (ValueError,KeyError,StopIteration) as error:
            need(not out.exists() and not rec.exists(),'Rejected actual ELF wrote no output');mutations.append({'name':name,'input_sha256':sha(inp),'rejected_before_write':True,'reason':str(error)});return
        raise ValueError('Malformed actual ELF admitted: '+name)
    def changed(name,offset,fmt,value):
        b=bytearray(e.raw);struct.pack_into(fmt,b,offset,value);reject(name,bytes(b))
    def sympos(name):
        for index,entries in e.symbol_tables.items():
            for ordinal,symbol in enumerate(entries):
                if symbol['name']==name:return e.sections[index]['offset']+16*ordinal
        raise ValueError('Required actual symbol absent')
    f=sympos(rule['symbol']);changed('wrong_function_NOTYPE',f+12,'B',16);changed('hidden_function',f+13,'B',2)
    mapping=next(s['name'] for s in e.symbols if s['index']==section['index'] and s['name'].startswith('$x'));pos=sympos(mapping);changed('interior_mapping_anchor',pos+4,'I',2)
    b=bytearray(e.raw);struct.pack_into('<I',b,pos+8,124);b[pos+12]=2;reject('overlapping_local_FUNC',bytes(b))
    comment=next(s for s in e.sections if s['name']=='.comment');h=shoff+comment['index']*40
    changed('duplicate_owner_section_name',h,'I',section['name_offset'])
    b=bytearray(e.raw);struct.pack_into('<II',b,h+16,start+2,20);reject('aliased_comment_storage',bytes(b))
    names_index=struct.unpack_from('<H',e.raw,50)[0];names=e.sections[names_index];b=bytearray(e.raw);at=names['offset']+comment['name_offset'];b[at:at+8]=b'.sframe\0';reject('implicit_unwind_section',bytes(b))
    rela=next(s for s in e.sections if s['type']==4);changed('relocation_inside_window',rela['offset'],'I',2);changed('TX_relocation_addend',rela['offset']+8,'i',2);info=struct.unpack_from('<I',e.raw,rela['offset']+4)[0];changed('TX_wrong_relocation_width',rela['offset']+4,'I',(info&~255)|45)
    changed('wrong_save_register',start+2,'H',int.from_bytes(e.raw[start+2:start+4],'little')^0x1c)
    changed('wrong_save_slot',start+2,'H',int.from_bytes(e.raw[start+2:start+4],'little')^0x200)
    changed('wrong_instruction_width',start+2,'H',int.from_bytes(e.raw[start+2:start+4],'little')|3)
    b=bytearray(e.raw);b[start+2:start+6]=b[start+4:start+6]+b[start+2:start+4];reject('wrong_compiler_order',bytes(b))
    changed('allocator_no_RA_link',start+0x20,'H',int.from_bytes(e.raw[start+0x20:start+0x22],'little')^0x1000)
    changed('altered_null_branch',start+0x22,'H',int.from_bytes(e.raw[start+0x22:start+0x24],'little')^4)
    changed('release_links_RA',start+0x6a,'H',int.from_bytes(e.raw[start+0x6a:start+0x6c],'little')^0x1000)
    reject('reapplication',output.read_bytes())
    path_controls=[]
    for name,inp,out,rec in [('input_output_alias',source,source,work/'alias-a.json'),('input_receipt_alias',source,work/'alias-b.o',source),('output_receipt_alias',source,work/'alias-c.o',work/'alias-c.o'),('existing_output',source,output,work/'collision-a.json'),('existing_receipt',source,work/'collision-b.o',receipt)]:
        snapshots={p:p.read_bytes() for p in (inp,out,rec) if p.exists()}
        try:api['transform'](root,inp,out,rec)
        except ValueError as error:
            need(all(p.read_bytes()==data for p,data in snapshots.items()),'Rejected alias/collision preserves existing bytes');path_controls.append({'name':name,'rejected':True,'reason':str(error)});continue
        raise ValueError('Path hazard admitted: '+name)
    receipt_controls=[]
    for name,key,value in [('false_hardware_claim','hardware',True),('wrong_policy_pin','policy_sha256','0'*64),('false_compiler_only_claim','compiler_alone_emitted_scheduled_order',True)]:
        altered=dict(positive);altered[key]=value;p=work/(name+'.json');write(p,(json.dumps(altered,indent=2)+'\n').encode())
        try:api['replay'](root,p)
        except ValueError as error:receipt_controls.append({'name':name,'rejected':True,'reason':str(error)});continue
        raise ValueError('Receipt tamper admitted: '+name)
    need(sha(tool)==before_tool and sha(policy)==policy_hash,'Tool/policy unchanged through audit')
    return {'schema':'TSL9-page-reply-ABI-order-independent-actual-controls-v1','passed':True,'tool_sha256':before_tool,'policy_sha256':policy_hash,'input_sha256':sha(source),'output_sha256':sha(output),'independent_native':independent,'actual_ELF_controls':mutations,'path_controls':path_controls,'receipt_controls':receipt_controls,'target_execution':False,'ISA_emulation':False,'hardware':False,'network':False}
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--folder',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args();r=audit(a.project_root,a.folder,a.work);write(a.work/'audit.json',(json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'passed':True,'ELF_controls':len(r['actual_ELF_controls']),'path_controls':len(r['path_controls']),'receipt_controls':len(r['receipt_controls'])}))
if __name__=='__main__':main()
