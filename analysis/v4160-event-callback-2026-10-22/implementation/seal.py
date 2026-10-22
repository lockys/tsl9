#!/usr/bin/env python3
"""Create-only selected source/metadata seal; generated archives are excluded."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;MODEL='experiments/tsl9-v4160-event-callback'
MEMBERS=['probe_native.py','verify_native.py','compare_inline.py','check.py','check.sh','seal.py','README.md','readme.zh-TW.md','readme.en.md','results.json','receipts/host-c.json','receipts/host-cpp.json','receipts/native-c.json','receipts/native-cpp.json','receipts/inline-comparison.json']
MODEL_MEMBERS=['.gitignore','verify.py','verify.sh','verify_host.py','README.md','readme.zh-TW.md','readme.en.md','src/callback.c','src/callback.h','src/io.h','src/host_io.c','tests/smoke.c']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();model=root/MODEL;scope=HERE.parent;reviews=[('source-review','c9edde476232c0c0e018c08e54d2d9d9a9afa20839d5e19a53f5ffa752e0e1c5'),('ABI-review','8f0956900f50a5b560ecd879eb5f1374884d8c20084503f96004f8df4cad60b7')]
    for name,pin in reviews:assert sha(scope/name/'seal.json')==pin
    for base,names in[(HERE,MEMBERS),(model,MODEL_MEMBERS)]:
        for n in names:data=(base/n).read_bytes();data.decode('utf-8');assert b'\r' not in data and data.endswith(b'\n') and not data.endswith(b'\n\n'),n
    result=dict(schema='TSL9-callback-shared-source-native-diagnostic-seal-v1',members={n:sha(HERE/n) for n in MEMBERS},model_members={n:sha(model/n) for n in MODEL_MEMBERS},independent_seals=[dict(case='v4160-event-callback-2026-10-22',scope=n,sha256=pin) for n,pin in reviews],native_bytes=658,original_bytes=632,native_fit=False,original_ABI_admitted=False,full_image_changed=False,BIN_exported=False,target_execution=False,hardware_OTA_proved=False)
    with(HERE/'seal.json').open('xb') as f:f.write((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps(dict(seal_sha256=sha(HERE/'seal.json'),implementation_members=len(MEMBERS),model_members=len(MODEL_MEMBERS))))
if __name__=='__main__':main()
