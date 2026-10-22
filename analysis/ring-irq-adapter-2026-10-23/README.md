# 52B Ring IRQ adapter

[English](readme.en.md)

官方 ID2966 `[0x12C24,0x12C58)` 已重建為 [C／C++ 架構區域](../../src/native/irq/ring_irq_adapter.c)。五區為14／10／18／6／4B，合計52B／17指令；42個非控制位元組與原廠相同。**三處控制立即數仍待解析，不宣稱完整52B相同、一般C ABI或可燒錄韌體。**

已確認的局部流程：

1. A0=`0x40006400`，fresh LW32 `[A0+12]` 後 mask3；為零跳到 `0x12C54` MRET，不建立frame。
2. 非零時SP−=32，A2=SP+12，再A1=0；`0x12C38` JAL到`0x18D78`，RA續接`0x12C3C`。
3. Provider返回後用當下SP做LBU A2,+22、LHU A0,+12、A1=SP+23，A3=0；`0x12C4A` JAL到ring`0x12BC8`，RA續接`0x12C4E`。
4. Ring返回後當下SP+=32，`0x12C50` MRET。adapter自身沒有RA保存／還原或普通RET。

v1把SP當成C位址值，LLVM多產生兩個move，其中一個寫回SP，得到54B／19指令，linker依52B契約拒絕。v2使用明示物理SP存取埠，保留錯誤來源與原始本機量測；未覆寫失敗證據。

`component.ld`產生的partial ET_REL仍有3筆RELA：offset12 RVC branch到真實empty FUNC、offset20 JAL到UND `18D78`、offset38 JAL到UND ring。ring另有獨立重建與原位證據，但本單體仍明確標記UND，未製造ABS或raw-byte假provider。先前586B原位graph未更改，本輪尚未把IRQ整合成完整可執行圖。

重播需保留本機build artifacts，公開JSON本身不足以重建整個build目錄：

```sh
python3 -B experiments/tsl9-ring-irq-adapter/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-ring-irq-adapter/build/verified-v2/c/verification.json
python3 -B scripts/verify-curated-source.py --replay build/curated-source/ring-irq-20261023-v2/verification.json
```

Windows可用`python`。工具限本機既有NDK LLVM18；其他OS／工具鏈未驗證。正式checker／收據／負例分類與實測結果記錄於[summary.json](summary.json)，`--require-firmware-ready`用於拒絕未完成的整機證明。

整理後`src/`有52個C/H、26個native編譯入口，來源／整理版C11及C++17通過52組比對、104個物件。舊50組結果及301個artifact雜湊不變。新收據含106個輸入、313個artifact及104條配方／MD。

公開證據：正式C／C++收據採變數路徑，公開副本逐位元組相同；[curated-source.json](receipts/curated-source.json)則是明示匿名衍生檔。原始收據SHA256為`8736e11ca4f0b7f1368eab4531a39e92f564996eb9e47343349094575740ef80`，保留本機；只替換路徑字串／字典鍵，反向JSON相等。衍生檔不宣稱可按原始收據雜湊直接replay。原始BIN／APK、歷史公開衍生檔與Git歷史未改寫。

下一步是[164B provider的可讀C重建](provider-next.md)。其局部SP保存、fresh word讀取與長度／欄位依賴已有靜態線索，完整IRQ上下文、resident、MMIO身分、晶片及OTA仍未知。未執行target／ISA／MMIO、硬體或第三方API，未產生完整韌體BIN。
