#ifndef TSL9_TARGET_IRQ_H
#define TSL9_TARGET_IRQ_H
#ifdef __cplusplus
extern "C" {
#endif
/* Fixed-target RV32 naked interrupt entry components, never normal C calls.
   Neither this header nor compiled objects establish a physical interrupt ABI.
   BB dispatches RAM[20000004]; LLE dispatches RAM[gp+384]. Their initialization
   and validity, gp20004000, original core/PFIC automatic context behavior and
   IRQ priority/nesting must be established before a final image is possible.
   LLE uses128B and saves29 registers at4..116; holes0/120/124 stay untouched.
   Do not insert generic interrupt attributes, C prologues or null guards.
   These entry functions finish with mret and must never be host-executed. */
#if defined(__riscv) && __riscv_xlen == 32
void tsl9_ble_bb_irq(void) __attribute__((noreturn));
void tsl9_ble_lle_irq(void) __attribute__((noreturn));
#endif
#ifdef __cplusplus
}
#endif
#endif
