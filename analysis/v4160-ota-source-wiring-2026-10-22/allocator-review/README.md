# Slot 0x40070 allocator 候選：A2 仍穿透未知呼叫

[English](readme.en.md)

本輪實際讀取既有兩個 SDK 候選及官方 ID2966 原始檔，沒有下載、編譯、執行或產生韌體。**不能證明配置器不觀察原 S 回覆指標 A2**：兩個候選的 wrapper 與下一層前綴雖然沒有直接讀寫 A2，卻有一路把它原值傳給 RAM 中新讀出的未知函式。不得因此縮減 full8 bridge 或宣稱指標不會逃逸。

## 已確認的原 App 與條件式候選

官方 Runtime SHA256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本輪重讀 `13B4C..13BA6` 的 90B，逐列比對既有封存的 `ota-handler-layout/reply-review/source-ledger.json`。原碼 `13B54` 讀 live S1+0x70，`13B60` 設 A0=length，`13B64` 存來源指標至 live SP+12；`13B68` 呼叫前 A2 仍是原來源指標。13B4C 的名稱或推測 API 原型不能消除這項實體參數。

| 既有候選 | Slot 40070 實際 word | 初始化映射的 wrapper Flash | Core Flash | Core fallback target word |
|---|---|---|---|---|
| V1.40 / carrier | 20000236 | 404E6 | 402F0 | RAM 20003270 |
| V1.31 / carrier-dec2023 | 20000236 | 404A6 | 402B0 | RAM 20003220 |

映射重用既有 `wch-resident-candidate/resident-entry` 的 word-copy 證據；並核對原 sparse HEX 與 segment 的完整既有雜湊。兩者都映射到 RAM wrapper `20000236..2000028C`，86B／35 指令，內容 SHA256 `dd02b794304fe9ae8b45e6cc3a888820393e679d5d3870a95a2a021fc0070faa`。Core 只讀 RAM `20000040..200000AE` 的 110B／37 指令，不把它誤稱完整配置器。

## 原碼欄位與停止邊界

Wrapper 先減 SP 16；依序存 S1+4、S2+0、RA+12、S0+8。S1=40024000；讀 MMIO+20C 至 S2、寫零、FENCE.I，才判斷 A0 是否零。這些效果不是純 malloc，也未在硬體執行。非零路徑 S0=A0，A0=low16(A0+8)，A1=F000 OR S0，於 RAM 2000026E 呼叫 core 20000040，link=20000270。完整 wrapper 沒有 A2 的讀、寫或 store。

Core 前綴再次使用自己的 16B frame、保存 S0/RA 與 MMIO save/zero/FENCE.I。由 A0 產生 `low16((A0+3)&~3)` 的長度，按 <=52 選小表或大表；讀 list head 和 sentinel。若兩者相等，fresh LW 從上述版本專屬 RAM word 取得 A4；非零才在 RAM `200000A0` JALR A4，link=`200000A2`。呼叫前 A0=1，A1 OR `(roundedLength<<16)`，而 **A2 沒有被前綴改寫，仍傳入未知 provider**。是否實際走到此路、該 word 的內容及其下游效果都未確認。

這是原始欄位與 CFG 的靜態論證，沒有建立或逐步執行 CPU 狀態。到這個 fresh indirect target 即停止；另一分支在 RAM 200000AE 進入未審的 allocation-search body，也沒有擴查。不能由未讀取的區段推斷其 A2 使用、終止或回傳。

Core 正常返回後，wrapper 使用 live S0/S1/S2/SP。若回傳 A0 非零：先 WRITE32 zero 至 A0+0，再 WRITE16 live S0 至 A0+4，再 WRITE8 FF 至 A0+6，恢復 MMIO，A0+=8，最後 fresh restore RA/S0/S1/S2、SP+=16、RET。此順序受 callee、記憶體 alias、故障與中斷影響；不能假設 core 遵循一般 C ABI。零入口／配置失敗有自己的 MMIO 還原與回傳路徑，沒有虛構成功 suffix。

後兩個 store 的條件式 ISA 來源是既有 LLVM `RISCVInstrInfoXwch.td`：`42a1` 為 QK_C_SH S0,4(A0)，`7ca1` 為 QK_C_SB A5,6(A0)。本輪獨立解析 funct3/quadrant、compact GPR 及 immediate 欄位；r2 的浮點 store 顯示不作語義證據。該 Xwchc 解讀仍是候選 profile，並非已安裝晶片 ISA 實測。

## 可重跑範圍

```sh
# Metadata 與已封存來源依賴；不讀外部候選 body 或原 BIN
python3 -B check.py --project-root ROOT

# 兩個參數一起提供，實讀原 App 與既有兩候選
python3 -B check.py --project-root ROOT \
  --firmware ID2966.bin --candidate-root EXISTING_WCH_REFERENCE
```

預設回報 `metadata_only=true`、`actual_original_firmware_read=false`、`actual_candidate_bodies_read=0`。顯式檔案回報 false／true／4，逐列驗證每候選 196B，重跑每候選四個 single-field 原始 byte 反例，共八個：core call link、header 長度 store、fallback slot offset、indirect target GPR。不是舊 HOST 矩陣，也不需要 W 歷史 build。工作區 `apk-analysis/tsl9-*` 與交付 `analysis/*` 路徑皆可解析。`capture.py` 只供最初 create-only 保存這些 operand 資料，不是韌體／provider 產生器。

## 仍未知

已安裝 resident、SDK 與 ISA 身分沒有證明；原 App 的 slot word 仍須 fresh 讀取。未知 provider 可讀 A2、其他 ambient GPR、caller frame 或記憶體，亦可改 SP/S/GP、slots、保存字、控制流或不返回。候選 wrapper 的局部保存字不構成整條鏈的暫存器保存證明。未證明 pointer nonescape、任意 alias 等價、完整 ABI、可用 Flash／NV 所有權、原 BOOT 或整體 OTA 相容性。

下一個必要證據是上述 RAM fallback word 的實際提供者／初始化關係；本輪沒有追到或假造它，也不把 ABS 40000 地址 witness 當 resident provider。維持原 full8 與 opaque-call 邊界。
