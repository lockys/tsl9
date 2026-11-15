/* Isolated candidate, not linked into the firmware. The real RAM binding and
 * read side effects remain unverified; a numeric witness is not deployable. */
#ifdef __cplusplus
extern "C" {
#endif
extern volatile unsigned short tsl9_d314_data __attribute__((visibility("hidden")));
__attribute__((section(".text.tsl9v4160.direct_closure_d314"), used, noinline, aligned(2)))
unsigned int __tsl9v4160_call_d314(void) { return tsl9_d314_data != 0; }
#ifdef __cplusplus
}
#endif
