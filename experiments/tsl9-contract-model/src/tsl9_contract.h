#ifndef TSL9_CONTRACT_H
#define TSL9_CONTRACT_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

/* Offline interpreter of observed OTA branches; no native hardware access. */
typedef enum { TC_UNKNOWN = -1, TC_NO = 0, TC_YES = 1 } tc_truth;
typedef enum { TC_BOOT, TC_RUNTIME } tc_image;
typedef enum { TC_GATT, TC_UART } tc_transport;
typedef enum { TC_RETURNED, TC_BUSY, TC_FLOW_UNKNOWN, TC_TRANSFER } tc_flow;
typedef enum { TC_SILENT, TC_REPLY, TC_INDETERMINATE, TC_STALLED, TC_TRANSFERRED } tc_outcome;
typedef enum {
    TC_EV_PROGRAM, TC_EV_READ, TC_EV_ROM_COPY, TC_EV_SCHEDULE,
    TC_EV_CANCEL_STARTUP, TC_EV_REPLY, TC_EV_STAY,
    TC_EV_DISCONNECT_REQUEST, TC_EV_JUMP_REQUEST, TC_EV_RESET_REQUEST,
    TC_EV_ELIGIBILITY_REFRESH
} tc_event_kind;
typedef struct {
    tc_event_kind kind;
    uint32_t va, address, argument;
    size_t length;
    tc_truth result;
} tc_event;
struct tc_model;
typedef struct {
    void *context;
    /* read fills data AND byte known masks (FF = fully known, 00 = unknown). */
    void (*read)(void *, uint32_t, uint8_t *, uint8_t *, size_t);
    /* The flow only describes whether the helper returned. Flash status is unchecked. */
    tc_flow (*program256)(void *, uint32_t, const uint8_t *, const uint8_t *);
    /* Explicit ROM overlap-copy assumption; absent callback leaves aligned source unknown. */
    void (*rom_copy)(void *, uint8_t *, uint8_t *, const uint8_t *, const uint8_t *, size_t);
    tc_truth (*schedule)(void *, uint32_t, uint32_t, uint32_t);
    void (*event)(void *, const tc_event *);
    /* Optional complete GATT wrapper adapter. Called after reply staging, before
       observation. UNKNOWN stops at its native-call boundary; known refusal is
       still RETURNED. Absent hook retains the earlier scalar-only contract. */
    tc_flow (*gatt_wrapper)(void *,struct tc_model *);
    /* Optional complete UART body adapter; a returned wrapper overrides the
       old uart_ready scalar. UNKNOWN preserves its actual native prefix. */
    tc_flow (*uart_wrapper)(void *,struct tc_model *);
} tc_backend;
typedef struct {
    uint8_t state, command, sum, sum_mask;
    uint16_t length, received;
    uint32_t last_clock;
    uint8_t clock_set;
    uint8_t data[1040], mask[1040];
} tc_parser;
typedef struct tc_model {
    tc_image image;
    tc_backend backend;
    uint8_t active, uart_session, stay;
    uint8_t active_mask, uart_session_mask;
    uint8_t stalled;
    uint8_t interpretation_halted; /* Evidence boundary, distinct from native busy. */
    uint8_t transferred; /* This caller activation did not return, not MCU death. */
    uint8_t uart_key, uart_sum;
    uint8_t uart_key_mask, uart_sum_mask;
    uint8_t identity[14], identity_mask[14];
    tc_parser gatt, uart;
    /* general_auth means BOTH Runtime connection-selection and auth gates passed. */
    tc_truth alloc_ok, link_ok, uart_ready, general_auth;
    tc_outcome outcome;
    uint8_t reply_command, reply_data[1040], reply_mask[1040];
    size_t reply_length;
    uint8_t reply_frame[1046], reply_frame_mask[1046];
    size_t reply_frame_length;
    tc_truth reply_queued;
    uint32_t command_count;
    /* 0=observed equal, 1=5-write budget exhausted, -1=unknown, -2=stalled, -3=transfer. */
    int metadata_result;
} tc_model;

void tc_init(tc_model *, tc_image, const tc_backend *);
/* Host selects a new analysis activation; no RAM/parser reset or native RET. */
int tc_resume_activation(tc_model *);
/* Synthetic identity or symbolic masks only; caller is responsible for never logging real IDs. */
void tc_identity(tc_model *, const uint8_t *, const uint8_t *);
/* Payload buffer has capacity>=1040; length may be zero and retain prior bytes.
   payload_address_mod4 supplies native alignment, not the host pointer's address. */
void tc_gatt_command(tc_model *, uint8_t, uint8_t *, uint8_t *, uint16_t, unsigned);
void tc_receive(tc_model *, tc_transport, const uint8_t *, size_t, uint32_t);
/* UART command-call staging for authoritative native SRAM adapters. The caller
   imports the original parser/session/key/data before calling, then exports effects. */
void tc_uart_command(tc_model *);
/* Raw GATT reply-wrapper staging for the general-command RAM adapter. */
int tc_gatt_reply(tc_model *,uint8_t,const uint8_t *,const uint8_t *,size_t);
int tc_metadata_select(tc_model *, uint8_t);
void tc_metadata_initialize(tc_model *);
/* Explicit callback delivery; scheduling is only a request and never executes itself. */
void tc_deliver_callback(tc_model *, uint32_t, uint32_t);

#ifdef __cplusplus
}
#endif
#endif
