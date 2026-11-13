#ifdef __cplusplus
extern "C" {
#endif
extern volatile unsigned char status_byte __attribute__((visibility("hidden")));
__attribute__((section(".leaf"), used))
int get_status(void) { return status_byte; }
#ifdef __cplusplus
}
#endif
