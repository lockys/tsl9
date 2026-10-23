#!/usr/bin/env python3
"""Finite, offline static proof; never execute firmware or a host behavior model."""
import argparse, copy, hashlib, json, os, re, runpy, struct, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
S=json.loads((HERE/'spec.json').read_bytes())
P=runpy.run_path(str(HERE/'probe.py'))
for n,h in S['pins'].items():
    if P['sha'](ROOT/n)!=h:raise ValueError('Frozen input: '+n)
E=runpy.run_path(str(P['READER']))['ELF']
BASE=0x20000332
OFFSETS=[0,4,8,12,16,18,20,22,24,28,32,34,38,42,46,48,52,56]

def need(v,msg):
    if not v:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def original():
    raw=P['CARRIER'].read_bytes();need(sha(raw)==P['CARRIER_SHA'],'Actual candidate identity')
    need(raw[0x4c:0x50]==bytes.fromhex('32030020'),'Candidate slot points to RAM')
    b=raw[0x5a2:0x5dc];need(sha(b)==P['BODY_SHA'],'Actual58B candidate')
    rows=json.loads((ROOT/'analysis/resident-copy-reference-2026-10-21/source/retained-source.json').read_bytes())['groups']['helper']
    need([(r['addr']-0x405a2,r['size']) for r in rows]==[(o,4 if o in {0,4,8,12,24,28,34,38,42,48,52} else 2) for o in OFFSETS],'All18 instruction locations')
    need(bytes.fromhex(''.join(r['bytes'] for r in rows))==b,'Retained bytes match actual carrier')
    need(0x402b0+(BASE-0x20000040)==0x405a2,'Conditional source/RAM correspondence')
    # This checks byte correspondence, not execution/completion of the loader.
    return b,rows

def facts(raw,linked,whole=True):
    e=E(raw);original_bytes,_=original()
    fs=sorted([s for s in e.symbols if s['info']&15==2 and s['size']],key=lambda s:s['value'] if linked else s['section'])
    need(len(fs)==6,'Six genuine regions')
    starts={};code=b''
    for s,(name,off,size) in zip(fs,S['regions']):
        need([s['name'],s['size']]==[name,size] and s['info']>>4==1,'Strong region identity/size/binding')
        need(s['section'] not in (0,0xfff1),'No fabricated provider')
        sec=e.sections[s['section']];starts[s['section']]=off
        index=s['value']-sec['address'] if linked else s['value']
        need(index==(off if linked else 0),'Exact region source offset')
        need(not linked or s['value']==BASE+off,'Conditional original RAM region PCs')
        code+=e.data(sec)[index:index+size]
    need(len(code)==58,'Exactly58owned code bytes')
    need(not [s for s in e.symbols if s['name'] and s['section']==0],'No undefined provider')
    need(not [s for s in e.symbols if s['info']>>4 and s['section']==0xfff1],'No absolute global provider')
    if linked:
        sec=e.section('.copy')
        need(sec['address']==BASE and sec['flags']==6 and sec['size']==58,'Exact allocated executable non-writable section')
        alloc=[s for s in e.sections if s['flags']&2 and s['size']]
        need(len(alloc)==1 and alloc[0]['name']=='.copy','No other allocated data/filler')
        need(struct.unpack_from('<H',e.raw,16)[0]==2 and struct.unpack_from('<I',e.raw,24)[0]==BASE,'Real executable entry')
        need(not e.relocations and code==original_bytes,'Whole58 linked bytes match actual candidate')
    else:
        rels=[[starts[r['section']]+r['offset'],r['type'],e.symbols[r['symbol']]['name'],r['addend']] for r in e.relocations]
        need(rels==S['relocations'],'All5 actual pending relocations and targets')
        need(struct.unpack_from('<H',e.raw,16)[0]==1,'Actual relocatable input')
        masks=bytearray(b'\xff'*58)
        for off,kind,name,add in rels:
            n,mask={44:(2,0xe383),16:(4,0x01fff07f),45:(2,0xe003)}[kind]
            masks[off:off+n]=mask.to_bytes(n,'little')
        need(all(not ((a^b)&m) for a,b,m in zip(code,original_bytes,masks)),'All nonrelocation bits and registers')
    if whole:need(sha(raw)==S['ELF_sha256']['linked' if linked else 'object'],'Whole ELF metadata identity')
    return e,code

def ir_contract(t,mode,whole=True):
    names=re.findall(r'^define .*?@(\w+)\(',t,re.M)
    need(names==[r[0] for r in S['regions']],'All6 C region definitions')
    scalars=[l.strip() for l in t.splitlines() if re.match(r'\s*%\d+ = (?:add |inttoptr |load volatile |zext |trunc )',l) or re.match(r'\s*store volatile ',l)]
    need(scalars==S['scalar_rows'][mode],'Exact18 C scalar/SSA/volatile lines')
    need('alloca ' not in t and not re.search(r'call.*@(?!llvm)',t),'No hidden stack or ordinary call')
    need('={x10},={x11},={x12},={x13},={x14},={x15},={x16}' in t and '{x17}' not in t and '{x5}' not in t,'Original live-register ports without T0/A7')
    need('asm sideeffect "fence.i", "~{memory}"' in t,'Explicit FENCE.I memory port')
    canonical='\n'.join(l for l in t.splitlines() if not l.startswith(('; ModuleID','source_filename')))+'\n'
    if whole:need(sha(canonical.encode())==S['IR_sha256'][mode],'Complete path-independent IR')
    return scalars

def rejects(fn):
    try:fn()
    except (ValueError,KeyError,IndexError,struct.error):return True
    return False
def negative_controls(obj,exe,ir,mode):
    eo,_=facts(obj,False);el,_=facts(exe,True);n=0
    for off in OFFSETS:
        b=bytearray(exe);b[el.section('.copy')['offset']+off]^=1
        need(rejects(lambda:facts(bytes(b),True,False)),'Instruction mutation rejected');n+=1
    symsec=next(s for s in eo.sections if s['type']==2)
    for i,s in enumerate(eo.symbols):
        if s['info']&15!=2 or not s['size']:continue
        b=bytearray(obj);b[symsec['offset']+16*i+12]=(s['info']&15)|0x20
        need(rejects(lambda:facts(bytes(b),False,False)),'Weak binding rejected');n+=1
    for sec in eo.sections:
        if sec['type']!=4:continue
        for off in range(0,sec['size'],12):
            b=bytearray(obj);b[sec['offset']+off+8]^=2
            need(rejects(lambda:facts(bytes(b),False,False)),'Addend mutation rejected');n+=1
    for line in S['scalar_rows'][mode]:
        mutated=line.replace('volatile ','') if 'volatile ' in line else line.replace('add i32','sub i32') if 'add i32' in line else line.replace('inttoptr','bitcast').replace('zext','sext').replace('trunc','zext')
        need(mutated!=line and rejects(lambda:ir_contract(ir.replace(line,mutated,1),mode,False)),'Scalar mutation rejected');n+=1
    need(rejects(lambda:ir_contract(ir.replace('{x16}','{x17}'),mode,False)),'Register port mutation rejected');n+=1
    b=bytearray(exe);b[24]^=2
    need(rejects(lambda:facts(bytes(b),True,False)),'Entry mutation rejected');n+=1
    b=bytearray(exe);shoff=struct.unpack_from('<I',b,32)[0]
    struct.pack_into('<I',b,shoff+40*el.section('.copy')['index']+8,7)
    need(rejects(lambda:facts(bytes(b),True,False)),'Writable text mutation rejected');n+=1
    need(n==50,'All50 bounded negative controls')
    return n

def audit(folder):
    record=json.loads((folder/'measurement.json').read_bytes());llvm=Path(os.environ.get('TSL9_LLVM_BIN',str(Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')))
    # Portable producer output is original evidence; resolve only declared roots.
    def resolve(p):
        p=p.replace('\\','/')
        if p.startswith('${TSL9_ROOT}/'):return ROOT/p[len('${TSL9_ROOT}/'):]
        if p.startswith('${PROJECT_ROOT}/'):return ROOT/p[len('${PROJECT_ROOT}/'):]
        if p.startswith('${LLVM_BIN}/'):return llvm/p[len('${LLVM_BIN}/'):]
        if p.startswith('${LLVM_ROOT}/'):return llvm.parent/p[len('${LLVM_ROOT}/'):]
        return Path(p)
    for p,h in record['inputs'].items():need(P['sha'](resolve(p))==h,'Retained input identity')
    results={}
    for mode in ('c','cpp'):
        r=record['modes'][mode];f=folder/mode
        need(r['all_recipes_succeeded'] and len(r['recipes'])==5 and all(x['exit']==0 for x in r['recipes']),'Actual compiler/link/read commands succeeded')
        for a in r['artifacts']:need(P['sha'](resolve(a['path']))==a['sha256'] and resolve(a['path']).stat().st_size==a['bytes'],'Complete producer artifacts')
        obj=(f/'native.o').read_bytes();exe=(f/'CANDIDATE-COMPONENT-ONLY.elf').read_bytes();ir=(f/'native.ll').read_text(encoding='utf8')
        facts(obj,False);facts(exe,True);ir_contract(ir,mode)
        rows=re.findall(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)',(f/'linked.log').read_text(encoding='utf8'),re.M)
        need([(int(pc,16),bytes.fromhex(b)) for pc,b in rows]==[(BASE+o,original()[0][o:o+(4 if o in {0,4,8,12,24,28,34,38,42,48,52} else 2)]) for o in OFFSETS],'All18 LLVM original-PC byte rows')
        results[mode]=dict(code_bytes=58,instructions=18,strong_regions=6,pending_object_relocations=5,linked_UND=0,linked_relocations=0,extra_scratch_writes=0,whole_code_equal_candidate=True,ELF_sha256=sha(exe),negative_controls=negative_controls(obj,exe,ir,mode))
    return dict(schema='TSL9-SDK-candidate-copy-arch-static-proof-v1',passed=True,results=results,
        inputs=[dict(path=p,sha256=h) for p,h in S['pins'].items()],checker_sha256=P['sha'](Path(__file__)),
        probe_receipt=dict(path=(folder/'measurement.json').relative_to(ROOT).as_posix(),sha256=P['sha'](folder/'measurement.json')),
        reference_candidate_only=True,installed_TSL9_identity_proved=False,full_startup_proved=False,whole_resident_ABI_proved=False,target_executed=False,ISA_emulated=False,hardware_OTA_proved=False,firmware_ready=False)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--folder',required=True,type=Path);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    folder=a.folder.resolve();need(folder.is_relative_to(HERE/'build'),'Owned evidence directory')
    result=audit(folder);encoded=(json.dumps(result,indent=2)+'\n').encode();p=folder/'verification.json'
    if a.write:need(not p.exists(),'Create-only receipt');p.write_bytes(encoded)
    else:need(p.read_bytes()==encoded,'Read-only complete replay')
    print(json.dumps(dict(passed=True,modes=result['results'],firmware_ready=False)))
if __name__=='__main__':main()
