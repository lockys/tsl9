"""Independent ELF-byte/role contracts for explicit source entry wiring; no ISA state execution."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import re
import struct

OLD='__tsl9v4160_ota_code_9c4a'
NEW='tsl9_ota_handler_native_9c4a'
ROM='__tsl9v4160_rom_entry'
BODY='b486c6eed0d3465c8947fd338e790f1441f29c64827a47b20e1fada18ff863af'
BASE={'c':('85c674487c0bf2b0bbcbc3f0f5607d82dd07014acaf0634cfd45525ccdcdf456','6ab2e06720dc9f9ea4fa531836605fed6d3b8832a7dfa008d76bd9bd0a54f7b2'),
      'cpp':('e0407c603786c3b747f3a8646a142a1b0ea8c8e47921f5058a31f0577a1a2f4b','a2e8629c2109cf17a11bb990c5ff61223477138cb33587f694c6d07150d4dbb2')}
IMAGE='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89'
NAMES={'__tsl9v4160_ota_code_92f2','__tsl9v4160_call_9c0a','__tsl9v4160_call_9124',
       '__tsl9v4160_ota_code_13f66','__tsl9v4160_conditional_code_13e98','__tsl9v4160_ota_code_9b8e',
       '__tsl9v4160_ota_code_8e18','__tsl9v4160_ota_code_9ee0','__tsl9v4160_captured_body_99e8'}
def need(v,m):
    if not v:raise ValueError(m)
def H(blob):return hashlib.sha256(blob).hexdigest()
def sha(path):return H(Path(path).read_bytes())
def case(root,n):return next(p for p in (root/'apk-analysis'/('tsl9-'+n),root/'analysis'/n) if p.is_dir())
def parser(root):
    p=case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py'
    need(sha(p)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Pinned bounded ELF reader')
    return runpy.run_path(str(p))['ELF']
def symbol(e,name):
    found=[s for s in e.symbols if s['name']==name];need(len(found)==1,'Unique symbol '+name);return found[0]
def role(e,s):return (s['name'],e.sections[s['index']]['name'] if 0<s['index']<len(e.sections) else s['index'],s['value'],s['size'],s['info'],s['other'])
def rel(e,r,replace=None):
    return (r['owner'],r['offset'],r['type'],r['addend'],*(replace[r['symbol']['name']] if replace and r['symbol']['name'] in replace else role(e,r['symbol'])))
def allocations(e):
    a=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len({s['name'] for s in a})==len(a),'Unique allocated owners')
    return {s['name']:(s['type'],s['flags'],s['alignment'],s['size'],None if s['type']==8 else H(e.data(s))) for s in a}
def ordinary(s):return s['info'] not in (3,4) and not s['name'].startswith(('$d','$x'))
def role_counter(e,replace=None):return Counter(replace.get(s['name'],role(e,s)) if replace else role(e,s) for s in e.symbols if ordinary(s))
def undef(e):return {s['name'] for s in e.symbols if s['index']==0 and s['name']}
def allocated_provider(e,s):return 0<s['index']<len(e.sections) and bool(e.sections[s['index']]['flags']&2)
def metadata_roles(e,linked=None):
    out=[]
    for s in e.symbols:
        if ordinary(s) or (linked and s['info']==3):continue
        r=list(role(e,s));r[0]=re.sub(r'\.\d+$','',r[0]) if r[0].startswith(('$d','$x')) else r[0]
        if linked and isinstance(r[1],str):
            if r[1]=='.comment':
                need(r==['$d','.comment',0,0,0,0], 'Only nonprovider zero comment mapping marker may be discarded');continue
            need(r[1] in linked.byname,'Retained final metadata owner');r[2]+=linked.byname[r[1]]['address']
        out.append(tuple(r))
    return Counter(out)
def metadata(base,native,tail,merged,linked):
    expected=metadata_roles(base)+metadata_roles(native)+metadata_roles(tail)
    removed=('$d','.riscv.attributes',0,0,0,0);need(expected[removed]==2,'Exactly2 real input attribute mapping markers')
    expected[removed]-=2;expected[('$d',65521,0,0,0,0)]+=2
    for e in (native,tail):
        sec=next(s for s in e.sections if s['flags']&2 and s['size'])
        expected[('',sec['name'],0,0,3,0)]+=1
    need(+expected==metadata_roles(merged),'Every metadata role retained with only2attributeABS conversions and2actualSECTION additions')
    need(not [s for s in linked.symbols if s['info']==3] and metadata_roles(merged,linked)==metadata_roles(linked),
         'Final FILE/code mappings genuinely placed; only SECTION and discarded comment mapping metadata removed')
    for name in ('.comment','.riscv.attributes'):
        need(merged.data(merged.byname[name])==base.data(base.byname[name]),'Retained partial metadata payload '+name)
    need('.comment' not in linked.byname and linked.data(linked.byname['.riscv.attributes'])==base.data(base.byname['.riscv.attributes']),
         'Historical final linker discards comment only; ISA attributes retained')
    need(native.data(native.byname['.comment'])==base.data(base.byname['.comment']) and native.data(native.byname['.riscv.attributes'])==base.data(base.byname['.riscv.attributes']),
         'Same actual compiler comment/ISA attribute inputs')
    sig=native.byname['.llvm_addrsig'];payload=native.data(sig)
    need(payload==bytes((5,7,9,11)) and sig['flags']==0x80000000 and sig['type']==0x6fff4c03,'Actual excluded native addrsig payload')
    actual=[native.symbol_tables[sig['link']][i]['name'] for i in payload]
    need(actual==[NEW,'__tsl9v4160_ota_code_8e18','__tsl9v4160_ota_code_9ee0','__tsl9v4160_captured_body_99e8'],'Input addrsig roles have actual source origin')
    need('.llvm_addrsig' not in tail.byname and merged.data(merged.byname['.llvm_addrsig'])==base.data(base.byname['.llvm_addrsig'])+payload and '.llvm_addrsig' not in linked.byname,
         'Exact excluded addrsig concatenation then final removal, not an addressprovider')
    return dict(metadata_role_preservation=True,attribute_markers_converted_to_nonprovider_ABS=2,new_allocated_SECTION_roles=2,
                addrsig_native_bytes=4,addrsig_partial_bytes=62,addrsig_final_absent=True,final_comment_payload_and_mapping_removed=True)
def weakened(base,copy):
    need(base.kind==copy.kind==1 and base.flags==copy.flags==1,'Real RV32C ET_REL base/copy')
    need(allocations(base)==allocations(copy) and len(allocations(base))==691,'All691 baseline allocation bytes/attributes retained by objcopy')
    old=symbol(base,OLD);weak=symbol(copy,OLD)
    need(old['info']==16 and weak==dict(old,info=32),'Only original GLOBAL NOTYPE becomes WEAK NOTYPE')
    expected=Counter(role(base,s) if s['name']!=OLD else role(copy,weak) for s in base.symbols)
    need(expected==Counter(role(copy,s) for s in copy.symbols),'Every base symbol role preserved except intended binding')
    need(Counter(rel(base,r,{OLD:role(copy,weak)}) for r in base.relocations)==Counter(rel(copy,r) for r in copy.relocations),
         'All8261 base relocation semantics survive exact weakening')
    need(len(base.relocations)==8261 and undef(base)==undef(copy)=={ROM},'Baseline relocation count and trueROM UND')
    return dict(allocated_owners=691,base_RELA=8261,weak_binding_only=True)
def partial(base,native,tail,merged):
    need(all(e.kind==1 and e.flags==1 for e in (native,tail,merged)),'Actual native/data/merged RV32C ET_REL')
    alias=symbol(native,OLD);entry=symbol(native,NEW)
    need(alias['info']==entry['info']==18 and alias['other']==entry['other']==0 and alias['size']==entry['size']==568,
         'Two truthful GLOBAL FUNC568 aliases')
    need(alias['index']==entry['index'] and alias['value']==entry['value']==0 and allocated_provider(native,alias),
         'Strong alias shares same actual allocated C body')
    need(H(native.function_bytes(alias))==BODY and len(allocations(native))==1,'Fresh C payload equals frozen compact kernel; no helper storage')
    need(undef(native)==NAMES and len(native.relocations)==20,'Actual nine UND and20 kernel relocations')
    need(not undef(tail) and not tail.relocations,'Tail fill introduces no unresolved provider or relocation')
    ta=allocations(tail);need(len(ta)==1,'One explicit tail data owner')
    ts=next(s for s in tail.sections if s['name'] in ta)
    need(ts['size']==456 and ts['type']==1 and not ts['flags']&4 and tail.data(ts)==b'\xff'*456,'Explicit456-byte nonexecuting FF page fill')
    ba,na,ma=allocations(base),allocations(native),allocations(merged)
    need(not set(ba)&(set(na)|set(ta)) and not set(na)&set(ta) and ma==dict(ba,**na,**ta),'Every original owner plus only realC568/nonexec456')
    providers={n:role(base,symbol(base,n)) for n in NAMES}
    need(all(allocated_provider(base,symbol(base,n)) for n in NAMES),'Nine actual allocated providers, neverABS')
    strong=role(merged,symbol(merged,OLD));fresh=role(merged,symbol(merged,NEW))
    need(strong[1:]==fresh[1:] and strong[3:]==(568,18,0),'Merged strong canonical alias has trueC extent')
    expected=Counter(rel(base,r,{OLD:strong}) for r in base.relocations)+Counter(rel(native,r,providers) for r in native.relocations)
    need(Counter(rel(merged,r) for r in merged.relocations)==expected,'Complete base/native RELA union and exact canonical preemption')
    need(undef(merged)=={ROM},'Partial still has sole trueROM UND')
    expected_roles=role_counter(base,{OLD:strong})
    expected_roles+=Counter(role(native,s) for s in native.symbols if ordinary(s) and s['index']!=0)
    expected_roles+=Counter(role(tail,s) for s in tail.symbols if ordinary(s) and s['index']!=0)
    # Strong canonical role coalesces into the preempted old role, not a second provider.
    expected_roles[role(native,alias)]-=1
    need(+expected_roles==role_counter(merged),'All nonmetadata symbol roles preserved plus actual source aliases')
    return dict(allocations=len(ma),RELA=len(merged.relocations),actual_allocated_providers=9,remaining_true_UND=[ROM],
                source_FUNC_alias_bytes=568,old530_retained=True,ROM_provider_proved=False)
def jal(raw,pc):
    w=int.from_bytes(raw,'little');need(len(raw)==4 and w&0x7f==0x6f,'Actual4-byte JAL instruction')
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    if imm&(1<<20):imm-=1<<21
    return ((w>>7)&31,(pc+imm)&0xffffffff,pc+4)
def loads(e):
    off=struct.unpack_from('<I',e.raw,28)[0];size,num=struct.unpack_from('<HH',e.raw,42)
    need(size==32 and off+num*size<=len(e.raw),'Bounded actual program headers');out=[]
    for i in range(num):
        typ,fo,va,pa,fs,ms,flags,align=struct.unpack_from('<8I',e.raw,off+i*size)
        if typ!=1:continue
        need(fs<=ms and fo+fs<=len(e.raw) and va==pa and align and align&(align-1)==0,'RealLOAD file/memory/address/alignment bounds')
        out.append(dict(offset=fo,address=va,filesz=fs,memsz=ms,flags=flags,align=align))
    for s in e.sections:
        if not s['flags']&2 or not s['size']:continue
        matches=[p for p in out if p['address']<=s['address'] and s['address']+s['size']<=p['address']+(p['memsz'] if s['type']==8 else p['filesz'])
                 and (s['type']==8 or p['offset']+s['address']-p['address']==s['offset'])]
        need(len(matches)==1,'Allocated section has exact unique LOAD coverage '+s['name'])
        p=matches[0];need(p['flags']&4 and bool(p['flags']&1)==bool(s['flags']&4) and (not s['flags']&1 or p['flags']&2),'ActualLOAD permissions coversection')
    return out
def linked_symbols(merged,linked):
    expected=[]
    for s in merged.symbols:
        if not ordinary(s):continue
        if s['index']==0 and s['name']==ROM:
            expected.append((ROM,65521,0x40000,0,16,0));continue
        r=list(role(merged,s))
        if 0<s['index']<len(merged.sections):
            name=merged.sections[s['index']]['name'];need(name in linked.byname,'Real linked symbol owner')
            r[2]+=linked.byname[name]['address']
        expected.append(tuple(r))
    need(Counter(expected)==role_counter(linked),'Every ordinary merged symbol is genuinely placed; only ROM numericwitness resolution')
def relocated_component(native,linked):
    symbol_native=symbol(native,NEW);owner=native.sections[symbol_native['index']]['name']
    raw=native.function_bytes(symbol_native);body=linked.function_bytes(symbol(linked,NEW));need(len(raw)==len(body)==568,'Exact physical C body')
    covered=set();facts=[]
    for r in native.relocations:
        need(r['owner']==owner and r['addend']==0 and r['type'] in (17,26,27),'Actual bounded C relocation kind/site')
        at=r['offset'];need(at%2==0 and at+4<=len(raw) and not covered.intersection(range(at,at+4)),'Nonoverlapping fullinstruction relocation')
        covered.update(range(at,at+4));before=int.from_bytes(raw[at:at+4],'little');after=int.from_bytes(body[at:at+4],'little')
        target=symbol(linked,r['symbol']['name']);need(allocated_provider(linked,target),'Actual allocated directcallee/callback target')
        if r['type']==17:
            need(before&0xfff==after&0xfff and jal(body[at:at+4],0x1ac00+at)==(1,target['value'],0x1ac04+at),'Actual final directJAL target/link/RA')
        elif r['type']==26:
            need(before&0xfff==after&0xfff and after&0x7f==0x37 and after&0xfffff000==(target['value']+0x800)&0xfffff000,'Actual allocated callback HI20')
        else:
            imm=after>>20;imm=imm-4096 if imm&2048 else imm
            want=target['value']&4095;want=want-4096 if want&2048 else want
            need(before&0xfffff==after&0xfffff and after&0x707f==0x13 and imm==want,'Actual allocated callback LO12')
        facts.append(dict(offset=at,type=r['type'],target=r['symbol']['name'],actual_address=target['value']))
    need(all(a==b for i,(a,b) in enumerate(zip(raw,body)) if i not in covered),'All C bytes outside20 actual relocations unchanged')
    need(len(facts)==20,'All20 native relocations checked');return facts
def final(base,merged,linked,base_image,image):
    need(base.kind==linked.kind==2 and merged.kind==1,'Actual linked witnesses and partial')
    ba=allocations(base);ma=allocations(merged);la=allocations(linked)
    need(set(ma)==set(la) and len(la)==693 and len(ba)==691,'Exact693 actual final allocated owners')
    changed=[]
    for name in ba:
        a,b=base.byname[name],linked.byname[name]
        need(all(a[k]==b[k] for k in ('type','flags','alignment','size','address')),'All prior allocated addresses/attributes unchanged')
        if a['type']==8:continue
        old,new=base.data(a),linked.data(b)
        if old!=new:
            need(a['address']<=0x14094 and 0x14098<=a['address']+a['size'],'Only real ingress owner may differ')
            at=0x14094-a['address'];need(old[:at]==new[:at] and old[at+4:]==new[at+4:],'Only caller JAL word changes in original owner')
            need(jal(new[at:at+4],0x14094)==(1,0x1ac00,0x14098),'Real caller now links to allocatedC while retaining14098 return')
            changed.append(name)
    need(len(changed)==1,'Exactly one changed original allocation owner')
    alias=symbol(linked,OLD);fresh=symbol(linked,NEW)
    need(role(linked,alias)[1:]==role(linked,fresh)[1:] and alias['value']==0x1ac00 and alias['size']==568 and alias['info']==18,
         'Real final allocated C aliases1AC00/FUNC568')
    need(allocated_provider(linked,alias) and linked.function_bytes(alias)==linked.data(linked.sections[alias['index']]),'No fake alias or borrowed extent')
    for name in NAMES:
        s=symbol(linked,name);need(allocated_provider(linked,s),'All nine final actual allocated providers')
    rom=symbol(linked,ROM);need((rom['index'],rom['value'],rom['size'],rom['info'],rom['other'])==(65521,0x40000,0,16,0),
                               'NumericROM address witness explicitly remains ABS, never installedproviderproof')
    need(not undef(linked),'Witness is numerically resolved, not a provider admission')
    linked_symbols(merged,linked)
    need(H(base_image)==IMAGE and len(base_image)==76800 and len(image)==77824,'Old75page image plus one explicit1024byte page')
    at=0x14094-0x8000;need(image[:at]==base_image[:at] and image[at+4:76800]==base_image[at+4:],'Every original image byte except oneJAL word preserved')
    need(jal(image[at:at+4],0x14094)==(1,0x1ac00,0x14098),'Actual flatimage caller is wired to realC')
    need(image[76800:76800+568]==linked.function_bytes(alias) and image[-456:]==b'\xff'*456,'Appended bytes solely actual linkedC plus explicitnonexecpagefill')
    mapped=[]
    for s in linked.sections:
        if s['flags']&2 and s['type']!=8 and s['size']:
            need(0x8000<=s['address'] and s['address']+s['size']<=0x1b000,'File-backed allocation inside explicitimage interval')
            need(image[s['address']-0x8000:s['address']-0x8000+s['size']]==linked.data(s),'Actual ELF section equals flatimage bytes')
            mapped.append((s['address'],s['address']+s['size']))
    mapped.sort();need(all(a[1]<=b[0] for a,b in zip(mapped,mapped[1:])),'No overlapping file-backed allocations')
    return dict(image_bytes=len(image),image_sha256=H(image),changed_original_owners=changed,newC_address=0x1ac00,actual_caller_RA=0x14098,
                explicit_nonexec_fill_bytes=456,LOADs=loads(linked),actual_reroute=True,source_entry_wiring_proved=True,
                installed_ROM_provider_proved=False,physical_capacity_or_free_storage_proved=False,full_ABI_admitted=False,hardware_OTA_proved=False)
