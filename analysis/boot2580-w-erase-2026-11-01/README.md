# ID2580 BOOT W 擦除呼叫：靜態指令核對

## 範圍與重現

只分析保存的官方 ID2580 decoded BOOT（12,288 bytes，SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`）；base `0x1000` 是分析座標，不是實測載入位址。延續[數值頁範圍](../boot2580-w-range-2026-11-01/README.md)，不推廣至其他 BOOT 或實機安裝版本。

`python -B analysis/boot2580-w-erase-2026-11-01/check.py` 唯讀全檔、固定 listing；逐條核對 W 的 `[2260,229e)`、wrapper `[20e6,2126)` 和全部直接 helper `[2fe2,30a8)` 共 119 條連續指令的原始 bytes。listing 以 radare2 `-n -q -a riscv -b 32 -m 0x1000 -c 'pDj N @ ADDRESS'` 對該檔逐區產生；`listing.json` 保存地址、bytes、opcode 和工具提供的跳轉資訊。checker 固定 listing 的 SHA-256，並不依賴 radare2 安裝；它**不重新解碼 mnemonic 或證明反組譯語意**。原始指令可用上述命令獨立重解，區長分別為 62、64、198 bytes。

負向測試在記憶體各改一處 W call、erase call、erase 位址 store、poll branch、program store、program loop、program call；繞過全檔 hash 直接進同一逐指令 gate，均須拒絕。另拒絕缺列與多列。這是靜態證據完整性測試，不是對設備注入故障，也不能獨立驗證所有控制流語意。

## 直接指令鏈與分支

以下從已通過 W 前置 guard 且到達 `2260` 開始，假設記憶體存取有效及被呼叫者依原程式正常返回。頁碼與 source 來源及 guard 見上篇；非同步干擾或破壞呼叫保存暫存器時不能保證四次。

* `2260/2262` 設 offset=0、limit=1024；`2266/226a` 分別組 a1 source、a0 destination；`226e` 加 256、`2272` 呼叫 `20e6`、`2274` 比較迴圈。依正常返回與暫存器保存條件，呼叫 offset 0、256、512、768。
* `20f6` 清 CSR `0x800` mask 136；`20fa → 2fea` 寫 unlock keys，`20fe/2102 → 2fe2` 對數值 `0x4002200c` 寫 49。`2106/2108 → 3016` 傳原 destination；返回後 `210c/210e/2110 → 3044` 用原 destination 與 source。`2114 → 3008` 設控制位，再 `2118` 設 CSR mask 136；不是保存與恢復原 CSR 值。wrapper **沒有測試 erase 的返回碼後再決定是否 program**。
* `3016..3042`：控制暫存器 `0x40022010` OR `0x20000`，`3020` 將 a0 下對齊 256，`3028` 寫 `0x40022014`，`302c/3030` 對控制值 OR `0x40`；`3032/3034/3036` 反覆讀 `0x4002200c`，只要 bit 0 非零便回 `3032`，清零才清控制 bit `0x20000` 並 return。沒有 timeout，也沒有另一個明示錯誤分支。bit 語意與寫入的硬體效果不在此證明。
* `3044..30a6` 將 destination 對齊 256、設定控制 bit `0x10000`，依序輪詢 status bit 0、bit 1；`306c..3084` 每次讀 source word 並 store 至 destination，再輪詢 bit 1，offset 加 4 至 256；然後設控制 bit `0x200000`、輪詢 bit 0、清 `0x10000` 返回。這是 64 次 word store 的條件式靜態路徑，不是已完成寫入的證明。
* 回到 W，`2282` 讀 destination，`2288` 讀 live source；`228a` 不等則跳 `21e2` 靜默返回；相等迴圈完成後 `2294..229c` 請求空 W 回覆。僅這條 readback 不相等分支是此處看見的寫後資料差異處理；它不是可辨識的 erase 狀態或錯誤碼。

## 已擦與失敗：不作硬體假設

在上述完整 wrapper 與 erase helper 路徑，沒有在發 erase 前讀 destination 或檢查「已擦」而跳過 erase；無論目的內容如何，正常控制流均發相同 erase 請求。這**不證明控制器實際擦除、擦除粒度或沒有其他路徑預先擦除**。輪詢 bit 一直為非零時原程式可能無限等待，後續 program/readback 不到達；匯流排 fault、復位、電源中斷或控制器拒絕等效果不由靜態指令確定。bit 清零也不能單獨證明成功，因為此路徑未解讀其他錯誤位或做 erase-blank check。readback 相等不證持久性、完整映像或可啟動性。

沒有連接設備、送封包、刷寫、執行 ISA 或模擬實體 Flash。地址、別名、實際擦除幾何與設備／版本配對均未知。
