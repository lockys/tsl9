"""Bounded static comparison, never an ISA interpreter or execution engine."""
import re

def need(value,why):
    if not value:raise ValueError(why)

def rows(body,decode):
    out=[];offset=0
    while offset<len(body):
        row=decode(body,offset+0x8000);row=dict(row,offset=offset)
        if row['target'] is not None:row['target']-=0x8000
        need(row['bytes'] in (2,4) and offset+row['bytes']<=len(body),'whole encoded instruction')
        out.append(row);offset+=row['bytes']
    need(offset==len(body),'exact byte coverage');return out

def compare(name,body,original,decode):
    need(len(body)==len(original),'complete original leaf extent')
    actual=rows(body,decode);expected=rows(original,decode)
    need(len(actual)==len(expected),'original leaf instruction count')
    for got,want in zip(actual,expected):
        fields=('offset','bytes','op','rd','rs1','rs2','immediate','target')
        need(all(got[k]==want[k] for k in fields),'all original instruction fields and frontiers '+name)
    need(body==original,'all five leaves must be byte-identical')
    return dict(passed=True,bytes=len(body),instructions=len(actual),byte_identical=body==original,all_original_instruction_boundaries=True,
                all_instruction_frontiers_same_architectural_integer_operation=True,commuted_ADD_offsets=[],rows=actual,
                asynchronous_physical_equivalence=False,physical_fault_equivalence=False,target_execution=False)

def ir_program(text):
    need(text.count('load volatile i32')==8 and text.count('store volatile i32')==4,'eight word loads/four word stores in source CFG')
    need(not re.search(r'(load|store) volatile i(?:8|16|64)\b',text),'word-width volatile effects only')
    first_read=text.index('load volatile i32');first_write=text.index('store volatile i32')
    bridges=lambda r:list(re.finditer(re.escape('asm sideeffect "", "={x'+str(r)+'},{x'+str(r)+'},~{memory}"'),text))
    a0=bridges(10);a3=bridges(13);a5=bridges(15)
    need(len(a0)==2 and len(a3)==3 and len(a5)==8 and len(bridges(14))==4,'fixed register site inventory')
    need(first_read<a5[0].start()<a3[0].start()<a0[0].start()<text.index(', -256')<a0[1].start()<a5[1].start()<first_write,'load A5, mask A3, align A0, RMW A5, first store order')
    need('={x10},{x11},{x12},{x13},{x14},{x15},{x16},{x10},~{memory}' in text,'complete fixed normal output bridge')
    need('i32 256' in text and '2097152' in text and 'i32 -65537' in text,'count and CTRL masks')
    need(text.count('asm sideeffect "add $0, $1, $2"')==2 and '={x13},{x11},{x15},~{memory}' in text and '={x13},{x10},{x15},~{memory}' in text,'two original ordered ADD address primitives')
    return dict(passed=True,volatile_i32_loads=8,volatile_i32_stores=4,original_first_RMW_register_and_alignment_order=True,
                branching_static_IR_only=True,target_execution=False)
