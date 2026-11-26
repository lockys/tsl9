"""Static-only candidate slot/load-image ledger; no instruction execution.

Constant propagation covers only straight startup operands up to the first
helper call. Adjacent APP encodings are candidates, not a CFG or writer census.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
BASE,LIB,MASK = 0x8000,0x40000,0xffffffff
APP_HASH = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PROFILES = (
 ('V1.31','carrier-dec2023','0006EA66',191078,'133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'),
 ('V1.40','carrier','0006EC56',191574,'b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941'))
SLOTS = (0x40034,0x40038,0x4003c,0x40048,0x4004c,0x40050,0x40058,
         0x40060,0x40068,0x4007c,0x40080,0x4013c,0x4022c)
HELPER = bytes.fromhex('6373b60082801c419105110523aef5fec5bf')
SEED_LOOP = bytes.fromhex('63fcc5008322050023a0550011059105e3eac5fe')
FILL = bytes.fromhex('374702408327c720232607200f10000001c53307c50011e6374702402326f72082800505a30fb5fee31de5fef5b7')
COPY_HASH = '558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36'
OUT = Path(__file__).with_name('v4160-provider-binding-ledger.json')


def check(ok,message):
    if not ok: raise RuntimeError(message)


def sx(v,n): return v-(1 << n) if v & (1 << (n-1)) else v


def take(data,pc,n):
    off = pc-LIB
    check(0 <= off and off+n <= len(data),'uncaptured candidate read')
    return data[off:off+n]


def word(data,pc): return int.from_bytes(take(data,pc,4),'little')


def jal(data,pc,rd):
    w = word(data,pc)
    check(w&127 == 0x6f and w>>7&31 == rd,'candidate JAL pin')
    v = (w>>31)<<20 | (w>>12&255)<<12 | (w>>20&1)<<11 | (w>>21&1023)<<1
    return (pc+sx(v,21))&MASK


def constants(data,start,end,stop_call=False):
    """Read-only operand evaluation. No data load/store, branch or callee runs."""
    r = {0:0}
    pc,addi = start,{}
    while pc < end:
        h = int.from_bytes(take(data,pc,2),'little')
        if h&3 != 3:
            # Startup contains only C.ADDI SP / C.SWSP / C.SW in these windows.
            q,f = h&3,h>>13
            check((q,f) in ((1,0),(2,6),(0,6)),'unsupported startup compressed operand')
            if (q,f) == (1,0):
                d = h>>7&31
                imm = sx((h>>2&31)|(h>>7&32),6)
                r[d] = ((r[d]+imm)&MASK) if d in r else None
                if r[d] is None: del r[d]
            pc += 2
            continue
        w = word(data,pc)
        op,d,f,a = w&127,w>>7&31,w>>12&7,w>>15&31
        if op == 0x37: r[d] = w&0xfffff000
        elif op == 0x17: r[d] = (pc+(w&0xfffff000))&MASK
        elif op == 0x13 and f == 0:
            if a in r: r[d] = (r[a]+sx(w>>20,12))&MASK
            elif d in r: del r[d]
            addi[d] = pc
        elif op == 0x67 and f == 0 and stop_call:
            check(d == 1 and a in r and all(x in r for x in (10,11,12)),'candidate copy call operands')
            return {'call_pc':pc,'target':(r[a]+sx(w>>20,12))&MASK&~1,
                    'source':r[10],'destination':r[11],'inclusive_last':r[12],
                    'source_addi_pc':addi[10],'destination_addi_pc':addi[11]}
        else: raise RuntimeError('unsupported startup operand')
        r[0] = 0
        pc += 4
    check(not stop_call,'candidate copy call missing')
    return r


def scan_adjacent(data):
    rows = {s:[] for s in SLOTS}
    for off in range(0,len(data)-5,2):
        w = int.from_bytes(data[off:off+4],'little')
        if w&127 != 0x37 or w&0xfffff000 != LIB: continue
        base = w>>7&31
        if not base: continue
        p = off+4
        h = int.from_bytes(data[p:p+2],'little')
        if h&3 != 3:
            f = h>>13
            if h&3 or f not in (2,6) or 8+(h>>7&7) != base: continue
            displacement = (h>>10&7)<<3 | (h>>6&1)<<2 | (h>>5&1)<<6
            kind,reg = ('load' if f == 2 else 'store'),8+(h>>2&7)
        else:
            if p+4 > len(data): continue
            v = int.from_bytes(data[p:p+4],'little')
            op = v&127
            if op not in (3,0x23) or v>>12&7 != 2 or v>>15&31 != base: continue
            displacement = sx(v>>20,12) if op == 3 else sx((v>>25)<<5 | (v>>7&31),12)
            kind,reg = ('load',v>>7&31) if op == 3 else ('store',v>>20&31)
        slot = (LIB+displacement)&MASK
        if slot in rows: rows[slot].append({'lui':hex(BASE+off),'access':hex(BASE+p),'kind':kind,'register':reg})
    return rows


def profile(data,label):
    entry = jal(data,LIB,0)
    setup = constants(data,entry,entry+40)
    check(take(data,entry+40,20) == SEED_LOOP,'candidate seed-copy loop pin')
    check(word(data,entry+64) == 0x30200073,'candidate MRET pin')
    check(setup.get(3) == 0x20004000 and setup.get(2) == 0x20010000,'candidate startup GP/SP operands')
    seed = {n:setup[n] for n in (10,11,12)}
    check(seed[11] == 0x20000010 and seed[12] == 0x20000040,'candidate seed operands')
    check(take(data,seed[10],18) == HELPER,'inclusive helper semantics pin')
    initializer = jal(data,entry+60,1)
    copy = constants(data,initializer,initializer+74,stop_call=True)
    check(copy['target'] == seed[11] and copy['inclusive_last'] >= copy['destination'] and
          (copy['inclusive_last']-copy['destination'])%4 == 0,'candidate inclusive copy operands')
    end = copy['inclusive_last']+4
    # Verify complete first load-image coverage without inventing sparse bytes.
    take(data,copy['source'],end-copy['destination'])
    rows = []
    for slot in SLOTS:
        raw = word(data,slot)
        target = raw if slot == 0x40034 else raw&~1
        source = copy['source']+target-copy['destination'] if copy['destination'] <= target < end else target
        check(LIB <= source < LIB+len(data),'unmapped candidate target')
        row = {'slot':hex(slot),'raw_pointer':hex(raw),'target':hex(target),
               'source':hex(source),'mapping':'first-copy load image' if source != target else 'captured flash',
               'installed_binding_proved':False}
        if slot == 0x40034:
            text = bytearray()
            for i in range(64):
                ch = take(data,source+i,1)[0]
                if not ch: break
                text.append(ch)
            else: raise RuntimeError('candidate version terminator missing')
            row['version'] = text.decode('ascii')
        else:
            prefix = take(data,source,16)
            row['prefix16_sha256'] = sha256(prefix).hexdigest()
            if slot == 0x40048:
                check(take(data,source,46) == FILL,'candidate fill body pin')
                row.update(body_bytes=46,body_sha256=sha256(FILL).hexdigest())
            elif slot == 0x4004c:
                body = take(data,source,58)
                check(sha256(body).hexdigest() == COPY_HASH,'candidate copy body mapping pin')
                row.update(body_bytes=58,body_sha256=COPY_HASH)
        rows.append(row)
    return {'label':label,'entry':hex(entry),'initializer':hex(initializer),
        'seed_source':hex(seed[10]),'first_copy':{k:hex(v) for k,v in copy.items()},
        'first_copy_end_exclusive':hex(end),'slots':rows}


def derive(app,carriers):
    check(app[0x1ab1c-BASE:0x1ab1c-BASE+21] == b'CH32V20x_BLE_LIB_V1.3','APP operand pin')
    operand = app[0x1ab1c-BASE:0x1ab1c-BASE+21]
    profiles = [profile(data,p[0]) for p,data in zip(PROFILES,carriers)]
    for p in profiles:
        version = p['slots'][0]['version'].encode('ascii')
        p['prefix21_matches_APP_operand'] = version[:21] == operand
        p['full_string_matches_APP_literal'] = version == operand
    scans = scan_adjacent(app)
    inventory = [{'slot':hex(s),'outside_APP_file':not BASE <= s < BASE+len(app),
                  'loads':sum(r['kind']=='load' for r in scans[s]),
                  'stores':sum(r['kind']=='store' for r in scans[s]),'pairs':scans[s]} for s in SLOTS]
    return {'schema':'TSL9-provider-binding-ledger-v1','installed_binding_proved':False,
        'scope':'Two local reference candidates; adjacent APP encodings only; no target execution',
        'app':{'base':hex(BASE),'end_exclusive':hex(BASE+len(app)),'sha256':sha256(app).hexdigest(),
               'comparison_operand_address':'0x1ab1c','comparison_operand_bytes':21},
        'candidate_inputs':[{'label':p[0],'bytes':len(b),'sha256':sha256(b).hexdigest()} for p,b in zip(PROFILES,carriers)],
        'profiles':profiles,'APP_adjacent_pair_candidates':inventory,
        'fill_scope':{'body_bytes':46,'candidate_body_equal':True,
            'static_GPR_writes':['a0','a4','a5'],'control_word':'0x4002420c',
            'fence_i_present':True,'null_and_zero_count_still_touch_control':True,
            'nonempty_normal_return_A0':'end pointer, not original destination',
            'provider_or_hardware_executed':False}}


def tests(app,carriers,ledger):
    probes = 0
    for slot in SLOTS:
        imm = slot-LIB
        for store in (False,True):
            lui = (LIB | (15<<7) | 0x37).to_bytes(4,'little')
            w = ((imm>>5)<<25 | (10<<20) | (15<<15) | (2<<12) | ((imm&31)<<7) | 0x23) if store else (
                 (imm<<20) | (15<<15) | (2<<12) | (10<<7) | 3)
            mock = lui+w.to_bytes(4,'little')
            check(scan_adjacent(mock)[slot][0]['kind'] == ('store' if store else 'load'),'synthetic slot access')
            probes += 1
    for h,kind in ((0x443c,'load'),(0xc43c,'store')):
        mock = bytes.fromhex('37040400')+h.to_bytes(2,'little')
        check(scan_adjacent(mock)[0x40048][0]['kind'] == kind,'synthetic compressed slot access')
        probes += 1
    first = ledger['profiles'][0]
    copy = {k:int(v,16) for k,v in first['first_copy'].items()}
    seed_source = int(first['seed_source'],16)
    fill_source = int(next(r for r in first['slots'] if r['slot']=='0x40048')['source'],16)
    rejected = 0
    for which,message in (("operand",'APP operand pin'),('helper','inclusive helper semantics pin'),
            ('source','candidate fill body pin'),('slot','unmapped candidate target'),
            ('fill','candidate fill body pin'),('truncated','uncaptured candidate read'),
            ('destination','candidate fill body pin'),('seed_loop','candidate seed-copy loop pin'),
            ('mret','candidate MRET pin')):
        a,b = bytearray(app),bytearray(carriers[0])
        if which == 'operand': a[0x1ab1c-BASE] ^= 1
        elif which == 'helper': b[seed_source-LIB+1] ^= 0x10
        elif which in ('source','destination'):
            pc = copy[which+'_addi_pc']-LIB
            w = int.from_bytes(b[pc:pc+4],'little')+(4<<20)
            b[pc:pc+4] = w.to_bytes(4,'little')
        elif which == 'slot': b[0x48:0x4c] = (0x20004000).to_bytes(4,'little')
        elif which == 'fill': b[fill_source-LIB+36] ^= 0x10
        elif which == 'seed_loop': b[int(first['entry'],16)-LIB+41] ^= 0x10
        elif which == 'mret': b[int(first['entry'],16)-LIB+64] = 0
        else: b = b[:int(first['slots'][0]['source'],16)-LIB+5]
        try: derive(a,(b,carriers[1]))
        except RuntimeError as error:
            check(str(error) == message,'unexpected binding mutation failure: '+str(error))
            rejected += 1
        else: raise RuntimeError('binding mutation escaped')
    odd = bytearray(carriers[0])
    old = word(odd,0x40050)
    odd[0x50:0x54] = (old|1).to_bytes(4,'little')
    changed = profile(odd,'odd-pointer probe')['slots']
    row = next(x for x in changed if x['slot']=='0x40050')
    original = next(x for x in first['slots'] if x['slot']=='0x40050')
    check(row['raw_pointer'] != original['raw_pointer'] and row['target'] == original['target'] and
          row['prefix16_sha256'] == original['prefix16_sha256'],'raw pointer versus JALR normalization')
    print('PASS: %d synthetic access encodings; %d specified raw mutations rejected; odd-pointer distinction' % (probes,rejected))


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--write',action='store_true',help='Create new ledger, refusing overwrite')
    options = args.parse_args()
    app = APP.read_bytes()
    check(len(app) == 76800 and sha256(app).hexdigest() == APP_HASH,'APP identity')
    carriers = []
    for label,folder,tail,n,digest in PROFILES:
        path = ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')
        b = path.read_bytes()
        check(len(b) == n and sha256(b).hexdigest() == digest,'candidate identity '+label)
        carriers.append(b)
    ledger = derive(app,carriers)
    tests(app,carriers,ledger)
    output = (json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    if options.write:
        with OUT.open('xb') as f: f.write(output)
    else: check(OUT.read_bytes() == output,'ledger replay mismatch')
    print('PASS: 13 slot words/profile; two independently decoded startup mappings; full copy58/fill46 byte guards')
    print('PASS: ledger exact replay; V1.31 prefix21 matches but full string does not; installed provider identity NOT proved')
    print('APP adjacent-pair load/store candidates:',{r['slot']:[r['loads'],r['stores']] for r in ledger['APP_adjacent_pair_candidates']})


if __name__ == '__main__': main()
