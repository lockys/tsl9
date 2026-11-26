"""Config length/count source and conditional NV buffer extent: static only.

Raw bytes, operands, CFGs and host integer relationships; no target ISA,
allocator, buffer, callback or MMIO execution/emulation is constructed.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_app_nv_callbacks_static as cb

init, ROOT, LIB, MASK = cb.init, cb.ROOT, cb.LIB, cb.MASK
check = init.check
OUT = Path(__file__).with_name('v4160-config-buffer-source-static.json')
APP_PC, APP_SIZE = 0x199e2,308
APP_SHA = 'c4adfa47a73e8a89af8c8625961cd798292c7c478503a250a005f885bc3e64a0'
UID_PC, UID_SIZE = 0x18f56,50
UID_SHA = '5ea71cc5060b528919272111556388a084fe65e49474efa62683825e4df2eedf'
FILL_PC = 0x2000039c
FILL_SHA = 'd67147a681aca68d4d082eebf74ab6214f61f43253be91e932eebd5c3e3d05a3'
DIRECT = ((0x19a42,15,16,4),(0x19a46,15,20,2),(0x19a52,15,24,4),
 (0x19a5a,14,30,2),(0x19a62,14,32,2),(0x19a6c,14,34,1),(0x19a70,15,36,2),
 (0x19a7e,14,72,4),(0x19a88,14,76,4),(0x19a90,15,52,4),(0x19a9a,14,46,2),
 (0x19a9e,15,60,4),(0x19aae,14,48,2),(0x19ab2,15,64,4))


def serialize(raw,pc,n):
    edges,cycles=init.timer.cfg(n,pc)
    return {'start':hex(pc),'end_exclusive':hex(pc+len(raw)),'bytes':len(raw),
        'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'conditional_normal_return_CFG':edges,'cyclic_SCCs':cycles,
        'store_PCs':[hex(p) for p,d in n.items() if d['op']=='store'],
        'encoded_GPR_writes':sorted({d['rd'] for d in n.values() if d.get('rd',0)})}


def app_contract(raw):
    n=cb.decode(raw,APP_PC)
    def g(pc,**f):init.g(n,pc,'APP source instruction '+hex(pc),**f)
    # Slot values and their semantic replies remain opaque. These checks pin
    # the operands which feed each call and every store in the complete body.
    g(0x199e8,op='addi',rd=2,rs1=2,imm=-96)
    for pc,reg,off in ((0x199ea,8,88),(0x199f8,1,92)):
        g(pc,op='store',rs1=2,rs2=reg,imm=off,width=4)
    g(0x199ec,op='store',rs1=3,rs2=15,imm=384,width=4)
    g(0x199f0,op='lui',rd=8,imm=LIB)
    g(0x199f4,op='load',rd=15,rs1=8,imm=60,width=4)
    g(0x199f6,op='load',rd=10,rs1=8,imm=52,width=4)
    g(0x199fa,op='li',rd=12,imm=21)
    g(0x199fc,op='auipc',rd=11,imm=0x1000)
    g(0x19a00,op='addi',rd=11,rs1=11,imm=288)
    g(0x19a04,op='call_indirect',rd=1,rs1=15)
    g(0x19a06,op='bnez',rs1=10,target=0x19a0a)
    for pc in (0x19a08,0x19ae0,0x19af0):g(pc,op='jump',target=pc)
    for pc in (0x19a18,0x19a26,0x19a32):g(pc,op='store',rs1=15,rs2=14,imm=44,width=4)
    g(0x19a20,op='addi',rd=12,rs1=0,imm=64);g(0x19a2e,op='li',rd=11,imm=0)
    g(0x19a34,op='load',rd=15,rs1=8,imm=72,width=4)
    g(0x19a36,op='addi',rd=10,rs1=2,imm=16);g(0x19a38,op='call_indirect',rd=1,rs1=15)
    g(0x19a3a,op='auipc',rd=15,imm=0x1ffea000)
    g(0x19a3e,op='addi',rd=15,rs1=15,imm=1874)
    check((0x19a3a+0x1ffea000+1874)&MASK==0x2000418c,'APP heap address algebra')
    g(0x19a44,op='lui',rd=15,imm=0x7000)
    # The callback/base windows are checked again as part of the full builder.
    for pc,reg,high,low in ((0x19a4a,15,0x08078000,-1024),):
        g(pc,op='lui',rd=reg,imm=high);g(pc+4,op='addi',rd=reg,rs1=reg,imm=low)
    g(0x19a54,op='lui',rd=15,imm=4096)
    g(0x19a56,op='addi',rd=14,rs1=15,imm=-2045)
    g(0x19a5e,op='addi',rd=14,rs1=0,imm=251)
    g(0x19a66,op='addi',rd=15,rs1=15,imm=-449)
    g(0x19a6a,op='li',rd=14,imm=3)
    g(0x19a74,op='load',rd=15,rs1=8,imm=124,width=4)
    for pc,low in ((0x19a76,-732),(0x19a80,-706)):
        g(pc,op='auipc',rd=14,imm=0);g(pc+4,op='addi',rd=14,rs1=14,imm=low)
    for pc,low in ((0x19a92,-674),(0x19aa4,-748)):
        g(pc,op='auipc',rd=15,imm=0);g(pc+4,op='addi',rd=15,rs1=15,imm=low)
    for pc,reg,off,width in DIRECT:g(pc,op='store',rs1=2,rs2=reg,imm=off,width=width)
    g(0x19aac,op='addi',rd=10,rs1=2,imm=8);g(0x19ab4,op='jal',rd=1,target=UID_PC)
    g(0x19ab8,op='addi',rd=14,rs1=2,imm=16);g(0x19aba,op='li',rd=15,imm=0);g(0x19abc,op='li',rd=13,imm=6)
    g(0x19abe,op='addi',rd=12,rs1=2,imm=8);g(0x19ac0,op='add',rd=12,rs1=12,rs2=15)
    g(0x19ac2,op='load',rd=12,rs1=12,imm=0,width=1);g(0x19ac6,op='addi',rd=15,rs1=15,imm=1)
    g(0x19ac8,op='addi',rd=14,rs1=14,imm=1);g(0x19aca,op='store',rs1=14,rs2=12,imm=23,width=1)
    g(0x19ace,op='bne',rs1=15,rs2=13,target=0x19abe)
    g(0x19ad2,op='load',rd=15,rs1=2,imm=16,width=4);g(0x19ad4,op='beqz',rs1=15,target=0x19ae0)
    g(0x19ad6,op='load',rd=14,rs1=2,imm=20,width=2);g(0x19ada,op='lui',rd=15,imm=4096)
    g(0x19adc,op='bgeu',rs1=14,rs2=15,target=0x19ae2)
    g(0x19ae2,op='lui',rd=15,imm=LIB);g(0x19ae6,op='load',rd=15,rs1=15,imm=164,width=4)
    g(0x19aea,op='addi',rd=10,rs1=2,imm=16);g(0x19aec,op='call_indirect',rd=1,rs1=15)
    g(0x19aee,op='beqz',rs1=10,target=0x19af2)
    g(0x19af2,op='li',rd=11,imm=1);g(0x19af4,op='addi',rd=10,rs1=0,imm=64)
    g(0x19af8,op='jal',rd=1,target=0x19106)
    for pc,reg,off in ((0x19b04,1,92),(0x19b06,8,88)):g(pc,op='load',rd=reg,rs1=2,imm=off,width=4)
    for pc,off in ((0x19b08,260),(0x19b0e,264)):g(pc,op='store',rs1=15,rs2=14,imm=off,width=4)
    g(0x19b12,op='addi',rd=2,rs1=2,imm=96);g(0x19b14,op='jr',rs1=1)
    stores={pc for pc,d in n.items() if d['op']=='store'}
    check(stores=={pc for pc,*_ in DIRECT}|{0x199ea,0x199ec,0x199f8,0x19a18,0x19a26,0x19a32,0x19aca,0x19b08,0x19b0e},'APP complete store census')
    own_stack={(d['imm'],d['width']) for pc,d in n.items() if pc>=0x19a3a and d['op']=='store' and d['rs1']==2}
    touched={x for off,width in own_stack for x in range(off,off+width)}|set(range(8,14))|set(range(40,46))
    check(touched.isdisjoint({28,29,68,69,70,71}),'APP local extents do not overwrite length or fallback')
    record=serialize(raw,APP_PC,n)
    check(record['cyclic_SCCs']==[[hex(pc)] for pc in (0x19a08,0x19ae0,0x19af0)]+[[hex(pc) for pc in (0x19abe,0x19ac0,0x19ac2,0x19ac6,0x19ac8,0x19aca,0x19ace)]],'APP SCC census')
    check(record['encoded_GPR_writes']==[1,2,8,10,11,12,13,14,15],'APP GPR writes')
    check(len(n)==106 and len(raw)==APP_SIZE and sha256(raw).hexdigest()==APP_SHA,'APP source complete identity')
    record.update(config_SP_offset=16,clear_call='0x19a38',clear_slot='0x40048',
        clear_request={'A0':'live SP+16','A1':0,'A2':64},config_call='0x19aec',config_slot='0x400a4',
        direct_config_stores=[{'pc':hex(pc),'SP_offset':off,'width':width,'config_offset':off-16} for pc,_,off,width in DIRECT],
        local_length_written_after_clear=False,call_normal_return_edges_assumed=True,
        UID_loop_source_SP_offsets=list(range(8,14)),UID_loop_destination_SP_offsets=list(range(40,46)),
        normal_APP_A0_reply='normal reply from final opaque callee19106, with required context intact; no later A0 definition',
        opaque_calls=['0x19a04 via fresh slot4003c','0x19a38 via then-live S0+72','0x19aec via fresh slot400a4','0x19af8 to19106'])
    return record


def uid_contract(raw):
    n=cb.decode(raw,UID_PC)
    expected={0:dict(op='lui',rd=14,imm=0x1ffff000),4:dict(op='load',rd=15,rs1=14,imm=2024,width=4),
      8:dict(op='srli',rd=13,rs1=15,imm=8),20:dict(op='srli',rd=13,rs1=15,imm=16),
      24:dict(op='srli',rd=15,rs1=15,imm=24),34:dict(op='load',rd=15,rs1=14,imm=2028,width=4),
      42:dict(op='srli',rd=15,rs1=15,imm=8),48:dict(op='jr',rs1=1)}
    for off,src,index in ((12,15,0),(16,13,1),(26,13,2),(30,15,3),(38,15,4),(44,15,5)):
        expected[off]=dict(op='store',rs1=10,rs2=src,imm=index,width=1)
    check(set(n)=={UID_PC+off for off in expected},'UID full instruction boundaries')
    for off,f in expected.items():init.g(n,UID_PC+off,'UID instruction '+hex(off),**f)
    r=serialize(raw,UID_PC,n)
    check(not r['cyclic_SCCs'] and r['encoded_GPR_writes']==[13,14,15],'UID no calls/frame and GPR writes')
    check(len(raw)==UID_SIZE and sha256(raw).hexdigest()==UID_SHA,'UID full identity')
    r.update(read_addresses=['0x1ffff7e8','0x1ffff7ec'],word_reads=2,output_extent_bytes=6,
             output_byte_order=['word0 bits0..7','word0 bits8..15','word0 bits16..23','word0 bits24..31','word1 bits0..7','word1 bits8..15'],
             source_words_physical_values_known=False)
    return r


def fill_contract(raw):
    pc=FILL_PC;n=cb.decode(raw,pc)
    expected={0:dict(op='lui',rd=14,imm=0x40024000),4:dict(op='load',rd=15,rs1=14,imm=524,width=4),
      8:dict(op='store',rs1=14,rs2=0,imm=524,width=4),12:dict(op='fence.i'),
      16:dict(op='beqz',rs1=10,target=pc+24),18:dict(op='add',rd=14,rs1=10,rs2=12),
      22:dict(op='bnez',rs1=12,target=pc+34),24:dict(op='lui',rd=14,imm=0x40024000),
      28:dict(op='store',rs1=14,rs2=15,imm=524,width=4),32:dict(op='jr',rs1=1),
      34:dict(op='addi',rd=10,rs1=10,imm=1),36:dict(op='store',rs1=10,rs2=11,imm=-1,width=1),
      40:dict(op='bne',rs1=10,rs2=14,target=pc+34),44:dict(op='jump',target=pc+24)}
    check(set(n)=={pc+off for off in expected},'fill full instruction boundaries')
    for off,f in expected.items():init.g(n,pc+off,'fill instruction '+hex(off),**f)
    r=serialize(raw,pc,n)
    check(r['cyclic_SCCs']==[[hex(pc+o) for o in (34,36,40)]] and r['encoded_GPR_writes']==[10,14,15],'fill cycle and GPR writes')
    check(len(raw)==46 and sha256(raw).hexdigest()==FILL_SHA,'fill complete identity')
    r.update(positive_nonnull_normal_output='low8(entry A1) at entry A0 + offsets0..entry A2-1, modulo32',
        normal_A0_reply='(entry A0 + entry A2) mod32 if both nonzero; entry A0 otherwise',
        encoded_S0_S1_S2_SP_RA_nonwrites=True,unconditional_context_or_memory_validity_proved=False)
    return r


def defaults_contract(raw,pc):
    n=cb.decode(raw,pc)
    rows=((114,'load',dict(rd=14,rs1=15,imm=12,width=2,mnemonic='qk.c.lhu')),
      (116,'bnez',dict(rs1=14,target=pc+124)),(118,'addi',dict(rd=14,rs1=0,imm=256)),
      (122,'store',dict(rs1=15,rs2=14,imm=12,width=2,mnemonic='qk.c.sh')),
      (124,'load',dict(rd=14,rs1=15,imm=14,width=1,mnemonic='qk.c.lbu')),
      (126,'bnez',dict(rs1=14,target=pc+132)),(128,'li',dict(rd=14,imm=1)),
      (130,'store',dict(rs1=15,rs2=14,imm=14,width=1,mnemonic='qk.c.sb')))
    for off,op,f in rows:init.g(n,pc+off,'defaults instruction '+hex(off),op=op,**f)
    return {'start':hex(pc+114),'end_exclusive':hex(pc+132),
        'instructions':[n[pc+off] for off,_,_ in rows],
        'length_rule':'U16[C+12] = old value if nonzero else 256',
        'count_rule':'U8[C+14] = old value if nonzero else 1',
        'fresh_reads_not_an_atomic_snapshot':True}


def derive(app,carriers,header):
    previous=cb.derive(app,carriers,header)
    a=app_contract(app[APP_PC-0x8000:APP_PC-0x8000+APP_SIZE]);u=uid_contract(app[UID_PC-0x8000:UID_PC-0x8000+UID_SIZE])
    profiles=[]
    for data,detail,p in zip(carriers,init.DETAILS,previous['candidate_copy_bodies']):
        mapping=init.binding.profile(data,p['label']);row=next(x for x in mapping['slots'] if x['slot']=='0x40048')
        check(row['target']==hex(FILL_PC),'fill slot target')
        source=int(row['source'],16);check(source==(0x4060c if p['label']=='V1.31' else 0x4064c),'fill source mapping')
        fill=fill_contract(init.binding.take(data,source,46));fill.update(flash_source=hex(source),slot='0x40048')
        pc=detail[2];raw=init.binding.take(data,pc,228);defaults=defaults_contract(raw,pc)
        check(sha256(raw).hexdigest()==detail[-1],'complete config body inherited identity')
        profiles.append({'label':p['label'],'fill':fill,'config_defaults':defaults,'config_target':hex(pc),
            'copied_config_base':hex(detail[5]),'copy_contract_sha256':p['sha256'],
            'post_defaults_calls':['APP field+44 callback, nominal target197f0','post-config local callee including config-I/O'],
            'actual_installed_binding_proved':False})
    bodies=[a,u]+[p['fill'] for p in profiles]
    check(sum(b['bytes'] for b in bodies)==450 and sum(len(b['instructions']) for b in bodies)==148,
          'complete source body byte/instruction totals')
    check(sum(len(b['store_PCs']) for b in bodies)==35,'complete source store total')
    return {'schema':'TSL9-config-buffer-source-static-v1','profile':init.timer.PROFILE,
        'scope':'APP builder and six-byte leaf complete bodies; two mapped fill bodies; guarded resident default slices; host extent algebra only',
        'APP_builder':a,'six_byte_source_leaf':u,'profiles':profiles,
        'conditional_source_fields':{'config_at':'live SP+16','heap_base':'0x2000418c','heap_length':28672,
            'NV_base':'0x08077c00','raw_length_field':0,'record_count':3,'neighbor_byte15':8,
            'read_callback':'0x1979a','write_callback':'0x197be','fallback_word52':0,
            'length_after_resident_default':256,'count_after_resident_default':3},
        'source_field_premises':['APP clear slot target matches candidate fill and completes valid 64-byte zero fill',
            'required SP/S0/code/frame stable at each projected access; no interfering aliases/writers',
            'six-byte leaf completes into SP+8..13 and six-byte loop destinations SP+40..45 are valid',
            'config validation and candidate 64-byte forward copy complete with matching source/destination context'],
        'stable_scenario_premises':['all source-field premises','resident defaults complete normally',
            'APP field+44 callback197f0 and every other call/writer preserve required fields, cache and frames',
            'L0=L1=each Li=256; bound byte remains3; fill preserves zero S2; per-record callbacks preserve counter',
            'core succeeds on valid nonwrapping block with B>=256; P and each reloaded Pcurrent agree',
            '256-byte fill and each pre-call word store valid; no alias with code/frame/config/MMIO/other live data',
            'program source reads valid; poll loops and callbacks return normally'],
        'stable_scenario_only':{'allocation_request':256,'allocation_tag':78,'rounded_request':256,'core_list':'large',
            'fit_header_minimum_B':256,'split_if_B_greater_than':264,
            'fill_byte':255,'fill_count':256,'record_indices':[0,1,2],
            'entry_num_ignored_by_APP_write_callback':64,
            'record_destinations':['0x08077c00','0x08077d00','0x08077e00'],
            'source_extent':'Pcurrent..Pcurrent+255, valid only under stated premises',
            'source_shape':'bytes0..3 little-endian current record address; bytes4..255 remain ff only under fill/preservation premises',
            'free_argument':'last reloaded Pcurrent, equal to original P only under the equality premise'},
        'proved_actual_L0_L1_Li_equality':False,'proved_real_heap_extent_or_ownership':False,
        'proved_actual_NV_contents_or_program_success':False,'installed_binding_proved':False,
        'unresolved':['complete effects of APP config+44 callback197f0 and other writers',
            'actual provider/ISA installation, initial NV contents, interrupts and pointer lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app,carriers):
    # No memory image or target register state: these are width/interval facts.
    for length in range(65536):
        effective=length if length else 256
        check(1<=effective<=65535 and (effective==256)==(length in (0,256)),'full U16 default algebra')
    for count in range(256):check((count if count else 1)==(1 if count<=1 else count),'full byte default algebra')
    for gap in range(65536):
        check((gap>8)==(256+gap>264),'nominal split threshold identity')
    for base in (0,0x2000418c,0xffffff00):
        for i in range(256):
            check((((base+i+1)&MASK)-1)&MASK==(base+i)&MASK,'fill increment-before-store identity')
    check(4096-2045==0x803 and (0x803&255)==3 and (0x803>>8)==8,'halfword count/neighbor split')
    check(((256+3)&65535)&0xfffc==256 and 256>52 and 256>>2==64,'nominal core/word-count algebra')
    check(tuple(0x08077c00+256*i for i in range(3))==(0x08077c00,0x08077d00,0x08077e00),'three aligned record addresses')
    cases=(('app',0x19a20,'13060004','13060002'),('app',0x19a36,'0808','0008'),
      ('app',0x19a56,'13873780','13871780'),('app',0x19a5a,'231fe100','231ee100'),
      ('app',0x19abc,'9946','9546'),('app',0x19aca,'a30bc700','a30ac700'),
      ('app',0x19ae6,'83a7470a','83a7070a'),('uid',UID_PC+44,'a302f500','2303f500'),
      ('fill',FILL_PC+36,'a30fb5fe','a30fb5fc'))
    for role,pc,old,new in cases:
        entry,size,fn=(APP_PC,APP_SIZE,app_contract) if role=='app' else ((UID_PC,UID_SIZE,uid_contract) if role=='uid' else (FILL_PC,46,fill_contract))
        raw=bytearray(init.binding.FILL if role=='fill' else app[entry-0x8000:entry-0x8000+size]);off=pc-entry
        check(raw[off:off+len(bytes.fromhex(old))]==bytes.fromhex(old),'source mutation pin '+role+hex(pc))
        raw[off:off+len(bytes.fromhex(new))]=bytes.fromhex(new)
        wanted=('APP source instruction '+hex(pc)) if role=='app' else role.upper()+' instruction '+hex(off) if role=='uid' else 'fill instruction '+hex(off)
        try:fn(raw)
        except RuntimeError as error:check(str(error)==wanted,'unexpected source mutation guard '+str(error))
        else:raise RuntimeError('source mutation escaped')
    pc=init.DETAILS[0][2];raw=bytearray(init.binding.take(carriers[0],pc,228))
    check(raw[118:122].hex()=='13070010','default mutation pin');raw[118:122]=bytes.fromhex('13070008')
    try:defaults_contract(raw,pc)
    except RuntimeError as error:check(str(error)=='defaults instruction 0x76','unexpected default mutation guard')
    else:raise RuntimeError('default mutation escaped')
    print('PASS: 65536 length defaults; 256 count defaults; 65536 split-gap identities; 768 fill-address identities; 10 specified raw mutations')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true',help='Create ledger exclusively');options=parser.parse_args()
    app,header=init.binding.APP.read_bytes(),init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(app,carriers);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if options.write:
        with OUT.open('xb') as stream:stream.write(output)
    else:check(OUT.read_bytes()==output,'config source exact ledger replay')
    print('PASS: 4 complete bodies, 450 bytes/148 instructions/35 store sites; 2 guarded resident default slices')
    print('PASS: exact ledger replay; conditional length256/count3/extent256; actual field stability UNPROVED; NO target execution')


if __name__=='__main__':main()
