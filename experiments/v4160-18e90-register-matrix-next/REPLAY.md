# 0x18e90：純 C leaf 的固定暫存器矩陣

離線 C11 編譯並原址連結純 C `leaf.c`，不執行或模擬產物。必要 BIN 為 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；base `0x8000` 是本實驗的線性映射假設。編譯器為固定 hash 的 Windows NDK Clang 18.0.2，linker 為固定 hash 的 LLD 18.0.2；工具實際路徑和所有 pin 見 `matrix.py`。`leaf.c` 使用 `<stdint.h>`，Clang resource header 未 pin；Python、工具動態依賴、OS 與檔案系統亦未 pin。子程序繼承環境變數，Python `-I` 不隔離編譯器環境；假設沒有並行替換，hash 不證明來源可信。

`leaf.c` 是 `experiments/v4160-18e90-direct-c/candidate.c` 的同 bytes 副本，並非 `experiments/v4160-next-c-leaf-native/leaf.c`。後者名稱、section 與負例分支不同。既有 flash-image 亦有其他 C 加 inline asm 的實作；本候選並未取代正式 owner。

在 repository 根目錄執行，`--out` 必須是本目錄不存在的直接子目錄；會保存 ELF、object、來源快照與含本機路徑的 JSON，失敗亦可能留下部分產物。請不要公開原始收據中的使用者路徑：

```text
python -I -B experiments/v4160-18e90-register-matrix-next/matrix.py --out my-normal
python -I -B -O experiments/v4160-18e90-register-matrix-next/matrix.py --out my-optimized
```

每次使用 `-Oz`、`-O1` 各編譯、連結 x11–x14 的全部 16 個固定子集，檢查實際 ET_REL 與 ET_EXEC 的完整 8-byte section、符號、入口及 load mapping，並與完整 hash-pinned BIN 的 `[0x18e90,0x18e98)` 視窗比對。這次每種最佳化只有四個暫存器全固定時相符：`b7270240c8c78280`；其他子集使用其他位址暫存器，bytes 不同。

負例包含錯誤 VMA、缺輸入、真實 ELF/object bytes 與 entry 變異、衝突 PT_LOAD、錯誤 BIN，以及停用正式 guard 的控制。Python normal 與 `-O` 各實際完成 32 個 case。這只證所列來源、選項與工具下的局部 bytes，不證固定這四個暫存器在其他 C 寫法或工具鏈中是全域最小，也不證 ABI、正式配置、MMIO 行為或完整 BIN。
