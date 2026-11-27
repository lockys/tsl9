"""Offline generator body, bounded-loop and integer-domain certificates.

Original operands/graphs and pure bitstring/scalar arithmetic only. No target
ISA, mutable register/RAM machine, RNG/provider/callback/MMIO execution.
"""
import argparse
import json
from collections import deque,Counter
from hashlib import sha256
from pathlib import Path
import check_v4160_comparator_tail_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
ranges=previous.ranges
OUT=Path(__file__).with_name('v4160-generator-static.json')
PARTS=('generator',)
STARTS=((0x640d8,),(0x641c2,))
SOURCES=STARTS
SIZES=(216,)
COUNTS=(73,)
FIELDS={**previous.FIELDS,'srl':('rd','rs1','rs2')}
BRANCHES=previous.BRANCHES
HASHES=(('550457058926bad27d26b639e435ee11b2716f53af68d0080ea9416e85d9bcde',), ('f4b8c265605c98c6788a60a1c2c148f4554ad0d717b2e032073297a925d7722b',))
LITERALS=(
{
'generator':'''
000 addi 2 2 -32
002 store 2 9 20 4
004 store 2 18 16 4
006 store 2 19 12 4
008 lui 9 65536
00a lui 18 1778384896
00e lui 19 2885681152
012 store 2 8 24 4
014 store 2 20 8 4
016 store 2 1 28 4
018 li 8 1
01a addi 9 9 -1
01c addi 18 18 230
020 addi 19 19 206
024 addi 20 0 32
028 bnez 8 80
02a addi 11 0 240
02e li 10 16
030 jal 1 278122
034 lui 15 1778429952
038 slli 10 10 16
03a addi 15 15 -794
03e or 10 10 15
040 load 1 2 28 4
042 load 8 2 24 4
044 load 9 2 20 4
046 load 18 2 16 4
048 load 19 2 12 4
04a load 20 2 8 4
04c addi 2 2 32
04e jr 1
050 mv 11 9
052 li 10 0
054 jal 1 278158
058 slli 15 10 8
05c andi 14 15 256
060 or 10 15 18
064 beqz 14 106
066 or 10 15 19
06a li 15 0
06c li 14 0
06e li 11 24
070 srl 13 10 15
074 addi 15 15 1
076 srl 12 10 15
07a andi 13 13 1
07c andi 12 12 1
07e beq 12 13 140
082 addi 14 14 1
084 andi 14 14 255
088 bltu 11 14 208
08c bne 15 20 112
090 li 15 0
092 addi 12 0 63
096 li 13 27
098 srl 14 10 15
09c andi 14 14 63
0a0 beqz 14 208
0a2 beq 14 12 208
0a6 addi 15 15 1
0a8 bne 15 13 152
0ac srli 14 10 8
0b0 andi 15 10 255
0b4 andi 14 14 255
0b8 bne 15 14 64
0bc srli 14 10 16
0c0 andi 14 14 255
0c4 bne 15 14 64
0c8 srli 14 10 24
0cc bne 15 14 64
0d0 addi 8 8 1
0d2 andi 8 8 255
0d6 jump 40
'''
},
{
'generator':'''
000 addi 2 2 -32
002 store 2 9 20 4
004 store 2 18 16 4
006 store 2 19 12 4
008 lui 9 65536
00a lui 18 1778384896
00e lui 19 2885681152
012 store 2 8 24 4
014 store 2 20 8 4
016 store 2 1 28 4
018 li 8 1
01a addi 9 9 -1
01c addi 18 18 230
020 addi 19 19 206
024 addi 20 0 32
028 bnez 8 80
02a addi 11 0 240
02e li 10 16
030 jal 1 278262
034 lui 15 1778429952
038 slli 10 10 16
03a addi 15 15 -794
03e or 10 10 15
040 load 1 2 28 4
042 load 8 2 24 4
044 load 9 2 20 4
046 load 18 2 16 4
048 load 19 2 12 4
04a load 20 2 8 4
04c addi 2 2 32
04e jr 1
050 mv 11 9
052 li 10 0
054 jal 1 278298
058 slli 15 10 8
05c andi 14 15 256
060 or 10 15 18
064 beqz 14 106
066 or 10 15 19
06a li 15 0
06c li 14 0
06e li 11 24
070 srl 13 10 15
074 addi 15 15 1
076 srl 12 10 15
07a andi 13 13 1
07c andi 12 12 1
07e beq 12 13 140
082 addi 14 14 1
084 andi 14 14 255
088 bltu 11 14 208
08c bne 15 20 112
090 li 15 0
092 addi 12 0 63
096 li 13 27
098 srl 14 10 15
09c andi 14 14 63
0a0 beqz 14 208
0a2 beq 14 12 208
0a6 addi 15 15 1
0a8 bne 15 13 152
0ac srli 14 10 8
0b0 andi 15 10 255
0b4 andi 14 14 255
0b8 bne 15 14 64
0bc srli 14 10 16
0c0 andi 14 14 255
0c4 bne 15 14 64
0c8 srli 14 10 24
0cc bne 15 14 64
0d0 addi 8 8 1
0d2 andi 8 8 255
0d6 jump 40
'''
}
)


def specs(index):
    pc=STARTS[index][0];out={}
    for line in LITERALS[index]['generator'].splitlines():
        if not line:continue
        off,op,*args=line.split();vals=[int(v,0) for v in args];check(len(vals)==len(FIELDS[op]),'generator literalfields')
        d=dict(zip(FIELDS[op],vals));d['op']=op
        if op in BRANCHES|{'jump'}:d['target']+=pc
        out[pc+int(off,16)]=d
    return out


def body(raw,index):
    pc=STARTS[index][0];n=decode(raw,pc);s=specs(index);check(set(n)==set(s),'generator boundaries')
    for p,f in s.items():init.g(n,p,'generator operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(216,73,HASHES[index][0]),'generator identity')
    edges={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'generator RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jal':check(v['rd']==1,'generator RAcall');calls.append({'offset':p-pc,'target':hex(v['target'])})
        check(all(q in n for q in qs),'generator closedCFG');edges[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(edges[p])
    check(seen==set(n),'generator allnodes reachable')
    scc=previous.previous.previous.common.sccs(edges);cycles=[c for c in scc if len(c)>1 or c[0] in edges[c[0]]]
    check(bool(cycles),'generator retry/scans cycles')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'offset_from_base':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check(len(stores)==6 and all(v['base']==2 and v['bytes']==4 for v in stores),'generator frameonly stores')
    check([(v['source'],v['offset_from_base']) for v in stores]==[(9,20),(18,16),(19,12),(8,24),(20,8),(1,28)],'generator exactframe saves')
    check(calls==[{'offset':0x30,'target':hex(0x43e6a+140*index)},{'offset':0x54,'target':hex(0x43e8e+140*index)}] and rets==[pc+0x4e],'generator fullcalls/returns')
    check([p-pc for p,v in n.items() if v.get('rd')==8]==[0x18,0x42,0xd0,0xd2],'generator retrycounter definitions')
    check([p-pc for p,v in n.items() if v.get('rd')==2]==[0,0x4c],'generator frame32 restoration')
    return {'start':pc,'end_exclusive':pc+216,'bytes':216,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
      'CFG':edges,'cyclic_SCCs':cycles,'calls':calls,'stores':stores,'returns':rets,'complete_local_body':True,'local_CFG_acyclic':False,'actual_finite_callchain_proved':False}


def certificates(b):
    pc=b['start'];e=b['CFG'];end=b['returns'][0];n={v['pc']:v for v in b['instructions']}
    def path(a,z):
        pending=deque([(a,[a])]);seen=set()
        while pending:
            p,s=pending.popleft()
            if p==z:return s
            if p in seen:continue
            seen.add(p);pending.extend((v,s+[v]) for v in e[p])
        return None
    witnesses=[]
    for p,qs in e.items():
        for q in qs:
            s=path(pc,p)+[q]+path(q,end)[1:];check(all(z in e[a] for a,z in zip(s,s[1:])),'generator edgewitness');witnesses.append([v-pc for v in s])
    selected={hex(o):[v-pc for v in path(pc,pc+o)+path(pc+o,end)[1:]] for o in (0x30,0x54,0x66,0x76,0x88,0x98,0xa2,0xb8,0xc4,0xcc,0xd2)}
    cuts=((0x8c,0x70),(0xa8,0x98),(0xd6,0x28));reduced={p:list(q) for p,q in e.items()}
    for a,z in cuts:check(pc+z in reduced[pc+a],'generator backedge exists');reduced[pc+a].remove(pc+z)
    check(not any(len(c)>1 or c[0] in reduced[c[0]] for c in previous.previous.previous.common.sccs(reduced)),'generator allcycles cutbythreeboundededges')
    check(n[pc+0x24]['imm']==32 and n[pc+0x74]['imm']==1 and n[pc+0x8c]['rs2']==20,'generator transitionloop32anchors')
    check(n[pc+0x90]['imm']==0 and n[pc+0x96]['imm']==27 and n[pc+0xa6]['imm']==1 and n[pc+0xa8]['rs2']==13,'generator windowloop27anchors')
    check(n[pc+0x18]['imm']==1 and n[pc+0xd0]['imm']==1 and n[pc+0xd2]['imm']==255 and n[pc+0x28]['rs1']==8,'generator retry255anchors')
    check(not any(pc+0x6a<=p<pc+0xd0 and v['op']=='jal' for p,v in n.items()),'generator noinnerloop callees')
    return {'selected_syntactic_walks':selected,'edge_witness_count':len(witnesses),'edge_witness_sha256':sha256(json.dumps(witnesses,separators=(',',':')).encode()).hexdigest(),
      'three_cycle_cut_edges':[list(x) for x in cuts],'cut_graph_acyclic':True,
      'transition_scan':'index0,step1,stop32; twoSRLs readbits k and((k+1)&31); <=32iterations/attempt',
      'window_scan':'index0,step1,stop27; masks63 atshifts0..26; <=27iterations/attempt',
      'retry':'S0=1; failureincrementsandmasks255; nonzero1..255 attempt;zero selectsonefallback call thenRET',
      'scope':'conditional local index/CFG proof; calleeS/SP/framepreservation,validaccesses/ordinaryRV32semantics required; no physicalprogress proof'}


def facts(word):
    # Pure 32-bit string predicates, not an instruction/register machine.
    rot=((word<<1)&0xffffffff)|(word>>31)
    transitions=(word^rot).bit_count()
    bad=[k for k in range(27) if ((word>>k)&63) in (0,63)]
    same=len({(word>>k)&255 for k in (0,8,16,24)})==1
    category='transitions' if transitions>24 else 'window' if bad else 'all_equal' if same else 'accepted'
    return transitions,bad,same,category


def domains():
    M=1<<32;counts=Counter();hist=Counter();accepted=[];witnesses={}
    for q in range(65535):
        word=(q<<8)|(0xac0000ce if q&1 else 0x6a0000e6)
        t,bad,same,category=facts(word)
        check(t==sum(((word>>k)&1)!=((word>>((k+1)&31))&1) for k in range(32)),'generator circular transition identity')
        check(not same and (word&255)!=(word>>24),'generator allbytes-equal reject unreachable in mainfamily')
        counts[category]+=1;hist[t]+=1;witnesses.setdefault(category,{'q':q,'word':hex(word),'transitions':t,'bad_window_shifts':bad})
        if category=='accepted':accepted.append(word)
    expected={'transitions':1,'window':16344,'accepted':49190}
    check(dict(counts)==expected,'generator exactmainclassification')
    check(dict(sorted(hist.items()))=={10:16,12:680,14:6188,16:19448,18:24310,20:12376,22:2380,24:136,26:1},'generator transitionhist')
    mainhash=sha256(b''.join(w.to_bytes(4,'little') for w in accepted)).hexdigest()
    check(mainhash=='5d9cd8565fe1e7c3199bac755ead409fba934998c4e999c39de789305a9669c3','generator mainworddigest')
    fallback=[(r<<16)|0x6a00ace6 for r in range(16,240)];failed=[r for r,w in zip(range(16,240),fallback) if facts(w)[3]!='accepted']
    check(failed==[31,63,64,95,126,127,128,129,159,191,192,223],'generator fallbackbypasseswindowfilter')
    fallbackhash=sha256(b''.join(w.to_bytes(4,'little') for w in fallback)).hexdigest()
    check(fallbackhash=='6651830196c0df5c68fba196c80e8267cae415fe219ee2604b2dd36be4b4437d','generator fallbackdigest')
    check(len(set(fallback))==224 and len(set(fallback)&set(accepted))==212,'generator fallbackoverlap')
    check(len(set(fallback)|set(accepted))==49202,'generator conditionalwordunion')
    sequence=[k&255 for k in range(1,257)];check(sequence==list(range(1,256))+[0],'generator255failures wraptofallback')
    check(65535*(M-1)//M==65534 and 224*(M-1)//M+16==239,'generator rangeenvelopes')
    generic=0x80000001;check(facts(generic)[0]==2 and sum(((generic>>k)&1)!=((generic>>(k+1))&1) for k in range(32))==3,'generator SRL32mask semantic witness')
    return {'pure_U16_reply_cases':65535,'U16_0_65535_reply_domain':[0,65534],'mainfamily':'(q<<8) OR (qbit0?ac0000ce:6a0000e6)',
      'classification_priority_counts':{**expected,'all_equal':0},'transition_histogram':dict(sorted(hist.items())),'first_witnesses':witnesses,
      'accepted_main_word_sha256_littleendian_qorder':mainhash,'fallback_byte_domain':[16,239],'fallback_word_count':224,
      'fallback_formula':'(r<<16) OR6a00ace6; immediateRET suffix, doesnotrunmainfilters','fallback_bad_window_byte_values':failed,
      'fallback_passes_mainfilters_count':212,'fallback_failed_mainfilters_count':12,'fallback_allword_sha256_littleendian_rorder':fallbackhash,
      'distinct_return_word_union_under_helper_domains':49202,'allreturnedwordspass_mainfilters':False,
      'main_candidate_attempts_max':255,'fallback_requests_max':1,'range_helper_requests_max':256,'inner_iterations_per_attempt_max':{'transition':32,'window':27},
      'domain_is_actualsource_reachability_or_probability':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        pc=STARTS[i][0];b=body(init.binding.take(data,pc,216),i);n={v['pc']-pc:v for v in b['instructions']}
        byte=pr['bodies']['byte_range'];half=ranges.body(init.binding.take(data,0x43e8e+140*i,36),'signed_range',i)
        check(b['calls'][0]['target']==hex(byte['start']) and b['calls'][1]['target']==half['start'],'generator matchingrange joins')
        check(n[0x2a]['imm']==240 and n[0x2e]['imm']==16 and n[0x52]['imm']==0 and n[0x8]['imm']+n[0x1a]['imm']==65535,'generator rangesarguments')
        callback=previous.previous.body(init.binding.take(data,0x57b7c+320*i,322),'callback',i);cn={v['pc']-callback['start']:v for v in callback['instructions']}
        check(cn[0xce]['target']==pc and cn[0xd2]['op']=='store' and cn[0xd2]['rs2']==10 and cn[0xd2]['imm']==88,'generator callbackreply N88join')
        check(n[0xa]['imm']+n[0x1c]['imm']==0x6a0000e6 and n[0xe]['imm']+n[0x20]['imm']==0xac0000ce and n[0x34]['imm']+n[0x3a]['imm']==0x6a00ace6,'generator fullconstant construction')
        profiles.append({'label':pr['label'],'body':b,'CFG_certificates':certificates(b),
          'reused_range_helpers':{'byte':{k:byte[k] for k in ('start','bytes','sha256')},'halfword':{k:half[k] for k in ('start','bytes','sha256')}},
          'caller_join':{'callback_start':callback['start'],'callee_offset':0xce,'store_offset':0xd2,'destination':'callbackcapturedNprime+88','stored':'fullactualgeneratorA0','inputA0':'ignored; overwrittenbeforeanyread; noseedmeaninginferred'},
          'local_contract':{'frame':32,'saved':['RA','S0','S1','S2','S3','S4'],'nonframe_stores':False,'no_direct_global/object_accesses':True,
            'callee_effects':'rangehelpers callstatefulwordsource withcontrolword/statewrites andoptionalcallbacks; no actualpurity/lifetimeclaim',
            'main_calls':'U16wrapper(0,65535) untilaccepted or255rejections','fallback':'bytewrapper(16,240),OR6a00ace6,RETwithoutmainfilters',
            'conditional_bounds':'<=255mainrequests,<=1fallback,<=32transition/27windowiterations each; ordinaryRV32SRL mask31,calleecompletion/liveS/frame preservation required',
            'fullcallchain_termination/source_distribution/installedbinding/retention/physicaleffects_proved':False},'target_execution_or_emulation':False})
    return {'schema':'TSL9-generator-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'newbytes':432,'instruction_guards':146,'scope':'two complete216B73i generators; helpers/callback proofs reused withoutnewcoverage',
      'remaining':['composeexistingtimer/lookup/arithmetic returnandpreservation contracts','actualsource/providerbindings,globals/callbackwriters,objectlifetimes/physicaleffects'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=walks=edges=0
    for i,data in enumerate(carriers):
        pc=STARTS[i][0];raw=init.binding.take(data,pc,216);b=body(raw,i);c=certificates(b);walks+=len(c['selected_syntactic_walks']);edges+=c['edge_witness_count']
        for p,v in decode(raw,pc).items():
            at=p-pc;z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
            try:body(buf,i)
            except RuntimeError as ex:check(str(ex).startswith('generator operand '),'generator mutation specific '+str(ex))
            else:raise RuntimeError('generator mutationescaped')
            mutations+=1
    check(mutations==146,'generator mutationcensus');domains()
    print('PASS:146 instruction mutations rejected;432 new originalbytes;'+str(walks)+' selectedCFG walks;'+str(edges)+' edge witnesses;65535 bitstring cases/224fallback values/255retry bound')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'generator exactledger replay')
    print('PASS:full generator/range/callback joins; three bounded cyclecuts; main/fallbackdomains;exact ledger')
    print('PASS:NO target execution/emulation;actualreachability/sourcebindings/calleecompletion/preservation UNPROVED')


if __name__=='__main__':main()
