"""Extract a portable source/byte ledger; no compilation or object linking."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def case(root,slug):return next(p for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--flash-component',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();old=root/'experiments/tsl9-v4160-irq-image-integration';m=read(old/'source-manifest.json')
    need(sha(old/'source-manifest.json')=='d952159ab2bf7c5294bc433510b88a7c19b23295ba11b0e7ab3d4a1ed39b1ce7','original full source inventory')
    plan=case(root,'v4160-flash-entry-order-2026-10-22')/'image-plan';need(sha(plan/'seal.json')=='81912879ab740bff2055d518eac48f2191fad242ed782fc84cc7e3d0ea62169d','eleven-function source plan')
    for r in read(plan/'seal.json')['members']:need(sha(plan/r['path'])==r['sha256'],'frozen plan member')
    report=read(plan/'report.json');vp=case(root,'v4160-irq-image-integration-2026-10-21')/'integration/verify_image.py';need(sha(vp)=='b26410ae9a0d9dece3e5404fb311407dd7c3022a08a7d2fb8c8df7834496c854','immutable generic layout helper');V=load('prior_image_helpers',vp);ctx=V.context(root);E=ctx['ELF']
    source_case=case(root,'v4160-flash-entry-order-2026-10-22');fp=source_case/'implementation/receipts/native-c.json';fr=read(fp);component=a.flash_component.resolve();need(sha(component)=='aeccc19da9c5764a386333dd26898429c35bf0ff40efb08c8f8417b11820339d','sealed current Flash component')
    e=E(component);firmware=next(root/n for n in ['firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'] if (root/n).is_file());original=firmware.read_bytes();need(sha(firmware)==m['original_image_sha256'],'exact reference')
    irq={r['name']:r for r in m['selected_sections']};rows=[];symbols={s['name']:s for s in e.symbols}
    expected=bytearray(original)
    for r in m['expected_differences']:expected[r['address']-0x8000]=r['native']
    for r in report['selected']:
        r=dict(r);va=r['originalVA'];r['family']='IRQ' if r['name'] in irq else 'Flash'
        if r['family']=='IRQ':r['new_C_symbol']=irq[r['name']]['new_C_symbol'];r['native_object_sha256']=ctx['native_code_sha256'][r['new_C_symbol']]
        else:
            name={0x9c0a:'quarter',0x18e90:'status',0x18e98:'unlock',0x18eb6:'lock',0x18ec4:'erase',0x18ef2:'program'}[va];r['new_C_symbol']='tsl9_flash_'+name+'_'+format(va,'x');r['native_object_sha256']=fr['checks']['functions'][name]['code_sha256'];body=e.function_bytes(symbols[r['new_C_symbol']]);need(len(body)==r['bytes'],'full current function extent');expected[va-0x8000:va-0x8000+r['bytes']]=body
        r['native_linked_bytes']=bytes(expected[va-0x8000:va-0x8000+r['bytes']]).hex();r['original_bytes']=original[va-0x8000:va-0x8000+r['bytes']].hex();rows.append(r)
    names={r['name'] for r in rows};old_irq_names=set(irq);m['old_selected_RELA']+= [r for r in report['old_owned_RELA'] if r['owner'] not in old_irq_names]
    need(len(m['old_selected_RELA'])==21,'original twentyone owned call/branch records')
    m.update(schema='TSL9-eleven-readable-function-source-image-manifest-v1',selected_sections=rows,retained_RELA_count=8259,retained_RELA_semantic_sha256=report['outside_RELA_semantic_sha256'],external_incoming_RELA=report['checks']['incoming'],entry_order_plan_seal_sha256=sha(plan/'seal.json'),entry_order_report_sha256=sha(plan/'report.json'),flash_native_receipt_sha256=sha(fp),flash_component_sha256=sha(component),filtered_carrier_units=report['filtered_carrier_units'])
    for n in ('flash_native.c','flash_native.h','native_io.h'):
        path=root/'experiments/tsl9-v4160-flash-entry-order/src'/n;m['source_files'][path.relative_to(root).as_posix()]=sha(path)
    m['expected_differences']=[dict(address=0x8000+i,original=x,native=y) for i,(x,y) in enumerate(zip(original,expected)) if x!=y]
    m['differences_from_previous_IRQ_image']=[r for r in m['expected_differences'] if r['address'] not in {x['address'] for x in read(old/'source-manifest.json')['expected_differences']}]
    old_plan=case(root,'v4160-irq-callframe-2026-10-21')/'image-plan/verification.json';retained={r['name']:r for r in read(old_plan)['retained_allocations']};m['retained_storage']={n:retained[n] for n in m['allocations'] if n not in names};need(len(m['retained_storage'])==680,'680 retained storage hashes')
    for r in m['old_selected_RELA']:
        if r['type'] in (16,44):
            owner=next(x for x in rows if x['name']==r['owner']);at=owner['originalVA']-0x8000+r['offset'];size=4 if original[at]&3==3 else 2;r['original_branch_bytes']=original[at:at+size].hex()
    for path,payload in [(H/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode()),(H/'original-image-layout.ld',(old/'original-image-layout.ld').read_bytes())]:
        need(not path.exists(),'create-only source ledger');path.write_bytes(payload)
    print(json.dumps(dict(passed=True,manifest_sha256=sha(H/'source-manifest.json'),selected=11,source_units=34,source_files=len(m['source_files']),retained_storage=680,outside_RELA=8259,original_owned_RELA=21,differences=len(m['expected_differences']),differences_from_previous_IRQ=len(m['differences_from_previous_IRQ_image']))))
if __name__=='__main__':main()
