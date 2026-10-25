#!/usr/bin/env python3
"""Adjacent-span original-coordinate diagnostic link. No target execution or BIN."""
import argparse,bisect,hashlib,json,runpy,struct,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CONFIG=HERE/'spec-v38.json'
K=json.loads(CONFIG.read_bytes())
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
def library(rel):return runpy.run_path(str(ROOT/rel),run_name='positive_static_library')
E=library(K['reader'])['ELF'];B=library(K['shared_helper'])
def source(mode):return ROOT/K['source_component']/mode/K['source_object']
def portable(v,llvm):
    pairs=[(llvm.parent/'lib/clang/18','$'+'{CLANG_RESOURCE}'),(llvm,'$'+'{LLVM_BIN}'),(ROOT,'$'+'{PROJECT_ROOT}')]
    if isinstance(v,str):
        for p,t in pairs:
            for f in [str(p),p.as_posix()]:v=v.replace(f,t)
        return v
    if isinstance(v,list):return [portable(x,llvm)for x in v]
    if isinstance(v,dict):return {portable(k,llvm):portable(x,llvm)for k,x in v.items()}
    return v
def pins(llvm):
    for p,v in K['pins'].items():need(sha(ROOT/p)==v,'Pinned source/proof input '+p)
    for p,k in [(K['reader'],'reader_sha256'),(K['firmware'],'firmware_sha256')]:need(sha(ROOT/p)==K[k],'Pinned '+k)
    for name,pin in K['tools'].items():need(sha(llvm/name)==pin,'Pinned actual '+name)
    for mode in ('c','cpp'):need(sha(source(mode))==K['source_sha256'],'Measured C/C++ component identity')
def source_proof(llvm):
    p=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/K['source_replay']),'--tool-dir',str(llvm),'--replay',str(ROOT/K['source_component'])],capture_output=True,cwd=ROOT,timeout=180)
    need(p.returncode==0,'Complete actual C/C++ source-component replay')
    result=json.loads(p.stdout);need(result['passed']and result['code_bytes']==43826 and result['data_bytes']==1832 and result['UND']==122,'Exact retained C-source scope')
    return result
def global_map(e):
    rows=[s for s in e.symbols if s['info']>>4];m={s['name']:s for s in rows}
    need(len(m)==len(rows),'Unique program globals')
    return m
def derive(e):
    maps={}
    def visit(x):
        if isinstance(x,dict):
            if all(k in x for k in ['name','start','end','bytes','original_sha256']):
                row={k:x[k]for k in ['name','start','end','bytes','original_sha256']}
                need(row['name']not in maps or maps[row['name']]==row,'Consistent frozen original span')
                maps[row['name']]=row
            for v in x.values():visit(v)
        elif isinstance(x,list):
            for v in x:visit(v)
    for rel in K['span_specs']:visit(json.loads((ROOT/rel).read_bytes()))
    contract=json.loads((ROOT/K['initializer_contract']).read_bytes());owners=[]
    for f in e.symbols:
        if f['info']not in (17,18)or not f['size']:continue
        try:pc=int(f['name'].rsplit('_',1)[1],16);coordinate='original-PC symbol'
        except ValueError:
            if f['info']==18:
                row=maps[f['name']];pc=row['start'];need(row['bytes']==f['size'],'Actual body/frozen span size');coordinate='frozen original span'
            else:
                need(f['name']==contract['data_symbol']and f['size']==contract['data_bytes'],'Actual initializer contract')
                pc=contract['data_original_start'];coordinate='frozen initializer contract'
        sec=e.sections[f['section']];data=e.data(sec)[f['value']:f['value']+f['size']]
        need(sec['type']==1 and sec['flags']==(6 if f['info']==18 else 2),'Genuine actual code/readonly source')
        need(len(data)==f['size']and pc%sec['align']==0,'Whole original-aligned source payload')
        owners.append(dict(name=f['name'],info=f['info'],source_section=sec['index'],source_offset=f['value'],bytes=f['size'],
            original_PC=pc,coordinate=coordinate,section=('.original_code_'if f['info']==18 else'.original_data_')+format(pc,'08x'),
            alignment=sec['align'],source_sha256=hashlib.sha256(data).hexdigest()))
    owners.sort(key=lambda x:x['original_PC'])
    need(len(owners)==3605 and sum(o['bytes']for o in owners if o['info']==18)==43826 and sum(o['bytes']for o in owners if o['info']==17)==1832,'All3587 code and18 data owners')
    need(all(a['original_PC']+a['bytes']<=b['original_PC']for a,b in zip(owners,owners[1:])),'No original code/data owner overlap')
    for sec in e.sections:
        if not(sec['flags']&2 and sec['size']):continue
        rows=sorted([o for o in owners if o['source_section']==sec['index']],key=lambda x:x['source_offset']);at=0
        for o in rows:need(o['source_offset']==at,'No native payload hole/duplicate');at+=o['bytes']
        need(at==sec['size'],'Every compiled allocated byte owned')
    used={r['symbol']for r in e.relocations};imports=[]
    for s in e.symbols:
        if not s['info']>>4 or s['section']:continue
        need(s['info']==16 and s['index']in used and s['value']==s['size']==0,'Explicit referenced unresolved provider')
        pc=int(s['name'].rsplit('_',1)[1],16)
        imports.append(dict(source_symbol=s['name'],source_symbol_index=s['index'],original_reference_PC=pc,
            reference_constant='__rea_original_reference_'+format(pc,'08x'),body_implementation_proved=False))
    imports.sort(key=lambda x:x['source_symbol'])
    need(len(imports)==122 and len({x['original_reference_PC']for x in imports})==122,'Exactly122 still-unreconstructed imports')
    groups=[]
    for o in owners:
        if groups and all(groups[-1][k]==o[k] for k in ('info','alignment')) and groups[-1]['original_PC']+groups[-1]['bytes']==o['original_PC']:
            group=groups[-1]
        else:
            group=dict(section=('.original_code_span_' if o['info']==18 else '.original_data_span_')+format(o['original_PC'],'08x'),
                original_PC=o['original_PC'],bytes=0,info=o['info'],alignment=o['alignment'],owners=[])
            groups.append(group)
        o['section']=group['section'];o['section_offset']=group['bytes']
        group['bytes']+=o['bytes'];group['owners'].append(o['name'])
    need(len(groups)==107 and sum(g['bytes'] for g in groups)==45658,'All actual bytes in107 adjacent-only spans preserving code/data and alignment roles')
    return dict(owners=owners,groups=groups,imports=imports,source_undefined_providers=122)
def lookup(plan,section,value):
    rows=sorted([o for o in plan['owners']if o['source_section']==section],key=lambda x:x['source_offset'])
    starts=[o['source_offset']for o in rows];i=bisect.bisect_right(starts,value)-1
    need(i>=0 and value<rows[i]['source_offset']+rows[i]['bytes'],'One real native byte owner')
    return rows[i],value-rows[i]['source_offset']
def original_value(e,plan,s):
    if not s['section']:
        need(s['info']==16,'Only actual global unresolved references')
        return int(s['name'].rsplit('_',1)[1],16)
    need(s['section']!=0xfff1,'No ABS provider in original C component')
    o,off=lookup(plan,s['section'],s['value'])
    return o['original_PC']+off
def validate_original(e,plan):
    fw=(ROOT/K['firmware']).read_bytes();payload={o['name']:bytearray(e.data(e.sections[o['source_section']])[o['source_offset']:o['source_offset']+o['bytes']])for o in plan['owners']}
    for r in e.relocations:
        o,off=lookup(plan,r['section'],r['offset']);kind=r['type'];target=e.symbols[r['symbol']];place=o['original_PC']+off;data=payload[o['name']]
        if kind in (16,17,44,45):
            width,mask=B['MASKS'][kind];dest=original_value(e,plan,target)+r['addend']
            original=fw[place-0x8000:place-0x8000+width]
            need(B['decode_control'](original,place)==(kind,dest),'Original encoded control agrees with reference coordinate')
            a=int.from_bytes(data[off:off+width],'little')
            data[off:off+width]=((a&mask)|B['immediate'](kind,dest-place)).to_bytes(width,'little')
        elif kind==23:
            dest=original_value(e,plan,target)+r['addend'];delta=(dest-place)&0xffffffff
            a=int.from_bytes(data[off:off+4],'little');data[off:off+4]=((a&0xfff)|((delta+0x800)&0xfffff000)).to_bytes(4,'little')
        elif kind==24:
            hi=[x for x in e.relocations if x['section']==target['section']and x['offset']==target['value']and x['type']==23]
            need(len(hi)==1 and target['info']==0,'One actual local HI anchor for each LO')
            hi=hi[0];hipc=original_value(e,plan,target);dest=original_value(e,plan,e.symbols[hi['symbol']])+hi['addend']
            a=int.from_bytes(data[off:off+4],'little');data[off:off+4]=((a&0xfffff)|(((dest-hipc)&0xfff)<<20)).to_bytes(4,'little')
        elif kind==1:
            data[off:off+4]=((original_value(e,plan,target)+r['addend'])&0xffffffff).to_bytes(4,'little')
        elif kind in (35,39):
            a=int.from_bytes(data[off:off+4],'little');v=original_value(e,plan,target)+r['addend']
            data[off:off+4]=((a+v if kind==35 else a-v)&0xffffffff).to_bytes(4,'little')
        else:raise ValueError('Unsupported actual relocation kind')
    failures=[]
    for o in plan['owners']:
        expected=fw[o['original_PC']-0x8000:o['original_PC']-0x8000+o['bytes']]
        if bytes(payload[o['name']])!=expected:failures.append(o['name'])
    need(not failures,'Full original-VA equality failed: '+','.join(failures[:8]))
    return payload

def split_object(e,plan,source_path):
    """Resection measured bytes and relocation owners; do not copy firmware bytes."""
    secs=[dict(name='',type=0,flags=0,address=0,data=b'',link=0,info=0,align=0,entsize=0)]
    def add(name,typ,flags,data,align=1,link=0,info=0,entsize=0):
        secs.append(dict(name=name,type=typ,flags=flags,address=0,data=data,link=link,info=info,align=align,entsize=entsize))
        return len(secs)-1
    owner_index={}
    byname={o['name']:o for o in plan['owners']}
    for g in plan['groups']:
        raw=bytearray()
        for name in g['owners']:
            o=byname[name]
            need(o['section_offset']==len(raw) and o['original_PC']==g['original_PC']+len(raw),'Adjacent-only real owner concatenation')
            raw.extend(e.data(e.sections[o['source_section']])[o['source_offset']:o['source_offset']+o['bytes']])
        need(len(raw)==g['bytes'],'No added gap or padding bytes')
        index=add(g['section'],1,6 if g['info']==18 else 2,bytes(raw),g['alignment'])
        for name in g['owners']:owner_index[name]=index
    used={r['symbol']for r in e.relocations};symbols=[];old_to_new={}
    for s in e.symbols:
        if s['info']==3:
            need(s['index']not in used and s['info']>>4==0,'Only unreferenced old section markers removed')
            continue
        item=dict(s)
        if s['section']not in (0,0xfff1):
            owner,off=lookup(plan,s['section'],s['value']);item['section']=owner_index[owner['name']];item['value']=owner['section_offset']+off
        old_to_new[s['index']]=len(symbols);symbols.append(item)
    need(old_to_new[0]==0 and symbols[0]['info']==0,'Preserved null symbol')
    strdata=bytearray(b'\0');strings={'':0}
    def string(s):
        if s not in strings:strings[s]=len(strdata);strdata.extend(s.encode('utf8')+b'\0')
        return strings[s]
    table=bytearray()
    for s in symbols:table.extend(struct.pack('<IIIBBH',string(s['name']),s['value'],s['size'],s['info'],s['other'],s['section']))
    first_global=next(i for i,s in enumerate(symbols)if s['info']>>4)
    need(all(not s['info']>>4 for s in symbols[:first_global])and all(s['info']>>4 for s in symbols[first_global:]),'Valid local/global symbol partition')
    symidx=add('.symtab',2,0,bytes(table),4,info=first_global,entsize=16)
    stridx=add('.strtab',3,0,bytes(strdata));secs[symidx]['link']=stridx
    grouped=defaultdict(list)
    for r in e.relocations:
        owner,off=lookup(plan,r['section'],r['offset'])
        grouped[owner['section']].append((owner['section_offset']+off,(old_to_new[r['symbol']]<<8)|r['type'],r['addend']))
    for g in plan['groups']:
        if g['section']not in grouped:continue
        data=b''.join(struct.pack('<IIi',*r)for r in grouped[g['section']])
        add('.rela'+g['section'],4,0,data,4,link=symidx,info=owner_index[g['owners'][0]],entsize=12)
    shstridx=add('.shstrtab',3,0,b'');names=bytearray(b'\0')
    for sec in secs:
        sec['name_offset']=len(names)if sec['name']else 0
        if sec['name']:names.extend(sec['name'].encode()+b'\0')
    secs[shstridx]['data']=bytes(names)
    blob=bytearray(52)
    for sec in secs[1:]:
        blob.extend(bytes((-len(blob))%max(sec['align'],1)));sec['offset']=len(blob);blob.extend(sec['data'])
    blob.extend(bytes((-len(blob))%4));shoff=len(blob)
    for i,sec in enumerate(secs):
        blob.extend(struct.pack('<IIIIIIIIII',sec['name_offset'],sec['type'],sec['flags'],0,sec.get('offset',0),len(sec['data']),sec['link'],sec['info'],sec['align'],sec['entsize']))
    blob[:16]=source_path.read_bytes()[:16]
    blob[16:52]=struct.pack('<HHIIIIIHHHHHH',1,243,1,0,0,shoff,e.header[6],52,0,0,40,len(secs),shstridx)
    return bytes(blob)
def audit_split(path,e,plan):
    out=E(path);need(out.header[0]==1 and not out.program_headers,'Actual resectioned ET_REL')
    srcm,dstm=global_map(e),global_map(out);need(set(srcm)==set(dstm),'All actual globals including122 unknowns retained before reference renaming')
    for name,s in srcm.items():
        t=dstm[name];need((s['info'],s['other'],s['size'])==(t['info'],t['other'],t['size']),'Original global role/type/extent')
        if not s['section']:need(t['section']==t['value']==0,'Original unknown remains undefined')
        else:
            o,off=lookup(plan,s['section'],s['value']);need(out.sections[t['section']]['name']==o['section']and t['value']==o['section_offset']+off,'Actual compiled global resection coordinate')
    expected=Counter()
    for r in e.relocations:
        o,off=lookup(plan,r['section'],r['offset']);s=e.symbols[r['symbol']]
        if s['section']:
            to,at=lookup(plan,s['section'],s['value']);role=(s['name'],s['info'],s['other'],s['size'],to['section'],to['section_offset']+at)
        else:role=(s['name'],s['info'],s['other'],s['size'],'',s['value'])
        expected[(o['section'],o['section_offset']+off,r['type'],r['addend'],role)]+=1
    actual=Counter()
    for r in out.relocations:
        s=out.symbols[r['symbol']];role=(s['name'],s['info'],s['other'],s['size'],out.sections[s['section']]['name']if s['section']else'',s['value'])
        actual[(out.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],role)]+=1
    need(actual==expected and len(out.relocations)==2849,'All2849 typed source-reference roles survive resection')
    need({s['name']for s in out.sections if s['flags']&2 and s['size']}=={o['section']for o in plan['owners']},'Every resectioned allocation owned')
    for g in plan['groups']:
        sec=out.section(g['section'])
        need(sec['size']==g['bytes'] and sec['flags']==(6 if g['info']==18 else 2) and sec['align']==g['alignment'],'Exact adjacent-span allocation')
    for o in plan['owners']:need(out.data(o['section'])[o['section_offset']:o['section_offset']+o['bytes']]==e.data(e.sections[o['source_section']])[o['source_offset']:o['source_offset']+o['bytes']],'Every actual C/C++ byte carrier unchanged')
def linker_text(plan):
    lines=['OUTPUT_ARCH(riscv)','PHDRS { evidence PT_NULL FLAGS(0); }','SECTIONS','{']
    for g in plan['groups']:
        lines.append(' '+g['section']+' 0x'+format(g['original_PC'],'x')+' : SUBALIGN('+str(g['alignment'])+') { *('+g['section']+') } :NONE')
    for imp in plan['imports']:lines.append(' HIDDEN('+imp['reference_constant']+' = 0x'+format(imp['original_reference_PC'],'x')+');')
    lines.extend([' /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }','}'])
    return '\n'.join(lines)+'\n'
def renamed_target(plan,name):
    return next((i['reference_constant']for i in plan['imports']if i['source_symbol']==name),name)
def audit_link(path,e,plan):
    linked=E(path);lm=global_map(linked);sm=global_map(e);fw=(ROOT/K['firmware']).read_bytes()
    need(linked.header[0]==2 and linked.header[1]==243 and linked.header[3]==0,'Diagnostic ET_EXEC format with zero entry')
    need(linked.program_headers and all(p[0]==0 for p in linked.program_headers),'PT_NULL only; zero loadable segments')
    imports={i['source_symbol']:i for i in plan['imports']};matched=0
    need(set(lm)==set(sm)-set(imports),'Only genuine compiled globals survive; hidden reference constants are not global providers')
    references=[s for s in linked.symbols if s['name'].startswith('__rea_original_reference_')]
    reference_map={s['name']:s for s in references}
    need(len(references)==len(reference_map)==122 and set(reference_map)=={i['reference_constant'] for i in plan['imports']},'Exactly122 distinct explicitly named hidden reference constants')
    for name,s in sm.items():
        if name in imports:
            t=reference_map[imports[name]['reference_constant']]
            need(t['section']==0xfff1 and t['info']==0 and t['other']==2 and t['size']==0 and t['value']==imports[name]['original_reference_PC'],'Local hidden NOTYPE ABS reference constant; no FUNC/body definition')
        else:
            t=lm[name]
            o,off=lookup(plan,s['section'],s['value'])
            need(t['info']==s['info']and t['other']==s['other']and t['size']==s['size']and t['value']==o['original_PC']+off and linked.sections[t['section']]['name']==o['section'],'Native linked actual code/data/alias address')
    need({s['name']for s in linked.sections if s['flags']&2 and s['size']}=={o['section']for o in plan['owners']},'No extra code,stubs,GOT or gap providers')
    for g in plan['groups']:
        sec=linked.section(g['section'])
        need(sec['type']==1 and sec['flags']==(6 if g['info']==18 else 2) and sec['address']==g['original_PC'] and sec['size']==g['bytes'] and sec['align']>=g['alignment'],'Actual linker adjacent original-coordinate allocation')
    for o in plan['owners']:
        sec=linked.section(o['section'])
        need(sec['address']+o['section_offset']==o['original_PC'],'Actual original owner offset within adjacent span')
        actual_bytes=linked.data(sec)[o['section_offset']:o['section_offset']+o['bytes']]
        need(actual_bytes==fw[o['original_PC']-0x8000:o['original_PC']-0x8000+o['bytes']],'Actual fully linked bytes equal official original range: '+o['name'])
        matched+=o['bytes']
    # Retained relocation roles after applying them; ET_EXEC offsets are original virtual addresses.
    expected=Counter()
    for r in e.relocations:
        o,off=lookup(plan,r['section'],r['offset']);s=e.symbols[r['symbol']]
        expected[(o['section'],o['original_PC']+off,r['type'],r['addend'],renamed_target(plan,s['name']),original_value(e,plan,s))]+=1
    actual=Counter()
    for r in linked.relocations:
        s=linked.symbols[r['symbol']]
        actual[(linked.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],s['name'],s['value'])]+=1
    need(actual==expected and len(linked.relocations)==2849,'Every applied2849 relocation has the exact original reference address and role')
    need(matched==45658 and not any(s['section']==0xfff1 and s['info']&15==2 for s in linked.symbols),'No ABS FUNC providers; all45658 selected bytes matched')
    return dict(passed=True,ELF_type=2,entry=0,PT_LOAD_count=0,code_regions=3587,readonly_objects=18,code_bytes=43826,data_bytes=1832,
        original_coordinate_bytes_equal=45658,adjacent_only_spans=107,source_unreconstructed_providers=122,reference_only_ABS_constants=122,ABS_FUNC_providers=0,
        applied_relocations_retained=2849,native_linker_addresses_and_bytes_equal_original=True,
        source_byte_carriers_preserved_before_actual_link=True,ELF_sha256=sha(path),full_image_rebuilt=False,
        whole_firmware_original_layout_proved=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,private_ABI_proved=False,
        firmware_BIN_generated=False,firmware_ready=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
def fallthrough(plan,linked):
    starts={o['original_PC']:o for o in plan['owners']if o['info']==18};edges=[];gaps=[];instructions=0
    for o in plan['owners']:
        if o['info']!=18:continue
        raw=linked.data(o['section'])[o['section_offset']:o['section_offset']+o['bytes']];at=0;last=None
        while at<len(raw):
            w=4 if raw[at]&3==3 else 2;need(at+w<=len(raw),'Whole actual mapped instruction')
            last=(at,w,int.from_bytes(raw[at:at+w],'little'));at+=w;instructions+=1
        off,w,v=last;possible=True
        if w==4:
            if v in (0x30200073,0x10200073,0x7b200073):possible=False
            elif v&127 in (0x6f,0x67)and(v>>7)&31==0:possible=False
        else:
            if v&3==1 and(v>>13)&7==5:possible=False
            elif v&0xf07f==0x8002 and(v>>7)&31:possible=False
        if possible:
            end=o['original_PC']+len(raw);row=dict(owner=o['name'],last_PC=o['original_PC']+off,next_PC=end,target=starts.get(end,{}).get('name'))
            edges.append(row)
            if end not in starts:gaps.append(row)
    need(instructions==15200,'All15200 mapped original instructions counted')
    return dict(possible_continuations=len(edges),bound_continuations=len(edges)-len(gaps),uncovered_continuations=gaps,
        all_selected_fallthrough_and_call_return_positions_owned=not gaps,edges=edges)
def inputs(llvm):
    paths={Path(__file__),CONFIG,ROOT/K['reader'],ROOT/K['firmware']}
    paths.update(ROOT/p for p in K['pins']);paths.update(llvm/n for n in K['tools'])
    for mode in ('c','cpp'):paths.add(source(mode))
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)}
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve();pins(llvm);proof=source_proof(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained layout')
        record=json.loads((out/'measurement.json').read_bytes());need(record['inputs']==before and record['source_proof']==proof,'All source/proof/tool identities unchanged')
        for mode in ('c','cpp'):
            e=E(source(mode));plan=derive(e);validate_original(e,plan);f=out/mode
            need(record['modes'][mode]['artifacts']==inventory(f),'Complete retained layout artifact inventory')
            need(json.loads((f/'layout-map.json').read_bytes())==plan,'Exact original-coordinate owner/import map')
            audit_split(f/'split-C-payload.o',e,plan)
            need(record['modes'][mode]['result']==audit_link(f/'NONLOADABLE-ORIGINAL-LAYOUT.elf',e,plan),'Actual linked layout replay')
            need(record['modes'][mode]['fallthrough']==fallthrough(plan,E(f/'NONLOADABLE-ORIGINAL-LAYOUT.elf')),'Actual continuation-position replay')
        print(json.dumps(dict(passed=True,mode='read-only-native-original-layout-replay',code_bytes=43826,data_bytes=1832,original_coordinate_bytes_equal=45658,adjacent_only_spans=107,source_unreconstructed_providers=122,PT_LOAD_count=0,firmware_ready=False)));return
    need(a.trial and Path(a.trial).name==a.trial,'Single create-only trial name');out=HERE/'build'/a.trial;need(not out.exists(),'Create-only native layout output')
    report=dict(schema='TSL9-native-original-coordinate-layout-v7',inputs=before,source_proof=proof,modes={})
    for mode in ('c','cpp'):
        e=E(source(mode));plan=derive(e);validate_original(e,plan);f=out/mode;f.mkdir(parents=True)
        (f/'layout-map.json').write_bytes(encoded(plan));(f/'split-C-payload.o').write_bytes(split_object(e,plan,source(mode)))
        audit_split(f/'split-C-payload.o',e,plan)
        (f/'reference-only.rename').write_text('\n'.join(i['source_symbol']+' '+i['reference_constant']for i in plan['imports'])+'\n',encoding='utf8')
        (f/'original-layout.ld').write_text(linker_text(plan),encoding='utf8')
        commands=[]
        for label,argv in [('rename',[str(llvm/'llvm-objcopy.exe'),'--redefine-syms='+str(f/'reference-only.rename'),str(f/'split-C-payload.o'),str(f/'reference-addresses.o')]),('link',[str(llvm/'ld.lld.exe'),'--no-relax','--emit-relocs','--no-undefined','--entry=0','-T',str(f/'original-layout.ld'),str(f/'reference-addresses.o'),'-o',str(f/'NONLOADABLE-ORIGINAL-LAYOUT.elf')]),('read',[str(llvm/'llvm-objdump.exe'),'-h','-t','-r',str(f/'NONLOADABLE-ORIGINAL-LAYOUT.elf')])]:
            proc=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(f/(label+'.log')).write_bytes(portable((proc.stdout+proc.stderr).decode('utf8','replace'),llvm).encode('utf8'));commands.append(dict(label=label,argv=argv,exit=proc.returncode))
            need(proc.returncode==0,'Actual layout tool failed: '+label+';log retained')
        result=audit_link(f/'NONLOADABLE-ORIGINAL-LAYOUT.elf',e,plan);continuations=fallthrough(plan,E(f/'NONLOADABLE-ORIGINAL-LAYOUT.elf'))
        (f/'verification.json').write_bytes(encoded(result));(f/'continuations.json').write_bytes(encoded(continuations))
        report['modes'][mode]=dict(result=result,fallthrough=continuations,commands=commands,artifacts=inventory(f))
        print(json.dumps(result|dict(possible_continuations=continuations['possible_continuations'],uncovered_continuations=len(continuations['uncovered_continuations']))))
    need(before==portable(inputs(llvm),llvm),'Every actual input unchanged during layout construction')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))
if __name__=='__main__':
    try:main()
    except Exception as e:
        msg=str(e)
        for p,t in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            for form in [str(p),p.as_posix()]:msg=msg.replace(form.replace('\\','\\\\'),t).replace(form,t)
        print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=msg)),file=sys.stderr);sys.exit(1)
