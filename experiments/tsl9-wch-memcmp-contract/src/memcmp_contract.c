#include "memcmp_contract.h"
#include <stddef.h>

void mc_init(mc_model *m, const mc_backend *backend, unsigned xwchc_profile)
{
    size_t i;
    volatile unsigned char *clear = (volatile unsigned char *)m;
    for (i = 0; i < sizeof(*m); ++i) clear[i] = 0;
    if (backend) m->backend = *backend;
    m->xwchc_profile = xwchc_profile;
    m->max_operations = 128;
    m->flow = MC_BACKEND_UNKNOWN;
}

static int request(mc_model *m, mc_kind kind, uint32_t pc,
                   uint32_t address, uint32_t value, uint32_t *out)
{
    m->last.kind = kind; m->last.pc = pc;
    m->last.address = address; m->last.value = value;
    m->boundary_pc = pc;
    if (m->operations >= m->max_operations) {
        m->flow = MC_OBSERVATION_LIMIT; return 0;
    }
    ++m->operations;
    if (!m->backend.invoke ||
        !m->backend.invoke(m->backend.context, &m->last, out)) {
        m->flow = MC_BACKEND_UNKNOWN; return 0;
    }
    return 1;
}

mc_flow mc_compare(mc_model *m, uint32_t src1, uint32_t src2, uint32_t length)
{
    uint32_t saved = 0, ignored = 0, left = 0, right = 0, offset = 0;
    uint32_t equal = 1, restore_pc = UINT32_C(0x2000045e);
    m->operations = 0; m->saved_known = 0; m->restored = 0;
    m->return_known = 0; m->flow = MC_BACKEND_UNKNOWN;
    if (!request(m, MC_READ32, UINT32_C(0x20000446),
                 UINT32_C(0x4002420c), 0, &saved)) return m->flow;
    m->saved_mmio = saved; m->saved_known = 1;
    if (!request(m, MC_WRITE32, UINT32_C(0x2000044a),
                 UINT32_C(0x4002420c), 0, &ignored)) return m->flow;
    if (!request(m, MC_FENCE_I, UINT32_C(0x2000044e), 0, 0, &ignored))
        return m->flow;
    if (src1 && src2 && length) {
        for (;;) {
            if (!request(m, MC_READ8, UINT32_C(0x20000474),
                         src1 + offset, 0, &left)) return m->flow;
            /* Decoding 0x2294 needs Xwchc; stop after preceding effects when
             * the caller has not selected that conditional ISA profile. */
            if (!m->xwchc_profile) {
                m->boundary_pc = UINT32_C(0x20000478);
                m->flow = MC_PROFILE_UNKNOWN; return m->flow;
            }
            if (!request(m, MC_READ8, UINT32_C(0x20000478),
                         src2 + offset, 0, &right)) return m->flow;
            if ((left & 255u) != (right & 255u)) {
                equal = 0; restore_pc = UINT32_C(0x20000482); break;
            }
            ++offset; /* RV32 modulo arithmetic; no fabricated wrap guard. */
            if (offset == length) break;
        }
    }
    if (!request(m, MC_WRITE32, restore_pc, UINT32_C(0x4002420c),
                 saved, &ignored)) return m->flow;
    m->restored = 1; m->return_value = equal; m->return_known = 1;
    m->flow = MC_RETURNED;
    return m->flow;
}
