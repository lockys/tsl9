"""Check real relocatable CODE ownership by original-PC tags,without execution."""
import argparse,collections,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def inspect(path):
    reader=ROOT/'experiments/tsl9-resident-root-chain-callees/elf_reader-v7.py';need(sha(reader)=='309ee86cd2d967e40fa29cd34a9ff420f9b5803c4c3931dfd93eec75a7e2a06c','Frozen native ELF reader');e=runpy.run_path(str(reader),run_name='owner_ELF_library')['ELF'](path);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
    sections={s['index']:s for s in e.sections if s['flags']&6==6 and s['size']};bysec=collections.defaultdict(list);origins={};instances=collections.defaultdict(set);values={};aliases=collections.defaultdict(set)
    for s in e.symbols:
        if not(s['info']==18 and s['size']):continue
        need(s['section']in sections,'Every positive FUNC has actual executable bytes,no ABS provider');m=re.search(r'_([0-9a-f]+)$',s['name']);need(m is not None,'Every current CODE owner carries original-PC tag');pc=int(m[1],16);sec=sections[s['section']];need(s['value']+s['size']<=sec['size'],'Real FUNC extent inside owner');start=pc-s['value'];need(s['section']not in origins or origins[s['section']]==start,'Aliases agree on original section origin');origins[s['section']]=start;bysec[s['section']].append(s)
        data=e.data(sec)
        for off in range(s['size']):
            at=pc+off;physical=(s['section'],s['value']+off);value=data[s['value']+off];need(at not in values or values[at]==value,'Conflicting native bytes at the same original-PC tag');values[at]=value;instances[at].add(physical);aliases[physical].add(s['name'])
    need(set(origins)==set(sections),'Every nonempty CODE section has positive original-PC owner')
    need(sum(len(v)for v in instances.values())==sum(s['size']for s in sections.values()),'Each actual CODE byte belongs to declared original-PC interval')
    def target(s):
        if s['section']in origins:return ['CODE',origins[s['section']]+s['value']]
        if not s['section']:
            m=re.search(r'_([0-9a-f]+)$',s['name']);need(m is not None,'Real unresolved CODE target retains address tag');return ['CODE',int(m[1],16)]
        if s['section']<len(e.sections):return ['DATA',e.sections[s['section']]['name'],s['value']]
        return ['ABS',s['value'],s['info']]
    relations=[]
    for v in e.relocations:
        owner=['CODE',origins[v['section']]+v['offset']]if v['section']in origins else['DATA',e.sections[v['section']]['name'],v['offset']];relations.append([owner,v['type'],v['addend'],target(e.symbols[v['symbol']])])
    typed=sorted({json.dumps(v,separators=(',',':'))for v in relations});dups=sorted(p for p,v in instances.items()if len(v)>1);intervals=[]
    for pc in dups:
        if intervals and intervals[-1][1]==pc:intervals[-1][1]=pc+1
        else:intervals.append([pc,pc+1])
    data={s['name']:dict(type=s['type'],flags=s['flags'],size=s['size'],alignment=s['align'],sha256=hashlib.sha256(e.data(s)).hexdigest())for s in e.sections if s['flags']&2 and not s['flags']&4 and s['size']}
    return dict(passed=not dups,object_sha256=sha(path),CODE_bytes=sum(s['size']for s in sections.values()),distinct_original_CODE_bytes=len(values),duplicate_original_CODE_bytes=len(dups),overlap_intervals=intervals,positive_FUNC_regions=sum(len(v)for v in bysec.values()),relocations=len(e.relocations),distinct_PC_typed_relocations=len(typed),native_byte_map_sha256=digest(sorted(values.items())),original_PC_typed_relocations_sha256=digest(typed),non_CODE_allocations=data,named_UND=sorted(s['name']for s in e.symbols if s['info']>>4 and not s['section']),original_PC_tags_are_source_contract_not_physical_placement=True,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,_byte_map=values,_typed_relations=typed)
def public(v):return {k:x for k,x in v.items()if not k.startswith('_')}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--object',required=True,type=Path);a=p.parse_args()
    try:
        result=inspect(a.object);print(json.dumps(public(result)));raise SystemExit(0 if result['passed']else 1)
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(2)
