# v4.1.60 callback 表消費至 `0x9f7a` 的原指令驗證

2026-11-26。使用 76800-byte decoded APP，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。在有限 RV32IMC 執行器內執行原指令；記憶體、事件與 provider 指標均為離線 fixture，不操作設備或網路傳輸。

本批補上 [註冊 gate 驗證](v4160-register-gate-cpu.zh-TW.md) 中當作 key 的 `0x9f7a` 函式體，以及真正消費表 key 的 `0x901a`。既有 C 對應為 `src/native/receive/callback_table.c` 及 `src/native/receive/output_dependencies.c`；本批未重建 C，也未增加覆蓋百分比。

## `0x9f7a` 與註冊 gate 的 K 判斷不同

GP fixture 為 `0x20004000`。先讀 `U32[GP+84]` 指標，再讀 config+8 bit4。

| 條件 | `U8[GP+172]` 結果 | 返回 A0 |
|---|---|---|
| config bit4=0 | 0 | 保留傳入值 |
| bit4=1，`U8[0x2000bee1]=0` | 0，不讀 K | 0 |
| bit4=1，getter 非零 | `(K ^ 1) & 1`，K=`U8[GP+354]` | getter 完整 byte |

啟用時 frame=16 bytes，只保存 RA。執行原 `0x8202` getter，再選擇性讀 K，**先恢復 RA，再寫 GP+172，最後恢復 SP**。停用時不建立 frame，讀 config 後才清 GP+172。所有路徑都覆寫舊 GP+172；相鄰 byte 保持。

註冊 gate `0x9fc8` 使用完整 K byte 的零判斷，僅 K=0 才尾跳 `0x9124`。callback 則看 K 的最低位：K=2、254 等非零偶數仍寫 1。對全部 256 個 K，存在 **127 個非零偶數**會呈現「gate 不註冊、callback 寫 1」。不能把 K 一律當布林值簡化。

callback 保持 S0/S1、GP、SP 和 caller RA；除了 A0/A5 及暫時的 RA/SP，沒有其他暫存器變化。此處傳入 A0 即使是非零 payload word，也未被解參照。

## `0x901a` 一次只消費最低事件 bit

輸入 A1 作為事件 mask；掃描 bit0..14，取第一個 set bit。表為 `0x2000be08`，15 槽、stride12，欄位為 flag byte(+0)、callback key word(+4)、payload word(+8)。

1. 沒有低 15 位事件時返回 0；bit15 不被掃描，即使輸入只有 bit15 也返回 0。
2. 有選中槽時先讀 key。key=0 不讀 flag/payload，不清表、不呼叫，但仍消耗該事件 bit。
3. key 非零時依序讀 flag byte、payload word。flag=0 **先清 key，再清 payload，才間接呼叫原 key**；flag 非零則保留表內容。
4. 間接呼叫入口 A0=原 payload、RA=`0x905a`、SP=caller_SP−16、S0=index、S1=原 A1。JALR 清除 key 最低 bit。
5. callback 正常返回後，A0 被覆寫為 `(S1 ^ (1 << S0)) & 0xffff`，恢復 RA/S0/S1/SP；每次最多處理一個槽。callback 返回值不影響剩餘 mask。

原 `0x9f7a` 保持消費者使用中的 S0/S1，因此可直接執行 `0x901a → 表中 key → 0x9f7a → 0x905a → caller`，最深 SP 為 caller_SP−32。對其他未知 key，測試只驗證到其入口，不替它假設正常返回或保存規約。

`0x901a` 不讀 `[0x40050]`、`[0x40058]`，也不呼叫計時、copy 或 free provider。不能將這條表消費路徑當作 provider 的身分或事件投遞證據。

## 可重跑的驗證

腳本：[test_v4160_callback_dispatch_cpu.py](test_v4160_callback_dispatch_cpu.py)。使用 `check()`，Python `-O` 不會移除檢查。共享執行器只增加標準 C.XOR 與 RV32 SRA；另在原址測 46 組指令向量，包括負數算術右移及 shift count 取低 5 位。

```text
python analysis/test_v4160_callback_dispatch_cpu.py
python -O analysis/test_v4160_callback_dispatch_cpu.py
python analysis/test_v4160_zero_id_queue_cpu.py
python analysis/test_v4160_register_gate_cpu.py
```

一般模式及 `-O` 的新腳本輸出相同：

```text
PASS: 196608 callback config/ready/K cases; 65536 full ready/K bytes; 1024 overwrite/input cases; 127 nonzero-even K gate differences
PASS: 46 original SRA/C.XOR vectors; 65536 event masks; 240 opaque callback boundaries; 1200 actual 901a-to-9f7a chains; 15 registration/injected-event chains; 4 mutations
PASS: exact access/store order and restored frames; nonzero payload stays opaque; event/timer/free providers NOT executed
```

範圍說明：196608 組為全部 config byte × ready={0,1,255} × 全部 K byte；另 65536 組為 config=16 下完整 ready/K byte 矩陣。mask 窮舉是 **全部 16-bit 輸入的空 key 路徑**，不代表全部 32-bit mask 或所有 callback 狀態。未知 key 邊界另測每槽、flag={0,1,2,255}、payload={0,1,0xdeadbeef,0xffffffff}，包括高位 mask 與奇數 key 的 JALR 對齊行為。

1200 組原 callback 串接涵蓋每槽、一次性/保留、config 開關、ready 零/非零、K={0,1,2,254,255} 及零/非零 payload。每段都核對完整資料讀寫順序、清槽時機與 frame 恢復。

15 組註冊串接使用前批 `0x9fc8 → 0x9124`，明示 `[0x40058]` 正常返回 0 的假設，檢查實際表項後，**由 fixture 注入事件**給 `0x901a`。這證明註冊表格式可以由原消費者接續，不證明 resident provider 實際投遞事件。正常返回假設仍保留前批的記憶體/SP/GP/frame 保存限制。

四個只作用於記憶體副本的 mutation，分別取消 callback 的 XOR1、把 GP+172 store 移至鄰 byte、將掃描上限 15 改成 14、把清 key 改為清 row+0；均由指定的存取/表內容檢查拒絕，沒有以解碼失敗冒充偵測。

原指令範圍 SHA-256：

| 範圍（右界不含） | SHA-256 |
|---|---|
| `0x9f7a..0x9fb2` | `1931bd328ae360a5c9baa78666f27af2fa1da1dbde70392c9bbfa05eda5689bc` |
| `0x901a..0x907a` | `1ca1876ac3f3458d2a170336f9d1598ee7dd62f359f802ceae6739d04fda437f` |
| `0x8202..0x820c` | `50eb8fe36724cbd053357f85622399ec523a178bddbc5f14ef899385201a094b` |

後續仍需確認實際 provider 綁定、非零 payload 的其他 callback 保存/釋放合約，以及 GP+172 更新之後的可達狀態流程。`0x907a` 將 `0x901a` 傳給 `[0x40080]` 的靜態註冊點已知，實際 resident 執行語意仍未證明。
