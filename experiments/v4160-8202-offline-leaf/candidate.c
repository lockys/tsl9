/* Experimental reconstruction; not part of the stock firmware build.
 * The symbol must be bound to the actual RAM carrier plus 32481, not merely
 * a numeric witness. This source alone does not establish runtime behavior.
 */
#ifdef __cplusplus
extern "C" {
#endif
extern volatile unsigned char tsl9_8202_data __attribute__((visibility("hidden")));
__attribute__((section(".text.tsl9v4160.direct_closure_8202"), used, noinline, aligned(2)))
unsigned int __tsl9v4160_call_8202(void) { return tsl9_8202_data; }
#ifdef __cplusplus
}
#endif
