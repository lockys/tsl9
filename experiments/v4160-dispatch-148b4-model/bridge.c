#include "model.h"
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) uint32_t run_gate(uint32_t a2, uint32_t s2) { return gate_1488e(a2, s2); }
__declspec(dllexport) size_t class_layout(unsigned i) {
    static const size_t layout[] = {
        sizeof(regs148de), sizeof(result148de),
        offsetof(regs148de, a1), offsetof(regs148de, a2), offsetof(regs148de, a4),
        offsetof(regs148de, a5), offsetof(regs148de, a6), offsetof(regs148de, a7),
        offsetof(regs148de, sp), offsetof(regs148de, t1), offsetof(regs148de, t3),
        offsetof(result148de, r), offsetof(result148de, pc), offsetof(result148de, write_addr),
        offsetof(result148de, write_value), offsetof(result148de, wrote)
    };
    return i < sizeof(layout) / sizeof(layout[0]) ? layout[i] : (size_t)-1;
}
__declspec(dllexport) void run_class(const regs148de *input, result148de *output) { *output = step_148de(*input); }
__declspec(dllexport) void run_step(const regs148b4 *input, uint16_t loaded, result148b4 *output) {
    *output = step_148b4(*input, loaded);
}
#ifdef __cplusplus
}
#endif
