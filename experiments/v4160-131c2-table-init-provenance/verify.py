"""Read-only byte-pinned evidence audit; no target execution or instruction emulation."""
from pathlib import Path
import hashlib
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
WINDOWS = {
    0x13208: 'b7070400fc47b785070813060010938505901795ff1f1305a52782971797ff1f0347f7369307a0056304f700eff03fc5',
    0x13268: 'b7070400fc47b775070813060010938505701795ff1f1305a53182971797ff1f0347f7409307a0056304f700eff07fceb7070400fc47b775070813060010938505601795ff1f1305a53e82971797ff1f0347f74d9307a0056304f700eff01fdc',
    0x1abc0: '94c4002094c5002094c60020',
    0x186aa: '97c1fe1f938161951781ff1f1301e194172500001305654a938501001386010863fac5008322050023a0550011059105e3eac5fe',
    0x167a6: '011122cc26ca4ac84ec606ce52c456c2aa840144938901061309e00f83a70900a29703c707006316970003c51700efe0dfdf0904e31424ff9d4a054493894106138a81061309400203a709005697834607000347170093771700a207d58f63989700098b09c7a2850145ef10a01703270a005697834607000347170093771700a207d58f6398f400098b09c7a2850545ef10401505041374f40f9d0ae31624fb',
    0x12e86: 'b70704004111bc4722c41794ff1f1304446006c6228513060010814582979307a005a30ff40eb717430b938727401cc0b717450d938747c45cc0b7370c2b9387a7c01cc4b7571f5ff9075cc4b727212a938707e21cc82244b24041016ff03ff7',
    0x12f7a: 'b70704004111bc4722c41794ff1f1304046106c6228513060010814582979307a005a30ff40e1c40370700ffb7a69a0493f70720d98f1cc0b7078099938707305cc01c444167130747f0898bd98f58441cc4b70700027d8f93863602558f58c45448370700031307f70f18c837070200758fb7a608ff938606b0558f58c8370723a018cc584cb716ff009386c68913770720558f58cc3707009f1307073018d05850b70601ff9386c6f0098b558f58d0185423080402b240f98f37a79e0c13073780d98f1cd4b707ff039387f70f5cd4224441016ff0bfef',
    0x13084: 'b70704004111bc4722c41794ff1f1304646006c6228513060010814582979307a005a30ff40e1c403717ff001307078093f70720d98f1cc099679387f70f2312f400d1472303f4002244b24041016ff01ff8',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check_windows(data):
    for address, text in WINDOWS.items():
        expected = bytes.fromhex(text)
        offset = address - BASE
        need(offset >= 0 and len(data) >= offset + len(expected), 'truncated window %#x' % address)
        need(data[offset:offset + len(expected)] == expected, 'changed window %#x' % address)
    need(struct.unpack('<III', data[0x1abc0-BASE:0x1abcc-BASE]) ==
         (0x2000c494, 0x2000c594, 0x2000c694), 'pointer words')


def check_image(data):
    need(len(data) == 76800, 'image length')
    need(hashlib.sha256(data).hexdigest() == SHA256, 'image SHA-256')
    check_windows(data)


def reject(fn, data, label):
    try:
        fn(data)
    except ValueError:
        return
    raise ValueError('malformed fixture accepted: ' + label)


def main():
    data = IMAGE.read_bytes()
    check_image(data)
    reject(check_image, data[:-1], 'truncated image')
    altered = bytearray(data)
    altered[0] ^= 1
    reject(check_image, bytes(altered), 'hash mismatch outside windows')
    for address, text in WINDOWS.items():
        offset = address - BASE
        reject(check_windows, data[:offset + len(bytes.fromhex(text)) - 1], 'truncated %#x' % address)
        for i in range(len(bytes.fromhex(text))):
            altered = bytearray(data)
            altered[offset + i] ^= 1
            reject(check_windows, bytes(altered), 'mutated %#x+%d' % (address, i))
    print('PASS: image identity, eight byte windows, pointer words, malformed and per-byte mutation fixtures')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        print('FAIL:', error, file=sys.stderr)
        sys.exit(1)
