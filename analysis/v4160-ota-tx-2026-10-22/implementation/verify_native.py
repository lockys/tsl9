#!/usr/bin/env python3
"""Compile and statically inspect one partial TX component. Never execute RV32."""
import argparse,hashlib,importlib.util,json,re,struct,subprocess,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-tx'
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
RAW='da17e505ec2b58cada40a80a12a645b7fa21c116ce76666544168f2c4ff6c6a7'
ABI='24ade8f364d00cbc6c7afc2239f13d67fef4f6822647fc4525c05cd9e64bd5eb'
ORIGINAL='4b226169737a533cf8bb1138b7e06b8ea9f24871e9037c0ed0ebe92aedf0c08f'
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SECTION='.text.tsl9_ota_tx_8a56'
SYMBOL='tsl9_ota_tx_8a56'
RAM='__tsl9v4160_data_2000b18c'
TOOLS={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f','llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
LAYOUT='OUTPUT_ARCH(riscv)\nENTRY(tsl9_ota_tx_8a56)\nSECTIONS { .text.tsl9_ota_tx_8a56 0x8A56 : { KEEP(*(.text.tsl9_ota_tx_8a56)) } /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) *(.llvm_addrsig) } }\n'
def H(b):return hashlib.sha256(b).hexdigest()
def sha(p):return H(p.read_bytes())
def need(x,m):
 if not x:raise ValueError(m)
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
def read(p):return json.loads(p.read_bytes())
def case(root,slug):return next(p for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def context(root,firmware=None):
 p=case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py';r=case(root,'v4160-ota-tx-2026-10-22')/'source-review/raw.py';need(sha(p)==PARSER and sha(r)==RAW,'immutable parser/raw field decoder')
 fw=firmware.resolve() if firmware else next(p for p in (root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin') if p.is_file());need(sha(fw)==FW,'exact validation-only original firmware');a=case(root,'v4160-ota-tx-2026-10-22')/'ABI-review/native.py';o=a.with_name('original.py');need(sha(a)==ABI and sha(o)==ORIGINAL,'independent subset/ABI rejection checker');return dict(ELF=module(p,'tx_native_ELF').ELF,raw=module(r,'tx_source_raw'),parser=p,decoder=r,firmware=fw,ABI=module(a,'tx_partial_ABI'),abi_path=a,original_path=o)
def flags(mode):
 allowed={1,2,5,6,7,*range(10,18),*range(28,32)}
 return ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',*['-ffixed-x'+str(i) for i in range(1,32) if i not in allowed],'-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17',*(['-fno-exceptions'] if mode=='cpp' else [])]
def source_pins(root):return {f'src/{n}':sha(root/MODEL/'src'/n) for n in ('tx_native.c','tx_native.h','tx_io.h')}
def recipes(root,folder,mode,tools):
 src=root/MODEL/'src/tx_native.c'
 return [[tools['clang'],'-print-resource-dir'],[tools['clang'],*flags(mode),'-c','-MD','-MF',folder/'tx_native.d','-MT','tx_native.o',src,'-o',folder/'tx_native.o'],[tools['clang'],*flags(mode),'-S','-emit-llvm',src,'-o',folder/'tx_native.ll'],[tools['llvm-objdump'],'-d',folder/'tx_native.o'],[tools['ld.lld'],'-m','elf32lriscv','--no-relax','--build-id=none','-T',folder/'component.ld',folder/'tx_native.o','-o',folder/'STRICT-MISSING-RAM.elf'],[tools['ld.lld'],'-m','elf32lriscv','--no-relax','--build-id=none','--defsym='+RAM+'=0x2000B18C','-T',folder/'component.ld',folder/'tx_native.o','-o',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf']]
def dependency_gate(root,folder,resource):
 dep=(folder/'tx_native.d').read_text().replace('\\\n',' ').replace('\\\r\n',' ');need(dep.startswith('tx_native.o:'),'actual dependency target');actual={str(Path(p).resolve()).replace('\\','/').lower() for p in dep.split(':',1)[1].split()};expected={str(p.resolve()).replace('\\','/').lower() for p in [root/MODEL/'src'/n for n in ('tx_native.c','tx_native.h','tx_io.h')]+[resource]};need(actual==expected,'exact actual native3 + compiler resource header -MD closure');return dict(target='tx_native.o',project_inputs=3,compiler_resource_headers=1)
def decode(ctx,body,base=0):
 rows=[];off=0
 while off<len(body):
  try:r=ctx['raw'].decode(body[off:],base+off)
  except ValueError:
   w=int.from_bytes(body[off:off+4],'little');need(len(body[off:off+4])==4 and w&127==0x63 and (w>>12)&7==7,'bounded additional BGEU form');imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);imm=imm-8192 if imm&4096 else imm;r=dict(PC=base+off,bytes=4,raw_hex=body[off:off+4].hex(),op='bgeu',rd=None,rs1=(w>>15)&31,rs2=(w>>20)&31,immediate=None,target=base+off+imm,memory_width=None)
  rows.append(r);off+=r['bytes']
 need(off==len(body),'exact decoded whole byte coverage');return rows
def coverage(body,text):
 rows=[]
 for line in text.splitlines():
  if re.match(r'^\s*[0-9a-f]+:',line):
   m=re.match(r'^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\s*\S.*$',line);need(m is not None,'no silently unparsed instruction row');rows.append((int(m[1],16),bytes.fromhex(m[2])))
 need(rows and rows[0][0]==0,'disassembly begins at actual object entry');off=0
 for address,raw in rows:need(address==off and len(raw) in (2,4) and body[off:off+len(raw)]==raw,'contiguous exact disassembly/ELF bytes');off+=len(raw)
 need(off==len(body),'disassembly covers exact function range');return len(rows)
def ir_gate(text):
 need('target triple = "riscv32-unknown-unknown-elf"' in text and text.count('define dso_local i32 @'+SYMBOL+'(')==1,'one RV32 i32 function')
 effects=re.findall(r'\b(load|store) volatile i(8|16|32)\b',text)
 need(effects==[('load','16'),('load','32'),('load','16'),('load','32'),('store','16'),('store','8'),('store','8'),('store','8'),('load','8'),('store','8'),('store','8'),('store','16'),('store','16'),('load','32'),('load','8')],'all15 ordered lexical volatile sites/widths (branches are not an execution trace)')
 calls=[l for l in text.splitlines() if 'asm sideeffect "jalr ra,' in l];need(len(calls)==2,'two opaque raw gate calls')
 for l in calls:need('={x10},={x11},={x12},={x13},={x15}' in l and all('~{x'+str(i)+'}' in l for i in (1,14,16,17,5,6,7,28,29,30,31)),'caller-saved gate clobbers and ambient A2/A3 outputs')
 need(len(re.findall(r'musttail call (?:noundef )?i32',text))==1 and not any('@llvm.mem' in l for l in text.splitlines()),'one actual musttail and no substituted memory libcalls')
 need(text.count('"={x3},~{memory}"()')==5,'five fresh GP IR observations')
 return dict(volatile_sites=len(effects),lexical_widths=[list(x) for x in effects],opaque_gate_calls=2,raw_ambient_A2_A3_outputs=True,musttail=True,whole_branch_semantics_proved=False)
def static_checks(root,folder,ctx):
 E=ctx['ELF'];e=E(folder/'tx_native.o');linked=E(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf');sym=next(s for s in e.symbols if s['name']==SYMBOL);body=e.function_bytes(sym);rows=decode(ctx,body);need(e.kind==1 and e.flags==1 and sym['info']==18 and sym['value']==0 and sym['size']==280,'actual ET_REL FUNC280/RVC ILP32')
 alloc=[s for s in e.sections if s['flags']&2 and s['size']];need(len(alloc)==1 and alloc[0]['name']==SECTION and alloc[0]['size']==280 and alloc[0]['flags']==6 and alloc[0]['alignment']==2,'only one actual AX280 allocation; no frame metadata or writable data')
 need([s['name'] for s in e.symbols if s['index']==0 and s['name']]==[RAM],'sole unresolved real SRAM role, no runtime helpers/ROM stubs')
 funcs=[s for s in e.symbols if s['info']&15==2];need(len(funcs)==1 and funcs[0]['name']==SYMBOL,'no hidden functions')
 rela=e.relocations;need(len(rela)==2 and [r['type'] for r in rela]==[23,24] and [r['offset'] for r in rela]==[0x74,0x78],'actual PC-relative SRAM address pair only')
 need(len(rows)==96 and coverage(body,(folder/'disassembly.log').read_text())==96,'whole96 instruction range')
 starts={r['PC'] for r in rows};need(all(r['target'] in starts for r in rows if r['target'] is not None),'all direct CFG targets are actual instruction boundaries')
 need(not any(r['rd'] in {3,4,17,*range(20,28)} for r in rows),'no GP/TP/A7/unrelated saved-register destination writes')
 transfers=[(r['PC'],r['rd'],r['rs1']) for r in rows if r['op']=='jalr'];need(transfers==[(0x38,1,15),(0x62,1,15),(0xd8,0,1),(0x116,0,6)],'two compressed gate links / fresh failure RET / terminal no-link T1')
 need([(r['PC'],r['rs2'],r['immediate']) for r in rows if r['op']=='sw' and r['rs1']==2]==[(2,1,28),(4,8,24),(6,9,20),(8,18,16),(10,19,12)],'actual compiler frame save order (different from original)')
 need(not any(r['rd'] in (12,13) for r in rows if 0x44<=r['PC']<0x62),'second gate ambient A2/A3 not overwritten on actual fallback block')
 need(rows[0]['op']=='addi' and rows[0]['rd']==2 and rows[0]['immediate']==-32,'actual compiler frame is before guard: explicit gap')
 attrs=e.data(e.byname['.riscv.attributes']);need(b'rv32i' in attrs and b'_m' in attrs and b'_a' in attrs and b'_c' in attrs and b'zicsr' in attrs,'actual object ISA attributes')
 lalloc=[s for s in linked.sections if s['flags']&2 and s['size']];need(linked.kind==2 and len(lalloc)==1 and lalloc[0]['name']==SECTION and lalloc[0]['address']==0x8a56 and lalloc[0]['size']==280 and lalloc[0]['flags']==6,'component-only linked extent')
 need(not linked.relocations and not any(s['index']==0 and s['name'] for s in linked.symbols),'no unresolved link symbols')
 rs=next(s for s in linked.symbols if s['name']==RAM);need(rs['index']==65521 and rs['value']==0x2000b18c,'numeric ABS SRAM witness only, not storage/provider')
 lb=linked.data(lalloc[0]);need(body[:0x74]==lb[:0x74] and body[0x7c:]==lb[0x7c:],'only PC-relative link fixups changed')
 w0=int.from_bytes(lb[0x74:0x78],'little');w1=int.from_bytes(lb[0x78:0x7c],'little');imm=w1>>20;imm=imm-4096 if imm&2048 else imm;need((0x8a56+0x74+(w0&0xfffff000)+imm)&0xffffffff==0x2000b18c,'actual encoded SRAM numeric target')
 original=ctx['firmware'].read_bytes()[0xa56:0xb6e];ctx['raw'].validate(original);diff=[dict(offset=i,original=a,compiled=b) for i,(a,b) in enumerate(zip(original,lb)) if a!=b];need(diff,'do not call this byte-exact original')
 return dict(passed=True,actual_bytes=280,actual_instructions=96,original_bytes=280,original_extent_fits=True,linked_entry=0x8a56,linked_end=0x8b6e,code_sha256=H(body),linked_code_sha256=H(lb),original_byte_differences=diff,IR=ir_gate((folder/'tx_native.ll').read_text()),object_relocations=2,strict_missing_RAM_rejected=True,numeric_RAM_witness_only=True,original_guard_before_frame=False,original_save_order=False,original_interleaved_success_restores=False,whole_original_ABI_admitted=False,full_GPR_prefix=False,arbitrary_callee_SP_preservation_proved=False,full_image_integration=False,physical_compatibility=False,hardware=False,RV32_execution=False)
def controls(root,folder,ctx):
 E=ctx['ELF'];e=E(folder/'tx_native.o');body=e.data(e.byname[SECTION]);ir=(folder/'tx_native.ll').read_text();dis=(folder/'disassembly.log').read_text();out=[]
 for name,fn in [('disassembly_gap',lambda:coverage(body,'\n'.join(l for l in dis.splitlines() if not re.match(r'\s*38:',l)))),('disassembly_truncation',lambda:coverage(body,'\n'.join(l for l in dis.splitlines() if not re.match(r'\s*116:',l)))),('volatile_width',lambda:ir_gate(ir.replace('store volatile i16 0','store volatile i32 0',1))),('missing_tail',lambda:ir_gate(ir.replace('musttail call','tail call',1))),('gate_A2_output',lambda:ir_gate(ir.replace('={x12},={x13}','={x14},={x13}',1)))]:
  try:fn()
  except (ValueError,KeyError,StopIteration):out.append(dict(name=name,rejected=True));continue
  raise ValueError('control unexpectedly accepted '+name)
 return out
def verify(root,folder,mode,tool_dir,firmware=None):
 folder.mkdir(parents=True);ctx=context(root,firmware);tools={n:next(p for p in (tool_dir/(n+'.exe'),tool_dir/n) if p.is_file()) for n in TOOLS};need(all(sha(tools[n])==pin for n,pin in TOOLS.items()),'actual pinned local LLVM tools');runner=sha(Path(__file__));source=source_pins(root);commands=[]
 def run(label,argv,expected=0):
  x=subprocess.run([str(a) for a in argv],cwd=folder,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr);commands.append(dict(label=label,argv=[str(a) for a in argv],exit=x.returncode,log=log.name,log_sha256=sha(log)));need((x.returncode==0) if expected==0 else x.returncode!=0,'actual command status '+label);return x
 resource=Path(run('resource-dir',[tools['clang'],'-print-resource-dir']).stdout.decode().strip()).resolve()/'include/stdint.h';rp=sha(resource);need(rp=='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34','actual measured compiler resource stdint header')
 src=root/MODEL/'src/tx_native.c';run('compile',[tools['clang'],*flags(mode),'-c','-MD','-MF',folder/'tx_native.d','-MT','tx_native.o',src,'-o',folder/'tx_native.o']);run('IR',[tools['clang'],*flags(mode),'-S','-emit-llvm',src,'-o',folder/'tx_native.ll']);run('disassembly',[tools['llvm-objdump'],'-d',folder/'tx_native.o']);(folder/'component.ld').write_bytes(LAYOUT.encode())
 strict=[tools['ld.lld'],'-m','elf32lriscv','--no-relax','--build-id=none','-T',folder/'component.ld',folder/'tx_native.o','-o',folder/'STRICT-MISSING-RAM.elf'];run('strict-missing-RAM',strict,1);need(RAM in (folder/'strict-missing-RAM.log').read_text() and not (folder/'STRICT-MISSING-RAM.elf').exists(),'missing SRAM provider strict failure')
 run('numeric-address-witness',[tools['ld.lld'],'-m','elf32lriscv','--no-relax','--build-id=none','--defsym='+RAM+'=0x2000B18C','-T',folder/'component.ld',folder/'tx_native.o','-o',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'])
 checks=static_checks(root,folder,ctx);negative=controls(root,folder,ctx);independent=ctx['ABI'].inspect_native(root,folder,ctx['firmware']);need(independent['checked_subset_passed'] and not independent['original_ABI_admitted'],'independent subset pass with original ABI rejected')
 dependencies=dependency_gate(root,folder,resource);need([c['argv'] for c in commands]==[[str(x) for x in a] for a in recipes(root,folder,mode,tools)],'exact actual native-only six recipes')
 need(source==source_pins(root) and runner==sha(Path(__file__)) and rp==sha(resource) and all(sha(tools[n])==pin for n,pin in TOOLS.items()),'stable sources/runner/resource/tools before-after')
 need(sha(ctx['parser'])==PARSER and sha(ctx['decoder'])==RAW and sha(ctx['abi_path'])==ABI and sha(ctx['original_path'])==ORIGINAL and sha(ctx['firmware'])==FW,'stable semantic evidence dependencies before-after')
 r=dict(schema='TSL9-OTA-TX-partial-native-v1',passed=True,mode=mode,checks=checks,independent_static_subset=independent,controls=negative,dependencies=dependencies,commands=commands,source_sha256=source,runner_sha256=runner,parser_sha256=PARSER,decoder_sha256=RAW,independent_checker_sha256=ABI,firmware_sha256=FW,tools={n:dict(path=str(p),sha256=TOOLS[n]) for n,p in tools.items()},resource=dict(path=str(resource),resource_relative='include/stdint.h',sha256=rp),artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},RV32_execution=False,ISA_emulation=False,network=False)
 write(folder/'verification.json',r);return dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),checks=checks)
def replay(root,receipt,firmware=None):
 r=read(receipt);folder=receipt.parent;ctx=context(root,firmware);need(r['passed'] and r['mode'] in ('c','cpp') and r['runner_sha256']==sha(Path(__file__)) and r['source_sha256']==source_pins(root),'native current source/runner identity')
 for n,pin in r['artifacts'].items():p=(folder/n).resolve();need(p.is_relative_to(folder.resolve()) and p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'],'actual native artifact '+n)
 need(r['parser_sha256']==PARSER and r['decoder_sha256']==RAW and r['firmware_sha256']==FW,'immutable semantic inputs')
 for n,pin in r['tools'].items():need(pin['sha256']==TOOLS[n] and sha(Path(pin['path']))==pin['sha256'],'actual tool identity')
 need(sha(Path(r['resource']['path']))==r['resource']['sha256']=='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34','actual resource header identity')
 labels=['resource-dir','compile','IR','disassembly','strict-missing-RAM','numeric-address-witness'];need([c['label'] for c in r['commands']]==labels,'exact ordered native-only command chain')
 need([c['argv'] for c in r['commands']]==[[str(x) for x in a] for a in recipes(root,folder,r['mode'],{n:Path(p['path']) for n,p in r['tools'].items()})],'exact actual native source/profile/link command recipes')
 resource=Path(r['commands'][0]['argv'][0]).parent
 need(str(Path((folder/'resource-dir.log').read_text().strip())/'include/stdint.h')==r['resource']['path'],'resource header follows actual Clang query log');need(dependency_gate(root,folder,Path(r['resource']['path']))==r['dependencies'],'fresh actual dependency rule/source/header replay')
 for c in r['commands']:need(sha(folder/c['log'])==c['log_sha256'] and ((c['exit']!=0) if c['label']=='strict-missing-RAM' else c['exit']==0),'actual command logs/status')
 need((folder/'component.ld').read_bytes()==LAYOUT.encode() and RAM in (folder/'strict-missing-RAM.log').read_text() and not (folder/'STRICT-MISSING-RAM.elf').exists(),'actual strict missing-provider/link layout')
 checks=static_checks(root,folder,ctx);need(checks==r['checks'] and controls(root,folder,ctx)==r['controls'],'fresh static artifact/control replay');need(r['independent_checker_sha256']==ABI and ctx['ABI'].inspect_native(root,folder,ctx['firmware'])==r['independent_static_subset'],'fresh independent seven-machine-control subset and ABI rejection replay');return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),checks=checks,controls=len(r['controls'])+len(r['independent_static_subset']['operand_controls']),RV32_execution=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--language',choices=['c','cpp','both']);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
 if a.replay:need(a.tool_dir is None and a.build_root is None and a.language is None,'replay rejects build-only tool/language/output options');print(json.dumps(replay(root,a.replay.resolve(),a.firmware)));return
 language=a.language or 'both';need(a.tool_dir is not None,'explicit local LLVM --tool-dir');base=a.build_root.resolve() if a.build_root else root/MODEL/'build'/('native-'+uuid.uuid4().hex);need(base.is_relative_to(root) and not base.exists(),'create-only new project build root');print(json.dumps(dict(passed=True,results=[verify(root,base/m,m,a.tool_dir.resolve(),a.firmware) for m in (['c','cpp'] if language=='both' else [language])],RV32_execution=False)))
if __name__=='__main__':main()
