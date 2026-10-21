"""Read-only exact replay; initial sealing writes only seal.json in this review."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEMBERS=['review.py','replay.py','context-check.py','context-check.json','tool-pins.json','review-c.json','review-cpp.json','README.md','readme.zh-TW.md','readme.en.md']
FORMAL={'c':'d3053edec5a507acbcf9d7408a435ba206ea43371c60f9b99260e5cbb2f0b069','cpp':'1439440dfad59aedd4b8c4834b86133cbcc39381ebdc9cfd387fa34e98f35318'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--context-json',type=Path);args=ap.parse_args()
    context=json.loads(args.context_json.read_bytes()) if args.context_json else {}
    root=Path(context.get('project_root',ROOT)).resolve()
    def local(value):
        p=Path(value);return p.resolve() if p.is_absolute() else (root/p).resolve()
    kwargs={k:local(context[k]) for k in ('parser_path','source_dir','firmware_path') if k in context}
    kwargs['project_root']=root
    if 'observed_tools' in context:kwargs['observed_tools']=context['observed_tools']
    review=runpy.run_path(str(HERE/'review.py'))['review'];reports=[];formal=[]
    for mode in ('c','cpp'):
        path=HERE/('review-'+mode+'.json');saved=json.loads(path.read_bytes())
        folder=local(context.get('build_roots',{}).get(mode,saved['build_root']))
        linked=local(context.get('linked_elfs',{}).get(mode,saved['component_link']['path']))
        result=review(folder,linked,**kwargs)
        # Only recorded location labels normalize; actual objects, source, tools, IR and code gates do not.
        result['build_root']=saved['build_root'];result['component_link']['path']=saved['component_link']['path']
        assert (json.dumps(result,indent=2)+'\n').encode('utf-8')==path.read_bytes()
        receipt=folder/'verification.json';raw=receipt.read_bytes();assert hashlib.sha256(raw).hexdigest()==FORMAL[mode]
        producer=json.loads(raw);assert producer['passed'] and producer['checks']['independent_normal_contract']==saved
        assert producer['runner_sha256']=='dc0c966f057a0562f0d51a0289b9b24ce242d47bee0cd397d72fc12bc0a42013'
        assert all(producer['source_sha256'][n]==h for n,h in saved['source_pins'].items())
        formal.append(dict(mode=mode,path=saved['build_root']+'/verification.json',sha256=FORMAL[mode],actual_independent_result_equals_formal_embedded_result=True))
        reports.append(dict(mode=mode,functions=len(result['functions']),all_fit=result['all_six_fit'],full_image=False))
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    members=[]
    for n in MEMBERS:
        raw=(HERE/n).read_bytes();assert b'\r' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n')
        members.append(dict(path=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    seal=dict(schema='ID2966-flash-independent-native-review-seal-v1',passed=True,members=members,replayed=reports,formal_native_receipts=formal,writers_stopped=True,target_execution=False,emulation=False,network=False,hardware=False,new_BIN=False,full_image_integration=False,pointwise_equivalence=False,OTA_ready=False)
    payload=(json.dumps(seal,indent=2)+'\n').encode('utf-8')
    if args.check:assert (HERE/'seal.json').read_bytes()==payload
    else:(HERE/'seal.json').write_bytes(payload)
    print(json.dumps(dict(passed=True,replayed=reports,seal_sha256=hashlib.sha256(payload).hexdigest(),readonly=args.check)))


if __name__=='__main__':main()
