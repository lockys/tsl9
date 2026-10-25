# Selector 狀態與查表資料：離線重建

`EBAC..ECA8` 的完整狀態流程已重建為 C，連同四個原始唯讀查表物件分別以 C11／C++17 編譯。252 bytes／81 條程式指令、26 個直接轉移與 61 個資料 bytes 均通過原始位元組比較；資料長度為 16、15、15、15，沒有納入相鄰 padding。

| 項目 | 已確認的靜態行為 |
|---|---|
| 狀態記憶體 | A2 指向狀態 byte +0、計數 byte +1、先前 selector byte +2 與時間 word +4；其他狀態值直接返回。 |
| phase 0 | 與完整寬度 A1 基準比較 selector；依 `(A0-58)&255 <=3`、計數與先前 selector 決定遞增／回繞或設 255 sentinel。保留全部比較寬度與存取順序。 |
| phase 1 | 完整輸入 selector 與已儲存 byte 相同時，以無號 32 位元 `now-stored` 差值是否大於 499 判斷後續路徑；不同時清 phase。沒有假設時間單位。 |
| phase 2 | 輸入等於基準時傳遞通知代碼 4，再用一個 halfword store 同時清 phase 與計數；先前 selector／時間仍保留。 |
| 通知 | 透過仍未提供的 `E220` 傳遞原始 selector、計數與代碼 0..4；目前不把代碼命名為特定按鍵或車輛動作。 |
| 四張 byte 表 | 提供 `1A4E4` 的 16 bytes，以及 `1A518`、`1A528`、`1A538` 各 15 bytes；對應前輪 high-nibble／signed REM15 索引範圍。每段都符合索引 bit 的 XOR 仿射關係，不另指定 CRC 演算法。 |

證據：[原始程式與資料](evidence.json)、[重建 C](../../src/native/receive/selector_storage.c)、[編譯與比較](../../experiments/tsl9-selector-storage/build-v1.py)。[English](readme.en.md)

完整來源證明通過 218 組／436 個物件；接上1個函式與4個資料入口，新增E220缺口，尚缺 122 個。45,658 個選用原址 bytes 吻合；靜態流程涵蓋 2,515 個直接轉移，一般延續位置無缺口，選用元件已無缺少本體的回呼位址參照；執行期間接目標仍未證明。時間單位、功能歸屬、私有 ABI 與硬體／OTA 尚未證明；沒有執行目標或硬體，沒有新 BIN。
