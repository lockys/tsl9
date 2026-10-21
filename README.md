# TSL9 offline C/C++ reconstruction / TSL9 離線 C/C++ 重建

## English

This private repository preserves the original APK,22 distinct decoded updater
BINs,readable C/C++ behavior models,source-bound native instruction carriers and
offline verification tools. Version labels alone do not prove hardware suitability.
**No rebuilt BIN has been verified to install and run through the original BLE OTA.**

The full goal remains necessary TSL9 functionality plus the original execution
layer,with hardware,startup,resident ROM,memory,IRQ and update compatibility proved
individually. Source observation,synthetic host tests,address witnesses and physical
evidence remain separate. Original/rebuilt firmware is not executed or emulated.

| Content | Location / current scope |
| --- | --- |
| Original APK1.2.7 | [APK](artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk),48,067,278 bytes |
|22 original decoded BINs | [Firmware archive](firmware-downloads/legacy-options-2026-10-20/BINs/) |
| V4.1.60 native carriers | [Native project](experiments/tsl9-v4160-startup/); latest actual691 allocations/8,280 RELA/one true resident UND |
| Reset / IRQ data effects | [Reset](experiments/tsl9-v4160-reset-contract/) / [IRQ](experiments/tsl9-v4160-irq-frame-contract/) |
| BOOT / UID | [Command](experiments/tsl9-boot2580-command-adapter/) / [UID](experiments/tsl9-boot2580-uid-helper/) |
| Reference byte-copy | [C/C++](experiments/tsl9-resident-copy-reference/);58B/18 source instructions |
| Reference entry/initializer | [C/C++](experiments/tsl9-resident-entry-reference/);230B/66 instructions plus4B header |
| Evidence and limitations | [Verified milestones](docs/verified-milestones.md) |
| Published file hashes | [Manifest](publication-manifest.json) |

The selected Dec2023 V1.31 candidate does not identify the installed resident.
Its second initializer copy requests140 bytes,but the captured tail supplies136.
Actual main+tail stops at READ32 source0x6EB2C; main-only stops at0x6EAA4.
Neither can skip that read to zeroing or MRET. Synthetic unknown-memory fixtures
test the suffix without filling the original artifact or proving real Flash behavior.

The76,800-byte [offline original-layout image](artifacts/offline-images/ID2966-V4.1.60-source-image-fidelity/NOT-FLASH-VALIDATED-original-layout.bin)
is byte-identical to original ID2966 and remains NOT-FLASH-VALIDATED. A SHN_ABS40000
address witness does not implement __tsl9v4160_rom_entry. Exact MCU/PCB,installed
BOOT/ROM,physical memory/IRQ ABI and OTA acceptance remain unproved. Historical
stage counts apply only to their original scope.

### Local verification and publication

The retained environment is Windows/PowerShell7,Python3,MSVC BuildTools and NDK
27.1.12297006 Clang/LLD. Historical tools may require fixed paths and local archives;
recent source proofs/model verifiers resolve this snapshot's analysis inputs.

```powershell
python scripts/verify-publication.py
pwsh -NoProfile -File experiments/tsl9-resident-copy-reference/verify.ps1
pwsh -NoProfile -File experiments/tsl9-resident-entry-reference/verify.ps1
```

Add -Cpp for C++17. Passing establishes only the declared source/host scope.
Commit/push follows each verified milestone. New documents are English plus
Traditional Chinese; sealed historical bytes stay unchanged with companion notes.
Real identifiers,credentials,private request/response logs,unrelated work and
temporary builds are excluded. Original APK/BIN rights remain with their holders.

## 繁體中文

此私人儲存庫保存原始APK、更新器回傳的22份不同解碼BIN、可讀C/C++行為模型、有來源依據
的原生指令carrier及離線驗證工具。版本標籤不能證明硬體適用性。**目前沒有已驗證可由
原藍牙OTA安裝並在原硬體執行的重建BIN。**

完整目標仍是TSL9必要功能與原機執行層，逐項證明硬體、啟動、resident ROM、記憶體、
IRQ及更新相容性。來源觀察、合成host測試、數值witness與實體證據分開；沒有執行或模擬
原始／重建韌體。上表提供APK、22份BIN、Runtime、reset／IRQ、BOOT／UID、copy／entry
重建程式及最新證據連結。最新原生實物為691配置／8280 RELA／1個真正resident UND；
歷史文件的舊數量只適用各自階段。

Dec2023 V1.31只是候選，不是實機resident辨識。第二段初始化請求140B，tail只捕獲136B；
主段加tail在0x6EB2C的READ32停止，只有主段更早在0x6EAA4停止，不能先跳到zero或MRET。
合成未知記憶體fixture可驗後綴，但不補原檔，也不證明實體Flash會回什麼值。

76,800B original-layout離線image與原ID2966逐byte相同，仍標示NOT-FLASH-VALIDATED。
SHN_ABS40000位址witness不是resident實作；確切MCU／PCB、原機BOOT／ROM、實體記憶體／
IRQ ABI及OTA接受都未證實。byte-copy有58B／18來源指令，entry／init／seed有230B／66
指令，另4B header；這些是有來源條件的重建，不是完整恢復的原始碼。

### 本機驗證與發佈

使用上方host指令；-Cpp可驗C++17。環境為Windows／PowerShell7、Python3、
MSVC BuildTools及NDK27.1.12297006。部分歷史工具需固定路徑／本機archive，不保證只靠
GitHub快照即可重播。通過只表示其來源／host範圍成立，不代表實體OTA或車輛功能。

依指定在每個完成驗證的里程碑commit／push；沒有啟用固定每小時publisher。新文件採
英文＋繁體中文，歷史封存bytes不改、改附雙語說明。發佈排除真實裝置識別資料、憑證、
私有請求／回應、無關檔案與暫存build。原APK／BIN權利仍屬各自權利人。
