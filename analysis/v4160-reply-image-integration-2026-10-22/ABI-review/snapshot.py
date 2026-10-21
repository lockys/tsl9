#!/usr/bin/env python3
"""Create portable verification-only role expectations from sealed prior11 artifacts."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD='de1a55014e3db06fc909cadd92a746c9922b08bcdecfa0bcb28862f98d1f9ca0'
MANIFEST='09bfe0613a88a395b048a397530f62e49b199e890c3d2fc04285ca44887915fe'
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
REPLY='.text.tsl9v4160.ota_handler_9b8e'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();out=HERE/'baseline.json';need(not out.exists(),'Create-only independent baseline')
    previous=root/'apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py';need(sha(previous)==OLD,'Immutable generic role/LOAD/scatter helper');old=runpy.run_path(str(previous));parser=root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py';need(sha(parser)==PARSER,'Immutable bounded ELF parser');ELF=runpy.run_path(str(parser))['ELF']
    plan=HERE.parent/'image-plan/source-manifest.json';need(sha(plan)==MANIFEST,'New independently prepared12-owner plan');m=json.loads(plan.read_bytes());selected={r['name']:r for r in m['selected_sections']};need(len(selected)==12 and sum(r['bytes'] for r in selected.values())==650,'Twelve650-byte selected owners')
    prior=root/'experiments/tsl9-v4160-register-image-integration/build/formal-final/c';merged=ELF(prior/'source-integrated.o');linked=ELF(prior/'ADDRESS-WITNESS-ONLY.elf');need(sha(prior/'verification.json')=='c279758c4036d99417e0eface017b79f02ba2924d92ea9dbfcd84f05b0f0a5ec','Sealed actual prior11 producer receipt');need(hashlib.sha256(merged.raw).hexdigest()=='4e86cebc1119d30a726386cc520d73c5384920bb74bd97dbbc5dfa505c6bfbf2','Sealed actual prior11 merged ELF');need(hashlib.sha256(linked.raw).hexdigest()=='14046e6231cc8e5e25aa978e91ff3bc05509989a00f142d2adbaec971559f5e2','Sealed actual prior11 linked ELF')
    facts={}
    for name,s in old['alloc'](merged).items():
        row={k:s[k] for k in ('type','flags','size','alignment','entry_size','address')};row.update(originalVA=linked.byname[name]['address'],merged_sha256=hashlib.sha256(old['data'](merged,s)).hexdigest(),linked_sha256=hashlib.sha256(old['data'](linked,linked.byname[name])).hexdigest());facts[name]=row
    need(len(facts)==691,'Actual691 old allocation owners');outside=[old['relocation'](merged,r) for r in merged.relocations if r['owner'] not in selected];digest=hashlib.sha256(old['canonical'](sorted(outside,key=lambda r:json.dumps(r,sort_keys=True))).encode()).hexdigest();need(len(outside)==8257 and digest==m['retained_RELA_semantic_sha256'],'Independent actual8257 outside source roles')
    owned=[old['relocation'](merged,r) for r in merged.relocations if r['owner'] in selected and r['type']==17];need(len(owned)==12,'Actual prior11 plus originalreply TX12 JAL roles')
    incoming=[]
    for r in m['external_incoming_RELA']:
        owner=r['owner'];va=linked.byname[owner]['address'];jump=old['direct_jump'](old['data'](linked,linked.byname[owner]),r['offset'],va);target=selected[r['symbol']['owner']]['originalVA'];need(jump['target']==target,'Independent actual incoming target');incoming.append(jump)
    need(len(incoming)==21,'Twenty-one physical incoming sites');call=next(r for r in incoming if r['site']==0x9df4);need((call['raw_hex'],call['rd'],call['target'],call['link'])==('693b',1,0x9b8e,0x9df6),'Corrected actual C.JAL entry contract')
    globals=old['count'](old['role'](merged,s) for s in merged.symbols if s['name'] and s['info']>>4 in (1,2));globals[old['canonical'](dict(name='tsl9_ota_page_reply_9b8e',owner=REPLY,offset=0,bytes=124,info=18,other=0))]+=1
    locals=old['count'](r for r in old['regular_roles'](merged) if r['info']>>4==0);removed=old['canonical'](dict(name='.Lota_handler_00009bfa',owner=REPLY,offset=108,bytes=0,info=0,other=0));need(locals[removed]==1,'One actual private reply null label');locals[removed]-=1
    meta=old['metadata_counter'](merged);common=dict(owner=REPLY,offset=0,bytes=0,info=0,other=0);key=old['canonical'](dict(name='$d',**common));need(meta[key]==1,'One original reply raw mapping');meta[key]-=1;meta[old['canonical'](dict(name='$x',**common))]+=1
    for owner,name,info in [('.comment','$d',0),('ABS','$d',0),('ABS','page_reply.c',4)]:meta[old['canonical'](dict(name=name,owner=owner,offset=0,bytes=0,info=info,other=0))]+=1
    private=sorted({r['symbol']['name'] for r in m['old_selected_RELA'] if r['type'] in (16,44)});need(len(private)==11,'Eleven explicit private branch labels')
    value={'schema':'TSL9-twelve-owner-independent-source-baseline-v1','verification_only':True,'source_plan_sha256':MANIFEST,'prior_actual_merged_sha256':hashlib.sha256(merged.raw).hexdigest(),'prior_actual_linked_sha256':hashlib.sha256(linked.raw).hexdigest(),'prior_producer_receipt_sha256':sha(prior/'verification.json'),'sections':facts,'nonempty_unallocated_data_sha256':{s['name']:hashlib.sha256(merged.data(s)).hexdigest() for s in merged.sections if not s['flags']&2 and s['size'] and s['type'] not in(2,3,4)},'outside_RELA_count':len(outside),'outside_RELA_semantic_sha256':digest,'owned_JAL_RELA':owned,'incoming':sorted(incoming,key=lambda r:r['site']),'expected_global_role_digest':old['counter_digest'](+globals),'expected_local_role_digest':old['counter_digest'](+locals),'expected_metadata':dict(+meta),'discharged_private_names':private,'canonical_bindings':m['section_relative_bindings'],'new_public_reply_FUNC_role':dict(name='tsl9_ota_page_reply_9b8e',owner=REPLY,offset=0,bytes=124,info=18,other=0),'expected_nonempty_comment_mappings':43,'old_ARCH_or_ROM_identity_claimed':False,'hardware_OTA_validated':False}
    out.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'passed':True,'baseline_sha256':sha(out),'allocations':691,'outside_RELA':8257,'owned_JAL_RELA':12,'incoming':21}))
if __name__=='__main__':main()
