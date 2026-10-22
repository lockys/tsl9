#!/usr/bin/env python3
"""Selected raw operand/use-def proof; never execute or simulate target code."""
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FW = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SOURCE_SEAL = 'f42e262c6b6c7a80fa3da77ce6af0b0df7ad70f6a8c9ff664b5eefa940554972'
REGISTER_SEAL = 'b49115005675a962220ed18fc416ebb0aaad6875b3994e301bd9f415b12939f3'

def need(v, m):
    if not v: raise ValueError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_bytes())
def load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def case(root, name):
    return next(p for p in (root/'analysis'/name, root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def closed(folder, pin):
    need(sha(folder/'seal.json') == pin, 'Pinned immutable review seal')
    for n, h in read(folder/'seal.json')['members'].items(): need(sha(folder/n) == h, 'Immutable member '+n)
def row_fields(r): return [r[k] for k in ('op','rd','rs1','rs2','immediate','target','memory_width')]
def rows(blob, entry, decode):
    result=[]; at=0
    while at < len(blob):
        r=decode(blob[at:],entry+at); need(at+r['bytes']<=len(blob),'Whole selected instruction'); result.append(r); at+=r['bytes']
    return result

ORIGINAL = [
    ['addi',15,3,None,0,None,None], ['lhu',15,15,None,42,None,16],
    ['addi',12,0,None,0,None,None], ['mv',11,9,None,None,None,None],
    ['sh',None,9,15,0,None,16], ['lw',15,23,None,212,None,32],
    ['mv',10,21,None,None,None,None], ['jalr',1,15,None,0,None,None],
    ['bne',None,10,0,None,0x87cc,None],
]
NATIVE = [
    ['lh',10,3,None,42,None,16], ['sh',None,19,10,0,None,16],
    ['lui',24,None,None,0x40000,None,None], ['lw',15,24,None,212,None,32],
    ['mv',10,18,None,None,None,None], ['mv',11,19,None,None,None,None],
    ['addi',12,0,None,0,None,None], ['jalr',1,15,None,0,None,None],
    ['beq',None,10,0,None,0x1254,None],
]
def original_gate(selected):
    need([row_fields(r) for r in selected] == ORIGINAL, 'Exact original GP datum/store/target-kill/call/branch operands')
    need([r['PC'] for r in selected] == [0x87fc,0x8800,0x8804,0x8806,0x8808,0x880c,0x8810,0x8812,0x8814], 'Exact original instruction anchors')
    datum, store, kill, call = selected[1], selected[4], selected[5], selected[7]
    need(datum['rd']==store['rs2']==kill['rd']==call['rs1']==15, 'A5 datum consumed by SH then killed by fresh target LW')
    need(not any(r['rd'] in (13,14,16,17) for r in selected), 'A3/A4/A6/A7 untouched in this straight-line window')
    return dict(datum_register='A5/x15',datum_PC=0x8800,store_PC=0x8808,kill_PC=0x880c,call_PC=0x8812,call_RA=0x8814,datum_live_at_call=False,unwritten_argument_registers=['A3','A4','A6','A7'])

def controls(blob, decode):
    # Three decodable field changes, rejected by the local semantic gate, not a hash gate.
    cases=[]
    for pc, field, value, label in [(0x8800,'rd',14,'datum moved to A4'),(0x8808,'rs2',14,'store consumes stale A4'),(0x880c,'immediate',216,'target slot D4 changed to D8')]:
        raw=bytearray(blob); at=pc-0x87fc; w=int.from_bytes(raw[at:at+4],'little')
        shift,bits={'rd':(7,5),'rs2':(20,5),'immediate':(20,12)}[field]
        raw[at:at+4]=((w&~(((1<<bits)-1)<<shift))|(value<<shift)).to_bytes(4,'little')
        changed=rows(bytes(raw),0x87fc,decode)
        need(next(r for r in changed if r['PC']==pc)[field]==value, 'Actual decodable intended operand control')
        try: original_gate(changed)
        except ValueError as e: cases.append(dict(case=label,PC=pc,field=field,rejected=True,reason=str(e))); continue
        raise ValueError('Accepted local def/use/kill counterexample')
    return cases

def inspect(root, firmware, component=None):
    root=Path(root).resolve(strict=True); firmware=Path(firmware).resolve(strict=True)
    if (HERE/'seal.json').exists():
        for n,h in read(HERE/'seal.json')['members'].items(): need(sha(HERE/n)==h,'Immutable frontier review member '+n)
    old=case(root,'v4160-event-callback-2026-10-22')/'source-review'; closed(old,SOURCE_SEAL)
    reg=case(root,'v4160-callback-registers-2026-10-22')/'source-review'; closed(reg,REGISTER_SEAL)
    S=load('frontier_original_fields',old/'check-source.py'); decode,E=S.context(root)
    need(sha(firmware)==FW and firmware.stat().st_size==76800,'Exact official ID2966 base8000 source')
    fw=firmware.read_bytes(); contract=read(old/'contracts.json'); retained={r['PC']:r for r in read(old/'instructions.json')}; calls=[]
    # Reuse the authoritative assigned_args/residue contract; no duplicate table or old 217/26 matrix.
    for c in contract['opaque_calls']:
        pc=int(c['PC'],16); r=decode(fw[pc-0x8000:pc-0x8000+4],pc)
        need(r==retained[pc] and (r['op'],r['rd'],r['rs1'],r['immediate'])==('jalr',1,16 if pc==0x886a else 15,0),'Actual selected JALR fields equal the closed call contract')
        need(pc+r['bytes']==int(c['link'],16),'Actual call width and raw RA')
        calls.append(dict(PC=pc,RA=pc+r['bytes'],target_register=r['rs1'],authoritative_contract_pointer='contracts.json#/opaque_calls/'+str(len(calls))))
    need(len(calls)==15,'All fifteen existing call records reused')
    before=rows(fw[0x7c8:0x7cc],0x87c8,decode)
    need([row_fields(r) for r in before]==[['andi',10,10,None,1,None,None],['bne',None,10,0,None,0x87fc,None]],'Post87C6 low-bit predicate enters original datum block without writing A3/A4/A6/A7')
    window=fw[0x7fc:0x816]; selected=rows(window,0x87fc,decode); fact=original_gate(selected); negative=controls(window,decode)
    findings=read(HERE/'findings.json'); need(findings['original_use_def_kill']==fact,'Reviewed source use-def-kill finding')
    current=root/'experiments/tsl9-v4160-callback-registers/src'
    for n,h in findings['current_source_pins'].items(): need(sha(current/n)==h,'Exact current C bridge source identity')
    text=(current/'callback.c').read_text(encoding='utf-8')
    need('CB_READ(h,0x8800u,CB_GP(h)+0x2au,16,v);a[1]=s->record;a[2]=0u;CB_WRITE(h,0x8808u,s->record,16,v);CB_READ(h,0x880cu,s->rom_base+0xd4u,32,target);a[0]=s->connection;CB_CALL(h,0x8812u,target,5,7u);' in text,'Current C passes datum only through low16 store then separate target')
    result=dict(schema='ID2966-callback-call-frontier-use-def-v1',passed=True,official_firmware_read=True,selected_original_call_sites_redecoded=15,old217_instruction_matrix_rerun=False,old26_controls_rerun=False,new_operand_controls=len(negative),original_use_def_kill=fact,reused_authoritative_assigned_args=15,actual_candidate_artifact_read=False,whole_call_ABI_proved=False,ROM_S7_preservation_proved=False,physical_fault_async_prefix_equal=False,HOST_tests_rerun=False,target_execution=False,ISA_emulation=False,network=False,hardware=False,calls=calls,controls=negative)
    if component:
        component=Path(component).resolve(strict=True); expected=read(reg/'selected-results.json')['c']['after']; need(sha(component)==expected['ELF_sha256'],'Exact previously reviewed actual624 component')
        e=E(component); s=next(s for s in e.symbols if s['name']=='tsl9_callback_native_8614'); body=e.function_bytes(s)
        need(s['value']==0x1000 and s['size']==len(body)==624 and hashlib.sha256(body).hexdigest()==expected['body_sha256'],'Complete actual native624 identity')
        def native_decode(raw,pc):
            w=int.from_bytes(raw[:4],'little')
            if len(raw)>=4 and w&127==3 and (w>>12)&7==1:
                immediate=w>>20; immediate=immediate-4096 if immediate&2048 else immediate
                return dict(PC=pc,bytes=4,raw_hex=raw[:4].hex(),op='lh',rd=(w>>7)&31,rs1=(w>>15)&31,rs2=None,immediate=immediate,target=None,memory_width=16)
            return decode(raw,pc)
        branch=rows(body[0x202:0x20a],0x1202,native_decode)
        need([row_fields(r) for r in branch]==[['andi',10,10,None,1,None,None],['addi',19,23,None,-2,None,None],['beq',None,10,0,None,0x1224,None]],'Candidate low-bit predicate enters datum block on complementary fallthrough; no A3/A4/A6/A7 write')
        candidate=rows(body[0x20a:0x224],0x120a,native_decode); need([row_fields(r) for r in candidate]==NATIVE,'Actual624 local store/kill/call and complementary branch operands')
        need(not any(r['rd'] in (13,14,16,17) for r in candidate),'Actual A3/A4/A6/A7 are untouched in the corresponding window')
        local=dict(actual_candidate_artifact_read=True,component_sha256=sha(component),datum_register='A0/x10',native_datum_PC=0x120a,native_store_PC=0x120e,native_datum_kill_PC=0x121a,native_call_PC=0x1220,native_RA=0x1222,projected_RA_at_original_entry=0x8614+(0x1222-0x1000),source_RA=0x8814,call_RA_projection_equal=False,datum_live_at_call=False,low16_datum_store_equivalence=True,call_target_address_equality_requires_live_S7_equals_0x40000=True,candidate_rows=candidate)
        result.update(local)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--project-root',required=True,type=Path); p.add_argument('--firmware',required=True,type=Path); p.add_argument('--component',type=Path); a=p.parse_args()
    print(json.dumps(inspect(a.project_root,a.firmware,a.component)))
