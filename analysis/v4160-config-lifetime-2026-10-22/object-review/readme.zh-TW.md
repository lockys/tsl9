# 真正宣告的回覆物件

[English](readme.en.md)

最終候選實測550B／186指令，48B frame、八個保存槽RA/S0..S6。它使用標準C11 `_Alignas(4)`／C++ `alignas(4)` 宣告未初始化的`volatile uint8_t response[4]`，不是強制指向saved area或spill bytes。

實際IR唯一allocation為`[4 x i8], align 4`，lifetime start/end均4B。物件起點轉為opaque呼叫的數值指標；本地只有byte0與byte1的volatile store，沒有上半兩byte初始化或word store。實際機器碼是SB於SP+12/+13（另有失敗路徑重寫SP+12），物件指標為SP+12。整個4B範圍SP12..15皆在48B frame內，不與任何保存、恢復或其他SPword讀寫相交；最低保存是S6@16。

因此，在共同入口SP為E的前提下，實際回覆地址E−48+12＝E−36與原始handler一致，且兩byte有真實獨立儲存。原七個保存位置也保持相同entry-relative地址。這是物件與位址投影的通過，不是完整ABI准入。

packet共用label有兩條路：S回覆以物件起點配長度2，E空回覆以null配長度0。檢查器逐一對應pointer/length phi的同一predecessor，沒有把4B backing大小當作傳輸長度，也沒有聲稱所有packet呼叫都是2B。未知allocator/callback仍可能看其他暫存器或超過宣告長度的記憶體；實機讀取範圍未證明。

相對先前556B來源，差異只有range guard之後的flash-base unsigned identity，以及native-only 4B/aligned宣告。HOST是同值uint32操作；標頭、演算法其他部分、provider效果順序、全部8-register read/write opaque橋及memory clobber保持。沒有重跑未改的HOST或舊baseline編譯；兩個codegen profiles已結束，未產新link/BIN。

第一個552B／186指令profile已減成八個保存槽，但2B物件在SP14/15，仍未匹配E−36；其來源快照只作歷史負結果。第二個真4B物件profile才取得SP12及完整不重疊範圍，不能只從「八個保存槽」推定成功。

四個有界反例拒絕：IR allocation縮成2B、packet長度改4、宣稱8B backing卻讓後半與保存槽相交，以及實際ELF的S6恢復槽改錯。前三項是實際IR文字變異／span檢查，最後一項為實際ELF欄位變異；沒有執行CPU或ISA模型。

```sh
python -B object-review/check.py --project-root ROOT
python -B object-review/review.py --project-root ROOT --folder MODE --firmware FW --receipt NEW.json --controls
python -B object-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

預設只讀封存metadata及精確source delta，不讀FW/generated物件。Actual模式要求明確folder/FW，收據create-only且不能寫入producer folder；replay唯讀，不重建反例。封存只含來源與metadata，build/內物件不交付。

額外S6保存及保存次序仍與原始程式不同；physical callee/S/GP/SP/RA、IRQ/fault/非同步、unknown callback、Flash/NV/BOOT與OTA限制均未關閉。回覆指標相同不能取代這些證據；新550B尚未整合進既有來源接線實驗BIN。
