#!/usr/bin/env python3
"""Bounded candidate wrapper/optional helper review, no target state or execution."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
PIN='ff930619bdd652c2cd0d15e9fe61e16763a8d5f27e185f428946e4e5359dc6ec'
CFG={'V1.40':dict(wrapper=0x45228,tail=0x44866,builder=0x44e44,copy=0x402f0,
                  head=0x200031e4,sentinel=0x200031dc),
     'V1.31':dict(wrapper=0x45194,tail=0x447d2,builder=0x44db0,copy=0x402b0,
                  head=0x20003194,sentinel=0x2000318c)}


def need(value,message):
    if not value:raise ValueError(message)


def H(raw):return hashlib.sha256(raw).hexdigest()


def context(root):
    source=next(p for p in (root/'analysis/v4160-callback-call-frontiers-2026-10-22/resident-review/review.py',
                            root/'apk-analysis/tsl9-v4160-callback-call-frontiers-2026-10-22/resident-review/review.py') if p.is_file())
    need(H(source.read_bytes())==PIN,'Immutable prior bounded field reader')
    seal=source.parent/'seal.json'
    need(H(seal.read_bytes())=='5085f6f586cf78e0a75ae48f15b4af00fc2ea5e391abe70d74fdc8a685b8bde4',
         'Closed prior conditional-profile evidence')
    need(H((source.parent/'profile-and-header.json').read_bytes())==
         json.loads(seal.read_bytes())['members']['profile-and-header.json'],'Exact retained profile references')
    return runpy.run_path(str(source))


def decode(raw,pc,base):
    row=base['decode'](raw,pc)
    if row['bytes']==4:
        word=int.from_bytes(raw[:4],'little')
        if word&0xfe00707f==0x40000033:
            row.update(op='sub',rd=(word>>7)&31,reads=[(word>>15)&31,(word>>20)&31],known_under_selected_profile=True)
        if word&0xfe00707f==0x40005013:
            row.update(op='srai',rd=(word>>7)&31,reads=[(word>>15)&31],immediate=(word>>20)&31,known_under_selected_profile=True)
    return row


def rows(raw,address,base):
    result=[];at=0
    while at<len(raw):
        row=decode(raw[at:],address+at,base);result.append(row);at+=row['bytes']
    need(at==len(raw),'Exact retained instruction boundaries')
    for previous,row in zip(result,result[1:]):
        if previous['op']=='auipc' and row['op']=='jalr' and previous['rd']==row['reads'][0]:
            row['paired_direct_target']=(previous['PC']+previous['immediate']+row['immediate'])&0xffffffff
    return result


def cfg(rows_,tail=None,prefix=False):
    table={r['PC']:r for r in rows_};todo=[rows_[0]['PC']];visited=set();escapes=[];calls=[]
    while todo:
        pc=todo.pop()
        if pc in visited:continue
        if pc not in table:
            need(prefix or pc==tail,'No unexplained local CFG escape');escapes.append(pc);continue
        visited.add(pc);r=table[pc];op=r['op'];following=pc+r['bytes']
        if op=='jal' and r['rd']==0:todo.append(r['target'])
        elif op=='jalr' and r['rd']==0:
            need(r['reads']==[1] and r['immediate']==0,'Only ordinary RET ends helper')
        elif op in ('jal','jalr') and r['rd']==1:
            calls.append(dict(PC=pc,target=r.get('paired_direct_target',r.get('target')),
                              register=r['reads'][0] if r['reads'] else None,RA=following));todo.append(following)
        elif op in ('beq','bne','blt','bge','bltu','bgeu'):todo.extend((r['target'],following))
        else:todo.append(following)
    need(visited==set(table),'All captured instruction rows reachable')
    return dict(visited_rows=len(visited),escapes=sorted(set(escapes)),calls=calls,
                captured_prefix_only=prefix,normal_call_return_assumed_for_continuation=True)


def inspect_wrapper(body,version,base):
    c=CFG[version];decoded=rows(body,c['wrapper'],base)
    need(len(body)==54 and len(decoded)==22 and all(r['known_under_selected_profile'] for r in decoded),
         'Complete actual 54-byte/22-instruction standard wrapper')
    expected=[('addi',2,[2]),('sw',None,[2,8]),('mv',8,[10]),('lw',10,[11]),
              ('sw',None,[2,1]),('mv',13,[11]),('li',14,[]),('beq',None,[10,0]),
              ('sw',None,[2,11]),('li',11,[]),('auipc',1,[]),('jalr',1,[1]),
              ('lw',13,[2]),('mv',14,[10]),('mv',10,[8]),('lw',8,[2]),('lw',1,[2]),
              ('lui',11,[]),('li',12,[]),('addi',11,[11]),('addi',2,[2]),('jal',0,[])]
    need([(r['op'],r['rd'],r['reads']) for r in decoded]==expected,'Exact argument/save/restore/transfer field projection')
    need(decoded[0]['immediate']==-32 and decoded[20]['immediate']==32,'Actual balanced32-byte frame')
    need(decoded[3]['memory']==dict(kind='load',width=32,base=11,offset=4),'Fresh descriptor+4 pointer read')
    need(decoded[1]['memory']==dict(kind='store',width=32,base=2,register=8,offset=24) and
         decoded[4]['memory']==dict(kind='store',width=32,base=2,register=1,offset=28), 'Actual source save slots/order')
    need(decoded[8]['memory']==dict(kind='store',width=32,base=2,register=11,offset=12) and
         decoded[12]['memory']==dict(kind='load',width=32,base=2,offset=12), 'Fresh descriptor slot after optional call')
    need(decoded[7]['target']==c['wrapper']+32 and decoded[9]['immediate']==3 and decoded[18]['immediate']==27,
         'Null pointer skips helper; raw constants3 and27 retained')
    need((decoded[17]['immediate']+decoded[19]['immediate'])&0xffffffff==c['builder'],
         'Actual builder pointer construction')
    need(decoded[11]['paired_direct_target']==0x200001e4 and decoded[-1]['target']==c['tail'],
         'One actual optional RAM call and restored-frame tail destination')
    graph=cfg(decoded,c['tail'])
    return dict(bytes=54,instructions=22,rows=decoded,local_CFG=graph,
                custom_instruction_sites=[r['PC'] for r in decoded if r['conditional_Xwchc']],
                incoming_arguments=[10,11],normal_frame=32,
                output_tail_arguments=dict(A0='live S0 from incoming A0',A1=c['builder'],A2=27,
                                           A3='incoming descriptor, fresh SP+12 after optional call',
                                           A4='zero for null descriptor+4, otherwise helper result'),
                incoming_RA_numeric_use_seen=False,RA_saved_restored_then_forwarded_to_tail=True,
                local_GP_S4_S7_use=False,transitive_contract_proved=False)


def inspect_helper(body,version,base):
    c=CFG[version];decoded=rows(body,0x200001e4,base)
    need(len(body)==56 and len(decoded)==17 and all(r['known_under_selected_profile'] for r in decoded),
         'Actual closed56-byte/17-instruction conditional RAM helper')
    expected=['lui','lui','lw','lw','mv','sub','bne','mv','jal','addi','lw','bltu','bgeu','mv','bltu','bgeu','jalr']
    need([r['op'] for r in decoded]==expected,'Exact unsigned range-list helper shape')
    need(decoded[5]['rd']==11 and decoded[5]['reads']==[10,11],'Subtraction is pointer-minus-delta, modulo32')
    need(decoded[2]['memory']['base']==15 and decoded[2]['memory']['offset']+decoded[0]['immediate']==c['head'] and
         decoded[3]['memory']['base']==13 and decoded[3]['memory']['offset']+decoded[1]['immediate']==c['sentinel'],
         'Candidate-specific two fresh global list pointers')
    need(not any(r['memory'] and r['memory']['kind']=='store' for r in decoded),'No helper memory writes')
    need(not any(n in [r['rd'],*r['reads']] for r in decoded for n in (2,3,8,9,*range(18,28))),
         'No SP/GP/S register data use')
    need([r['op'] for r in decoded if 1 in r['reads']]==['jalr'],'RA used only by RET')
    graph=cfg(decoded);need(not graph['calls'] and not graph['escapes'],'Closed helper with no opaque call')
    return dict(bytes=56,instructions=17,rows=decoded,local_CFG=graph,
                custom_instruction_sites=[r['PC'] for r in decoded if r['conditional_Xwchc']],
                arguments=dict(A0='original pointer',A1='subtract delta (wrapper sets3)'),
                memory_writes=False,SP_GP_S_register_use=False,incoming_RA_numeric_use_seen=False,
                algorithm='Follow next=READ32(node) until node==sentinel; return u32(original-delta) only if original and adjusted are both in unsigned [u32(node+8),next), otherwise return original at sentinel.',
                loop_iteration_bound_proved=False,termination_and_memory_validity_assumptions_required=True)


def derive(report,base):
    result={}
    for version,items in report['excerpts'].items():
        for item in items.values():need(H(bytes.fromhex(item['raw']))==item['sha256'],'Exact retained excerpt identity')
        wrapper=inspect_wrapper(bytes.fromhex(items['wrapper']['raw']),version,base)
        helper=inspect_helper(bytes.fromhex(items['optional_RAM_helper']['raw']),version,base)
        prefix=rows(bytes.fromhex(items['tail_prefix']['raw']),CFG[version]['tail'],base)
        result[version]=dict(wrapper=wrapper,optional_RAM_helper=helper,
                             tail_prefix=dict(bytes=128,rows=prefix,local_CFG=cfg(prefix,prefix=True),
                                              complete_body=False,unknown_rows=[r['PC'] for r in prefix if r['op']=='unknown']),
                             full_notification_or_installed_ABI_proved=False)
    return result


def controls(report,base):
    results=[]
    for version in CFG:
        for name,part,at,change in (
            ('tail_must_not_create_new_RA','wrapper',50,lambda w:w|(1<<7)),
            ('opcode27_changed','wrapper',42,lambda w:w^(1<<2)),
            ('fresh_descriptor_slot_changed','wrapper',28,lambda w:w^(1<<2)),
            ('helper_SUB_replaced_by_ADD','optional_RAM_helper',18,lambda w:w&~(1<<30))):
            bad=copy.deepcopy(report);item=bad['excerpts'][version][part];raw=bytearray.fromhex(item['raw'])
            n=4 if at in (50,18) else 2;raw[at:at+n]=change(int.from_bytes(raw[at:at+n],'little')).to_bytes(n,'little')
            item['raw']=raw.hex();item['sha256']=H(raw)
            try:derive(bad,base)
            except ValueError as error:results.append(dict(version=version,name=name,rejected=True,reason=str(error)));continue
            raise ValueError('Malformed source contract admitted '+name)
    return results


def source_check(root,report,base):
    profile=json.loads((base['HERE']/'profile-and-header.json').read_bytes())
    for item in profile['profile_inputs']:
        path=root/item['relative']
        need(path.stat().st_size==item['bytes'] and H(path.read_bytes())==item['sha256'],
             'Actual pinned Xwchc reference used for conditional tail preview')
    for version,items in report['excerpts'].items():
        reference=base['CANDIDATES'][version]
        original=root/reference['original'];segment=root/reference['directory']/reference['segment']
        need(H(original.read_bytes())==reference['original_sha256'] and H(segment.read_bytes())==reference['segment_sha256'],
             'Actual fixed candidate HEX/main-segment identities')
        raw=segment.read_bytes()
        for item in items.values():
            at=item['source_flash_address']-0x40000
            need(raw[at:at+item['bytes']].hex()==item['raw'],'Actual bounded candidate source excerpt')
    return dict(actual_candidate_bytes_read=True,actual_profile_references_read=True,candidate_is_installed=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path)
    p.add_argument('--candidate-root',type=Path);a=p.parse_args();root=a.project_root.resolve() if a.project_root else HERE.parents[2]
    base=context(root);report=json.loads((HERE/'evidence.json').read_bytes())
    need(derive(report,base)==report['derived'] and controls(report,base)==report['controls'],'Pure bounded field/CFG/contract replay')
    seal=json.loads((HERE/'seal.json').read_bytes())
    for name,pin in seal['members'].items():need(H((HERE/name).read_bytes())==pin,'Exact sealed source/text member')
    actual=source_check(a.candidate_root.resolve(),report,base) if a.candidate_root else dict(actual_candidate_bytes_read=False)
    print(json.dumps(dict(passed=True,metadata_excerpt_replay=True,**actual,wrapper_bytes=54,helper_bytes=56,
                         tail_transitive_contract_proved=False,target_execution=False,emulation=False)))


if __name__=='__main__':main()
