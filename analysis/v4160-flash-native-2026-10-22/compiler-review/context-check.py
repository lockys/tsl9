"""Check explicit path/tool context changes no semantic admission; no compiling or execution."""
from pathlib import Path
import argparse,copy,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]


def inspect(build_root):
    api=runpy.run_path(str(HERE/'review.py'));pins=json.loads((HERE/'tool-pins.json').read_bytes())['tools'];modes=[]
    parser=ROOT/'apk-analysis/tsl9-v4160-reset-memory-2026-10-21/compiler-review/elf32.py'
    for mode in ('c','cpp'):
        folder=build_root/mode;producer=json.loads((folder/'probe.json').read_bytes())
        toolpaths=[producer['functions'][0]['commands'][0]['argv'][0],producer['link_commands'][0]['argv'][0]]
        observed={p:dict(before_sha256=pins[Path(p).name]['sha256'],after_sha256=pins[Path(p).name]['sha256']) for p in toolpaths}
        kwargs=dict(project_root=ROOT,parser_path=parser,observed_tools=observed,source_dir=ROOT/'experiments/tsl9-v4160-flash-native/src',firmware_path=ROOT/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
        linked=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
        baseline=api['review'](folder,linked);explicit=api['review'](folder,linked,**kwargs)
        assert baseline==explicit
        negatives=[]
        bad=copy.deepcopy(kwargs);bad['observed_tools'][toolpaths[0]]['after_sha256']='0'*64
        trials=[('tool-byte-drift',bad),('wrong-parser-bytes',dict(kwargs,parser_path=HERE/'review.py')),('wrong-firmware-bytes',dict(kwargs,firmware_path=HERE/'tool-pins.json'))]
        for label,context in trials:
            try:api['review'](folder,linked,**context)
            except ValueError as ex:negatives.append(dict(name=label,rejected=True,reason=str(ex)))
            else:raise ValueError('context bypass '+label)
        modes.append(dict(mode=mode,default_equals_explicit=True,all_six_normal_boundaries=True,all_six_fit=True,context_negatives=negatives))
    return dict(schema='native-review-explicit-context-check-v1',passed=True,build_root=build_root.relative_to(ROOT).as_posix(),modes=modes,semantic_gates_unchanged=True,target_execution=False,emulation=False,network=False,new_BIN=False)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--build-root',type=Path,required=True);ap.add_argument('--check',action='store_true');a=ap.parse_args();result=inspect(a.build_root.resolve());payload=(json.dumps(result,indent=2)+'\n').encode('utf-8');path=HERE/'context-check.json'
    if a.check:assert path.read_bytes()==payload
    else:path.write_bytes(payload)
    print(json.dumps(dict(passed=True,modes=2,default_equals_explicit=True,context_negatives=6)))
