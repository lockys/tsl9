"""Immediate registration callback -> APP wrapper tail, strictly static.

Original operands, finite CFGs, GPR/store censuses and closed scalar/interval
identities only. No target ISA, callback, arithmetic, RAM or MMIO runner.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_constructor_publication_chain_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.mode.decode
OUT=Path(__file__).with_name('v4160-registration-return-chain-static.json')
DETAILS=((0x43b0a,0x43d62,560,436,412,564,
 'c1ae94b8dca2206f84673ac3b1afc8ce88784cc5d0a7083f9d46bc15ed4469ea',
 '28c771edbcd95fbf855f2569c9a88af86b39f2cefded1d66a8c4a27be8871b94'),
 (0x43b96,0x43dee,640,516,492,644,
 'aede15264ca4512a35a21886c468d388ec39ba74fbf4e985863f8748d8d00f12',
 '346dc3f382e6bdc69d2b867b1d7a94a5e959718091f23675f02d4e0d95e7c32e'))
ARITH_HASH='f4060bab83e2fde71bb16115cbc831a37ebc925599da24ca2015d5e4805a73b5'
CONTROLS=((8,'bne',13,0,350),(12,'bgeu',11,12,188),(18,'bltu',12,14,456),
 (26,'bltu',12,15,858),(56,'beqz',14,None,78),(110,'bgeu',16,11,130),
 (120,'bltu',16,17,128),(124,'bltu',16,11,902),(158,'bgeu',16,13,180),
 (168,'bltu',16,17,178),(174,'bltu',16,13,180),(186,'jr',1,None,0),
 (188,'bnez',12,None,196),(198,'bltu',17,14,438),(206,'bltu',17,15,866),
 (236,'bnez',15,None,474),(276,'bgeu',15,13,296),(286,'bltu',15,17,294),
 (290,'bltu',15,13,908),(322,'bgeu',15,29,344),(332,'bltu',15,17,342),
 (338,'bltu',15,29,344),(348,'jr',1,None,0),(350,'bltu',11,13,416),
 (356,'bltu',13,15,422),(364,'bltu',13,15,850),(396,'bne',28,0,608),
 (400,'bltu',13,11,874),(414,'jr',1,None,0),(420,'jr',1,None,0),
 (426,'bgeu',15,13,880),(436,'jump',None,None,374),(444,'bgeu',14,17,216),
 (454,'jump',None,None,216),(462,'bgeu',14,12,36),(472,'jump',None,None,36),
 (528,'bgeu',13,15,550),(538,'bltu',13,17,898),(542,'bgeu',13,15,898),
 (576,'bgeu',14,10,598),(586,'bltu',14,17,890),(590,'bgeu',14,10,890),
 (606,'jump',None,None,256),(672,'bgeu',17,11,694),(682,'bltu',17,13,894),
 (686,'bgeu',17,11,894),(722,'bgeu',11,6,744),(732,'bltu',11,13,886),
 (736,'bgeu',11,6,886),(794,'bgeu',13,14,800),(806,'bltu',11,12,842),
 (810,'beq',11,12,820),(818,'jr',1,None,0),(838,'bgeu',10,13,814),
 (848,'jr',1,None,0),(856,'jump',None,None,374),(864,'jump',None,None,36),
 (872,'jump',None,None,216),(878,'jr',1,None,0),(884,'jump',None,None,374),
 (888,'jump',None,None,744),(892,'jump',None,None,598),(896,'jump',None,None,694),
 (900,'jump',None,None,550),(906,'jump',None,None,130),(912,'jump',None,None,296))
CONTROL_OPS={'beq','bne','beqz','bnez','bgeu','bltu','jump','jr'}


def graph(n,pc,label):
    edges={}
    for p,d in n.items():
        if d['op']=='jr':check(d['rs1']==1,label+' ordinary RET');q=[]
        elif d['op']=='jump':q=[d['target']]
        elif d['op'] in CONTROL_OPS:q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),label+' CFG no cuts');edges[p]=q
    seen=set();active=set();length={}
    def visit(p):
        check(p not in active,label+' CFG acyclic')
        if p in seen:return length[p]
        active.add(p);value=1+max((visit(q) for q in edges[p]),default=0)
        active.remove(p);seen.add(p);length[p]=value;return value
    longest=visit(pc);check(seen==set(n),label+' whole local reachability')
    return edges,longest


def specs(role,index):
    reg,cb,slot,result,ctx,copied,*_=DETAILS[index];pc=reg if role=='registration' else cb;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v):e(o,'store',rs2=r,rs1=b,imm=v,width=4)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    if role=='registration':
        addi(0,2,2,-16);lui(2,15,0x20003000);store(6,1,2,12);store(8,10,15,slot)
        e(12,'call_indirect',rd=1,rs1=10);load(14,1,2,12);lui(16,15,0x20003000)
        store(20,10,15,result);e(24,'li',rd=10,imm=0);addi(26,2,2,16);e(28,'jr',rs1=1)
    else:
        addi(0,2,2,-32);store(2,18,2,16);lui(4,18,0x20003000);load(8,15,18,copied)
        for off,r,v in ((12,1,28),(14,8,24),(16,9,20),(18,20,8),(20,21,4),(22,19,12)):store(off,r,2,v)
        e(24,'call_indirect',rd=1,rs1=15);addi(26,20,0,1600);binary(30,'mulhu',11,10,20)
        addi(34,18,18,copied);load(38,21,18,8,2);e(42,'li',rd=13,imm=0)
        e(44,'mv',rd=12,rs2=21);binary(46,'mul',10,10,20)
        e(50,'jal',rd=1,target=previous.arithmetic.BASES[index]);lui(54,15,0x20003000)
        addi(58,14,15,ctx);load(62,8,14,24);e(64,'mv',rd=9,rs2=10);e(66,'li',rd=10,imm=0)
        e(68,'beq',rs1=8,rs2=9,target=pc+112);addi(72,19,15,ctx);binary(76,'sub',10,9,8)
        e(80,'bltu',rs1=8,rs2=9,target=pc+108);load(84,10,18,4)
        e(88,'mv',rd=12,rs2=21);e(90,'li',rd=13,imm=0);binary(92,'mulhu',11,20,10)
        binary(96,'mul',10,20,10);e(100,'jal',rd=1,target=previous.arithmetic.BASES[index])
        binary(104,'sub',10,10,8);binary(106,'add',10,10,9);store(108,9,19,24)
        for off,r,v in ((112,1,28),(114,8,24),(116,9,20),(118,18,16),(120,19,12),(122,20,8),(124,21,4)):load(off,r,2,v)
        addi(126,2,2,32);e(128,'jr',rs1=1)
    return pc,s


def body(raw,role,index):
    pc,s=specs(role,index);n=decode(raw,pc)
    check(set(n)==set(s),'return '+role+' boundaries')
    for p,f in s.items():init.g(n,p,'return '+role+' operand '+hex(p-pc),**f)
    size,count,digest=(30,11,DETAILS[index][6]) if role=='registration' else (130,46,DETAILS[index][7])
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'return '+role+' identity')
    edges,longest=graph(n,pc,'return '+role)
    stores=[p-pc for p,d in n.items() if d['op']=='store'];defs=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(stores==([6,8,20] if role=='registration' else [2,12,14,16,18,20,22,108]),'return exact store census')
    check(defs==([1,2,10,15] if role=='registration' else [1,2,8,9,10,11,12,13,14,15,18,19,20,21]),'return GPR census')
    check([p-pc for p,d in n.items() if d['op'] in ('call_indirect','jal')]==([12] if role=='registration' else [24,50,100]),'return exact call census')
    return {'start':hex(pc),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'longest_local_path_nodes':longest,'encoded_GPR_definitions':defs,'complete_function':True}


def arithmetic(raw,pc):
    n=decode(raw,pc)
    for off,op,a,b,t in CONTROLS:
        fields={'op':op}
        if a is not None:fields['rs1']=a
        if b is not None:fields['rs2']=b
        if op!='jr':fields['target']=pc+t
        init.g(n,pc+off,'return arithmetic control '+hex(off),**fields)
    check({p-pc for p,d in n.items() if d['op'] in CONTROL_OPS}=={c[0] for c in CONTROLS},'return arithmetic full control census')
    for off,rd,base in ((46,14,14),(226,13,14),(384,14,15)):
        init.g(n,pc+off,'return arithmetic load '+hex(off),op='load',rd=rd,rs1=base,imm=0,width=1,mnemonic='qk.c.lbu')
    check([p-pc for p,d in n.items() if d['op']=='load']==[46,226,384],'return arithmetic three byte loads')
    check(not any(d['op'] in ('store','jal','jalr','call_indirect','csr','fence.i') for d in n.values()),'return arithmetic no writes/calls/privileged operations')
    defs=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(defs==[6,10,11,12,13,14,15,16,17,28,29,30],'return arithmetic no RA/SP/GP/S definitions')
    check((len(raw),len(n),sha256(raw).hexdigest())==(914,296,ARITH_HASH),'return arithmetic complete byte identity')
    edges,longest=graph(n,pc,'return arithmetic')
    normalized=[]
    for d in n.values():
        c=dict(d);c['pc']-=pc
        if 'target' in c:c['target']-=pc
        normalized.append(c)
    return {'bytes':914,'instructions':normalized,'sha256':ARITH_HASH,'instruction_addresses':'relative to candidate entry',
        'normal_return_CFG':{hex(p-pc):[hex(q-pc) for q in qs] for p,qs in edges.items()},
        'encoded_GPR_definitions':defs,'longest_local_path_nodes':longest,
        'RET_offsets':[p-pc for p,q in edges.items() if not q],
        'complete_CFG_and_preservation':True,'general_numeric_quotient_proved':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage)
    profiles=[];common=None
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        reg,cb,slot,result,ctx,copied,*_=DETAILS[i]
        r=body(init.binding.take(data,reg,30),'registration',i);b=body(init.binding.take(data,cb,130),'callback',i)
        ar=arithmetic(init.binding.take(data,previous.arithmetic.BASES[i],914),previous.arithmetic.BASES[i])
        if common is None:common=ar
        else:check(ar==common,'return arithmetic full relative body identical across candidates')
        check(pr['unclosed_registration_call']['target']==hex(reg) and previous.gates.DETAILS[i][7]==cb,'return prior registration/callback argument joins')
        check(0x20003000+copied==int(pr['copied_config'],16) and 0x20003000+ctx+24==0x20003000+result,'return fresh copied source and result-slot alias')
        reader=previous.mode.service.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,previous.mode.service.APP_HASHES[1])
        check(not reader['calls'] and not any(d['op']=='store' for d in reader['instructions']),'return reader closure no stores or calls')
        # Both callback branches which store Q are followed by registration's
        # unconditional store of delta to that SAME address.
        fields=[(0x20003000+slot,4),(0x20003000+result,4)]
        protected=[(previous.TASK,1),(0x20003000+ctx+1,1),(0x20003000+ctx+2,1),
            (0x20003000+ctx+40,4),(int(pr['hook_word'],16),4),(int(pr['copied_config'],16),16),
            (int(pr['service_word'],16),4),(previous.previous.layout.B,8),(previous.previous.layout.T+12,4)]
        for p,w in fields:
            for q,z in protected:check(previous.previous.origin.separated(p,w,q,z),'return field stores exclude protected ranges')
        pc,size=previous.gates.DETAILS[i][:2];g=previous.gates.body(init.binding.take(data,pc,size),i)
        _,a=previous.gates.specs(pc,i);gn={d['pc']:d for d in g['instructions']}
        init.g(gn,a(150),'return config forces zero',op='li',rd=10,imm=0)
        suffix=[d for p,d in gn.items() if a(150)<=p<=a(158)]
        check([d['op'] for d in suffix]==['li','load','load','addi','jr'],'return config epilogue')
        tail=int.from_bytes(init.binding.take(data,0x40058,4),'little')
        profiles.append({'label':pr['label'],'registration':r,'callback':b,
            'callback_slot':hex(0x20003000+slot),'prior_and_final_result_word':hex(0x20003000+result),
            'copied_reader_word':hex(0x20003000+copied),'arithmetic_entry':hex(previous.arithmetic.BASES[i]),
            'config_return_suffix':suffix,'registration_return_zero':True,'config_return_zero':True,
            'conditional_task_byte':3,'conditional_count':4,'conditional_entry3':'0x1995c',
            'candidate40058_word':hex(tail),'tail_execution_or_actual_binding_proved':False})
    constructor=previous.app.body(image[0x19b56-0x8000:0x19bd4-0x8000],'construct')
    wrapper=previous.app.body(image[0x19b16-0x8000:0x19b56-0x8000],'wrapper')
    cn={d['pc']:d for d in constructor['instructions']};wn={d['pc']:d for d in wrapper['instructions']}
    for pc,f in ((0x19bce,dict(op='load',rd=1,rs1=2,imm=28,width=4)),
        (0x19bd0,dict(op='addi',rd=2,rs1=2,imm=32)),(0x19bd2,dict(op='jr',rs1=1))):init.g(cn,pc,'return constructor epilogue',**f)
    check(not any(d.get('rd')==10 for p,d in cn.items() if p>=0x19bce),'return constructor forwards config zero')
    init.g(wn,0x19b3a,'return wrapper re-reads unsigned byte',op='load',rd=10,rs1=8,imm=0,width=1)
    init.g(wn,0x19b40,'return wrapper fresh tail pointer',op='load',rd=6,rs1=9,imm=88,width=4)
    init.g(wn,0x19b54,'return wrapper tail no link',op='jr',rs1=6)
    check(0x2f000-512==192000 and 8192==0x2000,'return tail argument algebra')
    return {'schema':'TSL9-registration-return-chain-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),
        'scope':'complete two30B/11instruction registration wrappers, two130B/46instruction callbacks, two914B/296instruction general arithmetic bodies (same relative bytes); existing APP/reader/gates reused',
        'profiles':profiles,'shared_arithmetic_body':common,
        'callback_numeric_boundary':'R is matching reader reply, h=fresh copied U16+8, first helper input is exact unsigned1600*R as A1:A0 with A2=h,A3=0; first A0 result Q is opaque, helper A1 ignored',
        'callback_cases':{'old_equals_Q':'reply0, no callback ctx+24 store',
            'old_unsigned_less_than_Q':'reply(Q-old)mod2^32, callback first stores Q',
            'old_unsigned_greater_than_Q':'second helper input1600*fresh U32[copied+4], same saved h; opaque secondA0=Q2; reply(Q2-old+Q)mod2^32, callback first stores Q'},
        'result_alias':'registration stores callback delta reply to ctx+24 after callback returns, overwriting intermediate Q; final equals delta (including0 on equal), NOT generally Q',
        'frame_projection':'constructor C; provider SP=C-32; registration SP=C-48 savesRA atC-36; callback SP=C-80 saves7words in[C-76,C-48); arithmetic/reader no frame or stores',
        'restoration':'matching reader and full general arithmetic locally preserve RA/SP/GP/S; callback saves/restoresRA,S0..S5; registration saves/restoresRA/SP. Valid nonalias saved words and normal calls remain premises',
        'conditional_return_chain':'registration forces0 -> config forces0 and restoresS0 -> constructor restoresRA/SP and forwards0 -> wrapper19b3a overwritesA0 with saved task byte3',
        'wrapper_tail':{'fresh_slot_if_S1_preserved':'0x40058','call_site':'0x19b54','link_written':False,
            'conditional_arguments':{'A0':3,'A1':8192,'A2':192000},'SP_RA_S0_S1':'restored wrapper entry values before tail',
            'target':'fresh U32[then-live S1+88] & ~1, loaded at19b40 beforeS1restore; nominal40058 needsS1=40000',
            'callee_body_and_hardware_success_proved':False},
        'premises':'all prior alternative-path conditions; matching preserved candidate/reader/helper code, fresh copied word191c6 andrequired freshfields; valid nonwrapping/nonalias frames/globals/heap; no adverse lookup/MMIO/FENCE.I effects, IRQ/DMA/reentry/unknownwriters; required reads/calls return normally',
        'lifetime':'constructor stack source is released on return. Matching local copy transferred bytes/codepointer; no direct store sourced from the original config-pointer register is identified in the new callees. Opaque Q/delta may numerically equal C; no blanket provider-retention or later payload-lifetime guarantee',
        'remaining':['fresh40058 callee and setup continuation','actual provider/GP/slot preservation and externalwriters',
            'general arithmetic numerical quotient, reader progress, physical effects and later object lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=0
    for i,data in enumerate(carriers):
        for role,pc,size in (('registration',DETAILS[i][0],30),('callback',DETAILS[i][1],130)):
            raw=init.binding.take(data,pc,size)
            for p,d in decode(raw,pc).items():
                at=p-pc;w=d['size'];buf=bytearray(raw)
                buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
                try:body(buf,role,i)
                except RuntimeError as e:check(str(e).startswith('return '+role+' operand '),'return mutation operand guard '+str(e))
                else:raise RuntimeError('return operand mutation escaped')
                mutations+=1
        pc=previous.arithmetic.BASES[i];raw=init.binding.take(data,pc,914);nodes=decode(raw,pc)
        for off in [c[0] for c in CONTROLS]+[46,226,384]:
            d=nodes[pc+off];w=d['size'];buf=bytearray(raw)
            buf[off:off+w]=(int.from_bytes(buf[off:off+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
            try:arithmetic(buf,pc)
            except RuntimeError as e:check(str(e).startswith(('return arithmetic control ','return arithmetic load ')),'return arithmetic mutation guard '+str(e))
            else:raise RuntimeError('return arithmetic mutation escaped')
            mutations+=1
    check(mutations==252,'return full mutation census')
    child=set(range(-76,-48))|set(range(-36,-32));caller=set(range(16))|set(range(28,48))|set(range(-32,0))
    check(not child&caller and len(child)==32,'return nested frame disjointness')
    for value in range(65536):
        product=1600*value;check(((product>>32)<<32)+(product&0xffffffff)==product,'return wide multiply split identity')
    for r in (0,1,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff):
        product=1600*r;check(product<2**64 and product>>32<=1599,'return full U32 multiply boundaries')
    triples=0
    for old in range(16):
        for q in range(16):
            for q2 in range(16):
                if old==q:delta=0
                elif old<q:delta=(q-old)&0xffffffff
                else:delta=(q2-old+q)&0xffffffff
                staged=0 if old==q else (q-old if old<q else (((q2-old)&0xffffffff)+q)&0xffffffff)
                check(delta==staged,'return staged SUB/ADD vs modular identity');triples+=1
    check(triples==4096 and ((0xffffffff-0xfffffffe+7)&0xffffffff)==8,'return modular boundary case')
    print('PASS:252 registration/callback/arithmetic operand mutations rejected; frames;65536 product identities;4096 reply cases')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'registration return exact ledger replay')
    print('PASS:full immediate registration/callback/general arithmetic CFGs; ctx+24 delta overwrite; conditional wrapper tail(3,8192,192000); exact ledger')
    print('PASS:NO target execution; actualbinding/general quotient/physical effects/40058/later lifetime UNPROVED')


if __name__=='__main__':main()
