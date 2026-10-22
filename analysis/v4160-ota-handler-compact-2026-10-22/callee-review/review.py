#!/usr/bin/env python3
"""Bounded App UID and two candidate copy bodies, only static operand data."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
OLD_SEAL='7e32146e97e26f74eefa36fa8d8eab4d558dd1deae37e88bef8ccc4d8b059615'
ENTRY_SEAL='98e510f983b9c81feed31b4b64fa8f3ba07d733d4c0979c1dd1ab47ebdb688ae'
COPY_SHA='558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def closed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact prior evidence seal')
    d=read(folder/'seal.json')
    for n,h in d.get('members',d.get('files',{})).items():need(sha(folder/n)==(h if isinstance(h,str) else h['sha256']),'Immutable reference member '+n)
def context(root):
    old=case(root,'v4160-ota-handler-2026-10-22')/'source-review';closed(old,OLD_SEAL);C=load('compact_prior_source_capture',old/'capture-source.py');previous,E=C.context(root)
    def decode(raw,pc):
        if raw[:4]==bytes.fromhex('0f100000'):
            return dict(PC=pc,bytes=4,raw_hex='0f100000',op='fence.i',rd=None,rs1=None,rs2=None,immediate=None,target=None,memory_width=None)
        return previous(raw,pc)
    return decode,E,load('compact_existing_LLVM_text_fields',old/'llvm_fields.py').parse
def rows(blob,entry,decode):
    result=[];offset=0
    while offset<len(blob):
        r=decode(blob[offset:],entry+offset);need(offset+r['bytes']<=len(blob),'Whole bounded instruction');result.append(r);offset+=r['bytes']
    return result
def signature(r):return [r[k] for k in ('PC','op','rd','rs1','rs2','immediate','target','memory_width')]
def validate(blob,entry,decode,expected):
    result=rows(blob,entry,decode);need(result==expected,'All retained raw operand rows');return result
def candidate_inputs(root,refs=None):
    folder=Path(refs).resolve(strict=True) if refs else case(root,'wch-resident-candidate-2026-10-21')
    closed(folder/'resident-entry',ENTRY_SEAL);reference=read(folder/'resident-entry/contract.json');pins=read(HERE/'reference-pins.json');result=[]
    main=reference['entry']['word_copy_contracts'][0];historical=reference['historical_mapped_callee_comparison']
    layouts=[('carrier',main['source']['start'],main['destination_start']),('carrier-dec2023',historical['copy_source'],historical['copy_destination'])]
    for name,source,destination in layouts:
        pin=pins['candidate_files'][name];segment=folder/name/pin['segment'];hexfile=folder/pin['hex']
        need(sha(segment)==pin['segment_sha256'] and sha(hexfile)==pin['hex_sha256'],'Pinned existing sparse source and captured contiguous segment')
        data=segment.read_bytes();slot=data[0x4c:0x50];target=int.from_bytes(slot,'little');need(target==0x20000332,'Actual candidate slot4004C word')
        flash=source+(target-destination);need(flash==pin['mapped_flash_entry'],'Candidate-specific initialization mapping, not common flash offset')
        at=flash-0x40000;body=data[at:at+58];need(hashlib.sha256(body).hexdigest()==COPY_SHA,'Complete58B candidate copy body')
        result.append(dict(candidate=name,slot=0x4004c,raw_target=target,source_flash_entry=flash,source_flash_end=flash+58,RAM_entry=target,RAM_end=target+58,body_sha256=COPY_SHA,body=body))
    need(result[0]['body']==result[1]['body'],'Two bounded mapped candidate bodies exactly agree')
    return result
def local_contract(app,copy):
    b={r['PC']:r for r in app};c={r['PC']:r for r in copy}
    for pc,rd,rs1,imm in [(0x92ba,2,2,-16),(0x92ee,2,2,16),(0x92f8,2,2,-32),(0x9328,2,2,32)]:need((b[pc]['op'],b[pc]['rd'],b[pc]['rs1'],b[pc]['immediate'])==('addi',rd,rs1,imm),'Exact App frame changes')
    for pc,reg,offset in [(0x92bc,9,4),(0x92c4,8,8),(0x92ca,18,0),(0x92cc,1,12),(0x92fa,8,24),(0x9300,1,28)]:need((b[pc]['op'],b[pc]['rs1'],b[pc]['rs2'],b[pc]['immediate'])==('sw',2,reg,offset),'Actual interleaved saved words')
    for pc,reg,offset in [(0x92dc,8,8),(0x92e2,1,12),(0x92e4,9,4),(0x92ea,18,0),(0x9324,1,28),(0x9326,8,24)]:need((b[pc]['op'],b[pc]['rd'],b[pc]['rs1'],b[pc]['immediate'])==('lw',reg,2,offset),'Fresh saved words with original interleaving')
    need((b[0x92be]['op'],b[0x92be]['rd'],b[0x92be]['immediate'])==('lui',9,0x40000) and (b[0x92c6]['op'],b[0x92c6]['rd'],b[0x92c6]['immediate'])==('lui',8,0x1ffff000),'Original resident/factory numeric bases')
    need((b[0x92ce]['op'],b[0x92ce]['rd'],b[0x92ce]['rs1'],b[0x92ce]['immediate'])==('addi',11,8,0x7ec),'First copy source numeric1FFFF7EC')
    need((b[0x92f2]['rd'],b[0x92f2]['immediate'])==(15,14) and (b[0x92f4]['op'],b[0x92f4]['rs1'],b[0x92f4]['rs2'],b[0x92f4]['target'])==('bne',11,15,0x9330),'Comparator full length14 pre-frame gate')
    need((b[0x9302]['op'],b[0x9302]['rd'],b[0x9302]['target'])==('jal',1,0x92ba) and b[0x9302]['bytes']==2,'Actual comparator C.JAL links9304')
    need((b[0x930c]['op'],b[0x930c]['rd'],b[0x930c]['rs1'])==('lbu',12,14) and (b[0x9314]['op'],b[0x9314]['rd'],b[0x9314]['rs1'])==('lbu',14,14),'Input byte before fresh liveSP byte in comparator')
    need((b[0x92c2]['op'],b[0x92c2]['rd'],b[0x92c2]['rs1'],b[0x92c2]['immediate'])==('lw',15,9,76) and (b[0x92de]['op'],b[0x92de]['rd'],b[0x92de]['rs1'],b[0x92de]['immediate'])==('lw',6,9,76),'Two independent liveS1 slot loads; second target inT1')
    need((b[0x92d2]['rd'],b[0x92d2]['immediate'])==(12,8) and (b[0x92ec]['rd'],b[0x92ec]['immediate'])==(12,6),'8-byte first and6-byte tail copy counts')
    need((b[0x92d6]['op'],b[0x92d6]['rd'],b[0x92d6]['rs1'])==('jalr',1,15) and (b[0x92f0]['op'],b[0x92f0]['rd'],b[0x92f0]['rs1'])==('jalr',0,6),'First linked slot call92D8 then genuine tail viaT1')
    need((b[0x92d8]['rd'],b[0x92d8]['rs1'],b[0x92d8]['immediate'])==(11,8,0x7e8) and (b[0x92e6]['rd'],b[0x92e6]['rs1'],b[0x92e6]['immediate'])==(10,18,8),'Tail source/destination use post-first-call liveS0/liveS2')
    need(not any(r['rd'] in (3,16,17) for r in app),'No explicit App GP/A6/A7 writes; no transitive preservation inference')
    need(len(copy)==18 and copy[-1]['PC']==0x2000036a and copy[-1]['target']==0x2000034a,'Bounded58B leaf complete loop/exit geometry')
    need(not any(r['rd'] in (1,2,3,4,8,9,17,18,19,20,21,22,23,24,25,26,27) for r in copy),'No candidate explicit RA/SP/GP/TP/S/A7 writes')
    need(not any(r['rd'] in (10,11,12) for r in copy),'Candidate leaves destination/source/count unchanged, not Boolean status')
    need(not any(r['op']=='jal' and r['rd']==1 or r['op']=='jalr' and r['rd']==1 for r in copy),'No transitive calls in these candidate58B')
    need((c[0x20000336]['op'],c[0x20000336]['rd'],c[0x20000336]['immediate'])==('lw',14,0x20c) and c[0x2000033e]['op']=='fence.i' and c[0x2000034e]['rs2']==14,'Candidate MMIO save/zero/fence/restore obligation')
    need((c[0x20000332]['op'],c[0x20000332]['rd'],c[0x20000332]['immediate'])==('lui',15,0x40024000) and (c[0x2000033a]['op'],c[0x2000033a]['rs1'],c[0x2000033a]['rs2'],c[0x2000033a]['immediate'])==('sw',15,0,0x20c),'Exact MMIO zero before argument tests')
    need((c[0x20000358]['op'],c[0x20000358]['rd'],c[0x20000358]['memory_width'])==('lbu',16,8) and (c[0x20000362]['op'],c[0x20000362]['rs2'],c[0x20000362]['memory_width'])==('sb',16,8),'Candidate source LBU precedes destination SB')
    starts=set(c);need(all(r['target'] is None or r['target'] in starts for r in copy),'Complete candidate local direct CFG')
    return dict(comparator_bytes=66,builder_bytes=56,candidate_copy_bytes=58,candidate_copy_instructions=18,App_live_GP_written=False,App_A6_A7_written=False,candidate_direct_calls=0,candidate_own_S_GP_SP_RA_writes=False,installed_candidate_identity_proved=False)
def controls(blob,entry,decode,expected,selections):
    result=[]
    for pc,field,label in selections:
        before=decode(blob[pc-entry:],pc);found=None
        for bit in range(before['bytes']*8):
            raw=bytearray(blob);raw[pc-entry+bit//8]^=1<<(bit%8)
            try:r=decode(raw[pc-entry:],pc)
            except ValueError:continue
            if r['bytes']!=before['bytes'] or r[field] is None or r[field]==before[field]:continue
            if any(r[k]!=before[k] for k in ('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width') if k!=field):continue
            found=(bytes(raw),r,bit);break
        need(found is not None,'Decodable single-field counterexample '+label);raw,r,bit=found
        try:validate(raw,entry,decode,expected)
        except ValueError:result.append(dict(case=label,PC=pc,field=field,bit=bit,original=before[field],mutated=r[field],rejected=True));continue
        raise ValueError('Accepted callee operand control')
    return result
def inspect(root,firmware,refs=None,original_object=None):
    root=Path(root).resolve(strict=True);firmware=Path(firmware).resolve(strict=True)
    if (HERE/'seal.json').exists():closed(HERE,sha(HERE/'seal.json'))
    need(sha(firmware)==FW and firmware.stat().st_size==76800,'Exact original ID2966')
    decode,E,parse=context(root);fw=firmware.read_bytes();app=fw[0x12ba:0x1334];expected=read(HERE/'app-instructions.json');a=validate(app,0x92ba,decode,expected)
    need(a==parse((HERE/'app-llvm.txt').read_text(encoding='utf-8')),'All App fields independently equal staticLLVM text')
    candidates=candidate_inputs(root,refs);copy=candidates[0]['body'];c=validate(copy,0x20000332,decode,read(HERE/'copy-instructions.json'));facts=local_contract(a,c)
    contract=read(HERE/'contracts.json');need(contract['confirmed_App']['builder']['bytes']==56 and contract['confirmed_App']['comparator']['bytes']==66 and contract['conditional_candidates_only']['body_sha256']==COPY_SHA and not contract['installed_resident_identity_proved'],'Reviewed App/candidate distinction and bounded extents')
    negative=controls(app,0x92ba,decode,expected,[(0x92f2,'immediate','UID strict14'),(0x9302,'rd','builder link versus no-link'),(0x92de,'rs1','fresh second slot base'),(0x92ec,'immediate','tail length6')])
    negative+=controls(copy,0x20000332,decode,c,[(0x2000034e,'rs2','restore actual saved MMIO word'),(0x20000358,'rd','source byte feeds storeA6')])
    actual_object=False
    if original_object:
        e=E(Path(original_object).resolve(strict=True));need(e.kind==1,'Actual App carrier object');roles=read(HERE/'app-carrier.json');need(capture_roles(e)==roles['roles'],'Exact bounded App owners/symbols/RELA')
        need(e.data(e.byname['.text.tsl9v4160.direct_closure_92ba'])==app[:56] and e.data(e.byname['.text.tsl9v4160.ota_handler_92f2'])==app[56:],'Actual App carrier matches original122B');actual_object=True
    return dict(schema='ID2966-UID-callee-static-review-v1',passed=True,metadata_only=False,actual_original_firmware_read=True,App_instruction_rows=len(a),App_bytes=len(app),actual_candidate_source_bodies_read=2,candidate_copy_rows=len(c),candidate_body_pins_checked=True,raw_operand_controls=len(negative),raw_operand_controls_replayed=True,actual_App_carrier_replayed=actual_object,callee_facts=facts,candidate_sources=[{k:v for k,v in x.items() if k!='body'} for x in candidates],controls=negative,dropping_ambient_args_authorized=False,installed_resident_identity_proved=False,transitive_original_ABI_proved=False,target_execution=False,ISA_emulation=False,HOST_or_compiler_run=False,network=False,hardware=False)
def capture_roles(e):
    names=['.text.tsl9v4160.direct_closure_92ba','.text.tsl9v4160.ota_handler_92f2'];indices={e.byname[n]['index'] for n in names}
    def role(s):return dict(name=s['name'],owner=e.sections[s['index']]['name'] if 0<s['index']<len(e.sections) else 'ABS' if s['index']==65521 else 'UND',offset=s['value'],bytes=s['size'],info=s['info'],other=s['other'])
    return dict(owners=[{k:e.byname[n][k] for k in ('name','type','flags','size','alignment')} for n in names],symbols=sorted([role(s) for s in e.symbols if s['index'] in indices],key=lambda x:json.dumps(x,sort_keys=True)),RELA=sorted([dict(owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend'],symbol=role(r['symbol'])) for r in e.relocations if r['owner'] in names or r['symbol']['index'] in indices],key=lambda x:json.dumps(x,sort_keys=True)))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);p.add_argument('--candidate-root',type=Path);p.add_argument('--original-object',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.candidate_root,a.original_object)))
