#!/usr/bin/env python3
"""Independent actual full-image contracts with one non-identical TX allocation."""
import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import runpy
import struct
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
BASELINE='8dc4c64aa66aff78b4d47a773976488d0f344f340ae5bc164f196c451a24ac19'
NATIVE='24ade8f364d00cbc6c7afc2239f13d67fef4f6822647fc4525c05cd9e64bd5eb'
LOOP='cc505e92d084b2e0fe2bb33bfd53161c5ca1fc9c0892da0711b04b696ebba1df'
IMAGE='NOT-FLASH-VALIDATED-tx-integrated.bin'
# Verification-only hashes measured from the sealed, source-owned component.
# They are never supplied to the assembler/compiler/linker or used to generate bytes.
APPROVED_PARTS=('487c6497a4cdd3be5d1018e698b41718911d4f4e55c950749df0587a5b69fb99',
                '6b32a70463cc9d98649a492e3eb3de0b357d546093cf70fb15111a335a93c0d6',
                '7529d4e6ceb037815e2664a7277abb404b02f0bf9ddbf5c11658f52448221cba')
APPROVED_LINKED='8b129d84cbd65062315ec8197f7cbabb0eae7a4dfec4dca5bf39861851a525b9'


def setup(root,firmware):
    b=runpy.run_path(str(HERE/'base.py'));c=b['context'](root)
    b['need'](b['sha'](HERE/'baseline.json')==BASELINE,'Pinned verification-only twelve-region baseline')
    b['need'](b['sha'](firmware)==b['FW'] and firmware.stat().st_size==76800,'Original firmware is validation-only')
    c.update(b=b,baseline=json.loads((HERE/'baseline.json').read_bytes()),root=root,
             original=firmware.read_bytes())
    c['native']=b['pinned'](b['case'](root,'v4160-ota-tx-2026-10-22')/'ABI-review/native.py',NATIVE)
    c['raw_context']=c['native']['context'](root,firmware)
    c['loop']=b['pinned'](b['case'](root,'v4160-tx-register-abi-2026-10-22')/'ABI-review/loop.py',LOOP)
    return c


def allocated(merged,linked,c):
    b=c['b'];need=b['need'];old=c['old'];ref=c['baseline']['sections']
    ma=old['alloc'](merged);la=old['alloc'](linked)
    need(merged.kind==1 and linked.kind==2 and merged.flags==linked.flags==1,'Actual ET_REL/EXEC RVC pair')
    need(len(merged.byname)==len(merged.sections) and len(linked.byname)==len(linked.sections),'Unique section owner names')
    need(set(ma)==set(la)==set(ref) and len(ma)==691,'Exactly all691 original allocation owners')
    for name,base in ref.items():
        need(all(ma[name][key]==value for key,value in base['attributes'].items()),'Partial owner attributes '+name)
        want=dict(base['attributes'],address=base['originalVA'])
        need(all(la[name][key]==value for key,value in want.items()),'Linked owner attributes/address '+name)
        if name!=b['TX']:
            need(b['H'](old['data'](merged,ma[name]))==base['partial_sha256'] and
                 b['H'](old['data'](linked,la[name]))==base['linked_sha256'],
                 'All690 non-TX partial/linked owners retain actual previous bytes '+name)
    return dict(allocations=691,non_TX_allocation_owners_preserved=690,
                retained_raw_allocation_owners=678,prior_twelve_typed_owners_preserved=12)


def provider_metadata(folder,c):
    b=c['b'];need=b['need'];E=c['ELF'];extra=[];signatures=[];facts=[]
    for name in ('tx-entry.o','tx-valid_body-ordered.o','tx-return_leaf.o'):
        e=E(folder/name);roles=b['roles'](e,c)
        attributes=[r for r in roles if r['owner']=='.riscv.attributes' and r['name']=='$d']
        need(len(attributes)==1 and all(attributes[0][k]==0 for k in ('offset','bytes','info','other')),
             'One actual attribute marker per TX provider')
        extra.append(dict(attributes[0],owner='ABS'))
        for role in roles:
            if role['info']==4:
                need(role['owner']=='ABS' and role['offset']==role['bytes']==role['other']==0 and
                     role['name'] in ('valid_body.c','return_leaf.c'),'Actual new C FILE provenance')
                extra.append(role)
            if role['owner']=='.comment' and role['name']=='$d':
                need(all(role[k]==0 for k in ('offset','bytes','info','other')),'Actual unreferenced comment marker')
                extra.append(role)
        sig=e.byname.get('.llvm_addrsig');payload=e.data(sig) if sig else b''
        if payload:
            need(name=='tx-valid_body-ordered.o' and len(payload)==1 and payload[0]<128 and
                 sig['type']==0x6fff4c03 and sig['flags']==0x80000000 and sig['link'] in e.symbol_tables,
                 'Only genuine scoped body address-significance payload')
            s=e.symbol_tables[sig['link']][payload[0]]
            need((s['info'],s['other'],s['value'],s['size'])==(2,0,0,270) and
                 e.sections[s['index']]['name']=='.text.tsl9_tx_valid_body',
                 'Input addrsig actually identifies local allocated FUNC270')
        signatures.append(payload)
        facts.append(dict(name=name,sha256=b['sha'](folder/name),attribute_marker_count=1,
                          input_addrsig_hex=payload.hex()))
    need(len(extra)==7 and sum(1 for r in extra if r['info']==4)==2,'Exactly3attribute/2comment/2FILE additions')
    return extra,b''.join(signatures),facts


def symbol_roles(merged,linked,folder,c):
    b=c['b'];need=b['need'];old=c['old'];baseline=c['baseline'];TX=b['TX']
    extra,suffix,providers=provider_metadata(folder,c)
    outside=[r for r in b['roles'](merged,c) if r['owner']!=TX]
    expected=Counter(dict(baseline['outside_TX_roles_counter']));expected.update(b['count'](extra))
    need(b['count'](outside)==expected,'All non-TX roles preserved plus only measured provider metadata')
    tx=[r for r in b['roles'](merged,c) if r['owner']==TX]
    body_name='tsl9_tx_valid_body' if any(r['name']=='tsl9_tx_valid_body' for r in tx) else '_ZL18tsl9_tx_valid_bodyjjjj'
    def r(name,offset,size=0,info=0):
        return dict(name=name,owner=TX,offset=offset,bytes=size,info=info,other=0)
    wanted=[r('',0,info=3),r(b['CANONICAL'],0,8,18),r(body_name,8,270,2),
            r('tsl9_tx_oversized_return',278,2,18),r('.Lpcrel_hi0',128),
            r('$x',0),r('$x',8),r('$x',278)]
    need(b['count'](tx)==b['count'](wanted),'Exactly8 truthful allocated TX roles; no FUNC280 or ABS stand-in')
    source=b['roles'](merged,c);expected_link=[]
    for role in source:
        role=dict(role)
        if role['info']==3 or (role['owner']=='.comment' and role['name']=='$d' and not role['info']):
            continue  # Actual linker drops SECTION/comment-mapping metadata, not allocated providers.
        if role['owner']=='UND':
            if not role['name']:
                expected_link.append(role);continue
            need(role['name']=='__tsl9v4160_rom_entry' and role['info']==16 and role['offset']==0,
                 'Only retained numeric ROM witness may remain unresolved in partial image')
            role.update(owner='ABS',offset=0x40000)
        expected_link.append(role)
    need(b['count'](b['roles'](linked,c))==b['count'](expected_link),
         'All linked named roles follow actual section-relative providers; only explicit metadata retirement/ROM witness')
    for binding in baseline['canonical_bindings']:
        expected_role=copy.deepcopy(binding['role'])
        if binding['name']==b['CANONICAL']:
            expected_role['bytes']=8
        need(b['count'](old['role'](merged,s) for s in merged.symbols if s['name']==binding['name'])==
             b['count']([expected_role]),'Canonical binding remains allocated and source-owned '+binding['name'])
    for name,old_payload in baseline['nonallocated_payloads'].items():
        need(name in merged.byname,'Retained compiler metadata section '+name)
        section=merged.byname[name];payload=merged.data(section)
        need(all(section[k]==v for k,v in old_payload['attributes'].items()),'Compiler metadata attributes '+name)
        if name=='.llvm_addrsig':
            prefix=payload[:old_payload['bytes']]
            need(b['H'](prefix)==old_payload['sha256'] and payload[old_payload['bytes']:]==suffix and len(suffix)==1,
                 'Retained57B scoped address-significance prefix plus actual1B provider suffix')
            need(name not in linked.byname,'Excluded address-significance metadata not a linked provider')
        else:
            need(b['H'](payload)==old_payload['sha256'],'Other compiler metadata payload unchanged '+name)
    return dict(outside_roles_preserved=True,TX_roles=wanted,canonical_bindings=53,
                honest_entry_FUNC_bytes=8,actual_provider_parts=[8,270,2],
                metadata_additions=extra,metadata_provider_inputs=providers,
                address_significance_prior_bytes=57,address_significance_new_bytes=1)


def relocations(merged,linked,c):
    b=c['b'];need=b['need'];old=c['old'];baseline=c['baseline'];TX=b['TX']
    outside,projected=b['non_TX_relocations'](merged,c,8)
    need(len(outside)==8258 and b['digest'](outside)==baseline['non_TX_RELA_projected_digest'],
         'All8258 non-TX relocation roles identical after only explicit incoming target size280-to8 projection')
    owned=[old['relocation'](merged,r) for r in merged.relocations if r['owner']==TX]
    need(len(owned)==3 and sorted(r['type'] for r in owned)==[16,23,24] and
         len(merged.relocations)==8261 and not linked.relocations,'New full-image actual8261 RELAs')
    branch=next(r for r in owned if r['type']==16);hi=next(r for r in owned if r['type']==23);lo=next(r for r in owned if r['type']==24)
    need((branch['offset'],branch['addend'])==(4,0) and branch['symbol']==
         dict(name='tsl9_tx_oversized_return',owner=TX,offset=278,bytes=2,info=18,other=0),
         'Actual entry relocation targets real allocated typed RET')
    need((hi['offset'],hi['addend'])==(128,0) and hi['symbol']==
         dict(name='__tsl9v4160_data_2000b18c',owner='.bss.tsl9v4160.ram',offset=29068,bytes=0,info=16,other=0),
         'RAM HI targets actual allocated RAM alias, not component numeric ABS witness')
    need((lo['offset'],lo['addend'])==(132,0) and lo['symbol']==
         dict(name='.Lpcrel_hi0',owner=TX,offset=128,bytes=0,info=0,other=0),
         'RAM LO references genuine same-owner AUIPC anchor')
    return dict(total_RELA=8261,non_TX_RELA=8258,TX_RELA=3,outside_thirteen_regions_RELA=8246,
                owned_thirteen_regions_RELA=15,incoming_size_projection=projected,
                actual_RAM_allocated_provider=True)


def incoming(linked,c):
    b=c['b'];need=b['need'];old=c['old'];result=[]
    for expected in c['baseline']['incoming']:
        owner=next(s for s in old['alloc'](linked).values() if s['address']<=expected['site']<s['address']+s['size'])
        actual=old['direct_jump'](linked.data(owner),expected['site']-owner['address'],owner['address'])
        need(actual==expected,'Actual incoming width/rd/target/RA/raw preserved at '+hex(expected['site']))
        result.append(actual)
    selected=set(c['baseline']['twelve_typed_owners'])|{b['TX']}
    inside=[r for r in result if any(s['name'] in selected and
            s['address']<=r['site']<s['address']+s['size'] for s in old['alloc'](linked).values())]
    need(len(result)==30 and [r['site'] for r in inside]==[0x9be0],
         'Recorded30 boundary refs:29 outside selected owners and one selected page-reply call')
    return result


def tx_machine(merged,linked,folder,c):
    b=c['b'];need=b['need'];TX=b['TX'];E=c['ELF'];n=c['native'];raw=c['raw_context']
    providers=[]
    for name in ('tx-entry.o','tx-valid_body-ordered.o','tx-return_leaf.o'):
        e=E(folder/name);owners=[s for s in e.sections if s['flags']&2 and s['size']]
        need(len(owners)==1,'One allocated source extent per new TX provider')
        providers.append(e.data(owners[0]))
    need([len(p) for p in providers]==[8,270,2] and merged.data(merged.byname[TX])==b''.join(providers),
         'Partial TX bytes are exact fresh assembly/ordered-C/real-C-return concatenation')
    need(tuple(b['H'](part) for part in providers)==APPROVED_PARTS,
         'Actual fresh provider code matches the independently reviewed source-owned component, not original bytes')
    partial=merged.data(merged.byname[TX]);body=linked.data(linked.byname[TX]);rows=n['rows'](body,raw)
    need(b['H'](body)==APPROVED_LINKED,'Linked compound provider retains reviewed non-original machine bytes')
    need(len(rows)==96 and rows[0]['op']=='addi' and(rows[0]['rd'],rows[0]['rs1'],rows[0]['immediate'])==(15,0,1039),
         'Actual aggregate96 instruction bytes and entry limit')
    need(rows[1]['op']=='bltu' and(rows[1]['rs1'],rows[1]['rs2'],rows[1]['target'])==(15,13,0x8b6c),
         'Actual early unsigned guard reaches typed RET before frame')
    need(rows[2]['op']=='addi' and(rows[2]['rd'],rows[2]['rs1'],rows[2]['immediate'])==(2,2,-32),
         'Immediate source-owned entry fallthrough to typed frame')
    need([(r['op'],r['rs2'],r['rs1'],r['immediate'],r['bytes']) for r in rows[3:8]]==
         [('sw',8,2,24,2),('sw',9,2,20,2),('sw',18,2,16,2),('sw',19,2,12,2),('sw',1,2,28,2)],
         'Actual linked save order/slots/widths source S0/S1/S2/S3/RA')
    gates=[r for r in rows if r['op']=='jalr' and(r['rd'],r['rs1'])==(1,15)]
    need([(r['PC'],r['PC']+r['bytes']) for r in gates]==[(0x8a8e,0x8a90),(0x8ab4,0x8ab6)],
         'Both linked opaque gate targets keep original RA continuations')
    hi=next(r for r in rows if r['offset']==128);lo=next(r for r in rows if r['offset']==132)
    need(hi['op']=='auipc' and hi['rd']==13 and lo['op']=='addi' and(lo['rd'],lo['rs1'])==(13,13) and
         (hi['PC']+hi['immediate']+lo['immediate'])&0xffffffff==0x2000b18c,
         'Actual encoded RAM PCREL target equals allocated alias address')
    restored=bytearray(body)
    for offset in (4,128,132):
        restored[offset:offset+4]=partial[offset:offset+4]
    need(bytes(restored)==partial,'Final link changes only actual branch and RAM relocation fields')
    need(rows[-1]['op']=='jalr' and(rows[-1]['rd'],rows[-1]['rs1'])==(0,1) and rows[-1]['bytes']==2,
         'Actual typed oversized RET leaf')
    loop=c['loop']['compare'](raw['raw']['validate'](raw['original']),rows,n)
    return dict(bytes=280,instructions=96,sha256=b['H'](body),provider_bytes=[8,270,2],
                gate_RAs=[0x8a90,0x8ab6],RAM_target=0x2000b18c,loop_CFG=loop,
                original_byte_identity_required=False,full_original_ABI_proved=False)


def image(linked,payload,c):
    b=c['b'];need=b['need'];expected=c['old']['scatter'](linked,c);start=0x8a56-0x8000;end=start+280
    need(len(payload)==76800 and payload==expected,'Actual76800-byte image equals complete690-owner linked scatter')
    need(payload[:start]==c['original'][:start] and payload[end:]==c['original'][end:],
         'All76520 bytes outside TX retain original/previous full-image content')
    need(payload[start:end]==linked.data(linked.byname[b['TX']]),'Exported TX interval equals actual allocated new source provider')
    need(struct.unpack_from('<I',linked.raw,24)[0]==0x8000,'Original startup entry8000')
    changes=[dict(address=0x8000+i,old=a,new=z) for i,(a,z) in enumerate(zip(c['original'],payload)) if a!=z]
    return dict(bytes=76800,sha256=b['H'](payload),outside_TX_bytes=76520,
                outside_TX_unchanged=True,changed_bytes=len(changes),changes=changes,
                original_whole_image_hash_required=False,hardware_OTA_proved=False)


def passes(root,folder,merged,c):
    b=c['b'];need=b['need'];E=c['ELF']
    previous=b['pinned'](b['case'](root,'v4160-reply-image-integration-2026-10-22')/'ABI-review/review.py',b['OLD_REVIEW'])
    previous_result=previous['passes'](root,folder,E(folder/'pre-frame-integrated.o'),merged,c)
    path=root/'experiments/tsl9-v4160-tx-register-abi/postpass/schedule.py'
    tool=b['pinned'](path,'7a516d1098ed0b45cf6c3ff92515f14cf831a3472a32621352a10f1914526d7a')
    ctx=tool['context'](root);tool['policy_gate'](path.with_name('policy.json'))
    before=E(folder/'tx-valid_body.o');after=E(folder/'tx-valid_body-ordered.o')
    expected,facts=tool['transform'](before,ctx['decode'])
    need(expected==after.raw and before.sections==after.sections and before.symbols==after.symbols and
         before.relocations==after.relocations,'Actual new TX scheduling output and metadata equal pure frozen transform')
    receipt=json.loads((folder/'tx-frame-order.json').read_bytes())
    need(receipt['schema']=='TSL9-TX-image-explicit-frame-order-v1' and receipt['passed'] is True and
         receipt['input']==dict(path=str(folder/'tx-valid_body.o'),sha256=b['H'](before.raw)) and
         receipt['output']==dict(path=str(folder/'tx-valid_body-ordered.o'),sha256=b['H'](after.raw)) and
         receipt['facts']==facts and receipt['compiler_only'] is False and
         receipt['new_opcodes_generated'] is False and receipt['original_BIN_codegen_input'] is False and
         receipt['target_execution'] is False,'Actual TX pre/post scheduling receipt and limits')
    for name,pin in receipt['source_pins'].items():
        source=Path(name)
        need(source.is_relative_to(root) and b['sha'](source)==pin,'Actual TX scheduling source pin')
    changed=[i for i,(x,y) in enumerate(zip(before.raw,after.raw)) if x!=y]
    need(len(changed)==50,'Only50 actual file bytes change in TX scheduling')
    return dict(previous_result,TX_changed_file_bytes=50,TX_compiler_sha256=b['H'](before.raw),
                TX_scheduled_sha256=b['H'](after.raw),TX_existing_word_windows=facts)


def controls(merged,linked,payload,folder,c):
    b=c['b'];E=c['ELF'];old=c['old'];out=[]
    def reject(name,raw,gate):
        try:
            gate()
        except (ValueError,KeyError,IndexError,struct.error) as error:
            out.append(dict(name=name,mutated_sha256=b['H'](bytes(raw)),rejected=True,reason=str(error)))
            return
        raise ValueError('Malformed actual artifact admitted: '+name)
    def elf(raw):
        return E(old['BytesInput'](bytes(raw)))
    p=bytearray(merged.raw);at=old['symbol_offset'](merged,lambda s:s['name']==b['CANONICAL'])
    struct.pack_into('<I',p,at+8,280)
    reject('fabricated_canonical_FUNC280',p,lambda:symbol_roles(elf(p),linked,folder,c))
    p=bytearray(merged.raw);struct.pack_into('<H',p,at+14,0xfff1)
    reject('canonical_ABS_standin_instead_of_allocated_entry',p,lambda:symbol_roles(elf(p),linked,folder,c))
    p=bytearray(merged.raw);at=old['rela_offset'](merged,lambda r:r['owner']==b['TX'] and r['type']==24)
    struct.pack_into('<i',p,at+8,2)
    reject('new_RAM_LO_anchor_addend',p,lambda:relocations(elf(p),linked,c))
    p=bytearray(merged.raw);sig=merged.byname['.llvm_addrsig'];p[sig['offset']+sig['size']-1]^=1
    reject('new_body_address_significance_reference',p,lambda:symbol_roles(elf(p),linked,folder,c))
    # The sole original TX JAL x0 must remain a no-link jump, irrespective of relocation type17.
    p=bytearray(linked.raw);owner=next(s for s in linked.sections if s['flags']&2 and s['address']<=0x13eac<s['address']+s['size'])
    at=owner['offset']+0x13eac-owner['address'];w=struct.unpack_from('<I',p,at)[0]
    struct.pack_into('<I',p,at,w|(1<<7))
    reject('TX_incoming_no_link_JAL_changed_to_RA_write',p,lambda:incoming(elf(p),c))
    p=bytearray(linked.raw);at=linked.byname[b['TX']]['offset']+128;p[at+2]^=1
    reject('new_TX_RAM_PCREL_target_changed',p,lambda:tx_machine(merged,elf(p),folder,c))
    p=bytearray(linked.raw);at=linked.byname[b['TX']]['offset']+20;p[at]^=1
    reject('new_TX_nonrelocation_word_changed',p,lambda:tx_machine(merged,elf(p),folder,c))
    p=bytearray(linked.raw);phoff=struct.unpack_from('<I',p,28)[0];ents,n=struct.unpack_from('<HH',p,42)
    at=next(phoff+i*ents for i in range(n) if struct.unpack_from('<I',p,phoff+i*ents)[0]==1)
    struct.pack_into('<I',p,at+20,struct.unpack_from('<I',p,at+20)[0]+2)
    reject('LOAD_memory_tail_changed',p,lambda:old['program_headers'](elf(p)))
    p=bytearray(payload);p[0]^=1
    reject('exported_non_TX_byte_changed',p,lambda:image(linked,bytes(p),c))
    b['need'](len(out)==9 and all(r['rejected'] for r in out),'Nine focused actual artifact negatives')
    return out


def inspect(root,folder,firmware):
    if not folder.is_relative_to(root):
        raise ValueError('Explicit actual folder must be inside project root')
    c=setup(root,firmware);b=c['b'];E=c['ELF'];merged=E(folder/'source-integrated.o')
    linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');payload=(folder/IMAGE).read_bytes()
    checks=dict(allocations=allocated(merged,linked,c),symbols=symbol_roles(merged,linked,folder,c),
                relocations=relocations(merged,linked,c),incoming=incoming(linked,c),
                TX=tx_machine(merged,linked,folder,c),image=image(linked,payload,c),
                scheduling=passes(root,folder,merged,c))
    load=c['old']['program_headers'](linked)
    b['need'](load==c['baseline']['LOAD'],'All actual LOAD memory/file extents and permissions remain original')
    checks['LOAD']=load
    checks['negative_controls']=controls(merged,linked,payload,folder,c)
    artifacts={name:dict(bytes=(folder/name).stat().st_size,sha256=b['sha'](folder/name)) for name in
               ('pre-frame-integrated.o','source-integrated.o','ADDRESS-WITNESS-ONLY.elf',IMAGE,
                'frame-scheduling.json','reply.o','reply-ordered.o','reply-order.json',
                'tx-entry.o','tx-valid_body.o','tx-valid_body-ordered.o','tx-return_leaf.o',
                'tx-frame-order.json')}
    producer=folder/'verification.json'
    return dict(schema='TSL9-TX-thirteen-region-independent-image-review-v1',
                actual_build_artifact_replay=True,actual_original_firmware_read=True,
                static_full_image_contract_passed=True,actual_folder=folder.relative_to(root).as_posix(),
                baseline_sha256=BASELINE,checks=checks,artifacts=artifacts,
                producer_receipt_sha256=b['sha'](producer) if producer.exists() else None,
                recorded_boundary_refs=dict(total=30,outside_selected_owners=29,selected_page_reply=1,
                                            complete_all_calls_enumeration=False),
                current_review_sha256=b['sha'](HERE/'review.py'),
                current_base_sha256=b['sha'](HERE/'base.py'),target_execution=False,ISA_emulation=False,
                original_full_ABI_admitted=False,hardware_OTA_proved=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--firmware',type=Path,required=True);parser.add_argument('--folder',type=Path)
    parser.add_argument('--receipt',type=Path);parser.add_argument('--replay',type=Path);args=parser.parse_args()
    root=args.project_root.resolve();b=runpy.run_path(str(HERE/'base.py'))
    if args.replay:
        b['need'](args.folder is None and args.receipt is None,'Readonly replay has no output/folder arguments')
        previous=json.loads(args.replay.read_bytes());folder=(root/previous['actual_folder']).resolve()
        result=inspect(root,folder,args.firmware.resolve())
        b['need'](result==previous,'Exact actual artifact receipt readonly replay')
    else:
        b['need'](args.folder is not None and args.receipt is not None and not args.receipt.exists(),
                  'Explicit actual folder and create-only new receipt')
        result=inspect(root,args.folder.resolve(),args.firmware.resolve())
        args.receipt.parent.mkdir(parents=True,exist_ok=True);b['write'](args.receipt,result)
    print(json.dumps(dict(actual_build_artifact_replay=True,static_full_image_contract_passed=True,
                         allocations=691,total_RELA=8261,recorded_boundary_refs=30,image_bytes=76800,
                         changed_TX_bytes=result['checks']['image']['changed_bytes'],hardware_OTA_proved=False)))


if __name__=='__main__':
    main()
