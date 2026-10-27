# 必要候選 initializer `0x5362E`

[English](readme.en.md) · [前輪 NVM layout](../tsl9-NVM-record-layout/README.md) · [caller／callback 註冊](../tsl9-resident-callback-registration/README.md) · [原 RF register initializer](../tsl9-original-RF-tx-path/README.md)

新增 [C/C++ 本體](resident_init5362e.c)，完整範圍 **`0x5362E..0x537D8`，426 CODE bytes／138 指令**。同份來源以 C11／C++17 編譯，20 個正尺寸 FUNC、14 個 direct controls 與一組 far-call HI／LO（合計16 relocations）均吻合原始 SDK 編碼。12 個 Xwchc byte／halfword ports 依已保存官方 encoding 定義與 52 個正向 vectors 核對，實機 ISA profile 仍未確認。

這是原始暫存器上下文的 C arithmetic／volatile accesses 與明確 ISA／控制 ports；不是原廠 C 原始碼或普通可直接呼叫的 C API。

## 完整邊界與局部 frame

函式使用 16-byte frame，保存 S2／S1／S0／RA 於 offsets0／4／8／12。唯一正常出口在 `0x537C8` 不寫入 RA 地尾跳 `0x5E758`；四個 saved words 與 frame 在此前已還原。`0x537CC`、`0x537D2` 的 branch arms 雖位於 epilogue 後，仍可由原 CFG 到達並跳回本體，均已保留。`0x537D8` 起是另一個配置64-byte frame 的函式，沒有選入。

## 讀寫與必要 callee

- `0x5364A` 要求將 word `0x200034E4` 寫0。
- `0x53650/0x53654` 是真實 far call，指向已有本體的 RAM memset provider `0x2000039C`，參數為 address=`0x200033B8`、value=0、count=296，數值 end=`0x200034E0`；沒有把它列為 opaque callback。
- `0x53668` 將 low8(incoming A0) 寫至 `0x2000319F`，仍依賴前述 callees 保留 private saved registers。沒有認定該 byte 是 boolean initialized flag、有效 task ID 或成功狀態。
- `0x537B2` 呼叫已有完整本體的 RF register initializer `0x64298`；其他原始常數、條件分支、fresh memory accesses 與後續呼叫均依原碼保留，不擅自賦予 frequency／timing 單位。

本體暴露六個尚未提供的真實 callee：**`0x55BD4`、`0x55C48`、`0x43E24`、`0x57AC4`、`0x63704`、`0x5E758`**。它們保留具名依賴，不用 stub 補齊，也不宣稱其副作用或正常返回已封閉。

## Caller 的條件初始化與 callback 順序

完整 caller `0x60856..0x6089A` 讀取 `0x2000319F`。零值路徑先呼叫 `0x43C4E`，接著在 `0x60870` 呼叫本 initializer；incoming A0 來自前一 callee 的返回值。非零路徑跳過這兩次呼叫。

返回／跳過後，caller 都會寫入兩個 callback words，兩個 stores 均支配自己的正常 return：

| Store PC | RAM word | 數值 CODE pointer |
| --- | --- | --- |
| `0x60880` | `0x2000343C` | `0x5E8BC` |
| `0x60892` | `0x200034F8` | `0x60516` |

第一個 word 位於本 initializer 要求清空的296-byte state 範圍內。這證明編碼的 clear request／後續 binding 順序，**未證明 live callback 值、callee 不會改寫、初始化全程原子性，或 binding 前不存在 dispatch**。不能只看 caller 最後兩個 stores 就宣稱所有 RF／IRQ callback 都準備完成。

## 部分連結與限制

與前輪完整候選做實際非載入 ET_REL 部分連結後，兩份 C／C++ 組合皆為 **20,916 CODE＋256 DATA／7,163 指令**，1,340 個正尺寸 FUNC、1,011 relocations。每個輸入 byte／symbol／relocation 保留，原始 CODE 位址唯一，兩個獨立 ELF reader 一致。

原 `0x5362E` 依賴已有真實本體，兩個 imports 使用既有 real providers；同時新增六項實際缺口，因此具名未提供 callee 為 **10−1＋6＝15**。UND 數量不代表 runtime 封閉。本單元沒有真正的 opaque callback site，整個既有組合仍有其他未封閉間接呼叫／raw memory 契約。

[數值 assertions](init_abi.c) 亦經 C11／C++17 編譯，核對 RV32 pointer／word、自身 frame 與 state 數值範圍；沒有 allocated bytes、runtime provider 或 import，不證明實際 RAM 所有權。

## 重跑

[證據](evidence-v1.json) · [收據](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-init-5362e/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定本機 SDK／APP、前輪 native artifacts 與 Windows NDK LLVM；不下載依賴。其他平台未驗證。APP 保持159 C/H、95.54% 位元組覆蓋率（不是功能完成率）；未連入 APP、未產生新 BIN，也沒有目標／HOST model／ISA／硬體執行。

4-byte 啟動來源缺口、設定 writer 額外144／123-byte來源初始化、NVM映射，以及 ROM／RAM／ISA／IRQ／Flash／OTA 相容性仍開放；**尚未成功重建可用替代韌體**。後續功能候選為唯讀初始化階段／callback binding 診斷，尚未實作 UI，不改動 RF 或 IRQ 設定。
