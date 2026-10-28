# 原 APP 剩餘資料存取查核

[English](readme.en.md)

新增離線查核器，區分 **「基址已有資料 owner」與「完整存取範圍已有來源」**。原 C/C++、連結布局與覆蓋率均未修改；沒有新增 BIN。

原生 C/C++ 診斷覆蓋 73,374／76,800 bytes（**95.54%**）。未覆蓋的 3,426 bytes 中，3,128 bytes 屬既有排除範圍，其餘 298 bytes 尚未覆蓋；後者不等於應直接填入的 padding 或資料。

`1A078` 的 source symbol 仍是六個 compiler imports 之一。其基址位於實際 readonly owner `19ED8..1A088`（432 bytes）的 offset 416，從該處起只有 **16 bytes** 屬於這個 owner。

完整消費函式 `CEDC..CF96` 的原指令與 C/C++ 原位址產物一致。普通入口的資料流顯示，模式來源為 byte load 或零，nibble 經 `&15`；讀取式為：

```text
1A078 + 16*mode + nibble
```

若僅採用 byte／nibble 的保守範圍，存取 envelope 是 **`1A078..1B078`／4,096 bytes**，其中 1,144 bytes 超出提供的 APP 映像，且範圍會與既有排除資料交集。**這不是原始陣列宣告大小，也不表示全部索引可達，更不是已確認韌體缺陷。** 仍需證明更窄的全域模式不變條件、所有入口與實際 backing。

因此沒有僅依基址覆蓋就新增 alias、宣稱 provider 完整或擷取整個保守範圍；六個 imports 保留。查核器只輸出位址、數量與前提，不輸出排除 payload 或其個別雜湊。

[缺口圖](gaps-v1.json) · [存取契約與收據](verification-v1.json) · [查核器](verify-v1.py) · [輸入索引](inputs-v1.json) · [摘要](summary.json)

需要保留的參考檔、原生物件與已核對 LLVM。在專案根目錄執行唯讀查核：

```sh
python3 experiments/tsl9-APP-residual-access-audit/verify-v1.py --tool-dir "$LLVM_BIN"
```

Windows 可使用 `py -3`。來源查核涵蓋 159 個 C/H、266 次比較及 532 個既有物件；不執行目標、模型、模擬器、硬體或網路操作。**查核通過只證明上述證據與缺口一致，不代表實機或 OTA 相容性通過。**
