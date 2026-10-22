# Packet receive：未通過的離線候選

[English](readme.en.md)

[packet_receive.c](src/packet_receive.c) 是 v2 候選；[packet_receive.v1.c](src/packet_receive.v1.c) 保留第一版證據。兩版都未通過原始函式 gate，沒有納入 `src/`，不能用來產生可燒錄韌體。

v2 修正 incoming A1 被覆寫的實際 ABI 問題，前 34 bytes 已與官方相同；整體仍為 154B／58 指令，原碼是 142B／52 指令，並有出口 residue／排序差異。詳見[分析與匿名化收據](../../analysis/packet-receive-native-2026-10-23/README.md)。所有原始建置資料保留本機，沒有執行目標或 ISA 模擬。
