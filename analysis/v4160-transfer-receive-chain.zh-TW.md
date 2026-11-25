# v4.1.60 傳輸逾時原指令至接收／佇列的串接

2026-11-26。原廠 BIN：`ID-2966-V4.1.60-decoded.bin`，76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

## 這次補上的證據

前一批[取樣迴圈驗證](v4160-receive-frame-cpu.zh-TW.md) 直接指定每次 `0x16896` 返回值。本次改為在**同一組暫存器、同一個 caller frame** 中執行該函式的原指令，再繼續取樣、guard 與 queue，直到未知 provider 入口停止。STATUS 與 DATA 的讀值仍為合成輸入，沒有實際 MMIO 或設備操作。

離線解碼與指令解譯一致顯示：`0x16896..0x168de` 只改寫 A0、A3、A4、A5，沒有堆疊存取，也不改 RA、SP、A1/A2 或 S 暫存器。新測試對每次返回比較其餘所有暫存器，而不是用抽象 ABI 保存假設替代這段指令。

| 傳輸路徑 | STATUS halfword 取樣 | DATA halfword 存取 | 返回 A0 |
|---|---|---|---|
| 第一階段逾時 | bit 1 等待 255 次，皆未 ready | 無寫、無讀 | 0 |
| 第二階段逾時 | 第一階段成功後，bit 0 等待 255 次 | 寫輸入低 16 位一次；不讀 | 0 |
| 成功 | 每階段第 1–255 次首次 ready 都可成功 | 寫輸入低 16 位一次，讀一次 | DATA 低 8 位 |

STATUS 位址為 `0x40013008`，DATA 為 `0x4001300c`。測試將不相關狀態位設為 1、兩個 readiness 位按指定次數給值，使測錯 bit 可以被觀察到。這是合成的存取序列，不證明真實外設時序。

## 對 caller 的條件性影響

對固定的其他 14 次傳輸，依次把 15 個呼叫之一改為「成功收到零／第一階段逾時／第二階段逾時」，三種來源產生相同 frame 與 queue 內容，但存取紀錄不同。caller 沒有使用另一個成功旗標去區分這三種零值：

- 前兩次準備傳輸的返回值被捨棄；在後續合成輸入不變的條件下，任一準備傳輸逾時仍繼續取樣。
- 第 5 筆 frame byte 成為零時，長度檢查拒絕三種來源，沒有進 queue。
- 第 2 筆標頭成為零且其他有效時，仍可到 provider 入口；本測試 ID 從 325 改為 320。
- payload 某 byte 成為零時，guard 仍可通過，provider 的來源 frame 含該零值。未執行 provider，因此不宣稱複製成功。
- 全部 15 次都返回零時，三條路徑都得到全零 frame 並被拒絕；其 DATA 存取紀錄分別不同。

上面是指定獨立狀態序列下的條件性結果。真實外設可能在準備傳輸失敗後改變後續輸入，不能據此聲稱實機可重現相同序列或輸入資料遺失。

## 重現與檢查

```powershell
python analysis/test_v4160_transfer_receive_chain.py
python -O analysis/test_v4160_transfer_receive_chain.py
python analysis/test_v4160_receive_frame_cpu.py
```

只需 Python 標準庫、原 BIN 與已發布的 queue／guard／capture 測試。原 capture 腳本僅把既有合成返回處理抽成 `transfer()` 方法供覆寫；它原有 3,328 組 byte 與 15 組參數測試仍通過。

新測試一般與 `-O` 結果：

```text
PASS: 510 readiness-position chain cases; 45 zero/timeout substitutions; 3 all-zero paths; 8 lengths; full queue; 3 instruction mutations detected
```

510 個串接案例覆蓋兩階段各 1–255 的首次 ready 位置，每例把變動位置分配給 15 個呼叫之一；沒有枚舉每個呼叫的所有狀態交叉組合。另有逐呼叫的 45 組零值／逾時替換、3 組全零路徑、1–8 各長度（該長度傳輸的兩階段均第 255 次 ready）及滿 queue 返回案例。

每例比對返回值、兩階段取樣數、DATA 寫入低 16 位與讀取次數、15 次呼叫參數、13 個 frame byte store、caller 的合成 MMIO 寫入順序、guard 路由、queue 全部 bytes、provider 參數與來源 bytes。被拒絕或 queue 滿時也確認完整返回的 RA/SP 與 S0/S1/S2 恢復。

三個記憶體複本負向對照分別改錯第一 readiness mask、第二 readiness mask，以及把第一等待次數從 255 減為 254；必須被傳輸紀錄檢查抓出。原 BIN 沒有變動。

## 剩餘範圍

這是有限 RV32 指令切片解譯，遇到未知指令／地址即失敗，不是完整晶片模擬。沒有外設行為、中斷或真實輸入證據；未知 `[0x4004c]` provider 仍未執行。本批增加了傳輸至 queue 的原指令驗證，沒有新增 C/C++ 重建 bytes 或重算整體覆蓋率。後續仍可離線追查該 provider 的靜態來源與已知呼叫合約。
