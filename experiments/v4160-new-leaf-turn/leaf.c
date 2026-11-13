#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, section(".leaf")))
unsigned leaf(const volatile unsigned char *p) {
#ifdef NEGATIVE
    return p[3] == 5;
#else
    return p[3] == 4;
#endif
}
