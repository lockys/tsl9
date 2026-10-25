#!/usr/bin/env python3
"""Read-only evidence audit; range arithmetic is not target/model execution."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(v,label):
 if not v:raise ValueError(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def audit():
 s=json.loads((HERE/'spec-v1.json').read_bytes());need(sha(ROOT/s['evidence'])==s['evidence_sha256'],'Exact bounded original evidence');ev=json.loads((ROOT/s['evidence']).read_bytes());fw=(ROOT/ev['firmware']).read_bytes()
 need(len(fw)==76800 and sha(ROOT/ev['firmware'])==ev['firmware_sha256'],'Original official BIN')
 need(all(sha(ROOT/p)==h for p,h in ev['inputs'].items()),'Exact selected source/layout identities')
 b=runpy.run_path(str(ROOT/ev['layout_builder']),run_name='grid_layout_library');need(all(sha(ROOT/p)==h for p,h in b['K']['pins'].items()),'Transitive layout pins')
 need(sha(ROOT/b['K']['reader'])==b['K']['reader_sha256'],'Pinned ELF reader')
 parent=b['E'](b['source']('c'));plan=b['derive'](parent);e=b['E'](ROOT/ev['original_layout']);instructions={};total=0
 for owner in plan['owners']:
  if owner['info']!=18:continue
  raw=e.data(owner['section'])[owner['section_offset']:owner['section_offset']+owner['bytes']];pc=owner['original_PC'];need(raw==fw[pc-0x8000:pc-0x8000+owner['bytes']],'Every selected CODE byte');total+=len(raw);at=0
  while at<len(raw):
   size=4 if raw[at]&3==3 else 2;need(at+size<=len(raw)and pc+at not in instructions,'Whole unique instruction');instructions[pc+at]=raw[at:at+size];at+=size
 need(total==64544 and len(instructions)==21938,'Exact selected CODE scope')
 ops={}
 for w in ev['CODE_windows']:
  at=w['start']
  for op in w['operations']:
   need(op['addr']==at and bytes.fromhex(op['bytes'])==instructions[at]and op['size']==len(instructions[at])and at not in ops,'Captured r2 bytes and original boundaries');ops[at]=op;at+=op['size']
  need(at==w['end'],'Whole original disassembly window')
 need(len(ops)==86,'All86 fresh captured instructions')
 def operation(pc,text):need(ops[pc]['opcode']==text,'Exact original operation at '+hex(pc))
 def pair(hi,lo,reg):
  a=int.from_bytes(instructions[hi],'little');z=int.from_bytes(instructions[lo],'little');need(a&127==0x17 and(a>>7)&31==reg and z&0x707f==0x13 and(z>>7)&31==(z>>15)&31==reg,'Actual AUIPC/ADDI operands');return(hi+(a&0xfffff000)+sx(z>>20,12))&0xffffffff
 expected={0xcafa:'lbu a5, 4(s0)',0xcafe:'addi a3, a5, 1',0xcb02:'andi a3, a3, 15',0xcb04:'andi a5, a5, -16',0xcb06:'or a5, a5, a3',0xcb08:'sb a5, 4(s0)',0xcb0c:'andi a4, a5, 192',0xcb10:'andi a2, a5, 48',0xcb14:'bnez a4, 0xcc3e',0xcb18:'beqz a2, 0xcb1c',0xcb1a:'li a4, 10',0xcb1c:'lbu a5, 5(s0)',0xcb20:'andi a5, a5, 15',0xcb22:'add a4, a4, a5',0xcb24:'slli a4, a4, 0x4',0xcb2e:'add a5, a5, a4',0xcb30:'add a5, a5, a3',0xcb32:'lbu a5, 0(a5)',0xcb36:'j 0xcc38',0xcc3e:'li a4, 0',0xcc40:'beqz a2, 0xcc44',0xcc42:'li a4, 3',0xcc44:'srli a5, a5, 0x6',0xcc46:'add a5, a5, a4',0xcc48:'slli a5, a5, 0x4',0xcc52:'j 0xcb2e',0xcf06:'auipc a4, 0x1ffff',0xcf0a:'lbu a4, 51(a4)',0xcf1e:'li a3, 5',0xcf20:'bne a4, a3, 0xcf7c',0xcf3e:'slli a4, a4, 0x4',0xcf44:'andi a3, a3, 15',0xcf56:'add a4, a4, a5',0xcf58:'add a4, a4, a3',0xcf5a:'lbu a5, 0(a4)',0xcf7c:'andi a3, a4, 7',0xcf80:'slli a3, a3, 0x4',0xcf86:'or a5, a5, a3',0xcf88:'j 0xcf36',0xcf66:'li a2, 3',0xcf6c:'rem a3, a3, a2',0xcf74:'sb a3, -54(a2)'}
 for pc,text in expected.items():operation(pc,text)
 need([pair(a,z,r)for a,z,r in [(0xcb26,0xcb2a,15),(0xcc4a,0xcc4e,14),(0xcf4e,0xcf52,15)]]==[0x19ed8,0x1a018,0x1a078],'Three actual DATA literals')
 decoder=b['B']['decode_control'];direct=[]
 for pc,raw in sorted(instructions.items()):
  t=decoder(raw,pc)
  if t is not None:direct.append(dict(PC=pc,kind=t[0],target_PC=t[1]))
 incoming=[d for d in direct if any(w['start']<d['target_PC']<w['end']for w in ev['CODE_windows'])]
 need(incoming==ev['selected_incoming_transfers']and len(direct)==ev['selected_direct_transfer_count'],'Fresh whole-selected-CODE direct target scan')
 need([(d['PC'],d['target_PC'])for d in direct if 0xcafa<d['target_PC']<0xcb38]==[(0xcb18,0xcb1c),(0xcc52,0xcb2e)],'Only expected selected direct entries into first guarded lookup')
 need([(d['PC'],d['target_PC'])for d in direct if 0xcc3e<=d['target_PC']<0xcc54]==[(0xcb14,0xcc3e),(0xcc40,0xcc44)],'Second lookup is selected only through the nonzero upper-bit branch')
 first=dict(base=0x19ed8,row_bias_choices=[0,10],fresh_low_nibble_min=0,fresh_low_nibble_max=15,column_min=0,column_max=15,row_stride=16,read_bytes=1,minimum_offset=0,maximum_offset=(10+15)*16+15,end=0x19ed8+(10+15)*16+16)
 second=dict(base=0x1a018,nonzero_top_two_bit_min=1,nonzero_top_two_bit_max=3,row_bias_choices=[0,3],column_min=0,column_max=15,row_stride=16,read_bytes=1,minimum_offset=16,maximum_offset=(3+3)*16+15,end=0x1a018+(3+3)*16+16)
 need(first['end']==0x1a078 and second['end']==0x1a088,'Conservative bounded window ends')
 need(s['owner']['start']==0x19ed8 and s['owner']['end']==0x1a088 and s['owner']['bytes']==432,'One overlapping-envelope union,not guessed declarations')
 need(not any(s['owner']['start']<o['original_PC']+o['bytes']and o['original_PC']<s['owner']['end']for o in plan['owners']),'No accepted CODE/DATA overlap')
 need([(d['pool_offset'],d['size'])for d in s['labels']]==[(0,0),(320,0)],'Two genuinely backed interior DATA labels')
 third=dict(base=0x1a078,index_load_PC=0xcf0a,index_address=(0xcf06+0x1ffff000+51)&0xffffffff,index_bits=8,byte_only_index_maximum=255,column_maximum=15,row_stride=16,syntactic_envelope_end=0x1a078+255*16+16,image_end=0x1ac00,mask_PC=0xcf7c,mask_destination='a3',actual_scaled_index_register='a4',mask_clamps_actual_index=False,rem_destination='a3',global_index_bound_proved=False,source_DATA_provided=False)
 need(third['index_address']==0x2000bf39 and third['syntactic_envelope_end']==0x1b078,'Independent actual row byte and syntactic envelope')
 return dict(passed=True,schema='TSL9-grid-read-windows-audit-v1',selected_CODE_bytes=total,selected_instructions=len(instructions),captured_instructions=len(ops),first_lookup=first,second_lookup=second,third_lookup=third,pool_bytes=432,pool_start=0x19ed8,pool_end=0x1a088,DATA_label_offsets=[0,320],selected_direct_guard_bypasses=0,all_indirect_entries_or_async_paths_proved=False,global_state_bounds_proved=False,original_declared_extents_proved=False,source_manifest_updated=False,accepted_component_updated=False,coverage_added=0,firmware_BIN_generated=False,firmware_ready=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full',action='store_true');a=p.parse_args()
 try:
  result=audit();print(json.dumps(result if a.full else {k:result[k]for k in ['passed','captured_instructions','pool_bytes','selected_direct_guard_bypasses','global_state_bounds_proved','coverage_added','firmware_ready']}))
 except Exception as e:
  print(json.dumps(dict(passed=False,reason=str(e).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));raise SystemExit(1)
