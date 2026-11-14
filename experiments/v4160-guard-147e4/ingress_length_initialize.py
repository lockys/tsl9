"""Decode ingress counter reset and length formation at 0x89cc–0x89da.

Uses shared synthetic little-endian byte memory; accesses are assumed successful,
including unaligned and wrapping ones. No reachability or hardware claim.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE/'ingress_state_gate.py')
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
MASK=0xffffffff
EXPECTED=bytes.fromhex('2395010803d70d005d8f2397e108')

def put(mem,address,size,value):
    for i in range(size): mem[(address+i)&MASK]=(value>>(i*8))&255

def get(mem,address,size):
    return sum(mem.get((address+i)&MASK,0)<<(8*i) for i in range(size))

def run(code,gp,s11,a5,memory):
    if len(code)!=14 or any(not 0<=x<=MASK for x in (gp,s11,a5)): raise ValueError('invalid input')
    r=[(i*0x1020305)&MASK for i in range(32)]; r[3]=gp; r[27]=s11; r[15]=a5
    pc=0x89cc; events=[]
    while pc<0x89da:
        off=pc-0x89cc
        if off<0 or off+2>len(code): raise ValueError('outside block')
        half=int.from_bytes(code[off:off+2],'little')
        if half&3!=3:
            # C.OR: quadrant 1, funct3=100, bit12=0, bits11:10=11, bits6:5=01.
            if half&0xfc63 != 0x8c41: raise ValueError('unsupported compressed instruction')
            rd=8+((half>>7)&7); rs2=8+((half>>2)&7)
            r[rd]=(r[rd]|r[rs2])&MASK; pc+=2
        else:
            if off+4>len(code): raise ValueError('truncated instruction')
            word=int.from_bytes(code[off:off+4],'little')
            op,rd,f3,rs1,rs2=word&127,(word>>7)&31,(word>>12)&7,(word>>15)&31,(word>>20)&31
            if op==0x23 and f3==1:
                imm=((word>>25)<<5)|((word>>7)&31); addr=(r[rs1]+gate.signed(imm,12))&MASK
                value=r[rs2]&0xffff; events.append(('write',addr,2,value)); put(memory,addr,2,value)
            elif op==3 and f3==5:
                addr=(r[rs1]+gate.signed(word>>20,12))&MASK; value=get(memory,addr,2)
                events.append(('read',addr,2,value)); r[rd]=value
            else: raise ValueError('unsupported instruction')
            pc+=4
        r[0]=0
    if pc!=0x89da: raise ValueError('unexpected final pc')
    return r[14],events

def check(code,gp,s11,a5,initial):
    original=dict(initial); actual=dict(initial)
    counter=(gp+138)&MASK; length=(gp+142)&MASK
    put(original,counter,2,0); loaded=get(original,s11,2); result=(loaded|a5)&MASK
    expected=[('write',counter,2,0),('read',s11,2,loaded),('write',length,2,result&0xffff)]
    put(original,length,2,result)
    observed,events=run(code,gp,s11,a5,actual)
    if (observed,events,actual)!=(result,expected,original): raise ValueError('length initialization mismatch')

def main():
    image=gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x89cc-0x8000:0x89da-0x8000]
    if code!=EXPECTED: raise ValueError('original bytes mismatch')
    for value in range(65536):
        for a5 in (0,0xffff0000):
            memory={}; put(memory,0x1000,2,value)
            check(code,0x20004000,0x1000,a5,memory)
    for gp in (0,0xffffff76,MASK):
        for delta in (-1,0,1,2,3,4,5):
            for a5 in (0,0x10000,MASK):
                counter=(gp+138)&MASK; memory={}
                for i in range(-1,7): memory[(counter+i)&MASK]=(i*37+113)&255
                check(code,gp,(counter+delta)&MASK,a5,memory)
    for i in range(len(code)):
        mutant=bytearray(code); mutant[i]^=1
        try:
            memory={}; put(memory,0x1000,2,0x1234)
            check(mutant,0x20004000,0x1000,0x87650080,memory)
        except ValueError: continue
        raise ValueError(f'undetected byte mutation {i}')
    witness={}; put(witness,0x1000,2,0)
    full,events=run(code,0x20004000,0x1000,0x10000,witness)
    if full!=0x10000 or get(witness,0x2000408e,2)!=0: raise ValueError('full-register versus stored halfword witness missing')
    print('PASS: full a4=0x10000 can coexist with stored length halfword 0 in a synthetic input')
    print('PASS: 131072 value cases, 63 alias/wrap cases and 14 byte mutations')
    print('Ordering: clear gp+138, read [s11], OR full a5, store low halfword at gp+142.')
    print('Synthetic successful accesses; alignment, reachability and hardware not validated.')

if __name__=='__main__': main()
