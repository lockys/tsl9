#!/usr/bin/env python3
"""Build/replay receiver and consumer linkage evidence; never execute target code."""
import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess

HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-receive-wrapper'
SOURCE = MODEL + '/src/receive_wrapper.c'
SOURCE_PIN = 'df1e1f0633c50b8b2c9f7a58d2ac1e45664057de107dc04d28eca9e931538cdc'
COMPONENT_PIN = 'a19d817f2206b999d626e24cbb7f744f5646a2b465c72ccd1c72a5388de4d5fe'
PIPELINE_PIN = '26b1914e3cd98638fd1d0b180a21a300ffb907e262194491a6b9f6b1f178bfa1'
CONSUMER = 'experiments/tsl9-irq-flag-consumer'
CONSUMER_SOURCE_PIN = '9edf5f2571991062605863e88adf8028d4d54efc8d3e518c540026bd50b0ef12'
CONSUMER_CHECK_PIN = '5a7314d3f63e20babca57443ed55efcb00ff97487503e409b68ebe1d56871550'
PARSER = 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_PIN = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
FIRMWARE = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_PIN = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ORIGINAL_PIN = 'b12abed39cf1cc897ab42a51b6cfce8c150031819f747aab095fffd618ae6f80'
NONCALL_PIN = 'e862be93e54bd3d9027def687318afe6b59fa8676bac2197f9d4d2f0f31e01aa'
STDINT_PIN = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
ENTRY = 'tsl9_receive_entry_16b0a'
BODY = 'tsl9_receive_body'
CE = 'tsl9_flag_consumer_entry_17002'
CB = 'tsl9_flag_consumer_body'
PROVIDERS = ['tsl9_register_read_entry_16994', 'tsl9_receive_buffer_entry_16a7c',
             'tsl9_register_write_entry_16a30']
CALLS = [(14,PROVIDERS[0],0x16994,1),(32,PROVIDERS[1],0x16a7c,1),
         (46,PROVIDERS[1],0x16a7c,1),(66,PROVIDERS[2],0x16a30,0)]
ORIGINAL = bytes.fromhex('41119305c00222c426c206c6aa84eff0dfe7937715002a8491c7930510062685'
                         'eff03ff5098811c4930510072685eff05ff42244b2402685924401469305c00241016ff05fee')
SITES = [(0,2),(2,4),(6,2),(8,2),(10,2),(12,2),(14,4),(18,4),(22,2),(24,2),
         (26,4),(30,2),(32,4),(36,2),(38,2),(40,4),(44,2),(46,4),(50,2),(52,2),
         (54,2),(56,2),(58,2),(60,4),(64,2),(66,4)]
ENTRY_IR_PIN = 'f830b0e1e0b61ce1f4d539653463677e0b01e198393cf65a4a31bef84e34e657'
BODY_IR_PIN = {'c':'6bcacd5c234c5470bafa8a2928a4a9ec72b40d50c895daa01f4d43899b1ddc87',
               'cpp':'7819d105fec6a0b9c5cdc7872b6fb803411058c6a550e464e418c1fbfda28da9'}
ARTIFACTS = {'receiver.o','receiver.ll','receiver.d','consumer.o','consumer.ll','consumer.d',
             'RECEIVER-OPEN-CALLS.o','PIPELINE-OPEN-CALLS.o',
             *[name+'.log' for name in ('receiver-compile','receiver-IR','consumer-compile','consumer-IR',
                                       'receiver-combine','pipeline-combine','receiver-object','consumer-object',
                                       'receiver-combined','pipeline-combined')]}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def sx(value,bits):
    return value-(1<<bits) if value & (1<<(bits-1)) else value


def noncall(code):
    return b''.join(code[at:at+size] for at,size in SITES if at not in {14,32,46,66})


def trace(code,resolved=False):
    """Finite typed RV32 operand reader, no CPU/ISA evaluation."""
    need(len(code)==70,'Exact70B receiver extent')
    half=lambda at:struct.unpack_from('<H',code,at)[0]
    word=lambda at:struct.unpack_from('<I',code,at)[0]

    def immediate(at,funct,rd,rs1,value):
        w=word(at)
        need((w&127,w>>12&7,w>>7&31,w>>15&31,sx(w>>20,12))==(0x13,funct,rd,rs1,value),
             'Typed receiver immediate at+'+str(at))

    def compressed(at,funct,rd,value):
        h=half(at)
        need((h&3,h>>13,h>>7&31,sx(((h>>12&1)<<5)|(h>>2&31),6))==(1,funct,rd,value),
             'Typed receiver compressed immediate at+'+str(at))

    def move(at,rd,rs2):
        h=half(at)
        need((h&3,h>>12,h>>7&31,h>>2&31)==(2,8,rd,rs2),'Typed live-register MV at+'+str(at))

    def store(at,rs2,offset):
        h=half(at)
        need((h&3,h>>13,h>>2&31,((h>>9&15)<<2)|((h>>7&3)<<6))==(2,6,rs2,offset),
             'Typed original frame store at+'+str(at))

    def load(at,rd,offset):
        h=half(at)
        need((h&3,h>>13,h>>7&31,((h>>12&1)<<5)|((h>>4&7)<<2)|((h>>2&3)<<6))==(2,2,rd,offset),
             'Typed fresh frame reload at+'+str(at))

    def branch(at,rs1,target):
        h=half(at)
        displacement=sx(((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)
                        |((h>>3&3)<<1)|((h>>2&1)<<5),9)
        need((h&3,h>>13,8+(h>>7&7),at+displacement)==(1,6,rs1,target),
             'Typed live-register BEQZ at+'+str(at))

    compressed(0,0,2,-16);immediate(2,0,11,0,44)
    store(6,8,8);store(8,9,4);store(10,1,12);move(12,9,10)
    immediate(18,7,15,10,1);move(22,8,10);branch(24,15,36)
    immediate(26,0,11,0,97);move(30,10,9)
    h=half(36)
    need((h&3,h>>13,h>>10&3,8+(h>>7&7),sx(((h>>12&1)<<5)|(h>>2&31),6))==(1,4,2,8,2),
         'Then-live S0 ANDI2 after first possible callee')
    branch(38,8,50);immediate(40,0,11,0,113);move(44,10,9)
    load(50,8,8);load(52,1,12);move(54,10,9);load(56,9,4)
    compressed(58,2,12,0);immediate(60,0,11,0,44);compressed(64,0,2,16)
    calls=[]
    for at,symbol,target,rd in CALLS:
        w=word(at)
        delta=sx(((w>>31)<<20)|((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12),21)
        need((w&127,w>>7&31)==(0x6f,rd),'JAL link versus true-tail register at+'+str(at))
        if resolved:
            need(0x16b0a+at+delta==target,'Original resolved receiver target at+'+str(at))
        else:
            need(w==(0xef if rd else 0x6f),'Open receiver JAL raw immediate zero at+'+str(at))
        calls.append(dict(offset=at,rd=rd,symbol=symbol,original_target=hex(target),
                          original_continuation=hex(0x16b0a+at+4) if rd else None,
                          true_tail=(rd==0),pending_relocation=not resolved))
    return dict(bytes=70,instructions=26,calls=calls,
                rows=[dict(offset=at,bytes=size,hex=code[at:at+size].hex()) for at,size in SITES],
                frame_bytes=16,entry_bytes=14,body_bytes=56,
                prefix_order=['SP-16','A1=44','SW S0,8SP','SW S1,4SP','SW RA,12SP','S1=entryA0'],
                finish_order=['fresh S0,8SP','fresh RA,12SP','A0=then-live S1','fresh S1,4SP',
                              'A2=0','A1=44','SP+16','JAL x0 open write provider'],
                second_predicate='then-live S0&2; no cached pre-callee status',
                branches=[[24,36],[38,50]],ordinary_C_callee_preservation_assumed=False)


def flags(mode,receiver):
    need(mode in ('c','cpp'),'Known language')
    return ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr_zifencei','-mabi=ilp32','-Oz',
            '-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector',
            '-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections',
            '-fdata-sections','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++',
            '-std=c11' if mode=='c' else '-std=c++17',*(['-fno-exceptions'] if mode=='cpp' else []),
            *['-ffixed-x'+str(n) for n in range(1,32) if n not in (set(range(10,16)) if receiver else {10,14,15})]]


def portable(value,root,tools,header):
    text=str(value).replace('\\','/')
    for path,token in [(header.parent,'${CLANG_INCLUDE}'),(tools['clang'].parent,'${LLVM_BIN}'),(root,'${PROJECT_ROOT}')]:
        prefix=path.as_posix()
        if text==prefix or text.startswith(prefix+'/'):
            return token+text[len(prefix):]
    return text


def portable_record(value):
    if isinstance(value,dict):
        for key,item in value.items():portable_record(key);portable_record(item)
    elif isinstance(value,list):
        for item in value:portable_record(item)
    elif isinstance(value,str):
        need(not re.search(r'(?i)([a-z]:[/\\]|/(?:users|home)/|\\\\)',value)
             and not value.startswith('/'),'Portable receipt fields only')


def load(root,tool_dir):
    need(HERE==root/MODEL,'Canonical receiver root')
    for name,pin in [(SOURCE,SOURCE_PIN),(MODEL+'/component.ld',COMPONENT_PIN),(MODEL+'/pipeline.ld',PIPELINE_PIN),
                     (CONSUMER+'/src/flag_consumer.c',CONSUMER_SOURCE_PIN),(CONSUMER+'/verify.py',CONSUMER_CHECK_PIN),
                     (PARSER,PARSER_PIN)]:
        need(sha(root/name)==pin,'Frozen dependency: '+name)
    tools={n:(tool_dir/(n+('.exe' if os.name=='nt' else ''))).resolve() for n in TOOLS}
    need(all(sha(tools[n])==pin for n,pin in TOOLS.items()),'Pinned existing LLVM tools')
    header=tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
    need(sha(header)==STDINT_PIN,'Pinned compiler stdint resource')
    prior=runpy.run_path(str(root/CONSUMER/'verify.py'))
    return tools,header,runpy.run_path(str(root/PARSER))['ELF'],prior


def inputs(root,tools,header):
    files=[Path(__file__).resolve(),root/SOURCE,HERE/'component.ld',HERE/'pipeline.ld',
           root/CONSUMER/'src/flag_consumer.c',root/CONSUMER/'verify.py',root/PARSER,root/FIRMWARE,header,*tools.values()]
    return {portable(p,root,tools,header):sha(p) for p in sorted(files)}


def originals(root,prior):
    image=(root/FIRMWARE).read_bytes()
    need(len(image)==76800 and digest(image)==IMAGE_PIN,'Exact original Runtime')
    receiver=image[0xeb0a:0xeb50];consumer=image[0xf002:0xf040]
    need(receiver==ORIGINAL and digest(receiver)==ORIGINAL_PIN and digest(noncall(receiver))==NONCALL_PIN,
         'Original receiver70B and noncall54B')
    need(consumer==prior['ORIGINAL'] and digest(consumer)==prior['ORIGINAL_PIN'],'Original consumer62B')
    return dict(receiver=trace(receiver,True),consumer=prior['trace'](consumer,True))


def recipes(root,folder,mode,tools):
    jobs=[]
    for name,source,receiver in [('receiver',root/SOURCE,True),('consumer',root/CONSUMER/'src/flag_consumer.c',False)]:
        common=[tools['clang'],*flags(mode,receiver)]
        jobs += [(name+'-compile',[*common,'-c','-MD','-MF',folder/(name+'.d'),'-MT',name+'.o',source,'-o',folder/(name+'.o')]),
                 (name+'-IR',[*common,'-S','-emit-llvm',source,'-o',folder/(name+'.ll')])]
    jobs += [('receiver-combine',[tools['ld.lld'],'-r','--no-relax','-T',HERE/'component.ld',folder/'receiver.o','-o',folder/'RECEIVER-OPEN-CALLS.o']),
             ('pipeline-combine',[tools['ld.lld'],'-r','--no-relax','-T',HERE/'pipeline.ld',folder/'consumer.o',folder/'receiver.o',
                                  '-o',folder/'PIPELINE-OPEN-CALLS.o'])]
    for label,name in [('receiver-object','receiver.o'),('consumer-object','consumer.o'),
                       ('receiver-combined','RECEIVER-OPEN-CALLS.o'),('pipeline-combined','PIPELINE-OPEN-CALLS.o')]:
        jobs.append((label,[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/name]))
    return jobs


def dependencies(root,folder,tools,header):
    result={}
    for name,source in [('receiver',root/SOURCE),('consumer',root/CONSUMER/'src/flag_consumer.c')]:
        target,separator,tail=(folder/(name+'.d')).read_text().replace('\\\n',' ').partition(':')
        paths={Path(re.sub(r'\\(.)',r'\1',x)).resolve() for x in re.findall(r'(?:\\.|[^\s])+',tail)}
        need(separator and target==name+'.o' and paths=={source,header},'Exact '+name+' MD source/header closure')
        result[name]={portable(p,root,tools,header):sha(p) for p in sorted(paths)}
    return result


def normalized_ir(text):
    found=re.findall(r'define[^\n]*@([^ (]+)\([^\n]*\{\n(.*?)\n}',text,re.S)
    need(len(found)==2 and {n for n,_ in found}=={ENTRY,BODY},'Exactly two receiver IR functions')
    result={}
    for name,body in found:
        lines=[]
        for line in body.splitlines():
            line=line.split(';',1)[0].strip()
            if line:lines.append(re.sub(r' #\d+\b','',re.sub(r', ![A-Za-z.]+ !\d+','',line)))
        result[name]='\n'.join(lines)+'\n'
    return result


def ir_contract(text,mode,full=True):
    bodies=normalized_ir(text);entry=bodies[ENTRY];body=bodies[BODY]
    prefix=(r'tail call void asm sideeffect "addi sp, sp, -16\0Ali a1, 44\0Asw s0, 8(sp)\0Asw s1, 4(sp)\0Asw ra, 12(sp)\0Amv s1, a0\0A", ""()'
            +'\nunreachable\n')
    need(entry==prefix,'Original14B architectural frame/input order')
    need('alloca ' not in body and not re.search(r'\bcall\b[^\n]*@[A-Za-z_]',body),'No extra C frame or ordinary call')
    anchors=['%6 = and i32 %5, 1','br i1 %10, label %18, label %11',
             r'asm sideeffect "mv s0, a0\0A", "{x10},{x15},~{memory}"(i32 %9, i32 %8)',
             r'callbr void asm sideeffect "andi s0, s0, 2\0Abeqz s0, ${0:l}\0A", "!i,~{memory}"()',
             'to label %19 [label %26]',
             '%12 = tail call i32 asm sideeffect "", "={x11},{x11},~{memory}"(i32 97)',
             '%20 = tail call i32 asm sideeffect "", "={x11},{x11},~{memory}"(i32 113)',
             r'asm sideeffect "lw s0, 8(sp)\0Alw ra, 12(sp)\0A", "~{memory}"()',
             r'asm sideeffect "lw s1, 4(sp)\0A", "~{memory}"()',
             '%29 = tail call i32 asm sideeffect "", "={x12},{x12},~{memory}"(i32 0)']
    need(all(anchor in body for anchor in anchors),'Then-live S0 snapshot/branch and fresh frame ordering')
    s1='tail call '+('noundef ' if mode=='cpp' else '')+r'i32 asm sideeffect "mv $0, s1\0A", "={x10},~{memory}"()'
    need(body.count(s1)==3 and all('%'+str(n)+' = '+s1 in body for n in (13,21,27)),
         'Three actual then-live S1 imports; no cached channel')
    call_constraints=r'"={x10},={x11},{x10},{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"'
    for number,provider,args in [(4,PROVIDERS[0],'i32 %2, i32 %3'),(17,PROVIDERS[1],'i32 %15, i32 %16'),
                                  (25,PROVIDERS[1],'i32 %23, i32 %24')]:
        literal='%'+str(number)+r' = tail call { i32, i32 } asm sideeffect "jal ra, '+provider+r'\0A", '+call_constraints+'('+args+')'
        need(literal in body,'Exact private read/receive JAL bank at SSA'+str(number))
    tail=(r'tail call void asm sideeffect "addi sp, sp, 16\0Aj tsl9_register_write_entry_16a30\0A", '
          r'"{x10},{x11},{x12},~{memory}"(i32 %28, i32 44, i32 %29)'+'\nunreachable\n')
    need(body.endswith(tail),'True tail with A0=currentS1 A1=44 A2=0 after SP restore')
    need(body.index(r'lw s0, 8(sp)\0Alw ra, 12(sp)')<body.index('%27 = '+s1)<body.index(r'lw s1, 4(sp)'),
         'Fresh S0/RA reload precedes live S1 move and S1 restore')
    if full:
        need(digest(entry.encode())==ENTRY_IR_PIN and digest(body.encode())==BODY_IR_PIN[mode],
             'Complete mode-specific receiver SSA/callbr/port hash')
    return dict(entry_sha256=digest(entry.encode()),body_sha256=digest(body.encode()),body_lines=len(body.splitlines()),
                then_live_S1_imports=3,then_live_S0_callbr=True,cached_S0_or_S1_across_call_assumed=False,
                allocator_bank=['a0','a1','a2','a3','a4','a5'],reserved_architecture_ports=['ra','sp','s0','s1'],
                downstream_full_register_preservation_proved=False)


def elf_header(elf):
    h=struct.unpack_from('<16sHHIIIIIHHHHHH',elf.raw)
    need(elf.kind==1 and elf.flags==1 and h[3]==1 and h[4]==h[5]==h[9]==h[10]==0 and h[8]==52 and h[11]==40,
         'ET_REL RVC only; no executable entry or program mapping')


def metadata(elf,kind):
    # No carrier/data/NOBITS/unwind or extra executable sections are allowed.
    if kind=='native':
        alloc=[('.text.'+ENTRY,14),('.text.'+BODY,56)];relaname='.rela.text.'+BODY;relabytes=48
    else:
        alloc=[('.receiver' if kind=='receiver' else '.pipeline',70 if kind=='receiver' else 132)]
        relaname='.rela.receiver' if kind=='receiver' else '.rela.pipeline';relabytes=48 if kind=='receiver' else 72
    actual=[(s['name'],s['size']) for s in elf.sections if s['flags']&2 and s['size']]
    need(actual==alloc,'Exact allocated code inventory and lengths')
    for s in elf.sections:
        need(s['address']==0,'All ET_REL section VAs zero; no nominal placement')
        if s['flags']&2:
            need(s['type']==1 and s['flags']==6 and s['alignment']==2 and s['entry_size']==0,'AX only alignment2 sections')
        if s['type'] in (4,9):
            need(s['name']==relaname and s['type']==4 and s['flags']==64 and s['size']==relabytes
                 and s['alignment']==4 and s['entry_size']==12,'Exact RELA section shape')
    allowed={s for s,_ in alloc}|{'.text',relaname,'.llvm_addrsig','.symtab','.strtab',''}
    allowed|=({'.comment','.note.GNU-stack','.riscv.attributes'} if kind=='native' else {'.shstrtab'})
    need({s['name'] for s in elf.sections}==allowed and len(elf.sections)==len(allowed),'Complete known section inventory')
    need(elf.byname['.text']['size']==0,'No unowned extra text')
    need(elf.byname['.symtab']['size']==16*len(elf.symbols),'Complete symbol table closure')
    for name in ('.strtab',*(['.shstrtab'] if kind!='native' else [])):
        s=elf.byname[name];need(s['type']==3 and s['flags']==0 and s['alignment']==1,'String-table metadata')
    if kind=='native':
        expected=[('',0,0,0,0,0,0,0,0),('.strtab',3,0,0,273,0,0,1,0),('.text',1,6,0,0,0,0,2,0),
                  ('.text.'+ENTRY,1,6,0,14,0,0,2,0),('.text.'+BODY,1,6,0,56,0,0,2,0),
                  (relaname,4,64,0,48,10,4,4,12),('.comment',1,48,0,159,0,0,1,1),
                  ('.note.GNU-stack',1,0,0,0,0,0,1,0),('.riscv.attributes',0x70000003,0,0,64,0,0,1,0),
                  ('.llvm_addrsig',0x6fff4c03,0x80000000,0,2,10,0,1,0),('.symtab',2,0,0,176,1,6,4,16)]
    else:
        pipeline=kind=='pipeline'
        expected=[('',0,0,0,0,0,0,0,0),(alloc[0][0],1,6,0,132 if pipeline else 70,0,0,2,0),
                  ('.text',1,6,0,0,0,0,2,0),(relaname,4,64,0,72 if pipeline else 48,5,1,4,12),
                  ('.llvm_addrsig',0x6fff4c03,0x80000000,0,4 if pipeline else 2,0,0,1,0),
                  ('.symtab',2,0,0,304 if pipeline else 208,7,12 if pipeline else 8,4,16),
                  ('.shstrtab',3,0,0,72,0,0,1,0),('.strtab',3,0,0,258 if pipeline else 172,0,0,1,0)]
    fields=('name','type','flags','address','size','link','info','alignment','entry_size')
    need([tuple(s[k] for k in fields) for s in elf.sections]==expected,'Exact full section metadata closure')
    return [{k:s[k] for k in ('name','type','flags','address','size','link','info','alignment','entry_size')} for s in elf.sections]


def definitions(elf,kind):
    expected={ENTRY:(0,14),BODY:(0 if kind=='native' else 14 if kind=='receiver' else 76,56)}
    if kind=='pipeline':expected={CE:(0,8),CB:(8,54),ENTRY:(62,14),BODY:(76,56)}
    globals_=[s for s in elf.symbols if s['info']>>4 in (1,2)]
    defs={s['name']:s for s in globals_ if s['index']!=0}
    need(set(defs)==set(expected) and len(globals_)==len(expected)+3,'Only genuine function defs and three UND providers')
    for name,(value,size) in expected.items():
        s=defs[name]
        need(s['info']==18 and s['other']==0 and s['value']==value and s['size']==size,'Exact FUNC size/value/binding')
        owner=elf.sections[s['index']]
        need(owner['name']==('.text.'+name if kind=='native' else '.receiver' if kind=='receiver' else '.pipeline'),
             'Genuine FUNC section ownership')
    und=[s for s in globals_ if s['index']==0]
    need({s['name'] for s in und}==set(PROVIDERS) and len(und)==3
         and all(s['info']==16 and s['other']==s['value']==s['size']==0 for s in und),'Three exact strong UND providers')
    need(not any(s['index']==65521 for s in globals_),'No global ABS provider')
    fields=('name','value','size','info','other','index')
    if kind=='native':
        local_rows=[('',0,0,0,0,0),('receive_wrapper.c',0,0,4,0,65521),('$x.0',0,0,0,0,3),
                    ('$x.1',0,0,0,0,4),('$d.2',0,0,0,0,6),('$d.3',0,0,0,0,8)]
    elif kind=='receiver':
        local_rows=[('',0,0,0,0,0),('receive_wrapper.c',0,0,4,0,65521),('$x.0',0,0,0,0,1),
                    ('$x.1',14,0,0,0,1),('$d.3',0,0,0,0,65521),('',0,0,3,0,1),
                    ('',0,0,3,0,2),('',0,0,3,0,4)]
    else:
        local_rows=[('',0,0,0,0,0),('flag_consumer.c',0,0,4,0,65521),('$x.0',0,0,0,0,1),
                    ('$x.1',8,0,0,0,1),('$d.3',0,0,0,0,65521),('',0,0,3,0,2),('',0,0,3,0,4),
                    ('receive_wrapper.c',0,0,4,0,65521),('$x.0',62,0,0,0,1),('$x.1',76,0,0,0,1),
                    ('$d.3',0,0,0,0,65521),('',0,0,3,0,1)]
    need([s for s in elf.symbols if s['info']>>4==0]==[dict(zip(fields,row)) for row in local_rows],
         'Exact local metadata symbols; no local FUNC or alias provider')
    for s in elf.symbols:
        if s['info']>>4:continue
        need(s['name']=='' or s['name'] in ('receive_wrapper.c','flag_consumer.c') or re.fullmatch(r'\$(?:x|d)\.\d+',s['name']),
             'Known local metadata only; no hidden provider')
        if s['info']&15==4:need(s['index']==65521 and s['value']==s['size']==0,'Local FILE metadata only')
        if s['name'].startswith('$x.'):
            need(0<s['index']<len(elf.sections) and elf.sections[s['index']]['flags']==6,'Code mapping-symbol owner')
    return defs,und


def relocation_contract(elf,kind,defs,und):
    byname={s['name']:s for s in und};byname.update(defs)
    owner='.text.'+BODY if kind=='native' else '.receiver' if kind=='receiver' else '.pipeline'
    expected=[]
    if kind=='pipeline':
        expected += [dict(owner=owner,offset=at,type=17,addend=0,symbol=defs[ENTRY]) for at in (22,48)]
    for at,name,_,_ in CALLS:
        expected.append(dict(owner=owner,offset=at-14 if kind=='native' else at+(62 if kind=='pipeline' else 0),
                             type=17,addend=0,symbol=byname[name]))
    need(elf.relocations==expected,'Exact JAL17 closure, sites, zero addends and genuine targets')
    return expected


def elf_contract(elf,kind,prior):
    elf_header(elf);sections=metadata(elf,kind);defs,und=definitions(elf,kind)
    relocs=relocation_contract(elf,kind,defs,und)
    code=elf.function_bytes(defs[ENTRY])+elf.function_bytes(defs[BODY]);observed=trace(code)
    need(noncall(code)==noncall(ORIGINAL) and digest(noncall(code))==NONCALL_PIN,'Complete original54 noncall bytes')
    if kind!='native':
        section=elf.byname['.receiver' if kind=='receiver' else '.pipeline']
        expected=code
        if kind=='pipeline':
            consumer=elf.function_bytes(defs[CE])+elf.function_bytes(defs[CB]);prior['trace'](consumer)
            need(prior['noncall'](consumer)==prior['noncall'](prior['ORIGINAL']),'Pipeline consumer unchanged outside its two JALs')
            expected=consumer+code
        need(elf.data(section)==expected,'Actual contiguous entry/body/pipeline bytes; no padding')
    return dict(kind=kind,ET_REL=True,sections=sections,functions=[defs[n] for n in defs],
                UND=und,local_ABS_metadata=[s for s in elf.symbols if s['index']==65521 and not s['info']>>4],
                global_ABS_providers=[],relocations=relocs,receiver_trace=observed,
                receiver_open_code_sha256=digest(code),noncall54_sha256=digest(noncall(code)),
                internal_definition_linkage_evidence=(kind=='pipeline'),machine_JALs_resolved=False)


class MemoryFile:
    def __init__(self,data):self.data=data
    def read_bytes(self):return self.data


def negatives(reader,native,combined,pipeline,ir,mode,prior):
    result=[];funcs={s['name']:s for s in combined.symbols if s['info']==18}
    code=combined.function_bytes(funcs[ENTRY])+combined.function_bytes(funcs[BODY])
    def reject(label,operation,category,full=False):
        try:operation()
        except ValueError as error:result.append(dict(label=label,category=category,rejected_by=str(error),full_hash_used=full))
        else:raise ValueError('Negative accepted: '+label)
    for label,at,mask in [('SP-allocation',0,32),('A1-prefix44',4,16),('saveS0-slot',7,2),('saveS1-register',8,4),
                          ('saveRA-slot',11,2),('entry-liveS1',12,4),('read-JAL-link',14,128),('first-status-mask',20,16),
                          ('status-S0-snapshot',22,4),('first-branch',25,32),('first-buffer97',28,16),('liveS1-before-first',30,4),
                          ('second-liveS0-mask',36,4),('second-liveS0-branch',38,4),('second-buffer113',42,16),
                          ('liveS1-before-second',44,4),('freshS0-slot',50,16),('freshRA-slot',52,16),
                          ('liveS1-before-restore',54,4),('freshS1-slot',56,16),('tail-A2-zero',58,4),('tail-A1-44',62,16),
                          ('SP-restore',64,32),('true-tail-not-JALRA',66,128),('tail-immediate-open',69,1)]:
        changed=bytearray(code);changed[at]^=mask
        reject(label,lambda changed=changed:trace(bytes(changed)),'typed-raw')
    # Exercise typed original target decoding without a source/full-code digest.
    changed=bytearray(ORIGINAL);changed[17]^=1
    reject('resolved-original-call-target',lambda:trace(bytes(changed),True),'typed-original-target')

    def mutate(elf,offset,fmt,value):
        raw=bytearray(elf.raw);struct.pack_into(fmt,raw,offset,value);return reader(MemoryFile(bytes(raw)))
    r=combined.byname['.rela.receiver']['offset']
    for index,(at,_,_,_) in enumerate(CALLS):
        reject('RELA-site-'+str(at),lambda index=index,at=at:
               elf_contract(mutate(combined,r+12*index,'<I',at+2),'receiver',prior),'actual-ELF-relocation')
    reject('RELA-type-CALL',lambda:elf_contract(mutate(combined,r+4,'<I',(10<<8)|18),'receiver',prior),'actual-ELF-relocation')
    reject('RELA-addend',lambda:elf_contract(mutate(combined,r+8,'<i',4),'receiver',prior),'actual-ELF-relocation')
    symtab=pipeline.byname['.symtab'];entry=next(i for i,s in enumerate(pipeline.symbols) if s['name']==ENTRY)
    reject('pipeline-fake-receiver-offset',lambda:elf_contract(mutate(pipeline,symtab['offset']+16*entry+4,'<I',64),'pipeline',prior),
           'actual-ELF-adjacency')
    rawrel=pipeline.byname['.rela.pipeline']['offset'];consumer_target_index=pipeline.symbols.index(next(s for s in pipeline.symbols if s['name']==ENTRY))
    reject('pipeline-internal-call-wrong-type',lambda:elf_contract(mutate(pipeline,rawrel+4,'<I',(consumer_target_index<<8)|18),'pipeline',prior),
           'actual-ELF-relocation')
    global_und=next(i for i,s in enumerate(pipeline.symbols) if s['name']==PROVIDERS[0])
    reject('fake-ABS-provider',lambda:elf_contract(mutate(pipeline,symtab['offset']+16*global_und+14,'<H',65521),'pipeline',prior),
           'actual-ELF-provider')

    for label,old,new in [('entry-frame-order',r'li a1, 44\0Asw s0, 8(sp)',r'sw s0, 8(sp)\0Ali a1, 44'),
                          ('first-C-mask','%6 = and i32 %5, 1','%6 = and i32 %5, 2'),
                          ('snapshot-S0',r'mv s0, a0\0A',r'mv s0, a1\0A'),
                          ('callbr-liveS0',r'andi s0, s0, 2\0A',r'andi s0, s0, 1\0A'),
                          ('callbr-destination','to label %19 [label %26]','to label %26 [label %19]'),
                          ('fresh-liveS1',r'mv $0, s1\0A',r'mv $0, s0\0A'),
                          ('first-buffer-address','(i32 97)','(i32 98)'),
                          ('second-buffer-address','(i32 113)','(i32 114)'),
                          ('callee-UND-target',PROVIDERS[1],'invented_provider'),
                          ('RA-reload-slot',r'lw ra, 12(sp)\0A',r'lw ra, 8(sp)\0A'),
                          ('S1-restore-slot',r'lw s1, 4(sp)\0A',r'lw s1, 8(sp)\0A'),
                          ('tail-A2-zero','(i32 0)','(i32 1)'),
                          ('tail-is-call',r'j tsl9_register_write_entry_16a30\0A',r'jal ra, tsl9_register_write_entry_16a30\0A')]:
        need(old in ir,'Actual receiver IR mutation anchor')
        reject(label,lambda old=old,new=new:ir_contract(ir.replace(old,new,1),mode,False),'IR-finite-gates')
    for label,old,new in [('full-SSA-first-status-input','%6 = and i32 %5, 1','%6 = and i32 %3, 1'),
                          ('full-SSA-tail-A0-input','(i32 %27)','(i32 %9)')]:
        changed=ir.replace(old,new,1)
        # These intentionally bypass finite anchors but not the whole-SSA pin.
        if label=='full-SSA-first-status-input':
            # Keep its anchored line; change the extraction feeding that line.
            changed=ir.replace('%5 = extractvalue { i32, i32 } %4, 0','%5 = extractvalue { i32, i32 } %4, 1',1)
        ir_contract(changed,mode,False)
        reject(label,lambda changed=changed:ir_contract(changed,mode,True),'full-IR-SSA-hash',True)
    need(len(result)==50,'Complete50 receiver negative controls')
    return result


def objdump(log,elf):
    actual={};current=None
    for line in log.read_text().splitlines():
        head=re.match(r'Disassembly of section (.+):',line)
        if head:current=head[1]
        row=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)',line)
        if row:
            need(row[3] not in ('<unknown>','.word','.2byte'),'All actual objdump instructions decoded')
            actual.setdefault(current,[]).append((int(row[1],16),bytes.fromhex(row[2])))
    expected={}
    for section in elf.sections:
        if section['flags']&4 and section['size']:
            code=elf.data(section);at=0;rows=[]
            while at<len(code):
                width=2 if code[at]&3!=3 else 4
                need(at+width<=len(code),'Bounded disassembly projection')
                rows.append((at,code[at:at+width]));at+=width
            expected[section['name']]=rows
    need(actual==expected,'Complete actual objdump bytes/addresses/widths match all code')
    return dict(instructions=sum(len(x) for x in actual.values()),bytes=sum(len(data) for rows in actual.values() for _,data in rows))


def inventory(folder):
    need(all(p.is_file() for p in folder.iterdir()),'No hidden artifact subdirectories')
    actual={p.name:sha(p) for p in sorted(folder.iterdir()) if p.name!='verification.json'}
    need(set(actual)==ARTIFACTS,'Exact18-artifact inventory including all raw logs')
    return actual


def record(root,folder,mode,tools,header,reader,prior):
    before=inputs(root,tools,header);original=originals(root,prior);deps=dependencies(root,folder,tools,header)
    commands=[dict(label=label,argv=[portable(x,root,tools,header) for x in argv],exit=0,log_sha256=sha(folder/(label+'.log')))
              for label,argv in recipes(root,folder,mode,tools)]
    need(all((folder/(name+'.log')).read_bytes()==b'' for name in ('receiver-compile','receiver-IR','consumer-compile',
                                                                'consumer-IR','receiver-combine','pipeline-combine')),
         'Warning-free actual compilation and partial-link logs')
    native=reader(folder/'receiver.o');consumer=reader(folder/'consumer.o')
    combined=reader(folder/'RECEIVER-OPEN-CALLS.o');pipeline=reader(folder/'PIPELINE-OPEN-CALLS.o')
    ir=(folder/'receiver.ll').read_text();cir=(folder/'consumer.ll').read_text()
    facts=[elf_contract(native,'native',prior),prior['elf_contract'](consumer,False),
           elf_contract(combined,'receiver',prior),elf_contract(pipeline,'pipeline',prior)]
    ir_facts=ir_contract(ir,mode);consumer_ir=prior['ir_contract'](cir,mode)
    negative=negatives(reader,native,combined,pipeline,ir,mode,prior)
    dumps=[objdump(folder/(label+'.log'),elf) for label,elf in [('receiver-object',native),('consumer-object',consumer),
                                                            ('receiver-combined',combined),('pipeline-combined',pipeline)]]
    after=inputs(root,tools,header);need(before==after,'Inputs unchanged through complete static verification')
    result=dict(passed=True,actual_ELFs=4,ELFs=facts,receiver_IR=ir_facts,consumer_IR=consumer_ir,objdump=dumps,
                pipeline_bytes=132,pipeline_instructions=47,pipeline_function_offsets=[0,8,62,76],
                receiver_noncall54_equal=True,receiver_full70_equal_to_resolved_original=False,
                internal_definition_linkage_evidence=True,machine_JALs_resolved=False,
                consumer_relocations_to_genuine_receiver_FUNC=2,receiver_relocations_to_three_UND=4,
                firmware_ready=False,whole_firmware_equivalence=False,
                limitations=['ET_REL linkage evidence only; six JAL relocation records and zero raw immediates remain.',
                             'Three downstream providers are genuine UND, including opaque transitive resident effects.',
                             'Physical placement, full ABI/IRQ/fault context and flashable whole firmware are unproved.'],
                target_execution=False,ISA_emulation=False,MMIO_execution=False,hardware=False,network=False,BIN_generated=False)
    value=dict(schema='TSL9-receive-wrapper-open-pipeline-v1',mode=mode,inputs_before=before,inputs_after=after,
               compiler_dependencies=deps,commands=commands,original_resolved_traces=original,
               negative_controls=negative,result=result,artifacts=inventory(folder))
    portable_record(value);return value


def replay(root,receipt,tools,header,reader,prior):
    need(receipt.name=='verification.json' and receipt.parent.is_relative_to(HERE/'build') and receipt.parent.name in ('c','cpp'),
         'Owned replay receipt')
    raw=receipt.read_bytes();need(b'\r' not in raw,'Canonical LF receipt')
    actual=record(root,receipt.parent,receipt.parent.name,tools,header,reader,prior)
    need(actual==json.loads(raw),'Complete read-only reconstructed record equality')
    return actual


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--tool-dir',type=Path,default=os.environ.get('TSL9_LLVM_BIN'))
    p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path)
    p.add_argument('--require-firmware-ready',action='store_true')
    args=p.parse_args();root=args.project_root.resolve()
    need(args.tool_dir is not None,'Set TSL9_LLVM_BIN or explicit existing --tool-dir')
    tools,header,reader,prior=load(root,Path(args.tool_dir).resolve())
    need((args.build_root is None)!=(args.replay is None),'Choose new build or read-only replay')
    if args.replay:
        value=replay(root,args.replay.resolve(),tools,header,reader,prior)
        need(not args.require_firmware_ready,'Three UND providers and six pending relocations; firmware remains unproved')
        print(json.dumps(dict(passed=True,read_only_replay=True,actual_ELFs=4,negative_controls=len(value['negative_controls']),
                              firmware_ready=False,receipt_sha256=sha(args.replay.resolve()))));return
    need(not args.require_firmware_ready,'Three UND providers and six pending relocations; firmware remains unproved')
    out=args.build_root.resolve();need(out.is_relative_to(HERE/'build') and not out.exists(),'New owned build directory required')
    frozen=inputs(root,tools,header);originals(root,prior);out.mkdir(parents=True);receipts=[]
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir()
        for label,argv in recipes(root,folder,mode,tools):
            actual=subprocess.run([str(x) for x in argv],capture_output=True,cwd=root,timeout=120)
            (folder/(label+'.log')).write_bytes(actual.stdout+actual.stderr)
            need(actual.returncode==0,'Actual offline build/static-read failed; inspect '+label+'.log')
            need(inputs(root,tools,header)==frozen,'All pre/post recipe inputs unchanged')
        value=record(root,folder,mode,tools,header,reader,prior)
        need(value['inputs_before']==value['inputs_after']==frozen,'All language build inputs unchanged')
        receipt=folder/'verification.json';receipt.write_bytes((json.dumps(value,indent=2)+'\n').encode('utf-8'))
        replay(root,receipt,tools,header,reader,prior)
        receipts.append(dict(mode=mode,path=portable(receipt,root,tools,header),sha256=sha(receipt)))
    need(inputs(root,tools,header)==frozen,'Inputs unchanged across both language builds')
    need(all((out/'c'/name).read_bytes()==(out/'cpp'/name).read_bytes() for name in
             ('receiver.o','consumer.o','RECEIVER-OPEN-CALLS.o','PIPELINE-OPEN-CALLS.o')),'All four C/C++ ELF files byte-equal')
    print(json.dumps(dict(passed=True,actual_ELFs=8,negative_controls_per_mode=50,receipts=receipts,
                          firmware_ready=False,machine_JALs_resolved=False,target_execution=False,BIN_generated=False)))


if __name__=='__main__':
    try:main()
    except ValueError as error:
        print(json.dumps(dict(passed=False,error=str(error))));sys.exit(1)
