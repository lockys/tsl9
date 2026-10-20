"""Static main/direct-callee integration. Never execute or emulate RV32."""
from pathlib import Path
import argparse,hashlib,json,re,runpy,struct,subprocess,sys,uuid

ROOT=Path(__file__).resolve().parent
BASE=runpy.run_path(str(ROOT/'verify.py'))
ELF=BASE['ELF'];need=BASE['need'];BIN=BASE['BIN']
sha=lambda b:hashlib.sha256(b).hexdigest()
sx=lambda x,n:x-(1<<n) if x&(1<<(n-1)) else x

def direct_target(pc,width,w):
    if width==4:
        if w&127==0x6f:
            imm=((w>>31)&1)<<20|((w>>21)&1023)<<1|((w>>20)&1)<<11|((w>>12)&255)<<12
            return 17,pc+sx(imm,21)
        if w&127==0x63:
            imm=((w>>31)&1)<<12|((w>>25)&63)<<5|((w>>8)&15)<<1|((w>>7)&1)<<11
            return 16,pc+sx(imm,13)
    elif width==2:
        f=w>>13
        if w&3==1 and f in (1,5):
            imm=((w>>12)&1)<<11|((w>>11)&1)<<4|((w>>9)&3)<<8|((w>>8)&1)<<10|((w>>7)&1)<<6|((w>>6)&1)<<7|((w>>3)&7)<<1|((w>>2)&1)<<5
            return 45,pc+sx(imm,12)
        if w&3==1 and f in (6,7):
            imm=((w>>12)&1)<<8|((w>>10)&3)<<3|((w>>5)&3)<<6|((w>>3)&3)<<1|((w>>2)&1)<<5
            return 44,pc+sx(imm,9)
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--firmware',type=Path,default=ROOT.parents[1]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
    ap.add_argument('--baseline-receipt',type=Path)
    args=ap.parse_args();raw=args.firmware.read_bytes()
    need(len(raw)==76800 and sha(raw)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Pinned ID2966')
    specs=[('main_native','main-plan.json'),('callee_native','callee-plan.json')]
    plans={stem:json.loads((ROOT/'evidence'/file).read_text(encoding='utf-8')) for stem,file in specs}
    need(all(p['source_firmware_sha256']==sha(raw) for p in plans.values()),'All modules bind actual source')
    sources=[ROOT/'verify-dependencies.py']
    for stem,file in specs:sources.extend([ROOT/'src'/(stem+'.c'),ROOT/'src'/(stem+'.h'),ROOT/'evidence'/file])
    source_hashes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources}
    work=ROOT/'build'/('dependencies-'+uuid.uuid4().hex);work.mkdir(parents=True,exist_ok=False)
    def run(argv,folder,label,success=True):
        p=subprocess.run([str(x) for x in argv],cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90,check=False)
        (folder/(label+'.log')).write_bytes(p.stdout);need((p.returncode==0)==success,'Tool result '+label)
        return dict(argv=[str(x) for x in argv],exit=p.returncode,log_sha256=sha(p.stdout)),p.stdout
    if args.baseline_receipt:baseline_path=args.baseline_receipt.resolve()
    else:
        _,output=run([sys.executable,'-X','utf8','-B',ROOT/'verify-vector-platform.py','--firmware',args.firmware.resolve()],work,'baseline-vector-platform')
        baseline_path=Path(json.loads(output.decode('utf-8').strip().splitlines()[-1])['receipt'])
    baseline=json.loads(baseline_path.read_text(encoding='utf-8'))
    need(baseline['passed'] and baseline['schema']=='ID2966-native-vector-clock-platform-v1','Verified prior vector/clock platform')
    need(baseline['firmware_sha256']==sha(raw),'Same source, no cross-version reuse')
    need(all(sha((ROOT/n).read_bytes())==h for n,h in baseline['source_files'].items()),'Baseline source drift')
    need(all(sha(Path(n).read_bytes())==h for n,h in baseline['tools'].items()),'Baseline tool drift')
    cc=BIN/'clang.exe';ld=BIN/'ld.lld.exe'
    baseline_unit=ELF(Path(baseline['modes']['c']['integrated_object']))
    baseline_witness=ELF(baseline_path.parent/'c/ADDRESS-WITNESS-ONLY.elf')
    need(sha(baseline_witness.raw)==baseline['modes']['c']['numeric_witness_sha256'],'Baseline witness identity')
    renamed={'.text.tsl9v4160.reset':'.text.reset','.text.tsl9v4160.clock':'.text.clock','.rodata.tsl9v4160.initializer':'.rodata.initializer','.bss.tsl9v4160.ram':'.bss.ram'}
    allocations={}
    for section in baseline_unit.sections:
        if not(section['flags']&2 and section['size']):continue
        name=section['name'];linked=baseline_witness.byname[renamed.get(name,name)]
        need(section['size']==linked['size'] and section['type']==linked['type'],'Baseline section identity')
        allocations[name]=dict(originalVA=linked['address'],bytes=linked['size'],kind='RAM' if linked['type']==8 else 'code' if linked['flags']&4 else 'RO',flags=linked['flags'])
    providers={};unknown={}
    for plan in plans.values():
        for section in plan['sections']:
            need(section['name'] not in allocations,'No duplicate storage')
            allocations[section['name']]=dict(section,flags=6 if section['kind']=='code' else 2)
        for symbol in plan['defined_symbols']:
            need(symbol['name'] not in providers and symbol['section']!='ABS','New providers must be actual captured storage/code')
            providers[symbol['name']]=symbol
        for name,item in plan['expected_undefined_symbols'].items():
            need(name not in unknown or item['originalVA']==unknown[name]['originalVA'],'Consistent external address')
            unknown[name]=item
    need(set(providers)=={'__tsl9v4160_main'}|{'__tsl9v4160_call_'+x for x in ['81b0','93ee','12bc8','18d78','18e86','19272','19282','19296']},'Exactly nine observed new entry bodies')
    need(sum(s['bytes'] for p in plans.values() for s in p['sections'])==384,'18B main plus366B callees')
    intervals=sorted((s['originalVA'],s['originalVA']+s['bytes'],n) for n,s in allocations.items() if s['kind']!='RAM')
    need(all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:])),'No original byte allocated twice')
    ram_views=dict(baseline['modes']['c']['RAM_views'])
    added_ram={n:i['originalVA']-0x20004000 for n,i in unknown.items() if i['role'].startswith('data_address') and 0x20004000<=i['originalVA']<0x2000c958}
    ram_views.update(added_ram)
    need(added_ram=={'__tsl9v4160_data_2000c038':0x8038},'Only observed new RAM view')
    baseline_und=set(baseline['modes']['c']['undefined_symbols'])
    expected_und=(baseline_und|set(unknown))-set(providers)-set(ram_views)
    need(expected_und=={'__tsl9v4160_call_8180','__tsl9v4160_call_9250','__tsl9v4160_rom_entry'},'Three remaining direct local-stage dependencies')
    known_external={n:baseline_witness.symbol[n]['value'] for n in baseline_und}
    known_external.update({n:i['originalVA'] for n,i in unknown.items()})
    ram_script=work/'real-RAM-view.ld'
    ram_script.write_text('SECTIONS { .bss.tsl9v4160.ram 0 : { KEEP(*(.bss.tsl9v4160.ram))\n'+''.join(n+' = __tsl9v4160_ram + '+hex(o)+';\n' for n,o in sorted(added_ram.items()))+'} }\n',encoding='utf-8')
    layout=work/'original-address-layout.ld'
    text='OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for name,s in sorted(allocations.items(),key=lambda x:x[1]['originalVA']):
        text+=f' {name} {hex(s["originalVA"])}'+(' (NOLOAD)' if s['kind']=='RAM' else '')+f' : {{ KEEP(*({name})) }}\n ASSERT(SIZEOF({name})=={s["bytes"]}, "Original size changed")\n'
    text+=' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n'
    layout.write_text(text,encoding='utf-8')
    witness_script=work/'ADDRESS-WITNESS-ONLY.ld'
    witness_script.write_text('/* Missing entry numbers only; NOT implementations or firmware. */\n'+''.join(n+' = '+hex(known_external[n])+';\n' for n in sorted(expected_und)),encoding='utf-8')
    def check_ram(elf):
        ram=elf.symbol['__tsl9v4160_ram'];need(ram['index'] not in (0,0xfff1) and ram['size']==35160,'Real single RAM carrier')
        need(elf.sections[ram['index']]['type']==8 and elf.sections[ram['index']]['size']==35160,'No duplicated or initialized RAM storage')
        for name,offset in ram_views.items():
            s=elf.symbol[name];need(s['index']==ram['index'] and s['type']==0 and s['size']==0 and s['value']-ram['value']==offset,'Actual section-relative RAM view '+name)
    def check_providers(elf,linked=False):
        for name,s in providers.items():
            v=elf.symbol[name]
            need(v['index']==elf.byname[s['section']]['index'] and v['type']==2 and v['size']==s['size'],'Resolved by actual captured FUNC '+name)
            if linked:need(v['value']==s['originalVA'],'Exact linked provider address '+name)
    def audit_module(elf,plan):
        sections={s['name']:s for s in plan['sections']};defined={s['name']:s for s in plan['defined_symbols']}
        need(elf.kind==1 and {s['name'] for s in elf.sections if s['flags']&2 and s['size']}==set(sections),'Exact new ET_REL allocations')
        need({s['name'] for s in elf.symbols if s['name'] and s['index']==0}==set(plan['expected_undefined_symbols']),'New module keeps true external references')
        for name,s in sections.items():
            b=raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']]
            need(len(b)==s['bytes'] and elf.byname[name]['data']==b,'New source bytes '+name)
            if 'sha256' in s:need(sha(b)==s['sha256'],'Section evidence identity')
        for name,s in defined.items():
            v=elf.symbol[name];need(v['index']==elf.byname[s['section']]['index'] and v['value']==s['originalVA']-sections[s['section']]['originalVA'] and v['type']==s['elf_type'] and v['size']==s['size'],'Real new FUNC provider '+name)
        expected={(r['section'],r['offset']):r for r in plan['relocations']}
        need(len(expected)==len(plan['relocations'])==len(elf.relocations),'Exact relocation count/sites')
        for r in elf.relocations:
            spec=expected[(r['section'],r['offset'])];need(r['type']==spec['type_number'],'Exact new relocation type')
            symbol=elf.symbols[r['symbol_index']]
            if symbol['index']==0:
                need(symbol['name']==spec['target'] and symbol['name'] in plan['expected_undefined_symbols'],'Genuine undefined target')
                value=plan['expected_undefined_symbols'][symbol['name']]['originalVA']+r['addend']
            else:
                need(symbol['index']!=0xfff1,'No ABS new implementation')
                value=sections[elf.sections[symbol['index']]['name']]['originalVA']+symbol['value']+r['addend']
            need(value==spec['target_originalVA']+spec['addend'],'Exact new target/anchor')
        # Independent raw-bit inventory: every direct branch/jump needs a relocation.
        for name,s in sections.items():
            if s['kind']!='code':continue
            offset=0
            while offset<s['bytes']:
                h=struct.unpack_from('<H',elf.byname[name]['data'],offset)[0];width=4 if h&3==3 else 2
                need(offset+width<=s['bytes'],'Whole original instruction')
                w=int.from_bytes(elf.byname[name]['data'][offset:offset+width],'little')
                target=direct_target(s['originalVA']+offset,width,w)
                if target:
                    spec=expected[(name,offset)];need(spec['type_number']==target[0] and spec['target_originalVA']==target[1],'Original direct control-flow relocation')
                offset+=width
    modes={}
    for mode,lang,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();commands=[];objects=[]
        for stem,plan in plans.items():
            obj=folder/(stem+'.o')
            cmd,_=run([cc,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-stack-protector','-fno-builtin','-Wall','-Wextra','-Werror','-x',lang,'-std='+std,'-c',ROOT/'src'/(stem+'.c'),'-o',obj],folder,'compile-'+stem);commands.append(cmd)
            audit_module(ELF(obj),plan);objects.append(obj)
        baseline_object=Path(baseline['modes'][mode]['integrated_object'])
        need(sha(baseline_object.read_bytes())==baseline['modes'][mode]['integrated_sha256'],'Untouched baseline object')
        integrated=folder/'native-dependencies.o'
        cmd,_=run([ld,'-r','--no-relax','-T',ram_script,baseline_object,*objects,'-o',integrated],folder,'integrate-actual-providers');commands.append(cmd)
        merged=ELF(integrated);check_ram(merged)
        expected_relocations=211+sum(len(p['relocations']) for p in plans.values())
        need(len(merged.relocations)==expected_relocations,'All prior and new semantic relocations retained')
        und={s['name'] for s in merged.symbols if s['name'] and s['index']==0};need(und==expected_und,'Strict remaining obligations')
        for s in baseline_unit.sections:
            if s['flags']&2 and s['size']:need(merged.byname[s['name']]['type']==s['type'] and merged.byname[s['name']]['size']==s['size'] and merged.byname[s['name']]['data']==s['data'],'Existing source storage retained')
        check_providers(merged)
        strict=folder/'strict-incomplete.elf'
        cmd,log=run([ld,'--no-relax','--error-limit=0','-T',layout,integrated,'-o',strict],folder,'strict-final-link',False);commands.append(cmd)
        need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',log.decode('utf-8','replace')))==expected_und,'All three real missing entries remain fatal')
        witness=folder/'ADDRESS-WITNESS-ONLY.elf'
        cmd,_=run([ld,'--no-relax','-T',layout,'-T',witness_script,integrated,'-o',witness],folder,'numeric-address-witness');commands.append(cmd)
        linked=ELF(witness);check_ram(linked)
        need({s['name'] for s in linked.sections if s['flags']&2 and s['size']}==set(allocations),'No hidden code/data/stack allocations')
        for name,s in allocations.items():
            v=linked.byname[name];need(v['address']==s['originalVA'] and v['size']==s['bytes'],'Original section extent '+name)
            if s['kind']!='RAM':need(v['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'Every original byte at original address '+name)
        check_providers(linked,True)
        # Prove provider gate rejects real malformed ELF metadata (not just a fake dict).
        bad=bytearray(merged.raw);main_symbol=merged.symbol['__tsl9v4160_main'];changed=False
        for table in merged.sections:
            if table['type']!=2:continue
            strings=merged.sections[table['link']]['data']
            for offset in range(0,table['size'],16):
                start=struct.unpack_from('<I',table['data'],offset)[0];name=strings[start:strings.index(0,start)].decode('ascii')
                if name=='__tsl9v4160_main':struct.pack_into('<H',bad,table['offset']+offset+14,0xfff1);changed=True
        need(changed,'Main provider countercase selected')
        counter=folder/'COUNTERCASE-ABS-main.o';counter.write_bytes(bad);bad_main=ELF(counter).symbol['__tsl9v4160_main']
        need(bad_main['index']!=main_symbol['index'] and bad_main['index']==0xfff1,'Countercase changed actual ELF section index')
        rejected=False
        try:check_providers(ELF(counter))
        except AssertionError:rejected=True
        need(rejected,'Same provider gate must reject ABS-main ELF')
        modes[mode]=dict(passed=True,commands=commands,integrated_object=str(integrated),integrated_sha256=sha(integrated.read_bytes()),numeric_witness_sha256=sha(witness.read_bytes()),code_bytes=1706,RO_bytes=456,allocated_file_bytes=2162,RAM_NOBITS_bytes=35160,relocations=expected_relocations,allocation_sections=len(allocations),undefined_symbols=sorted(und),RAM_views=ram_views,strict_rejected=True,ABS_main_countercase_rejected=True,numeric_witness_is_firmware=False)
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256'] and modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256'],'C/C++ integrated artifacts byte-equal')
    need(source_hashes=={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources},'Source changed during verification')
    report=dict(schema='ID2966-native-dependencies-v1',passed=True,firmware_sha256=sha(raw),source_files=source_hashes,tools={str(p):sha(p.read_bytes()) for p in [cc,ld]},baseline_receipt=str(baseline_path),baseline_receipt_sha256=sha(baseline_path.read_bytes()),allocations=allocations,providers=providers,modes=modes,dynamic_pointer_targets_proved=False,IRQ_ABI_proved=False,firmware_executed=False,emulation=False,network=False,hardware=False,target_ready=False,ota_verified=False,native_bin=False)
    receipt=work/'verification.json';receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,code_bytes=1706,RO_bytes=456,relocations=modes['c']['relocations'],remaining_undefined=3,receipt=str(receipt),native_bin=False)))

if __name__=='__main__':main()
