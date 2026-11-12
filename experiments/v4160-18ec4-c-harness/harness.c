/* Host-only scripted callback checks; not a hardware model. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include "../v4160-18ec4-candidate/candidate.c"

enum kind { READ, WRITE };
struct event { enum kind kind; uint32_t address, value; };
struct script { const struct event *events; size_t count, next; };

static const struct event *take(struct script *s, enum kind kind, uint32_t address)
{
    const struct event *e;
    if (s->next == s->count) {
        fprintf(stderr, "unexpected callback after event %zu\n", s->next);
        exit(EXIT_FAILURE);
    }
    e = &s->events[s->next++];
    if (e->kind != kind || e->address != address) {
        fprintf(stderr, "callback mismatch at event %zu\n", s->next - 1);
        exit(EXIT_FAILURE);
    }
    return e;
}

static uint32_t read_event(void *context, uint32_t address)
{
    return take(context, READ, address)->value;
}

static void write_event(void *context, uint32_t address, uint32_t value)
{
    struct script *s = context;
    const struct event *e = take(s, WRITE, address);
    if (e->value != value) {
        fprintf(stderr, "write mismatch at event %zu\n", s->next - 1);
        exit(EXIT_FAILURE);
    }
}

#define C UINT32_C(0x40022010)
#define A UINT32_C(0x40022014)
#define S UINT32_C(0x4002200c)
#define R(a, v) { READ, a, UINT32_C(v) }
#define W(a, v) { WRITE, a, UINT32_C(v) }

/* Independent literal expectations, including different successive control reads. */
static const struct event busy[] = {
    R(C, 0x12340001), W(C, 0x12360001), W(A, 0xabcdef00),
    R(C, 0x80000002), W(C, 0x80000042),
    R(S, 0x00000001), R(S, 0x00000003), R(S, 0x00000002),
    R(C, 0xffffffff), W(C, 0xfffdffff)
};
static const struct event zero[] = {
    R(C, 0), W(C, 0x20000), W(A, 0),
    R(C, 0), W(C, 0x40), R(S, 0), R(C, 0), W(C, 0)
};

static void run(const struct event *events, size_t count, uint32_t input,
                uint32_t expected)
{
    struct script s = { events, count, 0 };
    uint32_t result = candidate_18ec4(&s, read_event, write_event, input);
    if (result != expected || s.next != s.count) {
        fprintf(stderr, "return or unconsumed events mismatch (%zu/%zu)\n",
                s.next, s.count);
        exit(EXIT_FAILURE);
    }
}

int main(void)
{
    run(busy, sizeof busy / sizeof busy[0], UINT32_C(0xabcdefab), UINT32_C(0xabcdef00));
    run(zero, sizeof zero / sizeof zero[0], UINT32_C(0), UINT32_C(0));
    return EXIT_SUCCESS;
}
