"""Compare pinned reference source and reconstructed erase path offline."""
import argparse
import hashlib
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--wch-flash-source', type=Path, required=True)
p.add_argument('--app-source', type=Path, required=True)
a = p.parse_args()
def pinned(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('source hash mismatch: ' + path.name)
    return raw.decode('utf-8')
wch = pinned(a.wch_flash_source, '19c421e76984d9dcb3d9cb813814919333478fc19066787fd0d532f4d37153bd')
app = pinned(a.app_source, '8b429370793df5149ff3a324a17f656b19c3158caa9ba89d3da8cc155fedbbc0')
def need(value):
    if not value: raise ValueError('source pattern or address condition mismatch')
for text in ('page size 4KB', '1page = 256Byte', '#define CR_PAGE_ER                 ((uint32_t)0x00020000)', '#define CR_STRT_Set                ((uint32_t)0x00000040)', '#define SR_BSY                     ((uint32_t)0x00000001)'):
    need(text in wch)
fast = wch.split('void FLASH_ErasePage_Fast(uint32_t Page_Address)', 1)[1].split('\n}', 1)[0]
for text in ('Page_Address &= 0xFFFFFF00', 'FLASH->CTLR |= CR_PAGE_ER', 'FLASH->ADDR = Page_Address', 'FLASH->CTLR |= CR_STRT_Set', 'while(FLASH->STATR & SR_BSY)', 'FLASH->CTLR &= ~CR_PAGE_ER'):
    need(text in fast)
leaf = app.split('/* Original0x18EC4..0x18EE0. */', 1)[1].split('/* Original0x18EF2', 1)[0]
for text in ('0x40022000', '0x00000010', '0x00020000', '0xffffff00', '0x00000014', '0x00000040', '0x0000000c', '0x00000001', '0xfffe0000'):
    need(text in leaf)
pages = list(range(0x08077500, 0x08077b00, 256))
need(len(pages) == 6 and len({p & ~0xff for p in pages}) == 6)
need({p & ~0xfff for p in pages} == {0x08077000})
print('Pinned candidate erase sources and six numerical page relationships verified; device behavior unverified.')
