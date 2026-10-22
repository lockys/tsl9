"""Source-owned register/frame fields only; never execute a RISC-V instruction."""
import hashlib,importlib.util,json,re,struct,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD_SEAL='f42e262c6b6c7a80fa3da77ce6af0b0df7ad70f6a8c9ff664b5eefa940554972'
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SAVE=[[8,40],[1,44],[9,36],[18,32],[19,28],[20,24],[21,20],[22,16],[23,12],[24,8],[25,4]]
RESTORE=[[1,44],[8,40],[9,36],[18,32],[19,28],[20,24],[21,20],[22,16],[23,12],[24,8],[25,4]]
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def context(root,firmware):
    root=Path(root).resolve(strict=True);firmware=Path(firmware).resolve(strict=True);old=case(root,'v4160-event-callback-2026-10-22')/'source-review';need(sha(old/'seal.json')==OLD_SEAL,'Immutable217-instruction source proof')
    for n,pin in read(old/'seal.json')['members'].items():need(sha(old/n)==pin,'Immutable original source proof member '+n)
    need(sha(firmware)==FW,'Actual official ID2966 source');S=load('callback_registers_original',old/'check-source.py');original_decode,E=S.context(root);blob=firmware.read_bytes()[0x614:0x88c];rows=S.validate(blob,original_decode)
    def decode(raw,pc):
        try:return original_decode(raw,pc)
        except ValueError:pass
        h=int.from_bytes(raw[:2],'little');size=4 if h&3==3 else 2;need(len(raw)>=size,'Bounded native instruction');w=int.from_bytes(raw[:size],'little')
        def row(op,rd=None,rs1=None,rs2=None,immediate=None,width=None):return dict(PC=pc,bytes=size,raw_hex=raw[:size].hex(),op=op,rd=rd,rs1=rs1,rs2=rs2,immediate=immediate,target=None,memory_width=width)
        if size==4:
            op=w&127;rd=(w>>7)&31;rs1=(w>>15)&31;rs2=(w>>20)&31;f=(w>>12)&7
            if op==0x33 and w>>25==0 and f in (6,7):return row('or' if f==6 else 'and',rd,rs1,rs2)
            if op==3 and f==1:
                v=w>>20;return row('lh',rd,rs1,immediate=v-4096 if v&2048 else v,width=16)
        elif h&3==1 and h>>13==4 and (h>>10)&3==3 and not h&0x1000 and (h>>5)&3 in (2,3):
            rs1=8+((h>>7)&7);return row('or' if (h>>5)&3==2 else 'and',rs1,rs1,8+((h>>2)&7))
        raise ValueError('Unadmitted bounded native field '+hex(pc)+' '+raw[:size].hex())
    return root,blob,rows,decode,E
def fields(blob,entry,decode):
    rows=[];at=0
    while at<len(blob):r=decode(blob[at:],entry+at);need(r['bytes'] in (2,4) and at+r['bytes']<=len(blob),'Whole actual instruction extent');rows.append(r);at+=r['bytes']
    return rows
def uses(rows,register):return [r for r in rows if any(r[k]==register for k in ('rd','rs1','rs2'))]
def sp_words(rows):return [r for r in rows if r['op'] in ('lw','sw') and r['rs1']==2 and r['memory_width']==32]
def source_gate(rows):
    need(len(rows)==217 and not uses(rows,26) and not uses(rows,27),'All217 explicit operand ports exclude S10/S11')
    need(not any(r['rd']==3 for r in rows),'No original explicit GP write')
    words=sp_words(rows);stores=[[r['rs2'],r['immediate']] for r in words if r['op']=='sw'];loads=[[r['rd'],r['immediate']] for r in words if r['op']=='lw'];need(stores==SAVE and loads==RESTORE and len(words)==22,'Exactly11 original saves/readbacks, slots4..44 and source order');need(not any(r['immediate']==0 for r in words),'No original direct SP+0 word access');need(rows[0]['op']=='addi' and (rows[0]['rd'],rows[0]['rs1'],rows[0]['immediate'])==(2,2,-48),'Original48-byte frame')
    calls=[r for r in rows if r['op']=='jalr' and r['rd']==1];need(len(calls)==15,'Original15 opaque caller-link writes');by={r['PC']:r for r in rows};need((by[0x8682]['op'],by[0x8682]['rd'],by[0x8682]['rs1'],by[0x8682]['immediate'])==('addi',2,2,48) and (by[0x8684]['op'],by[0x8684]['rd'],by[0x8684]['rs1'])==('jalr',0,1),'Original fresh-live-SP epilogue and fresh-RA return');need([r['PC'] for r in rows if r['rd']==2]==[0x8614,0x8682],'Only two original explicit SP writes')
    return dict(raw_instructions=217,explicit_S10_ports=0,explicit_S11_ports=0,frame_bytes=48,direct_frame_words=22,save_order=stores,readback_order=loads,direct_SP0_words=0,opaque_call_links=[dict(PC=r['PC'],RA=r['PC']+r['bytes'],target_register=r['rs1']) for r in calls],normal_return=dict(PC=0x8684,raw_target='fresh READ32(liveSP+44), then clear bit0',SP='current liveSP+48; entrySP equality conditional',saved_frame_reads='fresh liveSP addresses in recorded order'),callee_preserves_S10_S11_proved=False,SP0_never_aliased_or_written_by_callee=False)
def artifact(folder,decode,E):
    path=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf';e=E(path);functions=[s for s in e.symbols if s['info']&15==2 and s['size']];need(e.kind==2 and e.flags==1 and len(functions)==1,'Actual one-function RV32 RVC component');s=functions[0];need(s['name']=='tsl9_callback_native_8614' and s['info']==18 and s['other']==0 and 0<s['index']<len(e.sections),'Actual honest native function');owner=e.sections[s['index']];alloc=[a for a in e.sections if a['flags']&2 and a['size']];need(len(alloc)==1 and alloc[0]==owner and (owner['type'],owner['flags'],owner['address'],owner['alignment'])==(1,6,0x1000,2) and s['value']==0x1000 and owner['size']==s['size'] and not e.relocations and struct.unpack_from('<I',e.raw,24)[0]==0x1000,'Complete actual component allocation, no hidden helper/data/padding or unresolved RELA');body=e.function_bytes(s);rows=fields(body,s['value'],decode);need(not any(s['name'] and s['index']==0 for s in e.symbols),'No unresolved code/provider in actual component')
    text=(folder/'complete-static-disassembly.log').read_text(encoding='utf-8');display=[]
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*(\S+)\s*(.*)$',line)
        if m:display.append((int(m[1],16),bytes.fromhex(m[2]),m[3],m[4]))
    need(len(rows)==len(display),'All actual native instructions have independent LLVM rows')
    for r,(pc,raw,op,args) in zip(rows,display):
        need(pc==r['PC'] and raw.hex()==r['raw_hex'] and op not in ('.word','.2byte','<unknown>'),'Actual LLVM rows cover every native byte');printed={26 if name=='s10' else 27 for name in re.findall(r'\b(s10|s11)\b',args)};ports={r[k] for k in ('rd','rs1','rs2') if r[k] in (26,27)};need(printed==ports,'Raw S10/S11 register ports equal independent LLVM operands')
    words=sp_words(rows);calls=[r for r in rows if r['op']=='jalr' and r['rd']==1]
    return dict(ELF_sha256=sha(path),body_sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),instruction_rows=len(rows),S10_uses=uses(rows,26),S11_uses=uses(rows,27),stack_words=words,call_links=[dict(offset=r['PC']-s['value'],return_offset=r['PC']+r['bytes']-s['value'],target_register=r['rs1']) for r in calls],entry=s['value']),rows
def candidate_gate(rows):
    need(not uses(rows,26) and not uses(rows,27),'Actual candidate contains no explicit S10/S11 operand in ANY instruction')
    need(not any(r['rd']==3 for r in rows),'No candidate explicit physical GP write')
    words=sp_words(rows);stores=[[r['rs2'],r['immediate']] for r in words if r['op']=='sw'];loads=[[r['rd'],r['immediate']] for r in words if r['op']=='lw'];need(sorted(stores)==sorted(SAVE) and loads==RESTORE and len(words)==22,'Candidate has exactly original11 save/restore register-slot pairs, no extra spills');need(all(r['immediate']!=0 for r in words),'No candidate direct SP0 word access');need((rows[0]['op'],rows[0]['rd'],rows[0]['rs1'],rows[0]['immediate'])==('addi',2,2,-48),'Actual48-byte candidate frame');calls=[r for r in rows if r['op']=='jalr' and r['rd']==1];need(len(calls)==15 and sorted(r['rs1'] for r in calls)==[15]*14+[16],'Actual15 RA-writing A5/A6 opaque calls');return dict(passed=True,direct_SP0_words=0,explicit_S10_ports=0,explicit_S11_ports=0,register_slot_sets_equal_original=True,save_order_equal_original=stores==SAVE,opaque_RA_writing_calls=15,all_physical_prefixes_equal_original=False)

def controls(blob,entry,rows,decode,gate):
    # Four field-local mutations of actual code bytes, not generated providers.
    cases=[]
    arithmetic=next(r for r in rows if r['bytes']==4 and r['op'] in ('addi','slli') and r['rd'] not in (0,1,2,3))
    source=next(r for r in rows if r['bytes']==4 and r['op'] in ('addi','slli') and r['rs1'] not in (None,0,1,2,3))
    store=next(r for r in rows if r['bytes']==2 and r['op']=='sw' and r['rs1']==2)
    for label,row,field,value in [('S10 destination',arithmetic,'rd',26),('S11 source',source,'rs1',27),('GP destination',arithmetic,'rd',3),('SP0 store',store,'slot',0)]:
        raw=bytearray(blob);at=row['PC']-entry;word=int.from_bytes(raw[at:at+row['bytes']],'little')
        if field=='rd':word=(word&~(31<<7))|(value<<7)
        elif field=='rs1':word=(word&~(31<<15))|(value<<15)
        else:word&=~0x1f80
        raw[at:at+row['bytes']]=word.to_bytes(row['bytes'],'little');changed=fields(raw,entry,decode)
        try:gate(changed)
        except ValueError as e:cases.append(dict(case=label,PC=row['PC'],rejected=True,reason=str(e)));continue
        raise ValueError('Accepted source-driven register/frame mutation '+label)
    return cases
