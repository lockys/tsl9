"""Native startup+clock static integration. No target execution/emulation."""
from pathlib import Path
import argparse,hashlib,json,re,runpy,subprocess,uuid
ROOT=Path(__file__).resolve().parent
BASE=runpy.run_path(str(ROOT/'verify.py'))
ELF=BASE['ELF'];need=BASE['need'];BIN=BASE['BIN']
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--firmware',type=Path,default=ROOT.parents[1]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin');args=ap.parse_args()
    raw=args.firmware.read_bytes();need(len(raw)==76800 and sha(raw)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Pinned ID2966')
    reset=raw[0x106aa:0x10734];clock=raw[0x1074a:0x10834];initializer=raw[0x12b60:0x12be0]
    clock_evidence=json.loads((ROOT/'evidence/clock-evidence.json').read_text(encoding='utf-8'))
    need(len(clock)==234 and sha(clock)==clock_evidence['sha256'],'Clock source identity')
    work=ROOT/'build'/('platform-'+uuid.uuid4().hex);work.mkdir(parents=True,exist_ok=False)
    cc=BIN/'clang.exe';ld=BIN/'ld.lld.exe'
    inputs=[ROOT/n for n in ['src/startup.c','src/startup.h','src/clock.c','src/clock.h','verify.py','verify-platform.py','layout/platform.ld','layout/platform-address-witness.ld','evidence/startup-evidence.json','evidence/clock-evidence.json']]
    inputs_sha={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in inputs}
    expected_und={'__tsl9v4160_vector_base','__tsl9v4160_main','__tsl9v4160_rom_entry'};modes={}
    def run(argv,folder,label,success=True):
        p=subprocess.run([str(x) for x in argv],cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,check=False)
        (folder/(label+'.log')).write_bytes(p.stdout);need((p.returncode==0)==success,'Tool result '+label)
        return dict(argv=[str(x) for x in argv],exit=p.returncode,log_sha256=sha(p.stdout)),p.stdout
    for mode,lang,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();commands=[];units=[]
        for name in ['startup','clock']:
            obj=folder/(name+'.o')
            cmd,_=run([cc,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-stack-protector','-fno-builtin','-Wall','-Wextra','-Werror','-x',lang,'-std='+std,'-c',ROOT/('src/'+name+'.c'),'-o',obj],folder,'compile-'+name);commands.append(cmd);units.append(obj)
        clock_unit=ELF(units[1]);need(clock_unit.kind==1,'Clock ET_REL')
        section=clock_unit.byname['.text.tsl9v4160.clock'];need(section['data']==clock,'Complete clock234B and cold tail')
        fn=clock_unit.symbol['__tsl9v4160_clock_init'];need(fn['type']==2 and fn['size']==234 and fn['index']==section['index'],'Real clock FUNC')
        need(not{s['name'] for s in clock_unit.symbols if s['name'] and s['index']==0},'Clock introduces no undefined providers')
        expected_branches={int(r['model_VA'],16)-0x1874a:(r['control'],int(r['target_model_VA'],16)-0x1874a) for r in clock_evidence['control'] if r['control']!='RETURN'}
        need(len(clock_unit.relocations)==7,'Seven clock control relocations')
        for relocation in clock_unit.relocations:
            kind,target_offset=expected_branches[relocation['offset']]
            need(relocation['type']=={'BRANCH':16,'RVC_BRANCH':44,'RVC_JUMP':45}[kind],'Branch relocation encoding')
            symbol=clock_unit.symbols[relocation['symbol_index']]
            need(symbol['index']==section['index'] and symbol['value']+relocation['addend']==target_offset,'Each branch targets exact internal instruction')
        integrated=folder/'startup-clock.o'
        cmd,_=run([ld,'-r','--no-relax',*units,'-o',integrated],folder,'partial-link');commands.append(cmd)
        merged=ELF(integrated);und={s['name'] for s in merged.symbols if s['name'] and s['index']==0}
        need(und==expected_und and len(merged.relocations)==21,'Actual clock provider reduces four reset UND to three')
        need(merged.byname['.text.tsl9v4160.reset']['data']==reset and merged.byname['.text.tsl9v4160.clock']['data']==clock,'Original code retained in integrated unit')
        merged_clock=merged.symbol['__tsl9v4160_clock_init'];need(merged_clock['type']==2 and merged_clock['size']==234 and merged_clock['index']!=0xfff1,'Merged clock must remain a section-backed FUNC, never ABS')
        strict=folder/'strict-incomplete.elf'
        cmd,log=run([ld,'--no-relax','--error-limit=0','-T',ROOT/'layout/platform.ld',integrated,'-o',strict],folder,'strict-final-link',False);commands.append(cmd)
        need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',log.decode('utf-8','replace')))==expected_und,'Three true obligations must reject final ELF')
        witness=folder/'ADDRESS-WITNESS-ONLY.elf'
        cmd,_=run([ld,'--no-relax','-T',ROOT/'layout/platform.ld','-T',ROOT/'layout/platform-address-witness.ld',integrated,'-o',witness],folder,'numeric-address-witness');commands.append(cmd)
        linked=ELF(witness)
        for name,address,bytes_ in [('.text.reset',0x186aa,reset),('.text.clock',0x1874a,clock),('.rodata.initializer',0x1ab60,initializer)]:
            s=linked.byname[name];need(s['address']==address and s['data']==bytes_,'Exact original fixed-address bytes '+name)
        final_clock=linked.symbol['__tsl9v4160_clock_init'];need(final_clock['type']==2 and final_clock['index']!=0xfff1 and final_clock['value']==0x1874a and final_clock['size']==234,'Numeric witness must retain actual clock code')
        ram=linked.byname['.bss.ram'];need(ram['type']==8 and ram['address']==0x20004000 and ram['size']==35160,'Original numeric RAM carrier only')
        need({s['name'] for s in linked.sections if s['flags']&2 and s['size']}=={'.text.reset','.text.clock','.rodata.initializer','.bss.ram'},'No hidden stub/vector/main/stack providers')
        modes[mode]=dict(passed=True,commands=commands,clock_object=str(units[1]),clock_object_sha256=sha(units[1].read_bytes()),integrated_object=str(integrated),integrated_sha256=sha(integrated.read_bytes()),numeric_witness_sha256=sha(witness.read_bytes()),clock_bytes=234,reset_bytes=138,initializer_bytes=128,RAM_NOBITS_bytes=35160,relocations=21,undefined_symbols=sorted(und),strict_rejected=True,numeric_witness_is_firmware=False)
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256'],'C/C++ integrated object byte-equal')
    need(modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256'],'C/C++ numeric witness byte-equal')
    need(inputs_sha=={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in inputs},'Source changed during verification')
    report=dict(schema='ID2966-startup-clock-platform-v1',passed=True,firmware_sha256=sha(raw),source_files=inputs_sha,tools={str(p):sha(p.read_bytes()) for p in [cc,ld]},modes=modes,firmware_executed=False,emulation=False,network=False,hardware=False,IRQ_ABI_proved=False,target_ready=False,ota_verified=False,native_bin=False)
    receipt=work/'verification.json';receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,modes=['C11','C++17'],clock_bytes=234,total_code_bytes=372,relocations=21,remaining_undefined=3,receipt=str(receipt),native_bin=False)))
if __name__=='__main__':main()
