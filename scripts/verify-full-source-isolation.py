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
          'src/native/receive/ota_epilogue_14098.inc','src/native/receive/ota_entry_14056.inc',
          'src/native/receive/ota_more_140a6.inc','src/native/receive/ota_ae_140dc.inc',
          'src/native/receive/ota_ad_1417a.inc','src/native/receive/ota_dispatch_141d6.inc','src/native/receive/ota_dispatch_14230.inc']
paths += ['src/native/tx_candidate/postpass/'+x for x in ('elf32.py','decode.py','schedule.py','policy.json')]
paths += ['scripts/build-compact-source-layout.py','scripts/verify-source-aggregate.py','scripts/source-build-support.py',
          'scripts/build-source-spans.py','scripts/build-v4160-source-candidate.py','scripts/source-ota-epilogue.py',
          'scripts/verify-conditional-tx-storage.py','scripts/verify-conditional-full-payload-link.py']
if len(paths)!=197 or len(set(paths))!=197:raise ValueError('Unexpected isolation inventory')
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
if (not f['passed'] or f['compiled_epilogue_bytes_replacing_carrier']!=14 or f['compiled_entry_bytes_replacing_carrier']!=66 or f['compiled_more_bytes_replacing_carrier']!=54 or f['compiled_ae_bytes_replacing_carrier']!=70 or f['compiled_ad_bytes_replacing_carrier']!=50 or f['compiled_dispatch_bytes_replacing_carrier']!=90 or f['compiled_dispatch2_bytes_replacing_carrier']!=88 or f['historical_candidate_read_during_build']
    or f['hardware_validated'] or f['flashable_proved'] or not f['conditional_link_verified']
    or not f['resident_rom_still_undefined_in_strict_link'] or len(f['outputs'])!=2):
    raise ValueError('Unexpected isolated build result')
checker=tree/'scripts/verify-conditional-full-payload-link.py'
original=checker.read_bytes()
marker=b'ROOT = Path(__file__).resolve().parent.parent'
if original.count(marker)!=1:raise ValueError('Unexpected conditional checker marker')
negative=out/'negative'
try:
    checker.write_bytes(original.replace(marker,b"raise SystemExit('synthetic conditional link failure')\n"+marker))
    rejected=subprocess.run([sys.executable,'-B',str(tree/'scripts/build-v4160-source-candidate.py'),
                             '--tool-dir',str(a.tool_dir),'--out',str(negative)],capture_output=True,text=True)
    if (rejected.returncode==0 or 'synthetic conditional link failure' not in rejected.stderr
        or any((negative/('NOT-FLASH-VALIDATED-v4160-source-'+mode+'.bin')).exists() for mode in ('c','cpp'))):
        raise ValueError('Conditional link failure did not stop candidate production')
finally:
    checker.write_bytes(original)
print(json.dumps({'passed':True,'copied_files':len(paths),'source_contains_opaque_original_bytes':True,
                  'historical_bin_present':False,'compiled_epilogue_bytes':14,'compiled_entry_bytes':66,'compiled_more_bytes':54,'compiled_ae_bytes':70,'compiled_ad_bytes':50,'compiled_dispatch_bytes':90,'compiled_dispatch2_bytes':88,'outputs':f['outputs'],
                  'conditional_link_verified':True,'conditional_failure_negative_control':True,
                  'resident_rom_still_undefined_in_strict_link':True,
                  'hardware_validated':False,'flashable_proved':False}))
