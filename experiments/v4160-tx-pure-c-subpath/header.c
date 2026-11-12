/* ISO C11 abstract candidate for original [0x8ace, 0x8b0a), not an ABI entry. */
#include <stdint.h>
#include <stddef.h>
#include <limits.h>

_Static_assert(CHAR_BIT == 8, "requires octets");
struct tx_bank {
    uint8_t reserved[6];
    uint16_t magic;
    uint8_t command, length_hi, length_lo;
    uint8_t remaining[1051];
};
_Static_assert(offsetof(struct tx_bank, magic) == 6, "magic offset");
_Static_assert(offsetof(struct tx_bank, command) == 8, "command offset");
_Static_assert(offsetof(struct tx_bank, length_hi) == 9, "high offset");
_Static_assert(offsetof(struct tx_bank, length_lo) == 10, "low offset");
_Static_assert(sizeof(struct tx_bank) == 1062, "bank stride");

/* Conceptual RAM at 0x2000b18c, not automatically placed at that address. */
struct tx_ram { struct tx_bank bank[2]; };
struct tx_result { uint32_t a5, a4, a1, a2, a3; };

/* Precondition: bank is 0 or 1, ram points to a valid, non-overlapping
 * RAM object; length and command are the then-live full RV32 S0 and S3.
 * Returns the register values needed at the next cut, not a TX result. */
struct tx_result tx_header(volatile struct tx_ram *ram, uint32_t bank,
                           uint32_t length, uint32_t command)
{
    uint32_t a5 = (uint32_t)(bank * UINT32_C(1062));
    uint32_t a3 = UINT32_C(0x2000b18c);
    uint32_t a4 = UINT32_C(0xffff8000);
    uint32_t a1;
    struct tx_result result;
    a4 ^= UINT32_C(0xffffff55);
    a1 = length & UINT32_C(255);
    a5 = (uint32_t)(a5 + UINT32_C(6));
    a5 = (uint32_t)(a5 + a3);
    ram->bank[bank].magic = (uint16_t)a4;
    ram->bank[bank].length_lo = (uint8_t)a1;
    a4 = length >> 8;
    a1 = (uint32_t)(a1 + command);
    ram->bank[bank].length_hi = (uint8_t)a4;
    a4 = (uint32_t)(a4 + a1);
    ram->bank[bank].command = (uint8_t)command;
    a4 &= UINT32_C(255);
    a1 = 0;
    result.a5 = a5; result.a4 = a4; result.a1 = a1;
    result.a2 = bank; result.a3 = a3;
    return result;
}
