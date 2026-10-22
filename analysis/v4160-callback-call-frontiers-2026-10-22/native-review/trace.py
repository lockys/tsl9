"""Static CFG/reaching-definition analysis, not a register-state interpreter."""
from collections import deque

CALLER={1,5,6,7,10,11,12,13,14,15,16,17,28,29,30,31}


def need(value,message):
    if not value:raise ValueError(message)


def is_call(row):return row['op']=='jalr' and row['rd']==1


def graph(rows):
    bypc={r['PC']:r for r in rows};edges={pc:[] for pc in bypc}
    for r in rows:
        pc=r['PC'];nextpc=pc+r['bytes']
        if r['target'] is not None:
            need(r['target'] in bypc,'Known local target lies at an actual instruction boundary')
            edges[pc].append(r['target'])
            if r['op']!='jal' and nextpc in bypc:edges[pc].append(nextpc)
        elif r['op']=='jalr' and r['rd']==0:
            need(r['rs1']==1,'Only known normal RET boundary')
        elif nextpc in bypc:edges[pc].append(nextpc)
    return bypc,edges


def reaching(rows,policy):
    """Finite sets of static definition IDs. No register values or branch evaluation."""
    bypc,edges=graph(rows);entry=rows[0]['PC'];incoming={pc:None for pc in bypc}
    incoming[entry]=tuple(frozenset({('entry',reg)}) for reg in range(32))
    todo=deque([entry]);steps=0
    while todo:
        pc=todo.popleft();row=bypc[pc];out=list(incoming[pc])
        if is_call(row):
            killed=set(range(1,32)) if policy=='opaque-all' else CALLER
            for reg in killed:out[reg]=frozenset({('opaque',pc,reg)})
        elif row['rd'] not in (None,0):out[row['rd']]=frozenset({('instruction',pc,row['rd'])})
        for target in edges[pc]:
            before=incoming[target]
            merged=tuple(out) if before is None else tuple(a|b for a,b in zip(before,out))
            if before!=merged:incoming[target]=merged;todo.append(target)
        steps+=1;need(steps<20000,'Bounded static dataflow convergence')
    need(all(value is not None for value in incoming.values()),'Every retained row has a static reachable predecessor')
    return dict(rows=bypc,edges=edges,IN=incoming,policy=policy,iterations=steps)


def constants(flow,pc,reg,seen=frozenset()):
    """Only LUI/literal/MV/ADDI address-definition folding; no instruction execution."""
    if reg==0:return {0}
    key=(pc,reg)
    if key in seen:return None
    out=set();seen=seen|{key}
    for item in flow['IN'][pc][reg]:
        if item[0]!='instruction':return None
        row=flow['rows'][item[1]];op=row['op']
        if op=='lui':values={row['immediate']&0xffffffff}
        elif op=='mv':values=constants(flow,row['PC'],row['rs1'],seen)
        elif op=='addi':
            base=constants(flow,row['PC'],row['rs1'],seen)
            values=None if base is None else {(v+row['immediate'])&0xffffffff for v in base}
        else:return None
        if values is None:return None
        out|=values
    return out


def target_loads(flow,call):
    result=[]
    for item in flow['IN'][call['PC']][call['rs1']]:
        need(item[0]=='instruction','Each observed raw target has an actual local load definition')
        row=flow['rows'][item[1]]
        need(row['op']=='lw' and row['memory_width']==32,'Target comes from actual32-bit pointer read')
        base=constants(flow,row['PC'],row['rs1'])
        addresses=sorted((v+row['immediate'])&0xffffffff for v in base) if base is not None else None
        result.append(dict(PC=row['PC'],base_register=row['rs1'],offset=row['immediate'],
                           width=32,conditional_addresses=addresses))
    return sorted(result,key=lambda r:r['PC'])


def call_ancestors(rows):
    bypc,edges=graph(rows);entry=rows[0]['PC'];values={pc:set() for pc in bypc};todo=deque([entry]);seen=set()
    while todo:
        pc=todo.popleft();out=values[pc]|({pc} if is_call(bypc[pc]) else set())
        for target in edges[pc]:
            merged=values[target]|out
            if merged!=values[target] or target not in seen:
                values[target]=merged;seen.add(target);todo.append(target)
    return values


def labels(rows):
    conditional=reaching(rows,'conventional-callee-preservation')
    calls=[r for r in rows if is_call(r)];need(len(calls)==15,'Fifteen actual raw call sites')
    loads={r['PC']:target_loads(conditional,r) for r in calls};slots={}
    for pc,items in loads.items():
        addresses={value for item in items for value in (item['conditional_addresses'] or [])}
        need(len(addresses)==1,'Unique nominal resident slot under explicit preservation assumption')
        slots[pc]=next(iter(addresses))-0x40000
    ancestor=call_ancestors(rows);result={}
    unique={0x6c:'message_receive',0x68:'message_release',0xb8:'capacity_query',
            0x128:'buffer_allocate',0x4c:'buffer_copy',0x58:'post_retry',0xd4:'descriptor_send',
            0x1a8:'connection_parameters',0x1a4:'maintenance'}
    for call in calls:
        pc=call['PC'];slot=slots[pc]
        if slot in unique:name=unique[slot]
        elif slot==0x12c:
            a1=constants(conditional,pc,11)
            name='descriptor_release' if a1=={27} else 'message_dispatch'
        elif slot==0x13c:
            name='gate_after_copy' if any(slots.get(a)==0x4c for a in ancestor[pc]) else 'gate_before_capacity'
        elif slot==0x50:
            a1=constants(conditional,pc,11)
            need(a1 in ({1},{2}),'Post event has actual distinguishing A1 definition')
            name='post_progress' if a1=={1} else 'post_pending'
        else:raise ValueError('Unknown target family '+hex(slot))
        need(name not in result,'Signatures are unique; no address-order fallback')
        result[name]=dict(PC=pc,slot=slot,target_register=call['rs1'],RA=pc+call['bytes'],
                          target_loads=loads[pc],A1_constant=sorted(constants(conditional,pc,11) or []))
    bypc={v['PC']:name for name,v in result.items()}
    for name,item in result.items():
        item['possible_earlier_calls']=sorted(bypc[pc] for pc in ancestor[item['PC']])
    return result,conditional


def definition(item,flow,call_names,depth=2):
    if item[0]=='entry':return dict(kind='entry',register=item[1])
    if item[0]=='opaque':return dict(kind='opaque-output',call=call_names.get(item[1],hex(item[1])),register=item[2])
    row=flow['rows'][item[1]];value=dict(kind='instruction',PC=row['PC'],op=row['op'],rd=row['rd'],
            rs1=row['rs1'],rs2=row['rs2'],immediate=row['immediate'],width=row['memory_width'])
    if depth:
        for key in ('rs1','rs2'):
            reg=row[key]
            if reg not in (None,0):
                value[key+'_definitions']=[definition(v,flow,call_names,depth-1)
                                          for v in sorted(flow['IN'][row['PC']][reg])]
    return value


def frontiers(rows,matched):
    names={value['PC']:name for name,value in matched.items()};out={}
    for policy in ('opaque-all','conventional-callee-preservation'):
        flow=reaching(rows,policy);calls={}
        for name,site in matched.items():
            pc=site['PC'];calls[name]={str(reg):[definition(item,flow,names) for item in sorted(flow['IN'][pc][reg])]
                                     for reg in [*range(10,18),8,9,*range(18,26),3,2]}
        out[policy]=calls
    return out
