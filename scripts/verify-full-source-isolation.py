#!/usr/bin/env python3
"""Rebuild the full candidate from a bounded source-only copy."""
import argparse,json,runpy,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
a=p.parse_args();out=a.out.resolve()
if out.exists() or out==ROOT or ROOT in out.parents:raise SystemExit('Output must be a new directory outside the project')
support=runpy.run_path(str(ROOT/'scripts/source-build-support.py'))
manifest=support['metadata']()
paths=[x['destination'] for x in manifest['files']]
paths += ['src/source-build-manifest.json','src/compact-layout.json','src/native/tx_candidate/verify-linked.py',
          'src/native/tx_candidate/verify.py','src/native/tx_candidate/full-image-payload.json',
          'src/native/receive/ota_epilogue_14098.inc','src/native/receive/ota_entry_14056.inc']
paths += ['src/native/tx_candidate/postpass/'+x for x in ('elf32.py','decode.py','schedule.py','policy.json')]
paths += ['scripts/build-compact-source-layout.py','scripts/verify-source-aggregate.py','scripts/source-build-support.py',
          'scripts/build-source-spans.py','scripts/build-v4160-source-candidate.py','scripts/source-ota-epilogue.py']
if len(paths)!=190 or len(set(paths))!=190:raise ValueError('Unexpected isolation inventory')
tree=out/'source-only'
for name in paths:
    source,dest=(ROOT/name).resolve(),(tree/name).resolve()
    if not source.is_relative_to(ROOT) or not dest.is_relative_to(tree) or not source.is_file():
        raise ValueError('Rejected source path')
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
if any((tree/name).exists() for name in ('experiments','analysis','artifacts','firmware-downloads')):
    raise ValueError('Unexpected isolated input')
proc=subprocess.run([sys.executable,'-B',str(tree/'scripts/build-v4160-source-candidate.py'),
                     '--tool-dir',str(a.tool_dir),'--out',str(out/'build')],capture_output=True,text=True)
if proc.returncode:raise ValueError('Isolated candidate build failed: '+proc.stderr[:1000])
f=json.loads(proc.stdout)
if (not f['passed'] or f['compiled_epilogue_bytes_replacing_carrier']!=14 or f['compiled_entry_bytes_replacing_carrier']!=56 or f['historical_candidate_read_during_build']
    or f['hardware_validated'] or f['flashable_proved'] or len(f['outputs'])!=2):
    raise ValueError('Unexpected isolated build result')
print(json.dumps({'passed':True,'copied_files':len(paths),'source_contains_opaque_original_bytes':True,
                  'historical_bin_present':False,'compiled_epilogue_bytes':14,'compiled_entry_bytes':56,'outputs':f['outputs'],
                  'hardware_validated':False,'flashable_proved':False}))
