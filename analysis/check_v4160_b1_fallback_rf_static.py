"""Offline selected RF normal-return and following local helper preservation.

Immutable original byte/CFG/def-use and closed footprint/frame certificates.
No target execution/emulation or mutable RAM/MMIO/provider/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_role_static as previous
import check_v4160_b1_q_source_static as qsource
import check_v4160_b1_q_return_static as qreturn
import check_v4160_initializer_post_radio_static as post

init,sparse,check=previous.init,previous.sparse,previous.check
layout=previous.layout
OUT=Path(__file__).with_name('v4160-b1-fallback-rf-static.json')


def profile(data,hexraw,index,parent,pp):
 role=previous.role;d=role.DETAILS[index];G=0x20003000;delta=80*index;slot=parent['fallback_slot'];B=G+d['base'];F=G+d['ctx']+80;ctx=F-80;ip=d['initialize']
 pc=qsource.radio.DETAILS[index][0][0]
 check(parent['zero_branch']['RF_callee']==pc and parent['zero_branch']['cut_before_call']==ip+388 and parent['zero_branch']['fallback_at_cut']==0,'fallbackRF zero caller/callee/entry join')
 check(parent['zero_branch']['arguments']=={'A0':27,'A1':328,'A2':'8*(k+14)','A3':'8*(k+138)'},'fallbackRF actual current caller arguments')
 prefix=qsource.profile(data,hexraw,index);suffix=qreturn.profile(data,hexraw,index)
 effects=list(prefix['conditional_projected_write_intervals'])+list(suffix['projected_suffix_store_intervals'])
 raw=init.binding.take(data,pc,118);pn=qsource.radio.decode(raw,pc)
 early=[(a,v) for a,v in pn.items() if v['op']=='store' and v['rs1']!=2 and a<=pc+66]
 check([a-pc for a,v in early]==[4,12,28,40,52,66],'fallbackRF complete six early parent publications')
 for a,v in early:effects.append(dict(role='parent_early_publication',pc=a,address=G+v['imm'],bytes=v['width']))
 check(len(prefix['conditional_projected_write_intervals'])==96 and len(suffix['projected_suffix_store_intervals'])==131 and len(effects)==233,'fallbackRF 96prefix/131suffix/6early envelopes')
 protected=[('fallback',slot,4),('config64_and_clock_source',F,96),('role_object',B,296),('count',ctx+1,1),('capacity',ctx+2,1),('gate',ctx+3,1),('table_pointer',ctx+40,4),('owned_table',layout.T,4*212),('timer_head',G+previous.previous.timer.DETAILS[index][4],4),('nominal_timer_node',layout.A+8,16),('small_header',layout.A,8),('small_remainder_header',layout.A+24,8),('large_header',layout.B,8),('first_task',0x20004184,1),('second_task',0x200040a6,1)]
 for e in effects:
  a,z=e['address'],e['bytes'];check(0<=a<a+z<=1<<32,'fallbackRF nonwrapping projection')
  for name,b,w in protected:check(previous.previous.separated(a,z,b,w),'fallbackRF interval excludes '+name)
 check(prefix['publisher']['value']==0x40025000 and prefix['publisher']['address']==suffix['Q_slot']==G+1424+delta,'fallbackRF same invocation literal Q/capture join')
 check(suffix['RF_return_conditional']['Q_value']==0x40025000 and suffix['RF_return_conditional']['H7_after_tail']==0,'fallbackRF normal tail Q/state return joins')
 # The caller's 27 is not substituted for the RF helper's literal13.
 tp=qsource.previous.tail.DETAILS[index][0][2];tb=qsource.previous.tail.body(init.binding.take(data,tp,232),'tail',index);tn={v['pc']:v for v in tb['instructions']}
 check((pn[pc+80]['op'],pn[pc+80]['imm'],pn[pc+82]['imm'])==('li',1,7),'fallbackRF parent establishes state1')
 check((tn[tp+70]['op'],tn[tp+70]['rd'],tn[tp+70]['imm'])==('li',10,13),'fallbackRF tail establishes helper A0=13')
 check(pp['conditional_radio_return_link']==hex(ip+392) and int(pp['B'],16)==B and int(pp['F'],16)==F,'fallbackRF selected normal return to caller suffix')
 post_effects=list(pp['new_object_destination_extents'])+[dict(address=hex(0x4002420c),bytes=4)]
 check(len(post_effects)==7,'fallbackRF six following object extents plus helper control')
 for e in post_effects:
  a,z=int(e['address'],16),e['bytes']
  for name,b,w in protected:
   if name=='role_object':continue  # These are intentional writes inside B296.
   check(previous.previous.separated(a,z,b,w),'fallbackRF following helper excludes '+name)
 check(all(B<=int(e['address'],16) and int(e['address'],16)+e['bytes']<=B+296 for e in post_effects[:-1]),'fallbackRF all following data writes inside role object')
 nb=pp['bodies']['next_prefix'];np=int(nb['start'],16);nn={v['pc']:v for v in nb['instructions']}
 check(nn[np+10]['op']=='li' and nn[np+10]['rd']==12 and nn[np+10]['imm']==6,'fallbackRF next copy length6')
 check(12 not in pp['copy_provider']['encoded_GPR_writes'] and not any(v.get('rd')==12 for a,v in nn.items() if np+40<=a<np+46),'fallbackRF A2=6 survives matching copy and next prefix')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 for r,p,z in zip(post.ROLES,post.DETAILS[index][0],post.SIZES):
  b=init.binding.take(data,p,z);check(sparse.captured(mem,p,z)==b,'fallbackRF following helper strictHEX '+r);guards.append(dict(role=r,start=p,bytes=z,sha256=sha256(b).hexdigest()))
 for name in ('fill','copy'):
  h=suffix['matched_helpers'][name];b=init.binding.take(data,h['source'],h['bytes'])
  check(sparse.captured(mem,h['source'],h['bytes'])==b and pp[name+'_provider']['sha256']==h['sha256'],'fallbackRF following mapped helper strictHEX/identity '+name)
  guards.append(dict(role=name,source=h['source'],bytes=h['bytes'],sha256=h['sha256']))
 return dict(label=parent['label'],fallback_slot=slot,current_caller_arguments=parent['zero_branch']['arguments'],RF_entry=pc,
  RF_original_body_guards=dict(prefix=prefix['bodies'],suffix=suffix['selected_RF_return']),RF_effect_intervals=effects,
  protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],
  selected_RF_case=dict(parent_state_byte=G+1307+delta,parent_state_value=1,tail_helper_A0=13,Q_slot=suffix['Q_slot'],Q_value_at_capture_and_return=0x40025000,reply='fresh U32[400250d0] & f0ffffff',state_byte_after_return=0,fallback_after_return=0,caller_return_link=ip+392,
   branch_alternatives=['RFhelper Tlow2 zero OR nonzero with required state1','reset descriptor zero','large actual magic OR matching nonmagic leaf closure'],MMIO_payload_formulas_or_hardware_success_proved=False),
  following_local_helpers=dict(original_guards=guards,fill=pp['fill_request'],fill_reply=pp['conditional_fill_A0_return'],copy=pp['copy_request'],copy_ordered_pairs=pp['copy_ordered_byte_pairs'],effect_intervals=post_effects,preserved_sampled_object_bytes=pp['preserved_sampled_bytes'],initializer_frame_released_before_tail=True,new_frame_bytes=32),
  end_cut=dict(pc=int(pp['cut_before_next_call']['pc'],16),target=int(pp['cut_before_next_call']['target'],16),A0=0,A1=16383,A2=6,fallback=0,gate=5,count=6,initializer_return_to_gate_proved=False),
  required_premises=['previous selected gatezero caller/source/timer/metadata conditions remain; all candidate RF/helper/ISA/firstcopy code preserved, valid normal accesses/calls/polls','parent publications preserved until required fresh captures: Q40025000/T40024200/R40024100/descriptor0, state1 at required tail/helper samples, context pointer projections and live frames preserved','RF normal-return proof uses actually selected magic OR nonmagic path with matching mapped service and all needed S/SP/RA saves; wait must eventually satisfy its own condition; no physical clock/calibration success inferred','all numerical RF projections physically separate from protected RAM; no adverse MMIO/FENCE/IRQ/DMA/reentry/externalwriter effects, valid owned nonwrapping/nonalias frames/objects/source/table/heap','RF fresh config64+0 read is valid ordinary read; no initial caller argument value is promoted into state1/helper13; fresh masked reply is independent of earlier MMIO stores','following fill28/copy6 providers match actual mapped bytes, sources/destinations/savedframes stable and valid; copy6 is ordered fresh bytes, not atomic snapshot; preserved gate/count/GP/S fields as required'],
  boundary='zero branch only; cut before43e8e/43f1a next helper. No full initializer/gate/primary return, nonzero outer initializer, subsequent RF/event/payload lifetime proof',actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);pp=post.derive(image,carriers,header,coverage)
 return dict(schema='TSL9-fallback-selected-RF-return-posthelpers-nextcall-preservation-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i],pp['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],
  source_composition='gatezero caller fallback0 -> parent publications and selected RF return233write envelopes -> following fill28/clear/tail/copy6 sevenenvelopes -> before next helper with0,16383,6',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['43e8e/43f1a next helper/retry body and eventualinitializer/gate/primary return','nonzero gate outerinitializer and laterregistrations/tail','actual binding/freshfields/headheader/source/physicaleffects/IRQprogress/otherwriters/fullretention-consumption-release'])


def tests(carriers):
 qsource.tests(carriers);qreturn.reply.tests(carriers);post.tests(carriers);count=0
 for i,data in enumerate(carriers):
  for j,r in enumerate(qreturn.reply.leaves.ROLES):
   pc=qreturn.reply.leaves.DETAILS[i][0][j];raw=init.binding.take(data,pc,qreturn.reply.leaves.SIZES[j])
   for off in ((352,378,3288,3348) if r=='large' else (14,) if r=='enable' else (82,) if r=='wait' else (18,)):
    n=qreturn.reply.leaves.decode(raw,pc);z=n[pc+off]['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:qreturn.reply.leaves.inspect(bad,r,i)
    except RuntimeError:pass
    else:raise RuntimeError('fallbackRF leaf/capture mutationescaped')
    count+=1
  pc=qreturn.reply.tail.DETAILS[i][0][2];raw=init.binding.take(data,pc,232);n=qreturn.reply.tail.decode(raw,pc)
  for off in (70,206):
   z=n[pc+off]['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:qreturn.reply.tail.body(bad,'tail',i)
   except RuntimeError:pass
   else:raise RuntimeError('fallbackRF tail literal/state mutationescaped')
   count+=1
 check(count==18,'fallbackRF extra mutation census');qreturn.reply.domains()
 print('PASS:134 original publisher/RFreturn/posthelper/capture/leaf/state mutations rejected;fresh masked-word domains and fixed interval composition')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackRF exactledger')
 print('PASS:selected RF233 and following helper7 interval certificates;fallback0 to next-helper cut;strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;nexthelper/actualbinding/physicaleffects/full lifetime UNPROVED')


if __name__=='__main__':main()
