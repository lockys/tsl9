#include "observed_predicate.h"
#include <stddef.h>
/* Exact source identity and file offsets from evidence/predicate.json.
 * Equal routine bytes do not imply whole-image or hardware equivalence. */
static const tsl9_observed_profile profiles[] = {
    { UINT32_C(2389), UINT32_C(522), UINT32_C(76800), "bf45097893ba846e68b6099df2374cbb423591ceb0b4bae37b8988dcc28759c3" },
    { UINT32_C(2410), UINT32_C(522), UINT32_C(76800), "8efe823dd03fad5ae70f0df5a0a2c28233cd9045d25aace4425f08be92f49d37" },
    { UINT32_C(2527), UINT32_C(532), UINT32_C(76800), "6d3dc488cc545399424b01f9122b484ae255aec79ec96e60770cf0bb47959658" },
    { UINT32_C(2581), UINT32_C(532), UINT32_C(76800), "32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc" },
    { UINT32_C(2590), UINT32_C(532), UINT32_C(76800), "3a75070a782bb2e9de830347f41d52dcdf1b6705ecce4e4a411c698cf134a96f" },
    { UINT32_C(2816), UINT32_C(532), UINT32_C(76800), "9fec9ef63f785480fdaf9447bcc1e284fb7995bdbc54e2b4f3d4443d0b63511f" },
    { UINT32_C(2833), UINT32_C(532), UINT32_C(76800), "babe32e676aa5dae890699c636850e9cce83ef0d02e546ba94882de1584f0005" },
    { UINT32_C(2841), UINT32_C(532), UINT32_C(76800), "ae5a952960fe0e651ea9e5c05ae40377776c185f2910a0bd7adb79b8ff839cc4" },
    { UINT32_C(2869), UINT32_C(542), UINT32_C(76800), "05cf15431ea3f6fc78ee9e51e68333f2baf8a3770c59c1598845d3263a7a5a7e" },
    { UINT32_C(2873), UINT32_C(542), UINT32_C(77824), "e6aca84b3cbadb1dee072ca079eb172fa1f6f359b3cf131a20a0b789147ea2c6" },
    { UINT32_C(2914), UINT32_C(542), UINT32_C(77824), "bd4f3b605871e63514ff752beadbfea1c4ba4dec68b7ef4da059ee0d616021df" },
    { UINT32_C(2946), UINT32_C(542), UINT32_C(76800), "a00919a0995a79bb3e83eaa8bf29ebb985bf0011e895e3ca16d6b5970ed58569" },
    { UINT32_C(2958), UINT32_C(542), UINT32_C(76800), "b253a9ce466051f24b762015ffcbe3b2a62f14e1495f306096068b8f2922d608" },
    { UINT32_C(2963), UINT32_C(542), UINT32_C(76800), "8571763eb876d0314e50e2d547c99f7cdc9eac933f1e6ac5891f9f0c204a0547" },
    { UINT32_C(2966), UINT32_C(542), UINT32_C(76800), "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667" }
};
const tsl9_observed_profile *tsl9_find_observed_profile(uint32_t firmware_id) {
    size_t i;
    for (i = 0; i < sizeof(profiles) / sizeof(profiles[0]); ++i) {
        if (profiles[i].firmware_id == firmware_id) return &profiles[i];
    }
    return 0;
}
