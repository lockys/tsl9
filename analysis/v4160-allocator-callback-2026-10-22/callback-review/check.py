"""Static allocator callback-word ownership; metadata default, explicit retained refs only."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD='5869c85d3dacc8e901df14378da8f5107fc24febe72409c2329d07cf849b4c6d'
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def closed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact source proof seal')
    for n,h in read(folder/'seal.json')['members'].items():need(sha(folder/n)==(h if isinstance(h,str) else h['sha256']),'Immutable source member '+n)
def prior(root):
    folder=case(root,'v4160-ota-source-wiring-2026-10-22')/'allocator-review';closed(folder,OLD)
    spec=importlib.util.spec_from_file_location('callback_prior_allocator',folder/'check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def decoder(root):
    previous=prior(root).decoder(root)
    def decode(raw,pc):
        h=int.from_bytes(raw[:2],'little');v=int.from_bytes(raw[:4],'little')
        fields=dict(PC=pc,bytes=2,raw_hex=raw[:2].hex(),rd=None,rs1=None,rs2=None,immediate=None,target=None,memory_width=None)
        if h&3==2 and h>>13==1:
            fields.update(op='qk.c.lhu',rd=8+((h>>2)&7),rs1=8+((h>>7)&7),immediate=((h>>10)&7)*8+((h>>5)&3)*2,memory_width=16);return fields
        if h&3==1 and h>>13==4 and (h>>10)&3==3 and not(h&4096) and (h>>5)&3==3:
            fields.update(op='and',rd=8+((h>>7)&7),rs1=8+((h>>7)&7),rs2=8+((h>>2)&7));return fields
        if v&127==103 and (v>>12)&7==0:
            immediate=v>>20;immediate=immediate-4096 if immediate&2048 else immediate
            fields.update(bytes=4,raw_hex=raw[:4].hex(),op='jalr',rd=(v>>7)&31,rs1=(v>>15)&31,immediate=immediate);return fields
        return previous(raw,pc)
    return decode
def rows(raw,pc,decode):
    result=[];at=0
    while at<len(raw):
        r=decode(raw[at:],pc+at);need(at+r['bytes']<=len(raw),'Whole bounded field row');result.append(r);at+=r['bytes']
    return result
def target(hi,lo):
    need(hi['op']=='auipc' and lo['op']=='jalr' and hi['rd']==lo['rs1'],'Actual AUIPC/JALR register pair')
    return (hi['PC']+hi['immediate']+lo['immediate'])&0xfffffffe
def scan(raw,word):
    """Bounded adjacent standard encoding patterns, not whole-ROM disassembly/CFG."""
    records=[];stores=[];addresses=[]
    for at in range(0,len(raw)-7,2):
        hi=int.from_bytes(raw[at:at+4],'little');lo=int.from_bytes(raw[at+4:at+8],'little');base=(hi>>7)&31
        if hi&127!=55 or hi&0xfffff000!=0x20003000 or base==0 or (lo>>15)&31!=base:continue
        op=lo&127;f=(lo>>12)&7;imm=lo>>20 if op in (3,19) else ((lo>>25)<<5)|((lo>>7)&31)
        imm=imm-4096 if imm&2048 else imm;address=0x20003000+imm
        item=dict(LUI_PC=0x40000+at,access_PC=0x40000+at+4,base_GPR=base,raw_hex=raw[at:at+8].hex())
        if op==3 and f==2 and address==word:records.append(dict(item,rd=(lo>>7)&31))
        if op==35 and f in (0,1,2) and address<word+4 and address+(1<<f)>word:stores.append(dict(item,rs2=(lo>>20)&31,width_bits=8<<f))
        if op==19 and f==0 and address==word:addresses.append(dict(item,rd=(lo>>7)&31))
    literal=word.to_bytes(4,'little');hits=[0x40000+n for n in range(len(raw)-3) if raw[n:n+4]==literal]
    return dict(adjacent_LUI_LW=records,adjacent_standard_store_overlaps=stores,adjacent_LUI_ADDI_address=addresses,U32LE_literal_offsets=hits,all_segment_halfword_offsets_examined=True,whole_CFG_or_computed_reference_inventory=False)
def gate(record):
    prefix=record['init_prefix'];start=prefix[0]['PC'];p={r['PC']-start:r for r in prefix};z=record['zero_helper'];base=record['config_destination'];word=record['callback_word']
    def exact(off,**fields):need(all(p[off][k]==v for k,v in fields.items()),'Candidate config-owner field '+hex(start+off))
    exact(0x12,op='qk.c.lhu',rd=14,rs1=10,immediate=4,memory_width=16)
    exact(0x1c,op='mv',rd=9,rs1=10)
    need(target(p[0x28],p[0x2c])==0x200004bc,'Prior validation call remains an explicit live-state boundary')
    exact(0x46,op='lui',rd=8,immediate=0x20003000)
    exact(0x4a,op='addi',rd=12,rs1=0,immediate=64);exact(0x4e,op='addi',rd=11,rs1=0,immediate=0)
    exact(0x50,op='addi',rd=10,rs1=8,immediate=base-0x20003000)
    need(target(p[0x54],p[0x58])==0x2000039c,'Candidate zero-request numeric callee')
    exact(0x5c,op='addi',rd=12,rs1=0,immediate=64);exact(0x60,op='mv',rd=11,rs1=9)
    exact(0x62,op='addi',rd=10,rs1=8,immediate=base-0x20003000)
    need(target(p[0x66],p[0x6a])==0x20000332,'Actual bounded copy provider target')
    need(base+52==word and base<=word<base+64,'Copied config field52 owns callback word under normal live-state/copy conditions')
    need(len(z)==9 and sum(r['bytes'] for r in z)==30,'Complete bounded zero helper')
    need((z[0]['op'],z[0]['rd'],z[0]['immediate'])==('lui',15,0x20003000) and (z[1]['op'],z[1]['rd'],z[1]['immediate'])==('lui',14,0x20003000),'Zero range numeric bases')
    lower=0x20003000+z[2]['immediate'];upper=0x20003000+z[3]['immediate']
    need((z[4]['op'],z[4]['rs1'],z[4]['rs2'],z[4]['target'])==('bgeu',14,15,0x20000038),'Unsigned inclusive zero range gate')
    need((z[6]['op'],z[6]['rs1'],z[6]['rs2'],z[6]['immediate'])==('sw',15,0,0),'Zero value stored, not a callback function pointer')
    need((z[7]['rd'],z[7]['rs1'],z[7]['immediate'])==(15,15,4) and z[8]['target']==z[4]['PC'],'Zero stride/backedge')
    need(lower<=word and word+4<=upper+4 and (word-lower)%4==0,'Conditional startup zero covers full callback word')
    need(target(record['initializer_zero_tail'][0],record['initializer_zero_tail'][1])==0x20000022 and record['initializer_zero_tail'][1]['rd']==0,'Candidate initializer numeric tail to zero helper')
    inv=record['inventory'];need(len(inv['adjacent_LUI_LW'])==12 and not inv['adjacent_standard_store_overlaps'] and not inv['adjacent_LUI_ADDI_address'] and not inv['U32LE_literal_offsets'],'Exact bounded syntactic inventory, not computed-store absence')
    return dict(conditional_zero_interval=[lower,upper+4],conditional_copied_config_field=52,callback_word=word,config_destination=base,numeric_copy_target=0x20000332,source_pointer='live S1 after prior calls; each source byte is read freshly',installed_identity_proved=False,callback_lifetime_proved=False)
def candidate_data(root,refs):
    C=prior(root);R,old,_=C.references(root);folder=Path(refs).resolve(strict=True);C.inputs(root,folder)
    pins=read(old/'reference-pins.json')['candidate_files'];contract=read(folder/'resident-entry/contract.json');out=[]
    for name,entry,base in [('carrier',0x43d0a,0x2000323c),('carrier-dec2023',0x43c7e,0x200031ec)]:
        data=(folder/name/pins[name]['segment']).read_bytes();slot=int.from_bytes(data[0xa4:0xa8],'little');need(slot==entry,'Actual slot400A4 numeric entry')
        for off,value in [(0x48,0x2000039c),(0x4c,0x20000332)]:need(int.from_bytes(data[off:off+4],'little')==value,'Actual candidate slot identity')
        if name=='carrier':seed=0x402d2;oldrows=contract['entry']['initializer_instructions']
        else:seed=0x40292;oldrows=contract['historical_mapped_callee_comparison']['initializer_instructions']
        tail=oldrows[-2:];tailpc=tail[0]['VA'];tailbytes=data[tailpc-0x40000:tailpc-0x40000+8]
        need(tailbytes.hex()==''.join(r['raw_hex'] for r in tail),'Actual initializer tail agrees with existing sealed source')
        out.append(dict(candidate=name,segment_sha256=pins[name]['segment_sha256'],slot400A4=slot,config_destination=base,callback_word=base+52,init_prefix_bytes=data[entry-0x40000:entry-0x40000+114],zero_bytes=data[seed-0x40000:seed-0x40000+30],zero_flash=seed,initializer_zero_tail_bytes=tailbytes,initializer_zero_tail_PC=tailpc,segment=data))
    return out
def capture_record(item,decode):
    r={k:v for k,v in item.items() if k not in ('init_prefix_bytes','zero_bytes','initializer_zero_tail_bytes','segment')}
    r.update(init_prefix=rows(item['init_prefix_bytes'],item['slot400A4'],decode),zero_helper=rows(item['zero_bytes'],0x20000022,decode),initializer_zero_tail=rows(item['initializer_zero_tail_bytes'],item['initializer_zero_tail_PC'],decode),inventory=scan(item['segment'],item['callback_word']))
    r['facts']=gate(r);return r
def controls(item,decode,expected):
    result=[]
    # Actual byte mutations affect real source fields, not a fake resident execution.
    for key,offset,field,label in [('init_prefix_bytes',0x62,'immediate','config destination'),('init_prefix_bytes',0x5c,'immediate','copy count64'),('zero_bytes',22,'rs2','startup zero value')]:
        original=item[key];pc=item['slot400A4'] if key=='init_prefix_bytes' else 0x20000022;old=decode(original[offset:],pc+offset);found=None
        for bit in range(old['bytes']*8):
            raw=bytearray(original);raw[offset+bit//8]^=1<<(bit%8)
            try:r=decode(raw[offset:],pc+offset)
            except ValueError:continue
            fields=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if r[field]==old[field] or any(r[k]!=old[k] for k in fields if k!=field):continue
            found=(raw,r,bit);break
        need(found is not None,'Actual one-field control '+label);raw,r,bit=found;changed=dict(expected);changed['init_prefix' if key=='init_prefix_bytes' else 'zero_helper']=rows(raw,pc,decode)
        try:gate(changed)
        except ValueError:result.append(dict(case=label,PC=pc+offset,field=field,bit=bit,rejected=True));continue
        raise ValueError('Accepted ownership field mutation')
    raw=bytearray(item['segment']);ref=expected['inventory']['adjacent_LUI_LW'][0];at=ref['access_PC']-0x40000;raw[at+2]^=0x10
    changed=dict(expected);changed['inventory']=scan(raw,item['callback_word'])
    try:gate(changed)
    except ValueError:result.append(dict(case='callback load offset',PC=ref['access_PC'],field='immediate',bit=20,rejected=True))
    else:raise ValueError('Accepted callback load-offset mutation')
    return result
def inspect(root,firmware=None,candidate_root=None):
    root=Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists():closed(HERE,sha(HERE/'seal.json'))
    C=prior(root);ledger=read(HERE/'ledger.json');need(len(ledger['candidates'])==2,'Two candidate records')
    for record in ledger['candidates']:gate(record)
    need((firmware is None)==(candidate_root is None),'Supply both --firmware and --candidate-root, or neither')
    result=dict(schema='TSL9-callback-word-owner-review-v1',passed=True,metadata_only=firmware is None,actual_original_firmware_read=False,actual_candidate_sources_read=0,raw_controls_replayed=False,conditional_config_copy_owner_confirmed=True,callback_function_identity_proved=False,callback_lifetime_proved=False,installed_resident_identity_proved=False,ambient_A2_independence_proved=False,whole_ROM_reference_absence_proved=False,App_config_actually_zero_proved=False,full_original_ABI_proved=False,new_provider_or_BIN_generated=False,compiler_or_HOST_run=False,target_execution=False,ISA_emulation=False,network=False,hardware=False)
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Actual official ID2966');_,_,reply=C.references(root)
        need(C.rows(Path(firmware).read_bytes()[0xbb4c:0xbba6],0x13b4c,C.decoder(root))==read(reply/'source-ledger.json')['rows']['allocate_copy_TX_free'],'Original App ambient-A2 frontier remains source-bound')
        decode=decoder(root);negative=[]
        for item,expected in zip(candidate_data(root,candidate_root),ledger['candidates']):
            actual=capture_record(item,decode);need(actual==expected,'Actual prefix, zero helper, tail and complete bounded pattern inventory');negative+=controls(item,decode,expected)
        result.update(actual_original_firmware_read=True,actual_candidate_sources_read=2,actual_init_prefix_bytes_per_candidate=114,actual_init_prefix_rows_per_candidate=41,actual_zero_helper_bytes_per_candidate=30,actual_zero_helper_rows_per_candidate=9,actual_initializer_tail_bytes_per_candidate=8,adjacent_callback_load_pairs_per_candidate=12,raw_controls_replayed=True,raw_controls=len(negative),controls=negative)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--candidate-root',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.candidate_root)))
