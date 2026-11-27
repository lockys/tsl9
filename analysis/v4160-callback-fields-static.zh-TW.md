# v4.1.60：callback 欄位來源與完整 +4 消費端

本輪核對 callback 表的三個 word，並完整展開 V131 `0x4bb22..0x4bbc6`／V140 `0x4bbba..0x4bc5e` 的消費端，合計 **328 bytes／136 instructions**。另核對 APP `0x8fb8..0x8fce` 的 **22-byte／7-instruction 呼叫窗口**；該窗口不是完整 APP 函式。既有 C 重建覆蓋率不變。

[檢查器](check_v4160_callback_fields_static.py) 與 [固定帳本](v4160-callback-fields-static.json) 保存完整原始 operands、SHA-256、CFG、原始 HEX backing、欄位來源與條件性串接。沒有執行或模擬目標 ISA、callback、provider、RAM、heap、MMIO 或裝置。

## +8 的已知初始值是 0，不是沒有來源

重用 [啟動搬移合約](v4160-fallback-initialization-static.zh-TW.md)，由 initializer 的實際 second-copy source／destination／inclusive-last operands 投影這些 12-byte 來源。每個來源的 12 bytes 均由原始 sparse HEX 完整捕捉：

| 物件 | V131 source → destination | V140 source → destination |
| --- | --- | --- |
| dynamic callback 表 | `6eaa4 → 20002e70` | `6ec94 → 20002ebc` |
| fixed callback 表 | `6eaf0 → 20002ebc` | `6ece0 → 20002f08` |

| 物件 | V131 三個 words（+0／+4／+8） | V140 三個 words |
| --- | --- | --- |
| dynamic | `49156 / 49270 / 0` | `491ee / 49308 / 0` |
| fixed | `0 / 4b500 / 0` | `0 / 4b598 / 0` |

物件區間在請求的搬移範圍內，且位於後續 zero-helper 清零區間之前。[ID11 defaults](v4160-id11-outer-tail-static.zh-TW.md) 另有對 fixed object+8 的直接 zero store；它與上述搬移來源是兩份獨立證據。

**這只是已知來源及局部寫入，不代表執行後永遠為 0。** 整段 second-copy 請求仍有其他 sparse HEX 缺口，也未證明啟動完成、初始化順序、其他 writers／別名或後續保存。沒有把完整捕捉的 12-byte 子區間擴張成整段 startup 已成功。

## APP 保存的接收 callback 在 +4

原 APP `0x19dfc..0x19e08` 的 12-byte snapshot 是：

```text
+0  00000000
+4  0000888c
+8  00000000
```

這是原始檔案中的 bytes，未證明 canonical 結構完整 extent 或 runtime 不變。APP 呼叫窗口以 AUIPC／ADDI 在 A3 形成 `0x19dfc`，並明確準備 A0=live GP、A1=4、A2=16；目標來自 fresh U32[live S0+304]，JALR 清除最低 bit。

只有在 live S0=`0x40000` 時，它才選到 nominal slot `0x40130`。兩份候選 resident 此 slot 分別保存 `0x4cf22`／`0x4cfba`，即 [已驗證的 append](v4160-callback-list-writers-static.zh-TW.md)。窗口本身沒有證明 S0 的到達值、先前 callee 的保存、已安裝服務表、實際進入 append 或登記成功；緊接下一條指令載入另一個 target，也沒有立即測試登記返回碼。

在 matching append、正常成功路徑及物件來源保持的前提下，主節點 node+8 保存 A3 原值，即 APP callback 表指標；它沒有深拷貝該表。[既有 getter](v4160-typeb0-record-static.zh-TW.md) 返回 node+8 的**值**，本輪消費端再讀取這個表的 +4，所以才條件性取得 `0x888c`。

表的 +8 為 0，不能推論整份 callback 表沒有綁定；+0、+4、+8 是不同的欄位與路徑。特定 +8 路徑會檢查 null，不能一概說 null 都被靜默略過。

## 完整 +4 消費端：三個早退與 callback 回覆

消費端建立 64-byte frame，保存原 A0..A5 所需值。先請求：

```text
0x20000a48(original A1, &SP30)
```

返回 pointer 為 0 時，本函式返回 1。非零則捕捉為 lookup object，再 fresh 讀 U16[SP30]，以該值呼叫 callback-list getter `0x4b650`／`0x4b6e8`。

SP30 在本函式沒有本機初始化；非零 lookup 回覆本身不保證 callee 確曾寫入 scratch halfword。這個輸出合約仍需展開，不能只憑相鄰地址推定。

getter 返回 callback 表 pointer 為 0，或 fresh U32[表+4] 為 0，均返回 14。否則經捕捉的 A6 呼叫：

```text
F & ~1(original A0, lookup object,
       original A2, original A3, original A4, original A5)
```

null guard 測試完整 F；F 非零也不保證清除最低 bit 後的目標有效，仍需 code／ABI 前提。本函式不讀 callback 表 +8，也不直接寫 callback 表。所有九個 stores 都是 frame stores。

callback 的完整 A0 回覆先捕捉到 S0；非零直接返回該值。零則可能進入後續 helper，但正常最後返回仍使用保存的 S0。

## Callback 返回 0 後的條件性 post-helper

只有以下條件依序成立，才呼叫 `0x4b534`／`0x4b5cc`：

1. callback 返回 0。
2. 保存的**完整入口 A5**不等於 254，沒有截成 byte。
3. fresh U8[lookup object+0] 等於 2。
4. 從 fresh U32[lookup object+4] 讀取兩個 bytes，組成 little-endian U16，符號擴展後恰等於 `0x2902`。

第四步實際先讀 byte+1、再讀 byte+0；不是原子 halfword snapshot。成立後再從原 A2 指標以相同高 byte 先讀的順序取得另一個 U16，傳給 post-helper 的 A2；沒有本機 A2 pointer null／extent guard。

post-helper 的 A0=原 A0、A1=原 A1、A2=上述新組合。A3 是 callback 返回後的 then-live 值，沒有重載原 A3；A4 已由本機設為 `0x2902`，A5 是新讀 byte+1 左移 8，A6／A7 亦未重新設定。不能把這次呼叫當成原六個參數的另一份副本。

post-helper 的回覆正常返回後被 S0=0 蓋過，所以它的 status 不決定此函式最後的 A0。這不代表它沒有副作用，或 callback／來源／scratch 都保持不變。

## 重播與保存界線

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_callback_fields_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_callback_fields_static.py
```

檢查器拒絕 143 個 instruction mutations、6 個 typed-load mutations 及 APP 表的 12 個 byte mutations，核對 65,536 個 packed-ID 純量案例、frame 區間、原始 HEX 與帳本精確重播。mutation checks 包含完整 operands／hash 固定，不等於獨立 runtime 行為或可達性測試。

scratch SP30..31、借用參數的 SP8..15 與保存槽 SP36..63 不重疊；仍須有效存取、正常 callee 返回與 S／SP／RA／saved-frame 保存，以及無不利 alias／wrap／IRQ／DMA／重入等前提。節點保存原 callback 表指標，也不證明其 ownership 或保存期。

下一段可展開 `0x20000a48` 的 SP30 輸出合約與 `0x4b534/0x4b5cc` 副作用，並繼續核對其他 callback writers。實際 installed provider、完整 APP 路徑、啟動完成、資料保持及實機功能仍未驗證。
