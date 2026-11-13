#include "candidate.h"
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ALT UINT32_C(0x1000)
#define ALT2 UINT32_C(0x3000)
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #x); exit(1); } } while (0)

typedef struct {
    volatile uint8_t fixed[4]; /* BF10..BF13 */
    volatile uint8_t alt[24], alt2[24];
    char log[1024];
    size_t used;
    int effect1, effect2, indirect, stop;
    jmp_buf escape;
} state;

static volatile uint8_t *cell(state *s, uint32_t a)
{
    if (a >= C364_BF10 && a <= C364_BF13) return &s->fixed[a - C364_BF10];
    if (a >= ALT && a < ALT + 24) return &s->alt[a - ALT];
    if (a >= ALT2 && a < ALT2 + 24) return &s->alt2[a - ALT2];
    fprintf(stderr, "unexpected address %08lx\n", (unsigned long)a); exit(1);
}
static void event(state *s, char kind, uint32_t a, unsigned value)
{
    int n = snprintf(s->log + s->used, sizeof s->log - s->used,
                     "%c%08lx:%02x;", kind, (unsigned long)a, value);
    CHECK(n > 0 && (size_t)n < sizeof s->log - s->used);
    s->used += (size_t)n;
}
static uint8_t read8(void *ctx, uint32_t a)
{
    state *s = ctx;
    uint8_t v = *cell(s, a);
    event(s, 'R', a, v);
    if (s->indirect && a == C364_BF10) {
        s->fixed[2] = 0x42; s->fixed[3] = 0x81;
    }
    return v;
}
static void write8(void *ctx, uint32_t a, uint8_t v)
{
    state *s = ctx;
    event(s, 'W', a, v);
    *cell(s, a) = v;
}
static void call(void *ctx, uint32_t target, uint32_t a0, uint32_t *s0)
{
    state *s = ctx;
    event(s, 'C', target, (unsigned)a0);
    if (target == UINT32_C(0xef76)) {
        if (s->effect1 == 1) { *s0 = ALT; s->alt[22] = 0; s->alt[23] = 0x55; s->fixed[3] = 0x33; }
        if (s->effect1 == 2) { *s0 = ALT; s->alt[22] = 0x80; s->alt[23] = 0; s->fixed[3] = 0x44; }
        if (s->effect1 == 3) s->fixed[3] = 0x21;
        if (s->effect1 == 4) { *s0 = ALT; s->alt[23] = 0; s->fixed[3] = 0x33; }
        if (s->effect1 == 5) { *s0 = ALT; s->alt[23] = 0x55; s->fixed[3] = 0; }
        if (s->stop == 1) longjmp(s->escape, 1);
    } else {
        CHECK(target == UINT32_C(0xbd6e));
        if (s->effect2 == 1) { *s0 = ALT2; s->alt2[23] = 0x66; s->fixed[3] = 0x77; }
        if (s->effect2 == 2) s->fixed[3] = 0x32;
        if (s->effect2 == 3) s->fixed[3] = 0;
        if (s->stop == 2) longjmp(s->escape, 1);
    }
}
static void invoke(state *s)
{
    c364_bus bus = {s, read8, write8, call};
    c364_candidate(&bus, UINT32_C(0xdeadbeef));
}
static void expect(state *s, const char *name, const char *expected)
{
    if (strcmp(s->log, expected) != 0) {
        fprintf(stderr, "FAIL %s\nexpected %s\nactual   %s\n", name, expected, s->log); exit(1);
    }
    printf("PASS %s: %s\n", name, s->log);
}
static void branches(void)
{
    unsigned i;
    for (i = 0; i < 8; ++i) {
        state s = {0}; char expected[1024] = ""; char part[64]; char name[32];
        s.fixed[0] = (i & 1) ? 0x80 : 0;
        s.fixed[2] = (i & 2) ? 0x02 : 0;
        s.fixed[3] = (i & 4) ? 0xff : 0;
        snprintf(part, sizeof part, "R2000bf10:%02x;", (unsigned)s.fixed[0]); strcat(expected, part);
        if (i & 1) strcat(expected, "C0000ef76:00;");
        snprintf(part, sizeof part, "R2000bf12:%02x;", (unsigned)s.fixed[2]); strcat(expected, part);
        if (i & 2) strcat(expected, "C0000bd6e:00;");
        snprintf(part, sizeof part, "R2000bf13:%02x;", (unsigned)s.fixed[3]); strcat(expected, part);
        if (i & 4) strcat(expected, "W2000bf13:00;");
        invoke(&s); snprintf(name, sizeof name, "branches-%u", i); expect(&s, name, expected);
        CHECK(s.fixed[3] == 0);
    }
}
static void effects(void)
{
    state a = {0}, b = {0}, c = {0}, d = {0}, e = {0}, f = {0}, g = {0};
    f.fixed[0] = 1; f.effect1 = 4; invoke(&f);
    expect(&f, "redirect-zero-fixed-nonzero-no-store", "R2000bf10:01;C0000ef76:00;R00001016:00;R00001017:00;");
    CHECK(f.alt[23] == 0 && f.fixed[3] == 0x33);
    g.fixed[0] = 1; g.effect1 = 5; invoke(&g);
    expect(&g, "redirect-nonzero-fixed-zero-store", "R2000bf10:01;C0000ef76:00;R00001016:00;R00001017:55;W2000bf13:00;");
    CHECK(g.alt[23] == 0x55 && g.fixed[3] == 0);
    a.fixed[0] = 1; a.effect1 = 1; invoke(&a);
    expect(&a, "first-changes-both-reads", "R2000bf10:01;C0000ef76:00;R00001016:00;R00001017:55;W2000bf13:00;");
    CHECK(a.alt[23] == 0x55 && a.fixed[3] == 0);
    b.fixed[0] = 1; b.effect1 = 2; b.effect2 = 1; invoke(&b);
    expect(&b, "both-change-s0-and-bf13", "R2000bf10:01;C0000ef76:00;R00001016:80;C0000bd6e:00;R00003017:66;W2000bf13:00;");
    CHECK(b.alt2[23] == 0x66 && b.fixed[3] == 0);
    c.fixed[0] = 1; c.fixed[2] = 1; c.effect1 = 3; c.effect2 = 2; invoke(&c);
    expect(&c, "direct-alias-both-calls", "R2000bf10:01;C0000ef76:00;R2000bf12:01;C0000bd6e:00;R2000bf13:32;W2000bf13:00;");
    CHECK(c.fixed[3] == 0);
    d.fixed[2] = 1; d.fixed[3] = 9; d.effect2 = 3; invoke(&d);
    expect(&d, "callee-clears-no-candidate-store", "R2000bf10:00;R2000bf12:01;C0000bd6e:00;R2000bf13:00;");
    CHECK(d.fixed[3] == 0);
    e.indirect = 1; invoke(&e);
    expect(&e, "indirect-read-side-effect", "R2000bf10:00;R2000bf12:42;C0000bd6e:00;R2000bf13:81;W2000bf13:00;");
}
static void nonreturning(void)
{
    /* Static storage avoids indeterminate automatic objects after longjmp. */
    static state a, b;
    a.fixed[0] = 1; a.stop = 1;
    if (setjmp(a.escape) == 0) { invoke(&a); CHECK(0); }
    expect(&a, "first-does-not-return", "R2000bf10:01;C0000ef76:00;");
    b.fixed[2] = 1; b.stop = 2;
    if (setjmp(b.escape) == 0) { invoke(&b); CHECK(0); }
    expect(&b, "second-does-not-return", "R2000bf10:00;R2000bf12:01;C0000bd6e:00;");
}
int main(void)
{
    branches(); effects(); nonreturning();
    puts("all host model checks passed");
    return 0;
}
