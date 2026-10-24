# 離線 filter setup 架構來源

選用 `src/filter_setup.v2.c` 與 `src/helpers.v2.c`。共404B、152指令、33個實體區域；C/C++ native trial 均保留原廠全部非 relocation bits 與17個 typed control 的目的地。

這是 native 靜態 trial，不是 formal proof、可執行元件或燒錄 BIN。四個既有 provider 保持真依賴；resident、IRQ、記憶體所有權與普通 ABI 未證明。

`selected.json` 記錄來源、範圍與產物雜湊。失敗來源/trial 保留。原始 build 收據與 logs 含本機路徑，留在本機。

main v1 因 reserved S1 引發編譯器要求堆疊；v2 以實體 S1→A2 narrowing port 保留原序。helper v1 的 shift 被提早；v2 以 A0 read/write port 固定在 RA/SP 恢復之後。

[English](readme.en.md)
