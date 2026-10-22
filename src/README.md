# 目前選用的逆向 C/C++ 原始碼

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

這裡集中目前證據較完整的可讀原始碼，作為後續重建的工作入口。共 52 個 C/H 檔；同一份 C 原始碼可依既定配方分別編譯為 C11 與 C++17。原始實驗與封存證據仍保留於 `experiments/`、`analysis/`，以便追溯。

## 原始碼位置與證據範圍

| 目錄 | 內容 | 目前限制 |
| --- | --- | --- |
| [native/init_mask](native/init_mask/init_mask.c) | V4.1.60 初始化末端的 register-mask leaf | 完整 30-byte 函式與官方 BIN 相同；不證明完整啟動或實體配置 |
| [native/irq/irq_flag.c](native/irq/irq_flag.c) | 向量slot39的狀態／旗標函式 | 完整76B／21指令與官方16FB6相同；兩次即時狀態讀取／byte更新及MRET保留，原IRQ上下文與周邊身分未證 |
| [native/irq/flag_consumer.c](native/irq/flag_consumer.c) | 17002 的 GP 旗標消費函式 | 入口8B／主體54B；兩個未解決JAL以外54B與原廠相同，另驗部分連結相鄰關係；接收函式與provider ABI仍未閉合 |
| [native/receive](native/receive/receive_wrapper.c) | 16B0A 接收入口與尾端 register 寫入 | 入口14B／主體56B，非呼叫54B相同、4個JAL未解析；實體S0／S1與frame埠保留當下狀態，未新增C frame；下游ABI仍未閉合 |
| [register read](native/receive/register_read.c)／[write](native/receive/register_write.c) | GPIO選擇、32B frame與三次SPI傳輸 | read72B／write76B，非呼叫60B／64B與原廠相同；保留fresh槽位與清理前讀RA；單體物件保留SPI呼叫，另於352B部分連結綁定真實定義 |
| [SPI transfer](native/receive/spi_transfer_ports.c) | SPI輪詢／資料葉函式 | 8個架構區域與5個RVC埠，獨立原位連結完整72B／25指令相同；非一般C ABI或實機證據 |
| [packet receive](native/receive/packet_receive.c) | 封包接收、DLC／ID與共用出口 | 142B／52指令，3區域14／116／12B；120個非控制位元組相同，4個JAL與2個finish分支仍待解析；private ABI、硬體與燒錄未證 |
| [ring insert](native/receive/ring_insert.c) | 接收佇列與fresh resident間接呼叫 | 5個架構區域，原位連結完整92B／32指令與原廠相同；保留PC衍生table與呼叫後S0／S1；resident身分、caller bounds與硬體未證 |
| [ring IRQ adapter](native/irq/ring_irq_adapter.c) | 條件式frame與兩個MRET出口 | 52B／17指令，42個非控制位元組相同；3個edge仍待解析、2個UND；保留then-live SP埠，完整IRQ／provider ABI未證 |
| [native/irq](native/irq/interrupt_registers.c) | 四個 register helper 與 IRQ 初始化 | 四個 helper 各 30 bytes 相同；初始化正常出口有證據，180B 超出原144B，非同步等價未證 |
| [native/timer](native/timer/delay.c) | V4.1.60 計時器暫存器契約 | 完整54-byte leaf與官方相同；獨立編譯入口，尚未替換 NV callback／OTA BIN |
| [native/nv/nv_write_frame_contract.c](native/nv/nv_write_frame_contract.c) | 新 NV write callback frame／fresh source contract | 已量測原32B frame／source位置及前40B除JAL相同；結尾 LI0 提早，fault／IRQ等價仍未證 |
| [native/nv/nv_read_registers.c](native/nv/nv_read_registers.c) | NV read 暫存器介面 | 30B／14指令；wrapper無新增A3寫入及RA scratch；原版13指令，順序與provider仍有缺口 |
| [native/nv/nv_read_live_count.c](native/nv/nv_read_live_count.c) | NV read 保留原count | 30B／13指令；直接A2移位與原10B call window相同；frame／返回順序及installed provider未證 |
| [native/nv](native/nv/nv_write_callback.c) | NV read/write、timer 與 Flash helpers | 已採用兩處 A1 clobber 修正；write frame、source reload、timer 出口及間接 provider 仍有限制 |
| [native/adc](native/adc/caller_bank.c) | caller 專用 ADC 設定與真實 volatile port | 保留已知 live register bank；新增16-byte frame及 alias／IRQ限制 |
| [native/clock](native/clock/clock_query.c) | 較完整的 clock query／field register 結果 | fields正常出口有證據；query完整分支機器語意未證，196B超出原174B |
| [native/clock/clock_init.c](native/clock/clock_init.c) | BOOT／Runtime 時鐘初始化 | 232B／93指令，入口直接進入C主體；原始cold tail與完整IRQ／ABI及硬體仍未證 |
| [native/startup/init_writes.c](native/startup/init_writes.c) | 9250 初始化鏈的五筆有序寫入 | 完整40B／15指令與官方9F4C函式相同；五筆volatile word寫入，只改A4／A5；周邊身分與完整啟動未證 |
| [native/startup](native/startup/reset_memory.c) | Runtime reset記憶體／CSR交接 | reset138B／38指令＋clock232B，保留RA18724且未覆蓋下一函式；vector／main／resident與cold／間接入口未閉合 |
| [native/resident](native/resident/native.c) | SDK resident candidate 的 compare／fill／copy | 正常記憶體投影；並非已確認原機 ROM，scratch／fault／尺寸差異仍存在 |
| [reference/v4100](reference/v4100/dnd_actions.c) | 免打擾、一般設定、GATT framing 行為模型 | 來源是 V4.1.00；外部 provider 仍有未知，不混入 V4.1.60 原機實作 |

[source-manifest.json](source-manifest.json) 記錄每個檔案的原始來源、來源／整理後 SHA256、逐項 include 調整、兩處 A1 宣告修正，以及每個編譯入口的證據與限制。較新的 volatile source 實驗尚未解決 frame／slot 差異，仍保留在實驗目錄。

## 使用方式

在專案根目錄執行：

```sh
python3 scripts/verify-curated-source.py
```

預設只核對來源與清單，不需 LLVM。Windows 可將 `python3` 換成 `py -3` 或已安裝的 `python`。

若已安裝支援 RISC-V 的 LLVM，可明確指定工具目錄：

```sh
python3 scripts/verify-curated-source.py --tool-dir "/absolute/path/to/llvm/bin"
```

腳本依 manifest 選擇二十六個 native translation units，對原始與整理後版本分別編譯 C11／C++17，再讀取物件並比較所有函式、配置區段與 relocation。包含式 C core 由對應入口編入，不能把所有 `.c` 當成互不重複的連結單元。V4.1.00 reference 不納入此原機物件編譯；本次未重跑舊 HOST 矩陣。

本輪以 Android NDK 27.1.12297006 的 LLVM 18 在 Windows 實際通過 52 組比對（104 個物件），收據為 `build/curated-source/ring-irq-20261023-v2/verification.json`。舊 SPI 整理收據保留為歷史快照。Python 入口使用標準函式庫，未實機驗證其他作業系統；更換工具鏈需重新通過相同檢查，不下載工具或搜尋編譯旗標。

既有結果可唯讀重播：

```sh
python3 scripts/verify-curated-source.py --replay "/absolute/path/to/verification.json"
```

**這是原始碼整理與離線證據，不是完整韌體 build。** 尚未證明原機晶片、installed ROM、記憶體 ownership、完整啟動／中斷或 BLE OTA 相容性；重建韌體尚未完成在原硬體成功刷入及正常執行的驗證。腳本不執行 RV32／MMIO，也不產生或燒錄韌體 BIN。

[reset／clock整合檢查](../experiments/tsl9-runtime-reset-clock-fit/README.md)另外核對連結相鄰、原呼叫／RA、IR及負例。舊收據保留為本機歷史快照；其凍結檢查器可能拒絕此新版來源。

[SPI單體與管線檢查](../experiments/tsl9-spi-transfer-leaf/README.md)另外驗證已解析的函式機器碼與352B ET_REL連結；來源副本比對本身不解析這些架構邊界。

[Packet單體檢查](../experiments/tsl9-packet-receive/README.md)使用獨立 verifier；正式收據入口為本機 `experiments/tsl9-packet-receive/build/verified-v2/{c,cpp}/verification.json`。原始碼整理本身不解析六個控制轉移或補足 provider／IRQ ABI。

[ring與接收鏈原位圖](../experiments/tsl9-ring-insert/README.md)另外區分已解析的局部程式圖、未知的動態resident provider，以及完整韌體相容性。
