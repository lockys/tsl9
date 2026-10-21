"""Explicit new validation entry: partition new relative32 records, retain old gate.

The frozen data-anchor verifier's inherited gate counts all relative32 records.
This entry validates the exact new records first, passes every remaining record
to that unchanged gate, then checks the existing original-VA fixed table in the
actual merged object AND numeric witness. It never executes target instructions.
"""
from pathlib import Path
import argparse,collections,contextlib,hashlib,io,json,runpy,sys

ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())

def need(c,message):
    if not c:raise AssertionError(message)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--spec',type=Path,default=ROOT/'evidence/gatt-ingress-integration.json')
    parser.add_argument('--firmware',type=Path,default=ROOT.parents[1]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
    parser.add_argument('--baseline-receipt',type=Path)
    args=parser.parse_args();spec=read(args.spec)
    frozen=ROOT/'verify-data-anchor-extension.py'
    need(sha(frozen)=='53e98521e679f5e2db9c687932f52e95787ebeafbeb8f019c8aa4efcc0954cbe','Frozen verifier unchanged')
    item=next(x for x in spec['modules'] if x['name']=='gatt-ingress');plan_path=ROOT/item['plan'];plan=read(plan_path)
    need(sha(plan_path)==item['plan_sha256'],'New module plan identity')
    cfg_path=ROOT/item['cfg_evidence'];cfg=read(cfg_path)
    need(sha(cfg_path)==item['cfg_sha256']==plan['CFG_review_sha256'] and cfg['passed'],'Original instruction-boundary evidence')
    starts={i['va'] for g in cfg['graphs'] for i in g['instructions']}
    entries=plan['relative32_expressions'];need(len(entries)==5,'Five exact new symbolic table entries')
    sections={x['section'] for x in entries};need(len(sections)==1,'New table owns its records')
    expected=collections.Counter((r['section'],r['offset'],r['type_number'],r['target'],r['addend']) for r in plan['relocations'] if r['type_number'] in (35,39))
    need(sum(expected.values())==10 and all(v==1 for v in expected.values()),'Exact new nonduplicated ADD/SUB pair multiplicity')
    frozen_ns=runpy.run_path(str(frozen));entry=frozen_ns['main'];scope=entry.__globals__;original=scope['anchor_check_inherited_relative'];partition_checks=[]
    class InheritedView:
        def __init__(self,elf,records):self.elf=elf;self.relocations=records
        def __getattr__(self,name):return getattr(self.elf,name)
    def partition(elf,allocations,normalized,count):
        new=[r for r in elf.relocations if r['section'] in sections and r['type'] in (35,39)]
        actual=collections.Counter((r['section'],r['offset'],r['type'],r['target'],r['addend']) for r in new)
        need(actual==expected,'New relative32 exact semantic Counter; no missing/extra/cancelling records')
        ids={id(r) for r in new};remaining=[r for r in elf.relocations if id(r) not in ids]
        need(count==534 and sum(r['type'] in (35,39) for r in remaining)==1068,'All inherited 534 pairs remain')
        original(InheritedView(elf,remaining),allocations,normalized,count)
        partition_checks.append(dict(passed=True,new_records=len(new),inherited_records=1068))
    scope['anchor_check_inherited_relative']=partition
    old_argv=sys.argv;sys.argv=[str(frozen),'--spec',str(args.spec.resolve()),'--firmware',str(args.firmware.resolve())]
    if args.baseline_receipt:sys.argv+=['--baseline-receipt',str(args.baseline_receipt.resolve())]
    output=io.StringIO()
    try:
        with contextlib.redirect_stdout(output):entry()
    finally:sys.argv=old_argv;scope['anchor_check_inherited_relative']=original
    summary=json.loads(output.getvalue().strip());subreceipt=Path(summary['receipt']);report=read(subreceipt)
    need(summary['passed'] and report['passed'] and len(partition_checks)==2,'Both full adapted native modes passed')
    ELF=scope['ELF'];raw=args.firmware.read_bytes();fixed=plan['existing_original_VA_fixed_tables'];need(len(fixed)==1,'One explicit original-VA table contract')
    checks={}
    for mode in ('c','cpp'):
        meta=report['modes'][mode];obj=ELF(Path(meta['integrated_object']));witness=ELF(subreceipt.parent/mode/'ADDRESS-WITNESS-ONLY.elf')
        need(sha(Path(meta['integrated_object']))==meta['integrated_sha256'] and hashlib.sha256(witness.raw).hexdigest()==meta['numeric_witness_sha256'],'Actual current artifacts')
        for table in fixed:
            need(not table['new_storage'] and not table['new_RELA_emitted'] and table['existing_table_RELA_count']==0,'Do not pretend raw table has symbolic relocations')
            va=table['originalVA'];off=table['section_offset'];name=table['section'];storage=report['allocations'][name]
            need(storage['originalVA']+off==va and table['bytes']==28 and len(table['entries'])==7,'Exact original table interval')
            for elf,linked in ((obj,False),(witness,True)):
                section=elf.byname[name];symbol=elf.symbol[table['base_symbol']]
                need(section['size']==191 and hashlib.sha256(section['data']).hexdigest()==table['old_carrier_sha256'],'Original old191 bytes retained')
                need(symbol['index']==section['index'] and symbol['type']==1 and symbol['size']==191 and symbol['value']==(storage['originalVA'] if linked else 0),'Real old OBJECT provider retained')
                need(not linked or section['address']==storage['originalVA'],'Actual fixed original placement')
                for row in table['entries']:
                    offset=off+row['index']*4;word=int.from_bytes(section['data'][offset:offset+4],'little');target=(va+word)&0xffffffff
                    need(word==row['original_u32'] and target==row['target'] and raw[row['word_originalVA']-0x8000:row['word_originalVA']-0x8000+4]==word.to_bytes(4,'little'),'Original relative table words and targets')
                    need(target in starts,'Pinned raw CFG instruction start for each fixed-table target')
                    carriers=[(n,s) for n,s in report['allocations'].items() if s['kind']=='code' and s['originalVA']<=target<s['originalVA']+s['bytes']]
                    need(len(carriers)==1,'Unique actual code target storage');n,s=carriers[0];code=elf.byname[n];at=target-s['originalVA'];width=4 if int.from_bytes(raw[target-0x8000:target-0x8000+2],'little')&3==3 else 2
                    need(code['flags']==6 and code['data'][at:at+width]==raw[target-0x8000:target-0x8000+width],'Actual original target instruction bytes')
                    need(not linked or code['address']==s['originalVA'],'Target original numeric placement')
            need(not any(r['section']==name and off<=r['offset']<off+28 for r in obj.relocations),'Existing fixed table has no silently added RELA')
        checks[mode]=dict(passed=True,original_VA_fixed_entries=7,new_symbolic_entries=5,new_symbolic_records=10,arbitrary_relocation_safe=False)
    report.update(schema='ID2966-gatt-ingress-adapted-extension-report-v1',underlying_report=str(subreceipt),underlying_report_sha256=sha(subreceipt),verification_adapter=dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__)),frozen_source_sha256=sha(frozen),partition_checks=partition_checks),existing_original_VA_fixed_table_checks=checks,original_VA_layout_required=True,arbitrary_relocation_safe=False)
    report['source_files'][Path(__file__).name]=sha(Path(__file__))
    target=subreceipt.parent/'gatt-ingress-verification.json';need(not target.exists(),'New adapter receipt only')
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,receipt=str(target),sha256=sha(target),code_bytes=report['modes']['c']['code_bytes'],native_BIN=False,OTA_ready=False)))

if __name__=='__main__':main()
