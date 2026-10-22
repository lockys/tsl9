#!/usr/bin/env python3
"""Bounded resident-candidate field review. No target execution or ISA state."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
CANDIDATES = {
    'V1.40': dict(directory='carrier', original='original/wchble_rom.hex',
                 original_sha256='5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23',
                 segment='REFERENCE-CANDIDATE-ONLY-00040000-0006EC56.bin',
                 segment_sha256='b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941',
                 table=0x4b4ee, lookup=0x4b37c, notification=0x4c25c, copy_source=0x402f0,
                 opaque=[0x45228, 0x4b82c, 0x4ef0a]),
    'V1.31': dict(directory='carrier-dec2023', original='original-dec2023/wchble_rom.hex',
                 original_sha256='11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5',
                 segment='REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin',
                 segment_sha256='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22',
                 table=0x4b456, lookup=0x4b2e4, notification=0x4c1c4, copy_source=0x402b0,
                 opaque=[0x45194, 0x4b794, 0x4ee72])}


def need(value, message):
    if not value:
        raise ValueError(message)


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def sx(number, bits):
    return number - (1 << bits) if number & (1 << (bits - 1)) else number


def decode(raw, pc):
    """Individual instruction fields only; unknown forms stay unknown."""
    w = int.from_bytes(raw[:4], 'little'); h = w & 65535
    size = 4 if h & 3 == 3 else 2
    need(len(raw) >= size, 'No partial instruction')
    result = dict(PC=pc, bytes=size, raw=raw[:size].hex(), op='unknown', rd=None,
                  reads=[], memory=None, target=None, conditional_Xwchc=False)
    def set_(op, rd=None, reads=(), **extra):
        result.update(op=op, rd=rd, reads=list(reads), **extra)
    if size == 4:
        op=w&127; rd=(w>>7)&31; a=(w>>15)&31; b=(w>>20)&31; f=(w>>12)&7
        if op in (0x37,0x17):set_('lui' if op==0x37 else 'auipc',rd,immediate=w&0xfffff000)
        elif op==0x13:
            names={0:'addi',1:'slli',4:'xori',5:'srli',6:'ori',7:'andi'}
            if f in names:set_(names[f],rd,[a],immediate=sx(w>>20,12))
        elif op==3 and f in (0,1,2,4,5):
            name={0:'lb',1:'lh',2:'lw',4:'lbu',5:'lhu'}[f]
            set_(name,rd,[a],memory=dict(kind='load',width={0:8,1:16,2:32,4:8,5:16}[f],base=a,offset=sx(w>>20,12)))
        elif op==0x23 and f in (0,1,2):
            set_({0:'sb',1:'sh',2:'sw'}[f],reads=[a,b],
                 memory=dict(kind='store',width={0:8,1:16,2:32}[f],base=a,register=b,
                             offset=sx((w>>25)<<5|((w>>7)&31),12)))
        elif op==0x63 and f in (0,1,4,5,6,7):
            delta=sx(((w>>31)&1)<<12|((w>>25)&63)<<5|((w>>8)&15)<<1|((w>>7)&1)<<11,13)
            set_({0:'beq',1:'bne',4:'blt',5:'bge',6:'bltu',7:'bgeu'}[f],reads=[a,b],target=pc+delta)
        elif op==0x6f:
            delta=sx(((w>>31)&1)<<20|((w>>21)&1023)<<1|((w>>20)&1)<<11|((w>>12)&255)<<12,21)
            set_('jal',rd,target=pc+delta)
        elif op==0x67 and f==0:set_('jalr',rd,[a],immediate=sx(w>>20,12))
        elif op==0x33 and (w>>25)==0 and f==0:set_('add',rd,[a,b])
    else:
        q=h&3; f=h>>13; d=(h>>7)&31; b=(h>>2)&31; dp=8+((h>>2)&7); ap=8+((h>>7)&7)
        if q in (0,2) and f in (1,5):
            width=8 if q==0 else 16
            offset=(((h>>12)&1)|(((h>>10)&3)<<3)|(((h>>5)&3)<<1)) if q==0 else (((h>>10)&7)<<3)|(((h>>5)&3)<<1)
            load=f==1
            set_('qk.c.'+('lbu' if width==8 else 'lhu') if load else 'qk.c.'+('sb' if width==8 else 'sh'),
                 dp if load else None,[ap] if load else [ap,dp],conditional_Xwchc=True,
                 memory=dict(kind='load' if load else 'store',width=width,base=ap,offset=offset,
                             **({} if load else dict(register=dp))))
        elif q==0 and h>>11==16:
            kind=(h>>5)&3; load=kind<2; width=8 if kind in (0,2) else 16
            offset=((h>>7)&15) if width==8 else (((h>>8)&7)<<1)|(((h>>7)&1)<<4)
            set_('qk.c.'+('lbu' if width==8 else 'lhu')+'sp' if load else 'qk.c.'+('sb' if width==8 else 'sh')+'sp',
                 dp if load else None,[2] if load else [2,dp],conditional_Xwchc=True,
                 memory=dict(kind='load' if load else 'store',width=width,base=2,offset=offset,
                             **({} if load else dict(register=dp))))
        elif q==0 and f in (2,6):
            load=f==2;offset=(((h>>10)&7)<<3)|(((h>>6)&1)<<2)|(((h>>5)&1)<<6)
            set_('lw' if load else 'sw',dp if load else None,[ap] if load else [ap,dp],
                 memory=dict(kind='load' if load else 'store',width=32,base=ap,offset=offset,
                             **({} if load else dict(register=dp))))
        elif q==1 and f in (0,2):set_('addi' if f==0 else 'li',d,[d] if f==0 else [],immediate=sx(((h>>2)&31)|(((h>>12)&1)<<5),6))
        elif q==1 and f==3:
            imm=((((h>>12)&1)<<9)|(((h>>6)&1)<<4)|(((h>>5)&1)<<6)|(((h>>3)&3)<<7)|(((h>>2)&1)<<5)) if d==2 else (((h>>2)&31)|(((h>>12)&1)<<5))<<12
            set_('addi' if d==2 else 'lui',d,[2] if d==2 else [],immediate=sx(imm,10 if d==2 else 18))
        elif q==1 and f in (1,5):
            delta=sx(((h>>12)&1)<<11|((h>>11)&1)<<4|((h>>9)&3)<<8|((h>>8)&1)<<10|((h>>7)&1)<<6|((h>>6)&1)<<7|((h>>3)&7)<<1|((h>>2)&1)<<5,12)
            set_('jal',1 if f==1 else 0,target=pc+delta)
        elif q==1 and f in (6,7):
            delta=sx(((h>>12)&1)<<8|((h>>10)&3)<<3|((h>>5)&3)<<6|((h>>3)&3)<<1|((h>>2)&1)<<5,9)
            set_('beq' if f==6 else 'bne',reads=[ap,0],target=pc+delta)
        elif q==1 and f==4 and ((h>>10)&3)==0:set_('srli',ap,[ap],immediate=((h>>2)&31)|(((h>>12)&1)<<5))
        elif q==2 and f==0:set_('slli',d,[d],immediate=((h>>2)&31)|(((h>>12)&1)<<5))
        elif q==2 and f in (2,6):
            load=f==2;reg=d if load else b
            offset=((((h>>12)&1)<<5)|(((h>>4)&7)<<2)|(((h>>2)&3)<<6)) if load else (((h>>9)&15)<<2)|(((h>>7)&3)<<6)
            set_('lw' if load else 'sw',reg if load else None,[2] if load else [2,reg],
                 memory=dict(kind='load' if load else 'store',width=32,base=2,offset=offset,
                             **({} if load else dict(register=reg))))
        elif q==2 and f==4:
            if b:set_('add' if h&4096 else 'mv',d,[d,b] if h&4096 else [b])
            else:set_('jalr',1 if h&4096 else 0,[d],immediate=0)
    result['known_under_selected_profile']=result['op']!='unknown'
    return result


def rows(raw, address):
    out=[];at=0
    while at<len(raw):
        row=decode(raw[at:],address+at);out.append(row);at+=row['bytes']
    need(at==len(raw),'Complete source bytes, no data fill')
    for i,row in enumerate(out):
        if row['op']=='jalr' and row['rd']==1 and i and out[i-1]['op']=='auipc' and out[i-1]['rd']==row['reads'][0]:
            row['paired_direct_target']=(out[i-1]['PC']+out[i-1]['immediate']+row['immediate'])&0xffffffff
    return out


def local_cfg(instructions):
    bypc={row['PC']:row for row in instructions};todo=[instructions[0]['PC']];visited=set();calls=[]
    while todo:
        pc=todo.pop()
        if pc in visited:continue
        need(pc in bypc,'No unrecorded local CFG escape')
        visited.add(pc);row=bypc[pc];following=pc+row['bytes'];op=row['op']
        if op=='jalr':
            if row['rd']==0:
                need(row['reads']==[1] and row['immediate']==0,'Only RET ends local function')
                continue
            need(row['rd']==1 and 'paired_direct_target' in row,'No unresolved call in captured local body')
            calls.append(row['paired_direct_target']);todo.append(following)
        elif op=='jal':
            if row['rd']==0:todo.append(row['target'])
            else:need(row['rd']==1,'Normal direct link');calls.append(row['target']);todo.append(following)
        elif op in ('beq','bne','blt','bge','bltu','bgeu'):todo.extend((row['target'],following))
        else:todo.append(following)
    need(visited==set(bypc),'Every retained instruction is in bounded local CFG')
    return dict(instructions=len(visited),all_retained_rows_reachable=True,unrecorded_local_escapes=[],
                numeric_direct_call_targets=sorted(calls),call_return_assumption_for_continuation=True)


def closed_pair(functions, cfg):
    wrapper=functions['read_cfg']['rows'];lookup=functions['cfg_lookup']['rows'];allrows=wrapper+lookup
    need(all(r['known_under_selected_profile'] for r in allrows),'No unknown opcode in small closed pair')
    need([(r['op'],r['target']) for r in wrapper if r['op']=='jal' and r['rd']==1]==[('jal',cfg['lookup'])],
         'Exactly the one bounded direct lookup call')
    need(not any(r['op'] in ('jal','jalr') and r['rd']==1 for r in lookup),'Lookup has no nested call')
    need(not any(3 in [r['rd'],*r['reads']] or any(s in [r['rd'],*r['reads']] for s in (8,9,*range(18,28))) for r in allrows),
         'No GP/S-register operand in complete small pair')
    need(all(r['op'] in ('sw','lw','jalr') for r in allrows if 1 in r['reads']),
         'Incoming RA only normal save/return operand, no numeric test')
    need([(r['op'],r['memory']['base'],r['memory']['offset']) for r in wrapper if r['memory'] and r['memory']['width']==32]==
         [('sw',2,12),('lw',2,12)], 'Actual normal return-link stack slot')
    byte=wrapper[4]
    need(byte['op']=='qk.c.lbu' and byte['rd']==10 and byte['memory']==dict(kind='load',width=8,base=10,offset=2),
         'Conditional Xwchc returns the entry+2 BYTE, not a Boolean normalization')
    need(wrapper[8]['op']=='li' and wrapper[8]['rd']==10 and wrapper[8]['immediate']==0,
         'Null lookup returns literal zero')
    return dict(pair_bytes=58,complete_small_pair=True,selected_Xwchc_profile_required=True,
                incoming_semantic_arguments=[10,11],no_GP_or_S4_S7_operand=True,
                incoming_RA_numeric_inspection_seen=False,RA_normal_save_restore_return_only=True,
                nonnull_return_load=dict(width=8,address='lookup_entry+2',zero_extended=True),
                no_entry_return=0,normal_return_range=[0,255],Boolean_only_return_proved=False,
                normal_stack_and_return_memory_assumptions_required=True,
                installed_resident_identified=False,full_application_ABI_proved=False)


def derive(excerpts):
    out={}
    for version,cfg in CANDIDATES.items():
        functions={}
        for name,record in excerpts[version]['functions'].items():
            raw=bytes.fromhex(record['raw']);need(H(raw)==record['sha256'],'Exact retained excerpt hash')
            decoded=rows(raw,record['address'])
            functions[name]=dict(**record,rows=decoded,local_CFG=local_cfg(decoded))
        pair=closed_pair(functions,cfg)
        notification=functions['notification']['rows']
        calls=[r.get('paired_direct_target',r['target']) for r in notification
               if r['op'] in ('jal','jalr') and r['rd']==1]
        need(calls==[0x20000a1c,cfg['opaque'][0],0x20000a48,cfg['opaque'][1],cfg['opaque'][2]],
             'Exact five local call sites; no transitive expansion')
        need(all(r['known_under_selected_profile'] for r in notification),'Local notification decode complete only under Xwchc')
        for name in ('ram_connection','ram_attribute'):
            body=functions[name]['rows']
            need(not any(r['op'] in ('jal','jalr') and r['rd']==1 for r in body),'Small copied helper has no nested call')
            need(not any(x in [r['rd'],*r['reads']] for r in body for x in (3,8,9,*range(18,28))),
                 'Small copied helper has no GP/S operand')
        out[version]=dict(functions=functions,read_cfg_closed_contract=pair,
                          notification_local_calls=calls,notification_deeper_opaque_targets=cfg['opaque'],
                          notification_transitive_RA_S_GP_SP_contract_proved=False,
                          conditional_RAM_mapping=dict(source=cfg['copy_source'],destination=0x20000040,
                                                       RAM_helpers_require_candidate_startup_copy=True),
                          no_target_execution=True)
    return out


def source_check(candidate_root, report):
    profile=json.loads((HERE/'profile-and-header.json').read_bytes())
    for item in profile['profile_inputs']:
        path=candidate_root/item['relative']
        need(path.stat().st_size==item['bytes'] and H(path.read_bytes())==item['sha256'],
             'Actual retained conditional Xwchc reference identity')
    for version,cfg in CANDIDATES.items():
        source=candidate_root/cfg['original'];segment=candidate_root/cfg['directory']/cfg['segment']
        need(H(source.read_bytes())==cfg['original_sha256'] and H(segment.read_bytes())==cfg['segment_sha256'],
             'Explicit candidate HEX/main segment identities')
        data=segment.read_bytes()
        for offset,name in ((0x13c,'table'),(0xd4,'notification')):
            need(struct.unpack_from('<I',data,offset)[0]==cfg[name],'Actual candidate slot pointer')
        for name,item in report['excerpts'][version]['functions'].items():
            address=item['source_flash_address'];size=len(bytes.fromhex(item['raw']))
            need(data[address-0x40000:address-0x40000+size].hex()==item['raw'],
                 'Actual source excerpt bytes '+name)
    return dict(actual_candidate_bytes_read=True,actual_profile_references_read=True,
                versions=list(CANDIDATES),installed_identity_proved=False)


def controls(excerpts):
    import copy
    output=[]
    for version,cfg in CANDIDATES.items():
        for name,function,offset,change in (
            ('wrong_RA_link_register','read_cfg',4,lambda w:(w&~(31<<7))|(5<<7)),
            ('lookup_reads_incoming_S4','cfg_lookup',20,lambda w:(w&~(31<<2))|(20<<2)),
            ('wrong_saved_RA_slot','read_cfg',2,lambda w:w^(1<<9)),
            ('unknown_opcode_is_not_NOP','read_cfg',10,lambda w:0)):
            bad=copy.deepcopy(excerpts);record=bad[version]['functions'][function];raw=bytearray.fromhex(record['raw'])
            size=4 if offset==4 else 2;word=int.from_bytes(raw[offset:offset+size],'little')
            raw[offset:offset+size]=change(word).to_bytes(size,'little');record['raw']=raw.hex();record['sha256']=H(raw)
            try:derive(bad)
            except ValueError as error:output.append(dict(version=version,name=name,rejected=True,reason=str(error)));continue
            raise ValueError('Malformed bounded contract admitted '+name)
    need(decode(bytes.fromhex('0000'),0)['op']=='unknown','Unsupported opcode remains unknown')
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-root',type=Path)
    args=parser.parse_args();report=json.loads((HERE/'evidence.json').read_bytes())
    actual=derive(report['excerpts'])
    need(actual==report['derived'],'Retained source-field/limited-contract rederivation')
    need(controls(report['excerpts'])==report['controls'],'Bounded actual excerpt-field controls')
    seal=json.loads((HERE/'seal.json').read_bytes())
    for name,pin in seal['members'].items():need(H((HERE/name).read_bytes())==pin,'Exact sealed member '+name)
    source=source_check(args.candidate_root.resolve(),report) if args.candidate_root else dict(actual_candidate_bytes_read=False)
    print(json.dumps(dict(passed=True,metadata_and_excerpt_replay=True,**source,
                         complete_selected_profile_read_cfg_pair=True,notification_transitive_contract_proved=False,
                         candidate_is_installed=False,target_execution=False)))


if __name__=='__main__':
    main()
