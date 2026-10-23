# 通道分流與濾波器設定

[English](readme.en.md)

本輪把 `0x12ABE` 通道分流、內建 CAN 濾波器設定及外部 SPI 控制器設定接成真實 C/C++ 物件圖。這是離線重建與靜態證據，尚未成功產出經原硬體驗證的重建韌體。

| 範圍 | 實際結果 |
| --- | --- |
| 五個新 src 單元 | 840B；原始實驗與選用副本的 C11/C++17 物件一致 |
| 共用四個既有單元 | 402B；SPI 傳輸、寫入、修改及暫存器讀寫 |
| 原位址連結 | 六段、1242B、445 指令、94 strong FUNC；全部程式位元組與官方 BIN 相同 |
| 接入既有接收／分派圖 | 3166B、1104 指令、191 FUNC、144 pending RELA；剩一個直接 UND：14D2E |
| 全部 src 整理檢查 | 71 個 C/H、45 個 native units；90 組比較、180 個物件；舊80組 facts 未變 |

`ORIGINAL-PC-COMPONENT-NOT-FIRMWARE.elf` 僅證明六段程式，不是韌體。其單一 RX LOAD 為68340B，其中67098B是未證明的間隙。`UNRESOLVED-CHANNEL-GRAPH.o` 是 VMA0 診斷物件，含尚未重定位的控制與原 PC 相依運算，不能執行或當 BIN 刷寫。94／191 個 FUNC 是機器架構區段，並非等量的一般 C ABI 函式。

## 已確認與推論

- 分流保留完整32-bit A0：零值尾跳128FE，非零尾跳16CC4並設定A3=0；沒有新增 RA 連結。
- 128FE 以176B frame 整理濾波資料，經兩次不透明 resident call 後設定14個濾波器。18BA2 的描述結構、暫存器位移與已保留的官方 WCH `CAN_FilterInit` 結構高度一致。這支持程式辨識，不能證明板上 MCU 型號。
- 16CC4 以低8位元的 `A0-1<=1` 判斷可接受通道，整理最多12B資料並寫入六組11-bit ID。SPI 指令02／03／05及暫存器配置支持 MCP2515／MCP25625 相容系列候選，未確認實體型號。
- resident call 後讀取的是當時的 SP／S-register／回傳暫存器；未假設原廠 ROM 遵守一般 C ABI。各例程的 A0 殘值不能直接當作成功狀態。
- 14D2E 的完整候選範圍為1912B／666指令，含兩組相對跳表與至少71個外部直接目標。剩一個 UND 只描述本元件的邊界，不代表全韌體只缺一個函式。詳見[分派證據](../../analysis/feature-dispatch-frontier-2026-10-23/README.md)。

## 重現與限制

在專案根目錄執行；LLVM_BIN 指向本機已存在、雜湊符合 spec 的工具目錄，這些指令不下載工具：

```sh
python3 scripts/verify-curated-source.py --replay build/curated-source/channel-filter-20261023-v1/verification.json
python3 experiments/tsl9-channel-route/build.py --tool-dir "$LLVM_BIN" --output experiments/tsl9-channel-route/build/your-new-trial
python3 experiments/tsl9-channel-route/verify-v2.py --tool-dir "$LLVM_BIN" --folder experiments/tsl9-channel-route/build/your-new-trial/c --mode c --write
python3 experiments/tsl9-channel-route/verify-v2.py --tool-dir "$LLVM_BIN" --folder experiments/tsl9-channel-route/build/your-new-trial/cpp --mode cpp --write
```

輸出目錄僅允許新建。驗證器檢查來源、編譯依賴、工具、IR、ELF ownership、原位址完整位元組、parent保存及負例。沒有執行 HOST 模型、ISA 模擬、硬體、網路 API 或 OTA。Windows 工具鏈已驗證；其他平台仍需相同檢查。

v1 驗證器與收據保留不改。獨立覆核發現其 full-graph resident transfer 數量少算兩處；v2及覆核文件更正此統計，不把歷史收據冒稱正確新版。原始收據／編譯產物留本機，公開路徑匿名化副本另列原始 SHA-256。

值得新增的功能是「離線濾波配置預覽」：將內建14-bank與外部六組ID表示為可比較資料，顯示截斷、通道與後端差異。目前只是候選，尚未實作；不會為此發送 CAN 或更改硬體。
