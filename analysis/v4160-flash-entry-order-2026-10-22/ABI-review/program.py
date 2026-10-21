"""Pure bounded static proof for the 100-byte C-produced program helper; no ISA execution."""
import re

EXPECTED='''lui 14 1073881088
lw 12 14 16
andi 10 10 -256
lui 13 65536
or 12 12 13
sw 14 12 16
lw 15 14 12
andi 15 15 1
bne 15 0 16
lui 14 1073881088
lw 15 14 12
andi 15 15 2
bne 15 0 26
lui 14 1073881088
addi 12 0 256
add 13 15 11
lw 16 13 0
add 13 15 10
sw 13 16 0
lw 13 14 12
andi 13 13 2
bne 13 0 56
addi 15 15 4
bne 15 12 40
lw 13 14 16
lui 15 2097152
or 13 13 15
sw 14 13 16
lui 15 1073881088
lw 13 15 12
andi 13 13 1
bne 13 0 82
lw 14 15 16
lui 13 4294901760
addi 13 13 -1
and 14 14 13
sw 15 14 16
ret 1'''


def need(value,why):
    if not value:raise ValueError(why)


def rows(body,decode):
    pc=0;result=[]
    while pc<len(body):
        r=decode(body,pc+0x8000);r['offset']=pc
        if r['target'] is not None:r['target']-=0x8000
        result.append(r);pc+=r['bytes']
    need(pc==len(body),'complete bounded instruction coverage')
    return result


def event_projection(decoded):
    loads=[r for r in decoded if r['op']=='lw' and r['rs1']==14 and r['immediate']==16]
    stores=[r for r in decoded if r['op']=='sw' and r['rs1']==14 and r['immediate']==16]
    align=[r for r in decoded if (r['op'],r['rd'],r['rs1'],r['immediate'])==('andi',10,10,-256)]
    need(loads and stores and len(align)==1,'one A0 alignment and first control effects')
    polls=[r for r in decoded if r['op']=='bne' and r['rs2']==0][:2]
    return dict(first_CTRL_read=loads[0]['offset'],A0_alignment=align[0]['offset'],first_CTRL_write=stores[0]['offset'],first_CTRL_scratch_GPR=loads[0]['rd'],first_CTRL_write_GPR=stores[0]['rs2'],initial_poll_GPRs=[r['rs1'] for r in polls],align_before_initial_read=align[0]['offset']<loads[0]['offset'],align_before_initial_write=align[0]['offset']<stores[0]['offset'])


def event_contract(decoded):
    p=event_projection(decoded)
    need(p['first_CTRL_read']<p['A0_alignment']<p['first_CTRL_write'],'A0 align must follow completed first read and precede first write')
    return p


def check_program(body,decode,negative_controls=True):
    need(len(body)==100,'actual full original 100-byte extent')
    decoded=rows(body,decode);projection=event_contract(decoded);lines=[]
    for r in decoded:
        op=r['op'];d=r['rd'];s=r['rs1'];t=r['rs2'];imm=r['immediate']
        if op=='bne':line=f'bne {s} {t} {r["target"]}'
        elif op=='sw':line=f'sw {s} {t} {imm}'
        elif op=='ret':line=f'ret {s}'
        elif op=='lui':line=f'lui {d} {imm}'
        elif op in ('add','and','or'):line=f'{op} {d} {s} {t}'
        else:line=f'{op} {d} {s} {imm}'
        lines.append(line)
    need(lines==EXPECTED.splitlines(),'complete admitted program100 pattern')
    written={r['rd'] for r in decoded if r['rd'] not in (0,None)}
    need(written=={10,12,13,14,15,16},'all encoded GPR destinations')
    need(len(decoded)==38,'original instruction count retained')
    boundaries={r['offset'] for r in decoded}
    branch_targets=[r['target'] for r in decoded if r['op']=='bne']
    need(branch_targets==[16,26,56,40,82] and all(t in boundaries for t in branch_targets),'five original interior branch roles')
    seed=[r for r in decoded if 30<r['offset']<40]
    need(not any(r['rd']==15 for r in seed),'second poll zero in A5 reaches copy without rewrite')
    negative=[]
    if negative_controls:
        # All are actual in-memory mutations of machine bytes. Nothing executes them.
        early=bytearray(body);early[4:10]=body[6:10]+body[4:6]
        late=bytearray(body);late[6:10]=bytes.fromhex('13050500');late[22:26]=body[6:10]
        trials=[('100B-but-align-before-read',early),('100B-but-align-after-write',late)]
        for label,offset,h in [('wrong-poll-register',0x10,'5047'),('wrong-first-poll-mask',0x12,'898b'),('wrong-second-poll-mask',0x1c,'858b'),('word-read-halfwidth',0x2c,'03980600'),('word-write-halfwidth',0x34,'23900601'),('wrong-count512',0x24,'13060020'),('wrong-stride2',0x3e,'8907'),('wrong-loop-target',0x40,'e394c7fc'),('wrong-final-mask',0x5a,'8176'),('wrong-return-GPR',0x62,'0281')]:
            mutant=bytearray(body);b=bytes.fromhex(h);need(mutant[offset:offset+len(b)]!=b,'actual changed raw bytes');mutant[offset:offset+len(b)]=b;trials.append((label,mutant))
        for label,mutant in trials:
            try:check_program(mutant,decode,negative_controls=False)
            except ValueError as ex:negative.append(dict(name=label,rejected=True,reason=str(ex),bytes=len(mutant)))
            else:raise ValueError('accepted machine counterexample '+label)
    return dict(passed=True,bytes=100,instructions=38,rows=decoded,event_order=projection,encoded_GPR_destinations=sorted(written),normal_outputs=dict(A0='D&FFFFFF00',A1='S unchanged',A2=256,A3='FFFEFFFF',A4='freshFinalCTRL&FFFEFFFF',A5='40022000',A6='lastSourceWord(S+252)'),known_interior_offsets=[16,26,40,56,82],copy_words=64,source_offset8_still_instruction_boundary=8 in boundaries,full_original_boundary_set_preserved=False,full_scratch_GPR_prefix_equivalence=False,pointwise_async_equivalence=False,physical_fault_prefix_equivalence=False,raw_machine_negatives=negative,target_execution=False,emulation=False)


def check_program_ir(text):
    need(text.count('load volatile i32')==8 and text.count('store volatile i32')==4,'all word-width volatile IR effects')
    need(not re.search(r'(load|store) volatile i(?:8|16|64)\b',text),'no changed volatile width')
    first_read=text.index('load volatile i32');first_write=text.index('store volatile i32')
    a0=list(re.finditer(r'asm sideeffect "", "=\{x10\},\{x10\},~\{memory\}"',text))
    need(len(a0)==2 and first_read<a0[0].start()<a0[1].start()<first_write,'A0 memory anchors ordered after read and before write')
    align=text.index(', -256');need(a0[0].start()<align<a0[1].start(),'typed C alignment between physical A0 bridges')
    need(text.count('"={x14},{x14},~{memory}"')==3,'three source-site base materializations')
    need(text.count('"={x15},{x15},~{memory}"')==4,'two poll/A5 plus index/final-base bridges')
    need('={x10},{x11},{x12},{x13},{x14},{x15},{x16},{x10},~{memory}' in text,'all normal output bindings')
    need('i32 256' in text and '2097152' in text and 'i32 -65537' in text,'count and final control masks')
    negative=[]
    for before,after,label in [('load volatile i32','load i32','lost-volatile'),('={x14},{x14},~{memory}','={x13},{x13},~{memory}','lost-base-site'),('{x16},{x10}','{x17},{x10}','wrong-lastword-output')]:
        changed=text.replace(before,after,1)
        try:
            if label=='lost-volatile':need(changed.count('load volatile i32')==8,'all word-width volatile IR effects')
            elif label=='lost-base-site':need(changed.count('"={x14},{x14},~{memory}"')==3,'three source-site base materializations')
            else:need('={x10},{x11},{x12},{x13},{x14},{x15},{x16},{x10},~{memory}' in changed,'all normal output bindings')
        except ValueError as ex:negative.append(dict(name=label,rejected=True,compiled=False,reason=str(ex)))
        else:raise ValueError('accepted IR transcript counterexample '+label)
    return dict(passed=True,volatile_i32_loads=8,volatile_i32_stores=4,A0_order_after_read_before_write=True,IR_transcript_negatives=negative,physical_fault_prefix_equivalence=False)
