"""Conditional LLVM-Xwchc static lookup/clear-event leaf contracts.

Only source bytes, operands, CFGs and host algebra are inspected. No resident
instruction, linked-list memory, provider, loader or MMIO is executed/emulated.
"""
import argparse
import json
import re
from hashlib import sha256,sha1
from itertools import product
from pathlib import Path
import check_v4160_cancel_provider_static as outer

ROOT,LIB,MASK = outer.ROOT,outer.LIB,outer.MASK
REF = ROOT/'analysis/wch-resident-candidate-2026-10-21/instruction-reference'
PROFILE = 'conditional-LLVM-Xwchc-RVInst16CL-GPRC'
OUT = Path(__file__).with_name('v4160-timer-helpers-static.json')
PINS = {
 'RISCVInstrInfoXwch.td':('d18a5c4d0722e20d3d0398f180931118a5125c9ada56a64d32c602ad5bd71490','6a40511deb0a8964b16dc06af61575d7cf48b9b6'),
 'xwchc-valid.s':('d4b64865497e1ecb8a8e3089c5bdc961b54cdedcdb8c3116bf679c70df683b32','da0a3e44840bfc80efc7e0ee43e73e942a7ca155'),
 '../instruction-format-reference/RISCVInstrFormatsC.td':('35bd917d2c72ddc96e5d6d1677af94479168e20d0bf1094bd4f02f9ef1ae578c','4f0bcf4359b39771fbeea7146f78f288a2baf7c1'),
 '../instruction-format-reference/RISCVRegisterInfo.td':('407eb7bbeae09bb83edbd3d274dadba65e7f066624375672a58b6317d4ba43e2','e8b7ee8a91f731e88bc7802faccafaa5cdd04e0a')}
LOOKUP = bytes.fromhex('b737002083a7871e99e33e858280ba236315b7009823e30aa7fedc47f5b7')
CLEAR = bytes.fromhex('b747024083a6c72023a607200f100000373700200347d7196372e50237360020131715000325461e93c5f5ff3a951a21f98d0ea123a6d7200145828023a6d7200d458280')
DETAILS = (
 (0x40584,0x4358a,0x200031e8,0x2000319d,0x200031e4,
  '3dbc188eb9ab2d30be1a30431a4e29a19fa7bbc0b21326dc7accd6d73913e1e8',
  '1dc75e6d3f02458afbbaebd2a0fe3656a24b3c82b9c17066f210fe3f9940c38e'),
 (0x405c4,0x43616,0x20003238,0x200031ed,0x20003234,
  'fd479d64abd9a70599e2a32ecc5b0f66fda66c4345890568f90959997842c6b6',
  '18228e82f425e14ada63b8de3a47adf76c428db874429a6a087e37584cb54066'))


def check(ok,message):
    if not ok: raise RuntimeError(message)


def sx(v,n): return v-(1 << n) if v & (1 << (n-1)) else v


def qk(raw,profile):
    check(profile == PROFILE,'explicit conditional Xwchc profile required')
    check(type(raw) is int and 0 <= raw <= 65535,'uint16 Xwchc encoding required')
    fixed = raw&0xe003
    check(fixed in (0x2000,0x2002,0xa000,0xa002),'unsupported conditional Xwchc encoding')
    store,width = bool(fixed&0x8000),2 if fixed&2 else 1
    imm = ((raw>>10&7)<<3 | (raw>>5&3)<<1) if width == 2 else (
           (raw>>12&1) | (raw>>10&3)<<3 | (raw>>5&3)<<1)
    mnemonic = ('sh' if store else 'lhu') if width == 2 else ('sb' if store else 'lbu')
    return {'op':'store' if store else 'load','width':width,'rs1':8+(raw>>7&7),
            'rs2' if store else 'rd':8+(raw>>2&7),'imm':imm,'mnemonic':'qk.c.'+mnemonic}


def encode(mnemonic,reg,base,imm):
    check(mnemonic in ('lbu','sb','lhu','sh') and 8 <= reg <= 15 and 8 <= base <= 15,
          'Xwchc register/operation domain')
    half = mnemonic in ('lhu','sh')
    check(0 <= imm <= (62 if half else 31) and (not half or imm%2 == 0),'Xwchc immediate domain')
    fixed = {'lbu':0x2000,'sb':0xa000,'lhu':0x2002,'sh':0xa002}[mnemonic]
    bits = (imm>>3&7)<<10 if half else (imm&1)<<12 | (imm>>3&3)<<10
    return fixed | (reg-8)<<2 | (base-8)<<7 | bits | (imm>>1&3)<<5


def source_contract():
    sources,texts = {},{}
    for name,(digest,blob) in PINS.items():
        raw = (REF/name).read_bytes()
        check(sha256(raw).hexdigest() == digest and
              sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == blob,'local LLVM source identity '+name)
        sources[name] = {'bytes':len(raw),'sha256':digest,'git_blob_sha1':blob}
        texts[name] = raw.decode('utf-8')
    td = texts['RISCVInstrInfoXwch.td']
    for fragment in ('let Predicates = [HasVendorXwchc]',
        'def QK_C_LBU : RVInst16CL<0b001, OPC_C0','def QK_C_SB : RVInst16CS<0b101, OPC_C0',
        'def QK_C_LHU : RVInst16CL<0b001, OPC_C2','def QK_C_SH : RVInst16CS<0b101, OPC_C2',
        'let Inst{12} = imm{0};','let Inst{11-10} = imm{4-3};',
        'let Inst{12-10} = imm{5-3};','let Inst{6-5} = imm{2-1};',
        'CompressPat<(LHU GPRC:$rd','CompressPat<(SH GPRC:$rs2'):
        check(fragment in td,'LLVM Xwchc field evidence')
    fmt = texts['../instruction-format-reference/RISCVInstrFormatsC.td']
    for fragment in ('OPC_C0 : RISCVCOpcode<"C0", 0b00>','OPC_C2 : RISCVCOpcode<"C2", 0b10>',
                     'let Inst{15-13} = funct3;','let Inst{9-7} = rs1;',
                     'let Inst{4-2} = rd;','let Inst{4-2} = rs2;'):
        check(fragment in fmt,'LLVM inherited encoding evidence')
    regs = texts['../instruction-format-reference/RISCVRegisterInfo.td']
    check('DecodeSimpleRegisterClass<RISCV::X8, 8>' in regs and
          'register must be a GPR from x8 to x15' in regs,'LLVM compact GPR evidence')
    vectors = []
    lines = texts['xwchc-valid.s'].splitlines()
    for i,line in enumerate(lines):
        m = re.fullmatch(r'# CHECK-ASM-AND-OBJ: qk\.c\.(lbu|lhu|sb|sh) s0, (\d+)\(s0\)',line)
        if not m: continue
        e = re.fullmatch(r'# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',lines[i+1])
        check(e is not None,'LLVM expected encoding vector')
        raw = int.from_bytes(bytes(int(x,16) for x in e.groups()),'little')
        d = qk(raw,PROFILE)
        check(d['mnemonic'] == 'qk.c.'+m[1] and d['rs1'] == 8 and d.get('rd',d.get('rs2')) == 8 and
              d['imm'] == int(m[2]) and encode(m[1],8,8,int(m[2])) == raw,'LLVM expected vector decode')
        vectors.append({'mnemonic':d['mnemonic'],'imm':d['imm'],'word':hex(raw),'source_line':i+1})
    check(len(vectors) == 28 and all(sum(v['mnemonic']=='qk.c.'+n for v in vectors)==7
                                   for n in ('lbu','sb','lhu','sh')),'28 official LLVM vectors')
    return sources,vectors


def decode(raw,start):
    nodes,off = {},0
    while off < len(raw):
        h = int.from_bytes(raw[off:off+2],'little')
        n = 2 if h&3 != 3 else 4
        check(off+n <= len(raw),'leaf partial instruction')
        w = int.from_bytes(raw[off:off+n],'little')
        p = start+off
        d = {'pc':p,'bytes':raw[off:off+n].hex(),'size':n,'op':None}
        def emit(op,**fields): d.update(op=op,**fields)
        if n == 2 and h&0xe003 in (0x2000,0x2002,0xa000,0xa002): d.update(qk(h,PROFILE))
        elif n == 4:
            op,rd,f,a,b = w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31
            if op == 0x37: emit('lui',rd=rd,imm=w&0xfffff000)
            elif op == 3 and f in (2,4,5): emit('load',rd=rd,rs1=a,imm=sx(w>>20,12),width={2:4,4:1,5:2}[f])
            elif op == 0x23 and f == 2: emit('store',rs1=a,rs2=b,imm=sx((w>>25)<<5|(w>>7&31),12),width=4)
            elif op == 0x13 and f == 4: emit('xori',rd=rd,rs1=a,imm=sx(w>>20,12))
            elif op == 0x13 and f == 1 and w>>25 == 0: emit('slli',rd=rd,rs1=a,imm=b)
            elif op == 0x63 and f in (0,1,7):
                v = (w>>31)<<12 | (w>>7&1)<<11 | (w>>25&63)<<5 | (w>>8&15)<<1
                emit({0:'beq',1:'bne',7:'bgeu'}[f],rs1=a,rs2=b,target=p+sx(v,13))
            elif w == 0x0000100f: emit('fence.i')
        else:
            q,f,r,b = h&3,h>>13,h>>7&31,h>>2&31
            if q == 2 and f == 4 and not h&0x1000:
                if b: emit('mv',rd=r,rs2=b)
                elif r: emit('jr',rs1=r)
            elif q == 2 and f == 4 and h&0x1000 and b: emit('add',rd=r,rs1=r,rs2=b)
            elif q == 1 and f == 2: emit('li',rd=r,imm=sx((h>>2&31)|(h>>7&32),6))
            elif q == 1 and f == 4 and (h>>10&3) == 3 and not h&0x1000 and (h>>5&3) == 3:
                r = 8+(h>>7&7)
                emit('and',rd=r,rs1=r,rs2=8+(h>>2&7))
            elif q == 0 and f == 2:
                v = (h>>10&7)<<3 | (h>>6&1)<<2 | (h>>5&1)<<6
                emit('load',rd=8+(h>>2&7),rs1=8+(h>>7&7),imm=v,width=4)
            elif q == 1 and f in (6,7):
                v = (h>>12&1)<<8 | (h>>10&3)<<3 | (h>>5&3)<<6 | (h>>3&3)<<1 | (h>>2&1)<<5
                emit('beqz' if f == 6 else 'bnez',rs1=8+(h>>7&7),target=p+sx(v,9))
            elif q == 1 and f == 5:
                v = (h>>12&1)<<11 | (h>>11&1)<<4 | (h>>9&3)<<8 | (h>>8&1)<<10 | (h>>7&1)<<6 | (h>>6&1)<<7 | (h>>3&7)<<1 | (h>>2&1)<<5
                emit('jump',target=p+sx(v,12))
        check(d['op'] is not None,'unsupported static leaf encoding '+hex(p))
        nodes[p] = d
        off += n
    return nodes


def cfg(nodes,start):
    edges = {}
    for p,d in nodes.items():
        if d['op'] == 'jr':
            check(d['rs1'] == 1,'leaf return RA operand')
            qs = []
        elif d['op'] == 'jump': qs = [d['target']]
        elif d['op'] in ('beq','bne','bgeu','beqz','bnez'): qs = [p+d['size'],d['target']]
        else: qs = [p+d['size']]
        check(all(q in nodes for q in qs),'leaf edge outside body')
        edges[p] = qs
    seen = set()
    def reach(p):
        if p in seen: return
        seen.add(p)
        for q in edges[p]: reach(q)
    reach(start)
    check(seen == set(nodes),'unreachable static leaf bytes')
    serial,indices,low,stack,on,components = 0,{},{},[],set(),[]
    def visit(p):
        nonlocal serial
        indices[p] = low[p] = serial
        serial += 1; stack.append(p); on.add(p)
        for q in edges[p]:
            if q not in indices: visit(q); low[p] = min(low[p],low[q])
            elif q in on: low[p] = min(low[p],indices[q])
        if low[p] == indices[p]:
            group = []
            while True:
                q = stack.pop(); on.remove(q); group.append(q)
                if q == p: break
            if len(group)>1 or p in edges[p]: components.append(sorted(group))
    visit(start)
    return {hex(p):[hex(q) for q in qs] for p,qs in edges.items()},[[hex(p) for p in g] for g in components]


def leaf_guard(nodes,start,offset,message,**fields):
    check(all(nodes[start+offset].get(k) == v for k,v in fields.items()),message)


def derive(app,carriers,header):
    parent = outer.derive(app,carriers,header)
    profiles = []
    for data,meta,detail in zip(carriers,parent['profiles'],DETAILS):
        src,clear,head,count,table,lh,ch = detail
        lookup_target = int(meta['calls'][1]['target'],16)
        check((lookup_target,int(meta['calls'][1]['source'],16),int(meta['calls'][2]['target'],16)) ==
              (0x20000314,src,clear),'outer-to-leaf call mapping')
        mapping = outer.binding.profile(data,meta['label'])
        first = {k:int(v,16) for k,v in mapping['first_copy'].items()}
        check(first['destination'] <= lookup_target and lookup_target+30 <= int(mapping['first_copy_end_exclusive'],16) and
              first['source']+lookup_target-first['destination'] == src,'complete lookup first-copy source mapping')
        lr,cr = outer.binding.take(data,src,30),outer.binding.take(data,clear,68)
        ln,cn = decode(lr,lookup_target),decode(cr,clear)
        lg = lambda off,msg,**f:leaf_guard(ln,lookup_target,off,msg,**f)
        cg = lambda off,msg,**f:leaf_guard(cn,clear,off,msg,**f)
        lg(0,'lookup head base',op='lui',rd=15,imm=0x20003000)
        lg(4,'lookup head pointer slot',op='load',rd=15,rs1=15,imm=head-0x20003000,width=4)
        lg(8,'lookup null branch',op='bnez',rs1=15,target=lookup_target+14)
        lg(10,'lookup returned pointer',op='mv',rd=10,rs2=15)
        lg(14,'lookup event field operands',op='load',rd=14,rs1=15,imm=2,width=2,mnemonic='qk.c.lhu')
        lg(16,'lookup exact event branch',op='bne',rs1=14,rs2=11,target=lookup_target+26)
        lg(20,'lookup task field operands',op='load',rd=14,rs1=15,imm=0,width=1,mnemonic='qk.c.lbu')
        lg(22,'lookup exact task branch',op='beq',rs1=14,rs2=10,target=lookup_target+10)
        lg(26,'lookup next field operands',op='load',rd=15,rs1=15,imm=12,width=4)
        lg(28,'lookup loop edge',op='jump',target=lookup_target+8)
        cg(0,'clear control base',op='lui',rd=15,imm=0x40024000)
        for off,op,reg in ((4,'load',13),(8,'store',0),(52,'store',13),(60,'store',13)):
            fields = {'rd' if op == 'load' else 'rs2':reg}
            cg(off,'clear control operand',op=op,rs1=15,imm=524,width=4,**fields)
        cg(12,'clear FENCE.I operand',op='fence.i')
        cg(16,'clear count base',op='lui',rd=14,imm=0x20003000)
        cg(20,'clear task-count byte',op='load',rd=14,rs1=14,imm=count-0x20003000,width=1)
        cg(24,'clear unsigned task bound',op='bgeu',rs1=10,rs2=14,target=clear+60)
        cg(28,'clear table base',op='lui',rd=12,imm=0x20003000)
        cg(32,'clear table stride',op='slli',rd=14,rs1=10,imm=1)
        cg(36,'clear table pointer slot',op='load',rd=10,rs1=12,imm=table-0x20003000,width=4)
        cg(40,'clear event complement',op='xori',rd=11,rs1=11,imm=-1)
        cg(44,'clear entry address addition',op='add',rd=10,rs1=10,rs2=14)
        cg(46,'clear event entry load',op='load',rd=14,rs1=10,imm=0,width=2,mnemonic='qk.c.lhu')
        cg(48,'clear event bit operation',op='and',rd=11,rs1=11,rs2=14)
        cg(50,'clear event entry store',op='store',rs2=11,rs1=10,imm=0,width=2,mnemonic='qk.c.sh')
        cg(56,'clear valid status',op='li',rd=10,imm=0)
        cg(64,'clear invalid status',op='li',rd=10,imm=3)
        check(outer.normalized(lr,((4,4),)) == outer.normalized(LOOKUP,((4,4),)),'lookup full body template')
        check(outer.normalized(cr,((20,4),(36,4))) == outer.normalized(CLEAR,((20,4),(36,4))),
              'clear full body template')
        le,lc = cfg(ln,lookup_target)
        ce,cc = cfg(cn,clear)
        lw = sorted({d['rd'] for d in ln.values() if d.get('rd',0)})
        cw = sorted({d['rd'] for d in cn.values() if d.get('rd',0)})
        check(lw == [10,14,15] and cw == [10,11,12,13,14,15],'leaf GPR preservation set')
        check(len(lc) == 1 and not cc,'lookup loop/clear acyclic CFG')
        check(not any(d['op'] in ('store','fence.i') for d in ln.values()),'lookup leaf has no stores/fence')
        profiles.append({'label':meta['label'],'installed_binding_proved':False,
            'lookup':{'runtime_target':hex(lookup_target),'load_image_source':hex(src),'bytes':30,
                'sha256':sha256(lr).hexdigest(),'expected_sha256':lh,'head_pointer_slot':hex(head),
                'instructions':list(ln.values()),'edges':le,'cyclic_SCCs':lc,'GPR_writes':lw,
                'predicate':'U16[node+2] == full_A1, then U8[node+0] == full_A0; first match',
                'next':'U32[node+12], without pointer-bit normalization','return':'matched node or zero',
                'finite_termination_proved':False},
            'clear_event':{'flash_target':hex(clear),'bytes':68,'sha256':sha256(cr).hexdigest(),
                'expected_sha256':ch,'task_count_byte':hex(count),'event_table_pointer_slot':hex(table),
                'instructions':list(cn.values()),'edges':ce,'cyclic_SCCs':cc,'GPR_writes':cw,
                'invalid_task_condition':'full_unsigned_A0 >= U8[task_count_byte]',
                'valid_entry_address':'(U32[event_table_pointer_slot] + 2*full_unsigned_A0) & 0xffffffff',
                'entry_value_formula':'old_U16 & (~input_A1 & 0xffff)',
                'normal_return_valid':0,'normal_return_invalid':3,
                'control':'read/save 0x4002420c, write0, FENCE.I BEFORE task check; restore before encoded RET'},
            'outer_stop_live_S_preservation_supported_by_leaf_write_sets':True,
            'deallocate_private_helper_proved':False})
    return {'schema':'TSL9-timer-leaf-static-v1','profile':PROFILE,
        'scope':'Static source/operand/CFG/algebra only; no target ISA, linked-list or MMIO execution',
        'installed_binding_proved':False,'physical_ISA_profile_proved':False,'profiles':profiles}


def tests(app,carriers,header,ledger,vectors):
    roundtrips = 0
    for m in ('lbu','sb','lhu','sh'):
        for reg,base,value in product(range(8,16),range(8,16),range(32)):
            imm = value*2 if m in ('lhu','sh') else value
            d = qk(encode(m,reg,base,imm),PROFILE)
            check((d['mnemonic'],d.get('rd',d.get('rs2')),d['rs1'],d['imm']) ==
                  ('qk.c.'+m,reg,base,imm),'Xwchc operand roundtrip')
            roundtrips += 1
    target_words = (0x23ba,0x2398,0x211a,0xa10e)
    invalid,different = 0,0
    for raw in target_words:
        before = qk(raw,PROFILE)
        for bit in range(16):
            try: changed = qk(raw^(1 << bit),PROFILE)
            except RuntimeError as error:
                check(str(error) == 'unsupported conditional Xwchc encoding','unexpected decoder mutation error')
                invalid += 1
            else:
                check(changed != before,'Xwchc mutation did not alter operands')
                different += 1
    check((invalid,different) == (12,52),'four-word single-bit mutation classification')
    for profile in (None,'RV32IMC','unproved-other-profile'):
        try: qk(0x23ba,profile)
        except RuntimeError as error: check(str(error) == 'explicit conditional Xwchc profile required','profile guard')
        else: raise RuntimeError('profile requirement escaped')
    for raw in (-1,65536,True,'0x23ba',1.25):
        try: qk(raw,PROFILE)
        except RuntimeError as error: check(str(error) == 'uint16 Xwchc encoding required','uint16 guard')
        else: raise RuntimeError('uint16 requirement escaped')
    valid = sum(task < count for task,count in product(range(256),repeat=2))
    check(valid == 32640 and 65536-valid == 32896,'task-count unsigned interval algebra')
    for task,count in product((256,257,0x80000001,MASK),range(256)):
        check(not task < count,'high-word task cannot pass byte count')
    for old,index in product(range(65536),range(15)):
        mask = 1 << index
        new = old & (~mask & 0xffff)
        check(not new&mask and not (new^old)&(~mask&0xffff),'U16 event-mask algebra')
    cases = (
        ('lookup',14,'ba23','da23','lookup event field operands'),
        ('lookup',20,'9823','9833','lookup task field operands'),
        ('lookup',26,'dc47','9c47','lookup next field operands'),
        ('lookup',16,'6315b700','6305b700','lookup exact event branch'),
        ('clear',20,'0347d719','0357d719','clear task-count byte'),
        ('clear',32,'13171500','13172500','clear table stride'),
        ('clear',50,'0ea1','2ea1','clear event entry store'))
    for role,offset,old,new,message in cases:
        cs = [bytearray(b) for b in carriers]
        source = DETAILS[0][0 if role == 'lookup' else 1]+offset-LIB
        a,b = bytes.fromhex(old),bytes.fromhex(new)
        check(cs[0][source:source+len(a)] == a,'timer-leaf mutation pin')
        cs[0][source:source+len(a)] = b
        try: derive(app,cs,header)
        except RuntimeError as error: check(str(error) == message,'unexpected timer mutation error: '+str(error))
        else: raise RuntimeError('timer-leaf mutation escaped')
    print('PASS: %d saved LLVM vectors; %d operand roundtrips; 64 bit mutations (12 invalid/52 different); profile/type guards' % (len(vectors),roundtrips))
    print('PASS: 65536 byte task/count pairs; 1024 high-word rejects; 983040 U16/mask algebra cases; 7 specified raw mutations')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true',help='Create a new ledger, refusing overwrite')
    options = parser.parse_args()
    app,header = outer.binding.APP.read_bytes(),outer.HEADER.read_bytes()
    check(len(app) == 76800 and sha256(app).hexdigest() == outer.binding.APP_HASH,'APP identity')
    check(len(header) == 243435 and sha256(header).hexdigest() == outer.HEADER_HASH,'SDK header identity')
    carriers = []
    for label,folder,tail,n,digest in outer.binding.PROFILES:
        b = (ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(b) == n and sha256(b).hexdigest() == digest,'candidate identity '+label)
        carriers.append(b)
    sources,vectors = source_contract()
    ledger = derive(app,carriers,header)
    ledger['sources'],ledger['official_vectors'] = sources,vectors
    for p in ledger['profiles']:
        for k in ('lookup','clear_event'): check(p[k]['sha256'] == p[k]['expected_sha256'],'complete leaf body identity')
    tests(app,carriers,header,ledger,vectors)
    output = (json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    if options.write:
        with OUT.open('xb') as f: f.write(output)
    else: check(OUT.read_bytes() == output,'timer helper ledger exact replay')
    print('PASS: four complete leaf bodies, 196 bytes; lookup cycle and clear-event bounds; selected-profile GPR preservation')
    print('PASS: ledger exact replay; installed/physical-profile identity UNPROVED; NO ISA/provider/MMIO execution')


if __name__ == '__main__': main()
