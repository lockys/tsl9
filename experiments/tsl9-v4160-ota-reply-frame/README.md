# OTA reply frame：兩個有界 C 編譯實驗

[English](readme.en.md)

這輪保留共享演算法、全部八暫存器 asm 輸入／輸出及未知 callee 邊界，只用原值不變的 native port 限制 W offset 生命週期。HOST macro 是 identity；未重跑不變的 HOST 矩陣。

| 實際產物 | bytes / instructions | frame | 真 reply bytes |
| --- | --- | --- | --- |
| 已封存 compact 基準 | 568 / 193 | 48 | SP+6、7 |
| identity 在 quarter call 前 | 560 / 190 | 48 | SP+6、7 |
| identity 在 quarter call 後 | 556 / 188 | 48 | SP+10、11 |

兩個 profile 都實際編譯 C11／C++17，沒有新增 compiler flags。最終版本保存 RA、S0..S7，IR 中獨立的 volatile 2-byte object 不與 saved S7（SP+12..15）重疊。但 reply 相對 entry SP 是 -38，原本是 -36，因此指標／frame 修復目標仍失敗；不能把 reply 指向 saved S7。

無第三 profile、link、BIN、fake provider、opcode patch、硬體或 RV32／ISA 執行。正式 568B 模型與已交付 BIN 未替換；完整 ABI、placement、OTA 證明仍為 false。

## 重現

需要 Python 3 與既有 pinned LLVM。POSIX wrapper 可設定 PYTHON；Windows 可直接執行相同 verify.py。輸出只能建立在 model/build 內全新目錄；省略 build-root 會使用 UUID。

本輪實測為 Windows 上的固定 LLVM 工具雜湊；Python／sh 入口不代表 Linux 或 macOS 編譯器已被驗證或列入允許的工具身份。

```sh
sh experiments/tsl9-v4160-ota-reply-frame/verify.sh --project-root "$PWD" --tool-dir /path/to/llvm/bin --language both
```

每個 mode 包含 object、IR、完整 disassembly、實際 -MD closure、logs 與 verification.json。九個真 UND 與二十個 RELA 保留，未使用 numeric provider。原始 BIN 不作產碼輸入。

case implementation/probe.py 支援 `--project-root ROOT --replay MODE/verification.json`。check.py 的預設只有 metadata；明示重複的 `--receipt` 才重讀實際 sources、tools、resource header、recipes、MD 與 artifacts，缺檔即失敗。發布路徑為 analysis/v4160-allocator-callback-2026-10-22，工作路徑為 apk-analysis/tsl9-v4160-allocator-callback-2026-10-22。

第一個 560B source snapshot／receipt 保留在本機 build/offset-lifetime-v1，其歷史 source pin 不能用當前 556B source 宣稱 current-source replay。只交付 metadata，不發布 opaque objects。尺寸減少是有界減壓進展，不是原始 ABI 相容證據。
