#!/usr/bin/env python3
"""Bounded raw-data comparison; direct JAL operands only, never ISA execution."""
import argparse
import hashlib
import json
from pathlib import Path

OLD='32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'
BOOT='650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
NEW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
EVIDENCE='545b2a3ece433c0bd1676e7e3195565f748f1c5c689ef6cf30d050020bcc0c54'
PAIRS=[('status',0x18be4,0x18e90,8),('unlock',0x18bec,0x18e98,30),('lock',0x18c0a,0x18eb6,14),('erase',0x18c18,0x18ec4,46),('program',0x18c46,0x18ef2,100)]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def jal(raw,pc):
    need(len(raw)==4,'Only a complete 4B direct instruction')
    word=int.from_bytes(raw,'little');need(word&127==0x6f and (word>>7)&31==1,'Only direct JAL with rd=RA')
    immediate=((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1)
    if immediate&(1<<20):immediate-=1<<21
    return (pc+immediate)&0xffffffff
def compare(project,oldpath,bootpath,newpath,explicit_evidence=None):
    candidates=[project/'apk-analysis/tsl9-function-hardware/fifteenth-round/flash-review/native-evidence.json',project/'analysis/function-hardware/fifteenth-round/flash-review/native-evidence.json']
    candidates=[p for p in candidates if p.is_file()]
    if explicit_evidence is None:need(len(candidates)==1,'Supply --old-evidence for a checkout without the historical source evidence')
    evidence_path=explicit_evidence.resolve(strict=True) if explicit_evidence is not None else candidates[0]
    need(sha(evidence_path.read_bytes())==EVIDENCE,'Pinned old raw evidence')
    evidence=json.loads(evidence_path.read_text(encoding='utf-8'))
    old=oldpath.read_bytes();boot=bootpath.read_bytes();new=newpath.read_bytes()
    need((sha(old),sha(boot),sha(new))==(OLD,BOOT,NEW),'Three exact original images')
    source_inputs={p.relative_to(project).as_posix():sha(p.read_bytes()) for p in [project/'experiments/tsl9-contract-model/src/flash_page.c',project/'experiments/tsl9-contract-model/src/flash_page.h',project/'experiments/tsl9-contract-model/tests/test_flash_page.c']}
    source_inputs['historical_native_evidence']=sha(evidence_path.read_bytes())
    need(source_inputs['experiments/tsl9-contract-model/src/flash_page.c']=='fdfdcddf53e9f3f9cae3a30873893c10fd2689d2892a4fd5e64b6124e16c57fb','Reviewed old model identity')
    counts={}
    for region in evidence['ranges']:
        # Historical image labels vary in case; identity is authoritative.
        image=old if region['input_sha256']==OLD else boot
        cursor=region['lo']
        for row in region['records']:
            raw=bytes.fromhex(row['bytes']);need(row['va']==cursor and len(raw)==row['size'],'Exact old contiguous records')
            need(image[cursor-region['base']:cursor-region['base']+len(raw)]==raw,'Old record bytes match actual image')
            cursor+=len(raw)
        need(cursor==region['hi_exclusive'],'Exact old closed extent')
        counts[region['name']]=len(region['records'])
    rows=[]
    for name,oldva,newva,size in PAIRS:
        a=old[oldva-0x8000:oldva-0x8000+size];b=new[newva-0x8000:newva-0x8000+size]
        need(len(a)==size and a==b,'Full helper byte identity: '+name)
        rows.append({'name':name,'old_runtime_entry':oldva,'ID2966_entry':newva,'bytes':size,'old_new_delta':newva-oldva,'byte_equal':True,'range_sha256':sha(a)})
    before=old[0x9b6c-0x8000:0x9bac-0x8000];after=new[0x9c0a-0x8000:0x9c4a-0x8000]
    offsets=[22,23,30,31,36,37,44,45,48,49]
    need([i for i,(a,b) in enumerate(zip(before,after)) if a!=b]==offsets,'Only exact ten direct-JAL byte changes in64B wrapper')
    targets={a:b for _,a,b,_ in PAIRS};calls=[]
    for off in (20,28,34,42,46):
        oldtarget=jal(before[off:off+4],0x9b6c+off);newtarget=jal(after[off:off+4],0x9c0a+off)
        need(targets[oldtarget]==newtarget,'Actual raw JAL target maps to the matching helper')
        calls.append({'offset':off,'old_site':0x9b6c+off,'old_target':oldtarget,'new_site':0x9c0a+off,'new_target':newtarget})
    return {'schema':'TSL9-Flash-cross-version-raw-comparison-v1','passed':True,'image_sha256':{'old_runtime':OLD,'old_boot':BOOT,'ID2966':NEW},'source_inputs_sha256':source_inputs,'old_evidence_record_counts':counts,'helper_pairs':rows,'wrapper':{'old_entry':0x9b6c,'new_entry':0x9c0a,'bytes':64,'byte_equal':False,'differing_offsets':offsets,'raw_JAL_target_checks':calls},'scope':'Only six bounded functions; no whole-image/physical compatibility inference','original_executed':False,'ISA_emulation':False,'hardware':False,'network':False}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--old-runtime',type=Path)
    parser.add_argument('--boot',type=Path)
    parser.add_argument('--firmware',type=Path)
    parser.add_argument('--old-evidence',type=Path,help='Pinned historical native-evidence.json, required if not included in the checkout')
    parser.add_argument('--output',type=Path,help='Optional new LF UTF-8 JSON path; never overwrite')
    args=parser.parse_args();project=args.project_root.resolve(strict=True)
    bins=project/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs'
    result=compare(project,args.old_runtime or bins/'ID-2581-V4.1.00-decoded.bin',args.boot or project/'apk-analysis/tsl9-server-current/TSL9-boot-api-payload.bin',args.firmware or bins/'ID-2966-V4.1.60-decoded.bin',args.old_evidence)
    if args.output:
        need(not args.output.exists(),'Create-only metadata output')
        args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'passed':True,'helper_bytes_equal':198,'helpers':5,'wrapper_bytes':64,'direct_JAL_targets_checked':5,'wrapper_differing_bytes':10,'original_executed':False,'ISA_emulation':False},sort_keys=True))
if __name__=='__main__':main()
