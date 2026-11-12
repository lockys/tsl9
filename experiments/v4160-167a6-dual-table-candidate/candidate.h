#ifndef V4160_DUAL_TABLE_CANDIDATE_H
#define V4160_DUAL_TABLE_CANDIDATE_H
#include <stdint.h>

/* Abstract observations, not firmware ABI. All callbacks must return normally. */
typedef struct {
    void *context;
    const void *(*snapshot)(void *context, unsigned table);
    uint8_t (*read_byte)(void *context, const void *snapshot, unsigned offset);
    void (*dispatch)(void *context, unsigned table, unsigned index);
} dual_table_ops;

void v4160_dual_table(uint32_t event, const dual_table_ops *ops);
#endif
