"""Offline static pins and fixture checks only; never compiles or runs C."""
from pathlib import Path
import hashlib
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
MODEL = HERE.parent / 'v4160-1316a-default-candidate/model.c'
PINS = {
    'image': '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
    'window': '0eee723b584b06b7f4addfd45403bbfd17b9f0b09cb29aadaedfbf9f346a5514',
    'model': '91fa452ed5c321cb857c42c4ec1d9a3927e66e91d3525f1a9c088405167c694d',
    'harness': '9c57e29dd02a7701c42545a19d8ddd5ce3b5d72fb446d6f7de9042a6b096068a',
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def pin(name, data):
    require(hashlib.sha256(data).hexdigest() == PINS[name], name + ' pin mismatch')

def fixture(source, name):
    match = re.search(r'static const struct event ' + name + r'\[\]=\{(.*?)\};', source)
    require(match is not None, 'missing fixture ' + name)
    body = match.group(1).replace('PREFIX', 'R(0x13172,0x40048,0x1111), C(0x13188,0x1110,0x2000c29c,0,112), W(0x1318e,0x2000c29e,2,0xfff), W(0x13194,0x2000c2a0,1,1), W(0x1319c,0x2000c2a4,2,257)')
    tokens = re.findall(r'([RWCT])\(([^()]*)\)', body)
    remainder = re.sub(r'[RWCT]\([^()]*\)', '', body).replace(',', '').strip()
    require(not remainder and tokens, 'malformed fixture ' + name)
    return [(kind, *(int(v.strip(), 0) for v in args.split(','))) for kind, args in tokens]

PREFIX = [('R',0x13172,0x40048,0x1111),('C',0x13188,0x1110,0x2000c29c,0,112),('W',0x1318e,0x2000c29e,2,0xfff),('W',0x13194,0x2000c2a0,1,1),('W',0x1319c,0x2000c2a4,2,257)]
TAIL = ('T',0x131be,0x13138)
EXPECTED = {
 'normal': PREFIX+[('R',0x131a4,0x1054,0xfffffffc),('R',0x131a6,0x4004c,0x3333),('C',0x131b4,0x3332,8,0x1a69c,4),TAIL],
 'first': PREFIX[:2],
 'second': PREFIX+[('R',0x131a4,0x1054,0x8888),('R',0x131a6,0x4004c,0x2223),('C',0x131b4,0x2222,0x8894,0x1a69c,4)],
 'alias0': PREFIX+[('R',0x131a4,0x2000c29c,0x0fff0000),('R',0x131a6,0x4004c,0x2223),('C',0x131b4,0x2222,0x0fff000c,0x1a69c,4),TAIL],
 'alias1': PREFIX+[('R',0x131a4,0x2000c2a0,1),('R',0x131a6,0x4004c,0x2223),('C',0x131b4,0x2222,13,0x1a69c,4),TAIL],
 'alias2': PREFIX+[('R',0x131a4,0x2000c2a4,257),('R',0x131a6,0x4004c,0x2223),('C',0x131b4,0x2222,269,0x1a69c,4),TAIL],
 'wrap': PREFIX+[('R',0x131a4,0,0xfffffffc),('R',0x131a6,0x4004c,0x2223),('C',0x131b4,0x2222,8,0x1a69c,4),TAIL],
}

def check_fixture(source, name):
    require(fixture(source, name) == EXPECTED[name], name + ' fixture mismatch')

def rejected(fn):
    try:
        fn()
    except ValueError:
        return
    raise RuntimeError('negative test was accepted')

def main():
    image = IMAGE.read_bytes()
    data = {'image': image, 'window': image[0x1316a-0x8000:0x131c2-0x8000],
            'model': MODEL.read_bytes(), 'harness': (HERE / 'harness.c').read_bytes()}
    for name, blob in data.items():
        pin(name, blob)
        rejected(lambda name=name, blob=blob: pin(name, bytes([blob[0] ^ 1]) + blob[1:]))
    source = data['harness'].decode('ascii')
    for name in EXPECTED:
        check_fixture(source, name)
    rejected(lambda: check_fixture(source.replace('0x3332,8,0x1a69c', '0x3333,8,0x1a69c'), 'normal'))
    rejected(lambda: check_fixture(source.replace(', T(0x131be,0x13138)', '', 1), 'normal'))
    rejected(lambda: check_fixture(source.replace('R(0x131a4,0x1054,0xfffffffc), R(0x131a6,0x4004c,0x3333)', 'R(0x131a6,0x4004c,0x3333), R(0x131a4,0x1054,0xfffffffc)'), 'normal'))
    rejected(lambda: check_fixture(source.replace('0x2000c29c,0x0fff0000', '0x2000c29c,0x00000fff'), 'alias0'))
    rejected(lambda: check_fixture(source.replace('R(0x131a4,0,0xfffffffc)', 'R(0x131a4,2,0xfffffffc)'), 'wrap'))
    print('pins and literal fixtures checked; C not compiled or executed')

if __name__ == '__main__':
    main()
