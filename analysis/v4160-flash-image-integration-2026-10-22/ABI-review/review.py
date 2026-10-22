"""Independent actual full-image ABI/role review; reads bytes and never executes RV32."""
from pathlib import Path
from collections import Counter
import argparse,copy,hashlib,json,re,runpy,struct,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SHA=lambda b:hashlib.sha256(b).hexdigest()
MANIFEST='d952159ab2bf7c5294bc433510b88a7c19b23295ba11b0e7ab3d4a1ed39b1ce7'
PLAN_SEAL='81912879ab740bff2055d518eac48f2191fad242ed782fc84cc7e3d0ea62169d'
BASELINE_SHA='c3cf60fb54b9b4bc234e1c7408c15ec40679161201b95d61e3d89a06562a4e95'
DISCHARGED={'.Ldirect_closure_00018ee0','.Ldirect_closure_00018f02','.Ldirect_closure_00018f0c','.Ldirect_closure_00018f1a','.Ldirect_closure_00018f2a','.Ldirect_closure_00018f44'}
FLASH={0x9c0a:('quarter',64),0x18e90:('status',8),0x18e98:('unlock',30),0x18eb6:('lock',14),0x18ec4:('erase',46),0x18ef2:('program',100)}


def need(v,why):
    if not v:raise ValueError(why)


def case(root,slug):
    return next(p for p in [root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug] if p.is_dir())


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def count(value):return Counter(canonical(x) for x in value)
def data(e,s):return b'' if s['type']==8 else e.data(s)
def alloc(e):return {s['name']:s for s in e.sections if s['flags']&2 and s['size']}


def role(e,s,linked=False):
    i=s['index'];owner=e.sections[i]['name'] if 0<i<len(e.sections) else ('UND' if i==0 else 'ABS' if i==0xfff1 else 'SPECIAL:'+str(i))
    value=s['value']-(e.sections[i]['address'] if linked and 0<i<len(e.sections) else 0)
    return dict(name=s['name'],owner=owner,offset=value,bytes=s['size'],info=s['info'],other=s['other'])


def relocation(e,r):return dict(owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend'],symbol=role(e,r['symbol']))


def direct_jump(code,offset,base):
    h=int.from_bytes(code[offset:offset+2],'little');pc=base+offset
    if h&3==3:
        w=int.from_bytes(code[offset:offset+4],'little');need(w&127==0x6f,'actual JAL opcode')
        rd=(w>>7)&31;k=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        delta=k-(1<<21) if k&(1<<20) else k;n=4
    else:
        need(h&3==1 and h>>13 in (1,5),'actual RV32 C.JAL/C.J opcode')
        rd=1 if h>>13==1 else 0
        k=((h>>12)&1)<<11|((h>>11)&1)<<4|((h>>9)&3)<<8|((h>>8)&1)<<10|((h>>7)&1)<<6|((h>>6)&1)<<7|((h>>3)&7)<<1|((h>>2)&1)<<5
        delta=k-(1<<12) if k&(1<<11) else k;n=2
    return dict(site=pc,bytes=n,rd=rd,target=pc+delta,link=pc+n if rd else None,raw_hex=code[offset:offset+n].hex())


def checked_seal(directory,name,digest):
    raw=(directory/name).read_bytes();need(SHA(raw)==digest,'immutable dependency seal '+name);seal=json.loads(raw)
    members=seal.get('members',seal.get('files'))
    if isinstance(members,dict):members=[dict(path=n,sha256=h) for n,h in members.items()]
    for r in members:need(SHA((directory/r['path']).read_bytes())==r['sha256'],'immutable dependency member '+r['path'])


def historical_context(root,prior,flash_component,parser=None,firmware=None):
    plan_dir=case(root,'v4160-flash-entry-order-2026-10-22')/'image-plan';checked_seal(plan_dir,'seal.json',PLAN_SEAL);plan=json.loads((plan_dir/'report.json').read_bytes())
    manifest=root/'experiments/tsl9-v4160-irq-image-integration/source-manifest.json';need(SHA(manifest.read_bytes())==MANIFEST,'baseline full691 manifest');m=json.loads(manifest.read_bytes())
    parser=parser or case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py';need(SHA(parser.read_bytes())=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','bounded ELF parser')
    ELF=runpy.run_path(str(parser))['ELF'];base=ELF(prior/'source-integrated.o');oldlinked=ELF(prior/'ADDRESS-WITNESS-ONLY.elf')
    need(SHA(base.raw)==plan['prior_object_sha256'] and len(base.relocations)==8276,'actual prior IRQ-integrated carrier, not original8280')
    p100=case(root,'v4160-flash-entry-order-2026-10-22')/'ABI-review/program.py';need(SHA(p100.read_bytes())=='8896ae7d7ce7b59c2760099d493594cae43e49e177319cd6b78bf56b430eb73a','independent program100 checker')
    program=runpy.run_path(str(p100));fd=case(root,'v4160-flash-native-2026-10-22')/'compiler-review/review.py';need(SHA(fd.read_bytes())=='8b04718cadb328b6a84b5f0791df666f968340db75134807e9f299b6f43b1448','unchanged five Flash gates')
    f=runpy.run_path(str(fd));decode,_=f['pinned_helpers'](root,parser)
    component=ELF(flash_component);need(SHA(component.raw)=='aeccc19da9c5764a386333dd26898429c35bf0ff40efb08c8f8417b11820339d','actual sealed final six Flash component')
    irq=case(root,'v4160-irq-callframe-2026-10-21')/'compiler-review';checked_seal(irq,'final-audit.json','adf95bbe0f92f012e790b8226abc80c7ec6f6ec483bcdd31e91e34526afbc83b')
    oldIRQ=json.loads((irq/'receipts/c.json').read_bytes())['checks']['machine'];irq_functions=oldIRQ['functions']
    src=case(root,'v4160-interrupt-init-2026-10-21')/'source/inspect-source.py';need(SHA(src.read_bytes())=='352e9460efd082b6e6a9fe726c7141bc1efcb328d2988734f5b1b3d5c347c1ed','IRQ raw operand decoder')
    idecode=runpy.run_path(str(src))['decode']
    selected={r['name']:r for r in plan['selected']};need(len(selected)==11 and sum(r['bytes'] for r in selected.values())==526,'eleven526-byte owners')
    references={}
    for name,fact in irq_functions.items():
        address=fact['rows'][0]['addr'];references[address]=dict(name=name,bytes=fact['bytes'],code=bytes.fromhex(''.join(r['bytes'] for r in fact['rows'])),rows=fact['rows'],family='IRQ')
    for address,(name,size) in FLASH.items():
        public='tsl9_flash_'+name+'_'+format(address,'x');s=next(s for s in component.symbols if s['name']==public);body=component.function_bytes(s)
        need(len(body)==size and s['value']==address,'component original Flash entry/extent')
        references[address]=dict(name=public,bytes=size,code=body,family='Flash',short=name)
    firmware=firmware or root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    original=firmware.read_bytes();need(len(original)==76800 and SHA(original)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','original source image identity')
    return dict(root=root,ELF=ELF,plan=plan,manifest=m,base=base,oldlinked=oldlinked,selected=selected,references=references,decode=decode,idecode=idecode,program=program,flash=f,original=original)


def historical_sections_and_roles(merged,linked,ctx):
    base=ctx['base'];m=ctx['manifest'];selected=ctx['selected'];oldalloc=alloc(base);newalloc=alloc(merged);linkedalloc=alloc(linked)
    need(merged.kind==1 and linked.kind==2 and merged.flags==linked.flags==base.flags==1,'ET_REL/EXEC RVC image kinds')
    need(set(oldalloc)==set(newalloc)==set(linkedalloc)==set(m['allocations']) and len(oldalloc)==691,'all691 exact allocation owners')
    for name,old in oldalloc.items():
        q=newalloc[name];l=linkedalloc[name];a=m['allocations'][name]
        need(all(q[k]==old[k] for k in ('type','flags','size','alignment','entry_size','address')),'unchanged merged section role '+name)
        need(l['address']==a['originalVA'] and all(l[k]==old[k] for k in ('type','flags','size','alignment','entry_size')),'unchanged original linked placement '+name)
        if name not in selected:
            need(data(merged,q)==data(base,old),'all680 outside merged bytes '+name)
            need(data(linked,l)==data(ctx['oldlinked'],ctx['oldlinked'].byname[name]),'all680 outside linked bytes '+name)
    outside_before=[relocation(base,r) for r in base.relocations if r['owner'] not in selected]
    outside_after=[relocation(merged,r) for r in merged.relocations if r['owner'] not in selected]
    need(len(outside_before)==8259 and count(outside_before)==count(outside_after),'all8259 outside RELA exact semantic multiset')
    need(SHA(canonical(sorted(outside_before,key=lambda r:json.dumps(r,sort_keys=True))).encode())==ctx['plan']['outside_RELA_semantic_sha256'],'pinned sourceplan outside-role digest')
    need(len(merged.relocations)==8270 and len([r for r in merged.relocations if r['owner'] in selected])==11,'new8259+11 RELA after6 discharges')
    need(not linked.relocations,'no linked residual relocation')
    before=count(role(base,s) for s in base.symbols if s['name'] and s['info']>>4 in (1,2));after=count(role(merged,s) for s in merged.symbols if s['name'] and s['info']>>4 in (1,2))
    need(not before-after,'all original global/weak roles retained')
    expected=[]
    for address,(short,size) in FLASH.items():
        owner=next(n for n,r in selected.items() if r['originalVA']==address)
        expected.append(dict(name='tsl9_flash_'+short+'_'+format(address,'x'),owner=owner,offset=0,bytes=size,info=18,other=0))
    need(after-before==count(expected),'exact six new public Flash function roles')
    for b in m['section_relative_bindings']:
        s=[s for s in merged.symbols if s['name']==b['name']];need(len(s)==1 and role(merged,s[0])==b['role'],'all53 actual section-relative bindings')
    for name in DISCHARGED:
        symbol=next(s for s in base.symbols if s['name']==name);users=[r for r in base.relocations if role(base,r['symbol'])==role(base,symbol)]
        need(len(users)==1 and users[0]['owner']==base.sections[symbol['index']]['name'] and users[0]['type'] in (16,44) and users[0]['addend']==0,'branch label has one sole selected self-reference')
        need(not any(s['name']==name for s in merged.symbols),'discharged private label absent, not false numeric alias')
    referenced={id(e):{canonical(role(e,r['symbol'])) for r in e.relocations} for e in (base,merged,linked)}
    def metadata(e,s):
        if canonical(role(e,s)) in referenced[id(e)]:return False
        relative=role(e,s,e.kind==2)['offset']
        if s['info']==0 and not relative and not s['size'] and not s['other'] and re.fullmatch(r'\$(?:x|d)(?:\.\d+)?',s['name']):return True
        return s['info']==4 and s['index']==0xfff1 and not s['value'] and not s['size'] and not s['other']
    def regular(e,s):
        if s['name'] in DISCHARGED:return False
        return not metadata(e,s)
    oldlocals=count(role(base,s) for s in base.symbols if s['info']>>4==0 and regular(base,s));newlocals=count(role(merged,s) for s in merged.symbols if s['info']>>4==0 and regular(merged,s))
    need(not oldlocals-newlocals,'all nonmetadata local/SECTION roles outside6 discharges retained')
    extras=newlocals-oldlocals
    need(not extras,'no additional nonmetadata local/SECTION role')
    def normalized_metadata(e):
        result=[]
        for s in e.symbols:
            if metadata(e,s):
                r=role(e,s,e.kind==2)
                if r['info']==0:r['name']=r['name'].split('.')[0]
                result.append(r)
        return count(result)
    expected_meta=normalized_metadata(base)
    for address in FLASH:
        owner=next(n for n,a in selected.items() if a['originalVA']==address)
        common=dict(owner=owner,offset=0,bytes=0,info=0,other=0)
        old=canonical(dict(name='$d',**common));need(expected_meta[old]==1,'one actual old raw-code mapping');expected_meta[old]-=1;expected_meta[canonical(dict(name='$x',**common))]+=1
    for owner,name,info in [('.comment','$d',0),('ABS','$d',0),('ABS','flash_native.c',4)]:expected_meta[canonical(dict(name=name,owner=owner,offset=0,bytes=0,info=info,other=0))]+=6
    need(+expected_meta==normalized_metadata(merged),'exact six d-to-x, six comment/attributes/FILE metadata additions')
    # Compare every merged role against its linked owner-relative role; UND ROM is an explicit witness only.
    linkedroles=count(role(linked,s,True) for s in linked.symbols if s['name'] and regular(linked,s));expected_linked=[]
    for s in merged.symbols:
        if not s['name'] or not regular(merged,s):continue
        r=role(merged,s)
        if r['owner']=='UND':
            need(r['name']=='__tsl9v4160_rom_entry','sole resident ROM exterior')
            targets=[v for v in linked.symbols if v['name']==r['name']];need(len(targets)==1 and targets[0]['index']==0xfff1 and targets[0]['value']==0x40000 and all(targets[0][k]==s[k] for k in ('info','size','other')),'numeric40000 witness role, not actual ROM provider')
            r.update(owner='ABS',offset=0x40000)
        else:need(linkedroles[canonical(r)]>0,'merged-to-linked exact symbol role '+s['name'])
        expected_linked.append(r)
    need(count(expected_linked)==linkedroles,'no extra or lost linked nonmetadata named role')
    linked_meta=normalized_metadata(merged);comment=canonical(dict(name='$d',owner='.comment',offset=0,bytes=0,info=0,other=0))
    need(linked_meta[comment]==42,'one unreferenced comment mapping per actual translation unit')
    linked_meta[comment]-=42
    need(+linked_meta==normalized_metadata(linked),'linked metadata exact after42 unreferenced comment mappings discharged')
    return dict(allocations=691,retained_storage_sections=680,outside_RELA=8259,total_RELA=8270,canonical_bindings=53,private_branches_discharged=sorted(DISCHARGED),extra_selected_local_roles=list(extras.elements()))


def is_metadata(e,s):
    if any(role(e,r['symbol'])==role(e,s) for r in e.relocations):return False
    relative=role(e,s,e.kind==2)['offset']
    if s['info']==0 and not relative and not s['size'] and not s['other'] and re.fullmatch(r'\$(?:x|d)(?:\.\d+)?',s['name']):return True
    return s['info']==4 and s['index']==0xfff1 and not s['value'] and not s['size'] and not s['other']


def metadata_counter(e):
    result=[]
    # Pre-compute referenced roles: testing every relocation for every symbol is needlessly quadratic.
    refs={canonical(role(e,r['symbol'])) for r in e.relocations}
    for s in e.symbols:
        r=role(e,s,e.kind==2)
        if canonical(role(e,s)) in refs:continue
        mapping=s['info']==0 and not r['offset'] and not s['size'] and not s['other'] and re.fullmatch(r'\$(?:x|d)(?:\.\d+)?',s['name'])
        file=s['info']==4 and s['index']==0xfff1 and not s['value'] and not s['size'] and not s['other']
        if mapping or file:
            if mapping:r['name']=r['name'].split('.')[0]
            result.append(r)
    return count(result)


def regular_roles(e,named=False):
    refs={canonical(role(e,r['symbol'])) for r in e.relocations};result=[]
    for s in e.symbols:
        if s['name'] in DISCHARGED or (named and not s['name']):continue
        r=role(e,s,e.kind==2)
        if canonical(role(e,s)) not in refs:
            mapping=s['info']==0 and not r['offset'] and not s['size'] and not s['other'] and re.fullmatch(r'\$(?:x|d)(?:\.\d+)?',s['name'])
            file=s['info']==4 and s['index']==0xfff1 and not s['value'] and not s['size'] and not s['other']
            if mapping or file:continue
        result.append(r)
    return result


def counter_digest(c):return SHA(canonical(sorted(c.items())).encode())


def source_facts(ctx):
    """One-time source-derived snapshot; no firmware byte carrier is copied into this manifest."""
    base=ctx['base'];linked=ctx['oldlinked'];selected=ctx['selected'];manifest=ctx['manifest'];sections={}
    for name,s in alloc(base).items():
        sections[name]={k:s[k] for k in ('type','flags','size','alignment','entry_size','address')}
        sections[name].update(originalVA=manifest['allocations'][name]['originalVA'],merged_sha256=SHA(data(base,s)),linked_sha256=SHA(data(linked,linked.byname[name])))
    incoming=[]
    for r in ctx['plan']['checks']['incoming']:
        owner=r['owner'];incoming.append(direct_jump(data(linked,linked.byname[owner]),r['offset'],manifest['allocations'][owner]['originalVA']))
    proof=[]
    for name in sorted(DISCHARGED):
        s=next(s for s in base.symbols if s['name']==name);users=[relocation(base,r) for r in base.relocations if role(base,r['symbol'])==role(base,s)]
        need(len(users)==1 and users[0]['owner']==role(base,s)['owner'] and users[0]['type'] in (16,44) and users[0]['addend']==0,'snapshot actual sole private branch use')
        proof.append(dict(symbol=role(base,s),users=users))
    previous=scatter(linked,ctx);original=ctx['original'];delta=[dict(offset=i,value=b) for i,(a,b) in enumerate(zip(original,previous)) if a!=b]
    need(len(delta)==8 and SHA(previous)=='47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c','snapshot exact prior eight-byte delta')
    refs={str(k):dict(v,code=v['code'].hex()) for k,v in ctx['references'].items()}
    return dict(schema='TSL9-source-derived-whole-image-ABI-baseline-v1',source_manifest_sha256=MANIFEST,source_plan_seal_sha256=PLAN_SEAL,prior_object_sha256=SHA(base.raw),prior_linked_sha256=SHA(linked.raw),sections=sections,global_role_digest=counter_digest(count(role(base,s) for s in base.symbols if s['name'] and s['info']>>4 in (1,2))),local_role_digest=counter_digest(count(r for r in regular_roles(base) if r['info']>>4==0)),metadata=dict(metadata_counter(base)),private_role_proof=proof,incoming=incoming,prior_IRQ_delta=delta,references=refs)


def context(root,prior=None,flash_component=None,parser=None,firmware=None):
    facts_path=HERE/'source-baseline.json';raw=facts_path.read_bytes()
    need(SHA(raw)==BASELINE_SHA,'source-derived baseline manifest pin');facts=json.loads(raw)
    plan_dir=case(root,'v4160-flash-entry-order-2026-10-22')/'image-plan';checked_seal(plan_dir,'seal.json',PLAN_SEAL);plan=json.loads((plan_dir/'report.json').read_bytes())
    manifest=root/'experiments/tsl9-v4160-irq-image-integration/source-manifest.json';need(SHA(manifest.read_bytes())==MANIFEST,'original691 manifest pin');m=json.loads(manifest.read_bytes())
    parser=parser or case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py';need(SHA(parser.read_bytes())=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','bounded ELF parser pin');ELF=runpy.run_path(str(parser))['ELF']
    fd=case(root,'v4160-flash-native-2026-10-22')/'compiler-review/review.py';need(SHA(fd.read_bytes())=='8b04718cadb328b6a84b5f0791df666f968340db75134807e9f299b6f43b1448','unchanged five Flash gate pin');f=runpy.run_path(str(fd));decode,_=f['pinned_helpers'](root,parser)
    p100=case(root,'v4160-flash-entry-order-2026-10-22')/'ABI-review/program.py';need(SHA(p100.read_bytes())=='8896ae7d7ce7b59c2760099d493594cae43e49e177319cd6b78bf56b430eb73a','program100 checker pin');program=runpy.run_path(str(p100))
    src=case(root,'v4160-interrupt-init-2026-10-21')/'source/inspect-source.py';need(SHA(src.read_bytes())=='352e9460efd082b6e6a9fe726c7141bc1efcb328d2988734f5b1b3d5c347c1ed','IRQ raw operand decoder pin');idecode=runpy.run_path(str(src))['decode']
    firmware=firmware or root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin';original=firmware.read_bytes();need(SHA(original)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','original firmware identity')
    references={int(k):dict(v,code=bytes.fromhex(v['code'])) for k,v in facts['references'].items()};selected={r['name']:r for r in plan['selected']}
    result=dict(root=root,ELF=ELF,plan=plan,manifest=m,selected=selected,references=references,decode=decode,idecode=idecode,program=program,flash=f,original=original,facts=facts)
    # Optional archived-source replay validates how the portable facts were derived; never required for fresh builds.
    if prior is not None:
        old=historical_context(root,prior,flash_component,parser,firmware);need(source_facts(old)==facts,'optional archived source baseline replay')
        result['archived_source_replay']=True
    return result


def sections_and_roles(merged,linked,ctx):
    facts=ctx['facts'];selected=ctx['selected'];newalloc=alloc(merged);linkedalloc=alloc(linked);expected=facts['sections']
    need(merged.kind==1 and linked.kind==2 and merged.flags==linked.flags==1,'ET_REL/EXEC RVC image kinds')
    need(set(newalloc)==set(linkedalloc)==set(expected) and len(expected)==691,'all691 exact allocation owners')
    for name,old in expected.items():
        q=newalloc[name];l=linkedalloc[name]
        need(all(q[k]==old[k] for k in ('type','flags','size','alignment','entry_size','address')),'unchanged merged section role '+name)
        need(l['address']==old['originalVA'] and all(l[k]==old[k] for k in ('type','flags','size','alignment','entry_size')),'unchanged original linked placement '+name)
        if name not in selected:
            need(SHA(data(merged,q))==old['merged_sha256'],'all680 outside merged bytes '+name)
            need(SHA(data(linked,l))==old['linked_sha256'],'all680 outside linked bytes '+name)
    outside=[relocation(merged,r) for r in merged.relocations if r['owner'] not in selected]
    need(len(outside)==8259 and SHA(canonical(sorted(outside,key=lambda r:json.dumps(r,sort_keys=True))).encode())==ctx['plan']['outside_RELA_semantic_sha256'],'all8259 outside RELA exact semantic digest')
    need(len(merged.relocations)==8270 and len([r for r in merged.relocations if r['owner'] in selected])==11,'new8259+11 RELA after6 discharges');need(not linked.relocations,'no linked residual relocation')
    globals=count(role(merged,s) for s in merged.symbols if s['name'] and s['info']>>4 in (1,2))
    for address,(short,size) in FLASH.items():
        owner=next(n for n,r in selected.items() if r['originalVA']==address);key=canonical(dict(name='tsl9_flash_'+short+'_'+format(address,'x'),owner=owner,offset=0,bytes=size,info=18,other=0));need(globals[key]==1,'one exact public Flash function role');globals[key]-=1
    need(counter_digest(+globals)==facts['global_role_digest'],'all original global/weak roles exact after six additions')
    for b in ctx['manifest']['section_relative_bindings']:
        s=[s for s in merged.symbols if s['name']==b['name']];need(len(s)==1 and role(merged,s[0])==b['role'],'all53 actual section-relative bindings')
    need(not any(s['name'] in DISCHARGED for s in merged.symbols),'six private labels absent, no false numeric aliases')
    regular=regular_roles(merged);need(counter_digest(count(r for r in regular if r['info']>>4==0))==facts['local_role_digest'],'all nonmetadata local/SECTION roles exact except six discharges')
    meta=Counter(facts['metadata'])
    for address in FLASH:
        owner=next(n for n,a in selected.items() if a['originalVA']==address);common=dict(owner=owner,offset=0,bytes=0,info=0,other=0);key=canonical(dict(name='$d',**common));need(meta[key]==1,'one original raw-code mapping');meta[key]-=1;meta[canonical(dict(name='$x',**common))]+=1
    for owner,name,info in [('.comment','$d',0),('ABS','$d',0),('ABS','flash_native.c',4)]:meta[canonical(dict(name=name,owner=owner,offset=0,bytes=0,info=info,other=0))]+=6
    need(+meta==metadata_counter(merged),'exact six d-to-x, six comment/attributes/FILE additions')
    linkedroles=count(regular_roles(linked,True));wanted=[]
    for r in regular_roles(merged,True):
        r=dict(r)
        if r['owner']=='UND':need(r['name']=='__tsl9v4160_rom_entry','sole exterior ROM numeric witness');r.update(owner='ABS',offset=0x40000)
        wanted.append(r)
    need(count(wanted)==linkedroles,'all actual linked symbol roles exact including40000 numeric witness')
    comment=canonical(dict(name='$d',owner='.comment',offset=0,bytes=0,info=0,other=0));need(meta[comment]==42,'one comment mapping per42 actual TUs');meta[comment]-=42
    need(+meta==metadata_counter(linked),'only42 unreferenced comment mappings dropped at final link')
    return dict(allocations=691,retained_storage_sections=680,outside_RELA=8259,total_RELA=8270,canonical_bindings=53,private_branches_discharged=sorted(DISCHARGED),global_local_section_roles_verified=True,metadata_exceptions='six d-to-x; six ABS d/comment/FILE additions; final42 unreferenced comment mappings dropped',archived_source_replay=ctx.get('archived_source_replay',False))


def machine_contracts(merged,linked,ctx):
    functions=[];calls=[];m=ctx['manifest'];selected=ctx['selected'];rawrefs=ctx['references'];flash_rows={};allboundaries={}
    for owner,allocation in selected.items():
        address=allocation['originalVA'];ref=rawrefs[address];section=linked.byname[owner];body=data(linked,section)
        need(body==ref['code'],'whole linked typed function equals sealed component '+ref['name'])
        syms=[s for s in linked.symbols if s['name']==ref['name']];need(len(syms)==1 and syms[0]['value']==address and syms[0]['size']==ref['bytes'] and syms[0]['info']==18,'actual typed FUNC entry and extent')
        if ref['family']=='IRQ':
            for r in ref['rows']:
                off=r['addr']-address;need(ctx['idecode'](body[off:off+r['size']],r['addr'])==r['decoded'],'priorIRQ raw checker operand identity')
            boundaries={r['addr'] for r in ref['rows']}
        else:
            short=ref['short']
            if short=='program':proof=ctx['program']['check_program'](body,ctx['decode']);rows=proof['rows']
            else:
                o=data(merged,merged.byname[owner]);refs=[r for r in merged.relocations if r['owner']==owner]
                rows=ctx['flash']['native_contract'](short,o,refs,ctx['decode'])
            flash_rows[owner]=rows;boundaries={address+r['offset'] for r in rows}
        allboundaries[owner]=boundaries
        functions.append(dict(name=ref['name'],owner=owner,address=address,bytes=len(body),code_sha256=SHA(body),normal_contract_identical_to_sealed_component=True))
    owned=[r for r in merged.relocations if r['owner'] in selected]
    need(len(owned)==11 and all(r['type']==17 and r['addend']==0 for r in owned),'eleven exact4B typed calls')
    for r in owned:
        a=selected[r['owner']];target=role(merged,r['symbol']);need(target['owner'] in selected and target['offset']==0,'typed call target is another function entry')
        expected=selected[target['owner']]['originalVA'];body=data(linked,linked.byname[r['owner']]);jump=direct_jump(body,r['offset'],a['originalVA'])
        need(jump['bytes']==4 and jump['rd']==1 and jump['target']==expected and jump['link'] in allboundaries[r['owner']],'typed JAL RA/target/continuation')
        calls.append(jump)
    branches=[]
    for old in ctx['plan']['old_owned_RELA']:
        if old['type'] not in (16,44):continue
        owner=old['owner'];r=next(r for r in flash_rows[owner] if r['offset']==old['offset'])
        need(r['op']=='bne' and r['target']==old['symbol']['offset'],'same actual decoded branch-role target after discharge')
        branches.append(dict(owner=owner,site=selected[owner]['originalVA']+r['offset'],target=selected[owner]['originalVA']+r['target'],old_symbol=old['symbol']['name'],native_register_operands=[r['rs1'],r['rs2']]))
    incoming=[]
    for expected in ctx['plan']['checks']['incoming']:
        owner=expected['owner'];base=m['allocations'][owner]['originalVA'];offset=expected['offset'];new=direct_jump(data(linked,linked.byname[owner]),offset,base)
        old=next(r for r in ctx['facts']['incoming'] if r['site']==base+offset)
        target=selected[expected['symbol']['owner']]['originalVA'];need(old==new and new['target']==target,'actual incoming width/rd/target/RA contract unchanged')
        incoming.append(new)
    need(len(incoming)==20 and sum(c['rd']==0 for c in incoming)==1 and sum(c['bytes']==2 for c in incoming)==2,'twenty incoming includingone JALx0 andtwo C.JAL')
    return dict(functions=functions,typed_calls=sorted(calls,key=lambda c:c['site']),six_branch_discharges=branches,twenty_incoming=sorted(incoming,key=lambda c:c['site']),source_program_boundary8_preserved=False,full_scratch_fault_prefix_equivalence=False,pointwise_async_equivalence=False)


def scatter(e,ctx):
    image=bytearray(76800);coverage=bytearray(76800);sections=0
    for s in alloc(e).values():
        if s['type']==8:continue
        start=s['address']-0x8000;body=data(e,s);need(0<=start and start+len(body)<=len(image),'each backed allocation inside image')
        need(not any(coverage[start:start+len(body)]),'no overlapping image ownership')
        image[start:start+len(body)]=body;coverage[start:start+len(body)]=b'\1'*len(body);sections+=1
    need(sections==690 and all(coverage),'all76800 bytes/690 file-backed owners without holes')
    return bytes(image)


def image_contract(linked,image,ctx):
    previous=bytearray(ctx['original'])
    for r in ctx['facts']['prior_IRQ_delta']:previous[r['offset']]=r['value']
    previous=bytes(previous);need(SHA(previous)=='47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c','independent complete prior IRQ image witness')
    expected=scatter(linked,ctx);need(image==expected,'actual producer image equals complete linked scatter')
    original=ctx['original'];changed=[dict(address=0x8000+i,original=a,new=b) for i,(a,b) in enumerate(zip(original,image)) if a!=b]
    changed_prior=[dict(address=0x8000+i,previous=a,new=b) for i,(a,b) in enumerate(zip(previous,image)) if a!=b]
    ranges=[(v['originalVA'],v['originalVA']+v['bytes']) for v in ctx['selected'].values()]
    need(all(any(a<=d['address']<b for a,b in ranges) for d in changed),'no original difference outside eleven owned functions')
    need(struct.unpack_from('<I',linked.raw,24)[0]==0x8000,'original ELF entry8000')
    return dict(bytes=76800,file_backed_sections=690,sha256=SHA(image),differences_from_original=changed,differences_from_prior_IRQ=changed_prior,changed_original_bytes=len(changed),changed_prior_bytes=len(changed_prior),complete_image_storage_verified=True,hardware_or_original_behavior_equivalence=False)


def verify(merged,linked,image,ctx):
    return dict(roles=sections_and_roles(merged,linked,ctx),machine=machine_contracts(merged,linked,ctx),image=image_contract(linked,image,ctx),load_segments=program_headers(linked))


def program_headers(e):
    offset=struct.unpack_from('<I',e.raw,28)[0];size,n=struct.unpack_from('<HH',e.raw,42)
    need(size==32 and offset+n*size<=len(e.raw),'bounded ELF32 program headers');owned=alloc(e);seen=Counter();loads=[];special=[]
    for i in range(n):
        kind,fileoff,va,pa,filesz,memsz,flags,align=struct.unpack_from('<8I',e.raw,offset+i*size)
        need(fileoff+filesz<=len(e.raw),'bounded segment file bytes')
        if kind==1:
            need(va==pa and align==4096 and (va-fileoff)%align==0 and memsz>0,'original physical/virtual LOAD placement and alignment')
            members=[s for s in owned.values() if va<=s['address'] and s['address']+s['size']<=va+memsz]
            need(members and min(s['address'] for s in members)==va and max(s['address']+s['size'] for s in members)==va+memsz and sum(s['size'] for s in members)==memsz,'LOAD memory extent exactly owned without extra tail or gap')
            need(all(flags==(4|(2 if s['flags']&1 else 0)|(1 if s['flags']&4 else 0)) for s in members),'LOAD flags equal exact member permissions')
            backed=[s for s in members if s['type']!=8];need((filesz==memsz and len(backed)==len(members)) or (filesz==0 and not backed),'LOAD file/memory NOBITS distinction')
            for s in members:
                seen[s['name']]+=1
                if s['type']!=8:need(s['offset']==fileoff+s['address']-va,'LOAD bytes correspond to actual section file offsets')
            loads.append(dict(address=va,physical=pa,file_bytes=filesz,memory_bytes=memsz,flags=flags,members=len(members)))
        elif kind==0x6474e551:
            need((fileoff,va,pa,filesz,memsz,flags,align)==(0,0,0,0,0,6,0),'nonexecutable zero-size GNU stack');special.append(kind)
        elif kind==0x70000003:
            a=e.byname['.riscv.attributes'];need((fileoff,va,pa,filesz,memsz,flags,align)==(a['offset'],0,0,a['size'],a['size'],4,1),'RISC-V attributes segment exact');special.append(kind)
        else:raise ValueError('unexpected program header kind')
    need(seen==Counter({name:1 for name in owned}),'all691 allocations owned by exactlyone LOAD');need(sorted(special)==[0x6474e551,0x70000003],'exact two nonLOAD headers')
    return dict(segments=loads,all691_memory_extents_and_permissions_verified=True)


class BytesInput:
    def __init__(self,b):self.b=b
    def read_bytes(self):return self.b


def symbol_offset(e,predicate):
    hits=[]
    for table,entries in e.symbol_tables.items():
        for i,s in enumerate(entries):
            if predicate(s):hits.append(e.sections[table]['offset']+i*16)
    need(len(hits)==1,'one actual symbol mutation location');return hits[0]


def rela_offset(e,predicate):
    hits=[]
    for s in e.sections:
        if s['type']!=4:continue
        owner=e.sections[s['info']]['name'];symbols=e.symbol_tables[s['link']]
        for pos in range(s['offset'],s['offset']+s['size'],12):
            site,info,addend=struct.unpack_from('<IIi',e.raw,pos)
            if predicate(dict(owner=owner,offset=site,type=info&255,addend=addend,symbol=symbols[info>>8])):hits.append(pos)
    need(len(hits)==1,'one actual RELA mutation location');return hits[0]


def negative_controls(merged,linked,image,ctx):
    """Mutate actual artifact bytes in memory; reparse ELF before applying the named semantic gate."""
    ledger=[];ELF=ctx['ELF'];selected=ctx['selected'];refs=ctx['references']
    def reject(label,kind,offset,replacement,gate=None):
        original={'merged':merged.raw,'linked':linked.raw,'image':image}[kind];mutated=bytearray(original);old=bytes(mutated[offset:offset+len(replacement)]);need(old!=replacement,'negative really changes actual bytes');mutated[offset:offset+len(replacement)]=replacement;mutated=bytes(mutated)
        try:
            a=ELF(BytesInput(mutated)) if kind=='merged' else merged;b=ELF(BytesInput(mutated)) if kind=='linked' else linked;c=mutated if kind=='image' else image
            (gate or verify)(a,b,c,ctx)
        except (ValueError,KeyError,IndexError,struct.error) as exc:reason=str(exc)
        else:raise ValueError('negative unexpectedly accepted: '+label)
        ledger.append(dict(name=label,artifact=kind,offset=offset,before=old.hex(),after=replacement.hex(),original_sha256=SHA(original),mutated_sha256=SHA(mutated),rejected=True,reason=reason))
    def u32(kind,label,pos,value,gate=None):reject(label,kind,pos,struct.pack('<I',value),gate)
    outside=next(s for s in alloc(merged).values() if s['name'] not in selected and s['type']!=8 and s['size'])
    pos=outside['offset'];reject('outside-carrier-byte','merged',pos,bytes([merged.raw[pos]^1]))
    r=next(r for r in merged.relocations if r['owner'] not in selected);pos=rela_offset(merged,lambda a:a==r)
    u32('merged','outside-RELA-addend',pos+8,(r['addend']+2)&0xffffffff)
    info=struct.unpack_from('<I',merged.raw,pos+4)[0];u32('merged','outside-RELA-type',pos+4,(info&~255)|((r['type']+1)&255))
    binding=ctx['manifest']['section_relative_bindings'][0]['name'];pos=symbol_offset(merged,lambda s:s['name']==binding);value=struct.unpack_from('<I',merged.raw,pos+4)[0];u32('merged','canonical-interior-binding',pos+4,value+2)
    name='tsl9_flash_program_18ef2';pos=symbol_offset(merged,lambda s:s['name']==name);u32('merged','typed-FUNC-extent94-not100',pos+8,94)
    reject('typed-FUNC-kind-object','merged',pos+12,b'\x11')
    owner=next(n for n,r in selected.items() if r['originalVA']==0x18ef2);s=merged.byname[owner];shoff=struct.unpack_from('<I',merged.raw,32)[0];u32('merged','selected-owner-alignment',shoff+s['index']*40+32,s['alignment']*2)
    s=next(s for s in alloc(merged).values() if s['type']==8);u32('merged','NOBITS-resident-size',shoff+s['index']*40+20,s['size']+4)
    matches=[(table,i,s) for table,entries in merged.symbol_tables.items() for i,s in enumerate(entries) if re.fullmatch(r'\$d(?:\.\d+)?',s['name']) and s['index']==0xfff1 and not s['value']]
    need(len(matches)==42,'actual prior36 plusnew6 ABS metadata');table,i,s=matches[0];u32('merged','ABS-metadata-not-zero',merged.sections[table]['offset']+i*16+4,2)
    pos=symbol_offset(linked,lambda s:s['name']=='__tsl9v4160_rom_entry');u32('linked','ROM-witness40002',pos+4,0x40002)
    pos=symbol_offset(linked,lambda s:s['name']==binding);value=struct.unpack_from('<I',linked.raw,pos+4)[0];u32('linked','linked-canonical-binding',pos+4,value+2)
    def incoming_gate(a,b,c,d):machine_contracts(a,b,d)
    def at(address):
        s=next(s for s in alloc(linked).values() if s['type']!=8 and s['address']<=address<s['address']+s['size']);return s['offset']+address-s['address']
    pos=at(0x18906);word=struct.unpack_from('<I',linked.raw,pos)[0];u32('linked','tail-JAL-x0-becomes-ra',pos+0,(word&~(31<<7))|(1<<7),incoming_gate)
    pos=at(0x9d00);half=struct.unpack_from('<H',linked.raw,pos)[0];reject('incoming-CJAL-becomes-CJ','linked',pos,struct.pack('<H',(half&0x1fff)|(5<<13)),incoming_gate)
    incoming=next(x for x in ctx['facts']['incoming'] if x['bytes']==4 and x['rd']==1);pos=at(incoming['site']);word=struct.unpack_from('<I',linked.raw,pos)[0];u32('linked','incoming-JAL-target-plus2',pos,word^(1<<21),incoming_gate)
    site=0x9a42+0x1c;pos=at(site);word=struct.unpack_from('<I',linked.raw,pos)[0]
    expected=direct_jump(data(linked,linked.byname[next(n for n,r in selected.items() if r['originalVA']==0x9a42)]),0x1c,0x9a42)
    def typed_gate(a,b,c,d):
        s=next(s for s in alloc(b).values() if s['address']==0x9a42);need(direct_jump(data(b,s),0x1c,0x9a42)==expected,'typed helper call must retain rd1 target and RA continuation')
    u32('linked','typed-helper-JAL-becomes-tail',pos,word&~(31<<7),typed_gate)
    pos=at(0x18ef2+6);half=struct.unpack_from('<H',linked.raw,pos)[0]
    def program_gate(a,b,c,d):d['program']['check_program'](data(b,b.byname[owner]),d['decode'])
    reject('program-alignment-immediate','linked',pos,struct.pack('<H',half^4),program_gate)
    reject('image-outside-owner-byte','image',0,bytes([image[0]^1]),lambda a,b,c,d:image_contract(b,c,d))
    pos=0x18ef2-0x8000;reject('image-typed-owner-byte','image',pos,bytes([image[pos]^1]),lambda a,b,c,d:image_contract(b,c,d))
    phoff=struct.unpack_from('<I',linked.raw,28)[0];memsz=struct.unpack_from('<I',linked.raw,phoff+20)[0]
    u32('linked','LOAD-unowned-memory-tail',phoff+20,memsz+2,lambda a,b,c,d:program_headers(b))
    flags=struct.unpack_from('<I',linked.raw,phoff+24)[0];u32('linked','LOAD-permissions-writable-code',phoff+24,flags|2,lambda a,b,c,d:program_headers(b))
    need(len(ledger)==20,'bounded twenty actual artifact controls');return ledger


def relative(root,path):
    try:return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:return str(path.resolve())


def input_path(root,path):
    p=Path(path);return p if p.is_absolute() else root/p


def inspect_folder(root,folder,firmware=None,parser=None):
    ctx=context(root,parser=parser,firmware=firmware);files=dict(merged=folder/'source-integrated.o',linked=folder/'ADDRESS-WITNESS-ONLY.elf',image=folder/'NOT-FLASH-VALIDATED-irq-and-flash.bin');artifacts={k:dict(path=relative(root,p),bytes=p.stat().st_size,sha256=SHA(p.read_bytes())) for k,p in files.items()}
    merged=ctx['ELF'](files['merged']);linked=ctx['ELF'](files['linked']);image=files['image'].read_bytes();checks=verify(merged,linked,image,ctx);controls=negative_controls(merged,linked,image,ctx)
    producer=folder/'verification.json';producer_ref=None
    if producer.is_file():
        r=json.loads(producer.read_bytes());need(r.get('schema')=='TSL9-eleven-readable-source-image-v1' and r.get('passed') is True,'actual producer receipt schema/pass');producer_ref=dict(path=relative(root,producer),sha256=SHA(producer.read_bytes()),mode=r['mode'],runner_sha256=r['runner_sha256'],manifest_sha256=r['manifest_sha256'])
    fw=firmware or root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    return dict(schema='TSL9-independent-eleven-image-ABI-review-v1',passed=True,reviewer_sha256=SHA(Path(__file__).read_bytes()),baseline_sha256=BASELINE_SHA,firmware_path=relative(root,fw),artifacts=artifacts,producer=producer_ref,checks=checks,actual_artifact_negative_controls=controls,execution='Static parsing and raw instruction decoding only; no RV32 execution, emulation, device or network I/O.',archived_prior_object_required=False)


def replay(root,receipt,firmware=None,parser=None):
    report=json.loads(receipt.read_bytes());need(report.get('schema')=='TSL9-independent-eleven-image-ABI-review-v1' and report.get('passed') is True,'independent review receipt schema/pass')
    need(report['reviewer_sha256']==SHA(Path(__file__).read_bytes()) and report['baseline_sha256']==BASELINE_SHA,'independent checker and baseline pins')
    paths={k:input_path(root,r['path']) for k,r in report['artifacts'].items()}
    for k,p in paths.items():need(p.stat().st_size==report['artifacts'][k]['bytes'] and SHA(p.read_bytes())==report['artifacts'][k]['sha256'],'actual replay artifact pin '+k)
    if report['producer']:
        p=input_path(root,report['producer']['path']);need(SHA(p.read_bytes())==report['producer']['sha256'],'actual replay producer receipt pin')
    firmware=firmware or input_path(root,report['firmware_path']);ctx=context(root,parser=parser,firmware=firmware);a=ctx['ELF'](paths['merged']);b=ctx['ELF'](paths['linked']);c=paths['image'].read_bytes()
    need(verify(a,b,c,ctx)==report['checks'],'fresh independent semantic result replay');need(negative_controls(a,b,c,ctx)==report['actual_artifact_negative_controls'],'actual twenty artifact controls replay')
    return dict(passed=True,receipt=relative(root,receipt),image_sha256=SHA(c),actual_artifact_controls=20,archived_prior_object_required=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--project-root',type=Path,default=ROOT);ap.add_argument('--folder',type=Path);ap.add_argument('--receipt',type=Path);ap.add_argument('--replay',type=Path);ap.add_argument('--firmware',type=Path);ap.add_argument('--parser',type=Path);a=ap.parse_args();root=a.project_root.resolve()
    if a.replay:result=replay(root,a.replay.resolve(),a.firmware,a.parser)
    else:
        need(a.folder is not None and a.receipt is not None,'fresh review requires --folder and --receipt');result=inspect_folder(root,a.folder.resolve(),a.firmware,a.parser);a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_bytes((json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8'));result=dict(passed=True,receipt=str(a.receipt),sha256=SHA(a.receipt.read_bytes()),actual_artifact_controls=20,image_sha256=result['checks']['image']['sha256'])
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))


if __name__=='__main__':main()
