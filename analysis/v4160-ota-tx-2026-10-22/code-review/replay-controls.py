#!/usr/bin/env python3
"""Read-only, in-memory receipt counterexamples; no archived file is modified."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def load():
    spec=importlib.util.spec_from_file_location('TX_receipt_controls',HERE/'run-effects.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def inspect(root,receipt):
    receipt=receipt.resolve();m=load();baseline=m.replay(root,receipt);original_read=m.read;record=original_read(receipt)
    changes=[
        ('positive_compile_argument',lambda r:r['commands'][0]['argv'].__setitem__(-1,'unexpected-compile-input')),
        ('positive_compile_exit',lambda r:r['commands'][0].__setitem__('exit',1)),
        ('positive_launch_guard_missing',lambda r:r['commands'][1].__setitem__('host_executable_guard',None)),
        ('positive_checks_counter',lambda r:r['tests'].__setitem__('checks',78284)),
        ('negative_recipe_source',lambda r:r['actual_compiled_semantic_controls'][0].__setitem__('old','not-the-source-anchor')),
        ('negative_compile_argument',lambda r:r['actual_compiled_semantic_controls'][0]['commands'][0]['argv'].__setitem__(-1,'unexpected-negative-source')),
        ('negative_launch_exit',lambda r:r['actual_compiled_semantic_controls'][0]['commands'][1].__setitem__('exit',0)),
        ('negative_launch_guard_missing',lambda r:r['actual_compiled_semantic_controls'][0]['commands'][1].__setitem__('host_executable_guard',None)),
        ('negative_mutant_source_digest',lambda r:r['actual_compiled_semantic_controls'][0].__setitem__('mutant_sha256','0'*64)),
    ]
    results=[]
    for name,change in changes:
        altered=copy.deepcopy(record);change(altered)
        m.read=lambda path,altered=altered:altered if Path(path).resolve()==receipt else original_read(path)
        try:m.replay(root,receipt)
        except ValueError as error:results.append({'case':name,'rejected':True,'reason':str(error)})
        else:raise ValueError('Accepted in-memory receipt control '+name)
        finally:m.read=original_read
    # Simulate a second copied source change plus a forged matching artifact pin.
    # Files stay untouched; only this process's read view is temporarily replaced.
    victim=receipt.parent/'controls/length1039_rejected/src/host_io.h'
    original_bytes=Path.read_bytes;forged=original_bytes(victim)+b'\n'
    altered=copy.deepcopy(record);relative=victim.relative_to(receipt.parent).as_posix()
    altered['artifacts'][relative]={'bytes':len(forged),'sha256':hashlib.sha256(forged).hexdigest()}
    original_stat=Path.stat
    class ForgedStat:
        st_size=len(forged)
    m.read=lambda path:altered if Path(path).resolve()==receipt else original_read(path)
    Path.read_bytes=lambda path:forged if path.resolve()==victim else original_bytes(path)
    Path.stat=lambda path,*args,**kwargs:ForgedStat() if str(path)==str(victim) and not args and not kwargs else original_stat(path,*args,**kwargs)
    try:m.replay(root,receipt)
    except ValueError as error:
        if 'Exact single-change source' not in str(error):raise
        results.append({'case':'second_copied_source_with_forged_artifact_pin','rejected':True,'reason':str(error)})
    else:raise ValueError('Accepted second copied source with forged matching pin')
    finally:m.read=original_read;Path.read_bytes=original_bytes;Path.stat=original_stat
    return {'passed':True,'mode':baseline['mode'],'receipt_sha256':baseline['receipt_sha256'],'actual_receipt_replayed':True,'in_memory_receipt_controls_rejected':len(results),'controls':results,'archives_modified':False,'target_execution':False}
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();print(json.dumps(inspect(a.project_root.resolve(),a.receipt)))
if __name__=='__main__':main()
