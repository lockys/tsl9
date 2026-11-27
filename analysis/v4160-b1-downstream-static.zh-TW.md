# v4.1.60：B1 更新、flag 寫入與通知後釋放

本輪完整核對兩版本 dispatch、updater、notifier，共 **884 bytes／336 instructions**。所有 bytes 與原始 sparse HEX 一致，另重用 predicate／fill 共 216 bytes，不增加既有 C 重建覆蓋率。

| 完整本體（右端不含） | V131 | V140 | 每版 bytes／instructions |
| --- | --- | --- | --- |
| dispatch | `6c042..6c0c6` | `6c226..6c2aa` | 132／52 |
| update | `6b83e..6b928` | `6ba22..6bb0c` | 234／87 |
| notify | `44310..4435c` | `443a4..443f0` | 76／29 |

[檢查器](check_v4160_b1_downstream_static.py) 與 [固定帳本](v4160-b1-downstream-static.json) 固定完整 operands、SHA-256、CFG、calls／stores、Xwchc 編碼、不可變路徑及整數／區間憑證。承接 [B1 消費端](v4160-b1-task-route-static.zh-TW.md)，全程沒有執行或模擬目標、callback、NV、provider、RAM／heap、MMIO 或裝置。

## Dispatch：單筆成功回覆與 bulk sticky status

入口 `(ID=A0,H=A1,V=A2)`，H、V 保存為完整 words。

ID 不是完整 word `0xffff` 時，先請求 `20000a94(ID)`。返回 null 則回覆 20；非 null P 則以 `(fresh U8[P+5],P+6,0)` 呼叫 `6be3c / 6c020`。其完整無號回覆作為 index，若 index>=fresh U8[count] 回 21；否則呼叫 updater(index,H,V)，**忽略 updater status，固定回 0**。

ID=`0xffff` 時，index 從 0 開始，每次以 fresh byte count 比較。每個准入 index 呼叫 updater，初始 status=21，任何一次 updater 非零回覆都將 status 設成 0，後續不改回 21。這是 sticky aggregation，並非所有項目成功的證明；updater 的 1 也可能表示無變更或某個 read-request 非零。

index 每次加一後 mask255；index=255 不能小於任何 U8 count。因此在 callee 返回並保存 index／context 條件下，bulk 最多 255 次，不需假定 count 恆定。selector 回覆、count、pool 配置與有效範圍仍未閉合。

## Updater 的讀取參數與局部工作區

updater 保存 index、H、V，建立 96-byte frame，依序：

1. 請求 `440c2 / 44156((6*index+512) mod 2^32,16,SP)`；回覆非零則返回 0。
2. 請求 `200004bc(SP,255,6)`；非零則返回 0。
3. 將保存的 index 加 `0x7000`，請求 `440c2 / 44156(index+0x7000,64,SP+16)`；非零則返回 1，尚未直接寫入本輪 flag。
4. 呼叫 `6af42 / 6b126(SP+16)`，忽略其回覆，再依 H 選分支。

重用 [已驗證的 predicate](v4160-n136-predicate-static.zh-TW.md)：matching leaf 在 pointer 非 null、長度非零時，所有 fresh bytes 等於完整 value 才返回 1，否則 0；它還包含控制 word／FENCE 指令，僅以 bytes／CFG 分析，未執行。因此步驟 2 的非零路徑對應六個觀察皆為 FF 的條件。

**16、64 是 caller 傳入 A1 的數值，NV 單位與實際 output extent 未由此證明。** 本機後續使用 SP+16..79 作為 64-byte 槽位區間，保存槽從 SP+80 開始；區間分離不保證 provider 不會寫出其外，也不證明 read-request 成功初始化全部資料。第一個 transform 亦可能改動工作區，不能把後續觀察等同於原 NV snapshot。

當 dispatch 准入 index≤254 時，第一個數值地址為 512..2036，第二個為 `0x7000..0x70fe`；這只是算術，不推定實體 NV 地址或資料單位。

## H=0：條件性清空 64-byte 工作區

H=0 時，請求 `200004bc(SP+16,0,64)`。回覆非零直接返回 1；在 matching predicate 下，代表當次觀察皆為零。否則請求 `2000039c(SP+16,0,64)`，接入 changed path。

matching fill 的原始本體也已重播，但未實際呼叫；完成整區清零時亦會涵蓋各槽位 byte+3。工作區完成清零、provider／callee 保存、無不利 alias 等仍是條件；V 在這個 H=0 分支沒有決定本機更新方式。

## H 非零：16 個四-byte 槽位

工作區掃描 16 筆，每筆 stride4：U16 key 位於 +0，byte value 位於 +2，byte+3 沒有本機直接寫入。

- 第一遍比較 fresh U16 key 與**完整 H**，第一個命中就處理該槽位。
- 未命中且**完整 V=0**，返回 0。
- 未命中且 V 非零，第二遍找第一個 U16 key=0 的槽位；全滿返回 0。找到空槽先寫 low16(H)，再接入 value 比較。
- fresh U8[slot+2] 與**完整 V**相等，返回 1，略過本機 flag／save path。新槽的 key store 可能已先發生於局部工作區。
- 不相等則寫 low8(V) 至 +2；只有**完整 V=0**才另把 key 清為 0，接著進 changed path。

所以比較值、寫入值與清 key 判定不是同一個 byte 域。B1 的 V 是 U16，V>255 不可能等於 U8 slot value；非零 V=`0x0100` 可寫出 byte0，但不清 key。H 的 U16 來源限制只來自 B1 串接，updater 一般入口本身仍比較完整 H。

兩遍掃描的本機讀寫均落在 SP+16..79，每遍最多 16 筆。這不證明工作區來源完整、record key 唯一或底層儲存有相同布局。

## Changed path：flag 先設，再 transform／保存／通知

changed path 的直接寫入是：

```text
U8[20002fd4 / 20003024] = 1
```

該地址與 B1 parent 在處理前清零、處理後 fresh 重讀的 flag 相同。寫入之後才依序：

1. 再呼叫 `6af42 / 6b126(SP+16)`。
2. 請求 `4435c / 443f0(index+0x7000,64,SP+16)`。
3. fresh 讀 `20002ef0 / 20002f40` task byte，呼叫本輪 notifier。
4. 忽略這些 callees 的 status，返回 1。

這是直接 flag writer 與借用 stack buffer 的證據，不是已完成持久化。flag 已先設，後面的 callee 可以失敗、改寫 flag 或保存 SP+16；沒有本機 rollback。stack buffer 只有在 frame 存在且 provider 於有效期限內消費時才安全，實際保存合約仍未知。

updater 內部已可能呼叫 notifier；回到 parent 後，parent 又 fresh 檢查 flag，可能再呼叫一次。兩次 task、context 與 flag 讀值不必相同，不能宣稱 exactly once 或一定重複通知。

## Notifier：捕捉 callback，重讀待釋放 pointer

config base 為 `200031ec / 2000323c`，context base 為 `2000319c / 200031ec`。按順序檢查：

1. fresh U32[config+8] 非零；此 word 僅作 gate。
2. 捕捉 F=fresh U32[config+60]，必須非零。
3. 完整入口 A0 必須等於 1。
4. 捕捉 P=fresh U32[context+32]，必須非零。

前三個 gate 不過，直接返回且 A0 仍是原入口值；P=null 時略過 callback／release／清除，返回仍為 1。F 非零也不保證 JALR 清除最低 bit 後的目標有效。

正常 callback 參數為：

```text
F & ~1(
  fresh U32[context+36],
  fresh U16[config+12] >> 2,
  P
)
```

callback 返回後，函式**重新讀取** P′=U32[context+32]，直接請求 private release `20000110(P′)`，沒有再次做 null guard。P′ 不一定等於傳給 callback 的 P。之後才清除 context+32 與 context+36 兩個 words，正常返回 then-live 的 private-release A0，沒有統一強制成功碼。

因此不能從「callback 用過 P」推導「隨後釋放了同一個 P」，也不能由最後清除兩個 context words 證明 callback 不保留指標、private release 已完成或 ownership 已完整交接。callback、讀值及釋放之間的保存與有效範圍仍須另證。

## 重播與剩餘工作

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_b1_downstream_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_b1_downstream_static.py
```

檢查器拒絕 336 個 instruction mutations、6 個 typed-load mutations，檢查 fresh count／index、U16 value 拆合、16 槽位區間、callback size>>2 與帳本逐 byte 重播。所有 callee 正常返回、S／SP／RA／saved-frame 保存、有效存取及無不利 alias／wrap／IRQ／DMA／重入仍是條件，未以圖路徑替代實際執行或可達性。

下一段需展開 `20000a94`／`6be3c` selector、`6af42` transform、NV read/write 的 buffer 合約，以及 config callback／context pointers 的 writers。實際 provider、NV 持久化、callback 保存與完整物件生命週期仍未證明。
