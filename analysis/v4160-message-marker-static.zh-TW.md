# v4.1.60：message header 與通知描述項的條件性來源串接

日期：2026-11-26。接續 [allocator release 靜態合約](v4160-allocator-static.zh-TW.md)，把候選 message 配置 wrapper 的 header stores，接到原 APP 三個通知描述項建立點及 callback 的指標交回。本輪以原始 bytes／operands 與 host algebra 檢查，不執行指令、配置器、provider、合成 heap 或 MMIO；沒有增加 C 還原覆蓋率。

## 配置入口與完整 bytes

固定的 SDK header 宣告 `tmos_msg_allocate(uint16_t len)` 位於 **JT15／slot `0x40070`**。JT12／`0x40064` 是 `tmos_msg_send`；不能把它當作配置入口。deallocate 仍沿用前輪的 `0x40068`。

| 參考候選 | slot40070 word | 第一段 copy 的條件性來源 | runtime 本體（終點不含） |
| --- | --- | --- | --- |
| V1.31 | `0x20000236` | `0x404a6..0x404fc` | `0x20000236..0x2000028c` |
| V1.40 | `0x20000236` | `0x404e6..0x4053c` | 同上 |

每份 86 bytes／35 instructions，bytes 相同，SHA-256 均為 `dd02b794304fe9ae8b45e6cc3a888820393e679d5d3870a95a2a021fc0070faa`。[檢查器](check_v4160_message_marker_static.py) 固定全本體與每個 operand，核對 slot、完整 first-copy 範圍、header JT，重播 [JSON ledger](v4160-message-marker-static.json)。相同 bytes 不證明 installed 版本、loader 已完成或最終 RAM 未被覆寫。

解碼仍明示 `conditional-LLVM-Xwchc-RVInst16CL-GPRC`，沿用已保存 LLVM 四份來源的 SHA-256／Git blob 與 28 筆 encoding vectors。這是條件性 profile，不是實體晶片指令集的識別證據。

## 候選 wrapper 如何寫入 `D-2`

入口建立 16-byte frame，保存 RA／S0／S1／S2，先讀取並保存 `U32[0x4002420c]`、寫零、`FENCE.I`，才判斷完整 input A0 是否為零。零輸入也經過這個控制字前置路徑。

非零輸入 L 保存於 S0，再於 `0x2000026e` 呼叫私有 core `0x20000040`，link=`0x20000270`：

```text
A0 = (full_L + 8) & 0xffff
A1 = 0xf000 | full_L
A2 = wrapper 沒有寫入
```

core 的條件性 flash source 是 V1.31 `0x402b0`／V1.40 `0x402f0`。本輪不執行或展開其本體，不能推定它只觀察 A0／A1、一定返回、保存所有暫存器、提供有效大小或不外傳指標。先前 [allocator-review](v4160-ota-source-wiring-2026-10-22/allocator-review/README.md) 已保存完整 wrapper 與有界 core prefix；本輪補的是可重播的 APP／marker 串接，不把 prefix 升級為完整 core 合約。

若 core 正常返回非零 P，且 live S0／S1／S2、SP、saved frame 與程式碼保持所需內容，wrapper 依序：

1. 寫 `U32[P+0]=0`。
2. `0xa142` 解作 `qk.c.sh s0,4(a0)`，寫 `U16[P+4]=low16(L)`。
3. A5=-1；`0xa17c` 解作 `qk.c.sb a5,6(a0)`，寫 `U8[P+6]=255`。
4. 恢復控制字，計算 `D=(P+8)&0xffffffff`，恢復 frame 並返回。

因為 `((D-2)&0xffffffff)==((P+6)&0xffffffff)`，這建立了前輪 deallocate 所讀 `U8[D-2]` 為 255 的**條件性來源**。不代表任意輸入指標皆有此標記；合法存取、header 未被後續改寫及實際配置入口相符仍是前提。core 返回零則恢復控制字並返回零。

16-bit 型別域內，L=`65528..65535` 的 core request 會回繞成 `0..7`；本輪未證 core 對此有何處理。非零 P 也不保證返回 D 非零，例如 P=`0xfffffff8` 時 D=0。這些是編碼的模數算術，不是對這類指標作實際存取。

## APP 三個建立點：12-byte 請求與描述項欄位

承接既有 [描述項 ownership](v4160-notify-descriptor-ownership.zh-TW.md)／[來源說明](v4160-notify-descriptor-source.zh-TW.md)，本輪固定三個完整 APP 本體，解碼全部指令並對配置／欄位／登記／交回邊界設 operand guards；不宣稱對所有未知呼叫作語義執行或完整 CFG 證明。

| 建立函式 | 配置 call | `D[2]` 通知標記 | 寫入 `U32[D+4]` 的來源 | `0x9124` call |
| --- | --- | --- | --- | --- |
| `0x13660..0x136d0` | `0x13672` | `0xab` | `U32[GP+96]` | `0x136ac` |
| `0x136d0..0x13740` | `0x136e2` | `0xba` | `U32[GP+88]` | `0x1371c` |
| `0x13740..0x137c0` | `0x13756` | `0xb9` | 入口 A1 為零取 `U32[GP+100]`，否則 `U32[GP+104]` | `0x1379c` |

三者均從當次 `[0x40070]` 讀 target，以 A0=12 呼叫。返回 D=0 走尾聲；非零時把入口 A0 的 low16 識別值存至 D+0、通知標記存至 D+2、來源 word 存至 D+4、256 存至 U16[D+8]。第三個建立函式使用 32-byte frame，先保存並在配置返回後載回入口 A1／A2；另兩個是 16-byte frame。

這些直接 stores 的位置與配置 header 的 `D-2` 不同：**APP 的 `D+2` 通知標記不是 allocator 的 `D-2` 標記。** 對候選 request12，core 參數是 A0=20、A1=`0xf00c`，配置 header 的 U16 length=12；APP 再填的是 D 所指的描述項。這不證明未知 core 確實提供足夠空間。

三個 `0x9124` 邊界均是 key=`0x13f36`、flag=0、A3=D（取自 S0）。delay 的本機判斷涉及 `0x135e6`；本輪固定呼叫邊但把 callee 當成未知正常返回邊界，沿用既有說明的條件性解讀。登記返回非零時，建立端以保存的 D 尾跳當次 `[0x40068]`；零時在這裡不交回。這不把登記結果命名為已證實體排程成功，也不保證物件只釋放一次。

## callback 交回的仍是 D

完整 `0x13f36..0x13f66` 共 48 bytes 也固定並解碼。A0=0 直接返回；非零時保存 D 至 S0，依序讀 U16[D+8]→A3、U32[D+4]→A2、U8[D+2]→A1、U16[D]→A0，再呼叫 `0x13e98`。

只有在該 callee 正常返回並保存所需 live context／frame 的條件下，callback 以 S0 的原 D 覆蓋 A0、恢復 frame，尾跳當次 `[0x40068]`。交回的是 D，並非 D+4 內的來源指標。沒有證明 callback 必然被排程器呼叫、取回同一 D，或配置到交回之間沒有 ownership-changing 寫入。

APP 完整本體 SHA-256：

| 本體 | bytes | SHA-256 |
| --- | --- | --- |
| 13660 | 112 | `101aa514b5384a875ac5d0aed78902d5b371c24317897dff9643d090b5089392` |
| 136d0 | 112 | `27451c9e0ed74db53f6a1b5c627ef1dd69adb646727695f2d322d2708db5d16a` |
| 13740 | 128 | `d07d4c09659a93ad967d73787a5735d8eadfad01f2bafc932ea0542ee06de6d9` |
| 13f36 | 48 | `4eb573901c294659d125c03c49154ec9d5ce89cb6c4775e58df5572097667ed9` |

## 重播與實際結果

檢查器需要固定的原 APP、四個既有本機 Python dependency 模組，以及 `analysis/wch-resident-candidate-2026-10-21/` 的兩份 carrier、SDK header、四份 LLVM 原始碼／測試參考。候選輸入目錄未隨本次提交發布；只 clone repo 不足以重跑。程式不下載、安裝、啟動服務或操作設備。預設精確比對 JSON；`--write` 只可建立不存在的 ledger。

```text
python analysis/check_v4160_message_marker_static.py
python -O analysis/check_v4160_message_marker_static.py
```

兩種模式均實際輸出：

```text
PASS: 65535 typed nonzero lengths; 8 wrapping request sizes; 6 pointer identities; 8 specified raw mutations
PASS: 2 complete message wrappers (172 bytes), 3 APP builders + callback (400 bytes); marker/descriptor/free-pointer edges
PASS: ledger exact replay; installed/core/payload lifetime UNPROVED; NO ISA/provider/MMIO execution
```

typed lengths 是全部非零 U16 長度的 request 算式；six pointer cases 是模數位址關係的六個例證，不是所有指標或合法配置的窮舉。八個 raw mutations 分別改 header marker offset、header length offset、返回 pointer 調整、APP 配置 slot、12-byte request、APP 通知標記 offset、登記 payload register、callback 標記 read offset。均直接進入推導並由指定 guard 拒絕；不以全檔 hash 不符或任意 parser exception 充作通過。

仍需釐清實際 slot 綁定、完整 `0x20000040` core／其未知 fallback、真實 payload 寫入與保存期，以及 opaque calls 的 S／GP／SP、saved-frame、code／header 不重疊與穩定條件。這次串接提供可檢查的來源前提，沒有解除上述未知。
