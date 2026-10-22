"""Create-only flat source/metadata seal, excluding generated build archives."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def main():
    p=H/'seal.json'
    if p.exists():raise ValueError('Never replace a closed object review')
    members={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(H.iterdir()) if x.is_file() and x.name!='seal.json'}
    for name in members:
        raw=(H/name).read_bytes();raw.decode('utf-8')
        if b'\r' in raw or not raw.endswith(b'\n') or raw.endswith(b'\n\n'):raise ValueError('UTF8LF/singleEOF '+name)
    with p.open('xb') as f:f.write((json.dumps(dict(schema='TSL9-independent-owned-reply-object-seal-v1',members=members),indent=2)+'\n').encode())
    print(hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':main()
