#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private transport regions only; never execute on a host or device.
#endif

/* Original [0x8A56,0x8B6E), including the reachable post-RET copy body.
 * C owns free-register unsigned arithmetic, checksum and volatile memory.
 * Physical S-register source/destination operations use explicit ports: this
 * avoids the compiler inventing an ordinary ABI save frame for private state.
 * Explicit architectural ports preserve inherited registers, fresh memory,
 * frames, opaque calls and tail transfer. These are not ordinary C ABI entries.
 * The initial 1039 guard does not bound then-live S0 after opaque calls.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
#define FRAME ENTRY __attribute__((naked, used, aligned(2)))

REGION void tsl9_filter_external_8a56(void)
{
    register uint32_t limit __asm__("a5") = 1039;
    __asm__ volatile(".Ltransport_large:\nbltu a5, a3, .Ltransport_large\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_transport_bare_return_8b6c\n"
                     : : "r"(limit) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_transport_frame_8a5e(void)
{
    __asm__ volatile("addi sp, sp, -32\nsw s0, 24(sp)\nsw s1, 20(sp)\n"
                     "sw s2, 16(sp)\nsw s3, 12(sp)\nsw ra, 28(sp)\n"
                     "lhu a4, 150(gp)\nmv s2, a0\nmv s0, a3\n"
                     "mv s1, a2\nmv s3, a1\n"
                     ".Ltransport_first_miss:\nbne a4, a0, .Ltransport_first_miss\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_transport_second_8a96\n");
}

REGION void tsl9_transport_first_8a7a(void)
{
    register uint32_t provider __asm__("a5") = 65534;
    __asm__ volatile(".Ltransport_first_empty:\nbeq a4, a5, .Ltransport_first_empty\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_transport_second_8a96\n"
                     : : "r"(provider) : "memory");
    provider = 0x40000;
    __asm__ volatile("" : "+r"(provider) : : "memory");
    provider = *(volatile uint32_t *)(uintptr_t)(provider + 316);
    __asm__ volatile("addi a1, gp, 128\njalr a5\n"
                     : : "r"(provider)
                     : "a0", "a1", "a2", "a3", "a4", "a6", "memory");
    __builtin_unreachable();
}

REGION void tsl9_transport_first_result_8a90(void)
{
    register uint32_t one __asm__("a5") = 1;
    __asm__ volatile(".Ltransport_first_admitted:\nbeq a0, a5, .Ltransport_first_admitted\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_transport_select0_8acc\n"
                     : : "r"(one) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_transport_second_8a96(void)
{
    register uint32_t provider __asm__("a5");
    __asm__ volatile("lhu a5, 154(gp)\n" : "=r"(provider) : : "memory");
    __asm__ volatile(".Ltransport_second_miss:\nbne a5, s2, .Ltransport_second_miss\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_transport_reject_8abe\n"
                     : : "r"(provider) : "memory");
    __asm__ volatile("lui a5, 0x10\naddi a5, a5, -2\n" : "=r"(provider) : : "memory");
    __asm__ volatile(".Ltransport_second_empty:\nbeq s2, a5, .Ltransport_second_empty\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_transport_reject_8abe\n"
                     : : "r"(provider) : "memory");
    provider = 0x40000;
    __asm__ volatile("" : "+r"(provider) : : "memory");
    provider = *(volatile uint32_t *)(uintptr_t)(provider + 316);
    __asm__ volatile("addi a1, gp, 128\nmv a0, s2\njalr a5\n"
                     : : "r"(provider)
                     : "a0", "a1", "a2", "a3", "a4", "a6", "memory");
    __builtin_unreachable();
}

REGION void tsl9_transport_second_result_8ab6(void)
{
    register uint32_t one __asm__("a5") = 1;
    __asm__ volatile("" : "+r"(one) : : "memory");
    register uint32_t bank __asm__("a2") = 1;
    __asm__ volatile(".Ltransport_second_admitted:\nbeq a0, a5, .Ltransport_second_admitted\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_transport_pack_8ace\n"
                     : : "r"(one), "r"(bank) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_transport_reject_8abe(void)
{
    __asm__ volatile("lw ra, 28(sp)\nlw s0, 24(sp)\nlw s1, 20(sp)\n"
                     "lw s2, 16(sp)\nlw s3, 12(sp)\naddi sp, sp, 32\nret\n");
}

REGION void tsl9_transport_select0_8acc(void)
{
    register uint32_t bank __asm__("a2") = 0;
    __asm__ volatile("" : : "r"(bank) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_transport_pack_8ace(void)
{
    register uint32_t bank __asm__("a2");
    __asm__ volatile("" : "=r"(bank) : : "memory");
    register uint32_t buffer __asm__("a5") = 1062;
    __asm__ volatile("" : "+r"(buffer), "+r"(bank) : : "memory");
    buffer = bank * buffer;
    register uint32_t base __asm__("a3");
    __asm__ volatile("auipc a3, 0x20002\naddi a3, a3, 1718\n"
                     : "=r"(base), "+r"(buffer) : : "memory");
    register uint32_t checksum __asm__("a4") = 0xffff8000u;
    __asm__ volatile("" : "+r"(checksum), "+r"(buffer) : "r"(base) : "memory");
    checksum ^= 0xffffff55u;
    __asm__ volatile("" : "+r"(checksum), "+r"(buffer) : "r"(base) : "memory");
    register uint32_t index __asm__("a1");
    __asm__ volatile("andi a1, s0, 255" : "=r"(index) : : "memory");
    __asm__ volatile("" : "+r"(index), "+r"(buffer), "+r"(checksum) : "r"(base) : "memory");
    buffer += 6;
    __asm__ volatile("" : "+r"(buffer), "+r"(index), "+r"(checksum) : "r"(base) : "memory");
    buffer += base;
    *(volatile uint16_t *)(uintptr_t)buffer = (uint16_t)checksum;
    *(volatile uint8_t *)(uintptr_t)(buffer + 4) = (uint8_t)index;
    __asm__ volatile("srli a4, s0, 8" : "=r"(checksum) : : "memory");
    __asm__ volatile("" : "+r"(checksum), "+r"(index), "+r"(buffer) : : "memory");
    __asm__ volatile("add a1, a1, s3" : "+r"(index) : : "memory");
    __asm__ volatile("" : "+r"(index), "+r"(checksum), "+r"(buffer) : : "memory");
    *(volatile uint8_t *)(uintptr_t)(buffer + 3) = (uint8_t)checksum;
    __asm__ volatile("" : "+r"(checksum), "+r"(index), "+r"(buffer) : : "memory");
    checksum += index;
    __asm__ volatile("" : "+r"(checksum), "+r"(index), "+r"(buffer) : : "memory");
    __asm__ volatile("sb s3, 2(a5)" : "+r"(checksum), "+r"(index), "+r"(buffer) : : "memory");
    checksum &= 255u;
    __asm__ volatile("" : "+r"(checksum), "+r"(index), "+r"(buffer) : : "memory");
    index = 0;
    __asm__ volatile("" : : "r"(index), "r"(buffer), "r"(checksum), "r"(bank), "r"(base) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_transport_test_8b0a(void)
{
    register uint32_t index __asm__("a1");
    __asm__ volatile("" : "=r"(index) : : "memory");
    register uint32_t narrowed __asm__("a0") = index << 16;
    __asm__ volatile("" : "+r"(narrowed) : "r"(index) : "memory");
    narrowed >>= 16;
    __asm__ volatile(".Ltransport_copy_more:\nbltu a0, s0, .Ltransport_copy_more\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_transport_copy_8b52\n"
                     : : "r"(narrowed), "r"(index) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_transport_finish_8b14(void)
{
    register uint32_t buffer __asm__("a5");
    register uint32_t checksum __asm__("a4");
    register uint32_t bank __asm__("a2");
    register uint32_t base __asm__("a3");
    __asm__ volatile("" : "=r"(buffer), "=r"(checksum), "=r"(bank), "=r"(base) : : "memory");
    __asm__ volatile("add a5, a5, s0" : "+r"(buffer) : : "memory");
    *(volatile uint8_t *)(uintptr_t)(buffer + 5) = (uint8_t)checksum;
    buffer = 1062;
    __asm__ volatile("" : "+r"(buffer), "+r"(bank) : : "memory");
    buffer = bank * buffer;
    __asm__ volatile("addi s0, s0, 6" : "+r"(buffer), "+r"(bank) : : "memory");
    bank <<= 2;
    __asm__ volatile("lw ra, 28(sp)\nlw s1, 20(sp)\nlw s2, 16(sp)\nlw s3, 12(sp)\n"
                     : "+r"(bank), "+r"(buffer) : : "memory");
    register uint32_t one __asm__("a1") = 1;
    __asm__ volatile("" : "+r"(one), "+r"(buffer) : : "memory");
    buffer += base;
    __asm__ volatile("sh s0, 2(a5)" : : "r"(buffer) : "memory");
    *(volatile uint16_t *)(uintptr_t)(buffer + 4) = 0;
    __asm__ volatile("addi a5, gp, 148\n" : "=r"(buffer) : "r"(bank), "r"(one) : "memory");
    bank += buffer;
    __asm__ volatile("lw s0, 24(sp)\nlui a5, 0x40\nlw t1, 80(a5)\n"
                     : "+r"(bank), "=r"(buffer) : "r"(one) : "memory");
    register uint32_t selected __asm__("a0") = *(volatile uint8_t *)(uintptr_t)bank;
    __asm__ volatile("addi sp, sp, 32\njr t1\n"
                     : : "r"(selected), "r"(bank), "r"(one), "r"(buffer) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_transport_copy_8b52(void)
{
    register uint32_t index __asm__("a1");
    register uint32_t buffer __asm__("a5");
    register uint32_t checksum __asm__("a4");
    __asm__ volatile("" : "=r"(index), "=r"(buffer), "=r"(checksum) : : "memory");
    register uint32_t value __asm__("a0");
    __asm__ volatile("add a0, s1, a1" : "=r"(value) : "r"(index) : "memory");
    __asm__ volatile("" : "+r"(value) : "r"(index), "r"(buffer), "r"(checksum) : "memory");
    value = *(volatile uint8_t *)(uintptr_t)value;
    register uint32_t destination __asm__("a6") = buffer + index;
    __asm__ volatile("" : "+r"(destination), "+r"(value), "+r"(index) : "r"(buffer), "r"(checksum) : "memory");
    index += 1;
    __asm__ volatile("" : "+r"(index), "+r"(value), "+r"(checksum) : "r"(destination) : "memory");
    checksum += value;
    __asm__ volatile("" : "+r"(checksum), "+r"(value) : "r"(destination), "r"(index) : "memory");
    *(volatile uint8_t *)(uintptr_t)(destination + 5) = (uint8_t)value;
    checksum &= 255u;
    __asm__ volatile(".Ltransport_copy_test:\nc.j .Ltransport_copy_test\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_transport_test_8b0a\n"
                     : : "r"(checksum), "r"(index), "r"(value), "r"(destination) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_transport_bare_return_8b6c(void)
{
    __asm__ volatile("ret\n");
}
