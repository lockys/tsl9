"""Read-only candidate post-callback CFGs, sparse source mappings and frontiers."""
import argparse
import hashlib
import json
import runpy
import sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = 'b453913bfa81f02d097527cba2ee826b253dd43c7873be17d7881bb7b7b49ecc'
PARSER = '727ec4a519e751f72180381ab9129d58e351affd0bc467a99889f1f14e77e5df'
TD = 'd18a5c4d0722e20d3d0398f180931118a5125c9ada56a64d32c602ad5bd71490'
SOURCE = {
 'carrier':('original/wchble_rom.hex','5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23',0x402f0,11904,0x43d0a,0x2000323c,0x43bca,0x43190,0x4316c,0x43326,0x440b6),
 'carrier-dec2023':('original-dec2023/wchble_rom.hex','11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5',0x402b0,11828,0x43c7e,0x200031ec,0x43b3e,0x43104,0x430e0,0x4329a,0x44022),
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def need(ok,why):
    if not ok:raise ValueError(why)
def locate(root,n):
    p=root/n
    if n.startswith('analysis/') and not p.exists():p=root/('apk-analysis/tsl9-'+n.removeprefix('analysis/'))
    return p
def closed(root,folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact prior source seal')
    seal=read(folder/'seal.json')
    for n,h in seal['members'].items():need(sha(folder/n)==(h if isinstance(h,str) else h['sha256']),'Prior member '+n)
    for n,h in seal.get('external_inputs',{}).items():need(sha(locate(root,n))==h,'Prior dependency '+n)
def context(root):
    old=locate(root,'analysis/v4160-resident-memory-2026-10-22/continuation-review/seal.json').parent
    closed(root,old,OLD);module=runpy.run_path(str(old/'check.py'));previous=module['previous'](root)
    return module,previous,previous['rows'],module['decoder'](root),old
def ranges(name):
    _,_,source,count,slot,base,main,heap,scan,reset,table=SOURCE[name]
    return {'post_init':(main,main+272),'heap_init':(heap,heap+112),'heap_scan':(scan,scan+36),'reset_leaf':(reset,reset+10),'table_init':(table,table+160),'allocator':(0x20000040,0x20000110),'fill':(0x2000039c,0x200003ca),'free':(0x20000110,0x200001e4)}
def source_address(name,pc):
    v=SOURCE[name]
    if 0x20000040<=pc<0x20000040+v[3]:return v[2]+pc-0x20000040
    need(0x40000<=pc<0x80000,'Only direct or documented copied source view')
    return pc
def actual_sources(root,refs):
    refs=Path(refs).resolve(strict=True);need(sha(refs/'carrier/intel_hex.py')==PARSER,'Pinned existing strict sparseHEX parser')
    need(sha(refs/'instruction-reference/RISCVInstrInfoXwch.td')==TD,'Actual conditional Xwchc encoding source')
    _,previous,_,_,_=context(root);legacy=previous['prior'](root);R,_,_=legacy.references(root)
    R.closed(refs/'resident-entry',R.ENTRY_SEAL);contract=read(refs/'resident-entry/contract.json')
    parser=runpy.run_path(str(refs/'carrier/intel_hex.py'))['parse'];out={}
    for name,v in SOURCE.items():
        path=refs/v[0];need(sha(path)==v[1],'Actual complete candidate HEX '+name);parsed=parser(path.read_bytes())
        def take(a,n,segments=parsed['segments']):
            hit=[b[a-s:a-s+n] for s,b in segments if s<=a and a+n<=s+len(b)]
            need(len(hit)==1,'Requested source range has no synthesized holes '+hex(a));return hit[0]
        need(int.from_bytes(take(0x400a4,4),'little')==v[4],'Actual slot400A4 initializer')
        if name=='carrier':
            mapping=contract['entry']['word_copy_contracts'][0]
            need((mapping['source']['start'],mapping['destination_start'],mapping['requested_bytes'] if 'requested_bytes' in mapping else mapping['bytes'])==(v[2],0x20000040,v[3]),'Actual newer copied source range')
        else:
            mapping=contract['historical_mapped_callee_comparison']
            need((mapping['copy_source'],mapping['copy_destination'],mapping['copy_last_word_inclusive']-mapping['copy_destination']+4)==(v[2],0x20000040,v[3]),'Actual historical inclusive copy range')
        take(v[2],v[3])
        out[name]=(take,parsed)
    return out
def capture(root,refs):
    _,_,rows,decode,_=context(root);sources=actual_sources(root,refs);out={}
    for name,(take,parsed) in sources.items():
        groups={};mapped=[]
        for key,(a,z) in ranges(name).items():
            flash=source_address(name,a);blob=take(flash,z-a);groups[key]=rows(blob,a,decode)
            mapped.append(dict(group=key,view_start=a,view_end_exclusive=z,source_flash_start=flash,source_flash_end_exclusive=flash+z-a,bytes=z-a,sha256=hashlib.sha256(blob).hexdigest(),holes_materialized=False))
        v=SOURCE[name];out[name]=dict(candidate=name,HEX_sha256=v[1],slot400A4=v[4],config_base=v[5],config_word52=v[5]+52,copied_source_start=v[2],copied_RAM_start=0x20000040,copied_bytes=v[3],sparse_segment_count=len(parsed['segments']),sparse_source_bytes=sum(len(b) for _,b in parsed['segments']),groups=groups,mapped_ranges=mapped)
    return dict(schema='TSL9-postcallback-candidate-source-ledger-v1',candidates=out,installed_identity_proved=False)
def exact(idx,pc,**fields):need(all(idx[pc][k]==v for k,v in fields.items()),'Actual source field '+hex(pc)+' '+str(fields))
def cfg(rows):
    idx={x['PC']:x for x in rows};start=rows[0]['PC'];seen=set();pending=[start];calls=[];exits=[];edges=[]
    while pending:
        pc=pending.pop()
        if pc in seen:continue
        need(pc in idx,'No unexplained direct CFG escape');seen.add(pc);x=idx[pc];op=x['op'];nextpc=pc+x['bytes']
        if op=='jalr':
            if x['rd']==0:
                need((x['rs1'],x['immediate'])==(1,0),'Only normal RA return');exits.append(pc);nexts=[]
            else:
                need(x['rd']==1,'Only linked nested indirect call');previous=next((y for y in rows if y['PC']+y['bytes']==pc),None)
                target=None
                if previous and previous['op']=='auipc' and previous['rd']==x['rs1']:target=(previous['PC']+previous['immediate']+x['immediate'])&0xfffffffe
                calls.append(dict(PC=pc,kind='AUIPC/JALR' if target is not None else 'computed',target=target,rs1=x['rs1'],immediate=x['immediate']));nexts=[nextpc]
        elif op=='jal':
            if x['rd']==1:calls.append(dict(PC=pc,kind='direct',target=x['target']));nexts=[nextpc]
            else:need(x['rd']==0,'Only no-link local JAL');nexts=[x['target']]
        elif op in ('beq','bne','bltu','bgeu','blt','bge'):nexts=[nextpc,x['target']]
        else:nexts=[nextpc]
        for q in nexts:need(q in idx,'All normal-return/direct branches in bounded body');edges.append((pc,q));pending.append(q)
    need(seen==set(idx),'All retained rows reachable on conditional normal-return CFG')
    return dict(entry=start,end_exclusive=rows[-1]['PC']+rows[-1]['bytes'],bytes=sum(x['bytes'] for x in rows),rows=len(rows),normal_RET_PCs=sorted(exits),calls=sorted(calls,key=lambda x:x['PC']),backward_edges=[list(e) for e in edges if e[1]<=e[0]],call_return_edges_conditional=True)
def gate(record):
    name=record['candidate'];v=SOURCE[name];base=v[5];delta=base-0x20003000;groups=record['groups'];index={k:{x['PC']:x for x in rows} for k,rows in groups.items()}
    graph={k:cfg(rows) for k,rows in groups.items()};start=v[6];p=index['post_init'];a=index['allocator'];t=index['table_init'];tb=v[10];fill=index['fill']
    expected_calls={'post_init':[0x2000039c,0x2000039c,v[7],0x20000040,0x2000039c,v[9],v[10]],'heap_init':[v[8]],'heap_scan':[],'reset_leaf':[],'table_init':[None,0x20000040,0x2000039c,0x20000110,None],'allocator':[None],'fill':[],'free':[]}
    for k,wanted in expected_calls.items():need([x['target'] for x in graph[k]['calls']]==wanted,'Every direct dependency or computed frontier '+k)
    frames={'post_init':(-16,16),'heap_init':(-16,16),'table_init':(-32,32),'allocator':(-16,16),'fill':(),'free':(),'heap_scan':(),'reset_leaf':()}
    for k,values in frames.items():
        rows=groups[k];own=[x for x in rows if x['rd']==2]
        need(tuple(x['immediate'] for x in own)==values and all((x['op'],x['rs1'])==('addi',2) for x in own),'Only exact own SP frame changes '+k)
    need(not any(x['rd']==3 for rows in groups.values() for x in rows),'No own GP writes; callbacks remain unknown')
    for off,rs2,disp in [(4,0,delta-4),(0x12,0,delta+68),(0x24,0,delta-12),(0x88,10,delta+64),(0xb4,15,delta-40),(0xbe,15,delta-8)]:exact(p,start+off,op='sw',rs2=rs2,immediate=disp)
    exact(p,start+0x16,op='addi',rd=12,rs1=0,immediate=20)
    exact(p,start+0x1c,op='addi',rd=11,rs1=0,immediate=0);exact(p,start+0x1e,op='addi',rd=10,rs1=10,immediate=delta-36)
    exact(p,start+0x38,op='addi',rd=10,rs1=8,immediate=delta-80);exact(p,start+0x3c,op='addi',rd=12,rs1=0,immediate=40)
    exact(p,start+0x52,op='lbu',rd=15,rs1=15,immediate=delta+21)
    exact(p,start+0x56,op='addi',rd=8,rs1=8,immediate=delta-80)
    exact(p,start+0x76,op='qk.c.sb',rs1=8,rs2=10,immediate=2,memory_width=8)
    exact(p,start+0x88,op='sw',rs1=9,rs2=10,immediate=delta+64)
    exact(p,start+0x8c,op='beq',rs1=10,rs2=0,target=start+0x106)
    exact(p,start+0x8e,op='qk.c.lbu',rd=12,rs1=8,immediate=2)
    exact(p,start+0x98,op='addi',rd=12,rs1=12,immediate=576)
    for off,reg,slot in [(0x106,1,12),(0x108,8,8),(0x10a,9,4)]:exact(p,start+off,op='lw',rd=reg,rs1=2,immediate=slot)
    exact(p,start+0x10c,op='addi',rd=2,rs1=2,immediate=16)
    for off,reg,slot in [(0x22,1,12),(0x28,8,8),(0x2a,9,4)]:exact(p,start+off,op='sw',rs1=2,rs2=reg,immediate=slot)
    for off,base_reg in [(0xdc,14),(0xf2,14),(0x104,15)]:exact(p,start+off,op='sw',rs1=base_reg,rs2=12,immediate=0,memory_width=32)
    exact(a,0x20000094,op='lw',rd=14,rs1=14,immediate=delta+52,memory_width=32)
    exact(a,0x20000098,op='beq',rs1=14,rs2=0,target=0x2000005a)
    exact(a,0x2000009e,op='addi',rd=10,rs1=0,immediate=1);exact(a,0x200000a0,op='jalr',rd=1,rs1=14,immediate=0)
    exact(a,0x20000104,op='lw',rd=1,rs1=2,immediate=12);exact(a,0x20000106,op='lw',rd=8,rs1=2,immediate=8)
    exact(t,tb+8,op='addi',rd=15,rs1=8,immediate=delta)
    exact(t,tb+12,op='lw',rd=10,rs1=15,immediate=8)
    exact(t,tb+0x28,op='lw',rd=15,rs1=8,immediate=56)
    exact(t,tb+0x2c,op='lw',rd=14,rs1=8,immediate=60)
    exact(t,tb+0x30,op='addi',rd=12,rs1=2,immediate=12);exact(t,tb+0x32,op='addi',rd=11,rs1=0,immediate=1)
    exact(t,tb+0x34,op='jalr',rd=1,rs1=15,immediate=0)
    exact(t,tb+0x8e,op='lw',rd=14,rs1=8,immediate=60);exact(t,tb+0x9c,op='jalr',rd=1,rs1=14,immediate=0)
    for off,reg,slot in [(0x18,1,28),(0x1a,8,24),(0x1c,9,20),(0x1e,18,16)]:exact(t,tb+off,op='lw',rd=reg,rs1=2,immediate=slot)
    exact(fill,0x2000039c,op='lui',rd=14,immediate=0x40024000)
    exact(fill,0x200003a0,op='lw',rd=15,rs1=14,immediate=524)
    exact(fill,0x200003a4,op='sw',rs1=14,rs2=0,immediate=524)
    exact(fill,0x200003be,op='addi',rd=10,rs1=10,immediate=1);exact(fill,0x200003c0,op='sb',rs1=10,rs2=11,immediate=-1)
    exact(fill,0x200003c4,op='bne',rs1=10,rs2=14,target=0x200003be)
    exact(fill,0x200003b8,op='sw',rs1=14,rs2=15,immediate=524)
    # A2 writes in the allocation-success block cannot reach the failure callback.
    reverse={pc:set() for pc in a}
    for x in groups['allocator']:
        pc=x['PC'];op=x['op'];edges=[] if op=='jalr' and x['rd']==0 else [pc+x['bytes']]
        if op=='jal' and x['rd']==0:edges=[x['target']]
        elif op in ('beq','bne','bltu','bgeu'):edges.append(x['target'])
        for q in edges:
            if q in reverse:reverse[q].add(pc)
    prior=set();todo=[0x200000a0]
    while todo:
        pc=todo.pop()
        if pc in prior:continue
        prior.add(pc);todo.extend(reverse[pc])
    need(not any(a[pc]['rd']==12 for pc in prior),'Allocator callback keeps ambient A2 on every source path reaching it')
    return dict(candidate=name,bytes=1056,rows=359,groups=graph,
        config_base=base,config_word52=base+52,slot400A4=v[4],post_callback_direct_call=v[4]+0xce,
        fixed_zero_words=[base-4,base+68,base-12],initial_byte_fill20=[base-36,base-16],initial_byte_fill40=[base-80,base-40],
        allocation_result_word=base+64,initial_config21_count_formula='let x=one fresh U8(config+21); (3*((x>>2)+(x&3))+14)&255',
        allocation_count_reads_not_collapsed=True,success_fill_count='6*fresh U8(liveS0+2)+576',
        table_code_address_values=[v[9]+10,v[9]+140,v[9]+140],table_function_pointer_role_inferred=True,table_code_addresses_are_store_values_not_flash_destinations=True,
        computed_frontiers=[dict(PC=0x200000a0,pointer_field=52,pointer_word=base+52,A0=1,A1='liveA1 OR (rounded16_size<<16)',A2='ambient entry A2 on callback-reaching paths'),dict(PC=tb+0x34,pointer_field=56,pointer_word=base+56,A0='config+8 before opaque call',A1=1,A2='live SP+12 writable output word'),dict(PC=tb+0x9c,pointer_field=60,pointer_word='fresh READ32(live S0+60)',conditional_pointer_word_if_S0_preserved=base+60,A0='fresh liveS0+8 plus indexed offset',A1='fresh halfword(liveS0+12)>>2',A2='live state+32 pointer from prior calls')],
        own_GP_writes=False,SP_S_preservation_requires_computed_callback_contracts=True,
        additional_known_stack_below_post_init_entry=64,post_callback_known_frames_below_slot400A4_entry=80,
        unknown_callback_extra_stack_unbounded=True,normal_return_or_list_loop_termination_proved=False,
        config52_actual_value_or_full_lifetime_proved=False,computed_heap_and_output_aliases_excluded=False,
        config52_unchanged_only_if_all_dynamic_writes_disjoint_and_callbacks_preserve=True,
        installed_identity_proved=False)
def validate_metadata(root):
    _,_,rows,decode,old=context(root);ledger=read(HERE/'ledger.json');pins=read(HERE/'byte-pins.json');r2=read(HERE/'r2-static.json');parse=runpy.run_path(str(HERE/'r2_fields.py'))['parse'];facts=[];standards=vendor=0
    old_records={x['candidate']:x for x in read(old/'ledger.json')['candidates']}
    for name,c in ledger['candidates'].items():
        need((c['config_base'],c['slot400A4'])==(SOURCE[name][5],SOURCE[name][4]),'Candidate linkage values')
        rec=old_records[name];need(rec['next_init_target']==SOURCE[name][6],'Prior post-callback direct target')
        for key,(a,z) in ranges(name).items():
            group=c['groups'][key];blob=b''.join(bytes.fromhex(x['raw_hex']) for x in group);pin=pins[name][key]
            need(len(blob)==z-a==pin['bytes'] and len(group)==pin['rows'] and hashlib.sha256(blob).hexdigest()==pin['sha256'],'Complete pinned source range '+name+'/'+key)
            need(rows(blob,a,decode)==group,'Every raw field '+name+'/'+key)
            retained=r2['groups'][name][key];need(len(retained)==len(group),'Independent row count')
            for x,y in zip(group,retained):
                need((x['PC'],x['bytes'],x['raw_hex'])==(y['addr'],y['size'],y['bytes']),'All independent static boundaries')
                if x['op'].startswith('qk.'):vendor+=1
                else:need(x==parse(y),'Independent standard operand fields');standards+=1
        facts.append(gate(c))
    return ledger,facts,standards,vendor,decode,rows
def controls(record,decode,rows):
    name=record['candidate'];start=SOURCE[name][6];tb=SOURCE[name][10];out=[]
    for key,pc,field in [('post_init',start+0x16,'immediate'),('post_init',start+0x38,'immediate'),('allocator',0x20000094,'immediate'),('table_init',tb+0x28,'immediate'),('post_init',start+0x10c,'immediate')]:
        group=record['groups'][key];a=group[0]['PC'];old=next(x for x in group if x['PC']==pc);blob=b''.join(bytes.fromhex(x['raw_hex']) for x in group);found=None
        for bit in range(old['bytes']*8):
            raw=bytearray(blob);raw[pc-a+bit//8]^=1<<(bit%8)
            try:x=decode(raw[pc-a:],pc)
            except ValueError:continue
            stable=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if x[field]==old[field] or any(x[k]!=old[k] for k in stable if k!=field):continue
            found=raw,bit,x;break
        need(found is not None,'Actual single-field raw mutation available');raw,bit,x=found;changed=dict(record,groups=dict(record['groups']));changed['groups'][key]=rows(raw,a,decode)
        try:gate(changed)
        except ValueError as e:out.append(dict(candidate=name,PC=pc,field=field,bit=bit,old=old[field],new=x[field],raw_hex=x['raw_hex'],rejected=True,reason=str(e)));continue
        raise ValueError('Incorrect post-callback source operand admitted')
    return out
def inspect(root,candidate_root=None):
    root=Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists():closed(root,HERE,sha(HERE/'seal.json'))
    ledger,facts,standards,vendor,decode,rows=validate_metadata(root)
    result=dict(schema='TSL9-postcallback-initializer-source-review-v1',passed=True,metadata_only=candidate_root is None,
        actual_candidate_HEX_files_read=0,actual_candidate_bodies_read=0,raw_controls_replayed=False,
        candidate_source_bytes_each=1056,candidate_source_rows_each=359,standard_operand_rows=standards,conditional_QK_rows=vendor,
        facts=facts,computed_callback_effects_proved=False,whole_initializer_SP_S_GP_preservation_proved=False,
        config52_unconditional_preservation_or_zero_proved=False,full_ABI_proved=False,whole_OTA_proved=False,
        installed_identity_proved=False,holes_materialized=False,parser_self_tests_or_old_HOST_matrices_run=False,
        target_or_ISA_or_ESIL_execution=False,compiler_or_linker_run=False,new_BIN=False,network=False,hardware=False)
    if candidate_root is not None:
        need(capture(root,candidate_root)==ledger,'Actual two sparseHEX candidate byte/operand replay')
        _,_,_,_,old=context(root);old_records=read(old/'ledger.json')['candidates'];sources=actual_sources(root,candidate_root)
        for rec in old_records:
            blob=sources[rec['candidate']][0](rec['entry'],228)
            need(rows(blob,rec['entry'],decode)==rec['rows'],'Actual previous slot400A4 full228B source linkage')
        negatives=[x for c in ledger['candidates'].values() for x in controls(c,decode,rows)]
        result.update(actual_candidate_HEX_files_read=2,actual_candidate_bodies_read=16,actual_previous_initializer_bytes=456,raw_controls_replayed=True,raw_controls=len(negatives),controls=negatives)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--candidate-root',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.candidate_root)))
