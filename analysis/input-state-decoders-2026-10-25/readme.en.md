# Input and state decoders

[繁體中文](README.md) · [Source](../../src/native/receive/input_state_decoders.c) · [Contracts](provider-contracts.json) · [Summary](summary.json)

Reconstruct16 complete functions:1,822B/594 instructions,including long-frame inputs,two format wrappers,selector groups,gated record edits,callbacks,four-state predicate and mode20..23 stores. A2EA is a4B wrapper tail-jumping to retained A204 without duplicating its body.

D76C reads four static bytes in order and tests all for2. Four nearby entries write20/21/22/23 to one static byte. C472 passes three2-bit groups from record[8] to ECA8 with selector pairs120/121,128/129,136/137 and GP+216/217/218. Vehicle names and units remain unknown.

230 comparisons/460 objects pass;53,520 original-coordinate bytes match,69.69% coverage. Eight imports resolve;three functions and one data dependency are exposed,leaving105 providers. Seven callback references bind to real code.1AB48 remains an address-only dependency:its payload and standalone payload hash are neither exported nor counted as reconstructed data.

Confirmed:bytes,bit groups,static addresses,branch order and callback roles. Inferred:input gating and state dispatch. Unknown:vehicle feature attribution,units/bounds,table extent,physical ROM/RAM,private ABI,IRQ and OTA. No target/hardware execution or new BIN. Byte coverage is not feature completion or flash readiness.
