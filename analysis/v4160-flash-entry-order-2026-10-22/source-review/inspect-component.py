#!/usr/bin/env python3
"""Independent static checks of the actual emitted component, never execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

RANGES=((0x9c0a,64,'quarter'),(0x18e90,8,'status'),(0x18e98,30,'unlock'),(0x18eb6,14,'lock'),(0x18ec4,46,'erase'),(0x18ef2,100,'program'))
OLD='1097156d90ee982a6c03c903785b563acae0357d1bbc7b7c2e29315adbf5d613'
NEW='aeccc19da9c5764a386333dd26898429c35bf0ff40efb08c8f8417b11820339d'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,slug):return next(p for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def program_contract(body,decoder):
    need(len(body)==100,'Natural whole100B program extent')
    rows=[];offset=0
    while offset<len(body):
        r=decoder.decode(body,0x8000+offset);rows.append(r);offset+=r['bytes']
    need(offset==100 and len(rows)==38,'All100bytes/38instructions parsed')
    by={r['PC']-0x8000:r for r in rows}
    need(by[0]['op']=='lui' and by[0]['rd']==14 and by[0]['immediate']==0x40022000,'Initial controller base')
    r=by[4];need((r['op'],r['rd'],r['rs1'],r['immediate'])==('lw',12,14,16),'Fresh initialCTRL read before alignment')
    r=by[6];need((r['op'],r['rd'],r['rs1'],r['immediate'])==('andi',10,10,-256),'Actual fixedA0 alignment between initial read and write')
    r=by[14];need((r['op'],r['rs1'],r['rs2'],r['immediate'])==('sw',14,12,16),'FirstCTRL write after alignment')
    need(8 not in by,'Originaloffset8 is not silently advertised as a valid new boundary')
    branches=[r for r in rows if r['op']=='bne']
    need(sorted(r['target']-0x8000 for r in branches)==[16,26,40,56,82],'All five known original private loop roles retain their exact target offsets')
    expected=[('and',14,14,13,None),('sw',None,15,14,16),('ret',None,1,None,None)]
    need([(by[o]['op'],by[o]['rd'],by[o]['rs1'],by[o]['rs2'],by[o]['immediate']) for o in (94,96,98)]==expected,'Live final mask/store/RET at original tail addresses')
    need(all(r['rd'] is None or r['rd'] in (0,10,12,13,14,15,16) for r in rows),'Source-allowed program destination register set')
    pcs=set(by);reachable=set();pending=[0]
    while pending:
        pc=pending.pop()
        if pc in reachable:continue
        need(pc in pcs,'All static CFG successors are instruction boundaries');reachable.add(pc);r=by[pc]
        if r['op']=='ret':continue
        need(r['op']!='jal','No hidden direct call in program')
        pending.append(pc+r['bytes'])
        if r['op']=='bne':pending.append(r['target']-0x8000)
    need(reachable==pcs,'Every emitted instruction belongs to the admitted static CFG')
    return {'bytes':100,'instructions':38,'first_read_offset':4,'A0_alignment_offset':6,'first_store_offset':14,'original_alignment_offset':8,'known_program_interior_offsets':[16,26,40,56,82],'tail_raw':body[-6:].hex(),'all_CFG_nodes_reachable':True,'full_original_boundary_set_preserved':False,'full_scratch_GPR_prefix_equivalence':False}
def analyze(root,oldpath,newpath):
    need(sha(oldpath)==OLD and sha(newpath)==NEW,'Exact actual old/new component ELFs')
    parser=case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py'
    need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Pinned bounded ELF parser')
    decode_path=case(root,'v4160-flash-native-2026-10-22')/'source/inspect.py'
    need(sha(decode_path)=='4ae4c3f5eaa0076adcdc153cc87468b2c032b94e76c083ecc7b7b5d9fd251702','Pinned static integer decoder')
    E=module('entry_components_elf',parser).ELF;decoder=module('entry_components_raw',decode_path)
    old=E(oldpath);new=E(newpath);functions=[]
    need(new.kind==2 and new.flags==1,'Linked RV32 integer component')
    alloc=[s for s in new.sections if s['flags']&2 and s['size']]
    need(len(alloc)==6 and sum(s['size'] for s in alloc)==262 and all(s['flags']==6 for s in alloc),'Exactly six executable extents, no padding/storage allocation')
    bodies={}
    for address,size,name in RANGES:
        symbol='tsl9_flash_'+name+'_'+format(address,'x')
        a=next(s for s in old.symbols if s['name']==symbol);b=next(s for s in new.symbols if s['name']==symbol)
        oldbody=old.function_bytes(a);body=new.function_bytes(b);bodies[name]=body
        need(b['value']==address and b['size']==size and b['info']&15==2,'Actual typed FUNC at original entry with exact extent')
        same=body==oldbody
        need(same==(name!='program'),'Only the intended program native body changes')
        functions.append({'name':name,'address':address,'bytes':size,'sha256':hashlib.sha256(body).hexdigest(),'byte_identical_to_prior_component':same})
    contract=program_contract(bodies['program'],decoder);negatives=[]
    for label,offset,delta in (('wrong_A0_alignment',9,8),('wrong_tail_CTRL_store',96,4),('wrong_copy_backedge',65,1)):
        changed=bytearray(bodies['program']);changed[offset]^=delta
        try:program_contract(changed,decoder)
        except ValueError:negatives.append({'case':label,'offset':offset,'xor':delta,'rejected':True})
        else:raise ValueError('Actual native semantic byte control accepted '+label)
    return {'schema':'ID2966-independent-100B-component-static-review-v1','passed':True,'old_component_sha256':OLD,'new_component_sha256':NEW,'functions':functions,'program':contract,'raw_native_semantic_controls':negatives,'full_image_integration':False,'target_execution':False,'ISA_emulation':False,'hardware':False,'OTA_ready':False}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--old-component',required=True,type=Path);p.add_argument('--new-component',required=True,type=Path);p.add_argument('--output',type=Path);p.add_argument('--reference',type=Path);a=p.parse_args();r=analyze(a.project_root.resolve(strict=True),a.old_component,a.new_component)
    if a.reference:need(r==json.loads(a.reference.read_text(encoding='utf-8')),'Bound actual static component review')
    if a.output:
        output=a.output.resolve();output.relative_to(Path(__file__).resolve().parent);need(not output.exists(),'Create-only own result');output.write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'passed':True,'bytes':262,'program_bytes':100,'unchanged_native_functions':5,'new_program_controls':3,'target_execution':False}))
if __name__=='__main__':main()
