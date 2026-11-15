/* Experimental leaf reconstructions, not part of the stock firmware build.
 * GP and the symbols must be bound to the same actual RAM carrier; isolated
 * numeric witnesses do not prove this holds at runtime.
 */
#ifdef __cplusplus
extern "C" {
#endif
#if LEAF == 0x10402
extern volatile unsigned short tsl9_10402_data __attribute__((visibility("hidden")));
__attribute__((section(".text.tsl9v4160.direct_successors_10402"), used, noinline, aligned(2)))
unsigned int __tsl9v4160_call_10402(void) { return tsl9_10402_data; }
#elif LEAF == 0x10408
extern volatile unsigned char tsl9_10408_data __attribute__((visibility("hidden")));
__attribute__((section(".text.tsl9v4160.direct_frontier_10408"), used, noinline, aligned(2)))
unsigned int __tsl9v4160_call_10408(void) { return tsl9_10408_data; }
#else
#error Specify a supported LEAF
#endif
#ifdef __cplusplus
}
#endif
