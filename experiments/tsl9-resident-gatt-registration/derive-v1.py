#!/usr/bin/env python3
"""Derive ten complete root callees;retain original DIV,variable shifts and frame-released tails."""
import argparse,hashlib,json,re,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'experiments/tsl9-resident-gatt-registration/evidence-v1.json'
SHARED=ROOT/'experiments/tsl9-original-startup/build-v1.py'
def need(ok,label):
    if not ok:raise ValueError(label)
def custom_decode(word):
    regs=['s0','s1','a0','a1','a2','a3','a4','a5']
    if word&0xf803==0x8000:
        kind=(word>>5)&3
        imm=(word>>7)&15 if kind in [0,2]else((word>>8)&7)*2+((word>>7)&1)*16
        return ['qk.c.lbusp','qk.c.lhusp','qk.c.sbsp','qk.c.shsp'][kind]+' '+regs[(word>>2)&7]+', '+str(imm)+'(sp)'
    code=word&0xe003
    if code not in [0x2000,0xa000,0x2002,0xa002]:return None
    imm=(((word>>10)&7)*8 if code&2 else((word>>10)&3)*8+((word>>12)&1))+((word>>5)&3)*2
    return {0x2000:'qk.c.lbu',0xa000:'qk.c.sb',0x2002:'qk.c.lhu',0xa002:'qk.c.sh'}[code]+' '+regs[(word>>2)&7]+', '+str(imm)+'('+regs[(word>>7)&7]+')'

def generate():
    need(hashlib.sha256(SHARED.read_bytes()).hexdigest()=='1f6e3673c24a5d85c62d55ec8d8390b80225577010d81c8aba5c4b6750e208b5','Frozen static control decoder')
    B=runpy.run_path(str(SHARED),run_name='positive_static_library')
    e=json.loads(EVIDENCE.read_bytes());carrier=(ROOT/e['firmware']).read_bytes()
    need(hashlib.sha256((ROOT/e['instruction_reference']).read_bytes()).hexdigest()==e['instruction_reference_sha256'],'Pinned primary encoding definition')
    need(len(e['official_vectors']['checked'])==52 and all(custom_decode(v['word'])==v['instruction']for v in e['official_vectors']['checked']),'All52 positive eight-family vectors')
    need(all(custom_decode(int.from_bytes(bytes.fromhex(o['bytes']),'little'))==o['opcode']for f in e['selected_functions']for o in f['operations']if o.get('conditional_Xwchc')),'Every actual primary operand')
    class MappedCandidate:
        def __getitem__(self,key):
            start,end=key.start+0x8000,key.stop+0x8000
            rows=[f for f in e['selected_functions']if f['start']<=start and end<=f['end']]
            need(len(rows)==1,'One explicit conditional SDK source mapping')
            f=rows[0];at=f['source_start']+start-f['start']-0x40000
            return carrier[at:at+end-start]
    fw=MappedCandidate()
    need(hashlib.sha256(carrier).hexdigest()==e['firmware_sha256'],'Original firmware')
    fs=e['selected_functions'];ops={};entries={f['start']:f['name']for f in fs}
    need(len(fs)==4 and [(f['start'],f['end'])for f in fs]==[(280038, 280100), (280100, 280202), (314914, 315170), (315170, 315286)],'Four complete original SDK bodies')
    for f in fs:
        at=f['start']
        for o in f['operations']:
            raw=bytes.fromhex(o['bytes'])
            need(o['addr']==at and len(raw)==o['size']==(4 if raw[0]&3==3 else 2),'Whole contiguous original instruction')
            need(raw==fw[at-0x8000:at-0x8000+len(raw)] and o['opcode']!='invalid','Actual valid selected firmware bytes')
            ops[at]=o;at+=len(raw)
        need(at==f['end'],'Complete selected function')
    need(len(ops)==219 and sum(o['size']for o in ops.values())==536,'Full536B219i')
    starts=set(entries);decoded={};targets={int(k):v for k,v in e['target_names'].items()}
    for pc,o in ops.items():
        d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
        if d:
            decoded[pc]=d
            if d[1]in ops:starts.add(d[1])
            else:need(d[1]in targets,'Named actual external target')
        if d or o['type']in ('ucall','rjmp','ret','call','jmp','cjmp'):
            if pc+o['size']in ops:starts.add(pc+o['size'])
    regions=[];name_by_pc={pc:entries.get(pc,'tsl9_resident_gatt_registration_block_'+format(pc,'x'))for pc in starts}
    targets.update(name_by_pc);ordered=sorted(starts)
    for i,pc in enumerate(ordered):
        function_end=next(f['end']for f in fs if f['start']<=pc<f['end'])
        end=min(ordered[i+1],function_end)if i+1<len(ordered)else function_end
        raw=fw[pc-0x8000:end-0x8000]
        regions.append(dict(name=name_by_pc[pc],start=pc,end=end,bytes=end-pc,original_sha256=hashlib.sha256(raw).hexdigest()))
    pairs={};skipped=set()
    for pc,o in ops.items():
        a=int.from_bytes(bytes.fromhex(o['bytes']),'little')
        if o['size']!=4 or a&127!=0x17 or pc+4 not in ops:continue
        oo=ops[pc+4];b=int.from_bytes(bytes.fromhex(oo['bytes']),'little')
        if oo['size']!=4 or b&0x707f!=0x67 or (b>>15)&31!=(a>>7)&31 or (b>>7)&31 not in [0,(a>>7)&31]:continue
        imm=b>>20;imm=imm-4096 if imm&2048 else imm
        target=(pc+(a&0xfffff000)+imm)&0xffffffff
        if target in targets:
            pairs[pc]=dict(PC=pc,target_PC=target,target=targets[target]);skipped.add(pc+4)
    need(set(pairs)=={int(k)for k in e['reference_roles']}and len(pairs)==6,'Six actual far-call pairs')
    A={f'a{i}'for i in range(6)};widths={'lw':(32,False),'lbu':(8,False),'lhu':(16,False),'lb':(8,True),'lh':(16,True),'sw':(32,False),'sb':(8,False),'sh':(16,False)}
    def port(op,width):
        return '    PORT(".option push\\n.option '+('norvc'if width==4 else'rvc')+'\\n'+op+'\\n.option pop\\n");'
    def imm(n):return f'UINT32_C(0x{int(n,0)&0xffffffff:08x})'
    lines=['#include <stdint.h>','#if !defined(__riscv) || __riscv_xlen != 32','#error Original RV32 private regions only; no host ROM or radio model.','#endif','#ifdef __cplusplus','#define ENTRY extern "C"','#else','#define ENTRY','#endif',
     '#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))',
     '#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")',
     '#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")',
     '#define PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")','',
     '/* Four complete conditional SDK GATT registration/UUID bodies:536B/219i; installed ROM identity unproved. Register-bound C',
     ' * unsigned arithmetic and fresh volatile accesses retain original data flow.',
     ' * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU',
     ' * and original branch/call/literal roles. All regions require original layout.',
     ' * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */','']
    controls=[];literal=[]
    for r in regions:
        lines += [f"/* Original0x{r['start']:X}..0x{r['end']:X}. */",f"REGION void {r['name']}(void)",'{','    REGS;']
        bases=set()
        def base(reg):
            if reg in A:return reg
            need(reg in {'gp','sp','s0','s1'},'Supported explicit register base')
            name='original_'+reg
            if reg not in bases:
                lines.append(f'    register uintptr_t {name} __asm__("{reg}");');bases.add(reg)
            lines.append(f'    __asm__ volatile("":"=r"({name})::"memory");')
            return name
        for pc in sorted(p for p in ops if r['start']<=p<r['end']):
            o=ops[pc];text=o['opcode'];mn,*rest=text.split(' ',1);args=[x.strip()for x in rest[0].split(',')]if rest else []
            if pc in skipped:continue
            if pc in pairs:
                p=pairs[pc];need(pc+8<=r['end'],'Whole callable address in one region')
                p=dict(p,owner=r['name'],offset=pc-r['start'],reference_kind=e['reference_roles'][str(pc)]['reference_kind'],data_contents_provided=False);literal.append(p)
                rd=args[0];label='.Lresident_gatt_registration_literal_'+format(pc,'x');link='zero'if(int.from_bytes(bytes.fromhex(ops[pc+4]['bytes']),'little')>>7)&31==0 else rd
                lines.append(f'    PORT("{label}:\\n.option push\\n.option norvc\\nauipc {rd},0\\n.reloc .-4,R_RISCV_PCREL_HI20,{p["target"]}\\njalr {link},0({rd})\\n.reloc .-4,R_RISCV_PCREL_LO12_I,{label}\\n.option pop\\n");')
            elif pc in decoded:
                kind,target=decoded[pc];symbol=targets[target]
                if kind==17:
                    word=int.from_bytes(bytes.fromhex(o['bytes']),'little');insn='jal '+('zero'if (word>>7)&31==0 else'ra')
                elif kind==45:
                    word=int.from_bytes(bytes.fromhex(o['bytes']),'little');insn='c.jal'if (word>>13)&7==1 else'c.j'
                elif kind==44:insn=('c.beqz'if mn=='beqz'else'c.bnez')+' '+args[0]
                else:insn=mn+' '+','.join(args[:-1])
                label='.Lresident_gatt_registration_edge_'+format(pc,'x');rel={16:'BRANCH',17:'JAL',44:'RVC_BRANCH',45:'RVC_JUMP'}[kind]
                separator=' 'if kind==45 else','
                lines.append(f'    PORT("{label}:\\n.option push\\n.option '+('norvc'if o['size']==4 else'rvc')+f'\\n{insn}{separator}{label}\\n.option pop\\n.reloc .-{o["size"]},R_RISCV_{rel},{symbol}\\n");')
                controls.append(dict(owner=r['name'],offset=pc-r['start'],PC=pc,size=o['size'],type=kind,target=symbol,target_PC=target))
            elif mn in widths and len(args)==2 and (args[0]in A or args[0]=='zero'):
                mat=re.fullmatch(r'(-?(?:0x[0-9a-f]+|\d+))\((\w+)\)',args[1]);need(mat is not None,'Explicit original memory operand')
                offset,reg=mat.groups()
                if reg not in A|{'gp','sp'}:lines.append(port(text,o['size']));continue
                ptr=base(reg);bits,signed=widths[mn];typ=('int'if signed else'uint')+str(bits)+'_t'
                address=f'(uintptr_t)({ptr} + {imm(offset)})'
                if mn.startswith('l'):lines.append(f'    {args[0]} = *(volatile {typ} *){address}; LIVE;')
                else:lines.append(f'    *(volatile {typ} *){address} = ({typ})'+('0'if args[0]=='zero'else args[0])+'; LIVE;')
            elif mn=='sltiu' and args[0]in A and args[1]in A:
                lines.append(f'    {args[0]} = (uint32_t)({args[1]} < {imm(args[2])}); LIVE;')
            elif mn in ('snez','seqz') and args[0]in A and args[1]in A:
                op = '!=' if mn=='snez' else '=='
                lines.append(f'    {args[0]} = (uint32_t)({args[1]} {op} UINT32_C(0)); LIVE;')
            elif mn=='neg' and args[0]in A and args[1]in A:
                lines.append(f'    {args[0]} = UINT32_C(0) - {args[1]}; LIVE;')
            elif mn=='li' and args[0]in A:lines.append(f'    {args[0]} = {imm(args[1])}; LIVE;')
            elif mn=='lui' and args[0]in A:lines.append(f'    {args[0]} = UINT32_C(0x{(int(args[1],0)<<12)&0xffffffff:08x}); LIVE;')
            elif mn in ('addi','andi','xori','ori','slli','srli') and args[0]in A and args[1]in A|{'gp'}:
                rd,rs,n=args;v=base(rs);operator={'addi':'+','andi':'&','xori':'^','ori':'|','slli':'<<','srli':'>>'}[mn]
                lines.append(f'    {rd} = {v} {operator} {imm(n)}; LIVE;')
            elif mn in ('mul','and','or','xor','add','sub') and all(x in A for x in args):
                rd,rs1,rs2=args;operator={'mul':'*','and':'&','or':'|','xor':'^','add':'+','sub':'-'}[mn]
                lines.append(f'    {rd} = {rs1} {operator} {rs2}; LIVE;')
            elif mn=='c.srli' and len(args)==3 and args[0]==args[1]:
                lines.append(port('c.srli '+args[0]+','+args[2],o['size']))
            elif o.get('conditional_Xwchc'):
                word=int.from_bytes(bytes.fromhex(o['bytes']),'little')
                need(custom_decode(word)==text,'Actual primary Xwchc operand decode')
                lines.append('    /* Conditional Xwchc: '+text+'. */')
                lines.append(port('.2byte 0x'+format(word,'04x'),2))
            else:lines.append(port(text,o['size']))
        lines += ['    __builtin_unreachable();','}','']
    need(len(literal)==6,'Six actual far-call pairs')
    undefined=sorted({x['target']for x in controls+literal if x['target']not in {r['name']for r in regions}})
    return dict(source='\n'.join(lines),regions=regions,controls=controls,PC_relative_pairs=literal,literal_data=None,undefined=undefined)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--summary',action='store_true');p.add_argument('--counts',action='store_true');p.add_argument('--metadata-part',type=int);p.add_argument('--source-part',type=int);a=p.parse_args();g=generate()
    metadata=json.dumps({k:v for k,v in g.items()if k!='source'}|dict(source_chars=len(g['source'])),ensure_ascii=True)
    if a.counts:print(json.dumps(dict(regions=len(g['regions']),controls=len(g['controls']),pairs=len(g['PC_relative_pairs']),undefined=len(g['undefined']),source_chars=len(g['source']),metadata_chars=len(metadata))))
    elif a.summary:print(metadata)
    elif a.metadata_part is not None:print(json.dumps(metadata[a.metadata_part*7000:(a.metadata_part+1)*7000],ensure_ascii=True))
    elif a.source_part is not None:print(json.dumps(g['source'][a.source_part*7000:(a.source_part+1)*7000],ensure_ascii=True))
    else:print(json.dumps(g,ensure_ascii=True))
