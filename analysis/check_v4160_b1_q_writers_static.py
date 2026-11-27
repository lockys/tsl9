"""Offline literal-seeded local def-use census for writes overlapping Q.

Immutable decoded prefixes/backward definitions only; no ISA execution,
register machine, mutable target memory, provider/MMIO/IRQ model or hardware.
"""
import argparse,json
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_q_source_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-q-writers-static.json')
MASK=0xffffffff
BUDGET=32
NONCONTROL={'lui','li','auipc','mv','addi','add','load','store','nop','sub','and','andi','or','ori','xor','xori','slli','srli','srai','sll','srl','sra','slt','sltu','slti','sltiu','mul','mulh','mulhu','mulhsu','div','divu','rem','remu','neg','not'}


def census(mem,target,budget=BUDGET):
 check(budget>=1,'Qwriters positivebudget')
 counts=Counter();hits={};addresses={};stops=Counter()
 for origin in sorted(mem):
  if origin%2 or not all(origin+j in mem for j in range(4)):continue
  counts['halfword_complete4_windows']+=1
  w=int.from_bytes(bytes(mem[origin+j] for j in range(4)),'little')
  if w&127!=0x37 or not(w>>7&31):continue
  counts['standard_LUI_seeds']+=1;nodes=[];pc=origin
  for _ in range(budget):
   if not all(pc+j in mem for j in range(2)):stops['missing_halfword']+=1;break
   h=mem[pc]|mem[pc+1]<<8;z=4 if h&3==3 else 2
   if z==4 and h&31==31:stops['unsupported_long_encoding']+=1;break
   if not all(pc+j in mem for j in range(z)):stops['missing_instruction_bytes']+=1;break
   raw=bytes(mem[pc+j] for j in range(z))
   try:d=previous.radio.decode(raw,pc)[pc]
   except RuntimeError:stops['unsupported_encoding']+=1;break
   counts['decoded_instructions']+=1
   if d['op'] in ('jal','jalr','jr','call_indirect') or d['op'].startswith('b'):
    stops['control_flow']+=1;break
   if d['op'] not in NONCONTROL:stops['outside_noncontrol_allowlist']+=1;break
   # Each query follows nearest syntactic definitions backwards in this
   # immutable straight prefix. Loads/other defs are unknown, never read.
   @lru_cache(None)
   def literal(before,reg):
    if reg==0:return 0
    for j in range(before-1,-1,-1):
     n=nodes[j]
     if n.get('rd')!=reg:continue
     op=n['op']
     if op in ('lui','li'):return n['imm']&MASK
     if op=='auipc':return (n['pc']+n['imm'])&MASK
     if op=='mv':return literal(j,n['rs2'])
     if op=='addi':
      v=literal(j,n['rs1']);return None if v is None else (v+n['imm'])&MASK
     if op=='add':
      a,b=literal(j,n['rs1']),literal(j,n['rs2']);return None if a is None or b is None else (a+b)&MASK
     return None
    return None
   k=len(nodes)
   if d['op']=='store':
    counts['stores_in_prefixes']+=1;base=literal(k,d['rs1'])
    if base is not None:
     counts['literal_base_stores_in_prefixes']+=1;a=(base+d['imm'])&MASK
     if any(target<=((a+j)&MASK)<target+4 for j in range(d['width'])):
      key=(pc,a,d['width'],d['rs1'],d['rs2']);row=hits.setdefault(key,dict(store_pc=pc,address=a,width=d['width'],base_register=d['rs1'],source_register=d['rs2'],base_literal=base,witnesses=[]))
      row['witnesses'].append(dict(seed=origin,bytes=bytes(mem[j] for j in range(origin,pc+z)).hex(),instructions=k+1,source_literal=literal(k,d['rs2'])))
   nodes.append(d)
   if d.get('rd',0) and d['op'] in ('addi','mv','add'):
    value=literal(len(nodes),d['rd'])
    if value is not None and target<=value<target+4:
     key=(pc,value,d['rd']);addresses.setdefault(key,dict(pc=pc,address=value,register=d['rd'],seed=origin))
   pc+=z
  else:stops['instruction_budget']+=1
 check(sum(stops.values())==counts['standard_LUI_seeds'],'Qwriters eachseed hasexplicitstop')
 return dict(budget=budget,counts=dict(sorted(counts.items())),stops=dict(sorted(stops.items())),overlapping_stores=list(hits.values()),slot_address_constructions=list(addresses.values()),scope='every captured halfword standard LUI seed; at most32 decoded instructions; nearest backwards LUI/LI/AUIPC/ADDI/MV/ADD definitions only; unknown defs killed; stop at control/unsupported/gap/budget; not reachability or allwriters')


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());slot=0x20003590+80*index
 binary=census(dict(enumerate(data,0x40000)),slot);full=census(mem,slot)
 expected=previous.radio.DETAILS[index][0][0]+52
 for part in (binary,full):
  rows=part['overlapping_stores'];check(len(rows)==1 and rows[0]['store_pc']==expected and rows[0]['address']==slot and rows[0]['width']==4 and rows[0]['base_literal']==0x20003000,'Qwriters literalwriter census')
 check(binary['overlapping_stores']==full['overlapping_stores'],'Qwriters fullHEX samepublisher witnesses')
 return dict(label=init.binding.PROFILES[index][0],Q_slot=slot,binary_inventory=binary,full_sparse_inventory=full,actual_otherwriters_or_globalpreservation_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 app=[census(dict(enumerate(image,0x8000)),0x20003590+80*i) for i in range(2)]
 check(not any(p['overlapping_stores'] for p in app),'Qwriters APP nohit forbothcandidate slots')
 return dict(schema='TSL9-Q-literal-seeded-bounded-defuse-writer-census-v1',APP_sha256=sha256(image).hexdigest(),APP_inventories=app,profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,limitations=['no allwriters/reachability proof; includes data andoverlapping instruction origins','doesnotcross branches/calls/unknown/gaps/budget; incomingregister facts unknown','load-derived pointers/dynamicinput/copy-fill effects/aliases/externalwriters notclosed','AUIPC usesnominalsourcePC; copiedruntimePC/mapping notproved; no physicalalias proof','matching installedprovider/startuporder/cross-eventpreservation/fullownership remainunproved'])


def tests(carriers):
 def word(w):return w.to_bytes(4,'little')
 def lui(r,v):return word(v|(r<<7)|0x37)
 def addi(r,b,v):return word(((v&4095)<<20)|(b<<15)|(r<<7)|0x13)
 def store(s,b,v,f=2):return word(((v&4095)>>5<<25)|(s<<20)|(b<<15)|(f<<12)|((v&31)<<7)|0x23)
 def run(raw,target=0x20003590,budget=BUDGET,missing=()):return census({j:b for j,b in enumerate(raw) if j not in missing},target,budget)
 cases=0
 for width,f in ((1,0),(2,1),(4,2)):
  for off in range(1421,1431):
   r=run(lui(14,0x20003000)+store(13,14,off,f));want=off+width>1424 and off<1428
   check(bool(r['overlapping_stores'])==want,'Qwriters narrow overlapboundary');cases+=1
 base=lui(14,0x20003000)+addi(15,14,1424)
 check(run(base+store(13,15,0))['overlapping_stores'][0]['address']==0x20003590,'Qwriters renamedbase ADDI');cases+=1
 check(run(base+word(0x00072783)+store(13,15,0))['overlapping_stores']==[],'Qwriters loadkills pointer definition');cases+=1
 check(run(base+word(0x008000ef)+store(13,15,0))['overlapping_stores']==[],'Qwriters stopcall');cases+=1
 check(run(base+word(0x00000463)+store(13,15,0))['overlapping_stores']==[],'Qwriters stopbranch');cases+=1
 check(run(base+word(0x00000073)+store(13,15,0))['overlapping_stores']==[],'Qwriters stopunknown ECALL');cases+=1
 check(run(base+store(13,15,0),budget=2)['overlapping_stores']==[],'Qwriters budgetstop');cases+=1
 check(run(base+store(13,15,0),missing=(4,))['overlapping_stores']==[],'Qwriters sparsegapstop');cases+=1
 check(run(lui(14,0x20003000)+addi(14,14,1424)+(0x8002|(15<<7)|(14<<2)).to_bytes(2,'little')+store(13,15,0))['overlapping_stores'][0]['address']==0x20003590,'Qwriters compressedMV defuse');cases+=1
 check(run(lui(14,0x20003000)+addi(14,14,1424)+word((14<<15)|(15<<7)|0x33)+store(13,15,0))['overlapping_stores'][0]['address']==0x20003590,'Qwriters ADD defuse');cases+=1
 check(run(lui(5,0)+word(0x20003000|(14<<7)|0x17)+store(13,14,1420))['overlapping_stores'][0]['address']==0x20003590,'Qwriters nominalPC AUIPC defuse');cases+=1
 check(run(base+(0xc000|(7<<7)|(5<<2)).to_bytes(2,'little'))['overlapping_stores'][0]['width']==4,'Qwriters compressedSW');cases+=1
 # Address wraps before byte overlap; mathematical host fixture only.
 wrap=lui(14,0xfffff000)+addi(14,14,2047)+addi(14,14,2047)+store(13,14,0)
 check(run(wrap,target=0)['overlapping_stores'][0]['address']==0xfffffffe,'Qwriters wrappedstore byteinterval');cases+=1
 print('PASS:'+str(cases)+' closed host scanner fixtures; narrow boundaries/renamedbase/loadkill/control/unknown/gap/budget/wrap')
 mutations=0
 for i,data in enumerate(carriers):
  pc=previous.radio.DETAILS[i][0][0];raw=init.binding.take(data,pc,56);target=0x20003590+80*i
  for off,bit in ((48,1<<12),(52,14<<15)):
   bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^bit).to_bytes(4,'little')
   check(not census(dict(enumerate(bad,pc)),target)['overlapping_stores'],'Qwriters perturbed originalpublisher excluded');mutations+=1
 print('PASS:'+str(mutations)+' original-site base/store perturbations remove publisher hit')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'Qwriters exactledger')
 print('PASS:APP/BIN/fullstrictHEX literal-seeded Q writer inventories/exactledger; noallwriters/actualbinding/cross-event preservation claim')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,replay ortargetnetwork')


if __name__=='__main__':main()
