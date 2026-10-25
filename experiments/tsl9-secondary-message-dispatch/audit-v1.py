"""Check conservative static closure and literal roles without executing target code."""
import hashlib,json,re,runpy,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def audit():
    spec=json.loads((HERE/'spec-v1.json').read_text())
    evidence=json.loads((HERE/'evidence-v1.json').read_text())
    need(sha(HERE/'evidence-v1.json')==spec['reference_candidate_sha256'],'Pinned instruction evidence')
    fw=(ROOT/spec['firmware']).read_bytes()
    need(hashlib.sha256(fw).hexdigest()==spec['firmware_sha256'],'Actual original image')
    shared=ROOT/'experiments/tsl9-original-startup/build-v1.py'
    need(sha(shared)=='1f6e3673c24a5d85c62d55ec8d8390b80225577010d81c8aba5c4b6750e208b5','Pinned static decoder')
    decoder=runpy.run_path(str(shared),run_name='static_control_decoder')['decode_control']
    scope=evidence['scope'];plan=ROOT/scope['formal_parent_map']
    need(sha(plan)==scope['formal_parent_map_sha256'],'Actual previous formal owner map')
    owners=json.loads(plan.read_text())['owners'];formal_entries={s['original_PC'] for s in owners if s['info']==18}
    fs=evidence['selected_functions'];entries={f['start'] for f in fs};allops={o['addr']:o for f in fs for o in f['operations']}
    need(len(fs)==9 and len(allops)==690,'Nine complete bodies and690instructions')
    def opcode(pc):return re.sub(r'0x([0-9a-f]+)',lambda m:str(int(m[1],16)),allops[pc]['opcode'].replace(' ',''))
    expected={0x126a8:'lbua5,0(a1)',0x126ac:'lia4,6',0x126ae:'addia5,a5,-1',0x126b0:'andia5,a5,255',0x126b8:'auipca4,8',0x126bc:'addia4,a4,-300',0x126c0:'sllia5,a5,2',0x126c2:'adda5,a5,a4',0x126c4:'lwa5,0(a5)',0x126dc:'adda5,a5,a4',0x126e6:'jra5'}
    for pc,text in expected.items():need(opcode(pc)==text,'Exact event index/base/load/indirect instruction at'+hex(pc))
    need(opcode(0x126b4).startswith('bltua4,a5,'),'Unsigned reject guard')
    need(decoder(bytes.fromhex(allops[0x126b4]['bytes']),0x126b4)==(16,0x128fc),'Actual guard reject target')
    table=[0x1a58c+v for v in struct.unpack_from('<7i',fw,0x1a58c-0x8000)]
    need(table==scope['event_dispatch_table']['targets'] and len(set(table))==6,'Seven signed-relative cells and six targets')
    need(all(t in allops and 0x126a0<=t<0x128fe for t in table),'Actual whole case-entry boundaries')
    opaque_allowed={0x1269e,0x1333a};results=[];total=0
    for f in fs:
        ops={o['addr']:o for o in f['operations']};at=f['start']
        need(f['end']<=0x14056 or f['start']>=0x14c8a,'Excluded neighboring body')
        for pc,o in sorted(ops.items()):
            raw=bytes.fromhex(o['bytes']);need(pc==at and len(raw)==o['size']==(4 if raw[0]&3==3 else 2),'Whole contiguous instruction')
            need(raw==fw[pc-0x8000:pc-0x8000+len(raw)] and o['opcode']!='invalid','Actual selected bytes')
            need(not any(s['original_PC']<pc+len(raw) and s['original_PC']+s['bytes']>pc for s in owners),'No original formal overlap')
            at+=len(raw)
        need(at==f['end'],'Exact body end')
        pending=[f['start']];seen=set();tails=[];calls=[];opaque=[]
        while pending:
            pc=pending.pop()
            if pc in seen:continue
            need(pc in ops,'Every static successor on an actual body instruction boundary')
            seen.add(pc);o=ops[pc];kind=o['type'];after=pc+o['size'];successors=[]
            if kind in ('call','ucall'):
                if kind=='call':
                    edge=decoder(bytes.fromhex(o['bytes']),pc)
                    need(edge and edge[1]==o['jump'] and edge[1] in set(allops)|formal_entries,'Actual direct call provider')
                calls.append(dict(PC=pc,direct_target=o.get('jump'),indirect=kind=='ucall'));successors=[after]
            elif kind in ('jmp','cjmp'):
                edge=decoder(bytes.fromhex(o['bytes']),pc);need(edge and edge[1]==o['jump'],'Independent original direct edge')
                target=edge[1]
                if target in ops:successors.append(target)
                else:
                    need(kind=='jmp' and target in entries|formal_entries,'Explicit tail to a real selected/formal entry')
                    tails.append(dict(PC=pc,target=target))
                if kind=='cjmp':successors.append(after)
            elif kind=='rjmp':
                if pc==0x126e6:successors=sorted(set(table))
                else:
                    need(pc in opaque_allowed,'Exactly retained opaque ROM-slot tails');opaque.append(dict(PC=pc,opcode=o['opcode']))
            elif kind!='ret':successors=[after]
            pending.extend(successors)
        need(seen==set(ops),'All retained instructions reachable in conservative static CFG; missing='+str([hex(x) for x in sorted(set(ops)-seen)[:10]]))
        total+=len(seen);results.append(dict(start=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),CFG_reached_instructions=len(seen),direct_tails=tails,opaque_register_tails=opaque,calls=calls))
    need(total==690 and sum(f['bytes'] for f in results)==2048,'All2048B690i accounted for')
    hidden=fw[0x17832-0x8000:0x1787c-0x8000]
    def word(pc):return int.from_bytes(fw[pc-0x8000:pc-0x8000+4],'little')
    need(word(0x17832)==((370<<20)|(3<<15)|(4<<12)|(15<<7)|3),'Existing index byte is GP+370')
    need(word(0x17836)==0x00279613,'Existing byte index scaled by four')
    need(word(0x1783a)==0x00003697 and word(0x1783e)==((686<<20)|(13<<15)|(13<<7)|0x13),'Actual existing AUIPC/ADDI hidden base')
    need(0x1783a+0x3000+686==0x1aae8,'Hidden DATA address')
    need(int.from_bytes(fw[0x17842-0x8000:0x17844-0x8000],'little')==0x96b2,'Existing scaled index added to table base')
    need(int.from_bytes(fw[0x17844-0x8000:0x17846-0x8000],'little')==0x4294,'Actual compressed hidden table load')
    need(word(0x1785a)==0x02e7e7b3,'Actual modulo instruction follows the load')
    need(int.from_bytes(fw[0x17856-0x8000:0x1785a-0x8000],'little')==0x471d0785,'Increment then load modulo divisor seven')
    need(word(0x17868)==0x16f18923,'Reduced index stored back to GP+370')
    return dict(schema='TSL9-secondary-message-static-closure-v1',passed=True,functions=results,original_code_bytes=2048,original_instructions=690,
        CFG_kind='conservative static paths only; not path feasibility, actual invocation, ABI, or runtime bounds',
        event_jump_table=dict(base=0x1a58c,entries=7,unique_targets=6,targets=table,index_expression='(unsigned_byte(message[0])-1)&255',accepted_index=[0,6],reject_PC=0x128fc,jump_PC=0x126e6,DATA_provided=False),
        typed_address_pairs=7,unprovided_static_DATA=[0x19dd4,0x1a58c],
        hidden_existing_dependency=dict(base=0x1aae8,consumer_PC=0x1783a,index_byte_GP_offset=370,load_PC=0x17844,load_precedes_modulo=True,index_globally_bounded=False,consumer_window_sha256=hashlib.sha256(hidden).hexdigest(),DATA_provided=False,compiler_UND_inventory_exhaustive=False),
        curated_integration=False,formal_coverage_percent=91.83,installed_ROM_ABI_verified=False,global_RAM_bounds_verified=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False)

if __name__=='__main__':
    try:
        result=audit()
        print(json.dumps(dict(passed=result['passed'],bodies=len(result['functions']),bytes=result['original_code_bytes'],instructions=result['original_instructions'],event_entries=7,event_unique_targets=6,hidden_dependency=hex(result['hidden_existing_dependency']['base']),target_executed=False)))
    except (ValueError,OSError) as error:
        print(json.dumps(dict(passed=False,reason=str(error).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));raise SystemExit(1)
