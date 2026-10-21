"""Static original callframe facts; no compiler or RV32 execution."""
from pathlib import Path
import hashlib,importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2]
SOURCE='apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/source/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
spec=importlib.util.spec_from_file_location('original_decoder',R/(SOURCE+'inspect-source.py'));D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
def jal(word,pc):
    need(word&127==111,'four-byte JAL opcode')
    rd=(word>>7)&31
    u=((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1)
    delta=u-(1<<21) if u&(1<<20) else u
    return rd,pc+delta,delta
def swsp(word):
    need(word&3==2 and word>>13==6,'C.SWSP encoding')
    return (word>>2)&31,(((word>>9)&15)<<2)|(((word>>7)&3)<<6)
def lwsp(word):
    need(word&3==2 and word>>13==2,'C.LWSP encoding')
    return (word>>7)&31,(((word>>12)&1)<<5)|(((word>>4)&7)<<2)|(((word>>2)&3)<<6)
def check(data,reference):
    groups=D.capture(data);need(groups==reference['groups'],'all264 source bytes/94 decoded instructions')
    rows=groups['entry_9a42'];need(len(rows)==46,'46 main boundaries')
    bypc={r['addr']:r for r in rows};boundaries=set(bypc)
    callfacts=[]
    for pc,target,mask,flag,address in [(0x9a5e,0x19142,0x02020006,1,0x4002101c),(0x9a6a,0x19124,0x101d,1,0x40021018),(0x9a74,0x1917e,0x02020006,1,0x40021010),(0x9a7e,0x1917e,0x02020006,0,0x40021010),(0x9a88,0x19160,0x101d,1,0x4002100c),(0x9a92,0x19160,0x101d,0,0x4002100c)]:
        row=bypc[pc];need(row['size']==4,'call exactly4B')
        rd,to,delta=jal(int.from_bytes(bytes.fromhex(row['bytes']),'little'),pc)
        need(rd==1 and to==target and pc+4 in boundaries,'direct call rdRA target and continuation')
        need(to==groups['rcc_'+format(target,'x')][0]['addr'],'target helper entry boundary')
        need(delta%2==0 and -(1<<20)<=delta<(1<<20),'JAL2byte alignment/range')
        callfacts.append(dict(site=pc,target=to,link=pc+4,displacement=delta,bytes=4,raw=row['bytes'],A0_mask=mask,A1_flag=flag,MMIO_address=address))
    stores=[(0x9a44,18,0),(0x9a46,1,12),(0x9a48,8,8),(0x9a4a,9,4)]
    loads=[(0x9ac6,1,12),(0x9ac8,8,8),(0x9aca,9,4),(0x9acc,18,0)]
    for pc,reg,slot in stores:need(swsp(int(bypc[pc]['bytes'][2:]+bypc[pc]['bytes'][:2],16))==(reg,slot),'saved frame role')
    for pc,reg,slot in loads:need(lwsp(int.from_bytes(bytes.fromhex(bypc[pc]['bytes']),'little'))==(reg,slot),'fresh restored frame role')
    need(bypc[0x9a42]['decoded']==['addi',2,2,-16] and bypc[0x9ace]['decoded']==['addi',2,2,16],'balanced16B frame')
    fixed={0x9a4c:['addi',18,0,136],0x9a50:['csrrc',0,0x800,18],0x9a54:['lui',9,0x02020000],0x9a62:['lui',8,0x1000],0x9ac2:['csrrs',0,0x800,18],0x9ad0:['jalr',0,1,0]}
    for pc,decoded in fixed.items():need(bypc[pc]['decoded']==decoded,'live constants/CSR/return')
    need(all(bypc[pc]['decoded']==['addi',10,9,6] for pc in [0x9a58,0x9a6e,0x9a78]),'three masks from S1')
    need(all(bypc[pc]['decoded']==['addi',10,8,29] for pc in [0x9a64,0x9a82,0x9a8e]),'three masks from S0')
    return dict(main_rows=rows,all_helper_rows={k:v for k,v in groups.items() if k!='entry_9a42'},calls=callfacts,
        frame=dict(bytes=16,base='SPentry-16',stores=[dict(site=p,register=r,offset=o) for p,r,o in stores],fresh_loads=[dict(site=p,register=r,offset=o) for p,r,o in loads],SPentry_alignment_proved_here=False),
        long_lived_constants=dict(S2=dict(value=136,definition=0x9a4c,uses=[0x9a50,0x9ac2]),S1=dict(value=0x02020000,definition=0x9a54,uses=[0x9a58,0x9a6e,0x9a78]),S0=dict(value=0x1000,definition=0x9a62,uses=[0x9a64,0x9a82,0x9a8e])))
def run():
    refs=[SOURCE+'final-audit.json',SOURCE+'retained-instructions.json',SOURCE+'inspect-source.py',SOURCE+'source-map.json',
      'apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/abi-review/verification.json',
      'apk-analysis/tsl9-v4160-clock-abi-2026-10-21/caller-review/verification.json',
      'apk-analysis/tsl9-v4160-irq-native-2026-10-21/abi-review/verification.json',
      'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin']
    need(sha(R/refs[0])=='4d6745033aae496576b9db2fb7467396fbfda5067713cf1451a34b949b414283','original immutable source seal')
    seal=json.loads((R/refs[0]).read_text())
    for f in seal['files']:need(sha(R/SOURCE/f['path'])==f['sha256'],'source seal member')
    data=(R/refs[-1]).read_bytes();need(hashlib.sha256(data).hexdigest()==D.IMAGE_SHA,'original BIN0ee pin')
    reference=json.loads((R/refs[1]).read_text());facts=check(data,reference)
    controls=[]
    for name,pc,replacement in [('wrong_saved_RA_slot',0x9a46,'06c4'),('wrong_S2_reload_slot',0x9acc,'1249'),('frame_size',0x9a42,'0111'),('wrong_call_RD_x0',0x9a5e,'6ff0406e'),('wrong_call_target',0x9a6a,'eff0a06a'),('S1_mask_base',0x9a54,'b7040302'),('S0_mask',0x9a64,'1305c401'),('CSR_set_source',0x9ac2,'73200880'),('return_other_register',0x9ad0,'0285'),('A1_finalflag',0x9a8c,'8545'),('tail_width',0x9aa8,'2392e742')]:
        mutated=bytearray(data);new=bytes.fromhex(replacement);mutated[pc-D.BASE:pc-D.BASE+len(new)]=new
        try:check(mutated,reference)
        except ValueError as exc:controls.append(dict(name=name,site=pc,rejected=True,reason=str(exc),replacement=replacement))
        else:raise ValueError('raw mutation accepted '+name)
    return dict(schema='TSL9-original-IRQ-callframe-source-plan-v1',passed=True,inputs=[dict(path=p,sha256=sha(R/p)) for p in refs],**facts,
      source_bytes=264,source_instructions=94,main_bytes=144,main_instructions=46,raw_mutation_controls=controls,
      normal_outputs=dict(A0='last fresh READ32(0x4002100c) & 0xffffefe2',A1=0,A4=128,A5=0xe000e000,A2_A3='untouched',S0_S1_S2_RA='fresh stack reloads; equal incoming only if saved words unchanged',SP='entry SP if intervening execution keeps frame base'),
      constraints=dict(C_call_pseudo_may_use8bytes_not_original4=True,actual_linked_call_encoding_required=True,original_144B_fit_not_yet_proved=True,exact_original_stack_traffic_not_proved_for_newC=True,asynchronous_IRQ_equivalence=False,ISA_execution=False,compilation=False,hardware=False,network=False,BIN_created=False))
if __name__=='__main__':
    result=run();p=H/'verification.json'
    if p.exists():need(json.loads(p.read_text())==result,'readonly replay exact')
    else:p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,main_bytes=144,main_instructions=46,source_bytes=264,source_instructions=94,calls=6,raw_mutations_rejected=11,verification_sha256=sha(p))))
