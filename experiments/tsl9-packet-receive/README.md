# Packet receive：v5 離線原機契約

[English](readme.en.md)

[packet_receive.v5.c](src/packet_receive.v5.c) 對應官方 ID2966 的 `[0x16A7C,0x16B0A)`：C11／C++17 都編譯為 142B／52 指令，三個真實架構區域為 14＋116＋12B。120B 非控制碼與原廠相同；4 個 JAL、2 個分支仍是 **pending 重定位**，不是完整可執行函式或可燒錄韌體。

原位 frame、incoming A1、then-live S0／S1／S2、DLC 的 A4 算術，以及兩種拒絕出口／ring 返回後的 A0 都列入檢查。GPIO、mask 與 ID 算術由 C 表達；保留實體暫存器、堆疊與跨區控制的明示 asm ports，因此這不是一般 C ABI。

```sh
python3 -B experiments/tsl9-packet-receive/verify.py --language c --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-packet-receive/build/my-check/c
python3 -B experiments/tsl9-packet-receive/verify.py --language cpp --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-packet-receive/build/my-check/cpp
python3 -B experiments/tsl9-packet-receive/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-packet-receive/build/my-check/c/verification.json
```

`LLVM_BIN` 指向本機既有工具目錄。目前只驗證已記錄的 Windows NDK LLVM18 工具鏈；其他工具鏈須另行驗證，不會自動下載或搜尋旗標。輸出目錄須全新；Windows 可使用 `python`。兩語言各 41 個負例；`--require-firmware-ready` 必須拒絕並 exit 1。

舊 v1／v2／v3／v4 保留且未提升：v2 保留為 [packet_receive.c](src/packet_receive.c)；v3 修正初始化順序，v4 修正 DLC／A0／ID，但兩版仍因重複 epilogue 為 154B。v5 使用單一真實 finish FUNC，沒有複製原碼或修補物件 bytes。

[本輪證據與限制](../../analysis/packet-receive-v5-2026-10-23/README.md)／[舊版證據](../../analysis/packet-receive-native-2026-10-23/README.md)。原始建置資料留在本機；未執行目標、ISA／MMIO 模擬或硬體操作。完整 ring／resident ABI、IRQ／fault、晶片與 OTA 仍未證明。
