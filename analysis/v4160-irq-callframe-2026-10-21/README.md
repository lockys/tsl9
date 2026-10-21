# IRQ 呼叫框架與整合前證據

[English](readme.en.md)

新版可讀 C/C++ 位於 `experiments/tsl9-v4160-irq-callframe/`。原生元件為 144-byte main 與四個 30-byte helper，總計 264 bytes／94 指令，實際連結於五個原址；C++ 沒有額外 unwind 配置。這只通過元件範圍與正常呼叫框架檢查，完整原硬體相容 BIN 仍未完成。

| 範圍 | 已確認 | 限制 |
| --- | --- | --- |
| source-plan | 原 16-byte frame、六次四-byte JAL 與正常輸出；11 個 raw 反例 | 靜態原始來源契約 |
| cpp-profile | 舊 300-byte 核心僅加 `-fno-exceptions`，函式 bytes 不變，額外配置消失 | 此獨立實驗仍以舊 180-byte main 為目標 |
| source-review | 兩語言各 3820 案例／138312 斷言，合計拒絕 60 個編譯變異 | 不證明 native bridge／堆疊 |
| compiler-review | 兩語言各 264 bytes／94 指令；六個原址 JAL、完整 frame reload、IR 與反例 | 四個 prologue store 順序不同 |
| image-plan | 完整來源 carrier 的 34 個 C TU、691 個配置與 53 個 canonical alias 綁定 | 是整合規劃與既有物件審查，尚未生成新映像 |
| feature-candidates | 附既有來源延伸點的新功能候選 | 僅提案，未實作、未連硬體驗證 |

五項新功能候選包括免打擾狀態說明／本機間隔預覽、連線與更新階段面板、設定快照差異、離線韌體檢查與去識別診斷。詳見[提案](feature-candidates/readme.zh-TW.md)；封存文件內的原始來源連結是工作站來源溯源，發佈處的實際可用檔案請看[位置映射](evidence-locations.json)。未公開的原始 JS 不為了修補連結而複製；metadata 或文件缺檔不能冒稱已重新驗證來源。

main 的 SP 調整與 offset 10 後的 134 bytes 皆與原版一致；四個 helper 的 120 bytes 完全一致。差異只在 0x9A44／0x9A46／0x9A48／0x9A4A 四個兩-byte stack-store 指令的排列。slot 與資料集合相同，但每個中間時刻的 stack bytes 不同，不能宣稱逐指令或非同步 IRQ 等價。

```sh
sh experiments/tsl9-v4160-irq-callframe/verify.sh --language both
sh experiments/tsl9-v4160-irq-callframe/verify-native.sh --tool-dir /path/to/llvm/bin --language both
```

所有入口可直接以 Python 啟動。`cpp-profile` 的封存原 CLI 只認得原始工作站 dependency 路徑；發佈副本請用同層 `run-cpp-profile.sh --tool-dir /path/to/llvm/bin`。此 adapter 先核對封存 bytes，再只在記憶體調整 dependency 路徑，沒有修改封存檔案、compiler profile 或驗證 gate。

歷史 build 封存不搬移。metadata 綁定的既有 full-image 物件與舊 ABI 重播不能冒稱已在發佈位置重新編譯；主機與新原生元件則在交付位置實際重建。既有 76,800-byte 原始來源一致映像保持不變。本輪不執行 RV32、不模擬 ISA、不連硬體或廠商、不生成新 BIN。
