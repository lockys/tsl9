# 佇列消費與功能入口

[English](readme.en.md) · [C/C++候選與量測](../../experiments/tsl9-queue-consumer/README.md) · [107指令原始證據](../irq-provider-2026-10-23/next-consumer.json)

已核對官方V4.1.60 `[0x12C58,0x12D92)` 的314B／107指令。原始區段SHA256為 `89905d7666bbe8295d09c752f1fcd34246847ea86c6428b539406450f8980c0f`。以下是靜態結果，沒有執行原始程式或硬體。

| 證據 | 已確認行為 | 尚未證明 |
| --- | --- | --- |
| `12C6E..12C8C` | PC衍生table初值`2000C038`，初始stride12；LHU為0便略過該槽 | opaque call後S5／S6是否維持初值；ID0實際是否可到達 |
| `12C96..12CB0` | clear CSR800、fresh `[S3+76]`間接呼叫、清then-live S0槽、set CSR800、呼叫82D2 | resident身分、完整preservation與全域IRQ lock語意 |
| `12CB4..12CEA` | 82D2回0後比較ID與then-live S4，再比長度4／bytes`B5 62`／opcode0或`5A` | 座椅或免打擾的具體對應 |
| `12D0E..12D4A` | 呼叫820C／9454／9B36，兩次12ABE，以fresh byte及then-live S4準備內容 | 被呼叫函式的功能與所有副作用 |
| `12D4C..12D76` | 檢查`5A 55`路徑；第二次resident後將frame byte26改`56`、byte31清0，再呼叫12A08 | 是否已送出硬體回覆；A1／A2是resident留下的值 |
| `12D78..12D90` | fresh `[S7]`再讀pointer+4 bit3；81AA回非零才送frame指標至14D2E | gating旗標名稱、完整dispatch功能 |

局部CFG有13個條件分支、3個jump、9個direct call、2個indirect call與唯一RET。若opaque calls返回，107個指令節點在語法圖上皆可到達；不代表所有路徑實際可行。RET後的cold blocks不可省略。來源保留80B frame與then-live實體暫存器，不擅自修改queue layout或協定。

值得後續加入的功能：

- 離線queue診斷：標示ID0與空槽表示衝突、slot被清除前後的條件。先取得可達性與同步證據，再考慮硬體計數器或獨立occupancy欄位。
- 更新／通訊紀錄的分階段狀態：區分資料接收、local dispatch、provider效果及實際功能；不能只憑結尾字元宣稱韌體執行成功。
- 版本差異檢查：本次fresh官方leaf `81AA` 是`LBU A0,167(GP)`；舊V4.1.00模型的`GP+175`不能直接移植。未讀實體晶片，不能由此認定硬體型號。

兩個短leaf已另行完成C重建：[GP旗標與有界清除](../../src/native/receive/queue_small_providers.c)，6B／18B在C11與C++17的object／診斷link中逐byte等於官方。它們只在診斷VMA0驗證，尚未與consumer實際連結，因此consumer的八個UND仍全部保留。來源與完整限制見 [provider實驗](../../experiments/tsl9-queue-small-providers/README.md)。

[正式摘要](summary.json)彙整正式收據與來源SHA。[C](receipts/queue-c.json)／[C++](receipts/queue-cpp.json)是原始可攜收據；[provider C](receipts/small-providers-c.json)／[C++](receipts/small-providers-cpp.json)及[來源整理收據](receipts/curated-source.json)是僅路徑匿名化的衍生副本，原件留本機，不宣稱可直接作原收據重播。

下一步是[188B filter](next-filter.md)、其餘直接callee，以及動態resident／caller契約。上述功能建議尚未加入原機韌體；本輪沒有產出可燒錄BIN。
