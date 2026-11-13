#ifndef C364_CANDIDATE_H
#define C364_CANDIDATE_H
#include <stdint.h>

/* Host address-space model; these are not native firmware pointers or an ABI. */
#define C364_BF10 UINT32_C(0x2000bf10)
#define C364_BF13 UINT32_C(0x2000bf13)
#define C364_INITIAL_S0 UINT32_C(0x2000befc)

typedef struct {
    void *ctx;
    uint8_t (*read8)(void *ctx, uint32_t address);
    void (*write8)(void *ctx, uint32_t address, uint8_t value);
    /* A callback may alter memory and the modeled s0 before returning. */
    void (*call)(void *ctx, uint32_t target, uint32_t a0, uint32_t *s0);
} c364_bus;

void c364_candidate(const c364_bus *bus, uint32_t entry_value);
#endif
