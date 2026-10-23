#!/usr/bin/env python3
"""Link three genuine C providers at original PCs. Diagnostic ELF, never firmware."""
import argparse,hashlib,json,re,runpy,struct,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SPI=ROOT/'experiments/tsl9-spi-transfer-leaf'
SPI_CHECK=SPI/'verify.py'
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
need(sha(SPI_CHECK)=='8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8','Frozen SPI proof/ELF reader')
V=runpy.run_path(str(HERE/'verify.py'))
U=runpy.run_path(str(SPI_CHECK))
E=U['ELF']
decode=runpy.run_path(str(HERE/'decode.py'))['decode']
decode.__globals__['BASE']=0x16896

def portable(value,llvm):return U['portable'](value,ROOT,llvm)
def encode(value,llvm):return (json.dumps(portable(value,llvm),indent=2)+'\n').encode()
def paths(llvm):
    p=[Path(__file__).resolve(),HERE/'nominal.ld',HERE/'verify.py',HERE/'spec.json',SPI_CHECK,ROOT/U['SOURCE'],ROOT/U['LINKER'],ROOT/U['FIRMWARE']]
    p += [ROOT/n for n in V['S']['pins']]+[llvm/n for n in V['S']['tools']]+[llvm.parent/'lib/clang/18/include/stdint.h']
    p += [HERE/'build/verified-v1'/m/'verification.json' for m in ('c','cpp')]
    p += [SPI/'build/verified-v3'/m/'verification.json' for m in ('c','cpp')]
    # Retained artifacts actually consumed by recursive proofs and by LLD.
    # These are inputs, separate from artifacts created by this invocation.
    p += [q for q in (HERE/'build/verified-v1').rglob('*') if q.is_file()]
    for mode in ('c','cpp'):
        p += [q for q in (SPI/'build/verified-v3'/mode).iterdir() if q.is_file()]
    return sorted(set(p))
def snapshot(llvm):return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths(llvm)}

def upstream(llvm):
    # Re-evaluate actual original artifacts. Passing receipt text alone is not
    # accepted as a proof. Existing proofs are read-only, never regenerated.
    old=sys.argv;sys.argv=[str(HERE/'verify.py'),'--out-dir',str(HERE/'build/verified-v1'),'--llvm-bin',str(llvm)]
    try:need(V['main']()==0,'Current write-provider full read-only proof')
    finally:sys.argv=old
    results={}
    for mode in ('c','cpp'):
        folder=SPI/'build/verified-v3'/mode
        value,encoded=U['evaluate'](ROOT,llvm,folder,mode)
        need((folder/'verification.json').read_bytes()==encoded.encode(),'Current SPI original proof exact replay')
        results[mode]=dict(SPI_receipt_sha256=sha(folder/'verification.json'),write_receipt_sha256=sha(HERE/'build/verified-v1'/mode/'verification.json'))
    return results

def recipes(folder,llvm,mode):
    return [
      ('SPI-compile',[str(llvm/'clang.exe')]+U['flags'](mode)+['-MD','-MF',str(folder/'spi.d'),'-MT',str(folder/'spi.o'),'-c',str(ROOT/U['SOURCE']),'-o',str(folder/'spi.o')]),
      ('SPI-IR',[str(llvm/'clang.exe')]+U['flags'](mode)+['-S','-emit-llvm',str(ROOT/U['SOURCE']),'-o',str(folder/'spi.ll')]),
      ('nominal-link',[str(llvm/'ld.lld.exe'),'--no-relax','-T',str(HERE/'nominal.ld'),str(folder/'spi.o'),str(HERE/'build/verified-v1'/mode/'native.o'),'-o',str(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf')]),
      ('nominal-read',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf')])]

def consumed_inputs(label,folder,mode):
    if label in ('SPI-compile','SPI-IR'):files=[ROOT/U['SOURCE']]
    elif label=='nominal-link':files=[HERE/'nominal.ld',folder/'spi.o',HERE/'build/verified-v1'/mode/'native.o']
    else:files=[folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf']
    return {str(p):sha(p) for p in files}

def readback_contract(text,code):
    actual=[]
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)',line)
        if m:actual.append([int(m.group(1),16),bytes.fromhex(m.group(2)).hex()])
    expected=[[0x16896+r[0],code[r[0]:r[0]+r[1]].hex()] for r in decode(code)]
    need(actual==expected,'All93 actual LLVM addresses/widths/bytes equal linked code')
    return actual

def linked_contract(raw,original):
    e=E(raw);code=e.data('.spi_chain');sec=e.section('.spi_chain')
    need(e.header[0]==2 and sec['address']==0x16896 and len(code)==254,'Exact nominal EXEC254B extent at original PC')
    need(e.header[3]==0x16896 and sec['flags']==6 and sec['align']==2,'Original entry and exact AX/no-write code permissions')
    need([s['name'] for s in e.sections if s['size'] and s['flags']&2]==['.spi_chain'],'One owned allocated code section')
    loads=[p for p in e.program_headers if p[0]==1]
    need(loads and all(not(p[6]&2) for p in loads),'No writable load segment')
    cover=[p for p in loads if p[2]<=0x16896 and p[2]+p[4]>=0x16994]
    need(len(cover)==1 and cover[0][6]==5 and cover[0][1]+0x16896-cover[0][2]==sec['offset'],'Exact executable file-backed mapping')
    need(code==original,'All254 linked code bytes equal actual original; no pending immediate masks')
    need(not e.relocations,'No remaining control relocations')
    need(not [s for s in e.symbols if s['name'] and s['section']==0],'No undefined provider')
    need(not [s for s in e.symbols if s['section']==0xfff1 and s['info']>>4],'No fabricated global ABS provider')
    expected=[[n,0x16896+at,size] for n,at,size in zip(U['NAMES'],U['STARTS'],U['SIZES'])]
    expected += [[n,0x168de+at,size] for n,at,size in V['S']['regions']]
    actual=sorted([s for s in e.symbols if s['info']&15==2 and s['size']],key=lambda s:s['value'])
    need([[s['name'],s['value'],s['size']] for s in actual]==expected,'All28 genuine defined FUNCs have original extent/address')
    need(all(s['info']>>4==1 and s['section']==sec['index'] for s in actual),'Strong same-section definitions')
    rows=decode(code);need(len(rows)==93,'All93 complete typed instructions')
    calls=[r for r in rows if r[2]=='JAL']
    need(len(calls)==7 and all(r[3:]==[1,0x16896] for r in calls),'All seven real RA-linking calls resolve to genuine SPI body')
    return e,rows

def evaluate(folder,llvm,mode):
    original=(ROOT/U['FIRMWARE']).read_bytes()[0xe896:0xe994]
    need(len(original)==254,'Fresh original span')
    src=E(folder/'spi.o');U['elf_contract'](src,True)
    U['ir_contract']((folder/'spi.ll').read_text(),mode)
    md=(folder/'spi.d').read_text().replace('\\\n',' ').replace('\\\r\n',' ').replace('\\ ','\x01').replace('\\','/')
    target=str(folder/'spi.o').replace('\\','/')
    need(md.startswith(target+':'),'Actual SPI object MD target')
    deps=[x.replace('\x01',' ') for x in md[len(target)+1:].strip().split()]
    need(deps==[str(ROOT/U['SOURCE']).replace('\\','/'),str(llvm.parent/'lib/clang/18/include/stdint.h').replace('\\','/')],'Exact SPI source/header MD closure')
    raw=(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf').read_bytes();e,rows=linked_contract(raw,original)
    log=(folder/'nominal-read.log').read_text();read_rows=readback_contract(log,e.data('.spi_chain'))
    actual=load(folder/'recipes.json');expected=[dict(label=n,argv=a,returncode=0,consumed_inputs=consumed_inputs(n,folder,mode)) for n,a in recipes(folder,llvm,mode)]
    need(actual==portable(expected,llvm),'Four actual successful nominal build/read recipes')
    negative=[];sec=e.section('.spi_chain')
    for row in rows:
        b=bytearray(raw);b[sec['offset']+row[0]]^=0x80
        try:linked_contract(bytes(b),original)
        except (ValueError,KeyError,IndexError):negative.append('raw-original-byte-'+str(row[0]));continue
        raise ValueError('Changed instruction accepted')
    def rejects(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):negative.append(label);return
        raise ValueError('Negative accepted: '+label)
    changed=bytearray(raw);struct.pack_into('<I',changed,24,0x8000)
    rejects('wrong-entry',lambda:linked_contract(bytes(changed),original))
    changed=bytearray(raw);struct.pack_into('<I',changed,e.header[5]+sec['index']*40+8,7)
    rejects('writable-code-section',lambda:linked_contract(bytes(changed),original))
    line=next(l for l in log.splitlines() if re.match(r'^\s*16896:',l))
    rejects('LLVM-wrong-address',lambda:readback_contract(log.replace(line,line.replace('16896:','16898:'),1),original))
    rejects('LLVM-wrong-bytes',lambda:readback_contract(log.replace(line,line.replace('93 07','91 07'),1),original))
    return dict(language=mode,bytes=254,instructions=93,FUNC=28,strong_UND=0,pending_RELA=0,global_ABS=0,
        original_start='0x16896',original_end_exclusive='0x16994',whole_original_bytes_equal=True,
        ELF_sha256=sha(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'),SPI_native_sha256=sha(folder/'spi.o'),
        original_code_sha256=hashlib.sha256(original).hexdigest(),negative_controls=negative,
        exact_typed_rows=rows,actual_recipes=actual,
        complete_ELF_metadata=dict(header=e.header,program_headers=e.program_headers,sections=e.sections,symbols=e.symbols,relocations=e.relocations),
        full_LLVM_address_byte_rows=read_rows,
        artifacts={p.name:sha(p) for p in sorted(folder.iterdir()) if p.is_file() and p.name!='verification.json'},
        physical_MMIO_identity_confirmed=False,asynchronous_behavior_proved=False,full_image_proved=False,
        target_executed=False,ISA_emulated=False,hardware_tested=False,BIN_generated=False,firmware_ready=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out-dir',required=True,type=Path);p.add_argument('--build',action='store_true');p.add_argument('--strict-firmware',action='store_true');p.add_argument('--llvm-bin',type=Path,default=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin');a=p.parse_args();llvm=a.llvm_bin.resolve();out=a.out_dir.resolve();need(out.is_relative_to(HERE/'build') and out!=HERE/'build','Owned bounded output')
    before=snapshot(llvm);proofs=upstream(llvm)
    if a.build:need(not out.exists(),'Create-only nominal evidence')
    results=[]
    for mode in ('c','cpp'):
        folder=out/mode
        if a.build:
            folder.mkdir(parents=True);actual=[]
            for label,argv in recipes(folder,llvm,mode):
                used=consumed_inputs(label,folder,mode)
                child=subprocess.run(argv,cwd=ROOT,capture_output=True);(folder/(label+'.log')).write_bytes(child.stdout+child.stderr);actual.append(dict(label=label,argv=argv,returncode=child.returncode,consumed_inputs=used));need(child.returncode==0,'Nominal command failed: '+label)
            (folder/'recipes.json').write_bytes(encode(actual,llvm))
        value=evaluate(folder,llvm,mode);value['inputs']=before;value['upstream']=proofs
        need(snapshot(llvm)==before,'All nominal/dependency inputs unchanged')
        dest=folder/'verification.json';data=encode(value,llvm)
        if a.build:need(not dest.exists(),'Create-only nominal original receipt');dest.write_bytes(data)
        else:need(dest.read_bytes()==data,'Exact nominal original receipt read-only replay')
        results.append(dict(language=mode,receipt_sha256=hashlib.sha256(data).hexdigest(),ELF_sha256=value['ELF_sha256']))
    print(json.dumps(dict(passed=True,results=results,bytes=254,instructions=93,FUNC=28,pending_RELA=0,strong_UND=0,firmware_ready=False)))
    return 1 if a.strict_firmware else 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
