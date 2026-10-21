#include "memcmp_contract.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    mc_request trace[128]; unsigned count, fail_at;
    uint32_t mmio, base1, base2;
    unsigned char a[32], b[32];
} mock;
static unsigned checks;
#define CHECK(c) do { ++checks; if (!(c)) { \
    fprintf(stderr, "line %u: %s\n", (unsigned)__LINE__, #c); exit(1); \
} } while (0)
static int invoke(void *ctx, const mc_request *r, uint32_t *out)
{
    mock *v = (mock *)ctx;
    uint32_t offset;
    CHECK(v->count < 128);
    v->trace[v->count++] = *r;
    if (v->count == v->fail_at) return 0;
    if (r->kind == MC_READ32) {
        CHECK(r->address == UINT32_C(0x4002420c)); *out = v->mmio;
    } else if (r->kind == MC_WRITE32) {
        CHECK(r->address == UINT32_C(0x4002420c)); v->mmio = r->value;
    } else if (r->kind == MC_READ8) {
        if (r->pc == UINT32_C(0x20000474)) {
            offset = r->address - v->base1; CHECK(offset < 32); *out = v->a[offset];
        } else {
            CHECK(r->pc == UINT32_C(0x20000478));
            offset = r->address - v->base2; CHECK(offset < 32); *out = v->b[offset];
        }
    } else CHECK(r->kind == MC_FENCE_I);
    return 1;
}
static void prepare(mock *v, mc_model *m, unsigned profile)
{
    mc_backend backend;
    memset(v, 0, sizeof(*v));
    v->mmio = UINT32_C(0xfedcba98); v->base1 = 0x1000; v->base2 = 0x2000;
    backend.context = v; backend.invoke = invoke;
    mc_init(m, &backend, profile);
}
static void prefix(const mock *v)
{
    CHECK(v->trace[0].kind == MC_READ32 && v->trace[0].pc == UINT32_C(0x20000446));
    CHECK(v->trace[1].kind == MC_WRITE32 && v->trace[1].value == 0);
    CHECK(v->trace[2].kind == MC_FENCE_I);
}
int main(void)
{
    mock v; mc_model m; unsigned i, n, mismatch, fail;
    /* Early return still performs the MMIO read/clear/fence/restore sequence. */
    for (i = 0; i < 3; ++i) {
        prepare(&v, &m, 0);
        CHECK(mc_compare(&m, i == 0 ? 0 : v.base1,
                         i == 1 ? 0 : v.base2, i == 2 ? 0 : 21) == MC_RETURNED);
        CHECK(m.return_known && m.return_value == 1 && m.restored);
        CHECK(v.count == 4 && v.mmio == UINT32_C(0xfedcba98)); prefix(&v);
    }
    /* Every short-buffer mismatch position and equality exit; byte-read order. */
    for (n = 1; n <= 32; ++n) for (mismatch = 0; mismatch <= n; ++mismatch) {
        prepare(&v, &m, 1);
        for (i = 0; i < n; ++i) v.a[i] = v.b[i] = (unsigned char)(i * 37u + 129u);
        if (mismatch < n) v.b[mismatch] ^= 1;
        CHECK(mc_compare(&m, v.base1, v.base2, n) == MC_RETURNED);
        CHECK(m.return_known && m.return_value == (uint32_t)(mismatch == n));
        CHECK(m.restored && v.mmio == UINT32_C(0xfedcba98)); prefix(&v);
        for (i = 0; i < (mismatch == n ? n : mismatch + 1); ++i) {
            CHECK(v.trace[3 + i * 2].pc == UINT32_C(0x20000474));
            CHECK(v.trace[3 + i * 2].address == v.base1 + i);
            CHECK(v.trace[4 + i * 2].pc == UINT32_C(0x20000478));
            CHECK(v.trace[4 + i * 2].address == v.base2 + i);
        }
        CHECK(v.trace[v.count - 1].kind == MC_WRITE32);
        CHECK(v.trace[v.count - 1].pc == (mismatch == n ?
              UINT32_C(0x2000045e) : UINT32_C(0x20000482)));
    }
    /* Unknown completion must not create a result or a fictitious restoration. */
    for (fail = 1; fail <= 6; ++fail) {
        prepare(&v, &m, 1); v.fail_at = fail;
        CHECK(mc_compare(&m, v.base1, v.base2, 1) == MC_BACKEND_UNKNOWN);
        CHECK(v.count == fail && !m.return_known && !m.restored);
    }
    prepare(&v, &m, 0);
    CHECK(mc_compare(&m, v.base1, v.base2, 1) == MC_PROFILE_UNKNOWN);
    CHECK(v.count == 4 && !m.return_known && !m.restored && v.mmio == 0);
    CHECK(m.boundary_pc == UINT32_C(0x20000478));
    CHECK(m.last.pc == UINT32_C(0x20000474));
    prepare(&v, &m, 1); m.max_operations = 3;
    CHECK(mc_compare(&m, v.base1, v.base2, 1) == MC_OBSERVATION_LIMIT);
    CHECK(v.count == 3 && m.operations == 3 && !m.return_known && !m.restored);
    /* Numeric address wrap matches RV32 ADD and never dereferences host memory. */
    prepare(&v, &m, 1); v.base1 = UINT32_C(0xfffffff0); v.base2 = UINT32_C(0xffffffe0);
    CHECK(mc_compare(&m, v.base1, v.base2, 32) == MC_RETURNED);
    CHECK(v.trace[35].address == 0 && m.return_value == 1 && m.restored);
    /* The original app compares 21 bytes, excluding the historical suffix. */
    prepare(&v, &m, 1);
    memcpy(v.a, "CH32V20x_BLE_LIB_V1.3", 21);
    memcpy(v.b, "CH32V20x_BLE_LIB_V1.31", 22);
    CHECK(mc_compare(&m, v.base1, v.base2, 21) == MC_RETURNED && m.return_value == 1);
    prepare(&v, &m, 1);
    memcpy(v.a, "CH32V20x_BLE_LIB_V1.3", 21);
    memcpy(v.b, "CH32V20x_BLE_LIB_V1.40", 22);
    CHECK(mc_compare(&m, v.base1, v.base2, 21) == MC_RETURNED && m.return_value == 0);
    printf("{\"passed\":true,\"groups\":7,\"checks\":%u}\n", checks);
    return 0;
}
