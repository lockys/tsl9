#!/usr/bin/env python3
"""Original TX source operands/roles proof; optional actual ELF readback only."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MANIFEST='09bfe0613a88a395b048a397530f62e49b199e890c3d2fc04285ca44887915fe'
OWNER='.text.tsl9v4160.code_continuation_8a56'
BODY='3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b'
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
OWNED=[(4,16,278),(32,16,64),(40,16,64),(60,16,118),(68,16,104),(76,16,104),(100,16,120),(128,23,'__tsl9v4160_data_2000b18c'),(132,24,128),(186,16,252),(276,45,180)]
INCOMING=[('.text.tsl9v4160.direct_expansion_82d2',150,45),('.text.tsl9v4160.code_continuation_13346',610,17),('.text.tsl9v4160.post_table_code_13bd2',92,17),('.text.tsl9v4160.direct_followup_137c0',880,17),('.text.tsl9v4160.conditional_runtime_838e',142,45),('.text.tsl9v4160.conditional_runtime_13b4c',52,17),('.text.tsl9v4160.conditional_runtime_13e98',20,17),('.text.tsl9v4160.ota_handler_9b8e',82,17),('.text.tsl9v4160.gatt_ingress_13f7e',1978,17)]
def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def case(root,name):return next(p for p in (root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def count(rows):return Counter(json.dumps(row,sort_keys=True) for row in rows)
def shape(roles,relocations):
    public=[row for row in roles if row['name']=='__tsl9v4160_call_8a56'];need(public==[{'name':'__tsl9v4160_call_8a56','owner':OWNER,'offset':0,'bytes':280,'info':18,'other':0}],'Original actual canonical GLOBAL FUNC280')
    owned=[row for row in relocations if row['owner']==OWNER];incoming=[row for row in relocations if row['owner']!=OWNER and row['symbol']['owner']==OWNER]
    actual=[(row['offset'],row['type'],row['symbol']['offset'] if row['symbol']['owner']==OWNER else row['symbol']['name']) for row in owned];need(sorted(actual,key=str)==sorted(OWNED,key=str) and all(row['addend']==0 for row in owned),'Exact eleven owned source roles/PCREL/private edges')
    need(sorted((row['owner'],row['offset'],row['type']) for row in incoming)==sorted(INCOMING) and all(row['symbol']==public[0] and row['addend']==0 for row in incoming),'Exact nine external recorded references all to canonical entry')
    need(len(roles)==11 and sum(row['symbol']['owner']==OWNER for row in owned)==10,'Exact original mapping/SECTION/FUNC/eight private roles')
    return owned,incoming
def source_roles(root,m):
    roles=[row for row in m['baseline_symbol_roles'] if row['owner']==OWNER];names={row['name'] for row in roles if row['name']};named={}
    for row in m['baseline_symbol_roles']:
        if row['name']:named.setdefault(row['name'],[]).append(row)
    kinds={'R_RISCV_BRANCH':16,'R_RISCV_RVC_JUMP':45,'R_RISCV_JAL':17,'R_RISCV_PCREL_HI20':23,'R_RISCV_PCREL_LO12_I':24};relocations=[];statements=[]
    for name in m['source_units']:
        path=root/name;need(sha(path)==m['source_files'][name],'Pinned raw carrier source');owner=None
        for line in path.read_text(encoding='utf-8').splitlines():
            stripped=line.strip()
            if not stripped.startswith('"'):continue
            text=json.loads(stripped)
            if text.startswith('.section '):owner=text.split(',',1)[0].split(' ',1)[1]
            match=re.fullmatch(r'\.reloc\s+([^,]+),\s*(R_RISCV_\w+),\s*([^\s,]+)\s*\n?',text)
            if not match:continue
            site,kind,target=match.groups()
            if owner!=OWNER and target not in names:continue
            need(kind in kinds and target in named and len(named[target])==1,'Admitted unique recorded relocation target');pc=int(site.rsplit('_',1)[1],16);need(owner in m['allocations'],'Actual source owner for relocation site');relocations.append({'owner':owner,'offset':pc-m['allocations'][owner]['originalVA'],'type':kinds[kind],'addend':0,'symbol':named[target][0]});statements.append({'source':name,'directive':text})
    shape(roles,relocations);return roles,relocations,statements
def actual_roles(root,path):
    parser=case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py';need(sha(parser)==PARSER,'Immutable bounded ELF parser');E=load(parser,'TX_original_ELF').ELF;e=E(path);section=e.byname[OWNER];need((section['type'],section['flags'],section['size'],section['alignment'])==(1,6,280,2),'Actual original TX owner attributes')
    def role(symbol):
        index=symbol['index'];return {'name':symbol['name'],'owner':e.sections[index]['name'] if 0<index<len(e.sections) else 'ABS' if index==0xfff1 else 'UND','offset':symbol['value'],'bytes':symbol['size'],'info':symbol['info'],'other':symbol['other']}
    roles=[role(s) for s in e.symbols if s['index']==section['index']];relocations=[{'owner':r['owner'],'offset':r['offset'],'type':r['type'],'addend':r['addend'],'symbol':role(r['symbol'])} for r in e.relocations if r['owner']==OWNER or r['symbol']['index']==section['index']];shape(roles,relocations)
    need(hashlib.sha256(e.data(section)).hexdigest()==BODY,'Actual original retained TX body bytes')
    return {'object_sha256':sha(path),'roles':roles,'relocations':relocations}
def controls(decoder,body):
    def f3(w,value):return (w&~0x7000)|(value<<12)
    def imm(w,value):return (w&0xfffff)|((value&4095)<<20)
    def simm(w,value):return (w&~0xfe000f80)|(((value>>5)&127)<<25)|((value&31)<<7)
    cases=[
      ('length_limit1038',0x8a56,lambda w:imm(w,1038)),('signed_length_guard',0x8a5a,lambda w:f3(w,4)),('early_target_before_RET',0x8a5a,lambda w:w^0x100),
      ('frame16',0x8a5e,lambda w:0x1141),('saveS0_wrong_slot',0x8a60,lambda w:0xca22),('handle_LW_not_LHU',0x8a6a,lambda w:f3(w,2)),('first_handle_offset98',0x8a6a,lambda w:imm(w,152)),('context_from_A1',0x8a6e,lambda w:0x892e),
      ('sentinelFFFF',0x8a7c,lambda w:0x17fd),('first_slot138',0x8a86,lambda w:imm(w,312)),('first_argGP132',0x8a8a,lambda w:imm(w,132)),('predicate_no_link',0x8a8e,lambda w:w^0x1000),('predicate_accepts_two',0x8a90,lambda w:0x4789),
      ('second_handle96',0x8a96,lambda w:imm(w,150)),('second_slot140',0x8aaa,lambda w:imm(w,320)),('lane_two',0x8ab8,lambda w:0x4609),('stride1060',0x8ace,lambda w:imm(w,1060)),('REMU_not_MUL',0x8ad2,lambda w:f3(w,7)),
      ('PCREL_high_plus_page',0x8ad6,lambda w:w+0x1000),('PCREL_low_minus_two',0x8ada,lambda w:imm(w,1716)),('ADDI_not_XORI_same_SH_low16',0x8ae0,lambda w:f3(w,0)),('magic_SW_not_SH',0x8aec,lambda w:f3(w,2)),('length_low_wrong_offset',0x8af0,lambda w:simm(w,3)),('length_high_shift16',0x8af4,lambda w:imm(w,16)),
      ('checksum_mask127',0x8b04,lambda w:imm(w,127)),('loop_counter_u8',0x8b0a,lambda w:imm(w,8)),('signed_copy_bound',0x8b10,lambda w:f3(w,4)),('source_S2_not_S1',0x8b52,lambda w:(w&~(31<<15))|(18<<15)),('payload_LB_not_LBU',0x8b56,lambda w:f3(w,0)),('counter_stride_two',0x8b5e,lambda w:0x0589),('payload_wrong_store_offset',0x8b62,lambda w:simm(w,4)),
      ('metadata_zero_SW',0x8b36,lambda w:f3(w,2)),('handle_table96',0x8b3a,lambda w:imm(w,150)),('lane_handle_stride_two',0x8b24,lambda w:0x0606),('S0_restore_wrong_slot',0x8b40,lambda w:0x4452),('send_slot54',0x8b46,lambda w:imm(w,84)),('tail_handle_LHU',0x8b4a,lambda w:f3(w,5)),('send_tail_links_RA',0x8b50,lambda w:w^0x1000),('loop_backedge_links_RA',0x8b6a,lambda w:(w&~0xe000)|0x2000),('failure_return_T1',0x8aca,lambda w:0x8302)]
    result=[]
    for name,pc,change in cases:
        row=decoder.decode(body[pc-decoder.ENTRY:],pc);size=row['bytes'];old=int.from_bytes(bytes.fromhex(row['raw_hex']),'little');new=change(old);need(0<=new<1<<(size*8) and new!=old,'Bounded nonidentity operand control');mutant=bytearray(body);mutant[pc-decoder.ENTRY:pc-decoder.ENTRY+size]=new.to_bytes(size,'little')
        try:decoder.validate(mutant)
        except ValueError as error:result.append({'case':name,'PC':pc,'before':row['raw_hex'],'after':new.to_bytes(size,'little').hex(),'rejected':True,'reason':str(error)})
        else:raise ValueError('Accepted source operand control '+name)
    need(len(result)==40,'Forty targeted raw operand controls');return result
def inspect(root,firmware,objects=()):
    root=Path(root).resolve();firmware=Path(firmware).resolve();need(sha(firmware)==FW and firmware.stat().st_size==76800,'Exact original official ID2966 reference');full=firmware.read_bytes();body=full[0xa56:0xb6e];need(hashlib.sha256(body).hexdigest()==BODY,'Original280B source interval');decoder=load(HERE/'raw.py','TX_independent_raw');rows=decoder.validate(body)
    retained=read(HERE/'retained-disassembly.json');need([(r['PC'],r['bytes'],r['raw_hex']) for r in rows]==[(r['PC'],r['bytes'],r['raw_hex']) for r in retained['rows']],'Full fresh LLVM raw geometry agrees; mnemonic not decoder input')
    manifest=root/'experiments/tsl9-v4160-reply-image-integration/source-manifest.json';need(sha(manifest)==MANIFEST,'Immutable current twelve-image manifest');m=read(manifest);need(m['allocations'][OWNER]['originalVA']==0x8a56 and m['allocations'][OWNER]['bytes']==280 and m['allocations'][OWNER]['sha256']==BODY,'Original owner/extent/body binding');roles,relocations,statements=source_roles(root,m)
    owned,incoming=shape(roles,relocations);incoming_fields=[]
    for row in incoming:
        pc=m['allocations'][row['owner']]['originalVA']+row['offset'];decoded=decoder.decode(full[pc-0x8000:pc-0x8000+4],pc);need(decoded['op']=='jal' and decoded['target']==0x8a56 and decoded['rd'] in (0,1),'Every actual original incoming instruction decoded independently');incoming_fields.append({'owner':row['owner'],'offset':row['offset'],'relocation_type':row['type'],'instruction':decoded,'link_PC':pc+decoded['bytes'] if decoded['rd']==1 else None})
    need(sum(row['instruction']['rd']==1 for row in incoming_fields)==8 and sum(row['instruction']['rd']==0 for row in incoming_fields)==1,'Eight incoming linked calls, one no-link tail; not inferred from relocation type')
    boundaries={r['PC'] for r in rows};leaders={decoder.ENTRY,decoder.END}
    for row in rows:
        if row['op'] in ('beq','bne','bltu','jal','jalr'):
            leaders.add(row['PC']+row['bytes'])
            if row['target'] is not None:need(row['target'] in boundaries,'Exact in-owner branch boundary');leaders.add(row['target'])
    leaders=sorted(leaders);actual=[]
    for path in objects:
        report=actual_roles(root,Path(path));need(count(report['roles'])==count(roles) and count(report['relocations'])==count(relocations),'Actual original/current carrier symbol/RELA roles agree');actual.append({'sha256':report['object_sha256'],'actual_roles_replayed':True})
    need((0x8ad6+0x20002000+1718)&0xffffffff==0x2000b18c and (0xffff8000^0xffffff55)==0x7f55,'Static PCREL and literal algebra; no instruction execution')
    return {'schema':'ID2966-TX-independent-raw-source-v1','passed':True,'firmware_sha256':FW,'entry':decoder.ENTRY,'end_exclusive':decoder.END,'source_bytes':280,'instruction_count':96,'source_sha256':BODY,'decoded_rows':rows,'direct_local_written_GPRs':sorted({r['rd'] for r in rows if r['rd'] not in (None,0)}),'basic_block_extents':list(zip(leaders,leaders[1:])),'raw_operand_controls':controls(decoder,body),'source_roles':roles,'source_RELA':relocations,'source_directives':statements,'incoming_instruction_fields':incoming_fields,'owned_RELA_count':len(owned),'owned_internal_reference_count':10,'external_incoming_count':len(incoming),'recorded_external_interior_references':0,'actual_archived_carriers_replayed':len(actual),'actual_carriers':actual,'callee_GP_SP_S_preservation_proved':False,'single_common_status_proved':False,'physical_packet_or_ROM_identity_proved':False,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False,'OTA_ready':False}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--object',type=Path,action='append',default=[]);p.add_argument('--output',type=Path);a=p.parse_args();r=inspect(a.project_root,a.firmware,a.object)
    if a.output:
        out=a.output.resolve();out.relative_to(HERE);need(not out.exists(),'Create-only source proof');out.write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'passed':True,'source_bytes':280,'instruction_count':96,'raw_operand_controls':len(r['raw_operand_controls']),'owned_RELA_count':11,'external_incoming_count':9,'actual_archived_carriers_replayed':r['actual_archived_carriers_replayed']}))
if __name__=='__main__':main()
