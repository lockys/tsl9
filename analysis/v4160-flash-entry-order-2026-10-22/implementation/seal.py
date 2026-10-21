"""Create-only selected metadata and exact-member seal; compiled archives stay local."""
import argparse,hashlib,json
from pathlib import Path
import check as C
H=Path(__file__).resolve().parent;MODEL=C.MODEL
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d):return (json.dumps(d,indent=2)+'\n').encode()
def create(p,data):
    if p.exists():C.need(p.read_bytes()==data,'immutable existing evidence '+str(p))
    else:p.write_bytes(data)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();N=C.load('entry_native_seal',H/'verify_native.py');B=C.load('entry_host_seal',root/MODEL/'verify_host.py');(H/'receipts').mkdir(exist_ok=True);rows=[]
    for kind,base,runner in [('host','host-final',B),('native','native-final-cli',N)]:
        for mode in ('c','cpp'):
            actual=root/MODEL/'build'/base/mode/'verification.json';runner.replay(root,actual);name='receipts/'+kind+'-'+mode+'.json';create(H/name,actual.read_bytes());r=C.read(actual);row=dict(kind=kind,mode=mode,receipt=str(actual),sha256=sha(actual),metadata=name,artifact_dir=actual.parent.relative_to(root).as_posix())
            if kind=='host':row.update(tests=r['tests'],actual_compiled_controls=6)
            else:row.update(functions=r['checks']['functions'],ELF_sha256=sha(actual.parent/'COMPONENT-ONLY-NOT-FIRMWARE.elf'),allocated_function_bytes=262,instructions=99,program_bytes=100)
            rows.append(row)
    variants=[]
    for variant,base,expected in [('early-a0','first-native-02d1103ae344423693659184e2600de4',94),('fresh-bases','first-native-2180e7c500ea4bc497a0f08050d39075',102),('final','first-native-cfb39014280b4f45b8902f9a57229932',100)]:
        for mode in ('c','cpp'):
            actual=root/MODEL/'build'/base/mode/'probe.json';r=C.read(actual);C.need(next(x for x in r['functions'] if x['name']=='program')['bytes']==expected,'measured bounded variant footprint')
            source=(root/MODEL/'src') if variant=='final' else H/'variants'/variant
            for n in ('flash_native.c','flash_native.h','native_io.h'):C.need(sha(source/n)==r['source'][n],'preserved actual diagnostic source')
            name='receipts/probe-'+variant+'-'+mode+'.json';create(H/name,actual.read_bytes());variants.append(dict(variant=variant,mode=mode,receipt=str(actual),sha256=sha(actual),metadata=name,program_bytes=expected))
    create(H/'source-diff.json',encoded(C.source_diff(root)))
    option_base=root/MODEL/'build/cli-options-final';option_path=option_base/'verification.json';option=C.read(option_path);C.need(option['passed'] and option['runner_sha256']==sha(H/'verify_native.py') and option['script_sha256']==sha(H/'test_cli_options.py'),'final CLI regression identities');N.replay(root,option_base/'native/c/verification.json',option_base/'same-ID2966-alternate-location.bin');create(H/'receipts/cli-options.json',option_path.read_bytes())
    option_meta=dict(receipt=str(option_path),sha256=sha(option_path),metadata='receipts/cli-options.json',artifact_dir=option_base.relative_to(root).as_posix())
    create(H/'results.json',encoded(dict(schema='ID2966-flash-entry-order-index-v1',results=rows,bounded_variants=variants,CLI_options=option_meta,program_original_bytes=100,program_native_bytes=100,total_native_bytes=262,instructions=99,padding_added=False,original_A0_memory_event_order=True,full_instruction_boundary_equivalence=False,full_scratch_GPR_prefix_equivalence=False,pointwise_async_equivalence=False,full_image_integration=False,firmware_BIN_produced=False,target_execution=False,hardware=False,OTA_ready=False)))
    files=[p for p in H.rglob('*') if p.is_file() and p.name!='seal.json' and p.suffix in ('.py','.sh','.md','.json','.c','.h')];models=[p for p in (root/MODEL).rglob('*') if p.is_file() and 'build' not in p.relative_to(root/MODEL).parts]
    def record(p,n):return dict(path=n,bytes=p.stat().st_size,sha256=sha(p))
    for p in files+models:C.need(b'\r' not in p.read_bytes(),'new evidence/model uses LF')
    seal=dict(schema='ID2966-flash-entry-order-implementation-seal-v1',passed=True,members=[record(p,p.relative_to(H).as_posix()) for p in sorted(files)],model_members=[record(p,p.relative_to(root).as_posix()) for p in sorted(models)],selected_receipts=4,source_extent_occupancy=True,program_native_bytes=100,padding_added=False,full_image_integration=False,pointwise_async_equivalence=False,target_execution=False,hardware=False,OTA_ready=False)
    create(H/'seal.json',encoded(seal));print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),index_sha256=sha(H/'results.json'),members=len(files),model_members=len(models))))
if __name__=='__main__':main()
