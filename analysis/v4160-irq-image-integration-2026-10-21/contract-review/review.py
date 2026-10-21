"""Independent full ELF/image contract checker. Reads artifacts; never builds them."""
from pathlib import Path
import argparse,collections,hashlib,importlib.util,json,re,struct
H=Path(__file__).resolve().parent;R=H.parents[2]
PLAN=R/'apk-analysis/tsl9-v4160-irq-callframe-2026-10-21/image-plan/verification.json'
PARSER=R/'apk-analysis/tsl9-v4160-reset-memory-2026-10-21/compiler-review/elf32.py'
BASE=R/'experiments/tsl9-v4160-startup/build/image-fidelity-999d8125159a4d80bd6df9153f267002'
ORIGINAL=R/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
spec=importlib.util.spec_from_file_location('read_elf',PARSER);E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def role(e,s):
    return (s['name'],e.sections[s['index']]['name'] if 0<s['index']<len(e.sections) else ('UND' if s['index']==0 else 'ABS' if s['index']==0xfff1 else 'SPECIAL:'+str(s['index'])),s['value'],s['size'],s['info'],s['other'])
def rela(e,r):return (r['owner'],r['offset'],r['type'],role(e,r['symbol']),r['addend'])
def data(e,s):return b'' if s['type']==8 else e.data(s)
def globals_(e):return collections.Counter(role(e,s) for s in e.symbols if s['name'] and s['info']>>4 in (1,2))
def refs(e):return {role(e,r['symbol']) for r in e.relocations}
def metadata(e,s,referenced):
    rr=role(e,s)
    if rr in referenced:return False
    if s['info']==0 and not s['size'] and not s['value'] and not s['other'] and re.fullmatch(r'\$(?:d|x)(?:\.\d+)?',s['name']):return True
    if s['info']==4 and s['index']==0xfff1 and not s['size'] and not s['value'] and not s['other']:return True
    return False

def baseline():
    need(sha(PLAN)=='281d2628e7e47b138ca581010e6c9fa670367f792e80d5e3e4130ab9fb4ac38b','sealed image-plan receipt pin')
    p=json.loads(PLAN.read_text());b=E.ELF(BASE/'c/source-image-merged.o');linked=E.ELF(BASE/'c/ADDRESS-WITNESS-ONLY.elf')
    need(sha(BASE/'c/source-image-merged.o')=='646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97','baseline carrier pin')
    need(sha(ORIGINAL)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','original BIN pin')
    selected={s['name']:s for s in p['selected_sections']};alloc={s['name']:s for s in b.sections if s['flags']&2 and s['size']}
    need(len(alloc)==691 and len(b.relocations)==8280,'baseline691/8280')
    return p,b,linked,selected,alloc

def compare_merged(new,b,selected,alloc,p):
    need(new.kind==1 and new.flags==b.flags==1,'new object ET_REL/RVC flags')
    actual={s['name']:s for s in new.sections if s['flags']&2 and s['size']}
    need(set(actual)==set(alloc),'exact691 allocation names/no extra storage')
    for name,old in alloc.items():
        q=actual[name]
        need(all(q[k]==old[k] for k in ['type','flags','size','alignment','entry_size','address']),'allocation type/flags/size/alignment/entry-size/relativeVA '+name)
        if name not in selected:need(data(new,q)==data(b,old),'retained686 storage '+name)
    need(len(new.relocations)==8276,'new8276 RELA')
    before=collections.Counter(rela(b,r) for r in b.relocations if r['owner'] not in selected)
    after=collections.Counter(rela(new,r) for r in new.relocations if r['owner'] not in selected)
    need(sum(before.values())==8270 and before==after,'all8270 outside-owned RELA role/addend multiset')
    names=[s['name'] for s in new.symbols if s['name'] and s['info']>>4 in (1,2)]
    need(len(names)==len(set(names)),'no duplicated named global/weak records')
    oldglobals=globals_(b);newglobals=globals_(new)
    need(not oldglobals-newglobals,'every original global/weak role including true aliases and ROM UND')
    extras=newglobals-oldglobals;expected=collections.Counter()
    for name,s in selected.items():expected[(s['new_C_symbol'],name,0,s['bytes'],18,0)]+=1
    need(extras==expected,'exact five additional public C function roles')
    und=[s['name'] for s in new.symbols if s['name'] and s['index']==0]
    need(und==['__tsl9v4160_rom_entry'],'sole true ROM UND, no numeric closure')
    for binding in p['section_relative_bindings']:
        q=next(s for s in new.symbols if s['name']==binding['name']);rr=binding['role']
        need(role(new,q)==(rr['name'],rr['owner'],rr['offset'],0,16,0),'canonical53 binding role')
    nr=refs(new);br=refs(b)
    # Only source-private branch labels discharged with their own four old RELA.
    discharged={'.Lfrontier_00019132','.Lfrontier_00019150','.Lfrontier_0001916e','.Lfrontier_0001918c'}
    for name in discharged:
        old=next(s for s in b.symbols if s['name']==name)
        users=[r for r in b.relocations if role(b,r['symbol'])==role(b,old)]
        need(len(users)==1 and users[0]['owner'] in selected and users[0]['type']==44,'private branch label sole old use')
    oldlocals=collections.Counter(role(b,s) for s in b.symbols if s['info']>>4==0 and not metadata(b,s,br) and s['name'] not in discharged)
    newlocals=collections.Counter(role(new,s) for s in new.symbols if s['info']>>4==0 and not metadata(new,s,nr))
    # Original selected SECTION records stay; compiler-private local labels may
    # additionally occur only inside the selected five sections.
    need(not oldlocals-newlocals,'all nonmetadata old local/SECTION roles retained')
    extra_local=newlocals-oldlocals
    need(all(rr[1] in selected and rr[4] in (0,3) and rr[5]==0 for rr in extra_local),'extra locals limited to selected compiler blocks/SECTION records')
    owned=[r for r in new.relocations if r['owner'] in selected]
    main='.text.tsl9v4160.init_9a42'
    expected_calls=[(0x1c,'19142'),(0x28,'19124'),(0x32,'1917e'),(0x3c,'1917e'),(0x46,'19160'),(0x50,'19160')]
    expected_owned=collections.Counter()
    for offset,suffix in expected_calls:
        owner='.text.tsl9v4160.frontier_'+suffix;public=selected[owner]['new_C_symbol'];alias=selected[owner]['global_alias']
        rr=(public,owner,0,30,18,0)
        expected_owned[(main,offset,17,rr,0)]+=1
    need(collections.Counter(rela(new,r) for r in owned)==expected_owned,'six exact native main JALs/helper RELA zero')
    original=ORIGINAL.read_bytes();diffs=p['probes'][0]['differences']
    for name,s in selected.items():
        blob=bytearray(data(new,new.byname[name]));expected=bytearray(original[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']])
        for d in diffs:
            if s['originalVA']<=d['address']<s['originalVA']+s['bytes']:expected[d['address']-s['originalVA']]=d['native']
        if name==main:
            for offset,_ in expected_calls:
                word=int.from_bytes(blob[offset:offset+4],'little');need(word&127==111 and ((word>>7)&31)==1,'native unrelocated call is4B JAL RA')
                blob[offset:offset+4]=b'\0'*4;expected[offset:offset+4]=b'\0'*4
        need(blob==expected,'selected native bytes outside exact six relocation fields '+name)
    mapping_removed=[role(b,s) for s in b.symbols if metadata(b,s,br)]
    mapping_added=[role(new,s) for s in new.symbols if metadata(new,s,nr)]
    def mapping_counter(rows):
        return collections.Counter((rr[0].split('.')[0],)+rr[1:] for rr in rows if re.fullmatch(r'\$(?:d|x)(?:\.\d+)?',rr[0]))
    expected_mapping=mapping_counter(mapping_removed)
    for name in selected:
        need(expected_mapping[('$d',name,0,0,0,0)]==1,'one old raw data mapping per selected section')
        expected_mapping[('$d',name,0,0,0,0)]-=1
        expected_mapping[('$x',name,0,0,0,0)]+=1
    expected_mapping[('$d','.comment',0,0,0,0)]+=2
    expected_mapping[('$d','ABS',0,0,0,0)]+=2
    need(+expected_mapping==mapping_counter(mapping_added),'only exact five d-to-x and two comment/attributes mapping additions')
    oldfiles=collections.Counter(rr for rr in mapping_removed if rr[4]==4)
    expectedfiles=oldfiles+collections.Counter([(n,'ABS',0,0,4,0) for n in ['interrupt_callframe.c','rcc_helpers.c']])
    need(expectedfiles==collections.Counter(rr for rr in mapping_added if rr[4]==4),'exact two new typed FILE records')
    return dict(allocations=691,retained_storage_sections=686,outside_RELA=8270,total_RELA=8276,canonical_bindings=53,
                private_labels_discharged=sorted(discharged),extra_selected_local_roles=list(extra_local.elements()),old_unreferenced_mapping_file_roles=mapping_removed,new_unreferenced_mapping_file_roles=mapping_added)

def compare_linked(new,b,selected,alloc,p,image):
    need(new.kind==2 and new.flags==b.flags==1 and not new.relocations,'new linked ET_EXEC/RVC witness without RELA')
    need(struct.unpack_from('<I',new.raw,24)[0]==0x8000,'original ELF image entry8000')
    actual={s['name']:s for s in new.sections if s['flags']&2 and s['size']}
    need(set(actual)==set(alloc),'linked exact691 allocation names')
    original=ORIGINAL.read_bytes();allowed={d['address']:(d['original'],d['native']) for d in p['probes'][0]['differences']}
    need(set(allowed)==set(range(0x9a44,0x9a4c)),'sealed exact8 permitted values')
    observed={};backed={}
    for name,old in alloc.items():
        q=actual[name];expected=b.byname[name]
        need(all(q[k]==expected[k] for k in ['address','type','flags','size','alignment','entry_size']),'linked original placement/role '+name)
        if q['type']==8:need(q['size']==35160,'RAM35160 NOBITS');continue
        raw=data(new,q);need(q['address']>=0x8000 and q['address']+len(raw)<=0x1ac00,'file section inside source range')
        for i,value in enumerate(raw):
            addr=q['address']+i;need(addr not in backed,'no source section overlap');backed[addr]=value
            oldvalue=original[addr-0x8000]
            if value!=oldvalue:observed[addr]=(oldvalue,value)
    need(observed==allowed,'exact eight linked instruction-byte differences')
    need(set(backed)==set(range(0x8000,0x1ac00)),'all76800 source bytes section-backed/no holes')
    need(len(image)==76800 and all(image[a-0x8000]==v for a,v in backed.items()),'image length and linked section byte equality')
    diffs={0x8000+i:(a,c) for i,(a,c) in enumerate(zip(original,image)) if a!=c}
    need(diffs==allowed,'flat image exact eight byte values only')
    und=[s['name'] for s in new.symbols if s['name'] and s['index']==0];need(not und,'numeric witness has no UND')
    rom=next(s for s in new.symbols if s['name']=='__tsl9v4160_rom_entry');need(rom['index']==0xfff1 and rom['value']==0x40000 and rom['size']==0,'ROM remains explicit numeric ABS witness only')
    linkedglobals=globals_(new);oldglobals=globals_(b)
    extras=collections.Counter((s['new_C_symbol'],name,s['originalVA'],s['bytes'],18,0) for name,s in selected.items())
    need(linkedglobals==oldglobals+extras,'exact original linked globals plus five public C roles')
    for name,s in selected.items():need(linkedglobals[(s['new_C_symbol'],name,s['originalVA'],s['bytes'],18,0)]==1,'public C function at originalVA')
    phoff=struct.unpack_from('<I',new.raw,28)[0];stride,count=struct.unpack_from('<HH',new.raw,42);need(stride==32,'ELF32 program headers')
    loads={};headers=[]
    for i in range(count):
        kind,off,va,pa,filesz,memsz,flags,align=struct.unpack_from('<8I',new.raw,phoff+i*stride)
        if kind!=1:continue
        need(va==pa,'LOAD VMA equals physical/LMA')
        need(not filesz or 0x8000<=va<va+filesz<=0x1ac00,'no extra file-backed LOAD range')
        need(off+filesz<=len(new.raw),'LOAD raw bounds')
        for j,value in enumerate(new.raw[off:off+filesz]):
            a=va+j;need(a not in loads or loads[a]==value,'unambiguous LOAD overlap');loads[a]=value
        headers.append(dict(VA=va,PA=pa,file_bytes=filesz,memory_bytes=memsz,flags=flags,alignment=align))
    need(loads==backed,'actual LOAD contents equal all sections/image; RAM excluded')
    return dict(allocations=691,file_sections=690,image_bytes=76800,changed_bytes=[dict(address=a,original=v[0],native=v[1]) for a,v in sorted(observed.items())],LOAD_headers=headers,ROM_implementation_supplied=False)

class BytesInput:
    def __init__(self,raw):self.raw=raw
    def read_bytes(self):return self.raw

def symbol_offset(e,name):
    matches=[]
    for table in e.sections:
        if table['type']!=2:continue
        for i,s in enumerate(e.symbol_tables[table['index']]):
            if s['name']==name:matches.append(table['offset']+i*16)
    need(len(matches)==1,'one raw named symbol record');return matches[0]

def negative_controls(n,linked,image,b,bl,selected,alloc,p):
    results=[]
    def rejected(name,kind,raw):
        try:
            if kind=='merged':compare_merged(E.ELF(BytesInput(raw)),b,selected,alloc,p)
            elif kind=='linked':compare_linked(E.ELF(BytesInput(raw)),bl,selected,alloc,p,image)
            else:compare_linked(linked,bl,selected,alloc,p,raw)
        except (ValueError,KeyError,StopIteration,struct.error) as exc:
            results.append(dict(name=name,artifact=kind,rejected=True,reason=str(exc),mutated_sha256=hashlib.sha256(raw).hexdigest()))
        else:raise ValueError('mutated artifact accepted '+name)
    for name,symbol,field,value in [('old_provider_ABS','__tsl9v4160_call_9a42','index',0xfff1),('public_helper_wrong_size','tsl9_rebuild_rcc_registers_19124','size',29),('numeric_ROM_in_partial','__tsl9v4160_rom_entry','index',0xfff1),('canonical_binding_ABS',p['section_relative_bindings'][0]['name'],'index',0xfff1)]:
        raw=bytearray(n.raw);off=symbol_offset(n,symbol)
        struct.pack_into('<H' if field=='index' else '<I',raw,off+(14 if field=='index' else 8),value)
        rejected(name,'merged',bytes(raw))
    tables=[s for s in n.sections if s['type']==4 and s['size'] and n.sections[s['info']]['name'] not in selected]
    table=tables[0];raw=bytearray(n.raw);off=table['offset']+8;struct.pack_into('<i',raw,off,struct.unpack_from('<i',raw,off)[0]+1);rejected('outside_RELA_addend','merged',bytes(raw))
    raw=bytearray(n.raw);shoff=struct.unpack_from('<I',raw,32)[0];struct.pack_into('<I',raw,shoff+table['index']*40+20,table['size']-12);rejected('missing_outside_RELA','merged',bytes(raw))
    q=next(s for s in n.sections if s['flags']&4 and s['size'] and s['name'] not in selected);raw=bytearray(n.raw);raw[q['offset']]^=1;rejected('retained_instruction_byte','merged',bytes(raw))
    q=next(s for s in n.sections if not s['flags']&2 and s['type']==1 and s['size'] and s['name'] in ['.comment','.riscv.attributes']);raw=bytearray(n.raw);struct.pack_into('<I',raw,shoff+q['index']*40+8,q['flags']|2);rejected('extra_allocated_metadata','merged',bytes(raw))
    q=n.byname['.bss.tsl9v4160.ram'];raw=bytearray(n.raw);struct.pack_into('<I',raw,shoff+q['index']*40+4,1);rejected('RAM_becomes_file_backed','merged',bytes(raw))
    table=next(s for s in n.sections if s['type']==4 and s['size'] and n.sections[s['info']]['name']=='.text.tsl9v4160.init_9a42');raw=bytearray(n.raw);struct.pack_into('<i',raw,table['offset']+8,2);rejected('new_main_call_addend','merged',bytes(raw))
    raw=bytearray(linked.raw);shoff=struct.unpack_from('<I',raw,32)[0];q=linked.byname['.text.tsl9v4160.init_9a42'];struct.pack_into('<I',raw,shoff+q['index']*40+12,q['address']+2);rejected('linked_main_VA_shift','linked',bytes(raw))
    raw=bytearray(linked.raw);phoff=struct.unpack_from('<I',raw,28)[0];stride,count=struct.unpack_from('<HH',raw,42)
    site=next(phoff+i*stride for i in range(count) if struct.unpack_from('<I',raw,phoff+i*stride)[0]==1)
    struct.pack_into('<I',raw,site+12,struct.unpack_from('<I',raw,site+12)[0]+4);rejected('LOAD_physical_address_shift','linked',bytes(raw))
    raw=bytearray(linked.raw);struct.pack_into('<I',raw,24,0x8002);rejected('ELF_entry_shift','linked',bytes(raw))
    raw=bytearray(image);raw[0]^=1;rejected('image_outside_allowed_bytes','image',bytes(raw))
    raw=bytearray(image);raw[0x9a44-0x8000]^=1;rejected('image_wrong_value_inside_allowed_range','image',bytes(raw))
    rejected('image_truncated','image',image[:-1]);rejected('image_appended','image',image+b'\0')
    need(len(results)==17,'seventeen actual in-memory raw countercases');return results

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--merged',type=Path,required=True);ap.add_argument('--linked',type=Path,required=True);ap.add_argument('--image',type=Path,required=True);ap.add_argument('--label',choices=['c','cpp'],required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    need(a.output.resolve().is_relative_to(H),'review output stays in own scope')
    p,b,bl,selected,alloc=baseline();n=E.ELF(a.merged);linked=E.ELF(a.linked);image=a.image.read_bytes()
    merged=compare_merged(n,b,selected,alloc,p);li=compare_linked(linked,bl,selected,alloc,p,image);negatives=negative_controls(n,linked,image,b,bl,selected,alloc,p)
    result=dict(schema='TSL9-full-source-integration-independent-contract-review-v1',passed=True,label=a.label,
       inputs=[dict(path=str(q.resolve()),sha256=sha(q)) for q in [PARSER,PLAN,BASE/'c/source-image-merged.o',BASE/'c/ADDRESS-WITNESS-ONLY.elf',ORIGINAL,a.merged,a.linked,a.image]],merged=merged,linked=li,actual_raw_negative_controls=negatives,
       limits=dict(independent_build_performed=False,source_provenance_checked_by_this_artifact_CLI=False,RV32_execution=False,hardware=False,network=False,asynchronous_equivalence=False,ROM_implementation_supplied=False,OTA_verified=False,flashable=False))
    if a.output.exists():need(json.loads(a.output.read_text())==result,'readonly review replay exact')
    else:a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,label=a.label,allocations=691,RELA=8276,differences=8,output=str(a.output),sha256=sha(a.output))))
if __name__=='__main__':main()
