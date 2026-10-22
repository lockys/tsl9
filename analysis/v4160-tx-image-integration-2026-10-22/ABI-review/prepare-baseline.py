#!/usr/bin/env python3
"""Retain verification-only metadata from the actual sealed twelve-region image."""
import argparse
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def prepare(root,folder,firmware):
    b=runpy.run_path(str(HERE/'base.py'));c=b['context'](root);old=b['pinned'](
        b['case'](root,'v4160-reply-image-integration-2026-10-22')/'ABI-review/review.py',b['OLD_REVIEW'])
    verified=old['inspect'](root,folder,firmware)
    E=c['ELF'];merged=E(folder/'source-integrated.o');linked=E(folder/'ADDRESS-WITNESS-ONLY.elf')
    allocations=c['old']['alloc'](merged);b['need'](len(allocations)==691,'Actual original691 allocation owners')
    sections={}
    for name,section in allocations.items():
        target=linked.byname[name]
        sections[name]=dict(attributes={k:section[k] for k in ('type','flags','size','alignment','entry_size','address')},
                            originalVA=target['address'],partial_sha256=b['H'](c['old']['data'](merged,section)),
                            linked_sha256=b['H'](c['old']['data'](linked,target)))
    refs,projected=b['non_TX_relocations'](merged,c,280)
    source_roles=b['roles'](merged,c)
    old_context=old['context'](root,firmware)
    original=b['pinned'](b['case'](root,'v4160-ota-tx-2026-10-22')/'ABI-review/original.py',
                       'feeff6d2f8fae97b4ccb153b764a3b47798d48cfb26ca86cc9414da0608caf1a')
    tx=original['inspect'](root,firmware,folder)
    incoming=old_context['baseline']['incoming']+tx['incoming']
    b['need'](len({r['site'] for r in incoming})==30,'Existing21 plus TX9 actual incoming contracts')
    payloads={}
    for section in merged.sections:
        if section['size'] and not section['flags']&2 and section['type'] not in (2,3,4):
            payloads[section['name']]=dict(bytes=section['size'],sha256=b['H'](merged.data(section)),
                attributes={k:section[k] for k in ('type','flags','address','link','info','alignment','entry_size')})
    bindings=old_context['baseline']['canonical_bindings']
    return dict(schema='TSL9-TX-full-image-independent-baseline-v1',verification_only=True,
                original_bytes_used_for_generation=False,old_twelve_review_schema=verified['schema'],
                old_actual_partial_sha256=b['H'](merged.raw),old_actual_linked_sha256=b['H'](linked.raw),
                old_actual_producer_receipt_sha256=b['sha'](folder/'verification.json'),
                sections=sections,old_TX_roles=[r for r in source_roles if r['owner']==b['TX']],
                outside_TX_roles_count=len([r for r in source_roles if r['owner']!=b['TX']]),
                outside_TX_roles_digest=b['digest'](r for r in source_roles if r['owner']!=b['TX']),
                outside_TX_roles_counter=sorted(b['count'](r for r in source_roles if r['owner']!=b['TX']).items()),
                non_TX_RELA_count=len(refs),non_TX_RELA_projected_digest=b['digest'](refs),
                incoming_target_size_projection=projected,incoming=sorted(incoming,key=lambda r:r['site']),
                canonical_bindings=bindings,nonallocated_payloads=payloads,
                LOAD=c['old']['program_headers'](linked),
                twelve_typed_owners=list(old_context['selected']),
                old_TX_owner=b['TX'],old_TX_owned_RELA=tx['owned_RELA'],
                firmware_sha256=b['FW'],hardware_OTA_proved=False,target_execution=False,ISA_emulation=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--folder',type=Path,required=True);parser.add_argument('--firmware',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    value=prepare(args.project_root.resolve(),args.folder.resolve(),args.firmware.resolve())
    if args.output.exists():
        raise ValueError('Create-only portable baseline')
    b=runpy.run_path(str(HERE/'base.py'));args.output.parent.mkdir(parents=True,exist_ok=True);b['write'](args.output,value)
    print(json.dumps(dict(actual_sealed_twelve_image_replayed=True,allocations=len(value['sections']),
                         non_TX_RELA=value['non_TX_RELA_count'],incoming=len(value['incoming']),
                         baseline_sha256=b['sha'](args.output))))


if __name__=='__main__':
    main()
