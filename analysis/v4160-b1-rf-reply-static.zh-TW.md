# v4.1.60：RF 正常返回的 masked-word 回覆

接續[APP provider 與快取回覆](v4160-b1-provider-app-static.zh-TW.md)。本輪將 RF 主路徑原先 opaque 的 A0 收斂為：

```text
fresh U32[held Q+208] & 0xf0ffffff
```

Q 是 large 函式在 `+0x160` 捕獲的指標。此公式適用於兩版 large 的 **magic 與非 magic 編碼正常返回路徑**；非 magic 的三個前置 callees 仍須正常返回並保存必要 context／frame。沒有證明真實 Q 值、硬體讀值、實際 provider 綁定或輪詢終止，也沒有將回覆當成固定 success。

本輪重用完整原本體的 bytes／hash／CFG guard，新增返回切片、支配與 def-use 證書。重核的 RF 本體合計 **7684 bytes／2402 instructions**；新增原始 byte 覆蓋為 0，APP C 重建覆蓋率不變。

## 重用本體與確切範圍

| 角色 | V131 入口 | V140 入口 | 每版 bytes／instructions |
|---|---|---|---|
| RF 外層 | `0x641b0` | `0x6429a` | 232／79 |
| large | `0x6645c` | `0x6659a` | 3388／1032 |
| enable | `0x67198` | `0x672d6` | 18／6 |
| wait | `0x662da` | `0x66418` | 148／60 |
| final | `0x6636e` | `0x664ac` | 56／24 |

重用[完整 RF 外層](check_v4160_rf_tail_return_static.py)與[post-RF 本體](check_v4160_post_rf_leaves_static.py)，兩版全部範圍再次與 strict sparse HEX 逐 byte 對照，缺口不補零。Postservice 的完整 106-byte 本體也重核其呼叫及返回接點，但未算入上表 RF 本體總數。

Large 內的 99 個 signed DIV 與 packing 數值仍未在本輪完整重建。新的返回公式不需要求出那些計算的具體值；它仍以原指令正常完成、存取與 context 有效為前提。

## Large 唯一正常 RET 的最後 A0 定義

以下偏移相對 large 入口，兩版相同：

```text
+0x160  Q = fresh PTR[G+1424/1504]     // G=0x20003000；Q 保存在 A5
+0x1f6  A0 = 0xf1000000
+0x1fa  A0 = A0 - 1                  // 0xf0ffffff
          ... common arithmetic / stores ...
+0xccc  A4 = fresh U32[Q+208]
+0xcd0  A0 = A0 & A4
          ... 不再定義 A0 ...
+0xd32  RET
```

完整 1032-node CFG 的支配／reaching-definition 檢查確認：共同接點 `+0x154`、Q 捕獲、兩個遮罩定義、fresh word 讀取與 AND，都支配唯一的 `+0xd32` RET。完整本體只有四個 encoded A0 定義：`+0x172／+0x1f6／+0x1fa／+0xcd0`；最後一個到 RET 之間沒有 call 或 A0 定義。

Q 來自當次指標載入，不直接固定為 `0x40025000`。先前特定 mapping 可另給該名義值，但不能套到所有執行。只有在 Q 確實為該值時，名義 word 位址才是 `0x400250d0`。

本輪以 radare2 額外對照兩版末段 `LW A4,208(A5)`、`AND A0,A0,A4` 與後續 OR／SW；原 guard 也固定 raw bytes 與 operands。

## Fresh read 不是前後 store 的快照

`+0xccc` 的 fresh read 位於 `+0xcc8` 對同一 word 的 store **之後**。不能因為地址相同，就假設它讀回剛才寫入的值；實體 MMIO、非同步 writer 與其他副作用尚未閉合。

在 A0 已完成遮罩後，`+0xcd2/+0xcd4` 形成另一個 nibble，`+0xcd6` 將其與 A0 合併，再於 `+0xcd8` 寫入 Q+208。這筆後續 store 不改 A0，因此 **返回值也不是這筆最終 packed store 的完整值**。

遮罩會清除回覆 bits24～27，保留 bits0～23 與 bits28～31。它容許 2²⁸ 種 bit patterns，但沒有證明哪些實際可達；可能為零，也可能超過 U16。例如全 1 word 的遮罩結果是 `0xf0ffffff`，不能寫成固定 0、固定 13 或普遍的 U16 status。

## Magic 與非 magic 的前提分開

Magic 分支在 `+0x74` 比對 fresh word 是否為 `0x12345678`，相符時經 `+0xd34` 清除該 word，再由 `+0xd38` 的 `JAL x0` 回到 `+0x154`。這是本機不新增 link 的跳轉，不是另一個 callee，也不是直接 epilogue。

非 magic 路徑先經過 `+0xa0／+0xe2／+0x12e` 三個 mapped calls，再到同一共同接點。三者都位於新的遮罩定義之前，所以它們不必保存 A0 的數值才能得到最後的 masked-word 公式；**仍必須正常返回、保存後續需要的 S／SP／RA／frame，以及允許後續存取完成**。Magic 路徑略過這三個 calls，因而不需要它們的保存前提。

兩條完整語法路徑都記錄於 ledger。沒有用它們宣稱 magic 實際可達、mapped callees 的副作用已知、DIV／MMIO 必定正常完成，或所有外部 writer 都被排除。

## 接回 RF 外層的兩類正常返回

RF 外層有三條早退路徑：任一次 fresh context byte7 等於 4，或指定 global pointer 不符合原比較。它們跳往 frame 還原，沒有 A0 定義或子呼叫，故**保留 RF 入口 A0**。不能在這些路徑套用 13 或 large 回覆。

主路徑才在 `+0x46` 明確設 A0=13，於 `+0x48` 呼叫較前面的 RF helper。之後依序呼叫：

```text
+0x96  large
+0x9a  enable
+0x9e  wait
+0xa2  final
          ... frame 還原 ...
+0xe6  RET
```

後三個完整本體均無 nested call，也不定義 A0、SP、RA 或 S registers；外層在這些 call 之後亦不再定義 A0。因此主路徑的正常返回可追到 large 的 masked fresh word。

Wait 仍有完整六節點等待 SCC。只有其所需的條件最終允許退出，才可接到後續正常返回；A0 non-write 本身不是終止證據。完整 RF 外層的 32-byte frame、large 的 80-byte frame 及 saved register 還原，也仍依賴正常存取、無破壞性別名、必要 nested context 保存及無外部干擾。

## 接回發布後服務：RF 回覆與 getter 快取分開

Postservice 的 `+0x56` linked call 目標正是此 RF 外層。正常返回後，服務 `+0x5a` 寫回的是 **保存的 getter X 低 16 位**，而 A0 保留 RF 回覆至服務 RET，兩者不是同一份資料。

在前一輪的 matching APP getter／hook 與保存前提下，可列出：

| 服務路徑 | 正常返回 A0 |
|---|---|
| getter 槽為零 | 服務入口 A0 |
| matching getter 返回，未進 RF | U16 X |
| 進 RF、未呼叫 optional hook、RF 早退 | U16 X |
| 進 RF、已呼叫 optional hook、RF 早退 | mode 3 的回覆，這裡仍未限定 |
| 進 RF 主路徑，必要 calls／wait 返回 | `fresh U32[held Q+208] & 0xf0ffffff` |

這個分類沒有把所有路徑都寫成 masked word，也沒有把 getter 的 U16 界限套到 RF 主路徑。

## 驗證與剩餘缺口

[檢查器](check_v4160_b1_rf_reply_static.py)與[固定 ledger](v4160-b1-rf-reply-static.json)保存完整本體雜湊、返回切片、支配／def-use 證書、兩條 large 路徑、RF 三條早退、後三個 leaf 的 A0 non-write，以及 postservice 回覆／snapshot 區分。32 個返回切片／callee／non-write／snapshot 突變必須被拒絕；262144 個 host full-word 邊界族核對遮罩恆等式，沒有建立 target readback、MMIO 或可變 provider 模型。

```powershell
python analysis/check_v4160_b1_rf_reply_static.py
python -O analysis/check_v4160_b1_rf_reply_static.py
```

全程離線，沒有執行或模擬目標韌體、硬體存取、封包重放或 target network。尚需追查實際 Q／provider／magic writers、非 magic mapped services 的副作用、fresh read 與實體硬體行為及 IRQ 順序、wait 進展，以及同一物件的 N+12 writer、配置保留與完整消費釋放／notification 保存期。
