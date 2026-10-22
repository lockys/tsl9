"""Exact bounded source edit; no HOST or native executable is run."""
from pathlib import Path
import hashlib
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(root):
    root=Path(root);old=root/'experiments/tsl9-v4160-ota-handler-compact/src';new=root/'experiments/tsl9-v4160-ota-reply-frame/src'
    pins={'ota_handler.c':'a19348b53c6f620015552713ee35f7711fb0cd6377a01bed8de59147d2a140fd','io.h':'761fa97b4226513ebb26c6b9ec28a8589f2a7360f3ad625d74addd983e874014','ota_handler.h':'fa6165d20e935b5c69dbab733c2340de13093a8827840bbffbce491bf9dd61de'}
    for name,pin in pins.items():
        if sha(new/name)!=pin:raise ValueError('Frozen new source '+name)
    needle='            OH_CALL(h,0x9d00,OH_QUARTER_9C0A,0x9c0au,3u);\n'
    a=(old/'ota_handler.c').read_text();b=(new/'ota_handler.c').read_text()
    if a.count(needle)!=1 or b!=a.replace(needle,needle+'            s->buffer=OH_QUARTER_OFFSET(s->buffer);\n'):raise ValueError('Only post-quarter unsigned identity in shared algorithm')
    a=(old/'io.h').read_text();b=(new/'io.h').read_text()
    host='typedef oh_host oh_port;\n';native='typedef struct oh_port { oh_values values;uint32_t args[8];volatile uint8_t *response; } oh_port;\n'
    wanted=a.replace(host,host+'#define OH_QUARTER_OFFSET(value) ((uint32_t)(value))\n').replace(native,native+'static inline uint32_t oh_quarter_offset(uint32_t value){__asm__ volatile("":"+r"(value));return value;}\n#define OH_QUARTER_OFFSET(value) oh_quarter_offset(value)\n')
    if b!=wanted or (new/'ota_handler.h').read_bytes()!=(old/'ota_handler.h').read_bytes():raise ValueError('Only HOST identity/native empty+r bridge; header/opaque8 bridges unchanged')
    return dict(passed=True,new_source_pins=pins,only_post_quarter_identity=True,HOST_uint32_identity=True,full8_bridges_and_memory_clobbers_unchanged=True,
        no_new_provider_effects=True,native_source_pressure_change=True,HOST_rerun=False,physical_ABI_admitted=False)
