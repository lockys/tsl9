/* SDK ABI check, not firmware source or an executable test. */
#include "wchble_rom.h"
#define CHECK_FIELD(name, off) _Static_assert(__builtin_offsetof(blePaControlConfig_t, name) == (off) && sizeof(((blePaControlConfig_t *)0)->name) == 4, #name)
CHECK_FIELD(txEnableGPIO, 0);
CHECK_FIELD(txDisableGPIO, 4);
CHECK_FIELD(tx_pin, 8);
CHECK_FIELD(rxEnableGPIO, 12);
CHECK_FIELD(rxDisableGPIO, 16);
CHECK_FIELD(rx_pin, 20);
_Static_assert(sizeof(void *) == 4 && sizeof(blePaControlConfig_t) == 24, "RV32 layout");
_Static_assert(FUNCITON_BASE_ADDRESSS + 109 * 4 == 0x401e8, "default slot");
_Static_assert(_Generic(BLE_PAControlInit, void (*)(blePaControlConfig_t *): 1, default: 0), "setter type");
void invoke_for_ir_only(blePaControlConfig_t *p) { BLE_PAControlInit(p); }
