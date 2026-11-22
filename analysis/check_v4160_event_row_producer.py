"""APP-only 9b4e -> 9124 delayed producer. No resident call is executed."""
from pathlib import Path
from hashlib import sha256
from struct import unpack_from

APP = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')

def verify(b):
    def raw(pc,s):
        s=bytes.fromhex(s)
        if b[pc-0x8000:pc-0x8000+len(s)]!=s: raise ValueError(hex(pc))
    def pair(pc,rd):
        u,v=unpack_from('<II',b,pc-0x8000)
        if u&4095!=rd*128+23 or v&0xfffff!=(rd<<15)|(rd<<7)|19: raise ValueError(hex(pc))
        return (pc+(u&0xfffff000)+(v>>20)-((v>>31)<<12))&0xffffffff
    raw(0x9b4e,'2384010a 93874105 9c43 4111 06c6 83c73700 c18b 81cf 0566 8146 13068638 8145'); raw(0x9b76,'eff0efda')
    if pair(0x9b6e,10)!=0x9ad2 or pair(0x9132,18)!=0x2000be08 or pair(0x9188,15)!=0x2000be08: raise ValueError('address')
    raw(0x913a,'39e6'); raw(0x9190,'368a b289 2e84 3e87 8144 bd46 5043 6310a606'); raw(0x91a2,'b147 b387f402 ca97 8847 09c5 b7070400 bc57 8297');raw(0x91c6,'ca97 23808700 23a44701');raw(0x91d0,'9307803e 3386f902 c205 93071027 c181 3356f602 b7070400 31c0');raw(0x91fe,'8504 3107 e39dd4f8 0147 bd46 d043 05ee b147 b307f702 8545 b395e500 ca97 c8c3 23808700 23a44701 03c5610a 5db7 bc4f 8297 13351500');raw(0x9244,'0507 b107 e311d7fc 0545 ddb7')

def select(rows):
    for i,v in enumerate(rows):
        if v==0x9ad2: return ('reuse',i)
    for i,v in enumerate(rows):
        if not v: return ('new',i)
    return ('full',None)

if __name__=='__main__':
    b=APP.read_bytes()
    if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('identity')
    verify(b)
    for p in (0x9b60,0x9b68,0x9b72,0x9b76,0x919e,0x91c8,0x921c,0x9222,0x922c,0x924c):
        x=bytearray(b); x[p-0x8000]^=1
        try: verify(x)
        except ValueError: continue
        raise ValueError(hex(p))
    for i in range(15):
        r=[0]*15; r[i]=0x9ad2
        if select(r)!=('reuse',i): raise ValueError('match after holes')
        r=[1]*15; r[i]=0
        if select(r)!=('new',i): raise ValueError('free row')
    if select([1]*15)!=('full',None) or select([0,0x9ad2,0x9ad2]+[1]*12)!=('reuse',1): raise ValueError('priority')
    print('PASS: init caller 9b76; callback 9ad2; 32 bounded table selections; 10 byte mutations rejected')
