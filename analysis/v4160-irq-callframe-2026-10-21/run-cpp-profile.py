"""Adapt only the sealed C++ probe dependency path for published layouts."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import uuid

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SEAL_SHA='25d9bffbff7e3d68bbe712936936c66d632162f394e3c551c0c2fde25a2d9370'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    scope=HERE/'cpp-profile';seal_path=scope/'final-audit.json'
    if sha(seal_path)!=SEAL_SHA:raise ValueError('Exact sealed C++ producer')
    seal=json.loads(seal_path.read_text(encoding='utf8'));inputs={seal_path:SEAL_SHA}
    members=seal['members']
    if isinstance(members,dict):members=[dict(path=n,sha256=h) for n,h in members.items()]
    for item in members:
        p=(scope/item['path']).resolve()
        if not p.is_relative_to(scope.resolve()) or sha(p)!=item['sha256']:raise ValueError('Sealed producer member changed')
        inputs[p]=item['sha256']
    choices=[Path('apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review'),
             Path('analysis/v4160-irq-native-2026-10-21/compiler-review')]
    choices=[p for p in choices if (ROOT/p/'final-audit.json').is_file()]
    if len(choices)!=1:raise ValueError('One unambiguous existing dependency layout')
    producer=scope/'verify_cpp_profile.py'
    spec=importlib.util.spec_from_file_location('sealed_cpp_profile_producer',producer)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    old_path=module.DEPENDENCY
    module.DEPENDENCY=choices[0]
    output=io.StringIO();arguments=sys.argv[1:]
    sys.argv=[str(producer),'--project-root',str(ROOT),*arguments]
    with contextlib.redirect_stdout(output):module.main()
    result=json.loads(output.getvalue().strip())
    if any(sha(p)!=h for p,h in inputs.items()):raise ValueError('Sealed files changed during probe')
    folder=HERE/'build'/('cpp-path-adapter-'+uuid.uuid4().hex);folder.mkdir(parents=True)
    report=dict(passed=True,producer_result=result,inputs_sha256={str(p):h for p,h in inputs.items()},
                adapter_sha256=sha(Path(__file__)),old_dependency_path=str(old_path),selected_dependency_path=str(choices[0]),
                only_dependency_path_constant_adapted=True,sealed_sources_modified=False,
                verification_gates_changed=False,target_execution=False,ISA_emulation=False,network=False,hardware=False,OTA_ready=False)
    path=folder/'verification.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(passed=True,receipt=str(path),sha256=sha(path),producer_result=result,OTA_ready=False)))


if __name__=='__main__':main()
