"""Offline key removal, backing-pointer reset and record-ID clearing contracts.

Pinned operands/CFG, immutable match-position walks and scalar/interval facts.
No target ISA, mutable registry/heap/event machine, callback or MMIO executes.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_task5_object_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
OUT=Path(__file__).with_name('v4160-task5-removal-static.json')
PARTS=('remove','reset','id_clear')
STARTS=((0x57a4a,0x57a1e,0x43a14),(0x57b8a,0x57b5e,0x43aa0))
SOURCES=STARTS
SIZES=(122,44,120)
COUNTS=(43,15,43)
FIELDS={**previous.FIELDS,'sll':('rd','rs1','rs2')}
BRANCHES=previous.BRANCHES
UNSIGNED={'remove':((0x3c,2),(0x6c,2)),'reset':(),'id_clear':()}
HASHES=(('3e5e5eb6c57b81707f21ebe8ffa65aa5440ccc2a0cd219d2a14a8d9a70c0c9e5', '55b1119608e9e168e807d56a0970668abd9a3df513713a7081f15349a7b5a55a', '4e654ae99dc530a4c642b6c628411046e37841f187ea10a38da3b19b48393515'), ('905bb1f4fb09557fe2645546611536806e0cebbd09973a9e1ad7a5751c7b0bca', '73982c002b215290de526f5c05eac226b9f66db7c1ebbd2602c551ff2268b464', 'd02498f1c169316f0d8599f4e677f7ea1e8d9e5929c230f3b1ca397774b82108'))
LITERALS=(
{
'remove':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 lui 8 536883200
008 addi 15 8 952
00c load 13 15 156 4
010 store 2 1 12 4
012 li 14 0
014 mv 15 13
016 addi 8 8 952
01a beqz 15 108
01c load 12 15 8 2
01e bne 12 10 116
022 bnez 14 82
024 load 14 13 0 4
026 store 8 14 156 4
02a mv 10 15
02c auipc 1 536510464
030 jalr 1 1 1690
034 load 15 8 160 4
038 store 15 0 0 4
03c load 15 8 180 2
040 bnez 15 102
042 jal 1 358942
046 store 8 0 156 4
04a load 1 2 12 4
04c load 8 2 8 4
04e addi 2 2 16
050 jr 1
052 load 13 8 160 4
056 bne 13 15 96
05a store 8 14 160 4
05e jump 42
060 load 13 15 0 4
062 store 14 13 0 4
064 jump 42
066 addi 15 15 -1
068 store 8 15 180 2
06c load 15 8 180 2
070 bnez 15 74
072 jump 66
074 mv 14 15
076 load 15 15 0 4
078 jump 26
''',
'reset':'''
000 lui 15 536883200
004 addi 14 15 952
008 load 10 14 172 4
00c addi 2 2 -16
00e store 2 8 8 4
010 store 2 1 12 4
012 addi 8 15 952
016 beqz 10 32
018 auipc 1 536510464
01c jalr 1 1 1754
020 store 8 0 172 4
024 load 1 2 12 4
026 load 8 2 8 4
028 addi 2 2 16
02a jr 1
''',
'id_clear':'''
000 addi 2 2 -32
002 store 2 9 20 4
004 store 2 18 16 4
006 lui 9 1073889280
00a store 2 1 28 4
00c store 2 8 24 4
00e store 2 19 12 4
010 load 18 9 524 4
014 store 9 0 524 4
018 fence.i
01c addi 15 0 47
020 bltu 15 10 108
024 li 15 12
026 mul 8 10 15
02a lui 19 536883200
02e load 15 19 556 4
032 add 15 15 8
034 load 15 15 0 4
036 beqz 15 108
038 andi 15 10 15
03c li 11 1
03e sll 11 11 15
042 slli 11 11 16
044 srli 11 11 16
046 srli 10 10 4
048 jal 1 276904
04a load 15 19 556 4
04e li 10 0
050 add 15 15 8
052 store 15 0 0 4
056 store 15 0 4 4
05a store 9 18 524 4
05e load 1 2 28 4
060 load 8 2 24 4
062 load 9 2 20 4
064 load 18 2 16 4
066 load 19 2 12 4
068 addi 2 2 32
06a jr 1
06c lui 15 1073889280
070 store 15 18 524 4
074 li 10 2
076 jump 94
'''
},
{
'remove':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 lui 8 536883200
008 addi 15 8 1032
00c load 13 15 156 4
010 store 2 1 12 4
012 li 14 0
014 mv 15 13
016 addi 8 8 1032
01a beqz 15 108
01c load 12 15 8 2
01e bne 12 10 116
022 bnez 14 82
024 load 14 13 0 4
026 store 8 14 156 4
02a mv 10 15
02c auipc 1 536510464
030 jalr 1 1 1370
034 load 15 8 160 4
038 store 15 0 0 4
03c load 15 8 180 2
040 bnez 15 102
042 jal 1 359262
046 store 8 0 156 4
04a load 1 2 12 4
04c load 8 2 8 4
04e addi 2 2 16
050 jr 1
052 load 13 8 160 4
056 bne 13 15 96
05a store 8 14 160 4
05e jump 42
060 load 13 15 0 4
062 store 14 13 0 4
064 jump 42
066 addi 15 15 -1
068 store 8 15 180 2
06c load 15 8 180 2
070 bnez 15 74
072 jump 66
074 mv 14 15
076 load 15 15 0 4
078 jump 26
''',
'reset':'''
000 lui 15 536883200
004 addi 14 15 1032
008 load 10 14 172 4
00c addi 2 2 -16
00e store 2 8 8 4
010 store 2 1 12 4
012 addi 8 15 1032
016 beqz 10 32
018 auipc 1 536510464
01c jalr 1 1 1434
020 store 8 0 172 4
024 load 1 2 12 4
026 load 8 2 8 4
028 addi 2 2 16
02a jr 1
''',
'id_clear':'''
000 addi 2 2 -32
002 store 2 9 20 4
004 store 2 18 16 4
006 lui 9 1073889280
00a store 2 1 28 4
00c store 2 8 24 4
00e store 2 19 12 4
010 load 18 9 524 4
014 store 9 0 524 4
018 fence.i
01c addi 15 0 47
020 bltu 15 10 108
024 li 15 12
026 mul 8 10 15
02a lui 19 536883200
02e load 15 19 636 4
032 add 15 15 8
034 load 15 15 0 4
036 beqz 15 108
038 andi 15 10 15
03c li 11 1
03e sll 11 11 15
042 slli 11 11 16
044 srli 11 11 16
046 srli 10 10 4
048 jal 1 277044
04a load 15 19 636 4
04e li 10 0
050 add 15 15 8
052 store 15 0 0 4
056 store 15 0 4 4
05a store 9 18 524 4
05e load 1 2 28 4
060 load 8 2 24 4
062 load 9 2 20 4
064 load 18 2 16 4
066 load 19 2 12 4
068 addi 2 2 32
06a jr 1
06c lui 15 1073889280
070 store 15 18 524 4
074 li 10 2
076 jump 94
'''
}
)


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'task5 removal literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=pc
        out[pc+int(off,16)]=f
    return out


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    if part=='id_clear':check(raw[0x18:0x1c]==bytes.fromhex('0f100000'),'task5 removal fence bytes')
    for off,width in UNSIGNED[part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==0x5003,'task5 removal unsigned encoding')
    n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'task5 removal complete boundaries '+part)
    for p,f in s.items():init.g(n,p,'task5 removal operand '+part+' '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'task5 removal original identity '+part)
    e={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'task5 removal ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':check(v['rd']==1,'task5 removal linked call');calls.append({'offset':p-pc,'target':v['target']})
        elif op=='jalr':
            check(v['rd']==v['rs1']==1 and n[p-4]['op']=='auipc' and n[p-4]['rd']==1,'task5 removal call pair')
            calls.append({'offset':p-pc,'target':(p-4+n[p-4]['imm']+v['imm'])&0xfffffffe})
        check(all(q in n for q in qs),'task5 removal closed CFG');e[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(e[p])
    check(seen==set(n),'task5 removal all nodes reachable')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(calls),len(stores),len(rets))==((2,8,1),(1,3,1),(1,10,1))[k],'task5 removal census '+part)
    check(common.acyclic(e)==(part!='remove'),'task5 removal cycle classification')
    if part=='remove':
        cut={p:list(qs) for p,qs in e.items()};cut[pc+0x78].remove(pc+0x1a)
        check(common.acyclic(cut),'task5 removal only registry scan backedge')
        check([p-pc for p,v in n.items() if v.get('rd')==10]==[0x2a],'task5 removal only local A0 definition is selectedcur')
    return {'start':pc,'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'CFG':e,'calls':calls,'tails':[],
      'returns':rets,'stores':stores,'complete_local_body':True,'local_CFG_acyclic':common.acyclic(e),'actual_termination_or_release_success_proved':False}


def dag_paths(b):
    pc=b['start'];out=[]
    def visit(p,seq):
        check(p not in seq,'task5 removal DAG witness');seq=seq+[p]
        if not b['CFG'][p]:out.append([q-pc for q in seq]);return
        for q in b['CFG'][p]:visit(q,seq)
    visit(pc,[]);return out


def removal_paths(b):
    pc=b['start'];prefix=[p-pc for p in b['CFG'] if p<pc+0x1a];end=[0x4a,0x4c,0x4e,0x50];out={}
    for skipped in range(4):
        for matched in (False,True):
            for tail in (False,True):
                for before in (0,1,2):
                    for after in (0,1):
                        seq=prefix[:]
                        for _ in range(skipped):seq.extend((0x1a,0x1c,0x1e,0x74,0x76,0x78))
                        if matched:
                            seq.extend((0x1a,0x1c,0x1e,0x22))
                            if not skipped:seq.extend((0x24,0x26))
                            else:
                                seq.extend((0x52,0x56))
                                seq.extend((0x5a,0x5e) if tail else (0x60,0x62,0x64))
                            seq.extend((0x2a,0x2c,0x30,0x34,0x38,0x3c,0x40))
                            if before:
                                seq.extend((0x66,0x68,0x6c,0x70))
                                if not after:seq.extend((0x72,0x42,0x46))
                            else:seq.extend((0x42,0x46))
                        else:
                            seq.extend((0x1a,0x6c,0x70))
                            if not after:seq.extend((0x72,0x42,0x46))
                        seq.extend(end);common.previous.valid(b['CFG'],[pc+q for q in seq])
                        out[f'{skipped}:match{int(matched)}:tail{int(tail)}:before{before}:after{after}']=seq
    check(len(out)==96,'task5 removal immutable walk census')
    edges={(p-pc,q-pc) for p,qs in b['CFG'].items() for q in qs};covered={edge for seq in out.values() for edge in zip(seq,seq[1:])}
    check(edges==covered,'task5 removal every local edge witnessed')
    one=out['0:match1:tail1:before1:after0']
    check(0x26 in one and 0x5a not in one and one.index(0x30)<one.index(0x34)<one.index(0x38),'task5 removal head-only case tail unchanged until postfree store')
    return {'immutable_walk_count':len(out),'skipped_match_position_vectors':[0,1,2,3],'all_local_edges_witnessed':True,
      'walks_sha256':sha256(json.dumps(out,separators=(',',':')).encode()).hexdigest(),
      'examples':{k:out[k] for k in ('0:match0:tail0:before0:after0','0:match0:tail0:before2:after1','0:match1:tail1:before1:after0','1:match1:tail0:before2:after1','2:match1:tail1:before2:after1')},
      'single_object_boundary':'if capturedhead=cur,cur.next0,tailword retainscur,firstheadunlink storeshead0 butdoesnotchangetail;afterprivatefreecall fresh tail maystillcur,so SW0[cur0] follows cleanup attempt. Actualfree/safe lateraccess require separate ownership proof',
      'actual_path_feasibility_list_finiteness_or_ownership_proved':False}


def domains():
    groups=[]
    for identity in range(48):
        group,bit=identity>>4,identity&15;mask=(1<<bit)&65535
        check(group*16+bit==identity and 0<=group<=2 and mask and mask&(mask-1)==0,'task5 ID group/bit/mask identity')
        offset=12*identity;check(offset+8<=576 and set(range(offset,offset+8)).isdisjoint(range(offset+8,offset+12)),'task5 record footprint leaves metadata8')
        groups.append([identity,group,mask,offset])
    check(sum(v[1]==0 for v in groups)==sum(v[1]==1 for v in groups)==sum(v[1]==2 for v in groups)==16,'task5 record groups complete')
    for value in range(65536):
        if value:check(0<=value-1<=65534,'task5 registry nonzero count decrement')
    for byte in range(256):
        invoked=byte!=255;accepted=byte<=47
        check((invoked and accepted)==(0<=byte<=47),'task5 cleanup byte IDs admitted subset')
    check(65536>65535 and 0xffffffff>47,'task5 full unsigned ID/key boundaries')
    return {'record_ID_rows':groups,'record_ID_domain':[0,47],'caller_U8_domain_cases':256,'U16_count_domain_cases':65536,
      'no_match_nonzero_count_reply':'entry full requestedID unchanged: no call or local A0 definition on selected path',
      'count_matches_registry_length_proved':False,'count0_reset_even_without_match':True,
      'actual_ID_reachability_arena_ownership_or_pointer_alias_proved':False}


def profile(image,data,hexraw,index,parent):
    bs={part:body(init.binding.take(data,STARTS[index][k],SIZES[k]),part,index) for k,part in enumerate(PARTS)}
    remove,reset,id_clear=(bs[p] for p in PARTS);rp,zp,ip=STARTS[index];B=0x200033b8+80*index;C=0x2000319c+80*index
    rn={v['pc']-rp:v for v in remove['instructions']};zn={v['pc']-zp:v for v in reset['instructions']};inn={v['pc']-ip:v for v in id_clear['instructions']}
    check(remove['calls']==[{'offset':0x30,'target':0x20000110},{'offset':0x42,'target':zp}] and reset['calls']==[{'offset':0x1c,'target':0x20000110}],'task5 removal/reset private release joins')
    stop=common.dealloc.DETAILS[index][1]
    check(id_clear['calls']==[{'offset':0x48,'target':stop}],'task5 ID stop-task direct join')
    check(rn[4]['imm']+rn[8]['imm']==B and rn[0xc]['imm']==156 and rn[0x34]['imm']==160,'task5 registry head/tail addresses')
    check(zn[0]['imm']+zn[4]['imm']==B and zn[8]['imm']==zn[0x20]['imm']==172,'task5 reset backing pointer source/clear')
    check(inn[0x2a]['imm']+inn[0x2e]['imm']==C+144 and inn[0x2e]['imm']==inn[0x4a]['imm'],'task5 ID arena slot is separately fresh-reloaded')
    check(inn[0x38]['imm']==15 and inn[0x46]['imm']==4 and inn[0x26]['op']=='mul' and inn[0x24]['imm']==12,'task5 ID bit/group/stride operands')
    reset_paths=dag_paths(reset);id_paths=dag_paths(id_clear)
    check(len(reset_paths)==2 and len(id_paths)==3,'task5 reset/ID DAG path census')
    for seq in reset_paths:check(0x20 in seq,'task5 reset clears backing word after optional release')
    for seq in id_paths:
        defs=[o for o in seq if inn[o].get('rd')==10];last=inn[defs[-1]]
        check(last['op']=='li' and last['imm']==(0 if 0x48 in seq else 2),'task5 ID normal return code')
        check(int(0x5a in seq)+int(0x70 in seq)==1,'task5 ID control restore on normal paths')
        if 0x48 in seq:check(seq.index(0x4a)<seq.index(0x52)<seq.index(0x56),'task5 ID fresh arena read then clear0/4')
    cleanup=parent['bodies']['cleanup'];cn={v['pc']-cleanup['start']:v for v in cleanup['instructions']}
    check(next(c['target'] for c in cleanup['calls'] if c['offset']==0x6a)==rp,'task5 cleanup objectkey helper join')
    check([c['target'] for c in cleanup['calls'] if c['offset'] in (0x2e,0x3e,0x4e,0x5e)]==[ip]*4,'task5 cleanup four ID helper calls')
    check(cn[0x64]['imm']==41 and cn[0x64]['rs2']==15,'task5 cleanup only ID41 caller invalidation')
    check(not any(v['op']=='store' and v['imm'] in (38,39,40) for v in cleanup['instructions']),'task5 cleanup no ID38/39/40 local stores')
    life=common.previous;fr=life.release;fn,fe=life.free_body(init.binding.take(data,fr.DETAILS[index][0],212),index)
    check(not any(v.get('rd')==8 for v in fn.values()),'task5 private release keeps B register locally')
    _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
    for part,b in bs.items():
        check(sparse.captured(mem,b['start'],b['bytes'])==init.binding.take(data,b['start'],b['bytes']),'task5 removal original HEX backing')
        receipts.append({'part':part,'start':b['start'],'bytes':b['bytes'],'all_bytes_captured':True})
    return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,
      'CFG_certificates':{p:common.certificates(b) for p,b in bs.items()},'remove_paths':removal_paths(remove),'reset_paths':reset_paths,'id_clear_paths':id_paths,
      'roles':{'registry_head':B+156,'registry_tail':B+160,'backing_pointer':B+172,'registry_count_U16':B+180,'record_arena_pointer_slot':C+144},
      'remove_contract':['full requestedID compared to each freshU16[cur8],starting capturedhead B156 andfollowingcur0;firstmatch only;duplicatekey identity/listfiniteness not proved',
        'headmatch: B156=capturedhead.next,doesnotupdate B160;nonhead+freshB160==cur: B160=prev;else prev.next=cur.next',
        'then A0=cur ->private release; freshtail=U32[B160],SW0[tail0] withno nullguard;actualobjectfree/safe postcallaccess unproved',
        'sampled count!=0 ->decrementSH;freshcount0 ->reset(),thenSW0 B156;sampled count0 ->reset/clearhead immediately. No-match also resets iffreshcount0',
        'no fixed success return;no-match/nonzero-count returns entry requestedID;other paths forward then-live A0 from release/reset'],
      'reset_contract':['freshB172nonnull ->private release(pointer);both normal paths SW0 B172;no local B160 or B180 clear',
        'B172zero path returns0 frominitialload;nonnull forwards private A0. Pointer clear doesnotprove actualrelease/sharedowner safety'],
      'id_contract':['full unsigned ID>47 ->2 beforearena access;ID<=47 ->capture offset12*ID,read arena slot then record0;record0zero ->2',
        'active record ->stop(ID>>4,low16(1<<(ID&15))),ignore stopreply;fresharena reloaded,clearrecord0/4,return0;metadata+8 not locallycleared',
        'arena hasno localnullguard;freshpoststop arena maydiffer;correctsame-record clear needsstablepointer/offset andcontext. No record callback is invoked',
        'recordword clear isnot freeingarena,payload orcallbackargument;no atomic cancellation/delivery guarantee'],
      'cleanup_join':'cleanup U8 IDs39/38/40/41!=255 call IDhelper;values48..254 reject2,still normal return. Only byte41 caller writes255 aftercall,including reject2;others not locallyinvalidated. At57a4a boundary cleanup mayrelease some matching object,not proved originalO without keyidentity andallocation provenance;callerhasno later originalO dereference',
      'single_object_lifetime_boundary':'headcur,next0,retainedtailcur is consistent with headmatch branch;post-private-release freshtail store maywritecur0 after cleanup attempt. Do not treat successful release or valid ownership of that later store as established',
      'premises':'matching captured conditional ISA;valid frame/registryobjects>=12B/tailword/arena>=576B/control/privateheap/global storage;normal callees preserve S/B/SP/RA/savedframes;fresh-head/tail/pointer/count snapshots equated only with retention proof;no adverse alias/IRQ/DMA/reentry/unaccounted writers',
      'actual_provider_allocation_provenance_postrelease_access_and_lifetime_proved':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage,hexes):
    parent=previous.derive(image,carriers,header,coverage,hexes)
    profiles=[profile(image,d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==572,'task5 removal byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==202,'task5 removal instruction census')
    return {'schema':'TSL9-task5-removal-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'complete_body_bytes':572,'complete_body_instructions':202,'C_reconstruction_coverage_changed':False,
      'remaining':['object/backing allocation sources and post-release tail ownership','V34 target and original payload lifetimes','installed provider/task binding and physical progress'],
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
    mutations=unsigned=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,STARTS[i][k],SIZES[k]);n=decode(raw,STARTS[i][k])
            for p,v in n.items():
                off=p-STARTS[i][k];z=v['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(bad,part,i)
                except RuntimeError:pass
                else:raise RuntimeError('task5 removal mutation escaped')
                mutations+=1
            for off,width in UNSIGNED[part]:
                bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
                try:body(bad,part,i)
                except RuntimeError as ex:check('unsigned encoding' in str(ex),'task5 removal exact signedness guard')
                else:raise RuntimeError('task5 removal signedness escaped')
                unsigned+=1
    check((mutations,unsigned)==(202,4),'task5 removal mutation census');domains()
    print('PASS:202 instruction/4 signedness mutations rejected;192 removal walks +10 DAG paths;48 ID/group/mask +65536 count cases')


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
    ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    raw=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if args.write:
        with OUT.open('xb') as f:f.write(raw)
    else:check(OUT.read_bytes()==raw,'task5 removal exact ledger replay')
    print('PASS:572B/202i complete removal/reset/ID helpers;strict HEX backing;unlink/release/postcall-access contracts;exact ledger')
    print('PASS:NO target execution/emulation;actual release,post-release ownership and provider binding UNPROVED')


if __name__=='__main__':main()
