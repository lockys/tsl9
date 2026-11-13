/* Host-only examples for the two F030 C hypotheses, not a target emulator. */
#include <limits.h>
#include <stdio.h>

#if CHAR_BIT != 8
#error This bounded harness requires 8-bit bytes
#endif

#define tsl9_record_helpers_block_f030 adapter_f030
#include "../v4160-f030-purec-real-bd46-next/candidate.c"
#undef tsl9_record_helpers_block_f030
#define tsl9_record_helpers_block_f030 leaf_f030
#include "../v4160-f030-purec-real-bd46-next/leaf.c"
#undef tsl9_record_helpers_block_f030

static volatile unsigned char *active;
static volatile unsigned char *backing;
static unsigned char expected;
static unsigned calls;
static unsigned bad;

/* An intentionally modifying host stub; this is not the real BD46 provider. */
void tsl9_record_helpers_provider_bd46(void)
{
    unsigned i;
    ++calls;
    for (i = 0; i < 24; ++i) {
        unsigned char want = i == 13 ? expected : 0xa5;
        if (backing[i] != want) ++bad;
    }
    active[10] = (unsigned char)(expected ^ 0xffU);
    active[13] = 0x5a;
}

static int check(unsigned value)
{
    volatile unsigned char memory[24];
    unsigned i;
    expected = (unsigned char)value;
    for (i = 0; i < 24; ++i) memory[i] = 0xa5;
    active = memory + 3;
    backing = memory;
    memory[13] = (unsigned char)(expected ^ 1U);
    calls = bad = 0;
    adapter_f030(active, value);
    if (calls != 1 || bad != 0) return 1;
    for (i = 0; i < 24; ++i) {
        unsigned char want = i == 13 ? (unsigned char)(expected ^ 0xffU)
                            : i == 16 ? 0x5a : 0xa5;
        if (memory[i] != want) return 2;
    }
    for (i = 0; i < 24; ++i) memory[i] = 0xa5;
    memory[13] = (unsigned char)(expected ^ 1U);
    calls = bad = 0;
    leaf_f030(active, value);
    if (calls != 0 || bad != 0) return 3;
    for (i = 0; i < 24; ++i) {
        unsigned char want = i == 13 ? expected : 0xa5;
        if (memory[i] != want) return 4;
    }
    return 0;
}

int main(void)
{
    unsigned i;
    for (i = 0; i < 256; ++i) {
        if (check(i) || check(i + 256U)) {
            fprintf(stderr, "FAIL value %u or %u\n", i, i + 256U);
            return 1;
        }
    }
    if (check(UINT_MAX)) {
        fprintf(stderr, "FAIL UINT_MAX\n");
        return 1;
    }
    puts("PASS 513 values: stub-time and final array snapshots match");
    return 0;
}
