#include "model.h"
uint32_t gate_1488e(uint32_t a2, uint32_t s2) {
    return a2 < s2 ? UINT32_C(0x148b4) : UINT32_C(0x14892);
}
result148de step_148de(regs148de r) {
    result148de out = {0};
    r.t1 = r.a1 & r.a6;
    if (r.t1 != 0) {
        r.t1 = r.a4 + UINT32_C(1);
        r.t3 = r.sp + UINT32_C(160);
        out.write_addr = r.sp + UINT32_C(24) + (r.a4 << 1);
        r.a4 = r.t1 & UINT32_C(255);
        out.wrote = 1;
    } else {
        r.t1 = r.a1 & r.a7;
        if (r.t1 != 0) {
            r.t1 = r.a5 + UINT32_C(1);
            r.t3 = r.sp + UINT32_C(160);
            out.write_addr = r.sp + UINT32_C(36) + (r.a5 << 1);
            r.a5 = r.t1 & UINT32_C(255);
            out.wrote = 1;
        }
    }
    if (out.wrote) out.write_value = (uint16_t)r.a1;
    r.a2 &= UINT32_C(255);
    out.r = r;
    out.pc = UINT32_C(0x1488e);
    return out;
}
result148b4 step_148b4(regs148b4 r, uint16_t loaded) {
    result148b4 out = {0};
    r.a2 += UINT32_C(1);
    out.read_addr = r.s0 + (r.a2 << 1);
    r.a1 = loaded;
    if (r.a0 < r.a1) {
        out.pc = UINT32_C(0x148de);
    } else {
        r.t1 = r.a3 + UINT32_C(1);
        r.t3 = r.sp + UINT32_C(160);
        out.write_addr = r.t3 + (r.a3 << 1) - UINT32_C(112);
        out.write_value = (uint16_t)r.a1;
        out.wrote = 1;
        r.a3 = r.t1 & UINT32_C(255);
        r.a2 &= UINT32_C(255);
        out.pc = UINT32_C(0x1488e);
    }
    out.r = r;
    return out;
}
