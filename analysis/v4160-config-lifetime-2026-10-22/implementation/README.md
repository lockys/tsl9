# OTA reply：獨立四位元組 C object

[English](readme.en.md)

這輪實際 C11／C++17 元件為 **550B／186 指令／48B frame**。真正的四位元組、四位元組對齊 volatile reply object 配置在 SP+12..15，前兩 bytes 是原本的 reply 資料。其指標相對共同 entry SP 為 -36，與原始 reply 相同；最低保存槽為 S6@SP+16，因此整個四位元組 object 不重疊保存槽。

| 實物 | bytes／指令 | 保存槽數 | reply 前兩 bytes |
| --- | --- | --- | --- |
| 前輪封存版本 | 556／188 | 9 | SP+10、11 |
| 完整 Flash base 先形成 | 552／186 | 8 | SP+14、15 |
| 四位元組 reply backing | 550／186 | 8 | SP+12、13 |

只做兩個有來源依據的 source profiles：第一個在 range guard 後使用原值不變的 native +r identity port，讓完整 Flash base 在 copy 呼叫前形成，消除跨 call 保存的分拆常數；第二個將 native reply 宣告為標準 C11 `_Alignas(4)`／C++ `alignas(4)` 四位元組陣列。沒有新增 compiler flags、額外初始化或改為傳送四 bytes。共享演算法、effects 順序、全部八暫存器讀寫 bridge 與 memory clobber 保留。HOST port 是 identity，native 宣告不編入 HOST，未重跑未變更的 HOST 矩陣。

這只閉合獨立 object 與所選 reply 數值位址。原始函式是 530B；新元件仍多 20B、仍多保存 S6，save order、call RA、未知 resident 對 S／GP／SP 的觀察與 callback lifetime 尚未全部證明。完整原始 ABI、placement、installed ROM／BOOT、OTA 仍為 false。現有正式模型與 BIN 未替換，無新 link／BIN、RV32／ISA 執行或硬體操作。

## 重現

```sh
sh experiments/tsl9-v4160-ota-reply-object/verify.sh --project-root "$PWD" --tool-dir /path/to/llvm/bin --language both
```

輸出只能位於 model/build 的全新目錄，省略 build-root 會使用 UUID。每個 mode 有 object、IR、完整 disassembly、-MD、工具 logs 與 verification.json。九個 callee／callback 符號維持真 UND，20 個 RELA 未用 numeric provider 解決。

case implementation/probe.py 支援 `--project-root ROOT --replay MODE/verification.json`。check.py 預設 metadata-only；明示重複 `--receipt` 才重讀實際 recipe、sources、tools、resource header、MD、artifacts 與 reply storage。發布 case 路徑是 analysis/v4160-config-lifetime-2026-10-22，工作路徑是 apk-analysis/tsl9-v4160-config-lifetime-2026-10-22。

Python／sh 入口保持可攜；本輪實測與工具身份是固定 Windows LLVM，不表示 Linux／macOS 編譯器已驗證或准入。第一個 552B probe 的原 source snapshot／receipt 留在 build/full-base-v1；當前 source 已是四位元組版本，不能以當前 root 偽稱舊 receipt source replay。僅發布來源與 metadata，不發布 opaque objects。原始 BIN 僅供原始證據，不作產碼輸入。
