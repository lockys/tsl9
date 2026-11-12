# 0x9c0a 呼叫順序候選

唯一依據：相鄰 `v4160-9c0a-tail-callee-evidence/` 的靜態指令證據，尤其其正常返回條件與限制。這是條件式抽象，不是已還原的原始程式。`candidate.c` 不做實際 CSR、stack 或目標呼叫；呼叫者提供全部 callbacks 與共享 bus。`value` 是不透明的宿主值，並非聲稱目標資料型別或指標語意。

進入時先保存 entry a0 的值作為 s1 抽象，透過 write_slot 寫入 entry a1；read_slot 在第四個 callee 前實際重讀同一抽象 slot。bus 可表現與 entry a0 或其他位置的 alias，任何 callback 都可修改 bus 或 slot；保存的 s1 **值**不因此改變，所指內容則可能改變。此模型假定保存暫存器、frame 和返回控制完好。CSR callback 表示指令事件而非 CSR 效果，csrs 是設位操作，不是恢復先前值。

每個 callee callback 收到目前抽象 a0/a1/a2，正常返回時回傳三個新值；除了本函數明確設定者，後續參數取前一 callee 的回傳值，不能假設 a1/a2 保持 entry 值。五個 callee 的語意、存取及是否返回均未知。所有 callbacks 正常返回才到最後結果，其值為最後 callee 返回的 a0；若中途不返回或 fault，後續事件不保證發生。slot 與 CSR callbacks 代表抽象事件，不回傳暫存器，因此模型假定它們不改變抽象 a0/a1/a2；真實 CPU 上並不存在這些額外的 C 呼叫。C callback 介面要求每次取用的函數指標非空且型別相符，callbacks 物件、bus 與共享狀態在使用時有效，且不存在資料競爭或其他 C 未定義行為；對 fault、非返回、ABI、其他暫存器及保存區破壞不作實作或保證。

## 測試

```
python -B experiments/v4160-9c0a-call-sequence-candidate/test_model.py
python -B -O experiments/v4160-9c0a-call-sequence-candidate/test_model.py
```

Python reference model 用 token 表示未知 caller-saved 值，驗證事件順序、slot alias 改寫及每個 callee 以例外界定的非返回；另以 SHA-256 釘住 C source bytes。它不執行或測試 C，source pin 亦不證明 C 與 model 等價；不證明 ABI、實際 CSR、sp、硬體或 target 行為。沒有編譯、target 執行或模擬，也不使用網路、硬體或更改設定。
