"""Full candidate allocator-release bytes/CFG only; never runs target instructions.

Shares the explicit conditional Xwchc decoder/evidence pins with timer helpers.
No synthetic linked list, device/MMIO memory, loader or provider is executed.
"""
import argparse
import json
from hashlib import sha256
from itertools import product
from pathlib import Path
import check_v4160_timer_helpers_static as timer

outer, binding = timer.outer, timer.outer.binding
ROOT, LIB, ENTRY, LENGTH = timer.ROOT, timer.LIB, 0x20000110, 212
OUT = Path(__file__).with_name('v4160-allocator-static.json')
TEMPLATE = bytes.fromhex(
 'b747024003a8c72023a607200f10000001e523a607218280b737002003ae4719'
 'b737002003a3c7188146f28763fe670883a80700636df50863eba80813878700'
 '6364e508f223216705076319e60037360020034746fa05072302e6fa37360020'
 '1305c619ce237a21239307001306c6192e97420741837aa16383c70337350020'
 '03250519630df500ea2211e9de2223a016012107be95a105cea27aa2b6879843'
 '63046702b736002083a60619630ed700762399ead6234e231843a106ae96d6a3'
 '98c37e22a1077ea2b747024099b7be86c687a9bf')
DETAILS = (
 (0x40380,0x20003194,0x2000318c,0x20002fa4,0x2000319c,0x20003190,
  'a510cc84e9173549d7f5b68da894f5b5ba9109bcd0c2601653bbdf0f5c964c50'),
 (0x403c0,0x200031e4,0x200031dc,0x20002ff4,0x200031ec,0x200031e0,
  '2f3352fb93e881b9bcd6164c8d7b02def9073df23ccb1e51d4d0fc89607ef703'))
check, sx = timer.check, timer.sx


def decode(raw,start=ENTRY):
    """Extend pinned timer decoder with RV32 integer forms in this body only."""
    nodes,off = {},0
    while off < len(raw):
        h = int.from_bytes(raw[off:off+2],'little')
        size = 2 if h&3 != 3 else 4
        check(off+size <= len(raw),'allocator partial instruction')
        chunk,pc = raw[off:off+size],start+off
        w = int.from_bytes(chunk,'little')
        d = {'pc':pc,'bytes':chunk.hex(),'size':size}
        def emit(op,**f): d.update(op=op,**f)
        if size == 4:
            opcode,rd,f,a,b = w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31
            if opcode == 0x13 and f == 0: emit('addi',rd=rd,rs1=a,imm=sx(w>>20,12))
            elif opcode == 0x23 and f in (0,1):
                emit('store',rs1=a,rs2=b,width=1 << f,imm=sx((w>>25)<<5|(w>>7&31),12))
            elif opcode == 0x63 and f == 6:
                v = (w>>31)<<12 | (w>>7&1)<<11 | (w>>25&63)<<5 | (w>>8&15)<<1
                emit('bltu',rs1=a,rs2=b,target=pc+sx(v,13))
        else:
            q,f,r = h&3,h>>13,h>>7&31
            imm = sx((h>>2&31)|(h>>7&32),6)
            if q == 1 and f == 3 and r not in (0,2): emit('lui',rd=r,imm=(imm << 12)&0xffffffff)
            elif q == 1 and f == 0 and r: emit('addi',rd=r,rs1=r,imm=imm)
            elif q == 2 and f == 0 and r and not h&0x1000: emit('slli',rd=r,rs1=r,imm=h>>2&31)
            elif q == 1 and f == 4 and h>>10&3 == 0 and not h&0x1000:
                r = 8+(h>>7&7)
                emit('srli',rd=r,rs1=r,imm=h>>2&31)
            elif q == 0 and f == 6:
                v = (h>>10&7)<<3 | (h>>6&1)<<2 | (h>>5&1)<<6
                emit('store',rs1=8+(h>>7&7),rs2=8+(h>>2&7),imm=v,width=4)
        if 'op' not in d: d = timer.decode(chunk,pc)[pc]
        nodes[pc] = d
        off += size
    return nodes


def specifications(detail):
    _,head,limit,counter,account,sentinel,_ = detail
    # Every instruction has an independent operand specification, not just a hash.
    table = [
     (0,'lui',dict(rd=15,imm=0x40024000)),
     (4,'load',dict(rd=16,rs1=15,imm=524,width=4)),
     (8,'store',dict(rs2=0,rs1=15,imm=524,width=4)),
     (12,'fence.i',{}),(16,'bnez',dict(rs1=10,target=ENTRY+24)),
     (18,'store',dict(rs2=16,rs1=15,imm=524,width=4)),(22,'jr',dict(rs1=1)),
     (24,'lui',dict(rd=15,imm=0x20003000)),
     (28,'load',dict(rd=28,rs1=15,imm=head-0x20003000,width=4)),
     (32,'lui',dict(rd=15,imm=0x20003000)),
     (36,'load',dict(rd=6,rs1=15,imm=limit-0x20003000,width=4)),
     (40,'li',dict(rd=13,imm=0)),(42,'mv',dict(rd=15,rs2=28)),
     (44,'bgeu',dict(rs1=15,rs2=6,target=ENTRY+200)),
     (48,'load',dict(rd=17,rs1=15,imm=0,width=4)),
     (52,'bltu',dict(rs1=10,rs2=15,target=ENTRY+206)),
     (56,'bltu',dict(rs1=17,rs2=10,target=ENTRY+206)),
     (60,'addi',dict(rd=14,rs1=15,imm=8)),
     (64,'bltu',dict(rs1=10,rs2=14,target=ENTRY+200)),
     (68,'load',dict(rd=12,rs1=15,imm=6,width=2,mnemonic='qk.c.lhu')),
     (70,'lui',dict(rd=14,imm=0x8000)),(72,'addi',dict(rd=14,rs1=14,imm=1)),
     (74,'bne',dict(rs1=12,rs2=14,target=ENTRY+92)),
     (78,'lui',dict(rd=12,imm=0x20003000)),
     (82,'load',dict(rd=14,rs1=12,imm=counter-0x20003000,width=1)),
     (86,'addi',dict(rd=14,rs1=14,imm=1)),
     (88,'store',dict(rs2=14,rs1=12,imm=counter-0x20003000,width=1)),
     (92,'lui',dict(rd=12,imm=0x20003000)),
     (96,'addi',dict(rd=10,rs1=12,imm=account-0x20003000)),
     (100,'load',dict(rd=11,rs1=15,imm=4,width=2,mnemonic='qk.c.lhu')),
     (102,'load',dict(rd=14,rs1=10,imm=6,width=2,mnemonic='qk.c.lhu')),
     (104,'store',dict(rs2=0,rs1=15,imm=6,width=2)),
     (108,'addi',dict(rd=12,rs1=12,imm=account-0x20003000)),
     (112,'add',dict(rd=14,rs1=14,rs2=11)),
     (114,'slli',dict(rd=14,rs1=14,imm=16)),(116,'srli',dict(rd=14,rs1=14,imm=16)),
     (118,'store',dict(rs2=14,rs1=10,imm=6,width=2,mnemonic='qk.c.sh')),
     (120,'beq',dict(rs1=15,rs2=28,target=ENTRY+158)),
     (124,'lui',dict(rd=10,imm=0x20003000)),
     (128,'load',dict(rd=10,rs1=10,imm=sentinel-0x20003000,width=4)),
     (132,'beq',dict(rs1=10,rs2=15,target=ENTRY+158)),
     (136,'load',dict(rd=10,rs1=13,imm=6,width=2,mnemonic='qk.c.lhu')),
     (138,'bnez',dict(rs1=10,target=ENTRY+158)),
     (140,'load',dict(rd=15,rs1=13,imm=4,width=2,mnemonic='qk.c.lhu')),
     (142,'store',dict(rs2=17,rs1=13,imm=0,width=4)),
     (146,'addi',dict(rd=14,rs1=14,imm=8)),
     (148,'add',dict(rd=11,rs1=11,rs2=15)),(150,'addi',dict(rd=11,rs1=11,imm=8)),
     (152,'store',dict(rs2=11,rs1=13,imm=4,width=2,mnemonic='qk.c.sh')),
     (154,'store',dict(rs2=14,rs1=12,imm=6,width=2,mnemonic='qk.c.sh')),
     (156,'mv',dict(rd=15,rs2=13)),
     (158,'load',dict(rd=14,rs1=15,imm=0,width=4)),
     (160,'beq',dict(rs1=14,rs2=6,target=ENTRY+200)),
     (164,'lui',dict(rd=13,imm=0x20003000)),
     (168,'load',dict(rd=13,rs1=13,imm=sentinel-0x20003000,width=4)),
     (172,'beq',dict(rs1=14,rs2=13,target=ENTRY+200)),
     (176,'load',dict(rd=13,rs1=14,imm=6,width=2,mnemonic='qk.c.lhu')),
     (178,'bnez',dict(rs1=13,target=ENTRY+200)),
     (180,'load',dict(rd=13,rs1=15,imm=4,width=2,mnemonic='qk.c.lhu')),
     (182,'load',dict(rd=11,rs1=14,imm=4,width=2,mnemonic='qk.c.lhu')),
     (184,'load',dict(rd=14,rs1=14,imm=0,width=4)),
     (186,'addi',dict(rd=13,rs1=13,imm=8)),(188,'add',dict(rd=13,rs1=13,rs2=11)),
     (190,'store',dict(rs2=13,rs1=15,imm=4,width=2,mnemonic='qk.c.sh')),
     (192,'store',dict(rs2=14,rs1=15,imm=0,width=4)),
     (194,'load',dict(rd=15,rs1=12,imm=6,width=2,mnemonic='qk.c.lhu')),
     (196,'addi',dict(rd=15,rs1=15,imm=8)),
     (198,'store',dict(rs2=15,rs1=12,imm=6,width=2,mnemonic='qk.c.sh')),
     (200,'lui',dict(rd=15,imm=0x40024000)),(204,'jump',dict(target=ENTRY+18)),
     (206,'mv',dict(rd=13,rs2=15)),(208,'mv',dict(rd=15,rs2=17)),
     (210,'jump',dict(target=ENTRY+44))]
    return {ENTRY+off:dict(op=op,**fields) for off,op,fields in table}


def graph(nodes):
    # BLTU has exactly the same pair of CFG successors as other conditional
    # branches. This adapter affects topology only, never operand semantics.
    topology = {p:dict(d,op='bne') if d['op']=='bltu' else d for p,d in nodes.items()}
    edges,cycles = timer.cfg(topology,ENTRY)
    edges = {int(p,16):[int(q,16) for q in qs] for p,qs in edges.items()}
    all_nodes = set(nodes)
    dom = {p:({p} if p==ENTRY else set(all_nodes)) for p in nodes}
    preds = {p:[] for p in nodes}
    for p,qs in edges.items():
        for q in qs: preds[q].append(p)
    changed = True
    while changed:
        changed = False
        for p in nodes:
            if p == ENTRY: continue
            new = {p}|set.intersection(*(dom[q] for q in preds[p]))
            if new != dom[p]: dom[p],changed = new,True
    return edges,cycles,dom


def derive(app,carriers,header):
    parents = outer.derive(app,carriers,header)
    profiles = []
    for data,parent,detail in zip(carriers,parents['profiles'],DETAILS):
        src,head,limit,counter,account,sentinel,digest = detail
        call = parent['calls'][0]
        check((int(call['target'],16),int(call['source'],16)) == (ENTRY,src),'allocator parent call mapping')
        mapping = binding.profile(data,parent['label'])
        first = {k:int(v,16) for k,v in mapping['first_copy'].items()}
        check(first['destination'] <= ENTRY and ENTRY+LENGTH <= int(mapping['first_copy_end_exclusive'],16) and
              first['source']+ENTRY-first['destination'] == src,'complete allocator first-copy mapping')
        raw = binding.take(data,src,LENGTH)
        nodes,specs = decode(raw),specifications(detail)
        check(nodes.keys()==specs.keys(),'allocator instruction boundaries')
        for p,fields in specs.items():
            check(all(nodes[p].get(k)==v for k,v in fields.items()),'allocator instruction '+hex(p-ENTRY))
        spans = tuple((n,4) for n in (28,36,82,88,96,108,128,168))
        check(outer.normalized(raw,spans)==outer.normalized(TEMPLATE,spans),'allocator full body template')
        edges,cycles,dom = graph(nodes)
        writes = sorted({d['rd'] for d in nodes.values() if d.get('rd',0)})
        check(writes==[6,10,11,12,13,14,15,16,17,28],'allocator complete GPR write set')
        check([p for p,d in nodes.items() if d['op']=='jr']==[ENTRY+22],'allocator unique return')
        check(ENTRY+18 in dom[ENTRY+22],'allocator restore dominates normal return')
        check([p for p,d in nodes.items() if d.get('rd')==16]==[ENTRY+4],'allocator saved control register stable')
        stores = [p for p,d in nodes.items() if d['op']=='store']
        heap_stores = [p for p in stores if p not in (ENTRY+8,ENTRY+18)]
        check(all({ENTRY+16,ENTRY+44,ENTRY+52,ENTRY+56,ENTRY+64} <= dom[p] for p in heap_stores),
              'allocator range guards dominate heap stores')
        check(len(cycles)==1 and {hex(ENTRY+n) for n in (44,48,52,56,206,208,210)}==set(cycles[0]),
              'allocator traversal SCC')
        # At the unique restore: A5 is control base from entry or the shared tail.
        predecessors = {p for p,qs in edges.items() if ENTRY+18 in qs}
        check(predecessors=={ENTRY+16,ENTRY+204} and nodes[ENTRY+200]['rd']==15,
              'allocator restore base origins')
        profiles.append({'label':parent['label'],'runtime_target':hex(ENTRY),'load_image_source':hex(src),
            'bytes':LENGTH,'sha256':sha256(raw).hexdigest(),'expected_sha256':digest,
            'slots':{k:hex(v) for k,v in dict(head=head,limit=limit,counter=counter,account_base=account,sentinel=sentinel).items()},
            'instructions':list(nodes.values()),'edges':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
            'cyclic_SCCs':cycles,'GPR_writes':writes,'GPR_not_written':[r for r in range(1,32) if r not in writes],
            'store_pcs':[hex(p) for p in stores],
            'return_dominators':[hex(p) for p in sorted(dom[ENTRY+22])],
            'restore_dominates_encoded_return':True,'finite_termination_proved':False,
            'outer_stack_nonalias_proved':False,'code_immutability_proved':False,'installed_binding_proved':False})
    return {'schema':'TSL9-allocator-static-v1','profile':timer.PROFILE,
        'scope':'Full static operands/CFG/dominance/write sets and host algebra; no ISA or memory model execution',
        'installed_binding_proved':False,'physical_ISA_profile_proved':False,
        'range_predicate':'cur < limit, cur <= input_A0 <= next, input_A0 >= ((cur+8)&0xffffffff)',
        'range_requires_exact_payload_start':False,'counter_condition':'U16[cur+6] == 0x8001',
        'counter_formula':'(old_U8 + 1) & 0xff',
        'account_formula_nonalias':'(old_U16 + original_matched_payload_U16_at_0x20000174 + 8*previous_merge + 8*next_merge) & 0xffff',
        'account_formula_requires_stable_nonalias_reads':True,
        'normal_private_A0_is_status':False,'outer_free_A0_after_normal_private_return':0,
        'outer_success_proves_release':False,'profiles':profiles}


def tests(app,carriers,header):
    # Mathematical facts from guarded comparisons/widths, not an ISA simulation.
    admissible = [x for x in range(0x1000,0x1021) if 0x1000 <= x <= 0x1020 and x >= 0x1008]
    check(admissible==list(range(0x1008,0x1021)),'interior and inclusive-next interval witness')
    check(sum(flag==0x8001 for flag in range(65536))==1,'exact allocation flag comparison')
    for value in range(256): check((value+1)&255 == (0 if value==255 else value+1),'counter byte wrap')
    for value,merges in product(range(65536),range(3)):
        shifted = (((value+8*merges)&0xffffffff)<<16 & 0xffffffff)>>16
        check(shifted==(value+8*merges)&65535,'U16 merge-credit modulo algebra')
    cases = (
      (44,'63fe6708','63ee6708'),(56,'63eba808','63fba808'),
      (68,'f223','d223'),(104,'23930700','23920700'),
      (142,'23a01601','23a21601'),(198,'7ea2','5ea2'),
      (206,'be86','3e84'),(18,'23a60721','23a60720'))
    for off,before,after in cases:
        changed = [bytearray(c) for c in carriers]
        source = DETAILS[0][0]+off-LIB
        b,a = bytes.fromhex(before),bytes.fromhex(after)
        check(changed[0][source:source+len(b)]==b,'allocator mutation pin')
        changed[0][source:source+len(a)] = a
        try: derive(app,changed,header)
        except RuntimeError as error: check(str(error)=='allocator instruction '+hex(off),'unexpected allocator mutation guard: '+str(error))
        else: raise RuntimeError('allocator mutation escaped')
    print('PASS: 65536 flag values; 256 byte wraps; 196608 U16 merge-credit cases; interval witness; 8 specified raw mutations')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--write',action='store_true',help='Create ledger exclusively, refusing overwrite')
    options = p.parse_args()
    app,header = binding.APP.read_bytes(),outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==outer.HEADER_HASH,'SDK header identity')
    carriers = []
    for label,folder,tail,n,digest in binding.PROFILES:
        b = (ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(b)==n and sha256(b).hexdigest()==digest,'candidate identity '+label)
        carriers.append(b)
    sources,vectors = timer.source_contract()
    ledger = derive(app,carriers,header)
    ledger['sources'],ledger['official_Xwchc_vectors'] = sources,vectors
    for profile in ledger['profiles']: check(profile['sha256']==profile['expected_sha256'],'complete allocator body identity')
    tests(app,carriers,header)
    output = (json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    if options.write:
        with OUT.open('xb') as f: f.write(output)
    else: check(OUT.read_bytes()==output,'allocator ledger exact replay')
    print('PASS: 2 complete bodies, 424 bytes; all operands/CFG; restore dominance; S/GP/SP/RA not written')
    print('PASS: ledger exact replay; installed/physical profile/outer stack nonalias UNPROVED; NO ISA/provider/MMIO execution')


if __name__=='__main__': main()
