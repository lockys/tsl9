# CH32V208候選BIN建置範圍

使用者本次明確指示：「那先用最強候選產bin」。因此本輪可以在**CH32V208／D8W為候選平台**的明示假設下產生實驗BIN；原機已證明相容的完整目標仍未達成，不以此修改舊R81嚴格稽核或宣稱可安全燒錄。

只做本機靜態編譯／連結／objcopy／檔案與整數比對。來源為指定目錄 `C:/Users/locky/Documents/projects/re-tsl9` 現有C/C++和已保留本機原始TSL9 Runtime。沒有API、網路、識別資料外傳、目標執行／模擬或BLE/CAN/UART/SPI/Flash操作。

候選設計可使用**已從原指令觀察的數值地址**進行final placement／address-only external bindings，例如ROM entry 0x40000與0x19D10資料地址；它們必須在新候選manifest明列為assumed resident/external addresses，不能冒稱已取得ROM body、已證ABI或已補齊4096B資料域。保留原R81 strict failure與所有舊收據不變。

不得建立dummy函式／假ROM內容、忽略任意未解決符號、或用猜測補零／填FF來掩蓋來源缺失。候選映像只可包含可追到現有C/C++編譯section或原始載體已知bytes的區段。若必須保留尚未語意重建的原始片段，須以獨立C/C++ carrier section與逐區段來源／雜湊標明，不能把它們算成已恢復高層C/C++功能；不能只是將原BIN更名交付。

來源Runtime為76800B、SHA256 `32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc`，採用模型base0x8000；BOOT／ROOT／resident ROM不在此次候選Runtime輸出內。不能新增來源外的272B、任意借用其他型號或自行改驗證／功能行為。

先做完整section原VA/LMA coverage與嚴格final-link可行性檢查，再建置。實際產出須是由C與C++路徑編譯／連結／objcopy得到的binary，附ELF、map、編譯／連結／objcopy紀錄、原始片段比例、候選bindings與未驗條件，並獨立核對。若不能產生有實質重建內容的候選BIN，回報確切工具錯誤，不用空檔、fixture或改名的原始BIN充數。

持續交付目錄為指定re-tsl9；新來源與建置工具放獨立candidate experiment，產物放明示candidate輸出目錄。原480檔／292inputs的產品與舊封存不覆寫。本輪允許候選artifact，不等於原硬體或OTA驗收通過；`target_ready=false`、`ota_verified=false`、`goal_complete=false`始終保留。
