/* Synthetic host model fixture; this is not original-instruction execution. */
#define main upstream_ingress_test_main
#include "../tsl9-v4160-gatt-ingress-model/tests/test_gatt_ingress.c"
#undef main

static unsigned witness_frame(fixture *x, unsigned length)
{
    unsigned n = frame(x, 0xc0, length), i;
    uint8_t sum = (uint8_t)(0xc0u + (length >> 8) + (length & 255u));
    /* First word is padding; first parsed halfword is 0x0800 little-endian. */
    for (i = 0; i < length; ++i) {
        uint8_t value = (i < 2) ? 0xff : ((i & 1u) ? 0x08 : 0x00);
        if (length == 20 && i >= 4 && i < 16)
            value = (i & 1u) ? 0x10 : 0x00;
        if (length == 20 && i == 17) value = 0x20;
        if (length == 20 && i == 18) value = 0x01;
        if (length == 20 && i == 19) value = 0x30;
        put(x, CHUNK + 5 + i, 1, value);
        sum = (uint8_t)(sum + value);
    }
    put(x, CHUNK + 5 + length, 1, sum);
    return n;
}

static void witness(unsigned length, int corrupt)
{
    gi_model m;
    unsigned n;
    const gi_request *q;
    reset(&f, &m);
    n = witness_frame(&f, length);
    if (corrupt) f.mem[CHUNK + n - 1 - RB] ^= 1;
    CHECK(receive(&m, 0x1234, n) == GI_RETURNED);
    if (corrupt) {
        CHECK(f.dispatches == 0);
        return;
    }
    CHECK(f.dispatches == 1);
    q = last_dispatch(&f);
    CHECK(q->target == 0x14056 && q->args[0] == 0x1234 && q->args[1] == 0xc0);
    CHECK(q->args[2] == BUFFER && q->args[3] == length);
    CHECK(get(&f, BUFFER + 2, 2) == 0x0800);
    CHECK(!memcmp(f.mem + BUFFER - RB, f.mem + CHUNK + 5 - RB, length));
}

int main(void)
{
    witness(20, 0);
    witness(20, 1);
    witness(514, 0);
    witness(514, 1);
    printf("PASS: host ingress model dispatches 20- and 514-byte c0 frames; bad checksums rejected (%u checks)\n", checks);
    return 0;
}
