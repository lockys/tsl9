"""Bounded replay of one V1.31 lookup with two synthetic registry nodes."""
from pathlib import Path
from hashlib import sha256
from struct import pack_into, unpack_from
import sys


def need(ok):
    if not ok: raise ValueError('attribute lookup evidence mismatch')


def check(path):
    b=Path(path).read_bytes(); need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    p=0x20000a48; code=b[0xcb8:0xd04]
    need(b[0xbb44:0xbb4c].hex()=='9750fb1fe78040f0' and 0x4bb44+0x1ffb5000-252==p)
    need(b[0xbb50:0xbb52].hex()=='aa84' and b[0xbb6c:0xbb72].hex()=='a6854e850298')
    def run(key,rows,out):
        m=bytearray(2048); w=lambda a:unpack_from('<I',m,a)[0]; h=lambda a:unpack_from('<H',m,a)[0]
        for n,base,tab,seq in [(64,128,256,(3,4)),(128,0,512,rows)]:
            pack_into('<IHHI',m,n,base,len(seq),0,tab)
            for i,v in enumerate(seq):pack_into('<H',m,tab+16*i+10,v)
        x=[0]*32;x[10]=key;x[11]=out;pc=0
        for _ in range(200):
            n=4 if code[pc]&3==3 else 2; op=code[pc:pc+n].hex();pc+=n
            if op=='b7370020':x[15]=0x20003000
            elif op=='03a787f8':need(x[15]-120==0x20002f88);x[14]=64
            elif op=='19e3':pc=14 if x[14] else pc
            elif op=='0146':x[12]=0
            elif op=='15a8':pc=64
            elif op=='1c47':x[15]=w(x[14]+8)
            elif op=='03d8a700':x[16]=h(x[15]+10)
            elif op=='636b0501':pc=42 if x[10]<x[16] else pc
            elif op=='83584700':x[17]=h(x[14]+4)
            elif op=='b3860801':x[13]=x[17]+x[16]
            elif op=='6355d500':pc=42 if x[13]<=x[10] else pc
            elif op=='8146':x[13]=0
            elif op=='63941601':pc=46 if x[13]!=x[17] else pc
            elif op=='1843':x[14]=w(x[14])
            elif op=='f1bf':pc=8 if pc==46 else 38
            elif op=='3e86':x[12]=x[15]
            elif op=='c107':x[15]+=16
            elif op=='03d3a7ff':x[6]=h(x[15]-6)
            elif op=='6317a300':pc=68 if x[6]!=x[10] else pc
            elif op=='99c1':pc=64 if not out else pc
            elif op=='23900501':pack_into('<H',m,x[11],x[16])
            elif op=='3285':x[10]=x[12]
            elif op=='8280':return x[10],h(1024)
            elif op=='8506':x[13]+=1
            elif op=='c206':x[13]=(x[13]<<16)&0xffffffff
            elif op=='c182':x[13]>>=16
            else:raise ValueError(op)
        raise ValueError('step limit')
    cases=0
    for seq in [(10,11,12,13),(10,13,11,12),(10,10,12,12),(10,11,19,13)]:
        for key in range(22):
            for out in (0,1024):
                addr,first=0,0
                for base,rows in [(256,(3,4)),(512,seq)]:
                    if rows[0]<=key<rows[0]+len(rows) and key in rows:
                        addr,first=base+16*rows.index(key),rows[0];break
                need(run(key,seq,out)==(addr,first if out else 0));cases+=1
    print('PASS:',cases,'two-node cases; row identity and optional first-handle output')

if __name__=='__main__':check(sys.argv[1])
