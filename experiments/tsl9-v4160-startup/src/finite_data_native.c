#include "finite_data_native.h"
#define ORIGINAL_RO(address) \
    __attribute__((used, aligned(1), section(".rodata.tsl9v4160.finite_data_" #address)))

/* Exactly three length-prefixed AD records. The following three zeros are
 * not part of this reconstructed 13-byte payload. */
ORIGINAL_RO(19dec) const unsigned char __tsl9v4160_address_19dec[13] = {
    2, 1, 6, 3, 2, 0xf0, 0xff, 5, 9, 'T', 'S', 'L', '9'
};

/* Every array retains the original literal's NUL; the original caller's
 * requested comparison count excludes it. No resident ABI is supplied. */
ORIGINAL_RO(1a608) const unsigned char __tsl9v4160_conditional_address_1a608[9] = "Yiser-J6";
ORIGINAL_RO(1a614) const unsigned char __tsl9v4160_conditional_address_1a614[7] = "Free 2";
ORIGINAL_RO(1a61c) const unsigned char __tsl9v4160_conditional_address_1a61c[11] = "WiWU-WM105";
ORIGINAL_RO(1a628) const unsigned char __tsl9v4160_conditional_address_1a628[3] = "OM";
ORIGINAL_RO(1a62c) const unsigned char __tsl9v4160_conditional_address_1a62c[10] = "COIDEA KM";
ORIGINAL_RO(1a69c) const unsigned char __tsl9v4160_address_1a69c[5] = "1234";

/* Exact U16 scheduling-sequence source views, with private names. Keeping
 * their original canonical pointers unresolved preserves the unproved
 * state/alias/lifetime contracts. No inter-sequence padding is inserted. */
ORIGINAL_RO(1a430) const uint16_t __tsl9v4160_sequence_storage_1a430[17] = {
    50,150,50,150,50,350,50,150,50,150,50,400,150,250,150,250,150
};
ORIGINAL_RO(1a454) const uint16_t __tsl9v4160_sequence_storage_1a454[17] = {
    40,150,40,50,40,50,200,650,200,400,40,100,200,200,200,200,200
};
ORIGINAL_RO(1a478) const uint16_t __tsl9v4160_sequence_storage_1a478[53] = {
    40,150,40,150,40,150,40,150,40,150,200,450,40,150,40,150,40,150,
    40,150,40,150,200,450,40,50,40,50,40,50,40,50,40,50,40,50,40,
    50,40,50,40,150,40,150,40,150,40,150,150,250,150,250,150
};
#undef ORIGINAL_RO
