# 下一個缺口：接收佇列與 resident 間接呼叫

[English](ring-next.en.md)

已確認的靜態範圍是官方ID2966 `[0x12BC8,0x12C24)`，92B／32指令，SHA `d3d9af9bcec8af13dfd424d3bfb2bd79f8fc3fd61308cb6ec0d7c18b1b78b13b`。這是有界range證據，未證明全域入口／外部引用完整性。

- 16B frame，RA／S0／S1保存於SP+12／+8／+4。
- AUIPC原位計算RAM基底`0x2000C038`，掃描32個12B slots，以`LHU slot[0] == 0`選空位。
- 首個空位先`SH A0,0(S0)`、`SB A2,2(S0)`；新讀`LW[0x0004004C]`的32-bit function pointer。
- `0x12C0C`的`8297`是RV32C `JALR A5`，連結RA=`0x12C0E`。A0=slot+3，A1=原payload指標，A2=完整入口length。不可將r2 ESIL中的錯誤link描述當作ISA事實。
- 間接呼叫後，`0x12C0E`使用**當下**S0／S1做`SB S1,11(S0)`，再還原frame；不能先假設一般C callee-save。
- 滿表出口保留入口A0；成功出口保留resident返回的A0。resident看似複製資料是推論；APP檔中沒有證據證明其實際身分或保存契約。

下一步重建需保留原位AUIPC、A6零擴展、fresh pointer load、physical indirect call及返回後S0／S1。接上已驗證packet之前，須驗證這些ports與實際連結，而不是用`memcpy`替換。

可探索的新功能，尚未實作：

1. 接收佇列滿載／丟包計數：原範圍掃完32格便退出，沒有已確認的診斷回報；新增計數需先證明RAM ownership及安全唯讀輸出。
2. ID0佔用診斷：packet的11-bit ID算術允許0，而ring用16-bit ID0表示空位。這提示可能的零ID歧義；仍須核對consumer與實際上游輸入，不能直接宣稱發現實機丟包。新增獨立occupancy欄位會改變layout／consumer契約，現階段不修改。

所有結論僅來自靜態解碼與交叉核對，未執行目標、模擬ISA或操作車輛／硬體。
