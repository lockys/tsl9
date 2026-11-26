"""Static operand/CFG ledger for 18BA2. No ISA, provider or MMIO execution.

The decoder inventories instructions and graph edges only. Address/packing
formulae are host algebra guarded by original operands, not a device model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
BASE,START,END,MASK = 0x8000,0x18ba2,0x18ca4,0xffffffff
APP_HASH = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BODY_HASH = 'a7740d7785b0ab0def54148e8d56242da4341de1d4041a0ee7fffceed37338cc'
PRODUCER_HASH = 'ef3f4a2c364f1fcce5c826f7efe7fe6985d7d4ee06576b01aa677d39344eaa5a'
OUT = Path(__file__).with_name('v4160-18ba2-static.json')


def check(ok,message):
    if not ok: raise RuntimeError(message)


def sx(v,n): return v-(1 << n) if v & (1 << (n-1)) else v


def take(data,pc,n):
    off = pc-BASE
    check(0 <= off and off+n <= len(data),'static read outside captured APP')
    return data[off:off+n]


def decode(data,start=START,end=END):
    """Decode a closed, small RV32IMC vocabulary; never evaluate registers."""
    nodes = {}
    pc = start
    while pc < end:
        h = int.from_bytes(take(data,pc,2),'little')
        n = 2 if h&3 != 3 else 4
        check(pc+n <= end,'partial static instruction')
        w = int.from_bytes(take(data,pc,n),'little')
        d = {'pc':pc,'size':n,'bytes':take(data,pc,n).hex(),'op':None}
        def emit(op,**fields): d.update(op=op,**fields)
        if n == 4:
            op,rd,f,a,b = w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31
            imm = sx(w>>20,12)
            if op == 0x37: emit('lui',rd=rd,imm=w&0xfffff000)
            elif op == 0x13 and f in (0,4,6,7):
                emit({0:'addi',4:'xori',6:'ori',7:'andi'}[f],rd=rd,rs1=a,imm=imm)
            elif op == 3 and f in (2,4,5): emit('load',rd=rd,rs1=a,imm=imm,width={2:4,4:1,5:2}[f])
            elif op == 0x23 and f in (0,1,2):
                emit('store',rs1=a,rs2=b,imm=sx((w>>25)<<5 | (w>>7&31),12),width={0:1,1:2,2:4}[f])
            elif op == 0x33 and w>>25 == 0 and f in (1,6):
                emit('sll' if f == 1 else 'or',rd=rd,rs1=a,rs2=b)
            elif op == 0x63 and f == 1:
                off = (w>>31)<<12 | (w>>7&1)<<11 | (w>>25&63)<<5 | (w>>8&15)<<1
                emit('bne',rs1=a,rs2=b,target=pc+sx(off,13))
        else:
            q,f,rd,b = h&3,h>>13,h>>7&31,h>>2&31
            imm = sx((h>>2&31)|(h>>7&32),6)
            if q == 1 and f == 0: emit('addi',rd=rd,rs1=rd,imm=imm)
            elif q == 1 and f == 2: emit('li',rd=rd,imm=imm)
            elif q == 2 and f == 0 and not h&0x1000: emit('slli',rd=rd,rs1=rd,imm=b)
            elif q == 1 and f == 4 and (h>>10&3) == 2:
                r = 8+(h>>7&7)
                emit('andi',rd=r,rs1=r,imm=imm)
            elif q == 1 and f == 4 and (h>>10&3) == 3 and not h&0x1000 and (h>>5&3) in (2,3):
                r = 8+(h>>7&7)
                emit('or' if (h>>5&3) == 2 else 'and',rd=r,rs1=r,rs2=8+(h>>2&7))
            elif q == 2 and f == 4 and h&0x1000 and b:
                emit('add',rd=rd,rs1=rd,rs2=b)
            elif q == 2 and f == 4 and not h&0x1000 and not b and rd:
                emit('jr',rs1=rd)
            elif q == 0 and f == 2:
                off = (h>>10&7)<<3 | (h>>6&1)<<2 | (h>>5&1)<<6
                emit('load',rd=8+(h>>2&7),rs1=8+(h>>7&7),imm=off,width=4)
            elif q == 1 and f in (6,7):
                off = (h>>12&1)<<8 | (h>>10&3)<<3 | (h>>5&3)<<6 | (h>>3&3)<<1 | (h>>2&1)<<5
                emit('beqz' if f == 6 else 'bnez',rs1=8+(h>>7&7),target=pc+sx(off,9))
            elif q == 1 and f == 5:
                off = (h>>12&1)<<11 | (h>>11&1)<<4 | (h>>9&3)<<8 | (h>>8&1)<<10 | (h>>7&1)<<6 | (h>>6&1)<<7 | (h>>3&7)<<1 | (h>>2&1)<<5
                emit('jump',target=pc+sx(off,12))
        check(d['op'] is not None,'unsupported static encoding at '+hex(pc))
        nodes[pc] = d
        pc += n
    return nodes


def graph(nodes):
    edges = {}
    for p,d in nodes.items():
        if d['op'] == 'jr':
            check(d['rs1'] == 1,'static return must use RA')
            nexts = []
        elif d['op'] == 'jump': nexts = [d['target']]
        elif d['op'] in ('bne','bnez','beqz'): nexts = [p+d['size'],d['target']]
        else: nexts = [p+d['size']]
        check(all(x in nodes for x in nexts),'static edge outside complete body')
        edges[p] = nexts
    paths = []
    def visit(p,path):
        check(p not in path,'unexpected static CFG cycle')
        path = path+[p]
        if not edges[p]: paths.append(path)
        for q in edges[p]: visit(q,path)
    visit(START,[])
    check(set().union(*(set(p) for p in paths)) == set(nodes),'unreachable static bytes')
    return edges,paths


def guards(data,nodes):
    def at(pc,message,**fields):
        check(all(nodes[pc].get(k) == v for k,v in fields.items()),message)
    at(0x18ba2,'MMIO base operand',op='lui',rd=14,imm=0x40006000)
    at(0x18ba6,'MMIO base operand',op='addi',rd=14,rs1=14,imm=1024)
    for p in (0x18c08,0x18c20,0x18c3c,0x18c4a):
        at(p,'reloaded MMIO base operand',op='lui',rd=15,imm=0x40006000)
    for p in (0x18c0c,0x18c24):
        at(p,'reloaded MMIO base operand',op='addi',rd=15,rs1=15,imm=1024)
    for p,target in ((0x18c88,0x18bfe),(0x18c90,0x18c18),(0x18ca2,0x18c34)):
        at(p,'post-RET join target',op='jump',target=target)
    at(0x18bae,'record index operand',op='load',rd=15,rs1=10,imm=10,width=1)
    at(0x18bb2,'mask constant operand',op='li',rd=16,imm=1)
    at(0x18bc0,'RV32 mask shift operand',op='sll',rd=12,rs1=16,rs2=15)
    for p in (0x18bdc,0x18c66): at(p,'unmasked table-index stride',op='slli',rd=15,rs1=15,imm=3)
    for p in (0x18be8,0x18c72): at(p,'table base addition',op='add',rd=15,rs1=15,rs2=14)
    for p in (0x18bf4,0x18c7e): at(p,'table word0 store',op='store',rs1=15,rs2=11,imm=576,width=4)
    at(0x18c00,'table word1 store',op='store',rs1=15,rs2=14,imm=580,width=4)
    for p,reg,off,width in ((0x18bce,11,12,1),(0x18c04,14,11,1),(0x18c1c,14,8,2),(0x18c34,14,16,4)):
        at(p,'record branch field operand',op='load',rd=reg,rs1=10,imm=off,width=width)
    for p,op,r,target in ((0x18bd2,'bnez',11,0x18c5a),(0x18c10,'bnez',14,0x18c8a),(0x18c28,'bnez',14,0x18c92)):
        at(p,'branch polarity/target operand',op=op,rs1=r,target=target)
    for p,a,b,target in ((0x18c5a,11,16,0x18c04),(0x18c94,14,13,0x18c34),(0x18c38,14,15,0x18c4a)):
        at(p,'exact-one branch operand',op='bne',rs1=a,rs2=b,target=target)
    for p,r in ((0x18c36,15),(0x18c92,13)): at(p,'exact-one constant operand',op='li',rd=r,imm=1)
    # All direct MMIO load/store operands; table stores were checked above.
    expected = {
        0x18baa:('load',14,512),0x18bb8:('store',14,512),
        0x18bbc:('load',14,540),0x18bca:('store',14,540),
        0x18bd4:('load',14,524),0x18be0:('store',14,524),
        0x18c12:('load',15,516),0x18c18:('store',15,516),
        0x18c2a:('load',15,532),0x18c30:('store',15,532),
        0x18c40:('load',15,1564),0x18c46:('store',15,1564),
        0x18c4e:('load',15,1536),0x18c54:('store',15,1536),
        0x18c5e:('load',14,524),0x18c6a:('store',14,524),
        0x18c8a:('load',15,516),0x18c98:('load',15,532),0x18c9e:('store',15,532)}
    data_regs = {0x18baa:13,0x18bb8:13,0x18bbc:11,0x18bca:11,
                 0x18bd4:11,0x18be0:11,0x18c12:14,0x18c18:14,
                 0x18c2a:14,0x18c30:13,0x18c40:14,0x18c46:12,
                 0x18c4e:14,0x18c54:14,0x18c5e:11,0x18c6a:11,
                 0x18c8a:14,0x18c98:14,0x18c9e:14}
    for p,(op,r,off) in expected.items():
        fields = {'rd' if op == 'load' else 'rs2':data_regs[p]}
        at(p,'direct MMIO access operand',op=op,rs1=r,imm=off,width=4,**fields)
    for p,off,rd in ((0x18bd8,2,16),(0x18be4,6,11),(0x18bea,4,14),(0x18bf8,0,11),
                     (0x18c62,2,16),(0x18c6e,0,11),(0x18c74,4,14),(0x18c84,6,11)):
        at(p,'halfword packing source',op='load',rd=rd,rs1=10,imm=off,width=2)
    for p,r in ((0x18bee,11),(0x18bfc,14),(0x18c78,11),(0x18c82,14)):
        at(p,'halfword packing shift',op='slli',rd=r,rs1=r,imm=16)
    for p,op,r,a,b in ((0x18bf0,'or',11,11,16),(0x18bfe,'or',14,14,11),
                       (0x18c7a,'or',11,11,16),(0x18bc8,'and',11,11,13),
                       (0x18bde,'and',11,11,13),(0x18c68,'or',11,11,12),
                       (0x18c16,'and',14,14,13),(0x18c8e,'or',14,14,12),
                       (0x18c2e,'and',13,13,14),(0x18c9c,'or',14,14,12),
                       (0x18c44,'or',12,12,14)):
        at(p,'bit/packing combination operand',op=op,rd=r,rs1=a,rs2=b)
    at(0x18bb4,'control set-bit operand',op='ori',rd=13,rs1=13,imm=1)
    at(0x18bc4,'clear-mask complement operand',op='xori',rd=13,rs1=12,imm=-1)
    at(0x18c52,'control clear-bit operand',op='andi',rd=14,rs1=14,imm=-2)
    # Caller epilogues are pinned independently of the callee, with no A0 writes.
    for p,raw in ((0x1298e,'ba502a549a540a59fa496a4a4d618280'),
                  (0x129be,'b65065618280'),(0x12ae2,'f65009618280')):
        check(take(data,p,len(bytes.fromhex(raw))) == bytes.fromhex(raw),'caller return byte pin')
    check(sha256(take(data,0x1293c,0x4e)).hexdigest() == PRODUCER_HASH,'14-record producer pin')


def formula(record):
    """Pure record algebra; returns intended addresses/data, no MMIO state."""
    check(len(record) == 20,'static record size')
    h = [int.from_bytes(record[i:i+2],'little') for i in range(0,8,2)]
    index,mode,scale = record[10],record[11],record[12]
    fifo,enable = int.from_bytes(record[8:10],'little'),int.from_bytes(record[16:20],'little')
    words = [h[1]|h[3]<<16,h[0]|h[2]<<16] if scale == 0 else (
             [h[1]|h[0]<<16,h[3]|h[2]<<16] if scale == 1 else None)
    return {'index':index,'mask':hex(1 << (index&31)),
        'data_addresses':[hex(0x40006640+8*index+i) for i in (0,4)] if words is not None else [],
        'data_words':[hex(w) for w in words] if words is not None else [],
        'scale_bit':'clear' if scale == 0 else 'set' if scale == 1 else 'no access',
        'mode_bit':'set' if mode else 'clear',
        'fifo_bit':'clear' if fifo == 0 else 'set' if fifo == 1 else 'no access',
        'late_enable_bit_set':enable == 1}


def derive(data):
    nodes = decode(data)
    guards(data,nodes)
    edges,paths = graph(nodes)
    writes = sorted({d['rd'] for d in nodes.values() if d.get('rd',0)})
    check(writes == list(range(11,17)),'static GPR preservation set')
    check(all(d['rs1'] != 10 for d in nodes.values() if d['op'] == 'store'),'unexpected record store')
    check(len(paths) == 36,'static branch-path census')
    sets = []
    for selector,source,n in ((0,0x19ca8,96),(1,0x19d08,94),(2,0x19d68,106)):
        work = take(data,source,n)+bytes(112-n)  # explicit successful fill/copy premise
        records = []
        for index in range(14):
            values = [int.from_bytes(work[index*8+2*j:index*8+2*j+2],'little') for j in range(4)]
            record = b''.join(((v<<5)&0xffff).to_bytes(2,'little') for v in values)
            record += bytes([0,0,index,1])+bytes(4)+(1).to_bytes(4,'little')
            row = formula(record)
            check(row['scale_bit'] == 'clear' and row['mode_bit'] == 'set' and
                  row['fifo_bit'] == 'clear' and row['late_enable_bit_set'],'producer branch contract')
            records.append({'record':record.hex(),**row})
        sets.append({'selector':selector,'source':hex(source),'source_bytes':n,
                     'premise':'112-byte zero fill, then exact n-byte copy','records':records})
    return {'schema':'TSL9-18BA2-static-v1','scope':'Operand/CFG/address analysis only; no ISA or MMIO execution',
        'app_sha256':sha256(data).hexdigest(),'body_sha256':sha256(take(data,START,END-START)).hexdigest(),
        'body_bytes':END-START,'instructions':list(nodes.values()),
        'edges':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'path_count':len(paths),'path_memory_sites':[[hex(p) for p in path if nodes[p]['op'] in ('load','store')] for path in paths],
        'GPR_writes':writes,'A0_RA_SP_GP_S_preserved_on_normal_return':True,
        'control_address':'0x40006600','scale_address':'0x4000660c','mode_address':'0x40006604',
        'fifo_address':'0x40006614','early_clear_late_enable_address':'0x4000661c',
        'control_order':'fresh read/set bit0 near entry; separate fresh read/clear bit0 before RET',
        'table_address_formula':'0x40006640 + 8*U8(record+10), then +4',
        'mask_formula':'1 << (U8(record+10) & 31); table index is NOT masked',
        'return_A0_if_all_calls_return_normally':{'direct128FE':'entry_SP - 164',
            'selector1_or2_12AD0':'entry_SP - 292','selector0_12AD0':'entry_SP - 404'},
        'record_sets':sets}


def tests(data,ledger):
    probes = 0
    for index in range(256):
        r = bytearray.fromhex('1111222233334444000000010000000001000000')
        r[10] = index
        row = formula(r)
        check(row['mask'] == hex(1 << (index%32)) and
              row['data_addresses'] == [hex(0x40006640+8*index),hex(0x40006644+8*index)] and
              row['data_words'] == ['0x44442222','0x33331111'],'index/packing algebra')
        probes += 1
    for scale,expected in ((0,['0x44442222','0x33331111']),(1,['0x11112222','0x33334444']),(2,[]),(255,[])):
        r[12] = scale
        check(formula(r)['data_words'] == expected,'scale exact-zero/one algebra')
    for scale in range(256):
        r[12] = scale
        check(formula(r)['scale_bit'] == ('clear' if scale == 0 else 'set' if scale == 1 else 'no access'),
              'scale byte classification algebra')
    for mode in range(256):
        r[11] = mode
        check(formula(r)['mode_bit'] == ('set' if mode else 'clear'),'mode byte classification algebra')
    for fifo in range(65536):
        r[8:10] = fifo.to_bytes(2,'little')
        check(formula(r)['fifo_bit'] == ('clear' if fifo == 0 else 'set' if fifo == 1 else 'no access'),
              'FIFO halfword classification algebra')
    for enable in (0,1,2,255,256,257,0x80000001,MASK):
        r[16:20] = enable.to_bytes(4,'little')
        check(formula(r)['late_enable_bit_set'] == (enable == 1),'full-word enable algebra')
    mutations = (
        (0x18bc0,'3316f800','3316e800','RV32 mask shift operand'),
        (0x18bdc,'8e07','8a07','unmasked table-index stride'),
        (0x18bce,'8345c500','8345d500','record branch field operand'),
        (0x18c10,'2def','2dcf','branch polarity/target operand'),
        (0x18bea,'03574500','83564500','halfword packing source'),
        (0x18c46,'23aec760','23aed760','direct MMIO access operand'),
        (0x18c58,'8280','8282','static return must use RA'),
        (0x12944,'3949','3d49','14-record producer pin'))
    for pc,old,new,message in mutations:
        off = pc-BASE
        a,b = bytes.fromhex(old),bytes.fromhex(new)
        check(data[off:off+len(a)] == a,'static mutation pin')
        m = bytearray(data)
        m[off:off+len(a)] = b
        try: derive(m)
        except RuntimeError as error:
            check(str(error) == message,'unexpected static mutation failure: '+str(error))
        else: raise RuntimeError('static mutation escaped')
    check(ledger['GPR_writes'] == [11,12,13,14,15,16],'preservation ledger')
    print('PASS: algebra probes: 256 index, 256 scale, 256 mode, 65536 FIFO, 8 full-word enable; 8 specified raw mutations')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true',help='Create new ledger, refusing overwrite')
    options = parser.parse_args()
    data = APP.read_bytes()
    check(len(data) == 76800 and sha256(data).hexdigest() == APP_HASH,'APP identity')
    check(sha256(take(data,START,END-START)).hexdigest() == BODY_HASH,'complete body identity')
    ledger = derive(data)
    tests(data,ledger)
    output = (json.dumps(ledger,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if options.write:
        with OUT.open('xb') as f: f.write(output)
    else: check(OUT.read_bytes() == output,'static ledger exact replay')
    print('PASS: %d complete-body instructions; 36 closed CFG paths; GPR writes only A1..A6; no calls' % len(ledger['instructions']))
    print('PASS: 42 producer-record contracts; 14 bounded indices; exact ledger replay; NO ISA/provider/MMIO execution')


if __name__ == '__main__': main()
