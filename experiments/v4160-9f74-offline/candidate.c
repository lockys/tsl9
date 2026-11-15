/* Isolated numerical witness only; not linked into the stock image. */
#ifdef __cplusplus
extern "C" {
#endif
extern volatile unsigned char tsl9_9f74_data __attribute__((visibility("hidden")));
__attribute__((section(".text.tsl9_9f74_candidate"), used, noinline, aligned(2)))
void tsl9_9f74_candidate(void) { tsl9_9f74_data = 0; }
#ifdef __cplusplus
}
#endif
