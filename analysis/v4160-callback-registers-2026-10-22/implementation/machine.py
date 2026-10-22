"""Bounded RV32I/M/C register-field/storage inspection, never ISA execution."""
import hashlib,re,runpy,struct
from pathlib import Path
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fields(raw):
    w=int.from_bytes(raw,'little');q=w&3;rd=None;reads=[];memory=None;stack_adjust=None
    def sx(v,n):return v-(1<<n) if v>>(n-1) else v
    if len(raw)==4:
        need(q==3,'RV32 instruction width');op=w&127;d=(w>>7)&31;a=(w>>15)&31;b=(w>>20)&31;f=(w>>12)&7
        if op in(0x37,0x17,0x6f):rd=d
        elif op in(0x13,0x03,0x67):rd=d;reads=[a]
        elif op in(0x33,):rd=d;reads=[a,b]
        elif op in(0x23,0x63):reads=[a,b]
        else:raise ValueError('unsupported static RV32 opcode '+hex(op))
        if op==3:need(f in(0,1,2,4,5),'integer load width');memory=dict(kind='load',base=a,register=d,offset=sx(w>>20,12),width={0:8,1:16,2:32,4:8,5:16}[f])
        if op==0x23:need(f in(0,1,2),'integer store width');memory=dict(kind='store',base=a,register=b,offset=sx((w>>25)<<5|((w>>7)&31),12),width={0:8,1:16,2:32}[f])
        if op==0x13 and f==0 and d==a==2:stack_adjust=sx(w>>20,12)
    else:
        need(len(raw)==2 and q!=3,'compressed instruction width');f=w>>13;d=(w>>7)&31;b=(w>>2)&31;dp=8+((w>>2)&7);ap=8+((w>>7)&7)
        if q==0:
            if f==0:rd=dp;reads=[2]
            elif f==2:rd=dp;reads=[ap];memory=dict(kind='load',base=ap,register=dp,offset=(((w>>10)&7)<<3)|(((w>>6)&1)<<2)|(((w>>5)&1)<<6),width=32)
            elif f==6:reads=[ap,dp];memory=dict(kind='store',base=ap,register=dp,offset=(((w>>10)&7)<<3)|(((w>>6)&1)<<2)|(((w>>5)&1)<<6),width=32)
            else:raise ValueError('unsupported compressed quadrant0')
        elif q==1:
            if f==0:rd=d;reads=[d];stack_adjust=sx(((w>>2)&31)|(((w>>12)&1)<<5),6) if d==2 else None
            elif f==1:rd=1
            elif f==2:rd=d
            elif f==3:
                rd=d
                if d==2:reads=[2];stack_adjust=sx((((w>>12)&1)<<9)|(((w>>6)&1)<<4)|(((w>>5)&1)<<6)|(((w>>3)&3)<<7)|(((w>>2)&1)<<5),10)
            elif f==4:rd=ap;reads=[ap]+([dp] if ((w>>10)&3)==3 else [])
            elif f==5:pass
            elif f in(6,7):reads=[ap]
            else:raise ValueError('unsupported compressed quadrant1')
        elif q==2:
            if f==0:rd=d;reads=[d]
            elif f==2:rd=d;reads=[2];memory=dict(kind='load',base=2,register=d,offset=(((w>>12)&1)<<5)|(((w>>4)&7)<<2)|(((w>>2)&3)<<6),width=32)
            elif f==6:reads=[2,b];memory=dict(kind='store',base=2,register=b,offset=(((w>>9)&15)<<2)|(((w>>7)&3)<<6),width=32)
            elif f==4:
                if b:rd=d;reads=([d,b] if w&0x1000 else [b])
                else:rd=1 if w&0x1000 else None;reads=[d]
            else:raise ValueError('unsupported compressed quadrant2')
    return dict(destination=rd,reads=reads,memory=memory,stack_adjust=stack_adjust)
def inspect(root,folder,ordered=False,elf_path=None,disassembly=None):
    parser=next(p for p in(root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py') if p.is_file());need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','frozen ELF field parser');E=runpy.run_path(str(parser))['ELF'];e=E(elf_path or folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf');need(e.kind==2 and e.flags==1 and not e.relocations and not any(s['name'] and s['index']==0 for s in e.symbols),'strict linked RV32 RVC no UND/RELA');funcs=[s for s in e.symbols if s['info']&15==2 and s['size']];alloc=[s for s in e.sections if s['flags']&2 and s['size']];need(len(funcs)==len(alloc)==1,'one actual function/allocation, no hidden helpers/data');s=alloc[0];f=funcs[0];size=s['size'];need(size in(624,656) and(s['type'],s['flags'],s['address'],s['alignment'])==(1,6,0x1000,2) and(f['name'],f['value'],f['size'],f['index'],f['info'],f['other'])==('tsl9_callback_native_8614',0x1000,size,s['index'],18,0),'only two actually measured reserved profiles and complete AX storage');need(struct.unpack_from('<I',e.raw,24)[0]==0x1000,'scratch component entry only');payload=e.data(s);rows=[];offset=0
    transcript=(folder/'complete-static-disassembly.log').read_text() if disassembly is None else disassembly
    for line in transcript.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)',line)
        if not m:continue
        pc=int(m[1],16);raw=bytes.fromhex(m[2]);need(pc==0x1000+offset and len(raw) in(2,4) and payload[offset:offset+len(raw)]==raw and m[3] not in('<unknown>','.word','.2byte'),'all disassembly rows exactly contiguous actual ELF bytes');r=fields(raw);need(not ({r['destination'],*r['reads']} & {26,27}),'reserved x26/x27 absent from actual encoded read/write fields');rows.append(dict(address=pc,bytes=len(raw),raw=raw.hex(),**r));offset+=len(raw)
    need(offset==len(payload)==size,'complete measured byte field coverage');need(not any(r['destination']==3 for r in rows),'no encoded GP write');stack=[dict(address=r['address'],**r['memory']) for r in rows if r['memory'] and r['memory']['base']==2];saves=[r for r in stack if r['kind']=='store'];loads=[r for r in stack if r['kind']=='load'];slots=[(1,44),(8,40),(9,36),(18,32),(19,28),(20,24),(21,20),(22,16),(23,12),(24,8),(25,4)];save_slots=[slots[1],slots[0],*slots[2:]] if ordered else slots;need([(r['register'],r['offset']) for r in saves]==save_slots and [(r['register'],r['offset']) for r in loads]==slots and all(r['width']==32 for r in stack),'exact eleven save/load slots, no SP0 or replacement spill');adjust=[r for r in rows if r['destination']==2];need([r['stack_adjust'] for r in adjust]==[-48,48],'only one actual48B frame and pop');need(all(2 not in r['reads'] or r['memory'] or r['stack_adjust'] is not None for r in rows),'no hidden stack-address temporary');calls=[]
    for r in rows:
        raw=bytes.fromhex(r['raw']);w=int.from_bytes(raw,'little')
        if len(raw)==2 and w&0xf07f==0x9002:calls.append(dict(address=r['address'],target_register=(w>>7)&31,RA=r['address']+2))
    gp=[r for r in rows if 3 in r['reads']];need(len(gp)==(6 if size==624 else 16),'exact measured fresh-use or snapshot GP read count');need(sorted(r['target_register'] for r in calls)==[15]*14+[16],'fifteen actual RA-writing opaque A5/A6 calls');return dict(bytes=size,instructions=len(rows),code_sha256=hashlib.sha256(payload).hexdigest(),frame_bytes=48,encoded_registers=sorted({x for r in rows for x in [r['destination'],*r['reads']] if x is not None}),reserved_registers_absent=True,GP_read_sites=[r['address'] for r in gp],GP_writes=0,stack_memory=stack,stack_adjustments=[dict(address=r['address'],value=r['stack_adjust']) for r in adjust],opaque_calls=calls,SP0_access=False,extra_spills=False,relative_source_save_order_preserved=ordered,whole_entry_prefix_identical=False,original_bytes=632,size_within_original_extent=size<=632,uncovered_original_bytes=max(0,632-size),original_placement_admitted=False,original_ABI_admitted=False,target_execution=False)

def transcript_controls(root,folder,ordered=False):
    text=(folder/'complete-static-disassembly.log').read_text();lines=text.splitlines();indices=[i for i,line in enumerate(lines) if re.match(r'^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+',line)];need(len(indices)>2,'actual instruction transcript');variants=[('missing_interior_instruction','\n'.join(line for i,line in enumerate(lines) if i!=indices[1])),('truncated_instruction_range','\n'.join(lines[:indices[-1]])),('unknown_instruction',text.replace('addi','<unknown>',1))];result=[]
    for name,bad in variants:
        try:inspect(root,folder,ordered=ordered,disassembly=bad)
        except ValueError as error:result.append(dict(name=name,rejected=True,reason=str(error)));continue
        raise ValueError('Malformed actual transcript accepted '+name)
    return result
