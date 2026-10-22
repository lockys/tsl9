#!/usr/bin/env python3
"""Build/replay offline GPIO/register providers and a still-relocatable pipeline."""
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

HERE=Path(__file__).resolve().parent
MODEL='experiments/tsl9-register-providers'
RX='experiments/tsl9-receive-wrapper'
CO='experiments/tsl9-irq-flag-consumer'
PARSER='analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
FW='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FW_PIN='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SPI='tsl9_spi_transfer_entry_16896'
PACKET='tsl9_receive_buffer_entry_16a7c'
PINS={
 RX+'/verify.py':'29bec92a0f027df2be5120d00cb0bb7b4d7e43f410c7bd6fce0b2b25550dd0db',
 CO+'/verify.py':'5a7314d3f63e20babca57443ed55efcb00ff97487503e409b68ebe1d56871550',
 CO+'/src/flag_consumer.c':'9edf5f2571991062605863e88adf8028d4d54efc8d3e518c540026bd50b0ef12',
 RX+'/src/receive_wrapper.c':'df1e1f0633c50b8b2c9f7a58d2ac1e45664057de107dc04d28eca9e931538cdc',
 PARSER:'00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141',
 MODEL+'/pipeline.ld':'5099f57908aad1bb13df777b97ca85416c94c95a15037705c3171a13128d94a4',
 'experiments/tsl9-register-read/src/register_read.c':'5d0dfffde0adf21490e9108fbb95920595a851d67ac95b376549e20be3989846',
 'experiments/tsl9-register-read/component.ld':'feee5465a542451cc5b9a9f9e168ad2e346a240c2ac78cc2d1a9a00771ce4b98',
 'experiments/tsl9-register-write/src/register_write.c':'d4a0669559aeb497f787c98066db28da8fa9f285bf3b9be2bce574c0ed016f85',
 'experiments/tsl9-register-write/component.ld':'0bf2e920f51b03dc2440f91a3317515578987e9a13d5529e4b061e4029a1745c'}
UNITS={'consumer':CO+'/src/flag_consumer.c','receiver':RX+'/src/receive_wrapper.c',
       'read':'experiments/tsl9-register-read/src/register_read.c','write':'experiments/tsl9-register-write/src/register_write.c'}
ENTRY={'read':'tsl9_register_read_entry_16994','write':'tsl9_register_write_entry_16a30'}
BODY={'read':'tsl9_register_read_body','write':'tsl9_register_write_body'}
BASE={'read':0x16994,'write':0x16a30}
SIZE={'read':72,'write':76}
CALLS={'read':[38,46,52],'write':[40,48,56]}
ORIGINAL_PIN={'read':'0949ef0357f5c7543bc480b214103d78880ccba36a0551e0cb8cfb1edab2d538',
              'write':'cb0b2b3f0b4c676385ca97543b29c32bf0eaaa99317959e6ad2a54438f71cf6e'}
NONCALL_PIN={'read':'25e909875b6aac1598907cce188ea1334911e0077704c1dd21858bef6072cd7c',
             'write':'7ede0a9407f68aaa4e140e52adf67059f54a4c379748e59a89dcf46e9e6c1ef7'}
PREFIX_IR_PIN='41656544277cf591ff5dd1978b02231b1bdc3f0c8663a065035c23820570f105'
IR_PIN={'read':{'c':'62b943c8e56b0e0e9e81b25dadb09a30343a70ffccd85c2c84feb4d4840bca55',
                'cpp':'62b943c8e56b0e0e9e81b25dadb09a30343a70ffccd85c2c84feb4d4840bca55'},
        'write':{'c':'e191bb490bb6ece85ef208c5aafdfdfdfa150d4d4534f921d7c9040827222905',
                 'cpp':'07a75c2cf84a329c43896b247a3f7e87a229ff11693c09c4f2ac1d4cafb53373'}}
COMMON_SITES=[(0,2),(2,2),(4,4),(8,2),(10,4),(14,2),(16,4),(20,2),(22,2),(24,4),(28,2),(30,4)]
SITES={'read':COMMON_SITES+[(34,2),(36,2),(38,4),(42,2),(44,2),(46,4),(50,2),(52,4),(56,2),(58,4),(62,2),(64,4),(68,2),(70,2)],
       'write':COMMON_SITES+[(34,2),(36,2),(38,2),(40,4),(44,2),(46,2),(48,4),(52,2),(54,2),(56,4),(60,2),(62,4),(66,2),(68,4),(72,2),(74,2)]}


def need(ok,message):
    if not ok:raise ValueError(message)


def digest(data):return hashlib.sha256(data).hexdigest()
def sha(path):return digest(path.read_bytes())
def sx(n,b):return n-(1<<b) if n&(1<<(b-1)) else n
def noncall(code,kind):return b''.join(code[a:a+n] for a,n in SITES[kind] if a not in CALLS[kind])


def trace(code,kind,resolved=False):
    need(len(code)==SIZE[kind],'Exact provider extent')
    h=lambda at:struct.unpack_from('<H',code,at)[0]
    w=lambda at:struct.unpack_from('<I',code,at)[0]
    def imm(at,rd,rs1,value,funct=0):
        x=w(at);need((x&127,x>>12&7,x>>7&31,x>>15&31,sx(x>>20,12))==(0x13,funct,rd,rs1,value),
                     'Typed immediate at+'+str(at))
    def ci(at,rd,value):
        x=h(at);need((x&3,x>>13,x>>7&31,sx(((x>>12&1)<<5)|(x>>2&31),6))==(1,2,rd,value),
                     'Typed compressed LI at+'+str(at))
    def branch(at,rs1,target):
        x=h(at);d=sx(((x>>12&1)<<8)|((x>>10&3)<<3)|((x>>5&3)<<6)|((x>>3&3)<<1)|((x>>2&1)<<5),9)
        need((x&3,x>>13,8+(x>>7&7),at+d)==(1,6,rs1,target),'Independent GPIO BEQZ at+'+str(at))
    def lui(at):need(w(at)==0x400117b7,'GPIO base LUI A5 at+'+str(at))
    def sw(at,offset):
        x=w(at);need((x&127,x>>12&7,x>>15&31,x>>20&31,sx((x>>25<<5)|(x>>7&31),12))==(0x23,2,15,14,offset),
                     'GPIO SW32 offset at+'+str(at))
    def stack(at,reg,offset,load=False):
        x=h(at)
        if load:got=(x&3,x>>13,x>>7&31,((x>>12&1)<<5)|((x>>4&7)<<2)|((x>>2&3)<<6));expected=(2,2,reg,offset)
        else:got=(x&3,x>>13,x>>2&31,((x>>9&15)<<2)|((x>>7&3)<<6));expected=(2,6,reg,offset)
        need(got==expected,('Fresh frame LW' if load else 'Original frame SW')+' at+'+str(at))
    def mv(at,rs2):
        x=h(at);need((x&3,x>>12,x>>7&31,x>>2&31)==(2,8,10,rs2),'Then-live A0 MV at+'+str(at))
    need(h(0)==0x1101,'SP-32 before frame write');stack(2,1,28)
    imm(4,15,10,1,7);branch(8,15,20);lui(10);ci(14,14,16);sw(16,-2028)
    x=h(20);need((x&3,x>>13,x>>10&3,8+(x>>7&7),sx(((x>>12&1)<<5)|(x>>2&31),6))==(1,4,2,10,2),
                'Destructive A0 ANDI2 after first GPIO branch')
    branch(22,10,34);lui(24);ci(28,14,1);sw(30,-2028)
    ci(34,10,3 if kind=='read' else 2)
    if kind=='read':
        stack(36,11,12);stack(42,11,12,True);mv(44,11);ci(50,10,0);cleanup=56
    else:
        stack(36,12,12);stack(38,11,8);stack(44,11,8,True);mv(46,11);stack(52,12,12,True);mv(54,12);cleanup=60
    stack(cleanup,1,28,True);lui(cleanup+2);ci(cleanup+6,14,17);sw(cleanup+8,-2032)
    need(h(cleanup+12)==0x6105,'SP+32 after cleanup');need(h(cleanup+14)==0x8082,'RET via fresh RA')
    calls=[]
    for at in CALLS[kind]:
        x=w(at);delta=sx(((x>>31)<<20)|((x>>21&1023)<<1)|((x>>20&1)<<11)|((x>>12&255)<<12),21)
        need((x&127,x>>7&31)==(0x6f,1),'SPI four-byte JAL RA')
        need(BASE[kind]+at+delta==0x16896 if resolved else x==0xef,'Resolved original SPI target or open zero immediate')
        calls.append(dict(offset=at,original_target='0x16896',original_continuation=hex(BASE[kind]+at+4),pending_relocation=not resolved))
    return dict(bytes=len(code),instructions=len(SITES[kind]),rows=[dict(offset=a,bytes=n,hex=code[a:a+n].hex()) for a,n in SITES[kind]],
                calls=calls,frame_bytes=32,GPIO_selection_address='0x40010814',GPIO_cleanup_address='0x40010810',
                GPIO_width_bits=32,independent_channel_bits=True,RA_reload_before_cleanup=True,
                A0_exit='third opaque SPI returned residue; no forced zero',GP_S0_S1_own_writes=False)


def load(root,tool_dir):
    need(HERE==root/MODEL,'Canonical provider checker root')
    for name,pin in PINS.items():need(sha(root/name)==pin,'Frozen input: '+name)
    rx=runpy.run_path(str(root/RX/'verify.py'));co=runpy.run_path(str(root/CO/'verify.py'))
    tools={n:(tool_dir/(n+('.exe' if os.name=='nt' else ''))).resolve() for n in rx['TOOLS']}
    need(all(sha(tools[n])==v for n,v in rx['TOOLS'].items()),'Pinned existing LLVM tools')
    header=tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
    need(sha(header)==rx['STDINT_PIN'],'Pinned stdint resource')
    return tools,header,runpy.run_path(str(root/PARSER))['ELF'],rx,co


def inputs(root,tools,header,rx):
    files={Path(__file__).resolve(),*[root/n for n in PINS],root/FW,header,*tools.values()}
    return {rx['portable'](p,root,tools,header):sha(p) for p in sorted(files)}


def originals(root,rx,co):
    image=(root/FW).read_bytes();need(len(image)==76800 and digest(image)==FW_PIN,'Exact complete Runtime')
    result={}
    for kind in ('read','write'):
        code=image[BASE[kind]-0x8000:BASE[kind]-0x8000+SIZE[kind]]
        need(digest(code)==ORIGINAL_PIN[kind] and digest(noncall(code,kind))==NONCALL_PIN[kind],'Pinned original provider slices')
        result[kind]=trace(code,kind,True)
    need(image[0xeb0a:0xeb50]==rx['ORIGINAL'] and image[0xf002:0xf040]==co['ORIGINAL'],'Frozen upstream original slices')
    return result


def recipes(root,folder,mode,tools,rx):
    jobs=[]
    for name,source in UNITS.items():
        common=[tools['clang'],*rx['flags'](mode,name!='consumer')]
        jobs += [(name+'-compile',[*common,'-c','-MD','-MF',folder/(name+'.d'),'-MT',name+'.o',root/source,'-o',folder/(name+'.o')]),
                 (name+'-IR',[*common,'-S','-emit-llvm',root/source,'-o',folder/(name+'.ll')])]
    for kind in ('read','write'):
        jobs.append((kind+'-combine',[tools['ld.lld'],'-r','--no-relax','-T',root/('experiments/tsl9-register-'+kind+'/component.ld'),
                                    folder/(kind+'.o'),'-o',folder/(kind+'-OPEN.o')]))
    jobs.append(('pipeline-combine',[tools['ld.lld'],'-r','--no-relax','-T',HERE/'pipeline.ld',
                                    *[folder/(name+'.o') for name in UNITS],'-o',folder/'PIPELINE-OPEN.o']))
    for name in (*UNITS,'read-OPEN','write-OPEN','PIPELINE-OPEN'):
        jobs.append((name+'-dump',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/(name+'.o')]))
    return jobs


def dependencies(root,folder,tools,header,rx):
    result={}
    for name,source in UNITS.items():
        target,sep,tail=(folder/(name+'.d')).read_text().replace('\\\n',' ').partition(':')
        paths={Path(re.sub(r'\\(.)',r'\1',x)).resolve() for x in re.findall(r'(?:\\.|[^\s])+',tail)}
        need(sep and target==name+'.o' and paths=={root/source,header},'Exact '+name+' MD closure')
        result[name]={rx['portable'](p,root,tools,header):sha(p) for p in sorted(paths)}
    return result


def normalized(text,kind):
    found=re.findall(r'define[^\n]*@([^ (]+)\([^\n]*\{\n(.*?)\n}',text,re.S)
    need(len(found)==2 and {n for n,_ in found}=={ENTRY[kind],BODY[kind]},'Exactly two provider IR functions')
    result={}
    for name,body in found:
        lines=[]
        for line in body.splitlines():
            line=line.split(';',1)[0].strip()
            if line:lines.append(re.sub(r' #\d+\b','',re.sub(r', ![A-Za-z.]+ !\d+','',line)))
        result[name]='\n'.join(lines)+'\n'
    return result


def ir_contract(text,kind,mode,full=True):
    bodies=normalized(text,kind);entry=bodies[ENTRY[kind]];body=bodies[BODY[kind]]
    need(entry==r'tail call void asm sideeffect "addi sp, sp, -32\0Asw ra, 28(sp)\0A", ""()'+'\nunreachable\n',
         'Exact frame entry SP-32 then SW RA28')
    need(body.count('store volatile i32 ')==3 and not re.search(r'(?:store|load) volatile i(?:8|16)\b',body),
         'Exactly three volatile GPIO word stores')
    need(body.count(', -2028')==2 and body.count(', -2032')==1,'Exact GPIO selector and cleanup offsets')
    calltype='noundef i32' if kind=='write' and mode=='cpp' else 'i32'
    call='tail call '+calltype+r' asm sideeffect "jal ra, tsl9_spi_transfer_entry_16896\0A", "={x10},{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"'
    need(body.count(call)==3,'Three exact opaque SPI A0/result/clobber ports')
    need('alloca ' not in body and not re.search(r'\bcall\b[^\n]*@[A-Za-z_]',body),'No extra frame or helper')
    if kind=='read':
        anchors=['%2 = and i32 %1, 1','%15 = and i32 %4, 2','br i1 %6, label %14, label %7',
                 'br i1 %17, label %25, label %18','(i32 %8, i32 16)','(i32 %19, i32 1)','(i32 %31, i32 17)',
                 '%26 = tail call i32 asm sideeffect "", "={x10},{x10},~{memory}"(i32 3)',
                 r'asm sideeffect "sw a1, 12(sp)\0A", "~{memory}"()',
                 r'asm sideeffect "lw a1, 12(sp)\0A", "={x11},~{memory}"()',call+'(i32 %26)',call+'(i32 %28)',call+'(i32 0)']
        order=['(i32 3)',r'sw a1, 12(sp)\0A',call+'(i32 %26)',r'lw a1, 12(sp)\0A',
               call+'(i32 %28)',call+'(i32 0)',r'lw ra, 28(sp)\0A','%31 =','store volatile i32 %34',r'addi sp, sp, 32\0Aret\0A']
    else:
        anchors=['%3 = and i32 %2, 1','%16 = and i32 %6, 2','br i1 %7, label %15, label %8',
                 'br i1 %18, label %26, label %19','(i32 %9, i32 16)','(i32 %20, i32 1)','(i32 %37, i32 17)',
                 '%29 = tail call i32 asm sideeffect "", "={x10},{x10},~{memory}"(i32 2)',
                 r'asm sideeffect "sw a2, 12(sp)\0Asw a1, 8(sp)\0A", "{x10},{x11},{x12},~{memory}"(i32 %29, i32 %28, i32 %27)',
                 r'asm sideeffect "lw a1, 8(sp)\0A", "={x11},~{memory}"()',
                 r'asm sideeffect "lw a2, 12(sp)\0A", "={x12},~{memory}"()',call+'(i32 %29)',call+'(i32 %32)',call+'(i32 %35)',
                 r'asm sideeffect "addi sp, sp, 32\0Aret\0A", "{x10},~{memory}"(i32 %36)']
        order=['(i32 2)',r'sw a2, 12(sp)\0Asw a1, 8(sp)\0A',call+'(i32 %29)',r'lw a1, 8(sp)\0A',
               call+'(i32 %32)',r'lw a2, 12(sp)\0A',call+'(i32 %35)',r'lw ra, 28(sp)\0A','%37 =',
               'store volatile i32 %40',r'addi sp, sp, 32\0Aret\0A']
    need(all(x in body for x in anchors),'Independent bit branches, live bank and slot dataflow')
    need(all(body.index(a)<body.index(b) for a,b in zip(order,order[1:])),
         'Source alias order: command/save/reload/SPI/RA-before-cleanup/RET')
    need(body.splitlines()[-1]=='unreachable' and body.count(r'lw ra, 28(sp)\0A')==1,'Sole architectural return and fresh RA')
    if full:need(digest(entry.encode())==PREFIX_IR_PIN and digest(body.encode())==IR_PIN[kind][mode],'Complete provider SSA/CFG/port hash')
    return dict(entry_sha256=digest(entry.encode()),body_sha256=digest(body.encode()),body_lines=len(body.splitlines()),
                GPIO_word_stores=3,SPI_ports=3,RA_before_cleanup=True,frame_bytes=32,
                inherited_A0_result_not_normalized=True,complete_downstream_ABI_proved=False)


def locals_expected(kind,partial=False,pipeline=False,rx=None):
    rows=[('',0,0,0,0,0)]
    if pipeline:
        for index,(file,entry,body) in enumerate([('flag_consumer.c',0,8),('receive_wrapper.c',62,76),('register_read.c',132,136),('register_write.c',204,208)]):
            rows += [(file,0,0,4,0,65521),('$x.0',entry,0,0,0,1),('$x.1',body,0,0,0,1),('$d.3',0,0,0,0,65521)]
            if index==0:rows += [('',0,0,3,0,2),('',0,0,3,0,4)]
        rows += [('',0,0,3,0,1)]
    else:
        rows += [('register_'+kind+'.c',0,0,4,0,65521),('$x.0',0,0,0,0,1 if partial else 3),
                 ('$x.1',4 if partial else 0,0,0,0,1 if partial else 4)]
        rows += ([('$d.3',0,0,0,0,65521),('',0,0,3,0,1),('',0,0,3,0,2),('',0,0,3,0,4)] if partial else
                 [('$d.2',0,0,0,0,6),('$d.3',0,0,0,0,8)])
    return [dict(zip(('name','value','size','info','other','index'),row)) for row in rows]


def sections(elf,kind,partial,pipeline):
    name='.pipeline' if pipeline else '.register_read' if kind=='read' else '.writer'
    if pipeline or partial:
        size=280 if pipeline else SIZE[kind];rcount=12 if pipeline else 3
        expected=[('',0,0,0,0,0,0,0,0),(name,1,6,0,size,0,0,2,0),('.text',1,6,0,0,0,0,2,0),
                  ('.rela'+name,4,64,0,rcount*12,5,1,4,12),('.llvm_addrsig',0x6fff4c03,0x80000000,0,8 if pipeline else 2,0,0,1,0),
                  ('.symtab',2,0,0,480 if pipeline else 176,7,20 if pipeline else 8,4,16),
                  ('.shstrtab',3,0,0,72 if pipeline else 82 if kind=='read' else 68,0,0,1,0),
                  ('.strtab',3,0,0,400 if pipeline else 117 if kind=='read' else 120,0,0,1,0)]
    else:
        expected=[('',0,0,0,0,0,0,0,0),('.strtab',3,0,0,218 if kind=='read' else 221,0,0,1,0),('.text',1,6,0,0,0,0,2,0),
                  ('.text.'+ENTRY[kind],1,6,0,4,0,0,2,0),('.text.'+BODY[kind],1,6,0,SIZE[kind]-4,0,0,2,0),
                  ('.rela.text.'+BODY[kind],4,64,0,36,10,4,4,12),('.comment',1,48,0,159,0,0,1,1),
                  ('.note.GNU-stack',1,0,0,0,0,0,1,0),('.riscv.attributes',0x70000003,0,0,64,0,0,1,0),
                  ('.llvm_addrsig',0x6fff4c03,0x80000000,0,2,10,0,1,0),('.symtab',2,0,0,144,1,6,4,16)]
    fields=('name','type','flags','address','size','link','info','alignment','entry_size')
    need([tuple(s[k] for k in fields) for s in elf.sections]==expected,'Exact complete provider/pipeline section metadata')
    return [dict(zip(fields,row)) for row in expected]


def elf_contract(elf,kind,partial,rx,co,pipeline=False):
    rx['elf_header'](elf);section_facts=sections(elf,kind,partial,pipeline)
    need([s for s in elf.symbols if not s['info']>>4]==locals_expected(kind,partial,pipeline),'Exact locals; no hidden FUNC/ABS alias')
    if pipeline:
        expected={rx['CE']:(0,8),rx['CB']:(8,54),rx['ENTRY']:(62,14),rx['BODY']:(76,56),
                  ENTRY['read']:(132,4),BODY['read']:(136,68),ENTRY['write']:(204,4),BODY['write']:(208,72)}
        providers={PACKET,SPI};owner='.pipeline'
    else:
        expected={ENTRY[kind]:(0,4),BODY[kind]:(4 if partial else 0,SIZE[kind]-4)};providers={SPI}
        owner=('.register_read' if kind=='read' else '.writer') if partial else '.text.'+BODY[kind]
    global_=[s for s in elf.symbols if s['info']>>4 in (1,2)];defs={s['name']:s for s in global_ if s['index']!=0};und={s['name']:s for s in global_ if s['index']==0}
    need(set(defs)==set(expected) and set(und)==providers and len(global_)==len(expected)+len(providers),'Exact genuine FUNC/UND set')
    for n,(value,size) in expected.items():
        s=defs[n];need(s['info']==18 and s['other']==0 and (s['value'],s['size'])==(value,size),'Exact real FUNC sizes/adjacency')
        need(elf.sections[s['index']]['name']==(owner if pipeline or partial else '.text.'+n),'Exact FUNC ownership')
    need(all(s['info']==16 and s['value']==s['size']==s['other']==0 for s in und.values()),'Genuine strong UND; no fake ABS providers')
    def rel(at,n):return dict(owner=owner,offset=at,type=17,addend=0,symbol=(defs|und)[n])
    if pipeline:
        expected_reloc=[rel(22,rx['ENTRY']),rel(48,rx['ENTRY']),rel(76,ENTRY['read']),rel(94,PACKET),rel(108,PACKET),rel(128,ENTRY['write'])]
        expected_reloc += [rel(a,SPI) for a in [170,178,184,244,252,260]]
    else:expected_reloc=[rel(a if partial else a-4,SPI) for a in CALLS[kind]]
    need(elf.relocations==expected_reloc,'Exact pending JAL17 graph: internal genuine FUNC versus UND')
    traces={}
    for k in (('read','write') if pipeline else (kind,)):
        code=elf.function_bytes(defs[ENTRY[k]])+elf.function_bytes(defs[BODY[k]])
        traces[k]=trace(code,k)
        need(digest(noncall(code,k))==NONCALL_PIN[k],'Whole provider noncall bytes')
    if pipeline:
        consumer=elf.function_bytes(defs[rx['CE']])+elf.function_bytes(defs[rx['CB']]);co['trace'](consumer)
        receiver=elf.function_bytes(defs[rx['ENTRY']])+elf.function_bytes(defs[rx['BODY']]);rx['trace'](receiver)
        need(co['noncall'](consumer)==co['noncall'](co['ORIGINAL']) and rx['noncall'](receiver)==rx['noncall'](rx['ORIGINAL']),'Upstream noncall code unchanged')
        combined=consumer+receiver+b''.join(elf.function_bytes(defs[n]) for n in [ENTRY['read'],BODY['read'],ENTRY['write'],BODY['write']])
        need(elf.data(elf.byname[owner])==combined,'Actual280B contiguous code; no padding or carrier')
    elif partial:
        need(elf.data(elf.byname[owner])==elf.function_bytes(defs[ENTRY[kind]])+elf.function_bytes(defs[BODY[kind]]),'Real4B entry/body fall-through')
    return dict(sections=section_facts,functions=list(defs.values()),UND=list(und.values()),relocations=expected_reloc,
                local_ABS_metadata=[s for s in elf.symbols if s['index']==65521],traces=traces,
                ET_REL=True,internal_definition_linkage_only=pipeline,machine_JALs_resolved=False)


class MemoryFile:
    def __init__(self,data):self.data=data
    def read_bytes(self):return self.data


def negatives(reader,objects,irs,mode,rx,co):
    result=[]
    def reject(label,fn,category,full=False):
        try:fn()
        except ValueError as error:result.append(dict(label=label,category=category,rejected_by=str(error),full_hash_used=full))
        else:raise ValueError('Negative escaped: '+label)
    for kind in ('read','write'):
        e=objects[kind+'-OPEN'];defs={s['name']:s for s in e.symbols if s['info']==18};code=e.function_bytes(defs[ENTRY[kind]])+e.function_bytes(defs[BODY[kind]])
        cleanup=56 if kind=='read' else 60
        cases=[('SP32',0,32),('RA-save28',3,2),('first-mask',6,16),('first-branch-polarity',9,32),('GPIO-width32',17,16),
               ('destructive-A0-mask',20,4),('second-pin1',28,4),('command3-or2',34,4),('first-arg-save',36,4),
               ('fresh-A1-slot',42 if kind=='read' else 44,16),('third-input',50 if kind=='read' else 54,4),
               ('RA-reload28',cleanup,16),('cleanup-width32',cleanup+9,16),('SP-restore32',cleanup+12,4),
               ('RET-RA',cleanup+14,128),('JAL-RA',CALLS[kind][0],128),('JAL-open-immediate',CALLS[kind][-1]+3,1)]
        for label,at,mask in cases:
            changed=bytearray(code);changed[at]^=mask
            reject(kind+'-'+label,lambda changed=changed,kind=kind:trace(bytes(changed),kind),'typed-raw')
        changed=code[:cleanup]+code[cleanup+2:cleanup+12]+code[cleanup:cleanup+2]+code[cleanup+12:]
        reject(kind+'-RA-moved-after-cleanup-alias',lambda changed=changed,kind=kind:trace(changed,kind),'typed-alias-order')
        if kind=='write':
            changed=code[:36]+code[38:40]+code[36:38]+code[40:]
            reject('write-A2-before-A1-save',lambda:trace(changed,'write'),'typed-alias-order')
        else:
            changed=code[:34]+code[36:38]+code[34:36]+code[38:]
            reject('read-command-before-A1-save',lambda:trace(changed,'read'),'typed-alias-order')
        ir=irs[kind]
        cases=[('GPIO-volatile-word','store volatile i32','store volatile i16'),('GPIO-select-offset',', -2028',', -2024'),
               ('GPIO-cleanup-offset',', -2032',', -2028'),('freshRA-slot',r'lw ra, 28(sp)\0A',r'lw ra, 24(sp)\0A'),
               ('SPI-callee',SPI,'invented_provider'),('SPI-clobber', '~{x11},~{x12}', '~{x11},~{x13}'),
               ('first-branch', 'label %14, label %7' if kind=='read' else 'label %15, label %8',
                'label %7, label %14' if kind=='read' else 'label %8, label %15'),
               ('fresh-A1',r'lw a1, 12(sp)\0A' if kind=='read' else r'lw a1, 8(sp)\0A',r'lw a1, 4(sp)\0A')]
        if kind=='write':cases += [('A2-A1-save-order',r'sw a2, 12(sp)\0Asw a1, 8(sp)',r'sw a1, 8(sp)\0Asw a2, 12(sp)')]
        for label,old,new in cases:
            need(old in ir,'Actual IR negative anchor')
            reject(kind+'-'+label,lambda old=old,new=new,ir=ir,kind=kind:ir_contract(ir.replace(old,new,1),kind,mode,False),'IR-finite')
        # Move a real void architectural port without changing any SSA value.
        # Only the finite order gate, not the full body digest, rejects it.
        ra=re.search(r'^  tail call void asm sideeffect "lw ra, 28\(sp\)\\0A"[^\n]*\n',ir,re.M)
        need(ra is not None,'Actual raw IR RA-port line')
        shifted=ir[:ra.start()]+ir[ra.end():]
        finish=re.search(r'^  tail call void asm sideeffect "addi sp, sp, 32\\0Aret\\0A"',shifted,re.M)
        need(finish is not None,'Actual raw IR final SP/RET port')
        shifted=shifted[:finish.start()]+ra[0]+shifted[finish.start():]
        reject(kind+'-IR-RA-after-cleanup-alias',lambda shifted=shifted,kind=kind:ir_contract(shifted,kind,mode,False),'IR-alias-order')
        if kind=='read':
            save=re.search(r'^  tail call void asm sideeffect "sw a1, 12\(sp\)\\0A"[^\n]*\n',ir,re.M)
            need(save is not None,'Actual raw IR saved-A1 port')
            shifted=ir[:save.start()]+ir[save.end():]
            command=re.search(r'^  %26 = tail call',shifted,re.M)
            need(command is not None,'Actual raw IR command port')
            shifted=shifted[:command.start()]+save[0]+shifted[command.start():]
            reject('read-IR-save-before-command',lambda shifted=shifted:ir_contract(shifted,'read',mode,False),'IR-alias-order')
        old='%11 = extractvalue { i32, i32 } %9, 1' if kind=='read' else '%12 = extractvalue { i32, i32 } %10, 1'
        new=old[:-1]+'0';changed=ir.replace(old,new,1);ir_contract(changed,kind,mode,False)
        reject(kind+'-full-SSA-store-source',lambda changed=changed,kind=kind:ir_contract(changed,kind,mode,True),'full-SSA',True)
    pipe=objects['PIPELINE-OPEN'];relbase=pipe.byname['.rela.pipeline']['offset'];symbase=pipe.byname['.symtab']['offset']
    def mutate(offset,fmt,value):
        raw=bytearray(pipe.raw);struct.pack_into(fmt,raw,offset,value);return reader(MemoryFile(bytes(raw)))
    for i in range(12):
        at=pipe.relocations[i]['offset']
        reject('pipeline-reloc-site-'+str(at),lambda i=i,at=at:elf_contract(mutate(relbase+12*i,'<I',at+2),'read',True,rx,co,True),'ELF-relocation')
    for name in [ENTRY['read'],ENTRY['write']]:
        i=next(i for i,s in enumerate(pipe.symbols) if s['name']==name)
        reject('pipeline-adjacency-'+name,lambda i=i:elf_contract(mutate(symbase+16*i+4,'<I',134),'read',True,rx,co,True),'ELF-adjacency')
    i=next(i for i,s in enumerate(pipe.symbols) if s['name']==SPI)
    reject('pipeline-SPI-fakeABS',lambda:elf_contract(mutate(symbase+16*i+14,'<H',65521),'read',True,rx,co,True),'ELF-provider')
    reject('pipeline-local-FUNC',lambda:elf_contract(mutate(symbase+2*16+12,'<B',2),'read',True,rx,co,True),'ELF-local-metadata')
    return result


def inventory(folder,labels):
    need(all(p.is_file() for p in folder.iterdir()),'No unrecorded build subdirectories')
    expected={name+suffix for name in UNITS for suffix in ('.o','.ll','.d')}|{'read-OPEN.o','write-OPEN.o','PIPELINE-OPEN.o'}|{x+'.log' for x in labels}
    actual={p.name:sha(p) for p in sorted(folder.iterdir()) if p.name!='verification.json'}
    need(set(actual)==expected,'Complete exact artifacts and raw-log inventory')
    return actual


def record(root,folder,mode,tools,header,reader,rx,co):
    before=inputs(root,tools,header,rx);original=originals(root,rx,co);deps=dependencies(root,folder,tools,header,rx)
    jobs=recipes(root,folder,mode,tools,rx)
    commands=[dict(label=n,argv=[rx['portable'](x,root,tools,header) for x in a],exit=0,log_sha256=sha(folder/(n+'.log'))) for n,a in jobs]
    need(all((folder/(n+'.log')).read_bytes()==b'' for n,_ in jobs if not n.endswith('-dump')),'Warning-free compile/IR/partial-link logs')
    names=[*UNITS,'read-OPEN','write-OPEN','PIPELINE-OPEN'];objects={n:reader(folder/(n+'.o')) for n in names}
    facts={'consumer':co['elf_contract'](objects['consumer'],False),'receiver':rx['elf_contract'](objects['receiver'],'native',co)}
    for kind in ('read','write'):
        facts[kind]=elf_contract(objects[kind],kind,False,rx,co)
        facts[kind+'-OPEN']=elf_contract(objects[kind+'-OPEN'],kind,True,rx,co)
    facts['PIPELINE-OPEN']=elf_contract(objects['PIPELINE-OPEN'],'read',True,rx,co,True)
    irs={n:(folder/(n+'.ll')).read_text() for n in UNITS}
    ir_facts={'consumer':co['ir_contract'](irs['consumer'],mode),'receiver':rx['ir_contract'](irs['receiver'],mode)}
    for kind in ('read','write'):ir_facts[kind]=ir_contract(irs[kind],kind,mode)
    negative=negatives(reader,objects,irs,mode,rx,co)
    dumps={n:rx['objdump'](folder/(n+'-dump.log'),objects[n]) for n in names}
    after=inputs(root,tools,header,rx);need(before==after,'All inputs unchanged through complete check')
    result=dict(passed=True,actual_ELFs=7,ELFs=facts,IR=ir_facts,objdump=dumps,pipeline_bytes=280,pipeline_instructions=101,
                internal_definition_calls=4,remaining_UND_calls=8,genuine_UND_providers=[PACKET,SPI],
                machine_JALs_resolved=False,firmware_ready=False,whole_firmware_equivalence=False,
                limitations=['All12 JAL17 records and zero raw immediates remain in ET_REL output.',
                             'SPI and packet providers, transitive resident effects, physical MMIO and full IRQ/fault/alias context are unproved.'],
                target_execution=False,ISA_emulation=False,MMIO_execution=False,hardware=False,network=False,BIN_generated=False)
    value=dict(schema='TSL9-register-providers-open-pipeline-v1',mode=mode,inputs_before=before,inputs_after=after,
               compiler_dependencies=deps,commands=commands,original_resolved_traces=original,negative_controls=negative,
               result=result,artifacts=inventory(folder,[n for n,_ in jobs]))
    rx['portable_record'](value);return value


def replay(root,receipt,tools,header,reader,rx,co):
    need(receipt.name=='verification.json' and receipt.parent.is_relative_to(HERE/'build') and receipt.parent.name in ('c','cpp'),'Owned receipt')
    raw=receipt.read_bytes();need(b'\r' not in raw,'Portable canonical LF receipt')
    actual=record(root,receipt.parent,receipt.parent.name,tools,header,reader,rx,co)
    need(actual==json.loads(raw),'Complete read-only reconstructed record equality');return actual


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--tool-dir',type=Path,default=os.environ.get('TSL9_LLVM_BIN'));p.add_argument('--build-root',type=Path)
    p.add_argument('--replay',type=Path);p.add_argument('--require-firmware-ready',action='store_true');a=p.parse_args();root=a.project_root.resolve()
    need(a.tool_dir is not None,'Set TSL9_LLVM_BIN or explicit existing --tool-dir')
    tools,header,reader,rx,co=load(root,Path(a.tool_dir).resolve());need((a.build_root is None)!=(a.replay is None),'Choose build or read-only replay')
    if a.replay:
        value=replay(root,a.replay.resolve(),tools,header,reader,rx,co)
        need(not a.require_firmware_ready,'Two UND providers and12 pending relocations; firmware remains unproved')
        print(json.dumps(dict(passed=True,read_only_replay=True,actual_ELFs=7,negative_controls=len(value['negative_controls']),
                              firmware_ready=False,receipt_sha256=sha(a.replay.resolve()))));return
    need(not a.require_firmware_ready,'Two UND providers and12 pending relocations; firmware remains unproved')
    out=a.build_root.resolve();need(out.is_relative_to(HERE/'build') and not out.exists(),'New owned build directory only')
    frozen=inputs(root,tools,header,rx);originals(root,rx,co);out.mkdir(parents=True);receipts=[]
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir()
        for label,argv in recipes(root,folder,mode,tools,rx):
            s=subprocess.run([str(x) for x in argv],capture_output=True,cwd=root,timeout=120);(folder/(label+'.log')).write_bytes(s.stdout+s.stderr)
            need(s.returncode==0,'Actual offline recipe failed; inspect '+label+'.log')
            need(inputs(root,tools,header,rx)==frozen,'Input pins unchanged before/after every recipe')
        value=record(root,folder,mode,tools,header,reader,rx,co);need(value['inputs_before']==value['inputs_after']==frozen,'Whole build input equality')
        receipt=folder/'verification.json';receipt.write_bytes((json.dumps(value,indent=2)+'\n').encode('utf-8'));replay(root,receipt,tools,header,reader,rx,co)
        receipts.append(dict(mode=mode,path=rx['portable'](receipt,root,tools,header),sha256=sha(receipt),negative_controls=len(value['negative_controls'])))
    need(inputs(root,tools,header,rx)==frozen,'Inputs unchanged across language builds')
    need(all((out/'c'/(n+'.o')).read_bytes()==(out/'cpp'/(n+'.o')).read_bytes() for n in (*UNITS,'read-OPEN','write-OPEN','PIPELINE-OPEN')),'All7 C/C++ ELF pairs byte-equal')
    print(json.dumps(dict(passed=True,actual_ELFs=14,receipts=receipts,firmware_ready=False,machine_JALs_resolved=False,target_execution=False,BIN_generated=False)))


if __name__=='__main__':
    try:main()
    except ValueError as error:print(json.dumps(dict(passed=False,error=str(error))));sys.exit(1)
