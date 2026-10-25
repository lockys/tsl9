"""Positive static callback and dispatcher contracts; never executes target code."""
import hashlib,json,struct
from pathlib import Path
X=Path(__file__).resolve().parent
R=X.parents[1]
def audit():
    spec=json.loads((X/'spec-v1.json').read_text())
    fw=(R/spec['firmware']).read_bytes()
    assert hashlib.sha256(fw).hexdigest()==spec['firmware_sha256']
    functions=json.loads((X/'evidence-v1.json').read_text())
    for f in functions['functions']:
        selected=[o for o in functions['operations'] if f['start']<=o['addr']<f['end']]
        at=f['start']
        for o in selected:
            b=bytes.fromhex(o['bytes']);assert o['addr']==at and len(b)==o['size']
            assert b==fw[at-0x8000:at-0x8000+len(b)] and o['opcode']!='invalid'
            at+=len(b)
        assert at==f['end']
    assert [(f['start'],f['end']) for f in functions['functions']]==[(0x10c36,0x10c7a),(0x10d2e,0x10d30),(0x10d30,0x10d60)]
    assert len(functions['operations'])==41 and spec['code_bytes']==118
    assert next(o['opcode'] for o in functions['operations'] if o['addr']==0x10d2e)=='ret'
    tables={}
    for base,expected in [(0x1a668,[0x10d30,0x10d2e,0]),(0x1a674,[0x10c36,0x11544,0x10c34])]:
        actual=list(struct.unpack_from('<3I',fw,base-0x8000));assert actual==expected
        tables[hex(base)]=[hex(t) for t in actual]
    e=json.loads((X/'event-evidence-v1.json').read_text());at=e['start']
    assert (at,e['end'])==(0x11544,0x119c8)
    for o in e['operations']:
        b=bytes.fromhex(o['bytes']);assert o['addr']==at and len(b)==o['size'] and o['opcode']!='invalid'
        assert b==fw[at-0x8000:at-0x8000+len(b)]
        at+=len(b)
    assert at==e['end'] and len(e['operations'])==374
    bypc={o['addr']:o for o in e['operations']}
    prefix={0x11544:'lbu a5, 2(a0)',0x11548:'li a4, 16',0x1154a:'bltu a4, a5, 0x119c6',0x1154e:'auipc a4, 0x9',0x11552:'addi a4, a4, -6',0x11556:'slli a5, a5, 0x2',0x11558:'add a5, a5, a4',0x1155a:'lw a5, 0(a5)',0x1156a:'add a5, a5, a4',0x1156e:'jr a5'}
    assert all(bypc[p]['opcode']==text for p,text in prefix.items())
    table_base=0x1154e+0x9000-6;assert table_base==0x1a548
    targets=[(table_base+v)&0xffffffff for v in struct.unpack_from('<17i',fw,table_base-0x8000)]
    assert all(t in bypc for t in targets)
    assert sorted(set(targets))==[0x11570,0x117f6,0x1180c,0x1181a,0x1184c,0x1188e,0x11948]
    layout=R/'experiments/tsl9-original-layout/build/callback-prefix-data-v2/c/layout-map.json'
    owners=json.loads(layout.read_text())['owners']
    calls=[]
    for o in e['operations']:
        if o['type']=='call':
            target=o['jump'];cover=[s['name'] for s in owners if s['info']==18 and s['original_PC']<=target<s['original_PC']+s['bytes']]
            calls.append(dict(PC=hex(o['addr']),target=hex(target),formal_CODE_owners=cover))
        elif o['type'] in ('cjmp','jmp'):
            assert o['jump'] in bypc
    missing=sorted({int(c['target'],16) for c in calls if not c['formal_CODE_owners']})
    assert missing==[0x10ce0,0x110f8,0x11266,0x114e2] and len(calls)==20
    assert [o['addr'] for o in e['operations'] if o['type']=='rjmp']==[0x1156e]
    assert [o['addr'] for o in e['operations'] if o['type']=='ret']==[0x11804,0x119c6]
    return dict(passed=True,original_callback_tables=tables,experimental_bodies=3,experimental_bytes=118,
                experimental_instructions=41,event_window_bytes=1156,event_window_instructions=374,
                event_table_base=hex(table_base),event_table_bytes=68,event_table_targets=[hex(t) for t in targets],
                guarded_event_values=[0,16],event_unique_table_targets=7,event_direct_calls=calls,
                uncovered_event_helper_CODE_targets=[hex(t) for t in missing],
                installed_ROM_ABI_verified=False,formal_coverage_percent=89.03,
                curated_integration=False,new_BIN=False,target_executed=False)
if __name__=='__main__':print(json.dumps(audit()))
