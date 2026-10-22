"""Bounded original caller/timer/Flash evidence; no target or host model execution."""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
W=HERE.parents[2]
SCOPE=Path('apk-analysis/tsl9-v4160-resident-contracts-2026-10-21/flash-callers')
RECEIPT=Path('experiments/tsl9-v4160-startup/build/data-anchor-extension-ecb8f64d6d3640f2b8d2d6f6f6ad776e/verification.json')
ROOT_SHA='df90a9590431a62c937231117675a308feac9887a9aebce5825ee9bc76d86c09'
sha=lambda b:hashlib.sha256(b).hexdigest()

def need(ok,code):
    if not ok:raise ValueError(code)


def build(workspace):
    inputs={}
    def read(path):
        p=Path(path)
        if not p.is_absolute():p=workspace/p
        b=p.read_bytes();inputs[str(p)]=dict(path=str(p),bytes=len(b),sha256=sha(b));return b
    def load(path):return json.loads(read(path))
    parser=workspace/'apk-analysis/tsl9-v4160-opaque-contracts-2026-10-21/integration-review/elf_review.py'
    need(sha(read(parser))=='a839df729fc5ee2eed347a85ae9acf4ddf6ca9c01431d3ce0e3a614e4d54e21e','Pinned-host-only-ELF-reader')
    s=importlib.util.spec_from_file_location('flash_callers_elf',parser);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
    need(sha(read(RECEIPT))==ROOT_SHA,'Actual614-current-receipt')
    r=load(RECEIPT);alloc=r['allocations'];need(r['passed']and len(alloc)==614,'Latest-actual-layout-not-an-old-version')
    objects={};mode_meta={}
    for mode in('c','cpp'):
        p=r['modes'][mode]['integrated_object'];read(p);e=h.ELF32(p);wp=workspace/RECEIPT.parent/mode/'ADDRESS-WITNESS-ONLY.elf';read(wp);w=h.ELF32(wp)
        need(sha(e.raw)==r['modes'][mode]['integrated_sha256']and sha(w.raw)==r['modes'][mode]['numeric_witness_sha256'],'Actual-object-and-numeric-witness-hashes')
        mode_meta[mode]=dict(object_sha256=sha(e.raw),numeric_witness_sha256=sha(w.raw),allocations=len(alloc),semantic_RELA=len(e.relocations),named_UND=len(e.und()));objects[mode]=e
    need(mode_meta['c']==mode_meta['cpp'],'Both-language-current-artifacts-identical')
    e=objects['c']
    old=load('apk-analysis/tsl9-v4160-opaque-contracts-2026-10-21/body-triage/triage.json')
    cfg_path=workspace/'apk-analysis/tsl9-v4160-conditional-runtime-2026-10-21/native/cfg-proof.json'
    need(sha(read(cfg_path))=='ab1fd505f1e6de0e76d1cc27a5ee2e09c4492bd2cf8573c4941400bd42f42c08','Sealed-current-conditional-code-provenance')
    current=load(cfg_path);rows={}
    def gather(x):
        if isinstance(x,dict):
            if all(k in x for k in('va','raw_hex','disassembly')):
                if x['va']in rows:need(rows[x['va']]['raw_hex']==x['raw_hex'],'No-conflicting-retained-code-rows')
                rows[x['va']]=x
            for v in x.values():gather(v)
        elif isinstance(x,list):
            for v in x:gather(v)
    for p in old['old_CFG_pins']:
        need(sha(read(p['path']))==p['sha256'],'Original-captured-context-hash');gather(load(p['path']))
    gather(current)
    def view(pc):
        x=rows[pc];raw=bytes.fromhex(x['raw_hex']);owners=[(n,a)for n,a in alloc.items()if a['kind']=='code'and a['originalVA']<=pc<pc+len(raw)<=a['originalVA']+a['bytes']]
        need(len(owners)==1,'One-real-code-allocation-for-every-observed-instruction');n,a=owners[0]
        for obj in objects.values():need(obj.bysection[n]['data'][pc-a['originalVA']:pc-a['originalVA']+len(raw)]==raw,'Every-selected-original-row-matches-both-actual-ELFs')
        return dict(PC=pc,bytes=len(raw),raw_hex=raw.hex(),disassembly=x['disassembly'])
    def interval(start,end):
        out=[];pc=start
        while pc<end:
            x=view(pc);out.append(x);pc+=x['bytes']
        need(pc==end,'Finite-code-boundary-no-partial-instruction');return out
    code={f'{a:x}':interval(a,b)for a,b in[(0x19764,0x1979a),(0x1979a,0x197b8),(0x197be,0x197f0),(0x197f0,0x1995c),(0x199e2,0x19b16),(0x18e98,0x18f56)]}

    def mem(pc):
        x=view(pc);v=int.from_bytes(bytes.fromhex(x['raw_hex']),'little')
        if x['bytes']==4:
            op=v&127;f=(v>>12)&7
            need(op in(3,0x23),'Actual-memory-opcode')
            width={0:1,1:2,2:4,4:1,5:2}[f]
            return ('read'if op==3 else'write'),(v>>15)&31,h.signed(v>>20,12)if op==3 else h.signed(((v>>25)<<5)|((v>>7)&31),12),width,(v>>7)&31 if op==3 else(v>>20)&31
        q,f=v&3,(v>>13)&7
        need(q==0 and f in(2,6),'Only-actual-C-LW-SW-MMIO-format')
        return ('read'if f==2 else'write'),8+((v>>7)&7),(((v>>10)&7)<<3)|(((v>>6)&1)<<2)|(((v>>5)&1)<<6),4,8+((v>>2)&7)

    mmio=[]
    def memory_fact(pc,kind,base,offset,address,role):
        x=mem(pc);need(x[:4]==(kind,base,offset,4),'Exact-MMIO-operation-register-offset-and-width');mmio.append(dict(**view(pc),kind=kind,base_register=base,offset=offset,address=address,width=4,role=role))
    for pc,kind,offset in[(0x18ec8,'read',16),(0x18ed4,'write',16),(0x18ed6,'write',20),(0x18ed8,'read',16),(0x18ede,'write',16),(0x18ee0,'read',12),(0x18ee6,'read',16),(0x18eee,'write',16)]:memory_fact(pc,kind,15,offset,0x40022000+offset,'erase256-controller')
    for pc,kind,base,offset in[(0x18ef6,'read',14,16),(0x18f00,'write',14,16),(0x18f02,'read',14,12),(0x18f0c,'read',14,12),(0x18f2a,'read',14,12),(0x18f36,'read',14,16),(0x18f3e,'write',14,16),(0x18f44,'read',15,12),(0x18f4a,'read',15,16),(0x18f52,'write',15,16)]:memory_fact(pc,kind,base,offset,0x40022000+offset,'program256-controller')
    for pc,kind,offset in[(0x19768,'read',4),(0x1976e,'write',4),(0x19778,'write',16),(0x1977a,'write',20),(0x1977c,'read',0),(0x19782,'write',0),(0x19784,'read',0),(0x1978a,'write',0),(0x1978c,'read',4),(0x19792,'read',0),(0x19796,'write',0)]:memory_fact(pc,kind,15,offset,0xe000f000+offset,'polled-timer')
    need(mem(0x18f1e)==('read',13,0,4,16)and mem(0x18f26)==('write',13,0,4,16),'Actual-word-source-read-and-destination-store')
    for pc,target in[(0x18ee4,0x18ee0),(0x18f06,0x18f02),(0x18f10,0x18f0c),(0x18f2e,0x18f2a),(0x18f32,0x18f1a),(0x18f48,0x18f44),(0x19790,0x1978c)]:
        x=view(pc);d=h.direct(pc,x['bytes'],int.from_bytes(bytes.fromhex(x['raw_hex']),'little'));need(d and d[1]==target,'Every-Flash-or-timer-poll-loop-raw-target')
    need(view(0x18f0e)['raw_hex']=='898b'and view(0x18f16)['raw_hex']=='13060010'and view(0x18f30)['raw_hex']=='9107','Offset-starts-zero-after-bit1-clear-and-advances4-to256')
    need(view(0x19770)['raw_hex']=='03c7e117'and view(0x19774)['raw_hex']=='3306a702','Timer-reads-gp382-u8-and-multiplies-input-u32')
    wrapper_calls=[]
    for x in code['197be']:
        d=h.direct(x['PC'],x['bytes'],int.from_bytes(bytes.fromhex(x['raw_hex']),'little'))
        if d and d[0]==17:wrapper_calls.append(dict(PC=x['PC'],target=d[1],raw_hex=x['raw_hex']))
    need([(x['PC'],x['target'])for x in wrapper_calls]==[(0x197c8,0x18e98),(0x197ce,0x18ec4),(0x197d8,0x18ef2),(0x197dc,0x18eb6),(0x197e2,0x19764)],'Exact-wrapper-five-direct-calls-with-no-invented-status-clear')
    need(view(0x197e0)['raw_hex']=='0545'and view(0x197ea)['raw_hex']=='0145'and view(0x197b2)['raw_hex']=='0145','Timer-input1-and-both-hook-constant-zero-returns')
    for name in('197be','19764'):need(not any(x['bytes']==4 and int.from_bytes(bytes.fromhex(x['raw_hex']),'little')&127==0x73 for x in code[name]),'No-CSR-in-wrapper-or-timer-body')

    fields=[dict(offset=0,width=4,value=0x2000418c,store_PC=0x19a42,meaning='heap-address-like value; candidate MEMAddr'),dict(offset=4,width=2,value=0x7000,store_PC=0x19a46,meaning='candidate MEMLen'),dict(offset=8,width=4,value=0x08077c00,store_PC=0x19a52,meaning='candidate SNVAddr'),dict(offset=14,width=2,value=0x0803,store_PC=0x19a5a,meaning='candidate SNVNum3 / BufNumber8, not write mode'),dict(offset=16,width=2,value=251,store_PC=0x19a62,meaning='candidate BufMaxLen'),dict(offset=18,width=1,value=3,store_PC=0x19a6c,meaning='candidate TxNumEvent, not a Flash/OTA mode'),dict(offset=20,width=2,value=0x0e3f,store_PC=0x19a70,meaning='raw packed configuration bytes'),dict(offset=30,width=2,value=16000,store_PC=0x19a9a,meaning='candidate ClockFrequency'),dict(offset=32,width=2,value=1000,store_PC=0x19aae,meaning='candidate ClockAccuracy'),dict(offset=44,width=4,value=0x197f0,store_PC=0x19a9e,meaning='conditional peripheral hook; candidate tsCB'),dict(offset=48,width=4,value=0x197b8,store_PC=0x19ab2,meaning='old real six-byte hook; candidate rcCB'),dict(offset=56,width=4,value=0x1979a,store_PC=0x19a7e,meaning='conditional read-like hook; candidate readFlashCB'),dict(offset=60,width=4,value=0x197be,store_PC=0x19a88,meaning='conditional write-like hook; candidate writeFlashCB')]
    for f in fields:need(f['store_PC']in rows,'Every-record-field-has-an-original-store-site')
    for high,low,target in[(0x19a3a,0x19a3e,0x2000418c),(0x19a76,0x19a7a,0x1979a),(0x19a80,0x19a84,0x197be),(0x19a92,0x19a96,0x197f0),(0x19aa4,0x19aa8,0x197b8)]:
        hi=int.from_bytes(bytes.fromhex(view(high)['raw_hex']),'little');lo=int.from_bytes(bytes.fromhex(view(low)['raw_hex']),'little');need((high+h.signed(hi&0xfffff000,32)+h.signed(lo>>20,12))&0xffffffff==target,'Raw-record-pointer-formation-not-symbol-name-inference')
    need(view(0x19aec)['raw_hex']=='8297'and view(0x19af0)['raw_hex']=='01a0','Original-resident-record-call-and-failure-self-loop')
    need(h.direct(0x19aee,2,int.from_bytes(bytes.fromhex(view(0x19aee)['raw_hex']),'little'))==(44,0x19af2),'Zero-resident-result-continues-nonzero-traps')

    spec=load('experiments/tsl9-v4160-startup/evidence/conditional-runtime-integration.json');direct_to_hook=[]
    for n,a in alloc.items():
        if a['kind']!='code':continue
        data=e.bysection[n]['data'];off=0
        while off<len(data):
            width=4 if int.from_bytes(data[off:off+2],'little')&3==3 else 2
            d=h.direct(a['originalVA']+off,width,int.from_bytes(data[off:off+width],'little'))
            if d and d[1]==0x197be:direct_to_hook.append(dict(PC=a['originalVA']+off,type=d[0]))
            off+=width
    refs=[]
    for rel in e.relocations:
        if rel['symbol']['name']!='__tsl9v4160_address_197be':continue
        need(rel['type']==23 and rel['symbol']['index']==0 and rel['symbol']['type']==0,'Original-write-hook-canonical-remains-UND-address-only')
        refs.append(dict(PC=alloc[rel['section']]['originalVA']+rel['offset'],type=rel['type'],canonical=rel['symbol']['name'],originalVA=spec['expected_undefined_symbols'][rel['symbol']['name']]))
    need(not direct_to_hook and refs==[dict(PC=0x19a80,type=23,canonical='__tsl9v4160_address_197be',originalVA=0x197be)],'Bounded-current614-only-record-materialization-no-known-direct-OTA-edge')

    d=Path('C:/Users/locky/Documents/projects/re-tsl9/experiments/tsl9-contract-model')
    model={n:read(d/n).decode('utf-8')for n in('src/flash_page.c','src/flash_page.h','src/ram_bridge.c','src/target_ble_hal_init.c','verify-flash-page.ps1')}
    fixture=load(d/'fixtures/evidence.json');old_versions=load('apk-analysis/tsl9-server-current/verification.json')['serverInfoVersions']
    need(fixture['images']['runtime']['sha256']=='32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'and fixture['images']['boot']['sha256']=='650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb','Old-readable-model-artifact-identity-distinct-from-ID2966')
    need('0x15c02'in model['src/flash_page.c']and '18BE4/18BEC/'in model['src/flash_page.h'],'Exact-old-Runtime-helper-map')
    need('FP_CSR_CLEAR'in model['src/flash_page.c']and 'FP_CSR_SET'in model['src/flash_page.c']and '0x4002200c,49'in model['src/flash_page.c'],'Old-full-wrapper-has-extra-CSR-and-status49-not-present-in197BE')
    need('Fixed V4.1.00 HAL code only'in model['src/target_ble_hal_init.c'],'Old-HAL-source-explicitly-tags-V4100')
    # Vendor comments are not wholly UTF-8; only ASCII labels are compared,
    # with a lossless byte mapping and the original-byte SHA retained.
    header=workspace/'apk-analysis/tsl9-function-hardware/hardware/wchble_rom.h';header_text=read(header).decode('latin-1');timer_header=workspace/'apk-analysis/tsl9-function-hardware/third-round/platform/wch-core_riscv.h';read(timer_header)
    need('Version           : V1.40'in header_text and 'bonding information will not be saved'in header_text and 'pfnFlashWriteCB writeFlashCB'in header_text,'Candidate-V140-header-only-not-original-ROM-proof')
    probe=workspace/'apk-analysis/tsl9-v4160-resident-contracts-2026-10-21/sdk-layout/probe.c';read(probe)
    prior_flash=workspace/'apk-analysis/tsl9-v4160-conditional-runtime-2026-10-21/flash-evidence/flash-chain.json';flash=load(prior_flash)
    need(flash['passed']and not flash['OTA_ready'],'Earlier-sealed-flash-evidence-keeps-OTA-open')
    ledger=[dict(PC=0x197c8,target=0x18e98,a0='D',a1='entry ignored word X',a2='S',effect='four unlock-key writes'),dict(PC=0x197ce,target=0x18ec4,a0='D restored from s0',a1='X',a2='S',effect='align destination down256; erase/poll'),dict(PC=0x197d8,target=0x18ef2,a0='D restored from s0',a1='S restored from stack',a2='S, not length',effect='fixed256-byte word program/poll'),dict(PC=0x197dc,target=0x18eb6,a0='D&~255 after known callee',a1='S',a2='256 after known callee',effect='set controller lock bit15'),dict(PC=0x197e2,target=0x19764,a0=1,a1='S',a2='256 before timer overwrites it',effect='polled timer delay with unknown gp+382 scale'),dict(PC=0x197ea,target=None,a0=0,a1='unchanged by wrapper',a2='timer-dependent',effect='constant zero return, not hardware success')]
    return dict(schema='ID2966-independent-flash-caller-resident-contract-v1',passed=True,receipt=str(workspace/RECEIPT),receipt_sha256=ROOT_SHA,modes=mode_meta,original_firmware_sha256=current['source']['sha256'],selected_original_code=code,wrapper_call_register_ledger=ledger,MMIO_operations=mmio,program_word_access=dict(read_PC=0x18f1e,write_PC=0x18f26,width=4,initial_offset_proved_at=0x18f0e,initial_offset=0,step4_PC=0x18f30,limit256_PC=0x18f16,loop_branch_PC=0x18f32,conditional_stores=64,conditional_bytes=256,polls_termination_proved=False),timer=dict(entry=0x19764,bytes=54,base=0xe000f000,status_offset=4,compare_low_offset=16,compare_high_offset=20,GP_factor_offset=382,factor_width=1,compare_low_formula='u32(u8[gp+382] * input_a0)',compare_high=0,control_sequence=['OR16','OR33','AND~1'],status_sequence=['clearbit0','waitbit0set'],poll_PC=0x1978c,poll_branch_PC=0x19790,no_CSR_or_interrupt_restore=True,exact_time_unit_or_physical_clock_proved=False,candidate_source=str(timer_header),candidate_source_sha256=sha(read(timer_header))),record=dict(entry=0x199e2,stack_bytes=96,record_stack_offset=16,record_bytes=64,initial_opaque_zero_like_call=0x19a38,fields=fields,resident_pointer_slot=0x400a4,call_PC=0x19aec,input_a0='current sp+16',zero_result_continuation=0x19af2,nonzero_result_self_loop=0x19af0,stack_record_copied_or_retained_by_resident_unknown=True,hardware_write_success_checked_by_initializer=False),critical_section=dict(wrapper_CSR_operations=[],timer_CSR_operations=[],no_status49_write_in_wrapper=True,setup_after_resident_zero_result=[dict(PC=0x19b08,address=0xe000e104,value=0x80000000),dict(PC=0x19b0e,address=0xe000e108,value=1)],opaque_resident_or_other_callers_may_mask_interrupts_unknown=True),read_hook=dict(entry=0x1979a,bytes=30,input_symbols=['A','N','B'],resident_slot=0x4004c,call_PC=0x197ae,arguments=['B','A','u32(N<<2)'],return_value=0,resident_result_ignored=True,original_memcpy_ABI_or_read_extent_proved=False),other_record_hook=dict(entry=0x197f0,bytes=364,record_offset=44,effect='save/configure/poll/read/restore40021000/40012400-related peripheral registers',candidate_name='V1.40 tsCB temperature sample callback',physical_ADC_or_RF_identity_proved=False,Flash_or_OTA_route_proved=False),current_known_caller_scan=dict(allocations_scanned=len(alloc),semantic_RELA_scanned=len(e.relocations),direct_control_edges_to197BE=direct_to_hook,canonical_materializations=refs,arbitrary_dynamic_or_ROM_callers_excluded=False),candidate_corroboration=dict(header=str(header),header_sha256=sha(read(header)),version='V1.40 2024-01-02',layout_probe_source=str(probe),layout_probe_sha256=sha(read(probe)),checker_ran_compiler=False,field_names_are_candidate_not_original_ABI=True,SNV_comment_refers_to='bonding information persistence',field18_candidate_name='TxNumEvent, not a Flash/OTA operation mode'),role_classification=dict(confirmed='Original BLE-initialization-associated record carries read-like/write-like hooks and08077C00 storage-base-like field.',inference='Candidate V1.40 BLE-config layout and bonding/SNV comments support a BLE persistence/bonding-storage role.',not_proved=['Original resident invokes197BE.','Actual destination/source/count chosen by resident or its allowed Flash region.','Exclusive persistence use or a direct OTA command route.','Original V1.3 record ABI, pointer lifetime or interrupt exclusion.']),old_readable_model=dict(root=str(d),images=fixture['images'],source_contract=fixture['source_contract'],server_offered_runtime_label=old_versions['offeredRuntime'],registered_label_is_not_payload_identity=True,Runtime_site_delta=0x15c02,Runtime_helpers=[0x18be4,0x18bec,0x18c0a,0x18c18,0x18c46],matches_current_ID2966_artifact=False,reusable_semantic_patterns=['unlock keys','align256 erase','64word source-read/destination-write/poll','control-bit lock','explicit unknown MMIO backend/HALT/TRANSFER/source-knownness'],not_current_wrapper_contract=['old full wrapper CSR clear/set800/88','old status49 write','old PC mapping','no19764 timer step','does not close resident400A4-to197BE caller contract'],RAM_bridge_connection='Old ta_program_page routes through old OTA model; not original ID2966 resident proof.'),safe_readable_model_requirements=['Use a separate V4.1.60 source/PC table with197BE exact five-call order.','Represent source/destination accesses, MMIO reads/writes, timer GP-byte and unknown resident as explicit synthetic backend boundaries.','Keep unknown bits, unavailable or unaligned source words, unsigned wrap, polling budget/HALT and TRANSFER distinct from original constant-zero return.','No extra CSR save/restore or controller-status49 write; surrounding resident interrupt context stays unresolved.','Do not link the new host model as a provider for original opaque canonical names or a flashable image.'],inputs=sorted(inputs.values(),key=lambda x:x['path']),original_ROM_ABI_proved=False,OTA_route_proved=False,hardware_success_proved=False,target_ready=False,native_BIN=False,target_executed=False,emulation=False,network=False,hardware=False,ROOT_modified=False,D_modified=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,default=W);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args();need(a.workspace.is_absolute()and a.workspace.is_dir(),'Existing-explicit-workspace')
    if a.write:need(not(HERE/'seal.json').exists(),'Refuse-sealed-evidence-write')
    r=build(a.workspace.resolve());b=(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode()
    if a.write:(HERE/'proof.json').write_bytes(b)
    else:
        need((HERE/'proof.json').read_bytes()==b,'Readonly-byte-exact-bounded-proof')
        if(HERE/'seal.json').exists():
            s=json.loads((HERE/'seal.json').read_bytes());need(s['passed']and s['sealed'],'Terminal-evidence-seal')
            for x in s['members']:
                raw=(HERE/x['path']).read_bytes();need(len(raw)==x['bytes']and sha(raw)==x['sha256'],'Every-sealed-evidence-member')
    print(json.dumps(dict(passed=True,readonly_byte_exact=bool(a.check),proof_sha256=sha(b),record_flash_hook_offset=60,timer_entry=0x19764,OTA_route_proved=False,target_executed=False)))

if __name__=='__main__':
    try:main()
    except Exception as error:print(json.dumps(dict(passed=False,error_class=type(error).__name__,code=str(error))));raise SystemExit(1)
