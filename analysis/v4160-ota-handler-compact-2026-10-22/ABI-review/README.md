# OTA dispatcher 縮小版：獨立來源／HOST／原生審查

[English](readme.en.md)

本輪最終共享 C/C++ 原生元件為 **568 bytes／193 指令／48-byte frame**，相較前輪 776 bytes 減少 208 bytes，仍超出原 530-byte 範圍 **38 bytes**。九個外部身分保持真 UND，沒有連結、數值 provider、stub、padding 或新 BIN。原始 530 bytes／169 指令證據沿用前輪不可變來源審查；本套件另審查新程式差異，不把舊來源證據當成新 native 執行證明。

## 實際結果

- 不變的獨立 fixture 逐 byte 重用。新 C11／C++17 各執行 **16 敘事、18 次 dispatch、898 行為 assertions**；各四個實際編譯語意反例均遭拒絕。未重編譯舊 776-byte baseline，也未替無效的 no-unroll 假設執行 HOST 矩陣。
- `source_delta.py` 機械核對所有允許差異：六個既有回覆出口改跳同一 source-site／callee 的三個共用 label；所有參數 setters 與記憶體操作順序保留。W small/page mask 維持63，U/R維持7，packet維持15。HOST header／provider／frame primitives 不變。selected source 沒有 no-unroll pragma。
- 只有 native 回覆儲存從 `oh_port` 內嵌陣列拆成 wrapper 自有的 `volatile uint8_t[2]`，port 持有指標。完整八參數 readwrite assembly bridge 與 caller／memory clobbers 逐字相同。實際 IR 只剩這個兩-byte alloca，沒有 argument struct alloca；回覆 byte stores 及實際指標傳遞仍在。
- 全 193 條指令逐欄位與獨立 LLVM 文字相等。實際四個 source/tool/IR/resource recipes、MD 三個專案輸入與 Clang `stdint.h`、產物／來源 pins 均讀回。20 RELA 為十二個 direct JAL 與四組真 callback HI／LO，另有一個 slot4C 的間接 call；九個 UND 不由假位址解決。
- 實際 quarter 是 **一個** static JAL。局部 CFG 證明 counter 從1024每次減256，兩個 A0/A1 cursor 在正常返回後各加256，單一 backedge；callee 保留三個 S 暫存器時，形成四次呼叫、offset0／256／512／768。這是有前提的靜態算術與 def-use 證據，不是執行 MCU，也不證任意 callee mutation 或原實體 S0 呼叫前狀態。另拒絕兩個實際 loop 運算元變動，以及三個既有 SP/link/GP raw 反例。

## Frame 與 alias 限制

48-byte frame 相同不等於內容相同。原碼七個 saves；新碼十個依序為 RA@44、S0@40、S1@36、S2@32、S3@28、S4@24、S5@20、S6@16、S7@12、S8@8。實際 private reply 位於 **SP+6／SP+7**，原始使用 live SP+12／13。直接把新 pointer 綁回 SP+12 會碰到 S7 save，不能這樣修。

新 C 的兩個物件可供編譯器分開分析，不證明未知 resident 不觀察數值 pointer、SP、鄰接記憶體或原始 alias。下一項契約是確認真正 packet provider 是否僅依傳入內容／長度消費回覆，而非盲目要求或允許 pointer 數字相同。HOST live-SP fixture 不等於實體 native SP 證明。原始完整 ABI／入口前綴／callee footprint／配置／ROM／IRQ／BOOT／OTA 與復原仍未知。

## 前輪文件更正

`baseline-correction.json` 精確更正舊 case 的 README.md／readme.zh-TW.md／readme.en.md 第12行「native 展開為四個 static quarter call」：實際 776-byte object 只有一筆 quarter RELA，offset658（0x292）；backedge676（0x2A4）回652（0x28C）。原獨立報告及 selected 記錄本來就是一個。四次是條件式 dynamic 次數；no-unroll 實測無縮小效果。舊封存文件與產物均未修改。

## 執行

以下以本案目錄為相對起點；`ROOT` 為真實 project 根目錄。Python/sh 入口支援原 `apk-analysis/tsl9-...` 與交付後 `analysis/...` 證據路徑；不宣稱已在其他作業系統執行 LLVM。

```sh
python3 -B ABI-review/check.py --project-root ROOT
python3 -B ABI-review/run-host.py --project-root ROOT --language both
python3 -B ABI-review/run-host.py --project-root ROOT --replay HOST_RECEIPT.json
python3 -B ABI-review/review.py --project-root ROOT --folder NATIVE_MODE --receipt NEW_REVIEW.json --firmware OFFICIAL.bin
python3 -B ABI-review/review.py --project-root ROOT --replay NEW_REVIEW.json --firmware OFFICIAL.bin
```

default 只驗 source／metadata，`actual_native_artifacts_read` 與 `actual_host_artifacts_replayed` 為 false。實際 native review／HOST replay 才各自明示 true。新 HOST build 限本 scope `build/` 且不可覆寫，執行前後皆經不可變的本機 executable machine guard。新 native receipt 須在既有 producer folder 外；省略 `--firmware` 則不讀原 BIN，重播須維持同一模式。重播不重新編譯／啟動程式。seal 只含來源與 metadata，沒有 object／IR／executable archives。
