"""Create-only source/metadata seal; generated build artifacts excluded."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def main():
    p=H/'seal.json'
    if p.exists():raise ValueError('Never replace a closed frame review')
    members={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(H.iterdir()) if f.is_file() and f.name!='seal.json'}
    for name in members:
        raw=(H/name).read_bytes();raw.decode('utf-8')
        if b'\r' in raw or not raw.endswith(b'\n') or raw.endswith(b'\n\n'):raise ValueError('UTF8 LF/singleEOF '+name)
    with p.open('xb') as f:f.write((json.dumps(dict(schema='TSL9-independent-reply-frame-seal-v1',members=members),indent=2)+'\n').encode())
    print(hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':main()
