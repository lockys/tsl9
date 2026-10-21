#ifndef TSL9_RESET_MEMORY_REBUILD_H
#define TSL9_RESET_MEMORY_REBUILD_H
#ifdef __cplusplus
extern "C" {
#endif
/* A new leaf helper. Original 0x186BA..0x186F8 falls through, not RET.
 * An entry adapter and original startup/IRQ/ROM compatibility are unproved. */
void tsl9_rebuild_reset_memory_186ba(void);
#ifdef __cplusplus
}
#endif
#endif
