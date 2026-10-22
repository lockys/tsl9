"""Independent raw prefix/component review. Static parsing only; never execute RV32."""
from pathlib import Path
import argparse,hashlib,json,re,runpy,struct,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SHA=lambda b:hashlib.sha256(b).hexdigest()
PRIOR_REVIEW='4d7e1b4ffa5101347970a662390c4cb8ff6455161e47d6e68f2144a27b8ca7e1'
CORE={'flash_native.c':'94bbb25ff93325152240c03d2fe01fbc5c7215417ffd3d98b2a61ecde21a7393','flash_native.h':'b26fe2050e88708e7d18257841f5682ac49fcd4b402aac42ffc5aaae649dd7bd','native_io.h':'579916278d4967cef1af0d04b68b403a515f3d56977613015639a0c9c916c08c'}
FRAMES={0x9a42:dict(name='tsl9_rebuild_interrupt_registers_9a42',bytes=144,frame=16,original=[(18,0),(1,12),(8,8),(9,4)],compiler=[(1,12),(8,8),(9,4),(18,0)],end=10),0x9c0a:dict(name='tsl9_flash_quarter_9c0a',bytes=64,frame=32,original=[(8,24),(9,20),(1,28)],compiler=[(1,28),(8,24),(9,20)],end=8)}
FLASH={0x9c0a:('quarter',64),0x18e90:('status',8),0x18e98:('unlock',30),0x18eb6:('lock',14),0x18ec4:('erase',46),0x18ef2:('program',100)}


def need(value,why):
    if not value:raise ValueError(why)


def context(root,firmware=None):
    p=root/'apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py'
    if not p.is_file():p=root/'analysis/v4160-flash-image-integration-2026-10-22/ABI-review/review.py'
    need(SHA(p.read_bytes())==PRIOR_REVIEW,'sealed prior independent image checker');old=runpy.run_path(str(p));ctx=old['context'](root,firmware=firmware);ctx['prior']=old
    for n,h in CORE.items():need(SHA((root/'experiments/tsl9-v4160-flash-register-prefix/src'/n).read_bytes())==h,'new frozen readable native source '+n)
    return ctx


def frame_rows(body,va,ctx):
    rows=[];pc=0
    while pc<len(body):
        width=4 if int.from_bytes(body[pc:pc+2],'little')&3==3 else 2
        if va==0x9a42:decoded=ctx['idecode'](body[pc:pc+width],va+pc)
        else:
            r=ctx['decode'](body,0x8000+pc);op=r['op']
            if op in ('sw','sb','sh'):decoded=[op,r['rs2'],r['rs1'],r['immediate']]
            elif op=='mv':decoded=[op,r['rd'],r['rs1']]
            elif op in ('csrc','csrs'):decoded=[op,0,r['immediate'],r['rs1']]
            elif op=='jal':decoded=[op,r['rd'],r['target']-0x8000+va]
            elif op=='ret':decoded=['jalr',0,1,0]
            else:decoded=[op,r['rd'],r['rs1'],r['immediate']]
        rows.append(dict(address=va+pc,offset=pc,bytes=width,raw_hex=body[pc:pc+width].hex(),decoded=decoded));pc+=width
    need(pc==len(body),'whole frame body instruction coverage');return rows


def frame_contract(body,va,ctx):
    f=FRAMES[va];need(len(body)==f['bytes'],'frame function original extent');rows=frame_rows(body,va,ctx);original=ctx['original'][va-0x8000:va-0x8000+f['bytes']];source=frame_rows(original,va,ctx)
    need(rows[0]['decoded']==['addi',2,2,-f['frame']],'exact original SP decrement')
    stores=[r for r in rows if 2<=r['offset']<f['end']];need(len(stores)==len(f['original']) and all(r['bytes']==2 and r['decoded'][0]=='sw' and r['decoded'][2]==2 for r in stores),'actual two-byte stack-save-only frontier')
    order=[(r['decoded'][1],r['decoded'][3]) for r in stores];need(order in (f['original'],f['compiler']),'known complete disjoint register/slot set and permitted order');need(body[f['end']:]==original[f['end']:],'every byte after save frontier identical to original')
    frontier=[];old_slots=[];new_slots=[]
    for old,new in zip(source[1:1+len(stores)],stores):
        old_slots.append(old['decoded'][3]);new_slots.append(new['decoded'][3]);frontier.append(dict(next_PC=new['address']+2,original_saved_slots=list(old_slots),native_saved_slots=list(new_slots),original_instruction=old,native_instruction=new))
    return dict(address=va,bytes=len(body),frame_bytes=f['frame'],order='original' if order==f['original'] else 'compiler',stores=stores,frontier=frontier,convergence_PC=va+f['end'],all_other_GPR_values_unchanged_by_save_stores=True,byte_differences=[dict(address=va+i,original=a,native=b) for i,(a,b) in enumerate(zip(original,body)) if a!=b],same_complete_frame_after_convergence=True,partial_frame_fault_async_equivalence=body==original)


def mir_contract(folder,mode,unit,texts=None):
    before,after=texts if texts is not None else ((folder/mode/f'{unit}-before.mir').read_text(encoding='utf-8'),(folder/mode/f'{unit}-after.mir').read_text(encoding='utf-8'));address=0x9a42 if unit=='irq' else 0x9c0a;f=FRAMES[address]
    need('stackSize:       0' in before,'before frame lowering has no allocated total frame');need("callee-saved-register: '$x" not in before,'no actual callee-save register slots before prologepilog')
    expected=[f'SW killed $x{reg}, $x2, {slot} ::' for reg,slot in f['compiler']];positions=[after.index(x) for x in expected];need(positions==sorted(positions),'after prologepilog creates compiler-order saves')
    need(f'stackSize:       {f["frame"]}' in after and f'$x2 = frame-setup ADDI $x2, -{f["frame"]}' in after,'pass allocated exact frame')
    for reg,slot in f['compiler']:need(f"callee-saved-register: '$x{reg}'" in after,'new actual backend spill slot')
    calls=[l for l in before.splitlines() if 'INLINEASM &"jal ra,' in l];need(len(calls)==(6 if unit=='irq' else 5) and all(re.search(r'early-clobber \$x1(?:,|$)',l) for l in calls),'all actual narrow JAL primitives honestly declare RA clobber')
    first_body=after.index('body:             |');first_asm=after.index('INLINEASM',first_body);need(all(first_body<p<first_asm for p in positions),'all generated saves precede C inline primitives')
    return dict(mode=mode,unit=unit,before_sha256=SHA(before.encode()),after_sha256=SHA(after.encode()),compiler_order=[list(x) for x in f['compiler']],pass_generated_frame_and_saves=True,ordinary_C_universal_impossibility_proved=False)


def MIR_transcript_controls():
    folder=HERE/'build';records=[]
    changes=[('irq','wrong-frame-size','after','stackSize:       16','stackSize:       32'),('quarter','wrong-first-spill-register','after','SW killed $x1, $x2, 28','SW killed $x9, $x2, 28'),('irq','fictional-preexisting-backend-spill','before','stack:           []',"stack: [{callee-saved-register: '$x1'}]"),('quarter','omitted-JAL-RA-clobber','before','early-clobber $x1','early-clobber $x5')]
    for unit,name,side,a,b in changes:
        before=(folder/'c'/f'{unit}-before.mir').read_text();after=(folder/'c'/f'{unit}-after.mir').read_text();original=before if side=='before' else after;need(a in original,'actual MIR control substring');changed=original.replace(a,b,1)
        try:mir_contract(folder,'c',unit,(changed,after) if side=='before' else (before,changed))
        except ValueError as err:reason=str(err)
        else:raise ValueError('MIR transcript control accepted '+name)
        records.append(dict(name=name,unit=unit,side=side,original_sha256=SHA(original.encode()),mutated_sha256=SHA(changed.encode()),rejected=True,reason=reason,compiled=False))
    return records


def baseline_review(ctx):
    rows=[]
    for va in FRAMES:rows.append(frame_contract(ctx['references'][va]['code'],va,ctx))
    need([len(r['byte_differences']) for r in rows]==[8,6],'exact old IRQ8/quarter6 difference counts')
    diagnostic=json.loads((HERE/'frame-diagnostic.json').read_bytes());need(diagnostic['passed'] and len(diagnostic['commands'])==8,'actual eight fixed-profile diagnostics')
    mir=[]
    for c in diagnostic['commands']:
        for k in ('output','log'):need(SHA((HERE/c[k]).read_bytes())==c[k+'_sha256'],'actual diagnostic byte pin '+c[k])
    for mode in ('c','cpp'):
        for unit in ('irq','quarter'):mir.append(mir_contract(HERE/'build',mode,unit))
    return dict(frames=rows,MIR=mir,source_or_flag_sweep=False,conclusion='The fixed backend inserts the observed save order before the C body. No minimal sound ordinary-C order repair established; not a universal impossibility proof.',narrow_source_owned_scheduling_step_assessment='Potentially admissible only with actual compiled store permutation, exact register/slot/width/no-anchor/no-unwind gates, all other bytes and roles unchanged, explicit pre/post provenance and no compiler-emitted-order claim.')


def component_review(folder,ctx,strict=True,elf=None):
    ELF=ctx['ELF'];path=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf';e=elf or ELF(path);owners=ctx['prior']['alloc'](e);need(e.kind==2 and e.flags==1 and len(owners)==6 and not e.relocations,'six linked original-entry component allocations');need(not any(s['index']==0 and s['name'] for s in e.symbols),'no undefined component provider');functions=[]
    for va,(short,size) in FLASH.items():
        name='tsl9_flash_'+short+'_'+format(va,'x');symbols=[s for s in e.symbols if s['name']==name];need(len(symbols)==1,'one native function');s=symbols[0];need(s['value']==va and s['size']==size and s['info']==18,'exact original function entry/size/type');body=e.function_bytes(s);original=ctx['original'][va-0x8000:va-0x8000+size];need(e.sections[s['index']]['size']==size,'whole component owner extent');raw=ctx['flash']['raw_rows'](body,ctx['decode']);source=ctx['flash']['raw_rows'](original,ctx['decode']);need(len(raw)==len(source) and [x['offset'] for x in raw]==[x['offset'] for x in source],'all original instruction boundaries retained')
        exceptions=[];semantic=True
        for a,b in zip(source,raw):
            if a['raw_hex']==b['raw_hex']:continue
            keys=('op','rd','rs1','rs2','immediate','target','bytes','offset')
            same={k:a[k] for k in keys}=={k:b[k] for k in keys}
            commutative=short=='program' and a['offset'] in (0x28,0x30) and a['op']==b['op']=='add' and a['rd']==b['rd']==13 and a['rs1']==b['rs2'] and a['rs2']==b['rs1'] and a['bytes']==b['bytes']==4
            if same or commutative:exceptions.append(dict(offset=a['offset'],kind='commutative ADD source operand order' if commutative else 'same decoded instruction',original=a,native=b))
            else:semantic=False
        if short=='quarter':frame=frame_contract(body,va,ctx);semantic=True
        else:frame=None
        if strict:need(semantic,'normal source instruction/register contract '+short)
        if strict and short!='quarter':need(body==original,'final five leaf functions must be byte-identical to original, not just commutative equivalents')
        program_interiors=[]
        if short=='program':
            for offset in (0x10,0x1a,0x28,0x38,0x52):
                a=next(r for r in source if r['offset']==offset);b=next(r for r in raw if r['offset']==offset);need(a['op']==b['op'] and a['rd']==b['rd'] and a['immediate']==b['immediate'],'five known loop/copy role starts');program_interiors.append(dict(address=va+offset,original=a,native=b))
        functions.append(dict(name=name,address=va,bytes=size,code_sha256=SHA(body),source_code_sha256=SHA(original),original_byte_identity=body==original,normal_source_instruction_contract=semantic,semantic_encoding_exceptions=exceptions,frame=frame,program_interiors=program_interiors,rows=raw,source_rows=source))
    need(sum(s['size'] for s in owners.values())==262 and all(s['flags']==6 and s['type']==1 for s in owners.values()),'exact262 executable component bytes without extra data')
    incoming=[]
    for r in ctx['facts']['incoming']:
        if r['target'] in FLASH:need(any(s['value']==r['target'] for s in e.symbols if s['info']==18),'prior incoming target still original component entry')
        incoming.append(r)
    return dict(component_path=ctx['prior']['relative'](ctx['root'],path),component_sha256=SHA(e.raw),functions=functions,prior_twenty_incoming_contracts=incoming,known_prior_target_geometry_retained=True,new_whole_image_incoming_reverified=False,all_six_original_extents_retained=True,all_original_program_boundaries_retained=True,normal_static_instruction_semantics=all(f['normal_source_instruction_contract'] for f in functions),full_async_or_hardware_equivalence=False)


def object_IR_review(folder,ctx):
    ELF=ctx['ELF'];linked=ELF(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf');proof=[]
    for va,(short,size) in FLASH.items():
        name='tsl9_flash_'+short+'_'+format(va,'x');obj=ELF(folder/(short+'.o'));s=next(s for s in obj.symbols if s['name']==name);body=obj.function_bytes(s);need(obj.kind==1 and len(body)==size and s['size']==size and s['info']==18,'actual ET_REL function original extent');owners=ctx['prior']['alloc'](obj);need(len(owners)==1 and sum(x['size'] for x in owners.values())==size,'one executable object allocation')
        need(all(x['type']==1 and x['flags']==6 for x in owners.values()),'no added object data/unwind allocation');need(not any(any(k in x['name'] for k in ('frame','unwind','sframe','build-id')) for x in obj.sections),'no implicit unwind/build-id provider')
        ls=next(s for s in linked.symbols if s['name']==name);expected=linked.function_bytes(ls);patched=bytearray(body)
        if short=='quarter':
            need(len(obj.relocations)==5,'quarter five explicit calls');expected_calls={0x14:0x18e98,0x1c:0x18e90,0x22:0x18ec4,0x2a:0x18ef2,0x2e:0x18eb6}
            for r in obj.relocations:
                need(r['type']==17 and r['addend']==0 and r['offset'] in expected_calls,'quarter exact JAL relocation site');target=expected_calls[r['offset']];need(r['symbol']['name']=='tsl9_flash_'+FLASH[target][0]+'_'+format(target,'x'),'quarter original callee symbol')
                jump=ctx['prior']['direct_jump'](expected,r['offset'],va);need(jump['rd']==1 and jump['bytes']==4 and jump['target']==target,'actual linked helper target and link register');patched[r['offset']:r['offset']+4]=expected[r['offset']:r['offset']+4]
        else:need(not obj.relocations,'leaf has no relocation or hidden call')
        need(bytes(patched)==expected,'all actual object bytes match linked body after only five declared fixups')
        text=(folder/(short+'.ll')).read_text(encoding='utf-8');need('target triple = "riscv32-unknown-unknown-elf"' in text,'actual RV32 LLVM IR');loads=len(re.findall(r'\bload volatile i32\b',text));stores=len(re.findall(r'\bstore volatile i32\b',text));need((loads,stores)==ctx['flash']['IR_COUNTS'][short],'IR original volatile i32 static observation counts')
        need(not re.search(r'\bnaked\b',text),'ordinary compiler function, no naked body')
        proof.append(dict(name=name,object_sha256=SHA(obj.raw),IR_sha256=SHA(text.encode()),IR_volatile_i32_loads=loads,IR_volatile_i32_stores=stores,original_extent=size,object_to_link_only_declared_JAL_fixups=True))
    return proof


def actual_byte_controls(folder,ctx):
    e=ctx['ELF'](folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf');records=[]
    def pos(va):
        s=next(s for s in ctx['prior']['alloc'](e).values() if s['address']<=va<s['address']+s['size']);return s['offset']+va-s['address']
    def reject(label,offset,new):
        old=e.raw[offset:offset+len(new)];need(old!=new,'control changes actual bytes');b=bytearray(e.raw);b[offset:offset+len(new)]=new
        try:component_review(folder,ctx,elf=ctx['ELF'](ctx['prior']['BytesInput'](bytes(b))))
        except (ValueError,KeyError,IndexError,struct.error) as err:reason=str(err)
        else:raise ValueError('control accepted '+label)
        records.append(dict(name=label,file_offset=offset,before=old.hex(),after=new.hex(),mutated_sha256=SHA(bytes(b)),rejected=True,reason=reason))
    def xor(label,address,mask,width):
        p=pos(address);v=int.from_bytes(e.raw[p:p+width],'little');reject(label,p,(v^mask).to_bytes(width,'little'))
    xor('quarter-frame-decrement',0x9c0a,0x40,2)
    xor('quarter-save-slot',0x9c0c,0x200,2)
    xor('quarter-live-source-slot',0x9c14,0x200,2)
    xor('unlock-key1-immediate',0x18ea0,1<<20,4)
    xor('unlock-key2-immediate',0x18eaa,1<<20,4)
    xor('status-store-width',0x18e94,1<<12,4)
    xor('erase-alignment-mask',0x18ece,1<<20,4)
    xor('erase-poll-mask',0x18ee2,4,2)
    xor('program-initial-scratch-register',0x18ef6,1<<7,2)
    xor('program-copy-ADD-destination',0x18f1a,1<<7,4)
    xor('program-copy-ADD-source',0x18f22,1<<20,4)
    xor('program-destination-store-width',0x18f26,1<<12,4)
    xor('program-copy-stride',0x18f30,4,2)
    xor('program-loop-target',0x18f32,1<<8,4)
    p=ctx['prior']['symbol_offset'](e,lambda s:s['name']=='tsl9_flash_program_18ef2');reject('program-FUNC-size94',p+8,struct.pack('<I',94))
    p=ctx['prior']['symbol_offset'](e,lambda s:s['name']=='tsl9_flash_status_18e90');reject('missing-actual-provider',p+14,b'\0\0')
    s=e.sections[next(s for s in e.symbols if s['name']=='tsl9_flash_program_18ef2')['index']];shoff=struct.unpack_from('<I',e.raw,32)[0];reject('writable-code-allocation',shoff+s['index']*40+8,struct.pack('<I',7))
    s=e.byname['.comment'];reject('extra-comment-allocation',shoff+s['index']*40+8,struct.pack('<I',s['flags']|2))
    need(len(records)==18,'eighteen actual linked-ELF controls');return records


def inspect(root,folder,firmware=None,strict=True):
    ctx=context(root,firmware);probe=json.loads((folder/'probe.json').read_bytes());need({n:probe['source'][n] for n in CORE}==CORE,'actual native compiler source snapshot')
    baseline=baseline_review(ctx);component=component_review(folder,ctx,strict);objects=object_IR_review(folder,ctx);negatives=actual_byte_controls(folder,ctx) if strict else []
    names=['COMPONENT-ONLY-NOT-FIRMWARE.elf','probe.json','original-entry-component.ld']+[short+ext for short,size in FLASH.values() for ext in ('.o','.ll')]
    artifacts={n:dict(path=ctx['prior']['relative'](root,folder/n),bytes=(folder/n).stat().st_size,sha256=SHA((folder/n).read_bytes())) for n in names}
    producer=None
    if (folder/'verification.json').is_file():
        b=(folder/'verification.json').read_bytes();r=json.loads(b);need(r.get('passed') is True and r.get('schema')=='ID2966-flash-register-prefix-native-v1' and r.get('mode') in ('c','cpp') and r.get('source_sha256')==CORE,'actual formal producer receipt schema/source/pass');need(r.get('runner_sha256')=='617757c0bfe4612ca87337c7a84c98d68551876a2f5208bbb00df85bb61db09a','explicit frozen native producer CLI');producer=dict(path=ctx['prior']['relative'](root,folder/'verification.json'),sha256=SHA(b),schema=r.get('schema'),runner_sha256=r.get('runner_sha256'),mode=r.get('mode'))
    fw=firmware or root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    return dict(schema='TSL9-register-prefix-independent-ABI-review-v1',passed=strict and component['normal_static_instruction_semantics'],provisional=not strict,baseline=baseline,component=component,object_IR=objects,actual_ELF_byte_controls=negatives,MIR_transcript_controls=MIR_transcript_controls(),artifacts=artifacts,producer=producer,native_sources=CORE,firmware_path=ctx['prior']['relative'](root,fw),reviewer_sha256=SHA(Path(__file__).read_bytes()),target_execution=False,ISA_emulation=False,network=False,full_image_integrated=False,hardware_or_OTA_verified=False)


def replay(root,path,firmware=None):
    r=json.loads(path.read_bytes());need(r['schema']=='TSL9-register-prefix-independent-ABI-review-v1' and r['passed'] and not r['provisional'],'final independent review receipt')
    need(r['reviewer_sha256']==SHA(Path(__file__).read_bytes()),'independent reviewer source pin');ctx=context(root,firmware);input_path=ctx['prior']['input_path']
    for n,a in r['artifacts'].items():
        p=input_path(root,a['path']);need(p.stat().st_size==a['bytes'] and SHA(p.read_bytes())==a['sha256'],'actual retained input pin '+n)
    if r['producer']:need(SHA(input_path(root,r['producer']['path']).read_bytes())==r['producer']['sha256'],'formal producer receipt pin')
    fw=firmware or input_path(root,r['firmware_path']);folder=input_path(root,r['artifacts']['probe.json']['path']).parent;new=inspect(root,folder,fw)
    need(new==r,'fresh source/normal-register/prefix/MIR/negative-control replay')
    return dict(passed=True,receipt=ctx['prior']['relative'](root,path),actual_ELF_byte_controls=18,uncompiled_MIR_transcript_controls=4,five_leaves_original_byte_identity=True,frame_order_restored=False,new_whole_image_incoming_reverified=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,default=ROOT);p.add_argument('--component-folder',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--report',type=Path);p.add_argument('--replay',type=Path);p.add_argument('--provisional',action='store_true');a=p.parse_args();root=a.project_root.resolve()
    if a.replay:print(json.dumps(replay(root,a.replay.resolve(),a.firmware),sort_keys=True));return
    need(a.component_folder is not None and a.report is not None,'fresh review needs --component-folder and --report');result=inspect(root,a.component_folder.resolve(),a.firmware,not a.provisional)
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_bytes((json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode());print(json.dumps(dict(passed=result['passed'],report=str(a.report),sha256=SHA(a.report.read_bytes()),component_normal_contract=result['component']['normal_static_instruction_semantics'])))


if __name__=='__main__':main()
