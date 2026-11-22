"""Args: v4.1.60 APP, V1.31 reference, rasm2. Xwchc; separated RAM, no interference."""
import runpy
from pathlib import Path

base=Path(__file__).parent
q=runpy.run_path(str(base/'check_v131_outer_record_return.py'))
g=q['g'];g['window'](g['b'],0x40000,0x4da70,0x4db18)
# Fail closed on changes to register/base provenance, branch edges or Xwchc fields.
for pc,want in {
    0x4daa0:'lui s1 0x20003',0x4dabe:'sb zero -95(s1)',
    0x4daf2:'lui s4 0x20003',0x4daf6:'lbu a0 848(s4)',0x4dafe:'addi s1 s1 -95',
    0x4db06:'beqz a0 0x4db3e',0x4db20:'beqz a0 0x4db3e',
    0x4db22:'lbu a2 848(s4)',0x4db26:'addi a5 s4 848',0x4db2a:'lbu a5 1(a5)',
    0x4db34:'sb a5 0(s1)',0x4db42:'lbu a0 948(a5)',0x4db46:'lbu a5 0(s1)',
}.items():
    _,op,args=g['code'][pc]
    if [op,*args]!=want.split():raise ValueError((hex(pc),op,args,want))
# Model both outcomes of first allocation for every source byte, with the APP-derived A=5.
# trace() verifies actual ordered reads/writes, fill extent, and second allocator arguments.
for neighbor in range(256):
    for ok in (False,True):q['trace'](ok,1,neighbor,5)
print('PASS: 512 post-allocation traces, A=5: null retains initialized zero (256 requests of 80); nonnull copies neighbor (only neighbor zero requests 80)')
