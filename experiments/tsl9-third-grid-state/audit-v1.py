#!/usr/bin/env python3
"""Static operand/caller evidence audit; no target, HOST model, or ISA execution."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(v,label):
 if not v:raise ValueError(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def audit():
 s=json.loads((HERE/'spec-v1.json').read_bytes());need(all(sha(ROOT/p)==h for p,h in s['pins'].items()),'Pinned current evidence inputs');ev=json.loads((ROOT/s['evidence']).read_bytes());fw=(ROOT/ev['firmware']).read_bytes();need(sha(ROOT/ev['firmware'])==ev['firmware_sha256']and len(fw)==76800,'Original official BIN')
 need(all(sha(ROOT/p)==h for p,h in ev['inputs'].items()),'All captured source/layout/flow identities');B=runpy.run_path(str(ROOT/s['layout_builder']),run_name='row_static_layout');need(all(sha(ROOT/p)==h for p,h in B['K']['pins'].items()),'Transitive selected-source pins');need(sha(ROOT/B['K']['reader'])==B['K']['reader_sha256'],'Pinned actual ELF reader')
 need(all(sha(B['source'](mode))==B['K']['source_sha256']for mode in ['c','cpp']),'Both current accepted native components');e=B['E'](B['source']('c'));plan=B['derive'](e);linked=B['E'](ROOT/s['original_layout']);ins={};owner_names={};total=0
 for owner in plan['owners']:
  if owner['info']!=18:continue
  pc=owner['original_PC'];raw=linked.data(owner['section'])[owner['section_offset']:owner['section_offset']+owner['bytes']];need(raw==fw[pc-0x8000:pc-0x8000+len(raw)],'Every selected original CODE byte');total+=len(raw);at=0
  while at<len(raw):
   n=4 if raw[at]&3==3 else 2;need(at+n<=len(raw)and pc+at not in ins,'Whole unique original instruction');ins[pc+at]=raw[at:at+n];owner_names[pc+at]=owner['name'];at+=n
 need(total==64544 and len(ins)==21938,'Complete selected CODE scope');ops={}
 for window in ev['CODE_windows']:
  at=window['start']
  for op in window['operations']:
   need(op['addr']==at and bytes.fromhex(op['bytes'])==ins[at]and op['size']==len(ins[at])and at not in ops,'Fresh captured original bytes and boundaries');ops[at]=op;at+=op['size']
  need(at==window['end'],'Whole bounded original capture')
 need(len(ops)==275 and len(ev['CODE_windows'])==11,'All275 freshly captured instructions')
 def word(pc):return int.from_bytes(ins[pc],'little')
 def fields(pc):
  w=word(pc);return w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(w>>20,12)
 def pair(hi,lo,reg):
  a,z=word(hi),word(lo);need(len(ins[hi])==len(ins[lo])==4 and a&127==0x17 and(a>>7)&31==reg and z&0x707f==0x13 and(z>>7)&31==(z>>15)&31==reg,'Actual original AUIPC/ADDI register operands');return(hi+(a&0xfffff000)+sx(z>>20,12))&0xffffffff
 def cli(pc,reg,value):
  w=word(pc);need(len(ins[pc])==2 and w&0xe003==0x4001 and(w>>7)&31==reg and sx((((w>>12)&1)<<5)|((w>>2)&31),6)==value,'Actual compressed literal operand at '+hex(pc))
 def store(pc,base_reg,value_reg,kind,offset):
  w=word(pc);need(len(ins[pc])==4 and w&127==0x23 and(w>>15)&31==base_reg and(w>>20)&31==value_reg and(w>>12)&7==kind and sx(((w>>25)<<5)|((w>>7)&31),12)==offset,'Actual original store operands at '+hex(pc))
 direct=[];decoder=B['B']['decode_control']
 for pc,raw in sorted(ins.items()):
  target=decoder(raw,pc)
  if target is not None:direct.append(dict(PC=pc,kind=target[0],target_PC=target[1]))
 flow=json.loads((ROOT/s['flow']).read_bytes());need(direct==[{k:v[k]for k in ['PC','kind','target_PC']}for v in flow['direct_transfers']],'Every current selected direct transfer redecoded')
 callers=[v for v in direct if v['target_PC']==0xd05c];need([v['PC']for v in callers]==[0xa224,0xac6c,0xd528,0xe1ea,0xe6e8],'Exactly five selected direct writer callers')
 refs=[]
 for rel in e.relocations:
  if e.symbols[rel['symbol']]['name']!='tsl9_rom_dependency_external_d05c':continue
  owner,off=B['lookup'](plan,rel['section'],rel['offset']);refs.append(dict(PC=owner['original_PC']+off,type=rel['type'],addend=rel['addend']))
 need(refs==ev['D05C_native_references']and len(refs)==5 and all(v['type']==17 and v['addend']==0 for v in refs),'Only the five actual direct references;no selected address-taken DATA reference')
 need(pair(0xd05c,0xd060,15)==0x2000bf38,'Actual setter state base');store(0xd06e,15,10,0,1);need(ops[0xd07a]['opcode']=='ret','Original writer returns after byte stores')
 profiles=[]
 for call,literal,value in [(0xa224,0xa220,3),(0xd528,0xd524,5),(0xe1ea,0xe1e8,3),(0xe6e8,0xe6e6,3)]:
  cli(literal,10,value);need(not any(literal<v['target_PC']<=call for v in direct),'No selected direct entry bypasses this constant setter tail');profiles.append(dict(call_PC=call,value_PC=literal,row_values=[value]))
 cli(0xac12,10,1);cli(0xac64,10,3);need(ops[0xac10]['opcode']=='bnez a0, 0xac58'and ops[0xac68]['opcode']=='beqz a5, 0xac14'and ops[0xac16]['opcode']=='j 0xac6a','Original normalization paths')
 need([(v['PC'],v['target_PC'])for v in direct if v['target_PC']in(0xac14,0xac16,0xac6a,0xac6c)]==[(0xac16,0xac6a),(0xac68,0xac14)],'Only expected selected direct entries into shared normalization tails');need(not any(0xac64<v['target_PC']<=0xac68 for v in direct),'No selected direct entry bypasses the second normalization literal');profiles.append(dict(call_PC=0xac6c,value_PCs=[0xac12,0xac64],row_values=[1,3]))
 word_profiles=[]
 for high,low,value in [(0xd0b2,0xd0b6,0x01000501),(0xd0bc,0xd0c0,0x01000401),(0xd0d4,0xd0d8,0x01000201)]:
  need(fields(high)[:2]==(0x37,15)and word(high)&0xfffff000==0x01000000 and fields(low)[0:4]==(0x13,15,0,15)and(0x01000000+fields(low)[5])&0xffffffff==value,'Actual original word literal');need(not any(high<v['target_PC']<=low for v in direct),'No selected direct entry bypasses the word LUI');word_profiles.append(dict(high_PC=high,low_PC=low,word_value=value,row_byte=(value>>8)&255))
 store(0xd0c8,14,15,2,-396);need((0xd0c4+(word(0xd0c4)&0xfffff000)-396)&0xffffffff==0x2000bf38,'Word writer overlaps BF39 at byte1');need([(v['PC'],v['target_PC'])for v in direct if 0xd0c4<=v['target_PC']<=0xd0c8]==[(0xd0ba,0xd0c4),(0xd0dc,0xd0c4)],'Only expected selected direct word-writer joins')
 # Independently repeat the bounded syntactic address inventory;no CFG emulation.
 accesses=[];pointers=[];lui_near=[]
 for pc,raw in sorted(ins.items()):
  if len(raw)!=4 or len(ins.get(pc+4,b''))!=4:continue
  a,z=word(pc),word(pc+4);opcode=a&127;reg=(a>>7)&31
  if opcode not in(0x17,0x37)or not reg or(z>>15)&31!=reg:continue
  base=((pc if opcode==0x17 else 0)+(a&0xfffff000))&0xffffffff;op=z&127;kind=(z>>12)&7;row=None
  if op==0x13 and kind==0 and(z>>7)&31==reg:
   address=(base+sx(z>>20,12))&0xffffffff
   if 0x2000bf20<=address<0x2000bf60:
    row=dict(high_PC=pc,low_PC=pc+4,register=reg,address=address,owner=owner_names[pc],raw_high=raw.hex(),raw_low=ins[pc+4].hex())
    if opcode==0x17:pointers.append(row)
    else:lui_near.append(row)
  if op==3 and kind in(0,1,2,4,5):
   address=(base+sx(z>>20,12))&0xffffffff;n={0:1,1:2,2:4,4:1,5:2}[kind]
   if address<0x2000bf60 and address+n>0x2000bf20:row=dict(high_PC=pc,memory_PC=pc+4,operation='load',kind=kind,bytes=n,address=address,register=(z>>7)&31,owner=owner_names[pc])
  if op==0x23 and kind in(0,1,2):
   address=(base+sx(((z>>25)<<5)|((z>>7)&31),12))&0xffffffff;n=1<<kind
   if address<0x2000bf60 and address+n>0x2000bf20:row=dict(high_PC=pc,memory_PC=pc+4,operation='store',kind=kind,bytes=n,address=address,register=(z>>20)&31,owner=owner_names[pc])
  if row is not None and 'memory_PC'in row:
   if opcode==0x17:accesses.append(row)
   else:lui_near.append(row)
 need(accesses==ev['direct_accesses_near_state']and pointers==ev['materialized_near_state_pointers'],'Actual66 adjacent accesses and17 materialized pointers reproduced')
 sdk=json.loads((ROOT/s['cached_SDK_evidence']).read_bytes())['cached_SDK_reference'];slot=sdk['default_base']+sdk['table_offset']+sdk['memset_index']*sdk['stride'];need(slot==0x40048,'Pinned public SDK default slot formula')
 resets=[]
 for entry,load,length_pc,length,zero_pc,hi,lo,end in [(0xceaa,0xceae,0xceb2,20,0xceb4,0xceb6,0xceba,0xcebe),(0xd0ee,0xd0f2,0xd0f6,16,0xd0f8,0xd0fa,0xd0fe,0xd102)]:
  need(word(entry)==0x000407b7 and fields(load)==(3,6,2,15,8,72)and word(end)==0x8302,'Actual resident-table slot load and indirect tail transfer');cli(length_pc,12,length);cli(zero_pc,11,0);base=pair(hi,lo,10);resets.append(dict(entry=entry,slot=slot,destination=base,length_argument=length,value_argument=0,conditional_end=base+length,row_overlapped=base<=0x2000bf39<base+length,conditional_effect='zero range only if installed slot obeys cached SDK tmos_memset',installed_ROM_identity_or_ABI_proved=False))
 need([v['destination']for v in resets]==[0x2000bf24,0x2000bf38]and[bool(v['row_overlapped'])for v in resets]==[False,True],'Adjacent20-byte reset excludes row;16-byte reset includes row')
 # Reuse the independently pinned existing startup/GP operand proof,not runtime evidence.
 previous=runpy.run_path(str(ROOT/s['prior_index_audit']),run_name='prior_positive_index_library')['audit']();startup=previous['startup_zeroing'];need(startup['zero_start']<=0x2000bf39<startup['zero_end']and startup['GP']==0x20004000,'Row falls within the original coded zeroing interval')
 need(pair(0xc90a,0xc90e,12)==0x2000bf30 and decoder(ins[0xc91e],0xc91e)==(17,0xebac),'Original preceding-record pointer and helper call');need(ops[0xebb8]['opcode']=='mv s0, a2'and ops[0xebba]['opcode']=='beq a5, a4, 0xec50'and ops[0xec54]['opcode']=='bne a5, a0, 0xec82','Direct unchanged-A2 helper path')
 stores=[]
 for pc,op in sorted(ops.items()):
  if not(0xebac<=pc<0xeca8):continue
  w=word(pc);size=0;offset=0;base=0
  if len(ins[pc])==4 and w&127==0x23 and(w>>15)&31 in(8,12):
   base=(w>>15)&31;kind=(w>>12)&7;need(kind in(0,1,2),'Known helper store width');size=1<<kind;offset=sx(((w>>25)<<5)|((w>>7)&31),12)
  elif len(ins[pc])==2 and w&0xe003==0xc000 and 8+((w>>7)&7)==8:base=8;size=4;offset=(((w>>10)&7)<<3)|(((w>>6)&1)<<2)|(((w>>5)&1)<<6)
  if size:stores.append(dict(PC=pc,base_register=base,offset=offset,bytes=size,end_offset=offset+size))
 need(len(stores)==9 and max(v['end_offset']for v in stores)==8 and all(0<=v['offset']<v['end_offset']<=8 for v in stores),'Every selected direct helper store has an eight-byte local record footprint');need([v['PC']for v in stores if v['base_register']==12]==[0xec82],'Only the unchanged-A2 zero store uses A2')
 need([(v['PC'],v['target_PC'])for v in direct if v['target_PC']in(0xec50,0xec82)]==[(0xebba,0xec50),(0xec54,0xec82)],'No other selected direct entries into the unchanged-A2 helper path')
 selected_values=sorted({0}|{n for p in profiles for n in p['row_values']}|{v['row_byte']for v in word_profiles});need(selected_values==[0,1,2,3,4,5],'Known selected initialization profiles,not all runtime states')
 need(fields(0xcf0a)==(3,14,4,14,19,51)and ops[0xcf7c]['opcode']=='andi a3, a4, 7'and ops[0xcf3e]['opcode']=='slli a4, a4, 0x4'and ops[0xcf44]['opcode']=='andi a3, a3, 15','Actual unsigned-byte row and distinct packed-field mask')
 return dict(passed=True,schema='TSL9-third-grid-state-audit-v1',captured_original_instructions=275,selected_CODE_bytes=total,selected_instructions=len(ins),setter=dict(entry=0xd05c,row_store_PC=0xd06e,state_base=0x2000bf38,row_address=0x2000bf39,row_argument_register='a0',local_row_mask_present=False,selected_direct_callers=profiles,selected_address_taken_references=0),word_writer=dict(store_PC=0xd0c8,state_base=0x2000bf38,profiles=word_profiles),adjacent_AUIPC_access_count=len(accesses),adjacent_AUIPC_pointer_count=len(pointers),adjacent_LUI_near_state_uses=lui_near,conditional_resets=resets,startup_zeroing=startup,preceding_record_helper=dict(caller_PC=0xc91e,pointer=0x2000bf30,entry=0xebac,direct_store_footprint_bytes=8,direct_stores=stores,direct_store_end=0x2000bf38,row_overlapped=False,all_callee_or_alias_effects_closed=False),conditional_selected_row_values=selected_values,conditional_lookup=dict(base=0x1a078,row_minimum=0,row_maximum=5,row_stride=16,column_maximum=15,bytes=96,end=0x1a0d8,full_three_window_union_start=0x19ed8,full_three_window_union_end=0x1a0d8,full_three_window_union_bytes=512,overlap_with_current_pool_bytes=16,additional_original_bytes_if_justified=80,source_DATA_provided=False,original_declaration_extents_proved=False),unresolved=['Arbitrary record-pointer aliases and indirect entry paths','Opaque resident initialization/reset/callee side effects and installed ABI','Other non-adjacent or dynamic pointer derivations and asynchronous effects'],all_alias_writers_closed=False,global_row_bound_proved=False,physical_feature_names_proved=False,provided_DATA_bytes=0,source_manifest_updated=False,accepted_component_updated=False,accepted_UND_unchanged=22,accepted_coverage_percent_unchanged=88.89,firmware_BIN_generated=False,firmware_ready=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full',action='store_true');a=p.parse_args()
 try:
  r=audit();print(json.dumps(r if a.full else {k:r[k]for k in ['passed','captured_original_instructions','selected_CODE_bytes','conditional_selected_row_values','global_row_bound_proved','provided_DATA_bytes','accepted_UND_unchanged','accepted_coverage_percent_unchanged','firmware_ready']}))
 except Exception as e:
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=str(e).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));raise SystemExit(1)
