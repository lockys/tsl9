"""One-time bounded operand capture from original and an existing address witness."""
import argparse,json,subprocess
from pathlib import Path
import review

def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    for n in ('firmware','image-elf','objdump'):p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args();root=a.project_root.resolve();h=review.HERE
    review.need(not (h/'seal.json').exists(),'Never rewrite a closed scope')
    prior,decode,E=review.context(root);fw=a.firmware.read_bytes();review.need(review.sha(a.firmware)==review.FW,'Original firmware pin')
    old=review.case(root,'v4160-ota-handler-2026-10-22')/'source-review'
    parse=prior['context'](root)[2]
    review.need(review.sha(a.objdump)=='de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa','Known actual static tool')
    ledger={};records=[];displays=[];e=E(a.image_elf)
    for n,(start,end) in review.RANGES.items():
        actual=review.rows(fw[start-0x8000:end-0x8000],start,decode);ledger[n]=actual
        if n=='TX_original':
            expected=review.read(review.case(root,'v4160-ota-tx-2026-10-22')/'source-review/source-proof.json')['decoded_rows']
            review.need(actual==expected,'Original TX agrees with closed raw source fields');continue
        sec=next(s for s in e.sections if s['flags']&2 and s['address']<=start and end<=s['address']+s['size'])
        review.validate(e.data(sec)[start-sec['address']:end-sec['address']],start,decode,actual)
        argv=[str(a.objdump.resolve()),'--mattr=+m,+a,+c,+zicsr','-d','--start-address='+hex(start),'--stop-address='+hex(end),str(a.image_elf.resolve())]
        run=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
        text=run.stdout.decode('utf-8');review.need(run.returncode==0 and parse(text)==actual,'Independent LLVM/raw operands '+n)
        records.append(dict(name=n,argv=argv,exit=run.returncode,owner=sec['name'],owner_bytes=sec['size']))
        displays.append(text)
    data=dict(schema='TSL9-reply-consumer-original-operands-v1',firmware_sha256=review.FW,rows=ledger)
    meta=dict(firmware_sha256=review.FW,image_ELF_sha256=review.sha(a.image_elf),objdump_sha256=review.sha(a.objdump),
              static_commands=records,original_rows=sum(map(len,ledger.values())),new_target_execution=False)
    for name,value in [('source-ledger.json',data),('capture.json',meta)]:
        with (h/name).open('xb') as f:f.write((json.dumps(value,indent=2)+'\n').encode())
    with (h/'consumer-llvm.txt').open('xb') as f:f.write(('\n'.join(displays).replace('\r\n','\n').rstrip()+'\n').encode())
    print(json.dumps(dict(passed=True,rows=sum(map(len,ledger.values())),commands=len(records))))
if __name__=='__main__':main()
