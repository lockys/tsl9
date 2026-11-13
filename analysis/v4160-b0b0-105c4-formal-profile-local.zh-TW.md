# V4.1.60：B0B0 carrier 與 105c4 profile 的局部離線觀察

本紀錄不是完整 BIN 驗收，也不是正式來源整合。以下實驗均未執行、模擬或燒錄目標。所用實驗驗證器與測試尚未隨本紀錄發布；這是本機觀察，不是 clean-main 可重播或 CI 通過的聲明。

## B0B0：正式重建的 RAM carrier

在本機使用 manifest 固定的 `runtime-reset` profile，分別編譯完整 `src/native/startup/reset_data.c` 的 C11、C++17，經 LLD relocatable GC 擷取其 `.bss.tsl9_reset_ram`。carrier 為 35160-byte NOBITS，實驗腳本將它放在 `0x20004000`，並在同一區段定義 `destination = tsl9_runtime_reset_ram + 0x7eeb`。這是重建的地址模型，不是原廠來源或物理記憶體配置的證明。

已發布的純 C `experiments/v4160-b0b0-symbolic-c/leaf.c` 以 medany、`-mno-relax` 和額外固定 x11–x14 的實驗 flags 編譯；在 `0xb0b0` 連結出的 10 bytes `97170020a38da7e28280` 與固定 BIN 對應窗口相同。先驗證並使用原有 named `.Lpcrel_hi0` LO12_S anchor；另以修改暫存 ET_REL 的 section-symbol fixture 做連結，是合成 fixture，不是聲稱 LLD 自然產生此形式。錯地址、缺／重複 provider 和 raw ELF 變異等有限負例均在本機檢查。

探針預期輸出 `INCOMPLETE_FAIL_CLOSED`、exit 1。其測試包裝在 normal 和 `-O` 各 7 項通過。本機檢查不證明這個 RAM 載體是原始 data owner、呼叫者的 private ABI 可相容、正式 aggregate guard 可接受或完整映像相同。實驗依賴 Python、NDK Clang／LLD 和 resource header；工具 pin 不認證動態依賴與作業系統，並發替換仍有 TOCTOU。

## 105c4：純 C leaf 在兩組 profile 下的局部編譯

`experiments/v4160-new-leaf-turn/leaf.c` 為實驗候選，不是正式 owner。固定 `src/source-build-manifest.json` 的 `queue-consumer-a0-a5` 完整有序 C11／C++17 profile；另用舊實驗的簡化 flags 比較同一候選。在每組 flags 後加實驗 symbol 映射與 `-nostdinc`，並非正式 aggregate build。固定 NDK Clang 18.0.2 編譯四個 ET_REL：四者的 `.leaf` 均為 `034535007115133515008280`，等於下列 BIN 的 `0x105c4` 處 12 bytes；當次四個完整 object 的 SHA-256 亦相同，為 `4be6126f10b851cc7729d4579fccb9c66330b5fa604b861881e48e863a8e440c`。此個案相同不代表不同 flags 普遍等價。

兩語言各以 `-DNEGATIVE` 實際編譯 `==5`，得到 `034535006d15133515008280`，由完整 leaf byte 比對拒絕。測試額外核對實際 compiler argv 與另一段有限 section reader 抽取的 object bytes。探針預期 `INCOMPLETE_FAIL_CLOSED`、exit 1；本機 normal／`-O` 測試各 6 項通過。暫存 ELF 未保留，不可從本紀錄獨立重解析。

reference BIN 為 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，76800 bytes、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，base `0x8000`。固定 hash 只識別位元組，不是原廠認證。

本項尚未完成原址 final link、formal remap、原／split `.llvm_addrsig` 語義、未選區段與符號差異、caller ABI 或完整映像驗收；不得因此放寬正式 guard。
