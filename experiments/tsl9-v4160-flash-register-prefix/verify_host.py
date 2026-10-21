"""Compile and run only synthetic host C/C++ providers; firmware is never executed."""
import argparse,hashlib,importlib.util,json,os,struct,subprocess,sys,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_bytes((json.dumps(d,indent=2)+'\n').encode())

def host_architecture():
    """Derive runnable process architecture from Python itself, never the test artifact."""
    data=Path(sys.executable).read_bytes();bits=struct.calcsize('P')*8
    if os.name=='nt' and data[:2]==b'MZ':
        need(len(data)>=64,'current Python DOS header');offset=struct.unpack_from('<I',data,60)[0]
        need(offset>=64 and offset+26<=len(data) and data[offset:offset+4]==b'PE\0\0','current Python PE header bounds')
        machine=struct.unpack_from('<H',data,offset+4)[0];magic=struct.unpack_from('<H',data,offset+24)[0]
        need(magic==(0x10b if bits==32 else 0x20b),'current Python PE matches runtime pointer width');arch={0x8664:'x86_64',0xaa64:'arm64',0x14c:'x86'}.get(machine)
    elif sys.platform.startswith('linux') and data[:4]==b'\x7fELF':
        need(len(data)>=(52 if bits==32 else 64) and data[4]==(1 if bits==32 else 2) and data[5]==(1 if sys.byteorder=='little' else 2),'current Python ELF encoding/runtime width')
        arch={62:'x86_64',183:'arm64',3:'x86'}.get(int.from_bytes(data[18:20],sys.byteorder))
    elif sys.platform=='darwin' and data[:4] in (b'\xcf\xfa\xed\xfe',b'\xce\xfa\xed\xfe'):
        need(len(data)>=(32 if bits==64 else 28) and data[:4]==(b'\xcf\xfa\xed\xfe' if bits==64 else b'\xce\xfa\xed\xfe') and sys.byteorder=='little','current Python thin Mach-O encoding/runtime width')
        arch={0x1000007:'x86_64',0x100000c:'arm64',7:'x86'}.get(int.from_bytes(data[4:8],'little'))
    else:raise ValueError('unsupported current Python executable format; thin Mach-O required on macOS')
    need(arch is not None and bits==(32 if arch=='x86' else 64),'supported current Python architecture and pointer width')
    return arch

def host_executable(path):
    """Read headers only; reject unknown or non-native executable formats before launch."""
    path=Path(path);data=path.read_bytes();arch=host_architecture()
    if data[:2]==b'MZ':
        need(os.name=='nt' and len(data)>=64,'PE requires matching Windows host and complete DOS header')
        offset=struct.unpack_from('<I',data,60)[0]
        need(offset>=64 and offset+26<=len(data) and data[offset:offset+4]==b'PE\0\0','bounded complete PE header')
        value=struct.unpack_from('<H',data,offset+4)[0];size=struct.unpack_from('<H',data,offset+20)[0]
        need(size>=2 and offset+24+size<=len(data),'bounded PE optional header')
        need(value=={'x86_64':0x8664,'arm64':0xaa64,'x86':0x14c}[arch],'PE machine must match local host')
        magic=struct.unpack_from('<H',data,offset+24)[0];need(magic==(0x10b if arch=='x86' else 0x20b),'PE width must match host')
        format_name='PE';width=32 if magic==0x10b else 64
    elif data[:4]==b'\x7fELF':
        need(len(data)>=20,'complete ELF identity header');value=int.from_bytes(data[18:20], 'little' if data[5]==1 else 'big')
        need(value!=243,'RISC-V ELF is prohibited from host execution')
        width=32 if data[4]==1 else 64
        need(sys.platform.startswith('linux') and data[4] in (1,2) and data[5]==(1 if sys.byteorder=='little' else 2),'ELF requires matching Linux host encoding')
        need(len(data)>=(52 if width==32 else 64),'complete ELF header')
        need(value=={'x86_64':62,'arm64':183,'x86':3}[arch] and width==(32 if arch=='x86' else 64),'ELF machine/width must match local host')
        need(int.from_bytes(data[16:18],sys.byteorder) in (2,3),'ELF executable/shared object type')
        format_name='ELF'
    elif data[:4] in (b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xce\xfa\xed\xfe',b'\xfe\xed\xfa\xce'):
        little=data[:4] in (b'\xcf\xfa\xed\xfe',b'\xce\xfa\xed\xfe');order='little' if little else 'big';width=64 if data[:4] in (b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf') else 32
        need(sys.platform=='darwin' and order==sys.byteorder and len(data)>=(32 if width==64 else 28),'thin Mach-O requires matching macOS host encoding and complete header')
        value=int.from_bytes(data[4:8],order)
        need(value=={'x86_64':0x1000007,'arm64':0x100000c,'x86':7}[arch] and width==(32 if arch=='x86' else 64),'Mach-O CPU/width must match local host')
        need(int.from_bytes(data[12:16],order)==2,'Mach-O executable type');format_name='Mach-O-thin'
    else:raise ValueError('unrecognized host executable format')
    return dict(format=format_name,machine=value,bits=width,host_arch=arch,host_platform=sys.platform,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def host_tools(root):
    p=root/'scripts/portable_verify.py';s=importlib.util.spec_from_file_location('flash_host_compiler',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def source_evidence(root):
    scope=next(p for p in (root/'analysis/v4160-flash-native-2026-10-22/source',root/'apk-analysis/tsl9-v4160-flash-native-2026-10-22/source') if p.is_dir())
    seal=scope/'seal.json';need(sha(seal)=='dff9a51e3b59bbdddd150dde37614753bb3c3b440d7bde2f9402c8b6e9a2bce4','sealed ID2966 source contracts')
    pins={str(seal):sha(seal)}
    for row in read(seal)['members']:need(sha(scope/row['path'])==row['sha256'],'sealed original source proof member');pins[str(scope/row['path'])]=row['sha256']
    proof=read(scope/'source-proof.json');need(proof['source_bytes']==262 and proof['instruction_count']==99 and len(proof['owners'])==6,'six original functions262B99instructions evidence')
    return pins
def execute(args,folder,label,env,expect=0,host_test=False):
    guard=host_executable(args[0]) if host_test else None
    p=subprocess.run([str(x) for x in args],cwd=folder,env=env,capture_output=True,timeout=120);raw=p.stdout+p.stderr;(folder/(label+'.log')).write_bytes(raw)
    need(p.returncode==0 if expect==0 else p.returncode!=0,label+' failed; inspect '+str(folder/(label+'.log')))
    if host_test:need(host_executable(args[0])==guard,'stable host executable before/after launch')
    return dict(argv=[str(x) for x in args],exit=p.returncode,log=label+'.log',log_sha256=sha(folder/(label+'.log')),host_executable_guard=guard),p.stdout.decode('utf-8',errors='replace')
def compile_args(compiler,msvc,mode,source,folder,output):
    files=[source/'src/flash_native.c',source/'src/host_io.c',source/'tests/test_flash.c']
    if msvc:return [compiler,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DTSL9_FLASH_HOST_TEST=1','/I'+str(source/'src'),'/Fo'+str(folder)+os.sep,*files,'/Fe'+str(output),'/link','/INCREMENTAL:NO']
    return [compiler,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-DTSL9_FLASH_HOST_TEST=1','-I',source/'src',*files,'-o',output]
def controls(model,folder,compiler,msvc,mode,env):
    mutations=[
      ('wrong_unlock_key','src/flash_native.c','FN_WRITE(0x18ea8u,FN_ADD(base,FN_K(4u)),key1);','FN_WRITE(0x18ea8u,FN_ADD(base,FN_K(4u)),key2);'),
      ('wrong_word_stride','src/flash_native.c','offset+=4u;','offset+=8u;'),
      ('stale_source_word','src/flash_native.c','FN_SOURCE_ADDRESS(source,offset)','FN_SOURCE_ADDRESS(source,0u)'),
      ('wrong_source_frame_slot','src/native_io.h','FN_ADD(h->regs[2],FN_K(12u)),source)','FN_ADD(h->regs[2],FN_K(16u)),source)'),
      ('wrong_CSR_mask','src/host_io.c','h->regs[8]=fn_constant(136u);','h->regs[8]=fn_constant(64u);'),
      ('cleanup_after_unknown_poll','src/native_io.h','#define FN_CHECK_FLOW() do { if(h->flow!=FN_RETURNED) return fn_failed(); } while(0)','#define FN_CHECK_FLOW() ((void)0)')]
    rows=[]
    for name,file,old,new in mutations:
        base=folder/'compiled-controls'/name;base.mkdir(parents=True)
        for directory in ('src','tests'):
            (base/directory).mkdir()
            for path in (model/directory).glob('*'):
                if path.is_file():(base/directory/path.name).write_bytes(path.read_bytes())
        target=base/file;text=target.read_text(encoding='utf-8');need(text.count(old)==1,'one bounded source mutation '+name);target.write_bytes(text.replace(old,new).encode())
        exe=base/('negative.exe' if os.name=='nt' else 'negative');compile_command,_=execute(compile_args(compiler,msvc,mode,base,base,exe),base,'compile',env)
        test_command,output=execute([exe],base,'tests',env,1,host_test=True);need('failure line' in (base/'tests.log').read_text(encoding='utf-8',errors='replace'),'negative fails a semantic assertion, not process launch')
        rows.append(dict(case=name,compiled=True,rejected=True,mutation_file=file,old=old,new=new,commands=[compile_command,test_command],executable_sha256=sha(exe),artifacts={p.relative_to(base).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in base.rglob('*') if p.is_file()}))
    return rows
def verify(root,folder,mode):
    folder.mkdir(parents=True);model=root/'experiments/tsl9-v4160-flash-register-prefix';runner_pin=sha(Path(__file__));helper_pin=sha(root/'scripts/portable_verify.py');tools=host_tools(root);compiler,env,msvc=tools.compiler_for(mode)
    # Tool temporary outputs stay in this authorized create-only build folder.
    env=dict(env);env['TMP']=str(folder);env['TEMP']=str(folder)
    source_pins={p.relative_to(model).as_posix():sha(p) for d in ('src','tests') for p in (model/d).glob('*') if p.is_file()};compiler_pin=sha(compiler);evidence_pins=source_evidence(root)
    out=folder/('host-tests.exe' if os.name=='nt' else 'host-tests');c,_=execute(compile_args(compiler,msvc,mode,model,folder,out),folder,'compile',env)
    run,text=execute([out],folder,'tests',env,host_test=True);result=json.loads(text.strip())
    need(result==dict(passed=True,groups=5,cases=481,checks=247191,synthetic_provider=True,RV32_execution=False),'exact frozen five-group directed provider/prefix coverage')
    negatives=controls(model,folder,compiler,msvc,mode,env)
    for n,pin in source_pins.items():need(sha(model/n)==pin,'stable host source '+n)
    need(sha(compiler)==compiler_pin,'stable actual host compiler')
    need(sha(Path(__file__))==runner_pin and sha(root/'scripts/portable_verify.py')==helper_pin,'stable host runner/compiler-selection helper before and after execution')
    need(source_evidence(root)==evidence_pins,'stable sealed original source evidence before/after host compilation')
    r=dict(schema='ID2966-readable-flash-host-v1',passed=True,mode=mode,tests=result,source_sha256=source_pins,source_evidence_pins=evidence_pins,original_owner_audit_rerun=False,runner_sha256=runner_pin,portable_compiler_helper_sha256=helper_pin,compiler=dict(path=str(compiler),sha256=compiler_pin),commands=[c,run],actual_compiled_controls=negatives,executable_sha256=sha(out),artifacts={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.iterdir() if p.is_file()},
        original_firmware_executed=False,ISA_emulation=False,synthetic_provider=True,nonreturn_register_prefix_proved=False,native_registers_checked=False,hardware=False,network=False,OTA_ready=False)
    write(folder/'verification.json',r);return dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),tests=result)
def replay(root,receipt):
    root=Path(root).resolve();receipt=Path(receipt).resolve();folder=receipt.parent;r=read(receipt);model=root/'experiments/tsl9-v4160-flash-register-prefix'
    need(r['passed'] is True and r['runner_sha256']==sha(Path(__file__)) and r['portable_compiler_helper_sha256']==sha(root/'scripts/portable_verify.py'),'current host runner/helper identity')
    need(r['source_sha256']=={p.relative_to(model).as_posix():sha(p) for d in ('src','tests') for p in (model/d).glob('*') if p.is_file()},'current exact host source/test identity')
    need(source_evidence(root)==r['source_evidence_pins'],'current reused sealed source evidence, no historical owner rerun claimed')
    need(r['tests']==dict(passed=True,groups=5,cases=481,checks=247191,synthetic_provider=True,RV32_execution=False),'exact frozen host coverage')
    compiler=Path(r['compiler']['path']);need(sha(compiler)==r['compiler']['sha256'],'actual host compiler pin')
    for n,pin in r['artifacts'].items():
        p=(folder/n).resolve();need(p.is_relative_to(folder) and p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'],'actual positive host artifact '+n)
    need(json.loads((folder/'tests.log').read_text(encoding='utf-8'))==r['tests'],'actual positive test-output log')
    out=folder/('host-tests.exe' if (folder/'host-tests.exe').exists() else 'host-tests');need(host_executable(out)==r['commands'][1]['host_executable_guard'],'reinspect actual positive host executable before read-only admission')
    for command in r['commands']:need(command['exit']==0 and sha(folder/command['log'])==command['log_sha256'],'actual successful compile/run logs')
    need(len(r['actual_compiled_controls'])==6,'six actual compiled behavior controls')
    for row in r['actual_compiled_controls']:
        base=folder/'compiled-controls'/row['case'];need(row['compiled'] and row['rejected'],'actual compiled semantic rejection')
        for n,pin in row['artifacts'].items():
            p=(base/n).resolve();need(p.is_relative_to(base.resolve()) and p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'],'actual compiled-control artifact '+n)
        for n in r['source_sha256']:
            actual=(base/n).read_bytes();expected=(model/n).read_bytes()
            if n==row['mutation_file']:
                text=expected.decode();need(text.count(row['old'])==1,'unique selected mutation');expected=text.replace(row['old'],row['new']).encode()
            need(actual==expected,'exact one-change compiled source control')
        need(row['commands'][0]['exit']==0 and row['commands'][1]['exit']!=0 and 'failure line' in (base/'tests.log').read_text(encoding='utf-8'),'actual behavior assertion failure, not compile/launch failure')
        exe=base/('negative.exe' if (base/'negative.exe').exists() else 'negative');need(host_executable(exe)==row['commands'][1]['host_executable_guard'],'reinspect actual negative host executable')
        for command in row['commands']:need(sha(base/command['log'])==command['log_sha256'],'actual negative compile/run log')
    return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),tests=r['tests'],actual_compiled_controls_replayed=6,synthetic_host_only=True,native_target_execution=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=R);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:print(json.dumps(replay(root,a.replay)));return
    base=a.build_root.resolve() if a.build_root else root/'experiments/tsl9-v4160-flash-register-prefix/build'/('host-'+uuid.uuid4().hex);need(base.is_relative_to(root) and not base.exists(),'create-only host build root inside project')
    results=[verify(root,base/mode,mode) for mode in (['c','cpp'] if a.language=='both' else [a.language])];print(json.dumps(dict(passed=True,results=results,firmware_executed=False)))
if __name__=='__main__':main()
