#include "target_vectors.h"
#include "target_irq.h"
#include "target_reset.h"
#include "target_events.h"
#include "target_peripherals.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "Target vector entries require RV32"
#endif
#ifdef __cplusplus
static_assert(sizeof(tsl9_vector_handler) == 4, "RV32 vector pointer width");
#else
_Static_assert(sizeof(tsl9_vector_handler) == 4, "RV32 vector pointer width");
#endif
/* All observed nonzero vector targets now name actual native functions.
 * This does not establish physical IRQ entry ABI or final image placement. */
/* Original image entry 0x8000 is a four-byte JAL x0 to the reset entry.
 * The final linker must still establish the image and vector addresses. */
__attribute__((naked, noreturn, used, section(".text.tsl9_image_entry")))
void tsl9_image_entry(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option norvc\n"
        "j tsl9_reset_entry\n.option pop\n");
}
/* One symbol per confirmed original default handler; no inferred IRQ names. */
static void default_1838c(void) __asm__("tsl9_default_irq_1838c");
__attribute__((naked, used, section(".text.tsl9_default_irq_1838c")))
static void default_1838c(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_1838e(void) __asm__("tsl9_default_irq_1838e");
__attribute__((naked, used, section(".text.tsl9_default_irq_1838e")))
static void default_1838e(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_18390(void) __asm__("tsl9_default_irq_18390");
__attribute__((naked, used, section(".text.tsl9_default_irq_18390")))
static void default_18390(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_18392(void) __asm__("tsl9_default_irq_18392");
__attribute__((naked, used, section(".text.tsl9_default_irq_18392")))
static void default_18392(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_18394(void) __asm__("tsl9_default_irq_18394");
__attribute__((naked, used, section(".text.tsl9_default_irq_18394")))
static void default_18394(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_18396(void) __asm__("tsl9_default_irq_18396");
__attribute__((naked, used, section(".text.tsl9_default_irq_18396")))
static void default_18396(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_18398(void) __asm__("tsl9_default_irq_18398");
__attribute__((naked, used, section(".text.tsl9_default_irq_18398")))
static void default_18398(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_1839a(void) __asm__("tsl9_default_irq_1839a");
__attribute__((naked, used, section(".text.tsl9_default_irq_1839a")))
static void default_1839a(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_1839c(void) __asm__("tsl9_default_irq_1839c");
__attribute__((naked, used, section(".text.tsl9_default_irq_1839c")))
static void default_1839c(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_1839e(void) __asm__("tsl9_default_irq_1839e");
__attribute__((naked, used, section(".text.tsl9_default_irq_1839e")))
static void default_1839e(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183a0(void) __asm__("tsl9_default_irq_183a0");
__attribute__((naked, used, section(".text.tsl9_default_irq_183a0")))
static void default_183a0(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183a2(void) __asm__("tsl9_default_irq_183a2");
__attribute__((naked, used, section(".text.tsl9_default_irq_183a2")))
static void default_183a2(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183a4(void) __asm__("tsl9_default_irq_183a4");
__attribute__((naked, used, section(".text.tsl9_default_irq_183a4")))
static void default_183a4(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183a6(void) __asm__("tsl9_default_irq_183a6");
__attribute__((naked, used, section(".text.tsl9_default_irq_183a6")))
static void default_183a6(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183a8(void) __asm__("tsl9_default_irq_183a8");
__attribute__((naked, used, section(".text.tsl9_default_irq_183a8")))
static void default_183a8(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183aa(void) __asm__("tsl9_default_irq_183aa");
__attribute__((naked, used, section(".text.tsl9_default_irq_183aa")))
static void default_183aa(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183ac(void) __asm__("tsl9_default_irq_183ac");
__attribute__((naked, used, section(".text.tsl9_default_irq_183ac")))
static void default_183ac(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183ae(void) __asm__("tsl9_default_irq_183ae");
__attribute__((naked, used, section(".text.tsl9_default_irq_183ae")))
static void default_183ae(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183b0(void) __asm__("tsl9_default_irq_183b0");
__attribute__((naked, used, section(".text.tsl9_default_irq_183b0")))
static void default_183b0(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183b2(void) __asm__("tsl9_default_irq_183b2");
__attribute__((naked, used, section(".text.tsl9_default_irq_183b2")))
static void default_183b2(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183b4(void) __asm__("tsl9_default_irq_183b4");
__attribute__((naked, used, section(".text.tsl9_default_irq_183b4")))
static void default_183b4(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183b6(void) __asm__("tsl9_default_irq_183b6");
__attribute__((naked, used, section(".text.tsl9_default_irq_183b6")))
static void default_183b6(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183b8(void) __asm__("tsl9_default_irq_183b8");
__attribute__((naked, used, section(".text.tsl9_default_irq_183b8")))
static void default_183b8(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183bc(void) __asm__("tsl9_default_irq_183bc");
__attribute__((naked, used, section(".text.tsl9_default_irq_183bc")))
static void default_183bc(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183be(void) __asm__("tsl9_default_irq_183be");
__attribute__((naked, used, section(".text.tsl9_default_irq_183be")))
static void default_183be(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183c2(void) __asm__("tsl9_default_irq_183c2");
__attribute__((naked, used, section(".text.tsl9_default_irq_183c2")))
static void default_183c2(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183c4(void) __asm__("tsl9_default_irq_183c4");
__attribute__((naked, used, section(".text.tsl9_default_irq_183c4")))
static void default_183c4(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183c6(void) __asm__("tsl9_default_irq_183c6");
__attribute__((naked, used, section(".text.tsl9_default_irq_183c6")))
static void default_183c6(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183c8(void) __asm__("tsl9_default_irq_183c8");
__attribute__((naked, used, section(".text.tsl9_default_irq_183c8")))
static void default_183c8(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183ca(void) __asm__("tsl9_default_irq_183ca");
__attribute__((naked, used, section(".text.tsl9_default_irq_183ca")))
static void default_183ca(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183ce(void) __asm__("tsl9_default_irq_183ce");
__attribute__((naked, used, section(".text.tsl9_default_irq_183ce")))
static void default_183ce(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183d0(void) __asm__("tsl9_default_irq_183d0");
__attribute__((naked, used, section(".text.tsl9_default_irq_183d0")))
static void default_183d0(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183d2(void) __asm__("tsl9_default_irq_183d2");
__attribute__((naked, used, section(".text.tsl9_default_irq_183d2")))
static void default_183d2(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183d4(void) __asm__("tsl9_default_irq_183d4");
__attribute__((naked, used, section(".text.tsl9_default_irq_183d4")))
static void default_183d4(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183d6(void) __asm__("tsl9_default_irq_183d6");
__attribute__((naked, used, section(".text.tsl9_default_irq_183d6")))
static void default_183d6(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183d8(void) __asm__("tsl9_default_irq_183d8");
__attribute__((naked, used, section(".text.tsl9_default_irq_183d8")))
static void default_183d8(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183da(void) __asm__("tsl9_default_irq_183da");
__attribute__((naked, used, section(".text.tsl9_default_irq_183da")))
static void default_183da(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183dc(void) __asm__("tsl9_default_irq_183dc");
__attribute__((naked, used, section(".text.tsl9_default_irq_183dc")))
static void default_183dc(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183de(void) __asm__("tsl9_default_irq_183de");
__attribute__((naked, used, section(".text.tsl9_default_irq_183de")))
static void default_183de(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183e0(void) __asm__("tsl9_default_irq_183e0");
__attribute__((naked, used, section(".text.tsl9_default_irq_183e0")))
static void default_183e0(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183e2(void) __asm__("tsl9_default_irq_183e2");
__attribute__((naked, used, section(".text.tsl9_default_irq_183e2")))
static void default_183e2(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183e6(void) __asm__("tsl9_default_irq_183e6");
__attribute__((naked, used, section(".text.tsl9_default_irq_183e6")))
static void default_183e6(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183e8(void) __asm__("tsl9_default_irq_183e8");
__attribute__((naked, used, section(".text.tsl9_default_irq_183e8")))
static void default_183e8(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183ea(void) __asm__("tsl9_default_irq_183ea");
__attribute__((naked, used, section(".text.tsl9_default_irq_183ea")))
static void default_183ea(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183ec(void) __asm__("tsl9_default_irq_183ec");
__attribute__((naked, used, section(".text.tsl9_default_irq_183ec")))
static void default_183ec(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183ee(void) __asm__("tsl9_default_irq_183ee");
__attribute__((naked, used, section(".text.tsl9_default_irq_183ee")))
static void default_183ee(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183f4(void) __asm__("tsl9_default_irq_183f4");
__attribute__((naked, used, section(".text.tsl9_default_irq_183f4")))
static void default_183f4(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183f6(void) __asm__("tsl9_default_irq_183f6");
__attribute__((naked, used, section(".text.tsl9_default_irq_183f6")))
static void default_183f6(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183f8(void) __asm__("tsl9_default_irq_183f8");
__attribute__((naked, used, section(".text.tsl9_default_irq_183f8")))
static void default_183f8(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183fa(void) __asm__("tsl9_default_irq_183fa");
__attribute__((naked, used, section(".text.tsl9_default_irq_183fa")))
static void default_183fa(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_183fc(void) __asm__("tsl9_default_irq_183fc");
__attribute__((naked, used, section(".text.tsl9_default_irq_183fc")))
static void default_183fc(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
static void default_1848c(void) __asm__("tsl9_default_irq_1848c");
__attribute__((naked, used, section(".text.tsl9_default_irq_1848c")))
static void default_1848c(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\nmret\n.option pop\n");
}
static void default_18490(void) __asm__("tsl9_default_irq_18490");
__attribute__((naked, used, section(".text.tsl9_default_irq_18490")))
static void default_18490(void) {
    __asm__ volatile(".option push\n.option norelax\n.option rvc\n1: j 1b\n.option pop\n");
}
/* Pointer relocations, not the old image's absolute addresses.
 * Slots 70..81 are observed trailing zeros; reserved IRQ semantics unproved. */
__attribute__((used, section(".tsl9_vectors"), aligned(4)))
tsl9_vector_handler const __tsl9_vector_table[TSL9_OBSERVED_VECTOR_WORDS] = {
    tsl9_image_entry, /* word 0, original 0x8038 -> 0x8000 */
    0, /* word 1, original 0x803c -> 0x0 */
    default_1848c, /* word 2, original 0x8040 -> 0x1848c */
    default_18490, /* word 3, original 0x8044 -> 0x18490 */
    0, /* word 4, original 0x8048 -> 0x0 */
    tsl9_context_restore_irq, /* word 5, original 0x804c -> 0x8440 */
    0, /* word 6, original 0x8050 -> 0x0 */
    0, /* word 7, original 0x8054 -> 0x0 */
    tsl9_context_restore_irq, /* word 8, original 0x8058 -> 0x8440 */
    default_1838c, /* word 9, original 0x805c -> 0x1838c */
    0, /* word 10, original 0x8060 -> 0x0 */
    0, /* word 11, original 0x8064 -> 0x0 */
    default_1838e, /* word 12, original 0x8068 -> 0x1838e */
    0, /* word 13, original 0x806c -> 0x0 */
    default_18390, /* word 14, original 0x8070 -> 0x18390 */
    0, /* word 15, original 0x8074 -> 0x0 */
    default_18392, /* word 16, original 0x8078 -> 0x18392 */
    default_18394, /* word 17, original 0x807c -> 0x18394 */
    default_18396, /* word 18, original 0x8080 -> 0x18396 */
    default_18398, /* word 19, original 0x8084 -> 0x18398 */
    default_1839a, /* word 20, original 0x8088 -> 0x1839a */
    default_1839c, /* word 21, original 0x808c -> 0x1839c */
    default_1839e, /* word 22, original 0x8090 -> 0x1839e */
    default_183a0, /* word 23, original 0x8094 -> 0x183a0 */
    default_183a2, /* word 24, original 0x8098 -> 0x183a2 */
    default_183a4, /* word 25, original 0x809c -> 0x183a4 */
    default_183a6, /* word 26, original 0x80a0 -> 0x183a6 */
    default_183a8, /* word 27, original 0x80a4 -> 0x183a8 */
    default_183aa, /* word 28, original 0x80a8 -> 0x183aa */
    default_183ac, /* word 29, original 0x80ac -> 0x183ac */
    default_183ae, /* word 30, original 0x80b0 -> 0x183ae */
    default_183b0, /* word 31, original 0x80b4 -> 0x183b0 */
    default_183b2, /* word 32, original 0x80b8 -> 0x183b2 */
    default_183b4, /* word 33, original 0x80bc -> 0x183b4 */
    default_183b6, /* word 34, original 0x80c0 -> 0x183b6 */
    default_183b8, /* word 35, original 0x80c4 -> 0x183b8 */
    tsl9_can_rx0_irq, /* word 36, original 0x80c8 -> 0x12a34 */
    default_183bc, /* word 37, original 0x80cc -> 0x183bc */
    default_183be, /* word 38, original 0x80d0 -> 0x183be */
    tsl9_exti_5_9_irq, /* word 39, original 0x80d4 -> 0x16d22 */
    default_183c2, /* word 40, original 0x80d8 -> 0x183c2 */
    default_183c4, /* word 41, original 0x80dc -> 0x183c4 */
    default_183c6, /* word 42, original 0x80e0 -> 0x183c6 */
    default_183c8, /* word 43, original 0x80e4 -> 0x183c8 */
    default_183ca, /* word 44, original 0x80e8 -> 0x183ca */
    tsl9_timer3_irq, /* word 45, original 0x80ec -> 0x977c */
    default_183ce, /* word 46, original 0x80f0 -> 0x183ce */
    default_183d0, /* word 47, original 0x80f4 -> 0x183d0 */
    default_183d2, /* word 48, original 0x80f8 -> 0x183d2 */
    default_183d4, /* word 49, original 0x80fc -> 0x183d4 */
    default_183d6, /* word 50, original 0x8100 -> 0x183d6 */
    default_183d8, /* word 51, original 0x8104 -> 0x183d8 */
    default_183da, /* word 52, original 0x8108 -> 0x183da */
    default_183dc, /* word 53, original 0x810c -> 0x183dc */
    default_183de, /* word 54, original 0x8110 -> 0x183de */
    default_183e0, /* word 55, original 0x8114 -> 0x183e0 */
    default_183e2, /* word 56, original 0x8118 -> 0x183e2 */
    tsl9_rtc_alarm_irq, /* word 57, original 0x811c -> 0x19928 */
    default_183e6, /* word 58, original 0x8120 -> 0x183e6 */
    default_183e8, /* word 59, original 0x8124 -> 0x183e8 */
    default_183ea, /* word 60, original 0x8128 -> 0x183ea */
    default_183ec, /* word 61, original 0x812c -> 0x183ec */
    default_183ee, /* word 62, original 0x8130 -> 0x183ee */
    tsl9_ble_bb_irq, /* word 63, original 0x8134 -> 0x18492 */
    tsl9_ble_lle_irq, /* word 64, original 0x8138 -> 0x8490 */
    default_183f4, /* word 65, original 0x813c -> 0x183f4 */
    default_183f6, /* word 66, original 0x8140 -> 0x183f6 */
    default_183f8, /* word 67, original 0x8144 -> 0x183f8 */
    default_183fa, /* word 68, original 0x8148 -> 0x183fa */
    default_183fc, /* word 69, original 0x814c -> 0x183fc */
    0, /* word 70, original 0x8150 -> 0x0 */
    0, /* word 71, original 0x8154 -> 0x0 */
    0, /* word 72, original 0x8158 -> 0x0 */
    0, /* word 73, original 0x815c -> 0x0 */
    0, /* word 74, original 0x8160 -> 0x0 */
    0, /* word 75, original 0x8164 -> 0x0 */
    0, /* word 76, original 0x8168 -> 0x0 */
    0, /* word 77, original 0x816c -> 0x0 */
    0, /* word 78, original 0x8170 -> 0x0 */
    0, /* word 79, original 0x8174 -> 0x0 */
    0, /* word 80, original 0x8178 -> 0x0 */
    0, /* word 81, original 0x817c -> 0x0 */
};

