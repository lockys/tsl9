"""Prove the complete original event table consumer and its conditional read window."""
import hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
 if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='event_word_static_contract')
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def audit(K):
 for p,h in K['pins'].items():need(sha(R/p)==h,'Frozen input changed: '+p)
 e=read(R/K['evidence']);f=dict(start=0x176f8,end=0x1787c,operations=[o for o in e['operations']if 0x176f8<=o['addr']<0x1787c]);need(len(f['operations'])==135 and sum(o['size']for o in f['operations'])==388,'Whole selected original event consumer')
 B=lib(K['control_reader']);V=lib(K['CFG_reader']);external={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,cfg=V['whole_cfg'](f,B,external,48);raw=b''.join(bytes.fromhex(o['bytes'])for o in f['operations']);fw=(R/K['firmware']).read_bytes();need(hashlib.sha256(fw).hexdigest()==K['pins'][K['firmware']]and raw==fw[0x176f8-0x8000:0x1787c-0x8000],'Whole388 allowed CODE bytes equal the original APP')
 E=lib(K['APP_reader'])['ELF'];native=[];allops=None
 for mode in ['c','cpp']:
  path=R/K['APP_ELF'].replace('/c/','/'+mode+'/');elf=E(path);bm={};inventory={};total=0
  for s in elf.sections:
   if s['type']!=1 or s['flags']!=6:continue
   need(not(s['address']<0x14c8a and 0x14056<s['address']+s['size']),'Excluded CODE absent');bb=elf.data(s);at=0;total+=len(bb)
   while at<len(bb):
    n=4 if bb[at]&3==3 else 2;need(at+n<=len(bb),'Native instruction boundary');inventory[s['address']+at]=(n,int.from_bytes(bb[at:at+n],'little'));at+=n
   for p in range(max(s['address'],f['start']),min(s['address']+s['size'],f['end'])):need(p not in bm,'Unique whole-function native CODE owner');bm[p]=bb[p-s['address']]
  need(set(bm)==set(range(f['start'],f['end']))and bytes(bm[p]for p in range(f['start'],f['end']))==raw,'Every original instruction equals actual native C/C++ CODE');need((total,len(inventory))==(69412,23602),'Exact full selected CODE inventory');native.append(dict(mode=mode,ELF_sha256=sha(path),whole_CODE_bytes_equal=388))
  if allops is None:allops=inventory
  else:need(allops==inventory,'C/C++ actual instruction inventories identical')
 expected={0x1779a:'li a2, 7',0x1779c:'addi a0, sp, 8',0x177a0:'jalr a4',0x177be:'li a2, 7',0x177c0:'addi a0, sp, 8',0x177c2:'jalr a5',0x177c4:'lbu a5, 9(sp)',0x177c8:'andi a5, a5, 2',0x177ca:'beqz a5, 0x177e2',0x177cc:'lw a4, 8(sp)',0x177d0:'srli a5, a4, 0xa',0x177d4:'andi a5, a5, 63',0x177dc:'li a3, 2',0x177de:'beq a5, a3, 0x17832',0x177e2:'addi a0, sp, 8',0x177e4:'jal ra, 0xc776',0x17826:'mul a2, a5, a2',0x1782a:'li a1, 2',0x1782c:'mv a0, s1',0x1782e:'jalr a4',0x17830:'j 0x177e2',0x17832:'lbu a5, 370(gp)',0x17836:'slli a2, a5, 0x2',0x1783a:'auipc a3, 0x3',0x1783e:'addi a3, a3, 686',0x17842:'add a3, a3, a2',0x17844:'lw a3, 0(a3)',0x17846:'lui a2, 0x10',0x17848:'addi a2, a2, -1',0x1784a:'and a1, a3, a2',0x1784e:'and a4, a4, a2',0x17850:'slli a1, a1, 0x10',0x17852:'or a4, a4, a1',0x17854:'sw a4, 8(sp)',0x17856:'addi a5, a5, 1',0x17858:'li a4, 7',0x1785a:'rem a5, a5, a4',0x1785e:'srli a3, a3, 0x10',0x17860:'sb a3, 12(sp)',0x17864:'li a2, 800',0x17868:'sb a5, 370(gp)',0x1786c:'lw a5, 12(sp)',0x1786e:'lui a4, 0x40',0x17872:'lw a4, 88(a4)',0x17874:'srli a5, a5, 0x12',0x17876:'andi a5, a5, 31',0x17878:'addi a5, a5, 1',0x1787a:'j 0x17826'}
 need(all(ops[p]['opcode']==v for p,v in expected.items()),'Exact original index/read/packing/REM/fresh-word/raw-time operands')
 pcs=[o['addr']for o in f['operations']if 0x17832<=o['addr']<=0x1787a];need(all(set(g[a])=={b}for a,b in zip(pcs,pcs[1:]))and set(g[0x1787a])=={0x17826},'No branch or opaque call changes the table operands before local field writes')
 need(0x17844 in V['reachable'](g,f['start'],skip=0x17868),'Post-read modulo store does not dominate the current read');need(set(g[0x177de])=={0x17832,0x177e2},'Actual record selector2 branch')
 base=0x1783a+(3<<12)+686;need(base==0x1aae8 and base+7*4==0x1ab04,'Exact conditional seven-word read interval')
 refs=[];takes=0
 for p,(n,h)in sorted(allops.items()):
  if n!=4 or(h>>15)&31!=3:continue
  opcode=h&127;funct=(h>>12)&7
  if opcode==0x13 and funct==0:takes+=1
  if opcode not in [3,0x23]or funct not in [0,1,2,4,5]or opcode==0x23 and funct not in [0,1,2]:continue
  width={0:1,1:2,2:4,4:1,5:2}[funct];imm=sx((((h>>25)<<5)|((h>>7)&31))if opcode==0x23 else h>>20,12)
  if imm<=370<imm+width:refs.append(dict(PC=p,role='store'if opcode==0x23 else'load',offset=imm,width=width))
 need(refs==[dict(PC=0x17832,role='load',offset=370,width=1),dict(PC=0x17868,role='store',offset=370,width=1)]and takes==196,'Scoped selected-CODE GP-direct inventory;196 address aliases remain outside this direct-writer proof')
 h=allops[0x186aa][1];q=allops[0x186ae][1];need(h&127==0x17 and(h>>7)&31==3 and q&0x707f==0x13 and(q>>7)&31==3 and(q>>15)&31==3,'Original GP setup instructions');gp=(0x186aa+(h&0xfffff000)+sx(q>>20,12))&0xffffffff;need(gp==0x20004000,'Original nominal GP profile')
 words=[int.from_bytes(fw[p-0x8000:p-0x8000+4],'little')for p in range(base,base+28,4)];need(len(words)==7 and len(set(words))==7 and all(v<1<<24 for v in words),'Seven distinct low24-bit original words;only this28-byte DATA window selected')
 masks=[sum((((v>>(8*i))&255)!=0)<<i for i in range(3))for v in words];need(masks==[1,3,3,2,6,4,5],'Actual three-byte nonzero-channel pattern;physical channel semantics unproved')
 return dict(schema='TSL9-event-word-table-use-contract-v1',passed=True,whole_function=cfg,native_CODE_comparisons=native,table_base=base,lookup_PC=0x17844,lookup_formula='1AAE8 + 4*uint8(GP+370)',conditional_index_domain=[0,6],conditional_read_window=[base,base+28],conditional_read_bytes=28,index_GP_offset=370,nominal_GP=gp,logical_index_address=gp+370,physical_RAM_mapping_proved=False,index_update_PC=0x17868,index_update_expression='low8(signed_rem(uint8(previous_index)+1,7))',mathematical_post_update_domain=[0,6],post_read_update_does_not_bound_current_read=True,selected_CODE_direct_GP_references=refs,GP_ADDI_address_takes=takes,all_aliases_indirect_writers_IRQ_DMA_or_excluded_CODE_covered=False,global_index_at_read_invariant_proved=False,conservative_byte_index_domain=[0,255],conservative_read_window=[base,base+1024],conservative_read_bytes=1024,conservative_bytes_beyond_APP=base+1024-0x1ac00,conservative_window_is_not_full_table_size_or_actual_violation_proof=True,full_table_extent_proved=False,record_field_writes=dict(record_offset2='table word bits0..7',record_offset3='table word bits8..15',record_offset4='table word bits16..23',record_offsets0_1_5_6='retained from original frame accesses'),fresh_SP12_word_read_preserved=True,SP12_word_read_includes_bytes_beyond_seven_byte_copy=True,factor_expression='((fresh_word(SP+12)>>18)&31)+1',factor_uses_SP14_bits2_through6_not_table_bytes=True,factor_domain=[1,32],raw_A2_expression='800*factor',raw_A2_domain=[800,25600],indirect_transfer_PC=0x1782e,indirect_transfer_slot=0x40058,physical_timer_units_or_effects_proved=False,table_entries=7,table_words_are_distinct_low24_bit_values=True,nonzero_low_three_byte_masks=masks,palette_like_sequence_is_inference_only=True,physical_RGB_channels_or_lighting_feature_confirmed=False,conditions=['Index at the actual read is0..6;post-read modulo does not prove its initial value or all writers','Original nominal GP/register/private-entry context and valid aligned readable table/frame memory','No alias,IRQ,DMA,reentrant or callee interference invalidates the observed data/register use','Installed copy/timer slots,physical RAM mapping,time units and device feature identity remain unproved'],table_DATA_envelope_read=False,excluded_CODE_or_default_payload_read=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False,goal_complete=False)
