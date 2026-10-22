#!/usr/bin/env python3
"""Bounded raw direct-branch scan of the supplied immutable Runtime image.

Every two-byte site is considered, including data and the second half of
32-bit instructions. This is not CFG discovery, execution, or an indirect-
reference proof. Known source instruction boundaries classify false positives.
"""
import collections
import hashlib
import json
from pathlib import Path

RUNTIME_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ROWS_SHA='a75e92e17458158e7b1411052ac30987a45cefb6a38fccaa859754f73fbbe4df'
BASE=0x8000
START,END=0x1874a,0x18834


def need(ok,message):
    if not ok:
        raise ValueError(message)


def sx(value,bits):
    return value-(1<<bits) if value&(1<<(bits-1)) else value


def direct(raw,offset,pc):
    h=int.from_bytes(raw[offset:offset+2],'little');q=h&3;f=h>>13
    if q!=3:
        if q==1 and f in (1,5):
            imm=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)
            imm|=((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
            return dict(family='C.JAL' if f==1 else 'C.J',target=pc+sx(imm,12),bytes=2,rd=1 if f==1 else 0)
        if q==1 and f in (6,7):
            imm=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
            return dict(family='C.BEQZ' if f==6 else 'C.BNEZ',target=pc+sx(imm,9),bytes=2,rd=None)
        return None
    if offset+4>len(raw):
        return None
    w=int.from_bytes(raw[offset:offset+4],'little');op=w&127
    if op==0x6f:
        imm=((w>>31&1)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
        return dict(family='JAL',target=pc+sx(imm,21),bytes=4,rd=w>>7&31)
    if op==0x63 and (w>>12&7) in (0,1,4,5,6,7):
        imm=((w>>31&1)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
        return dict(family='B',target=pc+sx(imm,13),bytes=4,rd=None)
    return None


def inspect(root):
    path=root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    table_path=root/'analysis/boot2580-clock-2026-10-22/original-runtime-rows.json'
    raw=path.read_bytes();table_raw=table_path.read_bytes()
    need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==RUNTIME_SHA,'Exact original Runtime')
    need(hashlib.sha256(table_raw).hexdigest()==ROWS_SHA,'Frozen source-backed clock instruction table')
    table=json.loads(table_raw);rows=table['instructions'];cursor=START
    need(len(rows)==93 and table['original_start']==START,'Original clock boundary inventory')
    starts={}
    for row in rows:
        data=bytes.fromhex(row['bytes'])
        need(row['addr']==cursor and row['size']==len(data) and len(data) in (2,4)
             and raw[cursor-BASE:cursor-BASE+len(data)]==data,'Contiguous source instruction/raw-image equality')
        starts[cursor]=row;cursor+=len(data)
    need(cursor==END,'Complete original234B clock; cold tail included')
    counts=collections.Counter();hits=[]
    for offset in range(0,len(raw),2):
        pc=BASE+offset;candidate=direct(raw,offset,pc)
        if candidate is None:
            continue
        counts[candidate['family']]+=1
        if not START<=candidate['target']<END:
            continue
        n=candidate['bytes']
        known=pc in starts or pc==0x18720
        containing=[row['addr'] for row in rows if row['addr']<pc<row['addr']+row['size']]
        hits.append(dict(PC=pc,raw=raw[offset:offset+n].hex(' '),**candidate,
                         external=not START<=pc<END,source_instruction_start_confirmed=known,
                         containing_original_instruction=containing))
    expected=[
        (0x18720,0x1874a,'JAL',True,True),(0x187b0,0x187b8,'C.BNEZ',False,True),
        (0x187b4,0x187a2,'B',False,True),(0x187c2,0x18830,'B',False,True),
        (0x187ce,0x1882c,'B',False,True),(0x187da,0x18772,'C.BNEZ',False,False),
        (0x1880c,0x18806,'B',False,True),(0x18828,0x18824,'B',False,True),
        (0x18832,0x187ca,'C.J',False,True)]
    need([(h['PC'],h['target'],h['family'],h['external'],h['source_instruction_start_confirmed'])
          for h in hits]==expected,'Complete exact raw scan candidate inventory')
    need(counts==dict(JAL=1811,**{'C.J':917,'C.JAL':125,'C.BEQZ':601,'B':1492,'C.BNEZ':522}),
         'All scanned raw instruction-family counts')
    need(hits[0]['raw']=='ef 00 a0 02' and hits[0]['rd']==1,'Actual source-backed reset JAL to clock entry')
    need(hits[5]['containing_original_instruction']==[0x187d8],
         'Known false positive is a32-bit LUI second half')
    return dict(firmware_sha256=RUNTIME_SHA,source_rows_sha256=ROWS_SHA,
                file_base=BASE,target_range=[START,END],sites_scanned=38400,
                raw_family_candidates=dict(counts),window_candidates=hits,
                external_direct_entry_candidates=1,external_direct_interior_candidates=0,
                indirect_data_pointer_resident_BOOT_IRQ_coverage=False,
                raw_scan_contains_data_and_halfword_false_positives=True,
                original_cold_tail=dict(store_PC='0x18830',jump_PC='0x18832',target='0x187ca',
                                        inbound_from='0x187c2',free_space=False),
                full_incoming_reference_proof=False,target_execution=False,ISA_emulation=False)
