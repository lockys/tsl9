# Selector state transitions

[繁體中文](README.md) · [C/C++ source](../../src/native/receive/selector_transitions.c) · [Instruction contracts](provider-contracts.json) · [Verification summary](summary.json)

Reconstruct three complete functions at AB08,AB7C,ECA8:246B/94 instructions and31 private regions. Adjacent getters already exist and are not counted again.

AB08 preserves state equality,one-shot markers and action/timer ordering;the zero path passes1000 with unknown units. AB7C compares the new value with the byte at0x2000BEE8,selects action150/151 on decrease/increase when permitted,stores the low8 bits and returns a changed flag. ECA8 accepts only two specified values;its guard decides state storage and action dispatch. The write occurs before the action call. A nonzero guard with a changed state returns the saved guard value without normalizing it to bool.

232 comparisons/464 objects pass;53,766 original-coordinate bytes match,70.01% coverage. Three existing imports resolve with no new dependencies,leaving102 providers. The1AB48 table and other opaque data remain unprovided.

Confirmed:bytes,comparison/store widths and call order. Inferred:selector state handling. Unknown:vehicle feature names,units/ranges,private ABI,physical ROM/RAM,IRQ and OTA compatibility. No target/hardware execution or new BIN. Byte coverage is not feature completion or flash readiness. Offline transition tracing is only a proposed feature,not implemented vehicle control or App behavior.
