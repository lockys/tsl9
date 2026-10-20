#ifndef TSL9_TARGET_RUNTIME_MEMORY_H
#define TSL9_TARGET_RUNTIME_MEMORY_H
/* Storage ranges only; zero-size aliases elsewhere do not declare C objects. */
#ifdef __cplusplus
extern "C" {
#endif
extern unsigned char __tsl9_data_start[136];
extern const unsigned char __tsl9_data_load[136];
extern unsigned char __tsl9_bss_end[];
#ifdef __cplusplus
}
#endif
#endif
