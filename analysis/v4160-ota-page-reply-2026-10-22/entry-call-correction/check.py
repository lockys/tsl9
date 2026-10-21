#!/usr/bin/env python3
"""Narrow correction: decode actual 9DF4 C.JAL, not a no-link tail assumption."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
PC=0x9df4
CALLER='.text.tsl9v4160.ota_handler_9c4a'
OWNER='.text.tsl9v4160.ota_handler_9b8e'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def instruction(word,pc=PC):
    need(len(word)==2,'One complete compressed instruction');h=int.from_bytes(word,'little');need(h&3==1 and h>>13 in (1,5),'RV32 C.JAL/C.J encoding, not relocation-name inference')
    imm=(((h>>12)&1)<<11)|(((h>>11)&1)<<4)|(((h>>9)&3)<<8)|(((h>>8)&1)<<10)|(((h>>7)&1)<<6)|(((h>>6)&1)<<7)|(((h>>3)&7)<<1)|(((h>>2)&1)<<5);imm=imm-4096 if imm&2048 else imm;rd=1 if h>>13==1 else 0
    return {'PC':pc,'raw_hex':word.hex(),'halfword':h,'bytes':2,'quadrant':h&3,'funct3':h>>13,'instruction':'RV32 C.JAL' if rd else 'RV32 C.J','rd':rd,'signed_delta':imm,'target':pc+imm,'RA_written':pc+2 if rd else None}
def validate(word):
    r=instruction(word);need((r['instruction'],r['rd'],r['target'],r['RA_written'])==('RV32 C.JAL',1,0x9b8e,0x9df6),'Actual incoming call links RA9DF6 and targets9B8E');return r
def raw_controls(word):
    h=int.from_bytes(word,'little');controls=[]
    for name,value in [('same_target_no_link_CJ',h^0x8000),('changed_compressed_target',h^4),('wrong_instruction_width',h|2)]:
        payload=value.to_bytes(2,'little')
        try:validate(payload)
        except ValueError as error:controls.append({'name':name,'mutated_raw':payload.hex(),'rejected':True,'reason':str(error)});continue
        raise ValueError('Incorrect call instruction admitted: '+name)
    return controls
def ELF(root):
    paths=[root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'];path=next(p for p in paths if p.is_file());need(sha(path)==PARSER,'Pinned read-only ELF parser');s=importlib.util.spec_from_file_location('reply_entry_correction_ELF',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.ELF
def elf_contract(e,word,after):
    need(e.kind==1,'Actual boundary ET_REL object');caller=e.byname[CALLER];target=e.byname[OWNER];need(target['flags']==6 and target['type']==1 and target['alignment']==2 and target['size']==(124 if after else 0),'Actual target section boundary/zero-byte anchor')
    observed=e.data(caller)[426:428];r=validate(observed);need(observed==word,'Incoming actual object instruction equals original FW bytes')
    roles={s['name']:s for s in e.symbols if s['index']==target['index']};expected={'.Lota_handler_00009b8e':(0,0,0,0),'__tsl9v4160_ota_code_9b8e':(0,0,16,0)}
    if after:expected['tsl9_ota_page_reply_9b8e']=(0,124,18,0)
    for name,fields in expected.items():need(name in roles and tuple(roles[name][k] for k in ('value','size','info','other'))==fields,'Preserved section-relative entry role '+name)
    incoming=[x for x in e.relocations if x['symbol']['index']==target['index']];need(len(incoming)==1,'One recorded incoming boundary relocation');rel=incoming[0];need((rel['owner'],rel['offset'],rel['type'],rel['addend'],rel['symbol']['name'])==(CALLER,426,45,0,'.Lota_handler_00009b8e'),'Exact incoming type45/localentry role')
    return {'object_sha256':hashlib.sha256(e.raw).hexdigest(),'target_section_bytes':target['size'],'incoming_instruction':r,'recorded_incoming':{'owner':CALLER,'offset':426,'type':45,'addend':0,'symbol':'.Lota_handler_00009b8e','target_symbol_offset':0},'final_address_placement_proved':False}
class BytesInput:
    def __init__(self,payload):self.payload=payload
    def read_bytes(self):return self.payload
def elf_controls(parser,e,word):
    results=[];caller=e.byname[CALLER];b=bytearray(e.raw);at=caller['offset']+426;h=int.from_bytes(b[at:at+2],'little');b[at:at+2]=(h^0x8000).to_bytes(2,'little');mutants=[('actual_ELF_call_changed_to_no_link',bytes(b))]
    section=next(s for s in e.sections if s['type']==4 and s['info']==caller['index']);rawsite=None
    for offset in range(section['offset'],section['offset']+section['size'],12):
        if struct.unpack_from('<I',e.raw,offset)[0]==426:rawsite=offset
    need(rawsite is not None,'Actual incoming RELA record');b=bytearray(e.raw);info=struct.unpack_from('<I',b,rawsite+4)[0];struct.pack_into('<I',b,rawsite+4,(info&~255)|17);mutants.append(('actual_ELF_relocation_type_changed',bytes(b)))
    for table,entries in e.symbol_tables.items():
        for ordinal,s in enumerate(entries):
            if s['name']=='.Lota_handler_00009b8e':
                b=bytearray(e.raw);struct.pack_into('<I',b,e.sections[table]['offset']+16*ordinal+4,2);mutants.append(('actual_ELF_local_entry_offset_changed',bytes(b)))
    for name,payload in mutants:
        try:elf_contract(parser(BytesInput(payload)),word,True)
        except ValueError as error:results.append({'name':name,'actual_object_bytes_mutated_in_memory':True,'rejected':True,'reason':str(error)});continue
        raise ValueError('Incorrect actual ELF admitted: '+name)
    return results
def inspect(root,firmware,folder=None):
    need(sha(firmware)==FW,'Pinned actual ID2966 source firmware');full=firmware.read_bytes();word=full[PC-0x8000:PC-0x8000+2];r=validate(word);result={'schema':'TSL9-reply-entry-call-correction-actual-v1','passed':True,'firmware_sha256':FW,'incoming':r,'raw_semantic_controls':raw_controls(word),'scope':'Only9DF4 incoming call classification;9BF8 release tail remains unchanged','type45_alone_establishes_no_link':False,'whole_image_integrated':False,'target_execution':False,'ISA_emulation':False,'hardware_OTA_validated':False}
    if folder:
        parser=ELF(root);before=parser(folder/'carrier.o');after=parser(folder/'partial.o');result['actual_boundary_before']=elf_contract(before,word,False);result['actual_boundary_after']=elf_contract(after,word,True);result['actual_ELF_controls']=elf_controls(parser,after,word);result['actual_folder']=folder.resolve().relative_to(root).as_posix();result['boundary_receipt_sha256']=sha(folder/'verification.json')
    return result
def metadata():
    seal=read(HERE/'seal.json');need(seal['schema']=='TSL9-reply-entry-call-correction-seal-v1','Known supplemental seal');seen=set()
    for item in seal['files']:
        p=(HERE/item['path']).resolve();need(p.is_relative_to(HERE) and item['path'] not in seen and p!=HERE/'seal.json','Unique bounded seal member');seen.add(item['path']);need(p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],'Unchanged supplemental source/metadata')
    return {'passed':True,'mode':'metadata-only','members':len(seen),'actual_FW_or_object_replay':False,'hardware_OTA_validated':False}
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=HERE.parents[2]);p.add_argument('--firmware',type=Path);p.add_argument('--folder',type=Path);p.add_argument('--report',type=Path);a=p.parse_args();need(not a.folder or a.firmware is not None,'Actual boundary mode requires explicit original firmware')
    if a.firmware:result=inspect(a.project_root.resolve(),a.firmware.resolve(),a.folder.resolve() if a.folder else None)
    else:need(a.report is None,'Default metadata-only check creates no new evidence');result=metadata()
    if a.report:need(not a.report.exists(),'New create-only correction report');a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'passed':True,'mode':result.get('mode','actual-boundary' if a.folder else 'actual-original-FW'),'actual_FW_or_object_replay':bool(a.firmware),'incoming_rd':result.get('incoming',{}).get('rd'),'hardware_OTA_validated':False}))
if __name__=='__main__':main()
