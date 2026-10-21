# 條件式 registry-consumer 原始片段

來源是 ID2966 / V4.1.60 的 76800-byte Runtime，SHA-256：
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。
本輪只保存有原始指令及完整 bounded CFG 證據的 `[901A,907A)`：96B、38 個指令，
不是將其他 opaque 地址一律當成函式。

## 片段內可確認的機器行為

若從 `901A` 以有效機器狀態進入，片段掃描 a1 的 bit0..14，處理第一個置位的 slot。
slot base 由 `9034/9038` 形成 `2000BE08`，stride 為12；
`9040` 從 slot+4 讀取 a3；只有 callback 非零時，才在 `9048` 從 slot+8 讀取 argument 到 a0。
callback 非零且 mode byte 為0時，先清除 slot+4／+8，再在 `9058` 透過 a3 間接呼叫；
callback 為零的分支直接進入移除已處理 bit 的返回路徑。
返回路徑以當時的 s0／s1 做 XOR 並保留低16bits；若回呼正常返回且保存原程式期望的
s0／s1，這才等同移除原 mask 的選定 bit。沒有選中 slot 時返回0。
這些是條件進入片段後的原始指令行為，沒有把 a0／a1 定義成已確認的 ROM C ABI。

完整 CFG 由原始分支與 continuation 走到 loop／`906E` RA return，恰好覆蓋96B，
沒有 holes、原配置 overlap、直接 callee 或向外 tail。
五條直接控制分支的原始目標是 `902C→9070`、`9042→905A`、`904E→9058`、
`9072→9026`、`9078→9066`；另一項控制是尚有動態目標義務的 `9058` C.JALR。

## 有意保留的未知入口

唯一新增全域 label 是 `__tsl9v4160_conditional_code_901a`：
GLOBAL NOTYPE／size0，位於真 executable section 內；header 只公開 byte-storage identity，
沒有 C 函式 signature，也沒有 STT_FUNC。

原 `__tsl9v4160_address_901a` 仍是 NOTYPE0 UND。
原來 `909A` 形成該值並傳給未知 ROM callee 的 relocation 不改指向新 label；
同數值的已保存片段不能代替尚未證明的原 ROM 參數／entry／callback ABI。
其他15個 opaque canonical 與完整23個原 UND 同樣保留。

PCREL HI 使用已存在的 `__tsl9v4160_ram` OBJECT35160 加 `7E08`，
LOW 仍指向本 section 的 own-HI anchor；不新增 RAM、RAM view 或猜測別名。
這只證原址及既有模型的真 storage identity，尚未證明實體 SRAM、初始化或 stack 可用性。

## 重播與驗收

在此資料夾執行：
`python verify-data-anchor-extension.py --spec evidence/conditional-dispatcher-integration.json`。
D 交付副本可用預設 firmware；W 副本另加
`--firmware ../../exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`。
從其他工作目錄執行時，spec／firmware 請使用正確絕對路徑。

原 engine、舊 specs／程式／資料保留；新模組增加96B code、7項 RELA、零RO，
ROOT fresh verification 通過：56004B code、3676B RO、59680B file-backed payload、
600個非空配置、6679RELA；627個module providers、2codeviews、1獨立data-anchor、
534relative32 expressions、27RAMviews／35160B NOBITS保持。C11／C++17產物一致。
ROOT receipt 為 `build/data-anchor-extension-a137702d5f1041ec919699a600e75a60/verification.json`，
SHA-256 `b7c1f42a25b5cc7b1824ae58a8764d7357865f4e31d285527f3c7b5e55712515`。
Native 兩語言各拒絕13個實際負例，合計26個，包含錯誤canonical同section alias、
額外canonical storage、helper FUNC／ABS／visibility／size、RAM ABS、錯HI／LOW／branch、漏RELA與byte。
獨立審查與D目的地驗證的實際結果另以本輪receipts為準。
strict link 必須繼續拒絕全部原23個真UND；numeric witness 不可當成韌體。

原機 resident／低RAM／啟動／IRQ／實體記憶體及藍牙 OTA 契約仍未證明。
全程離線、沒有執行或模擬 Runtime、沒有硬體I/O／燒錄，沒有可宣稱可燒錄的重建BIN。
