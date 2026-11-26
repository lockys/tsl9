# v4.1.60：post-config 返回至首次 registration

本輪接通 post-config、外層 initializer、APP 返回尾段、setup 與首次 `40080` registration。符合下述名義配置與保存條件時，registration 返回舊索引 `3`，將 count 改為 `4`，並把 callback address `1995c` 寫入 `20004800`。證據止於 APP 返回位址 `19b30`，尚未涵蓋該處的 GP 相對索引保存及後續 constructor。

程式：[check_v4160_first_registration_chain_static.py](check_v4160_first_registration_chain_static.py)。逐指令證據：[v4160-first-registration-chain-static.json](v4160-first-registration-chain-static.json)。只有原 bytes、解碼、控制流與封閉算術驗證，未執行或模擬韌體、provider、MMIO、callback 或裝置；C 重建覆蓋率未增加。

## 三層返回值

先前 [shortcut 保存驗證](v4160-post-shortcut-preservation-static.zh-TW.md) 與 [mismatch 暫存區／free 驗證](v4160-mismatch-temp-release-static.zh-TW.md) 是兩條替代路徑，各自需要自己的前提，不能把相等與不相等 readback 條件同時套用。

| 層次 | 原指令效果 | 返回值 |
|---|---|---|
| post-config | shortcut 或名義 mismatch 正常返回 | 分別為 `1` 或 `0` |
| 外層 initializer | post call 後 `LI A5,0`，還原 saved words，再 `MV A0,A5`、RET | 強制 `0` |
| APP builder | initializer 回 `0` 時跳過 `19af0` 自迴圈，呼叫 `19106(64,1)`，其後不改 A0 | `W OR 64` |

`W` 是 helper 當次從 `40021014` 讀出的 32-bit word。`19106..19124` 完整 30 bytes／12 指令包含兩個分支：A1 非零時 OR 後寫回；A1 零時以反相 mask AND 後寫回。此 APP 呼叫使用非零分支，因此 A0 的 bit 6 必為 1，返回非零。不能將這個 APP 回覆當成 initializer 的狀態碼。

helper 只定義 A0／A4／A5，無 frame 或 nested call；未改 S registers、GP、SP、RA。APP 接著還原 RA／S0，向 `e000e104` 寫 `80000000`、向 `e000e108` 寫 `1`，釋放 96-byte frame 後返回。以上僅證明 CPU 指令的存取地址與資料，沒有執行硬體，也沒有證明 MMIO 的實際效果。

## setup 至首次註冊

重用完整 [APP 來源與 wrapper 驗證](v4160-app-config-source-static.zh-TW.md)、[hook 來源驗證](v4160-optional-hook-origin-static.zh-TW.md) 與 [registration 合約](v4160-task-registration-static.zh-TW.md)：

1. setup 的 `8ea8` 呼叫 `199e2` builder，返回後 `8eac` 直接呼叫 `19b16` wrapper，沒有檢查 builder 的非零 A0。
2. wrapper 從 fresh `U32[40080]` 載入 callee，重新建立 A0=`1995c`，在 `19b2e` 間接呼叫；返回 link 是 `19b30`。
3. 兩版候選 slot `400a4` 分別指向 `43c7e`／`43d0a` initializer；slot `40080` 分別指向 `43c4e`／`43cda`。完整 48-byte registration leaf 已重驗，但這些候選內容不代表裝置實際 installed 值。

使用 [首次 table 範圍證明](v4160-initial-table-extent-static.zh-TW.md) 及 post-config 的條件式輸出：

```text
T = 200047f4
n = 3
c = N0，N0 ∈ {14,17,…,212}
n < c，因此不走返回 255 的滿額分支
先寫 U8[ctx+1] = 4
再寫 U32[T+4*3] = 1995c
返回 A0 = 舊 n = 3
```

callback word 範圍 `[20004800,20004804)` 位於最小 table 終點 `2000482c` 之前，也位於配置的 payload 內。count 與此 word store 互不重疊，且均不碰 hook word。寫入 callback address 不等於執行 callback。

## 保存條件與界線

整條串接要求：前輪 fresh 名義 heap／有效且仍 owned 的 table、capacity、count=3 已成立；所需 code 與各 fresh provider slot 符合候選；各 call 正常返回；saved frames／globals／heap 互不別名且資料完整；所需 context 不被改寫。

外層尾段僅讀 saved words；APP 尾段與 helper 的 stores 是上述固定 MMIO；wrapper 呼叫前僅寫自己的 frame。在**沒有破壞所需 RAM／context 的 MMIO 副作用、interrupt／DMA／重入或外部 writers**這些額外條件下，可把 T／c／n／ownership 與 post-return 當時的 hook word 保存到首次 registration 返回。單純數值地址不相交，不能證明硬體及非同步行為也保存 RAM。

此處只保存 post-return 當時的 hook word，沒有證明它實際等於 `197b8`。較早 field44／copy 來源與其他 writers，以及真正 installed provider，仍須獨立釐清。也尚未證明 `19b30` 之後的 GP+388 byte-save、constructor `19b56`、fresh `40074`、optional hook 的完整串接與後續物件保存期。

## 驗證

一般與 Python `-O` 模式均重播完整 ledger。檢查包含兩版候選與 APP／SDK 原檔身分、原 Xwchc vectors、既有依賴合約、完整 helper 與返回尾段 operands／CFG、256 種 layout、65,536 個 RMW 低 word 等式及高 word 邊界；42 個逐指令 operand mutation 均須被拒絕。這些是靜態證據檢查，不含 target ISA 執行器。
