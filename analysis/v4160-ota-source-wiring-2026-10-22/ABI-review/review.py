"""Read-only independent source-wiring image review/replay; no compilation or target execution."""
import argparse,json
from pathlib import Path
import machine as M
import provenance
import controls

HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def read(p):return json.loads(Path(p).read_bytes())
def references(root):
    for name,pin in read(HERE/'reference-pins.json').items():
        path=root/name
        if not path.is_file() and name.startswith('apk-analysis/tsl9-'):path=root/name.replace('apk-analysis/tsl9-','analysis/',1)
        M.need(path.is_file() and M.sha(path)==pin,'Current pinned source/reference '+name)
def closed():
    if (HERE/'seal.json').exists():
        for n,pin in read(HERE/'seal.json')['members'].items():
            p=(HERE/n).resolve();M.need(p.is_relative_to(HERE) and M.sha(p)==pin,'Closed independent review member '+n)
def inspect(root,folder,firmware,negative_controls=False,allow_prototype=False):
    root=Path(root).resolve(strict=True);folder=Path(folder).resolve(strict=True);firmware=Path(firmware).resolve(strict=True);closed();references(root)
    record_path=folder/'verification.json'
    if not record_path.exists():
        M.need(allow_prototype,'Formal verification.json required');record_path=folder/'prototype.json'
    record=read(record_path);mode=record['mode'];M.need(mode in M.BASE,'Actual language')
    paths={k:Path(v).resolve(strict=True) for k,v in record['paths'].items()};E=M.parser(root)
    M.need(M.sha(paths['base_object'])==M.BASE[mode][0] and M.sha(paths['base_witness'])==M.BASE[mode][1] and M.sha(paths['base_image'])==M.IMAGE,
           'Actual known base ET_REL/witness/image, no invented archive path')
    baseline_receipt=read(paths['base_receipt']);M.need(baseline_receipt['mode']==mode,'Base generation language identity')
    for name,key in (('source-integrated.o','base_object'),('ADDRESS-WITNESS-ONLY.elf','base_witness'),('NOT-FLASH-VALIDATED-tx-integrated.bin','base_image')):
        p=paths[key];M.need(baseline_receipt['artifacts'][name]==dict(bytes=p.stat().st_size,sha256=M.sha(p)),'Base receipt binds actual retained input '+key)
    b=E(paths['base_object']);bw=E(paths['base_witness']);w=E(folder/'base-weakened.o');n=E(folder/'native_alias.o');t=E(folder/'page_tail.o');o=E(folder/'source-integrated.o');l=E(folder/'ADDRESS-WITNESS-ONLY.elf')
    base_image=paths['base_image'].read_bytes();image=(folder/'NOT-FLASH-VALIDATED-ota-source-wired.bin').read_bytes()
    fresh=provenance.inspect(root,folder,record,n)
    weak=M.weakened(b,w);partial=M.partial(b,n,t,o);metadata=M.metadata(b,n,t,o,l);relocated=M.relocated_component(n,l);final=M.final(bw,o,l,base_image,image)
    M.need(M.sha(firmware)==FW and firmware.stat().st_size==76800,'Actual original ID2966, validation only')
    raw=firmware.read_bytes();boundary=raw[0x18730-0x8000:0x18734-0x8000]
    M.need(boundary.hex()=='6f70120d' and M.jal(boundary,0x18730)==(0,0x40000,0x18734),'Original no-link ROM boundary rawrd0/target40000')
    calls=[r for r in b.relocations if r['symbol']['name']==M.ROM]
    M.need(len(calls)==1 and calls[0]['offset']==134 and calls[0]['type']==17 and calls[0]['addend']==0 and calls[0]['symbol']['index']==0,
           'Actual sole original ROM boundary remains genuine UND, not a provider')
    owner=bw.byname[calls[0]['owner']];M.need(owner['address']+134==0x18730,'Original reset relocation mapped actualPC')
    original530=raw[0x9c4a-0x8000:0x9e5c-0x8000];old=bw.byname['.text.tsl9v4160.ota_handler_9c4a']
    M.need(bw.data(old)==original530 and image[0x1c4a:0x1e5c]==original530,'Original530 preserved in actual full image')
    M.need(all(str(firmware) not in c['argv'] for c in record['commands']),'Original firmware is not a compiler/objcopy/link generation input')
    controls_result=controls.run(root,folder,b,bw,n,t,o,l,base_image,image) if negative_controls else []
    artifacts={name:dict(bytes=(folder/name).stat().st_size,sha256=M.sha(folder/name)) for name in
        ('native_alias.o','native_alias.ll','native_alias.d','page_tail.o','base-weakened.o','source-integrated.o','ADDRESS-WITNESS-ONLY.elf',
         'NOT-FLASH-VALIDATED-ota-source-wired.bin',record_path.name)}
    return dict(schema='TSL9-source-wiring-independent-image-review-v1',passed=True,metadata_only=False,
        actual_full_image_artifacts_read=True,actual_original_firmware_read=True,actual_firmware_sha256=FW,
        folder=folder.relative_to(root).as_posix(),mode=mode,artifacts=artifacts,source_provenance=fresh,
        weakening=weak,partial=partial,metadata=metadata,native_relocations=relocated,final=final,
        original_ROM_boundary=dict(PC=0x18730,raw=boundary.hex(),rd=0,target=0x40000,source_true_UND=True,numeric_witness_only=True),
        focused_actual_controls=controls_result,focused_controls_count=len(controls_result),ROM_provider_proved=False,
        actual_source_entry_reroute_proved=True,physical_free_storage_proved=False,full_ABI_admitted=False,
        HOST_rerun=False,target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path)
    p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);p.add_argument('--controls',action='store_true');p.add_argument('--prototype',action='store_true')
    a=p.parse_args();root=a.project_root.resolve(strict=True)
    if a.replay:
        M.need(not a.folder and not a.receipt and not a.controls and not a.prototype,'Read-only replay mode uses recorded folder')
        saved=read(a.replay);M.need(M.sha(a.firmware)==saved['result']['actual_firmware_sha256'],'Same actual firmware for replay')
        result=inspect(root,root/saved['result']['folder'],a.firmware,False,saved['prototype'])
        want=dict(saved['result']);want['focused_actual_controls']=[];want['focused_controls_count']=0
        M.need(result==want,'Canonical actual read-only result equals receipt');print(json.dumps(result));return
    M.need(a.folder and a.receipt,'Explicit actual folder and create-only receipt required')
    receipt=a.receipt.resolve();M.need(not receipt.exists() and not receipt.is_relative_to(a.folder.resolve()),'Create-only receipt outside generation folder')
    result=inspect(root,a.folder,a.firmware,a.controls,a.prototype);receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open('xb') as f:f.write((json.dumps(dict(prototype=a.prototype,result=result),indent=2)+'\n').encode())
    print(json.dumps(result))
if __name__=='__main__':main()
