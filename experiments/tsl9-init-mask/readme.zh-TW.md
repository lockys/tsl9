# 初始化末端的暫存器遮罩操作

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

`src/init_mask.c` 以可讀 C 實作官方 V4.1.60 的 `[0x19106,0x19124)` leaf；C++17 使用同一份來源與 C linkage。重用已封存的 `tsl9-v4160-irq-native/src/native_io.h`，只在必要邊界使用暫存器橋接，沒有原始 opcode carrier、stub 或假 ABS provider。

非零 enable 路徑新讀 `0x40021014` 的 32-bit word，寫回 `before | mask`；零路徑寫回 `before & ~mask`。A0 返回寫入值，A1 保留完整入口位元；非零路徑 A4=0x40021000、A5=before，零路徑則相反。mask 使用完整 32 bits，沒有只保留 bit 6。

## 實際證據

以固定 LLVM 18 工具和既有四個可配置暫存器策略，分別實際編譯 C11／C++17、連結並靜態讀回 ELF。兩種語言的完整函式均為 30 bytes／12 指令，與實讀官方 BIN 完全相同，code SHA256：

`69724f8e22551d238b67e52e25b3c1cbcaa62db28756da9b59a5c96ff7f16d87`

原始 BIN SHA256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，函式 file offset 為 0x11106，分析載入基底為 0x8000。最新實物收據位於本機 `build/canonical-20261022-v3/{c,cpp}/verification.json`。整個函式只有 A0／A4／A5 被寫入，沒有 call、SP／GP、CSR 或迴圈。沒有執行或模擬產生的 RV32 程式。

C 物件與 ELF 的配置均為 30 bytes 程式碼，linked 函式 VMA=0。C++ 物件另有 40-byte `.eh_frame` 與 3 筆 relocation，合計配置 70 bytes；連結後 `.eh_frame` 為 44 bytes，函式位於 VMA=0x2C，合計配置 74 bytes，剩餘 relocation=0。因此不能宣稱 C++ 整個元件只有 30 bytes，或將其配置直接等同 C 版本。

第一次驗證在正常的 `.text.<function>` 區段名稱檢查失敗，當時尚未產生成功收據；其目錄 `build/canonical-20261022-v1` 保留。修正檢查器後使用相同來源、旗標與工具重新驗證，沒有放寬完整 30-byte 比對。

獨立審查確認 v2 物件與 linked 函式實際相等，也指出收據來源檢查不足。v3 使用加強後的 schema：強制比較 object 與 linked 全文、精確工具／resource 雜湊、完整輸入集合、逐條成功命令與日誌，並明列 section 位址和全部配置 bytes。v1／v2 資料保留但不宣稱可由修改後 verifier 重播；目前 replay 入口對應 v3。這些靜態檢查不是可信執行環境的編譯證明，也不是硬體執行證據。

## 可攜入口

```sh
python3 experiments/tsl9-init-mask/verify.py --project-root ROOT --tool-dir LLVM_BIN --firmware ORIGINAL_BIN --build-root NEW_MODEL_BUILD
python3 experiments/tsl9-init-mask/verify.py --project-root ROOT --replay EXISTING_MODE/verification.json
```

所有路徑使用絕對路徑。NEW_MODEL_BUILD 必須是本模型 build 下不存在的目錄；省略時自動使用 UUID。目前只接受記錄的工具與 LLVM stdint resource 雜湊，不能將更換編譯器後的結果冒充此次證據。Python 入口不依賴 PowerShell，sh wrapper 只轉交參數；本次沒有執行 shell wrapper。replay 只讀既有來源、原 BIN、物件、ELF 與收據，不重新編譯。

## App 連接與限制

[source-map.json](source-map.json) 保存 leaf 與 App 末端的精確原始 bytes。額外靜態閱讀 App `[0x19AEE,0x19B16)`：前一個 initializer 的 A0=0 才走正常路徑；非零則進入 0x19AF0 自迴圈。App 設 A1=1、A0=64，呼叫 0x19106；之後新讀目前 SP+92 的 RA、SP+88 的 S0，再依序寫 0xE000E104=0x80000000、0xE000E108=1，SP+=96，於 0x19B14 返回。這 40-byte App 閱讀沒有被包裝為已重建的 C App，也不屬於 leaf checker 的通過範圍。

正常 App 出口 A0 是新讀 word OR 0x40，並非成功碼；A1=1、A4=1、A5=0xE000E000。保存 RA 指向的外部 caller 仍未知。固定數字尚不足以確認實際晶片或周邊語意。

此處 VMA 0 只用於離線元件比對，沒有證明可用 Flash、installed ROM、完整啟動、fault／IRQ／非同步等價或 OTA 相容。**尚未成功刷入重建韌體；沒有產生韌體 BIN，也不操作 BLE／CAN／UART／Flash 或第三方 API。**
