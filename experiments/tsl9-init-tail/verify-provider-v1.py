"""Read-only positive audit of the whole existing300B scheduler provider."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
N=runpy.run_path(str(HERE/'build-v1.py'))
S=N['S'];sha=N['sha'];need=N['need'];encoded=N['encoded']
K=json.loads((HERE/'provider-v1.json').read_bytes())
need(sha(ROOT/K['positive_checker'])==K['positive_checker_sha256'],'Frozen existing positive checker')
need(sha(ROOT/K['positive_spec'])==K['positive_spec_sha256'],'Frozen existing original-code specification')
P=runpy.run_path(str(ROOT/K['positive_checker']),run_name='readonly_scheduler_positive')
def native(mode):return ROOT/K['object_pattern'].format(mode=mode)
def inputs():
    paths=[Path(__file__),HERE/'provider-v1.json',HERE/'build-v1.py',HERE/'spec-v1.json',
        ROOT/K['positive_checker'],ROOT/K['positive_spec'],ROOT/K['source'],ROOT/K['curation'],
        ROOT/'src/source-manifest.json',ROOT/S['firmware'],ROOT/S['reader']]
    paths += [native(m)for m in('c','cpp')]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}
def portable(v):
    if isinstance(v,str):return v.replace(str(ROOT),'$'+'{PROJECT_ROOT}').replace(ROOT.as_posix(),'$'+'{PROJECT_ROOT}')
    if isinstance(v,list):return [portable(x)for x in v]
    if isinstance(v,dict):return {portable(k):portable(x)for k,x in v.items()}
    return v
def facts():
    need(sha(ROOT/K['source'])==K['source_sha256'],'Whole existing provider source unchanged')
    need(S['firmware_sha256']==P['S']['firmware_sha256']and S['reader_sha256']==P['S']['reader_sha256'],'Same original firmware andreader')
    need(sha(ROOT/S['firmware'])==S['firmware_sha256']and sha(ROOT/S['reader'])==S['reader_sha256'],'Pinned firmware andreader')
    before=portable(inputs());results={}
    for mode in('c','cpp'):
        e=N['elf'](native(mode));need(e.header[1]==243,'Actual RISC-V provider')
        row=P['audit_object'](native(mode))
        need(row['code_bytes']==300 and row['instructions']==115 and row['FUNC']==28 and row['RELA']==11 and row['UND']==[],'Complete real300B115i28-region provider')
        results[mode]=row
    need(before==portable(inputs()),'All provider inputs unchanged duringread')
    return dict(schema='TSL9-init-tail-real-provider-audit-v1',passed=True,inputs=before,modes=results,
        original_code_bytes=300,original_instructions=115,genuine_regions=28,typed_relocations=11,
        direct_undefined=0,source_rewritten=False,executable_stub_added=False,
        old_negative_matrices_executed=False,target_executed=False,HOST_model_executed=False,
        ISA_emulated=False,hardware_accessed=False,network=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path);a=p.parse_args()
    out=(a.replay or a.output).resolve();need(out.parent==HERE/'build','Owned report folder')
    report=facts()
    if a.replay:need(json.loads((out/'measurement.json').read_bytes())==report,'Exact currentwhole-provider read-only replay')
    else:
        need(not out.exists(),'Create-only provider report');out.mkdir(parents=True)
        (out/'measurement.json').write_bytes(encoded(report))
    print(json.dumps(dict(passed=True,languages=['c','cpp'],whole_provider_bytes=300,FUNC=28,RELA=11,UND=0,target_executed=False)))
if __name__=='__main__':main()
