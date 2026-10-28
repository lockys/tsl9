#include <stdint.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only candidate RV32 transmit handler assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
typedef struct {
 uint32_t next;
 uint32_t buffer;
 uint8_t argument_byte;
 uint8_t marker;
 uint16_t tag;
 uint16_t length;
 uint16_t unobserved_tail;
} candidate_queue_descriptor_t;
ASSERT(sizeof(void*)==4 && sizeof(pfnLibStatusErrorCB)==4,"RV32 pointer bytes");
ASSERT(sizeof(bleConfig_t)==64,"copied config size");
ASSERT(__builtin_offsetof(bleConfig_t,BufNumber)==15,"copied pool count byte");
ASSERT(__builtin_offsetof(bleConfig_t,staCB)==52,"copied optional status callback");
ASSERT(sizeof(candidate_queue_descriptor_t)==16,"observed pool stride");
ASSERT(__builtin_offsetof(candidate_queue_descriptor_t,next)==0,"next word");
ASSERT(__builtin_offsetof(candidate_queue_descriptor_t,buffer)==4,"stored buffer pointer");
ASSERT(__builtin_offsetof(candidate_queue_descriptor_t,argument_byte)==8,"incoming or overridden argument byte");
ASSERT(__builtin_offsetof(candidate_queue_descriptor_t,marker)==9,"marker byte");
ASSERT(__builtin_offsetof(candidate_queue_descriptor_t,tag)==10,"byte read then halfword write");
ASSERT(__builtin_offsetof(candidate_queue_descriptor_t,length)==12,"queued length halfword");
ASSERT(12+4==16 && 44+4==48,"encoded own frame RA saves");
/* Numeric assertions only: no live provider,MMIO identity or runtime allocation. */

ASSERT(__builtin_offsetof(bleConfig_t,TxNumEvent)==18,"copied transmit-event count byte");
ASSERT(__builtin_offsetof(bleConfig_t,BufMaxLen)==16,"copied configured buffer maximum");
