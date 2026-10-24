# Callback 提供者重建

[English](readme.en.md)

完整保留 D272、B0FC、12B24、13D48、10630 五個入口，及 B0FC 真正註冊的 B0D0 回呼：**558B／188 條指令／47 區塊，另有 62B 唯讀資料**。C11／C++17 原生物件相同；全部原碼經靜態原位址編碼後一致，七項相對跳轉表與兩組 17-byte 常數也逐 byte 相符。

[來源](../../src/native/receive/callback_providers.c) · [原始指令證據](../../analysis/callback-providers-2026-10-24/evidence.json) · [規格](spec-v1.json) · [通過的編譯收據](build/native-v2/measurement.json)

12B24 的 case 位於共用返回之後，已完整保留至 12BC8；不以第一個 ret 截斷。共核對 31 個直接轉移、8 個 PC-relative 參照及 14 個資料參照。保留原始堆疊、GP 計數與通知條件；單體編譯保留 12 個外部符號；現已接入主啟動圖，其中五個接到既有真實程式，七個仍為未知。[整合證據](../../analysis/callback-providers-2026-10-24/README.md)。

以本機 LLVM 目錄重查：

```sh
python3 experiments/tsl9-callback-providers/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-providers/build/native-v2
```

初次 native-v1 因產生器的組語換行跳脫錯誤而編譯失敗，來源與 UNACCEPTED 紀錄留存；未將其計為通過。原址配置、資料索引界限、RAM 擁有權、installed resident 身分／私有 ABI、實體 MCU／ROM／中斷及 OTA 相容性均未證明。未執行目標、模型或 ISA 模擬，未連線、接觸硬體或產生 BIN。
