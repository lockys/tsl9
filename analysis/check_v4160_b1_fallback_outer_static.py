"""Offline outer ID6 resource-prefix and selected large-pool preservation.

Original bytes/CFG and closed allocation geometry/record interval certificates.
No target execution/emulation or mutable heap/list/RAM/provider/MMIO model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_retry_static as previous
import check_v4160_outer_id6_initializer_static as outer
import check_v4160_timer_provider_closure_static as closure

init,sparse,check=previous.init,previous.sparse,previous.check
layout=previous.layout
OUT=Path(__file__).with_name('v4160-b1-fallback-outer-static.json')
CORE_PATH=(0,2,4,8,10,14,18,22,24,38,42,44,46,48,50,52,56,100,104,108,68,72,76,110,112,204,206,76,110,112,114,116,120,124,128,130,134,138,142,146,150,152,154,156,158,162,166,168,170,174,176,178,180,182,186,188,192,196,198,200,202)


def separated(a,z,b,w=4):return a+z<=b or b+w<=a


def geometry():
 rows={}
 for r in layout.facts():
  b=r['input_byte'];q=(b&3)+(b>>2)
  if q==0:continue
  cap=r['N0'];R0=r['rounded_payload'];M=layout.P+R0;size=layout.E-M-8;request=60*q;P=M+8;N=P+request
  check(cap==14+3*q and 1<=q<=66 and 60<=request<=3960 and request%4==0 and request>52,'fallbackouter large request/capacity domain')
  check(layout.B+8+R0==M and layout.T+4*cap<=M and size-request>8 and N+8<=layout.E,'fallbackouter two-stage split/table geometry')
  record_intervals=[(P+60*j+off,z) for j in range(q) for off,z in ((2,2),(4,1),(44,4))]
  check(all(P<=a<a+z<=P+request for a,z in record_intervals),'fallbackouter all per-record stores inside owned payload')
  check(size-request-8>=0 and N+8+(size-request-8)==layout.E,'fallbackouter new remainder exactly reaches sentinel')
  row=dict(q=q,capacity=cap,first_table_payload_R=R0,first_allocated_header=layout.B,required_B_tag=1,required_B_next=M,free_header=M,free_size=size,request=request,rounded=request,tag=0x9001,payload=P,new_remainder_header=N,new_remainder_size=size-request-8,account_delta=-(request+8),record_count=q,record_stride=60,owned_table=[layout.T,layout.T+4*cap],header_intervals=[(M,8),(N,8)],payload_interval=[P,P+request])
  check(q not in rows or rows[q]==row,'fallbackouter duplicate packed-byte geometry agreement');rows[q]=row
 check(set(rows)==set(range(1,67)),'fallbackouter all66 nonzero count cases')
 return list(rows.values())


def core_path(data,index):
 n,e=closure.core_body(init.binding.take(data,closure.core.DETAILS[index][0],208),index);pc=closure.core.ENTRY
 for a,z in zip(CORE_PATH,CORE_PATH[1:]):check(pc+z in e[pc+a],'fallbackouter finite graph walk edge')
 check(e[pc+CORE_PATH[-1]]==[] and CORE_PATH.count(76)==2 and CORE_PATH.count(112)==2,'fallbackouter exactly skip allocated B then fit M')
 check(all(n[pc+o]['op'] not in ('jal','jalr','call_indirect') for o in CORE_PATH) and 84 not in CORE_PATH and 96 not in CORE_PATH,'fallbackouter selected core no failure-slot load/callback')
 return dict(runtime_entry=pc,source=closure.core.DETAILS[index][0],bytes=208,sha256=sha256(init.binding.take(data,closure.core.DETAILS[index][0],208)).hexdigest(),graph_walk_offsets=list(CORE_PATH),repeated_CFG_nodes_are_a_finite_certificate_not_target_execution=True)


def profile(data,hexraw,index,parent,op,rows):
 G=0x20003000;delta=80*index;ip,rp=outer.STARTS[index];F=G+492+delta;D=G+940+delta;ctx=F-80;slot=parent['fallback_slot']
 check(parent['end_cut']['target']==ip and parent['end_cut']['fallback']==0 and [parent['end_cut'][k] for k in ('A0','A1','A2')]==[6,0xffffffff,7] and parent['end_cut']['count']==7,'fallbackouter prior zero/ID6/count7 entry join')
 b=op['bodies']['resources'];n={v['pc']:v for v in b['instructions']};ir=op['bodies']['initializer'];inn={v['pc']:v for v in ir['instructions']}
 raw=init.binding.take(data,rp,160);check((int.from_bytes(raw[4:8],'little')>>12&7)==4,'fallbackouter packed source unsigned byte encoding')
 check([int(c['pc'],16)-rp for c in b['calls']]==[58,82] and [int(c['pc'],16)-rp for c in b['tail_exits']]==[128],'fallbackouter allocation/fill/tail call offsets')
 check(n[rp+74]['imm']==852+delta and n[rp+86]['imm']==852+delta and n[rp+90]['imm']==8,'fallbackouter fresh pool/count reload operands')
 check([int(c['pc'],16)-ip for c in ir['calls']][:2]==[94,126],'fallbackouter resource return and next fill cut')
 protected=[('fallback',slot,4),('config64_clock_source',F,96),('role_object',0x200033b8+delta,296),('count',ctx+1,1),('capacity',ctx+2,1),('gate',ctx+3,1),('table_pointer',ctx+40,4),('entries0_to6',layout.T,28),('timer_head',ctx+76,4),('nominal_timer_node',layout.A+8,16),('small_header',layout.A,8),('small_remainder',layout.A+24,8),('first_task',0x20004184,1),('second_task',0x200040a6,1)]
 fixed=list(op['prefix_fixed_writes'])+[dict(address=hex(D+9),bytes=1,value='fresh_byte&3'),dict(address=hex(D+8),bytes=1,value='q'),dict(address=hex(G+788+delta),bytes=1,value=6)]
 check(len(fixed)==12,'fallbackouter nine prefix/two count/one saved ID stores')
 extra=[dict(role='control',address=0x4002420c,bytes=4),dict(role='core_account',address=ctx+6,bytes=2),dict(role='pool_pointer',address=G+852+delta,bytes=4),dict(role='resource_tail_fill48',address=G+856+delta,bytes=48)]
 def exclusion(a,z,name):
  check(0<=a<a+z<=1<<32,'fallbackouter nonwrapping '+name)
  for k,p,w in protected:check(separated(a,z,p,w),'fallbackouter '+name+' excludes '+k)
 for v in fixed:exclusion(int(v['address'],16),v['bytes'],'fixed')
 for v in extra:exclusion(v['address'],v['bytes'],v['role'])
 for r in rows:
  for a,z in r['header_intervals']+[(r['payload'],r['request'])]:
   exclusion(a,z,'owned resource range')
   check(separated(a,z,layout.B,8) and separated(a,z,r['owned_table'][0],r['owned_table'][1]-r['owned_table'][0]),'fallbackouter dynamic effects exclude B header/actual full table')
  check(layout.H<=r['free_header']<r['payload']<r['new_remainder_header']<layout.E,'fallbackouter resource inside nominal owned arena')
 cp=core_path(data,index)
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];fs=int(fc['source'],16)+0x2000039c-int(fc['destination'],16)
 fill=outer.previous.source.fill_contract(init.binding.take(data,fs,46));check(fill['encoded_GPR_writes']==[10,14,15],'fallbackouter fill preserves resource S/SP/RA')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 for name,a,z in [('initializer',ip,386),('resources',rp,160),('core_firstcopy_source',cp['source'],208),('fill_firstcopy_source',fs,46)]:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackouter strictHEX '+name);guards.append(dict(role=name,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 # Static own-frame save locations are derived relative to initializer entry S.
 check(inn[ip+72]['rs2']==10 and inn[ip+72]['imm']==12 and inn[ip+98]['rd']==10 and inn[ip+108]['rs2']==10,'fallbackouter saved ID reload/publication not allocator reply')
 check(op['zero_resource_case']['next_cut_before_fill']['pc']==hex(ip+126),'fallbackouter next call boundary')
 return dict(label=parent['label'],fallback_slot=slot,strictHEX_guards=guards,fixed_store_envelopes=fixed,nonzero_additional_fixed_envelopes=extra,core_skip_then_fit_certificate=cp,
  zero_resource_case=dict(fresh_F21=0,low2=0,q=0,resource_RET=rp+158,allocator_or_fill_called=False,old_pool_pointer_or_tail_table_cleared=False,normal_return_fallback=0),
  nonzero_resource_case=dict(fresh_byte_domain=[1,255],q_domain=[1,66],request_formula='60*q',tag=0x9001,normal_return_fallback=0,capacity_relation='retained first-table capacityN0=14+3*q for this nominal two-allocation family',large_head_is_allocated_B_not_free_remainder=True,
   geometry_cases='shared nonzero_geometry_cases',required_reloads=['fresh count after allocation and after fill == entry q','fresh pool pointer after fill == successful owned payload P'],record_writes=[dict(offset=2,bytes=2,value=65535),dict(offset=4,bytes=1,value=0),dict(offset=44,bytes=4,value=0)],tail_fill=dict(address=G+856+delta,bytes=48,resource_frame_released_before_tail=True),null_allocator_result_path_included=False),
  APP14_case=next(r for r in rows if r['q']==5),
  end_cut=dict(pc=ip+126,target=0x2000039c,A0=G+800+delta,A1=0,A2=48,fallback=0,saved_ID_byte_address=G+788+delta,saved_ID_byte_value=6,gate=5,count=7,initializer48Bframe_still_live=True),
  frames=dict(initializer=48,resources=16,core_child=16,resource_subgraph_peak_relative_initializer_entry=80,saved_ID6_relative_entry=-36,resource_RA_relative_entry=-52,valid_ownership_nonalias_and_savedwords_premise=True),
  required_premises=['all prior selected gatezero/retry ordinary-return/provider/source/timer/metadata premises remain; actual core/fill/ISA/firstcopy bytes/mappings preserved','zero resource case fresh F21=0 is separate from nonzero geometry and actualbootreachability notproved; no stale-pool cleanup inferred','nonzero case original nominal H/L/owned arena plus matching current largeheadB/tag1/sizeR0/nextM, freeM/tag0/nextE/sizeE-M-8, sentinel/account/frame/global facts; not an assertion these headers actually survived priorcalls','nonzero fresh packed source b has q=(b&3)+(b>>2), prior table capacity14+3*q, and same q at both later count loads; actual old/new header/payload ranges valid owned/stable/disjoint code/frames/protecteddata','successful core returns P=M+8; resource pointer store/fresh reload/fill P,0,60*q and record stores preserve D counts/headers/context/neededS/SP/RA; final fixed fill48 completesnormally','normal accesses/calls and valid nonwrapping nonalias frames/heap/globals/table; no adverse MMIO/FENCE/IRQ/DMA/reentry/externalwriter effects; numerical separation not physical side-effect proof','no allocationfailure/null-payload case admitted: no local result nullguard before fill/reloadedpool/recordloop, so fallback0 alone does not establish safe record destinations'],
  boundary='before parent next fill48 executes; no remaining parent allocators/getters/records/tail/nextregistration or fullretention-release proof',actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);op=outer.derive(image,carriers,header,coverage);rows=geometry()
 return dict(schema='TSL9-fallback-outer-ID6-zero-resource-and-successful-large-pool-v1',APP_sha256=sha256(image).hexdigest(),nonzero_geometry_cases=rows,profiles=[profile(d,h,i,parent['profiles'][i],op['profiles'][i],rows) for i,(d,h) in enumerate(zip(carriers,hexes))],
  source_composition='entryID6/fallback0 -> nine parent fixed stores -> zero resource directRET OR nominal two-header successful allocation/fill/records/tailfill -> savedID6 publication -> cut before parentfill48',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['actual resource source/count/pool/header preservation, nullfailure and other heap domains','parentfill/remainingallocators/getters/records/tail and laterouterregistrationIDs','actualprovider/ownership/physicaleffects/IRQprogress/fullconsumption-retention-release lifetime'])


def tests(carriers):
 outer.tests(carriers);rows=geometry();check(len(rows)==66,'fallbackouter 66successful geometry cases')
 for i,data in enumerate(carriers):core_path(data,i)
 for b in range(256):
  q=(b&3)+(b>>2);check((q==0)==(b==0),'fallbackouter all256 zero/nonzero byte cases')
  if q:check(rows[q-1]['q']==q and rows[q-1]['request']==60*q,'fallbackouter packed-byte geometry selection')
 print('PASS:356 original initializer/resource mutations rejected;256 packed bytes/66 split-record geometries;finite B-skip/M-fit graph certificate')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackouter exactledger')
 print('PASS:conditional outerID6 zero-resource OR successful large-pool path;fallback0 toparentfill48 cut;66geometrycases/strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;nullfailure/actualheaders/binding/remainingparent/full lifetime UNPROVED')


if __name__=='__main__':main()
