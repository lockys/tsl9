"""Bounded static source decoder. No CPU state, execution or emulation exists here."""
from pathlib import Path
import argparse, copy, hashlib, json, runpy, subprocess, sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FW = ROOT / 'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FW_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = ROOT / 'experiments/tsl9-v4160-startup/build/image-fidelity-999d8125159a4d80bd6df9153f267002'
PARSER = ROOT / 'apk-analysis/tsl9-v4160-reset-memory-2026-10-21/compiler-review/elf32.py'
R2 = Path('C:/Users/locky/Tools/radare2/bin/r2.exe')
RANGES = [(0x9c0a,64), (0x18e90,8), (0x18e98,30), (0x18eb6,14), (0x18ec4,46), (0x18ef2,100)]
PRIOR = [
 'apk-analysis/tsl9-v4160-ota-route-2026-10-21/flash-reachability',
 'apk-analysis/tsl9-v4160-resident-contracts-2026-10-21/flash-callers',
 'apk-analysis/tsl9-v4160-conditional-runtime-2026-10-21/flash-evidence',
]
SHA = lambda b: hashlib.sha256(b).hexdigest()


def require(v, why):
    if not v:
        raise ValueError(why)


def sx(v, bits):
    return v - (1 << bits) if v & (1 << (bits-1)) else v


def decode(raw, pc):
    """Decode the admitted integer/CSR/compressed forms only; never evaluate them."""
    off = pc-0x8000
    h = int.from_bytes(raw[off:off+2], 'little')
    n = 4 if h & 3 == 3 else 2
    w = int.from_bytes(raw[off:off+n], 'little')
    rd = (w >> 7) & 31
    rs = (w >> 15) & 31
    rt = (w >> 20) & 31
    f = (w >> 12) & 7
    out = dict(PC=pc, bytes=n, raw_hex=raw[off:off+n].hex())
    def result(op, d=None, s=None, t=None, imm=None, target=None):
        out.update(op=op, rd=d, rs1=s, rs2=t, immediate=imm, target=target)
        return out
    if n == 4:
        op = w & 127
        if op == 0x37:
            return result('lui',rd,imm=w & 0xfffff000)
        if op == 0x13 and f in (0,6,7):
            return result({0:'addi',6:'ori',7:'andi'}[f],rd,rs,imm=sx(w >> 20,12))
        if op == 0x33 and f == 0 and w >> 25 == 0:
            return result('add',rd,rs,rt)
        if op == 3 and f == 2:
            return result('lw',rd,rs,imm=sx(w >> 20,12))
        if op == 0x23 and f == 2:
            return result('sw',s=rs,t=rt,imm=sx(((w >> 25) << 5)|((w >> 7)&31),12))
        if op == 0x63 and f == 1:
            k=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
            return result('bne',s=rs,t=rt,target=pc+sx(k,13))
        if op == 0x6f:
            k=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
            return result('jal',rd,target=pc+sx(k,21))
        if op == 0x73 and rd == 0 and f in (2,3):
            return result('csrs' if f == 2 else 'csrc',0,rs,imm=w>>20)
    else:
        q=h&3; f=h>>13; rd=(h>>7)&31; rp=8+((h>>7)&7); tp=8+((h>>2)&7)
        ci=sx(((h>>12)&1)<<5|((h>>2)&31),6)
        if q==1 and f==0:
            return result('addi',rd,rd,imm=ci)
        if q==1 and f==2:
            return result('addi',rd,0,imm=ci)
        if q==1 and f==3:
            if rd==2:
                k=((h>>12)&1)<<9|((h>>6)&1)<<4|((h>>5)&1)<<6|((h>>3)&3)<<7|((h>>2)&1)<<5
                return result('addi',2,2,imm=sx(k,10))
            return result('lui',rd,imm=(ci<<12)&0xffffffff)
        if q==1 and f==4:
            sub=(h>>10)&3
            if sub==2:
                return result('andi',rp,rp,imm=ci)
            if sub==3 and ((h>>12)&1)==0 and ((h>>5)&3) in (2,3):
                return result('or' if ((h>>5)&3)==2 else 'and',rp,rp,tp)
        if q==0 and f in (2,6):
            k=((h>>10)&7)<<3|((h>>6)&1)<<2|((h>>5)&1)<<6
            return result('lw',tp,rp,imm=k) if f==2 else result('sw',s=rp,t=tp,imm=k)
        if q==2 and f==2:
            k=((h>>12)&1)<<5|((h>>4)&7)<<2|((h>>2)&3)<<6
            return result('lw',rd,2,imm=k)
        if q==2 and f==6:
            k=((h>>9)&15)<<2|((h>>7)&3)<<6
            return result('sw',s=2,t=(h>>2)&31,imm=k)
        if q==2 and f==4 and ((h>>12)&1)==0:
            t=(h>>2)&31
            return result('mv',rd,t) if t else result('ret',s=rd)
        if q==1 and f==7:
            k=((h>>12)&1)<<8|((h>>10)&3)<<3|((h>>5)&3)<<6|((h>>3)&3)<<1|((h>>2)&1)<<5
            return result('bne',s=rp,t=0,target=pc+sx(k,9))
    raise ValueError('unsupported admitted instruction at '+hex(pc))


def instructions(raw):
    result={}
    for start,size in RANGES:
        pc=start
        while pc<start+size:
            row=decode(raw,pc); result[pc]=row; pc+=row['bytes']
        require(pc==start+size,'exact instruction coverage')
    return result


def facts(raw):
    rows=instructions(raw)
    def at(pc,op,rd=None,rs=None,rt=None,imm=None,target=None):
        r=rows[pc]
        require((r['op'],r['rd'],r['rs1'],r['rs2'],r['immediate'],r['target']) == (op,rd,rs,rt,imm,target),'semantic contract at '+hex(pc))
    # Complete wrapper frame, CSR ordering and direct-call geometry.
    at(0x9c0a,'addi',2,2,imm=-32)
    for pc,reg,slot in [(0x9c0c,8,24),(0x9c0e,9,20),(0x9c10,1,28),(0x9c14,11,12)]: at(pc,'sw',rs=2,rt=reg,imm=slot)
    at(0x9c12,'mv',9,10); at(0x9c16,'addi',8,0,imm=136)
    at(0x9c1a,'csrc',0,8,imm=0x800); at(0x9c3c,'csrs',0,8,imm=0x800)
    calls=[(0x9c1e,0x18e98),(0x9c26,0x18e90),(0x9c2c,0x18ec4),(0x9c34,0x18ef2),(0x9c38,0x18eb6)]
    for pc,t in calls: at(pc,'jal',1,target=t)
    at(0x9c22,'addi',10,0,imm=49); at(0x9c2a,'mv',10,9); at(0x9c32,'mv',10,9)
    at(0x9c30,'lw',11,2,imm=12)
    for pc,reg,slot in [(0x9c40,1,28),(0x9c42,8,24),(0x9c44,9,20)]: at(pc,'lw',reg,2,imm=slot)
    at(0x9c46,'addi',2,2,imm=32); at(0x9c48,'ret',rs=1)
    # Ordered key stores and last lock residue.
    at(0x18e90,'lui',15,imm=0x40022000); at(0x18e94,'sw',rs=15,rt=10,imm=12)
    at(0x18e98,'lui',13,imm=0x45670000); at(0x18ea0,'addi',13,13,imm=291)
    at(0x18e9c,'lui',15,imm=0x40022000); at(0x18ea4,'lui',14,imm=0xcdef9000); at(0x18eaa,'addi',14,14,imm=-1621)
    for pc,reg,offset in [(0x18ea8,13,4),(0x18eae,14,4),(0x18eb0,13,36),(0x18eb2,14,36)]: at(pc,'sw',rs=15,rt=reg,imm=offset)
    at(0x18eb6,'lui',14,imm=0x40022000); at(0x18eba,'lw',15,14,imm=16); at(0x18ebc,'lui',13,imm=0x8000)
    at(0x18ebe,'or',15,15,13); at(0x18ec0,'sw',rs=14,rt=15,imm=16)
    # Erase: all fresh RMWs and poll exit are distinct source operations.
    at(0x18ec4,'lui',15,imm=0x40022000); at(0x18ec8,'lw',14,15,imm=16); at(0x18eca,'lui',13,imm=0x20000)
    at(0x18ece,'andi',10,10,imm=-256); at(0x18ed2,'or',14,14,13); at(0x18ed4,'sw',rs=15,rt=14,imm=16)
    at(0x18ed6,'sw',rs=15,rt=10,imm=20); at(0x18ed8,'lw',14,15,imm=16); at(0x18eda,'ori',14,14,imm=64); at(0x18ede,'sw',rs=15,rt=14,imm=16)
    at(0x18ee0,'lw',14,15,imm=12); at(0x18ee2,'andi',14,14,imm=1); at(0x18ee4,'bne',rs=14,rt=0,target=0x18ee0)
    at(0x18ee6,'lw',14,15,imm=16); at(0x18ee8,'lui',13,imm=0xfffe0000); at(0x18eea,'addi',13,13,imm=-1)
    at(0x18eec,'and',14,14,13); at(0x18eee,'sw',rs=15,rt=14,imm=16)
    # Program: literal 256, status-derived zero index, 32-bit word loop and final fresh RMW.
    at(0x18ef2,'lui',14,imm=0x40022000); at(0x18ef6,'lw',15,14,imm=16); at(0x18ef8,'lui',13,imm=0x10000)
    at(0x18efa,'andi',10,10,imm=-256); at(0x18efe,'or',15,15,13); at(0x18f00,'sw',rs=14,rt=15,imm=16)
    for load,mask,branch,rd,base,bit in [(0x18f02,0x18f04,0x18f06,15,14,1),(0x18f0c,0x18f0e,0x18f10,15,14,2),(0x18f2a,0x18f2c,0x18f2e,13,14,2),(0x18f44,0x18f46,0x18f48,14,15,1)]:
        at(load,'lw',rd,base,imm=12); at(mask,'andi',rd,rd,imm=bit); at(branch,'bne',rs=rd,rt=0,target=load)
    for pc,rd in [(0x18f08,14),(0x18f12,14),(0x18f40,15)]: at(pc,'lui',rd,imm=0x40022000)
    at(0x18f16,'addi',12,0,imm=256); at(0x18f1a,'add',13,11,15); at(0x18f1e,'lw',16,13,imm=0)
    at(0x18f22,'add',13,10,15); at(0x18f26,'sw',rs=13,rt=16,imm=0)
    at(0x18f30,'addi',15,15,imm=4); at(0x18f32,'bne',rs=15,rt=12,target=0x18f1a)
    at(0x18f36,'lw',15,14,imm=16); at(0x18f38,'lui',13,imm=0x200000); at(0x18f3c,'or',15,15,13); at(0x18f3e,'sw',rs=14,rt=15,imm=16)
    at(0x18f4a,'lw',14,15,imm=16); at(0x18f4c,'lui',13,imm=0xffff0000); at(0x18f4e,'addi',13,13,imm=-1)
    at(0x18f50,'and',14,14,13); at(0x18f52,'sw',rs=15,rt=14,imm=16)
    expected=[{1,2,8,9,10,11},{15},{13,14,15},{13,14,15},{10,13,14,15},{10,12,13,14,15,16}]
    ledgers=[]
    for (start,size),dest in zip(RANGES,expected):
        group=[r for pc,r in rows.items() if start<=pc<start+size]
        actual={r['rd'] for r in group if r['rd'] not in (None,0)}
        require(actual==dest,'all encoded destination registers '+hex(start))
        require(group[-1]['op']=='ret' and group[-1]['rs1']==1,'normal return '+hex(start))
        for r in group:
            if r['target'] is not None and r['op']!='jal': require(r['target'] in rows and start<=r['target']<start+size,'local branch boundary')
        ledgers.append(dict(entry=start,end_exclusive=start+size,bytes=size,instruction_count=len(group),written_GPRs=sorted(actual),instruction_rows=group))
    require(sum(len(x['instruction_rows']) for x in ledgers)==len(rows),'non-overlapping source ranges')
    return ledgers


def prior_pins():
    pins=[]
    for name in PRIOR:
        directory=ROOT/name; seal=json.loads((directory/'seal.json').read_bytes())
        members=seal.get('files')
        if isinstance(members,dict): items=members.items()
        else:
            entries=seal.get('members',members)
            require(isinstance(entries,list),'prior seal schema '+name)
            items=[(v['path'],v['sha256']) for v in entries]
        for path,digest in items: require(SHA((directory/path).read_bytes())==digest,'prior sealed member '+path)
        pins.append(dict(path=name+'/seal.json',sha256=SHA((directory/'seal.json').read_bytes())))
    return pins


def inspect():
    raw=FW.read_bytes();require(SHA(raw)==FW_SHA and len(raw)==76800,'original firmware identity')
    require(SHA(PARSER.read_bytes())=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','ELF parser identity')
    ELF=runpy.run_path(str(PARSER))['ELF']
    require(SHA((BASE/'verification.json').read_bytes())=='2e6585594c1b02de058e2fbb5838f591a5915efed7bc461b9083e99a2e97b8bd','full baseline receipt')
    receipt=json.loads((BASE/'verification.json').read_bytes()); obj=BASE/'c/source-image-merged.o'
    require(SHA(obj.read_bytes())=='646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97','full baseline carrier')
    e=ELF(obj);owners=[]
    for start,size in RANGES:
        selected=[(n,a) for n,a in receipt['allocations'].items() if a['originalVA']==start]
        require(len(selected)==1,'unique actual owner');name,a=selected[0]; s=e.byname[name]
        body=raw[start-0x8000:start-0x8000+size]
        require(a['bytes']==size and s['size']==size and s['flags']==6 and e.data(s)==body,'carrier extent and exact bytes')
        syms=[x for x in e.symbols if x['name']=='__tsl9v4160_call_'+format(start,'x')]
        require(len(syms)==1 and syms[0]['size']==size and syms[0]['value']==0 and syms[0]['info']==18 and syms[0]['index']==s['index'],'actual function symbol')
        owners.append(dict(entry=start,bytes=size,section=name,sha256=SHA(body),symbol=syms[0]))
    ledger=facts(raw)
    capture=json.loads((HERE/'r2-source.json').read_bytes())
    decoded={r['PC']:r for g in ledger for r in g['instruction_rows']}
    require(len(capture['instructions'])==len(decoded),'R2 instruction count')
    for r in capture['instructions']:
        a=decoded[r['PC']];require((a['bytes'],a['raw_hex'])==(r['bytes'],r['raw_hex']),'R2 exact row coverage')
    negatives=[]
    # Each actual raw-byte mutant is checked by semantics before any firmware hash comparison.
    mutations=[('wrapper-frame-slot',0x9c14,'2ec4'),('CSR-mask-restore-confusion',0x9c16,'13040008'),('CSR-set-instead-clear',0x9c1a,'73200480'),('wrong-helper-target',0x9c26,'eff0a027'),('status-not49',0x9c22,'13050003'),('key-order',0x18ea8,'d8c3'),('lock-mask',0x18ebc,'c166'),('erase-align128',0x18ece,'137505f8'),('erase-start-bit',0x18eda,'13670702'),('erase-poll-bit',0x18ee2,'098b'),('program-length512',0x18f16,'13060020'),('source-A2-notA1',0x18f1a,'3306f600'),('source-read-halfword',0x18f1e,'03980600'),('word-write-halfword',0x18f26,'23900601'),('index-stride2',0x18f30,'8907'),('program-poll-seed-bit',0x18f0e,'858b'),('program-loop-target',0x18f32,'e394c7fc'),('final-program-mask',0x18f4c,'8176'),('fresh-source-stack-slot',0x9c30,'d245'),('return-via-wrong-GPR',0x18f54,'0281')]
    for label,pc,h in mutations:
        m=bytearray(raw);old=m[pc-0x8000:pc-0x8000+len(bytes.fromhex(h))].hex();require(old!=h,'nonidentity mutation')
        m[pc-0x8000:pc-0x8000+len(bytes.fromhex(h))]=bytes.fromhex(h)
        try: facts(m)
        except ValueError as ex: negatives.append(dict(name=label,PC=pc,before=old,after=h,rejected=True,reason=str(ex)))
        else: raise ValueError('accepted raw semantic negative '+label)
    route=json.loads((ROOT/PRIOR[0]/'flash-route.json').read_bytes())
    caller=[r for context in route['raw_r2_contexts'] for r in context['instructions'] if 0x9cf0<=r['PC']<=0x9d22]
    for r in caller: require(raw[r['PC']-0x8000:r['PC']-0x8000+r['bytes']].hex()==r['raw_hex'],'retained W caller actual source')
    require(len(caller)==16,'bounded W caller rows')
    return dict(schema='ID2966-flash-source-ABI-v1',passed=True,firmware=dict(path=FW.relative_to(ROOT).as_posix(),sha256=FW_SHA,base=0x8000,bytes=len(raw)),prior_seals=prior_pins(),baseline=dict(receipt_sha256=SHA((BASE/'verification.json').read_bytes()),carrier_sha256=SHA(obj.read_bytes()),parser_sha256=SHA(PARSER.read_bytes())),owners=owners,source_bytes=262,instruction_count=len(decoded),ledger=ledger,raw_negatives=negatives,r2_capture_sha256=SHA((HERE/'r2-source.json').read_bytes()),bounded_caller_9d00=dict(instructions=caller,first_continuation='bne s0,s5; A5/A4/A3/A2 overwritten before read in admitted continuation',all_other_caller_liveness_proved=False),target_execution=False,emulation=False,network=False,hardware=False,new_BIN=False,OTA_ready=False,IRQ_equivalence=False)


def capture():
    require(SHA(R2.read_bytes())=='cf307a66636960527e1511d00d2be6484b3b45929bf49f3d0923b24b13e17e58','R2 identity')
    args=[str(R2),'-q','-n','-a','riscv','-b','32','-m','0x8000','-e','scr.color=0']
    for start,size in RANGES: args.extend(['-c',f'pDj {size} @ {start}'])
    p=subprocess.run(args+['-c','q',str(FW)],capture_output=True,text=True,encoding='utf-8',timeout=60)
    require(p.returncode==0,'R2 static decode completed');lines=[x for x in p.stdout.splitlines() if x.strip()];require(len(lines)==6,'six R2 contexts')
    rows=[]
    for (start,size),line in zip(RANGES,lines):
        group=json.loads(line); require(sum(x['size'] for x in group)==size,'R2 full range')
        rows.extend(dict(PC=x['addr'],bytes=x['size'],raw_hex=x['bytes'],disassembly=x['opcode']) for x in group)
    data=dict(schema='R2-static-source-capture-v1',tool_sha256=SHA(R2.read_bytes()),instructions=rows,target_execution=False)
    (HERE/'r2-source.json').write_bytes((json.dumps(data,indent=2)+'\n').encode('utf-8'))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--capture',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    if a.capture: capture()
    report=inspect();payload=(json.dumps(report,indent=2)+'\n').encode('utf-8');path=HERE/'source-proof.json'
    if a.check: require(path.read_bytes()==payload,'readonly exact proof replay')
    else: path.write_bytes(payload)
    print(json.dumps(dict(passed=True,bytes=report['source_bytes'],instructions=report['instruction_count'],raw_negatives=len(report['raw_negatives']),target_execution=False)))
