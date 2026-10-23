#include <stdint.h>
__attribute__((used,noinline,noreturn,aligned(2))) void read_register_probe(void)
{
    register uint32_t a5 __asm__("a5")=*(volatile uint16_t *)(uintptr_t)__builtin_read_register("s0");
    __asm__ volatile("" : "+r"(a5) : : "memory");
    __builtin_unreachable();
}
