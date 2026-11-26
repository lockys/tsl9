"""Static fallback-slot lifecycle: startup zero range and full config function.

All calls are opaque normal-return boundaries. Missing contiguous input bytes
are reported, never supplied or executed. No target ISA/heap/MMIO emulation.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_allocation_core_static as core

message,timer,binding = core.message,core.timer,core.binding
ROOT,LIB,MASK = core.ROOT,core.LIB,core.MASK
OUT=Path(__file__).with_name('v4160-fallback-initialization-static.json')
ZERO=0x20000022
CFG_TEMPLATE=bytes.fromhex(
 '1c41f1cf41777d8fb706002089476319d70c5a2171c7411126c21946aa849305f00f'
 '610506c622c497d0fb1fe780608105478d47630fe5089c4491c7985c994749cbd85c'
 '59c7373400201306000481451305c41e97c0fb1fe780a06c13060004a6851305c41e'
 '97c0fb1fe780e0649307c41eda2701e713070010daa7f82719e30547f8a79a2b19e3'
 '6d479aabf83719e31547f8b7b82b19e30547b8abb83b19e3f837b8bbd82b19e3'
 '2547d8abf82801e71307c003f8abdc5791c78297b73700202392a71ab7370020'
 '7d57a38ae75ecd3b8147b240224492443e854101828089473e858280')
DETAILS=(
 (0x6de0c,0x40292,0x43c7e,0x20002ef8,0x20003614,0x200031ec,0x6eaa4,0x20002e70,0x20002ef8,420,1525,
  '7a0cf58801fabb3dcb9d26fcece3d01b2f41276dacce4130daff0e663559927f',
  'c07bd6c2683b5aa3db852c523b30438cfff119d8920ba3c577943ebfc7b8ac6a',
  'dc0cfe70fdbcb5f85158fe44d57780e562607b7182ddfd371bdc05b0e4a754f3'),
 (0x6dffc,0x402d2,0x43d0a,0x20002f48,0x20003664,0x2000323c,0x6ec94,0x20002ebc,0x20002f48,500,1605,
  'e5a738246f7b39ca8dc057596acaf0040bb6673935fac8015ef1dba8af84c74e',
  'b50f930aec0a45c60255bb412cf59ca3ea8fbd89b992cef9569cc43bea1b8cbb',
  '4fc5bf263804bbb6e2633b2b5c597bde01b8cefaad605696b3e18b7bd4579d2c'))
check,sx=timer.check,timer.sx


def decode(raw,start):
    nodes,off={},0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'initialization partial instruction')
        chunk,pc=raw[off:off+size],start+off;w=int.from_bytes(chunk,'little')
        if size==4 and w&0x707f==0x67:
            d=dict(pc=pc,bytes=chunk.hex(),size=size,op='jalr',rd=w>>7&31,rs1=w>>15&31,imm=sx(w>>20,12))
        else:d=message.decode(chunk,pc)[pc]
        nodes[pc]=d;off+=size
    return nodes


def g(nodes,p,name,**fields):message.guard(nodes,p,name,**fields)


def pair(nodes,pc,rd,target,name):
    a,b=nodes[pc],nodes[pc+4]
    check(a['op']=='auipc' and a['rd']==(1 if rd==1 else 6) and b['op']=='jalr' and b['rd']==rd and
          b['rs1']==a['rd'] and ((pc+a['imm']+b['imm'])&MASK&~1)==target,name)


def zero_contract(data,src,start,last):
    raw=binding.take(data,src,30);nodes=decode(raw,ZERO)
    specs={0:dict(op='lui',rd=15,imm=0x20003000),4:dict(op='lui',rd=14,imm=0x20003000),
        8:dict(op='addi',rd=15,rs1=15,imm=start-0x20003000),
        12:dict(op='addi',rd=14,rs1=14,imm=last-0x20003000),
        16:dict(op='bgeu',rs1=14,rs2=15,target=ZERO+22),20:dict(op='jr',rs1=1),
        22:dict(op='store',rs2=0,rs1=15,imm=0,width=4),26:dict(op='addi',rd=15,rs1=15,imm=4),
        28:dict(op='jump',target=ZERO+16)}
    check(set(nodes)=={ZERO+p for p in specs},'zero helper boundaries')
    for p,f in specs.items():g(nodes,ZERO+p,'zero instruction '+hex(p),**f)
    edges,cycles=timer.cfg(nodes,ZERO)
    check(cycles==[[hex(ZERO+p) for p in (16,22,26,28)]],'zero helper SCC')
    check(start%4==0 and last%4==0 and start<=last and last+4<=MASK,'zero unsigned nonwrapping range')
    return raw,nodes,edges,cycles


def config_contract(data,pc,dest,half_offset,byte_offset):
    raw=binding.take(data,pc,228);n=decode(raw,pc)
    g(n,pc,'config initial field read',op='load',rd=15,rs1=10,imm=0,width=4)
    g(n,pc+2,'config zero field branch',op='beqz',rs1=15,target=pc+222)
    g(n,pc+18,'config length read',op='load',rd=14,rs1=10,imm=4,width=2,mnemonic='qk.c.lhu')
    g(n,pc+28,'config source saved',op='mv',rd=9,rs2=10)
    pair(n,pc+40,1,0x200004bc,'config validation call')
    g(n,pc+70,'config global base',op='lui',rd=8,imm=0x20003000)
    g(n,pc+74,'config fill count',op='addi',rd=12,rs1=0,imm=64)
    g(n,pc+78,'config fill byte',op='li',rd=11,imm=0)
    for off in (80,98):g(n,pc+off,'config destination',op='addi',rd=10,rs1=8,imm=dest-0x20003000)
    pair(n,pc+84,1,0x2000039c,'config fill call')
    g(n,pc+92,'config copy count',op='addi',rd=12,rs1=0,imm=64)
    g(n,pc+96,'config copy source',op='mv',rd=11,rs2=9)
    pair(n,pc+102,1,0x20000332,'config copy call')
    check(binding.word(data,0x40048)&~1==0x2000039c and binding.word(data,0x4004c)&~1==0x20000332,
          'config helper slot aliases')
    g(n,pc+110,'config post-copy base',op='addi',rd=15,rs1=8,imm=dest-0x20003000)
    fields=((122,12,2),(130,14,1),(138,16,2),(146,15,1),(154,18,1),(162,19,1),(170,20,1),(180,22,1))
    for i,(off,field,width) in enumerate(fields):
        g(n,pc+off,'config default store '+str(i),op='store',rs2=14,rs1=15,imm=field,width=width,
          mnemonic='qk.c.sh' if width==2 else 'qk.c.sb')
        check(set(range(field,field+width)).isdisjoint(range(52,56)),'config defaults disjoint from callback')
    g(n,pc+182,'config callback field',op='load',rd=15,rs1=15,imm=44,width=4)
    g(n,pc+184,'config callback null branch',op='beqz',rs1=15,target=pc+196)
    g(n,pc+186,'config callback register',op='call_indirect',rd=1,rs1=15)
    g(n,pc+188,'config callback result base',op='lui',rd=15,imm=0x20003000)
    g(n,pc+192,'config callback result store',op='store',rs2=10,rs1=15,imm=half_offset,width=2)
    g(n,pc+196,'config later store base',op='lui',rd=15,imm=0x20003000)
    g(n,pc+202,'config later byte store',op='store',rs2=14,rs1=15,imm=byte_offset,width=1)
    g(n,pc+206,'config later direct call',op='jal',rd=1,target=pc-320)
    spans=((40,8),(80,4),(84,8),(98,4),(102,8),(110,4),(192,4),(202,4))
    check(core.outer.normalized(raw,spans)==core.outer.normalized(CFG_TEMPLATE,spans),'complete config body template')
    # All calls in this topology mean ASSUMED normal returns, never callee effects.
    edges,cycles=timer.cfg(n,pc)
    check(not cycles,'config normal-return CFG acyclic')
    return raw,n,edges,[{'pc':hex(pc+off),'destination_field':field,'bytes':width} for off,field,width in fields]


def derive(app,carriers,header):
    parent=core.derive(app,carriers,header)
    m=re.search(rb'^#define\s+BLE_LibInit\s+[^\r\n]*BLE_LIB_JT\(\s*(\d+)\s*\)',header,re.M)
    check(m is not None and int(m[1])==28 and 0x40034+28*4==0x400a4,'config header JT28')
    profiles=[]
    for data,previous,detail in zip(carriers,parent['profiles'],DETAILS):
        init,zsrc,cfg,start,last,dest,copy2source,copy2dest,copy2last,hoff,boff,ih,zh,ch=detail
        mapping=binding.profile(data,previous['label']);seed=int(mapping['seed_source'],16)
        check(int(mapping['initializer'],16)==init and seed+18==zsrc and
              binding.take(data,seed,18)==binding.HELPER,'initializer and zero seed source')
        ir=binding.take(data,init,114);inn=decode(ir,init)
        g(inn,init,'initializer frame',op='addi',rd=2,rs1=2,imm=-16)
        g(inn,init+6,'initializer saved RA',op='store',rs2=1,rs1=2,imm=12,width=4)
        g(inn,init+102,'initializer restored RA',op='load',rd=1,rs1=2,imm=12,width=4)
        g(inn,init+104,'initializer restored SP',op='addi',rd=2,rs1=2,imm=16)
        pair(inn,init+106,0,ZERO,'initializer zero tail target')
        first=mapping['first_copy']
        pair(inn,init+62,1,0x20000010,'initializer first copy target')
        second=binding.constants(data,init+70,init+102,stop_call=True)
        check((second['source'],second['destination'],second['inclusive_last'],second['target'])==
              (copy2source,copy2dest,copy2last,0x20000010),'second copy operands')
        request=copy2last-copy2dest+4;file_end=LIB+len(data)
        captured=LIB<=copy2source and copy2source+request<=file_end
        check(not captured and copy2source-file_end==62,'second copy known contiguous-input gap')
        zr,zn,ze,zc=zero_contract(data,zsrc,start,last)
        slot=int(previous['slots']['fallback'],16)
        check(dest+52==slot and start<=slot and slot+4<=last+4 and (slot-start)%4==0,
              'fallback destination and zero range relation')
        check((last-start)//4+1==456 and (slot-start)//4+1==203,'zero word count and callback ordinal')
        check(binding.word(data,0x400a4)==cfg,'config entry slot')
        cr,cn,ce,defaults=config_contract(data,cfg,dest,hoff,boff)
        bodylist=[{'role':role,'source':hex(src),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),
                  'expected_sha256':digest,'instructions':list(nodes.values())}
            for role,src,raw,digest,nodes in (('initializer',init,ir,ih,inn),('zero_helper',zsrc,zr,zh,zn),('config',cfg,cr,ch,cn))]
        profiles.append({'label':previous['label'],'fallback_slot':hex(slot),'bodies':bodylist,
            'zero':{'runtime_target':hex(ZERO),'start':hex(start),'inclusive_last':hex(last),'end_exclusive':hex(last+4),
                'word_count':456,'fallback_one_based_word':203,'CFG':ze,'cyclic_SCCs':zc},
            'second_copy_request':{'source':hex(copy2source),'source_end_exclusive':hex(copy2source+request),
                'destination':hex(copy2dest),'inclusive_last':hex(copy2last),'bytes':request,
                'contiguous_input_end_exclusive':hex(file_end),'source_starts_after_file_end_by':62,
                'all_requested_bytes_captured':captured,'missing_bytes_supplied':False},
            'first_copy_end_exclusive':mapping['first_copy_end_exclusive'],
            'first_second_destination_overlap_bytes':int(first['inclusive_last'],16)+4-copy2dest,
            'second_zero_destination_overlap_bytes':copy2last+4-start,
            'config':{'slot':'0x400a4','target':hex(cfg),'destination':hex(dest),'source':'live S1',
                'copy_bytes':64,'fallback_source_field':[52,56],'fallback_write':'four ordered source bytes via copy helper',
                'copy_target':'0x20000332','fill_target':'0x2000039c','default_stores':defaults,
                'post_copy_opaque_calls':[hex(cfg+186),hex(cfg+206)],
                'optional_callback_field':[44,48],'optional_callback_is_fallback_field':False,
                'other_direct_post_copy_stores':[{'address':hex(0x20003000+hoff),'bytes':2},
                    {'address':hex(0x20003000+boff),'bytes':1}],
                'conditional_normal_return_CFG':ce,'normal_return_CFG_acyclic':True},
            'full_startup_completed_proved':False,'installed_binding_proved':False,
            'slot_value_at_later_allocation_proved':False})
    return {'schema':'TSL9-fallback-init-static-v1','profile':timer.PROFILE,
        'scope':'Static startup ranges and complete config bytes/conditional CFG; no target ISA/data simulation',
        'installed_binding_proved':False,'physical_ISA_profile_proved':False,
        'whole_ROM_writer_absence_proved':False,'profiles':profiles,
        'zero_then_config_copy_is_conditional_source_chain':True,
        'required_premises':['all prior calls return with required live registers/frame/code intact',
            'valid stable accesses and suitable nonaliasing','matching installed resident/ISA/slot targets',
            'no intervening writes when transferring a slot-value conclusion between program points']}


def tests(app,carriers,header):
    for d in DETAILS:
        _,_,_,start,last,dest,_,_,_,_,_,_,_,_=d
        words=range(start,last+1,4);slot=dest+52
        check(len(words)==456 and words[202]==slot and slot+3<=last+3,'zero address-range algebra')
        field=set(range(52,56))
        check(all(field.isdisjoint(range(o,o+n)) for o,n in ((12,2),(14,1),(16,2),(15,1),(18,1),(19,1),(20,1),(22,1))),
              'default field byte-range algebra')
    # Changes enter derive without full-file hash rejection; exact guards required.
    cases=(
      (0x40292+16,'6373f700','6363f700','zero instruction 0x10'),
      (0x40292+22,'23a00700','23a0a700','zero instruction 0x16'),
      (0x6de0c+78,None,None,'second copy operands'),
      (0x6de0c+110,None,None,'initializer zero tail target'),
      (0x43c7e+80,None,None,'config destination'),
      (0x43c7e+74,None,None,'config fill count'),
      (0x43c7e+106,None,None,'config copy call'),
      (0x43c7e+122,'daa7','faa7','config default store 0'),
      (0x43c7e+182,'dc57','dc5b','config callback field'),
      (0x43c7e+186,'8297','0297','config callback register'))
    for pc,oldhex,newhex,error in cases:
        cs=[bytearray(c) for c in carriers];off=pc-LIB
        if oldhex is None:
            old=bytes(cs[0][off:off+4]);new=(int.from_bytes(old,'little')+(4<<20)).to_bytes(4,'little')
        else:old,new=bytes.fromhex(oldhex),bytes.fromhex(newhex)
        check(cs[0][off:off+len(old)]==old,'fallback-init mutation pin');cs[0][off:off+len(new)]=new
        try:derive(app,cs,header)
        except RuntimeError as e:check(str(e)==error,'unexpected initialization mutation guard: '+str(e))
        else:raise RuntimeError('fallback initialization mutation escaped')
    print('PASS: 2 x 456 zero-word addresses; field+52/word203 relations; 16 disjoint default fields; 10 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');options=p.parse_args()
    app,header=binding.APP.read_bytes(),core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==core.outer.HEADER_HASH,'SDK header identity')
    cs=[]
    for label,folder,tail,n,digest in binding.PROFILES:
        b=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(b)==n and sha256(b).hexdigest()==digest,'candidate identity '+label);cs.append(b)
    sources,vectors=timer.source_contract();ledger=derive(app,cs,header)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    for profile in ledger['profiles']:
        for b in profile['bodies']:check(b['sha256']==b['expected_sha256'],'complete initialization body identity')
    tests(app,cs,header);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if options.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'fallback initialization ledger exact replay')
    print('PASS: 6 complete bodies, 744 bytes; full config suffix/conditional CFG; second-copy source gaps retained')
    print('PASS: ledger exact replay; installed/full boot/later slot identity UNPROVED; NO ISA/provider/MMIO execution')


if __name__=='__main__':main()
