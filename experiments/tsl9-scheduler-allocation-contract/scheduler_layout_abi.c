#include "scheduler_layout.h"
#include <stddef.h>
#if defined(__cplusplus)
#define CHECK static_assert
#else
#define CHECK _Static_assert
#endif
CHECK(sizeof(uint32_t)==4 && sizeof(uint16_t)==2, "RV32 numeric words");
CHECK(sizeof(tsl9_scheduler_record_words)==12, "encoded record stride");
CHECK(offsetof(tsl9_scheduler_record_words,word4)==4, "encoded word4");
CHECK(offsetof(tsl9_scheduler_record_words,word8)==8, "uninterpreted word8");
CHECK(sizeof(tsl9_scheduler_prefix_words)==576, "48-record prefix");
CHECK(sizeof(tsl9_task_callback_word)==4, "first suffix word stride");
CHECK(sizeof(tsl9_task_event_word)==2, "second suffix word stride");
CHECK(sizeof(tsl9_task_callback_word)+sizeof(tsl9_task_event_word)==6,
      "encoded request suffix stride");
CHECK(TSL9_SCHEDULER_RECORD_COUNT*TSL9_SCHEDULER_RECORD_BYTES==576,
      "numeric table extent");
CHECK(576+6*TSL9_ENCODED_COUNT_LOWER_BOUND==TSL9_REQUEST_LOWER_BOUND,
      "algebraic lower bound");
CHECK(576+6*TSL9_ENCODED_COUNT_UPPER_BOUND==TSL9_REQUEST_UPPER_BOUND,
      "algebraic upper bound");
/* No functions, storage, callable target model, or executable test cases. */
