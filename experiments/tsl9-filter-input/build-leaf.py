"""Create-only offline compiler/linker measurements. Never execute emitted code."""
from pathlib import Path
import argparse, hashlib, json, os, struct, subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RANGES=[('tsl9_filter_program_18ba2',0x18BA2,50),('tsl9_filter_scale16_18bd4',0x18BD4,42),
('tsl9_filter_fr2_18bfe',0x18BFE,6),('tsl9_filter_mode_18c04',0x18C04,14),
('tsl9_filter_mode_mask_18c12',0x18C12,6),('tsl9_filter_mode_store_18c18',0x18C18,4),
('tsl9_filter_fifo_18c1c',0x18C1C,14),('tsl9_filter_fifo0_18c2a',0x18C2A,10),
('tsl9_filter_activation_18c34',0x18C34,8),('tsl9_filter_activate_18c3c',0x18C3C,14),
('tsl9_filter_finish_18c4a',0x18C4A,16),('tsl9_filter_scale_test_18c5a',0x18C5A,4),
('tsl9_filter_scale32_18c5e',0x18C5E,44),('tsl9_filter_mode_list_18c8a',0x18C8A,8),
('tsl9_filter_fifo_test_18c92',0x18C92,6),('tsl9_filter_fifo1_18c98',0x18C98,12)]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def jout(p,v): p.write_bytes((json.dumps(v,indent=2,sort_keys=True)+'\n').encode('utf-8'))
def elf(path):
 b=Path(path).read_bytes(); assert b[:6]==b'\x7fELF\x01\x01'
 h=struct.unpack_from('<16sHHIIIIIHHHHHH',b,0)
 assert h[2]==243
 sh=[struct.unpack_from('<IIIIIIIIII',b,h[6]+i*h[11])for i in range(h[12])]
 names=b[sh[h[13]][4]:sh[h[13]][4]+sh[h[13]][5]]
 def string(s,n): return s[n:s.index(0,n)].decode()
 sections=[]
 for i,s in enumerate(sh):
  sections.append(dict(index=i,name=string(names,s[0])if s[0] else '',type=s[1],flags=s[2],address=s[3],offset=s[4],size=s[5],link=s[6],info=s[7],align=s[8],entry=s[9]))
 symbols=[]; relocs=[]
 for s in sections:
  if s['type']==2:
   st=sh[s['link']];ss=b[st[4]:st[4]+st[5]]
   for off in range(s['offset'],s['offset']+s['size'],16):
    n,v,z,info,other,idx=struct.unpack_from('<IIIBBH',b,off)
    symbols.append(dict(name=string(ss,n)if n else '',value=v,size=z,bind=info>>4,type=info&15,section=idx))
  if s['type']==4:
   for off in range(s['offset'],s['offset']+s['size'],12):
    o,info,a=struct.unpack_from('<IIi',b,off)
    relocs.append(dict(section=sections[s['info']]['name'],offset=o,type=info&255,symbol=info>>8,addend=a))
 for r in relocs:r['target']=symbols[r['symbol']]['name']
 return b,sections,symbols,relocs

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--source',required=True);ap.add_argument('--trial',required=True)
 args=ap.parse_args()
 source=(HERE/args.source).resolve();assert source.is_relative_to(HERE/'src')
 folder=(HERE/'build'/args.trial).resolve();assert folder.is_relative_to(HERE/'build') and not folder.exists()
 folder.mkdir(parents=True)
 pins=json.loads((ROOT/'experiments/tsl9-record-program/spec.json').read_bytes())
 llvm=Path(os.environ['USERPROFILE'])/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin'
 for name,pin in pins['tools'].items():assert sha(llvm/name)==pin,(name,'tool drift')
 assert sha(llvm.parent/'lib/clang/18/include/stdint.h')==pins['stdint_sha256']
 firmware=ROOT/pins['firmware'];assert sha(firmware)==pins['firmware_sha256']
 original=firmware.read_bytes()[0x10BA2:0x10CA4]
 assert len(original)==258
 # Original architecture and pinned transport-a0-a6 allocator bank only.
 common=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz',
 '-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector',
 '-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections',
 '-fdata-sections','-Wall','-Wextra','-Werror']
 fixed=['-ffixed-x'+str(n)for n in range(1,32)if n not in {10,11,12,13,14,15,16}]
 text='OUTPUT_ARCH(riscv)\nENTRY(tsl9_filter_program_18ba2)\nSECTIONS {\n .filter 0x18BA2 : ALIGN(2) {\n'
 text+=''.join('  KEEP(*(.text.'+n+'))\n'for n,va,size in RANGES)
 text+=' }\n /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }\n'
 text+=' ASSERT(SIZEOF(.filter)==258,"Complete original258B")\n'
 text+=''.join(' ASSERT('+n+'=='+hex(va)+',"Original '+n+'")\n'for n,va,size in RANGES)
 text+='}\n';(folder/'nominal.ld').write_bytes(text.encode('utf-8'))
 source_before=sha(source);reports=[]
 for mode in ['c','cpp']:
  out=folder/mode;out.mkdir()
  flags=common+['-x','c'if mode=='c'else'c++','-std=c11'if mode=='c'else'-std=c++17']
  if mode=='cpp':flags+=['-fno-exceptions']
  flags+=fixed
  commands=[]
  def run(label,argv):
   r=subprocess.run([str(x)for x in argv],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   (out/(label+'.log')).write_bytes(r.stdout)
   commands.append(dict(label=label,argv=[str(x)for x in argv],exit=r.returncode,log_sha256=hashlib.sha256(r.stdout).hexdigest()))
   jout(out/'commands.json',commands)
   return r.returncode==0
  report={'mode':mode,'source':str(source.relative_to(ROOT)),'source_sha256':source_before,'profile':'transport-a0-a6',
          'tools':{n:sha(llvm/n)for n in pins['tools']},'target_execution':False,'HOST_model_execution':False,'network':False,
          'firmware_sha256':sha(firmware),'expected_range':[hex(0x18BA2),hex(0x18CA4)],'expected_sha256':hashlib.sha256(original).hexdigest()}
  ok=run('compile',[llvm/'clang.exe',*flags,'-c','-MD','-MF',out/'leaf.d','-MT','leaf.o',source,'-o',out/'leaf.o'])
  report['compile_passed']=ok
  if ok:
   run('IR',[llvm/'clang.exe',*flags,'-S','-emit-llvm',source,'-o',out/'leaf.ll'])
   run('native-read',[llvm/'llvm-objdump.exe','-dr',out/'leaf.o'])
   ob,sections,symbols,relocs=elf(out/'leaf.o')
   funcs={s['name']:s for s in symbols if s['bind']==1 and s['type']==2}
   report['regions']=[dict(name=n,expected=size,actual=funcs.get(n,{}).get('size'),nominal=hex(va))for n,va,size in RANGES]
   report['relocations']=relocs
   report['undefined']=[s['name']for s in symbols if s['section']==0 and s['name']]
   report['ABS']=[s['name']for s in symbols if s['section']==0xfff1 and s['name'] and s['bind']!=0]
   linked=run('nominal-link',[llvm/'ld.lld.exe','--no-relax','-T',folder/'nominal.ld',out/'leaf.o','-o',out/'LEAF-ONLY-NOT-FIRMWARE.elf'])
   report['nominal_link_passed']=linked
   if linked:
    run('nominal-read',[llvm/'llvm-objdump.exe','-dr',out/'LEAF-ONLY-NOT-FIRMWARE.elf'])
    eb,es,sy,rs=elf(out/'LEAF-ONLY-NOT-FIRMWARE.elf')
    sec=next(s for s in es if s['name']=='.filter')
    actual=eb[sec['offset']:sec['offset']+sec['size']]
    report['complete_original_bytes_equal']=actual==original
    report['linked_code_sha256']=hashlib.sha256(actual).hexdigest()
    report['byte_mismatches']=[{'offset':i,'va':hex(0x18BA2+i),'original':a,'compiled':v}for i,(a,v)in enumerate(zip(original,actual))if a!=v]
    assert not report['undefined'] and not report['ABS']
  assert sha(source)==source_before
  report['commands']=commands
  report['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.iterdir())if p.is_file()}
  jout(out/'measurement.json',report);reports.append(report)
 print(json.dumps([{'mode':r['mode'],'compile':r['compile_passed'],'link':r.get('nominal_link_passed'),
                   'equal':r.get('complete_original_bytes_equal'),'region_sizes':[(x['name'],x['expected'],x['actual'])for x in r.get('regions',[])if x['expected']!=x['actual']]}for r in reports]))
if __name__=='__main__':main()
