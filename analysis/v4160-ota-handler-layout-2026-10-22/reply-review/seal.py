"""Create-only source/metadata seal, excluding generated build artifacts."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def main():
    p=HERE/'seal.json'
    if p.exists():raise ValueError('Never replace a closed review seal')
    members={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(HERE.iterdir()) if x.is_file() and x.name!='seal.json'}
    for name in members:
        raw=(HERE/name).read_bytes()
        if name.endswith(('.py','.sh','.md','.json','.txt')):
            raw.decode('utf-8');assert b'\r' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'),name
    with p.open('xb') as f:f.write((json.dumps(dict(schema='TSL9-reply-consumer-static-seal-v1',members=members),indent=2)+'\n').encode())
    print(hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':main()
