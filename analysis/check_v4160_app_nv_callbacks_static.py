"""APP config callbacks and conditional copy: bytes/operands/CFG only.

No target instruction, provider, buffer, peripheral or polling loop runs or
is emulated. Algebra checks below operate on host integers, without memory.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_config_io_static as io

init, ROOT, LIB, MASK = io.init, io.ROOT, io.LIB, io.MASK
check, sx = init.check, init.sx
OUT = Path(__file__).with_name('v4160-app-nv-callbacks-static.json')
APP_BODIES = (
 ('read',0x1979a,30,13,'e9e2a0f4b50184fa5c7b37ee004867f393b8c960fe9e66e81dc40af897114f62'),
 ('write',0x197be,50,20,'3151a48b2f1025b196bfaf5de65799da21b9f699d3049d88879e4c4d3a5a8426'),
 ('unlock',0x18e98,30,10,'189df44380136df661f68edac275f96adf74345b610e415e0daba5d34c36b604'),
 ('lock',0x18eb6,14,6,'20c1f57d6f8294aa24230996a9311f4a73ae3da72b0eed0acc4da3e2330ea7de'),
 ('erase',0x18ec4,46,19,'40e81eda78577543dd451a59487376d58352cb623c796194e0fcc9c12b23995d'),
 ('program',0x18ef2,100,38,'8cd6ddd7edd2d5a0adb776d396c8cb499d64ce974f38df7e651f9af720114dd8'),
 ('timer',0x19764,54,22,'0bcb7577e755f1ca9736b0fd0b05e4d3f0a0e1e0cd3a59976b947191d3df74a4'))
STORES = {'read':[10], 'write':[2,4,6], 'unlock':[16,22,24,26],
          'lock':[10], 'erase':[16,18,26,42], 'program':[14,52,76,96],
          'timer':[10,20,22,30,38,50], 'copy':[8,28,48]}
WRITES = {'read':[1,2,10,11,12,14,15], 'write':[1,2,8,10,11,12],
          'unlock':[13,14,15], 'lock':[13,14,15], 'erase':[10,13,14,15],
          'program':[10,12,13,14,15,16], 'timer':[12,13,14,15], 'copy':[13,14,15,16]}
CYCLES = {'erase':[[28,30,32]], 'program':[[16,18,20],[26,28,30],
          [40,44,48,52,56,58,60,62,64],[82,84,86]], 'timer':[[40,42,44]],
          'copy':[[34,38,42,46,48,52]]}


def decode(raw,start):
    nodes,off = {},0
    while off < len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'APP callback partial instruction')
        chunk,pc=raw[off:off+size],start+off;w=int.from_bytes(chunk,'little')
        d=dict(pc=pc,bytes=chunk.hex(),size=size)
        if size==4 and w&0xfe00707f==0x33:
            d.update(op='add',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif size==4 and w&0x707f==0x6013:
            d.update(op='ori',rd=w>>7&31,rs1=w>>15&31,imm=sx(w>>20,12))
        elif size==4 and w&0x707f==0x23:
            d.update(op='store',rs1=w>>15&31,rs2=w>>20&31,
                     imm=sx((w>>25)<<5|(w>>7&31),12),width=1)
        else:d=io.decode(chunk,pc)[pc]
        nodes[pc]=d;off+=size
    return nodes


def specs(role,pc):
    # All body bytes are separately pinned. These operands expose the specific
    # dataflow/loop/preservation statements, before the complete identity check.
    rows=[]
    def e(off,op,**kw):rows.append((off,dict(op=op,**kw)))
    def load(off,rd,rs1,imm=0,width=4):e(off,'load',rd=rd,rs1=rs1,imm=imm,width=width)
    def store(off,rs2,rs1,imm=0,width=4):e(off,'store',rs2=rs2,rs1=rs1,imm=imm,width=width)
    def poll(off,reg,mask,branch):
        e(off,'andi',rd=reg,rs1=reg,imm=mask)
        e(off+2,branch,rs1=reg,target=pc+off-2)
    if role=='read':
        e(0,'lui',rd=15,imm=LIB);load(4,15,15,76)
        e(6,'addi',rd=2,rs1=2,imm=-16);e(8,'mv',rd=14,rs2=12);store(10,1,2,12)
        e(12,'slli',rd=12,rs1=11,imm=2);e(16,'mv',rd=11,rs2=10);e(18,'mv',rd=10,rs2=14)
        e(20,'call_indirect',rd=1,rs1=15);load(22,1,2,12);e(24,'li',rd=10,imm=0)
        e(26,'addi',rd=2,rs1=2,imm=16);e(28,'jr',rs1=1)
    elif role=='write':
        e(0,'addi',rd=2,rs1=2,imm=-32);store(2,1,2,28);store(4,8,2,24);store(6,12,2,12)
        e(8,'mv',rd=8,rs2=10)
        for off,target in ((10,0x18e98),(16,0x18ec4),(26,0x18ef2),(30,0x18eb6),(36,0x19764)):
            e(off,'jal',rd=1,target=target)
        e(14,'mv',rd=10,rs2=8);load(20,12,2,12);e(22,'mv',rd=10,rs2=8);e(24,'mv',rd=11,rs2=12)
        e(34,'li',rd=10,imm=1);load(40,1,2,28);load(42,8,2,24);e(44,'li',rd=10,imm=0)
        e(46,'addi',rd=2,rs1=2,imm=32);e(48,'jr',rs1=1)
    elif role=='unlock':
        e(0,'lui',rd=13,imm=0x45670000);e(4,'lui',rd=15,imm=0x40022000)
        e(8,'addi',rd=13,rs1=13,imm=291);e(12,'lui',rd=14,imm=0xcdef9000)
        store(16,13,15,4);e(18,'addi',rd=14,rs1=14,imm=-1621)
        store(22,14,15,4);store(24,13,15,36);store(26,14,15,36);e(28,'jr',rs1=1)
    elif role=='lock':
        e(0,'lui',rd=14,imm=0x40022000);load(4,15,14,16);e(6,'lui',rd=13,imm=0x8000)
        e(8,'or',rd=15,rs1=15,rs2=13);store(10,15,14,16);e(12,'jr',rs1=1)
    elif role=='erase':
        e(0,'lui',rd=15,imm=0x40022000);load(4,14,15,16);e(6,'lui',rd=13,imm=0x20000)
        e(10,'andi',rd=10,rs1=10,imm=-256);e(14,'or',rd=14,rs1=14,rs2=13)
        store(16,14,15,16);store(18,10,15,20);load(20,14,15,16)
        e(22,'ori',rd=14,rs1=14,imm=64);store(26,14,15,16);load(28,14,15,12)
        poll(30,14,1,'bnez');load(34,14,15,16);e(36,'lui',rd=13,imm=0xfffe0000)
        e(38,'addi',rd=13,rs1=13,imm=-1);e(40,'and',rd=14,rs1=14,rs2=13)
        store(42,14,15,16);e(44,'jr',rs1=1)
    elif role=='program':
        e(0,'lui',rd=14,imm=0x40022000);load(4,15,14,16);e(6,'lui',rd=13,imm=0x10000)
        e(8,'andi',rd=10,rs1=10,imm=-256);e(12,'or',rd=15,rs1=15,rs2=13);store(14,15,14,16)
        load(16,15,14,12);poll(18,15,1,'bnez');e(22,'lui',rd=14,imm=0x40022000)
        load(26,15,14,12);poll(28,15,2,'bnez');e(32,'lui',rd=14,imm=0x40022000)
        e(36,'addi',rd=12,rs1=0,imm=256);e(40,'add',rd=13,rs1=11,rs2=15)
        load(44,16,13);e(48,'add',rd=13,rs1=10,rs2=15);store(52,16,13)
        load(56,13,14,12);poll(58,13,2,'bnez');e(62,'addi',rd=15,rs1=15,imm=4)
        e(64,'bne',rs1=15,rs2=12,target=pc+40);load(68,15,14,16)
        e(70,'lui',rd=13,imm=0x200000);e(74,'or',rd=15,rs1=15,rs2=13);store(76,15,14,16)
        e(78,'lui',rd=15,imm=0x40022000);load(82,14,15,12);poll(84,14,1,'bnez')
        load(88,14,15,16);e(90,'lui',rd=13,imm=0xffff0000);e(92,'addi',rd=13,rs1=13,imm=-1)
        e(94,'and',rd=14,rs1=14,rs2=13);store(96,14,15,16);e(98,'jr',rs1=1)
    elif role=='timer':
        e(0,'lui',rd=15,imm=0xe000f000);load(4,14,15,4);e(6,'li',rd=13,imm=0)
        e(8,'andi',rd=14,rs1=14,imm=-2);store(10,14,15,4);load(12,14,3,382,1)
        e(16,'mul',rd=12,rs1=14,rs2=10);store(20,12,15,16);store(22,13,15,20)
        load(24,14,15);e(26,'ori',rd=14,rs1=14,imm=16);store(30,14,15)
        load(32,14,15);e(34,'ori',rd=14,rs1=14,imm=33);store(38,14,15)
        load(40,14,15,4);poll(42,14,1,'beqz');load(46,14,15)
        e(48,'andi',rd=14,rs1=14,imm=-2);store(50,14,15);e(52,'jr',rs1=1)
    elif role=='copy':
        e(0,'lui',rd=15,imm=0x40024000);load(4,14,15,524);store(8,0,15,524);e(12,'fence.i')
        e(16,'beqz',rs1=10,target=pc+24);e(18,'beqz',rs1=11,target=pc+24);e(20,'li',rd=15,imm=0)
        e(22,'bnez',rs1=12,target=pc+34);e(24,'lui',rd=15,imm=0x40024000);store(28,14,15,524)
        e(32,'jr',rs1=1);e(34,'add',rd=13,rs1=11,rs2=15);load(38,16,13,0,1)
        e(42,'add',rd=13,rs1=10,rs2=15);e(46,'addi',rd=15,rs1=15,imm=1);store(48,16,13,0,1)
        e(52,'bne',rs1=12,rs2=15,target=pc+34);e(56,'jump',target=pc+24)
    else:raise RuntimeError('unknown body role')
    return {pc+off:f for off,f in rows}


def body(raw,role,pc,count,digest):
    n=decode(raw,pc);expected=specs(role,pc)
    check(set(n)==set(expected),role+' complete instruction boundaries')
    for p,f in expected.items():init.g(n,p,role+' instruction '+hex(p-pc),**f)
    edges,cycles=init.timer.cfg(n,pc)
    normalized=sorted(sorted(int(p,16)-pc for p in c) for c in cycles)
    check(normalized==sorted(CYCLES.get(role,[])),role+' complete cyclic SCC census')
    stores=[p-pc for p,d in n.items() if d['op']=='store']
    check(stores==STORES[role],role+' complete store census')
    writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(writes==WRITES[role],role+' encoded GPR writes')
    check(len(n)==count and sha256(raw).hexdigest()==digest,role+' complete body identity')
    return {'role':role,'start':hex(pc),'end_exclusive':hex(pc+len(raw)),'bytes':len(raw),
        'sha256':digest,'instructions':list(n.values()),'conditional_normal_return_CFG':edges,
        'cyclic_SCCs':cycles,'store_PCs':[hex(pc+x) for x in stores],'encoded_GPR_writes':writes}


def bindings(app):
    rows=[]
    for pc,reg,spoff,value in ((0x19a4a,15,24,0x08077c00),(0x19a76,14,72,0x1979a),(0x19a80,14,76,0x197be)):
        raw=app[pc-0x8000:pc-0x8000+10];n=decode(raw,pc)
        check(len(n)==3,'APP binding complete window')
        init.g(n,pc,'APP binding high '+hex(pc),op='lui' if reg==15 else 'auipc',rd=reg,
               imm=0x08078000 if reg==15 else 0)
        initial=n[pc]['imm']+(pc if reg==14 else 0)
        init.g(n,pc+4,'APP binding low '+hex(pc),op='addi',rd=reg,rs1=reg,imm=value-initial)
        init.g(n,pc+8,'APP binding store '+hex(pc),op='store',rs1=2,rs2=reg,imm=spoff,width=4)
        rows.append({'start':hex(pc),'bytes':10,'sha256':sha256(raw).hexdigest(),
            'instructions':list(n.values()),'value':hex(value),'live_SP_offset':spoff,
            'config_field_if_C_equals_SP_plus_16':spoff-16})
    return rows


def derive(app,carriers,header):
    parent=io.derive(app,carriers,header)
    apps=[body(app[pc-0x8000:pc-0x8000+size],role,pc,count,digest)
          for role,pc,size,count,digest in APP_BODIES]
    copies=[]
    for data,prev,(label,*_) in zip(carriers,parent['profiles'],init.binding.PROFILES):
        mapping=init.binding.profile(data,label)
        row=next(r for r in mapping['slots'] if r['slot']=='0x4004c')
        check(row['raw_pointer']=='0x20000332' and row['target']=='0x20000332','copy slot value')
        source=int(row['source'],16);check(source==(0x405a2 if label=='V1.31' else 0x405e2),'copy flash source')
        c=body(init.binding.take(data,source,58),'copy',0x20000332,18,init.binding.COPY_HASH)
        c.update(label=label,slot='0x4004c',flash_source=hex(source),
                 first_copy=mapping['first_copy'],config_IO_target=prev['target'],
                 output_word_if_matching_context='4 forward byte transfers into caller SP+12..15',
                 actual_output_value_known=False,installed_binding_proved=False)
        copies.append(c)
    check(sum(x['bytes'] for x in apps+copies)==440,'full-body byte total')
    check(sum(len(x['instructions']) for x in apps+copies)==164,'full-body instruction total')
    check(sum(len(x['store_PCs']) for x in apps+copies)==29,'full-body store total')
    return {'schema':'TSL9-APP-NV-callbacks-static-v1','profile':init.timer.PROFILE,
        'scope':'7 complete APP bodies, 2 conditional mapped copy bodies and 3 APP binding windows; no target execution',
        'APP':{'bytes':len(app),'sha256':sha256(app).hexdigest()},'APP_bodies':apps,
        'APP_config_binding_windows':bindings(app),'candidate_copy_bodies':copies,
        'read_contract':{'entry':['source address','word count num','destination pointer'],
            'copy_arguments':['entry A2','entry A0','(entry A1 << 2) mod 2^32'],
            'slot_load_is_fresh':True,'forced_normal_reply':0,'provider_reply_checked':False,
            'initial_resident_count':1,'initial_conditional_output_bytes':4,
            'caller_output_initialized_by_wrapper_itself':False,
            'output_available_premises':['matching installed slot and copied callback fields',
                'nonnull valid source and destination; completed copy; supported encoding semantics',
                'required code/SP/frame/GP/register context valid; no interfering aliases or external changes'],
            'readback_value_or_comparison_branch_proved':False},
        'write_contract':{'entry':['destination address','ignored count','source pointer'],
            'ordered_calls':['unlock','erase','program','lock','timer(A0=1)'],
            'program_source':'fresh load of saved entry A2 from then-live SP+12',
            'program_destination':'then-live S0 masked with 0xffffff00',
            'source_read_bytes_on_completed_path':256,'source_read_width':4,'word_offsets':list(range(0,256,4)),
            'entry_count_used_by_wrapper_or_prefix_leaves':False,'forced_normal_reply':0,
            'hardware_status_success_test':False,'poll_timeout_or_universal_termination_proved':False,
            'source_snapshot_or_memmove_guarantee':False,
            'GP_byte_for_timer_count':382,'timer_input_A0':1,'physical_duration_known':False},
        'context':{'read_wrapper_frame_bytes':16,'write_wrapper_frame_bytes':32,
            'read_wrapper_RA_store_relative_to_caller_SP':-4,
            'resident_initial_output_relative_to_same_caller_SP':[12,15],
            'resident_saved_S2_relative_to_same_caller_SP':[16,19],
            'write_wrapper_own_saved_S0':24,'write_wrapper_own_saved_RA':28,
            'explicit_write_closure_GPR_nonwrites':[3,9,18],
            'reference_copy_explicit_GPR_nonwrites':[1,2,3,8,9,18],
            'nonwrites_do_not_prove_preservation_under_memory_alias_or_external_change':True,
            'normal_frame_restore_requires_intact_SP_saved_words_and_code':True},
        'unresolved':['actual installed provider/physical ISA profile',
            'initial NV source bytes and readback comparison branch',
            'allocation L0, fill L1, iteration Li freshness and valid 256-byte source extent',
            'MMIO completion/effects, aliases, external interference and unconditional preservation'],
        'coverage_change':'Static verification only; reconstructed C coverage unchanged',
        'installed_binding_proved':False,'target_ISA_provider_MMIO_execution':False}


def tests(app,carriers,header):
    # Host-width identities only: no target memory or execution state exists.
    for num in range(65536):check((num<<2)&MASK==num*4,'U16 read count scaling')
    for num in (0,1,0x3fffffff,0x40000000,0x80000001,MASK):
        check(((num<<2)&MASK)==(num%0x40000000)*4,'U32 count wrap identity')
    offsets=tuple(4*i for i in range(64))
    check(offsets==tuple(range(0,256,4)) and offsets[-1]+4==256,'fixed word transfer algebra')
    for base in (0,0x08077c00,0x20000000,0xffffff00):
        for low in range(256):check(((base+low)&0xffffff00)==base,'all low address bits discarded')
    for status in range(256):check(((status&2)==0)==(not bool(status&2)),'poll exit zero-offset seed')
    # Fixed read output interval, wrapper spill and adjacent resident S2 word.
    check(set(range(-4,0)).isdisjoint(range(12,16)) and
          set(range(16,20)).isdisjoint(range(12,16)),'relative nonwrapping stack separation')
    cases=(('read',12,4,'13962500','13961500'),('read',16,2,'aa85','b285'),
           ('write',20,2,'3246','2246'),('program',8,4,'137505f0','137505f8'),
           ('program',28,2,'898b','858b'),('program',36,4,'13060010','13060008'),
           ('program',44,4,'03a80600','03a84600'),('program',52,4,'23a00601','23a20601'),
           ('program',62,2,'9107','a107'),('timer',44,2,'75df','75ff'),
           ('copy',38,4,'03c80600','03a80600'),('copy',48,4,'23800601','2380e601'))
    details={role:(pc,size,count,digest) for role,pc,size,count,digest in APP_BODIES}
    for role,off,size,old,new in cases:
        if role=='copy':
            pc,length,count,digest=0x20000332,58,18,init.binding.COPY_HASH
            raw=bytearray(init.binding.take(carriers[0],0x405a2,58))
        else:
            pc,length,count,digest=details[role];raw=bytearray(app[pc-0x8000:pc-0x8000+length])
        check(len(bytes.fromhex(old))==size and raw[off:off+size]==bytes.fromhex(old),'mutation source pin '+role+hex(off))
        raw[off:off+size]=bytes.fromhex(new)
        try:body(raw,role,pc,count,digest)
        except RuntimeError as error:check(str(error)==role+' instruction '+hex(off),'unexpected mutation guard '+str(error))
        else:raise RuntimeError('specified mutation escaped')
    altered=bytearray(app);altered[0x19a7a-0x8000:0x19a7e-0x8000]=bytes.fromhex('130767d2')
    try:bindings(altered)
    except RuntimeError as error:check(str(error)=='APP binding low 0x19a76','binding mutation guard')
    else:raise RuntimeError('APP binding mutation escaped')
    print('PASS: 65536 U16 counts; 6 U32 wrap cases; 1024 alignment cases; 256 poll-bit cases; fixed 64-word algebra; 13 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app,header=init.binding.APP.read_bytes(),init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(app,carriers,header);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'APP callbacks ledger exact replay')
    print('PASS: 9 complete bodies, 440 bytes/164 instructions/29 store sites; 30 binding bytes/9 instructions')
    print('PASS: exact ledger replay; fixed 256-byte write versus scaled read; NO target ISA/provider/MMIO execution')


if __name__=='__main__':main()
