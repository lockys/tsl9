# 0x11544 收到什麼記錄？

原 APP 在 `0x12372` 把回呼表 `0x1a674` 放入 a2，`0x12382` 呼叫名義 slot `0x401b0`；表內 +4 是 `0x11544`。全 APP 逐 byte 搜尋完整 LE32 指標只在 `0x1a678` 找到；半字視窗未見以此為目標的標準 JAL。這不是間接呼叫普查。

在 V1.31 參考映像的 Xwchc 解讀下，註冊端 `0x6adac` 保留非空表指標。事件處理器 `0x6abc6` 的訊息分支取得指標後，在 `0x6abee` 存入 s0。若訊息首 byte 為 208、次操作碼（+2）為 13，`0x6ac98` 起的分支依序排除 5、6、12，直接到 `0x6aca6`；不經 `0x6c964`。表與 +4 回呼都非空時，`0x6acb4` 把同一訊息指標放入 a0，`0x6acb6` 間接呼叫。此段沒有重建或複製事件記錄。這把候選派發端接到原 APP 的 case 13，但不證實機安裝的 ROM 或曾經派發。

以真實 `wchble_rom.h`（SHA-256 `647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c`）做 RV32 freestanding C11 靜態斷言，確認 `GAP_MSG_EVENT=208`、`GAP_DEVICE_INFO_EVENT=13`，以及 `gapDeviceInfoEvent_t` 中 opcode/addr/rssi/dataLen/pEvtData 的 offset 分別為 2/5/11/12/16。參考 SDK 將此記錄描述為探索時收到的廣播或掃描回應。原 APP 高三個鍵位元組的來源與該結構的 `addr[0..2]` 相符；不能將整個查表鍵當作完整藍牙位址，亦不能據此認定某台實體裝置。

可重播：將下列 C 以 `clang --target=riscv32 -ffreestanding -std=c11 -I <header-dir> -fsyntax-only` 檢查。它驗證參考 ABI，不驗證韌體對此型別的宣告。

```c
#include "wchble_rom.h"
#define F(f,o) _Static_assert(__builtin_offsetof(gapDeviceInfoEvent_t,f)==o,#f)
F(opcode,2); F(addr,5); F(rssi,11); F(dataLen,12); F(pEvtData,16);
_Static_assert(sizeof(void*)==4 && GAP_DEVICE_INFO_EVENT==13 && GAP_MSG_EVENT==208,"event");
```
