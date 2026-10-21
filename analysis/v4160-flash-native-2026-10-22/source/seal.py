"""Seal this review only; --check reads without writing."""
from pathlib import Path
import hashlib, json, subprocess, sys

HERE=Path(__file__).resolve().parent
MEMBERS=['inspect.py','r2-source.json','source-proof.json','contracts.json','README.md','readme.zh-TW.md','readme.en.md','seal.py']


def main():
    subprocess.run([sys.executable,'-B',str(HERE/'inspect.py'),'--check'],check=True)
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    rows=[]
    for name in MEMBERS:
        b=(HERE/name).read_bytes()
        assert b.endswith(b'\n') and not b.endswith(b'\n\n') and b'\r' not in b
        if name.endswith('.json'): json.loads(b)
        rows.append(dict(path=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
    report=dict(schema='ID2966-flash-native-source-seal-v1',passed=True,members=rows,writers_stopped=True,target_execution=False,emulation=False,network=False,hardware=False,new_BIN=False,IRQ_equivalence=False,OTA_ready=False)
    payload=(json.dumps(report,indent=2)+'\n').encode('utf-8');target=HERE/'seal.json'
    if '--check' in sys.argv: assert target.read_bytes()==payload
    else: target.write_bytes(payload)
    print(json.dumps(dict(passed=True,members=len(rows),seal_sha256=hashlib.sha256(payload).hexdigest(),readonly='--check' in sys.argv)))


if __name__=='__main__': main()
