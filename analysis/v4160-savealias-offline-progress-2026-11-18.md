# v4.1.60 offline SAVEALIAS progress

A bounded synthetic composition of the record dispatcher and peripheral writer was examined for a deliberately chosen stack alias. With post-prologue SP 0x40006558, bank-0 writer words coincide with saved s0 and ra. In the model, ordered writes change the restored values to 0x46800001 and 0x55667786 respectively. The event ledger contains 41 reads and writes; a separate synthetic byte-memory replay checks their internal consistency.

Static rasm2 checks cover 29 selected original instructions, not the entire path. The provider's normal return, no memory events, and preservation of required registers are assumed; status and memory are synthetic. The analyses are not an independent CPU execution, a reachability proof, device evidence, or a flashable reconstruction. Review found and corrected an ordering error in the initial summary and clarified the limits of the ledger and provider assumptions.

Local experiments and their dependencies have not been published in this report. No firmware is included.