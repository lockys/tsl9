#!/usr/bin/env python3
"""Fresh C/C++ RV32 compile/link and static readback; never execute target code."""
import argparse,hashlib,importlib.util,json,os,re,subprocess,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-page-reply'
NAME='tsl9_ota_page_reply_9b8e'
ABI_PIN='a6f64ae51a1aeaad78a678b9db71d3af9439710e4a39ccb1c696d92b42883907'
SOURCE_SEAL='2fe1ed8e78cbb6e054a0368c330b5d1d15f9c75bc0510769340371464b3d32f3'
TOOLS={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f','llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
LAYOUT='''OUTPUT_ARCH(riscv)
ENTRY(tsl9_ota_page_reply_9b8e)
SECTIONS {
 .reply 0x9B8E : { *(.text.tsl9_ota_page_reply_9b8e) }
 /DISCARD/ : { *(.comment) *(.note.GNU-stack) }
}
ASSERT(SIZEOF(.reply) == 124, "reply component size must be124")
'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
 if not x:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def write(p,r):p.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def case(root):return next(p for p in (root/'analysis/v4160-ota-page-reply-2026-10-22',root/'apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22') if (p/'implementation/verify_native.py').is_file())
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def context(root):
 c=case(root);need(sha(c/'ABI-review/native.py')==ABI_PIN,'independent ABI checker pin');need(sha(c/'source-review/seal.json')==SOURCE_SEAL,'source contract seal pin');pins={}
 for name,pin in read(c/'source-review/seal.json')['members'].items():p=c/'source-review'/name;need(sha(p)==pin,'source sealed member');pins[p.relative_to(root).as_posix()]=sha(p)
 a=load(c/'ABI-review/native.py','reply_native_ABI');decoder,elf,original=a.context(root)
 parser=next(p for p in (root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py') if p.is_file())
 ordering=root/'experiments/tsl9-v4160-reply-abi-order/order.py';schedule=load(ordering,'reply_explicit_ABI_order')
 for p in [Path(__file__),c/'ABI-review/native.py',c/'source-review/seal.json',parser,*[p for p in(root/MODEL/'src').glob('*') if p.is_file()],*[p for p in ordering.parent.glob('*') if p.is_file()]]:pins[p.relative_to(root).as_posix()]=sha(p)
 return dict(root=root,case=c,a=a,decoder=decoder,elf=elf,original=original,pins=pins,schedule=schedule,ordering=ordering)
def flags(mode):
 allowed={1,2,5,6,7,*range(10,18),*range(28,32)}
 return ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',*['-ffixed-x'+str(i) for i in range(1,32) if i not in allowed],'-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17',*(['-fno-exceptions'] if mode=='cpp' else [])]
def invoke(argv,folder,label,commands,success=True):
 p=subprocess.run([str(x) for x in argv],cwd=folder,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(p.stdout+p.stderr);commands.append(dict(argv=[str(x) for x in argv],exit=p.returncode,log=log.name,log_sha256=sha(log)));need(p.returncode==0 if success else p.returncode!=0,'actual command '+label+'; inspect '+str(log));return p.stdout.decode(errors='replace')
def toolset(directory):
 out={}
 for name,pin in TOOLS.items():p=next(p for p in (directory/(name+'.exe'),directory/name) if p.is_file());need(sha(p)==pin,'actual pinned LLVM '+name);out[name]=p
 return out
def recipes(ctx,folder,mode,tools,python):
 need(mode in ('c','cpp'),'recorded language C11/C++17');model=ctx['root']/MODEL
 link=[tools['ld.lld'],'-m','elf32lriscv','--no-relax','-T',folder/'original-entry-component.ld',folder/'source-ordered.o']
 return [
 ('compile.o',[tools['clang'],*flags(mode),'-c','-MMD','-MF',folder/'page_reply.d','-MT','page_reply.o',model/'src/page_reply.c','-o',folder/'page_reply.o'],True),
 ('compile.ll',[tools['clang'],*flags(mode),'-S','-emit-llvm',model/'src/page_reply.c','-o',folder/'page_reply.ll'],True),
 ('explicit-ABI-order',[python,'-B',ctx['ordering'],'--project-root',ctx['root'],'--input',folder/'page_reply.o','--output',folder/'source-ordered.o','--receipt',folder/'ABI-order.json'],True),
 ('strict-missing-TX',[*link,'-o',folder/'STRICT-MISSING-TX.elf'],False),
 ('numeric-TX-witness',[*link,'--defsym=__tsl9v4160_call_8a56=0x8a56','-o',folder/'ADDRESS-WITNESS-ONLY.elf'],True),
 ('disassembly',[tools['llvm-objdump'],'-d',folder/'page_reply.o'],True)]
def disassembly_gate(path,body):
 rows=[]
 for line in path.read_text(errors='replace').splitlines():
  m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s].*)$',line)
  if m:rows.append((int(m[1],16),bytes.fromhex(m[2]),m[3]))
 need(len(rows)==50,'all50 actual disassembly instruction rows');at=0
 for address,raw,op in rows:need(address==at and raw==body[at:at+len(raw)] and len(raw) in (2,4),'exact contiguous raw disassembly/ELF binding');need(not op.startswith('<unknown>'),'known disassembly instruction');at+=len(raw)
 need(at==len(body)==124,'full exact124B disassembly coverage');return dict(rows=50,bytes=at,ELF_bytes_bound=True)
def static_checks(ctx,folder):
 a=ctx['a'];e=ctx['elf'].ELF(folder/'page_reply.o');proof=a.object_contract(ctx['decoder'],ctx['elf'],folder/'page_reply.o',ctx['original']);ir=a.ir_contract((folder/'page_reply.ll').read_text());s=next(s for s in e.symbols if s['name']==NAME);body=e.function_bytes(s)
 need(e.flags==1,'RV32 RVC softfloat ELF flags');allocated=[x for x in e.sections if x['flags']&2 and x['size']];need(len(allocated)==1 and allocated[0]['name']==proof['owner'],'only124 allocated executable bytes, no data/unwind/hidden functions');need([x['name'] for x in e.symbols if x['info']&15==2 and x['size']]==[NAME],'only one native function')
 dis=disassembly_gate(folder/'disassembly.log',body);ordered=ctx['a'].object_contract(ctx['decoder'],ctx['elf'],folder/'source-ordered.o',ctx['original'],True);order_receipt=ctx['schedule'].replay(ctx['root'],folder/'ABI-order.json');need(len(order_receipt['proof']['changed_file_offsets'])==28,'actual28 byte source ABI ordering, no new words');post=ctx['elf'].ELF(folder/'source-ordered.o');postsym=next(s for s in post.symbols if s['name']==NAME);postbody=post.function_bytes(postsym)
 linked=ctx['elf'].ELF(folder/'ADDRESS-WITNESS-ONLY.elf');need(linked.kind==2 and linked.flags==1 and not linked.relocations,'strict linked RV32 ELF, no unresolved relocations');sym=next(s for s in linked.symbols if s['name']==NAME);need(sym['value']==0x9b8e and sym['size']==124,'original entry/extent numeric placement');need(not any(s['name'] and s['index']==0 for s in linked.symbols),'no linked undefined symbols');need([(x['name'],x['address'],x['size'],x['flags']) for x in linked.sections if x['flags']&2 and x['size']]==[('.reply',0x9b8e,124,6)],'only one linked124B AX allocation')
 linkedbody=linked.function_bytes(sym);need(linkedbody[:0x52]+postbody[0x52:0x56]+linkedbody[0x56:]==postbody,'only actual TX relocation changes ordered object body');need(linkedbody==ctx['original'],'actual linked source-ordered124B equals all original words');row=next(r for r in ctx['decoder'].rows(linkedbody) if r['PC']==0x9be0);need(row['op']=='jal' and row['rd']==1 and row['target']==0x8a56,'actual linked TX JAL target and RA9BE4')
 need((folder/'original-entry-component.ld').read_text()==LAYOUT,'exact authored linker recipe');strict=(folder/'strict-missing-TX.log').read_text(errors='replace');need('undefined symbol: __tsl9v4160_call_8a56' in strict and strict.count('undefined symbol:')==strict.count('error:')==1 and not(folder/'STRICT-MISSING-TX.elf').exists(),'strict sole missing TX provider rejects without output')
 deps=(folder/'page_reply.d').read_text().replace('\\\n',' ');target,inputs=deps.split(':',1);need(target=='page_reply.o','MMD target matches actual compiler-MT');actual=[Path(x.replace('\\ ', ' ')).resolve() for x in re.findall(r'(?:\\ |\S)+',inputs)];need(set(actual)=={(ctx['root']/MODEL/'src'/n).resolve() for n in ('page_reply.c','page_reply.h','reply_io.h')} and len(actual)==3,'exact three actual native source/header MMD inputs')
 return dict(component=proof,explicit_source_ordered_component=ordered,ABI_order_receipt=order_receipt,IR=ir,disassembly=dis,numeric_entry_extent_fit=True,full_original_byte_identity_after_explicit_order=True,compiler_only_pointwise_identity=False,universal_native_opaque_SP_S_ABI=False,provider_witness_only=True,TX_provider_bytes=0,strict_missing_provider_rejected=True,linked_code_sha256=hashlib.sha256(linkedbody).hexdigest(),image_integrated=False,OTA_ready=False)
MUTATIONS=[('header_shift','src/reply_io.h','(value)>>8','(value)>>16'),('truncate_index','src/reply_io.h','((value)+(index))','((value)+((index)&65535u))'),('tail_residue_swap','src/reply_io.h','(a0,(r1),(r2))','(a0,(r2),(r1))')]
def compiled_controls(ctx,folder,mode,tools):
 results=[];model=ctx['root']/MODEL
 for name,file,old,new in MUTATIONS:
  base=folder/'compiled-controls'/name;base.mkdir(parents=True)
  for p in (model/'src').glob('*'):
   if p.is_file():q=base/'src'/p.name;q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes())
  p=base/file;text=p.read_text();need(text.count(old)==1,'unique actual native mutation '+name);p.write_bytes(text.replace(old,new).encode());commands=[]
  for suffix,action in (('.o',['-c']),('.ll',['-S','-emit-llvm'])):invoke([tools['clang'],*flags(mode),*action,base/'src/page_reply.c','-o',base/('page_reply'+suffix)],base,'compile'+suffix,commands)
  try:ctx['a'].object_contract(ctx['decoder'],ctx['elf'],base/'page_reply.o',ctx['original']);ctx['a'].ir_contract((base/'page_reply.ll').read_text())
  except (ValueError,KeyError):results.append(dict(name=name,rejected=True,file=file,old=old,new=new,commands=commands));continue
  raise ValueError('actual compiled native mutant accepted '+name)
 return results
def verify(root,folder,mode,directory):
 folder.mkdir(parents=True);ctx=context(root);tools=toolset(directory);pins={str(p):sha(p) for p in [*tools.values(),Path(sys.executable)]};commands=[];model=root/MODEL
 (folder/'original-entry-component.ld').write_bytes(LAYOUT.encode())
 for label,argv,success in recipes(ctx,folder,mode,tools,Path(sys.executable)):invoke(argv,folder,label,commands,success)
 checks=static_checks(ctx,folder);e=ctx['elf'].ELF(folder/'page_reply.o');s=next(s for s in e.symbols if s['name']==NAME);controls=ctx['a'].controls(ctx['decoder'],e.function_bytes(s),ctx['original'],(folder/'page_reply.ll').read_text());negatives=compiled_controls(ctx,folder,mode,tools)
 need(ctx['pins']==context(root)['pins'] and all(sha(Path(p))==v for p,v in pins.items()),'stable actual source/checker/LLVM identities before/after build')
 r=dict(schema='TSL9-OTA-page-reply-native-v1',passed=True,mode=mode,input_sha256=ctx['pins'],tools=pins,commands=commands,checks=checks,raw_IR_controls=controls,actual_compiled_controls=negatives,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},RV32_execution=False,ISA_emulation=False,network=False,hardware=False);write(folder/'verification.json',r);return dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),bytes=124,instructions=50,compiler_pointwise_identity=False,provider_witness_only=True)
def replay(root,receipt):
 r=read(receipt);folder=receipt.parent;ctx=context(root);need(r['passed'] and ctx['pins']==r['input_sha256'],'exact current native input identities')
 for p,pin in r['tools'].items():need(sha(Path(p))==pin,'actual tool identity')
 for n,pin in r['artifacts'].items():p=(folder/n).resolve();need(p.is_relative_to(folder.resolve()) and p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'],'actual native artifact '+n)
 need(static_checks(ctx,folder)==r['checks'],'fresh static native artifact checks')
 tools={name:next(Path(p) for p,pin in r['tools'].items() if pin==expected) for name,expected in TOOLS.items()};need(len(r['commands'])==6,'six exact actual native/provenance stages');python=Path(r['commands'][2]['argv'][0]);need(str(python) in r['tools'],'actual ordering Python identity recorded')
 for c,(label,argv,success) in zip(r['commands'],recipes(ctx,folder,r['mode'],tools,python)):need(c['argv']==[str(x) for x in argv] and c['log']==label+'.log' and sha(folder/c['log'])==c['log_sha256'] and (c['exit']==0 if success else c['exit']!=0),'exact actual source-only command/profile and expected outcome/log')
 e=ctx['elf'].ELF(folder/'page_reply.o');sym=next(s for s in e.symbols if s['name']==NAME);need(ctx['a'].controls(ctx['decoder'],e.function_bytes(sym),ctx['original'],(folder/'page_reply.ll').read_text())==r['raw_IR_controls'],'fresh static byte/IR controls');need(len(r['raw_IR_controls'])==11 and len(r['actual_compiled_controls'])==3,'bounded static and actual compiled negative inventory')
 for row,(name,file,old,new) in zip(r['actual_compiled_controls'],MUTATIONS):
  base=folder/'compiled-controls'/name;need((row['name'],row['file'],row['old'],row['new'])==(name,file,old,new),'compiled mutant identity')
  for p in (root/MODEL/'src').glob('*'):
   if p.is_file():expected=p.read_bytes();expected=expected.decode().replace(old,new).encode() if p.name==Path(file).name else expected;need((base/'src'/p.name).read_bytes()==expected,'one-change actual mutant source')
  try:ctx['a'].object_contract(ctx['decoder'],ctx['elf'],base/'page_reply.o',ctx['original']);ctx['a'].ir_contract((base/'page_reply.ll').read_text())
  except (ValueError,KeyError):pass
  else:raise ValueError('compiled mutant replay accepted')
  need(len(row['commands'])==2,'two compiled native mutation products')
  for c,(suffix,action) in zip(row['commands'],(('.o',['-c']),('.ll',['-S','-emit-llvm']))):need(c['argv']==[str(x) for x in [tools['clang'],*flags(r['mode']),*action,base/'src/page_reply.c','-o',base/('page_reply'+suffix)]] and c['exit']==0 and sha(base/c['log'])==c['log_sha256'],'exact same-profile mutant compiled successfully')
 return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),bytes=124,instructions=50,actual_compiled_controls=3,provider_witness_only=True,RV32_execution=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--tool-dir',type=Path);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
 if a.replay:print(json.dumps(replay(root,a.replay.resolve())));return
 need(a.tool_dir is not None,'explicit local LLVM --tool-dir required');base=a.build_root.resolve() if a.build_root else root/MODEL/'build'/('native-'+uuid.uuid4().hex);need(base.is_relative_to(root) and not base.exists(),'create-only native build root inside project');print(json.dumps(dict(passed=True,results=[verify(root,base/m,m,a.tool_dir.resolve()) for m in (['c','cpp'] if a.language=='both' else [a.language])],RV32_execution=False)))
if __name__=='__main__':main()
