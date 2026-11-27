"""Join APP configuration producers to task5 allocation scalar domains.

Original complete-body contracts and host integer/interval facts only. No
target ISA, mutable frame/global/heap model, provider or hardware is run.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_task5_allocation_static as previous
import check_v4160_app_config_source_static as app_source
import check_v4160_role_initializer_fields_static as fields
import check_v4160_config_gates_static as gates
import check_v4160_mode3_frame_static as mode
import check_v4160_config_arithmetic_static as arithmetic

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
source=previous.source
OUT=Path(__file__).with_name('v4160-task5-config-provenance-static.json')


def receipt(body):
    return {k:body[k] for k in ('start','bytes','sha256')}


def compose(image,carriers):
    app=source.app_contract(image[source.APP_PC-0x8000:source.APP_PC-0x8000+source.APP_SIZE])
    con=app_source.body(image[0x19b56-0x8000:0x19bd4-0x8000],'construct')
    an={v['pc']:v for v in app['instructions']};cn={v['pc']:v for v in con['instructions']}
    for p,f in ((0x19a54,dict(op='lui',rd=15,imm=4096)),
                (0x19a56,dict(op='addi',rd=14,rs1=15,imm=-2045)),
                (0x19a5a,dict(op='store',rs1=2,rs2=14,imm=30,width=2)),
                (0x19a5e,dict(op='addi',rd=14,rs1=0,imm=251)),
                (0x19a62,dict(op='store',rs1=2,rs2=14,imm=32,width=2))):
        init.g(an,p,'task5 config APP producer',**f)
    packed=4096-2045;n=(packed>>8)&255;initial_half=251
    check(packed==0x0803 and n==8 and (packed&255)==3,'task5 config high byte, not low byte')
    check((30-16,32-16)==(14,16),'task5 config first source offset translation')
    # Explicit local interval facts; no target frame is populated or simulated.
    relevant={31,32,33}
    later_stores=[v for v in app['instructions'] if v['op']=='store' and v['pc']>0x19a62 and v['rs1']==2]
    check(all(set(range(v['imm'],v['imm']+v['width'])).isdisjoint(relevant) for v in later_stores),'task5 config later direct APP stores exclude n/h bytes')
    uid=source.uid_contract(image[source.UID_PC-0x8000:source.UID_PC-0x8000+source.UID_SIZE])
    check(set(range(8,14)).isdisjoint(relevant) and set(range(40,46)).isdisjoint(relevant),'task5 config UID source/destination exclude source n/h')
    init.g(cn,0x19b66,'task5 config constructor zero+12',op='store',rs1=2,rs2=0,imm=12,width=4)
    init.g(cn,0x19bca,'task5 config second provider argument',op='mv',rd=10,rs2=2)
    init.g(cn,0x19bc8,'task5 config second provider slot',op='load',rd=15,rs1=15,imm=116,width=4)
    direct_after=[v for v in con['instructions'] if v['op']=='store' and v['rs1']==2 and v['pc']>0x19b66]
    check(all(set(range(v['imm'],v['imm']+v['width'])).isdisjoint(range(12,16)) for v in direct_after),'task5 config constructor direct stores preserve flag source')
    reader=mode.service.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,mode.service.APP_HASHES[1])
    reader_defs=sorted({v['rd'] for v in reader['instructions'] if v.get('rd',0)})
    mb=mode.body(image[mode.PC-0x8000:mode.END-0x8000],reader_defs)
    profiles=[]
    for i,data in enumerate(carriers):
        B=0x200033b8+80*i;C=0x2000319c+80*i;F=C+80
        fd=init.DETAILS[i];cfgpc=fd[2]
        check(fd[5]==F,'task5 config first destination matches F')
        raw,fn,_,_=init.config_contract(data,cfgpc,F,fd[9],fd[10])
        check(sha256(raw).hexdigest()==fd[-1],'task5 config complete first config identity')
        for o,f in ((140,dict(op='load',rd=14,rs1=15,imm=15,width=1)),
                    (142,dict(op='bnez',rs1=14,target=cfgpc+148)),
                    (144,dict(op='li',rd=14,imm=5)),
                    (146,dict(op='store',rs1=15,rs2=14,imm=15,width=1)),
                    (132,dict(op='load',rd=14,rs1=15,imm=16,width=2)),
                    (134,dict(op='bnez',rs1=14,target=cfgpc+140)),
                    (136,dict(op='li',rd=14,imm=27))):
            init.g(fn,cfgpc+o,'task5 config defaults source',**f)
        check(n!=0 and initial_half!=0,'task5 config selected source bypasses zero defaults')
        ip=fields.previous.DETAILS[i]['initialize']
        ib=fields.body(init.binding.take(data,ip,426),'initializer',i)
        inn={v['pc']:v for v in ib['instructions']}
        for o,f in ((230,dict(op='load',rd=14,rs1=18,imm=16,width=2)),
                    (262,dict(op='addi',rd=13,rs1=0,imm=251)),
                    (270,dict(op='bgeu',rs1=13,rs2=14,target=ip+278)),
                    (274,dict(op='addi',rd=14,rs1=0,imm=251)),
                    (284,dict(op='store',rs1=15,rs2=14,imm=46,width=2))):
            init.g(inn,ip+o,'task5 config h clamp/store',**f)
        gd=gates.DETAILS[i];gp,size,base,copied=gd[:4]
        gb=gates.body(init.binding.take(data,gp,size),i)
        gn={v['pc']:v for v in gb['instructions']}
        _,a=gates.specs(gp,i)
        check(0x20003000+copied+12==C+164==F+84,'task5 config flag is second config byte12')
        check((0x20003000+copied,0x20003000+copied+16)==(F+72,F+88),'task5 config independent destination extent')
        check(set(range(F,F+64)).isdisjoint(range(F+72,F+88)),'task5 config two copies are disjoint')
        init.g(gn,a(74),'task5 config second copy count',op='li',rd=12,imm=16)
        init.g(gn,a(76),'task5 config second copy destination',op='addi',rd=10,rs1=10,imm=copied)
        init.g(gn,a(206),'task5 config null branch flag zero',op='store',rs1=15,rs2=0,imm=12,width=1)
        check(init.binding.word(data,0x40074)==gp,'task5 config second candidate slot')
        mapping=init.binding.profile(data,init.binding.PROFILES[i][0]);m=mapping['first_copy']
        cp=int(m['source'],16)+0x20000332-int(m['destination'],16)
        cb=arithmetic.payload.body(init.binding.take(data,cp,58),'copy',0x20000332,58,18,3,init.binding.COPY_HASH)
        check(cb['encoded_GPR_writes']==[13,14,15,16] and not cb['calls'],'task5 config reused copy code preservation')
        # Parent's consumers pin all three addresses independently.
        profiles.append({'label':init.binding.PROFILES[i][0],
          'first_config':{'start':cfgpc,'bytes':228,'sha256':sha256(raw).hexdigest(),'destination':F,'copy_bytes':64,
            'n_source_APP_store':0x19a5a,'n_source_SP_byte':31,'n_candidate':8,'n_default_zero_only':5,
            'h_source_APP_store':0x19a62,'h_source_SP_half':32,'h_input_candidate':251,'h_default_zero_only':27,
            'default_cut_PC_before_callback':cfgpc+182},
          'initializer':{**receipt(ib),'h_load_PC':ip+230,'h_store_PC':ip+284,'h_slot':B+46,'h_rule':'min(fresh U16[F+16],251)','candidate_h':251,'late_call_cut':ip+388},
          'second_config':{**receipt(gb),'slot':0x40074,'destination':0x20003000+copied,'copy_bytes':16,'flag_slot':C+164,
            'source_APP_constructor_SP_byte':12,'source_value_if_precallees_complete_and_frame_retained':0,
            'precopy_optional_hook':True,'null_config_branch_directly_stores_flag0':True},
          'copy_reuse':{'source':cp,**receipt(cb),'new_code_bytes_counted':0},
          'allocation_join':{'consumer_n_slot':F+15,'consumer_h_slot':B+46,'consumer_flag_slot':C+164,'if_retained_n8_h251':{'flag_zero_request':400,'flag_nonzero_request':2304},
            'if_retained_second_source_flag0_request':400,'independently_proved_simultaneous_runtime_tuple':False},
          'retention_boundaries':['first64 copy normal completion,source-frame validity/nonoverlap and actual binding',
            'first-config APP callback197f0 and later nested callees can intervene after defaults; no all-writer closure',
            'initializer post+388 calls/tail and later object creation before allocation; h source is fresh',
            'constructor normal pre-call returns preserve byte12 only under their explicit frame/MMIO premises',
            'second config optional hook precedes source validation/copy and may alter source frame',
            'both copies use forward byte semantics; require source validity/noninterference rather than snapshot assumption',
            'global n/flag/h and post-allocation fresh n may change before or during backing initializer'],
          'installed_binding_or_reachable_values_or_ownership_proved':False})
    return {'APP_builder':receipt(app),'APP_constructor':receipt(con),'APP_UID_leaf':receipt(uid),
      'mode3_precallees_reuse':{**receipt(mb),'new_code_bytes_counted':0,'normal_return_only_frame_preservation':True},
      'profiles':profiles}


def domains():
    digest=sha256();cases=0
    for input_half in range(65536):
        h=min(input_half,251);R=32*((h+33)//32)
        check(32<=R<=256,'task5 config clamped stride bound')
        for flag_zero in (True,False):
            n=8;D=n+1 if flag_zero else 2*n;K=D-n;full=16*D+R*K
            check(full==(144+R if flag_zero else 256+8*R),'task5 config fixed n formula')
            check((176<=full<=400 if flag_zero else 512<=full<=2304) and full==(full&65535),'task5 config no request truncation within source-derived domain')
            digest.update(input_half.to_bytes(2,'little')+bytes((flag_zero,))+full.to_bytes(2,'little'));cases+=1
    check(cases==131072,'task5 config scalar case census')
    for value in range(256):check((value if value else 5) in range(1,256),'task5 config zero-only n default range')
    h=251;R=32*((h+33)//32);check(R==256 and 16*9+R==400 and 16*16+R*8==2304,'task5 config concrete two request values')
    check(9-8==1 and 16-8==8 and 9*16+1*R==400 and 16*16+8*R==2304,'task5 config stable post-allocation n row/layout extents')
    check((0x0803>>8)==8 and (0x0803&255)==3 and 8!=3,'task5 config reject low-byte interpretation')
    return {'clamped_input_half_cases':65536,'flag_classes_per_input':2,'fixed_n_cases':cases,'fixed_n':8,'h_bound':[0,251],
      'stride_bound':[32,256],'request_bounds_by_flag':{'zero':[176,400],'nonzero':[512,2304]},
      'h251_requests_by_flag':{'zero':400,'nonzero':2304},'vectors_sha256':digest.hexdigest(),
      'zero_only_n_default_cases':256,'new_code_bytes_counted':0,'simultaneous_runtime_tuple_or_allocation_success_proved':False}


def derive(image,carriers,header,coverage,hexes):
    parent=previous.derive(image,carriers,header,coverage,hexes)
    joins=compose(image,carriers)
    for p,q in zip(joins['profiles'],parent['profiles']):
        check(p['allocation_join']['consumer_n_slot']==q['roles']['n_U8'] and p['allocation_join']['consumer_h_slot']==q['roles']['h_U16'] and p['allocation_join']['consumer_flag_slot']==q['roles']['flag_U8'],'task5 config producer/consumer exact address joins')
    return {'schema':'TSL9-task5-config-provenance-static-v1','APP_sha256':sha256(image).hexdigest(),**joins,'integer_domains':domains(),
      'new_code_bytes_counted':0,'C_reconstruction_coverage_changed':False,
      'remaining':['intervening writers/optional hook and simultaneous tuple retention','V34 downstream and post-release ownership','actual installed provider and physical progress'],
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(image,carriers):
    # Mutation fixtures remain immutable input copies, never target state.
    sites=[('APP',None,p) for p in (0x19a54,0x19a56,0x19a5a,0x19a5e,0x19a62,0x19b66,0x19bc8,0x19bca)]
    for i in range(2):
        cp=init.DETAILS[i][2];ip=fields.previous.DETAILS[i]['initialize'];gp=gates.DETAILS[i][0];_,a=gates.specs(gp,i)
        sites.extend(('candidate',i,p) for p in [cp+132,cp+134,cp+140,cp+142,cp+144,cp+146,ip+230,ip+262,ip+270,ip+274,ip+284,a(74),a(76),a(206)])
    for kind,i,p in sites:
        app=image;cs=list(carriers);raw=bytearray(image if i is None else carriers[i]);off=p-(0x8000 if i is None else 0x40000)
        half=int.from_bytes(raw[off:off+2],'little');z=2 if half&3!=3 else 4
        raw[off:off+z]=(int.from_bytes(raw[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
        if i is None:app=bytes(raw)
        else:cs[i]=bytes(raw)
        try:compose(app,cs)
        except RuntimeError:pass
        else:raise RuntimeError('task5 config source mutation escaped '+hex(p))
    check(len(sites)==36,'task5 config source mutation census')
    domains()
    print('PASS:36 APP/candidate producer-source mutations rejected;131072 clamped-size/flag cases;high-byte and address joins')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
    ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers=carriers,image=image)
    raw=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if args.write:
        with OUT.open('xb') as f:f.write(raw)
    else:check(OUT.read_bytes()==raw,'task5 config exact ledger replay')
    print('PASS:APP64/16-byte configuration provenance;conditional n8/h251/flag0 -> request400;exact ledger;0 new code bytes')
    print('PASS:NO target execution/emulation;simultaneous tuple,intervening writers,installed binding and lifetime UNPROVED')


if __name__=='__main__':main()
