#ifndef TSL9_SCHEDULER_ALLOCATION_LAYOUT_H
#define TSL9_SCHEDULER_ALLOCATION_LAYOUT_H
#include <stdint.h>
/* Numeric candidate-SDK layout only. These are original 32-bit words,
 * not host pointers, allocation code, or a hardware memory declaration.
 * Record word +8 has no inferred meaning here. */
typedef struct tsl9_scheduler_record_words {
    uint32_t word0;
    uint32_t word4;
    uint32_t word8;
} tsl9_scheduler_record_words;
typedef struct tsl9_scheduler_prefix_words {
    tsl9_scheduler_record_words slots[48];
} tsl9_scheduler_prefix_words;
typedef uint32_t tsl9_task_callback_word;
typedef uint16_t tsl9_task_event_word;
enum {
    TSL9_SCHEDULER_RECORD_COUNT = 48,
    TSL9_SCHEDULER_RECORD_BYTES = 12,
    TSL9_SCHEDULER_PREFIX_BYTES = 576,
    TSL9_TASK_SUFFIX_BYTES_PER_COUNT = 6,
    TSL9_ENCODED_COUNT_LOWER_BOUND = 14,
    TSL9_ENCODED_COUNT_UPPER_BOUND = 212,
    TSL9_REQUEST_LOWER_BOUND = 660,
    TSL9_REQUEST_UPPER_BOUND = 1848
};
/* 43B90 reads x as an unsigned byte. 43B9A..43BB4 computes/stores
 * n = 3*((x >> 2) + (x & 3)) + 14, then low8(n).
 * The bit-width bounds 0<=x>>2<=63, 0<=x&3<=3 imply
 * 14<=n<=212, so that low8 store does not truncate this expression.
 * Allocation at 43BBE requests 576 + 6*n, A1=1.
 * After allocation/memset, fresh loads are distinct observations:
 * p=word[322C], n1=byte[319E], then word[31C4]=p+576,
 * word[31E4]=p+576+4*n1. A second 2*n1 suffix is only a
 * conditional numeric interpretation of the total request.
 * Equality of counts/pointers over time requires valid, stable,
 * non-overlapping memory and compatible callee/IRQ contracts. */
#endif
