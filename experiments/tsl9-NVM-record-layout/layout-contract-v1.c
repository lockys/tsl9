#include "requirements-v1.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only original RV32 NVM layout requirements;no host model.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void *)==4,"RV32 pointer width");
ASSERT(TSL9_NVM_RECORDS==6,"six original records");
ASSERT(TSL9_NVM_NUMERIC_END-TSL9_NVM_NUMERIC_START==6*256,"numeric page span");
ASSERT(TSL9_NVM_0_BYTES+TSL9_NVM_1_BYTES+TSL9_NVM_2_BYTES+TSL9_NVM_3_BYTES+TSL9_NVM_4_BYTES+TSL9_NVM_5_BYTES==1269,"copied payload bytes");
ASSERT(TSL9_NVM_RAM_END-TSL9_NVM_RAM_START==1272,"numeric RAM span");
ASSERT(TSL9_NVM_RAM_END<=UINT32_C(0x2000c958),"inside original reset zero end");
ASSERT(TSL9_NVM_CPU_PROGRAM_BYTES<=268 && 268+4==272,"writer source avoids savedRA in own frame");
ASSERT(TSL9_NVM_CPU_PROGRAM_BYTES-TSL9_NVM_0_BYTES==144,"first additional source extent");
ASSERT(TSL9_NVM_CPU_PROGRAM_BYTES-TSL9_NVM_5_BYTES==123,"last additional source extent");
ASSERT((TSL9_NVM_0_SOURCE&255)==0,"record0 numeric alignment");
ASSERT(TSL9_NVM_0_BYTES<=TSL9_NVM_CPU_PROGRAM_BYTES,"record0 payload fits CPU transfer");
ASSERT((TSL9_NVM_1_SOURCE&255)==0,"record1 numeric alignment");
ASSERT(TSL9_NVM_1_BYTES<=TSL9_NVM_CPU_PROGRAM_BYTES,"record1 payload fits CPU transfer");
ASSERT((TSL9_NVM_2_SOURCE&255)==0,"record2 numeric alignment");
ASSERT(TSL9_NVM_2_BYTES<=TSL9_NVM_CPU_PROGRAM_BYTES,"record2 payload fits CPU transfer");
ASSERT((TSL9_NVM_3_SOURCE&255)==0,"record3 numeric alignment");
ASSERT(TSL9_NVM_3_BYTES<=TSL9_NVM_CPU_PROGRAM_BYTES,"record3 payload fits CPU transfer");
ASSERT((TSL9_NVM_4_SOURCE&255)==0,"record4 numeric alignment");
ASSERT(TSL9_NVM_4_BYTES<=TSL9_NVM_CPU_PROGRAM_BYTES,"record4 payload fits CPU transfer");
ASSERT((TSL9_NVM_5_SOURCE&255)==0,"record5 numeric alignment");
ASSERT(TSL9_NVM_5_BYTES<=TSL9_NVM_CPU_PROGRAM_BYTES,"record5 payload fits CPU transfer");
ASSERT(TSL9_NVM_0_RAM+TSL9_NVM_0_BYTES<=TSL9_NVM_2_RAM,"buffers0,2 disjoint");
ASSERT(TSL9_NVM_2_RAM+TSL9_NVM_2_BYTES<=TSL9_NVM_5_RAM,"buffers2,5 disjoint");
ASSERT(TSL9_NVM_5_RAM+TSL9_NVM_5_BYTES<=TSL9_NVM_1_RAM,"buffers5,1 disjoint");
ASSERT(TSL9_NVM_1_RAM+TSL9_NVM_1_BYTES<=TSL9_NVM_3_RAM,"buffers1,3 disjoint");
ASSERT(TSL9_NVM_3_RAM+TSL9_NVM_3_BYTES<=TSL9_NVM_4_RAM,"buffers3,4 disjoint");
ASSERT(TSL9_NVM_1_RAM-(TSL9_NVM_5_RAM+TSL9_NVM_5_BYTES)==3,"three-byte gap");
/* No storage,callable function,MMIO access or executable entry. */
