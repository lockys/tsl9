#ifndef TSL9_TARGET_VECTORS_H
#define TSL9_TARGET_VECTORS_H
#ifdef __cplusplus
extern "C" {
#endif
/* R33: fixed V4.1.00 observed 82-word block. Physical IRQ count is unproved. */
typedef void (*tsl9_vector_handler)(void);
enum { TSL9_OBSERVED_VECTOR_WORDS = 82 };
extern tsl9_vector_handler const __tsl9_vector_table[TSL9_OBSERVED_VECTOR_WORDS];
void tsl9_image_entry(void);
#ifdef __cplusplus
}
#endif
#endif

