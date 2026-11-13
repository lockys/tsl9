#!/usr/bin/env python3
"""Offline leaf link replay. Never execute the generated RISC-V artifacts."""
import hashlib, json, os, struct, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    'manifest': ('src/source-build-manifest.json', '466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739'),
    'candidate': ('experiments/v4160-new-leaf-turn/leaf.c', 'e358a04a1c0d57589107315751ac0daf33cad9c53e104da80a7598da983396ff'),
    'owner': ('src/native/receive/feature_state_records.c', '19a1c39ee7831f42960454d02393512520c425ea1ad90f9e08b0f8d4e3b32db3'),
    'bin': ('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin', '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')}
TOOL_PINS = {'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6', 'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
NAME = 'tsl9_feature_state_records_provider_105c4'
ADDR = 0x105c4
REFERENCE = bytes.fromhex('034535007115133515008280')
OBJECT_SHA = '4be6126f10b851cc7729d4579fccb9c66330b5fa604b861881e48e863a8e440c'
IMAGE_SHA = 'fe4b3f31080ee42012ff0ce963d7f5a8a75804ada7232c3b8718bf1d00976988'


def need(ok, message):
    if not ok: raise ValueError(message)
def sha(data): return hashlib.sha256(data).hexdigest()
def tool_directory():
    value = os.environ.get('TSL9_NDK_BIN')
    need(bool(value), 'TSL9_NDK_BIN must be provided')
    directory = Path(value)
    need(directory.is_absolute() and directory.is_dir(), 'TSL9_NDK_BIN must be an absolute existing directory')
    return directory

def snapshot(tools):
    data = {}
    for name, (path, digest) in PINS.items():
        data[name] = (ROOT/path).read_bytes()
        need(sha(data[name]) == digest, name+' pin mismatch')
    for name, digest in TOOL_PINS.items():
        need(sha((tools/name).read_bytes()) == digest, name+' pin mismatch')
    return data


def inspect(data, typ, owner=False):
    """Bounded ELF32 reader for these inputs; not a general adversarial parser."""
    def unpack(fmt, pos):
        size = struct.calcsize(fmt)
        need(0 <= pos <= len(data)-size, 'ELF bounds')
        return struct.unpack_from(fmt, data, pos)
    h = unpack('<16sHHIIIIIHHHHHH', 0)
    need(h[0] == b'\x7fELF\x01\x01\x01'+bytes(9) and h[1:4] == (typ,243,1), 'ELF identity')
    need(h[7:9] == (1,52) and h[11] == 40 and 0 < h[12] <= 1024 and h[13] < h[12], 'ELF header')
    need(h[6] <= len(data) and h[12]*40 <= len(data)-h[6], 'section table bounds')
    if h[10]:
        need(h[9] == 32 and h[5] <= len(data) and h[10]*32 <= len(data)-h[5], 'program table bounds')
    else: need(h[5] == 0, 'empty program table')
    ph = [unpack('<8I',h[5]+32*i) for i in range(h[10])]
    for p in ph: need(p[1] <= len(data) and p[4] <= len(data)-p[1], 'program bounds')
    need(not any(p[0] == 1 for p in ph), 'PT_LOAD forbidden')
    if typ == 1: need(not ph, 'object program headers')
    rows = [unpack('<10I',h[6]+40*i) for i in range(h[12])]
    def content(r):
        need(r[3]+r[5] <= 0x100000000, 'section address bounds')
        if r[1] == 8: return b''
        need(r[4] <= len(data) and r[5] <= len(data)-r[4], 'section bounds')
        return data[r[4]:r[4]+r[5]]
    def text(b, off):
        need(off < len(b), 'string bounds')
        end = b.find(b'\0', off); need(end >= 0, 'string termination')
        return b[off:end].decode('utf-8')
    need(rows[h[13]][1] == 3, 'section strings')
    strings = content(rows[h[13]])
    sections = [(text(strings,r[0]),r,content(r)) for r in rows]
    tables = [(i,r) for i,(_,r,_) in enumerate(sections) if r[1] == 2]
    need(len(tables)==1, 'symbol table inventory')
    stidx, st = tables[0]
    need(st[6] < len(rows) and rows[st[6]][1] == 3 and st[9] == 16 and st[5] % 16 == 0, 'symbol table metadata')
    names = content(rows[st[6]])
    raw_symbols = content(st); count = st[5]//16
    need(1 <= st[7] <= count, 'symbol sh_info')
    need(raw_symbols[:16] == bytes(16), 'symbol zero')
    symbols = []
    for i in range(count):
        no, val, size, info, other, ndx = unpack('<IIIBBH',st[4]+16*i)
        need((info >> 4 == 0) == (i < st[7]), 'symbol partition')
        symbols.append((text(names,no),val,size,info,other,ndx))
    target = [s for s in symbols if s[0] == NAME]
    need(len(target)==1 and 0 < target[0][5] < len(rows), 'target symbol')
    s = target[0]; name,r,raw = sections[s[5]]
    expected_name = '.text.'+NAME if owner else '.leaf'
    need(name == expected_name and sum(x[0]==name for x in sections)==1, 'target section')
    need((r[1],r[2],r[3],r[5]) == (1,6,ADDR if typ==2 else 0,12), 'target section metadata')
    need(s[1:] == (ADDR if typ==2 else 0,12,0x12,0,s[5]), 'target symbol metadata')
    need(raw == REFERENCE, 'target bytes differ')
    if owner:
        need(not any(x[1][1] in (4,9) and x[1][7]==s[5] and x[1][5] for x in sections), 'owner target relocations')
    else:
        inventory = ({'', '.strtab', '.text', '.leaf', '.comment', '.note.GNU-stack', '.riscv.attributes', '.llvm_addrsig', '.symtab'} if typ==1 else
                     {'', '.strtab', '.text', '.leaf', '.comment', '.riscv.attributes', '.symtab', '.shstrtab'})
        need(len(sections)==len(inventory) and {x[0] for x in sections}==inventory, 'section inventory')
        need(h[4] == (ADDR if typ==2 else 0), 'entry address')
        need(not any(x[1][1] in (4,9) for x in sections), 'relocations')
        need(all(x[3]>>4 == 0 or x[0]==NAME for x in symbols), 'foreign symbol')
        need(sha(data) == (OBJECT_SHA if typ==1 else IMAGE_SHA), 'whole ELF bytes differ')
    return {'sha256':sha(data), 'leaf':raw.hex(), 'section_index':s[5], 'symbol_index':symbols.index(s), 'sections':len(rows), 'symbols':len(symbols), 'program_types':[p[0] for p in ph]}


def command(argv, directory, env):
    p = subprocess.run([str(x) for x in argv], cwd=directory, env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
    need(p.returncode == 0 and not p.stdout and not p.stderr,
         'command failed or output: exit=%s stdout=%r stderr=%r' % (p.returncode,p.stdout,p.stderr))


def rejected(fn, reason):
    try: fn()
    except ValueError as e:
        need(str(e)==reason, 'wrong rejection: '+str(e)); return
    raise ValueError('negative accepted: '+reason)


def run():
    tools = tool_directory()
    clang, ld = tools/'clang.exe', tools/'ld.lld.exe'
    data = snapshot(tools)
    need(len(data['bin']) == 76800 and data['bin'][ADDR-0x8000:ADDR-0x8000+12] == REFERENCE, 'BIN window')
    profiles = json.loads(data['manifest'])['code_profiles']['queue-consumer-a0-a5']
    need(set(profiles)=={'c','cpp'} and all(isinstance(x,list) and all(isinstance(y,str) for y in x) for x in profiles.values()), 'profiles')
    body = data['owner'].decode().split('REGION void '+NAME+'(void)',1)[1].split('\n}',1)[0]
    need('PORT(' in body and 'LIVE;' in body and b'__asm__' in data['owner'], 'owner asm witness')
    result = {'status':'INCOMPLETE_FAIL_CLOSED', 'passed':False, 'checks_passed':False, 'reference':REFERENCE.hex(), 'cases':{}}
    with tempfile.TemporaryDirectory(prefix='replay-',dir=HERE) as temp:
        d=Path(temp); env={k:os.environ[k] for k in ('SystemRoot','WINDIR') if k in os.environ}; env.update(TEMP=temp,TMP=temp,TMPDIR=temp,TSL9_NDK_BIN=str(tools))
        source=d/'leaf.c'; source.write_bytes(data['candidate'])
        owner=d/'owner.c'; owner.write_bytes(data['owner'])
        layout=d/'layout.ld'; layout.write_text('PHDRS { none PT_NULL; }\nSECTIONS { .leaf 0x105c4 : { KEEP(*(.leaf)) } :none }\n',encoding='ascii')
        for mode in ('c','cpp'):
            obj=d/(mode+'.o'); image=d/(mode+'.elf'); original=d/('owner-'+mode+'.o')
            cc=[clang,*profiles[mode],'-Dleaf='+NAME,'-nostdinc','-c',source,'-o',obj]
            command(cc,d,env); need(source.read_bytes()==data['candidate'], 'candidate snapshot changed')
            raw=obj.read_bytes(); ob=inspect(raw,1)
            link=[ld,'--no-relax','--fatal-warnings','--no-undefined','-T',layout,'-e',NAME,'-o',image,obj]
            command(link,d,env); need(obj.read_bytes()==raw, 'object changed during link')
            linked=inspect(image.read_bytes(),2)
            command([clang,*profiles[mode],'-c',owner,'-o',original],d,env)
            need(owner.read_bytes()==data['owner'], 'owner snapshot changed')
            own=inspect(original.read_bytes(),1,True)
            neg=d/(mode+'-negative.o')
            command([clang,*profiles[mode],'-Dleaf='+NAME,'-nostdinc','-DNEGATIVE','-c',source,'-o',neg],d,env)
            rejected(lambda:inspect(neg.read_bytes(),1),'target bytes differ')
            negimage=d/(mode+'-negative.elf')
            command([ld,'--no-relax','--fatal-warnings','--no-undefined','-T',layout,'-e',NAME,'-o',negimage,neg],d,env)
            rejected(lambda:inspect(negimage.read_bytes(),2),'target bytes differ')
            result['cases'][mode]={'object':ob,'linked':linked,'owner':own,'negative':'object and linked bytes rejected','compile':[str(x) for x in cc], 'link':[str(x) for x in link]}
        need(source.read_bytes()==data['candidate'] and owner.read_bytes()==data['owner'], 'snapshot changed')
    need(snapshot(tools)==data,'inputs changed')
    result['checks_passed']=True
    return result


def main(argv):
    try:
        need(not argv, 'no arguments accepted')
        result=run()
    except Exception as exc:
        result={'status':'INCOMPLETE_FAIL_CLOSED','passed':False,'checks_passed':False,'error':type(exc).__name__+': '+str(exc)}
    print(json.dumps(result,indent=2))
    return 1

if __name__=='__main__': sys.exit(main(sys.argv[1:]))
