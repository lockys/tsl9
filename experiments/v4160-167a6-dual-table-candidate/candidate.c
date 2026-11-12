#include "candidate.h"

void v4160_dual_table(uint32_t event, const dual_table_ops *ops)
{
    unsigned index;
    for (index = 1; index != 36; ++index) {
        unsigned table;
        unsigned offset = index * 7;
        for (table = 0; table != 2; ++table) {
            const void *p = ops->snapshot(ops->context, table);
            uint8_t low = ops->read_byte(ops->context, p, offset);
            uint8_t high = ops->read_byte(ops->context, p, offset + 1);
            uint32_t key = (uint32_t)low | ((uint32_t)(high & 1u) << 8);
            if (key == event && (high & 2u) != 0)
                ops->dispatch(ops->context, table, index);
        }
    }
}
