#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Offline RV32 architectural regions only; never run on a HOST or device.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define FRAME ENTRY __attribute__((used,naked,aligned(2)))
#define INPUT(x) __asm__ volatile("" : "=r"(x) : : "memory")

/* Complete original header/defaults/reset/IRQ ports/clock spans.
 * C owns free-bank arithmetic/constants and ordinary memory.
 * SP/GP/reserved-S/frame/PC/control effects remain explicit architecture ports.
 * Regions require original placement and adjacency, not independent C ABI.
 * Every opaque call ends a region; following regions resample live registers.
 * No installed ROM, time units, field identities, bounds or IRQ assumptions.
 * Static authoring only; native original-byte comparison is separate. */

/* Original0x8000-0x8004. */
FRAME void tsl9_boot_entry_8000(void)
{
    __asm__ volatile(".Levent_control_8000:\n.option push\n.option norvc\njal zero, .Levent_control_8000\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_reset_original_186aa\n");
}

/* Original0x8004-0x8038. */
FRAME void tsl9_boot_8004(void)
{
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nnop\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nebreak\n.option pop\n");
}

/* Original0x18630-0x18632. */
FRAME void tsl9_boot_18630(void)
{
    __asm__ volatile(".Levent_control_18630:\n.option push\n.option rvc\nc.j .Levent_control_18630\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18630\n");
}

/* Original0x18632-0x18634. */
FRAME void tsl9_boot_18632(void)
{
    __asm__ volatile(".Levent_control_18632:\n.option push\n.option rvc\nc.j .Levent_control_18632\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18632\n");
}

/* Original0x18634-0x18636. */
FRAME void tsl9_boot_18634(void)
{
    __asm__ volatile(".Levent_control_18634:\n.option push\n.option rvc\nc.j .Levent_control_18634\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18634\n");
}

/* Original0x18636-0x18638. */
FRAME void tsl9_boot_18636(void)
{
    __asm__ volatile(".Levent_control_18636:\n.option push\n.option rvc\nc.j .Levent_control_18636\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18636\n");
}

/* Original0x18638-0x1863A. */
FRAME void tsl9_boot_18638(void)
{
    __asm__ volatile(".Levent_control_18638:\n.option push\n.option rvc\nc.j .Levent_control_18638\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18638\n");
}

/* Original0x1863A-0x1863C. */
FRAME void tsl9_boot_1863a(void)
{
    __asm__ volatile(".Levent_control_1863a:\n.option push\n.option rvc\nc.j .Levent_control_1863a\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1863a\n");
}

/* Original0x1863C-0x1863E. */
FRAME void tsl9_boot_1863c(void)
{
    __asm__ volatile(".Levent_control_1863c:\n.option push\n.option rvc\nc.j .Levent_control_1863c\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1863c\n");
}

/* Original0x1863E-0x18640. */
FRAME void tsl9_boot_1863e(void)
{
    __asm__ volatile(".Levent_control_1863e:\n.option push\n.option rvc\nc.j .Levent_control_1863e\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1863e\n");
}

/* Original0x18640-0x18642. */
FRAME void tsl9_boot_18640(void)
{
    __asm__ volatile(".Levent_control_18640:\n.option push\n.option rvc\nc.j .Levent_control_18640\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18640\n");
}

/* Original0x18642-0x18644. */
FRAME void tsl9_boot_18642(void)
{
    __asm__ volatile(".Levent_control_18642:\n.option push\n.option rvc\nc.j .Levent_control_18642\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18642\n");
}

/* Original0x18644-0x18646. */
FRAME void tsl9_boot_18644(void)
{
    __asm__ volatile(".Levent_control_18644:\n.option push\n.option rvc\nc.j .Levent_control_18644\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18644\n");
}

/* Original0x18646-0x18648. */
FRAME void tsl9_boot_18646(void)
{
    __asm__ volatile(".Levent_control_18646:\n.option push\n.option rvc\nc.j .Levent_control_18646\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18646\n");
}

/* Original0x18648-0x1864A. */
FRAME void tsl9_boot_18648(void)
{
    __asm__ volatile(".Levent_control_18648:\n.option push\n.option rvc\nc.j .Levent_control_18648\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18648\n");
}

/* Original0x1864A-0x1864C. */
FRAME void tsl9_boot_1864a(void)
{
    __asm__ volatile(".Levent_control_1864a:\n.option push\n.option rvc\nc.j .Levent_control_1864a\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1864a\n");
}

/* Original0x1864C-0x1864E. */
FRAME void tsl9_boot_1864c(void)
{
    __asm__ volatile(".Levent_control_1864c:\n.option push\n.option rvc\nc.j .Levent_control_1864c\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1864c\n");
}

/* Original0x1864E-0x18650. */
FRAME void tsl9_boot_1864e(void)
{
    __asm__ volatile(".Levent_control_1864e:\n.option push\n.option rvc\nc.j .Levent_control_1864e\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1864e\n");
}

/* Original0x18650-0x18652. */
FRAME void tsl9_boot_18650(void)
{
    __asm__ volatile(".Levent_control_18650:\n.option push\n.option rvc\nc.j .Levent_control_18650\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18650\n");
}

/* Original0x18652-0x18654. */
FRAME void tsl9_boot_18652(void)
{
    __asm__ volatile(".Levent_control_18652:\n.option push\n.option rvc\nc.j .Levent_control_18652\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18652\n");
}

/* Original0x18654-0x18656. */
FRAME void tsl9_boot_18654(void)
{
    __asm__ volatile(".Levent_control_18654:\n.option push\n.option rvc\nc.j .Levent_control_18654\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18654\n");
}

/* Original0x18656-0x18658. */
FRAME void tsl9_boot_18656(void)
{
    __asm__ volatile(".Levent_control_18656:\n.option push\n.option rvc\nc.j .Levent_control_18656\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18656\n");
}

/* Original0x18658-0x1865A. */
FRAME void tsl9_boot_18658(void)
{
    __asm__ volatile(".Levent_control_18658:\n.option push\n.option rvc\nc.j .Levent_control_18658\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18658\n");
}

/* Original0x1865A-0x1865C. */
FRAME void tsl9_boot_1865a(void)
{
    __asm__ volatile(".Levent_control_1865a:\n.option push\n.option rvc\nc.j .Levent_control_1865a\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1865a\n");
}

/* Original0x1865C-0x1865E. */
FRAME void tsl9_boot_1865c(void)
{
    __asm__ volatile(".Levent_control_1865c:\n.option push\n.option rvc\nc.j .Levent_control_1865c\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1865c\n");
}

/* Original0x1865E-0x18660. */
FRAME void tsl9_boot_1865e(void)
{
    __asm__ volatile(".Levent_control_1865e:\n.option push\n.option rvc\nc.j .Levent_control_1865e\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1865e\n");
}

/* Original0x18660-0x18662. */
FRAME void tsl9_boot_18660(void)
{
    __asm__ volatile(".Levent_control_18660:\n.option push\n.option rvc\nc.j .Levent_control_18660\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18660\n");
}

/* Original0x18662-0x18664. */
FRAME void tsl9_boot_18662(void)
{
    __asm__ volatile(".Levent_control_18662:\n.option push\n.option rvc\nc.j .Levent_control_18662\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18662\n");
}

/* Original0x18664-0x18666. */
FRAME void tsl9_boot_18664(void)
{
    __asm__ volatile(".Levent_control_18664:\n.option push\n.option rvc\nc.j .Levent_control_18664\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18664\n");
}

/* Original0x18666-0x18668. */
FRAME void tsl9_boot_18666(void)
{
    __asm__ volatile(".Levent_control_18666:\n.option push\n.option rvc\nc.j .Levent_control_18666\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18666\n");
}

/* Original0x18668-0x1866A. */
FRAME void tsl9_boot_18668(void)
{
    __asm__ volatile(".Levent_control_18668:\n.option push\n.option rvc\nc.j .Levent_control_18668\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18668\n");
}

/* Original0x1866A-0x1866C. */
FRAME void tsl9_boot_1866a(void)
{
    __asm__ volatile(".Levent_control_1866a:\n.option push\n.option rvc\nc.j .Levent_control_1866a\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1866a\n");
}

/* Original0x1866C-0x1866E. */
FRAME void tsl9_boot_1866c(void)
{
    __asm__ volatile(".Levent_control_1866c:\n.option push\n.option rvc\nc.j .Levent_control_1866c\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1866c\n");
}

/* Original0x1866E-0x18670. */
FRAME void tsl9_boot_1866e(void)
{
    __asm__ volatile(".Levent_control_1866e:\n.option push\n.option rvc\nc.j .Levent_control_1866e\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1866e\n");
}

/* Original0x18670-0x18672. */
FRAME void tsl9_boot_18670(void)
{
    __asm__ volatile(".Levent_control_18670:\n.option push\n.option rvc\nc.j .Levent_control_18670\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18670\n");
}

/* Original0x18672-0x18674. */
FRAME void tsl9_boot_18672(void)
{
    __asm__ volatile(".Levent_control_18672:\n.option push\n.option rvc\nc.j .Levent_control_18672\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18672\n");
}

/* Original0x18674-0x18676. */
FRAME void tsl9_boot_18674(void)
{
    __asm__ volatile(".Levent_control_18674:\n.option push\n.option rvc\nc.j .Levent_control_18674\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18674\n");
}

/* Original0x18676-0x18678. */
FRAME void tsl9_boot_18676(void)
{
    __asm__ volatile(".Levent_control_18676:\n.option push\n.option rvc\nc.j .Levent_control_18676\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18676\n");
}

/* Original0x18678-0x1867A. */
FRAME void tsl9_boot_18678(void)
{
    __asm__ volatile(".Levent_control_18678:\n.option push\n.option rvc\nc.j .Levent_control_18678\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18678\n");
}

/* Original0x1867A-0x1867C. */
FRAME void tsl9_boot_1867a(void)
{
    __asm__ volatile(".Levent_control_1867a:\n.option push\n.option rvc\nc.j .Levent_control_1867a\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1867a\n");
}

/* Original0x1867C-0x1867E. */
FRAME void tsl9_boot_1867c(void)
{
    __asm__ volatile(".Levent_control_1867c:\n.option push\n.option rvc\nc.j .Levent_control_1867c\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1867c\n");
}

/* Original0x1867E-0x18680. */
FRAME void tsl9_boot_1867e(void)
{
    __asm__ volatile(".Levent_control_1867e:\n.option push\n.option rvc\nc.j .Levent_control_1867e\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1867e\n");
}

/* Original0x18680-0x18682. */
FRAME void tsl9_boot_18680(void)
{
    __asm__ volatile(".Levent_control_18680:\n.option push\n.option rvc\nc.j .Levent_control_18680\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18680\n");
}

/* Original0x18682-0x18684. */
FRAME void tsl9_boot_18682(void)
{
    __asm__ volatile(".Levent_control_18682:\n.option push\n.option rvc\nc.j .Levent_control_18682\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18682\n");
}

/* Original0x18684-0x18686. */
FRAME void tsl9_boot_18684(void)
{
    __asm__ volatile(".Levent_control_18684:\n.option push\n.option rvc\nc.j .Levent_control_18684\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18684\n");
}

/* Original0x18686-0x18688. */
FRAME void tsl9_boot_18686(void)
{
    __asm__ volatile(".Levent_control_18686:\n.option push\n.option rvc\nc.j .Levent_control_18686\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18686\n");
}

/* Original0x18688-0x1868A. */
FRAME void tsl9_boot_18688(void)
{
    __asm__ volatile(".Levent_control_18688:\n.option push\n.option rvc\nc.j .Levent_control_18688\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18688\n");
}

/* Original0x1868A-0x1868C. */
FRAME void tsl9_boot_1868a(void)
{
    __asm__ volatile(".Levent_control_1868a:\n.option push\n.option rvc\nc.j .Levent_control_1868a\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1868a\n");
}

/* Original0x1868C-0x1868E. */
FRAME void tsl9_boot_1868c(void)
{
    __asm__ volatile(".Levent_control_1868c:\n.option push\n.option rvc\nc.j .Levent_control_1868c\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1868c\n");
}

/* Original0x1868E-0x18690. */
FRAME void tsl9_boot_1868e(void)
{
    __asm__ volatile(".Levent_control_1868e:\n.option push\n.option rvc\nc.j .Levent_control_1868e\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1868e\n");
}

/* Original0x18690-0x18692. */
FRAME void tsl9_boot_18690(void)
{
    __asm__ volatile(".Levent_control_18690:\n.option push\n.option rvc\nc.j .Levent_control_18690\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18690\n");
}

/* Original0x18692-0x18694. */
FRAME void tsl9_boot_18692(void)
{
    __asm__ volatile(".Levent_control_18692:\n.option push\n.option rvc\nc.j .Levent_control_18692\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18692\n");
}

/* Original0x18694-0x18696. */
FRAME void tsl9_boot_18694(void)
{
    __asm__ volatile(".Levent_control_18694:\n.option push\n.option rvc\nc.j .Levent_control_18694\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18694\n");
}

/* Original0x18696-0x18698. */
FRAME void tsl9_boot_18696(void)
{
    __asm__ volatile(".Levent_control_18696:\n.option push\n.option rvc\nc.j .Levent_control_18696\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18696\n");
}

/* Original0x18698-0x1869A. */
FRAME void tsl9_boot_18698(void)
{
    __asm__ volatile(".Levent_control_18698:\n.option push\n.option rvc\nc.j .Levent_control_18698\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_18698\n");
}

/* Original0x1869A-0x1869C. */
FRAME void tsl9_boot_1869a(void)
{
    __asm__ volatile(".Levent_control_1869a:\n.option push\n.option rvc\nc.j .Levent_control_1869a\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1869a\n");
}

/* Original0x1869C-0x1869E. */
FRAME void tsl9_boot_1869c(void)
{
    __asm__ volatile(".Levent_control_1869c:\n.option push\n.option rvc\nc.j .Levent_control_1869c\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1869c\n");
}

/* Original0x1869E-0x186A0. */
FRAME void tsl9_boot_1869e(void)
{
    __asm__ volatile(".Levent_control_1869e:\n.option push\n.option rvc\nc.j .Levent_control_1869e\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1869e\n");
}

/* Original0x186A0-0x186A2. */
FRAME void tsl9_boot_186a0(void)
{
    __asm__ volatile(".Levent_control_186a0:\n.option push\n.option rvc\nc.j .Levent_control_186a0\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_186a0\n");
}

/* Original0x186A2-0x186A4. */
FRAME void tsl9_boot_186a2(void)
{
    __asm__ volatile(".Levent_control_186a2:\n.option push\n.option rvc\nc.j .Levent_control_186a2\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_186a2\n");
}

/* Original0x186A4-0x186A6. */
FRAME void tsl9_boot_186a4(void)
{
    __asm__ volatile(".Levent_control_186a4:\n.option push\n.option rvc\nc.j .Levent_control_186a4\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_186a4\n");
}

/* Original0x186A6-0x186A8. */
FRAME void tsl9_boot_186a6(void)
{
    __asm__ volatile(".Levent_control_186a6:\n.option push\n.option rvc\nc.j .Levent_control_186a6\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_186a6\n");
}

/* Original0x186A8-0x186AA. */
FRAME void tsl9_boot_186a8(void)
{
    __asm__ volatile(".Levent_control_186a8:\n.option push\n.option rvc\nc.j .Levent_control_186a8\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_186a8\n");
}

/* Original0x186AA-0x186BA. */
FRAME void tsl9_reset_original_186aa(void)
{
    __asm__ volatile(".option push\n.option norvc\nauipc gp, 0x1ffec\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\naddi gp, gp, -1706\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nauipc sp, 0x1fff8\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\naddi sp, sp, -1714\n.option pop\n");
}

/* Original0x186BA-0x186C2. */
REGION void tsl9_boot_186ba(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    __asm__ volatile(".Levent_hi_186ba:\nauipc a0, 0\n.reloc .-4, R_RISCV_PCREL_HI20, tsl9_boot_initializer_1ab60\n" : "=r"(a0) :  : "memory");
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __asm__ volatile(".option push\n.option norvc\naddi a0, a0, 0\n.option pop\n.reloc .-4, R_RISCV_PCREL_LO12_I, .Levent_hi_186ba\n" : "+r"(a0) :  : "memory");
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __builtin_unreachable();
}

/* Original0x186C2-0x186CE. */
FRAME void tsl9_boot_186c2(void)
{
    __asm__ volatile(".option push\n.option norvc\nmv a1, gp\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\naddi a2, gp, 128\n.option pop\n");
    __asm__ volatile(".Levent_control_186ca:\n.option push\n.option norvc\nbleu a2, a1, .Levent_control_186ca\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_boot_186de\n");
}

/* Original0x186CE-0x186D6. */
FRAME void tsl9_boot_186ce(void)
{
    __asm__ volatile(".option push\n.option norvc\nlw t0, 0(a0)\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nsw t0, 0(a1)\n.option pop\n");
}

/* Original0x186D6-0x186DE. */
REGION void tsl9_boot_186d6(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    a0 = a0 + UINT32_C(0x4);
    __asm__ volatile("" : "+r"(a0), "+r"(a1) :  : "memory");
    a1 = a1 + UINT32_C(0x4);
    __asm__ volatile("" : "+r"(a0), "+r"(a1) :  : "memory");
    __asm__ volatile(".Levent_control_186da:\n.option push\n.option norvc\nbltu a1, a2, .Levent_control_186da\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_boot_186ce\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x186DE-0x186E2. */
FRAME void tsl9_boot_186de(void)
{
    __asm__ volatile(".option push\n.option norvc\naddi a0, gp, 128\n.option pop\n");
}

/* Original0x186E2-0x186EE. */
REGION void tsl9_boot_186e2(void)
{
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    __asm__ volatile("auipc a1, 0x1fff4\n" : "=r"(a1) :  : "memory");
    __asm__ volatile("" : "+r"(a1) :  : "memory");
    a1 = a1 + UINT32_C(0x276);
    __asm__ volatile("" : "+r"(a1) :  : "memory");
    __asm__ volatile(".Levent_control_186ea:\n.option push\n.option norvc\nbleu a1, a0, .Levent_control_186ea\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_boot_186f8\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x186EE-0x186F8. */
REGION void tsl9_boot_186ee(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0)) = (uint32_t)0u;
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    a0 = a0 + UINT32_C(0x4);
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __asm__ volatile(".Levent_control_186f4:\n.option push\n.option norvc\nbltu a0, a1, .Levent_control_186f4\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_boot_186ee\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x186F8-0x18724. */
FRAME void tsl9_boot_186f8(void)
{
    __asm__ volatile(".option push\n.option rvc\nli t0, 31\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\ncsrw 0xbc0, t0\n.option pop\n");
    __asm__ volatile(".option push\n.option rvc\nli t0, 3\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\ncsrw 0x804, t0\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\nlui t0, 0x2\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\naddi t0, t0, -1912\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\ncsrs mstatus, t0\n.option pop\n");
    __asm__ volatile(".Levent_hi_18710:\nauipc t0, 0\n.reloc .-4, R_RISCV_PCREL_HI20, tsl9_boot_vector_data_8038\n");
    __asm__ volatile(".option push\n.option norvc\naddi t0, t0, 0\n.option pop\n.reloc .-4, R_RISCV_PCREL_LO12_I, .Levent_hi_18710\n");
    __asm__ volatile(".option push\n.option norvc\nori t0, t0, 3\n.option pop\n");
    __asm__ volatile(".option push\n.option norvc\ncsrw mtvec, t0\n.option pop\n");
    __asm__ volatile(".Levent_control_18720:\n.option push\n.option norvc\njal ra, .Levent_control_18720\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_clock_original_1874a\n");
}

/* Original0x18724-0x18734. */
FRAME void tsl9_boot_18724(void)
{
    __asm__ volatile(".Levent_hi_18724:\nauipc t0, 0\n.reloc .-4, R_RISCV_PCREL_HI20, tsl9_boot_main_9008\n");
    __asm__ volatile(".option push\n.option norvc\naddi t0, t0, 0\n.option pop\n.reloc .-4, R_RISCV_PCREL_LO12_I, .Levent_hi_18724\n");
    __asm__ volatile(".option push\n.option norvc\ncsrw mepc, t0\n.option pop\n");
    __asm__ volatile(".Levent_control_18730:\n.option push\n.option norvc\njal zero, .Levent_control_18730\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_boot_resident_40000\n");
}

/* Original0x18734-0x18738. */
FRAME void tsl9_boot_18734(void)
{
    __asm__ volatile("mret\n");
}

/* Original0x18738-0x1873C. */
FRAME void tsl9_boot_18738(void)
{
    __asm__ volatile("mret\n");
}

/* Original0x1873C-0x1873E. */
FRAME void tsl9_boot_1873c(void)
{
    __asm__ volatile(".Levent_control_1873c:\n.option push\n.option rvc\nc.j .Levent_control_1873c\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_1873c\n");
}

/* Original0x1873E-0x18746. */
REGION void tsl9_boot_1873e(void)
{
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = UINT32_C(0x20000000);
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    __asm__ volatile("jalr a5\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x18746-0x1874A. */
FRAME void tsl9_boot_18746(void)
{
    __asm__ volatile("mret\n");
}

/* Original0x1874A-0x18754. */
REGION void tsl9_clock_original_1874a(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = UINT32_C(0x40021000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0xf8ff0000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x18754-0x18756. */
FRAME void tsl9_boot_18754(void)
{
    __asm__ volatile(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
}

/* Original0x18756-0x18790. */
REGION void tsl9_boot_18756(void)
{
    register uint32_t a2 __asm__("a2"); INPUT(a2);
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = a4 | UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a2 = UINT32_C(0x20000);
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 & a3;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0));
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0xfef70000);
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = a3 + UINT32_C(0xffffffff);
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 & a3;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0));
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0xfffc0000);
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = a3 + UINT32_C(0xffffffff);
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 & a3;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0xff810000);
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = a3 + UINT32_C(0xffffffff);
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 & a3;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = UINT32_C(0x9f0000);
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x8)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x18790-0x18794. */
FRAME void tsl9_boot_18790(void)
{
    __asm__ volatile(".option push\n.option rvc\nsw zero, 8(sp)\n.option pop\n");
    __asm__ volatile(".option push\n.option rvc\nsw zero, 12(sp)\n.option pop\n");
}

/* Original0x18794-0x187A2. */
REGION void tsl9_boot_18794(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0x10000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 | a3;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0x40021000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = UINT32_C(0x1000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x187A2-0x187A6. */
REGION void tsl9_boot_187a2(void)
{
    register uint32_t a2 __asm__("a2"); INPUT(a2);
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0));
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a5) :  : "memory");
    a5 = a5 & a2;
    __asm__ volatile("" : "+r"(a2), "+r"(a3), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x187A6-0x187AA. */
FRAME void tsl9_boot_187a6(void)
{
    __asm__ volatile(".option push\n.option rvc\nsw a5, 12(sp)\n.option pop\n");
    __asm__ volatile(".option push\n.option rvc\nlw a5, 8(sp)\n.option pop\n");
}

/* Original0x187AA-0x187AC. */
REGION void tsl9_boot_187aa(void)
{
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 + UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x187AC-0x187B2. */
FRAME void tsl9_boot_187ac(void)
{
    __asm__ volatile(".option push\n.option rvc\nsw a5, 8(sp)\n.option pop\n");
    __asm__ volatile(".option push\n.option rvc\nlw a5, 12(sp)\n.option pop\n");
    __asm__ volatile(".Levent_control_187b0:\n.option push\n.option rvc\nbnez a5, .Levent_control_187b0\n.option pop\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_boot_187b8\n");
}

/* Original0x187B2-0x187B8. */
FRAME void tsl9_boot_187b2(void)
{
    __asm__ volatile(".option push\n.option rvc\nlw a5, 8(sp)\n.option pop\n");
    __asm__ volatile(".Levent_control_187b4:\n.option push\n.option norvc\nbne a5, a4, .Levent_control_187b4\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_boot_187a2\n");
}

/* Original0x187B8-0x187C6. */
REGION void tsl9_boot_187b8(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = UINT32_C(0x40021000);
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a5 << 14u;
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_187c2:\n.option push\n.option norvc\nbgez a4, .Levent_control_187c2\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_boot_18830\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x187C6-0x187C8. */
REGION void tsl9_boot_187c6(void)
{
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x187C8-0x187CA. */
FRAME void tsl9_boot_187c8(void)
{
    __asm__ volatile(".option push\n.option rvc\nsw a5, 12(sp)\n.option pop\n");
}

/* Original0x187CA-0x187CC. */
FRAME void tsl9_boot_187ca(void)
{
    __asm__ volatile(".option push\n.option rvc\nlw a4, 12(sp)\n.option pop\n");
}

/* Original0x187CC-0x187D2. */
REGION void tsl9_boot_187cc(void)
{
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_187ce:\n.option push\n.option norvc\nbne a4, a5, .Levent_control_187ce\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_boot_1882c\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x187D2-0x18806. */
REGION void tsl9_boot_187d2(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = UINT32_C(0x40021000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0xffc10000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = a3 + UINT32_C(0xffffffff);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 | UINT32_C(0x400);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 & a3;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0x290000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 | a3;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0x1000000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 | a3;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x18806-0x18810. */
REGION void tsl9_boot_18806(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = a4 << 6u;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_1880c:\n.option push\n.option norvc\nbgez a3, .Levent_control_1880c\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_boot_18806\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x18810-0x18824. */
REGION void tsl9_boot_18810(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0x40021000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 & UINT32_C(0xfffffffc);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 | UINT32_C(0x2);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x4)) = (uint32_t)a4;
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = UINT32_C(0x8);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x18824-0x1882C. */
REGION void tsl9_boot_18824(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a3), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0xc);
    __asm__ volatile("" : "+r"(a3), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_18828:\n.option push\n.option norvc\nbne a5, a4, .Levent_control_18828\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_boot_18824\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x1882C-0x18830. */
FRAME void tsl9_boot_1882c(void)
{
    __asm__ volatile(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    __asm__ volatile("ret\n");
}

/* Original0x18830-0x18834. */
FRAME void tsl9_boot_18830(void)
{
    __asm__ volatile(".option push\n.option rvc\nsw zero, 12(sp)\n.option pop\n");
    __asm__ volatile(".Levent_control_18832:\n.option push\n.option rvc\nc.j .Levent_control_18832\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_boot_187ca\n");
}
