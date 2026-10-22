"""Bounded source rewrite proof, not a C interpreter or resident ABI claim."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD='experiments/tsl9-v4160-ota-handler/src/'
NEW='experiments/tsl9-v4160-ota-handler-compact/src/'
BASE={'ota_handler.c':'17998205c781a9223a7d2eb01f9a4bbd7cc5cc3013336795bb76e0da6e0bf9d0',
      'ota_handler.h':'fa6165d20e935b5c69dbab733c2340de13093a8827840bbffbce491bf9dd61de',
      'io.h':'64ef7d4de24543628ddee3254dacd5e79b3ac6a0950f504cad72c5ac880c3af5',
      'host_io.c':'3285e6228573cb39e5b09a845450268a74c2fbfb475e2d95b3673dc22a7b3d1b'}


def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(root):
    root=Path(root).resolve();new=json.loads((HERE/'core-pins.json').read_bytes())
    for name,pin in BASE.items():need(sha(root/OLD/name)==pin,'Immutable prior shared source '+name)
    for name,pin in new.items():need(sha(root/NEW/name)==pin,'Final compact shared source '+name)
    for name in ('ota_handler.h','host_io.c'):
        need((root/OLD/name).read_bytes()==(root/NEW/name).read_bytes(),'HOST API/provider/frame implementation unchanged '+name)
    prior=(root/OLD/'ota_handler.c').read_text();wanted=prior
    edits=[]
    for site,kind,target,mask,label in (
        ('0x9d7a','OH_SMALL_REPLY_13F66','0x13f66u','63u','small_reply'),
        ('0x9d7a','OH_SMALL_REPLY_13F66','0x13f66u','7u','small_reply'),
        ('0x9df4','OH_PAGE_REPLY_9B8E','0x9b8eu','63u','page_reply'),
        ('0x9df4','OH_PAGE_REPLY_9B8E','0x9b8eu','7u','page_reply'),
        ('0x9db4','OH_PACKET_REPLY_13E98','0x13e98u','15u','packet_reply')):
        old=f'OH_CALL(h,{site},{kind},{target},{mask});return;'
        need(wanted.count(old)==1,'Unique existing effect-plus-return endpoint '+old)
        wanted=wanted.replace(old,'goto '+label+';')
        edits.append(dict(site=site,callee=kind,mask=mask,label=label,setting_order_unchanged=True))
    old='OH_CALL(h,0x9db4,OH_PACKET_REPLY_13E98,0x13e98u,15u);'
    need(wanted.count(old)==1,'Unique remaining E packet effect endpoint')
    wanted=wanted.replace(old,'goto packet_reply;')
    marker='    }\n}\n\n#ifdef OH_HOST'
    labels=('    }\n    return;\nsmall_reply:\n'
            '    OH_CALL(h,0x9d7a,OH_SMALL_REPLY_13F66,0x13f66u,command==0x57u?63u:7u);return;\n'
            'packet_reply:\n'
            '    OH_CALL(h,0x9db4,OH_PACKET_REPLY_13E98,0x13e98u,15u);return;\n'
            'page_reply:\n'
            '    OH_CALL(h,0x9df4,OH_PAGE_REPLY_9B8E,0x9b8eu,command==0x57u?63u:7u);\n'
            '}\n\n#ifdef OH_HOST')
    need(wanted.count(marker)==1,'Exact original function-end insertion boundary')
    wanted=wanted.replace(marker,labels)
    old='    oh_port h;h.args[0]=context;h.args[1]=command;h.args[2]=payload;h.args[3]=length;'
    # Keep all native setters in their original order; only split the escaping allocation.
    new_line=('    volatile uint8_t response[2];oh_port h;h.response=response;\n'
              '    h.args[0]=context;h.args[1]=command;h.args[2]=payload;h.args[3]=length;')
    need(wanted.count(old)==1,'Original native wrapper construction/setter anchor')
    wanted=wanted.replace(old,new_line)
    need(wanted==(root/NEW/'ota_handler.c').read_text(),'Only six shared reply exits plus separate native response allocation changed in C')
    oldio=(root/OLD/'io.h').read_text();newio=(root/NEW/'io.h').read_text()
    array='typedef struct oh_port { oh_values values;uint32_t args[8];volatile uint8_t response[2]; } oh_port;'
    pointer=('/* Only the response bytes escape to the packet provider. Keep the argument\n'
             ' * state in a separate object so that this exposure does not alias args[]. */\n'
             'typedef struct oh_port { oh_values values;uint32_t args[8];volatile uint8_t *response; } oh_port;')
    need(oldio.count(array)==1 and oldio.replace(array,pointer)==newio,'Only native response field array-to-pointer and its explanatory comment changed in IO')
    need(oldio.split('#else\n',1)[0]==newio.split('#else\n',1)[0],'HOST primitives byte-identical')
    bridge='static __attribute__((always_inline)) inline void oh_native_call'
    need(oldio.split(bridge,1)[1]==newio.split(bridge,1)[1],'Entire native eight-register readwrite adapter and all caller/memory clobbers unchanged')
    fixture=HERE/'independent_host.c';oldfixture=root/'apk-analysis/tsl9-v4160-ota-handler-2026-10-22/ABI-review/independent_host.c'
    if not oldfixture.is_file():oldfixture=root/'analysis/v4160-ota-handler-2026-10-22/ABI-review/independent_host.c'
    need(sha(oldfixture)=='254b6dd5e60640eea6f7d0d54433d6abf1ff9f5af65c1761ecd58f36869b00f1'
         and fixture.read_bytes()==oldfixture.read_bytes(),'Genuinely independent prior narrative fixture reused byte-for-byte')
    return dict(schema='TSL9-OTA-handler-compact-bounded-source-delta-v1',passed=True,
                baseline_pins=BASE,selected_pins=new,shared_reply_rewrites=edits,
                E_packet_exit_to_same_shared_effect=True,W_small_page_mask=63,U_R_small_page_mask=7,packet_mask=15,
                branch_predicates_and_memory_effect_order_unchanged=True,HOST_API_and_primitives_identical=True,
                native_response_object='Separate volatile uint8_t[2], same typed pointer operation and length2 input',
                full_eight_argument_native_bridge_unchanged=True,callee_memory_clobber_unchanged=True,
                no_unroll_pragma_in_selected_source='#pragma' not in wanted,
                fixture_sha256=sha(fixture),fixture_byte_identity=True,
                physical_live_SP12_equivalence_proved=False,opaque_callee_footprint_proved=False,
                full_original_ABI_admitted=False,target_execution=False,ISA_emulation=False)
