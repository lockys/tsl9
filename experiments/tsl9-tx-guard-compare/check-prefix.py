"""Compare the allowed TX prefix without executing the target."""
from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parents[2]
paths=(
 root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
 root/'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin',
)
def read(path):
    if path.stat().st_size!=76800: raise ValueError('unexpected image size')
    with path.open('rb') as stream:
        stream.seek(0x8a56-0x8000)
        data=stream.read(180)
    if len(data)!=180: raise ValueError('short prefix')
    return data
def mul(raw):
    w=int.from_bytes(raw,'little')
    if (w&127,(w>>12)&7,(w>>25)&127)!=(0x33,0,1):
        raise ValueError('not RV32 MUL')
    return ((w>>7)&31,(w>>15)&31,(w>>20)&31)
a,b=map(read,paths)
if any(a[i]!=b[i] for i in range(180) if not (40<=i<44 or 124<=i<128)):
    raise ValueError('unexpected prefix difference')
if a[40:44]!=bytes.fromhex('630cf700') or b[40:44]!=bytes.fromhex('638ca700'):
    raise ValueError('sentinel comparison changed')
if mul(a[124:128])!=(15,12,15) or mul(b[124:128])!=(15,15,12):
    raise ValueError('MUL operands changed')
subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('check.py'))],
               stdout=subprocess.DEVNULL,check=True)
print(json.dumps({'range':'[0x8a56,0x8b0a)','bytes_per_image':180,
 'changed_instruction_groups':2,'changed_bytes':sum(x!=y for x,y in zip(a,b)),
 'mul':'a5 = a2*a5 versus a5 = a5*a2','sentinel':'conditional fallthrough proof checked',
 'scope':'no alternate entry, exceptions, asynchronous interference or ABI proof',
 'excluded_app_read':False,'target_executed':False}))
