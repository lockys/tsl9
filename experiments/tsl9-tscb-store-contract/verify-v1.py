#!/usr/bin/env python3
"""Static reaching-definition, affine-stack and encoded-store obligations; no machine execution."""
import argparse,hashlib,json,re,runpy
from collections import deque
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
REGS=['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1']+['a'+str(i)for i in range(8)]+['s'+str(i)for i in range(2,12)]+['t'+str(i)for i in range(3,7)]
RID={n:i for i,n in enumerate(REGS)};RID['fp']=8
SREGS={8,9,*range(18,28)};CLOBBER={1,5,6,7,*range(10,18),*range(28,32)}
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='static_store_library')
def parts(o):
    m,*r=o['opcode'].split(' ',1);return m,[v.strip()for v in r[0].split(',')]if r else[]
def rd(o):
    """Decode written GPR only; do not evaluate instructions, flags, loads or memory."""
    v=int.from_bytes(bytes.fromhex(o['bytes']),'little')
    if o['size']==4:
        code=v&127
        if code in[3,19,23,51,55,103,111]:return (v>>7)&31 or None
        need(code in[15,35,99],'Only reviewed RV32 integer/control/store instructions');return None
    q=v&3;f=v>>13
    if q==0:
        if f in[0,2]:return 8+((v>>2)&7)
        need(f==6,'Reviewed quadrant0 form');return None
    if q==1:
        if f in[0,2,3]:return (v>>7)&31 or None
        if f==1:return 1
        if f==4:return 8+((v>>7)&7)
        need(f in[5,6,7],'Reviewed quadrant1 form');return None
    need(q==2,'Whole compressed instruction')
    if f in[0,2]:return (v>>7)&31 or None
    if f==4:
        if(v>>2)&31:return (v>>7)&31 or None
        if v&0x1000:need((v>>7)&31!=0,'No unmodelled EBREAK');return 1
        return None
    need(f==6,'Reviewed quadrant2 form');return None
def raw_store(o):
    v=int.from_bytes(bytes.fromhex(o['bytes']),'little')
    return v&127==35 if o['size']==4 else (v&3,v>>13)in[(0,6),(2,6)]
class Graph:
    def __init__(self,f,B):
        self.f=f;self.ops={o['addr']:o for o in f['operations']};self.succ={};self.calls={};self.exits={}
        for pc,o in self.ops.items():
            after=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
            if o['opcode']=='ret':self.succ[pc]=[];self.exits[pc]='return';continue
            if d:
                k,t=d;v=int.from_bytes(bytes.fromhex(o['bytes']),'little');call=(k==17 and(v>>7)&31!=0)or(k==45 and(v>>13)&7==1)
                if k in[16,44]:nexts=[after,t]
                elif call:self.calls[pc]=dict(target=t,tail=False);nexts=[after]
                elif t in self.ops:nexts=[t]
                else:self.calls[pc]=dict(target=t,tail=True);self.exits[pc]='tail';nexts=[]
            else:
                need(o['type']not in['ucall','rjmp'],'No unassigned indirect call/jump outside the separately specialized fill body');nexts=[after]
            need(all(n in self.ops for n in nexts),'Every local successor owned');self.succ[pc]=nexts
        start=f['start'];self.stack={pc:set()for pc in self.ops};todo=[(start,0)];seen=set()
        while todo:
            pc,delta=todo.pop()
            if(pc,delta)in seen:continue
            need(len(seen)<len(self.ops)*8,'Finite affine stack states');seen.add((pc,delta));self.stack[pc].add(delta);o=self.ops[pc];d=rd(o)
            if d==2:
                m,a=parts(o);need(m=='addi'and a[:2]==['sp','sp'],'Only literal stack adjustments');delta+=int(a[2],0)
            if pc in self.exits:need(delta==0,'Every local return/tail restores its incoming SP')
            for nxt in self.succ[pc]:todo.append((nxt,delta))
        need({pc for pc,v in seen}==set(self.ops),'Every non-fill instruction syntactically reachable')
        initial=tuple(frozenset(['entry:'+REGS[i]])for i in range(32));self.defs={pc:None for pc in self.ops};self.defs[start]=initial;queue=deque([start])
        while queue:
            pc=queue.popleft();state=list(self.defs[pc]);d=rd(self.ops[pc])
            if d is not None:state[d]=frozenset([pc])
            if pc in self.calls:
                for r in CLOBBER:state[r]=frozenset(['call:'+str(pc)+':'+REGS[r]])
            state=tuple(state)
            for nxt in self.succ[pc]:
                prev=self.defs[nxt];joined=state if prev is None else tuple(a|b for a,b in zip(prev,state))
                if prev!=joined:self.defs[nxt]=joined;queue.append(nxt)
    def value(self,pc,reg,entry_args=None,seen=None):
        """Resolve only literal/move/add-immediate address definitions, never loaded values."""
        args=entry_args or{};seen=set()if seen is None else seen
        if reg==0:return ('constant',0)
        if reg==2:
            need(len(self.stack[pc])==1,'One affine SP at an address use');return ('stack',next(iter(self.stack[pc])))
        key=(pc,reg);need(key not in seen,'Address definition is not a cyclic or loaded value');seen=seen|{key};values=[]
        for origin in self.defs[pc][reg]:
            if isinstance(origin,str):
                need(origin=='entry:'+REGS[reg]and reg in args,'Only explicitly proved entry arguments may form addresses');values.append(args[reg]);continue
            o=self.ops[origin];m,a=parts(o);need(a and RID.get(a[0])==reg,'Decoded definition register agrees with primary operand')
            if m=='li':v=('constant',int(a[1],0)&0xffffffff)
            elif m=='lui':v=('constant',(int(a[1],0)<<12)&0xffffffff)
            elif m=='mv':v=self.value(origin,RID[a[1]],args,seen)
            elif m=='addi':
                base=self.value(origin,RID[a[1]],args,seen);n=int(a[2],0);v=(base[0],(base[1]+n)&0xffffffff)if base[0]=='constant'else('stack',base[1]+n)
            else:raise ValueError('Address depends on an unproved nonliteral definition at '+hex(origin))
            values.append(v)
        need(values and len(set(values))==1,'All reaching address definitions agree');return values[0]
def audit():
    S=json.loads((HERE/'spec-v1.json').read_bytes());need(sha(ROOT/S['instructions'])==S['instructions_sha256'],'Immutable instruction snapshot')
    for k in['firmware','control_decoder','reader','independent_reader','comparator','ledger','manifest']:need(sha(ROOT/S[k])==S[k+'_sha256'],'Pinned '+k)
    E=json.loads((ROOT/S['instructions']).read_bytes());fw=(ROOT/S['firmware']).read_bytes();B=lib(S['control_decoder']);functions={f['start']:f for f in E['functions']};need(len(functions)==14,'Exactly14 real function entries')
    count=total=stores=0;allops={}
    for f in functions.values():
        at=f['start'];need(not(f['start']<0x14c8a and f['end']>0x14056)and not(f['start']<0x1a6a0 and f['end']>0x1a69c),'Protected ranges excluded')
        for o in f['operations']:
            raw=bytes.fromhex(o['bytes']);need(o['addr']==at and o['size']==len(raw)==(4 if raw[0]&3==3 else 2)and raw==fw[at-0x8000:at-0x8000+len(raw)],'Every original instruction exact')
            need(raw_store(o)==(o['type']=='store'),'Independent raw store detection agrees with primary inventory');rd(o);allops[at]=o;at+=len(raw);count+=1;stores+=raw_store(o)
        need(at==f['end']and hashlib.sha256(fw[f['start']-0x8000:f['end']-0x8000]).hexdigest()==f['original_sha256'],'Complete immutable function body');total+=f['end']-f['start']
    need((total,count,stores)==(1072,390,79),'Complete bounded CPU-store corpus')
    native=[];ledger=json.loads((ROOT/S['ledger']).read_bytes())
    for unit in S['native_units']:
        source=ROOT/unit['source'];need(sha(source)==unit['source_sha256']==ledger['inputs'][str(source)],'Current curated C matches actual prior compilation input')
        for mode,v in unit['objects'].items():
            obj=ROOT/v['path'];need(sha(obj)==v['sha256']==ledger['artifacts'][unit['unit']+'/'+mode+'/curated/unit.o'],'Exact retained compiled C/C++ object')
            result=lib(S['comparator'])['audit'](obj);need(result['passed'],'Independent complete native ELF agreement');native.append(dict(unit=unit['unit'],mode=mode,object_sha256=sha(obj),independent_readers=result))
    graphs={p:Graph(f,B)for p,f in functions.items()if p!=0x8520};root=graphs[0x197f0];need(root.f['end']==0x1995c,'Complete callback excludes following event handler')
    # All callees have no encoded S-register write; their normal-return/tail SP balance is checked above.
    for p,f in functions.items():
        if p==0x197f0:continue
        need(not any(rd(o)in SREGS for o in f['operations']),'Every selected callee preserves encoded S-register contents')
        if p==0x8520:need(not any(rd(o)in[2,3]for o in f['operations']),'Fill does not write SP/GP')
    need(root.value(0x1986e,9)==('constant',0x40012400)and root.value(0x198dc,8)==('constant',0x40012000),'Actual callback S1/S0 address definitions')
    calls=[dict(source=p,PC=pc,**v)for p,g in graphs.items()for pc,v in g.calls.items()]
    need(len(calls)==16 and all(v['target']in functions for v in calls),'Every direct callee/tail has a real selected body')
    arg_helpers={0x1892e,0x18986,0x18996,0x189ae,0x18a98};arg_evidence=[]
    for v in calls:
        if v['target']in arg_helpers:
            need(v['source']==0x197f0 and root.value(v['PC'],10)==('constant',0x40012400),'Every actual A0-relative writer receives the fixed peripheral base')
            arg_evidence.append(dict(PC=v['PC'],target=v['target'],A0=0x40012400))
    need({v['target']for v in arg_evidence}==arg_helpers,'All parameter-relative writers covered')
    # This invocation of the existing computed-tail fill is length32,value0,destination current SP+32.
    need(root.calls[0x19814]['target']==0x8520 and root.value(0x19814,10)==('stack',-96)and root.value(0x19814,11)==('constant',0)and root.value(0x19814,12)==('constant',32),'Exact fill caller arguments')
    fill=functions[0x8520];fo={o['addr']:o for o in fill['operations']}
    expected={0x8520:'li t1, 15',0x8522:'mv a4, a0',0x8524:'bleu a2, t1, 0x854a',0x8528:'andi a5, a4, 15',0x852c:'bnez a5, 0x85aa',0x852e:'bnez a1, 0x8598',0x8530:'andi a3, a2, -16',0x8534:'andi a2, a2, 15',0x8536:'add a3, a3, a4',0x8538:'sw a1, 0(a4)',0x853a:'sw a1, 4(a4)',0x853c:'sw a1, 8(a4)',0x853e:'sw a1, 12(a4)',0x8540:'addi a4, a4, 16',0x8542:'bltu a4, a3, 0x8538',0x8546:'bnez a2, 0x854a',0x8548:'ret'}
    for pc,want in expected.items():need(fo[pc]['opcode']==want,'Actual fixed-length fill proof operand '+hex(pc))
    obligations=[];mmio=set()
    for p,f in sorted(functions.items()):
        for o in f['operations']:
            if not raw_store(o):continue
            m,a=parts(o);mat=re.fullmatch(r'(-?(?:0x[0-9a-f]+|\d+))\((\w+)\)',a[1]);need(mat is not None,'Explicit store base/offset')
            offset,base=mat.groups();offset=int(offset,0);width={'sb':1,'sh':2,'sw':4}[m];record=dict(function=p,PC=o['addr'],width=width,operand=o['opcode'])
            if p==0x8520:
                if o['addr']in[0x8538,0x853a,0x853c,0x853e]:record.update(kind='specialized-fill-word',destination_relative_to_callback_entry_SP=[-96+offset,-96+offset+4],second_iteration_relative_to_callback_entry_SP=[-80+offset,-80+offset+4],condition='incoming aligned valid nonwrapping stack; length32/value0; two16-byte iterations')
                else:need(0x855a<=o['addr']<=0x8592,'Only the15 descending byte stores remain');record.update(kind='inactive-fill-tail',condition='Unreachable for the proved length32/value0/aligned invocation; no general fill claim')
            elif base=='sp':
                g=graphs[p];need(len(g.stack[o['addr']])==1,'One local stack displacement at every store');d=next(iter(g.stack[o['addr']]))
                need(d<0 and d<=d+offset and d+offset+width<=0,'Each encoded stack write stays in its allocated frame')
                record.update(kind='local-stack',relative_to_this_function_entry_SP=[d+offset,d+offset+width],function_frame_bytes=-min(v for ds in g.stack.values()for v in ds))
            else:
                g=graphs[p];ctx={10:('constant',0x40012400)}if p in arg_helpers else{};value=g.value(o['addr'],RID[base],ctx)
                need(value[0]=='constant','No loaded or computed pointer may silently form an MMIO proof');address=value[1]+offset
                need(address in {0x40021004,0x4002100c,0x40021018}|set(range(0x40012404,0x4001243c,4))and width==4,'Only exact reviewed numeric peripheral word addresses')
                mmio.add(address);record.update(kind='numeric-MMIO',address=address,physical_alias_or_device_behavior_proved=False)
            obligations.append(record)
    kinds={k:sum(v['kind']==k for v in obligations)for k in['local-stack','numeric-MMIO','specialized-fill-word','inactive-fill-tail']}
    need(kinds=={'local-stack':27,'numeric-MMIO':33,'specialized-fill-word':4,'inactive-fill-tail':15}and len(mmio)==17,'Every79 encoded store site classified without a provider stub')
    depth={0x8520:0}
    def extra(p,visiting=None):
        if p in depth:return depth[p]
        visiting=set()if visiting is None else visiting;need(p not in visiting,'Selected direct call graph is acyclic');g=graphs[p];n=max(-v for ds in g.stack.values()for v in ds)
        for pc,c in g.calls.items():
            need(len(g.stack[pc])==1,'One stack displacement at every call/tail');n=max(n,-next(iter(g.stack[pc]))+extra(c['target'],visiting|{p}))
        depth[p]=n;return n
    need(extra(0x197f0)==144,'Exact local allocated callback/callee depth bound under the stated call contracts')
    return dict(schema='TSL9-tsCB-encoded-store-contract-v1',passed=True,checker_sha256=sha(__file__),static_only=True,concrete_machine_state_or_memory_simulated=False,
        input_functions=14,input_bytes=1072,input_instructions=390,store_sites=79,store_classification=kinds,store_obligations=obligations,numeric_MMIO_word_addresses=sorted(mmio),
        callback_range=[0x197f0,0x1995c],callback_own_frame_bytes=128,local_allocated_stack_depth_bytes=144,whole_program_stack_bound_proved=False,
        actual_call_arguments=arg_evidence,direct_calls_and_tails=sorted(calls,key=lambda v:(v['source'],v['PC'])),
        fill_specialization=dict(caller=0x19814,target=0x8520,destination_relative_to_callback_entry_SP=[-96,-64],length=32,value=0,word_loop_iterations=2,inactive_byte_tail_store_sites=15,computed_tail_controls_reached=False,requires_incoming_SP_alignment=16,requires_nonwrapping_valid_memory=True),
        retained_native_objects=native,new_target_compilation=False,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,
        conditional_conclusion='Encoded CPU stores are confined to the local stack/fill intervals and17 numeric peripheral word addresses; excluding CFG/heap requires the explicit stack and hardware nonalias assumptions.',
        unproved=['actual incoming stack address,capacity and nonoverlap with ROM configuration and APP heap','physical memory mapping and MMIO aliases','IRQ,DMA and asynchronous peripheral effects','polling termination and actual completion','installed ROM/ISA and original-hardware startup/OTA'],
        staCB_value_at_heap_call_proved=False,total_callback_hardware_side_effects_proved=False,actual_RAM_capacity_proved=False,firmware_ready=False,new_BIN=False,goal_complete=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit()
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only static contract receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items()if k in['passed','static_only','input_functions','input_bytes','input_instructions','store_sites','store_classification','local_allocated_stack_depth_bytes','whole_program_stack_bound_proved','new_target_compilation','APP_byte_coverage_unchanged','staCB_value_at_heap_call_proved','firmware_ready','new_BIN']}))
    except Exception as error:
        message=str(error)
        for path,token in[(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
