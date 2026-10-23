# Feature candidates: offline diagnostics and rejection reasons
[繁體中文](feature-candidates.md)

Confirmed:821E returns0 for pointer+4 bit3, unsigned index>2, or state byte>=3.12A08 also has status/ID/tag paths. Static18CA4 returns4 without its writes when none of three banks qualifies. Evidence:`next-821e-contract.json`,`root-native-review.json`,`next-peripheral-contract.json`. These values do not establish DND, seat failure or CAN congestion.

Useful additions: an offline report of original branch conditions, unresolved providers and written-page hashes. Only after proving owned RAM, IRQ concurrency, resident ABI and BLE response format should read-only version/rejection/diagnostic-counter queries on the original hardware be considered.

No new hardware feature is implemented here. No vehicle controls, automatic retries, Flash operations or unknown memory writes are added. Reconstruct18CA4 and its provider boundaries first; diagnostics must not alter the original guards or OTA compatibility.
