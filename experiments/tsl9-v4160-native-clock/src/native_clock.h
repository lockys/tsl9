#ifndef TSL9_REBUILD_NATIVE_CLOCK_H
#define TSL9_REBUILD_NATIVE_CLOCK_H
#ifdef __cplusplus
extern "C" {
#endif
/* New ordinary-C interfaces. Void does not promise preservation of the
 * original functions' A0/A1, caller-saved registers, or interrupt ABI. */
void tsl9_rebuild_clock_query_18834(void);
void tsl9_rebuild_clock_fields_1973c(void);
#ifdef __cplusplus
}
#endif
#endif
