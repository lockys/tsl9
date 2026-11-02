#!/usr/bin/env python3
"""Synthetic acceptance and rejection tests for the public HEX stream parser."""
import base64,json,subprocess,sys
from pathlib import Path
parser=Path(__file__).resolve().parent/'inspect.py'
def record(kind,offset,data):
    row=bytes([len(data),offset>>8,offset&255,kind])+data
    return b':'+(row+bytes([(-sum(row))&255])).hex().upper().encode()+b'\n'
def run(data):return subprocess.run([sys.executable,'-B',str(parser)],input=base64.b64encode(data),capture_output=True)
eof=record(1,0,b'');marker=b'CH32V20x_BLE_LIB_V1.31'
good=record(4,0,b'\x00\x06')+record(0,0xeb2c,b'\x00\x00\x00\x00')+record(0,0xe000,marker)+eof
p=run(good)
if p.returncode:raise ValueError('Synthetic valid input rejected')
d=json.loads(p.stdout)
if d['v131_markers']!=1 or d['same_numeric_hole_bytes_present']!=4:raise ValueError('Synthetic coverage mismatch')
bad=[good[:-1]+b'X',record(0,0,b'x')+record(0,0,b'x')+eof,record(0,0,b'x'),record(1,0,b'x')]
if any(run(x).returncode==0 for x in bad):raise ValueError('Invalid synthetic input accepted')
print(json.dumps({'passed':True,'valid_cases':1,'rejection_cases':len(bad),'network':False,'target_executed':False}))
