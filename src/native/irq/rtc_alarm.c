#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; never execute on a host or device.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")
#define CALL(label,target) __asm__ volatile(label ":\n.option push\n.option norvc\njal ra," label "\n.option pop\n.reloc .-4,R_RISCV_JAL," #target : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")

/* Original19BD4..19BF0. No C interrupt ABI or hardware-created frame assumed.
 * Each assembly call port exposes then-live registers; no synthetic frame.
 */
REGION void tsl9_rtc_alarm_entry_19bd4(void)
{
    REGS;
    a5=1; LIVE;
    a0=0x20000; LIVE;
    __asm__ volatile("sw a5,392(gp)"::"r"(a5):"memory");
    CALL(".Lrtc_exti",tsl9_rtc_exti_write_18e86);
    a0=2; LIVE;
    CALL(".Lrtc_clear_alias",tsl9_rtc_clear_alias_19296);
    CALL(".Lrtc_wait",tsl9_rtc_wait_19272);
    __asm__ volatile("mret":::"memory");
    __builtin_unreachable();
}

/* Raw word write at40010414; matches a saved EXTI profile only. */
REGION void tsl9_rtc_exti_write_18e86(void)
{
    REGS;
    a5=0x40010000; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5+1044u)=a0; LIVE;
    __asm__ volatile("ret"::"r"(a0),"r"(a5):"memory");
    __builtin_unreachable();
}

/* Preserve the original unbounded status polling; static compilation only.
 * Neither termination nor the underlying peripheral state is established.
 */
REGION void tsl9_rtc_wait_19272(void)
{
    REGS;
    a4=0x40003000; LIVE;
    __asm__ volatile(".Lrtc_poll:");
    a5=*(volatile uint16_t *)(uintptr_t)(a4-2044u); LIVE;
    a5&=32u; LIVE;
    __asm__ volatile("c.beqz a5,.Lrtc_poll\nret"::"r"(a4),"r"(a5):"memory");
    __builtin_unreachable();
}

/* Original halfword read/complement-mask/halfword write at40002804.
 * A0 retains its original complemented-and-masked result on return.
 */
REGION void tsl9_rtc_clear_19282(void)
{
    REGS;
    a5=0x40003000; LIVE;
    a4=*(volatile uint16_t *)(uintptr_t)(a5-2044u); LIVE;
    a0=~a0; LIVE;
    a0&=a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5-2044u)=(uint16_t)a0; LIVE;
    __asm__ volatile("ret"::"r"(a0),"r"(a4),"r"(a5):"memory");
    __builtin_unreachable();
}

/* A genuine4-byte no-link tail jump, not a new call/return wrapper. */
REGION void tsl9_rtc_clear_alias_19296(void)
{
    REGS;
    __asm__ volatile(".Lrtc_tail:\n.option push\n.option norvc\njal zero,.Lrtc_tail\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rtc_clear_19282":::"memory");
    __builtin_unreachable();
}
