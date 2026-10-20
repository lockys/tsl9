/* R81: an original address-only linker constant. No allocated target bytes.
 * No resident ROM entry or executable provider is supplied by this unit.
 */
#include "target_stack_address_r81.h"
#define TSL9_R81_STRING_IMPL(x) #x
#define TSL9_R81_STRING(x) TSL9_R81_STRING_IMPL(x)
__asm__(
".globl __tsl9_stack_top\n"
".set __tsl9_stack_top," TSL9_R81_STRING(TSL9_SOURCE_INITIAL_SP_ADDRESS_R81) "\n"
".size __tsl9_stack_top,0\n"
);
