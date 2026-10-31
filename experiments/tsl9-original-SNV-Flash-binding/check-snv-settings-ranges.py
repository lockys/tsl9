"""Cross-check numerical SNV and settings windows using pinned receipts."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
def receipt(relative, expected):
    data = (root / relative).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit('Reviewed receipt changed')
    result = json.loads(data)
    if not result['passed'] or not result['contract']['passed']:
        raise SystemExit('Prior contract is not verified')
    return result['contract']

snv = receipt('experiments/tsl9-original-SNV-Flash-binding/verification-v1.json',
              '440f3848555e285dbfee3d0533b7d2f27c0c55f8a39d0ff5632c29790865abcb')
settings = receipt('experiments/tsl9-NVM-record-layout/verification-v1.json',
                   '77ee969b41b5fd031dd448462d8540607abcb78be4e214e8dcc21874d6450da5')
pages = sorted((row['writer']['Flash_destination'], row['writer']['CPU_program_bytes'])
               for row in settings['records'])
if pages != [(0x08077500 + 256 * i, 256) for i in range(6)]:
    raise SystemExit('Settings writer windows changed')
if snv['effective_SNVBlock'] != 256 or snv['logical_page_arguments'] != [0x08077c00 + 256 * i for i in range(3)]:
    raise SystemExit('SNV logical windows changed')
if snv['logical_window'] != [0x08077c00, 0x08077f00]:
    raise SystemExit('SNV endpoint changed')
if 0x08077c00 - 0x08077b00 != 256 or 0x08077f00 - 0x08000000 != 491264:
    raise SystemExit('Gap or conditional end offset changed')
print('Settings and conditional SNV numeric windows verified; target not executed.')
