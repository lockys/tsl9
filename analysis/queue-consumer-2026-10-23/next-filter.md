# 下一段：封裝／轉送 filter

[English](next-filter.en.md) · [原始逐指令證據](next-filter.json)

`[0x82D2,0x838E)` 是consumer在 `12CB0` 呼叫的完整局部範圍：188B／69指令，SHA256 `7a49eb89a2c698b0a9d4a97083329c2a12e200c1f27fbdadec16784a6edb0e30`。RET在8388；cold block838A..838E仍可到達，不能截掉。

64B frame保存S0..S9／RA，PC衍生table初值`2000C794`；初始index0，cold path再設1，stride4。檢查`LHU[entry+2] != FFFE`、`LBU[entry+5] == 2`及`LBU[entry+4] != 0`。832C先更新S4，832E才拒絕長度>8，因此非零回傳不等於已成功轉送。

8356的C.JALR以A5為target，RA8358；8368是**2-byte C.JAL** 到8A56、RA836A。下一份decoder／relocation檢查必須區分它與無link的C.J。resident與8A56可能改變S-register／SP或alias；後續fresh讀取不能換成先前C值。本次尚未將188B重建成C。

另一個direct target14D2E只核對初始256B。它有七項jump table與跳出範圍的case，完整邊界未知，不能在14DA8的RET處截斷。現有V4.1.60證據不足以把它命名為座椅或免打擾。
