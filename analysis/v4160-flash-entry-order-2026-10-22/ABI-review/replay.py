"""Read-only static replay with explicit package-path mapping; no compilation or ISA execution."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEMBERS=['program.py','audit.py','replay.py','original-roles.json','variants.json','review-c.json','review-cpp.json','README.md','readme.zh-TW.md','readme.en.md']
FORMAL={'c':'61438bcfa7bc61fc0b328024367eaa3c0b67565fa3b3d66f9440c3321a977cc1','cpp':'d7297cbd8f1fd8ba1f8159d927a7eb5ffd1d8adad150a97392a1bac9aeef5b81'}
SHA=lambda b:hashlib.sha256(b).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--context-json',type=Path);args=p.parse_args();cfg=json.loads(args.context_json.read_bytes()) if args.context_json else {};root=Path(cfg.get('project_root',ROOT)).resolve()
    def local(value):
        q=Path(value);return q.resolve() if q.is_absolute() else (root/q).resolve()
    prior=local(cfg.get('prior_build','experiments/tsl9-v4160-flash-native/build/native-93a4dce3d2154291a48dea3a519f4b3f'))
    fw=local(cfg.get('firmware','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'))
    source=local(cfg.get('source_dir','experiments/tsl9-v4160-flash-entry-order/src'));parser=local(cfg['parser']) if 'parser' in cfg else None
    api=runpy.run_path(str(HERE/'audit.py'));_,old,new,decode,ELF=api['context'](root,parser);formal=[]
    for mode in ('c','cpp'):
        path=HERE/('review-'+mode+'.json');saved=json.loads(path.read_bytes());folder=local(cfg.get('build_roots',{}).get(mode,saved['build_root']))
        result=api['inspect'](root,folder,prior,fw,source,parser,False)
        result['build_root']=saved['build_root'];result['linked_component']['path']=saved['linked_component']['path']
        assert (json.dumps(result,indent=2)+'\n').encode('utf-8')==path.read_bytes()
        receipt=(folder/'verification.json').read_bytes();assert SHA(receipt)==FORMAL[mode];r=json.loads(receipt)
        assert r['passed'] and r['runner_sha256']=='ef514efb1155f73f0a61bbf843527eb789b1afc0f49855bc4aba651134dfc744'
        program=next(v for v in saved['functions'] if v['name']=='program')
        assert r['checks']['program_contract']==program['proof'] and r['checks']['IR']['program']==program['IR']
        formal.append(dict(mode=mode,path=saved['build_root']+'/verification.json',sha256=FORMAL[mode],actual_independent_program_result_equals_formal_result=True))
    # Diagnostics are immutable retained observations. Recheck their actual bytes when retained locally.
    for v in json.loads((HERE/'variants.json').read_bytes())['variants']:
        folder=local(cfg.get('variant_build_roots',{}).get(v['label']+'/'+v['mode'],v['build_root']))
        if (folder/'program.o').is_file():
            assert SHA((folder/'program.o').read_bytes())==v['object_sha256']
            assert SHA((folder/'program.ll').read_bytes())==v['IR_sha256']
            body=api['program_bytes'](ELF,folder);decoded=new['rows'](body,decode)
            assert decoded==v['rows'] and new['event_projection'](decoded)==v['events']
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    members=[]
    for name in MEMBERS:
        raw=(HERE/name).read_bytes();assert raw.endswith(b'\n') and not raw.endswith(b'\n\n') and b'\r' not in raw
        members.append(dict(path=name,bytes=len(raw),sha256=SHA(raw)))
    seal=dict(schema='ID2966-flash-entry-order-independent-ABI-seal-v1',passed=True,members=members,formal_native_receipts=formal,writers_stopped=True,normal_contracts=True,program_bytes=100,program_instructions=38,known5_interior_roles=True,full_original_role_identity=False,full_GPR_prefix_equivalence=False,physical_fault_prefix_equivalence=False,pointwise_async_equivalence=False,full_image_integration=False,target_execution=False,emulation=False,network=False,hardware=False,new_BIN=False)
    payload=(json.dumps(seal,indent=2)+'\n').encode('utf-8')
    if args.check:assert (HERE/'seal.json').read_bytes()==payload
    else:(HERE/'seal.json').write_bytes(payload)
    print(json.dumps(dict(passed=True,modes=2,program_bytes=100,program_instructions=38,full_role_identity=False,seal_sha256=SHA(payload),readonly=args.check)))


if __name__=='__main__':main()
