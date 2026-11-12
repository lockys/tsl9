/* Conditional call-sequence abstraction; not target code or an ABI model. */
#include <stdint.h>

typedef uintptr_t value;
typedef struct { value a0, a1, a2; } regs;
typedef struct {
    void *bus;
    void (*write_slot)(void *bus, value v);
    value (*read_slot)(void *bus);
    void (*csrc)(void *bus, unsigned csr, unsigned mask);
    void (*csrs)(void *bus, unsigned csr, unsigned mask);
    regs (*call_18e98)(void *bus, regs in);
    regs (*call_18e90)(void *bus, regs in);
    regs (*call_18ec4)(void *bus, regs in);
    regs (*call_18ef2)(void *bus, regs in);
    regs (*call_18eb6)(void *bus, regs in);
} callbacks;

value candidate(const callbacks *cb, regs r)
{
    value s1 = r.a0;
    cb->write_slot(cb->bus, r.a1);
    cb->csrc(cb->bus, 0x800, 136);
    r = cb->call_18e98(cb->bus, r);
    r.a0 = 49;
    r = cb->call_18e90(cb->bus, r);
    r.a0 = s1;
    r = cb->call_18ec4(cb->bus, r);
    r.a1 = cb->read_slot(cb->bus);
    r.a0 = s1;
    r = cb->call_18ef2(cb->bus, r);
    r = cb->call_18eb6(cb->bus, r);
    cb->csrs(cb->bus, 0x800, 136);
    return r.a0;
}
