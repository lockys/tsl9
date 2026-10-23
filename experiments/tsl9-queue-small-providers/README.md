# V4.1.60 queue：兩個小型實際 provider

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

只重建原版V4.1.60的兩個leaf：[src/providers.c](src/providers.c)。普通C處理volatile byte load、u32比較、pointer sum及byte store；ASM只含空字串register ports。沒有複製opcode carrier、stub、ABS provider，沒有改consumer／curated source。

| Original PC | Raw | Instruction |
|---|---|---|
| `81AA` | `03c5710a` | LBU A0,167(GP) |
| `81AE` | `8280` | RET |
| `820C` | `8947` | LI A5,2 |
| `820E` | `63e7a700` | BLTU A5,A0,821C |
| `8212` | `9387010c` | ADDI A5,GP,192 |
| `8216` | `aa97` | ADD A5,A5,A0 |
| `8218` | `a3800700` | SB ZERO,1(A5) |
| `821C` | `8280` | RET |

## 實際結果與契約

官方完整BIN SHA256為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`、76,800B，分析base=`0x8000`。直接讀原檔的兩span並核全部關鍵operand；本輪不使用V4.1.00偏移或refs。status使用 **GP+167**。

- C11／C++17首次、單一固定配方均成功；object及linked元件的完整函式各為 **6B／2指令**、**18B／6指令**，逐byte等於原leaf。全部配置只有真實的兩個FUNC與24B AX code，無UND、global ABS、REL／RELA、writable／NOBITS／unwind、stack或callee。
- assembler已直接解析區內BLTU。0relocs是實際結果；不為湊relocation增加flag/profile，也不偽造target。檢查rs1=A5、rs2=A0、unsigned BLTU及目的offset16的真正RET。
- status正常返回A0=`zext_u8[GP+167]`，只寫A0。clear保留entryA0：unsigned index>2不存取memory且A5=2；index<=2寫0至 `u32(GP+193+index)`，A5=`u32(GP+192+index)`。clear只寫A5，兩leaf都不寫GP/SP/RA或其他GPR。
- 診斷link是 **VMA0**，函式spans為 `[0,6)`／`[6,24)`。原VA81AA／820C是原BIN追蹤身分，不能當成本元件原位placement。
- MD精確只含實際C檔與編譯器stdint.h；來源／工具／resource／完整命令及exit/log hash留於compile receipt。LLVM全8列raw回讀；IR明示fresh volatile byte load/zext、unsigned predicate、C pointer arithmetic及唯一conditional byte store。C++的noundef差異各自保留完整SSA hash。

每語言有12個actual raw ELF負例（object及linked各6個：machine、GP167→175、signed branch、store offset、ABS函式、writable allocation）及3個actual IR負例（GP偏移、signed predicate、nonvolatile store）。變異只在memory，沒有生成或執行錯誤provider；不是只拿收據常數比自己。兩份 [verification.json](build/component-v1/c/verification.json) 均可唯讀重播；build目錄不需加入Git。

## 重播

```sh
# Existing local LLVM and exact official file; all output is create-only.
python experiments/tsl9-queue-small-providers/build.py --project-root . --tool-dir /absolute/LLVM/bin --firmware /absolute/ID-2966-V4.1.60-decoded.bin --build-root /absolute/project/experiments/tsl9-queue-small-providers/build/new-run
# Static review / create-only receipt; no target execution.
python experiments/tsl9-queue-small-providers/check.py --project-root . --folder /absolute/project/experiments/tsl9-queue-small-providers/build/new-run/c --receipt /absolute/project/experiments/tsl9-queue-small-providers/build/new-run/c/verification.json
python experiments/tsl9-queue-small-providers/check.py --project-root . --replay /absolute/project/experiments/tsl9-queue-small-providers/build/new-run/c/verification.json
# Source metadata only; repeat review/replay for cpp.
python experiments/tsl9-queue-small-providers/check.py --project-root .
```

[verify.sh](verify.sh)是POSIX入口，`QUEUE_PYTHON`可指定Python路徑。只實測Windows Python及既有NDK27.1.12297006／LLVM18；POSIX shell執行未驗證，沒有重試已被拒絕的Git Bash。建置路徑與重播都限定本experiment/build；重播不啟動compiler或linker。

## 限制

這是兩個真實callee的離線code evidence，尚未與queue consumer做實際composition或納入整機image。原址映射、GP來源、memory validity/alias、IRQ/fault全域context、installed ROM與硬體用途尚未閉合。完全相同的leaf bytes不代表已證物理placement或安全刷寫。

**firmware_ready=false、OTA_ready=false、rebuilt_flashable_BIN=false**；未下載、連網、執行target/HOST model/ISA/MMIO/BLE/CAN或產生BIN。
