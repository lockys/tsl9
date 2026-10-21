# Flash 暫存器前綴與自動 frame 保存：獨立審查

正式 C11／C++17 元件皆通過獨立靜態檢查。五個 Flash leaf 函式共 **198 位元組，完全等同原版機器碼**；program 為 100 位元組／38 指令，全部原始指令邊界及五個已知迴圈／複製進入角色均保留。六函式元件共 262 位元組／99 指令；wrapper 的六位元組保存順序差異仍存在。[English](readme.en.md)

`receipts/c.json`、`receipts/cpp.json` 綁定正式 `native-final` 產物，元件 ELF SHA-256 為 `575b2e1009437c77d71081fffeaa32988ff10b23c78decb01e9ad976c5e6c9c7`。每種語言另有 **18 個實際 ELF 位元組反例**，全部拒絕；四個未編譯 MIR 文字反例另列，不冒稱編譯測試。

## 逐指令保存順序

IRQ `9A42` 的 SP 皆先減 16。原版 `9A44..9A4A` 依序保存 `S2→SP+0`、`RA→+12`、`S0→+8`、`S1→+4`；LLVM 輸出依序保存 RA、S0、S1、S2 到相同各自槽位。四個二位元組指令共差八個位元組，`9A4C` 起所有內容與原版相同，包括最後從 live frame 重新載入 RA／S0／S1／S2。

Flash wrapper `9C0A` 的 SP 皆先減 32。原版 `9C0C..9C10` 保存 S0→SP+24、S1→+20、RA→+28；LLVM 輸出為 RA、S0、S1。三個指令差六個位元組，`9C12` 起相同：S1 接收 A0、`9C14` 將 A1 存到 SP+12，隨後建立 CSR mask136，並保留所有呼叫、重新載入及返回角色。

兩種順序在全部 store 完成後形成相同 frame；store 本身不改寫其他 GPR。但中途已寫入的槽位、可能第一個發生 fault 的位置及非同步觀察不同。回條逐指令列出這些 frontier，未將完整 frame 相同當成逐點等價。

## 固定 backend 的實測原因

以相同編譯器、來源及原有 profile，只在 `prologepilog` pass 前／後停止，共取得八份 MIR：C／C++ × IRQ／wrapper × 前／後。沒有 profile 搜尋或目標執行。所有來源、adapter 及編譯器皆綁定前後雜湊。

IRQ 在該 pass 前沒有 stack object 或保存指令；pass 後新增 16 位元組 frame 與 RA／S0／S1／S2 spill。Wrapper 在 pass 前只有 20 位元組 source-slot 物件；pass 後新增 32 位元組 frame 及 RA／S0／S1 保存。這些 store 位於所有 C 本體及 inline primitive 之前；實際 JAL primitive 皆誠實宣告 RA clobber。

因此目前差異來自自動 frame lowering；一般 C 宣告／生命週期順序沒有直接排序這些 backend store 的機制。此證據不代表所有 C 寫法皆不可能。省略 RA 或 callee-save clobber、重複手動 store 並不能構成可靠修正。明確標示的來源自有 ABI scheduling pass 必須另外驗證；本封存的 native 元件**未套用**該 pass，也未宣稱編譯器已輸出原始保存順序。

## 原生合約與可攜重驗

六個實際 ET_REL 物件經宣告的五個 JAL fixup 後，逐位元組等於連結元件。Leaf 無額外呼叫或資料配置；LLVM IR 的 RV32 target、volatile i32 觀察次數及非 naked 函式亦核對。正常 GPR 殘值及存取順序由原始指令身分約束；wrapper 要求有效 frame、完成存取、輪詢終止與無未建模非同步干擾。

先前全映像 20 個進入合約的原始位址／寬度／RA 角色保留於回條，原始元件 entry 均未移動。此輪元件不含那些外部 caller，故明確標為 `new_whole_image_incoming_reverified=false`；沒有把舊 caller 證據冒稱新全映像驗證。

```sh
python3 -B apk-analysis/tsl9-v4160-flash-register-prefix-2026-10-22/ABI-review/check_seal.py --project-root .
python3 -B apk-analysis/tsl9-v4160-flash-register-prefix-2026-10-22/ABI-review/review.py --project-root . --component-folder MODE_DIR --report independent-result.json
python3 -B apk-analysis/tsl9-v4160-flash-register-prefix-2026-10-22/ABI-review/review.py --project-root . --replay independent-result.json
```

Windows 可用 `python -X utf8 -B`；`review.sh` 提供同參數的 POSIX 包裝。Shell 包裝僅靜態檢查，沒有執行 WSL／Git Bash。一般重驗只讀封存 MIR、原始韌體、固定來源證據與實際元件，不需舊 W 路徑物件或 Windows compiler。`diagnose_frame.py` 是保留的八次編譯診斷生產器，與只讀重驗分開。

本 native seal 僅涵蓋列出的成員，排除 preliminary 回條及另行審查的 `frame-pass-review/`。整個工作維持離線，無目標 ISA 執行／模擬、實體 I/O 或新 BIN。硬體、ROM、未知計算式內部進入點、完整非返回／非同步與 OTA 成功皆未由此證實。
