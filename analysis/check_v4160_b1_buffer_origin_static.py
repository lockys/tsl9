"""Offline packet-buffer provenance/extent composition from existing full bodies.
Original operands/hashes, affine sources and scalar/interval certificates only.
No target execution/emulation, allocator/packet/provider or mutable state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_completion_static as previous
import check_v4160_config_buffer_source_static as source
import check_v4160_fallback_initialization_static as fallback
import check_v4160_heap_bootstrap_static as heap
import check_v4160_radio_config_chain_static as radio
import check_v4160_b1_binding_order_static as bindingorder
import check_v4160_b1_request_leaves_static as cleanup
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-b1-buffer-origin-static.json')
H,L=0x2000418c,0x7000


def app_body(image):
 raw=image[source.APP_PC-0x8000:source.APP_PC-0x8000+source.APP_SIZE];b=source.app_contract(raw)
 operand,geometry=heap.app_operands(image);n={d['pc']:d for d in b['instructions']}
 check(operand['H']==hex(H) and operand['L']==hex(L),'bufferorigin APP nominalH/L')
 check(n[0x19a42]['imm']==16 and n[0x19a42]['rs2']==15 and n[0x19a46]['imm']==20 and n[0x19a46]['width']==2,'bufferorigin descriptorword/halfword frame locations')
 check(n[0x19aea]['rs1']==2 and n[0x19aea]['imm']==16 and n[0x19aec]['op']=='call_indirect','bufferorigin liveframe toconfigAPI')
 return b,operand,geometry


def bootstrap_body(data,mem,index,config):
 walker,pc,reset,wh,digest,rh=heap.DETAILS[index];meta=config-80;raw=init.binding.take(data,pc,112);n=heap.decode(raw,pc)
 check(sparse.captured(mem,pc,112)==raw and sha256(raw).hexdigest()==digest,'bufferorigin bootstrap fullstrictHEX/hash')
 heap.guard_body(n,pc,heap.bootstrap_spec(pc,walker,config,meta),'bootstrap')
 edges,cycles=init.timer.cfg(n,pc);check(not cycles and len(n)==36,'bufferorigin bootstrap completeDAG')
 return dict(start=pc,bytes=112,sha256=digest,instructions=list(n.values()),CFG=edges,opaque_walker_call=walker,actual_heap_state_constructed=False)


def profile(image,data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());detail=fallback.DETAILS[index];pc,dest=detail[2],detail[5]
 check(dest==0x200031ec+80*index,'bufferorigin configcopy base')
 raw,n,edges,defaults=fallback.config_contract(data,pc,dest,detail[9],detail[10])
 check(sparse.captured(mem,pc,228)==raw and sha256(raw).hexdigest()==detail[-1],'bufferorigin completeconfig strictHEX/hash')
 check(init.binding.word(data,0x400a4)==pc and sparse.captured(mem,0x400a4,4)==init.binding.take(data,0x400a4,4),'bufferorigin configAPI originaltable')
 check(all(d['destination_field']!=0 for d in defaults),'bufferorigin localdefaultstores excludeconfigword0')
 cfg=dict(start=pc,bytes=228,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,defaults=defaults)
 pubpc=radio.DETAILS[index][0][0];pubraw=init.binding.take(data,pubpc,118)
 check(sparse.captured(mem,pubpc,118)==pubraw,'bufferorigin fullRFpublisher strictHEX');pub=radio.body(pubraw,'parent',index);pn={d['pc']-pubpc:d for d in pub['instructions']}
 S=0x20003514+80*index;C=0x20003560+80*index
 check(pn[84]['imm']+pn[88]['imm']==dest and pn[92]['rs2']==14 and pn[92]['imm']==36 and pn[94]['rd']==14 and pn[94]['rs1']==14 and pn[94]['imm']==272 and pn[98]['rs2']==14 and pn[98]['imm']==32,'bufferorigin freshconfigword toS36/S32 exactoperands')
 # Separate C4 source/free and actual completion load, never substitute slot identity for pointer equality.
 rfpc=bindingorder.STARTS[index][0];rfraw=init.binding.take(data,rfpc,318)
 check(sparse.captured(mem,rfpc,318)==rfraw,'bufferorigin RFconfig strictHEX');rf=bindingorder.body(rfraw,'config',index);rn={d['pc']-rfpc:d for d in rf['instructions']}
 check(rn[0xb2]['rs1']==rn[0xca]['rs1']==9 and rn[0xb2]['imm']==rn[0xca]['imm']==4 and rn[0xca]['rs2']==10 and rn[0xc0]['imm']==2 and rn[0xbc]['imm']==73,'bufferorigin separateC4 allocatorreply publication')
 innerpc=cleanup.STARTS[index][0];innerraw=init.binding.take(data,innerpc,148)
 check(sparse.captured(mem,innerpc,148)==innerraw,'bufferorigin cleanup strictHEX');inner=cleanup.body(innerraw,'inner',index);q={d['pc']-innerpc:d for d in inner['instructions']}
 check(q[0x20]['rd']==10 and q[0x20]['imm']==4 and q[0x2a]['rs1']==10 and inner['calls'][0]['target']==0x20000110 and q[0x3e]['imm']==4,'bufferorigin cleanup capturesC4/free/clear')
 cr=init.binding.take(data,previous.STARTS[index],430);check(sparse.captured(mem,previous.STARTS[index],430)==cr,'bufferorigin callback strictHEX');cb=previous.body(cr,index);cn={d['pc']-cb['start']:d for d in cb['instructions']}
 check(cn[0x5e]['imm']==cn[0x7c]['imm']==36 and cn[0x7c]['rd']==8 and cn[0xe6]['rs1']==8 and cn[0xe6]['imm']==19 and cn[0xe2]['target']==innerpc,'bufferorigin cachedS36 pointer usedaftercleanup')
 bootstrap=bootstrap_body(data,mem,index,dest)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];helpers={}
 for role,target,z,fn in (('copy',0x20000332,58,lambda b:previous.leaves.copier.body(b,'copy',0x20000332,18,init.binding.COPY_HASH)),('fill',0x2000039c,46,source.fill_contract)):
  src=int(first['source'],16)+target-int(first['destination'],16);hr=init.binding.take(data,src,z)
  check(sparse.captured(mem,src,z)==hr and target+z<=int(mapping['first_copy_end_exclusive'],16),'bufferorigin helper fullstrictHEX/affine source');helpers[role]=dict(source=src,target=target,body=fn(hr),actual_binding_proved=False)
 protected_configword=set(range(dest,dest+4));directfixed={dest+d['destination_field']+k for d in defaults for k in range(d['bytes'])}
 check(protected_configword.isdisjoint(directfixed),'bufferorigin defaults donotdirectly overwrite heapbase field')
 check(set(range(S+36,S+40)).isdisjoint(range(C+4,C+8)) and S+32!=S+36 and S+36+4<=C,'bufferorigin pointer slots separated notpointervalues')
 return dict(label=init.binding.PROFILES[index][0],reused_bodies=dict(config_initializer=cfg,RF_pointer_publisher=pub,bootstrap=bootstrap,RF_C4_config=rf,cleanup=inner,completion=cb),reused_helpers=helpers,
  config_destination=dest,packet_pointer_slot=S+36,transmit_pointer_slot=S+32,release_pointer_slot=C+4,
  conditional_nominal_pointer_values=dict(packet=H,transmit=H+272),
  source_contract=['APPstaticliteralH inconfigframeword0,not allocatorreply;acceptedmatching400a4copy64 toresidentconfig preservesword0 onlyunderargument/frame/copy/gate/optionalcallback/postcallee conditions',
   'RFpublisherfreshX=U32[residentconfig0] ->S36=X,S32=low32(X+272) beforethree nestedcalls/tail;laterfreshcompletionS36 maydiffer duecallees/writers',
   'bootstrap usesfreshconfigH/L,smallheadH+544,largeheadH+544+split,sentinelH+L-8;nominaltwo272byteprefixes aregeometry beforefirstheapheader,not newlyallocatedpacketbuffers/proveninitializedcontents'],
  lifetime_contract=['C4 isseparateconfigslot receiving(2+freshF29,73) allocatorreplyafteroldcapturedC4 release/clear;notpublishedHliteral. Distinctslots alone donotprove C4value !=S36value',
   'cleanuprequestsreleasefreshC4,completioncachedS36 inS0 priorcall;validallocation/disjointness/lifetime require currentownership/range/providers/writers proof',
   'conditionalvalidC4payload confinedto managedregion startingH+544 excludes reservedprefixH..H+544;no currentheap invariant,allocationhistory oractualC4rangeprovenhere',
   'packetminimum27 bytes fitsfirst272prefix onlyifactualmatchingstableX/H,validconfiguredextent andordinarydevice/sourcewrites preservecontents. Not an ingress-length orinitialization proof'],
  actual_pointer_values_extent_content_initialization_release_disjointness_or_complete_lifetime_proved=False)


def intervals():
 end=H+L;rx=(H,H+272);tx=(H+272,H+544);small=H+544;large=small+512;sentinel=end-8
 check((rx,tx,small,large,sentinel)==((0x2000418c,0x2000429c),(0x2000429c,0x200043ac),0x200043ac,0x200045ac,0x2000b184),'bufferorigin nominalprefix geometry')
 check(H+27<=rx[1] and H+15<=rx[1] and H+9<=rx[1] and tx[0]+4<=tx[1] and rx[1]==tx[0] and tx[1]==small<large<sentinel<end<2**32,'bufferorigin requiredaccesses fitnumericprefix')
 for off,size in ((2,1),(3,6),(9,6),(15,4),(19,3),(22,4),(26,1)):check(0<=off and off+size<=272,'bufferorigin callback footprint interval')
 # Conditional interval exclusion, not an allocator or ownership simulator.
 cases=0
 for baseoff in range(544,L-8):
  check(H+baseoff>=rx[1] and H+baseoff>=tx[1],'bufferorigin managedaddress excludesprefix');cases+=1
 check(cases==28120,'bufferorigin regionaddress census')
 for size in range(2,258):check(size<=0x10001 and 2+size>=4,'bufferorigin C4request finitebyte envelope')
 return dict(H=H,L=L,configured_interval=[H,end],nominal_packet_prefix=list(rx),nominal_transmit_prefix=list(tx),small_header=small,large_header=large,sentinel=sentinel,
  required_callback_extent=27,reserved_prefix_bytes=544,managed_address_interval_cases=cases,
  C4_request='A0=2+freshU8[F29],range2..257;A1=73;separatefromHliteral',C4_nominal_APP_preserved_default_request=[253,73],
  nominal_geometry_is_not_runtime_extent_initialization_ownership_or_heap_invariant=True,target_execution_or_emulation=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes);app,operand,geometry=app_body(image)
 return dict(schema='TSL9-B1-packet-buffer-origin-interval-composition-static-v1',APP_sha256=sha256(image).hexdigest(),reused_APP_builder=app,reused_APP_operand_subrange=operand,nominal_heap_geometry=geometry,
  profiles=[profile(image,d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],intervals=intervals(),
  new_original_body_bytes=0,new_original_body_instructions=0,revalidated_unique_body_bytes=3224,APP_operand16_already_inside_builder308=True,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['actualP/S36 writers andbyte-contentproducer/ingressbounds','currentC4 ownership/allocationrange andpreservationthroughcleanup','actualinstalledproviders/callbackdispatch vsouterclear/order/pollprogress/fullpointerlifetimes'])


def tests(image,carriers):
 count=0
 # Original operand mutations exercise reused fullbody guards, without target execution.
 ar=image[source.APP_PC-0x8000:source.APP_PC-0x8000+source.APP_SIZE]
 fixtures=[(ar,source.APP_PC,source.app_contract,[0x19a3a-source.APP_PC,0x19a3e-source.APP_PC,0x19a42-source.APP_PC,0x19a46-source.APP_PC,0x19aea-source.APP_PC])]
 for i,data in enumerate(carriers):
  pc=radio.DETAILS[i][0][0];fixtures.append((init.binding.take(data,pc,118),pc,lambda r,i=i:radio.body(r,'parent',i),[84,88,92,94,98]))
  pc=bindingorder.STARTS[i][0];fixtures.append((init.binding.take(data,pc,318),pc,lambda r,i=i:bindingorder.body(r,'config',i),[0xaa,0xb2,0xba,0xbc,0xc0,0xc6,0xca]))
  pc=cleanup.STARTS[i][0];fixtures.append((init.binding.take(data,pc,148),pc,lambda r,i=i:cleanup.body(r,'inner',i),[0x20,0x2a,0x30,0x3e]))
 for raw,pc,fn,offsets in fixtures:
  nodes=decode(raw,pc)
  for o in offsets:
   z=nodes[pc+o]['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:fn(bad)
   except RuntimeError:pass
   else:raise RuntimeError('bufferorigin sourceoperand mutation escaped')
   count+=1
 check(count==37,'bufferorigin mutationcensus');intervals()
 print('PASS:37 original source/publication/C4/free operand mutations rejected;28120 interval cases;source-vs-allocation distinction')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
 check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,tail,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
  check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
 coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers)
 encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'bufferorigin exactledger replay')
 print('PASS:3224B revalidated fullbodies;strictHEX;APPconfig ->S36/S32 andC4/release/extent joins;0newbodybytes;exactledger')
 print('PASS:NO target execution/emulation;actualcontents/ownership/installedbinding/lifetime/pollprogress UNPROVED')


if __name__=='__main__':main()
