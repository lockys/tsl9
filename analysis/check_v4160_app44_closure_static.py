"""Static APP44 software call closure, including computed memset transfers.

Bytes, operands, finite call-context CFG and integer/interval algebra only.
No target instructions, registers, buffers, provider or MMIO are emulated.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_app44_callback_static as parent

init,ROOT,MASK=parent.init,parent.ROOT,parent.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-app44-closure-static.json')
DETAILS=(
 (0x8520,0x85c8,55,19,[1,5,6,11,12,13,14,15],'50232f532bf996f5d738050c60480fab6069d6ef4cb842cfc582170e351630c6'),
 (0x188e2,0x1892e,25,1,[1,2,10,11,15],'0149a0ddbea9fe8921c3b187b9af3ecf7c58bc88a5fa0eab292654a1bc625fe2'),
 (0x1892e,0x18986,37,3,[13,14,15],'2f5e265070408a8fcbb4172fb5a1a4574baecd33ffc971eaafb5fc02d678653e'),
 (0x18986,0x18996,7,1,[15],'1b0a6df26eca1dbb567293f57aaef784f3ece2541b357c34a7b9b0b73db968ac'),
 (0x18996,0x189ae,10,1,[14,15],'109d29fa3c462fd901491a44a3194fb0c75304697c274141c30a71adf332c200'),
 (0x189ae,0x18a66,64,5,[11,12,13,14,15,16],'4ed751edae4e2951378a0bd2cc45f177132b3eddac354508e2a4d226cdc38172'),
 (0x18a6e,0x18a8e,12,1,[13,14,15],'16b62275fb19c8620b88718782fbb625e7cdfed61651f7c100323911aea2d177'),
 (0x18a98,0x18ab0,10,1,[14,15],'902658d8747cb4cefe949b5936b88f01ddf2327d1f4d67e8e48ab7cf77b86ff9'),
 (0x1908c,0x1909e,8,1,[10,13,14,15],'8a1f8aa217067a65d4a6cfa6420d03b423019f47471c699a98afc65062a01b0a'),
 (0x19124,0x19142,12,2,[10,14,15],'ca3d4aef350f5c783ee6eeae7d25ba85b74055551058135024d07edf1804e864'),
 (0x19160,0x1917e,12,2,[10,14,15],'a5541a42d8ec2844fcd1d2df5492c90e2b140ce22ae79b02f50e330277c31b60'))


def decode(raw,pc):
    nodes,off={},0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'closure partial instruction')
        chunk,p=raw[off:off+size],pc+off;w=int.from_bytes(chunk,'little');key=w&0xfe00707f
        d=dict(pc=p,bytes=chunk.hex(),size=size)
        if size==4 and key in (0x40000033,0x1033,0x7033):
            d.update(op={0x40000033:'sub',0x1033:'sll',0x7033:'and'}[key],rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif size==2 and h&0xfc63==0x8c01:
            r=8+(h>>7&7);d.update(op='sub',rd=r,rs1=r,rs2=8+(h>>2&7))
        else:d=parent.decode(chunk,p)[p]
        nodes[p]=d;off+=size
    return nodes


def guard(n,pc,**fields):init.g(n,pc,'closure instruction '+hex(pc),**fields)


def memset_guards(n):
    rows=(
      (0x8520,'li',dict(rd=6,imm=15)),(0x8522,'mv',dict(rd=14,rs2=10)),
      (0x8524,'bgeu',dict(rs1=6,rs2=12,target=0x854a)),
      (0x8528,'andi',dict(rd=15,rs1=14,imm=15)),(0x852c,'bnez',dict(rs1=15,target=0x85aa)),
      (0x852e,'bnez',dict(rs1=11,target=0x8598)),(0x8530,'andi',dict(rd=13,rs1=12,imm=-16)),
      (0x8534,'andi',dict(rd=12,rs1=12,imm=15)),(0x8536,'add',dict(rd=13,rs1=13,rs2=14)),
      (0x8540,'addi',dict(rd=14,rs1=14,imm=16)),(0x8542,'bltu',dict(rs1=14,rs2=13,target=0x8538)),
      (0x8546,'bnez',dict(rs1=12,target=0x854a)),(0x8548,'jr',dict(rs1=1)),
      (0x854a,'sub',dict(rd=13,rs1=6,rs2=12)),(0x854e,'slli',dict(rd=13,rs1=13,imm=2)),
      (0x8550,'auipc',dict(rd=5,imm=0)),(0x8554,'add',dict(rd=13,rs1=13,rs2=5)),
      (0x8556,'jalr',dict(rd=0,rs1=13,imm=10)),(0x8596,'jr',dict(rs1=1)),
      (0x8598,'andi',dict(rd=11,rs1=11,imm=255)),(0x859c,'slli',dict(rd=13,rs1=11,imm=8)),
      (0x85a0,'or',dict(rd=11,rs1=11,rs2=13)),(0x85a2,'slli',dict(rd=13,rs1=11,imm=16)),
      (0x85a6,'or',dict(rd=11,rs1=11,rs2=13)),(0x85a8,'jump',dict(target=0x8530)),
      (0x85aa,'slli',dict(rd=13,rs1=15,imm=2)),(0x85ae,'auipc',dict(rd=5,imm=0)),
      (0x85b2,'add',dict(rd=13,rs1=13,rs2=5)),(0x85b4,'mv',dict(rd=5,rs2=1)),
      (0x85b6,'jalr',dict(rd=1,rs1=13,imm=-88)),(0x85ba,'mv',dict(rd=1,rs2=5)),
      (0x85bc,'addi',dict(rd=15,rs1=15,imm=-16)),(0x85be,'sub',dict(rd=14,rs1=14,rs2=15)),
      (0x85c0,'add',dict(rd=12,rs1=12,rs2=15)),(0x85c2,'bgeu',dict(rs1=6,rs2=12,target=0x854a)),
      (0x85c6,'jump',dict(target=0x852e)))
    expected={pc:dict(op=op,**f) for pc,op,f in rows}
    for i in range(4):expected[0x8538+2*i]=dict(op='store',rs1=14,rs2=11,imm=4*i,width=4)
    for i in range(15):expected[0x855a+4*i]=dict(op='store',rs1=14,rs2=11,imm=14-i,width=1)
    check(set(n)==set(expected),'memset complete independent instruction boundaries')
    for pc,f in expected.items():guard(n,pc,**f)


def peripheral_guards(n,entry):
    covered=set()
    def g(pc,**f):guard(n,pc,**f);covered.add(pc)
    def load(pc,rd,base,off):g(pc,op='load',rd=rd,rs1=base,imm=off,width=4)
    def store(pc,src,base,off):g(pc,op='store',rs1=base,rs2=src,imm=off,width=4)
    if entry in (0x19124,0x19160):
        off=24 if entry==0x19124 else 12
        g(entry,op='beqz',rs1=11,target=entry+14);g(entry+2,op='lui',rd=14,imm=0x40021000)
        load(entry+6,15,14,off);g(entry+8,op='or',rd=10,rs1=10,rs2=15);store(entry+10,10,14,off)
        g(entry+12,op='jr',rs1=1);g(entry+14,op='lui',rd=15,imm=0x40021000);load(entry+18,14,15,off)
        g(entry+20,op='xori',rd=10,rs1=10,imm=-1);g(entry+24,op='and',rd=10,rs1=10,rs2=14)
        store(entry+26,10,15,off);g(entry+28,op='jr',rs1=1)
    elif entry==0x188e2:
        g(entry,op='addi',rd=2,rs1=2,imm=-16);store(0x188e8,1,2,12)
        g(0x188e4,op='lui',rd=15,imm=0x40012000);g(0x188ea,op='addi',rd=15,rs1=15,imm=1024)
        g(0x188ee,op='bne',rs1=10,rs2=15,target=0x1890a)
        g(0x1890a,op='lui',rd=15,imm=0x40013000);g(0x1890e,op='addi',rd=15,rs1=15,imm=-2048)
        g(0x18912,op='bne',rs1=10,rs2=15,target=0x18928)
        for pc,value in ((0x188f2,1),(0x188fc,0),(0x18916,1),(0x18920,0)):g(pc,op='li',rd=11,imm=value)
        for pc,value in ((0x188f4,512),(0x188fe,512),(0x18918,1024),(0x18922,1024)):g(pc,op='addi',rd=10,rs1=0,imm=value)
        for pc in (0x188f8,0x1891c):g(pc,op='jal',rd=1,target=0x19160)
        g(0x18906,op='jal',rd=0,target=0x19160);g(0x18926,op='jump',target=0x18902)
        for pc in (0x18902,0x18928):
            load(pc,1,2,12);g(pc+2,op='addi',rd=2,rs1=2,imm=16)
        g(0x1892c,op='jr',rs1=1)
    elif entry==0x1908c:
        g(entry,op='lui',rd=13,imm=0x40021000);load(entry+4,15,13,4)
        g(entry+6,op='lui',rd=14,imm=0xffff4000);g(entry+8,op='addi',rd=14,rs1=14,imm=-1)
        g(entry+10,op='and',rd=15,rs1=15,rs2=14);g(entry+12,op='or',rd=10,rs1=10,rs2=15)
        store(entry+14,10,13,4);g(entry+16,op='jr',rs1=1)
    elif entry in (0x18986,0x18996,0x18a98):
        off=4 if entry==0x18a98 else 8;load(entry,15,10,off)
        branch=entry+(12 if entry==0x18986 else 14);g(entry+2,op='beqz',rs1=11,target=branch)
        dest=entry+(8 if entry==0x18986 else 10)
        if entry==0x18986:
            g(entry+4,op='ori',rd=15,rs1=15,imm=1);g(branch,op='andi',rd=15,rs1=15,imm=-2)
            g(entry+14,op='jump',target=dest)
        else:
            mask=0x500000 if entry==0x18996 else 0x4000000
            g(entry+4,op='lui',rd=14,imm=mask);g(entry+8,op='or',rd=15,rs1=15,rs2=14)
            g(branch,op='lui',rd=14,imm=(~mask+1)&MASK);g(branch+4,op='addi',rd=14,rs1=14,imm=-1)
            g(branch+6,op='and',rd=15,rs1=15,rs2=14);g(branch+8,op='jump',target=dest)
        store(dest,15,10,off);g(dest+2,op='jr',rs1=1)
    elif entry==0x18a6e:
        g(entry,op='lui',rd=15,imm=0x40012000);g(entry+4,op='addi',rd=15,rs1=15,imm=1024)
        load(entry+8,14,15,8);g(entry+10,op='beqz',rs1=10,target=entry+22)
        g(entry+12,op='lui',rd=13,imm=0x800000);g(entry+16,op='or',rd=14,rs1=14,rs2=13)
        store(entry+18,14,15,8);g(entry+20,op='jr',rs1=1)
        g(entry+22,op='lui',rd=13,imm=0xff800000);g(entry+26,op='addi',rd=13,rs1=13,imm=-1)
        g(entry+28,op='and',rd=14,rs1=14,rs2=13);g(entry+30,op='jump',target=entry+18)
    elif entry==0x1892e:
        # Full stores, input reads and mask/value path, independent of profile names.
        for pc,rd,base,off in ((0x1892e,15,10,4),(0x18938,13,11,24),(0x1893c,15,11,0),
          (0x18940,13,11,28),(0x18944,13,11,4),(0x1894e,15,10,8),(0x18958,13,11,12),
          (0x1895c,15,11,16),(0x18960,13,11,8),(0x1896a,15,10,44)):load(pc,rd,base,off)
        for pc,high,low in ((0x18930,0xe0f10000,-257),(0x18950,0xfff1f000,2045),(0x1896c,0xff100000,-1)):
            g(pc,op='lui',rd=14,imm=high);g(pc+4,op='addi',rd=14,rs1=14,imm=low)
        for pc in (0x1893a,0x1895a,0x18972):g(pc,op='and',rd=14,rs1=14,rs2=15)
        for pc in (0x1893e,0x18942,0x18948,0x1895e,0x18964):g(pc,op='or',rd=15,rs1=15,rs2=13)
        for pc in (0x1894a,0x18966,0x18980):g(pc,op='or',rd=15,rs1=15,rs2=14)
        g(0x18946,op='slli',rd=13,rs1=13,imm=8);g(0x18962,op='slli',rd=13,rs1=13,imm=1)
        g(0x18974,op='load',rd=15,rs1=11,imm=20,width=1);g(0x18978,op='addi',rd=15,rs1=15,imm=-1)
        g(0x1897a,op='andi',rd=15,rs1=15,imm=255);g(0x1897e,op='slli',rd=15,rs1=15,imm=20)
        for pc,off in ((0x1894c,4),(0x18968,8),(0x18982,44)):store(pc,15,10,off)
        g(0x18984,op='jr',rs1=1)
    elif entry==0x189ae:
        for pc,op,f in (
          (0x189ae,'li',dict(rd=15,imm=9)),(0x189b0,'bgeu',dict(rs1=15,rs2=11,target=0x189fe)),
          (0x189b4,'li',dict(rd=15,imm=3)),(0x189b6,'addi',dict(rd=14,rs1=11,imm=-10)),
          (0x189ba,'mul',dict(rd=14,rs1=14,rs2=15)),(0x189c2,'li',dict(rd=15,imm=7)),
          (0x189c4,'sll',dict(rd=15,rs1=15,rs2=14)),(0x189c8,'xori',dict(rd=15,rs1=15,imm=-1)),
          (0x189cc,'and',dict(rd=15,rs1=15,rs2=16)),(0x189d0,'sll',dict(rd=13,rs1=13,rs2=14)),
          (0x189d4,'or',dict(rd=13,rs1=13,rs2=15)),(0x189d8,'li',dict(rd=15,imm=6)),
          (0x189da,'bltu',dict(rs1=15,rs2=12,target=0x18a20)),(0x189de,'li',dict(rd=15,imm=5)),
          (0x189e0,'addi',dict(rd=12,rs1=12,imm=-1)),(0x189e2,'mul',dict(rd=12,rs1=12,rs2=15)),
          (0x189e8,'li',dict(rd=15,imm=31)),(0x189ea,'sll',dict(rd=15,rs1=15,rs2=12)),
          (0x189ee,'xori',dict(rd=15,rs1=15,imm=-1)),(0x189f2,'and',dict(rd=15,rs1=15,rs2=14)),
          (0x189f4,'sll',dict(rd=12,rs1=11,rs2=12)),(0x189f8,'or',dict(rd=12,rs1=12,rs2=15))):g(pc,op=op,**f)
        for pc,rd,off in ((0x189be,16,12),(0x189e6,14,52),(0x18a04,16,16),(0x18a2e,14,48),(0x18a4e,14,44)):load(pc,rd,10,off)
        for pc,src,off in ((0x189d6,13,12),(0x189fa,12,52),(0x18a1c,13,16),(0x18a42,12,48),(0x18a62,11,44)):store(pc,src,10,off)
        g(0x18a20,op='li',rd=15,imm=12);g(0x18a22,op='bltu',rs1=15,rs2=12,target=0x18a46)
        g(0x189fe,op='li',rd=14,imm=3);g(0x18a00,op='mul',rd=14,rs1=11,rs2=14)
        g(0x18a08,op='li',rd=15,imm=7);g(0x18a0a,op='sll',rd=15,rs1=15,rs2=14)
        g(0x18a0e,op='xori',rd=15,rs1=15,imm=-1);g(0x18a12,op='and',rd=15,rs1=15,rs2=16)
        g(0x18a16,op='sll',rd=13,rs1=13,rs2=14);g(0x18a1a,op='or',rd=13,rs1=13,rs2=15)
        g(0x18a1e,op='jump',target=0x189d8)
        for pc,sub,shiftreg in ((0x18a26,-7,12),(0x18a46,-13,11)):
            g(pc,op='li',rd=15,imm=5);g(pc+2,op='addi',rd=12,rs1=12,imm=sub)
            g(pc+4,op='mul',rd=12,rs1=12,rs2=15);g(pc+10,op='li',rd=15,imm=31)
            g(pc+12,op='sll',rd=15,rs1=15,rs2=12);g(pc+16,op='xori',rd=15,rs1=15,imm=-1)
            g(pc+20,op='and',rd=15,rs1=15,rs2=14);g(pc+22,op='sll',rd=shiftreg,rs1=11,rs2=12)
            g(pc+26,op='or',rd=shiftreg,rs1=shiftreg,rs2=15)
        for pc in (0x189fc,0x18a44,0x18a64):g(pc,op='jr',rs1=1)
    else:raise RuntimeError('unknown closure body')
    check(covered==set(n),'peripheral complete independent instruction boundaries '+hex(entry))


def graph(n,entry):
    # Two static call contexts for 8520's one internal JALR. They carry no
    # target registers/memory; this is a finite CFG, not instruction execution.
    contexts=('outer','prefix') if entry==0x8520 else ('outer',)
    edges={};pending=[(entry,'outer')];seen=set()
    while pending:
        pc,ctx=pending.pop()
        if (pc,ctx) in seen:continue
        seen.add((pc,ctx));d=n[pc];op=d['op'];nextpc=pc+d['size']
        if entry==0x8520 and pc==0x8556:
            check(ctx=='outer','tail computation call context');qs=[(0x8596-4*r,'outer') for r in range(16)]
        elif entry==0x8520 and pc==0x85b6:
            check(ctx=='outer','prefix computation call context');qs=[(0x8556+4*m,'prefix') for m in range(1,16)]
        elif op=='jr':
            check(d['rs1']==1,'closure return operand')
            qs=[(0x85ba,'outer')] if entry==0x8520 and ctx=='prefix' else []
            if ctx=='prefix':check(pc==0x8596,'prefix return source')
        elif op=='jal' and d['rd']==0:
            check(entry==0x188e2 and d['target']==0x19160,'closed external tail');qs=[]
        elif op=='jump':qs=[(d['target'],ctx)]
        elif op in ('beqz','bnez','beq','bne','bltu','bgeu'):qs=[(nextpc,ctx),(d['target'],ctx)]
        else:
            check(op!='jalr','unresolved closure indirect transfer');qs=[(nextpc,ctx)]
        check(all(q in n for q,_ in qs),'closure CFG outside body')
        edges[hex(pc)+'/'+ctx]=[hex(q)+'/'+c for q,c in qs];pending.extend(qs)
    check({pc for pc,_ in seen}==set(n),'closure complete CFG byte reachability')
    if entry==0x8520:check(len(edges)==71,'memset55 outer plus16 prefix CFG nodes')
    else:
        visiting,finished=set(),set()
        def acyclic(k):
            check(k not in visiting,'peripheral CFG cycle')
            if k in finished:return
            visiting.add(k)
            for q in edges[k]:acyclic(q)
            visiting.remove(k);finished.add(k)
        acyclic(hex(entry)+'/outer')
    return edges


def body(raw,detail):
    entry,end,count,stores,writes,digest=detail;n=decode(raw,entry)
    if entry==0x8520:memset_guards(n)
    else:peripheral_guards(n,entry)
    check(len(n)==count and sum(d['op']=='store' for d in n.values())==stores,'closure body counts '+hex(entry))
    check(sorted({d['rd'] for d in n.values() if d.get('rd',0)})==writes,'closure GPR writes '+hex(entry))
    edges=graph(n,entry)
    check(len(raw)==end-entry and sha256(raw).hexdigest()==digest,'closure full body identity '+hex(entry))
    return {'start':hex(entry),'end_exclusive':hex(end),'bytes':len(raw),'sha256':digest,
        'instructions':list(n.values()),'encoded_GPR_writes':writes,
        'stores':[d for d in n.values() if d['op']=='store'],'static_call_context_CFG':edges}


def derive(app,carriers,header):
    old=parent.derive(app,carriers,header)
    bodies=[body(app[a-0x8000:b-0x8000],detail) for detail in DETAILS for a,b in [detail[:2]]]
    check(sum(b['bytes'] for b in bodies)==690 and sum(len(b['instructions']) for b in bodies)==252,'closure new body totals')
    check(sum(len(b['stores']) for b in bodies)==37,'closure new store total')
    intervals=[(d[0],d[1]) for d in DETAILS]+[(0x197f0,0x1995c),(0x18a66,0x18a6e),(0x18a8e,0x18a98)]
    check(all(hi<=otherlo or otherhi<=lo for i,(lo,hi) in enumerate(intervals) for otherlo,otherhi in intervals[i+1:]),
          'combined closure14 code intervals disjoint')
    allowed={a for a,*_ in DETAILS}|{parent.POLL,parent.RESULT}
    check(all(t in allowed for _,t in parent.CALLS),'all APP44 direct targets expanded')
    transfers=[]
    for b in bodies:
        for d in b['instructions']:
            if d['op']=='jal':
                check(d['target'] in allowed,'closure direct target outside set');transfers.append(d)
            elif d['op']=='jalr':check(d['pc'] in (0x8556,0x85b6),'closure indirect target outside bounded windows')
    return {'schema':'TSL9-APP44-closure-static-v1','profile':init.timer.PROFILE,
        'scope':'11 complete new APP bodies; prior callback and poll/result bodies revalidated; static software call closure only',
        'bodies':bodies,'direct_transfers':transfers,
        'combined_unique_code':{'bodies':14,'bytes':1072,'instructions':390,'static_store_sites':79},
        'memset':{'input':'entry destination D, full fill value V, count N',
            'tail_JALR':{'pc':'0x8556','domain':'r=0..15','targets':[hex(0x8596-4*r) for r in range(16)],
                'formula':'(0x8550+4*(15-r)+10)&~1 = 0x8596-4*r'},
            'prefix_JALR':{'pc':'0x85b6','domain':'m=D&15 in1..15 and N>15',
                'targets':[hex(0x8556+4*m) for m in range(1,16)],
                'formula':'(0x85ae+4*m-88)&~1 = 0x8556+4*m','internal_link':'0x85ba',
                'caller_RA_saved_in_T0_then_restored':True},
            'byte_store_order':'descending offsets within each prefix/tail, not a forward snapshot',
            'bulk':'four aligned SWs per16B; unsigned pointer comparison requires nonwrapping access premises',
            'conditional_output':'exactly N bytes of low8(V) into D..D+N-1 with valid ranges, D+N<=0xffffffff, intact context/code',
            'A0_encoded_nonwrite':True,'SP_GP_S_register_encoded_nonwrites':True,
            'callback_request':{'D':'callback SP+32','V':0,'N':32,'all16_alignments_partition_checked':True},
            'full_arbitrary_input_termination_or_memory_validity_proved':False},
        'nominal_helper_effects':{
            '19124(512,1)':'fresh U32[40021018] OR00000200, write same word',
            '1908c(c000)':'(fresh U32[40021004] & ffff3fff) OR0000c000',
            '188e2(40012400)':'19160(512,1), then tail19160(512,0); two fresh RMWs at4002100c',
            '1892e(base,cfg)':['base+4: (fresh word & e0f0feff) OR cfg words0/24/28 OR(word4<<8)',
                'base+8: (fresh word & fff1f7fd) OR cfg words12/16 OR(word8<<1)',
                'base+44: (fresh word & ff0fffff) OR(((U8[cfg+20]-1)&255)<<20)'],
            '1892e_callback_config_reduction':['base+4: fresh word & e0f0feff',
                'base+8: (fresh word & fff1f7fd) OR000e0000','base+44: fresh word & ff0fffff'],
            '18986(base,1)':'fresh U32[base+8] OR1',
            '18a98(base,1)':'fresh U32[base+4] OR04000000',
            '18a6e(1)':'fresh U32[40012408] OR00800000',
            '189ae(base,16,1,7)':['base+12: (fresh word & ffe3ffff) OR001c0000',
                                  'base+52: (fresh word & ffffffe0) OR00000010'],
            '18996(base,1)':'fresh U32[base+8] OR00500000',
            'unsnapshotted_reset_word':'4002100c is not among callback16 snapshot words; last reset is fresh word ANDfffffdff under nominal context'},
        'conditional_preservation':{'all_callback_software_call_targets_resolved_in_bytes':True,
            'hardware_effects_or_installed_binding_proved':False,
            'nested_extra_frame_bytes':16,'maximum_nominal_stack_depth_from_callback_entry':144,
            'leaf_helpers_S_SP_GP_nonwrites':True,'188e2_frame_RA_restore_encoded':True,
            'RAM_write_projection':'callback128B frame; 8520 writes only its32B local scratch; reset wrapper spill at callbackSP-4',
            'config_length_count_cache_no_explicit_store_with_required_bases':True,
            'premises':['matching original APP bytes and supported ISA semantics','valid nonwrapping stack/ranges and preserved code; memset D+N<=0xffffffff',
                'callback/reset frames and32B clear range disjoint from config/cache/heap objects whose preservation is claimed',
                'MMIO projected addresses map separately from RAM/config/cache/frame; effects do not invalidate them',
                'no interrupts/other writers or aliased accesses corrupt control/frame/context',
                'callback poll eventually completes; all required accesses return normally'],
            'actual_fields_or_pointer_lifetime_unconditionally_preserved':False},
        'remaining_boundaries':['actual provider binding and physical memory/ISA mapping','MMIO read/write side effects and poll completion',
            'interrupts/external writers and broader config-I/O/heap ownership'],
        'prior_reply_stores':old['resident_reply_stores'],'C_reconstruction_coverage_changed':False,
        'target_execution_or_emulation':False}


def tests(app):
    # Partition and computed-address facts only. No target memory/register model.
    for count in range(256):
        for alignment in range(16):
            prefix=16-alignment if count>15 and alignment else 0
            left=count-prefix;bulk=left//16 if left>15 else 0;tail=left%16
            check(prefix+16*bulk+tail==count and 0<=tail<=15,'memset width partition')
            if prefix:check(count>=prefix and (alignment+prefix)%16==0,'memset aligned prefix')
    for r in range(16):check((0x8550+4*(15-r)+10)&~1==0x8596-4*r,'computed tail domain')
    for m in range(1,16):check((0x85ae+4*m-88)&~1==0x8556+4*m,'computed prefix domain')
    for value in range(256):check((value|(value<<8)|(value<<16)|(value<<24))&MASK==value*0x01010101,'word byte replication')
    check((16-10)*3==18 and ((7<<18)&MASK)==0x1c0000 and (1-1)*5==0,'selected helper mask arithmetic')
    check((~0x1c0000)&MASK==0xffe3ffff and (~31)&MASK==0xffffffe0,'selected helper mask complements')
    cases=((0x8520,0x8530,'937606ff','937606fe'),(0x8520,0x8556,'6780a600','6780c600'),
      (0x8520,0x855a,'2307b700','2306b700'),(0x8520,0x85b6,'e78086fa','e780a6fa'),
      (0x8520,0x85ba,'9680','9a80'),(0x188e2,0x18906,'6f00b005','6f00d005'),
      (0x1892e,0x18974,'83c74501','83c75501'),(0x189ae,0x189d0,'b396e600','b396c600'),
      (0x189ae,0x189e0,'7d16','7916'),(0x18a6e,0x18a80,'98c7','98c3'),
      (0x1908c,0x1909a,'c8c2','c8c6'),(0x19160,0x19160,'99c5','99e5'))
    details={d[0]:d for d in DETAILS}
    for entry,pc,old,new in cases:
        detail=details[entry];raw=bytearray(app[entry-0x8000:detail[1]-0x8000]);off=pc-entry
        check(raw[off:off+len(bytes.fromhex(old))]==bytes.fromhex(old),'closure mutation source '+hex(pc))
        raw[off:off+len(bytes.fromhex(new))]=bytes.fromhex(new)
        try:body(raw,detail)
        except RuntimeError as error:check(str(error)=='closure instruction '+hex(pc),'unexpected closure mutation guard '+str(error))
        else:raise RuntimeError('closure mutation escaped')
    print('PASS: 4096 size/alignment partitions; 31 computed transfer targets; 256 byte-replication cases; 12 specified raw mutations')


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
    tests(app);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'closure exact ledger replay')
    print('PASS: 11 new complete bodies, 690 bytes/252 instructions/37 stores; combined closure14 bodies/1072 bytes')
    print('PASS: exact ledger replay; computed memset edges bounded; software callees expanded; physical binding/effects UNPROVED; NO target execution')


if __name__=='__main__':main()
