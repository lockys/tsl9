# Notification 子函式候選：有界 wrapper 契約

[English](readme.en.md)

只分析已保存候選 V1.40 的0x45228與 V1.31 的0x45194。兩者都是 **54B／22指令** 的 wrapper，另有一個條件映射至 RAM0x200001E4 的 **56B／17指令** helper。未新增C/C++ ROM模型、下載、執行目標、模擬ISA、修改舊seal或產生BIN。候選不等於實機resident。

| 版本 | wrapper | builder pointer（LUI＋signed ADDI） | 未閉合tail |
| --- | --- | --- | --- |
| V1.40 | 0x45228..0x4525E | 0x44E44 | 0x44866 |
| V1.31 | 0x45194..0x451CA | 0x44DB0 | 0x447D2 |

## 真實本地算法與邊界

wrapper配置32B frame，保存S0@24與RA@28。A0原始值置於S0；以32-bit fresh load讀A1描述項+4，A3先保留描述項，A4預設0。若該pointer非空，先SW描述項到SP+12，再以(A0=pointer,A1=3)呼叫RAM0x200001E4；返回後 **fresh LW SP+12→A3**、A4=helper返回A0。不能在可變stack假設下把它換成不重讀的C local。

接著A0=liveS0，fresh恢復S0／RA，A1為表列builder pointer、A2=27，SP+=32，再以無link的JAL x0轉移tail。沒有自己的統一返回status；tail將承接已恢復的caller RA。未指定的其餘raw GPR不是本報告已證的全參數投影。

54B本體只有S0與RA的普通save/use/restore；不讀GP、S4、S7，也不把incoming RA當數值計算或比較。但RA被轉交未閉合tail，故**不能以本地未觀察推論transitive不觀察**。opaque call期間的S0/SP變化、ownstack alias與async條件均未消除。

## 56B helper：無子呼叫的指標範圍查找

條件startup映射：V1.40 flash0x40494、V1.31 flash0x40454→RAM0x200001E4。兩候選差別包含global list位置：V1.40讀0x200031E4與0x200031DC；V1.31讀0x20003194與0x2000318C。

helper保留original=A0，計算adjusted=u32(A0-A1)。從head開始，直到node等於sentinel；每輪讀next=READ32(node)，並以unsigned條件檢查original與adjusted是否都在[u32(node+8),next)。若是則返回adjusted；否則沿next繼續；碰到sentinel返回original。沒有寫memory、SP／GP／S使用或nested call，RA僅RET。不能憑此稱為通用allocator／length函式；循環list、壞指標或memory變化可使其不終止／fault，沒有杜撰iteration cap。

## tail frontier：故意不擴展

只保留tail前128B／54個指令分界。可見64B frame、多個新call及經S6的間接call；還有超出節錄的CFG邊。bounded reader將原始2C08保持unknown（r2顯示SP-relative ADDI），其他QK stack半字stores仍為明確的Xwchc條件解碼，未當NOP。**完整tail body／builder body／深層callee／notification結果未知。**

來源header的literal0x1B命名為ATT_HANDLE_VALUE_NOTI，描述項型別有pointer成員；只作候選命名旁證，不以SDK C型別取代實際raw args。修正紀錄：早期手算builder地址錯為451E4／451B0，raw LUI＋ADDI gate在任何seal前拒絕並改為44E44／44DB0。

## 可攜只讀檢查

```sh
python3 -B analysis/v4160-notification-callees-2026-10-22/candidate-review/review.py
python3 -B analysis/v4160-notification-callees-2026-10-22/candidate-review/review.py --candidate-root /existing/wch-resident-candidate-2026-10-21
```

工作區前綴是apk-analysis/tsl9-，P是analysis/。可選--project-root ROOT；Windows可用python -B。預設純metadata／238B每候選文字節錄重算，actual_candidate_bytes_read=false；明示candidate-root才讀固定pin的原HEX／segment／profile references、核對節錄，true。沒有複製整份vendor ROM進P，也沒有在checker呼叫r2或target。六個實際靜態r2 commands原始bytes view另存observations.json；不用其ESIL。八個raw field反例全部拒絕。完整ABI／installed identity／OTA皆false。
