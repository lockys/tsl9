# 條件式 CCC 清除與查表的分段組合

`counter-ccc-lookup-composition.py` 將既有 `counter-reference-ccc-alias.py` 的參考候選清除投影，與 `counter-index-envelope.py` 對原 APP 查表指令的解碼結果串接。兩者在邊界重建記憶體，並非連續 CPU 執行。256 個合成容量結果：

- 容量 0–12：counter 初值 1 未被清除，查表位址為 `0x1ab4a`，屬已核對資料。
- 容量 13–255：counter 寫為 255，查表位址為 `0x1ad46`，超出提供的 APP 映像範圍 `[0x8000,0x1ac00)`。

**重要限制：**候選 V1.31 中已辨識的初始化會把容量設為設定 byte `& 3`，因此若該值保持到清除時，容量最多為 3，上述需要容量至少 13 的反例不會發生。`counter-ccc-initialized-bound.py` 對全部 256 個設定 byte 檢查此條件；現有 `experiments/tsl9-resident-CCC-capacity-initialization/verify-v1.py` 記錄初始化與 APP 呼叫順序的靜態證據。名目設定 `0x0e` 對應容量 2，但並未證實實機值或排除其他寫入。

結論須同時假設候選 ROM 實際安裝、Xwchc 解讀正確、GP 和容量符合投影、清除完成、之後真的執行該查表，且中間沒有重寫 counter。以上均未證實；超出提供映像也不等於實體記憶體一定無效或發生 fault。缺少本機參考 carrier 時明確非零 SKIP。
