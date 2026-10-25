# State,action and scheduling support

[繁體中文](README.md) · [Source](../../src/native/receive/state_action_support.c) · [Contracts](provider-contracts.json) · [Summary](summary.json)

Reconstruct15 complete functions:562B/199 instructions,covering scheduling/cancellation,state access,conditional action and pending-flag cleanup. Five callback addresses bind to four real bodies,including retained A3CC and self-rescheduling1016E.

1016E queries B6A8 first:a nonzero result reschedules itself with A2=100;otherwise it clears GP+304/305/306/307 in order before calling BD6E/CC8C/F688/F6BA. Other scheduler arguments include5000 and1000;time units remain unknown. FDA6 retains original GP+289 states0/1/2,guards and unresolved query/consumer ports.

226 comparisons/452 objects pass;50,958 original-coordinate bytes match,66.35% byte coverage. Eleven imports resolve without new dependencies;115 remain. All seven existing guarded tables are rechecked.

Confirmed:bytes,flag order,masks,static addresses and callback references. Inferred:state cleanup and conditional action support. Unknown:seat/button meanings,time units,physical ROM/RAM,private ABI,IRQ and OTA. No target/hardware execution or new BIN. Byte coverage is not feature completion or flash readiness.
