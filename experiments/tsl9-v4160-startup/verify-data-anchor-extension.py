"""Plan-pinned native extension audit; host tools only, no RV32 execution."""
from pathlib import Path
import argparse,collections,hashlib,json,re,runpy,struct,subprocess,sys,uuid

ROOT=Path(__file__).resolve().parent
HOST=runpy.run_path(str(ROOT/'verify.py'))
FLOW=runpy.run_path(str(ROOT/'verify-dependencies.py'))
ELF=HOST['ELF'];need=HOST['need'];BIN=HOST['BIN'];direct_target=FLOW['direct_target']
sha=lambda b:hashlib.sha256(b).hexdigest()

"""Typed data-anchor gates; raw finite-domain/known-ingress recomputation, host only."""
def anchor_sx(x,n):return x-(1<<n) if x&(1<<(n-1)) else x

def anchor_flow(raw,pc):
    h=struct.unpack_from('<H',raw,pc-0x8000)[0];width=4 if h&3==3 else 2;w=int.from_bytes(raw[pc-0x8000:pc-0x8000+width],'little');d=direct_target(pc,width,w)
    if d:
        typ,target=d
        if typ in (16,44):return width,'conditional_branch',[target,pc+width],None
        link=((w>>7)&31) if width==4 else (1 if h>>13==1 else 0)
        if link:return width,'direct_call',[pc+width],dict(target=target,link_register=link,return_address=pc+width)
        return width,'direct_jump',[target],None
    if width==2 and h&0xe07f==0x8002:
        r=h>>7&31
        if h>>12&1:return width,'indirect_call',[pc+width],dict(register=r,link_register=1,return_address=pc+width)
        return width,('return' if r==1 else 'indirect_tail'),[],None
    if width==4 and w&127==0x67:
        rd=w>>7&31;rs=w>>15&31
        if rd:return width,'indirect_call',[pc+width],dict(register=rs,link_register=rd,return_address=pc+width)
        return width,('return' if rs==1 and anchor_sx(w>>20,12)==0 else 'indirect_tail'),[],None
    if w==0x30200073:return width,'mret',[],None
    return width,'linear',[pc+width],None

def anchor_consumer_core(raw):
    get=lambda p,n:raw[p-0x8000:p-0x8000+n];word=lambda p:struct.unpack_from('<I',raw,p-0x8000)[0]
    z=word(0xf9f2);need(z&0x707f==0x4003 and z>>7&31==14 and z>>15&31==15 and anchor_sx(z>>20,12)==0,'Anchor input is actual unsigned byte load')
    z=struct.unpack_from('<H',raw,0xf9f6-0x8000)[0];need(z&3==1 and z>>13==4 and z>>10&3==2 and 8+(z>>7&7)==14,'Actual ANDI register')
    mask=anchor_sx((z>>12&1)<<5|(z>>2&31),6);need(mask==7,'Actual raw mask7, no index8')
    z=struct.unpack_from('<H',raw,0xf9f8-0x8000)[0];need(z>>13==6 and 8+(z>>7&7)==14 and anchor_flow(raw,0xf9f8)[:3]==(2,'conditional_branch',[0xfa22,0xf9fa]),'Actual zero exit excludes index0')
    hi,lo=struct.unpack_from('<II',raw,0xf9fa-0x8000);need(hi&127==0x17 and hi>>7&31==13 and lo&0x707f==0x13 and lo>>7&31==lo>>15&31==13,'Original base AUIPC own ADDI')
    base=(0xf9fa+anchor_sx(hi&0xfffff000,32)+anchor_sx(lo>>20,12))&0xffffffff;need(base==0x1ab58,'Exact original anchor base')
    need(get(0xfa02,2).hex()=='3697','Unscaled C.ADD a4,a3')
    z=word(0xfa04);need(z&0x707f==0x4003 and z>>7&31==15 and z>>15&31==14 and anchor_sx(z>>20,12)==0,'Actual LBU width1 at base plus index')
    expected={0xf9ec:'93874105',0xf9f0:'9c43',0xf9f2:'03c70700',0xf9f6:'1d8b',0xf9f8:'0dc7',0xf9fa:'97b60000',0xf9fe:'9386e615',0xfa02:'3697',0xfa04:'83470700'}
    need(all(get(pc,len(hx)//2).hex()==hx for pc,hx in expected.items()),'Critical raw operands exact')
    nodes={};pending=[0xf9ec]
    while pending:
        pc=pending.pop()
        if pc in nodes:continue
        need(0xf9ec<=pc<0xfa24,'Local bounded consumer CFG');width,kind,edges,call=anchor_flow(raw,pc);nodes[pc]=dict(PC=pc,bytes=width,raw_hex=get(pc,width).hex(),flow=kind,successors=edges,call=call)
        if kind=='direct_jump':need(edges==[0x13d48],'Only captured local tail')
        else:pending.extend(edges)
    pred={pc:set()for pc in nodes}
    for pc,n in nodes.items():
        for target in n['successors']:
            if target in pred:pred[target].add(pc)
    dom={pc:({0xf9ec}if pc==0xf9ec else set(nodes))for pc in nodes};changed=True
    while changed:
        changed=False
        for pc in nodes:
            if pc==0xf9ec:continue
            need(bool(pred[pc]),'Actual consumer node reachable');d={pc}|set.intersection(*(dom[p]for p in pred[pc]))
            if d!=dom[pc]:dom[pc]=d;changed=True
    need({0xf9f2,0xf9f6,0xf9f8,0xf9fa,0xf9fe,0xfa02}<=dom[0xfa04],'Mask/guard/base dominate actual read')
    domain=sorted({x&mask for x in range(256)if x&mask});need(domain==list(range(1,8)),'Derived byte index domain1..7')
    return dict(base=base,domain=domain,CFG=[nodes[p]for p in sorted(nodes)],dominators=sorted(dom[0xfa04]),nodes=set(nodes))

def anchor_norm(elf,row,allocations,addresses):
    sym=elf.symbols[row['symbol_index']]
    if sym['index']==0:base=addresses[sym['name']] if sym['name'] else 0
    elif sym['index']==0xfff1:base=sym['value']
    else:base=allocations[elf.sections[sym['index']]['name']]['originalVA']+sym['value']
    return (base+row['addend'])&0xffffffff

def anchor_check_known_ingress(rows,nodes):
    unsafe={p for p in nodes if 0xf9f8<=p<=0xfa04}
    need(not any(r['target']in unsafe for r in rows),'No known external guard bypass')

def anchor_validate_proof(proof,v,raw,baseline,base_obj,base_witness,new_sections):
    need(proof['schema']=='ID2966-existing-data-anchor-1AB58-bounded-consumer-contract-v1','Explicit typed data-anchor consumer schema')
    need(proof['source']['sha256']==sha(raw) and not proof['blocking_findings'],'Proof source identity and no blocking findings')
    need(v['name']=='__tsl9v4160_address_1ab58' and v['role']=='existing_RO_section_end_address_anchor_no_storage_or_original_object_claim','Narrow reviewed anchor identity/role')
    need((v['section'],v['originalVA'],v['offset'],v['elf_type'],v['size'])==('.rodata.tsl9v4160.readonly_view_1ab50',0x1ab58,8,0,0),'Exact RO section-end NOTYPE0 anchor')
    alloc=baseline['allocations'];need(len(alloc)==549 and len(base_obj.relocations)==6302 and len(baseline['modes']['c']['undefined_symbols'])==61,'Current reviewed baseline scope')
    core=anchor_consumer_core(raw);local=proof['local_consumer']
    need((local['entry'],local['end_exclusive'],local['mask_PC'],local['mask'],local['zero_guard_PC'],local['zero_exit'],local['base_materialization_PC'],local['ADD_PC'],local['read_PC'],local['read_width'],local['scale'])==(0xf9ec,0xfa24,0xf9f6,7,0xf9f8,0xfa22,0xf9fa,0xfa02,0xfa04,1,1),'Proof critical raw fields')
    need(local['index_domain']==core['domain'] and local['effective_addresses']==[0x1ab58+i for i in core['domain']] and local['CFG']==core['CFG'] and local['read_dominators']==core['dominators'],'Recomputed CFG/domain/dominators, not passed boolean')
    need(anchor_symbol_record(base_obj,v['name'])['other']==0,'Original canonical NOTYPE visibility unchanged')
    old=alloc[v['section']];section=base_obj.byname[v['section']];carrier=base_obj.symbol['__tsl9v4160_readonly_view_1ab50'];view=base_obj.symbol['__tsl9v4160_address_1ab50'];canonical=base_obj.symbol[v['name']]
    need((old['originalVA'],old['bytes'],section['type'],section['flags'],section['size'])==(0x1ab50,8,1,2,8),'Actual old RO8 carrier')
    need(section['data']==raw[0x1ab50-0x8000:0x1ab58-0x8000] and sha(section['data'])==old['sha256']==proof['old_carrier']['sha256'],'Old RO8 source bytes exact')
    need((carrier['index'],carrier['bind'],carrier['type'],carrier['size'],carrier['value'])==(section['index'],1,1,8,0) and (view['index'],view['type'],view['size'],view['value'])==(section['index'],0,0,0),'Original OBJECT8 and NOTYPE view remain real')
    need((canonical['index'],canonical['bind'],canonical['type'],canonical['size'],canonical['value'])==(0,1,0,0,0) and base_witness.symbol[v['name']]['value']==0x1ab58,'Only original true UND NOTYPE is resolved')
    a=proof['data_anchor_contract'];need((a['address_symbol'],a['originalVA'],a['section'],a['section_originalVA'],a['section_offset'],a['expected_symbol_type'],a['expected_binding'],a['expected_size'],a['own_storage_bytes'])==(v['name'],0x1ab58,v['section'],0x1ab50,8,0,1,0,0),'Proof anchor representation fields')
    need(a['known_read_offsets']==core['domain'] and a['forbidden_offsets']==[0,8] and a['read_width']==1 and not a['byte0_storage_proved'] and not a['original_C_same_object_proved'],'No byte0 or original same-object inference')
    frag=proof['observed_fragment'];need((frag['originalVA'],frag['end_exclusive'],frag['bytes'],frag['ELF_type_required'],frag['flags_required'],frag['OBJECT_size_required'])==(0x1ab59,0x1ab60,7,1,2,7),'Only observed7B fragment')
    need(frag['raw_hex']==raw[0x1ab59-0x8000:0x1ab60-0x8000].hex() and frag['sha256']==sha(bytes.fromhex(frag['raw_hex'])) and a['required_observed_fragment']==frag,'Actual observed7B original bytes')
    need(v['fragment_section']in new_sections,'Anchor has actual new fragment carrier');new=new_sections[v['fragment_section']]
    need((new['originalVA'],new['bytes'],new['kind'],new['sha256'])==(0x1ab59,7,'RO',frag['sha256']),'Fragment exact position/size/hash; no byte0')
    need(not any(s['kind']!='RAM' and s['originalVA']<=0x1ab58<s['originalVA']+s['bytes']for s in list(alloc.values())+list(new_sections.values())),'Byte0 gap has no section allocation')
    addresses={n:base_witness.symbol[n]['value']for n in baseline['modes']['c']['undefined_symbols']};norm=lambda r:anchor_norm(base_obj,r,alloc,addresses)
    canonical_refs=[r for r in base_obj.relocations if r['target']==v['name']];need(len(canonical_refs)==1,'All actual canonical references accounted for');hi=canonical_refs[0]
    need((hi['type'],hi['addend'],alloc[hi['section']]['originalVA']+hi['offset'])==(23,0,0xf9fa),'Actual consumer HI23 retained')
    lows=[r for r in base_obj.relocations if r['section']==hi['section']and r['offset']==hi['offset']+4];need(len(lows)==1 and lows[0]['type']==24 and lows[0]['addend']==0,'Actual own LOW24 retained');low=lows[0];anchor=base_obj.symbols[low['symbol_index']]
    need(anchor['index']==base_obj.byname[hi['section']]['index'] and anchor['value']==hi['offset'] and norm(hi)==0x1ab58 and norm(low)==0xf9fa,'Actual own-HIGH anchor semantics')
    refs=proof['actual_canonical_references'];need(len(refs)==1 and all(refs[0]['HI'][k]==hi[k] and refs[0]['LOW'][k]==low[k]for k in ('section','offset','type','target','addend')) and refs[0]['raw_pair_hex']==raw[0xf9fa-0x8000:0xfa02-0x8000].hex(),'Proof actual canonical HI/LOW ledger complete')
    numeric=[r for r in base_obj.relocations if norm(r)==0x1ab58];listed=proof['all_actual_numeric_base_references'];need(len(numeric)==len(listed)==1 and all(numeric[0][k]==listed[0][k]for k in ('section','offset','type','target','addend')),'All numeric-base references complete, no missing RELA')
    control_in=[];noncontrol_in=[]
    for r in base_obj.relocations:
        target=norm(r);pc=alloc[r['section']]['originalVA']+r['offset']
        if 0xf9ec<=target<0xfa24:
            row=dict(sourcePC=pc,target=target,type=r['type'])
            if r['type']in (16,17,44,45):
                width=4 if struct.unpack_from('<H',raw,pc-0x8000)[0]&3==3 else 2;bits=int.from_bytes(raw[pc-0x8000:pc-0x8000+width],'little');need(direct_target(pc,width,bits)==(r['type'],target),'Actual incoming control RELA agrees with original raw target');control_in.append(row)
            else:noncontrol_in.append(row)
    outside_control=[r for r in control_in if not 0xf9ec<=r['sourcePC']<0xfa24];need(outside_control==[dict(sourcePC=0xd022,target=0xf9ec,type=17)],'Actual known control ingress complete and guarded')
    need(all(r['type']==24 and r['target']==0xf9fa for r in noncontrol_in),'Only own-HI anchors are non-control references into consumer')
    anchor_check_known_ingress(outside_control,core['nodes'])
    direct=[];fall=[]
    for name,s in alloc.items():
        if s['kind']!='code':continue
        need(base_obj.byname[name]['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'Actual captured old code matches source for ingress scan');pc=s['originalVA'];end=pc+s['bytes']
        while pc<end:
            width,kind,edges,call=anchor_flow(raw,pc);targets=(edges if kind=='direct_jump'else edges[:1]if kind=='conditional_branch'else[])+([call['target']]if call and 'target'in call else[])
            for target in targets:
                if 0xf9ec<=target<0xfa24 and not 0xf9ec<=pc<0xfa24:direct.append(dict(sourcePC=pc,target=target,raw_hex=raw[pc-0x8000:pc-0x8000+width].hex(),flow=kind))
            if kind=='linear'and pc+width in core['nodes']and not 0xf9ec<=pc<0xfa24:fall.append(dict(sourcePC=pc,target=pc+width))
            pc+=width
        need(pc==end,'Captured ingress code has complete instructions')
    ingress=proof['current_known_ingress'];need(direct==ingress['raw_direct_instruction_scan_external_edges'] and fall==ingress['external_linear_fallthrough'] and len(direct)==1 and direct[0]['sourcePC']==0xd022 and direct[0]['target']==0xf9ec and not fall,'Recomputed all captured direct/linear ingress')
    anchor_check_known_ingress(direct,core['nodes'])
    plus=[r for r in base_obj.relocations if r['type']==35];minus=[r for r in base_obj.relocations if r['type']==39];need(len(plus)==len(minus)==len(ingress['relative_entries'])==534,'Every known relative32 entry retained')
    actual_relative=[]
    for r in plus:
        subs=[q for q in minus if q['section']==r['section']and q['offset']==r['offset']];need(len(subs)==1,'One actual relative32 SUB per ADD');base=norm(subs[0]);target=norm(r);word=struct.unpack_from('<I',raw,alloc[r['section']]['originalVA']+r['offset']-0x8000)[0];need((target-base)&0xffffffff==word,'Actual relative32 source delta');actual_relative.append(dict(section=r['section'],offset=r['offset'],raw_u32=word,raw_pre_JR_address=target,cleared_target=target&0xfffffffe,base=base,guard_bypass=False))
    key=lambda x:(x['section'],x['offset']);need(sorted(actual_relative,key=key)==sorted(ingress['relative_entries'],key=key),'All534 actual relative entry source/target ledger exact');anchor_check_known_ingress([dict(target=x['cleared_target'])for x in actual_relative],core['nodes'])
    selfedges=[dict(source=0x8556,target=0x855a+4*i,constraint='u32(a2)=='+str(15-i))for i in range(16)]+[dict(source=0x85b6,target=0x855a+4*i,constraint='u32(a5)=='+str(i+1))for i in range(15)]
    # Use numeric edge set after validating self-HIGH/JALR raw operands; proof carries original constraint text.
    need(raw[0x8550-0x8000:0x8554-0x8000].hex()=='97020000' and raw[0x85ae-0x8000:0x85b2-0x8000].hex()=='97020000','Known self-PC HIGH anchors original')
    need(ingress['self_PC_proof']['sha256']=='652d268afb4de1acb5e9e6a43f60602755087eceebddf36f77471d0e7a7947c9','Previously sealed finite dispatch source certificate')
    need(raw[0x8556-0x8000:0x855a-0x8000].hex()=='6780a600' and raw[0x85b6-0x8000:0x85ba-0x8000].hex()=='e78086fa' and raw[0x8596-0x8000:0x8598-0x8000].hex()=='8280','Actual known self-PC JR/JALR/RET operands')
    computed={(0x8556,0x855a+4*i)for i in range(16)}|{(0x85b6,0x855a+4*i)for i in range(15)}|{(0x8596,0x85ba)}
    need({(x['source'],x['target'])for x in ingress['self_PC_computed_edges']}==computed and len(ingress['self_PC_computed_edges'])==32 and ingress['self_PC_computed_source_sites']==[0x8556,0x85b6],'All known finite self-PC edges complete');anchor_check_known_ingress([dict(target=t)for _,t in computed],core['nodes']);need(not ingress['known_guard_bypass'],'No reported known bypass')
    expected_kills={0x13d48:'4111',0x13d4a:'06c6',0x135e6:'4167',0x135e8:'9796ff1f',0xd026:'2244',0xd028:'b240',0xd02a:'4101',0x13c4e:'4167',0x13c50:'9796ff1f'}
    need(all(raw[p-0x8000:p-0x8000+len(hx)//2].hex()==hx for p,hx in expected_kills.items()),'Live pointer sink register kills before dereference, no ABI clobber assumption')
    need(anchor_flow(raw,0xfa1e)[2]==[0x13d48] and anchor_flow(raw,0x13d4c)[3]['target']==0x135e6 and anchor_flow(raw,0xd022)[3]['target']==0xf9ec and anchor_flow(raw,0xd02c)[2]==[0x13c4e],'Known tail/call/return continuation sink chain')
    sinks=proof['pointer_liveness_sinks'];need((sinks['tail_from_consumer']['sourcePC'],sinks['tail_from_consumer']['target'],sinks['tail_from_consumer']['first_direct_call_PC'],sinks['tail_from_consumer']['first_direct_call_target'],sinks['tail_from_consumer']['callee_kills_effective_pointer_PC'],sinks['tail_from_consumer']['callee_kills_base_PC'])==(0xfa1e,0x13d48,0x13d4c,0x135e6,0x135e6,0x135e8),'Tail sink fields bind original kills')
    need((sinks['return_from_consumer']['return_PC'],sinks['return_from_consumer']['only_known_direct_caller_PC'],sinks['return_from_consumer']['tail_PC'],sinks['return_from_consumer']['tail_target'],sinks['return_from_consumer']['kills_effective_pointer_PC'],sinks['return_from_consumer']['kills_base_PC'])==(0xfa22,0xd022,0xd02c,0x13c4e,0x13c4e,0x13c50),'Return sink fields bind original kills')
    need(not sinks['known_unbounded_callee_receives_live_base_without_prior_kill'] and not sinks['arbitrary_dynamic_callers_or_register_aliases_excluded'],'Current known bounded sinks only, arbitrary lifetime remains unknown')
    return dict(raw_domain=core['domain'],read_width=1,canonical_HI_refs=1,own_LOW_refs=1,actual_relative_entries=534,computed_edges=32,unknown_dynamic_callers_excluded=False)

def anchor_check_fragment(elf,plan):
    if not plan.get('existing_data_anchors'):return
    need(len(plan['sections'])==len(plan['defined_symbols'])==1 and not plan['relocations'] and not plan['expected_undefined_symbols'],'Data anchor module has only one dependency-free observed carrier')
    s=plan['sections'][0];need((s['originalVA'],s['bytes'],s['kind'],s['alignment'])==(0x1ab59,7,'RO',1),'Observed fragment excludes base byte0 and offset8')
    actual=elf.byname[s['name']];need((actual['type'],actual['flags'],actual['size'],actual['alignment'])==(1,2,7,1),'Actual observed RO7 type/flags/size/alignment')
    symbol=plan['defined_symbols'][0];need((symbol['originalVA'],symbol['elf_type'],symbol['size'])==(0x1ab59,1,7),'Observed carrier is actual OBJECT7 only')
    need(elf.symbol[symbol['name']]['bind']==1 and anchor_symbol_record(elf,symbol['name'])['other']==0,'Observed OBJECT default exported visibility')

def anchor_symbol_record(elf,name):
    found=[]
    for table in elf.sections:
        if table['type']!=2:continue
        strings=elf.sections[table['link']]['data']
        for offset in range(0,table['size'],16):
            start=struct.unpack_from('<I',table['data'],offset)[0]
            if strings[start:strings.index(0,start)].decode('ascii')==name:found.append(table['offset']+offset)
    need(len(found)==1,'Unique actual raw SYMTAB identity '+name);at=found[0]
    return dict(file_offset=at,other=elf.raw[at+13],info=elf.raw[at+12],value=struct.unpack_from('<I',elf.raw,at+4)[0],size=struct.unpack_from('<I',elf.raw,at+8)[0],shndx=struct.unpack_from('<H',elf.raw,at+14)[0])

def anchor_check_fields(elf,anchors,allocations,linked=False):
    for name,v in anchors.items():
        symbol=elf.symbol[name];section=elf.byname[v['section']];old=allocations[v['section']]
        need(anchor_symbol_record(elf,name)['other']==0,'Actual data-anchor default visibility st_other0')
        need(symbol['index']==section['index'] and symbol['bind']==1 and symbol['type']==0 and symbol['size']==0,'Actual data anchor is GLOBAL NOTYPE0 in exact old RO, never ABS/FUNC/OBJECT')
        need(section['type']==1 and section['flags']==2 and section['size']==old['bytes']==8,'Anchor does not change or replace old RO8 storage')
        need(symbol['value']==(v['originalVA']if linked else v['offset']) and v['offset']==8,'Exact section-end data anchor value')

        frag=elf.byname[v['fragment_section']];storage=allocations[v['fragment_section']]
        need((frag['type'],frag['flags'],frag['size'],frag['alignment'])==(1,2,7,1) and sha(frag['data'])==storage['sha256'],'Fresh actual observed fragment remains exact RO7')
        if linked:
            need(frag['address']==storage['originalVA']==0x1ab59,'Fresh observed fragment exact original position, never base byte0')
            need(not any(s['flags']&2 and s['address']<=0x1ab58<s['address']+s['size']for s in elf.sections),'No actual witness section covers base byte0; LOAD padding is separate')
        carrier=elf.symbol['__tsl9v4160_readonly_view_1ab50'];view=elf.symbol['__tsl9v4160_address_1ab50'];base=old['originalVA']if linked else 0
        need((carrier['index'],carrier['bind'],carrier['type'],carrier['size'],carrier['value'])==(section['index'],1,1,8,base),'Fresh actual old OBJECT8 unchanged')
        need((view['index'],view['bind'],view['type'],view['size'],view['value'])==(section['index'],1,0,0,base),'Fresh actual old NOTYPE view unchanged')
        need(anchor_symbol_record(elf,carrier['name'])['other']==anchor_symbol_record(elf,view['name'])['other']==0,'Fresh old carrier visibility unchanged')

def anchor_actual_countercases(elf,anchors,allocations,folder,linked=False):
    out=[]
    for name,v in anchors.items():
        record=anchor_symbol_record(elf,name);at=record['file_offset'];wrong=next(n for n,s in allocations.items()if s['kind']=='RO'and n!=v['section']and s['originalVA']<v['originalVA']);wrong_section=elf.byname[wrong]['index']
        cases=['ABS_same_numeric','wrong_section_same_numeric','offset7','offset9','TYPE_FUNC','TYPE_OBJECT','nonzero_size','wrong_visibility'] if not linked else ['wrong_section_same_numeric','wrong_visibility']
        for tag in cases:
            bad=bytearray(elf.raw)
            if tag=='ABS_same_numeric':struct.pack_into('<I',bad,at+4,v['originalVA']);struct.pack_into('<H',bad,at+14,0xfff1)
            elif tag=='wrong_section_same_numeric':struct.pack_into('<I',bad,at+4,v['originalVA']if linked else v['originalVA']-allocations[wrong]['originalVA']);struct.pack_into('<H',bad,at+14,wrong_section)
            elif tag.startswith('offset'):struct.pack_into('<I',bad,at+4,(v['originalVA']-8 if linked else 0)+int(tag[6:]))
            elif tag.startswith('TYPE_'):bad[at+12]=(bad[at+12]&0xf0)|(2 if tag=='TYPE_FUNC'else 1)
            elif tag=='nonzero_size':struct.pack_into('<I',bad,at+8,1)
            else:bad[at+13]=2
            path=folder/('COUNTERCASE-data-anchor-'+('witness-'if linked else'')+tag+'.elf');path.write_bytes(bad);fixture=ELF(path);rejected=False;reason=''
            try:anchor_check_fields(fixture,anchors,allocations,linked)
            except AssertionError as error:rejected=True;reason=str(error)
            need(rejected,'Same typed anchor gate rejects actual '+tag)
            out.append(dict(kind=tag,path=str(path),sha256=sha(path.read_bytes()),linked=linked,rejected=True,reason=reason,original_symbol=elf.symbol[name],mutated_symbol=fixture.symbol[name],original_raw_symbol=record,mutated_raw_symbol=anchor_symbol_record(fixture,name)))
    return out

def anchor_check_inherited_relative(elf,allocations,normalized,count):
    rows=[r for r in elf.relocations if r['type']in (35,39)];need(len(rows)==2*count,'All inherited relative32 records retained')
    for r in rows:
        sym=elf.symbols[r['symbol_index']];need(sym['index']not in (0,0xfff1),'Inherited relative operand still has actual section provider')
        section=elf.sections[sym['index']]['name'];storage=allocations[section]
        if r['type']==35:need(storage['kind']=='code'and 0<=sym['value']+r['addend']<storage['bytes'],'Inherited ADD target stays in real code')
        else:need(section==r['section']and storage['kind']=='RO'and normalized(elf,r)==storage['originalVA'],'Inherited SUB stays at real owning table base')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--spec',type=Path,default=ROOT/'evidence/data-anchor-integration.json')
    ap.add_argument('--firmware',type=Path,default=ROOT.parents[1]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
    ap.add_argument('--baseline-receipt',type=Path)
    args=ap.parse_args();spec_path=args.spec.resolve();spec=json.loads(spec_path.read_text(encoding='utf-8'))
    need(spec['schema']=='ID2966-native-data-anchor-extension-spec-v1','Explicit reviewed extension spec')
    need(sha((ROOT/'verify-table-extension.py').read_bytes())=='20241839b9a419514087efa2d41d3786190d6b5b9356a92570bfe85c0567aabd','Frozen parent verifier retained unchanged')
    def local(name):
        p=(ROOT/name).resolve();need(p.is_relative_to(ROOT),'All source/tool entries stay in this project');return p
    raw=args.firmware.read_bytes();need(len(raw)==76800 and sha(raw)==spec['firmware_sha256']=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Pinned ID2966, no cross-version filling')
    work=ROOT/'build'/('data-anchor-extension-'+uuid.uuid4().hex);work.mkdir(parents=True,exist_ok=False)
    cc=BIN/'clang.exe';ld=BIN/'ld.lld.exe'
    def run(argv,folder,label,success=True):
        p=subprocess.run([str(x) for x in argv],cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90,check=False)
        (folder/(label+'.log')).write_bytes(p.stdout);need((p.returncode==0)==success,'Tool result '+label)
        return dict(argv=[str(x) for x in argv],exit=p.returncode,log_sha256=sha(p.stdout)),p.stdout
    if args.baseline_receipt:baseline_path=args.baseline_receipt.resolve()
    else:
        entry=local(spec['baseline_entry']);need(entry.suffix=='.py','Baseline is the declared local host verifier')
        _,output=run([sys.executable,'-X','utf8','-B',entry,'--spec',local(spec['baseline_spec']),'--firmware',args.firmware.resolve()],work,'baseline')
        baseline_path=Path(json.loads(output.decode('utf-8').strip().splitlines()[-1])['receipt'])
    baseline=json.loads(baseline_path.read_text(encoding='utf-8'))
    need(baseline['passed'] and baseline['schema']==spec['baseline_schema'] and baseline['firmware_sha256']==sha(raw),'Reviewed baseline/source identity')
    def check_chain(path,seen):
        path=path.resolve();need(path.is_relative_to(ROOT/'build') and path not in seen,'Retained receipt stays in this build tree, no cycle')
        seen.add(path);row=json.loads(path.read_text(encoding='utf-8'))
        need(row['passed'] and row['firmware_sha256']==sha(raw),'Every retained stage binds source')
        need(all(sha(local(n).read_bytes())==h for n,h in row['source_files'].items()),'Transitive baseline source drift')
        need(all(sha(Path(n).read_bytes())==h for n,h in row['tools'].items()),'Transitive tool drift')
        if 'baseline_receipt' in row:
            prior=Path(row['baseline_receipt']);need(sha(prior.read_bytes())==row['baseline_receipt_sha256'],'Retained baseline digest')
            check_chain(prior,seen)
    check_chain(baseline_path,set())
    sources=[Path(__file__).resolve(),ROOT/'verify-table-extension.py',ROOT/'verify.py',ROOT/'verify-dependencies.py',spec_path]
    sources.append(local(spec['baseline_spec']))
    need(spec['baseline_entry']=='verify-table-extension.py','Fresh full baseline uses unchanged frozen parent')
    modules=[];new_sections={};new_symbols={};unknown={};code_views={};cfg_docs={};data_anchors={};anchor_proofs={}
    for item in spec['modules']:
        plan_path=local(item['plan']);need(sha(plan_path.read_bytes())==item['plan_sha256'],'Pinned independently reviewed module plan')
        plan=json.loads(plan_path.read_text(encoding='utf-8'));need(plan['source_firmware_sha256']==sha(raw),'Module source digest')
        cfg_path=local(item['cfg_evidence'])
        need(sha(cfg_path.read_bytes())==item['cfg_sha256']==plan['CFG_review_sha256'],'Pinned independent local-CFG evidence')
        source=local(item['source']);header=local(item['header'])
        need(sha(source.read_bytes())==item['source_sha256'] and sha(header.read_bytes())==item['header_sha256'],'Pinned new source/header')
        sources.extend([plan_path,source,header,cfg_path]);modules.append((item,plan))
        cfg_docs[item['name']]=(item,json.loads(cfg_path.read_text(encoding='utf-8')))
        old_storage={**baseline['allocations'],**new_sections}
        for v in plan.get('existing_code_views',[]):
            need(v['name'] not in code_views and v['section'] in old_storage,'Unique view of already captured storage')
            storage=old_storage[v['section']]
            need(storage['kind']=='code' and v['elf_type']==0 and v['size']==0 and 0<=v['offset']<storage['bytes'],'Only NOTYPE0 view, never an implementation')
            need(v['originalVA']==storage['originalVA']+v['offset'],'Exact captured code address')
            owner,proof=cfg_docs[v['boundary_cfg_module']]
            need(owner['cfg_sha256']==v['boundary_cfg_sha256'] and proof['passed'],'Pinned old CFG instruction-boundary evidence')
            graph=next(g for g in proof['graphs'] if g['entry']==v['boundary_root_originalVA'])
            instruction=next(i for i in graph['instructions'] if i['va']==v['originalVA'])
            bits=bytes.fromhex(instruction['raw_hex'])
            need(instruction['raw_hex']==v['boundary_raw_hex'] and len(bits) in (2,4) and v['offset']+len(bits)<=storage['bytes'],'Actual old instruction start, not alignment alone')
            need(raw[v['originalVA']-0x8000:v['originalVA']-0x8000+len(bits)]==bits,'Boundary original bytes')
            code_views[v['name']]=v
        for v in plan.get('existing_data_anchors',[]):
            need(v['name'] not in data_anchors and v['section'] in baseline['allocations'],'Unique typed anchor into prior captured RO')
            need(v['proof_source']=='module_cfg_evidence' and v['proof_sha256']==item['cfg_sha256'],'Anchor consumes the pinned module CFG proof, no external path drift')
            data_anchors[v['name']]=v;anchor_proofs[v['name']]=cfg_docs[item['name']][1]
        for section in plan['sections']:
            need(section['name'] not in new_sections and section['kind'] in ('code','RO','captured_view'),'Distinct observed code/data storage')
            new_sections[section['name']]=section
        for s in plan['defined_symbols']:
            need(s['name'] not in new_symbols and s['section'] in new_sections,'No new ABS or duplicate implementation')
            new_symbols[s['name']]=s
        for name,row in plan['expected_undefined_symbols'].items():
            need(name not in unknown or unknown[name]['originalVA']==row['originalVA'],'Consistent external address')
            unknown[name]=row
    source_hashes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources}
    need(set(baseline.get('new_providers',{}))==set(spec['required_inherited_providers']) and not(set(baseline.get('new_providers',{}))&set(new_symbols)),'Explicit unchanged inherited providers disjoint from new providers')
    need(set(baseline.get('existing_code_views',{}))==set(spec['required_inherited_code_views']),'Explicit inherited code-view identities')
    need(baseline['relative32_expression_count']==spec['expected_inherited_relative32_expression_count'],'Explicit inherited relative32 scope')
    need(set(new_symbols)==set(spec['required_providers']),'Exactly the selected entry providers')
    need(set(code_views)==set(spec.get('required_code_views',[])) and not(set(code_views)&set(new_symbols)),'Explicit noncolliding existing-code views')
    need(set(data_anchors)==set(spec.get('required_data_anchors',[])) and not(set(data_anchors)&(set(new_symbols)|set(code_views)|set(unknown))),'Explicit distinct data anchors, no module provider or dummy UND')
    base_obj=ELF(Path(baseline['modes']['c']['integrated_object']))
    base_witness=ELF(baseline_path.parent/'c/ADDRESS-WITNESS-ONLY.elf')
    need(sha(base_obj.raw)==baseline['modes']['c']['integrated_sha256'] and sha(base_witness.raw)==baseline['modes']['c']['numeric_witness_sha256'],'Actual reviewed baseline artifacts')
    allocations=dict(baseline['allocations'])
    need(not(set(allocations)&set(new_sections)),'Never replace baseline storage')
    allocations.update({n:dict(s,flags=6 if s['kind']=='code' else 2) for n,s in new_sections.items()})
    data_anchor_results={n:anchor_validate_proof(anchor_proofs[n],v,raw,baseline,base_obj,base_witness,new_sections) for n,v in data_anchors.items()}
    inherited_code_views=baseline.get('existing_code_views',{})
    need(not(set(inherited_code_views)&set(code_views)),'Preserve inherited code-view identities')
    ranges=sorted((s['originalVA'],s['originalVA']+s['bytes'],n) for n,s in allocations.items() if s['kind']!='RAM')
    need(all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:])),'All old/new bytes allocated once')
    ram_views=dict(baseline['modes']['c']['RAM_views'])
    observed_ram={n:s['originalVA']-0x20004000 for n,s in unknown.items() if s['role'].startswith('data_address') and 0x20004000<=s['originalVA']<0x2000c958}
    need(all(n not in ram_views or ram_views[n]==o for n,o in observed_ram.items()),'Consistent existing RAM address views')
    added_ram={n:o for n,o in observed_ram.items() if n not in ram_views}
    ram_views.update(added_ram)
    if 'expected_RAM_view_count' in spec:need(len(ram_views)==spec['expected_RAM_view_count'],'Exact reviewed address-only RAM view count')
    prior_und=set(baseline['modes']['c']['undefined_symbols'])
    prior_real={n for n,s in base_obj.symbol.items() if s['index'] not in (0,0xfff1) and base_obj.sections[s['index']]['flags']&2}
    need(set(data_anchors)<=prior_und and not(set(data_anchors)&(prior_real|set(ram_views))),'Only proven original UND is supplied by data anchor')
    need(not(set(code_views)&prior_real),'Never replace a real prior symbol with a view')
    need(all(n not in prior_real or base_witness.symbol[n]['value']==s['originalVA'] for n,s in unknown.items()),'New references agree with actual prior provider addresses')
    need(all(n in unknown and unknown[n]['originalVA']==v['originalVA'] and unknown[n]['role']=='existing_code_section_relative_view_no_storage' for n,v in code_views.items()),'Views resolve only their declared existing-code dependencies')
    need(all(n not in new_symbols or new_symbols[n]['originalVA']==s['originalVA'] for n,s in unknown.items()),'New cross-module references agree with actual provider addresses')
    remaining=(prior_und|set(unknown))-set(new_symbols)-set(ram_views)-set(code_views)-set(data_anchors)-prior_real
    need(remaining==set(spec['expected_undefined_symbols']),'Explicit unresolved dependency frontier')
    addresses={n:base_witness.symbol[n]['value'] for n in prior_und}
    addresses.update({n:s['originalVA'] for n,s in unknown.items()})
    need(all(addresses[n]==a for n,a in spec['expected_undefined_symbols'].items()),'Original unresolved numeric addresses, not providers')
    layout=work/'original-address-layout.ld'
    text='OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for name,s in sorted(allocations.items(),key=lambda x:x[1]['originalVA']):
        text+=f' {name} {hex(s["originalVA"])}'+(' (NOLOAD)' if s['kind']=='RAM' else '')+f' : {{ KEEP(*({name})) }}\n ASSERT(SIZEOF({name})=={s["bytes"]}, "Original size changed")\n'
    layout.write_text(text+' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n',encoding='utf-8')
    ram_script=work/'actual-RAM-views.ld'
    partial='SECTIONS { .bss.tsl9v4160.ram 0 : { KEEP(*(.bss.tsl9v4160.ram))\n'+''.join(n+' = __tsl9v4160_ram + '+hex(o)+';\n' for n,o in sorted(added_ram.items()))+'}\n'
    grouped_views=collections.defaultdict(list)
    for n,v in sorted(code_views.items()):grouped_views[v['section']].append((n,v))
    for section,rows in sorted(grouped_views.items()):
        partial+=section+' 0 : {\n'+''.join(n+' = . + '+hex(v['offset'])+';\n' for n,v in rows)+'KEEP(*('+section+'))\n}\n'
    ram_script.write_text(partial+'}\n',encoding='utf-8')
    grouped_data=collections.defaultdict(list)
    for n,v in sorted(data_anchors.items()):grouped_data[v['section']].append((n,v))
    anchor_partial=''
    for section,rows in sorted(grouped_data.items()):
        anchor_partial+=section+' 0 : {\n'+''.join(n+' = . + '+hex(v['offset'])+';\n' for n,v in rows)+'KEEP(*('+section+'))\n}\n'
    ram_script.write_text(partial+anchor_partial+'}\n',encoding='utf-8')
    witness_script=work/'ADDRESS-WITNESS-ONLY.ld'
    witness_script.write_text('/* Only unresolved original numbers; NOT code/data implementations. */\n'+''.join(n+' = '+hex(addresses[n])+';\n' for n in sorted(remaining)),encoding='utf-8')
    def normalized(elf,r):
        sym=elf.symbols[r['symbol_index']]
        if sym['index']==0:
            if r['symbol_index']==0:return r['addend']
            need(sym['name'] in addresses or sym['name'] in new_symbols,'Known unresolved address role')
            return (addresses[sym['name']] if sym['name'] in addresses else new_symbols[sym['name']]['originalVA'])+r['addend']
        if sym['index']==0xfff1:return sym['value']+r['addend']
        name=elf.sections[sym['index']]['name'];need(name in allocations,'Actual allocated target section')
        return allocations[name]['originalVA']+sym['value']+r['addend']
    def check_ram(elf):
        ram=elf.symbol['__tsl9v4160_ram'];need(ram['index'] not in (0,0xfff1) and ram['size']==35160,'Single existing RAM provider')
        need(elf.sections[ram['index']]['type']==8 and elf.sections[ram['index']]['size']==35160,'No fabricated RAM values or extra storage')
        for name,offset in ram_views.items():
            v=elf.symbol[name];need(v['index']==ram['index'] and v['type']==0 and v['size']==0 and v['value']-ram['value']==offset,'Section-relative RAM view '+name)
    def check_new_providers(elf,linked=False):
        for name,s in new_symbols.items():
            v=elf.symbol[name];need(v['index']==elf.byname[s['section']]['index'] and v['type']==s['elf_type'] and v['size']==s['size'],'Actual extension provider '+name)
            need(v['value']==(s['originalVA'] if linked else s['originalVA']-new_sections[s['section']]['originalVA']),'Exact extension provider offset '+name)
    def check_code_views(elf,linked=False):
        for n,v in code_views.items():
            sym=elf.symbol[n]
            need(sym['index']==elf.byname[v['section']]['index'] and sym['type']==0 and sym['size']==0 and sym['bind']==1,'Actual section-relative old-code NOTYPE0 view '+n)
            need(sym['value']==(v['originalVA'] if linked else v['offset']),'View does not allocate or replace bytes '+n)
    def check_data_anchors(elf,linked=False):
        anchor_check_fields(elf,data_anchors,allocations,linked)
        for n,v in inherited_code_views.items():
            sym=elf.symbol[n];need(sym['index']==elf.byname[v['section']]['index'] and sym['type']==0 and sym['size']==0 and sym['bind']==1 and sym['value']==(v['originalVA'] if linked else v['offset']),'Inherited actual code view unchanged')
    def check_relative_providers(elf):
        records=collections.defaultdict(list)
        for row in elf.relocations:
            if row['type'] in (35,39):records[(row['section'],row['offset'])].append(row)
        for item,plan in modules:
            for e in plan.get('relative32_expressions',[]):
                rows=records[(e['section'],e['offset'])]
                need(len(rows)==2 and collections.Counter(r['type'] for r in rows)=={35:1,39:1},'Actual merged relative32 pair')
                for row in rows:
                    symbol=elf.symbols[row['symbol_index']]
                    need(symbol['index'] not in (0,0xfff1),'Relative32 operands require actual section-backed providers, never numeric substitutes')
                    section=elf.sections[symbol['index']]['name'];storage=allocations[section]
                    if row['type']==35:
                        need(storage['kind']=='code' and 0<=symbol['value']+row['addend']<storage['bytes'],'ADD target is within captured code storage')
                        need(normalized(elf,row)==e['target_originalVA']+e['target_addend'],'Exact captured target plus addend')
                    else:
                        need(section==e['section'] and normalized(elf,row)==e['base_originalVA']+e['base_addend'],'SUB base belongs to its actual table')
    def inspect_module(elf,plan):
        sections={s['name']:s for s in plan['sections']}
        need(elf.kind==1 and {s['name'] for s in elf.sections if s['flags']&2 and s['size']}==set(sections),'Exact selected extension allocations')
        need({s['name'] for s in elf.symbols if s['name'] and s['index']==0}==set(plan['expected_undefined_symbols']),'Keep every true standalone dependency')
        for s in plan['defined_symbols']:
            v=elf.symbol[s['name']];need(v['index']==elf.byname[s['section']]['index'] and v['value']==s['originalVA']-sections[s['section']]['originalVA'] and v['type']==s['elf_type'] and v['size']==s['size'],'Real module symbol')
        anchor_check_fragment(elf,plan)
        need({s['name'] for s in elf.symbols if s['bind']==1 and s['index']!=0}=={s['name'] for s in plan['defined_symbols']},'Exact module global definitions, no hidden anchor/ABS provider')
        expected=collections.defaultdict(list)
        for e in plan['relocations']:expected[(e['section'],e['offset'])].append(e)
        wanted=collections.Counter((e['section'],e['offset'],e['type_number'],e['target_originalVA']+e['addend']) for e in plan['relocations'])
        actual=collections.Counter((r['section'],r['offset'],r['type'],normalized(elf,r)) for r in elf.relocations)
        need(actual==wanted,'Exact extension relocation semantic multiset, including same-site ADD/SUB')
        for r in elf.relocations:
            sym=elf.symbols[r['symbol_index']]
            if sym['index']==0:
                need(sym['name'] in plan['expected_undefined_symbols'] and any(e['target']==sym['name'] and e['type_number']==r['type'] and e['target_originalVA']+e['addend']==normalized(elf,r) for e in expected[(r['section'],r['offset'])]),'Unresolved target name/role retained')
        expressions={}
        for e in plan.get('relative32_expressions',[]):
            key=(e['section'],e['offset']);need(key not in expressions,'One expression per word, never duplicate providers')
            need(e['section'] in sections and sections[e['section']]['kind']=='RO' and e['offset']%4==0 and 0<=e['offset']<=sections[e['section']]['bytes']-4,'Bounded relative32 RO word')
            need(e['initial_u32']==0,'Canonical symbolic table has zero initial word, not copied encoded delta')
            rows=expected[key]
            need(len(rows)==2 and collections.Counter(x['type_number'] for x in rows)=={35:1,39:1},'Exactly one ADD32 and one SUB32 at this word')
            add=next(x for x in rows if x['type_number']==35);sub=next(x for x in rows if x['type_number']==39)
            need((add['target'],add['target_originalVA'],add['addend'])==(e['target_symbol'],e['target_originalVA'],e['target_addend']),'Exact ADD target/addend')
            need((sub['target'],sub['target_originalVA'],sub['addend'])==(e['base_symbol'],e['base_originalVA'],e['base_addend']),'Exact SUB base/addend')
            result=(e['initial_u32']+add['target_originalVA']+add['addend']-sub['target_originalVA']-sub['addend'])&0xffffffff
            pc=sections[e['section']]['originalVA']+e['offset'];original=struct.unpack_from('<I',raw,pc-0x8000)[0]
            need(result==e['original_u32']==original,'Relative32 expression equals original encoded word modulo 2^32')
            expressions[key]=e
        need({(r['section'],r['offset']) for r in plan['relocations'] if r['type_number'] in (35,39)}==set(expressions),'Every ADD/SUB word has a reviewed complete expression')
        for section in {name for name,offset in expressions}:
            need(sections[section]['bytes']%4==0 and {offset for name,offset in expressions if name==section}==set(range(0,sections[section]['bytes'],4)),'Every word of each captured relative table has its expression')
        for name,s in sections.items():
            b=raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']]
            need(len(b)==s['bytes'] and sha(b)==s['sha256'],'Pinned original code/data view')
            initial=bytearray(b)
            for (section,offset),e in expressions.items():
                if section==name:struct.pack_into('<I',initial,offset,e['initial_u32'])
            need(elf.byname[name]['data']==initial,'Exact unlinked bytes, with explicit relative32 initial words')
            if s['kind']!='code':continue
            offset=0
            while offset<s['bytes']:
                half=struct.unpack_from('<H',b,offset)[0];width=4 if half&3==3 else 2
                need(offset+width<=s['bytes'],'No truncated native instruction')
                target=direct_target(s['originalVA']+offset,width,int.from_bytes(b[offset:offset+width],'little'))
                if target:need(any((e['type_number'],e['target_originalVA']+e['addend'])==target for e in expected[(name,offset)]),'Every direct control transfer has exact provider-plus-addend relocation')
                offset+=width
    counts=dict(code_bytes=sum(s['bytes'] for s in allocations.values() if s['kind']=='code'),RO_bytes=sum(s['bytes'] for s in allocations.values() if s['kind']!='code' and s['kind']!='RAM'),allocation_sections=len(allocations),relocations=baseline['modes']['c']['relocations']+sum(len(p['relocations']) for _,p in modules))
    need(all(counts[n]==v for n,v in spec['expected_counts'].items()),'Reviewed exact integration scope')
    need(sum(len(p.get('relative32_expressions',[])) for _,p in modules)==spec['expected_relative32_expression_count'],'Exact independently reviewed relative32 scope')
    modes={}
    for mode,language,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();commands=[];objects=[];relative_countercases=[]
        for item,plan in modules:
            obj=folder/(item['name']+'.o')
            cmd,_=run([cc,'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-stack-protector','-fno-builtin','-Wall','-Wextra','-Werror','-x',language,'-std='+std,'-c',local(item['source']),'-o',obj],folder,'compile-'+item['name']);commands.append(cmd)
            module_elf=ELF(obj);inspect_module(module_elf,plan);objects.append(obj)
            if plan.get('relative32_expressions'):
                e=plan['relative32_expressions'][0]
                bad=bytearray(module_elf.raw);section=module_elf.byname[e['section']]
                need(e['original_u32']!=e['initial_u32'],'Nontrivial actual encoded-delta countercase')
                struct.pack_into('<I',bad,section['offset']+e['offset'],e['original_u32'])
                counter=folder/(item['name']+'-COUNTERCASE-double-encoded.o');counter.write_bytes(bad)
                rejected=False;reason=''
                try:inspect_module(ELF(counter),plan)
                except AssertionError as error:rejected=True;reason=str(error)
                need(rejected,'Same module gate rejects actual raw-delta initial word')
                relative_countercases.append(dict(kind='raw_delta_initial_word',path=str(counter),sha256=sha(counter.read_bytes()),rejected=True,reason=reason))
                bad=bytearray(module_elf.raw);changed=False
                for table in module_elf.sections:
                    if table['type']!=4 or table['info']!=section['index']:continue
                    for offset in range(0,table['size'],12):
                        site,info=struct.unpack_from('<II',table['data'],offset)
                        if site==e['offset'] and info&255==39:
                            struct.pack_into('<I',bad,table['offset']+offset+4,(info&~255)|35);changed=True
                need(changed,'Actual SUB32 record selected')
                counter=folder/(item['name']+'-COUNTERCASE-SUB-to-ADD.o');counter.write_bytes(bad)
                rejected=False;reason=''
                try:inspect_module(ELF(counter),plan)
                except AssertionError as error:rejected=True;reason=str(error)
                need(rejected,'Same module gate rejects actual changed relocation multiset')
                relative_countercases.append(dict(kind='SUB32_changed_to_ADD32',path=str(counter),sha256=sha(counter.read_bytes()),rejected=True,reason=reason))
        prior_path=Path(baseline['modes'][mode]['integrated_object']);need(sha(prior_path.read_bytes())==baseline['modes'][mode]['integrated_sha256'],'Actual prior object digest')
        prior=ELF(prior_path);integrated=folder/'native-extension.o'
        cmd,_=run([ld,'-r','--no-relax','-T',ram_script,prior_path,*objects,'-o',integrated],folder,'integrate-actual-providers');commands.append(cmd)
        merged=ELF(integrated);check_ram(merged);check_new_providers(merged);check_code_views(merged);check_data_anchors(merged);check_relative_providers(merged);anchor_check_inherited_relative(merged,allocations,normalized,spec['expected_inherited_relative32_expression_count'])
        need({s['name'] for s in merged.sections if s['flags']&2 and s['size']}==set(allocations),'No added code-view storage')
        need(len(merged.relocations)==counts['relocations'],'All old/new relocations retained')
        old=collections.Counter((r['section'],r['offset'],r['type'],normalized(prior,r)) for r in prior.relocations)
        current=collections.Counter((r['section'],r['offset'],r['type'],normalized(merged,r)) for r in merged.relocations)
        need(not(old-current),'Every prior semantic relocation preserved with multiplicity')
        for section in prior.sections:
            if section['flags']&2 and section['size']:
                now=merged.byname[section['name']];need(now['type']==section['type'] and now['size']==section['size'] and now['data']==section['data'],'All prior original storage preserved')
        for name,s in prior.symbol.items():
            # ELF local mapping symbols ($d.0, etc.) may repeat across objects;
            # a name-indexed table does not identify them uniquely. Their storage
            # and references are checked above; only external providers/views
            # have a unique exported-name identity here.
            if s['bind']==0 or s['index'] in (0,0xfff1) or not(prior.sections[s['index']]['flags']&2):continue
            now=merged.symbol[name];need(now['index']==merged.byname[prior.sections[s['index']]['name']]['index'] and (now['type'],now['size'],now['value'])==(s['type'],s['size'],s['value']),'Every prior real provider/view preserved')
        need({s['name'] for s in merged.symbols if s['name'] and s['index']==0}==remaining,'Explicit true dependency frontier')
        strict=folder/'strict-incomplete.elf'
        cmd,log=run([ld,'--no-relax','--error-limit=0','-T',layout,integrated,'-o',strict],folder,'strict-final-link',False);commands.append(cmd)
        need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',log.decode('utf-8','replace')))==remaining,'Strict unresolved dependencies are fatal, no ELF')
        witness=folder/'ADDRESS-WITNESS-ONLY.elf'
        cmd,_=run([ld,'--no-relax','-T',layout,'-T',witness_script,integrated,'-o',witness],folder,'numeric-address-witness');commands.append(cmd)
        linked=ELF(witness);check_ram(linked);check_new_providers(linked,True);check_code_views(linked,True);check_data_anchors(linked,True)
        need({s['name'] for s in linked.sections if s['flags']&2 and s['size']}==set(allocations),'No hidden code/data/stack storage')
        for name,s in allocations.items():
            section=linked.byname[name];need(section['address']==s['originalVA'] and section['size']==s['bytes'],'Exact original allocation address/size')
            if s['kind']!='RAM':need(section['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'All allocated source bytes exact')
        # Genuine ELF mutation must be rejected by the same provider gate.
        bad=bytearray(merged.raw);chosen=sorted(new_symbols)[0];changed=False
        for table in merged.sections:
            if table['type']!=2:continue
            strings=merged.sections[table['link']]['data']
            for off in range(0,table['size'],16):
                at=struct.unpack_from('<I',table['data'],off)[0];name=strings[at:strings.index(0,at)].decode('ascii')
                if name==chosen:struct.pack_into('<H',bad,table['offset']+off+14,0xfff1);changed=True
        need(changed,'Actual provider countercase selected')
        counter=folder/'COUNTERCASE-ABS-provider.o';counter.write_bytes(bad);rejected=False
        try:check_new_providers(ELF(counter))
        except AssertionError:rejected=True
        need(rejected,'Same provider gate rejects actual ABS substitution')
        code_view_negative=None
        if code_views:
            chosen=sorted(code_views)[0];bad=bytearray(merged.raw);changed=False
            for table in merged.sections:
                if table['type']!=2:continue
                strings=merged.sections[table['link']]['data']
                for offset in range(0,table['size'],16):
                    at=struct.unpack_from('<I',table['data'],offset)[0]
                    if strings[at:strings.index(0,at)].decode('ascii')==chosen:
                        struct.pack_into('<H',bad,table['offset']+offset+14,0xfff1);changed=True
            need(changed,'Actual existing-code view selected')
            counter=folder/'COUNTERCASE-ABS-existing-code-view.o';counter.write_bytes(bad);rejected=False
            try:check_code_views(ELF(counter))
            except AssertionError:rejected=True
            need(rejected,'Same old-code view gate rejects actual ABS substitution')
            code_view_negative=dict(symbol=chosen,path=str(counter),sha256=sha(counter.read_bytes()),rejected=True)
        data_anchor_countercases=anchor_actual_countercases(merged,data_anchors,allocations,folder)+anchor_actual_countercases(linked,data_anchors,allocations,folder,True)
        modes[mode]=dict(data_anchor_actual_countercases=data_anchor_countercases,existing_data_anchors={n:dict(symbol=merged.symbol[n],raw_symbol=anchor_symbol_record(merged,n),witness_symbol=linked.symbol[n],witness_raw_symbol=anchor_symbol_record(linked,n)) for n in data_anchors},passed=True,commands=commands,integrated_object=str(integrated),integrated_sha256=sha(integrated.read_bytes()),numeric_witness_sha256=sha(witness.read_bytes()),undefined_symbols=sorted(remaining),RAM_views=ram_views,RAM_NOBITS_bytes=35160,strict_rejected=True,ABS_provider_countercase_rejected=True,relative32_actual_countercases=relative_countercases,inherited_relative32_actual_countercases=baseline['modes'][mode]['relative32_actual_countercases'],inherited_existing_code_view_ABS_countercase=baseline['modes'][mode].get('existing_code_view_ABS_countercase'),existing_code_view_ABS_countercase=code_view_negative,**counts)
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256'] and modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256'],'C/C++ objects and witnesses byte-equal')
    need(source_hashes=={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources},'Source unchanged during verification')
    report=dict(schema='ID2966-native-data-anchor-extension-report-v1',extension_name=spec['name'],passed=True,firmware_sha256=sha(raw),source_files=source_hashes,tools={str(p):sha(p.read_bytes()) for p in [cc,ld]},baseline_receipt=str(baseline_path),baseline_receipt_sha256=sha(baseline_path.read_bytes()),allocations=allocations,new_providers={**baseline.get('new_providers',{}),**new_symbols},new_module_provider_names=sorted(new_symbols),inherited_provider_names=sorted(baseline.get('new_providers',{})),new_module_provider_count=len(new_symbols),inherited_module_provider_count=len(baseline.get('new_providers',{})),existing_code_views={**inherited_code_views,**code_views},new_existing_code_views=code_views,existing_data_anchors=data_anchors,data_anchor_proof_results=data_anchor_results,data_anchor_count=len(data_anchors),data_anchor_storage_bytes=0,original_C_same_object_proved=False,byte0_storage_proved=False,relative32_expression_count=baseline['relative32_expression_count']+sum(len(p.get('relative32_expressions',[])) for _,p in modules),new_relative32_expression_count=sum(len(p.get('relative32_expressions',[])) for _,p in modules),inherited_relative32_expression_count=baseline['relative32_expression_count'],modes=modes,all_runtime_pointer_targets_proved=False,IRQ_ABI_proved=False,firmware_executed=False,emulation=False,network=False,hardware=False,target_ready=False,ota_verified=False,native_bin=False)
    receipt=work/'verification.json';receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,**counts,remaining_undefined=len(remaining),receipt=str(receipt),native_bin=False)))

if __name__=='__main__':main()
