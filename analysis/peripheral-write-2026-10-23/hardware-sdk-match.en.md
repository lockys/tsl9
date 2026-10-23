# Static CAN SDK correspondence
[繁體中文](hardware-sdk-match.md) · [Hashes and source lines](hardware-sdk-match.json)

Reads three previously cached CH32V20x SDK header/CAN sources and verifies their hashes offline. No new download or SDK execution.

| Original BIN observation | Cached SDK correspondence |
| --- | --- |
| Caller base40006400; status+8; bits26/27/28 | CAN1_BASE; CAN_TypeDef.TSTATR; TME0/1/2 |
| Mailboxes at+384, stride16, three banks | Eight words plus88 reserved words; sTxMailBox[3], four words each |
| +384/388/392/396 | TXMIR/TXMDTR/TXMDLR/TXMDHR |
| Record words0/4, bytes8/9/10, payload11..18 | CanTxMsg.StdId/ExtId/IDE/RTR/DLC/Data[8] |
| ID shifts21/3, full IDE/RTR bytes, DLC&15, two payload words, finalOR1, no-selection4 | CAN_Transmit, cached source lines399..451 |

This strongly corresponds to a CAN_Transmit/bxCAN-style SDK routine and supports the CH32V20x family candidate. Shared peripheral layouts do not uniquely identify the TSL9 part, package, pins or transceivers. High-level SDK C expressions do not establish the original BIN's access evaluation order; reconstruction follows all72 original instructions.

No physical CAN transmission was observed. The16B7C tag1/2 path remains to reconstruct; it does not yet establish a count of physical external CAN controllers.
