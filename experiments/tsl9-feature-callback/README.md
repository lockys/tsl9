# 回呼、封包校驗與狀態路徑

[English](readme.en.md)

同一份 [C 原始碼](src/callback.v4.c) 已實際編譯為 C11／C++17：七段共314B、109指令、31個架構區段。20筆直接控制及6筆PC-relative relocation做純資料原位址編碼後，314B全部與官方 ID2966 V4.1.60 BIN 相同。不是一般 C ABI 或可刷寫韌體。

| 原入口 | 已重建的靜態行為 |
| --- | --- |
| 828C | 即時讀取2000BFB4，回傳是否至少4 |
| ED00 | 16-bit header加總與length指定的payload，跳過A1索引，逐步保留低8bit |
| 1069E | 以A1=7呼叫ED00，與重新讀取的byte[then-live S0+10]比較 |
| 106E8 | 檢查後再次讀取計數byte並遞增；兩次讀取間的IRQ不保證值不變 |
| 1074C／107C0 | 更新狀態及條件式註冊工作；所有真正外部函式保持未解析 |
| 1083C | 10846透過A5呼叫回呼；非零時清除狀態並註冊107C0 |

C負責加總、位移、比較、常數及一般記憶體。SP／RA／S0、原指令控制與PC效果是架構介面。v1／v2正常編譯成功，但固定LLVM交換ED24加法的兩個來源暫存器，未通過逐位元組檢查；v3調整空輸入介面的宣告順序，維持C加法並得到原始編碼。失敗試驗與原件保留，未放寬比對。

```sh
python3 experiments/tsl9-feature-callback/build-v4.py --tool-dir "$LLVM_BIN" --trial YOUR_NEW_TRIAL
python3 experiments/tsl9-feature-callback/build-v4.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-feature-callback/build/trial-v4
```

需要既有LLVM與官方BIN；不下載依賴。第二行只核對本機保留原件。無硬體、網路、HOST模型、ISA或目標程式執行；沒有新的畸形輸入／負例矩陣。指標界限、IRQ、實體記憶體、常駐ROM、9124排程與所有外部回呼仍未證明。

值得後續考慮：僅讀的封包校驗失敗計數、回呼拒絕原因及待排程工作狀態，協助區分傳輸問題與功能拒絕。尚未實作；不能由本次靜態結果推論已可在硬體運作。

## 真實物件整合

v4將兩個clear呼叫綁到既有的strong `tsl9_queue_external_820c` 定義，不重複放入helper或新增ABS替身。C／C++皆實際部分連結為5402B code＋60B table、432 FUNC、412 RELA。已補上原圖三個直接依賴；展開後仍有75個未解析符號（73個直接、2個literal-code參照）及額外間接／常駐依賴，並非完整韌體圖。

```sh
python3 experiments/tsl9-feature-callback/integrate-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-feature-callback/build/graph-v2
```

98組來源比較／196個物件通過；原96組與577個artifact記錄不變。父元件採精確增加一檔／一單元的範圍重驗，不把新metadata冒稱舊完整收據原樣重播。單體與src版ELF的local FILE名稱不同；code、relocation carrier及其他parsed symbols相同，分別釘選真實雜湊。ET_REL的VMA仍為0，不能執行或燒錄。
