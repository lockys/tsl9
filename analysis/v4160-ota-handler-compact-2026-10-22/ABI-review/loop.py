"""Bounded emitted-loop and private response SSA facts; no CPU/IR execution."""
import re


def need(value,message):
    if not value:raise ValueError(message)


def quarter(rows,relocations):
    sites=[r['offset'] for r in relocations if r['type']==17 and
           r['symbol']['name']=='__tsl9v4160_call_9c0a']
    need(len(sites)==1,'One actual quarter JAL, never four static callsites')
    call=sites[0];bypc={r['PC']:r for r in rows}
    branches=[r for r in rows if call<r['PC']<=call+24 and r['op']=='bne' and
              r['rs2']==0 and r['target'] is not None and call-12<=r['target']<call]
    need(len(branches)==1,'Actual simple backward nonzero-counter edge after the call')
    branch=branches[0];start=branch['target'];counter=branch['rs1']
    body=[r for r in rows if start<=r['PC']<call]
    arguments={reg:[r for r in body if r['rd']==reg][-1] for reg in (10,11)}
    need(all(r['op']=='mv' for r in arguments.values()),'Quarter A0/A1 come directly from the two live cursor registers')
    destination=arguments[10]['rs1'];source=arguments[11]['rs1']
    preserved={8,9,*range(18,28)}
    need(len({source,destination,counter})==3 and {source,destination,counter}<=preserved,
         'Distinct counter/source/destination in conventional callee-saved registers')
    prior=[r for r in rows if r['PC']<start and r['rd']==counter]
    need(prior and prior[-1]['op']=='addi' and prior[-1]['rs1']==0 and prior[-1]['immediate']==1024,
         'Actual dominating straight-line counter setup is literal1024')
    setup=prior[-1]
    need(not [r for r in rows if setup['PC']<r['PC']<start and r['target'] is not None],
         'No branch skips the local counter setup-to-header path')
    after=[r for r in rows if call<r['PC']<branch['PC']]
    facts={}
    for register,amount,name in ((counter,-256,'counter'),(destination,256,'destination'),(source,256,'source')):
        definitions=[r for r in after if r['rd']==register]
        need(len(definitions)==1 and definitions[0]['op']=='addi' and
             definitions[0]['rs1']==register and definitions[0]['immediate']==amount,
             'One exact native loop step for '+name)
        facts[name]=definitions[0]
    need(not [r for r in body if r['rd'] in (counter,destination,source)],
         'No hidden cursor/counter change before the actual quarter call')
    call_relocations={r['offset'] for r in relocations if r['type']==17}
    incoming=[r for r in rows if r['target'] is not None and r['PC'] not in call_relocations
              and start<=r['target']<=branch['PC']]
    need(incoming==[branch],'Only recorded local entry into the loop is its actual backedge')
    return dict(static_quarter_JALs=1,call_offset=call,header=start,setup=setup,
                argument_definitions={str(k):v for k,v in arguments.items()},steps=facts,backedge=branch,
                conditional_dynamic_calls=4,conditional_argument_offsets=[0,256,512,768],
                recurrence='1024 - 256*n; first zero at n=4; both argument cursors advance256 after each normal return',
                required_normal_return_and_preserved_registers=sorted((counter,source,destination)),
                source_named_S0_increment_before_call=True,physical_original_S0_prefix_equivalence=False,
                arbitrary_callee_effects_covered=False,computed_external_entries_excluded=False,
                unresolved_ET_REL_JAL_immediates_not_used_as_local_targets=True,
                target_execution=False,ISA_emulation=False)


def frame_contents(rows):
    saved=[]
    for row in rows[1:]:
        if row['op']!='sw' or row['rs1']!=2:break
        saved.append(dict(PC=row['PC'],register=row['rs2'],slot=row['immediate']))
    stores=[dict(PC=r['PC'],slot=r['immediate'],source_register=r['rs2']) for r in rows
            if r['op']=='sb' and r['rs1']==2]
    slots=sorted({r['slot'] for r in stores})
    need(len(saved)==10 and slots==[6,7],'Actual selected ten-save prefix and private response bytes SP+6/SP+7')
    pointers=[dict(PC=r['PC'],register=r['rd'],offset=r['immediate']) for r in rows
              if r['op']=='addi' and r['rs1']==2 and r['rd']!=2 and r['immediate']==6]
    need(pointers,'Actual source-owned response pointer materialization is SP+6')
    return dict(actual_save_prefix=saved,actual_reply_byte_stores=stores,
                actual_response_pointer_materializations=pointers,actual_reply_slots=[6,7],
                original_reply_slots=[12,13],original_saved_register_count=7,
                original_frame_contents_equal=False,original_save_order_equal=False,
                original_SP12_overlaps_native_saved_S7=True,
                pointer_numeric_identity_or_unbounded_callee_access_proved_irrelevant=False,
                require_provider_contract_before_rebinding_reply_pointer=True)


def response_ir(text):
    allocations=[list(item) for item in re.findall(r'^\s*(%\d+) = alloca (.*)$',text,re.M)]
    need(len(allocations)==1 and allocations[0][1].startswith('[2 x i8], align 1'),
         'Actual IR has exactly one separate two-byte response allocation, not an escaping argument struct')
    pointer=allocations[0][0]
    users=[line.strip() for line in text.splitlines() if re.search(r'ptr '+re.escape(pointer)+r'(?:,|\)| to )',line)]
    second=re.compile(r'getelementptr inbounds i8, ptr '+re.escape(pointer)+r', i32 1(?:,|$)')
    need(users and all('store volatile i8 ' in line or second.search(line)
                      or 'ptrtoint ptr '+pointer in line or '@llvm.lifetime.' in line for line in users),
         'Response pointer uses are byte stores, own second-byte address or explicit i32 call pointer')
    need(any('ptrtoint ptr '+pointer+' to i32' in line for line in users),
         'Actual response address is materialized for the opaque packet call')
    need(any('store volatile i8 ' in line and 'ptr '+pointer in line for line in users),
         'First response byte still has a volatile store')
    second_user=next(line for line in users if second.search(line));second_ssa=second_user.split(' = ',1)[0]
    need('store volatile i8 1, ptr '+second_ssa in text,'Actual second response byte remains a volatile one store')
    return dict(allocations=allocations,response_pointer=pointer,users=users,
                separate_volatile_two_byte_response=True,no_argument_struct_alloca=True,
                source_pointer_and_length2_preserved=True,physical_original_SP12_equal=False,
                unknown_resident_footprint_or_alias_proved=False)


def controls(raw,rows,relocations,fields,ctx):
    normal=quarter(rows,relocations);out={}
    changes=(('quarter_counter_start_changed',normal['setup'],1024^768),
             ('quarter_source_stride_changed',normal['steps']['source'],256^128))
    for name,row,immediate_xor in changes:
        need(row['bytes']==4,'Actual selected immediate control uses a complete32-bit source word')
        blob=bytearray(raw);offset=row['PC'];word=int.from_bytes(blob[offset:offset+4],'little')
        blob[offset:offset+4]=(word^(immediate_xor<<20)).to_bytes(4,'little')
        try:quarter(fields['rows'](bytes(blob),0,ctx),relocations)
        except ValueError:out[name]=True;continue
        raise ValueError('Unrejected actual loop operand counterexample '+name)
    return out
