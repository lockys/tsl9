/* New compiler-call contract only. Include guards keep the original IO
 * definitions while the two measured missing clobbers are overlaid. */
#include "../../tsl9-v4160-flash-entry-order/src/flash_native.h"
#include "../../tsl9-v4160-flash-entry-order/src/native_io.h"
#undef FN_CALL_UNLOCK
#undef FN_CALL_ERASE
#define FN_CALL_UNLOCK(v) FN_ONE_CALL(tsl9_flash_unlock_18e98,(v),"a1","a3","a4","a5")
#define FN_CALL_ERASE(v) FN_ONE_CALL(tsl9_flash_erase_18ec4,(v),"a1","a3","a4","a5")
#include "../../tsl9-nv-write-callback/src/nv_write_callback.c"
