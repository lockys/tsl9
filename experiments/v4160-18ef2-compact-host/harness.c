/* Host-only scripted bus; no target access. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "candidate.c"

typedef struct { char kind; uint32_t address, value; } event;
typedef struct {
    const char *name;
    uint32_t a0, a1, result;
    const event *events;
    size_t count;
} fixture;
#include "fixtures.h"

typedef struct { const fixture *test; size_t next; } state;

static const event *take(state *s, char kind, uint32_t address)
{
    const event *e;
    if (s->next == s->test->count) {
        fprintf(stderr, "%s: unexpected event beyond budget %zu\n", s->test->name, s->next);
        exit(EXIT_FAILURE);
    }
    e = &s->test->events[s->next++];
    if (e->kind != kind || e->address != address) {
        fprintf(stderr, "%s: event %zu: got %c %08" PRIx32 ", expected %c %08" PRIx32 "\n",
                s->test->name, s->next - 1, kind, address, e->kind, e->address);
        exit(EXIT_FAILURE);
    }
    return e;
}
static uint32_t read32(void *context, uint32_t address)
{
    return take(context, 'R', address)->value;
}
static void write32(void *context, uint32_t address, uint32_t value)
{
    state *s = context;
    const event *e = take(s, 'W', address);
    if (e->value != value) {
        fprintf(stderr, "%s: event %zu: got value %08" PRIx32 ", expected %08" PRIx32 "\n",
                s->test->name, s->next - 1, value, e->value);
        exit(EXIT_FAILURE);
    }
}
int main(void)
{
    size_t i;
    for (i = 0; i < sizeof fixtures / sizeof fixtures[0]; ++i) {
        state s = { &fixtures[i], 0 };
        event_bus bus = { &s, read32, write32 };
        uint32_t result = candidate_18ef2(&bus, s.test->a0, s.test->a1);
        if (result != s.test->result || s.next != s.test->count) {
            fprintf(stderr, "%s: return or event count mismatch (%zu/%zu)\n",
                    s.test->name, s.next, s.test->count);
            return EXIT_FAILURE;
        }
        printf("%s: pass\n", s.test->name);
    }
    return EXIT_SUCCESS;
}
