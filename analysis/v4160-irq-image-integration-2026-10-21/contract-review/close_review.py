"""Replay independent artifacts and source provenance; write only first receipt."""
from pathlib import Path
import hashlib,importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def run():
    A=module('independent_contract',H/'review.py');P=module('independent_provenance',H/'provenance.py')
    evidence=[('final-c.json','e1cdcfe3403d6aa26f93037f23849fb4996e8b6f7204c1e3c94a649a4939ea87'),('final-cpp.json','64d30445d23291eea88bf30480a7e5af3659dcdd940f2bab5af246e8e2cf34af')]
    p,b,bl,selected,alloc=A.baseline();rows=[]
    for filename,pin in evidence:
        path=H/filename;need(sha(path)==pin,'selected final independent receipt pin');v=read(path)
        for f in v['inputs']:need(sha(Path(f['path']))==f['sha256'],'every baseline/final actual input pin')
        inp=v['inputs'][-3:];obj=A.E.ELF(Path(inp[0]['path']));linked=A.E.ELF(Path(inp[1]['path']));image=Path(inp[2]['path']).read_bytes()
        mg=A.compare_merged(obj,b,selected,alloc,p);lg=A.compare_linked(linked,bl,selected,alloc,p,image);neg=A.negative_controls(obj,linked,image,b,bl,selected,alloc,p)
        need(canon(mg)==canon(v['merged']) and canon(lg)==canon(v['linked']) and canon(neg)==canon(v['actual_raw_negative_controls']),'fresh independent exact artifact/control replay')
        rows.append(dict(mode=v['label'],receipt=filename,sha256=pin,allocations=691,retained_sections=686,RELA=8276,outside_RELA=8270,raw_controls_rejected=17,image_sha256=inp[2]['sha256']))
    need(rows[0]['image_sha256']==rows[1]['image_sha256']=='47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c','actual C/CPP source images identical')
    provenance=P.run();need(provenance==read(H/'source-provenance.json') and sha(H/'source-provenance.json')=='7261f46375a8b4db30a7ae5824698fb79cf0b80b9f328763a7a138696769ed26','fresh independent actual source/command/dependency closure')
    wrapper=R/'experiments/tsl9-v4160-irq-image-integration/verify.py';need(sha(wrapper)=='2231fc18a8356d6d545f074d6bb4336e4fcac05c601324dfef5d75ad241f36c0','portable wrapper frozen')
    need((H/'README.md').read_bytes()==(H/'readme.zh-TW.md').read_bytes(),'README contains full Traditional Chinese copy')
    if (H/'seal.json').exists():
        for member in read(H/'seal.json')['files']:need(sha(H/member['path'])==member['sha256'],'immutable review member')
    return dict(schema='TSL9-source-integrated-IRQ-independent-contract-closure-v1',passed=True,selected_actual_build='source-integrated-99841ffbf5234f3a843228157e832782',modes=rows,
       source_provenance_sha256=sha(H/'source-provenance.json'),runner_sha256=provenance['runner_sha256'],manifest_sha256=provenance['manifest_sha256'],wrapper_sha256=sha(wrapper),
       source_commands_per_mode=44,dependency_rules_per_mode=36,pinned_native_dependencies_per_mode=71,generated_inputs_per_mode=4,artifact_readbacks_per_mode=144,
       original_main_bytes=144,native_main_bytes=144,exact_helper_bytes=120,whole_image_bytes=76800,changed_bytes=8,changed_range=[0x9a44,0x9a4c],
       limits=dict(strict_ROM_provider=False,numeric_ROM_witness_only=True,ROM_bytes_supplied=0,asynchronous_equivalence=False,pointwise_equivalence=False,hardware=False,OTA_ready=False,flashable=False,reviewer_executed_RV32=False,reviewer_compiled=False,reviewer_generated_BIN=False,network=False))
if __name__=='__main__':
    r=run();path=H/'final-audit.json'
    if path.exists():need(read(path)==r,'readonly final closure exact')
    else:path.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,modes=2,raw_controls_rejected=34,source_provenance=True,final_audit_sha256=sha(path))))
