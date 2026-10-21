"""Bounded static byte/transcript checks, not an ISA evaluator or emulator."""
from pathlib import Path
import hashlib,importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
P='apk-analysis/tsl9-v4160-placement-2026-10-21/abi-review/audit.py'
spec=importlib.util.spec_from_file_location('sealed_static',R/P);M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
MAIN=bytes.fromhex('1307800873300780370502021905371702405c4f5d8d48cf854505657505371702401c4f5d8d08cf8545370502021905371702401c4b5d8d08cb8545370502021905b7170240984b1345f5ff798d88cb814505657505371702405c475d8d48c7854505657505b7170240d8471345f5ff798dc8c78145b7e500e0a3860542096793870510d8c3130700022382e5424147d8c313070003a383e54213070008d8c3130780087320078013070008b7e700e081458280')
def main_check(blob,base):
    need(len(blob)==180,'main180')
    rr=M.rows(blob,base);dest={r['destination'] for r in rr if r['destination'] is not None}
    need(dest=={10,11,14,15},'only A0/A1/A4/A5 destinations')
    need(blob[178:]==bytes.fromhex('8280'),'original RA return')
    need(blob[176:178]==bytes.fromhex('8145'),'final exact A1 zero')
    need(blob[168:172]==bytes.fromhex('13070008'),'final A4 128')
    need(blob[172:176]==bytes.fromhex('b7e700e0'),'final A5 e000e000')
    need(blob[:8]==bytes.fromhex('1307800873300780') and blob[160:168]==bytes.fromhex('1307800873200780'),'CSR800 clear/set mask88')
    need(blob[98:116]==bytes.fromhex('05657505b7170240d8471345f5ff798dc8c7'),'fresh last masked RMW')
    a0=[r for r in rr if r['destination']==10];need(a0[-1]['address']==base+112,'A0 not overwritten after final AND')
    need(blob[118:160]==MAIN[118:160],'six tail store widths/addresses/order')
    need(blob==MAIN,'all180 exact admitted native bytes')
    byoffset={r['address']-base:r for r in rr}
    effects=[dict(offset=4,kind='CSR_CLEAR',csr=0x800,value=0x88)]
    for read,write,address,op,mask in [(18,22,0x4002101c,'OR',0x02020006),(34,38,0x40021018,'OR',0x101d),(52,56,0x40021010,'OR',0x02020006),(70,78,0x40021010,'AND_NOT',0x02020006),(90,94,0x4002100c,'OR',0x101d),(106,114,0x4002100c,'AND_NOT',0x101d)]:
        effects += [dict(offset=read,kind='READ32',address=address),dict(offset=write,kind='WRITE32',address=address,expression=op,mask=mask)]
    effects += [dict(offset=o,kind=k,address=a,value=v) for o,k,a,v in [(122,'WRITE8',0xe000e42d,0),(132,'WRITE32',0xe000e104,0x2000),(138,'WRITE8',0xe000e424,0x20),(144,'WRITE32',0xe000e104,0x10),(150,'WRITE8',0xe000e427,0x30),(158,'WRITE32',0xe000e104,0x80)]]
    effects.append(dict(offset=164,kind='CSR_SET',csr=0x800,value=0x88))
    need(len(effects)==20 and [x['offset'] for x in effects]==sorted(x['offset'] for x in effects),'ordered20effect ledger')
    for effect in effects:effect.update(site=base+effect['offset'],raw=byoffset[effect['offset']]['raw'])
    return dict(bytes=180,instructions=len(rr),destinations=sorted(dest),rows=rr,static_effect_ledger=effects,
                final_A0_def=base+112,last_fresh_word_load=base+106,final_A1_def=base+176,final_A4_def=base+168,final_A5_def=base+172,
                transient_A1_address_scratch_site=base+118,normal_outputs=dict(A0='fresh READ32(0x4002100c) & ~0x101d',A1=0,A4=128,A5=0xe000e000))
def run():
    refs=[P,'apk-analysis/tsl9-v4160-reset-memory-2026-10-21/compiler-review/elf32.py',
       'experiments/tsl9-v4160-irq-native/src/interrupt_registers.c','experiments/tsl9-v4160-irq-native/src/native_io.h',
       'experiments/tsl9-v4160-interrupt-registers/src/interrupt_registers.h',
       'apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/abi-review/verification.json',
       'apk-analysis/tsl9-v4160-clock-abi-2026-10-21/caller-review/verification.json',
       'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin']
    binary=R/refs[-1];need(sha(binary)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','original source pin')
    raw=binary.read_bytes();expected={a:raw[a-0x8000:a-0x8000+30] for a in [0x19124,0x19142,0x19160,0x1917e]}
    results=[]
    for mode,folder in [('c','candidate-f6b889ced5854ef4a19b4b232fe80d98-c'),('cpp','candidate-3d6ab05fdb9d4ee2b1d2a54b0900b3d9-cpp')]:
        b='experiments/tsl9-v4160-irq-native/build/'+folder+'/'
        refs += [b+n for n in ['probe.json','COMPONENT-ONLY-NOT-FIRMWARE.elf','irq.ll','disassembly.log']]
        e=M.module.ELF(R/(b+'COMPONENT-ONLY-NOT-FIRMWARE.elf'))
        need(not e.relocations and not [s for s in e.symbols if s['name'] and s['index']==0],'no relocations or UND')
        need(not [s for s in e.sections if s['flags']&1 and s['flags']&2 and s['size']],'no writable allocations')
        funcs=[s for s in e.symbols if s['info']&15==2 and s['size']];need(len(funcs)==5,'no extra outlined functions')
        execs=[s for s in e.sections if s['flags']&4 and s['size']];need(len(execs)==1 and execs[0]['size']==300,'all300 executable bytes owned')
        addresses=[];ledger=[]
        for f in sorted(funcs,key=lambda f:f['value']):
            blob=e.function_bytes(f);addresses.extend(range(f['value'],f['value']+len(blob)))
            if 'rcc_registers' in f['name']:
                original=int(f['name'].rsplit('_',1)[1],16);need(blob==expected[original],'all helper bytes identical to original')
                rr=M.rows(blob,f['value']);need({r['destination'] for r in rr if r['destination'] is not None}=={10,14,15},'helper preserves A1/all other GPRs')
                ledger.append(dict(name=f['name'],native_address=f['value'],original_address=original,bytes=30,sha256=hashlib.sha256(blob).hexdigest(),raw=blob.hex(),rows=rr,exact_original_identity=True))
            else:ledger.append(dict(name=f['name'],native_address=f['value'],**main_check(blob,f['value'])))
        need(sorted(addresses)==list(range(execs[0]['address'],execs[0]['address']+300)),'no gaps/overlaps/hidden executable bytes')
        probe=json.loads((R/(b+'probe.json')).read_text());flags=probe['flags'];need('-Oz' in flags and '-enable-machine-outliner=never' in flags,'specific documented profile')
        need(all('-ffixed-x'+str(n) in flags for n in range(1,32) if n not in [10,11,14,15]),'all remaining registers fixed')
        results.append(dict(mode=mode,ELF_sha256=sha(R/(b+'COMPONENT-ONLY-NOT-FIRMWARE.elf')),functions=ledger,executable_bytes=300,profile=flags))
    negatives=[]
    for name,offset,replacement in [('A2_clobber',176,'0146'),('SP_clobber',176,'0141'),('return_wrong_register',178,'0285'),('A1_nonzero',176,'8545'),('A4_wrong',168,'13071008'),('A5_wrongbase',172,'b7f700e0'),('CSR_set_wrongmask',162,'9008'),('lost_final_fresh_load',106,'d843'),('final_A0_overwrite',176,'0145'),('tail_write_width',138,'2392e542')]:
        mutant=bytearray(MAIN);v=bytes.fromhex(replacement);mutant[offset:offset+len(v)]=v
        try:main_check(bytes(mutant),0x1078)
        except ValueError as ex:negatives.append(dict(name=name,rejected=True,gate=str(ex),offset=offset,raw=bytes(mutant).hex()))
        else:raise ValueError('mutant accepted '+name)
    helper=bytearray(expected[0x19124]);helper[2]^=1
    need(bytes(helper)!=expected[0x19124],'helper identity mutation rejected');negatives.append(dict(name='helper_changed_byte',rejected=True,gate='original exact byte identity',offset=2,raw=bytes(helper).hex()))
    return dict(schema='TSL9-IRQ-native-independent-ABI-review-v1',passed=True,
       inputs=[dict(path=p,sha256=sha(R/p)) for p in refs],modes=results,mutated_transcript_controls=negatives,
       source_callback_obligation='A3 query residue passes original9A42/1973C/9F4C to opaque131E0; callback consumption unknown',
       conclusions=dict(helper_original_exact_bytes=True,helper_A1_exact_bits_preserved=True,normal_main_outputs_match=True,unwritten_GPRs_preserved_including_A2_A3_SP_RA=True,
          main_original_pointwise_equivalence=False,asynchronous_IRQ_equivalence=False,original_stack_effects_equal=False,original_main_size=144,native_main_size=180,
          fits_original_main_extent=False,integrated_placement_proved=False,original_VA_link_performed_here=False,native_compilation_performed_here=False,RV32_executed=False,hardware=False,network=False,BIN_created=False))
if __name__=='__main__':
    result=run();p=H/'verification.json'
    if p.exists():need(json.loads(p.read_text())==result,'read-only replay exact')
    else:p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,modes=2,helper_identity_bytes_per_mode=120,main_bytes_per_mode=180,native_instructions_per_mode=113,mutated_transcripts_rejected=11,verification_sha256=sha(p))))
