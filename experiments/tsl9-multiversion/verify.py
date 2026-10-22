"""Verify pinned BIN evidence and test new portable C/C++ on Windows x64.
No firmware execution/emulation, network, or device access. RV32 is compile-only.
"""
from pathlib import Path
import argparse, ctypes, hashlib, json, struct, subprocess, uuid

_paths = __import__("runpy").run_path(str(next(p for p in Path(__file__).resolve().parents if (p / "scripts/project_paths.py").is_file()) / "scripts/project_paths.py"))

ROOT=Path(__file__).resolve().parent
TOOLBIN=_paths["llvm_bin"]()
sha=lambda b:hashlib.sha256(b).hexdigest()

def require(test, message):
    if not test:raise AssertionError(message)

def command(argv, cwd, label):
    run=subprocess.run([str(x) for x in argv], cwd=cwd, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=60, check=False)
    (cwd/(label+'.log')).write_bytes(run.stdout)
    require(run.returncode==0,'Compile/link failed; inspect '+str(cwd/(label+'.log')))
    return dict(argv=[str(x) for x in argv],exit=run.returncode,log_sha256=sha(run.stdout))

class Profile(ctypes.Structure):
    _fields_=[('firmware_id',ctypes.c_uint32),('file_offset',ctypes.c_uint32),
              ('image_bytes',ctypes.c_uint32),('source_sha256',ctypes.c_char*65)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--firmware-root',type=Path,default=ROOT.parents[1]/'firmware-downloads/legacy-options-2026-10-20/BINs')
    args=ap.parse_args()
    evidence_file=ROOT/'evidence/predicate.json'
    evidence=json.loads(evidence_file.read_text(encoding='utf-8'))
    require(evidence['passed'] is True and evidence['matched_count']==15,'Expected reviewed evidence')
    pattern=b''.join(bytes.fromhex(i['bytes_hex']) for i in evidence['instructions'])
    require(len(pattern)==42 and sha(pattern)==evidence['baseline']['sha256_slice'],'42-byte instruction partition')
    profiles={}
    versions=evidence['versions']
    require(len(versions)==22 and len({r['FirmwareID'] for r in versions})==22,'22 unique evidence IDs')
    for row in versions:
        path=args.firmware_root/Path(row['source']).name
        raw=path.read_bytes()
        require(len(raw)==row['source_bytes'] and sha(raw)==row['source_sha256'],'Pinned source identity: '+path.name)
        hits=[];pos=raw.find(pattern)
        while pos>=0:hits.append(pos);pos=raw.find(pattern,pos+1)
        require(len(hits)==row['exact_predicate_matches'],'Exact whole-routine match count: '+path.name)
        if hits:
            require(hits==[row['predicate_offset']],'Unique exact routine offset')
            profiles[row['FirmwareID']]=row
    require(len(profiles)==15,'15 matched source images')
    build=ROOT/'build'/uuid.uuid4().hex;build.mkdir(parents=True,exist_ok=False)
    cc=TOOLBIN/'clang.exe';ld=TOOLBIN/'ld.lld.exe'
    sources=[ROOT/'src/observed_predicate.c',ROOT/'src/observed_profiles.c']
    report=dict(schema='multiversion-portable-C-CXX-verification-v1',passed=False,
        evidence_sha256=sha(evidence_file.read_bytes()),verified_images=22,matched_images=15,
        pattern_sha256=sha(pattern),source_sha256={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [*sources,ROOT/'src/observed_predicate.h',Path(__file__)]},
        tools={str(p):sha(p.read_bytes()) for p in [cc,ld]},modes={},firmware_executed=False,
        firmware_emulated=False,network=False,hardware=False,ota_verified=False,target_ready=False)
    for mode,lang,std in [('c','c','c11'),('cpp','c++','c++17')]:
        work=build/mode;work.mkdir();commands=[];host_objects=[];native_objects=[]
        for source in sources:
            common=['-ffreestanding','-fno-stack-protector','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-x',lang,'-std='+std]
            host=work/(source.stem+'-host.obj');native=work/(source.stem+'-rv32.o')
            commands.append(command([cc,'--target=x86_64-pc-windows-msvc',*common,'-c',source,'-o',host],work,source.stem+'-host'))
            commands.append(command([cc,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32',*common,'-c',source,'-o',native],work,source.stem+'-rv32'))
            raw=native.read_bytes()
            require(raw[:4]==b'\x7fELF' and raw[4:6]==b'\x01\x01' and struct.unpack_from('<H',raw,16)[0]==1 and struct.unpack_from('<H',raw,18)[0]==243,'RV32 little-endian relocatable object only')
            host_objects.append(host);native_objects.append(native)
        dll=work/'portable-predicate.dll'
        commands.append(command([ld,'-flavor','link','/dll','/noentry','/nodefaultlib','/machine:x64','/export:tsl9_observed_predicate','/export:tsl9_find_observed_profile','/out:'+str(dll),*host_objects],work,'host-link'))
        raw=dll.read_bytes();pe=struct.unpack_from('<I',raw,0x3c)[0]
        require(raw[:2]==b'MZ' and struct.unpack_from('<H',raw,pe+4)[0]==0x8664,'Host x64 DLL only')
        lib=ctypes.CDLL(str(dll));fn=lib.tsl9_observed_predicate
        fn.argtypes=[ctypes.c_uint8,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint8)];fn.restype=ctypes.c_uint32
        lookup=lib.tsl9_find_observed_profile;lookup.argtypes=[ctypes.c_uint32];lookup.restype=ctypes.POINTER(Profile)
        cases=0
        # Expected states 0/1/2 are derived from LBU+SLTIU 3 in the captured instruction table.
        for flags in range(256):
            for index in range(3):
                for state in range(256):
                    vals=[255,255,255];vals[index]=state;arr=(ctypes.c_uint8*3)(*vals)
                    expected=1 if not(flags&8) and state in (0,1,2) else 0
                    require(fn(flags,index,arr)==expected,'Unsigned byte/flag/index case');cases+=1
            for index in (3,4,255,0x7fffffff,0x80000000,0xffffffff):
                require(fn(flags,index,None)==0,'Out-of-range unsigned index must not access state');cases+=1
            if flags&8:
                for index in range(3):
                    require(fn(flags,index,None)==0,'Disabled predicate must not access state');cases+=1
        for row in versions:
            got=lookup(row['FirmwareID'])
            if row['FirmwareID'] in profiles:
                require(bool(got),'Known profile present');p=got.contents
                require((p.firmware_id,p.file_offset,p.image_bytes,p.source_sha256.decode('ascii'))==(row['FirmwareID'],row['predicate_offset'],row['source_bytes'],row['source_sha256']),'C profile equals reviewed BIN identity')
            else:require(not got,'Unmatched image must remain unknown')
        for unknown in (0,1,2967,0xffffffff):require(not lookup(unknown),'Unknown IDs must remain unknown')
        report['modes'][mode]=dict(passed=True,host_value_cases=cases,profile_cases=26,commands=commands,
            host_DLL_sha256=sha(dll.read_bytes()),RV32_compile_only_objects={p.name:sha(p.read_bytes()) for p in native_objects})
    report['passed']=True
    receipt=build/'verification.json';receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,images=22,matched_images=15,cases_per_mode=cases+26,
        modes=['C11','C++17'],RV32='compile-only relocatable objects',receipt=str(receipt),ota_verified=False)))

if __name__=='__main__':main()
