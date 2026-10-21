#!/usr/bin/env python3
"""Independent data-only ELF/relocation/LOAD/BIN admission; no target execution."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct

ORIGINAL='646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97'
PRIOR='9a5bd413ce37d618859031c4246f55a717b4c0cc64063adaee9c933ef07179b9'
IRQ_ELF='e05fca68de182150f103fc8f18e1476c607a32c12c36e44c0d505dcaf12cf977'
FLASH_ELF='aeccc19da9c5764a386333dd26898429c35bf0ff40efb08c8f8417b11820339d'
FIRMWARE='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ROM='__tsl9v4160_rom_entry'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,slug):return next(p for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def roles(e,s,linked=False):
    i=s['index'];owner=e.sections[i]['name'] if 0<i<len(e.sections) else 'UND' if i==0 else 'ABS'
    offset=s['value']-(e.sections[i]['address'] if linked and 0<i<len(e.sections) else 0)
    return {'name':s['name'],'owner':owner,'offset':offset,'bytes':s['size'],'info':s['info'],'other':s['other']}
def relocation(e,r):return {'owner':r['owner'],'offset':r['offset'],'type':r['type'],'addend':r['addend'],'symbol':roles(e,r['symbol'])}
def counter(rows):return collections.Counter(json.dumps(x,sort_keys=True,separators=(',',':')) for x in rows)
def allocated(e):return {s['name']:s for s in e.sections if s['flags']&2 and s['size']}
def content(e,s):return b'' if s['type']==8 else e.data(s)
def filter_intervals(raw,selected):
    lines=raw.splitlines(keepends=True);literals={}
    for i,line in enumerate(lines):
        text=line.strip()
        if text.startswith(b'"'):literals[i]=json.loads(text)
    deleted=set()
    for row in selected:
        starts=[i for i,text in literals.items() if text.startswith('.section '+row['name']+',')]
        need(len(starts)==1,'One exact quoted assembly owner');start=starts[0]
        ends=[i for i,text in literals.items() if i>=start and text=='.size '+row['global_alias']+','+str(row['bytes'])+'\n']
        need(len(ends)==1,'One exact declared owner terminator');end=ends[0]
        need(all(i in literals for i in range(start,end+1)),'Only quoted assembly is removed')
        need(not any(literals[i].startswith('.section ') for i in range(start+1,end+1)),'No next owner crossed by removal')
        span=set(range(start,end+1));need(not deleted&span,'Nonoverlapping selected source intervals');deleted|=span
    return b''.join(line for i,line in enumerate(lines) if i not in deleted)
def named_semantics(e,discharged=(),linked=False):
    skip=counter(discharged);rows=[]
    for s in e.symbols:
        r=roles(e,s,linked);name=r['name'];typ=r['info']&15
        if typ in (3,4):continue
        if re.fullmatch(r'\$[dx]\.\d+',name):
            need(r['info']==r['bytes']==r['other']==0,'Mapping metadata has no provider type/size/visibility');continue
        if not name:
            need(r['info']==r['offset']==r['bytes']==r['other']==0,'Only empty null metadata is excluded');continue
        key=json.dumps(r,sort_keys=True,separators=(',',':'))
        if skip[key]:skip[key]-=1;continue
        rows.append(r)
    need(not any(skip.values()),'Every discharged private role existed exactly once')
    return rows
def prepare(root,firmware,original_path,prior_path,irq_path,flash_path):
    need(sha(firmware)==FIRMWARE and firmware.stat().st_size==76800,'Exact original image')
    manifest_path=root/'experiments/tsl9-v4160-irq-image-integration/source-manifest.json'
    need(sha(manifest_path)=='d952159ab2bf7c5294bc433510b88a7c19b23295ba11b0e7ab3d4a1ed39b1ce7','Pinned original full manifest');m=read(manifest_path)
    plan=case(root,'v4160-flash-entry-order-2026-10-22')/'image-plan'
    need(sha(plan/'seal.json')=='5cacfc4682a0e493ca6826f86b855a46a386155db3da1cf56c283f021a3b7bfe','Sealed eleven-function source plan')
    for x in read(plan/'seal.json')['members']:need(sha(plan/x['path'])==x['sha256'],'Sealed source plan member')
    p=read(plan/'report.json');selected=p['selected'];names={x['name'] for x in selected};need(len(names)==11 and sum(x['bytes'] for x in selected)==526,'Eleven exact owned extents')
    parser=case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py';need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Bounded read-only ELF parser');E=load('independent_image_ELF',parser).ELF
    for path,pin in ((original_path,ORIGINAL),(prior_path,PRIOR),(irq_path,IRQ_ELF),(flash_path,FLASH_ELF)):need(sha(path)==pin,'Actual pinned source/component object')
    original=E(original_path);prior=E(prior_path);irq=E(irq_path);flash=E(flash_path)
    need(len(original.relocations)==8280 and len(prior.relocations)==8276,'Original and previous integration counts stay distinct')
    def outside(e):return [relocation(e,r) for r in e.relocations if r['owner'] not in names]
    out=outside(prior);need(len(out)==8259 and counter(out)==counter(outside(original)),'All8259 outside role/site/type/signed-addend/multiplicity records match both baselines')
    need(digest(sorted(out,key=lambda x:json.dumps(x,sort_keys=True)))==p['outside_RELA_semantic_sha256'],'Independent outside records match sealed plan digest')
    old_owned=[relocation(prior,r) for r in prior.relocations if r['owner'] in names];original_owned=[relocation(original,r) for r in original.relocations if r['owner'] in names]
    need(len(old_owned)==17 and len(original_owned)==21,'Four original IRQ branches already discharged in prior carrier')
    incoming=[r for r in out if r['symbol']['owner'] in names];need(len(incoming)==20 and all(r['symbol']['offset']==0 for r in incoming),'Exactly20 known external entry references')
    for b in m['section_relative_bindings']:
        need(b['role']['owner'] not in names,'Canonical53 roles are outside selected owners')
        need(counter([roles(original,s) for s in original.symbols if s['name']==b['name']])==counter([b['role']]) and counter([roles(prior,s) for s in prior.symbols if s['name']==b['name']])==counter([b['role']]),'Every original/prior relative binding role')
    need(len(m['section_relative_bindings'])==53,'All53 relative bindings')
    filters=[]
    for row in p['filtered_carrier_units']:
        raw=(root/row['path']).read_bytes();need(hashlib.sha256(raw).hexdigest()==row['before_sha256'],'Pinned carrier source')
        after=filter_intervals(raw,[x for x in selected if x['producer']==row['path']]);need(hashlib.sha256(after).hexdigest()==row['filtered_sha256'] and len(raw)-len(after)==row['removed_source_bytes'],'Independent exact quoted-interval filter')
        filters.append({'path':row['path'],'removed':row['removed'],'sha256':hashlib.sha256(after).hexdigest(),'bytes':len(after)})
    need(len(filters)==4 and len(m['source_units'])==34,'Four source filters/34 original TUs')
    public={r['name']:r['new_C_symbol'] for r in m['selected_sections']}
    flash_names={0x9c0a:'quarter',0x18e90:'status',0x18e98:'unlock',0x18eb6:'lock',0x18ec4:'erase',0x18ef2:'program'}
    public.update({r['name']:'tsl9_flash_'+flash_names[r['originalVA']]+'_'+format(r['originalVA'],'x') for r in selected if r['originalVA'] in flash_names})
    expected=bytearray(firmware.read_bytes());native={}
    for row in selected:
        e=flash if row['originalVA'] in flash_names else irq
        symbol=next(s for s in e.symbols if s['name']==public[row['name']]);need(symbol['value']==row['originalVA'] and symbol['size']==row['bytes'] and symbol['info']==18,'Actual sealed-component typed function at original VA')
        body=e.function_bytes(symbol);native[row['name']]=body;off=row['originalVA']-0x8000;expected[off:off+len(body)]=body
    retained=set(m['allocations'])-names;need(len(retained)==680,'All680 retained allocation owners')
    for name in retained:need(content(original,original.byname[name])==content(prior,prior.byname[name]),'Raw retained storage unchanged between baselines')
    new_owned=[]
    for row in old_owned:
        if row['type'] in (16,44):continue
        need(row['type']==17 and row['addend']==0,'Only eleven direct JAL source roles remain')
        value=json.loads(json.dumps(row));value['symbol']['name']=public[value['symbol']['owner']];new_owned.append(value)
    need(len(new_owned)==11,'Expected native JAL multiplicity derived from actual baseline, not byte budget')
    prior_discharged=[r['symbol'] for r in old_owned if r['type'] in (16,44)]
    original_discharged=[r['symbol'] for r in original_owned if r['type'] in (16,44)]
    addition=lambda row:{'name':public[row['name']],'owner':row['name'],'offset':0,'bytes':row['bytes'],'info':18,'other':0}
    expected_roles=named_semantics(prior,prior_discharged)+[addition(r) for r in selected if r['originalVA'] in flash_names]
    need(counter(expected_roles)==counter(named_semantics(original,original_discharged)+[addition(r) for r in selected]),'Independent original21/prior17 discharge yields the same final named roles')
    return {'E':E,'m':m,'plan':p,'selected':selected,'names':names,'original':original,'prior':prior,'outside':out,'incoming':incoming,'old_owned':old_owned,'original_owned':original_owned,'new_owned':new_owned,'public':public,'native':native,'expected':bytes(expected),'original_bytes':firmware.read_bytes(),'retained':retained,'filters':filters,'retained_hashes':{n:hashlib.sha256(content(prior,prior.byname[n])).hexdigest() for n in retained},'expected_named_semantic_sha256':digest(sorted(expected_roles,key=lambda r:json.dumps(r,sort_keys=True)))}
def allocation_gate(e,c,linked=False):
    actual=allocated(e);m=c['m'];need(set(actual)==set(m['allocations']) and len(actual)==691,'All691 original allocations, no missing/extra raw storage')
    for name,s in actual.items():
        need({k:s[k] for k in ('type','flags','size','alignment','entry_size')}==m['section_metadata'][name],'Original exact section metadata '+name)
        if linked:need(s['address']==m['allocations'][name]['originalVA'],'Exact original section VA '+name)
def canonical_code(body,relocations):
    raw=bytearray(body)
    for r in relocations:
        need(r['type']==17 and r['offset']+4<=len(raw),'Only expected direct JAL fixups normalized')
        off=r['offset'];w=int.from_bytes(raw[off:off+4],'little');need(w&127==0x6f,'Actual JAL instruction at relocation');raw[off:off+4]=(w&0xfff).to_bytes(4,'little')
    return bytes(raw)
def retained_context(root,firmware,reference):
    """Use hashes independently derived from W baselines; do not pretend to reread them."""
    q=read(reference);need(sha(firmware)==q['original_firmware_sha256'] and firmware.stat().st_size==76800,'Original image for portable artifact admission')
    old_path=root/'experiments/tsl9-v4160-irq-image-integration/source-manifest.json';need(sha(old_path)==q['original_manifest_sha256'],'Immutable original section metadata manifest');m=read(old_path)
    manifest=root/'experiments/tsl9-v4160-flash-image-integration/source-manifest.json';need(sha(manifest)=='afe5eba6e7b6af15c9556fa9c9a366e5c4713dcbf343b16d2d8077eb6c1b4b1c','Current eleven-function source ledger');n=read(manifest)
    need(n['allocations']==m['allocations'] and n['section_metadata']==m['section_metadata'] and n['section_relative_bindings']==m['section_relative_bindings'],'All original691 owners/metadata and53 canonical bindings retained')
    selected=q['selected'];names={r['name'] for r in selected};retained=set(m['allocations'])-names
    hashes={name:r['sha256'] for name,r in n['retained_storage'].items()};need(set(hashes)==retained and digest(hashes)==q['retained_raw_hashes_digest'],'All680 raw retained hashes anchored to actual independent baseline reads')
    need(len(n['source_files'])==76 and len(n['source_units'])==34,'Actual native source ledger cardinality')
    for path,pin in n['source_files'].items():need(sha(root/path)==pin,'Pinned project source/header '+path)
    groups={}
    for r in selected:groups.setdefault(r['producer'],[]).append(r)
    for r in q['filters']:
        value=filter_intervals((root/r['path']).read_bytes(),groups[r['path']]);need(hashlib.sha256(value).hexdigest()==r['sha256'],'Independent source interval filtering')
    native={};raw=firmware.read_bytes();expected=bytearray(raw)
    need(len(n['selected_sections'])==11 and {r['name'] for r in n['selected_sections']}==names,'Exact eleven source-derived native owners')
    for r in n['selected_sections']:
        source=next(x for x in selected if x['name']==r['name']);need(all(r[k]==v for k,v in source.items()) and r['new_C_symbol']==q['public'][r['name']],'Original native entry/alias/storage/source role')
        body=bytes.fromhex(r['native_linked_bytes']);need(len(body)==r['bytes'] and hashlib.sha256(body).hexdigest()==q['expected_native_hashes'][r['name']],'Native linked byte ledger independently anchored to sealed component ELFs')
        off=r['originalVA']-0x8000;need(raw[off:off+r['bytes']].hex()==r['original_bytes'],'Actual original source bytes before overlay');expected[off:off+r['bytes']]=body;native[r['name']]=body
    differences=[{'address':0x8000+i,'original':a,'native':b} for i,(a,b) in enumerate(zip(raw,expected)) if a!=b]
    need(differences==n['expected_differences'] and len(differences)==70 and hashlib.sha256(expected).hexdigest()==q['expected_image_sha256'],'Independent native overlay and exact70 changed byte values')
    parser=case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py';need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Reviewed bounded ELF parser')
    return {'E':load('portable_independent_ELF',parser).ELF,'m':m,'new_manifest':n,'selected':selected,'names':names,'retained':retained,'retained_hashes':hashes,'outside_sha256':q['outside_RELA_sha256'],'incoming':q['incoming'],'new_owned':q['new_owned'],'public':q['public'],'native':native,'expected':bytes(expected),'original_bytes':raw,'expected_named_semantic_sha256':q['expected_named_semantic_sha256'],'filters':q['filters'],'original_baseline_archives_replayed':False}
def artifact_gate(obj,linked,bin_path,c):
    need(obj.kind==1 and obj.flags==1 and linked.kind==2 and linked.flags==1,'RV32 integer partial/linked ELF identity');allocation_gate(obj,c);allocation_gate(linked,c,True)
    outside=[relocation(obj,r) for r in obj.relocations if r['owner'] not in c['names']];inside=[relocation(obj,r) for r in obj.relocations if r['owner'] in c['names']]
    expected_outside=c.get('outside_sha256') or digest(sorted(c['outside'],key=lambda r:json.dumps(r,sort_keys=True)))
    need(len(outside)==8259 and digest(sorted(outside,key=lambda r:json.dumps(r,sort_keys=True)))==expected_outside,'Exact outside8259 role/multiplicity records')
    need(len(inside)==11 and counter(inside)==counter(c['new_owned']) and len(obj.relocations)==8270,'Actual eleven typed JALs replace17prior/21original owned relocations')
    need(counter([r for r in outside if r['symbol']['owner'] in c['names']])==counter(c['incoming']),'All20 actual incoming aliases retained at entries')
    for name in c['retained']:need(hashlib.sha256(content(obj,obj.byname[name])).hexdigest()==c['retained_hashes'][name],'Exact retained raw storage '+name)
    for row in c['selected']:
        name=row['name'];rels=[r for r in inside if r['owner']==name]
        need(canonical_code(obj.data(obj.byname[name]),rels)==canonical_code(c['native'][name],rels),'Typed partial code matches sealed native components modulo actual JAL fields')
        need(linked.data(linked.byname[name])==c['native'][name],'Linked typed code equals actual sealed native code')
        for symbol in (row['global_alias'],c['public'][name]):
            expected={'name':symbol,'owner':name,'offset':0,'bytes':row['bytes'],'info':18,'other':0}
            need(counter([roles(obj,s) for s in obj.symbols if s['name']==symbol])==counter([expected]) and counter([roles(linked,s,True) for s in linked.symbols if s['name']==symbol])==counter([expected]),'Real section-owned FUNC alias/provider '+symbol)
    need(digest(sorted(named_semantics(obj),key=lambda r:json.dumps(r,sort_keys=True)))==c['expected_named_semantic_sha256'],'Every independently derived nonmetadata role, with precise original/prior discharges and typed additions')
    for b in c['m']['section_relative_bindings']:
        need(counter([roles(obj,s) for s in obj.symbols if s['name']==b['name']])==counter([b['role']]) and counter([roles(linked,s,True) for s in linked.symbols if s['name']==b['name']])==counter([b['role']]),'Actual53 section-relative canonical roles; no ABS shortcut')
    need({s['name'] for s in obj.symbols if not s['index'] and s['name']}=={ROM},'Sole actual ROM undefined provider remains')
    need(not linked.relocations and not any(s['name'] and not s['index'] for s in linked.symbols),'Numerical witness fully linked, not real ROM-provider proof')
    expected_linked=[r for r in named_semantics(obj) if r['name']!=ROM]+[{'name':ROM,'owner':'ABS','offset':0x40000,'bytes':0,'info':16,'other':0}]
    need(counter(named_semantics(linked,linked=True))==counter(expected_linked),'All linked nonmetadata symbol roles plus sole numeric ROM witness, no added/interior ABS providers')
    source={};section_memory={}
    for name,s in allocated(linked).items():
        permissions=4|(1 if s['flags']&4 else 0)|(2 if s['flags']&1 else 0)
        for j in range(s['size']):
            a=s['address']+j;need(a not in section_memory,'No section memory overlap');section_memory[a]=permissions
        if s['type']==8:need(name=='.bss.tsl9v4160.ram' and s['address']==0x20004000 and s['size']==35160,'Exact RAM NOBITS allocation');continue
        for j,b in enumerate(linked.data(s)):
            a=s['address']+j;need(a not in source,'No section byte overlap');source[a]=b
    need(set(source)==set(range(0x8000,0x1ac00)),'File-backed sections cover exactly original image range')
    phoff=struct.unpack_from('<I',linked.raw,28)[0];entsize,count=struct.unpack_from('<HH',linked.raw,42);need(entsize==32 and phoff+count*32<=len(linked.raw),'Bounded real ELF program headers')
    loaded={};load_memory={};segments=[]
    for i in range(count):
        typ,off,va,pa,filesz,memsz,flags,align=struct.unpack_from('<8I',linked.raw,phoff+i*32)
        if typ!=1:continue
        need(va==pa and filesz<=memsz and off+filesz<=len(linked.raw),'Actual LOAD physical/virtual/file bounds')
        need(flags&~7==0 and flags&4,'LOAD readable integer permissions')
        if filesz:need(0x8000<=va<va+filesz<=0x1ac00 and filesz==memsz,'Exact file LOAD memory bounds, no hidden zero tail')
        else:need(va==0x20004000 and memsz==35160 and flags==6,'Only original RAM has exact non-file-backed LOAD storage')
        for j in range(memsz):
            a=va+j;need(a not in load_memory or load_memory[a]==flags,'Unambiguous memory LOAD permissions');load_memory[a]=flags
        for j,b in enumerate(linked.raw[off:off+filesz]):
            a=va+j;need(a not in loaded or loaded[a]==b,'No ambiguous LOAD overlap');loaded[a]=b
        segments.append({'VA':va,'PA':pa,'file_bytes':filesz,'memory_bytes':memsz,'flags':flags,'alignment':align})
    candidate=bin_path.read_bytes();need(len(candidate)==76800 and source==loaded and section_memory==load_memory,'Actual section and LOAD file/memory/permission coverage agree')
    need(bytes(source[a] for a in range(0x8000,0x1ac00))==candidate==c['expected'],'Actual sections=LOAD=BIN=independent sealed-native overlay')
    need(struct.unpack_from('<I',linked.raw,24)[0]==0x8000,'Original reset entry')
    return {'allocations':691,'retained_allocations':680,'typed_allocations':11,'outside_RELA':8259,'actual_owned_RELA':len(inside),'total_RELA':len(obj.relocations),'incoming_entry_RELA':20,'relative_bindings':53,'image_bytes':len(candidate),'image_sha256':hashlib.sha256(candidate).hexdigest(),'differences_from_original':sum(a!=b for a,b in zip(candidate,c['original_bytes'])),'LOADs':segments,'actual_sections_LOAD_BIN_equal':True,'numeric_ROM_witness_only':True,'target_execution':False,'hardware':False,'OTA_ready':False}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--original-object',type=Path,required=True);p.add_argument('--prior-object',type=Path,required=True);p.add_argument('--IRQ-elf',dest='irq',type=Path,required=True);p.add_argument('--Flash-elf',dest='flash',type=Path,required=True);p.add_argument('--new-object',type=Path);p.add_argument('--new-elf',type=Path);p.add_argument('--new-bin',type=Path);p.add_argument('--output',type=Path);p.add_argument('--reference',type=Path);a=p.parse_args();c=prepare(a.project_root.resolve(strict=True),a.firmware,a.original_object,a.prior_object,a.irq,a.flash)
    r={'schema':'ID2966-independent-eleven-function-image-review-v1','passed':True,'original_RELA':8280,'prior_IRQ_RELA':8276,'outside_RELA':8259,'old_original_owned_RELA':21,'old_prior_owned_RELA':17,'native_owned_expected':11,'typed_bytes':526,'filters':c['filters'],'independent_expected_image_sha256':hashlib.sha256(c['expected']).hexdigest(),'expected_differences':sum(a!=b for a,b in zip(c['expected'],c['original_bytes'])),'artifact_checks':None,'target_execution':False,'hardware':False,'network':False,'OTA_ready':False}
    if a.new_object or a.new_elf or a.new_bin:
        need(all((a.new_object,a.new_elf,a.new_bin)),'Allthree actual image artifacts required');r['artifact_checks']=artifact_gate(c['E'](a.new_object),c['E'](a.new_elf),a.new_bin,c)
    if a.reference:need(r==read(a.reference),'Exact bound independent source/artifact review')
    if a.output:
        out=a.output.resolve();out.relative_to(Path(__file__).resolve().parent);need(not out.exists(),'Create-only own independent report');out.write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(r if not a.output else {'passed':True,'report':str(a.output),'expected_sha256':r['independent_expected_image_sha256'],'artifact_checks':r['artifact_checks']}))
if __name__=='__main__':main()
