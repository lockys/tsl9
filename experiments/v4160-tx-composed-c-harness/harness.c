/* Host-only concrete tests of the adjacent abstract candidate. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "../v4160-tx-composed-ram-c/candidate.c"

enum { SIZE = 135536, BASE_INDEX = 100, D0 = 106, D1 = 1168 };
#define ORIGIN UINT32_C(0x2000b128)
static unsigned char ram[SIZE], expected[SIZE];
static int failures;

static void check_u32(const char *test, const char *field, uint32_t got, uint32_t want)
{
    if (got != want) {
        fprintf(stderr, "%s: %s got %lu expected %lu\n", test, field,
                (unsigned long)got, (unsigned long)want);
        ++failures;
    }
}

static void check_result(const char *test, struct tx_composed_result r,
                         struct tx_composed_result e)
{
#define CHECK(field) check_u32(test, #field, r.field, e.field)
    CHECK(a0); CHECK(a1); CHECK(a2); CHECK(a3); CHECK(a4);
    CHECK(a5); CHECK(a6); CHECK(s0); CHECK(s1); CHECK(s3);
#undef CHECK
}

static void reset(void)
{
    memset(ram, 0xa5, sizeof ram);
    memset(expected, 0xa5, sizeof expected);
}

static void header(unsigned d, unsigned char command, unsigned char hi, unsigned char lo)
{
    expected[d] = 0x55; expected[d+1] = 0x7f; expected[d+2] = command;
    expected[d+3] = hi; expected[d+4] = lo;
}

static void check_memory(const char *test)
{
    size_t i;
    for (i = 0; i < sizeof ram; ++i) {
        if (ram[i] != expected[i]) {
            fprintf(stderr, "%s: RAM[%lu] got %u expected %u\n", test,
                    (unsigned long)i, (unsigned)ram[i], (unsigned)expected[i]);
            ++failures;
            return;
        }
    }
}

static void zero_cases(void)
{
    struct tx_composed_result r;
    reset(); header(D0, 0x34, 0, 0);
    r = tx_composed(ram, ORIGIN, BASE_INDEX, 20, 0, 0, 0x1234, 0xdeadbeef);
    check_result("zero bank0", r, (struct tx_composed_result){
        0, 0, 0, 0x2000b18c, 0x34, 0x2000b192, 0xdeadbeef,
        0, 0x2000b13c, 0x1234 });
    check_memory("zero bank0");

    reset(); header(D1, 0xcd, 0, 0);
    r = tx_composed(ram, ORIGIN, BASE_INDEX, 20, 1, 0, 0xabcd, 0x76543210);
    check_result("zero bank1", r, (struct tx_composed_result){
        0, 0, 1, 0x2000b18c, 0xcd, 0x2000b5b8, 0x76543210,
        0, 0x2000b13c, 0xabcd });
    check_memory("zero bank1");
}

static void header_alias(void)
{
    static const unsigned char payload[] = {0x55, 0x7f, 0x23, 0, 5};
    struct tx_composed_result r;
    reset(); header(D0, 0x23, 0, 5);
    memcpy(expected + D0 + 5, payload, sizeof payload);
    r = tx_composed(ram, ORIGIN, BASE_INDEX, D0, 0, 5, 0x123, 7);
    check_result("header alias", r, (struct tx_composed_result){
        5, 5, 0, 0x2000b18c, 0x24, 0x2000b192, 0x2000b196,
        5, 0x2000b192, 0x123 });
    check_memory("header alias");
}

static void forward_overlap(void)
{
    struct tx_composed_result r;
    unsigned i;
    reset(); header(D0, 0x42, 0, 6);
    /* Source 110 becomes the length byte (6); each write feeds the next read. */
    for (i = 0; i < 6; ++i) expected[111 + i] = 6;
    r = tx_composed(ram, ORIGIN, BASE_INDEX, 110, 0, 6, 0x42, 7);
    check_result("forward overlap", r, (struct tx_composed_result){
        6, 6, 0, 0x2000b18c, 0x6c, 0x2000b192, 0x2000b197,
        6, 0x2000b196, 0x42 });
    check_memory("forward overlap");
}

static void nonoverlap(void)
{
    static const unsigned char payload[] = {1, 2, 0xfe, 0xff};
    struct tx_composed_result r;
    reset(); memcpy(ram + 300, payload, sizeof payload);
    memcpy(expected + 300, payload, sizeof payload);
    header(D0, 2, 0, 4); memcpy(expected + 111, payload, sizeof payload);
    r = tx_composed(ram, ORIGIN, BASE_INDEX, 300, 0, 4, 0x102, 7);
    check_result("nonoverlap", r, (struct tx_composed_result){
        4, 4, 0, 0x2000b18c, 6, 0x2000b192, 0x2000b195,
        4, 0x2000b254, 0x102 });
    check_memory("nonoverlap");
}

static void maximum(void)
{
    struct tx_composed_result r;
    reset();
    memset(ram + 70000, 1, 65535); memset(expected + 70000, 1, 65535);
    header(D0, 0x23, 0xff, 0xff); memset(expected + 111, 1, 65535);
    /* Explicit sentinels immediately outside the complete destination region. */
    ram[105] = expected[105] = 0x3c;
    ram[65646] = expected[65646] = 0xc3;
    r = tx_composed(ram, ORIGIN, BASE_INDEX, 70000, 0, 65535, 0x123, 7);
    check_result("maximum", r, (struct tx_composed_result){
        65535, 65535, 0, 0x2000b18c, 0x20, 0x2000b192, 0x2001b190,
        65535, 0x2001c298, 0x123 });
    check_u32("maximum", "leading sentinel", ram[105], 0x3c);
    check_u32("maximum", "trailing sentinel", ram[65646], 0xc3);
    check_memory("maximum");
}

int main(void)
{
    zero_cases(); header_alias(); forward_overlap(); nonoverlap(); maximum();
    if (failures) {
        fprintf(stderr, "%d checks failed\n", failures);
        return 1;
    }
    puts("all concrete host cases passed");
    return 0;
}
