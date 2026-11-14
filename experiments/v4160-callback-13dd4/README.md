# 0x13dd4 callback 的受限靜態控制流

`verify.py` 固定原始 BIN 雜湊與 `[0x13dd4,0x13e0e)` 的 58 bytes，解碼三個 JAL、條件分支與尾呼叫目標，並測試 JAL 位移變造。依原始指令，wrapper 先保存返回位址，再依序呼叫 `0x90b0(0x13dd4)`、`0x13d48(0)`、`0x81aa()`；最後結果非零則恢復堆疊返回，為零則恢復堆疊並尾跳至 `0x9124(0x13f88, 0, 300, 0)`。

`wrapper.py` 對固定指令窗執行受限模擬，以回傳 stub 取代三個外部呼叫；3,072 個合成案例覆蓋所有 256 個 queue byte、不同返回值與堆疊位址，檢查呼叫順序、堆疊恢復與分支，並偵測三種指令變造。stub 僅提供設定的 `a0` 回傳值，不模擬被呼叫者記憶體副作用或任意暫存器破壞。

`model.c` 將 wrapper 的呼叫、回傳／尾跳與參數投影成可攜式 C；`differential.py` 以 C11、C++17 各 3,072 組案例比對原始指令模擬，並以分支反轉與延遲數值變造測試差分檢查。C 模型不執行真實呼叫或實體堆疊寫入。

這些步驟以各前置呼叫正常返回為條件；並未執行它們，也未證明 callback 表命中、排程、300 的單位、非同步副作用或實機行為。呼叫目標經位移解碼；其餘參數由固定指令窗靜態判讀，不是完整指令模擬。

```text
python -I -B experiments/v4160-callback-13dd4/verify.py
python -B experiments/v4160-callback-13dd4/wrapper.py
python -B experiments/v4160-callback-13dd4/differential.py --vcvars <vcvars64.bat>
```
