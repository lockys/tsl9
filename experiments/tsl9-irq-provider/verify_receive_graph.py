#!/usr/bin/env python3
"""Link/replay nine original-address receive/IRQ spans; never execute this ELF."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
OBJECT='NOT-A-FIRMWARE-IRQ-RECEIVE-GRAPH.elf'
ELF_PIN='2a2f02d0581d387d7170a1828b1e3bcc5b383975ba1f62e6e09e9f1b3db5f546'
AGGREGATE_PIN='1946d38e90500f279c650b7f80df32004f05507a2bafeaeceb372ab4b53ee169'
LINKER_PIN='4e642d9e4f2a6d3cbc315790ff6d68140d9ee60e042ab756a978f1a786fb6c00'
OLD_CHECKER='experiments/tsl9-ring-insert/verify_receive_graph.py'
OLD_PIN='e14b2ad2f4474887be3a63e3b1d415fa1aece600315a18ed56c6741e0924e031'
OLD_RECEIPTS={'c':'01be2d069bdd98fea035ef29e3cfac85cf22badef2422b50e9f11424808ba37b',
              'cpp':'b8db0029ebf52da9f5b1afaacb28d7bc4f1c0eebc0dc659b6cfcb80fe9426db7'}
IRQ_CHECKER='experiments/tsl9-ring-irq-adapter/verify.py'
IRQ_PIN='b8d2c1ee3204d554ab6e446fdcc2807c8c117861ccf313a1c875d4ed77728023'
IRQ_RECEIPTS={'c':'cad601ec3fa8ad298b3d64c9629646bc363b30a7ff510d0c329831d8b974d6e4',
              'cpp':'bd17c39f96067886f8eacaa17dc417d5bf97e6bcdc36a6cb7d3b532e7f32710f'}
PROVIDER_CHECKER='experiments/tsl9-irq-provider/verify.py'
# No formal graph may build until the separately owned provider proof freezes.
PROVIDER_PIN='3e0fd056537fbd189f88739862dbed70b8129423d8ef0db3e6770c7bae3e45f9'
PROVIDER_BUILD='verified-v3'
PROVIDER_RECEIPTS={'c':'8ff286e24611f568857d50d4acccb9eafb8803af69b9bbaef3e16262adaab25a',
                   'cpp':'9ca82b0a314182630bae5aa29ca9a0b4b4140ccd2251f52691e986216269dcf4'}
SPI_CHECKER='experiments/tsl9-spi-transfer-leaf/verify.py'
SPI_PIN='8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8'
SPECS=[["consumer",".consumer",94210,62,[["tsl9_flag_consumer_entry_17002",0,8],["tsl9_flag_consumer_body",8,54]]],["receiver",".receiver",92938,70,[["tsl9_receive_entry_16b0a",0,14],["tsl9_receive_body",14,56]]],["read",".read",92564,72,[["tsl9_register_read_entry_16994",0,4],["tsl9_register_read_body",4,68]]],["write",".write",92720,76,[["tsl9_register_write_entry_16a30",0,4],["tsl9_register_write_body",4,72]]],["spi",".spi",92310,72,[["tsl9_spi_transfer_entry_16896",0,8],["tsl9_spi_tx_poll_1689e",8,8],["tsl9_spi_tx_ready_168a6",16,16],["tsl9_spi_rx_poll_168b6",32,8],["tsl9_spi_rx_done_168be",40,10],["tsl9_spi_tx_wait_168c8",50,8],["tsl9_spi_timeout_168d0",58,4],["tsl9_spi_rx_wait_168d4",62,10]]],["packet",".packet",92796,142,[["tsl9_receive_buffer_entry_16a7c",0,14],["tsl9_packet_receive_body",14,116],["tsl9_packet_receive_finish_16afe",130,12]]],["ring",".ring",76744,92,[["tsl9_ring_insert_entry_12bc8",0,8],["tsl9_ring_init_12bd0",8,16],["tsl9_ring_scan_12be0",24,50],["tsl9_ring_finish_12c12",74,10],["tsl9_ring_advance_12c1c",84,8]]],["irq",".irq",76836,52,[["tsl9_ring_irq_entry_12c24",0,14],["tsl9_ring_irq_frame_12c32",14,10],["tsl9_ring_irq_dispatch_12c3c",24,18],["tsl9_ring_irq_finish_12c4e",42,6],["tsl9_ring_irq_empty_12c54",48,4]]],["provider",".provider",101752,164,[["tsl9_irq_provider_18d78",0,18],["tsl9_irq_provider_standard_18d8a",18,8],["tsl9_irq_provider_common_18d92",26,108],["tsl9_irq_provider_bank0_18dfe",134,10],["tsl9_irq_provider_extended_18e08",144,10],["tsl9_irq_provider_bank1_18e12",154,10]]]]
SECTION_ROWS=[tuple(x) for x in [["",0,0,0,0,0,0,0,0,0],[".ring",1,6,76744,3016,92,0,0,2,0],[".irq",1,6,76836,3108,52,0,0,2,0],[".spi",1,6,92310,18582,72,0,0,2,0],[".read",1,6,92564,18836,72,0,0,2,0],[".write",1,6,92720,18992,76,0,0,2,0],[".packet",1,6,92796,19068,142,0,0,2,0],[".receiver",1,6,92938,19210,70,0,0,2,0],[".consumer",1,6,94210,20482,62,0,0,2,0],[".provider",1,6,101752,28024,164,0,0,2,0],[".text",1,6,101916,28188,0,0,0,2,0],[".symtab",2,0,0,28188,1424,13,54,4,16],[".shstrtab",3,0,0,29612,100,0,0,1,0],[".strtab",3,0,0,29712,1306,0,0,1,0]]]
NAME_OFFSETS=[0,1,7,12,17,23,30,38,48,58,68,74,82,92]
PROGRAM_HEADERS=[[6,52,73780,73780,128,128,4,4],[1,0,73728,73728,180,180,4,4096],[1,3016,76744,76744,25172,25172,5,4096],[1685382481,0,0,0,0,0,6,0]]


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(data):return hashlib.sha256(data).hexdigest()
def digest(path):return sha(Path(path).read_bytes())


need(digest(ROOT/SPI_CHECKER)==SPI_PIN,'frozen SPI ELF reader')
_spi=runpy.run_path(str(ROOT/SPI_CHECKER),run_name='nine_span_reader')
ELF=_spi['ELF']


def portable(value,llvm):return _spi['portable'](value,ROOT,llvm)


def resolve(value,llvm):
    text=str(value)
    for token,path in [('${TSL9_ROOT}',ROOT),('${LLVM_BIN}',llvm),('${CLANG_INCLUDE}',llvm.parent/'lib/clang/18/include')]:
        text=text.replace(token,str(path))
    need('${' not in text,'unknown evidence path token')
    return Path(text).resolve()


def inventory(directory):
    directory=Path(directory)
    need(directory.is_dir() and all(p.is_file() and not p.is_symlink() for p in directory.iterdir()),'ordinary complete artifact directory')
    return {p.name:digest(p) for p in directory.iterdir()}


def snapshots(expected):return {p:digest(p) for p in expected}


def dependencies(language,llvm):
    for relative,pin in [(OLD_CHECKER,OLD_PIN),(IRQ_CHECKER,IRQ_PIN),(PROVIDER_CHECKER,PROVIDER_PIN),(SPI_CHECKER,SPI_PIN)]:
        need(len(pin)==64 and digest(ROOT/relative)==pin,'frozen formal checker '+relative)
    need(digest(HERE/'receive_graph.ld')==LINKER_PIN,'frozen nine-span original-address linker')
    old=runpy.run_path(str(ROOT/OLD_CHECKER),run_name='nine_span_old586')
    irq=runpy.run_path(str(ROOT/IRQ_CHECKER),run_name='nine_span_irq52')
    provider=runpy.run_path(str(ROOT/PROVIDER_CHECKER),run_name='nine_span_provider164')
    modules=[
      ('old586',ROOT/'experiments/tsl9-ring-insert/build/receive-graph-verified-v1'/language,OLD_RECEIPTS[language],old),
      ('irq52',ROOT/'experiments/tsl9-ring-irq-adapter/build/verified-v2'/language,IRQ_RECEIPTS[language],irq),
      ('provider164',HERE/'build'/PROVIDER_BUILD/language,PROVIDER_RECEIPTS[language],provider)]
    expected={};inventories={};records=[];inputs={}
    def add(path,pin):
        path=resolve(path,llvm)
        need(path not in expected or expected[path]==pin,'consistent inherited pin '+path.name)
        expected[path]=pin
    def add_inventory(directory,values):
        directory=resolve(directory,llvm)
        need(inventory(directory)==values,'complete replayed inventory '+directory.name)
        key=str(directory)
        need(key not in inventories or inventories[key]==values,'consistent inherited inventory')
        inventories[key]=values
        for name,pin in values.items():
            need(Path(name).name==name,'bounded inherited artifact name')
            add(directory/name,pin)
    for relative,pin in [(OLD_CHECKER,OLD_PIN),(IRQ_CHECKER,IRQ_PIN),(PROVIDER_CHECKER,PROVIDER_PIN),(SPI_CHECKER,SPI_PIN)]:
        add(ROOT/relative,pin)
    add(HERE/'receive_graph.ld',LINKER_PIN);add(Path(__file__).resolve(),digest(__file__))
    for name,directory,pin,module in modules:
        receipt=directory/'verification.json'
        need(digest(receipt)==pin,'frozen formal parent receipt '+name)
        if name=='old586':record,encoded=module['evaluate'](language,llvm,directory)
        else:record,encoded=module['evaluate'](ROOT,llvm,directory,language)
        encoded=encoded.encode() if isinstance(encoded,str) else encoded
        need(receipt.read_bytes()==encoded and json.loads(encoded)==record,'complete canonical LF parent replay '+name)
        if name=='old586':
            need(record['inputs_before']==record['inputs_after'],'stable full old586 dependency closure')
            for path,pin_value in record['inputs_before'].items():add(path,pin_value)
            for directory_key,values in record['dependency_inventories'].items():add_inventory(directory_key,values)
            values=dict(record['artifacts'])
            for item in record['native_inputs']:
                path=resolve(item['path'],llvm);need(digest(path)==item['sha256'],'old native input pin')
                inputs[item['unit']]=path
        else:
            inherited=record['inputs']
            if isinstance(inherited,dict):
                for path,pin_value in inherited.items():add(path,pin_value)
            else:
                for item in inherited:add(item['path'],item['sha256'])
            values={Path(item['path']).name:item['sha256'] for item in record['artifacts']}
            inputs['irq' if name=='irq52' else 'provider']=directory/'native.o'
        values['verification.json']=pin;add_inventory(directory,values)
        records.append(dict(component=name,schema=record['schema'],receipt=str(receipt),receipt_sha256=pin,replayed=True,
            controls=len(record['negative_controls']),commands=record.get('commands',record.get('recipes',[])),
            inherited_dependency_replays=record.get('dependency_replays',[])))
    need(set(inputs)=={s[0] for s in SPECS} and all(path.resolve() in expected for path in inputs.values()),'all nine actual native inputs explicitly pinned by replayed receipts')
    need(snapshots(expected)==expected,'joined source/tool/header/native/artifact pins equal actual pre-link snapshot')
    return dict(ELF=ELF,expected=expected,inventories=inventories,records=records,inputs=inputs,
                objects={n:ELF(path) for n,path in inputs.items()})


def sx(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def control(word,kind,pc):
    if kind==17:
        need(word&127==0x6f,'JAL opcode')
        imm=((word>>31)<<20)|(((word>>21)&1023)<<1)|(((word>>20)&1)<<11)|(((word>>12)&255)<<12)
        rd=(word>>7)&31;need(rd in (0,1),'JAL architectural rd')
        return ('jal',rd),pc+sx(imm,21),word&0xfffff000,4,pc+4 if rd==1 else None
    if kind==16:
        need(word&127==0x63,'B opcode');f3=(word>>12)&7;need(f3 in (0,1,4,5,6,7),'B condition')
        imm=((word>>31)<<12)|(((word>>7)&1)<<11)|(((word>>25)&63)<<5)|(((word>>8)&15)<<1)
        return ('branch',f3,(word>>15)&31,(word>>20)&31),pc+sx(imm,13),word&0xfe000f80,4,None
    if kind==44:
        need(word&3==1 and word>>13 in (6,7),'compressed branch opcode')
        imm=(((word>>12)&1)<<8)|(((word>>10)&3)<<3)|(((word>>5)&3)<<6)|(((word>>3)&3)<<1)|(((word>>2)&1)<<5)
        return ('c.branch',word>>13,8+((word>>7)&7)),pc+sx(imm,9),word&0x1c7c,2,None
    if kind==45:
        need(word&3==1 and word>>13==5,'C.J opcode, no fabricated link')
        imm=(((word>>12)&1)<<11)|(((word>>11)&1)<<4)|(((word>>9)&3)<<8)|(((word>>8)&1)<<10)|(((word>>7)&1)<<6)|(((word>>6)&1)<<7)|(((word>>3)&7)<<1)|(((word>>2)&1)<<5)
        return ('c.j',0),pc+sx(imm,12),word&0x1ffc,2,None
    raise ValueError('supported native symbolic relocation family')


def model(dep):
    definitions={};locals_expected=[('',0,0,0,0,0)];native_sections={};sites=[]
    final_indices={s[0]:i for i,s in enumerate(SECTION_ROWS)}
    for unit,section,va,size,regions in SPECS:
        e=dep['objects'][unit];need(e.header[0]==1 and e.header[6]==1,'actual RVC native ET_REL input')
        expected={n:(0,z,18,0,'.text.'+n) for n,_,z in regions}
        actual={s['name']:(s['value'],s['size'],s['info'],s['other'],e.sections[s['section']]['name'])
                for s in e.symbols if s['info']&15==2 and s['size']}
        need(actual==expected,'exact genuine native FUNC ownership/extent')
        alloc=[s for s in e.sections if s['flags']&2 and s['size']]
        need(sum(s['size'] for s in alloc)==size and len(alloc)==len(regions) and
             all(s['flags']==6 and s['type']==1 and s['align']==2 for s in alloc),'no extra native data/allocation')
        for n,start,z in regions:
            need(n not in definitions,'one actual definition per graph provider')
            definitions[n]=(va+start,z,18,0,final_indices[section]);native_sections['.text.'+n]=(unit,section,va+start,z)
        for s in e.symbols:
            if s['index']==0:continue
            if s['info']>>4:
                need(s['section']!=65521,'no native ABS providers')
                if s['section']==0:need(s['value']==s['size']==s['other']==0 and s['info']==16,'genuine native UND reference')
            else:
                need(s['info'] in (0,4),'native local metadata type')
                if s['section']==65521:locals_expected.append((s['name'],s['value'],s['size'],s['info'],s['other'],65521))
                else:
                    name=e.sections[s['section']]['name']
                    if name in ('.comment','.riscv.attributes'):
                        need(s['name'].startswith('$d.') and s['value']==s['size']==s['info']==s['other']==0,
                             'exact discarded native metadata mapping')
                        if name=='.riscv.attributes':locals_expected.append((s['name'],0,0,0,0,65521))
                        continue
                    need(name in native_sections,'native code mapping owner')
                    _,_,address,_=native_sections[name]
                    locals_expected.append((s['name'],address+s['value'],s['size'],s['info'],s['other'],final_indices[section]))
        for relocation in e.relocations:
            owner=e.sections[relocation['section']];need(owner['name'] in native_sections and relocation['addend']==0,'actual native relocation owner/addend')
            _,_,pc,size=native_sections[owner['name']];offset=relocation['offset'];symbol=e.symbols[relocation['symbol']]
            width=2 if relocation['type'] in (44,45) else 4
            need(offset%2==0 and offset+width<=size,'native symbolic site bounds')
            word=int.from_bytes(e.data(owner)[offset:offset+width],'little');signature,_,immediate,w,ra=control(word,relocation['type'],pc+offset)
            need(immediate==0 and width==w,'native symbolic placeholder immediate zero')
            sites.append(dict(unit=unit,owner=owner['name'],pc=pc+offset,offset=offset,type=relocation['type'],
                              name=symbol['name'],before_word=word,width=width,signature=signature,return_address=ra))
    need(len(definitions)==35 and len(sites)==32,'actual35 native definitions/32 symbolic sites')
    need(all(site['name'] in definitions for site in sites),'every native symbolic target has a genuine graph FUNC definition')
    return definitions,locals_expected,sites


def contract(e,dep,full=True):
    need(e.header==[2,243,1,0x17002,52,31020,1,52,32,4,40,14,12] and len(e.raw)==31580,
         'whole original-layout ELF header/file extent')
    need(e.program_headers==PROGRAM_HEADERS,'exact ELF container program headers, not a flat image')
    keys=['name','type','flags','address','offset','size','link','info','align','entsize']
    need([tuple(s[k] for k in keys) for s in e.sections]==SECTION_ROWS and
         [s['name_offset'] for s in e.sections]==NAME_OFFSETS,
         'exact nine AX spans and complete section metadata, no added data')
    definitions,local_rows,sites=model(dep);sk=['name','value','size','info','other','section']
    need(len(local_rows)==54 and [tuple(s[k] for k in sk) for s in e.symbols[:54]]==local_rows,
         'exact native-derived local FILE/mapping metadata')
    actual={s['name']:tuple(s[k] for k in sk[1:]) for s in e.symbols[54:]}
    need(len(e.symbols)==89 and len(actual)==35 and actual==definitions and not e.relocations,
         '35 strong real FUNC definitions, no UND/ABS/RELA/aliases')
    checked=[];excluded={}
    for site in sites:
        section=next(s for s in e.sections if s['address']<=site['pc']<s['address']+s['size'] and s['flags']&2)
        at=site['pc']-section['address'];word=int.from_bytes(e.data(section)[at:at+site['width']],'little')
        signature,target,_,width,ra=control(word,site['type'],site['pc'])
        need(signature==site['signature'] and target==definitions[site['name']][0] and ra==site['return_address'],
             'resolved native control preserves opcode/registers/genuine target/RA continuation')
        excluded.setdefault(section['name'],set()).update(range(at,at+width))
        checked.append(dict(owner=site['owner'],pc=site['pc'],type=site['type'],target_function=site['name'],
                            target=target,signature=signature,return_address=ra,
                            before_hex=site['before_word'].to_bytes(width,'little').hex(),after_hex=word.to_bytes(width,'little').hex()))
    ring=e.data('.ring')
    need(ring[54:60]==bytes.fromhex('b7070400fc47') and ring[68:70]==bytes.fromhex('8297'),
         'unknown resident pointer LW[0004004C] followed by C.JALR A5 is retained')
    original=(ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
    need(sha(original)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','whole official BIN identity')
    spans=[];joined=b'';instructions=0
    for unit,section,va,size,regions in sorted(SPECS,key=lambda row:row[2]):
        code=e.data(section);need(code==original[va-0x8000:va-0x8000+size],'all original bytes in each bounded span')
        native=b''.join(dep['objects'][unit].data('.text.'+n) for n,_,_ in regions)
        need(all(code[i]==native[i] for i in range(size) if i not in excluded.get(section,set())),
             'unchanged native noncontrol projection after real relocation')
        i=0;count=0
        while i<size:i+=4 if code[i]&3==3 else 2;count+=1
        need(i==size,'complete span instruction boundaries');instructions+=count;joined+=code
        spans.append(dict(section=section,start=va,end=va+size,bytes=size,instructions=count,sha256=sha(code)))
    need(len(joined)==802 and instructions==280 and sha(joined)==AGGREGATE_PIN,'nine original spans aggregate802B280i')
    gaps=[dict(start=a['end'],end=b['start'],bytes=b['start']-a['end']) for a,b in zip(spans,spans[1:]) if b['start']>a['end']]
    need(sum(g['bytes'] for g in gaps)==24370 and [(g['start'],g['end']) for g in gaps]==
         [(0x12c58,0x16896),(0x168de,0x16994),(0x169dc,0x16a30),(0x16b50,0x17002),(0x17040,0x18d78)],
         'five unowned LOAD gaps explicitly excluded from original-byte proof')
    if full:need(sha(e.raw)==ELF_PIN,'complete measured ELF metadata pin')
    return dict(allocated_bytes=802,instructions=280,genuine_FUNCs=35,UND=[],RELA=[],ABS_providers=[],
                original_spans=spans,original_aggregate_sha256=sha(joined),resolved_native_symbolic_sites=checked,
                resident_call=dict(pointer_word_address=0x4004c,call_pc=0x12c0c,source_register='A5',
                                   link_register='RA',return_address=0x12c0e,target_identity='UNKNOWN',ABI_closed=False),
                executable_LOAD_span_bytes=25172,unvalidated_LOAD_gap_bytes=25172-802,unowned_LOAD_gaps=gaps,
                flat_firmware_image=False,firmware_ready=False,sections=e.sections,symbols=e.symbols,
                program_headers=e.program_headers)


def negatives(e,dep):
    """Raw ELF faults are rejected with the whole-file SHA gate disabled."""
    results=[]
    def add(name,position,fmt,value):
        data=bytearray(e.raw);struct.pack_into(fmt,data,position,value)
        try:contract(ELF(data),dep,full=False)
        except (ValueError,IndexError,KeyError,StopIteration) as exc:
            results.append(dict(name=name,rejected=True,whole_hash_enabled=False,reason=str(exc)))
        else:raise ValueError('negative accepted '+name)
    byname={s['name']:s for s in e.symbols if s['info']>>4}
    for name in ['tsl9_ring_insert_entry_12bc8','tsl9_spi_transfer_entry_16896',
                 'tsl9_receive_buffer_entry_16a7c','tsl9_ring_irq_entry_12c24','tsl9_irq_provider_18d78']:
        at=e.section('.symtab')['offset']+byname[name]['index']*16
        for tag,delta,fmt,value in [('ABS',14,'<H',65521),('UND',14,'<H',0),('weak',12,'<B',34),
                                   ('value',4,'<I',byname[name]['value']+2),('size',8,'<I',2)]:
            add(tag+'_'+name,at+delta,fmt,value)
    add('local_FUNC_alias',e.section('.symtab')['offset']+2*16+12,'<B',2)
    add('wrong_entry',24,'<I',0x8000);add('ET_REL',16,'<H',1);add('wrong_RVC_flags',36,'<I',0)
    add('writable_RX_LOAD',52+2*32+24,'<I',6)
    for section,field,value in [('.ring',8,7),('.irq',20,50),('.spi',20,70),('.packet',12,0x16a7e),
                                ('.provider',32,4),('.text',20,2),('.shstrtab',8,2)]:
        add('section_'+section+'_'+str(field),e.header[5]+40*e.section(section)['index']+field,'<I',value)
    _,_,sites=model(dep)
    for index,site in enumerate(sites):
        section=next(s for s in e.sections if s['flags']&2 and s['address']<=site['pc']<s['address']+s['size'])
        position=section['offset']+site['pc']-section['address']
        word=int.from_bytes(e.raw[position:position+site['width']],'little')
        bit=21 if site['type']==17 else 8 if site['type']==16 else 3
        add('control_target_'+str(index),position,'<I' if site['width']==4 else '<H',word^(1<<bit))
        bit=7 if site['type']==17 else 12 if site['type']==16 else 13
        add('control_rd_or_condition_'+str(index),position,'<I' if site['width']==4 else '<H',word^(1<<bit))
    position=e.section('.ring')['offset']+58
    add('resident_pointer_address_changed',position,'<H',int.from_bytes(e.raw[position:position+2],'little')^4)
    add('resident_JALR_register_changed',e.section('.ring')['offset']+68,'<H',0x9702)
    for unit,section,_,_,_ in SPECS:
        position=e.section(section)['offset']
        add('native_noncontrol_'+unit,position,'<B',e.raw[position]^4)
    # IRQ MMIO-width/frame and the two physical MRET exits are owned bytes.
    for tag,at in [('irq_MMIO_operand',0),('irq_frame_allocation',14),('irq_MRET_finish',44),('irq_MRET_empty',48),
                   ('provider_byte_store',32),('provider_fresh_word_read',56),('provider_exit_register',142)]:
        section='.irq' if tag.startswith('irq_') else '.provider';position=e.section(section)['offset']+at
        add(tag,position,'<H',int.from_bytes(e.raw[position:position+2],'little')^4)
    return results


def recipes(dep,llvm,out):
    inputs=[str(dep['inputs'][n]) for n,_,_,_,_ in SPECS]
    return [('link',[str(llvm/'ld.lld.exe'),'--no-relax','-T',str(HERE/'receive_graph.ld'),*inputs,'-o',str(out/OBJECT)]),
            ('object',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(out/OBJECT)])]


def evaluate(language,llvm,out):
    dep=dependencies(language,llvm);before=dep['expected'];inv=inventory(out)
    need(set(inv) in [{OBJECT,'link.log','object.log','recipes.json'},
                     {OBJECT,'link.log','object.log','recipes.json','verification.json'}],
         'exact nine-span graph artifact inventory')
    commands=[dict(label=n,argv=portable(a,llvm),returncode=0) for n,a in recipes(dep,llvm,out)]
    need(json.loads((out/'recipes.json').read_bytes())==commands and not (out/'link.log').read_bytes(),
         'actual exact successful linker/reader recipe and empty diagnostics')
    log=(out/'object.log').read_text()
    need(str(out/OBJECT) in log and all(n in log for n in model(dep)[0]),'retained disassembly binds actual ELF/all FUNCs')
    e=ELF(out/OBJECT);facts=contract(e,dep);controls=negatives(e,dep)
    need(snapshots(before)==before,'complete input/artifact/source/header/tool snapshots stable')
    for directory,values in dep['inventories'].items():
        need(inventory(directory)==values,'complete inherited artifact inventory stable')
    need(inventory(out)==inv,'nine-span graph outputs unchanged while reading')
    record=dict(schema='TSL9-original-layout-IRQ-receive-graph-v1',language=language,firmware_ready=False,
                target_executed=False,ISA_emulated=False,inputs_before={str(k):v for k,v in before.items()},
                inputs_after={str(k):digest(k) for k in before},dependency_inventories=dep['inventories'],
                dependency_replays=dep['records'],native_inputs=[dict(unit=n,path=str(p),sha256=digest(p)) for n,p in dep['inputs'].items()],
                commands=commands,artifacts={n:v for n,v in inv.items() if n!='verification.json'},facts=facts,
                negative_controls=controls,limitations=[
                 'Only nine bounded original code spans match; the RX LOAD contains 24370 unowned gap bytes and is not a flat firmware image.',
                 'Thirty-two native symbolic controls resolve to 35 genuine defined FUNCs; the resident call through fresh LW[0004004C] remains UNKNOWN.',
                 'The original-byte/linkage proof inherits separate source/IR/recipe/MD proofs, not ordinary C ABI assumptions or hardware execution.',
                 'Resident/full private ABI, incoming interior/cold entries, IRQ/fault/alias effects, physical memory and hardware are not proved.',
                 'No firmware BIN, target/ISA/MMIO execution, OTA acceptance or flash validation.'])
    # Tuples describe decoded signatures internally; receipts use JSON-native
    # lists so replay compares the complete record as well as canonical bytes.
    record=json.loads(json.dumps(portable(record,llvm)))
    encoded=(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
    need(not re.search(rb'(?i)(?<![a-z0-9_])[a-z]:[/\\]|/(?:users|home)/',encoded),'portable LF evidence has no host path')
    return record,encoded


def main():
    parser=argparse.ArgumentParser(description=__doc__);action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--out-dir',type=Path);action.add_argument('--replay',type=Path)
    parser.add_argument('--language',choices=['c','cpp']);parser.add_argument('--llvm-bin',type=Path,
        default=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    parser.add_argument('--require-firmware-ready',action='store_true');args=parser.parse_args();llvm=args.llvm_bin.resolve()
    if args.replay:
        receipt=args.replay.resolve();out=receipt.parent;saved=json.loads(receipt.read_bytes());language=saved['language']
        need(args.language is None or args.language==language,'replay language')
    else:
        need(args.language is not None,'build language');language=args.language;out=args.out_dir.resolve()
    need(language in ('c','cpp') and out.is_relative_to(HERE/'build') and
         out.parent.name.startswith('receive-graph-verified-') and out.name==language,'owned nine-span graph output')
    if not args.replay:
        need(not out.exists(),'fresh output only');dep=dependencies(language,llvm);out.mkdir(parents=True);actual=[]
        for label,argv in recipes(dep,llvm,out):
            child=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (out/(label+'.log')).write_bytes(child.stdout)
            actual.append(dict(label=label,argv=portable(argv,llvm),returncode=child.returncode))
            need(child.returncode==0,'actual native recipe failed '+label)
        (out/'recipes.json').write_bytes((json.dumps(actual,indent=2)+'\n').encode())
        need(snapshots(dep['expected'])==dep['expected'],'stable complete dependency closure across actual link')
    record,encoded=evaluate(language,llvm,out)
    if args.replay:need(saved==record and receipt.read_bytes()==encoded,'complete canonical LF nine-span graph replay')
    else:(out/'verification.json').write_bytes(encoded)
    print(json.dumps(dict(result='PASS',language=language,bytes=802,instructions=280,FUNCs=35,resolved_symbolic_sites=32,
        UND=0,RELA=0,resident_target='UNKNOWN',controls=len(record['negative_controls']),inputs=len(record['inputs_before']),
        dependency_inventories=len(record['dependency_inventories']),ELF_sha256=ELF_PIN,receipt_sha256=sha(encoded),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: resident ABI, unowned LOAD gaps, full image/memory/hardware and flashability remain unproved.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,IndexError,KeyError,StopIteration) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
