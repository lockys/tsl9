#!/usr/bin/env python3
"""Entire original530B raw/RELA contract; no target execution or emulator."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def validate(blob,decode,C):
    actual=C.rows(blob,decode);need(actual==read(HERE/'instructions.json'),'All169 original raw operand/order records');return actual
def controls(blob,decode,C):
    selected=[(0x9ca2,'immediate','strict W1026'),(0x9cfc,'immediate','W increment256 before callee'),(0x9d10,'rd','first Flash word read destination'),(0x9dd4,'immediate','R UID14'),(0x9e00,'immediate','strict E15'),(0x9da6,'rs2','S active takes postUID S1'),(0x9df4,'rd','page reply C.JAL link'),(0x9dac,'immediate','liveSP+12 reply pointer')];result=[]
    for pc,field,label in selected:
        before=decode(blob[pc-0x9c4a:],pc);found=None
        for bit in range(before['bytes']*8):
            changed=bytearray(blob);changed[pc-0x9c4a+bit//8]^=1<<(bit%8)
            try:r=decode(changed[pc-0x9c4a:],pc)
            except ValueError:continue
            if r['bytes']!=before['bytes'] or r[field] is None or r[field]==before[field]:continue
            if field=='memory_width':
                if r['op'] not in ('lw','lhu','lbu'):continue
            elif r['op']!=before['op']:continue
            if any(r[k]!=before[k] for k in ('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width') if k!=field):continue
            found=(bytes(changed),r,bit);break
        need(found is not None,'Actual decodable semantic control '+label);changed,r,bit=found
        try:validate(changed,decode,C)
        except ValueError:result.append(dict(PC=pc,case=label,field=field,bit=bit,original=before[field],mutated=r[field],rejected=True));continue
        raise ValueError('Accepted source operand counterexample '+label)
    return result
def inspect(root,firmware,objects=()):
    root=Path(root).resolve(strict=True);firmware=Path(firmware).resolve(strict=True)
    if (HERE/'seal.json').exists():
        for name,pin in read(HERE/'seal.json')['members'].items():need(sha(HERE/name)==pin,'Immutable handler source proof '+name)
    C=load('handler_source_capture_reader',HERE/'capture-source.py');decode,E=C.context(root)
    need(sha(firmware)==C.FW and firmware.stat().st_size==76800,'Actual official ID2966 source')
    fw=firmware.read_bytes();blob=fw[0x1c4a:0x1e5c];need(hashlib.sha256(blob).hexdigest()==C.BODY,'Original530B digest');actual=validate(blob,decode,C);by={r['PC']:r for r in actual}
    need(actual==load('handler_independent_text_fields',HERE/'llvm_fields.py').parse((HERE/'llvm-disassembly.txt').read_text(encoding='utf-8')),'Every raw operand independently equals retained actual LLVM text')
    capture=read(HERE/'capture.json');need(capture['firmware_sha256']==C.FW and capture['body_sha256']==C.BODY and capture['instructions']==169 and capture['exit']==0 and capture['static_only'],'Actual original capture identity')
    contract=read(HERE/'contracts.json');need(contract['entry']==0x9c4a and contract['end_exclusive']==0x9e5c and contract['instructions']==169 and len(contract['calls'])==13,'Whole original source contract')
    for c in contract['calls']:
        pc=int(c['PC'],16);r=by[pc];need(r['rd']==1 and pc+r['bytes']==int(c['RA'],16),'Every actual source call writes exact RA')
        if c['kind']=='direct':need(r['op']=='jal' and r['target']==int(c['target'],16),'Every actual source direct target')
        else:need(pc==0x9cec and r['op']=='jalr' and r['rs1']==15 and r['immediate']==0,'Only original indirect call via fresh slot A5')
    need(len([r for r in actual if r['op']=='jal' and r['rd']==1])==12 and [r['PC'] for r in actual if r['op']=='jalr']==[0x9c8a,0x9cec],'Exactly12 direct calls, one indirect call and one final JR')
    need(by[0x9df4]['raw_hex']=='693b' and (int.from_bytes(bytes.fromhex(by[0x9df4]['raw_hex']),'little')>>13)==1,'9DF4 actual compressed link bit, not inferred from RVC relocation type')
    for (reg,offset),pc in zip(contract['frame']['save_order'],contract['frame']['save_PCs']):r=by[pc];need((r['op'],r['rs1'],r['rs2'],r['immediate'],r['memory_width'])==('sw',2,reg,offset,32),'Exact7 physical save word order')
    for i,(reg,offset) in enumerate(contract['frame']['restore_order']):r=by[0x9c7a+i*2];need((r['op'],r['rd'],r['rs1'],r['immediate'],r['memory_width'])==('lw',reg,2,offset,32),'Exact7 fresh liveSP readbacks')
    need((by[0x9c4a]['rd'],by[0x9c4a]['rs1'],by[0x9c4a]['immediate'])==(2,2,-48) and (by[0x9c88]['rd'],by[0x9c88]['rs1'],by[0x9c88]['immediate'])==(2,2,48) and (by[0x9c8a]['rd'],by[0x9c8a]['rs1'])==(0,1),'Frame48 pop then fresh-RA return')
    for pair in contract['numeric_address_pairs']:
        pc=int(pair['PC'],16);hi,lo=by[pc],by[pc+4];need(hi['op']=='auipc' and lo['op']=='addi' and hi['rd']==lo['rd']==lo['rs1'] and (pc+hi['immediate']+lo['immediate'])&0xffffffff==int(pair['address'],16),'Four exact PC-relative numeric callback addresses, no execution')
    roles=read(HERE/'carrier-roles.json')['roles'];owned=[r for r in roles['RELA'] if r['owner']==C.OWNER];incoming=[r for r in roles['RELA'] if r['owner']!=C.OWNER];need(len(owned)==51 and len(incoming)==1 and all(r['addend']==0 for r in owned+incoming),'Exact carrier51 owned plus one recorded external role')
    layout=read(HERE/'owner-addresses.json');need(layout['linked_ELF_sha256']==capture['linked_ELF_sha256'],'Retained actual original numeric layout identity');bases=layout['addresses']
    for r in owned:
        source=by[0x9c4a+r['offset']]
        if r['type'] in (16,17,44,45):
            target=r['symbol'];need(source['target']==bases[target['owner']]+target['offset'],'Actual source direct target equals actual original owner/offset role')
        elif r['type']==23:
            lo=by[source['PC']+4];need((source['PC']+source['immediate']+lo['immediate'])&0xffffffff==bases[r['symbol']['owner']]+r['symbol']['offset'],'Actual PCREL pair equals the original target owner and offset')
        elif r['type']==24:
            need(r['symbol']['owner']==C.OWNER and 0x9c4a+r['symbol']['offset']==source['PC']-4 and by[source['PC']-4]['op']=='auipc','Actual LO role binds the preceding owner-local HI instruction')
        else:raise ValueError('Unreviewed original relocation kind')
    internal=[r for r in actual if r['target'] is not None and 0x9c4a<=r['target']<0x9e5c];need(len(internal)==31 and all(r['target'] in by for r in internal),'All31 internal edges target source instruction boundaries')
    inc=incoming[0];need((inc['owner'],inc['offset'],inc['type'],inc['symbol']['offset'],inc['symbol']['bytes'],inc['symbol']['info'])==('.text.tsl9v4160.gatt_ingress_13f7e',0x116,17,0,0,16),'Known external direct call role at14094, original NOTYPE0 entry')
    need(bases[inc['owner']]+inc['offset']==0x14094,'Actual incoming owner+offset is14094');call=decode(fw[0xc094:0xc098],0x14094);need(call['op']=='jal' and call['rd']==1 and call['target']==0x9c4a,'Actual incoming JAL links14098; not SDK-inferred')
    replay=[]
    for path in objects:
        path=Path(path).resolve(strict=True);e=E(path);need(e.kind==1 and e.data(e.byname[C.OWNER])==blob and C.object_roles(e)==roles,'Actual carrier raw530B and exact normalized roles');replay.append(dict(sha256=sha(path),passed=True))
    reconciliation=read(HERE/'source-reconciliation.json')
    for name,pin in reconciliation['source_files'].items():
        path=(root/name).resolve(strict=True);path.relative_to(root);need(sha(path)==pin,'Exact independently inspected frozen consumer source '+name)
    negative=controls(blob,decode,C)
    return dict(schema='ID2966-OTA-handler-source-review-v1',passed=True,raw_instructions=169,source_bytes=530,opaque_call_sites=13,direct_calls=12,indirect_calls=1,final_returns=1,internal_direct_edges=31,memory_instructions=sum(r['memory_width'] is not None for r in actual),owned_RELA=51,recorded_external_incoming=1,raw_semantic_controls=len(negative),page_reply_C_JAL_rd=by[0x9df4]['rd'],page_reply_RA=0x9df6,argument_write_PCs={str(reg):[r['PC'] for r in actual if r['rd']==reg] for reg in range(10,18)},explicit_GP_ports=[r for r in actual if 3 in (r['rd'],r['rs1'],r['rs2'])],source_operands_rechecked=True,actual_original_objects_replayed=len(replay),objects=replay,controls=negative,inspected_consumer_source_identities_checked=4,consumer_source_reconciliation_is_inspection_only=True,actual_native_or_HOST_replayed=False,whole_original_ABI_admitted=False,target_execution=False,ISA_emulation=False,network=False,hardware=False,OTA_ready=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);p.add_argument('--original-object',action='append',default=[],type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.original_object)))
