"""Static byte/register/layout audit; no target execution or image generation."""
import hashlib, importlib.util, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def need(x,m):
    if not x: raise ValueError(m)

PARSER='apk-analysis/tsl9-v4160-reset-memory-2026-10-21/compiler-review/elf32.py'
spec=importlib.util.spec_from_file_location('bounded_elf',ROOT/PARSER)
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

def rd(raw):
    v=int.from_bytes(raw,'little')
    if len(raw)==4:
        op=v&127
        if op in (3,19,23,51,55,103,111,115): return ((v>>7)&31) or None
        if op in (35,99): return None
    else:
        q=v&3; f=v>>13
        if q==0 and f==2: return 8+((v>>2)&7)
        if q==0 and f==6: return None
        if q==1 and f in (0,2,3): return ((v>>7)&31) or None
        if q==1 and f==4: return 8+((v>>7)&7)
        if q==1 and f in (5,6,7): return None
        if q==1 and f==1: return 1
        if q==2 and f==2: return ((v>>7)&31) or None
        if q==2 and f==6: return None
        if q==2 and f==4:
            rs2=(v>>2)&31
            if rs2: return ((v>>7)&31) or None
            return 1 if ((v>>12)&1) else None
    raise ValueError('unsupported destination encoding '+raw.hex())

def rows(blob,base):
    out=[]; off=0
    while off<len(blob):
        size=4 if blob[off]&3==3 else 2
        raw=blob[off:off+size]; need(len(raw)==size,'whole instruction')
        out.append(dict(address=base+off,raw=raw.hex(),destination=rd(raw)))
        off+=size
    return out

def jal0(a,b):
    delta=b-a; need(delta%2==0 and -(1<<20)<=delta<(1<<20),'JAL displacement')
    u=delta&0x1fffff
    v=0x6f|((u>>20)<<31)|(((u>>1)&1023)<<21)|(((u>>11)&1)<<20)|(((u>>12)&255)<<12)
    back=((v>>31)<<20)|(((v>>21)&1023)<<1)|(((v>>20)&1)<<11)|(((v>>12)&255)<<12)
    if back&(1<<20): back-=1<<21
    need(a+back==b and ((v>>7)&31)==0 and rd(v.to_bytes(4,'little')) is None,'JAL x0 roundtrip')
    return dict(site=a,target=b,raw=v.to_bytes(4,'little').hex(),writes_gpr=False)

def run():
    refs=[PARSER,
      'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
      'apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/abi-review/verification.json',
      'apk-analysis/tsl9-v4160-clock-abi-2026-10-21/caller-review/verification.json',
      'apk-analysis/tsl9-v4160-reset-memory-2026-10-21/caller-review/verification.json',
      'experiments/tsl9-v4160-startup/build/image-fidelity-999d8125159a4d80bd6df9153f267002/original-image-layout.ld',
      'experiments/tsl9-v4160-startup/build/image-fidelity-999d8125159a4d80bd6df9153f267002/verification.json']
    binary=ROOT/refs[1]; need(sha(binary)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','source pin')
    full=(ROOT/refs[5]).read_text(); need(full.count('ASSERT(SIZEOF(')==691,'691 owned size assertions')
    original=load(refs[2]); source=[]
    for extent in original['ranges']:
        rr=[]
        for r in extent['rows']:
            raw=bytes.fromhex(r['bytes']); need(binary.read_bytes()[r['addr']-0x8000:r['addr']-0x8000+len(raw)]==raw,'source bytes')
            rr.append(dict(address=r['addr'],raw=raw.hex(),destination=rd(raw)))
        source.append(dict(start=extent['start'],bytes=extent['byte_count'],destinations=sorted({r['destination'] for r in rr if r['destination'] is not None}),rows=rr))
    native=[]
    for mode,folder in [('c','native-5ff4800bb3334e60881a75b9e0b0490d-c'),('cpp','native-47be327990f2428a9b86bbd1b0561b47-cpp')]:
        base='apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/native-plan/build/'+folder+'/'
        for name in ['verification.json','COMPONENT-ONLY-NOT-FIRMWARE.elf','interrupt_init.ll','component-disassembly.log']: refs.append(base+name)
        elf=module.ELF(ROOT/(base+'COMPONENT-ONLY-NOT-FIRMWARE.elf'))
        funcs=[]
        for sym in elf.symbols:
            if sym['info']&15!=2 or not sym['size']: continue
            rr=rows(elf.function_bytes(sym),sym['value']); dest=sorted({r['destination'] for r in rr if r['destination'] is not None})
            expected=[10,11,12,13,14] if 'interrupt_init' in sym['name'] else [10,12,13]
            need(dest==expected,'native IRQ destination set')
            funcs.append(dict(name=sym['name'],bytes=sym['size'],destinations=dest,rows=rr))
        need(len(funcs)==5,'five native functions'); native.append(dict(mode=mode,functions=funcs))
    extents=[(0x186ba,62),(0x18834,174),(0x1973c,40),(0x9a42,144),(0x19124,30),(0x19142,30),(0x19160,30),(0x1917e,30)]
    transports=[jal0(a,b) for a,_ in extents for b,_ in extents if a!=b]
    result=dict(schema='TSL9-placement-ABI-counterevidence-v1',passed=True,
      inputs=[dict(path=r,sha256=sha(ROOT/r)) for r in refs],original_irq=source,native_irq=native,
      source_pool=[dict(start=a,bytes=n) for a,n in extents],pool_bytes=sum(n for _,n in extents),
      jal_x0_transport_checks=transports,
      original_main_normal_outputs={'a0':'last fresh READ32(0x4002100c) & 0xffffefe2','a1':0,'a2':'unchanged','a3':'unchanged','a4':128,'a5':0xe000e000},
      old_native_main_normal_outputs={'a0':'last fresh READ32(0x4002100c) & 0xffffefe2','a1':136,'a2':0xe000e000,'a3':128,'a4':0x101d,'a5':'unchanged'},
      original_helper_normal_outputs={'a0':'enabled ? before | mask : before & ~mask','a1':'incoming exact bits','a2':'unchanged','a3':'unchanged','a4':'enabled ? 0x40021000 : before','a5':'enabled ? before : 0x40021000'},
      old_native_helper_normal_outputs={'a0':'same RMW result','a1':'incoming exact bits','a2':0x40021000,'a3':'before','a4':'unchanged','a5':'unchanged'},
      conclusions={'old_irq_118_22_abi_compatible':False,'old_irq_savings_available_as_proved_slack':False,'query196_contiguous_fit_in_pool':False,'transport_encodings_only':True,'integrated_layout_proved':False,'full_original_abi_proved':False,'irq_asynchronous_equivalence_proved':False,'original_or_rebuilt_rv32_executed':False,'new_firmware_bin_created':False,'hardware_tested':False})
    need(result['pool_bytes']==540 and len(transports)==56,'pool and transport count')
    return result

if __name__=='__main__':
    result=run(); out=HERE/'verification.json'
    if out.exists(): need(json.loads(out.read_text(encoding='utf-8'))==result,'read-only replay exact result')
    else: out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,pool_bytes=540,native_modes=2,functions_per_mode=5,jal_x0_checks=56,verification_sha256=sha(out))))
