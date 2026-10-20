"""Static vector/IRQ/clock/reset integration; no RV32 execution or emulation."""
from pathlib import Path
import argparse,hashlib,json,re,runpy,struct,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parent
BASE=runpy.run_path(str(ROOT/'verify.py'));ELF=BASE['ELF'];need=BASE['need'];BIN=BASE['BIN']
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--firmware',type=Path,default=ROOT.parents[1]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin');ap.add_argument('--baseline-receipt',type=Path);args=ap.parse_args()
    raw=args.firmware.read_bytes();need(len(raw)==76800 and sha(raw)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Pinned ID2966')
    plan_path=ROOT/'evidence/vector-plan.json';plan=json.loads(plan_path.read_text(encoding='utf-8'))
    need(plan['source_firmware_sha256']==sha(raw) and len(plan['sections'])==13 and len(plan['relocations'])==190,'Reviewed vector cohort')
    sections={s['name']:s for s in plan['sections']};defined={s['name']:s for s in plan['defined_symbols']};unknown=plan['expected_undefined_symbols']
    ram_views={n:r['originalVA']-0x20004000 for n,r in unknown.items() if r['role'].startswith('data_address')}
    expected_und={n for n in unknown if n not in ram_views and n!='tsl9v4160_reset'}|{'__tsl9v4160_main','__tsl9v4160_rom_entry'}
    need(len(ram_views)==7 and len(expected_und)==9 and all(0<=o<35160 for o in ram_views.values()),'Bounded RAM aliases and true remaining obligations')
    work=ROOT/'build'/('vectors-'+uuid.uuid4().hex);work.mkdir(parents=True,exist_ok=False)
    cc=BIN/'clang.exe';ld=BIN/'ld.lld.exe'
    inputs=[ROOT/n for n in ['src/startup.c','src/startup.h','src/clock.c','src/clock.h','src/vector_native.c','src/vector_native.h','verify.py','verify-platform.py','verify-vector-platform.py','layout/vector-platform.ld','layout/vector-ram-views.ld','layout/vector-platform-address-witness.ld','evidence/startup-evidence.json','evidence/clock-evidence.json','evidence/vector-plan.json']]
    source_hashes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in inputs}
    def run(argv,folder,label,success=True):
        p=subprocess.run([str(x) for x in argv],cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90,check=False)
        (folder/(label+'.log')).write_bytes(p.stdout);need((p.returncode==0)==success,'Tool result '+label)
        return dict(argv=[str(x) for x in argv],exit=p.returncode,log_sha256=sha(p.stdout)),p.stdout
    if args.baseline_receipt:
        baseline_path=args.baseline_receipt
    else:
        _,output=run([sys.executable,'-X','utf8','-B',ROOT/'verify-platform.py','--firmware',args.firmware.resolve()],work,'baseline-clock')
        baseline_path=Path(json.loads(output.decode('utf-8').strip().splitlines()[-1])['receipt'])
    baseline=json.loads(baseline_path.read_text(encoding='utf-8'));need(baseline['passed'] and baseline['schema']=='ID2966-startup-clock-platform-v1','Verified clock baseline')
    need(all(sha((ROOT/n).read_bytes())==h for n,h in baseline['source_files'].items()),'Baseline source drift')
    need(all(sha(Path(n).read_bytes())==h for n,h in baseline['tools'].items()),'Baseline tool drift')
    def check_ram(elf):
        ram=elf.symbol['__tsl9v4160_ram'];need(ram['size']==35160 and ram['index'] not in (0,0xfff1),'Actual RAM carrier')
        carrier=elf.sections[ram['index']];need(carrier['type']==8 and carrier['size']==35160,'One NOBITS RAM carrier')
        for name,offset in ram_views.items():
            alias=elf.symbol[name]
            need(alias['index']==ram['index'] and alias['type']==0 and alias['size']==0 and alias['value']-ram['value']==offset,'Section-relative RAM view, no ABS value substitution: '+name)
        return ram
    modes={}
    for mode,lang,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();commands=[];vector=folder/'vector-native.o'
        baseline_object=Path(baseline['modes'][mode]['integrated_object'])
        need(sha(baseline_object.read_bytes())==baseline['modes'][mode]['integrated_sha256'],'Baseline object identity')
        cmd,_=run([cc,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-stack-protector','-fno-builtin','-Wall','-Wextra','-Werror','-x',lang,'-std='+std,'-c',ROOT/'src/vector_native.c','-o',vector],folder,'compile-vector');commands.append(cmd)
        unit=ELF(vector);need(unit.kind==1,'Vector ET_REL')
        need({s['name'] for s in unit.symbols if s['name'] and s['index']==0}==set(unknown),'Standalone keeps fifteen real external obligations')
        need({s['name'] for s in unit.sections if s['flags']&2 and s['size']}==set(sections),'Exactly thirteen vector allocations')
        for name,spec in sections.items():
            section=unit.byname[name];original=raw[spec['originalVA']-0x8000:spec['originalVA']-0x8000+spec['bytes']]
            need(len(original)==spec['bytes'] and sha(original)==spec['sha256'] and section['data']==original,'Every vector/code byte matches original: '+name)
        for name,spec in defined.items():
            sym=unit.symbol[name];need(sym['type']==spec['elf_type'] and sym['size']==spec['size'],'Defined symbol type/size '+name)
            if spec['section']=='ABS':need(sym['index']==0xfff1 and sym['value']==spec['originalVA'],'Address-only ABS constant')
            else:need(sym['index']==unit.byname[spec['section']]['index'] and sym['value']==spec['originalVA']-sections[spec['section']]['originalVA'],'Defined symbol in real captured section')
        expected={(r['section'],r['offset']):r for r in plan['relocations']}
        need(len(unit.relocations)==190 and len(expected)==190,'190 exact vector relocation positions')
        for relocation in unit.relocations:
            spec=expected[(relocation['section'],relocation['offset'])];need(relocation['type']==spec['type_number'],'Relocation encoding')
            symbol=unit.symbols[relocation['symbol_index']]
            if symbol['index']==0:
                if relocation['symbol_index']==0:
                    need(spec['target'] in defined and defined[spec['target']]['section']=='ABS','Only known ABS address may canonicalize to null symbol')
                    value=relocation['addend']
                else:
                    need(symbol['name']==spec['target'] and symbol['name'] in unknown,'Undefined target name preserved')
                    value=unknown[symbol['name']]['originalVA']+relocation['addend']
            elif symbol['index']==0xfff1:
                need(spec['target'] in defined and defined[spec['target']]['section']=='ABS','No ABS implementation provider');value=symbol['value']+relocation['addend']
            else:
                s=unit.sections[symbol['index']];need(s['name'] in sections,'Real captured target section')
                value=sections[s['name']]['originalVA']+symbol['value']+relocation['addend']
            need(value==spec['target_originalVA']+spec['addend'],'Exact target/own-anchor address')
        integrated=folder/'native-platform.o'
        cmd,_=run([ld,'-r','--no-relax','-T',ROOT/'layout/vector-ram-views.ld',baseline_object,vector,'-o',integrated],folder,'integrate-real-RAM-views');commands.append(cmd)
        merged=ELF(integrated);need(len(merged.relocations)==211,'21 existing plus190 vector relocations')
        und={s['name'] for s in merged.symbols if s['name'] and s['index']==0};need(und==expected_und,'Nine genuine unresolved code providers')
        check_ram(merged)
        need(merged.byname['.text.tsl9v4160.reset']['data']==raw[0x106aa:0x10734] and merged.byname['.text.tsl9v4160.clock']['data']==raw[0x1074a:0x10834],'Existing reset/clock instructions retained')
        # Genuine malformed ELF fixture: an address-only ABS symbol must not be
        # accepted as an alias backed by the existing real RAM section.
        mutated=bytearray(merged.raw);target=sorted(ram_views)[0];changed=False
        for table in merged.sections:
            if table['type']!=2:continue
            strings=merged.sections[table['link']]['data']
            for offset in range(0,table['size'],16):
                nameoff=struct.unpack_from('<I',table['data'],offset)[0];name=strings[nameoff:strings.index(0,nameoff)].decode('ascii')
                if name==target:struct.pack_into('<H',mutated,table['offset']+offset+14,0xfff1);changed=True
        need(changed,'RAM alias countercase selected');counter=folder/'COUNTERCASE-ABS-RAM.o';counter.write_bytes(mutated)
        rejected=False
        try:check_ram(ELF(counter))
        except AssertionError:rejected=True
        need(rejected,'ABS RAM countercase must be rejected')
        strict=folder/'strict-incomplete.elf'
        cmd,log=run([ld,'--no-relax','--error-limit=0','-T',ROOT/'layout/vector-platform.ld',integrated,'-o',strict],folder,'strict-final-link',False);commands.append(cmd)
        need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',log.decode('utf-8','replace')))==expected_und,'All nine obligations remain fatal')
        witness=folder/'ADDRESS-WITNESS-ONLY.elf'
        cmd,_=run([ld,'--no-relax','-T',ROOT/'layout/vector-platform.ld','-T',ROOT/'layout/vector-platform-address-witness.ld',integrated,'-o',witness],folder,'numeric-address-witness');commands.append(cmd)
        linked=ELF(witness);ram=check_ram(linked);need(ram['value']==0x20004000,'Known numeric RAM model')
        for name,spec in sections.items():
            section=linked.byname[name];need(section['address']==spec['originalVA'] and section['data']==raw[spec['originalVA']-0x8000:spec['originalVA']-0x8000+spec['bytes']],'Final exact original vector/IRQ bytes')
        for name,address,length in [('.text.reset',0x186aa,138),('.text.clock',0x1874a,234),('.rodata.initializer',0x1ab60,128)]:
            section=linked.byname[name];need(section['address']==address and section['data']==raw[address-0x8000:address-0x8000+length],'Existing code/data preserved')
        for name,size in [('tsl9v4160_reset',138),('__tsl9v4160_clock_init',234)]:
            sym=linked.symbol[name];need(sym['type']==2 and sym['index']!=0xfff1 and sym['size']==size,'Existing real FUNC provider')
        base=linked.symbol['__tsl9v4160_vector_base'];need(base['index']==linked.byname['.rodata.tsl9v4160.vector_capture']['index'] and base['value']==0x8038 and base['type']==0 and base['size']==0,'Vector base points to true finite captured storage')
        allocations={s['name'] for s in linked.sections if s['flags']&2 and s['size']};need(allocations==set(sections)|{'.text.reset','.text.clock','.rodata.initializer','.bss.ram'},'Exactly17 real allocation sections, no hidden code/RAM/stack')
        modes[mode]=dict(passed=True,commands=commands,vector_object=str(vector),vector_sha256=sha(vector.read_bytes()),integrated_object=str(integrated),integrated_sha256=sha(integrated.read_bytes()),numeric_witness_sha256=sha(witness.read_bytes()),allocated_file_bytes=1778,code_bytes=1322,RO_captured_bytes=456,RAM_NOBITS_bytes=35160,relocations=211,undefined_symbols=sorted(und),RAM_views=ram_views,strict_rejected=True,ABS_RAM_countercase_rejected=True,numeric_witness_is_firmware=False)
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256'] and modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256'],'C/C++ integrated results byte-equal')
    need(source_hashes=={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in inputs},'Source changed during audit')
    report=dict(schema='ID2966-native-vector-clock-platform-v1',passed=True,firmware_sha256=sha(raw),baseline_receipt=str(baseline_path),baseline_receipt_sha256=sha(baseline_path.read_bytes()),source_files=source_hashes,tools={str(p):sha(p.read_bytes()) for p in [cc,ld]},modes=modes,logical_vector_extent_proved=False,IRQ_ABI_proved=False,firmware_executed=False,emulation=False,network=False,hardware=False,target_ready=False,ota_verified=False,native_bin=False)
    receipt=work/'verification.json';receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,modes=['C11','C++17'],code_bytes=1322,RO_captured_bytes=456,RAM_NOBITS_bytes=35160,relocations=211,remaining_undefined=9,receipt=str(receipt),native_bin=False)))
if __name__=='__main__':main()
