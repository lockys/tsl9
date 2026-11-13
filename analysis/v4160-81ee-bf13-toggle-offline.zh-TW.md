# 81EE 候選與 BF13 toggle 的離線觀察

## `0x81ee` 純 C leaf

對 76,800-byte 參考 BIN（base 假設 `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`），窗口 `[0x81ee,0x81f8)` 為 `17450020034575ce8280`：`auipc a0,0x20004; lbu a0,-793(a0); ret`，靜態解碼地址為 `0x2000bed5`。

`experiments/v4160-81ee-symbolic-c/candidate.c` 是獨立的 `extern volatile unsigned char` getter，沒有 inline asm。以人工 ABS 地址 `0x2000bed5`、原址 `0x81ee`、Clang/LLD 的 RV32 medany `--no-relax` 條件分別編譯連結 C11／C++17，兩者 `.leaf` 的 10 bytes 均與該 BIN 窗口一致。地址錯置 `+0x1000` 的負例分別得到 `17550020034575ce8280`。正常及 Python `-O` 模式各 12 項測試通過，含 ELF relocation、symbol、ABI flags、範圍及拒絕案例。此 10-byte 匹配不證資料 owner、caller ABI 或完整映像。

驗證器、測試與 README **尚未包含於本提交**：當次 `verify.py` SHA-256 `fcec1a63cc742fb3d46cca625aff049e575d90406d1005ddde45dd5b5912faf9`、`test_verify.py` `94a964395dd21ecd5679f410b830691945574a0936198cba9e16935097ab0db0`。它們只在本機 `experiments/v4160-81ee-symbolic-c/`；這不是 clean checkout 重播或 CI 通過的證明。

## BD5A／BD64 toggle 的受限連結探測

從 `src/native/receive/action_dispatch.c` 的已驗 source 編譯完整 caller，再以 `ld.lld -r --no-relax --gc-sections` 選出 `0x15e5a` 和 `0x15e5e` 的兩個 caller sections；未選的原 unit sections **沒有保留**。caller 仍含 inline asm，並非純 C。已發布的 `candidate.c` 透過編譯選項映射為兩個 provider 名稱，並使用共同的人工 ABS `0x2000bf13`；BD5A 額外使用 `-ffixed-x11` 至 `-ffixed-x14`。此受限 profile 不等於正式 ABI。

本輪實際 normal／`-O` 的 C11／C++17 探測，原址、無 PT_LOAD 的正例連結四個選定 sections；兩個 caller 加兩個 leaf 的 46 bytes 與參考 BIN 窗口相同。把資料 witness 改為 `0x2000cf13`，caller bytes 不變，BD5A／BD64 leaf 分別成為 `97170020a38ca71a8280`、`171500200345f51a8280`。缺少 BD5A provider 的 linker 命令非零退出。

這仍是 **`INCOMPLETE_FAIL_CLOSED`，探測器按設計退出 1**，不是正式整合驗收：GC 後 `.llvm_addrsig` 有 524 bytes、`sh_link=0`，其跨單元語義、完整 section-symbol／RELA metadata 投影、原 unit 其他 sections、真實 data owner 和 caller 的 private ABI 均未閉合。caller 需既有 stack frame，不能將它當一般獨立 C 函式。人工 ABS 不配置資料，也不證執行期無干擾；read／write 並非原子 toggle。

本次提交前，實際核對 GitHub `main` 的 `2b6904a1fc092f411f09eaf75a3d3658b3980342` 非截斷 tree 中六個檔案與本機 raw Git blobs 相符：caller `85ad17c254f6632ba22ce2696873c0f22f48b5c2`、source manifest `66de11cd6310fb3e08cd1710a5a0f2aac84dc6e6`、action spec `4085c1f790615f971b0b09fe849e24768bee4685`、BD5A candidate `0d5507f9a660ffb04ef23ea778224010ff6528b2`、BD64 candidate `f21a73487d6b7a60f11e3d5c2599cd22e8c14854`、BIN `e6cd0db8bd7d460a16967a5df9eadb42b04fa00d`。這只是列舉的 blob 一致，不證 origin→curated 鏈、完整 tree 或 link 等價。

探測器與測試仍在本機 `experiments/v4160-bd5a-bd64-toggle-gc-link/`，不包含於本提交。當次 `probe.py` SHA-256 `4206eb0578aabaabdd13da8b637ce9b742bc461f6f3e817a9ef862c3674fe531`，`test_probe.py` `9dc2305faa877668dc9fd5675ff4c9114d6e1eaadcae25c39b4663fa84fb1bd8`；測試覆蓋不足，不能把探測結果升格為 verifier 通過。工具、OS、DLL 與中間檔假設不被並行替換；暫存目錄不是安全 sandbox。未執行、模擬或燒錄目標。
