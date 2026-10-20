#ifndef TSL9_STARTUP_CLOCK_H
#define TSL9_STARTUP_CLOCK_H
#include "dnd_actions.h"
#define SC_API_VERSION 1
#define SC_CONTROL UINT32_C(0x40021000)
#define SC_CONFIG UINT32_C(0x40021004)
#define SC_INTERRUPT UINT32_C(0x40021008)
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 void *context;
 da_flow (*read)(void *,uint32_t,unsigned,uint32_t,uint32_t,da_scalar *);
 da_flow (*write)(void *,uint32_t,uint32_t,unsigned,uint32_t,uint32_t);
} sc_backend;
typedef struct {
 const sc_backend *io;da_flow flow;
 uint32_t boundary_va,boundary_address,needed_mask,reads,writes,hse_iterations,hse_ready;
} sc_machine;
/* Complete fixed Runtime1849E..18588 SystemInit, no ROM calls or heap.
   Register names are conveniences; addresses/masks/order follow original bytes.
   Local loop/status objects have no fake target stack address. Every MMIO read
   is fresh. The first loop stops on bit17 or4096 iterations, then re-reads bit17.
   PLL and switch waits have no native timeout. Bound host providers explicitly
   to stop unready synthetic streams; never add an invented native return.
   RETURNED means this component returned, not proof of measured clock speed.
   Backend and machine stable/non-reentrant; TRANSFER sticky. */
void sc_init(sc_machine *,const sc_backend *);
da_flow sc_run(sc_machine *);
#if defined(__riscv) && __riscv_xlen == 32
/* Actual RV32-only volatile MMIO C core with a naked48-byte aligned shim.
   On normal return it preserves a0/a1/a6/a7/t0..t6/ra and restores original
   incidental a2=20000,a3=40021000,a4/a5=(0,1) for HSE failure or(8,8) after
   successful switch. C ABI preserves s-registers/gp/tp. It adds stack/calls;
   IRQ timing and whole-stack compatibility remain unverified. Never host-run.
   Literal fixed-target accesses; no claim of exact board/resident-ROM match. */
void sc_native_init(void);
#endif
#ifdef __cplusplus
}
#endif
#endif
