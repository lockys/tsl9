"""LLVM SSA input provenance for existing inline call adapters; no IR execution."""
import re


def need(value,message):
    if not value:raise ValueError(message)


def parse(text):
    definitions={};calls={}
    for line in text.splitlines():
        match=re.match(r'\s*(%\d+) = (.*)',line)
        if match:definitions[match[1]]=match[2]
        match=re.match(r'\s*(%\d+) = .*asm sideeffect "jalr ra,a([56]),0", .*"\((.*?)\) #',line)
        if not match:continue
        args=[part.removeprefix('i32 ').strip() for part in match[3].split(', ')]
        need(len(args)==8 and all(re.fullmatch(r'%\d+|-?\d+',a) for a in args),
             'Actual eight simple raw-register adapter inputs')
        target=args[int(match[2])]
        load=definitions.get(target,'')
        slot=re.search(r'load volatile i32, ptr inttoptr \(i32 (\d+) to ptr\)',load)
        need(slot is not None,'Actual target operand has identifiable volatile constant resident-slot definition')
        calls[match[1]]=dict(SSA=match[1],target_register=int(match[2])+10,
                             slot=int(slot[1])-0x40000,args=args,target_SSA=target,
                             target_definition=load)
    need(len(calls)==15,'Fifteen IR adapters, independently of source or address order')
    return definitions,calls


def origin(value,definitions,calls,names,seen=frozenset()):
    if re.fullmatch(r'-?\d+',value):return [dict(kind='literal',value=int(value)&0xffffffff)]
    if value in seen:return [dict(kind='cycle',SSA=value)]
    if value in {'%'+str(i) for i in range(8)}:
        return [dict(kind='entry-argument',argument=int(value[1:]))]
    definition=definitions.get(value,'')
    match=re.fullmatch(r'extractvalue \{[^}]+\} (%\d+), (\d+)',definition)
    if match and match[1] in calls:
        return [dict(kind='opaque-output',call=names.get(match[1],match[1]),argument=int(match[2]))]
    if definition.startswith('phi i32 '):
        result=[]
        for incoming in re.findall(r'\[\s*([^,\]]+),\s*%\d+\s*\]',definition):
            result+=origin(incoming.strip(),definitions,calls,names,seen|{value})
        return result
    return [dict(kind='SSA-definition',SSA=value,definition=definition)]


def labels(text):
    definitions,calls=parse(text);names={}
    unique={0x6c:'message_receive',0x68:'message_release',0xb8:'capacity_query',
            0x128:'buffer_allocate',0x4c:'buffer_copy',0x58:'post_retry',0xd4:'descriptor_send',
            0x1a8:'connection_parameters',0x1a4:'maintenance'}
    for ident,call in calls.items():
        slot=call['slot'];a1=call['args'][1]
        if slot in unique:name=unique[slot]
        elif slot==0x12c:name='descriptor_release' if a1=='27' else 'message_dispatch'
        elif slot==0x50:
            need(a1 in ('1','2'),'IR post signature uses literal distinguishing event')
            name='post_progress' if a1=='1' else 'post_pending'
        elif slot==0x13c:continue
        else:raise ValueError('Unknown IR target family')
        need(name not in names.values(),'Unique independent IR signature')
        names[ident]=name
    for ident,call in calls.items():
        if call['slot']!=0x13c:continue
        value=origin(call['args'][2],definitions,calls,names)
        if value==[dict(kind='entry-argument',argument=2)]:name='gate_before_capacity'
        elif value==[dict(kind='opaque-output',call='buffer_copy',argument=2)]:name='gate_after_copy'
        else:raise ValueError('Gate cannot be matched by its actual A2 provenance')
        need(name not in names.values(),'Distinct gate signatures, not address ranking')
        names[ident]=name
    result={}
    for ident,call in calls.items():
        name=names[ident]
        result[name]=dict(call,arguments=[origin(value,definitions,calls,names) for value in call['args']])
    send=result['descriptor_send']
    for argument in (3,4):
        need(send['arguments'][argument]==[dict(kind='opaque-output',call='gate_after_copy',argument=argument)],
             'Descriptor-send IR preserves earlier gate A3/A4 outputs')
    return result
