#!/usr/bin/env python3
"""Independent original ADC1892E raw operand contract; no ISA execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def case(root,slug):return next(p for p in(root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def locate(root,relative):
    p=root/relative
    if p.is_file():return p
    if relative.startswith('apk-analysis/tsl9-'):
        slug,tail=relative[len('apk-analysis/tsl9-'):].split('/',1);return case(root,slug)/tail
    return p
def module(p):
    s=importlib.util.spec_from_file_location('adc_independent_'+p.parent.name+'_'+p.stem,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def context(root):
    p=case(root,'v4160-register-contract-2026-10-22')/'adc-review/check.py';need(sha(p)==read(HERE/'reference-pins.json')['old_adc_reader'],'Pinned preexisting raw reader');m=module(p);previous,C,decode,E,old=m.context(root);return C,decode,E
def inspect(root,firmware=None):
    C,decode,E=context(root);ledger=read(HERE/'source-ledger.json');blob=bytes.fromhex(ledger['raw_hex']);rows=C.rows(blob,0x1892e,decode)
    need(len(blob)==88 and len(rows)==37 and sha(HERE/'source-ledger.json')==read(HERE/'reference-pins.json')['source_ledger'],'Frozen independent88-byte/37-row source')
    need(rows==ledger['rows'],'All original raw operands equal complete retained source inventory')
    bypc={x['PC']:x for x in rows};u=lambda n:n&0xffffffff
    masks=[u(bypc[a]['immediate']+bypc[b]['immediate']) for a,b in((0x18930,0x18934),(0x18950,0x18954),(0x1896c,0x18970))]
    need(masks==[0xe0f0feff,0xfff1f7fd,0xff0fffff],'Exact original LUI+ADDI mask constants')
    mem=[(x['PC'],x['op'],x['rs1'],x['immediate'],x['memory_width']) for x in rows if x['memory_width'] is not None]
    expected=[(0x1892e,'lw',10,4,32),(0x18938,'lw',11,24,32),(0x1893c,'lw',11,0,32),(0x18940,'lw',11,28,32),(0x18944,'lw',11,4,32),(0x1894c,'sw',10,4,32),(0x1894e,'lw',10,8,32),(0x18958,'lw',11,12,32),(0x1895c,'lw',11,16,32),(0x18960,'lw',11,8,32),(0x18968,'sw',10,8,32),(0x1896a,'lw',10,44,32),(0x18974,'lbu',11,20,8),(0x18982,'sw',10,44,32)]
    need(mem==expected,'All fourteen source effects, width, base, offset and order')
    need(sorted({x['rd'] for x in rows if x['rd'] not in(None,0)})==[13,14,15],'Original scratch-only own writes; A0/A1/A2/SP/RA/GP/TP/S unchanged')
    need([(x['PC'],x['immediate']) for x in rows if x['op']=='slli']==[(0x18946,8),(0x18962,1),(0x1897e,20)],'Unmasked full32 config word shifts and final byte shift')
    need(bypc[0x18978]['op']=='addi' and bypc[0x18978]['immediate']==-1 and bypc[0x1897a]['op']=='andi' and bypc[0x1897a]['immediate']==255,'Byte20 minusone then mask255')
    need(rows[-1]['op']=='jalr' and rows[-1]['rd']==0 and rows[-1]['rs1']==1 and rows[-1]['immediate']==0 and not any(x['op'] in('jal','beq','bne','blt','bltu','bge','bgeu') for x in rows),'Closed straightline source to original RET')
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Actual original ID2966 file identity');need(Path(firmware).read_bytes()[0x1092e:0x10986]==blob,'Actual original firmware88bytes')
    return dict(passed=True,source_bytes=88,source_rows=37,ordered_effects=14,masks=masks,original_written_GPRs=[13,14,15],A0_A1_preserved_by_every_own_instruction=True,config_words_full32=True,config_byte20_minusone_mask255=True,alias_requires_sequential_fresh_reads=True,actual_firmware_read=firmware is not None,metadata_only=firmware is None,target_execution=False,ISA_emulation=False,installed_identity_proved=False)
