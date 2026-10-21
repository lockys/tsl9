#!/usr/bin/env python3
"""Bounded raw instruction-field proof; no CPU state, evaluation or emulator."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ENTRY=0x9b8e
END=0x9c0a
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PROTOCOL_SHA='9a66b861219b9d0b2307f5968bd5e44081e40ccb48600ca397713485145d0564'
MANIFEST_SHA='743c087e24760779073cd27ef06b7355b9f61ced6a8b14a2e9fc410d3fa10c5e'
OWNER='.text.tsl9v4160.ota_handler_9b8e'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def case(root,name):return next(p for p in (root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def sx(x,bits):return x-(1<<bits) if x&(1<<(bits-1)) else x
def decode(body,pc):
    """Decode only the admitted RV32I/C integer forms; do not compute register values."""
    offset=pc-ENTRY;h=int.from_bytes(body[offset:offset+2],'little');n=4 if h&3==3 else 2;need(offset+n<=len(body),'Bounded whole instruction');w=int.from_bytes(body[offset:offset+n],'little');r={'PC':pc,'bytes':n,'raw_hex':body[offset:offset+n].hex()}
    def done(op,rd=None,rs1=None,rs2=None,imm=None,target=None,width=None):r.update(op=op,rd=rd,rs1=rs1,rs2=rs2,immediate=imm,target=target,memory_width=width);return r
    if n==4:
        op=w&127;rd=(w>>7)&31;rs=(w>>15)&31;rt=(w>>20)&31;f=(w>>12)&7
        if op==0x37:return done('lui',rd,imm=w&0xfffff000)
        if op==0x13 and f==0:return done('addi',rd,rs,imm=sx(w>>20,12))
        if op==0x13 and f==5 and w>>25==0:return done('srli',rd,rs,imm=(w>>20)&31)
        if op==3 and f==2:return done('lw',rd,rs,imm=sx(w>>20,12),width=32)
        if op==0x23 and f==0:return done('sb',rs1=rs,rs2=rt,imm=sx(((w>>25)<<5)|((w>>7)&31),12),width=8)
        if op==0x6f:
            imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1);return done('jal',rd,target=pc+sx(imm,21))
    else:
        q=h&3;f=h>>13;rd=(h>>7)&31;rt=(h>>2)&31;ci=sx((((h>>12)&1)<<5)|((h>>2)&31),6)
        if q==1 and f==0:return done('addi',rd,rd,imm=ci)
        if q==1 and f==3 and rd==2:
            imm=(((h>>12)&1)<<9)|(((h>>6)&1)<<4)|(((h>>5)&1)<<6)|(((h>>3)&3)<<7)|(((h>>2)&1)<<5);return done('addi',2,2,imm=sx(imm,10))
        if q==1 and f==6:
            imm=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5);return done('beq',rs1=8+((h>>7)&7),rs2=0,target=pc+sx(imm,9))
        if q==2 and f==0 and not h&0x1000:return done('slli',rd,rd,imm=(h>>2)&31)
        if q==2 and f==2:
            imm=(((h>>12)&1)<<5)|(((h>>4)&7)<<2)|(((h>>2)&3)<<6);return done('lw',rd,2,imm=imm,width=32)
        if q==2 and f==6:
            imm=(((h>>9)&15)<<2)|(((h>>7)&3)<<6);return done('sw',rs1=2,rs2=rt,imm=imm,width=32)
        if q==2 and f==4:
            high=(h>>12)&1
            if rt:return done('add',rd,rd,rt) if high else done('mv',rd,rt)
            need(rd!=0,'Admitted nonzero JALR source register');return done('jalr',1 if high else 0,rd,imm=0)
    raise ValueError('Unsupported admitted instruction at '+hex(pc))

# Each tuple is (PC, opcode, rd, rs1, rs2, immediate, target, memory width).
# This independent operand contract is not parsed from R2 mnemonic or ESIL.
EXPECTED=[
 (0x9b8e,'addi',2,2,None,-32,None,None),(0x9b90,'sw',None,2,18,16,None,32),
 (0x9b92,'lui',18,None,None,0x40000,None,None),(0x9b96,'lw',15,18,None,0x70,None,32),
 (0x9b9a,'sw',None,2,9,20,None,32),(0x9b9c,'sw',None,2,19,12,None,32),
 (0x9b9e,'sw',None,2,20,8,None,32),(0x9ba0,'sw',None,2,1,28,None,32),
 (0x9ba2,'sw',None,2,8,24,None,32),(0x9ba4,'mv',19,10,None,None,None,None),
 (0x9ba6,'addi',10,0,None,1026,None,None),(0x9baa,'mv',20,11,None,None,None,None),
 (0x9bac,'mv',9,12,None,None,None,None),(0x9bae,'jalr',1,15,None,0,None,None),
 (0x9bb0,'beq',None,10,0,None,0x9bfa,None),(0x9bb2,'srli',15,9,None,8,None,None),
 (0x9bb6,'sb',None,10,9,1,None,8),(0x9bba,'sb',None,10,15,0,None,8),
 (0x9bbe,'lui',11,None,None,0x20000,None,None),(0x9bc2,'lw',15,18,None,0x4c,None,32),
 (0x9bc6,'addi',11,11,None,4,None,None),(0x9bc8,'add',11,11,9,None,None,None),
 (0x9bca,'mv',8,10,None,None,None,None),(0x9bcc,'addi',12,0,None,1024,None,None),
 (0x9bd0,'slli',11,11,None,10,None,None),(0x9bd2,'addi',10,10,None,2,None,None),
 (0x9bd4,'jalr',1,15,None,0,None,None),(0x9bd6,'mv',10,19,None,None,None,None),
 (0x9bd8,'mv',12,8,None,None,None,None),(0x9bda,'mv',11,20,None,None,None,None),
 (0x9bdc,'addi',13,0,None,1026,None,None),(0x9be0,'jal',1,None,None,None,0x8a56,None),
 (0x9be4,'mv',10,8,None,None,None,None),(0x9be6,'lw',8,2,None,24,None,32),
 (0x9be8,'lw',6,18,None,0x68,None,32),(0x9bec,'lw',1,2,None,28,None,32),
 (0x9bee,'lw',9,2,None,20,None,32),(0x9bf0,'lw',18,2,None,16,None,32),
 (0x9bf2,'lw',19,2,None,12,None,32),(0x9bf4,'lw',20,2,None,8,None,32),
 (0x9bf6,'addi',2,2,None,32,None,None),(0x9bf8,'jalr',0,6,None,0,None,None),
 (0x9bfa,'lw',1,2,None,28,None,32),(0x9bfc,'lw',8,2,None,24,None,32),
 (0x9bfe,'lw',9,2,None,20,None,32),(0x9c00,'lw',18,2,None,16,None,32),
 (0x9c02,'lw',19,2,None,12,None,32),(0x9c04,'lw',20,2,None,8,None,32),
 (0x9c06,'addi',2,2,None,32,None,None),(0x9c08,'jalr',0,1,None,0,None,None)
]
def rows(body):
    pc=ENTRY;result=[]
    while pc<END:r=decode(body,pc);result.append(r);pc+=r['bytes']
    need(pc==END and len(result)==50,'Exact124B/50-instruction extent');return result
def validate(body):
    need(len(body)==124,'Exact source extent');r=rows(body);keys=('PC','op','rd','rs1','rs2','immediate','target','memory_width');observed=[tuple(x[k] for k in keys) for x in r];need(observed==EXPECTED,'Independent exact raw operand/order contract');return r
def symbol_role(e,s):return {'name':s['name'],'owner':e.sections[s['index']]['name'] if 0<s['index']<len(e.sections) else ('ABS' if s['index']==0xfff1 else 'UND'),'offset':s['value'],'bytes':s['size'],'info':s['info'],'other':s['other']}
def carrier_roles(root,path):
    parser=case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py';need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Bounded immutable ELF parser');s=importlib.util.spec_from_file_location('reply_source_ELF',parser);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);e=m.ELF(path);section=e.byname[OWNER];need(section['size']==124 and section['type']==1 and section['flags']==6 and section['alignment']==2,'Actual original source owner');roles=[symbol_role(e,x) for x in e.symbols if x['index']==section['index']];rel=[]
    for r in e.relocations:
        if r['owner']==OWNER or r['symbol']['index']==section['index']:rel.append({'owner':r['owner'],'offset':r['offset'],'type':r['type'],'addend':r['addend'],'symbol':symbol_role(e,r['symbol'])})
    return {'carrier_sha256':sha(path),'owner':OWNER,'bytes':124,'roles':roles,'relocations':rel}
def inspect(root,firmware,carrier=None):
    raw=firmware.read_bytes();need(len(raw)==76800 and sha(firmware)==FW_SHA,'Exact original ID2966 source image');body=raw[ENTRY-0x8000:END-0x8000];decoded=validate(body);retained=read(HERE/'retained-evidence.json');need(retained['raw_body_sha256']==hashlib.sha256(body).hexdigest(),'Retained original source interval')
    need([(x['PC'],x['bytes'],x['raw_hex']) for x in decoded]==[(x['PC'],x['bytes'],x['raw_hex']) for x in retained['r2_rows']],'Retained R2 raw geometry agrees; ESIL not consumed')
    manifest=root/'experiments/tsl9-v4160-register-image-integration/source-manifest.json';need(sha(manifest)==MANIFEST_SHA,'Existing691-layout manifest');m=read(manifest);need(m['allocations'][OWNER]['originalVA']==ENTRY and m['allocations'][OWNER]['bytes']==124 and m['allocations'][OWNER]['sha256']==hashlib.sha256(body).hexdigest(),'Manifest owner/raw source binding')
    producer=root/'experiments/tsl9-v4160-startup/src/ota_handler_native.c';need(sha(producer)==m['source_files'][producer.relative_to(root).as_posix()],'Existing source carrier text binding');text=producer.read_text(encoding='utf-8')
    for literal in retained['source_RELA_statements']:need(literal in text,'Exact recorded incoming/owned relocation statement')
    for role in retained['binding_symbol_roles']:need(role in m['baseline_symbol_roles'],'Existing691 manifest entry/interior symbol role')
    mutations=[('frame16',0x9b8e,'4111'),('allocator_slot74',0x9b96,'83274907'),('index_from_A3',0x9bac,'b684'),('allocation1024',0x9ba6,'13050040'),('call_via_A4',0x9bae,'0297'),('header_shift16',0x9bb2,'93d70401'),('low_index_wrong_byte_offset',0x9bb6,'23009500'),('copy_slot50',0x9bc2,'83270905'),('source_uses_S0',0x9bc8,'a295'),('copy1026',0x9bcc,'13062040'),('copy_shift9',0x9bd0,'a605'),('destination_plus1',0x9bd2,'0505'),('TX_command_from_S3',0x9bda,'ce85'),('TX1024',0x9bdc,'93060040'),('free_slot64',0x9be8,'03234906'),('RA_restore_from24',0x9bec,'e240'),('tail_JR_RA',0x9bf8,'8280'),('null_RET_T1',0x9c08,'0283')];controls=[]
    for name,pc,h in mutations:
        mutant=bytearray(body);at=pc-ENTRY;replacement=bytes.fromhex(h);need(mutant[at:at+len(replacement)]!=replacement,'Nonidentity source control');before=mutant[at:at+len(replacement)].hex();mutant[at:at+len(replacement)]=replacement
        try:validate(mutant)
        except ValueError as error:controls.append({'case':name,'PC':pc,'before':before,'after':h,'rejected':True,'reason':str(error)})
        else:raise ValueError('Accepted new raw operand control '+name)
    result={'schema':'ID2966-page-reply-independent-raw-source-v1','passed':True,'firmware_sha256':FW_SHA,'entry':ENTRY,'end_exclusive':END,'bytes':124,'instructions':50,'raw_body_sha256':hashlib.sha256(body).hexdigest(),'decoded_rows':decoded,'direct_instruction_written_GPRs':sorted({x['rd'] for x in decoded if x['rd'] not in (None,0)}),'raw_controls':controls,'retained_roles':retained['carrier_roles'],'actual_carrier_replayed':False,'original_canonical_FUNC_exists':False,'normal_return_values_normalized':False,'unknown_callee_preservation_proved':False,'computed_interior_entries_proved_absent':False,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False,'OTA_ready':False}
    if carrier:
        actual=carrier_roles(root,carrier);need(actual['owner']==retained['carrier_roles']['owner'] and actual['roles']==retained['carrier_roles']['roles'] and actual['relocations']==retained['carrier_roles']['relocations'],'Actual carrier entry/interior/incoming roles agree');result['actual_carrier_replayed']=True;result['actual_carrier_sha256']=actual['carrier_sha256']
    return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--object',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();r=inspect(a.project_root.resolve(),a.firmware.resolve(),a.object.resolve() if a.object else None)
    if a.output:
        out=a.output.resolve();out.relative_to(HERE);need(not out.exists(),'Create-only source proof');out.write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'passed':True,'bytes':124,'instructions':50,'raw_controls':len(r['raw_controls']),'actual_carrier_replayed':r['actual_carrier_replayed']}))
if __name__=='__main__':main()
