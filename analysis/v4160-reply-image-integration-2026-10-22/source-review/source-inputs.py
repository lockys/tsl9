"""Independent bounded source/filter context; no compilation or target execution."""
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True

REPLY='.text.tsl9v4160.ota_handler_9b8e'
PUBLIC='__tsl9v4160_ota_code_9b8e'
LOCAL='.Lota_handler_00009b8e'
PREVIOUS='743c087e24760779073cd27ef06b7355b9f61ced6a8b14a2e9fc410d3fa10c5e'
CORRECTION='89992f1f7d8f98595b5e151d34479ef0876162d697087c8e562d72036472a34c'
REPLY_INPUTS={
 'experiments/tsl9-v4160-ota-page-reply/src/page_reply.c':'0b2ea78e7a55dcee6e5adc3857e1b272b9faa578f1c8776b930fd4812abef9f0',
 'experiments/tsl9-v4160-ota-page-reply/src/page_reply.h':'5f84c99810942eeaaa31ad194751a544cf38c476cc72a45e0c2c81f09d862a1e',
 'experiments/tsl9-v4160-ota-page-reply/src/reply_io.h':'b6f693cecac98b87a320cbf14d7c23177d48a6b9133c917baed1fb83ae40aa1d'}
def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def case(root,name):return next(p for p in (root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def project(root,name):
    p=(root/name).resolve(strict=True);p.relative_to(root);return p
def filtered(raw,selected):
    """Remove only exact quoted owner spans; replace reply with its zero-byte roles."""
    lines=raw.splitlines(keepends=True);literals={i:json.loads(line.strip()) for i,line in enumerate(lines) if line.strip().startswith(b'"')};replacements={};removed=set()
    for row in selected:
        starts=[i for i,text in literals.items() if text.startswith('.section '+row['name']+',')];need(len(starts)==1,'One actual quoted owner');start=starts[0];reply=row['name']==REPLY
        terminator='.size '+row['global_alias']+','+str(0 if reply else row['bytes'])+'\n';ends=[i for i,text in literals.items() if i>=start and text==terminator];need(len(ends)==1,'Exact owner size directive');end=ends[0]
        need(all(i in literals for i in range(start,end+1)) and not any(literals[i].startswith('.section ') for i in range(start+1,end+1)),'Only one contiguous quoted assembly owner');span=set(range(start,end+1));need(not removed&span,'Disjoint source spans');removed|=span
        if reply:
            need(row['bytes']==124 and row['global_alias']==PUBLIC,'Exact old NOTYPE124 storage owner')
            anchor=['.section '+REPLY+',"ax",@progbits','.balign 2','.globl '+PUBLIC,'.type '+PUBLIC+',@notype',PUBLIC+':',LOCAL+':','.size '+PUBLIC+',0']
            replacements[start]=''.join('    '+json.dumps(text+'\n')+'\n' for text in anchor).encode('utf-8')
    return b''.join(replacements.get(i,b'')+(line if i not in removed else b'') for i,line in enumerate(lines))
def context(root,manifest_path,expected_sha=None):
    root=Path(root).resolve(strict=True);manifest_path=Path(manifest_path).resolve(strict=True)
    if expected_sha:need(sha(manifest_path)==expected_sha,'Frozen twelve-image manifest')
    m=read(manifest_path);need(sha(root/'experiments/tsl9-v4160-reply-image-integration/original-image-layout.ld')==m['layout_sha256'],'Exact original691 allocation linker source');oldpath=root/'experiments/tsl9-v4160-register-image-integration/source-manifest.json';need(sha(oldpath)==PREVIOUS,'Sealed prior eleven-image manifest');old=read(oldpath)
    need(m['source_files']==dict(old['source_files'],**REPLY_INPUTS) and len(m['source_files'])==79,'Exactly old76 plus three source-owned native reply files')
    need(m['source_units']==old['source_units'] and len(m['source_units'])==34,'Exactly retained34 raw source units')
    for name,pin in m['source_files'].items():need(sha(project(root,name))==pin,'Current native project input '+name)
    rows=m['selected_sections'];need(len(rows)==12 and sum(x['bytes'] for x in rows)==650,'Twelve exact owned extents650B');need({r['name'] for r in rows}=={r['name'] for r in old['selected_sections']}|{REPLY},'Only new reply storage owner')
    groups={}
    for row in rows:groups.setdefault(row['producer'],[]).append(row)
    need(len(groups)==5 and set(groups)=={x['path'] for x in m['filtered_carrier_units']},'Five exact source filters')
    generated={}
    for row in m['filtered_carrier_units']:
        path=project(root,row['path']);raw=path.read_bytes();result=filtered(raw,groups[row['path']]);need(sha(path)==row['before_sha256'] and hashlib.sha256(result).hexdigest()==row['filtered_sha256'] and len(raw)-len(result)==row['removed_source_bytes'],'Independent exact quoted-source removal/boundary insertion');generated[row['path']]=result
    for field in ('frame_schedule_source_files','reply_order_source_files'):
        for name,pin in m[field].items():need(sha(project(root,name))==pin,'Current explicit ABI ordering source '+name)
    correction=case(root,'v4160-ota-page-reply-2026-10-22')/'entry-call-correction';need(sha(correction/'seal.json')==CORRECTION,'Narrow source-caller correction89992')
    for row in read(correction/'seal.json')['files']:
        p=(correction/row['path']).resolve(strict=True);p.relative_to(correction);need(sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],'Immutable caller correction member')
    incoming=m['incoming_call'];need((incoming['PC'],incoming['raw_hex'],incoming['rd'],incoming['target'],incoming['return_PC'],incoming['correction_seal_sha256'])==(0x9df4,'693b',1,0x9b8e,0x9df6,CORRECTION),'Actual incoming C.JAL source role; relocation name alone insufficient')
    return {'root':root,'manifest':m,'generated_filters':generated,'selected':rows,'source_files':79,'raw_units':34,'filtered_units':5,'external_resource_headers_actual_checked':False}
