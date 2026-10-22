# NV 寫入 callback：frame 與來源重讀

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

以可讀 C 重建官方 ID2966 V4.1.60 `[0x197BE,0x197F0)` 的堆疊與五次呼叫。這是獨立候選，尚未整合進 OTA BIN。

## 本輪改善

先前 volatile 單一來源 slot 的候選配置16-byte frame，來源在 caller SP−12。此版本以24-byte C frame object 加上編譯器保存的 RA／S0，實際產出：

- frame=32 bytes。
- RA 保存於 caller SP−4，S0 保存於 caller SP−8。
- 入口 A2 來源保存於 caller SP−20，在 unlock／erase 返回後才重新讀取。
- 不清零其餘 frame bytes；原函式沒有初始化那些位置的證據。
- 五次 JAL 都保留真正 relocation，必須連到真實 C helpers，沒有 ABS／固定回傳 stub。

C11／C++17 的 callback object 皆為50 bytes／20指令。前40 bytes在遮除五個 JAL 的 relocation 立即數後與官方完全相同，包括 prologue、來源 save／reload及呼叫參數準備順序。

## 尚存的具體差異

原始結尾：`LW RA → LW S0 → A0=0 → SP+=32 → RET`。

目前結尾：`A0=0 → LW RA → LW S0 → SP+=32 → RET`。

因此正常返回的 A0／RA／S0／SP 可一致，但 restore fault 或中途 IRQ 時的 A0 不同；不能宣稱整個 callback 的機器碼或非同步行為相同。原始 callback 的固定 A0=0 也不是硬體寫入成功的證明。

使用最小 register／JAL bridge，C 本體保留 volatile source save／reload及有尺寸的 stack object。沒有裸函式、複製 opcode 或手寫整個 prologue／epilogue。原實驗 `native-v1` 曾把 A1/A0 兩個準備指令交換；修正 register dependency 後保留為 `native-v2`，不覆寫先前輸出。

## Provider 與驗證邊界

`src/flash_provider.c` 編入現有六個真實 Flash helpers，保留兩處 A1 clobber 修正與 noinline 呼叫邊界。`tsl9_delay_registers_19764` 使用已確認完整54-byte code相同的獨立計時函式，不能以舊 NV translation unit 內的 timer 代替。

本輪 component 驗證已通過 C11／C++17：三個 translation units、實際連結後的八個 FUNC、十個真實 JAL（包含五個 callback 目的地）、所有配置區段、UND／global ABS及 relocation，並保存 compiler dependency closure。六個 helpers 的 object code hash 等於既有配方，timer在連結後仍完整54B等於原 BIN。連結配方不使用 GC 或 provider stub。

C 元件共366B配置；C++元件共410B（程式366B加上44B .eh_frame）。C++的callback entry為0x2C，C則為0；這些僅是離線配置，不是原機Flash位址。兩者均無UND、global ABS或未解relocation。相同callback來源已整理至 [src/native/nv/nv_write_frame_contract.c](../../src/native/nv/nv_write_frame_contract.c)。

## 使用方式

在專案根目錄明確指定原 BIN、本機工具與全新build目錄：

```sh
python3 experiments/tsl9-nv-write-frame-contract/verify.py --project-root . --tool-dir "/absolute/path/to/llvm/bin" --firmware "/absolute/path/to/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/path/experiments/tsl9-nv-write-frame-contract/build/new-run"
```

Windows可改用 `py -3`／`python`。本輪實際工具為Windows Android NDK27.1.12297006／LLVM18，verifier核對既定工具與stdint hash；未實測其他平台。最新本機收據在 `build/component-v1/{c,cpp}/verification.json`，來源、工具、實際命令與日誌皆有hash。

唯讀重播不重新編譯：

```sh
python3 experiments/tsl9-nv-write-frame-contract/verify.py --project-root . --replay "/absolute/path/to/build/component-v1/c/verification.json"
```

來源等於入口 A2、恢復值等於入口 RA／S0，需要排除有害 frame alias／外部改寫。真實 helpers 的既有正常出口投影不能擴大為完整 fault／IRQ／installed ROM 證明。原函式 busy loop 沒有 timeout；此候選未加入會改變行為的超時。

所有操作只讀原始 BIN、編譯與連結本機元件。不執行 RV32／MMIO、操作硬體或聯繫非凡服務。完整原機相容性與可燒錄映像仍未證明。
