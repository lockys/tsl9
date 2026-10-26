"""Derive a conditional trap profile from original bytes and saved official headers."""
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def inspect(reference_root):
    S=load(HERE/'spec-v1.json');P=load(HERE/'source-provenance.json');headers={};primary=[]
    for row in P['references']:
        path=reference_root/row['relative_path'];manifest=reference_root/row['manifest_relative_path'];need(sha(path)==row['sha256']and path.stat().st_size==row['bytes']and sha(manifest)==row['manifest_sha256'],'Actual saved primary file and provenance pins')
        actual=next(v for v in load(manifest)if v.get(row['manifest_name_key'])==path.name);need(actual['sha256']==row['sha256']and actual['source_url']==row['source_url']and actual['repository_commit']==row['repository_commit'],'Original primary manifest correspondence');headers[path.name]=path.read_text(encoding='utf-8');primary.append(dict(path=row['path'],sha256=sha(path),source_url=row['source_url'],repository_commit=row['repository_commit']))
    h=headers['wch-ch32v20x.h'];core=headers['wch-core_riscv.h'];enum={};lines={}
    for name in ['Ecall_M_Mode_IRQn','Ecall_U_Mode_IRQn','BB_IRQn','LLE_IRQn']:
        matches=[(i+1,re.fullmatch(r'\s*'+name+r'\s*=\s*(\d+)\s*,.*',line))for i,line in enumerate(h.splitlines())];found=[(i,m)for i,m in matches if m];need(len(found)==1,'Unique official IRQ enum');i,m=found[0];enum[name]=int(m[1]);lines[name]=i
    need(enum==dict(Ecall_M_Mode_IRQn=5,Ecall_U_Mode_IRQn=8,BB_IRQn=63,LLE_IRQn=64),'Pinned device exception and BLE indices')
    needle='interrupt nesting enable(CSR-0x804 bit1 = 1)';need(core.count(needle)==1 and core.count('interrupt nesting disable(CSR-0x804 bit1 = 0)')==1,'Primary header documents CSR804 bit1 only');core_line=next(i+1 for i,l in enumerate(core.splitlines())if needle in l)
    for k,pin in S['inputs'].items():need(sha(ROOT/k)==pin,'Existing original/candidate proof input identity')
    app=(ROOT/S['firmware']).read_bytes();m=load(ROOT/S['startup_source_map']);rows=[o for o in m['instructions']if 0x186aa<=o['PC']<0x18724];need(len(rows)==33,'Actual complete reset prefix rows')
    pos=0x186aa
    for o in rows:
        raw=bytes.fromhex(o['bytes']);need(o['PC']==pos and app[pos-0x8000:pos-0x8000+len(raw)]==raw,'Actual original reset PC/file-base correspondence');pos+=len(raw)
    need(pos==0x18724,'Complete122-byte reset prefix without gaps')
    ops={o['PC']:o for o in rows}
    def word(pc,size=4):
        b=bytes.fromhex(ops[pc]['bytes']);need(len(b)==size,'Actual instruction width');return int.from_bytes(b,'little')
    def sext(v,b):return v-(1<<b)if v&(1<<(b-1))else v
    def upper(pc,rd,opcode):
        w=word(pc);need(w&127==opcode and(w>>7)&31==rd,'Actual U-type opcode/register');return sext(w&0xfffff000,32)
    def imm(pc,rd,rs,funct=0):
        w=word(pc);need(w&127==0x13 and(w>>7)&31==rd and(w>>15)&31==rs and(w>>12)&7==funct,'Actual immediate opcode/registers');return sext(w>>20,12)
    def li(pc,rd):
        w=word(pc,2);need(w&0xe003==0x4001 and(w>>7)&31==rd,'Actual C.LI fields');return sext(((w>>12)&1)*32+((w>>2)&31),6)
    def csr(pc,address,funct,rs):
        w=word(pc);need(w&127==0x73 and(w>>7)&31==0 and(w>>12)&7==funct and(w>>15)&31==rs and w>>20==address,'Actual CSR write/set fields')
    gp=(0x186aa+upper(0x186aa,3,0x17)+imm(0x186ae,3,3))&0xffffffff;sp=(0x186b2+upper(0x186b2,2,0x17)+imm(0x186b6,2,2))&0xffffffff
    copy_end=gp+imm(0x186c6,12,3);zero_start=gp+imm(0x186de,10,3);zero_end=(0x186e2+upper(0x186e2,11,0x17)+imm(0x186e6,11,11))&0xffffffff
    cache_value=li(0x186f8,5);csr(0x186fa,0xbc0,1,5);reset804=li(0x186fe,5);csr(0x18700,0x804,1,5);mstatus_set=(upper(0x18704,5,0x37)+imm(0x18708,5,5))&0xffffffff;csr(0x1870c,0x300,2,5)
    vector_base=(0x18710+upper(0x18710,5,0x17)+imm(0x18714,5,5))&0xffffffff;mode_bits=imm(0x18718,5,5,6);csr(0x1871c,0x305,1,5);mtvec=vector_base|mode_bits
    need((gp,sp,copy_end,zero_start,zero_end,cache_value,reset804,mstatus_set,vector_base,mode_bits,mtvec)==(0x20004000,0x20010000,0x20004080,0x20004080,0x2000c958,31,3,0x1888,0x8038,3,0x803b),'All independent reset numeric operands')
    previous=load(ROOT/'experiments/tsl9-resident-lle-callback-gateway/evidence-v1.json');restore=previous['original_APP']['references'][0];op={o['addr']:o for o in restore['operations']};need(bytes.fromhex(op[0x8448]['bytes'])==app[0x448:0x44c]and bytes.fromhex(op[0x844c]['bytes'])==app[0x44c:0x450],'Actual restore mask/write reference')
    liw=int.from_bytes(app[0x448:0x44c],'little');csrw=int.from_bytes(app[0x44c:0x450],'little');need(liw&127==0x13 and(liw>>7)&31==11 and(liw>>15)&31==0 and(liw>>12)&7==0 and sext(liw>>20,12)==32,'Actual restore mask32 ADDI fields');need(csrw&127==0x73 and(csrw>>7)&31==0 and(csrw>>12)&7==2 and(csrw>>15)&31==11 and csrw>>20==0x804,'Actual restore CSRRS preserves other bits')
    vectors=[]
    for name,index in enum.items():
        storage=vector_base+index*4;value=int.from_bytes(app[storage-0x8000:storage-0x8000+4],'little');vectors.append(dict(name=name,index=index,storage=storage,value=value,primary_enum_line=lines[name]))
    need([v['value']for v in vectors]==[0x8448,0x8448,0x1873e,0x8498],'Actual APP vector words correspond to pinned primary enum indices')
    pointer=gp+384;need(zero_start<=pointer and pointer+4<=zero_end and pointer%4==0,'LLE GP+384 word lies wholly inside original zero interval')
    need(previous['original_APP_frame_match_is_conditional']and previous['LLE_MEPC_assignment_references_gateway_proved_static']and not previous['physical_trap_route_proved'],'Prior conditional gateway evidence remains limited')
    return dict(schema='TSL9-conditional-trap-profile-evidence-v1',passed=True,scope='Static original bytes and saved official definitions;no execution or physical observation',primary_references=primary,official_CSR804_nesting_line=core_line,reset_prefix=dict(start=0x186aa,end=0x18724,bytes=122,instructions=len(rows),sha256=hashlib.sha256(app[0x106aa:0x10724]).hexdigest(),operations=rows),initial_GP=gp,initial_SP=sp,copy_end=copy_end,zero_start=zero_start,zero_end=zero_end,LLE_GP_plus384_pointer=pointer,LLE_pointer_is_zeroed_if_original_reset_completes=True,LLE_pointer_nonzero_before_dispatch_not_proved=True,reset_CSR804_write=reset804,reset_CSR804_documented_nesting_bit_set=True,restore_CSR804_set_mask=32,restore_CSR804_preserves_bit1=True,restore_bit5_physical_meaning_proved=False,cache_CSRBC0_write=cache_value,mstatus_set_mask=mstatus_set,vector_base=vector_base,mtvec_write=mtvec,mtvec_low_bits=mode_bits,vector_enum_correspondence=vectors,mtvec_mode3_dispatch_semantics_proved=False,required_no_early_unbound_LLE_dispatch=True,GP_stability_after_resident_calls_proved=False,SDK_installed_identity_proved=False,physical_IRQ_or_ECALL_frame_proved=False,global_stack_or_IRQ_budget_proved=False,APP_byte_coverage_unchanged=95.54,new_APP_CODE_bytes=0,new_SDK_CODE_bytes=0,new_BIN=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
def source(e):
    constants={'INITIAL_GP':e['initial_GP'],'INITIAL_SP':e['initial_SP'],'ZERO_START':e['zero_start'],'ZERO_END':e['zero_end'],'LLE_POINTER':e['LLE_GP_plus384_pointer'],'VECTOR_BASE':e['vector_base'],'MTVEC_WRITE':e['mtvec_write'],'RESET_CSR804':e['reset_CSR804_write'],'RESTORE_CSR804_SET':e['restore_CSR804_set_mask']}
    text='#include <stdint.h>\n#if !defined(__riscv) || __riscv_xlen != 32\n#error Offline RV32 compile-only evidence; never execute on host or hardware.\n#endif\n#ifdef __cplusplus\n#define CHECK static_assert\n#else\n#define CHECK _Static_assert\n#endif\n/* Numeric constraints only: no functions, DATA, firmware provider or startup policy. */\n'
    text+=''.join('#define TSL9_'+k+' UINT32_C(0x'+format(v,'x')+')\n'for k,v in constants.items())
    for v in e['vector_enum_correspondence']:
        key=v['name'].upper();text+='#define TSL9_'+key+' '+str(v['index'])+'u\n';text+='CHECK(TSL9_VECTOR_BASE + TSL9_'+key+' * 4u == UINT32_C('+hex(v['storage'])+'), "pinned enum vector word location");\n'
    text+='CHECK(TSL9_LLE_POINTER == TSL9_INITIAL_GP + 384u, "initial live GP-relative callback word");\nCHECK(TSL9_LLE_POINTER >= TSL9_ZERO_START && TSL9_LLE_POINTER + 4u <= TSL9_ZERO_END, "callback word initially falls in zero interval");\nCHECK((TSL9_MTVEC_WRITE & ~UINT32_C(3)) == TSL9_VECTOR_BASE && (TSL9_MTVEC_WRITE & 3u) == 3u, "original encoded vector operands only; mode semantics unproved");\nCHECK((TSL9_RESET_CSR804 & 2u) == 2u, "primary candidate nesting bit initially set");\nCHECK((TSL9_RESTORE_CSR804_SET & 2u) == 0u, "restore CSRRS mask does not clear or set nesting bit");\nCHECK(120u + 4u <= 128u && 29u * 4u == 116u, "prior inherited frame arithmetic only");\n'
    return text
