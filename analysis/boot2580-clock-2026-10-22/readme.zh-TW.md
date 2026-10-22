# BOOT 時鐘初始化來源核對

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

原廠 ID2580 BOOT `[0x2C78,0x2D62)` 與 ID2966 Runtime `[0x1874A,0x18834)` 的 **234 bytes／93指令完全相同**，SHA256 `e0debe8b77025cfb56144045a0aa7524b7a2cd2ad0bd3daa2d880408ad9758f5`。檔案offset分別為0x1C78及0x1074A。

[ledger.json](ledger.json) 保存93列原始bytes／運算元、43個記憶體存取位置及14組read-modify-write。本輪重讀兩份原檔，並以既有radare2重新對照93列；沒有執行指令、HOST模型或MMIO。

## 已確認的局部契約

- 沒有子呼叫或CSR指令；只改寫SP及A2–A5，正常返回恢復16B frame。
- MMIO數值範圍為40021000／04／08；live stack欄位為SP+8及SP+12。
- 第一個poll以fresh counter與ready欄位判斷；4096是普通無alias情境的相等終值，0x20000是ready mask。
- 離開第一個poll後再讀狀態；保留cold tail、兩次same-value寫入。後兩個poll沒有軟體timeout。
- leaf內沒有數值位址4004C的明示寫入。這不排除實體alias、MMIO副作用、中斷或其他writer。

## 離線重播

```sh
python3 -B analysis/boot2580-clock-2026-10-22/check.py --project-root .
# 選用：加上 --r2-exe "/path/to/r2" 重新擷取靜態反組譯
```

`original_fields.py` 僅保留既有raw operand核對函式；`original-runtime-rows.json` 是對應原始列，不包含舊HOST測試／報告入口。檢查只使用專案內來源，不依賴舊工作區。

可讀行為基礎是既有[clock_contract.c](../../experiments/tsl9-v4160-clock-contract/src/clock_contract.c)；新原生元件見[boot-clock-init](../../experiments/tsl9-boot-clock-init/README.md)。來源相同不證明installed resident、實體時鐘頻率、完整ABI／IRQ或OTA相容性。
