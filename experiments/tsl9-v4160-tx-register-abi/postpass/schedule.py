#!/usr/bin/env python3
"""Explicit scheduling of ten already-compiled stack words; no opcode encoder."""
import argparse,hashlib,json,runpy,struct,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
RAW='da17e505ec2b58cada40a80a12a645b7fa21c116ce76666544168f2c4ff6c6a7'
SECTION='.text.tsl9_tx_valid_body'
SLOTS={1:28,8:24,9:20,18:16,19:12}
def H(b):return hashlib.sha256(b).hexdigest()
def sha(p):return H(p.read_bytes())
def need(v,m):
 if not v:raise ValueError(m)
def case(root,slug):return next(p for p in(root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def context(root):
 parser=case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py';raw=case(root,'v4160-ota-tx-2026-10-22')/'source-review/raw.py';need(sha(parser)==PARSER and sha(raw)==RAW,'pinned bounded ELF/instruction field readers');return dict(ELF=runpy.run_path(str(parser))['ELF'],decode=runpy.run_path(str(raw))['decode'],parser=parser,raw=raw)
def policy_gate(path):
 p=json.loads(path.read_bytes());need(p==dict(schema='TSL9-TX-explicit-compiled-frame-order-v1',section=SECTION,frame_bytes=32,saved_slots={str(k):v for k,v in SLOTS.items()},prefix_compiler_order=[1,8,9,18,19],prefix_source_order=[8,9,18,19,1],success_head_restore_order=[1,9,18,19],success_S0_restore_after_descriptor_stores=True,success_S0_restore_before_ROM_tail_pointer_read=True,compiler_output_equivalence_claimed=False,original_full_function_ABI_claimed=False,opcode_generation=False,original_firmware_codegen_input=False),'exact source-owned scheduling policy');return p
def rows(body,decode):
 out=[];off=0
 while off<len(body):
  try:r=decode(body[off:],off)
  except ValueError:
   w=int.from_bytes(body[off:off+4],'little');need(len(body[off:off+4])==4 and w&127==0x63 and(w>>12)&7==7,'bounded BGEU field form');r=decode((w^(1<<12)).to_bytes(4,'little'),off);r.update(op='bgeu',raw_hex=body[off:off+4].hex())
  r['offset']=off;out.append(r);off+=r['bytes']
 need(off==len(body),'complete instruction byte coverage');return out
def shape(r):return (r['op'],r['rd'],r['rs1'],r['rs2'],r['immediate'])
def inspect(e,decode):
 need(e.kind==1 and e.flags==1,'actual RV32 RVC ILP32 relocatable object');owners=[s for s in e.sections if s['name']==SECTION];need(len(owners)==1,'unique typed body section name');owner=owners[0];need((owner['type'],owner['flags'],owner['size'],owner['alignment'])==(1,6,270,2),'actual typed AX270 align2 body');need([s['index'] for s in e.sections if s['flags']&2 and s['size']]==[owner['index']],'no extra allocated storage');funcs=[s for s in e.symbols if s['info']&15==2];need(len(funcs)==1 and(funcs[0]['index'],funcs[0]['value'],funcs[0]['size'],funcs[0]['info'],funcs[0]['other'])==(owner['index'],0,270,2,0) and funcs[0]['name'] in('tsl9_tx_valid_body','_ZL18tsl9_tx_valid_bodyjjjj'),'one allowlisted LOCAL FUNC270/default-visibility typed body')
 lo,hi=owner['offset'],owner['offset']+owner['size'];shoff=struct.unpack_from('<I',e.raw,32)[0];need(struct.unpack_from('<H',e.raw,44)[0]==0,'relocatable compiler object has no program headers');need(not(lo<52 and hi>0) and not(lo<shoff+40*len(e.sections) and hi>shoff),'code storage does not overlap ELF header/section headers')
 for s in e.sections:
  if s['index']!=owner['index'] and s['type']!=8 and s['size']:need(not(lo<s['offset']+s['size'] and hi>s['offset']),'selected code storage does not alias any other section payload')
 need(not any(any(t in s['name'] for t in('.eh_frame','.debug_frame','.gcc_except_table')) for s in e.sections),'no unwind/exception location metadata');body=e.data(owner);rs=rows(body,decode);need(shape(rs[0])==('addi',2,2,None,-32),'frame allocation stays compiler-authored outside store window');prefix=rs[1:6];need([r['rs2'] for r in prefix]==[1,8,9,18,19] and all(r['op']=='sw' and r['rs1']==2 and r['immediate']==SLOTS[r['rs2']] and r['bytes']==2 for r in prefix),'exact five compiled C.SWSP values/slots');need(shape(rs[6])==('lhu',14,3,None,150),'first connection read after prefix stores')
 starts=[i for i,r in enumerate(rs) if shape(r)==('add',15,15,8,None)];need(len(starts)==1,'one success finish region');tail=rs[starts[0]:]
 expected=[('add',15,15,8,None),('sb',None,15,14,5),('addi',15,0,None,1062),('mul',15,15,12,None),('addi',8,8,None,6),('slli',12,12,None,2),('addi',11,0,None,1),('add',15,15,13,None),('sh',None,15,8,2),('sh',None,15,0,4),('add',12,12,3,None),('addi',12,12,None,148),('lui',15,None,None,262144),('lw',6,15,None,80),('lbu',10,12,None,0),('lw',1,2,None,28),('lw',8,2,None,24),('lw',9,2,None,20),('lw',18,2,None,16),('lw',19,2,None,12),('addi',2,2,None,32),('jalr',0,6,None,0)]
 need([shape(r) for r in tail]==expected,'whole bounded success-tail operand contract');need(all(tail[i]['bytes']==2 for i in(15,16,17,18,19)),'only compiled C.LWSP words are moved');prefix_range=(prefix[0]['offset'],prefix[-1]['offset']+2);tail_range=(tail[0]['offset'],len(body));ranges=[prefix_range,tail_range]
 for lo,hi in ranges:
  for s in e.symbols:
   if s['index']==owner['index']:need(not lo<=s['value']<hi,'no symbol at or inside scheduling window')
  for rel in e.relocations:
   if rel['owner']==owner['name']:need(not lo<=rel['offset']<hi,'no relocation at a moved instruction/window')
   s=rel['symbol']
   if s['index']==owner['index']:need(not lo<=s['value']+rel['addend']<hi,'no recorded relocation target at or inside window')
  for r in rs:
   if r['target'] is not None:
    need(not lo<r['target']<hi,'no direct branch/jump target inside scheduling window')
    if r['target']==lo:need(lo==208 and(r['offset'],r['op'],r['rs1'],r['rs2'])==(178,'bgeu',10,8),'only the known loop exit may target unchanged success-window start')
   if r['op']=='jalr' and r['rd']==1:need(not lo<=r['offset']+r['bytes']<hi,'no callreturn at or inside scheduling window')
 need(prefix_range==(2,12) and tail_range==(208,270),'actual fixed window geometry');return dict(owner=owner,body=body,rows=rs,prefix=prefix,tail=tail,ranges=ranges)
def transform(e,decode):
 f=inspect(e,decode);body=f['body'];prefix=f['prefix'];tail=f['tail'];prefix_after=[prefix[i] for i in(1,2,3,4,0)];tail_after=[tail[i] for i in[*range(6),15,17,18,19,*range(6,12),16,*range(12,15),20,21]];out=bytearray(e.raw);windows=[]
 for name,(lo,hi),before,after in [('five_compiled_SWSP',f['ranges'][0],prefix,prefix_after),('five_compiled_LWSP',f['ranges'][1],tail,tail_after)]:
  a=b''.join(bytes.fromhex(r['raw_hex']) for r in before);b=b''.join(bytes.fromhex(r['raw_hex']) for r in after);need(a==body[lo:hi] and len(a)==len(b),'exact complete source-window bytes');need(Counter(r['raw_hex'] for r in before)==Counter(r['raw_hex'] for r in after),'no instruction opcode created or removed');off=f['owner']['offset']+lo;out[off:off+len(b)]=b;windows.append(dict(name=name,section_offset=lo,bytes=hi-lo,before_sha256=H(a),after_sha256=H(b),before_word_hex=[r['raw_hex'] for r in before],after_word_hex=[r['raw_hex'] for r in after]))
 diff=[i for i,(a,b) in enumerate(zip(e.raw,out)) if a!=b];need(all(any(f['owner']['offset']+lo<=i<f['owner']['offset']+hi for lo,hi in f['ranges']) for i in diff),'all ELF metadata/other bytes remain exact');return bytes(out),dict(windows=windows,changed_file_byte_offsets=diff,changed_bytes=len(diff),compiler_output_equivalence_claimed=False,original_full_ABI_claimed=False,original_firmware_codegen_input=False,opcode_generation=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--receipt',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve();src=a.input.resolve();dst=a.output.resolve();receipt=a.receipt.resolve();need(src.is_file() and dst!=src and receipt not in(src,dst) and not dst.exists() and not receipt.exists(),'distinct existing input/create-only output and receipt');allowed=[root/'experiments/tsl9-v4160-tx-register-abi/build',case(root,'v4160-tx-register-abi-2026-10-22')/'implementation/build'];need(all(any(p.is_relative_to(base.resolve()) for base in allowed) for p in(dst,receipt)),'outputs stay in this new model/case build scope');need(dst.parent.is_dir() and receipt.parent.is_dir(),'output parents must already exist');ctx=context(root);policy=Path(__file__).with_name('policy.json');policy_gate(policy);pins={str(p):sha(p) for p in(Path(__file__),policy,ctx['parser'],ctx['raw'],src)};e=ctx['ELF'](src);raw,facts=transform(e,ctx['decode'])
 with dst.open('xb') as f:f.write(raw)
 check=ctx['ELF'](dst);need(check.raw==raw and len(raw)==len(e.raw),'actual output readback');need(all(sha(Path(p))==pin for p,pin in pins.items()),'stable pass/policy/readers/input');r=dict(schema='TSL9-TX-explicit-compiled-frame-order-v1',passed=True,input=dict(path=str(src),sha256=sha(src),bytes=src.stat().st_size),output=dict(path=str(dst),sha256=sha(dst),bytes=dst.stat().st_size),policy_sha256=sha(policy),source_pins=pins,**facts,RV32_execution=False,ISA_emulation=False,network=False,hardware=False)
 with receipt.open('xb') as f:f.write((json.dumps(r,indent=2)+'\n').encode())
 print(json.dumps(dict(passed=True,receipt=str(receipt),sha256=sha(receipt),changed_bytes=r['changed_bytes'])))
if __name__=='__main__':main()
