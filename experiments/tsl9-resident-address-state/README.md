# 初始化尾段與六位元組 state constructor

[English](readme.en.md) · [前輪 providers](../tsl9-resident-init-leaves/README.md)

[C/C++](resident_address_state.c) 新增四個完整本體，**364 CODE bytes／129 指令**。實際 C11／C++17 物件相同，25 個正尺寸 FUNC、21 筆 relocations；依原始位址正規化後，每個指令 byte 都與候選 SDK 相同。保留暫存器、分支及呼叫 ports，並非恢復出的原廠 C 原始碼。

| 本體範圍（半開） | Bytes／指令 | 已確認的指令行為 |
| --- | --- | --- |
| `0x43E8E..0x43EB2` | 36／16 | 16-bit range，保留 signed×unsigned 高32位 MULHSU，結果取低16位 |
| `0x43EB2..0x43ED2` | 32／14 | 32-bit range，保留 unsigned×unsigned 高32位 MULHU |
| `0x53868..0x5397C` | 276／94 | 六位元組複製、候選值建構、遮罩、比較與重試 |
| `0x5E758..0x5E76C` | 20／5 | 清除兩個欄位後，無 link 尾跳至 `0x53868` |

兩個 range helpers 都使用已重建的 `0x433A8`；不可改為 modulo 或混用 MULHSU／MULHU。前三個函式自身 frame 各32 bytes，尾段自身 frame 為0。

## 原始執行鏈與資料欄位

原 initializer 在 `0x537C6` 釋放自身16-byte frame，`0x537C8` 尾跳 `0x5E758`。新尾段以 byte／word 寬度分別清除 `0x20003480`／`0x20003484`，再於 `0x5E768` 無 link 跳至 constructor，保留 incoming RA／SP。

constructor 的實際 far call `0x53888/0x5388C` 呼叫已重建的 RAM `0x20000332` copy provider，從 `0x20003204` 複製6 bytes至 `0x200034A0`。官方候選 header 的64-byte `bleConfig_t` 中，MacAddr offset=24、size=6，已以 C11／C++17 assertions 核對。只有前輪64-byte config copy、穩定記憶體、相符 ROM、callee／IRQ／alias 等條件成立，才可建立來源關係；**沒有讀取或公開實際 MAC bytes／獨立雜湊**。

| 半開 RAM 欄位 | 指令證據 |
| --- | --- |
| `[0x200034A0,0x200034A6)` | 六位元組來源副本 |
| `[0x200034AC,0x200034B2)` | 第一候選欄位；`0x538CA` ORI −64，最後 byte 高2位為11 |
| `[0x200034B2,0x200034B8)` | 第二候選欄位；`0x53926` ANDI 63，最後 byte 高2位為00 |

三個欄位數值上互不重疊，均位於前輪296-byte state request 範圍。第一候選值的 retry arm `0x53966..0x5397C` 位於正常 RET `0x53964` 之後，仍可到達，已完整保留。常數 upper 為 `0x3FFF`，不是4095。

第二候選值與副本以三組 halfword 比較：candidate offsets250／252／254 對 copied offsets232／234／236。原 signed LH 經遮罩後比較；`0x53934` 或 `0x53944` 不同即返回，只有 `0x53954` 最後一組也相同才重試。第二個比較不支配所有返回路徑，沒有把短路 CFG 改成無條件三次比較。

**重試終止、亂數分布／熵、全域唯一性、實機藍牙位址角色與配對效果均未證明。** 沒有觀測 live 值。保留原始篩選條件，未因代數推論刪除分支。

## 驗證與限制

[address_abi.c](address_abi.c) 只驗證 RV32 widths、primary config layout、field disjointness 與32-byte自身 frame slots；C／C++物件相同且 allocated bytes=0，沒有 runtime provider。

實際非載入 ET_REL 組合為 **21,370 CODE＋256 DATA／7,320 指令**，1,375 正尺寸 FUNC、1,038 relocations。所有 input bytes／symbols／relocations 完整保留，原始 CODE 位址無重複，兩個獨立 ELF readers 一致。`0x5E758` 的真實本體補上一個缺口，具名依賴 **12→11**；本輪兩個 imports 均有前輪真實 provider，沒有新增具名依賴或 stub。其他間接呼叫與 memory effects 仍開放。

[證據](evidence-v1.json) · [驗證收據](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-address-state/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定本機 APP／SDK、前輪 native artifacts 與 Windows NDK LLVM；不下載依賴，其他平台未驗證。APP仍159 C/H、95.54%位元組覆蓋率，**不是功能完成率**。4-byte啟動來源缺口、ROM／RAM／ISA／IRQ／Flash／OTA 相容性與 binding 前無 dispatch 均未封閉。

未連入 APP、未產生 BIN，沒有 target／HOST model／ISA／硬體執行；**尚未成功重建可用替代韌體**。後續唯讀欄位／遮罩／重試診斷只是候選功能，尚未實作。
