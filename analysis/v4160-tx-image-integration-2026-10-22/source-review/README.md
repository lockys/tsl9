# TX 完整映像：獨立來源與入口角色審查

[English](readme.en.md)

這份審查只使用離線檔案與靜態欄位。原始 ID2966 V4.1.60 的 TX 範圍是 `0x8A56..0x8B6E`，280 bytes；韌體檔案基底為 `0x8000`。來源與 baseline 指紋保存在 `reference.json`，產生 reference 時實際讀過十二區域的完整 object；可攜驗證不需要那份歷史 build。

新來源誠實提供三個函式，而非偽造一個 280-byte FUNC：canonical `__tsl9v4160_call_8a56` 是真 GLOBAL FUNC8，body 是真 LOCAL FUNC270，return leaf 是真 GLOBAL FUNC2。它們在原 280-byte allocation 依序配置；沒有 ABS 入口 provider、整段原始組語或原 BIN 產生程式碼。統計為 **13 個原始區域、15 個真實 provider FUNC、930 bytes**，其餘區域仍來自原 carrier。

原八個私有角色包含七個 control target，以及一個 PC-relative anchor；不是八個 branch。原十一個 owned RELA 由九個 control reference 與一組 HI/LO 構成。新三個 RELA 是 offset4 的標準 branch、offset128 的真 RAM HI，以及 offset132 指向新 local anchor 的 LO，全部 addend0。八個其餘 control reference 由實際編譯 CFG 承接；這項局部 CFG／frame 證據在獨立 ABI 審查中核對，不能只因標籤消失便宣稱成功。

九個已知外部入口都維持指向 `0x8A56`：

| PC | 指令寬度 | rd | link |
|---|---:|---:|---|
| 0x8368 | 2 | 1 | 0x836A |
| 0x841C | 2 | 1 | 0x841E |
| 0x9BE0 | 4 | 1 | 0x9BE4 |
| 0x135A8 | 4 | 1 | 0x135AC |
| 0x13B30 | 4 | 1 | 0x13B34 |
| 0x13B80 | 4 | 1 | 0x13B84 |
| 0x13C2E | 4 | 1 | 0x13C32 |
| 0x13EAC | 4 | 0 | 不寫 RA |
| 0x14738 | 4 | 1 | 0x1473C |

`0x9BE0` 在 ET_REL 中仍有 JAL placeholder；檢查以真 RELA 與最後 linked bytes 為準，不要求未連結立即數已是最終位址。所有 8258 個非 TX RELA 必須保持原語意，僅容許 canonical target 的 size metadata 由280投影為8。FUNC8 是誠實角色差異，不單獨構成 runtime 失敗或完整相容證明。

來源檢查獨立重建67步驟的完整順序：46個新編譯 TU（34 raw、11 typed C/C++、1直接 assembler）、11份 IR、三個明示 Python ordering stages。45份 `-MD` 各自綁定 target、primary source、forced adapter；實際閉包是78個 project dependency、14個 generated input、一份 compiler resource header，另有一個不經預處理的 entry assembly direct input。85個 source pins 中的 canonical `src/tx_native.c` 僅作來源身分對照，沒有被誤稱為此次實際編譯的 TU。

每個 TX provider 都有一個 attributes mapping marker，包含 assembler input。它們在 merge 後形成三個額外 ABS `$d` metadata，與禁止的數值入口 provider 不同。新 `.llvm_addrsig` 只有 typed body 的 `02` 一個 byte；它不進入 linked ELF/BIN。

預設命令只驗來源、原始 reference 與 metadata，輸出 `actual_source_compile_provenance_replayed:false`。加入新 build 的 receipt 才會讀回所有真實來源／命令／dependency／object／ELF／BIN，輸出該欄位為 true：

```sh
python3 -B check-review.py --project-root /path/to/project --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python3 -B check-review.py --project-root /path/to/project --firmware /absolute/ID-2966-V4.1.60-decoded.bin --receipt /absolute/new-build/c/verification.json
```

真正執行的控制包含每語言9個實際 ELF byte mutation，以及14個獨立 recipe／dependency／receipt countercase。它們檢查假 FUNC280、ABS 入口、錯誤 local/global、PCREL addend、interior incoming、RA/link、RET、錯誤來源、stage bypass、語言、預處理、dependency association、漏列 IR、外層日誌、preflight argv 與 direct ASM stability pin。沒有重跑未改變的 HOST 行為矩陣。

此映像需要窄 entry assembly 與明示既有 instruction-word ordering，不能宣稱是 pure Clang 或一般 C ABI 的完整重建。完整原始 ABI、未知 ROM 回應、computed/interior reference 不存在、非同步行為、code-as-data、硬體、BOOT 身分、燒錄與 OTA 相容仍未證實。所有執行旗標維持 false；這份審查不提供裝置操作或可燒錄宣告。
