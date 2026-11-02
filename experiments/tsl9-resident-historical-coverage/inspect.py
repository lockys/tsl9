"""Summarize public Intel HEX from stdin; never print source data."""
import base64,hashlib,json,re,sys
encoded=re.sub(rb'\s+',b'',sys.stdin.buffer.read())
raw=base64.b64decode(encoded,validate=True)
upper=0;addresses={};eof=False;records=0
for line in raw.splitlines():
    if eof or not line.startswith(b':'):raise ValueError('Invalid record order')
    rec=bytes.fromhex(line[1:].decode('ascii'))
    if len(rec)<5 or len(rec)!=rec[0]+5 or sum(rec)&255:raise ValueError('Invalid record checksum or length')
    n,offset,kind=rec[0],int.from_bytes(rec[1:3],'big'),rec[3];payload=rec[4:4+n]
    if kind in (2,4):
        if n!=2:raise ValueError('Invalid address record')
        upper=int.from_bytes(payload,'big')<<(4 if kind==2 else 16)
    elif kind==0:
        if offset+n>65536:raise ValueError('Data record crosses address boundary')
        for i,b in enumerate(payload):
            address=upper+offset+i
            if address in addresses:raise ValueError('Overlapping HEX records')
            addresses[address]=b
    elif kind==1:
        if n!=0 or offset!=0:raise ValueError('Invalid EOF record')
        eof=True
    elif kind in (3,5):
        if n!=4 or offset!=0:raise ValueError('Invalid start address record')
    else:raise ValueError('Unsupported record')
    records+=1
if not eof:raise ValueError('Missing EOF')
needle=b'CH32V20x_BLE_LIB_V1.31'
hits=[]
for address,value in addresses.items():
    if value==needle[0] and all(addresses.get(address+i)==b for i,b in enumerate(needle)):
        hits.append(address)
known=sum(x in addresses for x in range(0x6eb2c,0x6eb30))
print(json.dumps({'sha256':hashlib.sha256(raw).hexdigest(),'records':records,'captured_bytes':len(addresses),'v131_markers':len(hits),'same_numeric_hole_bytes_present':known,'installed_rom_proved':False}))
