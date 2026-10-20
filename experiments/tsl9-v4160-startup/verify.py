"""Compile C/C++; inspect ELF bytes/relocations. Never execute the target."""
from pathlib import Path
import argparse,hashlib,json,re,struct,subprocess,uuid
ROOT=Path(__file__).resolve().parent
BIN=Path(r'C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin')
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(x,message):
    if not x:raise AssertionError(message)
class ELF:
    def __init__(self,path):
        self.raw=path.read_bytes();b=self.raw
        need(b[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<H',b,18)[0]==243,'ELF32 little-endian RISC-V')
        self.kind=struct.unpack_from('<H',b,16)[0];off=struct.unpack_from('<I',b,32)[0]
        size,n,strings=struct.unpack_from('<HHH',b,46);need(size==40,'section header size')
        headers=[struct.unpack_from('<10I',b,off+i*size) for i in range(n)]
        sh=headers[strings];names=b[sh[4]:sh[4]+sh[5]]
        text=lambda blob,o:blob[o:blob.index(0,o)].decode('ascii')
        self.sections=[]
        for i,h in enumerate(headers):
            self.sections.append(dict(index=i,name=text(names,h[0]),type=h[1],flags=h[2],address=h[3],offset=h[4],size=h[5],link=h[6],info=h[7],alignment=h[8],entsize=h[9],data=b'' if h[1]==8 else b[h[4]:h[4]+h[5]]))
        self.byname={s['name']:s for s in self.sections};self.symbols=[]
        symsections={}
        for s in self.sections:
            if s['type']!=2:continue
            strings=self.sections[s['link']]['data'];symbols=[]
            for p in range(0,s['size'],16):
                name,value,size,info,other,index=struct.unpack_from('<IIIBBH',s['data'],p)
                symbols.append(dict(name=text(strings,name),value=value,size=size,type=info&15,bind=info>>4,index=index))
            symsections[s['index']]=symbols;self.symbols.extend(symbols)
        self.symbol={s['name']:s for s in self.symbols if s['name']};self.relocations=[]
        for s in self.sections:
            if s['type']!=4:continue
            for p in range(0,s['size'],12):
                offset,info,addend=struct.unpack_from('<IIi',s['data'],p)
                self.relocations.append(dict(section=self.sections[s['info']]['name'],offset=offset,type=info&255,target=symsections[s['link']][info>>8]['name'],symbol_index=info>>8,addend=addend))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--firmware',type=Path,default=ROOT.parents[1]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin');args=ap.parse_args()
    evidence=json.loads((ROOT/'evidence/startup-evidence.json').read_text(encoding='utf-8'));chosen=evidence['selected']
    raw=args.firmware.read_bytes();need(len(raw)==76800 and sha(raw)==chosen['sha256'],'pinned ID2966 source')
    reset=bytes.fromhex(chosen['reset_hex']);init=bytes.fromhex(chosen['initializer_hex'])
    need(raw[chosen['entry_file_offset']:chosen['entry_file_offset']+138]==reset,'actual reset range')
    need(raw[chosen['initializer_file_offset']:chosen['initializer_file_offset']+128]==init,'actual initializer range')
    work=ROOT/'build'/uuid.uuid4().hex;work.mkdir(parents=True,exist_ok=False)
    cc=BIN/'clang.exe';ld=BIN/'ld.lld.exe';source=ROOT/'src/startup.c'
    expected_und={'__tsl9v4160_vector_base','__tsl9v4160_main','__tsl9v4160_clock_init','__tsl9v4160_rom_entry'}
    modes={}
    def run(argv,folder,label,success=True):
        result=subprocess.run([str(x) for x in argv],cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,check=False)
        (folder/(label+'.log')).write_bytes(result.stdout)
        need((result.returncode==0)==success,'unexpected compiler/linker result: '+label)
        return dict(argv=[str(x) for x in argv],exit=result.returncode,log_sha256=sha(result.stdout)),result.stdout
    for mode,lang,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();obj=folder/'startup.o';strict=folder/'strict-incomplete.elf';witness=folder/'ADDRESS-WITNESS-ONLY.elf';commands=[]
        command,_=run([cc,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-stack-protector','-fno-builtin','-Wall','-Wextra','-Werror','-x',lang,'-std='+std,'-c',source,'-o',obj],folder,'compile');commands.append(command)
        elf=ELF(obj);need(elf.kind==1,'relocatable unit')
        und={s['name'] for s in elf.symbols if s['name'] and s['index']==0};need(und==expected_und,'four genuine external obligations')
        need(elf.byname['.text.tsl9v4160.reset']['data']==reset,'all original reset instruction bytes retained before relocation')
        need(elf.byname['.rodata.tsl9v4160.initializer']['data']==init,'initializer preserved')
        ram=elf.byname['.bss.tsl9v4160.ram'];need(ram['type']==8 and ram['size']==35160,'single NOBITS RAM carrier')
        sp=elf.symbol['__tsl9v4160_sp_address'];need(sp['index']==0xfff1 and sp['value']==0x20010000 and sp['size']==0,'SP constant only; no allocated stack')
        relocs=elf.relocations;need(len(relocs)==14 and {r['type'] for r in relocs}=={17,23,24},'14 semantic relocations, no relax')
        expected={0:(23,'__tsl9v4160_gp',0),4:(24,'.Lreset_000',0),8:(23,'',0x20010000),12:(24,'.Lreset_008',0),16:(23,'__tsl9v4160_initializer',0),20:(24,'.Lreset_010',0),56:(23,'__tsl9v4160_bss_end',0),60:(24,'.Lreset_038',0),102:(23,'__tsl9v4160_vector_base',0),106:(24,'.Lreset_066',0),118:(17,'__tsl9v4160_clock_init',0),122:(23,'__tsl9v4160_main',0),126:(24,'.Lreset_07a',0),134:(17,'__tsl9v4160_rom_entry',0)}
        # The assembler canonicalizes the known ABS SP target to null-symbol +
        # absolute addend. It is still an address expectation, not stack storage.
        need({r['offset']:(r['type'],r['target'],r['addend']) for r in relocs}==expected and next(r for r in relocs if r['offset']==8)['symbol_index']==0,'exact relocation roles/own anchors/ABS address')
        command,log=run([ld,'--no-relax','--error-limit=0','-T',ROOT/'layout/component.ld',obj,'-o',strict],folder,'strict-final-link',False);commands.append(command)
        need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',log.decode('utf-8','replace')))==expected_und,'incomplete component must fail strict final link')
        command,_=run([ld,'--no-relax','-T',ROOT/'layout/component.ld','-T',ROOT/'layout/address-witness.ld',obj,'-o',witness],folder,'address-witness-only');commands.append(command)
        address=ELF(witness)
        for name,location,content in [('.text.reset',0x186aa,reset),('.rodata.initializer',0x1ab60,init)]:
            section=address.byname[name];need(section['address']==location and section['data']==content,'numeric fixed-address byte witness: '+name)
        ram=address.byname['.bss.ram'];need(ram['address']==0x20004000 and ram['type']==8 and ram['size']==35160,'RAM numeric extent only')
        need({s['name'] for s in address.sections if s['flags']&2 and s['size']}=={'.text.reset','.rodata.initializer','.bss.ram'},'no implicit code/provider/stack allocation')
        modes[mode]=dict(passed=True,commands=commands,object=str(obj),object_sha256=sha(obj.read_bytes()),undefined_symbols=sorted(und),relocations=relocs,reset_bytes=138,initializer_bytes=128,RAM_NOBITS_bytes=35160,BSS_clear_bytes=35032,strict_rejected=True,numeric_witness_sha256=sha(witness.read_bytes()),numeric_witness_is_firmware=False)
    need(modes['c']['object_sha256']==modes['cpp']['object_sha256'],'C/C++ native objects byte-identical')
    report=dict(schema='ID2966-native-startup-component-audit-v1',passed=True,source_firmware_sha256=sha(raw),
        source_files={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [source,ROOT/'src/startup.h',ROOT/'verify.py',ROOT/'layout/component.ld',ROOT/'layout/address-witness.ld',ROOT/'evidence/startup-evidence.json']},
        tools={str(p):sha(p.read_bytes()) for p in [cc,ld]},modes=modes,original_executed=False,rebuilt_executed=False,emulation=False,network=False,hardware=False,stack_validity_proved=False,ROM_ABI_proved=False,target_ready=False,ota_verified=False,native_bin=False)
    path=work/'verification.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,reset_bytes=138,initializer_bytes=128,RAM_NOBITS_bytes=35160,relocations=14,strict_undefined=4,modes=['C11','C++17'],receipt=str(path),native_bin=False)))
if __name__=='__main__':main()
