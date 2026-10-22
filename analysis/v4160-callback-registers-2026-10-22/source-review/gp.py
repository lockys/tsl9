"""Bounded six-use GP-source transformation and actual register-port checks."""
def source_identity(P,root):
    old=root/'experiments/tsl9-v4160-event-callback/src';new=root/'experiments/tsl9-v4160-callback-registers/src';pins=P.read(P.case(root,'v4160-event-callback-2026-10-22')/'source-review/source-reconciliation.json')['source_files']
    for n,pin in pins.items():P.need(P.sha(root/n)==pin,'Immutable prior algorithm/provider source '+n)
    c=(old/'callback.c').read_text(encoding='utf-8');actual=(new/'callback.c').read_text(encoding='utf-8');entry='__asm__ volatile("mv %0,gp":"=r"(h.values.gp)::"memory");';P.need(c.count('s->gp')==6 and c.count(entry)==1,'Exactly six logical GP uses and one native entry snapshot');expected=c.replace('s->gp','CB_GP(h)').replace(entry,'');P.need(actual==expected,'Only six live-GP uses and removed native entry snapshot; all algorithm/control/width code unchanged')
    io=(old/'io.h').read_text(encoding='utf-8');actual_io=(new/'io.h').read_text(encoding='utf-8');state='#define CB_STATE(h) ((h)->values)\n';post='    __asm__ volatile("mv %0,gp":"=r"(h->values.gp)::"memory");\n';helper='static inline uint32_t cb_native_gp(void){register uint32_t value __asm__("gp");__asm__ volatile("":"=r"(value)::"memory");return value;}\n#define CB_GP(h) ((void)(h),cb_native_gp())\n';needle='#define CB_READ(h,pc,a,w,out) do{(void)(pc);'
    P.need(io.count(post)==1 and io.count(needle)==1,'One native postcall snapshot and unique native macro insertion');expected_io=io.replace(state,state+'#define CB_GP(h) ((h)->values.gp)\n',1).replace(post,'').replace(needle,helper+needle);P.need(actual_io==expected_io,'Only explicit HOST identity GP macro and native live-register port replace unused snapshots');P.need((old/'callback.h').read_bytes()==(new/'callback.h').read_bytes(),'Header/API byte identity')
    P.need('cb_values *s=&CB_STATE(h);uint32_t *a=CB_ARGS(h);' in c and '#define CB_GP(h) ((h)->values.gp)' in actual_io,'HOST macro refers to identical stable carried field through fixed local alias')
    return dict(passed=True,mechanical_GP_use_replacements=6,removed_native_entry_snapshots=1,removed_native_postcall_snapshot_site=1,old_expanded_postcall_snapshots=15,HOST_field_alias_identity=True,HOST_algorithm_changed=False,HOST_tests_rerun=False,source_files={p.relative_to(root).as_posix():P.sha(p) for p in (new/'callback.c',new/'callback.h',new/'io.h')})

def machine(P,rows,ir):
    ports=P.uses(rows,3);P.need(len(ports)==6 and not any(r['rd']==3 for r in rows),'Exactly six actual live-GP uses, no physical GP writes or sixteen snapshot moves')
    wanted=[('lbu',148),('lbu',152),('add',None),('addi',128),('addi',128),('lh',42)];P.need([(r['op'],r['immediate']) for r in ports]==wanted and all(r['rs1']==3 for r in ports),'Actual six-source GP register ports, including lowered LH+SH')
    index={r['PC']:i for i,r in enumerate(rows)};third=ports[2];i=index[third['PC']];shift=rows[i-1];read=rows[i+1];P.need((shift['op'],shift['rd'],shift['immediate'])==('slli',third['rs2'],2) and read['op']=='lhu' and read['rs1']==third['rd'] and read['immediate']==150,'Static address algebra GP+(lane<<2)+0x96 equals original GP+0x94+(lane<<2)+2')
    for r in ports[3:5]:
        i=index[r['PC']];P.need(r['rd']==11 and any(x['op']=='jalr' and x['rd']==1 for x in rows[i+1:i+4]),'Fresh GP+0x80 feeds immediate opaque-call A1')
    second=ports[4];i=index[second['PC']];P.need(rows[i-1]['op']=='lw' and rows[i-1]['immediate']==316 and any(x['op']=='jalr' and x['rd']==1 for x in rows[max(0,i-4):i-1]),'Fresh postcopy GP use after actual copy call and fresh target slot load')
    last=ports[-1];i=index[last['PC']];P.need(rows[i+1]['op']=='sh' and rows[i+1]['rs2']==last['rd'] and rows[i+1]['memory_width']==16,'Native LH sign extension only forwarded through low16 descriptor SH at this boundary')
    count=ir.count('asm sideeffect "", "={x3},~{memory}"()');P.need(count==6 and 'mv $0,gp' not in ir and 'mv $0, gp' not in ir,'Six actual volatile fixed-x3 output ports in IR, no old snapshot assembly')
    return dict(passed=True,actual_live_GP_ports=ports,empty_volatile_IR_ports=count,GP_written=False,GP_preservation_assumed=False,postcopy_fresh_GP=True,last_source_LHU_lowered_to_LH_then_SH=True,full_temporary_GPR_identity=False)

def control(P,blob,entry,rows,decode,ir):
    first=P.uses(rows,3)[0];P.need(first['bytes']==4 and first['op']=='lbu','Actual direct first GP memory port');raw=bytearray(blob);at=first['PC']-entry;word=int.from_bytes(raw[at:at+4],'little');word=(word&~(31<<15))|(9<<15);raw[at:at+4]=word.to_bytes(4,'little');changed=P.fields(raw,entry,decode)
    try:machine(P,changed,ir)
    except ValueError as e:return dict(case='fresh GP load replaced with stale s1 base',PC=first['PC'],rejected=True,reason=str(e))
    raise ValueError('Actual GP port substitution incorrectly accepted')
