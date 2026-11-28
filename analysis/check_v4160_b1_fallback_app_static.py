"""Fallback preservation through APP return and first callback registration.

Immutable original-byte/CFG/operand and closed interval/scalar certificates.
No target execution, emulation, or mutable RAM/heap/MMIO/provider model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_post_static as previous
import check_v4160_first_registration_chain_static as chain

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-fallback-app-static.json')


def app_bodies(image):
 def take(pc,z):return image[pc-0x8000:pc-0x8000+z]
 clock=chain.body(take(0x19106,30),'clock')
 tail=chain.body(take(0x19aee,40),'app_tail')
 builder=chain.source.app_contract(take(chain.source.APP_PC,chain.source.APP_SIZE))
 setup=chain.origin.window(take(0x8e88,40),'setup')
 wrapper=chain.app_source.body(take(0x19b16,64),'wrapper')
 sn={d['pc']:d for d in setup['instructions']};wn={d['pc']:d for d in wrapper['instructions']}
 check(sn[0x8ea8]['target']==int(builder['start'],16) and sn[0x8eac]['target']==int(wrapper['start'],16),'fallbackAPP setup builder/wrapper joins')
 check(sn[0x8eac]['pc']==sn[0x8ea8]['pc']+sn[0x8ea8]['size'],'fallbackAPP setup no intervening instruction')
 check(wrapper['calls'][0]['pc']=='0x19b2e' and wrapper['calls'][0]['target']=='fresh U32[40080] & ~1','fallbackAPP first registration cutoff')
 check(wn[0x19b26]['op']=='auipc' and wn[0x19b2a]['imm']==-458 and 0x19b26-458==0x1995c,'fallbackAPP callback address')
 check(wn[0x19b16]['imm']==-16,'fallbackAPP wrapper frame16')
 stores=[(p,d['rs1'],d['imm'],d['width'],d['rs2']) for p,d in wn.items() if p<0x19b30 and d['op']=='store']
 check(stores==[(0x19b18,2,4,4,9),(0x19b22,2,12,4,1),(0x19b24,2,8,4,8)],'fallbackAPP prefix only three saved-frame stores')
 tn={d['pc']:d for d in tail['instructions']};cn={d['pc']:d for d in clock['instructions']}
 check([d['pc'] for d in tail['instructions'] if d['op']=='store']==[0x19b08,0x19b0e],'fallbackAPP tail store census')
 check(not any(d.get('rd')==10 for p,d in tn.items() if p>0x19af8),'fallbackAPP tail forwards clock A0')
 check(cn[0x1910e]['op']=='or' and cn[0x1910e]['rs1']==10 and cn[0x1910e]['rs2']==15,'fallbackAPP clock OR source')
 return dict(clock=clock,tail=tail,builder=builder,setup=setup,wrapper=wrapper)


def profile(data,hexraw,index,parent,bodies):
 _,mem=sparse.inspect(hexraw,sparse.parser());reg=chain.registration;pc=reg.DETAILS[index][0]
 raw=init.binding.take(data,pc,48);leaf=reg.body(raw,index)
 check(sparse.captured(mem,pc,48)==raw,'fallbackAPP registration strictHEX')
 check(sparse.captured(mem,0x40080,4)==init.binding.take(data,0x40080,4),'fallbackAPP candidate40080 strictHEX')
 check(init.binding.word(data,0x40080)==pc,'fallbackAPP candidate registration mapping')
 slot=parent['fallback_slot'];ctx=int(leaf['context_base'],16);table=previous.layout.T
 check(slot==ctx+132 and parent['conditional_result']['initializer_reply']==0 and parent['conditional_result']['initializer_normal_return_fallback']==0,'fallbackAPP prior zero and metadata layout join')
 effects=[dict(role=r,address=a,bytes=z,value=v) for r,a,z,v in (
  ('clock_RMW',0x40021014,4,'fresh W | 64'),
  ('APP_late_store0',0xe000e104,4,0x80000000),('APP_late_store1',0xe000e108,4,1),
  ('registration_count',ctx+1,1,4),('registration_callback',table+12,4,0x1995c))]
 for e in effects:check(0<=e['address']<e['address']+e['bytes']<=1<<32 and previous.separated(e['address'],e['bytes'],slot),'fallbackAPP interval excludes fallback')
 rows=previous.footprint_cases()
 for row in rows:
  cap=row['capacity'];end=table+4*cap
  check(3<cap and table+16<=end<=row['first_payload'][1]<=row['remainder_header'],'fallbackAPP firstregistration inside preserved nominal table')
  check(previous.separated(table+12,4,slot) and previous.separated(ctx+1,1,slot),'fallbackAPP all67 firstregistration footprints')
 return dict(label=parent['label'],fallback_slot=slot,registration_entry=pc,registration_original_sha256=sha256(raw).hexdigest(),
  candidate_slot_40080=pc,actual_installed_binding_proved=False,
  own_projected_effects=effects,protected_saved_frame_requirements=['builder entry SP-96..SP, RA at SP+92/S0 at SP+88 must survive','wrapper prefix allocates16bytes, saves S1/RA/S0 at then-liveSP+4/+12/+8; frame must exclude fallback and prior live state'],
  first_registration=dict(fresh_count=3,fresh_capacity_domain=[14,212,3],fresh_table=table,callback=0x1995c,returned_old_count=3,stored_count=4,all67_nominal_footprints_exclude_fallback=True,callback_invoked=False),
  conditional_result=dict(initializer_reply=0,initializer_RET_fallback=0,APP_builder_RET=0x19b14,APP_builder_RET_fallback=0,APP_builder_reply='fresh W | 64, always nonzero',setup_wrapper_call=0x8eac,wrapper_registration_call=0x19b2e,cut_at_registration_return_link=0x19b30,fallback_at_cut=0,reply_at_cut=3),
  required_premises=['all preceding source/getter/post shortcut OR mismatch path conditions remain in force; prior initializer normalRET fallback0/reply0','matching APP original bytes/ISA and current candidate registration/provider40080; fresh count3/capacityN0/tableT and metadata preserved from selectedpost path','valid owned nonwrapping nonalias builder/wrapper frames and preserved SP/RA/S/GP/code/stack-save words at each boundary','normal MMIO/read/write/call/return completion; numerical MMIO interval exclusion is not a proof of physical mapping or side-effect exclusion','no adverse alias/IRQ/DMA/reentry/other writer between these boundaries; required fresh sampling order is conditional'],
  boundary='stops at19b30 before wrapper byte-save19b34, constructor19b56, fresh40074, tail40058/param774 or RF; not fullcross-event lifetime')


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);b=app_bodies(image)
 return dict(schema='TSL9-fallback-APP-return-first-registration-preservation-v1',APP_sha256=sha256(image).hexdigest(),
  original_APP_bodies=b,profiles=[profile(d,h,i,parent['profiles'][i],b) for i,(d,h) in enumerate(zip(carriers,hexes))],
  composition='prior conditional fallback0 at initializerRET -> APP19106 and fixed tail writes -> builderRET -> setup wrapper call/prefix -> matching first registration normalreturn19b30',
  clock_reply_certificate='for all32bit W=65536*h+l, (W|64)=65536*h+(l|64); bit6=1, hence nonzero; a register RMW observation, not an error/status classification',
  original_scope=dict(APP_builder_bytes=308,APP_tail_bytes=40,complete_clock_leaf_bytes=30,setup_window_bytes=40,wrapper_body_bytes=64,each_complete_registration_bytes=48,new_C_bytes=0),
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,
  remaining=['wrapper byte-save/constructor/callees/tail and RF/param774 preservation','actual installed mapping/provider and fresh metadata/ownership/physical side effects','other input/callback domains, external writers, IRQ/poll progress and full retention-consumption-release lifetime'])


def tests(image,carriers):
 count=0
 scopes=[(0x19106,30,lambda b:chain.body(b,'clock')),(0x19aee,40,lambda b:chain.body(b,'app_tail')),
  (0x19b16,64,lambda b:chain.app_source.body(b,'wrapper')),(0x8e88,40,lambda b:chain.origin.window(b,'setup'))]
 for pc,z,guard in scopes:
  raw=image[pc-0x8000:pc-0x8000+z]
  for p,d in chain.decode(raw,pc).items():
   o=p-pc;w=d['size'];bad=bytearray(raw);bad[o:o+w]=(int.from_bytes(bad[o:o+w],'little')^(4 if w==2 else 1<<20)).to_bytes(w,'little')
   try:guard(bad)
   except RuntimeError:pass
   else:raise RuntimeError('fallbackAPP APP mutationescaped')
   count+=1
 for i,data in enumerate(carriers):
  pc=chain.registration.DETAILS[i][0];raw=init.binding.take(data,pc,48)
  for p,d in chain.decode(raw,pc).items():
   o=p-pc;w=d['size'];bad=bytearray(raw);bad[o:o+w]=(int.from_bytes(bad[o:o+w],'little')^(4 if w==2 else 1<<20)).to_bytes(w,'little')
   try:chain.registration.body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('fallbackAPP registration mutationescaped')
   count+=1
 check(count==94,'fallbackAPP mutation census')
 for low in range(65536):check((low|64)&64==64 and 0<low|64<65536,'fallbackAPP low16 OR certificate')
 for high in range(65536):check((high<<16)&64==0 and ((high<<16)|64)==(high<<16)+64,'fallbackAPP disjoint high16 lanes')
 print('PASS:94 original APP/clock/setup/wrapper/registration mutations rejected; all 65536 low/high16 lane certificates')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackAPP exactledger')
 print('PASS:conditional fallback-zero preservation through APP RET and first registration19b30; 67capacity cases/profile; strictHEX/exactledger')
 print('PASS:NO target execution/emulation or mutabletargetmodel; installedbinding/physicaleffects/laterwrapper/full lifetime UNPROVED')


if __name__=='__main__':main()
