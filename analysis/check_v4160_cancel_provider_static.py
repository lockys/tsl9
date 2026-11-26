"""Static-only reference contracts for slots4005C/40068; installed identity unknown.

Reads pinned local carriers/header and original APP. No candidate instruction,
MMIO, private callee or provider is executed or mapped as an executable model.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_provider_binding_ledger as binding

ROOT,BASE,LIB,MASK = binding.ROOT,binding.BASE,binding.LIB,binding.MASK
HEADER = ROOT/'analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h'
HEADER_HASH = '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c'
OUT = Path(__file__).with_name('v4160-cancel-provider-static.json')
FREE = bytes.fromhex('411122c426c23744024006c68324c420232604200f10000009e9232694201545b24022449244410182800347e5ff9307f00f6306f700232694201145d5b797d0fb1fe78080f1014523269420d1bf')
STOP = bytes.fromhex('011122cc4ac84ec6b747024006ce26ca83a9c7202a892e8423a607200f10000097d0fb1fe780c094aa8419c123110500a2854a857d36b737002083c7c71963992701b737002003d7c71d598c239e871cb747024023a63721014591e01945f2406244d2444249b24905618280')
DETAILS = (
    (0x431ba,0x439a8,0x2000319c,0x200031dc,
     '45e504a67ace2215263cfbaddc9d99a0cc0c1714f8289f19889a9573e7c520b5',
     'b7039b31b68bfe6aeae2e453d4b159efab81edade95c9f3079a56898444ff098'),
    (0x43246,0x43a34,0x200031ec,0x2000322c,
     '3db0d77ac9e5b56d1b327b3c3576a91acd4895f9d752b337e06b44b07758dfa7',
     'ef68aa1e9331e08e48880f35aa3b1d0ec25d2f781fa60289d78a07330beec866'))


def check(ok,message):
    if not ok: raise RuntimeError(message)


def sx(v,n): return v-(1 << n) if v & (1 << (n-1)) else v


def w(raw,off):
    check(0 <= off and off+4 <= len(raw),'static operand read range')
    return int.from_bytes(raw[off:off+4],'little')


def upper(raw,off,rd):
    v = w(raw,off)
    check(v&127 == 0x37 and v>>7&31 == rd,'candidate LUI base operand')
    return v&0xfffff000


def load(raw,off,rd,base,width,message):
    v = w(raw,off)
    check(v&127 == 3 and v>>7&31 == rd and v>>15&31 == base and
          v>>12&7 == {1:4,2:5,4:2}[width],message)
    return sx(v>>20,12)


def store(raw,off,src,base,width,message):
    v = w(raw,off)
    check(v&127 == 0x23 and v>>20&31 == src and v>>15&31 == base and
          v>>12&7 == {1:0,2:1,4:2}[width],message)
    return sx((v>>25)<<5 | (v>>7&31),12)


def auipc_call(raw,off,pc):
    a,b = w(raw,off),w(raw,off+4)
    check(a&127 == 0x17 and a>>7&31 == 1 and b&127 == 0x67 and b>>7&31 == 1 and
          b>>15&31 == 1 and b>>12&7 == 0,'candidate private-call encoding')
    return (pc+(a&0xfffff000)+sx(b>>20,12))&MASK&~1


def cjal(raw,off,pc):
    v = int.from_bytes(raw[off:off+2],'little')
    check(v&3 == 1 and v>>13 == 1,'candidate clear-event C.JAL')
    imm = (v>>12&1)<<11 | (v>>11&1)<<4 | (v>>9&3)<<8 | (v>>8&1)<<10 | (v>>7&1)<<6 | (v>>6&1)<<7 | (v>>3&7)<<1 | (v>>2&1)<<5
    return pc+sx(imm,12)


def normalized(raw,spans):
    b = bytearray(raw)
    for off,n in spans: b[off:off+n] = bytes(n)
    return bytes(b)


def li(raw,off,rd):
    v = int.from_bytes(raw[off:off+2],'little')
    check(v&3 == 1 and v>>13 == 2 and v>>7&31 == rd,'candidate return LI operand')
    return sx((v>>2&31)|(v>>7&32),6)&MASK


def header_contract(raw):
    # Header has non-UTF-8 comments. Parse only ASCII code patterns from bytes;
    # never transcode or normalize the source file.
    def match(pattern,message):
        m = re.search(pattern,raw,re.M)
        check(m is not None,message)
        return m
    flash = int(match(rb'^\s*#define\s+LIB_FLASH_BASE_ADDRESSS\s+(0x[0-9A-Fa-f]+)',
                      'header flash base').group(1),16)
    offset = int(match(rb'^\s*#define\s+FUNCITON_BASE_ADDRESSS\s+\(LIB_FLASH_BASE_ADDRESSS\s*\+\s*(0x[0-9A-Fa-f]+)\)',
                       'header JT base').group(1),16)
    match(rb'^\s*#define\s+BLE_LIB_JT\(n\)\s+\(\*\(uint32_t\*\)\(\s*FUNCITON_BASE_ADDRESSS\s*\+\s*n\*4\s*\)\)',
          'header JT stride')
    check((flash,offset) == (LIB,0x34),'header JT address operands')
    types = {}
    for name,bits in ((b'bStatus_t',8),(b'tmosTaskID',8),(b'tmosEvents',16)):
        m = match(rb'^\s*typedef\s+uint(8|16|32)_t\s+'+name+rb'\s*;','header type width')
        check(int(m.group(1)) == bits,'header type width')
        types[name.decode('ascii')] = bits
    apis = []
    for name,index,slot in ((b'tmos_clear_event',8,0x40054),(b'tmos_stop_task',10,0x4005c),
                            (b'tmos_msg_deallocate',13,0x40068)):
        line = match(rb'^\s*#define\s+'+name+rb'\s+([^\r\n]+)','header API macro').group(1)
        m = re.search(rb'BLE_LIB_JT\(\s*(\d+)\s*\)',line)
        check(m is not None and int(m.group(1)) == index,'header JT API index')
        check(flash+offset+4*index == slot,'header JT API slot')
        args = b'uint8_t*msg_ptr' if index == 13 else b'tmosTaskIDtaskID,tmosEventsevent'
        signature = b'((bStatus_t(*)('+args+b'))BLE_LIB_JT('+str(index).encode('ascii')+b'))'
        check(re.sub(rb'\s+',b'',line) == signature,'header API function type')
        apis.append({'name':name.decode('ascii'),'index':index,'slot':hex(slot),
                     'macro_body_sha256':sha256(line).hexdigest()})
    return {'source':'original-dec2023/wchble_rom.h only','bytes':len(raw),
            'sha256':sha256(raw).hexdigest(),'flash_base':hex(flash),'JT_base':hex(flash+offset),
            'types_bits':types,'APIs':apis,'installed_binding_proved':False}


def app_contract(app):
    def pin(pc,raw,message):
        b = bytes.fromhex(raw)
        check(app[pc-BASE:pc-BASE+len(b)] == b,message)
    pin(0x90d8,'b7070400bc57','APP free slot load')
    pin(0x90fa,'b7070400','APP event slot base')
    pin(0x9106,'03a3c705','APP event slot load')
    pin(0x90f2,'03c5610a','APP task byte input')
    pin(0x90e6,'8545b3958500','APP event mask input')
    pin(0x90f0,'c205','APP mask truncation')
    pin(0x90f6,'c181','APP mask truncation')


def derive(app,carriers,header):
    app_contract(app)
    h = header_contract(header)
    rows = []
    for spec,cfg,data in zip(binding.PROFILES,DETAILS,carriers):
        profile = binding.profile(data,spec[0])
        free,stop,current,pending,free_sha,stop_sha = cfg
        pf,ps = binding.word(data,0x40068),binding.word(data,0x4005c)
        check(pf&~1 == free,'candidate deallocate entry pointer')
        check(ps&~1 == stop,'candidate stop-task entry pointer')
        f,s = binding.take(data,free,78),binding.take(data,stop,108)
        check(upper(f,6,8)+load(f,12,9,8,4,'candidate free control read') == 0x4002420c,
              'candidate free control address')
        for off,src in ((16,0),(26,9),(54,9),(72,9)):
            check(store(f,off,src,8,4,'candidate free control store') == 524,
                  'candidate free control address')
        check(w(f,20) == 0x0000100f and w(s,28) == 0x0000100f,'candidate FENCE.I operand')
        check(upper(s,8,15)+load(s,16,19,15,4,'candidate stop control read') == 0x4002420c and
              store(s,24,0,15,4,'candidate stop control clear') == 524 and
              upper(s,80,15)+store(s,84,19,15,4,'candidate stop control restore') == 0x4002420c,
              'candidate stop control address')
        check(store(s,44,0,10,2,'candidate timer halfword clear') == 2,
              'candidate timer halfword clear')
        check(load(f,42,14,10,1,'candidate payload marker load') == -2,'candidate payload marker load')
        check(f[46:50] == bytes.fromhex('9307f00f'),'candidate payload marker value')
        check(load(s,58,15,15,1,'candidate current-task byte load')+upper(s,54,15) == current,
              'candidate current-task byte address')
        check(load(s,70,14,15,2,'candidate pending-event load')+upper(s,66,15) == pending and
              store(s,76,8,15,2,'candidate pending-event store')+upper(s,66,15) == pending,
              'candidate pending-event address')
        fcall = auipc_call(f,62,free+62)
        scall = auipc_call(s,32,stop+32)
        clear = cjal(s,52,stop+52)
        check((fcall,scall,clear) == (0x20000110,0x20000314,free+0x3d0),
              'candidate direct-call targets')
        check(binding.word(data,0x40054)&~1 == clear,'candidate clear-event JT alias')
        check(normalized(f,((62,8),)) == normalized(FREE,((62,8),)),'candidate deallocate body template')
        spans = ((32,8),(58,4),(70,4),(76,4))
        check(normalized(s,spans) == normalized(STOP,spans),'candidate stop-task body template')
        codes = {'null':li(f,30,10),'tag_mismatch':li(f,58,10),'private_return':li(f,70,10),
                 'timer_found':li(s,88,10),'timer_missing':li(s,92,10)}
        check(codes == {'null':5,'tag_mismatch':4,'private_return':0,'timer_found':0,'timer_missing':6},
              'candidate normal-return status operands')
        # Mapping is conditional on the pinned candidate initializer's first copy.
        copy = {k:int(v,16) for k,v in profile['first_copy'].items()}
        end = int(profile['first_copy_end_exclusive'],16)
        calls = []
        for role,target in (('deallocate private helper',fcall),('timer lookup private helper',scall),
                            ('clear-event flash helper',clear)):
            ram = copy['destination'] <= target < end
            check(not ram or target+16 <= end,'complete private-helper prefix mapping')
            source = copy['source']+target-copy['destination'] if ram else target
            prefix = binding.take(data,source,16)
            calls.append({'role':role,'target':hex(target),'source':hex(source),
                          'mapping':'first-copy load image' if ram else 'captured flash',
                          'prefix16_sha256':sha256(prefix).hexdigest(),'body_or_ABI_proved':False})
        rows.append({'label':spec[0],'carrier_bytes':len(data),'carrier_sha256':sha256(data).hexdigest(),
            'slot40068':{'raw_pointer':hex(pf),'target':hex(free),'body_bytes':78,'body_sha256':sha256(f).hexdigest(),
                        'expected_body_sha256':free_sha,'template_sha256':sha256(normalized(f,((62,8),))).hexdigest()},
            'slot4005c':{'raw_pointer':hex(ps),'target':hex(stop),'body_bytes':108,'body_sha256':sha256(s).hexdigest(),
                        'expected_body_sha256':stop_sha,'template_sha256':sha256(normalized(s,spans)).hexdigest()},
            'current_task_byte':hex(current),'pending_event_halfword':hex(pending),
            'calls':calls,'clear_event_alias_slot':'0x40054',
            'decoded_return_codes':codes,'installed_binding_proved':False})
    check(len(rows) == 2,'two candidate profiles required')
    return {'schema':'TSL9-cancel-provider-reference-static-v1',
        'scope':'Pinned candidate bodies and operand/address formulas only; no ISA/provider/MMIO execution',
        'installed_binding_proved':False,'app_sha256':sha256(app).hexdigest(),'header':h,'profiles':rows,
        'control_word':'0x4002420c','control_scope':'encoded outer return paths: read/save, write0, FENCE.I before argument checks, restore; valid access and nested normal-return/preservation premises required',
        'deallocate_reference':{'outer_frame_bytes':16,'saved_S_registers':['S0','S1'],
            'pointer_zero_normal_return':5,'nonzero_pointer_extra_read':'U8[pointer-2]',
            'marker_not255_normal_return':4,'marker255_then_private_call_normal_return':0,
            'private_helper_preservation_and_return_proved':False},
        'stop_task_reference':{'outer_frame_bytes':32,'saved_S_registers':['S0','S1','S2','S3'],
            'lookup_nonzero_store':'SH zero at lookup_result+2 before clear-event call',
            'lookup_result_zero_normal_return':6,'lookup_result_nonzero_normal_return':0,
            'clear_event_reply_checked':False,'current_task_equal_action':'SH low16(input_event OR old_pending) to profile pending halfword',
            'private_helper_preservation_and_return_proved':False},
        'APP_argument_domain':{'task':'U8[GP+166], 0..255','event_mask':'1 << matched_index, matched_index 0..14',
            'fits_header_widths':True,'payload_nonzero_proves_pointer_minus2_tag':False}}


def tests(app,carriers,header,ledger):
    # Host-only path classification, with valid reads and private normal return
    # as premises; no pointer dereference or candidate execution occurs here.
    codes = ledger['profiles'][0]['decoded_return_codes']
    check(all(p['decoded_return_codes'] == codes for p in ledger['profiles']),'candidate return-code agreement')
    check(codes['null'] == 5,'null-pointer classification')
    counts = {}
    for marker in range(256):
        status = codes['private_return'] if marker == 255 else codes['tag_mismatch']
        counts[status] = counts.get(status,0)+1
    check(counts == {4:255,0:1},'tag classification algebra')
    returns = []
    for result in (0,1,0x80000000,MASK):
        returns.append(codes['timer_found'] if result else codes['timer_missing'])
    check(returns == [6,0,0,0],'lookup result classification algebra')
    widths = ledger['header']['types_bits']
    for task in range(256):
        for index in range(15):
            check(task < 1<<widths['tmosTaskID'] and 1<<index < 1<<widths['tmosEvents'],
                  'APP/header argument widths')
    def expect(which,message,action):
        a,h = bytearray(app),bytearray(header)
        cs = [bytearray(x) for x in carriers]
        action(a,cs,h)
        try: derive(a,cs,h)
        except RuntimeError as error:
            check(str(error) == message,'unexpected provider-static mutation failure: '+str(error))
        else: raise RuntimeError('provider-static mutation escaped '+which)
    first = DETAILS[0]
    def slot(cs,offset,value): cs[0][offset:offset+4] = value.to_bytes(4,'little')
    def marker(a,cs,h): cs[0][first[0]-LIB+44] = 0xf5
    def task(a,cs,h): cs[0][first[1]-LIB+60] ^= 0x10
    def private(a,cs,h): cs[0][first[0]-LIB+68] ^= 0x20
    def macro(a,cs,h):
        old = b'BLE_LIB_JT(10))'
        pos = h.index(old,h.index(b'#define    tmos_stop_task'))
        h[pos:pos+len(old)] = b'BLE_LIB_JT(11))'
    expect('slot5c','candidate stop-task entry pointer',lambda a,cs,h:slot(cs,0x5c,first[1]+2))
    expect('slot68','candidate deallocate entry pointer',lambda a,cs,h:slot(cs,0x68,first[0]+2))
    expect('marker','candidate payload marker load',marker)
    expect('task','candidate current-task byte address',task)
    expect('private','candidate direct-call targets',private)
    expect('header','header JT API index',macro)
    odd = [bytearray(x) for x in carriers]
    odd[0][0x5c:0x60] = (first[1]|1).to_bytes(4,'little')
    changed = derive(app,odd,header)['profiles'][0]['slot4005c']
    check(changed['raw_pointer'] != ledger['profiles'][0]['slot4005c']['raw_pointer'] and
          changed['target'] == ledger['profiles'][0]['slot4005c']['target'],'raw slot versus JALR normalization')
    print('PASS: 257 free-path/4 lookup-result algebra cases; 3840 APP typed argument shapes; 6 specified raw mutations; odd-slot distinction')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true',help='Create new ledger without overwrite')
    options = parser.parse_args()
    app,header = binding.APP.read_bytes(),HEADER.read_bytes()
    check(len(app) == 76800 and sha256(app).hexdigest() == binding.APP_HASH,'APP identity')
    check(len(header) == 243435 and sha256(header).hexdigest() == HEADER_HASH,'local SDK header identity')
    carriers = []
    for label,folder,tail,n,digest in binding.PROFILES:
        p = ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')
        b = p.read_bytes()
        check(len(b) == n and sha256(b).hexdigest() == digest,'candidate identity '+label)
        carriers.append(b)
    ledger = derive(app,carriers,header)
    for row in ledger['profiles']:
        for name in ('slot40068','slot4005c'):
            check(row[name]['body_sha256'] == row[name]['expected_body_sha256'],'complete candidate body hash')
    tests(app,carriers,header,ledger)
    output = (json.dumps(ledger,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if options.write:
        with OUT.open('xb') as f: f.write(output)
    else: check(OUT.read_bytes() == output,'provider ledger exact replay')
    print('PASS: 4 complete candidate bodies, 372 bytes; 6 call targets; 4 conditional RAM-source mappings; header JT8/JT10/JT13 slots')
    print('PASS: ledger exact replay; installed binding/private ABI UNPROVED; NO candidate ISA/provider/MMIO execution')


if __name__ == '__main__': main()
