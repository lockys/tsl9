"""Final frozen CLI binding; independently recheck current native artifacts without sealed rewrites."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=BASE.parents[2]
SHA=lambda b:hashlib.sha256(b).hexdigest()
MEMBERS=['replay.py','report.json','README.md','readme.zh-TW.md','readme.en.md']
FORMAL={'c':'94df38a3a6447fc5a7cc5e23081dd4dff3fbc144dc865e7d922758185e6c2d9e','cpp':'feb63cb495a3405851d9534bee63244b6668cabd332430e4f2e3ebd19128a66d'}
RUNNER='0f96c209bb486581056ea3b68fbe4581dfeb4ff48fc03cba9a07e2e80dd7fa89'


def immutable(directory,digest):
    raw=(directory/'seal.json').read_bytes();assert SHA(raw)==digest
    for row in json.loads(raw)['members']:assert SHA((directory/row['path']).read_bytes())==row['sha256']


def inspect(cfg):
    root=Path(cfg.get('project_root',ROOT)).resolve()
    def local(value):
        q=Path(value);return q.resolve() if q.is_absolute() else (root/q).resolve()
    immutable(BASE,'73d1375e87cda816939e22a5612431462e16a7f0f005744c8771b442b371eb0c')
    immutable(BASE/'final-binding','02dbc879f6de783899c4a20c6fcc97f58cf95101246d1fbf3ec7854e0bd7c8bb')
    api=runpy.run_path(str(BASE/'audit.py'))
    prior=local(cfg.get('prior_build','experiments/tsl9-v4160-flash-native/build/native-93a4dce3d2154291a48dea3a519f4b3f'))
    firmware=local(cfg.get('firmware','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'))
    source=local(cfg.get('source_dir','experiments/tsl9-v4160-flash-entry-order/src'));parser=local(cfg['parser']) if 'parser' in cfg else None
    records=[]
    for mode in ('c','cpp'):
        default='experiments/tsl9-v4160-flash-entry-order/build/native-final-cli/'+mode
        folder=local(cfg.get('build_roots',{}).get(mode,default));baseline=json.loads((BASE/('review-'+mode+'.json')).read_bytes())
        fresh=api['inspect'](root,folder,prior,firmware,source,parser,False)
        canonical=json.loads(json.dumps(fresh));canonical['build_root']=baseline['build_root'];canonical['linked_component']['path']=baseline['linked_component']['path'];assert canonical==baseline
        raw=(folder/'verification.json').read_bytes();assert SHA(raw)==FORMAL[mode];receipt=json.loads(raw);assert receipt['passed'] and receipt['runner_sha256']==RUNNER
        program=next(v for v in fresh['functions'] if v['name']=='program')
        assert receipt['checks']['program_contract']==program['proof'] and receipt['checks']['IR']['program']==program['IR']
        assert fresh['linked_component']['sha256']=='aeccc19da9c5764a386333dd26898429c35bf0ff40efb08c8f8417b11820339d'
        records.append(dict(mode=mode,logical_build_root=default,formal_receipt_sha256=FORMAL[mode],baseline_report_sha256=SHA((BASE/('review-'+mode+'.json')).read_bytes()),actual_current_inputs_equal_immutable_ABI_after_location_normalization=True,source_pins=fresh['source_pins'],component_ELF_sha256=fresh['linked_component']['sha256'],functions=[{k:v[k] for k in ('name','address','bytes','limit','fits','object_sha256','IR_sha256')} for v in fresh['functions']],program_bytes=100,program_instructions=38,raw_machine_negatives=12,IR_transcript_negatives=3,known5_interior_roles=True))
    return dict(schema='final-frozen-CLI-independent-ABI-binding-v2',passed=True,base_ABI_seal_sha256='73d1375e87cda816939e22a5612431462e16a7f0f005744c8771b442b371eb0c',previous_binding_seal_sha256='02dbc879f6de783899c4a20c6fcc97f58cf95101246d1fbf3ec7854e0bd7c8bb',formal_runner_sha256=RUNNER,modes=records,normal_contracts=True,full_role_identity=False,full_GPR_prefix_equivalence=False,physical_fault_prefix_equivalence=False,pointwise_async_equivalence=False,full_image_integration=False,target_execution=False,emulation=False,network=False,hardware=False,new_BIN=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--context-json',type=Path);args=p.parse_args();cfg=json.loads(args.context_json.read_bytes()) if args.context_json else {}
    result=inspect(cfg);report=(json.dumps(result,indent=2)+'\n').encode('utf-8')
    if args.check:assert (HERE/'report.json').read_bytes()==report
    else:(HERE/'report.json').write_bytes(report)
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    members=[]
    for name in MEMBERS:
        raw=(HERE/name).read_bytes();assert raw.endswith(b'\n') and not raw.endswith(b'\n\n') and b'\r' not in raw
        members.append(dict(path=name,bytes=len(raw),sha256=SHA(raw)))
    seal=dict(schema='final-frozen-CLI-independent-ABI-binding-v2-seal',passed=True,members=members,base_ABI_seal_sha256=result['base_ABI_seal_sha256'],previous_binding_seal_sha256=result['previous_binding_seal_sha256'],writers_stopped=True,normal_contracts=True,full_role_identity=False,pointwise_async_equivalence=False,full_image_integration=False,target_execution=False,emulation=False,network=False,hardware=False,new_BIN=False)
    payload=(json.dumps(seal,indent=2)+'\n').encode('utf-8')
    if args.check:assert (HERE/'seal.json').read_bytes()==payload
    else:(HERE/'seal.json').write_bytes(payload)
    print(json.dumps(dict(passed=True,current_binding='v2',modes=2,program_bytes=100,program_instructions=38,full_role_identity=False,seal_sha256=SHA(payload),readonly=args.check)))


if __name__=='__main__':main()
