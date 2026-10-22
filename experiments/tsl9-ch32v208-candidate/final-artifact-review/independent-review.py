"""Independent stdlib ELF32/byte/numeric review; no build or target execution."""
from pathlib import Path
import hashlib, json, re, struct

_paths = __import__("runpy").run_path(str(next(p for p in Path(__file__).resolve().parents if (p / "scripts/project_paths.py").is_file()) / "scripts/project_paths.py"))

W = _paths["analysis_workspace"]()
D = _paths["project_root"]()
OUT = W/'apk-analysis/tsl9-function-hardware/ch32v208-candidate-bin/final-artifact-review'
ROOT = D/'experiments/tsl9-ch32v208-candidate/build'
BUILDS = {'c': ROOT/'c/9d67b31c0a504ab7835d26e94b1d6802', 'cpp': ROOT/'cpp/4a468349eb29421caee467369d4d45fe'}
SOURCE = W/'apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def check(x, message):
    if not x: raise AssertionError(message)
def sx(x, n): return x-(1<<n) if x&(1<<(n-1)) else x

class ELF:
    def __init__(self, path):
        self.raw = Path(path).read_bytes()
        check(self.raw[:7] == b'\x7fELF\x01\x01\x01', 'ELF32 LE identity')
        h = struct.unpack_from('<HHIIIIIHHHHHH', self.raw, 16)
        self.type,self.machine,_,self.entry,po,so,self.flags,_,pe,pn,se,sn,ni = h
        self.sections = []
        for i in range(sn):
            v = struct.unpack_from('<IIIIIIIIII', self.raw, so+i*se)
            self.sections.append(dict(zip(('name_offset','type','flags','addr','offset','size','link','info','align','entsize'),v), index=i))
        names = self.data(self.sections[ni])
        for s in self.sections: s['name'] = names[s['name_offset']:].split(b'\0',1)[0].decode()
        self.names = {s['name']:s for s in self.sections}
        self.symbols=[]
        for s in self.sections:
            if s['type'] != 2: continue
            st = self.data(self.sections[s['link']])
            for i in range(s['size']//s['entsize']):
                no,val,size,inf,other,idx = struct.unpack_from('<IIIBBH', self.raw,s['offset']+i*s['entsize'])
                self.symbols.append(dict(name=st[no:].split(b'\0',1)[0].decode(),value=val,size=size,bind=inf>>4,type=inf&15,other=other,index=idx))
        self.syms={s['name']:s for s in self.symbols if s['name'] and s['bind'] in (1,2)}
        self.phdr=[]
        for i in range(pn):
            v=struct.unpack_from('<IIIIIIII',self.raw,po+i*pe)
            self.phdr.append(dict(zip(('type','offset','vaddr','paddr','filesz','memsz','flags','align'),v)))
    def data(self,s): return self.raw[s['offset']:s['offset']+s['size']] if s['type']!=8 else b''
    def allocated(self): return [s for s in self.sections if s['flags']&2 and s['size']]
    def und(self): return sorted(s['name'] for s in self.symbols if s['name'] and s['index']==0)
    def word(self,pc):
        for s in self.allocated():
            if s['type']==1 and s['addr']<=pc and pc+4<=s['addr']+s['size']:
                return struct.unpack_from('<I',self.raw,s['offset']+pc-s['addr'])[0]
        raise AssertionError('word outside PROGBITS')

def jal(e,pc,rd):
    w=e.word(pc); check(w&127==0x6f and (w>>7)&31==rd, 'JAL opcode/register')
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    return (pc+sx(imm,21))&0xffffffff
def pair(e,pc,rd):
    a,b=e.word(pc),e.word(pc+4)
    check(a&127==0x17 and (a>>7)&31==rd, 'AUIPC register/opcode')
    check(b&127==0x13 and (b>>12)&7==0 and (b>>7)&31==rd and (b>>15)&31==rd, 'ADDI pair register/opcode')
    return (pc+sx(a&0xfffff000,32)+sx(b>>20,12))&0xffffffff
def addi(e,pc,rd,rs):
    w=e.word(pc); check(w&127==0x13 and (w>>12)&7==0 and (w>>7)&31==rd and (w>>15)&31==rs,'ADDI opcode/register')
    return sx(w>>20,12)

source=SOURCE.read_bytes()
check(len(source)==76800 and sha(SOURCE)=='32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc','original runtime identity')
report={'schema':'independent-final-artifact-review-v1','method':'own stdlib ELF32 parser, numeric RISC-V decoder and direct byte/hash checks; no project audit imports or executions','modes':{}}
for mode, folder in BUILDS.items():
    plan=read(folder/'plan.json'); producer=read(folder/'producer.json')
    e=ELF(folder/'tsl9-ch32v208-candidate.elf'); core=ELF(plan['core_object']['path']); carrier=ELF(folder/'carrier.o')
    binary=(folder/'tsl9-ch32v208-candidate.bin').read_bytes()
    check(e.type==2 and e.machine==243 and e.entry==0x8000 and e.flags==1,'ET_EXEC RV32 RVC soft float entry')
    check(not e.und() and not any(s['type'] in (4,9) and s['size'] for s in e.sections),'no UND or REL/RELA sections')
    check(sha(plan['core_object']['path'])==plan['core_object']['sha256']=='e60e2df377b398c564e18203de2669da62cb8745309eeb29061aa1c17ff04eab','retained core identity')
    check(core.und()==['__tsl9_opaque_address_19d10','__tsl9_rom_entry'],'old core two UND retained')
    alloc=e.allocated(); flash=sorted((s for s in alloc if s['type']==1),key=lambda s:s['addr']); ram=[s for s in alloc if s['type']==8]
    check(len(flash)==692 and len(ram)==1 and len(alloc)==693,'allocated section counts')
    check(len([s for s in flash if s['name'].startswith('.tsl9_carrier_')])==25,'25 carrier sections')
    check(ram[0]['name']=='.tsl9_runtime_ram' and ram[0]['addr']==0x20004000 and ram[0]['size']==35152 and ram[0]['flags']==3,'RAM NOBITS exact shape')
    cursor=0x8000; rebuilt=bytearray(); core_bytes=0; carrier_bytes=0
    for s in flash:
        check(s['addr']==cursor and int(s['name'].rsplit('_',1)[1],16)==s['addr'],'explicit contiguous section VMA')
        payload=e.data(s); check(payload==source[cursor-0x8000:cursor-0x8000+s['size']],'all final section bytes match original')
        if s['name'].startswith('.tsl9_carrier_'):
            cs=carrier.names[s['name']]; check(cs['size']==s['size'] and carrier.data(cs)==payload,'fresh carrier object interval bytes')
            carrier_bytes+=s['size']
        else:
            cs=core.names[s['name']];check(cs['size']==s['size'] and cs['type']==s['type'] and cs['flags']==s['flags'],'retained core section provenance')
            core_bytes+=s['size']
        cursor+=s['size'];rebuilt+=payload
    check(cursor==0x1ac00 and binary==source==bytes(rebuilt),'BIN and independent section reconstruction equal original')
    check(core_bytes==76447 and carrier_bytes==353,'byte provenance split')
    loads=[p for p in e.phdr if p['type']==1]; attrs=[p for p in e.phdr if p['type']==0x70000003]
    check(len(e.phdr)==3 and len(loads)==2 and len(attrs)==1,'2 LOAD and 1 attributes program header')
    f,r=loads
    check((f['vaddr'],f['paddr'],f['filesz'],f['memsz'],f['flags'])==(0x8000,0x8000,76800,76800,5),'runtime PT_LOAD')
    check((r['vaddr'],r['paddr'],r['filesz'],r['memsz'],r['flags'])==(0x20004000,0x20004000,0,35152,6),'RAM PT_LOAD no file bytes')
    check(e.raw[f['offset']:f['offset']+f['filesz']]==source,'runtime PT_LOAD original payload')
    attr=e.names['.riscv.attributes'];check(not attr['flags']&2 and attrs[0]['filesz']==attr['size'],'attributes not allocated or loadable')
    abs_final={n:s['value'] for n,s in e.syms.items() if s['index']==0xfff1}
    abs_core={n:s['value'] for n,s in core.syms.items() if s['index']==0xfff1}
    expected_abs=abs_core|{'__tsl9_rom_entry':0x40000,'__tsl9_opaque_address_19d10':0x19d10}
    check(abs_final==expected_abs,'only two new global ABS bindings')
    for name in ('__tsl9_rom_entry','__tsl9_opaque_address_19d10','__tsl9_stack_top'):
        check(e.syms[name]['type']==0 and e.syms[name]['size']==0,'ABS address-only NOTYPE size0')
    for n,s in core.syms.items():
        if s['index'] in (0,0xfff1): continue
        check(s['index']<len(core.sections),'normal core symbol index')
        sec=core.sections[s['index']]
        if not sec['flags']&2: continue
        matches=[t for t in e.symbols if t['name']==n and t['value']==e.names[sec['name']]['addr']+s['value'] and t['size']==s['size'] and t['type']==s['type']]
        check(len(matches)==1,'defined symbol value/type/size retained: '+n)
    values={'entry_jal':jal(e,0x8000,0),'gp':pair(e,0x183fe,3),'sp':pair(e,0x18406,2),'data_load':pair(e,0x1840e,10),'bss_end':pair(e,0x18436,11),'vector_base':pair(e,0x18464,5),'clock_call':jal(e,0x18474,1),'mepc':pair(e,0x18478,5),'ROM_tail':jal(e,0x18484,0)}
    check(values=={'entry_jal':0x183fe,'gp':0x20004000,'sp':0x20010000,'data_load':0x1a7e0,'bss_end':0x2000c950,'vector_base':0x8038,'clock_call':0x1849e,'mepc':0x8fe6,'ROM_tail':0x40000},'reset numeric targets')
    check(addi(e,0x1841a,12,3)==136 and addi(e,0x18432,10,3)==136,'copy/zero GP+136 boundaries')
    csr=[]
    for pc,expected in zip((0x1844e,0x18454,0x18460,0x18470,0x18480),(0xbc0,0x804,0x300,0x305,0x341)):
        w=e.word(pc);check(w&127==0x73 and w>>20==expected and (w>>7)&31==0 and (w>>15)&31==5,'CSR register fidelity');csr.append({'pc':pc,'csr':w>>20,'funct3':(w>>12)&7})
    check(e.syms['__tsl9_data_load']['value']==0x1a7e0 and e.syms['__tsl9_data_load']['size']==136 and e.syms['__tsl9_data_start']['value']==0x20004000,'initializer symbols')
    init_sections=[s for s in flash if s['addr']<=0x1a7e0 and 0x1a868<=s['addr']+s['size']]
    check(len(init_sections)==1 and init_sections[0]['name']=='.tsl9_ro_0001a2d0','initializer one physical allocation')
    external_refs=[]
    for rs in core.sections:
        if rs['type']!=4:continue
        target_section=core.sections[rs['info']]
        for off in range(0,rs['size'],rs['entsize']):
            loc,info,addend=struct.unpack_from('<IIi',core.raw,rs['offset']+off)
            sym=core.symbols[info>>8]
            if sym['name'] not in ('__tsl9_rom_entry','__tsl9_opaque_address_19d10'):continue
            pc=e.names[target_section['name']]['addr']+loc;rtype=info&255
            dest=jal(e,pc,0) if rtype==17 else pair(e,pc,(e.word(pc)>>7)&31)
            check(dest==expected_abs[sym['name']]+addend,'external reference numerically decoded')
            external_refs.append({'symbol':sym['name'],'pc':pc,'relocation_type':rtype,'decoded_target':dest})
    old=read(plan['retained_producer']['path']);baseline=read(old['baseline_receipt'])
    check(sha(plan['retained_producer']['path'])==plan['retained_producer']['sha256'],'retained producer pinned')
    check(sha(old['baseline_receipt'])==old['baseline_receipt_sha256'],'baseline receipt pinned')
    guards=old['sources']|baseline['source_sha256']
    for p,digest in guards.items():check(sha(p)==digest,'retained compile source hash')
    check(len(guards)==plan['core_source_count']==98,'98 retained compilation-source guards')
    strict=Path(old['strict_log']).read_text(encoding='utf-8-sig')
    check(old['strict_exit']!=0 and sha(old['strict_log'])==old['strict_log_sha256'],'old failure log hash')
    check(sorted(re.findall(r'undefined symbol: (\S+)',strict))==core.und(),'strict two original UND retained')
    for p,digest in producer['sources'].items():check(sha(p)==digest,'candidate tool source guard')
    for name,record in producer['outputs'].items():check(sha(record['path'])==record['sha256'],'producer output hash '+name)
    check(all(producer[n]==0 for n in ('compile_exit','link_exit','objcopy_exit')),'recorded successful tool exits')
    check(producer['compiler_args'][producer['compiler_args'].index('-x')+1]==('c' if mode=='c' else 'c++'),'language path')
    for key in ('target_ready','ota_verified','goal_complete','network','target_executed','hardware','emulation'):check(producer[key] is False and plan[key] is False,'truth label '+key)
    report['modes'][mode]={'ELF_sha256':sha(folder/'tsl9-ch32v208-candidate.elf'),'BIN_sha256':sha(folder/'tsl9-ch32v208-candidate.bin'),'BIN_bytes':len(binary),'zero_named_UND':True,'zero_REL_RELA':True,'allocated_flash_sections':len(flash),'core_sections':667,'carrier_sections':25,'core_bytes':core_bytes,'fresh_carrier_bytes':carrier_bytes,'retained_core_source_guards':len(guards),'program_headers':e.phdr,'absolute_global_symbols':abs_final,'decoded_reset':values,'CSR_writes':csr,'decoded_external_references':external_refs,'initializer_once':True,'old_strict_two_UND_retained':True,'fresh_compile_evidence':'carrier object plus producer compiler args/exits and source/object byte correspondence; review did not rebuild','BIN_equals_original_and_independent_section_reconstruction':True}

manifest=read(D/'export-manifest.json')
for item in manifest['files']:
    p=D/item['file'];check(p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],'preserved product file '+item['file'])
check(manifest['source_model_inputs']==292,'product input count')
report.update(passed=True,preserved_product_manifest_files=len(manifest['files']),product_model_inputs=292,product_input_profile=manifest['source_model_input_profile'],product_manifest_sha256=sha(D/'export-manifest.json'),independent_C_CPP_BIN_equal=True,limitations=['Both linked BINs reproduce the retained V4.1.00 runtime byte for byte; this is static reconstruction equivalence, not high-level semantic source recovery or new functionality.','Existing core object reused with 98 checked active compilation source guards; 292 is preserved product model input count, not fresh compile count.','ROM body/ABI and full lookup extent remain unproved; the final 272 bytes beyond the retained runtime are absent.','No target/hardware/OTA/physical stack or IRQ verification.'],target_ready=False,ota_verified=False,goal_complete=False,network=False,target_executed=False,emulation=False,hardware=False,build_performed_by_reviewer=False)
out=OUT/'review.json';check(not out.exists(),'do not overwrite old review')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'review':str(out),'C_BIN':report['modes']['c']['BIN_sha256'],'CPP_BIN':report['modes']['cpp']['BIN_sha256'],'preserved_product_files':len(manifest['files'])}))
