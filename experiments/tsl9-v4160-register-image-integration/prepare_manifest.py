"""Derive validation ledgers from sealed component metadata, never generate code."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def case(root,slug):return next(p for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(p,d):
    need(not p.exists(),'create-only validation ledger');p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--flash-component',type=Path);p.add_argument('--refresh-scheduler-only',action='store_true');a=p.parse_args();root=a.project_root.resolve()
    if a.refresh_scheduler_only:
        current=H/'source-manifest.json';need(sha(current)=='d71f2b3aea85203418e8022ac2674caa487930e6c5888c9e5227d75023fc8442','one known unsealed prebuild ledger')
        freeze=root/'exports/frame-schedule-model-freeze.json';need(sha(freeze)=='cb98068c1b85affef4fc20aa60d32d53bf92c6c585c6ea35c0c4937df6a4096c','parent final scheduler source ledger')
        diagnostic=H/'build/prebuild-source-drift';diagnostic.mkdir(parents=True);(diagnostic/'source-manifest-d71f2b.json').write_bytes(current.read_bytes());m=read(current);m['frame_schedule_source_files']={r['path']:r['sha256'] for r in read(freeze)['files']}
        for name,pin in m['frame_schedule_source_files'].items():need(sha(root/name)==pin,'actual final parent scheduler file')
        current.write_bytes((json.dumps(m,indent=2)+'\n').encode());print(json.dumps(dict(passed=True,manifest_sha256=sha(current),scheduler_files=len(m['frame_schedule_source_files']))));return
    need(a.flash_component is not None,'explicit current component required');old=root/'experiments/tsl9-v4160-flash-image-integration';need(sha(old/'source-manifest.json')=='afe5eba6e7b6af15c9556fa9c9a366e5c4713dcbf343b16d2d8077eb6c1b4b1c','sealed prior691 ledger');m=read(old/'source-manifest.json');prior=json.loads(json.dumps(m))
    native=case(root,'v4160-flash-register-prefix-2026-10-22')/'implementation';need(sha(native/'seal.json')=='b945b1e5f19fef328ca1dac6289b131f6fabb154977b4c7080f353f22b27e331','closed exact-five-leaf source');report=read(native/'receipts/native-c.json');component=a.flash_component.resolve();need(sha(component)=='575b2e1009437c77d71081fffeaa32988ff10b23c78decb01e9ad976c5e6c9c7','actual sealed current Flash component')
    parser=case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py';need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','pinned ELF parser');E=load('register_image_ledger_elf',parser).ELF;e=E(component)
    scheduler=root/'experiments/tsl9-v4160-frame-schedule';need(sha(scheduler/'schedule.py')=='dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d','explicit scheduling algorithm');S=load('register_image_ledger_schedule',scheduler/'schedule.py');policy=read(scheduler/'frame-policy.json')
    for row in m['selected_sections']:
        symbol=row['new_C_symbol'];va=row['originalVA'];compiled=bytes.fromhex(row['native_linked_bytes']);object_pin=row['native_object_sha256']
        if row['family']=='Flash':
            name=next(n for n in report['checks']['functions'] if symbol=='tsl9_flash_'+n+'_'+format(va,'x'));compiled=e.function_bytes(next(x for x in e.symbols if x['name']==symbol));object_pin=report['checks']['functions'][name]['code_sha256']
        obj=bytearray(compiled)
        for r in m['old_selected_RELA']:
            if r['owner']==row['name'] and r['type']==17:
                at=r['offset'];word=int.from_bytes(obj[at:at+4],'little');need(word&0xfff==0xef,'original explicit JAL RA opcode');obj[at:at+4]=(0xef).to_bytes(4,'little')
        need(hashlib.sha256(obj).hexdigest()==object_pin,'sealed compiler object identity derived only by declared JAL fixups')
        row['compiler_native_object_sha256']=object_pin;row['compiler_linked_bytes']=compiled.hex();scheduled_obj=bytes(obj);scheduled=compiled
        for name,rule in policy['functions'].items():
            if rule['symbol']!=symbol:continue
            def permute(body):
                order=[tuple(x) for x in rule['compiler_order']];actual=[S.decode_save(struct.unpack_from('<H',body,2+2*i)[0]) for i in range(len(order))];need(actual==order,'observed compiler save sequence');words={pair:body[2+2*i:4+2*i] for i,pair in enumerate(order)};return body[:2]+b''.join(words[tuple(x)] for x in rule['required_order'])+body[2+2*len(order):]
            scheduled_obj=permute(scheduled_obj);scheduled=permute(scheduled)
        row['native_object_sha256']=hashlib.sha256(scheduled_obj).hexdigest();row['native_linked_bytes']=scheduled.hex();need(scheduled.hex()==row['original_bytes'],'all eleven expected linked bodies match immutable original reference')
    old_flash='experiments/tsl9-v4160-flash-entry-order/src/';m['source_files']={n:pin for n,pin in m['source_files'].items() if not n.startswith(old_flash)}
    for name in ('flash_native.c','flash_native.h','native_io.h'):
        path=root/'experiments/tsl9-v4160-flash-register-prefix/src'/name;m['source_files'][path.relative_to(root).as_posix()]=sha(path)
    m.update(schema='TSL9-explicit-register-scheduled-source-image-ledger-v1',previous_manifest_sha256=sha(old/'source-manifest.json'),flash_native_receipt_sha256=sha(native/'receipts/native-c.json'),flash_component_sha256=sha(component),register_prefix_implementation_seal_sha256=sha(native/'seal.json'),frame_schedule_source_files={p.relative_to(root).as_posix():sha(p) for p in scheduler.iterdir() if p.is_file() and p.name!='seal.json'},expected_differences=[],differences_from_previous_full_image=[dict(address=r['address'],previous=r['native'],native=r['original']) for r in prior['expected_differences']],differences_from_previous_IRQ_image=[dict(address=r['address'],previous=r['native'],native=r['original']) for r in read(root/'experiments/tsl9-v4160-irq-image-integration/source-manifest.json')['expected_differences']])
    write(H/'source-manifest.json',m);need(not(H/'original-image-layout.ld').exists(),'create-only historical layout copy');(H/'original-image-layout.ld').write_bytes((old/'original-image-layout.ld').read_bytes())
    print(json.dumps(dict(passed=True,manifest_sha256=sha(H/'source-manifest.json'),compiler_units=42,selected_functions=11,expected_original_differences=0,previous_image_differences=len(m['differences_from_previous_full_image']),original_BIN_read_for_generation=False)))
if __name__=='__main__':main()
