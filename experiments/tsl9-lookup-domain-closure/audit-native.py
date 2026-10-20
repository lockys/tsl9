"""Independent ELF32/RELA/address audit. This never runs target instructions."""
from pathlib import Path
import argparse,hashlib,json,struct,re
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(test,message):
 if not test:raise AssertionError(message)
class ELF:
 def __init__(self,path):
  self.raw=Path(path).read_bytes();b=self.raw
  require(len(b)>=52 and b[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<HH',b,16)==(1,243),'RV32 LE ET_REL header')
  at=struct.unpack_from('<I',b,32)[0];size,count,strings=struct.unpack_from('<HHH',b,46)
  require(size==40 and at+count*40<=len(b) and strings<count,'Section header bounds')
  self.sections=[]
  for i in range(count):
   v=struct.unpack_from('<10I',b,at+i*40)
   require(v[1]==8 or v[4]+v[5]<=len(b),'Section payload bounds')
   self.sections.append(dict(index=i,name_offset=v[0],type=v[1],flags=v[2],addr=v[3],offset=v[4],size=v[5],link=v[6],info=v[7],align=v[8],entsize=v[9]))
  st=self.sections[strings];names=b[st['offset']:st['offset']+st['size']]
  def string(buf,off):
   require(off<len(buf) and b'\0' in buf[off:],'String bounds');return buf[off:buf.index(0,off)].decode('ascii')
  for s in self.sections:s['name']=string(names,s['name_offset'])
  self.names={s['name']:s for s in self.sections if s['name']};self.symbols=[];tables={}
  for s in self.sections:
   if s['type']!=2:continue
   require(s['entsize']==16 and s['size']%16==0 and s['link']<count,'Symbol table bounds')
   st=self.sections[s['link']];buf=b[st['offset']:st['offset']+st['size']];table=[]
   for at in range(s['offset'],s['offset']+s['size'],16):
    name,val,n,info,other,idx=struct.unpack_from('<IIIBBH',b,at)
    sym=dict(name=string(buf,name),value=val,size=n,binding=info>>4,type=info&15,visibility=other&3,index=idx)
    table.append(sym);self.symbols.append(sym)
   tables[s['index']]=table
  self.rel=[]
  for s in self.sections:
   require(s['type']!=9 or not s['size'],'Unexpected REL table')
   if s['type']!=4:continue
   require(s['entsize']==12 and s['size']%12==0 and s['link'] in tables and s['info']<count,'RELA table bounds')
   for at in range(s['offset'],s['offset']+s['size'],12):
    off,info,add=struct.unpack_from('<IIi',b,at);table=tables[s['link']]
    require(info>>8<len(table),'RELA symbol index')
    self.rel.append((s['info'],off,info&255,table[info>>8],add))
 def symbol(self,name):
  rows=[s for s in self.symbols if s['name']==name];require(len(rows)==1,'Unique symbol '+name);return rows[0]
 def data(self,s):
  require(s['index'] not in [0,65521] and s['index']<len(self.sections),'Defined symbol')
  sec=self.sections[s['index']];require(sec['type']!=8 and s['value']+s['size']<=sec['size'],'Symbol bounds')
  return self.raw[sec['offset']+s['value']:sec['offset']+s['value']+s['size']]
 def allocated(self):return [s for s in self.sections if s['flags']&2 and s['size']]
def addbase(bases,idx,va):
 require(idx not in bases or bases[idx]==va,'Conflicting section base');bases[idx]=va
def baseline_map(e,c):
 out={}
 for g in c['groups']:
  if g['kind']=='code':
   for m in g['members']:
    s=e.symbol(m['name']);require(s['type']==2 and s['size']==m['bytes'] and e.sections[s['index']]['name']==m['input_section'],'Original code shape')
    addbase(out,s['index'],m['original_va']-s['value'])
  else:
   m=g['members'][0];s=e.names[m['input_section']];require(s['size']==g['bytes'] and s['flags']==2,'Original RO shape');addbase(out,s['index'],g['original_va'])
 require(set(out)=={s['index']for s in e.allocated()},'Complete original allocated mapping');return out
def mapped_bytes(e,bases,va,n):
 rows=[s for s in e.allocated() if s['index']in bases and bases[s['index']]<=va and va+n<=bases[s['index']]+s['size']]
 require(len(rows)==1,'Unique physical span');s=rows[0];require(s['type']!=8,'Cannot read NOBITS');at=s['offset']+va-bases[s['index']];return e.raw[at:at+n]
def norm(e,bases,bindings=None):
 out=[];bindings=bindings or {}
 for idx,off,ty,s,add in e.rel:
  require(idx in bases and off+1<=e.sections[idx]['size'],'Mapped relocation site')
  if s['index']==0:
   target=('D',bindings[s['name']]+add) if s['name']in bindings else ('U',s['name'],add)
  elif s['index']==65521:target=('A',s['value']+add)
  else:
   require(s['index']in bases,'Mapped relocation target including local/section symbols');target=('D',bases[s['index']]+s['value']+add)
  out.append((bases[idx]+off,ty,target))
 return sorted(out)
"""Main body merged into the existing ELF parser in the delivered verifier."""
def symbol_metadata(e,s):
 i=s['index'];section='UND'if i==0 else'ABS'if i==65521 else e.sections[i]['name']
 return tuple(s[k]for k in ['name','value','size','binding','type','visibility'])+(section,)
def logical_bytes(e,bases,va,n):
 b=bytearray(mapped_bytes(e,bases,va,n))
 for site,ty,target in norm(e,bases):
  if not(va<=site<va+n)or ty not in [1,35,39]or target[0]not in ['D','A']:continue
  require(site+4<=va+n,'Logical word must fit the supplied view');off=site-va;word=struct.unpack_from('<I',b,off)[0]
  value=target[1]if ty==1 else word+target[1]if ty==35 else word-target[1];struct.pack_into('<I',b,off,value&0xffffffff)
 return bytes(b)
def main(receipt):
 from collections import Counter
 root=Path(__file__).resolve().parent;p=read(receipt);cfg=read(root/'layout/closure.json');plan=read(root/'layout/callback-native-plan.json');cpath=root/'../tsl9-contract-model/layout/known-runtime-layout.json';c=read(cpath)
 require(p['schema']=='R81-native-closure-producer'and p['mode']in ['c','cpp']and cfg['schema']=='R81-original-SP-address-expectation','Current producer schema')
 require(sha(cpath)==cfg['baseline_layout_sha256'],'Unchanged baseline layout')
 for path,digest in p['sources'].items():require(sha(path)==digest,'Current source identity')
 require(len(p['sources'])==19 and sha(p['objcopy'])==p['objcopy_sha256'],'Guarded native inputs and alias tool')
 require(sha(p['baseline_receipt'])==p['baseline_receipt_sha256'],'Baseline receipt identity');base=read(p['baseline_receipt']);require(base['passed']and sha(base['object'])==base['object_sha256']==cfg['baseline_platform_sha256'],'Baseline ELF identity')
 for path,digest in base['source_sha256'].items():require(sha(path)==digest,'Baseline source identity')
 for kind in ['compiler','linker']:require(sha(base[kind])==base[kind+'_sha256'],'Native tool identity')
 elves={}
 for name,row in p['objects'].items():
  require(Path(row['path']).stat().st_size==row['bytes']and sha(row['path'])==row['sha256'],'Derived object identity');elves[name]=ELF(row['path'])
 before=ELF(base['object']);oldmap=baseline_map(before,c);named=elves['baseline_aliases'];namedmap=baseline_map(named,c);platform=elves['platform'];after=elves['memory'];aliasnames={a['name']for a in plan['baseline_aliases']}
 require(len(aliasnames)==16 and len(before.allocated())==662 and len(before.rel)==4591,'Original baseline cohort')
 require(Counter(symbol_metadata(before,s)for s in before.symbols)==Counter(symbol_metadata(named,s)for s in named.symbols if s['name']not in aliasnames),'All original symbols retained without globalization')
 require(norm(before,oldmap)==norm(named,namedmap),'Alias injection retains all local/global/section/anonymous references')
 for s in before.allocated():
  t=named.names[s['name']];require(all(s[k]==t[k]for k in ['type','flags','addr','size','align'])and before.raw[s['offset']:s['offset']+s['size']]==named.raw[t['offset']:t['offset']+t['size']],'Alias injection preserves section bytes/shape')
 require(before.raw[36:40]==named.raw[36:40],'ELF ABI flags')
 for a in plan['baseline_aliases']:
  s=named.symbol(a['name']);require(s['binding']==1 and s['visibility']==2 and s['type']==0 and s['size']==0 and namedmap[s['index']]+s['value']==a['origin']and named.sections[s['index']]['name']==a['section'],'Section-relative alias must name real existing code')
  old=named.symbol(a['source_symbol']);require(old['binding']==0 and old['type']==2 and old['size']==a['source_bytes']and old['index']==s['index']and old['value']==s['value'],'Original LOCAL code provider remains present')
 newmap={};oldnames={before.sections[i]['name']:va for i,va in oldmap.items()};unionnames={g['input_section']:g['start']for g in cfg['coalesced_groups']};addednames={r['input_section']:r['start']for r in plan['regions']};addednames.update({d['input_section']:d['origin']for d in plan['descriptors']});addednames[plan['constant']['input_section']]=plan['constant']['start']
 for s in platform.allocated():
  va=unionnames.get(s['name'],addednames.get(s['name'],oldnames.get(s['name'])));require(va is not None,'Every platform section must have source-VA evidence');newmap[s['index']]=va
 require(len(platform.allocated())==670,'Coalesced platform allocation cohort')
 outmap={}
 for g in cfg['output_groups']:
  s=after.names[g['output_section']];require(s['type']==1 and s['flags']==(6 if g['kind']=='code' else 2)and s['addr']==0 and s['size']==g['bytes'],'Exact final represented group');outmap[s['index']]=g['original_va']
 ram=after.names['.tsl9_runtime_ram'];require(ram['type']==8 and ram['flags']==3 and ram['size']==35152 and ram['align']==4 and ram['addr']==0,'RAM representation');outmap[ram['index']]=0x20004000
 require(len(outmap)==668 and set(outmap)=={s['index']for s in after.allocated()},'Full final allocation mapping')
 spans=sorted((outmap[s['index']],outmap[s['index']]+s['size'])for s in after.allocated());require(all(a[1]<=b[0]for a,b in zip(spans,spans[1:])),'One physical allocation per source byte')
 old_functions=[s for s in before.symbols if s['type']==2 and s['index']and s['size']];require(len(old_functions)==707,'Original FUNC cohort')
 for old in old_functions:
  for e,m in [(platform,newmap),(after,outmap)]:
   s=e.symbol(old['name']);require(all(s[k]==old[k]for k in ['size','type','binding','visibility'])and m[s['index']]+s['value']==oldmap[old['index']]+old['value']and e.data(s)==before.data(old),'Original code bytes/metadata/VA retained')
 for section in before.allocated():
  va=oldmap[section['index']];raw=before.raw[section['offset']:section['offset']+section['size']]
  require(mapped_bytes(after,outmap,va,section['size'])==raw,'Every R77 allocated code/RO byte retained')
 for old in before.symbols:
  if old['type']!=1 or not old['index']or not old['size']:continue
  s=after.symbol(old['name']);require(all(s[k]==old[k]for k in ['size','type','binding','visibility'])and outmap[s['index']]+s['value']==oldmap[old['index']]+old['value']and logical_bytes(after,outmap,outmap[s['index']]+s['value'],s['size'])==logical_bytes(before,oldmap,oldmap[old['index']]+old['value'],old['size']),'Original OBJECT views retained')
 bindings={v['name']:v['start']for v in cfg['views']};bindings.update({v['name']:v['origin']for v in plan['descriptors']});late={a['name']:a['origin']for a in cfg['memory']['aliases']if a['name']!='__tsl9_data_load'};require(len(bindings)==9 and len(late)==37,'Nine early and37 late bindings')
 def expected_new(memory):
  rows=[]
  for rr in plan['relocations']:
   target=('U',rr['symbol'],rr['addend'])if rr['late_ram']and not memory else('D',rr['original_target']);rows.append((rr['pc'],rr['type'],target))
  return sorted(rows)
 spcfg=cfg['stack_address_expectation'];sp_source=root/'../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin';require(sha(sp_source)==spcfg['source_sha256']==cfg['source_sha256'],'Fixed original source for initial-SP derivation')
 with sp_source.open('rb')as stream:stream.seek(0x18406-0x8000);sp_pair=stream.read(8)
 require(hashlib.sha256(sp_pair).hexdigest()==spcfg['original_pair_sha256'],'Original admitted8B instruction pair')
 hi,lo=struct.unpack('<II',sp_pair);upper=hi&0xfffff000;upper=upper-(1<<32)if upper&(1<<31)else upper;imm=((lo>>20)^0x800)-0x800
 require(hi&0x7f==0x17 and(hi>>7)&31==2 and lo&0x707f==0x13 and(lo>>7)&31==2 and(lo>>15)&31==2,'Original AUIPC/ADDI uses sp with unchanged opcode/register bits')
 sp_value=(0x18406+upper+imm)&0xffffffff;require(sp_value==spcfg['value']==0x20010000 and upper==0x1fff8000 and imm==-1030,'Exact original initial-SP literal; not physical stack proof')
 unit=elves['stack_literal'];require(not unit.allocated() and not unit.rel,'Address-only unit allocates no target bytes or references')
 require([s['name']for s in unit.symbols if s['binding']==1 and s['index']]==['__tsl9_stack_top'],'No invented data/code/ROM providers')
 for current in [unit,platform,after]:
  symbol=current.symbol('__tsl9_stack_top');require(symbol['index']==65521 and symbol['value']==sp_value and symbol['size']==0 and symbol['type']==0 and symbol['binding']==1 and symbol['visibility']==0,'Exact default GLOBAL NOTYPE ABS address constant; not OBJECT or FUNC')
 def stack_expected(rows):
  expected=(0x18406,23,('U','__tsl9_stack_top',0));require(rows.count(expected)==1,'Only the actual initial-SP HI reference may change')
  return sorted((pc,ty,('A',sp_value))if(pc,ty,target)==expected else(pc,ty,target)for pc,ty,target in rows)
 require(norm(platform,newmap)==sorted(stack_expected(norm(before,oldmap,bindings))+expected_new(False)),'Every old/new platform relocation has its exact semantic target')
 require(norm(after,outmap)==sorted(stack_expected(norm(before,oldmap,dict(bindings,**late)))+expected_new(True)),'Every old/new memory relocation has its exact semantic target')
 require(len(after.rel)==4591+plan['new_relocations']==5654 and plan['new_relocations']==1063,'Complete relocation cohort')
 for region in plan['regions']:
  for e,m in [(platform,newmap),(after,outmap)]:
   s=e.symbol(region['name']);require(s['type']==2 and s['binding']==1 and s['visibility']==2 and s['size']==region['bytes']and m[s['index']]+s['value']==region['start'],'Physical emission region metadata')
   raw=e.data(s)
   for row in region['rows']:
    off=row['addr']-region['start'];original=int.from_bytes(bytes.fromhex(row['bytes']),'little');got=int.from_bytes(raw[off:off+row['size']],'little');require(got==(original&~row['relocated_mask']),'Every original instruction bit outside semantic relocation fields')
 for entry in plan['entries']:
  s=after.symbol(entry['name']);region=after.symbol(entry['region']);require(s['type']==2 and s['binding']==1 and s['visibility']==2 and s['size']==entry['bytes']and s['index']==region['index']and s['value']==region['value']+entry['offset']and outmap[s['index']]+s['value']==entry['origin'],'Actual callback entry code view')
 require(len([s for s in after.symbols if s['type']==2 and s['index']and s['size']])==771,'707 old plus23 region and41 entry FUNC anchors')
 require(sum(s['size']for s in elves['callbacks'].allocated()if s['flags']==6)==9868 and sum(s['size']for s in elves['callbacks'].allocated()if s['flags']==2)==96,'New code and existing-table physical allocation')
 require(sum(s['size']for s in elves['lookup'].allocated())==1022 and not elves['lookup'].rel,'Raw lookup difference excludes semantic96B')
 compare=elves['compare'];require(len(compare.allocated())==2 and sum(s['size']for s in compare.allocated())==52 and not compare.rel,'Only52 exact new RO bytes, no invented references')
 for fragment in cfg['r80_compare_view']['new_fragments']:
  s=after.symbol('tsl9_r80_fragment_%x'%fragment['start']);require(s['type']==1 and s['binding']==0 and s['size']==fragment['bytes'] and outmap[s['index']]+s['value']==fragment['start'] and hashlib.sha256(logical_bytes(after,outmap,fragment['start'],fragment['bytes'])).hexdigest()==fragment['sha256'],'Exact new gap and original-address metadata')
 require(sum(s['size']for s in elves['tables'].allocated())==60 and len(elves['tables'].rel)==8 and all(s['flags']==2 for s in elves['tables'].allocated()),'Only exact descriptor/constant views')
 require(len(elves['ram'].allocated())==1 and elves['ram'].allocated()[0]['type']==8 and elves['ram'].allocated()[0]['size']==35152 and not elves['ram'].rel,'Unchanged RAM-only unit')
 for v in cfg['views']:
  s=after.symbol(v['name']);require(s['type']==1 and s['binding']==1 and s['visibility']==0 and s['size']==v['bytes']and outmap[s['index']]+s['value']==v['start'],'Existing R78 captured provider metadata')
 for fragment in cfg['fragments']:
  s=after.symbol('tsl9_r78_fragment_%x'%fragment['start']);require(s['type']==1 and s['binding']==0 and s['size']==fragment['bytes']and outmap[s['index']]+s['value']==fragment['start'],'Old raw-fragment OBJECT view metadata')
 for a in cfg['memory']['aliases']:
  s=after.symbol(a['name']);require(s['type']==a['type']and s['size']==a['bytes']and s['binding']==1 and s['visibility']==0 and outmap[s['index']]+s['value']==a['origin'],'All38 memory contract names')
 original=(root/'provenance/target_runtime_memory-r77.c').read_bytes();require(hashlib.sha256(original).hexdigest()==cfg['ram_source_derivation']['original_sha256'],'Exact source preimage');text=original.decode().replace('\r\n','\n');a=text.index('".section .rodata.tsl9_init_image,');b=text.index('".section .bss.tsl9_runtime_ram,');derived=(root/'src/target_runtime_ram_only.c').read_text();require(derived[derived.index('*/')+3:]==text[:a]+text[b:],'Only previous initializer definition removed')
 carrier=root/'../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin';require(sha(carrier)==cfg['source_sha256'],'Fixed original carrier identity')
 with carrier.open('rb')as stream:
  for v in cfg['selected_windows']:
   stream.seek(v['start']-0x8000);source=stream.read(v['bytes']);require(hashlib.sha256(source).hexdigest()==v['sha256']and logical_bytes(after,outmap,v['start'],v['bytes'])==source,'Existing lookup values retain exact source meaning through semantic table upgrades')
  constant=plan['constant'];stream.seek(constant['start']-0x8000);source=stream.read(12);require(hashlib.sha256(source).hexdigest()==constant['raw_sha256']and logical_bytes(after,outmap,constant['start'],12)==source,'Conditional constant view exact source bytes')
 for table in plan['tables']:
  raw=logical_bytes(after,outmap,table['table_base'],table['bytes']);require(hashlib.sha256(raw).hexdigest()==table['raw_sha256'],'Semantic switch table equals retained original offsets')
  for case in table['cases']:require((table['table_base']+struct.unpack_from('<i',raw,4*case['index'])[0])&0xffffffff==case['target'],'Every guarded case target retains its original PC')
 for d in plan['descriptors']:
  s=after.symbol(d['name']);require(s['type']==1 and s['binding']==1 and s['visibility']==0 and s['size']==12 and outmap[s['index']]+s['value']==d['origin'],'Captured descriptor provider shape');raw=logical_bytes(after,outmap,d['origin'],12);require(hashlib.sha256(raw).hexdigest()==d['raw_sha256'],'Eight symbolic callbacks and four original nulls retain exact source words')
  for field in d['fields']:
   rr=[r for r in norm(after,outmap)if r[0]==d['origin']+field['offset']]
   require(rr==([(d['origin']+field['offset'],1,('D',field['original_target']))]if field['symbol']else[]),'Callback pointer must have exact R32 or original null, never a numeric-PC provider')
 initializer=cfg['memory']['initializer'];require(hashlib.sha256(logical_bytes(after,outmap,initializer['origin'],136)).hexdigest()==initializer['sha256'],'Initializer exact136B remains allocated once')
 require(sum(s['size']for s in after.allocated()if s['flags']==2)==4685,'Exact final readonly coverage')
 remaining=sorted(s['name']for s in after.symbols if not s['index']and s['name']);require(remaining==['__tsl9_opaque_address_19d10','__tsl9_rom_entry'],'Keep two real external obligations fatal')
 require(len([s for s in platform.symbols if not s['index']and s['name']])==39,'Platform39 real UND')
 require(sha(p['strict_log'])==p['strict_log_sha256']and p['strict_exit']!=0,'Real strict final link failure');missing=sorted(set(re.findall(r'undefined symbol: ([^\r\n]+)',Path(p['strict_log']).read_text())));require(missing==remaining,'Every remaining obligation must be fatal')
 for name in remaining:
  a=before.symbol(name);b=after.symbol(name);require(all(a[k]==b[k]for k in ['value','size','binding','type','visibility']),'Remaining undefined metadata unchanged')
 return dict(schema='R81-complete-native-static-audit',passed=True,mode=p['mode'],old_physical_code_preserved=618,old_function_names_preserved=707,new_emission_regions=23,new_entry_views=41,new_original_code_bytes=9868,new_original_instructions=3323,function_names=771,relocations=5654,new_relocations=1063,existing_LOCAL_code_names_added_without_mutation=16,old_RO_bytes_preserved=3455,existing_RO_semantically_upgraded_bytes=96,new_table_ADD32_SUB32_relocations=48,new_callback_R32_relocations=8,original_null_fields=4,r79_descriptor_constant_bytes=60,r80_new_readonly_bytes=52,new_readonly_bytes=0,readonly_bytes=4685,allocated_sections=668,conditional_BLE_view_bytes=1572,coalesced_union_bytes=2204,old_RO_reused_in_union=2152,physical_ROM_read_extent_proved=False,initializer_allocated_once_bytes=136,late_memory_aliases=37,original_initial_SP_literal=sp_value,stack_symbol_is_address_only=True,stack_storage_allocated=False,physical_stack_validity_proved=False,original_SP_instruction_pair_verified=True,remaining_UND=remaining,remaining_UND_count=2,strict_undefined_fatal=2,all_old_code_and_relocation_meanings_preserved=True,all_new_instruction_bits_and_reference_targets_verified=True,all_shared_tails_have_one_physical_allocation=True,native_bin=False,target_ready=False,source_object_extents_proved=False,physical_hardware_proved=False,ROM_ABI_proved=False,stack_or_copy_validity_proved=False,final_VMA_LMA_proved=False,ota_verified=False,network=False,target_executed=False,hardware=False,emulation=False)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True);args=parser.parse_args();print(json.dumps(main(args.receipt),separators=(',',':')))
