"""Exact source-only delta against the immutable556B model; no HOST run."""
from pathlib import Path
import hashlib
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(root):
    root=Path(root);old=root/'experiments/tsl9-v4160-ota-reply-frame/src';new=root/'experiments/tsl9-v4160-ota-reply-object/src'
    pins={'ota_handler.c':'b3f41a6ec5caaa283428a421a28fa9d009601ccb7d593da9a3ffd85dca33d4c8','io.h':'e0c07e0b784d086f208890e3017d7236cc8f1187318c4414236fa4d1bc52ec65','ota_handler.h':'fa6165d20e935b5c69dbab733c2340de13093a8827840bbffbce491bf9dd61de'}
    for n,pin in pins.items():
        if sha(new/n)!=pin:raise ValueError('Final candidate source identity '+n)
    a=(old/'ota_handler.c').read_text();b=(new/'ota_handler.c').read_text()
    guard='        if(s->flash+UINT32_C(0xf7fff000)>UINT32_C(0x6f00))return;\n'
    original='    volatile uint8_t response[2];oh_port h;h.response=response;\n'
    backing='#ifdef __cplusplus\n    alignas(4) volatile uint8_t response[4];\n#else\n    _Alignas(4) volatile uint8_t response[4];\n#endif\n    oh_port h;h.response=response;\n'
    if a.count(guard)!=1 or a.count(original)!=1 or b!=a.replace(guard,guard+'        s->flash=OH_FLASH_BASE(s->flash);\n').replace(original,backing):raise ValueError('Only guarded full-base identity and native owned4B backing')
    a=(old/'io.h').read_text();b=(new/'io.h').read_text()
    host='#define OH_QUARTER_OFFSET(value) ((uint32_t)(value))\n';native='#define OH_QUARTER_OFFSET(value) oh_quarter_offset(value)\n'
    wanted=a.replace(host,host+'#define OH_FLASH_BASE(value) ((uint32_t)(value))\n').replace(native,native+'static inline uint32_t oh_flash_base(uint32_t value){__asm__ volatile("":"+r"(value));return value;}\n#define OH_FLASH_BASE(value) oh_flash_base(value)\n')
    if b!=wanted or (old/'ota_handler.h').read_bytes()!=(new/'ota_handler.h').read_bytes():raise ValueError('Only full-base HOST identity/native empty+r bridge; full8 and header unchanged')
    return dict(passed=True,source_pins=pins,guard_before_identity=True,HOST_uint32_identity=True,HOST_effect_order_unchanged=True,
        native_declared_backing_bytes=4,native_backing_alignment=4,backing_not_initialized=True,packet_semantic_lengths_unchanged=True,
        full8_and_memory_clobbers_text_unchanged=True,new_LINK_or_BIN=False,HOST_rerun=False)
