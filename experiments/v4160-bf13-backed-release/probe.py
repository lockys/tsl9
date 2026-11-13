#!/usr/bin/env python3
"""Offline bounded link witness; no target execution."""
from collections import Counter
import hashlib, json, os, re, struct, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TOOLS = Path(r'C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin')
RESOURCE = TOOLS.parent/'lib/clang/18'
STDINT = RESOURCE/'include/stdint.h'
RAM = '.bss.tsl9v4160.ram'
PINS = {
 'experiments/tsl9-v4160-startup/src/startup.c':'ff513337ad3a32a1c56763b2060b0b3fbe7ddcd1606e3f50ff1d3036c9127a4c',
 'experiments/tsl9-v4160-startup/src/startup.h':'3d173456a94ae2f820cb94012a30f7adf2e4a52b3229d8980cf8eaff65d48dba',
 'experiments/tsl9-v4160-startup/layout/component.ld':'100745152102efad5fbf47d7cea3a1c5c81056913709011871068fcd9a8eaaa4',
 'experiments/v4160-bd5a-symbolic-c/candidate.c':'bcdd620449f9eda1c88fb32382689ee0265ccbda91bf458348910a6d088d29a7',
 'experiments/v4160-bd64-symbolic-c/candidate.c':'9b91d7ec92934269d9a0436d18751fca836501063a3ba75525759adc4a8c4bfd',
 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin':'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
}
READER = '6d42c704af3a9553aa6a632b8a6923c62c861315ee54cdcb894c7949a90c7818'
HEADER = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
TOOLPINS = {'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6', 'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
WITNESS = b'''OUTPUT_ARCH(riscv)
PHDRS { none PT_NULL; }
SECTIONS {
.bd5a 0xbd5a : { *setter.o(.leaf) } :none
.bd64 0xbd64 : { *getter.o(.leaf) } :none
.ram 0x20004000 (NOLOAD) : { KEEP(*(.bss.tsl9v4160.ram)) record_flag_bf13 = __tsl9v4160_ram + 0x7f13; } :none
/DISCARD/ : { *(.text) *(.riscv.attributes) }
}
'''

def need(ok, msg):
    if not ok: raise ValueError(msg)
def load(p, h):
    b=p.read_bytes(); need(hashlib.sha256(b).hexdigest()==h, 'pin: '+str(p)); return b
def sym(e,n):
    a=[s for s in e.symbols if s['name']==n]; need(len(a)==1,'symbol count: '+n); return a[0]
def attrs(s, keys): return tuple(s[k] for k in keys.split())
def shape(e, kind):
    need((e.header[0],e.header[3],e.header[6])==(kind,0,1),'ELF type/entry/flags')
    need(not any(s['type'] in (9,11) for s in e.sections),'unsupported tables')
def carrier(e):
    shape(e,1); need(not e.program_headers,'carrier phdr')
    s=e.section(RAM)
    need(attrs(s,'type flags address size link info align entsize')==(8,3,0,35160,0,0,4,0),'carrier section')
    need({x['name'] for x in e.sections if x['flags']&2}=={RAM},'carrier alloc')
    need(not e.relocations and not any(x['type'] in (4,9) for x in e.sections),'carrier reloc')
    need(not any(x['index'] and x['section']==0 for x in e.symbols),'carrier undefined')
    names=['__tsl9v4160_ram','__tsl9v4160_gp','__tsl9v4160_bss_end','__tsl9v4160_sp_address']
    need(Counter(x['name'] for x in e.symbols if x['info']>>4)==Counter(names),'carrier globals')
    for n,v,z,i,sec in [(names[0],0,35160,0x11,s['index']),(names[1],0,0,0x11,s['index']),(names[2],35160,0,0x11,s['index']),(names[3],0x20010000,0,0x10,0xfff1)]:
        need(attrs(sym(e,n),'value size info other section')==(v,z,i,0,sec),'carrier symbol '+n)
def final(e,refs):
    shape(e,2); need(len(e.program_headers)==1 and e.program_headers[0][0]==0,'final phdr: expected one PT_NULL')
    need(not e.relocations and not any(s['type'] in (4,9) for s in e.sections),'final reloc')
    need(not any(s['index'] and s['section']==0 for s in e.symbols),'final undefined')
    need({s['name'] for s in e.sections if s['flags']&2}=={'.bd5a','.bd64','.ram'},'final alloc')
    r=e.section('.ram'); need(attrs(r,'type flags address size align')==(8,3,0x20004000,35160,4),'final RAM')
    names=['__tsl9v4160_ram','__tsl9v4160_gp','__tsl9v4160_bss_end','__tsl9v4160_sp_address','record_flag_bf13','tsl9_record_dispatch_provider_bd5a','tsl9_record_dispatch_provider_bd64']
    need(Counter(x['name'] for x in e.symbols if x['info']>>4)==Counter(names),'final globals')
    for n,v,z,i,sec in [(names[0],0x20004000,35160,0x11,r['index']),(names[1],0x20004000,0,0x11,r['index']),(names[2],0x2000c958,0,0x11,r['index']),(names[3],0x20010000,0,0x10,0xfff1),(names[4],0x2000bf13,0,0x10,r['index'])]:
        need(attrs(sym(e,n),'value size info other section')==(v,z,i,0,sec),'final symbol '+n)
    for name,addr in [('bd5a',0xbd5a),('bd64',0xbd64)]:
        s=e.section('.'+name)
        need(attrs(s,'type flags address size')==(1,6,addr,10),'final section '+name)
        need(e.data(s)==refs[name],'final bytes '+name)
        need(attrs(sym(e,'tsl9_record_dispatch_provider_'+name),'value size info other section')==(addr,10,0x12,0,s['index']),'final function '+name)

def run(cmd, success=True):
    env={k:v for k,v in os.environ.items() if k.upper() in ('SYSTEMROOT','WINDIR','TEMP','TMP')}
    p=subprocess.run([str(x) for x in cmd],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90,env=env)
    need((p.returncode==0)==success,'command status: '+repr(cmd)+'\n'+p.stderr.decode('utf8','replace'))
    return p
def headers(p,expected):
    lines=p.stderr.decode('utf8','replace').splitlines()
    paths=[Path(m.group(1)).resolve() for line in lines if (m:=re.match(r'^\.+ (.+)$',line))]
    need(paths==[x.resolve() for x in expected],'include trace: '+repr(lines))
    for x in paths:
        if x.name.lower()=='stdint.h': load(x,HEADER)
def rejected(fn,reason):
    try: fn()
    except (ValueError,IndexError,struct.error,UnicodeError) as e:
        need(str(e)==reason,'wrong rejection: '+repr(str(e))+' expected '+reason); return reason
    raise ValueError('accepted negative: '+reason)
def patch(raw,off,b):
    x=bytearray(raw); x[off:off+len(b)]=b; return bytes(x)
def u32(x): return struct.pack('<I',x)

def main():
    need(len(sys.argv)==1 and sys.flags.isolated and sys.dont_write_bytecode and sys.flags.optimize in (0,1),'use python -I -B with optional -O, no arguments')
    data={n:load(ROOT/n,h) for n,h in PINS.items()}
    for n,h in TOOLPINS.items(): load(TOOLS/n,h)
    load(STDINT,HEADER); reader=load(HERE/'elf.py',READER)
    need((HERE/'witness.ld').read_bytes()==WITNESS,'witness bytes')
    ns={'__name__':'pinned_reader'}; exec(compile(reader,'<pinned reader>','exec'),ns); E=ns['ELF']
    source=data['experiments/tsl9-v4160-startup/src/startup.c']; layout=data['experiments/tsl9-v4160-startup/layout/component.ld']
    binary=data['firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin']
    need(len(binary)==76800 and b'uint8_t __tsl9v4160_ram[35160];' in source and b'.bss.ram 0x20004000 (NOLOAD)' in layout,'source/layout')
    need(binary[0x186aa-0x8000:0x186aa-0x8000+8]==bytes.fromhex('97c1fe1f93816195'),'reset bytes')
    refs={n:binary[a-0x8000:a-0x8000+10] for n,a in [('bd5a',0xbd5a),('bd64',0xbd64)]}
    need(all(len(v)==10 for v in refs.values()) and 0x20004000+0x7f13==0x2000bf13,'references')
    inc=['--no-default-config','-resource-dir',RESOURCE,'-nostdinc','-isystem',RESOURCE/'include','-H']
    flags=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mcmodel=medany','-mno-relax','-fno-pic','-ffreestanding','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Oz','-Wall','-Wextra','-Werror']
    report=[]
    with tempfile.TemporaryDirectory(prefix='run-',dir=HERE) as tmp:
        t=Path(tmp); (t/'startup.c').write_bytes(source); (t/'startup.h').write_bytes(data['experiments/tsl9-v4160-startup/src/startup.h'])
        for n in ('bd5a','bd64'): (t/(n+'.c')).write_bytes(data['experiments/v4160-'+n+'-symbolic-c/candidate.c'])
        for std,lang in [('c11','c'),('c++17','c++')]:
            d=t/std.replace('+','p'); d.mkdir(); full=d/'full.o'; gc=d/'carrier.o'; setter=d/'setter.o'; getter=d/'getter.o'
            start=[TOOLS/'clang.exe',*inc,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-stack-protector','-fno-builtin','-Wall','-Wextra','-Werror','-x',lang,'-std='+std,'-c',t/'startup.c','-o',full]
            headers(run(start),[t/'startup.h',STDINT])
            run([TOOLS/'ld.lld.exe','-r','--no-relax','--gc-sections','-u','__tsl9v4160_ram',full,'-o',gc]); ce=E(gc.read_bytes()); carrier(ce)
            f=E(full.read_bytes()); shape(f,1); fs=f.section(RAM); cs=ce.section(RAM)
            need(attrs(fs,'type flags address size link info align entsize')==attrs(cs,'type flags address size link info align entsize'),'GC section changed')
            members=lambda e,s: sorted(attrs(x,'name value size info other') for x in e.symbols if x['section']==s['index'] and x['info']&15!=3)
            need(members(f,fs)==members(ce,cs) and not any(r['section']==fs['index'] for r in f.relocations),'GC members changed')
            for n,obj in [('bd5a',setter),('bd64',getter)]:
                defs=['-Dcandidate=tsl9_record_dispatch_provider_bd5a','-Drecord_flag_bd5a=record_flag_bf13'] if n=='bd5a' else ['-Dtsl9_get_bd64=tsl9_record_dispatch_provider_bd64','-Drecord_flag_bd64=record_flag_bf13']
                headers(run([TOOLS/'clang.exe',*inc,*flags,*(['-ffixed-x%d'%i for i in range(11,15)] if n=='bd5a' else []),*defs,'-x',lang,'-std='+std,'-c',t/(n+'.c'),'-o',obj]),[])
            def link(label,script=WITNESS,objects=(setter,getter,gc),success=True):
                ld=d/(label+'.ld'); out=d/(label+'.elf'); ld.write_bytes(script)
                p=run([TOOLS/'ld.lld.exe','--no-relax','-T',ld,'-o',out,*objects],success)
                if not success:
                    need(not out.exists(),'failed link output'); return p.stderr.decode('utf8','replace')
                return E(out.read_bytes())
            e=link('positive'); final(e,refs); neg={}
            for label,old,new,reason in [('wrong_base',b'0x20004000',b'0x20005000','final RAM'),('wrong_offset',b'0x7f13',b'0x7f14','final symbol record_flag_bf13')]:
                need(WITNESS.count(old)==1,'script replacement'); x=link(label,WITNESS.replace(old,new)); neg[label]=rejected(lambda:final(x,refs),reason)
                need(all(x.data('.'+n)!=refs[n] for n in refs),'wrong-address bytes unchanged')
            for label,objs,diag in [('missing',(setter,getter),'__tsl9v4160_ram'),('duplicate',(setter,getter,gc,gc),'duplicate symbol')]:
                msg=link(label,objects=objs,success=False); need(diag in msg,label+' diagnostic'); neg[label]=diag
            extra=d/'extra.c'; extra.write_bytes(b'__attribute__((section(".extra"),used)) int extra;\n'); eo=d/'extra.o'
            headers(run([TOOLS/'clang.exe',*inc,*flags,'-x',lang,'-std='+std,'-c',extra,'-o',eo]),[])
            x=link('extra',WITNESS.replace(b'/DISCARD/',b'.extra 0x30000000 : { *(.extra) } :none\n/DISCARD/'),(setter,getter,gc,eo)); neg['extra']=rejected(lambda:final(x,refs),'final alloc')
            raw=e.raw; sh=struct.unpack_from('<I',raw,32)[0]; ph=struct.unpack_from('<I',raw,28)[0]; need(bool(e.program_headers),'no phdr')
            st=next(s for s in e.sections if s['type']==2); alias=sym(e,'record_flag_bf13'); sec=e.section('.bd5a')
            changes={'pt_load':(ph,u32(1),'final phdr: expected one PT_NULL'), 'pt_interp':(ph,u32(3),'final phdr: expected one PT_NULL'), 'pt_dynamic':(ph,u32(2),'final phdr: expected one PT_NULL'), 'phdr_none':(44,struct.pack('<H',0),'final phdr: expected one PT_NULL'), 'phdr_extra':(44,struct.pack('<H',2),'final phdr: expected one PT_NULL'), 'ram_type':(sh+40*e.section('.ram')['index']+4,u32(1),'final RAM'), 'alias_abs':(st['offset']+16*alias['index']+14,struct.pack('<H',0xfff1),'final symbol record_flag_bf13'), 'leaf_byte':(sec['offset'],bytes([raw[sec['offset']]^1]),'final bytes bd5a')}
            for label,(off,b,reason) in changes.items():
                modified=patch(raw+(bytes(35160) if label=='ram_type' else b''),off,b)
                neg[label]=rejected(lambda:final(E(modified),refs),reason)
            cr=gc.read_bytes(); co=struct.unpack_from('<I',cr,32)[0]; neg['carrier_size']=rejected(lambda:carrier(E(patch(cr,co+40*cs['index']+20,u32(35159)))),'carrier section')
            raw=e.raw; sh=struct.unpack_from('<I',raw,32)[0]; st=next(s for s in e.sections if s['type']==2)
            for label,index,reason in [('symstr_type',st['link'],'symbol string table type'),('shstr_type',struct.unpack_from('<H',raw,50)[0],'section name string table type')]:
                neg[label]=rejected(lambda:E(patch(raw,sh+40*index+4,u32(1))),reason)
            target=sym(e,'__tsl9v4160_sp_address'); other=sym(e,'__tsl9v4160_gp')
            forged=patch(raw,st['offset']+16*other['index'],raw[st['offset']+16*target['index']:st['offset']+16*target['index']+4])
            neg['duplicate_global']=rejected(lambda:final(E(forged),refs),'final globals')
            # Mutate actual generated ELF bytes at the reader boundary, with one
            # independently checked reason for each full/GC/final case.
            for label,obj in [('full',f),('gc',ce),('final',e)]:
                raw=obj.raw; sh=struct.unpack_from('<I',raw,32)[0]
                tab=next(s for s in obj.sections if s['type']==2); count=tab['size']//16
                alloc=obj.section('.ram' if label=='final' else RAM)
                local=next(x for x in obj.symbols if x['index'] and x['info']>>4==0)
                glob=next(x for x in obj.symbols if x['info']>>4!=0)
                mutations={
                    'relr':(sh+40*alloc['index']+4,u32(19),'unsupported section type'),
                    'unknown_type':(sh+40*alloc['index']+4,u32(0x12345678),'unsupported section type'),
                    'sym_zero_name':(tab['offset'],u32(1),'symbol zero entry'),
                    'sym_zero_value':(tab['offset']+4,u32(1),'symbol zero entry'),
                    'sym_zero_size':(tab['offset']+8,u32(1),'symbol zero entry'),
                    'sym_zero_info':(tab['offset']+12,b'\x01','symbol zero entry'),
                    'sym_zero_other':(tab['offset']+13,b'\x01','symbol zero entry'),
                    'sym_zero_shndx':(tab['offset']+14,struct.pack('<H',1),'symbol zero entry'),
                    'shinfo_zero':(sh+40*tab['index']+28,u32(0),'symbol local boundary'),
                    'shinfo_large':(sh+40*tab['index']+28,u32(count+1),'symbol local boundary'),
                    'shinfo_early':(sh+40*tab['index']+28,u32(tab['info']-1),'symbol local boundary'),
                    'shinfo_late':(sh+40*tab['index']+28,u32(tab['info']+1),'symbol local boundary'),
                    'local_binding':(tab['offset']+16*local['index']+12,bytes([local['info']|0x10]),'symbol local boundary'),
                    'global_binding':(tab['offset']+16*glob['index']+12,bytes([glob['info']&15]),'symbol local boundary'),
                }
                for case,(off,b,reason) in mutations.items():
                    neg[label+'_'+case]=rejected(lambda:E(patch(raw,off,b)),reason)
            # LLD emits real SECTION symbols in the GC carrier, not full/final.
            raw=ce.raw; tab=next(s for s in ce.sections if s['type']==2)
            ss=next(x for x in ce.symbols if x['info']&15==3); base=tab['offset']+16*ss['index']
            named=next(x for x in ce.symbols if x['name'])
            nameoff=raw[tab['offset']+16*named['index']:tab['offset']+16*named['index']+4]
            section_mutations={
                'name':(0,nameoff,'SECTION symbol metadata'),
                'value':(4,u32(ss['value']+1),'SECTION symbol metadata'),
                'size':(8,u32(1),'SECTION symbol metadata'),
                'binding':(12,b'\x13','symbol local boundary'),
                'other':(13,b'\x01','SECTION symbol metadata'),
                'shndx_undef':(14,struct.pack('<H',0),'SECTION symbol metadata'),
                'shndx_abs':(14,struct.pack('<H',0xfff1),'SECTION symbol metadata'),
                'shndx_oob':(14,struct.pack('<H',len(ce.sections)),'symbol index'),
            }
            for case,(off,b,reason) in section_mutations.items():
                neg['gc_section_'+case]=rejected(lambda:E(patch(raw,base+off,b)),reason)
            # Put a SECTION record in a global slot, isolating its invalid binding
            # from the independently enforced local/global partition.
            global_slot=next(x for x in ce.symbols if x['info']>>4!=0)
            pos=tab['offset']+16*global_slot['index']
            forged=patch(raw,pos,raw[base:base+16]); forged=patch(forged,pos+12,b'\x13')
            neg['gc_section_global_slot_binding']=rejected(lambda:E(forged),'SECTION symbol metadata')
            expected={'wrong_base','wrong_offset','missing','duplicate','extra','pt_load','pt_interp','pt_dynamic','phdr_none','phdr_extra','ram_type','alias_abs','leaf_byte','carrier_size','symstr_type','shstr_type','duplicate_global'}
            expected |= {label+'_'+case for label in ('full','gc','final') for case in ('relr','unknown_type','sym_zero_name','sym_zero_value','sym_zero_size','sym_zero_info','sym_zero_other','sym_zero_shndx','shinfo_zero','shinfo_large','shinfo_early','shinfo_late','local_binding','global_binding')}
            expected |= {'gc_section_'+case for case in ('name','value','size','binding','global_slot_binding','other','shndx_undef','shndx_abs','shndx_oob')}
            need(set(neg)==expected and all(neg.values()),'negative matrix'); final(E(e.raw),refs); carrier(E(cr))
            report.append({'language':std,'negative_reasons':neg,'leaf_bytes':{n:b.hex() for n,b in refs.items()}})
    need(len(report)==2 and {x['language'] for x in report}=={'c11','c++17'},'case matrix')
    print(json.dumps({'status':'PASS','python_optimize':sys.flags.optimize,'cases':report},sort_keys=True))

if __name__=='__main__':
    try: main()
    except Exception as e:
        print('FAIL CLOSED: '+str(e),file=sys.stderr); sys.exit(1)
