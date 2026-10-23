# 內建 CAN 濾波器路徑

[English](readme.en.md)

本實驗將128FE資料整理與18BA2濾波器寫入重建為同一份 C11／C++17 原始碼。兩段共418B／139指令，在原位址連結後與官方BIN逐位元組相同；176B frame、14-bank迴圈、描述結構與cold blocks均納入。

這是靜態程式證據，不能證明實體MCU、installed ROM、記憶體保存或OTA相容。兩個resident呼叫仍不透明，未假設一般C ABI。

最新整合與重現入口見[通道及兩後端驗證](../tsl9-channel-route/README.md)。原始listing與編譯產物保留本機；公開收據副本見[本輪證據](../../analysis/channel-filter-2026-10-23/README.md)。

v1 source／metadata與失敗試驗均保留；metadata-correction.json說明旗標清單序列化的更正，不代表重做或改寫舊編譯結果。
