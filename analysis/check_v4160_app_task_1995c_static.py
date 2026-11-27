"""Offline APP1995c task dispatch, registration and service call contracts.

Pinned original operands/CFG, bitstring identities and source-field joins.
No target ISA, mutable event/queue/register machine, callback or MMIO runs.
"""
import argparse,json,re
from collections import Counter
from hashlib import sha256
from pathlib import Path
import check_v4160_message_receive_static as previous
import check_v4160_app_config_source_static as source
import check_v4160_mode3_frame_static as mode
import check_v4160_task_registration_static as registration
import check_v4160_constructor_publication_chain_static as publication
import check_v4160_first_registration_chain_static as first
import check_v4160_timer_start_setup_static as timer
import check_v4160_first_role_gate_static as role
import check_v4160_rf_tail_return_static as rf

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.previous
OUT=Path(__file__).with_name('v4160-app-task-1995c-static.json')
PC,SIZE,COUNT=0x1995c,134,49
HASH='f091e186b336f48c8ce3719606bd99403fe3965445529d252be0da22a5cfef5c'
FIELDS={**previous.FIELDS,'xor':('rd','rs1','rs2'),'xori':('rd','rs1','imm')}
BRANCHES=previous.BRANCHES
LITERAL='''
000 addi 2 2 -16
002 slli 15 11 16
006 store 2 8 8 4
008 store 2 1 12 4
00a store 2 9 4 4
00c srai 15 15 16
00e mv 8 11
010 bge 15 0 48
014 lui 9 262144
018 load 15 9 108 4
01a call_indirect 1 15
01c beqz 10 34
01e load 15 9 104 4
020 call_indirect 1 15
022 lui 10 32768
024 xor 10 10 8
026 load 1 2 12 4
028 load 8 2 8 4
02a load 9 2 4 4
02c addi 2 2 16
02e jr 1
030 andi 15 11 1
034 xori 10 11 1
038 bnez 15 38
03a slli 15 11 18
03e bge 15 0 102
042 lui 9 262144
046 load 15 9 492 4
04a call_indirect 1 15
04c jal 1 104376
050 load 15 9 88 4
052 lui 12 192512
056 addi 12 12 -512
05a lui 11 8192
05c load 10 3 388 1
060 call_indirect 1 15
062 lui 10 8192
064 jump 36
066 slli 15 11 17
06a li 10 0
06c bge 15 0 38
070 lui 15 262144
074 load 15 15 88 4
076 addi 12 0 1600
07a lui 11 16384
07c load 10 3 388 1
080 call_indirect 1 15
082 lui 10 16384
084 jump 36
'''


def specs():
    out={}
    for line in LITERAL.splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'APP1995c literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=PC
        out[PC+int(off,16)]=f
    return out


def body(raw):
    for off in (0x5c,0x7c):check(int.from_bytes(raw[off:off+4],'little')&0x707f==0x4003,'APP1995c unsigned task encoding')
    n=decode(raw,PC);s=specs();check(n.keys()==s.keys(),'APP1995c whole boundaries')
    for p,f in s.items():init.g(n,p,'APP1995c operand '+hex(p-PC),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNT,HASH),'APP1995c original identity')
    edges={};calls=[];rets=[]
    slots={0x1a:(0x4006c,0x18),0x20:(0x40068,0x1e),0x4a:(0x401ec,0x46),0x60:(0x40058,0x50),0x80:(0x40058,0x74)}
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'APP1995c ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':
            check(v['rd']==1 and v['target']==0x197b8,'APP1995c direct mode3 target')
            calls.append({'offset':p-PC,'target':v['target'],'link':p+v['size']})
        elif op=='call_indirect':
            off=p-PC;check(v['rd']==1 and v['rs1']==15 and off in slots,'APP1995c call register')
            slot,load=slots[off];z=n[PC+load]
            check(z['rd']==15 and z['imm']==slot-0x40000,'APP1995c fresh slot displacement')
            calls.append({'offset':off,'slot':slot,'load_offset':load,'effective_target':'fresh word & ~1','link':p+v['size'],
              'literal_slot_if_base_preserved':True,'actual_installed_binding_proved':False})
        check(all(q in n for q in qs),'APP1995c complete local CFG');edges[p]=qs
    seen=set();pending=[PC]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(edges[p])
    check(seen==set(n) and common.acyclic(edges),'APP1995c all nodes reachable/local DAG')
    stores=[{'offset':p-PC,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check(stores==[{'offset':6,'base':2,'source':8,'imm':8,'bytes':4},{'offset':8,'base':2,'source':1,'imm':12,'bytes':4},{'offset':10,'base':2,'source':9,'imm':4,'bytes':4}],'APP1995c exact frame-only writes')
    check(len(calls)==6 and rets==[PC+0x2e],'APP1995c call/return census')
    defs=sorted({v['rd'] for v in n.values() if v.get('rd',0)})
    check(defs==[1,2,8,9,10,11,12,15],'APP1995c complete GPR definitions')
    check([p-PC for p,v in n.items() if v.get('rd')==8]==[0xe,0x28] and [p-PC for p,v in n.items() if v.get('rd')==2]==[0,0x2c],'APP1995c saved full event and frame definitions')
    return {'start':PC,'bytes':SIZE,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'CFG':edges,'calls':calls,'tails':[],
      'returns':rets,'stores':stores,'GPR_definitions':defs,'complete_local_body':True,'local_CFG_acyclic':True,'transitive_progress_proved':False}


def paths(b):
    choices={'message_null':{0x10:0x14,0x1c:0x22},'message_nonzero':{0x10:0x14,0x1c:0x1e},
      'bit0':{0x10:0x30,0x38:0x26},'bit13':{0x10:0x30,0x38:0x3a,0x3e:0x42},
      'bit14':{0x10:0x30,0x38:0x3a,0x3e:0x66,0x6c:0x70},
      'none':{0x10:0x30,0x38:0x3a,0x3e:0x66,0x6c:0x26}}
    out={name:common.walk(b,c) for name,c in choices.items()}
    expected={'message_null':[0x1a],'message_nonzero':[0x1a,0x20],'bit0':[],
      'bit13':[0x4a,0x4c,0x60],'bit14':[0x80],'none':[]}
    calls={c['offset'] for c in b['calls']}
    for name,seq in out.items():
        check([o for o in seq if o in calls]==expected[name],'APP1995c selected call order '+name)
        check(seq[-5:]==[0x26,0x28,0x2a,0x2c,0x2e],'APP1995c shared restore/RET')
    return out


def domains():
    hist=Counter();examples={};highs=(0,1,0x7fff,0x8000,0xffff);cases=0
    for low in range(65536):
        selected=0x8000 if low&0x8000 else 1 if low&1 else 0x2000 if low&0x2000 else 0x4000 if low&0x4000 else 0
        hist[hex(selected)]+=1;examples.setdefault(hex(selected),low)
        for high in highs:
            word=(high<<16)|low
            half=(word<<16)&0xffffffff
            shift18=(word<<18)&0xffffffff;shift17=(word<<17)&0xffffffff
            by_branches=0x8000 if half&0x80000000 else 1 if word&1 else 0x2000 if shift18&0x80000000 else 0x4000 if shift17&0x80000000 else 0
            check(by_branches==selected,'APP1995c shift/sign predicates equal bit priority')
            reply=word^selected if selected else 0
            if selected:check(reply>>16==high and not reply&selected,'APP1995c lowmask XOR preserves upper16')
            else:check(reply==0,'APP1995c no handled bits returns0, not E')
            cases+=1
    check(dict(hist)=={'0x0':4096,'0x1':16384,'0x2000':8192,'0x4000':4096,'0x8000':32768},'APP1995c complete low16 priority partition')
    check(0x2f000-512==192000 and 1600==0x640,'APP1995c timer literal construction')
    GP,TASK=publication.GP,publication.TASK
    check(GP==0x20004000 and TASK==0x20004184 and GP+388==TASK,'APP1995c nominal task byte address')
    for i in range(2):
        C=0x2000319c+80*i
        check(TASK!=C+3 and C+1!=C+3,'APP1995c saved registered ID differs from resident builder-task storage')
        check(C+1+1<=C+3 and C+3+1<=first.layout.T+12,'APP1995c registration writes exclude builder task byte')
    return {'low16_event_cases':65536,'five_highword_vector_cases':cases,'priority_partition':dict(hist),'first_examples':examples,
      'priority_masks':[0x8000,1,0x2000,0x4000],'unhandled_event_reply':0,'handled_reply':'full32 E XOR chosen lowmask,with required saved-event preservation',
      'all_highwords_algebra':'branch sign depends only on low bits15/13/14; XOR mask<65536 preserves full upper16 for any highword',
      'timer_arguments':{'bit13':[8192,192000],'bit14':[16384,1600]},'actual_event_or_task_reachability_proved':False}


def joins(image,data,index,parent):
    GP,TASK=publication.GP,publication.TASK;C=0x2000319c+80*index
    wrapper=source.body(image[0x19b16-0x8000:0x19b56-0x8000],'wrapper')
    wn={v['pc']:v for v in wrapper['instructions']}
    init.g(wn,0x19b26,'APP1995c source upper',op='auipc',rd=10,imm=0)
    init.g(wn,0x19b2a,'APP1995c registration target source',op='addi',rd=10,rs1=10,imm=-458)
    check(0x19b26-458==PC,'APP1995c wrapper pointer equals new complete body')
    init.g(wn,0x19b30,'APP1995c saved ID byte address',op='addi',rd=8,rs1=3,imm=388)
    init.g(wn,0x19b34,'APP1995c saved ID byte write',op='store',rs1=8,rs2=10,imm=0,width=1)
    registered=registration.body(init.binding.take(data,registration.DETAILS[index][0],48),index)
    check(init.binding.word(data,0x40080)==int(registered['start'],16),'APP1995c registration candidate slot')
    check(int(registered['count_byte'],16)==C+1,'APP1995c registration context join')
    for fact in first.layout.facts():check(fact['N0']>=14 and 3<fact['N0'],'APP1995c nominal registration capacity')
    check(first.layout.T+12==0x20004800 and first.layout.T+12+4<=first.layout.T+14*4,'APP1995c nominal entry3 footprint')
    mode_tail=source.body(image[0x197b8-0x8000:0x197be-0x8000],'mode_tail')
    mn={v['pc']:v for v in mode_tail['instructions']}
    check(mn[0x197b8]['rd']==10 and mn[0x197b8]['imm']==3 and mode_tail['external_tails']==[{'pc':'0x197ba','target':'0x1929a','link_written':False}],'APP1995c direct call ->mode3 tail')
    mode_body=mode.body(image[mode.PC-0x8000:mode.END-0x8000],{10,11,12,13,14,15})
    timerpc=timer.DETAILS[index][0];timerbody=timer.body(init.binding.take(data,timerpc,332),'service',index)
    check(init.binding.word(data,0x40058)==timerpc,'APP1995c timer candidate slot')
    rd=role.DETAILS[index]
    gate=role.body(init.binding.take(data,rd['gate'],84),'gate',index)
    initialize=role.body(init.binding.take(data,rd['initialize'],62),'initialize',index)
    gn={v['pc']-rd['gate']:v for v in gate['instructions']};rn={v['pc']-rd['initialize']:v for v in initialize['instructions']}
    check(gn[14]['imm']+gn[18]['imm']==rd['handler'] and gn[22]['target']==rd['reg'] and gn[26]['target']==rd['initialize'],'APP1995c resident zero-gate registration source')
    check(rn[20]['rd']==8 and rn[20]['rs2']==10 and rn[58]['rs2']==8 and rn[58]['imm']+0x20003000==C+3,'APP1995c distinct resident gate-byte writer')
    check(5<14 and first.layout.T+20==0x20004808 and 5!=3,'APP1995c nominal task5 is not APP task3')
    rfpc=rf.DETAILS[index][0][2];rfbody=rf.body(init.binding.take(data,rfpc,232),'tail',index)
    check(init.binding.word(data,0x401ec)==rfpc,'APP1995c BLE_RegInit candidate body alias')
    check(parent['bodies']['receive']['start']==0x2000028c and init.binding.word(data,0x4006c)==0x2000028c,'APP1995c full receive join')
    check(init.binding.word(data,0x40068)==common.dealloc.DETAILS[index][0],'APP1995c public free join')
    return {'label':init.binding.PROFILES[index][0],
      'candidate_slots':{hex(slot):hex(init.binding.word(data,slot)) for slot in (0x40058,0x40068,0x4006c,0x40080,0x401ec)},
      'registration_wrapper':{k:wrapper[k] for k in ('start','bytes','sha256')},
      'registration_leaf':{k:registered[k] for k in ('start','bytes','sha256')},
      'conditional_registration':{'old_count':3,'new_count':4,'callback_entry_address':first.layout.T+12,'callback_value':PC,'saved_low8_reply_address':TASK,'saved_reply':3},
      'registration_premises':'matching prior nominal allocation/bootstrap and registration path; valid stable capacity/table/count3,normal provider return and GP/frame preservation; no intervening writers',
      'resident_builder_task_byte':C+3,'saved_APP_task_byte':TASK,'these_storage_addresses_equal':False,
      'builder_task_relation':'registration writes count C1 and tableentry3,then APP savesreply atGP388; neither establishes builder task byte C3=3. All writers,retention and actual dispatch remain unproved',
      'conditional_distinct_routing':{'gate_bytes_SHA256':gate['sha256'],'initializer_prefix_SHA256':initialize['sha256'],
        'fresh_gate_before_registration':0,'prior_count':5,'new_count':6,'entry5_address':first.layout.T+20,
        'entry5_handler':rd['handler'],'initializer_stored_task':5,'builder_task_if_retained':5,'APP_saved_task_if_retained':3,
        'premises':'same prior selected second-registration/count5 chain,matching current gate0/capacity/table,normal fill/setter returns and S0 preservation,execution reaches initializer+62; no initializer return inferred,no later gate/APP byte writers',
        'conclusion':'under retention of these selected values, threshold-builder task5 differs from APP1995c task3; no causal message route to APP1995c established'},
      'mode_tail':{k:mode_tail[k] for k in ('start','bytes','sha256','external_tails')},
      'mode_callee':{k:mode_body[k] for k in ('start','bytes','sha256','calls')},'mode_new_return_link':'0x199ac',
      'mode_preservation':'197b8 forcesA0=3 and tails1929a with original taskcall link199ac; matching complete mode/reader proof preserves required S/GP/SP/RA on normal return with valid nonalias savedframe/MMIO and no external interference; polling/signed arithmetic/physical completion not proved',
      'timer_body':{k:timerbody[k] for k in ('start','bytes','sha256')},
      'BLE_RegInit_candidate_body':{k:rfbody[k] for k in ('start','bytes','sha256')},
      'receive_free_join':'matching slots +returned M nonzero +preserved S1=40000 ->fresh publicfree(M); receive/unlink restores markerFF. Previous nominal interior-free proof applies only with its retained heap/header/account premises',
      'BLE_RegInit_boundary':'SDK JT110 declares void(void); encoded fresh401ec call sees ambient A0=E XOR1,A1=E before opaque call. No argument normalization, callable identity or physical effects established',
      'RF_reentry_boundary':'fresh later invocation may have different state/magic/descriptors/slots from startup; prior selected state1/RF progress/return cannot be carried over without renewed premises',
      'runtime_dispatch_or_builder_task_equality_proved':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);raw=image[PC-0x8000:PC-0x8000+SIZE];b=body(raw)
    match=re.search(rb'^#define\s+BLE_RegInit\s+[^\r\n]*BLE_LIB_JT\(\s*(\d+)\s*\)',header,re.M)
    check(match is not None and int(match[1])==110 and 0x40034+4*110==0x401ec,'APP1995c SDK BLE_RegInit alias')
    n={v['pc']-PC:v for v in b['instructions']}
    check(n[0x4c]['target']==0x197b8 and PC+0x4c==0x199a8,'APP1995c exact JAL callsite/callee')
    check(not any(v['op'] in ('load','store') and (v.get('rs1')==10 or v.get('rs2')==10) for o,v in n.items() if 0x1a<o<0x22),'APP1995c no message-body dereference before cleanup')
    check(n[0x52]['imm']+n[0x56]['imm']==192000 and n[0x5a]['imm']==8192 and n[0x76]['imm']==1600 and n[0x7a]['imm']==16384,'APP1995c exact timer inputs')
    return {'schema':'TSL9-APP1995c-task-static-v1','APP_sha256':sha256(image).hexdigest(),'body':b,'CFG_certificates':common.certificates(b),'selected_walks':paths(b),'integer_domains':domains(),
      'profiles':[joins(image,d,i,parent['profiles'][i]) for i,d in enumerate(carriers)],
      'event_contract':['bit15 first:receive(entrytask),nonnull reply ->free(reply),return E XOR8000; no message body parse or direct pointer storage',
        'elsebit0: return E XOR1 with no service call',
        'elsebit13:fresh401ec;direct197b8;fresh40058(freshU8[thenliveGP388],8192,192000);return E XOR2000',
        'elsebit14:fresh40058(freshU8[thenliveGP388],16384,1600);return E XOR4000; neither ->0',
        'receive pointer result is tested for null; cleanup and other service scalar replies are not tested; handled return uses preserved full event,not service success; at most one handled mask per normal invocation'],
      'preservation_premises':'matching APP/ISA; valid frame,code,source/global/MMIO accesses; normal nested return and S0/S1/GP/SP/RA/savedframe preservation as needed; no adverse alias/IRQ/DMA/reentry/external writers; fresh task/slot samples not equated without evidence',
      'new_complete_APP_body_bytes':SIZE,'new_complete_APP_body_instructions':COUNT,'C_reconstruction_coverage_changed':False,
      'remaining':['actual task table invocation and builder-task-byte writers','fresh BLE_RegInit/provider identity and side effects','other APP consumers and lifetime/physical progress'],
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(image):
    raw=image[PC-0x8000:PC-0x8000+SIZE];ns=decode(raw,PC);mutations=0
    for p,v in ns.items():
        off=p-PC;z=v['size'];bad=bytearray(raw)
        bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
        try:body(bad)
        except RuntimeError:pass
        else:raise RuntimeError('APP1995c instruction mutation escaped')
        mutations+=1
    for off in (0x5c,0x7c):
        bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
        try:body(bad)
        except RuntimeError as ex:check('unsigned task' in str(ex),'APP1995c specific signedness guard')
        else:raise RuntimeError('APP1995c signedness mutation escaped')
    # Independent bit encoding distinguishes mode-tail197b8 from config44 callback197f0.
    delta=(0x197f0-(PC+0x4c))&0x1fffff
    word=((delta>>20&1)<<31)|((delta>>1&1023)<<21)|((delta>>11&1)<<20)|((delta>>12&255)<<12)|(1<<7)|0x6f
    check(decode(word.to_bytes(4,'little'),PC+0x4c)[PC+0x4c]['target']==0x197f0,'APP1995c alternative JAL regression vector')
    bad=bytearray(raw);bad[0x4c:0x50]=word.to_bytes(4,'little')
    try:body(bad)
    except RuntimeError as ex:check('operand' in str(ex),'APP1995c exact callee operand guard')
    else:raise RuntimeError('APP1995c wrong callee escaped')
    check(mutations==49,'APP1995c mutation census');domains()
    print('PASS:49 instruction mutations,2 signedness variants and wrong-callee regression rejected;65536 event classes/327680 highword vectors')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image)
    output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if args.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'APP1995c exact ledger replay')
    print('PASS:complete APP1995c134B/49i;priority,receive/free,registration,mode3/timer joins;exact ledger')
    print('PASS:NO target execution/emulation;actual dispatch/task-byte/provider binding and physical effects UNPROVED')


if __name__=='__main__':main()
