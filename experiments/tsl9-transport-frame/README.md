# 傳輸封裝、複製與 checksum

[English](readme.en.md) · [目前 C 來源](src/transport_frame.v6.c) · [整理副本](../../src/native/receive/transport_frame.c) · [原始指令契約](../../analysis/transport-frame-2026-10-23/original-contract.md)

重建官方 V4.1.60 `[0x8A56,0x8B6E)` 的 280B／96 指令，包含 RET 後仍可到達的 copy loop。13 個 FUNC 是相鄰的私有架構區域，不能當成獨立的普通 C ABI 函式。C 負責自由暫存器的 unsigned 算術、checksum 與 volatile memory；實體 S 暫存器、frame、分支、opaque call 與 tail transfer 使用明示架構 port。

目前只採用 **v6**。C11／C++17 的實際 native 與 partial ELF 都是 280B／96 指令：246B 完整非控制指令與全部 2133 個保留位元符合原始 BIN。九筆 local RELA 尚未套用；0 UND 不代表兩個 admission provider 或最後的 tail provider 已知。診斷 VMA 為零，AUIPC 的原位意義仍須另外證明。

兩次 admission 都 fresh 讀取 `0x4013C`，是原始 `LUI 0x40` 得到 `0x40000` 再加 316；先前筆記的 `0x40013C` 是位址換算錯誤。初始 unsigned A3≤1039 的 guard 發生在 opaque call 前，不能推導 post-call S0 有界。loop 僅將比較暫存值縮為 uint16，來源與目的位址仍用完整 32-bit A1；零次 copy 保留原 A6。成功路徑還原 RA／S 暫存器與 SP 後，以不寫 RA 的 `JR T1` 轉移至 fresh `[0x40050]`。

正式 checker 每語言檢查 263 個負例：216 個 raw ELF 重新解析、11 個 typed rows、31 個 SSA／port、2 個完整 IR、3 個 MD。全部停用 whole-ELF pin，其中 261 個也停用完整 IR pin。完整來源／工具／header／五條實際配方與兩項 MD 依賴一起核對。

```sh
# Existing pinned Windows LLVM only; output must be a new directory.
python3 -B experiments/tsl9-transport-frame/probe.py --version 6 --out-dir experiments/tsl9-transport-frame/build/my-new-probe
python3 -B experiments/tsl9-transport-frame/verify.py --replay experiments/tsl9-transport-frame/build/verified-v1/c/verification.json
```

正式收據位於 `build/verified-v1/{c,cpp}/verification.json`；加入 `--require-firmware-ready` 必須拒絕並 exit 1。本輪只驗證 Windows 上已存在且綁定雜湊的 LLVM，沒有測試其他 OS 或下載工具。

[source-history.json](source-history.json) 保留六版來源與原始本機產物的雜湊：v1／v3 編譯失敗、v2／v4 配置不符、v5 的 ANDI／store 次序不符；同一配方下 v6 通過。早期版本包含錯誤位址或指令次序，僅供稽核，未整理進 `src/`。

這是離線 compiler／link／static evidence。未執行 target、ISA、MMIO 或 HOST 行為測試；未產生整機韌體 BIN，未操作藍牙／硬體。resident 身分、完整 IRQ／memory／ROM／晶片／OTA 相容性與座椅／免打擾對應仍未確認，不能宣稱可安全刷入。
