# v4.1.60 ID 2047 狀態更新與實際 byte getter

2026-11-26。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批從 `0x14d2e` 執行原 mode getter、mode 1 ID 樹、ID 2047 的 `[0x152f4,0x153ba)` 狀態流程，並串入 `0xcd4e` 原 getter。所有資料、CSR 與 copy 控制均為本機合成模型，不操作設備。

## 三種子命令

P=record 指標，子命令為 `U8[P+3]`；下列欄位均是相對 GP 的 byte，fixture 的 GP=`0x20004000`：

| 子命令 | 原指令資料操作，依序 |
|---|---|
| 1 | 讀 byte8；寫 `U8[GP+348]=((byte8&7)<4)`；讀 byte4；寫 `U8[GP+355]=((byte4>>3)&1)` |
| 2 | 讀 byte8；寫 `U8[GP+353]=((byte8&0x18)==8)` |
| 3 | 讀 byte4；寫 `U8[GP+356]=((byte4&0x70)==0x10)`；讀 byte5；查下述跳表，再寫 GP+357 |
| 其他 byte 值 | 不再讀其他 record byte、不寫全域資料，直接走 epilogue |

上述比較結果存為 byte 0／1；不替欄位指定未證明的產品功能名稱。本段沒有先讀取 record 長度或 tag；不能把直接 fixture 當作正常 ingress 的完整可達性證明。

## 子命令 3 的八項原跳表

selector=`(byte5>>2)&7`，表位址 `0x1a6d4`。執行用表是原 APP 內的相對 word，不另外合成。先前 GP+356 的 store 發生在讀表之前。

| selector | 原入口 | GP+357 結果 |
|---|---|---|
| 0 | `0x15364` | 7 |
| 1 | `0x1536c` | 8 |
| 2 | `0x15370` | 見下述 K／H／J／getter 分支 |
| 3 | `0x15394` | 見下述 K／H／J 分支 |
| 4／5／6 | `0x153b4` | 0 |
| 7 | `0x153b0` | 9 |

令 K=`U8[GP+354]`、H=`U8[GP+348]`、J=`U8[GP+352]`：

- selector 2 先讀 K。K 非零時執行原 `0xcd4e`，getter byte 非零→結果 10，零→5。K 為零時讀 H；H 非零→1，否則再讀 J，J 非零→1，否則→3。
- selector 3 先讀 K。K 非零→6。K 為零時讀 H；H 非零→2，否則再讀 J，J 非零→2，否則→4。

H 非零時不讀 J；K 非零時兩者均不讀。其餘 selectors 不讀 K／H／J。本批的精確 trace 分別核對這些短路，而不是只比最後結果。所有路徑只寫該分支指定的欄位，不把其他舊狀態清零。

## `0xcd4e` 已串入原指令

此函式為 10 bytes：AUIPC A0、LBU A0、RET。絕對資料來源是 `U8[0x2000bf27]`，不讀傳入 record，也不呼叫其他函式。只有 A0 被改寫，沒有 stores。

由完整 outer 進入時，呼叫入口 A0=`0x1a6bc`、RA=`0x1537a`、SP=`caller_SP-16`、S0=P。此時 GP+356 已寫入、GP+357 尚未寫。測試在入口檢查這些邊界，再執行 getter 原碼，核對來源 byte、其他暫存器保持及無 stores，然後執行原 handler 後段返回 caller。此處沒有合成返回或 callee 保存假設。

最後 epilogue 按 RA→S0 讀回 frame，再恢復 SP；A0 結果為：

- selector 2 且 K 非零：保留 getter 的完整 byte（0–255），不是正規化為 boolean。
- 其他路徑：保留 `0x1a6bc` 跳表 cell 位址。

因此 GP+357 的 5／10 分類值與 A0 不同，不可把其中之一直接命名為此 handler 的成功碼。全程核對 RA／SP／S0 恢復、其他未用暫存器保持、record 不變，以及整個 16-byte 全域 fixture 的 canary。

## 重現與矩陣

```powershell
python analysis/test_v4160_state2047_cpu.py --standalone-only
python analysis/test_v4160_state2047_cpu.py
python -O analysis/test_v4160_state2047_cpu.py
```

獨立部分只需標準庫、原 APP 與既有 outer／有限 CPU 模組。完整串接另外依賴既有 consumer/filter/classification 模組及本機 SDK copy **參考候選**；可用 `--carrier` 指定路徑。串接前核對 carrier 長度、SHA-256、槽位與 body SHA-256，候選資料不另行上傳。

```text
PASS: 256 subcommands; 65536 sub1 byte pairs; 256 sub2 bytes; 65536 sub3 field pairs; 648 state probes; 65536 K/getter pairs; 48 sequential triples; 3 mutations; actual cd4e getter
PASS: 3840 original consumer/state/scan completions; 48 actual getter calls; candidate-only upstream copy/probe premise
```

| 組數 | 覆蓋 |
|---|---|
| 256 | 子命令 byte 全值 |
| 65536 | 子命令 1 的 byte4×byte8 全值 |
| 256 | 子命令 2 的 byte8 全值 |
| 65536 | 子命令 3 的 byte4×byte5 全值，H／J／K 固定零 |
| 648 | H／J／K 各取 0／1／255 × 八個 selector × getter 0／1／255 |
| 65536 | selector 2 下 K×getter byte 全值 |
| 48 個三步序列 | 同一 CPU／全域資料依序執行子命令 1→2→3；不在步驟之間重設全域狀態 |

序列先檢查子命令 1 寫入的新 H，再由子命令 3 的 selector 2／3 實際讀取；另變動 J／K／getter。這是指定輸入矩陣，沒有宣稱所有 record 與全域 bytes 的笛卡兒積已窮舉。

三項記憶體複本變異分別把比較門檻 4 改為 3、selector 0 表項改到 selector 1 入口、getter 改讀相鄰 byte；均須由精確存取或 getter 結果檢查抓出，不以未知指令失敗充當通過。原 APP 與共用 CPU 均未修改。

## consumer 到返回的串接

3840 組為五個子命令值（0／1／2／3／255）×八個 selector×H／J／K 各取 0／255×三種 getter byte×四組 byte4／byte8 fixture。每組都從 slot 17 執行原 consumer snapshot、清除 queue ID、空匹配 filter、分類、完整 outer、狀態 handler，再繼續原剩餘掃描至 caller 返回；其中 48 組實際執行 `0xcd4e`。

上游 copy 仍是已釘定的 SDK **參考候選**，並非安裝 provider 的證明；分類的 `0x81aa` 仍使用指定正常返回 1、保存 SP／S／GP／記憶體並改寫 caller-saved 暫存器的明示前提。mode getter、ID 樹、本機狀態流程和 `0xcd4e` 都執行 APP 原碼。

逐例核對完整 queue、snapshot、CSR=0x88、copy 控制 word 恢復、caller SP／S0–S7，以及上述狀態存取。沒有實體設備／IRQ 行為或其他 callees 的成功聲明。

既有 `feature_dispatch_handlers.c` 已包含這段 C；本批補上狀態資料流與實際 getter 證據，沒有新增 C/C++ 重建 bytes 或重算覆蓋率。仍需追查這些狀態的後續消費、mode 1 其他 call／tail 函式及未知 provider 綁定。
