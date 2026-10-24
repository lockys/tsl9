/* Original8038-8180 address carrier, including trailing zero words.
 * Stored function addresses only: no C calling-convention or IRQ-count claim.
 * This file contains no executable fallback handlers or hardware accesses.
 */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef void (*tsl9_vector_entry_address)(void);
extern void tsl9_boot_entry_8000(void);
extern void tsl9_boot_18738(void);
extern void tsl9_boot_1873c(void);
extern void tsl9_vector_entry_8448(void);
extern void tsl9_boot_18638(void);
extern void tsl9_boot_1863a(void);
extern void tsl9_boot_1863c(void);
extern void tsl9_boot_1863e(void);
extern void tsl9_boot_18640(void);
extern void tsl9_boot_18642(void);
extern void tsl9_boot_18644(void);
extern void tsl9_boot_18646(void);
extern void tsl9_boot_18648(void);
extern void tsl9_boot_1864a(void);
extern void tsl9_boot_1864c(void);
extern void tsl9_boot_1864e(void);
extern void tsl9_boot_18650(void);
extern void tsl9_boot_18652(void);
extern void tsl9_boot_18654(void);
extern void tsl9_boot_18656(void);
extern void tsl9_boot_18658(void);
extern void tsl9_boot_1865a(void);
extern void tsl9_boot_1865c(void);
extern void tsl9_boot_1865e(void);
extern void tsl9_boot_18660(void);
extern void tsl9_boot_18662(void);
extern void tsl9_boot_18664(void);
extern void tsl9_vector_entry_12c24(void);
extern void tsl9_boot_18668(void);
extern void tsl9_boot_1866a(void);
extern void tsl9_vector_entry_16fb6(void);
extern void tsl9_boot_1866e(void);
extern void tsl9_boot_18670(void);
extern void tsl9_boot_18672(void);
extern void tsl9_boot_18674(void);
extern void tsl9_boot_18676(void);
extern void tsl9_vector_entry_979e(void);
extern void tsl9_boot_1867a(void);
extern void tsl9_boot_1867c(void);
extern void tsl9_boot_1867e(void);
extern void tsl9_boot_18680(void);
extern void tsl9_boot_18682(void);
extern void tsl9_boot_18684(void);
extern void tsl9_boot_18686(void);
extern void tsl9_boot_18688(void);
extern void tsl9_boot_1868a(void);
extern void tsl9_boot_1868c(void);
extern void tsl9_boot_1868e(void);
extern void tsl9_vector_entry_19bd4(void);
extern void tsl9_boot_18692(void);
extern void tsl9_boot_18694(void);
extern void tsl9_boot_18696(void);
extern void tsl9_boot_18698(void);
extern void tsl9_boot_1869a(void);
extern void tsl9_boot_1873e(void);
extern void tsl9_vector_entry_8498(void);
extern void tsl9_boot_186a0(void);
extern void tsl9_boot_186a2(void);
extern void tsl9_boot_186a4(void);
extern void tsl9_boot_186a6(void);
extern void tsl9_boot_186a8(void);

extern const tsl9_vector_entry_address tsl9_boot_vector_data_8038[82];
const tsl9_vector_entry_address tsl9_boot_vector_data_8038[82]
__attribute__((used, section(".rodata.tsl9_original_vectors"), aligned(4))) = {
    tsl9_boot_entry_8000, /* word 0; original0x8038 */
    0, /* word 1; original0x803c */
    tsl9_boot_18738, /* word 2; original0x8040 */
    tsl9_boot_1873c, /* word 3; original0x8044 */
    0, /* word 4; original0x8048 */
    tsl9_vector_entry_8448, /* word 5; original0x804c */
    0, /* word 6; original0x8050 */
    0, /* word 7; original0x8054 */
    tsl9_vector_entry_8448, /* word 8; original0x8058 */
    tsl9_boot_18638, /* word 9; original0x805c */
    0, /* word 10; original0x8060 */
    0, /* word 11; original0x8064 */
    tsl9_boot_1863a, /* word 12; original0x8068 */
    0, /* word 13; original0x806c */
    tsl9_boot_1863c, /* word 14; original0x8070 */
    0, /* word 15; original0x8074 */
    tsl9_boot_1863e, /* word 16; original0x8078 */
    tsl9_boot_18640, /* word 17; original0x807c */
    tsl9_boot_18642, /* word 18; original0x8080 */
    tsl9_boot_18644, /* word 19; original0x8084 */
    tsl9_boot_18646, /* word 20; original0x8088 */
    tsl9_boot_18648, /* word 21; original0x808c */
    tsl9_boot_1864a, /* word 22; original0x8090 */
    tsl9_boot_1864c, /* word 23; original0x8094 */
    tsl9_boot_1864e, /* word 24; original0x8098 */
    tsl9_boot_18650, /* word 25; original0x809c */
    tsl9_boot_18652, /* word 26; original0x80a0 */
    tsl9_boot_18654, /* word 27; original0x80a4 */
    tsl9_boot_18656, /* word 28; original0x80a8 */
    tsl9_boot_18658, /* word 29; original0x80ac */
    tsl9_boot_1865a, /* word 30; original0x80b0 */
    tsl9_boot_1865c, /* word 31; original0x80b4 */
    tsl9_boot_1865e, /* word 32; original0x80b8 */
    tsl9_boot_18660, /* word 33; original0x80bc */
    tsl9_boot_18662, /* word 34; original0x80c0 */
    tsl9_boot_18664, /* word 35; original0x80c4 */
    tsl9_vector_entry_12c24, /* word 36; original0x80c8 */
    tsl9_boot_18668, /* word 37; original0x80cc */
    tsl9_boot_1866a, /* word 38; original0x80d0 */
    tsl9_vector_entry_16fb6, /* word 39; original0x80d4 */
    tsl9_boot_1866e, /* word 40; original0x80d8 */
    tsl9_boot_18670, /* word 41; original0x80dc */
    tsl9_boot_18672, /* word 42; original0x80e0 */
    tsl9_boot_18674, /* word 43; original0x80e4 */
    tsl9_boot_18676, /* word 44; original0x80e8 */
    tsl9_vector_entry_979e, /* word 45; original0x80ec */
    tsl9_boot_1867a, /* word 46; original0x80f0 */
    tsl9_boot_1867c, /* word 47; original0x80f4 */
    tsl9_boot_1867e, /* word 48; original0x80f8 */
    tsl9_boot_18680, /* word 49; original0x80fc */
    tsl9_boot_18682, /* word 50; original0x8100 */
    tsl9_boot_18684, /* word 51; original0x8104 */
    tsl9_boot_18686, /* word 52; original0x8108 */
    tsl9_boot_18688, /* word 53; original0x810c */
    tsl9_boot_1868a, /* word 54; original0x8110 */
    tsl9_boot_1868c, /* word 55; original0x8114 */
    tsl9_boot_1868e, /* word 56; original0x8118 */
    tsl9_vector_entry_19bd4, /* word 57; original0x811c */
    tsl9_boot_18692, /* word 58; original0x8120 */
    tsl9_boot_18694, /* word 59; original0x8124 */
    tsl9_boot_18696, /* word 60; original0x8128 */
    tsl9_boot_18698, /* word 61; original0x812c */
    tsl9_boot_1869a, /* word 62; original0x8130 */
    tsl9_boot_1873e, /* word 63; original0x8134 */
    tsl9_vector_entry_8498, /* word 64; original0x8138 */
    tsl9_boot_186a0, /* word 65; original0x813c */
    tsl9_boot_186a2, /* word 66; original0x8140 */
    tsl9_boot_186a4, /* word 67; original0x8144 */
    tsl9_boot_186a6, /* word 68; original0x8148 */
    tsl9_boot_186a8, /* word 69; original0x814c */
    0, /* word 70; original0x8150 */
    0, /* word 71; original0x8154 */
    0, /* word 72; original0x8158 */
    0, /* word 73; original0x815c */
    0, /* word 74; original0x8160 */
    0, /* word 75; original0x8164 */
    0, /* word 76; original0x8168 */
    0, /* word 77; original0x816c */
    0, /* word 78; original0x8170 */
    0, /* word 79; original0x8174 */
    0, /* word 80; original0x8178 */
    0, /* word 81; original0x817c */
};

#ifdef __cplusplus
}
static_assert(sizeof(tsl9_vector_entry_address) == 4, "RV32 address carrier required");
static_assert(sizeof(tsl9_boot_vector_data_8038) == 328, "Exact selected carrier bytes");
#else
_Static_assert(sizeof(tsl9_vector_entry_address) == 4, "RV32 address carrier required");
_Static_assert(sizeof(tsl9_boot_vector_data_8038) == 328, "Exact selected carrier bytes");
#endif
