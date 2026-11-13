"""Limited offline smoke, not the seven local tests. Never run target code."""
import hashlib, io, json, os, struct, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
N='tsl9_feature_state_records_provider_105c4'
REF=bytes.fromhex('034535007115133515008280')
COMMON='--target=riscv32-unknown-elf -march=rv32imac_zicsr -mabi=ilp32 -Oz -mllvm -enable-machine-outliner=never -ffreestanding -fno-builtin -fno-stack-protector -fno-unwind-tables -fno-asynchronous-unwind-tables -mno-relax -ffunction-sections -fdata-sections -Wall -Wextra -Werror -x'.split()
FIXED=['-ffixed-x'+str(i) for i in list(range(1,10))+list(range(16,32))]
PROFILES={'c':COMMON+['c','-std=c11']+FIXED,'cpp':COMMON+['c++','-std=c++17','-fno-exceptions']+FIXED}
READ,RUN=Path.read_bytes,subprocess.run
def sha(b): return hashlib.sha256(b).hexdigest()
p=HERE/'replay.py'; source=READ(p)
if sha(source)!='83955add1f3bb60df55c4e759eae6b0b4c88c4709e49aac2dd2dfe55d2669ff7': sys.exit('replay source pin mismatch')
ns={'__file__':str(p),'__name__':'replay_smoke'}
exec(compile(source,str(p),'exec'),ns)
# Source pin fixes these tables; retain separate copies.
PINS,TOOLS=dict(ns['PINS']),dict(ns['TOOL_PINS'])
ELF={1:ns['OBJECT_SHA'],2:ns['IMAGE_SHA']}

def section(b,name):
 h=struct.unpack_from('<16sHHIIIIIHHHHHH',b)
 rows=[struct.unpack_from('<10I',b,h[6]+40*i) for i in range(h[12])]
 s=rows[h[13]]; names=b[s[4]:s[4]+s[5]]
 found=[(i,r) for i,r in enumerate(rows) if names[r[0]:].split(b'\0',1)[0]==name.encode()]
 if len(found)!=1: raise ValueError('section count')
 return h,*found[0]

class Smoke(unittest.TestCase):
 def setUp(self):
  value=os.environ.get('TSL9_NDK_BIN',''); self.tools=Path(value)
  self.assertTrue(value and self.tools.is_absolute() and self.tools.is_dir())
  self.eq=self.assertEqual; self.calls=[]; p=mock.patch('subprocess.run',side_effect=self.guard); p.start(); self.addCleanup(p.stop)
 def guard(self,argv,*args,**kw):
  self.eq(ns['PINS'],PINS); self.eq(ns['TOOL_PINS'],TOOLS)
  self.eq(args,()); self.eq(set(kw),{'cwd','env','stdin','capture_output','timeout'})
  d=Path(kw['cwd']); self.eq(d.parent,HERE)
  self.eq(kw['env']['TSL9_NDK_BIN'],str(self.tools)); self.assertIs(kw['stdin'],subprocess.DEVNULL)
  self.assertIs(kw['capture_output'],True); self.eq(kw['timeout'],60)
  cmd=list(map(str,argv)); self.assertIn('-o',cmd); out=Path(cmd[cmd.index('-o')+1]); name=out.name
  self.eq(out,d/name)
  if name=='m.o':
   self.eq(READ(d/'m.c'),b'extern unsigned absent(void); unsigned leaf(void) { return absent(); }')
   expected=[self.tools/'clang.exe',*PROFILES['c'],'-c',d/'m.c','-o',out]
  elif name=='m.elf':
   expected=[self.tools/'ld.lld.exe','--no-undefined','-e','leaf','-o',out,d/'m.o']
  elif name in {m+s for m in ('c','cpp') for s in ('.o','.elf','-negative.o','-negative.elf')}|{'owner-c.o','owner-cpp.o'}:
   mode='cpp' if 'cpp' in name else 'c'; owner=name.startswith('owner-'); neg='-negative' in name
   if name.endswith('.o'):
    src=d/('owner.c' if owner else 'leaf.c')
    extra=[] if owner else ['-Dleaf='+N,'-nostdinc']+(['-DNEGATIVE'] if neg else [])
    expected=[self.tools/'clang.exe',*PROFILES[mode],*extra,'-c',src,'-o',out]
    self.eq(sha(READ(src)),PINS['owner' if owner else 'candidate'][1])
   else:
    expected=[self.tools/'ld.lld.exe','--no-relax','--fatal-warnings','--no-undefined','-T',d/'layout.ld','-e',N,'-o',out,d/name.replace('.elf','.o')]
    self.eq((d/'layout.ld').read_text(encoding='ascii'),'PHDRS { none PT_NULL; }\nSECTIONS { .leaf 0x105c4 : { KEEP(*(.leaf)) } :none }\n')
  else: self.fail('unexpected output: '+name)
  self.eq(cmd,list(map(str,expected)))
  for name,(path,digest) in PINS.items(): self.eq(sha(READ(ROOT/path)),digest,name)
  for name,digest in TOOLS.items(): self.eq(sha(READ(self.tools/name)),digest,name)
  self.calls.append(cmd); return RUN(argv,*args,**kw)
 def test_build(self):
  captured={}; guarded=subprocess.run; eq=self.eq
  def capture(argv,*args,**kw):
   cmd=list(map(str,argv)); out=Path(cmd[cmd.index('-o')+1]); name=out.name
   p=guarded(argv,*args,**kw); eq((p.returncode,p.stdout,p.stderr),(0,b'',b''))
   self.assertNotIn(name,captured); captured[name]=(cmd,READ(out)); return p
  rejected=ns['rejected']; rejection_calls=[]
  def track_rejected(fn,reason):
   calls=[]
   def tracked():
    calls.append(True); return fn()
   rejected(tracked,reason); rejection_calls.append((reason,len(calls)))
  with mock.patch.dict(ns,{'rejected':track_rejected}),mock.patch('subprocess.run',side_effect=capture),mock.patch('sys.stdout',new_callable=io.StringIO) as out: rc=ns['main']([])
  eq(rejection_calls,[('target bytes differ',1)]*4)
  report=json.loads(out.getvalue()); eq((rc,report['status'],report['passed'],report['checks_passed']),(1,'INCOMPLETE_FAIL_CLOSED',False,True))
  eq(set(report['cases']),{'c','cpp'})
  eq(set(captured),{m+s for m in ('c','cpp') for s in ('.o','.elf','-negative.o','-negative.elf')}|{'owner-c.o','owner-cpp.o'})
  for mode in ('c','cpp'):
   case=report['cases'][mode]
   for suffix in ('','-negative'):
    for typ,ext in ((1,'.o'),(2,'.elf')):
     cmd,blob=captured[mode+suffix+ext]; self.check_elf(blob,typ,False,suffix)
     if not suffix: eq(case['object' if typ==1 else 'linked']['sha256'],ELF[typ])
   self.check_elf(captured['owner-'+mode+'.o'][1],1,True,'')
 def check_elf(self,blob,typ,owner,suffix):
  h,i,r=section(blob,'.text.'+N if owner else '.leaf'); addr=0 if typ==1 else 0x105c4
  self.eq((h[1],h[2],r[1],r[2],r[3],r[5]),(typ,243,1,6,addr,12))
  self.eq(blob[r[4]:r[4]+12],bytes.fromhex('034535006d15133515008280') if suffix else REF)
  if suffix:
   with self.assertRaises(ValueError) as error: ns['inspect'](blob,typ,owner)
   self.eq(str(error.exception),'target bytes differ')
   return
  if not owner: self.eq(sha(blob),ELF[typ])
  for pos,value,reason in ((r[4],blob[r[4]]^1,'target bytes differ'),(h[6]+40*i+8,3,'target section metadata')):
   bad=bytearray(blob); bad[pos]=value
   with self.assertRaisesRegex(ValueError,'^'+reason+'$'): ns['inspect'](bad,typ,owner)
 def test_missing_changed(self):
  for name,(rel,_) in PINS.items():
   for changed in (False,True):
    def read(path):
     if path==ROOT/rel:
      if not changed: raise FileNotFoundError('controlled missing')
      return READ(path)+b'changed'
     return READ(path)
    with mock.patch.object(Path,'read_bytes',read),mock.patch('sys.stdout',new_callable=io.StringIO) as out:
     self.eq(ns['main']([]),1); r=json.loads(out.getvalue())
     self.eq((r['status'],r['passed'],r['checks_passed']),('INCOMPLETE_FAIL_CLOSED',False,False))
     self.assertIn(name+' pin mismatch' if changed else 'FileNotFoundError',r['error']); self.eq(self.calls,[])
 def test_link_failure(self):
  with tempfile.TemporaryDirectory(dir=HERE) as tmp:
   d=Path(tmp); src=d/'m.c'; obj=d/'m.o'; image=d/'m.elf'
   src.write_bytes(b'extern unsigned absent(void); unsigned leaf(void) { return absent(); }')
   env={k:os.environ[k] for k in ('SystemRoot','WINDIR') if k in os.environ}; env.update(TEMP=tmp,TMP=tmp,TMPDIR=tmp,TSL9_NDK_BIN=str(self.tools))
   ns['command']([self.tools/'clang.exe',*PROFILES['c'],'-c',src,'-o',obj],d,env)
   p=subprocess.run([self.tools/'ld.lld.exe','--no-undefined','-e','leaf','-o',image,obj],cwd=d,env=env,stdin=subprocess.DEVNULL,capture_output=True,timeout=60)
   self.assertNotEqual(p.returncode,0); self.assertIn(b'undefined symbol: absent',p.stderr); self.assertFalse(image.exists())

if __name__=='__main__':
 if sys.argv[1:]==['--worker']:
  output=io.StringIO()
  r=unittest.TextTestRunner(stream=output,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Smoke))
  if not r.wasSuccessful() or r.testsRun!=3 or r.skipped:
   sys.stderr.write(output.getvalue()); sys.exit(1)
  sys.exit(0)
 if sys.argv[1:]: sys.exit('no arguments accepted')
 smoke_source=READ(Path(__file__).resolve())
 worker="import sys; p=sys.argv[1]; sys.argv=[p,'--worker']; exec(compile(sys.stdin.buffer.read(),p,'exec'),{'__file__':p,'__name__':'__main__'})"
 for opt in ([],['-O']):
  p=RUN([sys.executable,'-I','-B',*opt,'-c',worker,str(Path(__file__).resolve())],input=smoke_source,capture_output=True,timeout=300)
  label='optimized' if opt else 'normal'
  if p.returncode or p.stdout or p.stderr:
   sys.stderr.buffer.write(p.stdout+p.stderr)
   sys.exit(label+' smoke failed')
  print(label+' smoke passed')
