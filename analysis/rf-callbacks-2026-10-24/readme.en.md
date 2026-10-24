# Corrected RF task and status callbacks

[繁體中文](README.md)

The new [C/C++ source](../../src/native/receive/rf_callbacks.c) covers **17476–1753A:196B,65 instructions,23 architectural regions**. Actual C11/C++17 objects preserve144 non-control bytes and16 typed references;data-only original-VA encoding matches all196B. [Receipt](evidence/standalone-trial.json)

## Address correction

Earlier manual addresses were16B early. Direct encoded AUIPC/ADDI decoding establishes task17476 andRF status174EE. [Correction record](literal-address-correction.json) / [Corrected instructions](corrected-frontier.json)

The original212B projection remains preserved. Its17466 start lies inside the4B LW at17464,causing two1B invalid decode rows;it doesnot prove invalid firmware instructions. Authored analysis/indexes were corrected without rewriting native parent objects ororiginal receipts.

## Static behavior

The task retains a16B frame,signed low16-bit event test,message receive/deallocate calls andshared restores. Eventbit1 uses fresh then-live S1+464/+460 withoriginal state buffer/length andA2/A3=255,then returns S0 XOR1. Eventbit2 calls173EE withA0=1 andreturns S0 XOR2;unselected events return0.

The frameless status callback retainsA0==2/A1 guards,three raw byte comparisons atA2+1/+2/+3,andoriginal17442/173EE tails. No checks were removed orbuffer accesses narrowed. Buffer bounds andinstalled callback ABI remain unproved. [Default SDK profile](rom-profile-correspondence.json) corresponds to message handling/RF_Shut/RF_Tx,not installed ROM orphysical TX success.

## Integration and limits

All196B are present as genuine native callback bodies. No fake alias orruntime literal-pointer binding is claimed. The component has **4030B code+456B data,340 nonzero FUNC regions,13 retained aliases,278 RELA and19 direct UND**. New173EE/17442 providers increase UND from17 to19;all3834B parent code,456B data and62 vector bindings remain intact. [Evidence](evidence/native-c.json) / [Provider ledger](pending-providers.json)

Selected sources contain92 C/H files:130 code comparisons/260 objects pluspointer-data2/4,total **132/264**. Parent SDK layout objects are reused;their[public receipt](evidence/rf-layout.json) only normalizes CRLF toLF while theoriginal remains local.

[Next173EE–17476 providers](next-rf-providers.json) cover136B/45 instructions. Passive RF-result diagnostics remain a future candidate requiring ABI/memory ownership evidence,not firmware functionality.

VMA-zero ET_REL doesnot prove original placement,installed ROM,memory,startup/IRQ,physical hardware orBLE OTA. No target/HOST-model/ISA/ESIL execution,hardware/network access,newBIN,commit orpush. [Build receipt](evidence/integration-build.json) / [Publication provenance](publication-provenance.json)
