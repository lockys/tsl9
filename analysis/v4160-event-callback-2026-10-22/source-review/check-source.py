#!/usr/bin/env python3
"""Official callback raw/contract proof, optional original carrier role readback."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BODY='3e21432057f673abea404541e0745937d894448b492478b5fed5775e91b398bf'
OWNER='.text.tsl9v4160.callback_8614'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def context(root):
    p=case(root,'v4160-ota-tx-2026-10-22')/'source-review/raw.py';q=case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py';need(sha(p)=='da17e505ec2b58cada40a80a12a645b7fa21c116ce76666544168f2c4ff6c6a7' and sha(q)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Immutable raw-field/ELF readers');base=load('event_original_base',p).decode;extensions=load('event_new_fields',HERE/'raw.py');return lambda raw,pc:extensions.decode(raw,pc,base),load('event_original_ELF',q).ELF
def signature(r):return {k:v for k,v in r.items() if k!='raw_hex'}
def validate(blob,decode):
    need(len(blob)==632,'Entire callback extent632');expected=read(HERE/'instructions.json');actual=[];at=0
    while at<len(blob):r=decode(blob[at:],0x8614+at);actual.append(r);at+=r['bytes']
    need(len(actual)==217 and at==632 and [signature(r) for r in actual]==[signature(r) for r in expected],'All217 independently retained raw operand records');return actual
def controls(blob,decode):
    selections=[(0x8614,'immediate'),(0x8616,'immediate'),(0x861a,'rs2'),(0x8630,'op'),(0x8634,'op'),(0x8646,'memory_width'),(0x864e,'target'),(0x8656,'immediate'),(0x8662,'immediate'),(0x866c,'immediate'),(0x8686,'immediate'),(0x8694,'rs2'),(0x86ae,'memory_width'),(0x86d4,'immediate'),(0x86e4,'rs2'),(0x86e8,'rs2'),(0x86f6,'op'),(0x86fa,'op'),(0x871a,'op'),(0x87a2,'rd'),(0x87a4,'rs2'),(0x87c8,'immediate'),(0x881a,'memory_width'),(0x8824,'memory_width'),(0x8862,'immediate'),(0x8884,'rs1')];rows=[]
    for pc,field in selections:
        before=decode(blob[pc-0x8614:],pc);found=None
        for bit in range(before['bytes']*8):
            raw=bytearray(blob);raw[pc-0x8614+bit//8]^=1<<(bit%8)
            try:changed=decode(raw[pc-0x8614:],pc)
            except ValueError:continue
            if changed['bytes']!=before['bytes'] or changed[field]==before[field] or changed[field] is None:continue
            if field=='op':
                if changed['op']!={'srai':'srli','bge':'bgeu','blt':'bltu'}[before['op']]:continue
            elif field=='memory_width':
                if (before['op'].startswith('l') and changed['op'] not in ('lw','lbu','lhu')) or (before['op'].startswith('s') and changed['op'] not in ('sw','sb','sh')):continue
            elif changed['op']!=before['op']:continue
            found=(bytes(raw),changed,bit);break
        need(found is not None,'Actual decodable field mutation at '+hex(pc));raw,changed,bit=found
        try:validate(raw,decode)
        except ValueError:rows.append(dict(PC=pc,field=field,bit=bit,original=before[field],mutated=changed[field],rejected=True));continue
        raise ValueError('Accepted raw semantic control '+hex(pc))
    return rows
def role(e,s):return dict(name=s['name'],owner=e.sections[s['index']]['name'] if 0<s['index']<len(e.sections) else 'ABS' if s['index']==65521 else 'UND',offset=s['value'],bytes=s['size'],info=s['info'],other=s['other'])
def object_roles(e):
    s=e.byname[OWNER];rs=[dict(owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend'],symbol=role(e,r['symbol'])) for r in e.relocations if r['owner']==OWNER or r['symbol']['index']==s['index']]
    return dict(owner_metadata={k:s[k] for k in ('name','type','flags','size','alignment')},owner_symbols=sorted([role(e,x) for x in e.symbols if x['index']==s['index']],key=lambda r:json.dumps(r,sort_keys=True)),RELA=sorted(rs,key=lambda r:json.dumps(r,sort_keys=True)))
def inspect(root,firmware,objects=()):
    root=Path(root).resolve(strict=True);firmware=Path(firmware).resolve(strict=True);decode,E=context(root)
    if (HERE/'seal.json').exists():
        for name,pin in read(HERE/'seal.json')['members'].items():need(sha(HERE/name)==pin,'Immutable callback source proof '+name)
    need(sha(firmware)==FW and firmware.stat().st_size==76800,'Exact official ID2966 original');blob=firmware.read_bytes()[0x614:0x88c];actual=validate(blob,decode);need(hashlib.sha256(blob).hexdigest()==BODY,'Original callback byte digest')
    text=load('event_independent_LLVM_syntax',HERE/'llvm_fields.py').parse((HERE/'llvm-disassembly.txt').read_text(encoding='utf-8'));need(actual==text,'All raw fields independently equal retained LLVM operands');capture=read(HERE/'capture.json');need(capture['firmware_sha256']==FW and capture['slice_sha256']==BODY and capture['instructions']==217 and capture['exit']==0 and capture['static_only'],'Retained actual independent LLVM capture provenance');negative=controls(blob,decode);contract=read(HERE/'contracts.json');by={r['PC']:r for r in actual};need(len(contract['opaque_calls'])==15,'Explicit15 named call contracts')
    for c in contract['opaque_calls']:
        pc=int(c['PC'],16);r=by[pc];need((r['op'],r['rd'],pc+r['bytes'])==('jalr',1,int(c['link'],16)),'Every opaque call width/rd/raw link')
    for pair in contract['numeric_address_pairs']:
        pc=int(pair['PC'],16);hi=by[pc];lo=by[pc+4];need(hi['op']=='auipc' and lo['op']=='addi' and hi['rd']==lo['rd']==lo['rs1'] and (pc+hi['immediate']+lo['immediate'])&0xffffffff==int(pair['address'],16),'Static PC-relative address pair, no execution')
    starts=set(by);edges=[]
    for r in actual:
        if r['target'] is not None:need(r['target'] in starts,'All26 direct targets are known instruction starts');edges.append(dict(PC=r['PC'],op=r['op'],target=r['target'],normal_fallthrough=r['PC']+r['bytes'] if r['op']!='jal' else None))
    need(len(edges)==26 and sum(r['memory_width'] is not None for r in actual)==64,'Exact control/memory inventory')
    for (register,offset),pc in zip(contract['frame']['save_order'],contract['frame']['save_PC_order']):r=by[pc];need((r['op'],r['rs1'],r['rs2'],r['immediate'],r['memory_width'])==('sw',2,register,offset,32),'Exact physical save order')
    for i,(register,offset) in enumerate(contract['frame']['restore_order']):r=by[0x866c+2*i];need((r['op'],r['rd'],r['rs1'],r['immediate'],r['memory_width'])==('lw',register,2,offset,32),'Fresh live-SP restore order')
    ref=read(HERE/'carrier-roles.json');allr=ref['roles']['RELA'];owned=[r for r in allr if r['owner']==OWNER];incoming=[r for r in allr if r['owner']!=OWNER];need(len(owned)==36 and len(incoming)==3 and all(r['addend']==0 for r in allr),'Exact original role counts/addends')
    control=[r for r in owned if r['type'] in (16,44,45)];anchors=[r for r in owned if r['type']==24];need(len(control)==26 and len(anchors)==5 and sum(r['type']==23 for r in owned)==5,'26control and5HI/LO pairs')
    for r in control:
        source=by[0x8614+r['offset']];need(source['target']==0x8614+r['symbol']['offset'],'Raw edge and actual original private-role target agree')
    need(all(r['type']==23 and r['symbol']['name']=='__tsl9v4160_address_8614' and (r['symbol']['offset'],r['symbol']['bytes'],r['symbol']['info'])==(0,0,16) for r in incoming),'Three address materializations, not inferred direct incoming execution')
    replayed=[]
    for p in objects:
        p=Path(p).resolve(strict=True);e=E(p);need(e.kind==1 and e.data(e.byname[OWNER])==blob and object_roles(e)==ref['roles'],'Actual original carrier632B/role/RELA readback');replayed.append(dict(sha256=sha(p),passed=True))
    reconciliation=read(HERE/'source-reconciliation.json')
    for name,pin in reconciliation['source_files'].items():p=(root/name).resolve(strict=True);p.relative_to(root);need(sha(p)==pin,'Read-only reconciled frozen model source '+name)
    return dict(passed=True,original_bytes=632,raw_instructions=217,direct_control_edges=26,memory_instructions=64,opaque_calls=15,raw_semantic_controls_rejected=len(negative),known_external_address_RELA=3,known_direct_call_incoming_RELA=0,owned_RELA=36,private_control_target_roles=19,private_PCREL_anchor_roles=5,actual_original_objects_replayed=len(replayed),actual_current_model_source_identity_checked=4,actual_native_or_HOST_replayed=False,whole_original_ABI_admitted=False,source_operands_rechecked=True,target_execution=False,ISA_emulation=False,network=False,hardware=False,controls=negative,objects=replayed)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);p.add_argument('--original-object',action='append',default=[],type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.original_object)))
