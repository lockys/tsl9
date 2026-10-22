#!/usr/bin/env python3
"""Create-only seal for selected source/docs/metadata; no build archive publication."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;MODEL='experiments/tsl9-v4160-tx-image-integration'
MEMBERS=['prototype.py','tx_order.py','prepare_manifest.py','verify_image.py','check.py','check.sh','seal.py','README.md','readme.zh-TW.md','readme.en.md','results.json','receipts/native-c.json','receipts/native-cpp.json']
MODEL_MEMBERS=['.gitignore','verify.py','verify.sh','README.md','readme.zh-TW.md','readme.en.md','adapter/entry.S','source-manifest.json','original-image-layout.ld']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--source-seal',required=True);p.add_argument('--ABI-seal',required=True);a=p.parse_args();root=a.project_root.resolve();model=root/MODEL
    for base,names in [(H,MEMBERS),(model,MODEL_MEMBERS)]:
        for n in names:
            data=(base/n).read_bytes();data.decode('utf-8')
            if n=='original-image-layout.ld':assert sha(base/n)=='651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b';continue
            assert b'\r' not in data and data.endswith(b'\n') and not data.endswith(b'\n\n'),n
    result=dict(schema='TSL9-TX-full-image-source-implementation-seal-v1',members={n:sha(H/n) for n in MEMBERS},model_members={n:sha(model/n) for n in MODEL_MEMBERS},independent_seals=[dict(case='v4160-tx-image-integration-2026-10-22',scope='source-review',sha256=a.source_seal),dict(case='v4160-tx-image-integration-2026-10-22',scope='ABI-review',sha256=a.ABI_seal)],historical_layout_byteidentity_exception='original-image-layout.ld retains exact historical bytes, including CRLF',whole_original_ABI_admitted=False,hardware_OTA_proved=False,target_execution=False)
    with(H/'seal.json').open('xb') as f:f.write((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps(dict(seal_sha256=sha(H/'seal.json'),members=len(MEMBERS),model_members=len(MODEL_MEMBERS))))
if __name__=='__main__':main()
