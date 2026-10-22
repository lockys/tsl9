# 未通過燒錄驗證的 ADC caller 候選

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

`NOT-FLASH-VALIDATED-adc-caller-bank.bin`：78848 bytes，SHA256 `ecd2a9fe757117ab8af19211a56c5090dc3a2c777422fcd12ca2fb6298565e55`。

原77824-byte實驗映像保留，僅在副本的19896 caller改用真JAL連結至1B000的110-byte C/C++配置函式；caller RA仍為1989A，附加914-byte FF封裝資料。原88-byte函式未刪除。這不是把110B塞進原88B範圍。

僅有條件正常caller投影通過；私有frame殘值、完整callee ABI、fault／非同步／中斷、Flash／NV ownership、installed ROM、BOOT及硬體BLE OTA仍有未證條件。raw BIN沒有execute權限資訊。不可因編譯、link或合成驗證通過就視為可刷寫；本輪未接觸硬體。

這份候選也繼承舊OTA568元件與ROM地址witness的限制。[整合來源與實檔驗證](../../../analysis/v4160-adc-caller-2026-10-22/integration/README.md)；[本輪完整證據](../../../analysis/v4160-adc-caller-2026-10-22/README.md)。
