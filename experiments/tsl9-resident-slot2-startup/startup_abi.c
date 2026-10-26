#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 startup numeric contracts only.
#endif
#ifdef __cplusplus
#define CHECK static_assert
#else
#define CHECK _Static_assert
#endif
CHECK(sizeof(void*)==4 && sizeof(uintptr_t)==4 && sizeof(uint32_t)==4,"RV32 widths");
CHECK(0x20000008u+4u<=0x20000010u,"slot2 disjoint seed code destination");
CHECK(0x20000010u+48u==0x20000040u,"seed destination endpoint");
CHECK(0x402b0u+(0x20002e34u-0x20000040u)==0x430a4u,"candidate LLE source mapping");
CHECK(0x20002e6cu<=0x20002e70u && 0x20002e6cu<=0x20002ef8u,"LLE code disjoint later destination writes");
CHECK(0x20002e70u-0x20000040u+4u==11828u,"first inclusive word-copy bytes");
CHECK(0x20002ef8u-0x20002e70u+4u==140u,"second inclusive word-copy bytes");
CHECK(0x20003614u-0x20002ef8u+4u==1824u,"inclusive zero bytes");
/* These are numeric constraints,not mapped-memory/IRQ/startup-success proof. */
