# TX register／frame ABI：正式元件證據

[English](readme.en.md)

正式 producer 是 `experiments/tsl9-v4160-tx-register-abi/verify.py`，包裝本目錄 `verify_native.py`。它從本次來源 fresh compile C11／C++17，經明示窄 assembly 入口與 source-owned frame scheduling，得到真實 280-byte 元件；沒有產生 BIN、整合完整映像、執行 RV32、硬體或網路操作。

```sh
sh experiments/tsl9-v4160-tx-register-abi/verify.sh --project-root . --tool-dir /path/to/audited/llvm/bin --language both
python -B analysis/v4160-tx-register-abi-2026-10-22/implementation/check.py --project-root .
python -B experiments/tsl9-v4160-tx-register-abi/verify.py --project-root . --replay /path/to/ordered/c/verification.json
```

研究工作目錄使用 `apk-analysis/tsl9-`，發布使用 `analysis/`。預設新建 UUID build；顯式 `--build-root` 須尚不存在且位於此 model 的 `build/`。`--firmware` 只指定固定 SHA-256 的原始驗證證據，不生成任何 code bytes。重播會明確拒絕建置用 tool-dir／language／output 選項，不重新編譯或執行。

每語言的 `pre/{c,cpp}` 是三個新來源的 compiler 產物：無預處理／include 的 raw assembly 入口、typed C body、typed C return leaf。另產生 body／leaf LLVM IR；`-MD` 實測 body 三個 project inputs、leaf 一個 input，加一個 Clang resource `include/stdint.h`。raw assembly 直接來源另行稽核，沒有偽稱使用 C dependency header closure。九個 pre native commands 均有 exact argv／profile／來源／日誌／退出碼紀錄。

`ordered/{c,cpp}` 的七個 native／Python commands 包含實際 explicit frame pass、`ld.lld -r`、strict missing-RAM link、數字位址見證、真正遠距 leaf 的 linker overflow 負控制，以及顯式 `--mattr=+m,+a,+c,+zicsr` 的完整反組譯。ET_REL sole AX allocation 為 280 bytes，真 FUNC offsets `0/8/278`、sizes `8/270/2`，恰三個標準 RELA `+4/type16`、`+128/type23`、`+132/type24`，唯一未解符號是實際 SRAM role。payload 必須逐 byte 等於真 entry、ordered typed body、typed leaf 的串接，不容 padding、fallback、helper 或 public ABS stand-in。

窄入口的標準 `.reloc` 讓 linker 擁有 branch 位移與 overflow 檢查；實際 unsigned guard `8A5A→8B6C` 在 frame 前，拒絕路徑不改 A0／RA／SP。普通 C dispatcher 的 290-byte 版本，以及外部分支被 assembler 放寬的 284-byte 版本，都保留為本機 rejected diagnostics，沒有把假設尺寸標成通過。

新 pass 僅排兩個視窗：typed body `+2..+12` 的五個既有 SWSP words，及 `+208..+270` 內五個既有 LWSP words。前者恢復 S0／S1／S2／S3／RA save order；後者把 RA／S1／S2／S3 read 排在 descriptor SH 前、S0 read 排在 SH 後與 ROM tail slot read 前。其他 words 順序及所有 metadata 不動。若 code storage 與別的 section／ELF headers overlap、typed function binding／visibility不符、window 有 symbol／RELA／interior target／callreturn，或不是精確 inventory，就拒絕。pass 不讀原 BIN、不產 opcode，也不宣稱與 unscheduled compiler output 在 alias／fault 情境等價。

獨立證據分工：`source-review` 封存原始前緣、saved-RA alias witness、來源 extraction 與 pre-motion 入口；`ABI-review` 檢查實際 entry／body／leaf、frame pre/post、三個 linked-byte 負控制、十四個 malformed-object guard controls，以及原 BLTU／新 BGEU 的互補 loop CFG、低16 counter 對 live S0、即時 payload effects、backedge 與 checksum finish（九個指令變異負控制）。正式 producer 在每份 artifact replay 重新執行固定雜湊的獨立 entry／frame／loop checks。

目前已改善 guard、兩個 gate 返回 PC `8A90/8AB6`、save／fresh-restore 的相對資料操作順序與 loop 關係。public entry 的真 FUNC size 是 8，沒有偽造原 whole-FUNC280 metadata。完整原 ABI、私人 symbol／computed targets、逐指令 interrupt／fault、完整映像整合及實體硬體相容性仍未通過；數字 `0x2000B18C` 只供 SRAM 位址見證，並非 provider 或板上記憶體配置證明。

`results.json` 選定兩份正式 C／C++ 收據；`receipts/` 只保存逐 byte 相同的 JSON metadata。預設 `check.py` 僅驗封存來源／metadata，`--require-local-builds` 才讀取原本機 archives，`--receipt` 則驗另一個 checkout fresh 建置的收據。執行檔、objects、ELF、IR、日誌與歷史診斷留本機 `build/`，不隨來源封存發布。`probe_adapter.py`／`probe_ordered.py` 是正式固定子 stages；`diagnose.py`／`inspect_temp.py` 僅是歷史診斷，正式 producer 不呼叫它們。
