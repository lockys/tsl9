#!/usr/bin/env python3
"""Audit original fixed-length readonly arguments; preserve unknown resident contracts."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(v,label):
 if not v:raise ValueError(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def audit():
 s=json.loads((HERE/'spec-v1.json').read_bytes());need(sha(ROOT/s['evidence'])==s['evidence_sha256']and sha(ROOT/s['source'])==s['source_sha256'],'Pinned original evidence and actual C data source');ev=json.loads((ROOT/s['evidence']).read_bytes());fw=(ROOT/ev['firmware']).read_bytes();need(len(fw)==76800 and sha(ROOT/ev['firmware'])==ev['firmware_sha256'],'Original official firmware')
 need(all(sha(ROOT/p)==h for p,h in ev['inputs'].items()),'Current selected-layout/source identities');B=runpy.run_path(str(ROOT/ev['layout_builder']),run_name='prefix_selected_layout');need(all(sha(ROOT/p)==h for p,h in B['K']['pins'].items()),'Transitive selected-source/layout pins');need(sha(ROOT/B['K']['reader'])==B['K']['reader_sha256'],'Pinned ELF reader')
 need(all(sha(B['source'](mode))==s['parent_component_sha256']for mode in ['c','cpp']),'Both exact accepted parent objects');e=B['E'](B['source']('c'));plan=B['derive'](e);linked=B['E'](ROOT/ev['original_layout']);ins={};total=0
 for owner in plan['owners']:
  if owner['info']!=18:continue
  pc=owner['original_PC'];raw=linked.data(owner['section'])[owner['section_offset']:owner['section_offset']+owner['bytes']];need(raw==fw[pc-0x8000:pc-0x8000+len(raw)],'Every current selected CODE byte');total+=len(raw);at=0
  while at<len(raw):
   n=4 if raw[at]&3==3 else 2;need(at+n<=len(raw)and pc+at not in ins,'Whole unique original instruction');ins[pc+at]=raw[at:at+n];at+=n
 need(total==64544 and len(ins)==21938,'Complete selected CODE audit scope');ops={}
 for window in ev['CODE_windows']:
  at=window['start']
  for op in window['operations']:
   need(op['addr']==at and op['size']==len(ins[at])and bytes.fromhex(op['bytes'])==ins[at]and at not in ops,'Fresh captured original instruction/boundary');ops[at]=op;at+=op['size']
  need(at==window['end'],'Whole bounded disassembly window')
 need(len(ops)==104 and len(ev['CODE_windows'])==16,'All104 freshly captured instructions')
 def word(pc):return int.from_bytes(ins[pc],'little')
 def fields(pc):
  w=word(pc);return w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sx(w>>20,12)
 def pair(hi,lo,reg):
  a,z=word(hi),word(lo);need(len(ins[hi])==len(ins[lo])==4 and a&127==0x17 and(a>>7)&31==reg and z&0x707f==0x13 and(z>>7)&31==(z>>15)&31==reg,'Actual original AUIPC/ADDI operands');return(hi+(a&0xfffff000)+sx(z>>20,12))&0xffffffff
 old=json.loads((ROOT/'experiments/tsl9-registered-callbacks/spec-v1.json').read_bytes());literal_roles={v['target']:v for v in old['PC_relative_pairs']};regions=s['data_regions'];need(regions==ev['data_regions']and len(regions)==14 and sum(v['bytes']for v in regions)==109,'Exact14 source argument windows')
 RX=runpy.run_path(str(ROOT/'scripts/audit-sensitive-data.py'),run_name='prefix_raw_privacy_library')['RX'];facts=[]
 for region in regions:
  n=region['bytes'];start=region['start'];hi=region['HI_PC'];need(start+n==region['end']<=0x1a638 and n==region['length_argument'],'Only selected non-protected DATA ranges')
  raw=fw[start-0x8000:region['end']-0x8000];need(list(raw)==region['original_bytes']and hashlib.sha256(raw).hexdigest()==region['original_sha256'],'Every original readonly argument byte');need(all(32<=v<127 for v in raw)and not any(rx.search(raw)for rx in RX.values()),'Original selected bytes have no sensitive candidates')
  need(not any(start<o['original_PC']+o['bytes']and o['original_PC']<start+n for o in plan['owners']),'No accepted CODE/DATA overlap');need(region['name']in literal_roles and literal_roles[region['name']]['PC']==hi and literal_roles[region['name']]['target_PC']==start,'Existing native HI reference provenance')
  need(pair(hi,hi+4,10)==start,'Actual readonly argument source');w=word(region['length_PC']);need(len(ins[region['length_PC']])==2 and w&0xe003==0x4001 and(w>>7)&31==12 and sx((((w>>12)&1)<<5)|((w>>2)&31),6)==n,'Actual A2 constant length')
  need(ops[hi-2]['opcode']=='mv a1, s5'and word(region['call_PC'])==0x9782,'Original A1 argument and JALR through A5');load=region['window_start']+(4 if start==0x1a600 else 0);need(fields(load)==(3,15,2,22,region['slot_offset']),'Actual original indirect function load')
  need(region['actual_next_byte_is_NUL']==(fw[start-0x8000+n]==0),'Retained next-byte observation without guessing a C string extent')
  facts.append(dict(name=region['name'],start=start,end=start+n,bytes=n,length_PC=region['length_PC'],HI_PC=hi,LO_PC=hi+4,call_PC=region['call_PC'],callee_pointer_load_PC=load,callee_pointer_offset=region['slot_offset'],actual_source_register='a0',actual_length_register='a2',selected_argument_window_only=True,original_declaration_extent_proved=False,installed_callee_read_contract_proved=False))
 need(word(0x11a4c)==0x000409b7 and fields(0x11a68)==(0x13,22,0,19,60)and word(0x11d62)==0x00040b37,'Two original nominal resident-slot materialization forms')
 sdk=ev['cached_SDK_reference'];need(sdk['default_base']+sdk['table_offset']+sdk['memcmp_index']*sdk['stride']==sdk['memcmp_slot']==0x4003c and sdk['SDK_declares_BOOL_TRUE_same']and not sdk['installed_ROM_or_ABI_proved'],'Candidate SDK slot/polarity;not installed semantics')
 need(word(0x1236a)==0x000407b7 and fields(0x1236e)==(3,15,2,15,432)and word(0x12382)==0x9782,'Actual candidate central-start slot call');need(pair(0x12372,0x12376,12)==0x1a674 and pair(0x1237a,0x1237e,11)==0x1a668,'Actual two candidate callback-record arguments')
 need(sdk['default_base']+sdk['table_offset']+sdk['central_start_index']*sdk['stride']==0x401b0 and sdk['bond_callbacks_pointer_fields']==sdk['central_callbacks_pointer_fields']==3 and sdk['RV32_pointer_bytes']==4,'Candidate SDK three-pointer record sizes')
 callback_tables=[];missing=[]
 for candidate in ev['unprovided_candidate_callback_tables']:
  slots=[]
  for descriptor in candidate['slots']:
   offset=descriptor['offset'];pc=int.from_bytes(fw[candidate['base']-0x8000+offset:candidate['base']-0x8000+offset+4],'little');owners=[v for v in plan['owners']if v['info']==18 and v['original_PC']<=pc<v['original_PC']+v['bytes']]if pc else[]
   need(pc==descriptor['original_target']and bool(owners)==descriptor['selected_CODE_covered'],'Actual pointer bytes and selected CODE coverage')
   if pc and not owners:missing.append(pc)
   slots.append(descriptor)
  callback_tables.append(dict(base=candidate['base'],candidate_bytes=12,slots=slots,source_DATA_provided=False,installed_SDK_layout_proved=False))
 need(sorted(set(missing))==ev['unprovided_callback_CODE_targets']==[0x10c36,0x10d2e,0x10d30,0x11544],'Four actual candidate callback target gaps remain visible')
 return dict(passed=True,schema='TSL9-callback-prefix-audit-v1',captured_original_instructions=104,CODE_windows=16,selected_CODE_bytes=total,selected_instructions=len(ins),readonly_argument_windows=facts,selected_argument_bytes=109,positive_DATA_owners=14,nominal_candidate_compare_slot=0x4003c,SDK_candidate_TRUE_same=True,original_branch_polarity_preserved=True,full_C_string_or_NUL_extent_claimed=False,nonterminated_selected_window_count=sum(not v['actual_next_byte_is_NUL']for v in regions),installed_ROM_or_ABI_proved=False,all_indirect_entry_or_read_footprints_proved=False,unprovided_candidate_callback_tables=callback_tables,newly_identified_callback_CODE_gaps=sorted(set(missing)),callback_tables_provided=False,source_curated=False,accepted_component_updated=False,coverage_added=0,accepted_UND_unchanged=22,accepted_coverage_percent_unchanged=88.89,physical_feature_names_proved=False,firmware_BIN_generated=False,firmware_ready=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full',action='store_true');a=p.parse_args()
 try:
  r=audit();print(json.dumps(r if a.full else {k:r[k]for k in ['passed','captured_original_instructions','selected_argument_bytes','positive_DATA_owners','newly_identified_callback_CODE_gaps','installed_ROM_or_ABI_proved','coverage_added','firmware_ready']}))
 except Exception as e:
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=str(e).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));raise SystemExit(1)
