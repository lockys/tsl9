"""Offline registry-object/backing allocation provenance; no target execution.

Pinned complete operands, closed CFGs and host scalar algebra only. Candidate
resident profiles are conditional references, not installed-provider evidence.
"""
import argparse,json
from collections import Counter
from hashlib import sha256
from pathlib import Path
import check_v4160_task5_removal_static as previous
import check_v4160_config_buffer_source_static as source

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
OUT=Path(__file__).with_name('v4160-task5-allocation-static.json')
PARTS=('descriptor_lookup', 'backing_init', 'create')
STARTS=((358498, 358564, 358754), (358818, 358884, 359074))
SIZES=(66,190,188)
COUNTS=(22,66,64)
HASHES=(('a212b537bb8e186f316cefa82614202a7623fd3381b6e7de4d71c477a31107cf', 'efbe793cd206cb3aea3e0c358d8a3ba623928d07c780125da469579ac278a46f', '14d55c249afdcfe89ccf1c5ab596c56c0ebbb13bc681207c1de861c2d3878e6b'), ('c7615664826416142e957130b570e0ee4e3cd8837a09a56eafe553e2b3e7bba9', '11a680fdd708df14b81e8a927830f4817e6e964a139f8031eff3a46e1a51bf7d', '105fcebc32c94cd5c73e8a79c4794ac5a9e610d2d528bc2f0a82271f333004e5'))
FIELDS={**previous.FIELDS,'srai':('rd','rs1','imm')}
BRANCHES=previous.BRANCHES
UNSIGNED={'descriptor_lookup':((4,1),(12,1)),'backing_init':((0x2a,1),(0x40,2),(0x70,1)),'create':((0x96,2),)}
LITERALS=(
{
'descriptor_lookup':'''
000 lui 14 536883200
004 load 13 14 507 1
008 lui 14 536883200
00c load 12 14 576 1
010 lui 15 536883200
014 load 15 15 1124 4
018 addi 14 13 1
01c beqz 12 34
01e slli 14 13 1
022 slli 14 14 4
024 lui 13 65536
026 add 14 14 15
028 addi 13 13 -1
02a bne 14 15 52
02e li 15 0
030 mv 10 15
032 jr 1
034 load 12 15 10 2
036 beq 12 10 48
03a beq 12 13 48
03e addi 15 15 16
040 jump 42
''',
'backing_init':'''
000 addi 2 2 -32
002 store 2 19 12 4
004 lui 19 536883200
008 addi 15 19 952
00c load 15 15 172 4
010 store 2 1 28 4
012 store 2 8 24 4
014 store 2 9 20 4
016 store 2 18 16 4
018 store 2 20 8 4
01a bnez 15 142
01c lui 14 536883200
020 addi 15 14 492
024 lui 13 536883200
028 load 15 15 15 1
02a load 13 13 576 1
02e addi 19 19 952
032 addi 20 14 492
036 addi 18 15 1
03a beqz 13 64
03c slli 18 15 1
040 load 8 19 46 2
044 sub 10 18 15
048 slli 9 18 4
04c addi 8 8 33
050 srai 8 8 5
052 slli 8 8 5
054 slli 8 8 16
056 srli 8 8 16
058 mul 10 8 10
05c addi 11 0 580
060 add 10 10 9
062 slli 10 10 16
064 srli 10 10 16
066 auipc 1 536510464
06a jalr 1 1 1846
06e beqz 10 142
070 load 13 20 15 1
074 store 19 10 172 4
078 add 14 10 9
07c sub 13 18 13
080 li 15 0
082 addi 12 0 -172
086 addi 11 0 -174
08a bltu 15 18 158
08e load 1 2 28 4
090 load 8 2 24 4
092 load 9 2 20 4
094 load 18 2 16 4
096 load 19 2 12 4
098 load 20 2 8 4
09a addi 2 2 32
09c jr 1
09e bgeu 15 13 182
0a2 store 10 14 4 4
0a4 store 10 11 10 2
0a6 add 14 14 8
0a8 addi 15 15 1
0aa slli 15 15 16
0ac store 10 0 9 1
0b0 srli 15 15 16
0b2 addi 10 10 16
0b4 jump 138
0b6 store 10 12 10 2
0b8 store 10 0 4 4
0bc jump 168
''',
'create':'''
000 addi 2 2 -16
002 addi 11 0 611
006 addi 10 0 488
00a store 2 1 12 4
00c store 2 8 8 4
00e store 2 9 4 4
010 auipc 1 536510464
014 jalr 1 1 1742
018 addi 12 0 488
01c li 11 0
01e mv 8 10
020 auipc 1 536514560
024 jalr 1 1 -1510
028 li 10 0
02a beqz 8 92
02c lui 9 536883200
030 addi 15 9 952
034 load 13 15 156 4
038 addi 9 9 952
03c beqz 13 106
03e mv 14 13
040 li 15 1
042 load 12 14 8 2
044 beq 12 15 166
048 load 14 14 0 4
04a bnez 14 66
04c store 8 15 8 2
04e bnez 15 144
050 mv 10 8
052 auipc 1 536510464
056 jalr 1 1 1884
05a load 10 8 8 2
05c load 1 2 12 4
05e load 8 2 8 4
060 load 9 2 4 4
062 addi 2 2 16
064 jr 1
066 mv 14 13
068 jump 66
06a li 15 1
06c store 8 15 8 2
06e store 9 8 156 4
072 store 9 8 160 4
076 store 9 15 180 2
07a jal 1 358564
07e load 15 9 160 4
082 store 15 0 0 4
086 store 8 0 10 1
08a store 8 0 14 1
08e jump 90
090 load 15 9 160 4
094 store 15 8 0 4
096 load 15 9 180 2
09a store 9 8 160 4
09e addi 15 15 1
0a0 store 9 15 180 2
0a4 jump 126
0a6 addi 14 15 1
0aa slli 15 14 16
0ae slli 12 14 16
0b2 srli 15 15 16
0b4 bge 12 0 102
0b8 li 15 0
0ba jump 76
'''
},
{
'descriptor_lookup':'''
000 lui 14 536883200
004 load 13 14 587 1
008 lui 14 536883200
00c load 12 14 656 1
010 lui 15 536883200
014 load 15 15 1204 4
018 addi 14 13 1
01c beqz 12 34
01e slli 14 13 1
022 slli 14 14 4
024 lui 13 65536
026 add 14 14 15
028 addi 13 13 -1
02a bne 14 15 52
02e li 15 0
030 mv 10 15
032 jr 1
034 load 12 15 10 2
036 beq 12 10 48
03a beq 12 13 48
03e addi 15 15 16
040 jump 42
''',
'backing_init':'''
000 addi 2 2 -32
002 store 2 19 12 4
004 lui 19 536883200
008 addi 15 19 1032
00c load 15 15 172 4
010 store 2 1 28 4
012 store 2 8 24 4
014 store 2 9 20 4
016 store 2 18 16 4
018 store 2 20 8 4
01a bnez 15 142
01c lui 14 536883200
020 addi 15 14 572
024 lui 13 536883200
028 load 15 15 15 1
02a load 13 13 656 1
02e addi 19 19 1032
032 addi 20 14 572
036 addi 18 15 1
03a beqz 13 64
03c slli 18 15 1
040 load 8 19 46 2
044 sub 10 18 15
048 slli 9 18 4
04c addi 8 8 33
050 srai 8 8 5
052 slli 8 8 5
054 slli 8 8 16
056 srli 8 8 16
058 mul 10 8 10
05c addi 11 0 580
060 add 10 10 9
062 slli 10 10 16
064 srli 10 10 16
066 auipc 1 536510464
06a jalr 1 1 1526
06e beqz 10 142
070 load 13 20 15 1
074 store 19 10 172 4
078 add 14 10 9
07c sub 13 18 13
080 li 15 0
082 addi 12 0 -172
086 addi 11 0 -174
08a bltu 15 18 158
08e load 1 2 28 4
090 load 8 2 24 4
092 load 9 2 20 4
094 load 18 2 16 4
096 load 19 2 12 4
098 load 20 2 8 4
09a addi 2 2 32
09c jr 1
09e bgeu 15 13 182
0a2 store 10 14 4 4
0a4 store 10 11 10 2
0a6 add 14 14 8
0a8 addi 15 15 1
0aa slli 15 15 16
0ac store 10 0 9 1
0b0 srli 15 15 16
0b2 addi 10 10 16
0b4 jump 138
0b6 store 10 12 10 2
0b8 store 10 0 4 4
0bc jump 168
''',
'create':'''
000 addi 2 2 -16
002 addi 11 0 611
006 addi 10 0 488
00a store 2 1 12 4
00c store 2 8 8 4
00e store 2 9 4 4
010 auipc 1 536510464
014 jalr 1 1 1422
018 addi 12 0 488
01c li 11 0
01e mv 8 10
020 auipc 1 536514560
024 jalr 1 1 -1830
028 li 10 0
02a beqz 8 92
02c lui 9 536883200
030 addi 15 9 1032
034 load 13 15 156 4
038 addi 9 9 1032
03c beqz 13 106
03e mv 14 13
040 li 15 1
042 load 12 14 8 2
044 beq 12 15 166
048 load 14 14 0 4
04a bnez 14 66
04c store 8 15 8 2
04e bnez 15 144
050 mv 10 8
052 auipc 1 536510464
056 jalr 1 1 1564
05a load 10 8 8 2
05c load 1 2 12 4
05e load 8 2 8 4
060 load 9 2 4 4
062 addi 2 2 16
064 jr 1
066 mv 14 13
068 jump 66
06a li 15 1
06c store 8 15 8 2
06e store 9 8 156 4
072 store 9 8 160 4
076 store 9 15 180 2
07a jal 1 358884
07e load 15 9 160 4
082 store 15 0 0 4
086 store 8 0 10 1
08a store 8 0 14 1
08e jump 90
090 load 15 9 160 4
094 store 15 8 0 4
096 load 15 9 180 2
09a store 9 8 160 4
09e addi 15 15 1
0a0 store 9 15 180 2
0a4 jump 126
0a6 addi 14 15 1
0aa slli 15 14 16
0ae slli 12 14 16
0b2 srli 15 15 16
0b4 bge 12 0 102
0b8 li 15 0
0ba jump 76
'''
}
)

def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'task5 allocation literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=pc
        out[pc+int(off,16)]=f
    return out


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    for off,width in UNSIGNED[part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==(((4 if width==1 else 5)<<12)|3),'task5 allocation unsigned encoding')
    n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'task5 allocation complete boundaries '+part)
    for p,f in s.items():init.g(n,p,'task5 allocation operand '+part+' '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'task5 allocation original identity '+part)
    e={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'task5 allocation ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':check(v['rd']==1,'task5 allocation linked call');calls.append({'offset':p-pc,'target':v['target']})
        elif op=='jalr':
            check(v['rd']==v['rs1']==1 and n[p-4]['op']=='auipc' and n[p-4]['rd']==1,'task5 allocation call pair')
            calls.append({'offset':p-pc,'target':(p-4+n[p-4]['imm']+v['imm'])&0xfffffffe})
        check(all(q in n for q in qs),'task5 allocation closed CFG');e[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(e[p])
    check(seen==set(n),'task5 allocation all nodes reachable')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(calls),len(rets))==((0,1),(1,1),(4,1))[k],'task5 allocation call/return census')
    cuts={'descriptor_lookup':((0x40,0x2a),),'backing_init':((0xb4,0x8a),),'create':((0x4a,0x42),(0x68,0x42))}
    cut={p:list(qs) for p,qs in e.items()}
    for a,z in cuts[part]:
        check(pc+z in cut[pc+a],'task5 allocation cycle edge');cut[pc+a].remove(pc+z)
    check(not common.acyclic(e) and common.acyclic(cut),'task5 allocation cycles completely cut')
    return {'start':pc,'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'CFG':e,'calls':calls,'tails':[],
      'returns':rets,'stores':stores,'complete_local_body':True,'cycle_cut_edges':cuts[part],'actual_termination_or_safe_access_proved':False}


def domains():
    histogram=Counter((((h+33)//32)*32)&65535 for h in range(65536))
    check(set(histogram)==set(range(0,65536,32)) and sum(histogram.values())==65536,'allocation full U16 rounding domain')
    total=zero=truncated=maximum=0;digest=sha256()
    for flag in range(2):
        for n in range(256):
            D=n+1 if flag==0 else 2*n;K=D-n;L=16*D
            check(0<=D<=510 and K==(1 if flag==0 else n),'allocation descriptor/payload count')
            for R in sorted(histogram):
                full=L+R*K;W=full&65535
                check(W%16==0 and ((W+3)&~3)==W,'allocation request already core aligned')
                check((full<=65535)==(full==W),'allocation truncation equivalence')
                maximum=max(maximum,full);total+=1;zero+=W==0;truncated+=full>65535
                digest.update(bytes((flag,n))+R.to_bytes(2,'little')+W.to_bytes(2,'little'))
    check(total==1048576 and maximum==16711680,'allocation request domain census/max')
    # Pointer/counter algebra, not a memory or instruction model.
    for D in range(511):
        check(D<65536 and D*16<2**32,'allocation counter never U16 wraps and descriptor distance fits U32')
        for fresh_n in range(256):
            K_after=(D-fresh_n)&0xffffffff;payload_rows=min(D,K_after)
            check(0<=payload_rows<=D,'allocation fresh count row partition')
            if fresh_n<=D:check(payload_rows==D-fresh_n,'allocation ordinary row partition')
            else:check(payload_rows==D,'allocation underflow selects every descriptor')
    keys=list(range(1,32769));check(keys[-2]==32767 and all(((k<<16)&0x80000000)==0 for k in keys[:-1]) and ((keys[-1]<<16)&0x80000000)!=0,'allocation key signed threshold')
    # Descriptor step16 has order2**28 modulo2**32. D<=510 gives
    # no earlier equality to end, even for a base near address wrap.
    check(510<2**28,'lookup finite pointer difference bound')
    return {'rounding_U16_cases':65536,'rounding_distinct_values':2048,'rounding_histogram':sorted(histogram.items()),
      'request_cases':total,'zero_requests':zero,'truncated_requests':truncated,'maximum_untruncated_formula':maximum,'request_vectors_sha256':digest.hexdigest(),
      'formula':'D=(n+1 if flag==0 else 2*n);K=D-n;L=16*D;R=(32*((h+33)//32))&65535;W=(L+R*K)&65535',
      'fresh_n_row_partition_cases':511*256,'fresh_n_formula':'K_after=(D-fresh_n_after)&0xffffffff;payload_rows=min(D,K_after)',
      'key_increment_cases':32768,'accepted_key_domain':[1,32767],'descriptor_count_domain':[0,510],
      'reachable_configuration_or_memory_safety_proved':False}


def profile(image,data,hexraw,index,parent):
    bs={p:body(init.binding.take(data,STARTS[index][k],SIZES[k]),p,index) for k,p in enumerate(PARTS)}
    lookup,backing,create=(bs[p] for p in PARTS);lp,bp,cp=STARTS[index]
    B=0x200033b8+80*index;C=0x2000319c+80*index;G=0x20003000
    ln={v['pc']-lp:v for v in lookup['instructions']};bn={v['pc']-bp:v for v in backing['instructions']};cn={v['pc']-cp:v for v in create['instructions']}
    check(backing['calls']==[{'offset':0x6a,'target':0x20000040}],'backing core join')
    check(create['calls']==[{'offset':0x14,'target':0x20000040},{'offset':0x24,'target':0x2000039c},{'offset':0x56,'target':0x20000110},{'offset':0x7a,'target':bp}],'create core/fill/release/backing joins')
    check(cn[2]['imm']==611 and cn[6]['imm']==cn[0x18]['imm']==488 and cn[0x1c]['imm']==0,'object request/fill arguments')
    check(cn[0x1e]['rs2']==10 and cn[0x2a]['rs1']==8,'object pointer saved before fill and null check')
    check(cn[0x4c]['imm']==cn[0x5a]['imm']==8 and cn[0x50]['rs2']==8,'zero-key release then fresh object key read')
    check(ln[4]['imm']+G==C+95 and ln[12]['imm']+G==C+164 and ln[0x14]['imm']+G==B+172,'lookup config and backing source')
    check(bn[0x0c]['imm']==bn[0x74]['imm']==172 and bn[0x40]['imm']==46,'backing slot and h source')
    check(bn[0x5c]['imm']==580 and bn[0x70]['imm']==15,'backing tag and post-allocation fresh n')
    check(lookup['stores']==[] and lookup['calls']==[],'descriptor lookup no local writes/calls')
    nonframe=[v for v in backing['stores'] if v['base']!=2]
    check({(v['base'],v['imm'],v['bytes']) for v in nonframe}=={(19,172,4),(10,4,4),(10,10,2),(10,9,1)},'backing exact initialized fields; no payload fill')
    reset=parent['bodies']['reset'];rn={v['pc']-reset['start']:v for v in reset['instructions']}
    check(rn[8]['imm']==172 and rn[0x20]['imm']==172,'previous reset releases same backing slot')
    life=common.previous;fr=life.release
    free_nodes,_=life.free_body(init.binding.take(data,fr.DETAILS[index][0],212),index)
    check(len(free_nodes)>0,'existing private release strict reuse')
    fill_pc=0x4060c+64*index;fill=source.fill_contract(init.binding.take(data,fill_pc,46))
    check(fill['encoded_S0_S1_S2_SP_RA_nonwrites'],'fill preserves saved object pointer in encoded body')
    _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
    for p,b in bs.items():
        check(sparse.captured(mem,b['start'],b['bytes'])==init.binding.take(data,b['start'],b['bytes']),'allocation original HEX backing')
        receipts.append({'part':p,'start':b['start'],'bytes':b['bytes'],'all_bytes_captured':True})
    return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,
      'CFG_certificates':{p:common.certificates(b) for p,b in bs.items()},
      'roles':{'registry_head':B+156,'registry_tail':B+160,'registry_count_U16':B+180,'backing_pointer':B+172,'n_U8':C+95,'flag_U8':C+164,'h_U16':B+46},
      'fill_reuse':{'source':fill_pc,'bytes':46,'sha256':fill['sha256'],'null_destination_guard':True},
      'object_contract':['core(488,611),save O;fill(O,0,488) before null check;matching fill null guard prevents destination writes for O0,then creator returns0',
        'if captured head empty:key1,head=tail=O,count1 before backing_init;ignore backing reply;fresh tail.next=0 without null guard;clear O10/O14;fresh U16[O8] reply',
        'nonempty:find first missing key1..32767 by rescanning captured head;append via fresh tail;SH(count+1);fresh tail.next0;clear O10/O14;fresh U16[O8] reply',
        'all keys present:store O8=0,attempt private release(O),then fresh U16[O8] read;safe post-release access and fixed0 reply UNPROVED',
        'successful return key does not prove backing initialization succeeded;no rollback or list snapshot guarantee'],
      'backing_contract':['entry B172 nonzero returns ambient entry A0 unchanged;otherwise compute W and core(W,580);null allocation returns0',
        'nonnull P:read fresh n,store B172=P before descriptor initialization;initialize D rows,then return cursor P+16D modulo32,not baseP',
        'first min(D,(D-fresh_n)&0xffffffff) rows get payload cursor at+4 and tagff52 at+10;remaining rows get0 at+4 and tagff54 at+10;all rows byte9=0',
        'payload cursor starts P+16D and advances R only for payload rows;other descriptor bytes and payload contents are not locally cleared',
        'ordinary bounds require nontruncated size,retained fresh n,valid returned extent and address arithmetic;actual reachable n/flag/h and allocation success unproved'],
      'lookup_contract':['fresh config recomputes D independently of allocator snapshot;scan B172 in16-byte steps until end P+16D',
        'return first row with U16[row10]==full requested A0 OR sentinelffff;otherwise0. Initial ff52/ff54 tags are not ffff',
        'no backing null guard;D0 exits without row read;D<=510 algebra bounds scan only under valid memory/normal instruction premises'],
      'removal_join':'registry-held O is original488-byte core payload only with retained registry/key/heap identity;previous remove may pass O to release then fresh tail write. New exhaustion path also reads O after release attempt',
      'premises':'conditional matching candidate ISA/profile;valid frame/global/heap/object/backing memory;normal callee preservation of saved registers/frames;stable snapshots only where separately justified;no adverse alias/reentry/IRQ/DMA/unaccounted writers',
      'actual_installed_provider_or_postrelease_lifetime_proved':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage,hexes):
    parent=previous.derive(image,carriers,header,coverage,hexes)
    profiles=[profile(image,d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==888,'allocation byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==304,'allocation instruction census')
    return {'schema':'TSL9-task5-allocation-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'complete_body_bytes':888,'complete_body_instructions':304,'C_reconstruction_coverage_changed':False,
      'remaining':['actual configuration writers/reachable size domain','release-after-access ownership and V34 downstream','installed provider binding and physical progress'],
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
                else:raise RuntimeError('task5 allocation mutation escaped')
                mutations+=1
            for off,width in UNSIGNED[part]:
                bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
                try:body(bad,part,i)
                except RuntimeError as ex:check('unsigned encoding' in str(ex),'task5 allocation exact signedness guard')
                else:raise RuntimeError('task5 allocation signedness escaped')
                unsigned+=1
    check((mutations,unsigned)==(304,12),'task5 allocation mutation census');domains()
    print('PASS:304 instruction/12 signedness mutations rejected;65536 rounding/1048576 request/130816 fresh-count/32768 key scalar cases')


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
    else:check(OUT.read_bytes()==raw,'task5 allocation exact ledger replay')
    print('PASS:888B/304i complete lookup/backing/create;strict HEX backing;allocation provenance;exact ledger')
    print('PASS:NO target execution/emulation;installed binding/reachable sizes/post-release lifetime UNPROVED')


if __name__=='__main__':main()
