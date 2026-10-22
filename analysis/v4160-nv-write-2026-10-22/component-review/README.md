# NV 寫入離線元件：獨立 ELF 檢查

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

這份檢查獨立重讀實際 C／C++ `native.o` 與實際連結的 `linked.elf`，沒有用 producer 的結果欄位或 replay 作為判決。checker 不編譯、不連結、不執行目標／HOST／CPU／ISA／ESIL、不存取 MMIO／硬體、不連網，也不產生 BIN。

兩個語言的原始 ET_REL 物件 SHA-256 均為 `b30c679bd1e15a7a59be59b4ed723a6f98f78cc022e93e314e4c59f85c7aa09f`；實際連結後 `.text` SHA-256 均為 `bc6c4438642ee15072836bb30b7e97fdff168b1c49bda5fe9ce9fdde58283aca`。

|真實定義|位元組|元件內 VA，十六進位|
|---|---:|---:|
|tsl9_flash_status_18e90|8|0|
|tsl9_flash_unlock_18e98|30|8|
|tsl9_flash_lock_18eb6|14|26|
|tsl9_flash_erase_18ec4|46|34|
|tsl9_flash_program_18ef2|100|62|
|tsl9_flash_quarter_9c0a|64|C6|
|tsl9_delay_19764|60|106|
|tsl9_nv_write_callback_197be|72|142|
|合計|394|終點 18A|

八個非零大小的 global FUNC 都由實際輸入 section 定義，輸出完整保留八個函式、394 bytes、148 條指令。元件 VMA 0 只是離線連結位置，不是實體硬體位址；入口是實際 write symbol 的 VA 0x142。從 write 入口沿這些實際呼叫可達六個函式，另外 status 和 quarter 兩個未使用的真實函式也完整保留，沒有 GC。

## 呼叫與完整位元組保存

輸入有十個真實 relocation：quarter 內五個 `R_RISCV_JAL`（type 17），以及 write 內五個 `R_RISCV_CALL_PLT`（type 19）。輸出沒有 UND、remaining REL／RELA section 或 ABS address provider。checker 從實際 JAL 即時值及 AUIPC RA／JALR RA,RA 配對重建目標，逐一確認它等於對應真實 FUNC 的輸出位址；不是從 disassembler 的 symbol 註解推定。

每個函式的全部輸入／輸出 bytes 逐一比較。只允許五個 JAL 的 immediate bits 31..12，以及五個 CALL_PLT 的 AUIPC bits 31..12、JALR bits 31..20 改變，合計 260 個可編輯 immediate bits。opcodes、rd、rs1 及其他非 relocation 欄位仍必須一致。十個 relocation 覆蓋的 60-byte 指令範圍並未整段豁免。

實際只有 24 個 byte 改變：quarter 15 個，write 9 個；其餘六個函式完全逐 byte 相同。兩份實際 LLVM 靜態輸出也各自與全部原始／連結指令 bytes 和 PC 核對，共重讀 788 函式 bytes、296 列指令。checker 不執行這些指令。

## 區段、provider 與 metadata

實際 linker 配方只有 `ld.lld --no-relax -T component.ld native.o -o linked.elf`，沒有 GC、數值 provider、ROM stub 或額外物件。實際腳本把 `.text.*` 放在 VMA 0，入口引用真實 write symbol，並僅捨棄 `.comment`。

唯一 allocated section 是完整的 RX `.text` 394 bytes；唯一 PT_LOAD 的 file／memory size 都是 394，正好覆蓋該 section，不含 ELF headers、空洞、其他 payload 或 NOBITS。另有一個 PT_RISCV_ATTRIBUTES，精確對應 flags=0、64-byte 的非 allocated `.riscv.attributes` metadata，唯讀且不屬於載入程式區段。

`ABS_providers=0` 不等於所有 symbol 的 SHN_ABS 數量為零：輸出保留一個 local STT_FILE 檔名，以及一個 local、零大小、零值 `$d.N` mapping metadata symbol。checker 只允許這兩種精確 metadata 形式；任何把真實函式換成 ABS 的 provider 仍被拒絕。

## 實際檢查與重跑

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT --component-receipt /absolute/build/component-v2/c/verification.json --receipt /absolute/new-review-c.json
python3 -B check.py --project-root ROOT --replay /absolute/new-review-c.json
./check.sh --project-root ROOT --replay /absolute/new-review-c.json
```

Windows 可直接以現有 Python 執行 check.py。預設模式只核對封存 metadata／來源 pin，不讀 actual object／linked ELF，回報 `actual_artifacts_read=false`。明確 receipt 模式重讀實檔，建立不存在的新 review receipt；replay 重新讀取同一份實際證據，保持唯讀。來源 pin 解析支援工作目錄與發布目錄配置；actual logs／receipts 中的絕對路徑仍須存在。

七個反例都在記憶體內修改真實 linked ELF：錯誤 CALL_PLT 目標、錯誤 section size、LOAD memory hole、可寫 LOAD、偽造 ABS provider、錯誤 FUNC size、保留的未使用函式 byte 被修改。全部由獨立 gate 拒絕，不執行修改內容，也不輸出修改後的 ELF／BIN。C／C++ 實際檢查及唯讀 replay 通過；新文字為 LF、單一結尾換行，README.md 與 readme.zh-TW.md 完全相同。check.sh 沒有重試先前被拒絕的 Git Bash，已驗證 Python 入口。

第一次 component-v1 的 producer reader 錯把「一個 LOAD」寫成「一個 program header」，因此拒絕了正常的 attributes metadata header；失敗輸出保留在原 build/component-v1。component-v2 只修正 reader，沒有改變 C／C++ 指令、來源、link flags 或腳本；本檢查另外核對兩個實際 program headers。

## 保留的界線

本次只證明真實定義、實際 relocation 解析與完整靜態元件保存。原始來源契約 `source-review` seal 為 `2d9c5278019c0a2e452f42cc2cadf8af60b486c95244cd1b855567b5fc060005`，沒有修改。

完整原始 ABI 與正常 caller replacement 仍未證明：新的 write 使用 16-byte frame，原始 wrapper 使用 32-byte frame 並新讀保存的 source；新的 timer 也使用不同 scratch／出口 GPR。元件成功連結無法解決這些差異，也不證明 fault、IRQ、非同步、alias、installed provider、Flash ownership、輪詢終止、OTA 或實體寫入成功。沒有產生可燒錄 BIN。
