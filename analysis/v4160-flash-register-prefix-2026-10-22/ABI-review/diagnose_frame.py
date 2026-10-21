"""One bounded MIR diagnostic at the unchanged profile's prologepilog boundary; no target execution."""
from pathlib import Path
import hashlib,json,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    records=[]
    for mode in ('c','cpp'):
        source=ROOT/'experiments/tsl9-v4160-flash-image-integration/build/formal-final'/mode
        receipt=source/'verification.json';r=json.loads(receipt.read_bytes());expected={'c':'655bb92d1e3f57ea0db68c95efcc8d64d772fc3760d57425c189d897a2ea81fc','cpp':'0c2328f747b27348554b727d2fe18ddb88c57275d29300a11291b59272320a52'}
        if SHA(receipt)!=expected[mode]:raise ValueError('immutable actual baseline producer receipt')
        source_pins={str(ROOT/path):digest for path,digest in r['source_files'].items()}
        if any(SHA(Path(path))!=digest for path,digest in source_pins.items()):raise ValueError('actual baseline source before diagnostic')
        for unit,label in [('irq','typed-main-object'),('quarter','typed-flash-quarter-object')]:
            command=next(c for c in r['commands'] if c['label']==label)['argv'];tool=Path(command[0]);before=SHA(tool);adapter=Path(command[command.index('-include')+1]);adapter_pin=SHA(adapter)
            for when in ('before','after'):
                folder=HERE/'build'/mode;folder.mkdir(parents=True,exist_ok=True);out=folder/f'{unit}-{when}.mir';args=[];i=0
                while i<len(command):
                    token=command[i]
                    if token in ('-MF','-MT','-o'):i+=2;continue
                    if token in ('-MMD','-c'):i+=1;continue
                    args.append(token);i+=1
                args+=['-S','-mllvm',f'-stop-{when}=prologepilog','-o',str(out)]
                done=subprocess.run(args,capture_output=True,timeout=60);log=folder/f'{unit}-{when}.log';log.write_bytes(done.stdout+done.stderr)
                if done.returncode:raise ValueError(f'fixed diagnostic failed: {mode}/{unit}/{when}; see {log}')
                if SHA(tool)!=before:raise ValueError('compiler changed during bounded diagnostic')
                if SHA(adapter)!=adapter_pin or any(SHA(Path(path))!=digest for path,digest in source_pins.items()):raise ValueError('input changed during fixed diagnostic')
                records.append(dict(mode=mode,unit=unit,when=when,argv=args,exit=done.returncode,compiler_sha256=before,source_receipt_sha256=SHA(receipt),source_before_after_sha256=source_pins,adapter_sha256=adapter_pin,output=out.relative_to(HERE).as_posix(),output_sha256=SHA(out),log=log.relative_to(HERE).as_posix(),log_sha256=SHA(log)))
    result=dict(schema='TSL9-fixed-profile-prologepilog-diagnostic-v1',passed=True,commands=records,target_execution=False,ISA_emulation=False,profile_search=False,source_variant=False)
    (HERE/'frame-diagnostic.json').write_bytes((json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps(dict(passed=True,diagnostic_commands=len(records),target_execution=False)))


if __name__=='__main__':main()
