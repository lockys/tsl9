"""Compile/link/read the entire160B input plus genuine258B leaf; never run it."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def jout(p,v):p.write_bytes((json.dumps(v,indent=2,sort_keys=True)+'\n').encode())
INPUT=[('tsl9_channel_external_128fe',0x128FE,6),('tsl9_filter_input_frame_12904',0x12904,6),
('tsl9_filter_input_fill_1290a',0x1290A,22),('tsl9_filter_input_cap_12920',0x12920,12),
('tsl9_filter_input_small_1292c',0x1292C,4),('tsl9_filter_input_copy_12930',0x12930,12),
('tsl9_filter_input_loop_init_1293c',0x1293C,10),('tsl9_filter_input_loop_12946',0x12946,68),
('tsl9_filter_input_next_1298a',0x1298A,4),('tsl9_filter_input_finish_1298e',0x1298E,16)]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',required=True);ap.add_argument('--trial',required=True)
 a=ap.parse_args();source=(HERE/a.source).resolve();assert source.is_relative_to(HERE/'src')
 folder=(HERE/'build'/a.trial).resolve();assert folder.is_relative_to(HERE/'build')and not folder.exists();folder.mkdir(parents=True)
 leaf=runpy.run_path(str(HERE/'build-leaf.py'),run_name='data_reader_only');parse=leaf['elf'];LR=leaf['RANGES']
 pins=json.loads((ROOT/'experiments/tsl9-record-program/spec.json').read_bytes())
 llvm=Path(os.environ['USERPROFILE'])/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin'
 for n,v in pins['tools'].items():assert sha(llvm/n)==v
 assert sha(llvm.parent/'lib/clang/18/include/stdint.h')==pins['stdint_sha256']
 firmware=ROOT/pins['firmware'];assert sha(firmware)==pins['firmware_sha256'];b=firmware.read_bytes()
 text='OUTPUT_ARCH(riscv)\nENTRY(tsl9_channel_external_128fe)\nSECTIONS {\n'
 for section,va,rs in [('input',0x128FE,INPUT),('filter',0x18BA2,LR)]:
  text+=' .'+section+' '+hex(va)+' : ALIGN(2) {\n'+''.join('  KEEP(*(.text.'+n+'))\n'for n,v,z in rs)+' }\n'
  text+=' ASSERT(SIZEOF(.'+section+')=='+str(sum(z for n,v,z in rs))+',"Complete '+section+'")\n'
  text+=''.join(' ASSERT('+n+'=='+hex(v)+',"Original '+n+'")\n'for n,v,z in rs)
 text+=' /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }\n}\n'
 (folder/'nominal.ld').write_bytes(text.encode());before=sha(source);reports=[]
 for mode in ['c','cpp']:
  out=folder/mode;out.mkdir();commands=[]
  def run(label,argv):
   r=subprocess.run([str(x)for x in argv],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   (out/(label+'.log')).write_bytes(r.stdout)
   commands.append(dict(label=label,argv=[str(x)for x in argv],exit=r.returncode,log_sha256=hashlib.sha256(r.stdout).hexdigest()))
   jout(out/'commands.json',commands);return r.returncode==0
  flags=pins['flags'][mode]
  assert '-ffixed-x16'in flags and '-ffixed-x15'not in flags
  provider=HERE/'build/leaf-v2'/mode/'leaf.o'
  previous=json.loads((provider.parent/'measurement.json').read_bytes())
  assert sha(HERE/'src/filter_leaf.v2.c')==previous['source_sha256']
  assert sha(provider)==previous['artifacts']['leaf.o']['sha256']
  assert previous['complete_original_bytes_equal'] is True
  result={'source':str(source.relative_to(ROOT)),'source_sha256':before,'mode':mode,'profile':'queue-consumer-a0-a5 (identical fixed flags from record spec)',
          'tools':{n:sha(llvm/n)for n in pins['tools']},'flags':flags,'leaf_provider':str(provider.relative_to(ROOT)),
          'leaf_provider_sha256':sha(provider),'leaf_source_sha256':previous['source_sha256'],
          'target_executed':False,'HOST_model_executed':False,'network':False,'firmware_ready':False}
  ok=run('compile',[llvm/'clang.exe',*flags,'-c','-MD','-MF',out/'input.d','-MT','input.o',source,'-o',out/'input.o'])
  result['compile_passed']=ok
  if ok:
   run('IR',[llvm/'clang.exe',*flags,'-S','-emit-llvm',source,'-o',out/'input.ll'])
   run('native-read',[llvm/'llvm-objdump.exe','-dr',out/'input.o'])
   ob,os_,sy,rs=parse(out/'input.o');functions={s['name']:s for s in sy if s['type']==2 and s['bind']==1}
   result['input_regions']=[dict(name=n,expected=z,actual=functions.get(n,{}).get('size'),VA=hex(v))for n,v,z in INPUT]
   result['input_undefined']=[s['name']for s in sy if s['section']==0 and s['name']]
   result['input_relocations']=rs
   linked=run('nominal-link',[llvm/'ld.lld.exe','--no-relax','-T',folder/'nominal.ld',out/'input.o',provider,'-o',out/'INPUT-LEAF-ONLY-NOT-FIRMWARE.elf'])
   result['nominal_link_passed']=linked
   if linked:
    run('nominal-read',[llvm/'llvm-objdump.exe','-dr',out/'INPUT-LEAF-ONLY-NOT-FIRMWARE.elf'])
    eb,es,sy,rs=parse(out/'INPUT-LEAF-ONLY-NOT-FIRMWARE.elf')
    result['ranges']=[]
    for name,lo,hi in [('input',0x128FE,0x1299E),('filter',0x18BA2,0x18CA4)]:
     sec=next(s for s in es if s['name']=='.'+name);actual=eb[sec['offset']:sec['offset']+sec['size']];original=b[lo-0x8000:hi-0x8000]
     result['ranges'].append(dict(name=name,VA=[hex(lo),hex(hi)],bytes=len(actual),equal=actual==original,code_sha256=hashlib.sha256(actual).hexdigest(),
           mismatches=[{'offset':i,'VA':hex(lo+i),'original':x,'compiled':y}for i,(x,y)in enumerate(zip(original,actual))if x!=y]))
    result['linked_undefined']=[s['name']for s in sy if s['section']==0 and s['name']]
    result['global_ABS']=[s['name']for s in sy if s['section']==0xfff1 and s['bind']!=0]
    result['strong_FUNC']=[s for s in sy if s['bind']==1 and s['type']==2]
    result['complete_418B_original_equal']=all(x['equal']for x in result['ranges'])
    assert not result['linked_undefined']and not result['global_ABS']
  assert sha(source)==before
  result['commands']=commands;result['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(out.iterdir())if p.is_file()}
  jout(out/'measurement.json',result);reports.append(result)
 print(json.dumps([dict(mode=r['mode'],compile=r['compile_passed'],link=r.get('nominal_link_passed'),equal=r.get('complete_418B_original_equal'),
          size_differences=[x for x in r.get('input_regions',[])if x['expected']!=x['actual']])for r in reports]))
if __name__=='__main__':main()
