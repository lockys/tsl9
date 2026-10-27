#include <stdint.h>
#include <stddef.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 message and stack numeric layout.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
typedef struct {uint8_t prefix[36];uint8_t payload[];} tsl9_event_extent;
ASSERT(sizeof(void*)==4 && sizeof(uint32_t)==4,"RV32 widths");
ASSERT(offsetof(tsl9_event_extent,payload)==36,"observed payload offset");
ASSERT(36+UINT8_MAX==291,"maximum numeric allocation request");
ASSERT(10+6==16 && 25+6==31 && 32+4==36,"observed copies and pointer slot");
ASSERT(76+4==80 && 28+12*4==76,"event builder saved registers and RA");
ASSERT(80+12==92 && 80+16==96,"incoming stack slots after own frame");
ASSERT(16+4<=40 && 40+9*4==76,"caller outgoing words do not overlap saved words");
/* No object,provider or executable entry;no live allocation/ownership proof. */
