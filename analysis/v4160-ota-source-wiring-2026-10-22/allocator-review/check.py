"""Bounded static candidate allocator review. No code generation or target execution."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PRIOR_SEAL='5b915632290d82c30545fa9ec517fc96bb67d706abf71f592e53354c3a622a8c'
REPLY_SEAL='c7f659d4edcad4e9412a7cbb05b3e74c28d806c86287b78bbcd22e7d3d1c8281'
TD_SHA='d18a5c4d0722e20d3d0398f180931118a5125c9ada56a64d32c602ad5bd71490'

def need(value,message):
    if not value:raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def case(root,name):return next(p for p in (root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def load(path):
    spec=importlib.util.spec_from_file_location('allocator_prior_reader',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def closed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact existing proof seal')
    for n,v in read(folder/'seal.json')['members'].items():need(sha(folder/n)==(v if isinstance(v,str) else v['sha256']),'Existing immutable member '+n)
def references(root):
    prior=case(root,'v4160-ota-handler-compact-2026-10-22')/'callee-review';closed(prior,PRIOR_SEAL)
    reply=case(root,'v4160-ota-handler-layout-2026-10-22')/'reply-review';closed(reply,REPLY_SEAL)
    return load(prior/'review.py'),prior,reply
def decoder(root):
    R,_,_=references(root);previous,_,_=R.context(root)
    def decode(raw,pc):
        h=int.from_bytes(raw[:2],'little')
        # LLVM's existing HasVendorXwchc QK_C_SH: funct3=101, OPC_C2;
        # compact registers, imm[5:3]=12:10 and imm[2:1]=6:5.
        if h&3==2 and h>>13==5:
            return dict(PC=pc,bytes=2,raw_hex=raw[:2].hex(),op='qk.c.sh',rd=None,rs1=8+((h>>7)&7),rs2=8+((h>>2)&7),immediate=((h>>10)&7)*8+((h>>5)&3)*2,target=None,memory_width=16)
        if h&3==0 and h>>13==5:
            return dict(PC=pc,bytes=2,raw_hex=raw[:2].hex(),op='qk.c.sb',rd=None,rs1=8+((h>>7)&7),rs2=8+((h>>2)&7),immediate=((h>>12)&1)+((h>>10)&3)*8+((h>>5)&3)*2,target=None,memory_width=8)
        return previous(raw,pc)
    return decode
def rows(blob,pc,decode):
    out=[];at=0
    while at<len(blob):
        r=decode(blob[at:],pc+at);need(at+r['bytes']<=len(blob),'Whole bounded instruction');out.append(r);at+=r['bytes']
    return out
def inputs(root,refs):
    R,prior,_=references(root);folder=Path(refs).resolve(strict=True)
    R.closed(folder/'resident-entry',R.ENTRY_SEAL);contract=read(folder/'resident-entry/contract.json');pins=read(prior/'reference-pins.json')['candidate_files']
    need(sha(folder/'instruction-reference/RISCVInstrInfoXwch.td')==TD_SHA,'Pinned conditional Xwchc format source')
    mapping=contract['entry']['word_copy_contracts'][0];hist=contract['historical_mapped_callee_comparison']
    result=[]
    for name,source,destination in [('carrier',mapping['source']['start'],mapping['destination_start']),('carrier-dec2023',hist['copy_source'],hist['copy_destination'])]:
        pin=pins[name];p=folder/name/pin['segment'];need(sha(p)==pin['segment_sha256'] and sha(folder/pin['hex'])==pin['hex_sha256'],'Existing candidate source identity')
        raw=p.read_bytes();target=int.from_bytes(raw[0x70:0x74],'little');need(target==0x20000236 and destination==0x20000040,'Actual slot40070 and mapped initialization destination')
        flash=source+(target-destination);wrapper=raw[flash-0x40000:flash-0x40000+86];prefix=raw[source-0x40000:source-0x40000+110]
        result.append(dict(candidate=name,slot=0x40070,raw_target=target,mapped_wrapper_flash=flash,mapped_core_flash=source,RAM_core=destination,wrapper=wrapper,core_prefix=prefix,callback_word_address=0x20003270 if name=='carrier' else 0x20003220))
    return result
def gate(wrapper,prefix,callback):
    w={r['PC']:r for r in wrapper};p={r['PC']:r for r in prefix};b=0x20000236;c=0x20000040
    def exact(d,pc,**fields):need(all(d[pc][k]==v for k,v in fields.items()),'Actual allocator source frontier '+hex(pc))
    exact(w,b,op='addi',rd=2,rs1=2,immediate=-16)
    for off,reg,slot in [(2,9,4),(4,18,0),(10,1,12),(12,8,8)]:exact(w,b+off,op='sw',rs1=2,rs2=reg,immediate=slot)
    exact(w,b+14,op='lw',rd=18,rs1=9,immediate=524);exact(w,b+18,op='sw',rs1=9,rs2=0,immediate=524);exact(w,b+22,op='fence.i')
    exact(w,b+56,op='jal',rd=1,target=c)
    exact(w,b+66,op='qk.c.sh',rs1=10,rs2=8,immediate=4,memory_width=16)
    exact(w,b+68,op='qk.c.sb',rs1=10,rs2=15,immediate=6,memory_width=8)
    for off,reg,slot in [(32,1,12),(34,8,8),(36,9,4),(38,18,0)]:exact(w,b+off,op='lw',rd=reg,rs1=2,immediate=slot)
    need(not any(r['rd']==12 or r['rs1']==12 or r['rs2']==12 for r in wrapper),'Wrapper has no explicit A2 read/write/store, but calls core with A2 live')
    need(not any(r['rd']==12 or r['rs1']==12 or r['rs2']==12 for r in prefix),'Reviewed core prefix leaves A2 live through indirect call')
    exact(p,c+0x50,op='lui',rd=14,immediate=0x20003000)
    exact(p,c+0x54,op='lw',rd=14,rs1=14,immediate=callback-0x20003000,memory_width=32)
    exact(p,c+0x5e,op='addi',rd=10,rs1=0,immediate=1)
    exact(p,c+0x60,op='jalr',rd=1,rs1=14,immediate=0)
    exact(p,c+0x5c,op='or',rd=11,rs1=11,rs2=15)
    need([(r['PC'],r['rs1']) for r in prefix if r['op']=='jalr' and r['rd']==1]==[(c+0x60,14)],'Exactly one opaque indirect call in reviewed core prefix')
    return True
def controls(blob,pc,decode,other,callback,wrapper):
    out=[]
    choices=[(pc+56,'rd','linked core call'),(pc+66,'rs2','header length store')] if wrapper else [(pc+0x54,'immediate','fresh fallback slot'),(pc+0x60,'rs1','indirect target register')]
    before=rows(blob,pc,decode);index={r['PC']:r for r in before}
    for at,field,label in choices:
        old=index[at];found=None
        for bit in range(old['bytes']*8):
            raw=bytearray(blob);raw[at-pc+bit//8]^=1<<(bit%8)
            try:r=decode(raw[at-pc:],at)
            except ValueError:continue
            keys=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if r[field]==old[field] or any(r[k]!=old[k] for k in keys if k!=field):continue
            found=(raw,r,bit);break
        need(found is not None,'Single-field byte control '+label);raw,r,bit=found
        try:gate(rows(raw,pc,decode) if wrapper else other,other if wrapper else rows(raw,pc,decode),callback)
        except ValueError:out.append(dict(case=label,PC=at,field=field,bit=bit,original=old[field],mutated=r[field],rejected=True));continue
        raise ValueError('Accepted allocator field mutation')
    return out
def inspect(root,firmware=None,candidate_root=None):
    root=Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists():closed(HERE,sha(HERE/'seal.json'))
    _,_,reply=references(root);ledger=read(HERE/'source-ledger.json');need(len(ledger['candidates'])==2,'Two bounded retained candidates')
    for item in ledger['candidates']:
        for key in ('wrapper','core_prefix'):need(hashlib.sha256(b''.join(bytes.fromhex(r['raw_hex']) for r in item[key])).hexdigest()==item[key+'_sha256'],'Metadata row byte closure')
        gate(item['wrapper'],item['core_prefix'],item['callback_word_address'])
    need((firmware is None)==(candidate_root is None),'Use both --firmware and --candidate-root, or neither')
    result=dict(schema='TSL9-conditional-slot70-static-review-v1',passed=True,metadata_only=firmware is None,actual_original_firmware_read=False,actual_candidate_bodies_read=0,raw_operand_controls_replayed=False,conditional_candidate_CFG_forwards_A2_to_unknown_call=True,installed_resident_identity_proved=False,allocation_transitive_A2_independence_proved=False,pointer_nonescape_proved=False,dropping_ambient_arguments_authorized=False,full_original_ABI_proved=False,physical_Flash_or_NV_ownership_proved=False,new_provider_or_BIN_generated=False,compiler_or_HOST_run=False,target_execution=False,ISA_emulation=False,network=False,hardware=False)
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Exact official Runtime ID2966');decode=decoder(root);data=Path(firmware).read_bytes()
        expected=read(reply/'source-ledger.json')['rows']['allocate_copy_TX_free'];need(rows(data[0xbb4c:0xbba6],0x13b4c,decode)==expected,'Actual original90B caller context and incoming ambient A2')
        negatives=[];sources=[]
        for item,retained in zip(inputs(root,candidate_root),ledger['candidates']):
            w=rows(item['wrapper'],0x20000236,decode);p=rows(item['core_prefix'],0x20000040,decode)
            need(item['candidate']==retained['candidate'] and w==retained['wrapper'] and p==retained['core_prefix'],'Actual source bytes and all fields match retained bounded bodies');gate(w,p,item['callback_word_address'])
            negatives+=controls(item['wrapper'],0x20000236,decode,p,item['callback_word_address'],True)
            negatives+=controls(item['core_prefix'],0x20000040,decode,w,item['callback_word_address'],False)
            sources.append({k:v for k,v in item.items() if k not in ('wrapper','core_prefix')})
        result.update(actual_original_firmware_read=True,actual_candidate_bodies_read=4,reviewed_bytes_per_candidate=196,raw_operand_controls_replayed=True,raw_operand_controls=len(negatives),controls=negatives,candidate_sources=sources,stop_boundary='fresh indirect target from RAM20003270/V1.40 or20003220/V1.31; allocation-search branch beyond prefix also not reviewed')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--candidate-root',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.candidate_root)))
