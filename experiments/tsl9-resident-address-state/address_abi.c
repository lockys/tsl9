#include <stddef.h>
#include <stdint.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 candidate configuration assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void *)==4 && sizeof(uint32_t)==4,"RV32 widths");
ASSERT(sizeof(bleConfig_t)==64 && offsetof(bleConfig_t,MacAddr)==24,"primary MAC source offset");
ASSERT(sizeof(((bleConfig_t *)0)->MacAddr)==6,"primary MAC source bytes");
ASSERT(UINT32_C(0x200031ec)+24==UINT32_C(0x20003204),"conditional config source word address");
ASSERT(232+6<=244 && 244+6==250 && 250+6<=296,"state fields nonoverlap and containment");
ASSERT(12+4<=16 && 16+4<=20 && 20+4<=24 && 24+4<=28 && 28+4==32,"five saved words fit own frame32");
/* No object,provider,import or executable entry;not a physical memory proof. */
