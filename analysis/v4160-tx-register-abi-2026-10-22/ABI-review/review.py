#!/usr/bin/env python3
"""Explicit actual-artifact ABI subset replay; default metadata has another CLI."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
POSTPASS='7a516d1098ed0b45cf6c3ff92515f14cf831a3472a32621352a10f1914526d7a'
POLICY='370ea3f33c0164b83a04ee7623bc8507dc8da1e628af7de011ccb951f4dba9a2'


def need(value,message):
    if not value:
        raise ValueError(message)


def H(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def partial_contract(root,firmware,path):
    p=runpy.run_path(str(HERE/'predicates.py'));n=p['prior'](root);context=n['context'](root,firmware)
    e=context['ELF'](path)
    one=n['one'];entry=one(e.symbols,lambda s:s['name']=='tsl9_ota_tx_8a56','Actual partial entry')
    valid=one(e.symbols,lambda s:s['name'] in ('tsl9_tx_valid_body','_ZL18tsl9_tx_valid_bodyjjjj'),'Actual partial typed body')
    leaf=one(e.symbols,lambda s:s['name']=='tsl9_tx_oversized_return','Actual partial return leaf')
    need(e.kind==1 and e.flags==1 and len({s['index'] for s in (entry,valid,leaf)})==1,
         'Actual partial ET_REL combines three source-owned providers')
    owner=e.sections[entry['index']]
    need((owner['type'],owner['flags'],owner['size'],owner['alignment'])==(1,6,280,2) and
         [s['index'] for s in e.sections if s['flags']&2 and s['size']]==[owner['index']],
         'Actual partial aggregate AX280 extent')
    need([(s['value'],s['size'],s['info'],s['other']) for s in (entry,valid,leaf)]==
         [(0,8,18,0),(8,270,2,0),(278,2,18,0)],'Partial FUNC roles remain honest section-relative providers')
    need(len(e.relocations)==3 and sorted(r['type'] for r in e.relocations)==[16,23,24],
         'Actual partial branch and RAM HI/LO relocations only')
    branch=next(r for r in e.relocations if r['type']==16)
    need(branch['offset']==4 and branch['addend']==0 and branch['symbol']['index']==owner['index'] and
         branch['symbol']['value']==278,'Partial branch truly references the typed RET provider')
    hi=next(r for r in e.relocations if r['type']==23);lo=next(r for r in e.relocations if r['type']==24)
    need(hi['offset']==128 and lo['offset']==132 and hi['addend']==lo['addend']==0 and
         hi['symbol']['name']=='__tsl9v4160_data_2000b18c' and hi['symbol']['index']==0 and
         lo['symbol']['index']==owner['index'] and lo['symbol']['value']==128,
         'Partial genuine RAM provider/PCREL anchor roles')
    return dict(actual_partial_ELF_read=True,sha256=H(path),allocated_bytes=280,
                function_parts=[8,270,2],actual_RELA_types=[16,23,24],
                original_full_image_roles_integrated=False)


def inspect(root,firmware,folder,providers=None):
    producer=folder/'verification.json'
    need(producer.is_file(),'Actual producer receipt required to identify the fresh pre-provider folder')
    receipt=json.loads(producer.read_bytes())
    if providers is None:
        providers=Path(receipt['pre_folder']).resolve()
    need(folder.is_relative_to(root) and providers.is_relative_to(root),'Explicit artifact folders stay within project root')
    tool=root/'experiments/tsl9-v4160-tx-register-abi/postpass/schedule.py'
    need(H(tool)==POSTPASS and H(tool.with_name('policy.json'))==POLICY,'Frozen new source-owned frame pass and policy')
    modules={name:runpy.run_path(str(HERE/(name+'.py'))) for name in ('entry','tail','loop','controls')}
    body=folder/'valid_body-ordered.o';linked=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
    entry=modules['entry']['inspect'](root,firmware,folder,'valid_body-ordered.o',providers=providers)
    frame=modules['tail']['audit'](root,firmware,providers/'valid_body.o',body)
    loop=modules['loop']['inspect'](root,firmware,linked)
    guards=modules['controls']['inspect'](root,tool,providers/'valid_body.o')
    partial=partial_contract(root,firmware,folder/'source-integrated-component.o')
    artifacts={}
    for base,names in [(providers,['entry.o','valid_body.o','valid_body.ll','return_leaf.o','return_leaf.ll']),
                       (folder,['valid_body-ordered.o','COMPONENT-ONLY-NOT-FIRMWARE.elf',
                                'source-integrated-component.o','verification.json'])]:
        for name in names:
            path=base/name;need(path.is_file(),'Actual artifact: '+name)
            artifacts[path.relative_to(root).as_posix()]=H(path)
    return dict(schema='TSL9-TX-independent-layered-ABI-review-v1',
                actual_build_artifact_replay=True,checked_layered_subsets_passed=True,
                actual_folder=folder.relative_to(root).as_posix(),
                actual_providers=providers.relative_to(root).as_posix(),
                actual_artifact_sha256=artifacts,entry=entry,frame=frame,loop=loop,guard_controls=guards,
                partial_link=partial,
                original_full_ABI_admitted=False,whole_image_integrated=False,
                hardware_OTA_proved=False,target_execution=False,ISA_emulation=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--firmware',type=Path,required=True)
    parser.add_argument('--folder',type=Path)
    parser.add_argument('--providers',type=Path)
    parser.add_argument('--receipt',type=Path)
    parser.add_argument('--replay',type=Path)
    args=parser.parse_args();root=args.project_root.resolve();firmware=args.firmware.resolve()
    if args.replay:
        need(not args.folder and not args.providers and not args.receipt,'Replay has no creation arguments')
        saved=json.loads(args.replay.read_bytes())
        result=inspect(root,firmware,root/saved['actual_folder'],root/saved['actual_providers'])
        need(result==saved,'Actual archives and all independent static results match saved receipt')
    else:
        need(args.folder and args.receipt,'Explicit actual folder and create-only receipt required')
        result=inspect(root,firmware,args.folder.resolve(),args.providers.resolve() if args.providers else None)
        need(not args.receipt.exists(),'Create-only independent layered review receipt')
        args.receipt.parent.mkdir(parents=True,exist_ok=True)
        args.receipt.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(actual_build_artifact_replay=True,checked_layered_subsets_passed=True,
                         entry_prefix_proved=True,frame_fresh_read_frontiers_proved=True,
                         loop_CFG_correspondence_proved=True,
                         original_full_ABI_admitted=False,whole_image_integrated=False,
                         guard_controls=result['guard_controls']['total_rejected'],
                         linked_controls=len(result['entry']['controls']),
                         loop_controls=len(result['loop']['controls']))))


if __name__=='__main__':
    main()
