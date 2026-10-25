#ifndef TSL9_MEMORY_ROM_REQUIREMENTS_V1_H
#define TSL9_MEMORY_ROM_REQUIREMENTS_V1_H

#include <stdint.h>

/* ID2966 only. verify-v1.py binds these numbers to the exact official image.
 * These are observed software requirements, not a detected hardware profile. */
#define TSL9_FW_SHA256 "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667"
#define TSL9_FW_BASE UINT32_C(0x8000)
#define TSL9_FW_END UINT32_C(0x1ac00)
#define TSL9_RESET_PC UINT32_C(0x186aa)
#define TSL9_INITIAL_GP UINT32_C(0x20004000)
#define TSL9_INITIAL_SP UINT32_C(0x20010000)
#define TSL9_INITIALIZER_SOURCE UINT32_C(0x1ab60)
#define TSL9_INITIALIZED_BYTES UINT32_C(128)
#define TSL9_ZERO_END UINT32_C(0x2000c958)
#define TSL9_VECTOR_BASE UINT32_C(0x8038)
#define TSL9_INITIAL_MEPC UINT32_C(0x9008)
#define TSL9_RESIDENT_ENTRY UINT32_C(0x40000)

/* Conditional 64 KiB RAM candidate. These bounds do not identify a chip,
 * establish RAM ownership, or certify stack/heap availability. */
#define TSL9_CANDIDATE_RAM_BASE UINT32_C(0x20000000)
#define TSL9_CANDIDATE_RAM_END UINT32_C(0x20010000)

/* Saved WCH SDK's default ROM-library profile; installed contents unknown. */
#define TSL9_SDK_TABLE_BASE UINT32_C(0x40034)
#define TSL9_SDK_SLOT_STRIDE UINT32_C(4)
#define TSL9_SDK_MEMSET_SLOT UINT32_C(0x40048)
#define TSL9_SDK_MEMCPY_SLOT UINT32_C(0x4004c)

#define TSL9_COPY_END (TSL9_INITIAL_GP + TSL9_INITIALIZED_BYTES)
#define TSL9_INITIALIZATION_SPAN (TSL9_ZERO_END - TSL9_INITIAL_GP)
#define TSL9_ZERO_BYTES (TSL9_ZERO_END - TSL9_COPY_END)
#define TSL9_NUMERIC_GAP_TO_SP (TSL9_INITIAL_SP - TSL9_ZERO_END)

#endif
