#ifndef TSL9_RUNTIME_MEMORY_LAYOUT_H
#define TSL9_RUNTIME_MEMORY_LAYOUT_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Offline recognizer for the two observed reset instruction shapes.
 * It decodes operands only; never executes/emulates code, reads target RAM,
 * or asserts physical RAM/ROM, completed initialization, ABI or OTA readiness.
 * No linker symbols or memory allocations are generated. */
typedef struct {
 uint32_t reset, gp, sp, data_load, data_start, data_end;
 uint32_t bss_start, bss_end, vector, mtvec_value;
 uint32_t clock_entry, runtime_entry, rom_entry;
 uint32_t data_bytes, bss_bytes, numeric_gap_to_sp;
} rml_layout;
typedef enum {RML_OK=0,RML_BAD_ARGUMENT=1,RML_BAD_PATTERN=2,
 RML_BAD_LAYOUT=3,RML_OUTSIDE_IMAGE=4} rml_status;
typedef enum {RML_RANGE_OUTSIDE=0,RML_RANGE_DATA=1,RML_RANGE_BSS=2,
 RML_RANGE_CROSSES=3,RML_RANGE_EMPTY=4,RML_RANGE_WRAP=5} rml_range;
/* Exactly148 bytes; image extents describe the supplied fixed file.
 * Output is zeroed on failure when non-null. */
rml_status rml_decode_reset(const unsigned char *,size_t,uint32_t,
 uint32_t,uint32_t,rml_layout *);
/* The one-past endpoint must fit uint32_t. Even [UINT32_MAX,2^32)
 * is conservatively RML_RANGE_WRAP; this is a metadata range policy. */
rml_range rml_classify_range(const rml_layout *,uint32_t,uint32_t);
/* Observed code metadata only. bytes describes an observed access/window,
 * never an allocation size. Address-only witnesses have bytes=0. A pointer
 * load requires a provider even when the reset copy/zero loop covers it.
 * GP addition uses RV32 modulo arithmetic and separately reports wrapping.
 * RML_OK means internally consistent metadata; it proves no physical memory,
 * payload, callable pointer, ABI, execution, linker placement or OTA outcome.
 * Requires the same memory-shape invariants as a decoded rml_layout.
 * The report is zeroed on failure when non-null. */
typedef enum {RML_WITNESS_ADDRESS=0,RML_WITNESS_READ=1,
 RML_WITNESS_WRITE=2,RML_WITNESS_POINTER_LOAD=3,
 RML_WITNESS_SPAN=4} rml_witness_use;
typedef struct {
 uint32_t address,bytes;
 int32_t gp_offset;
 unsigned gp_relative;
 rml_witness_use use;
} rml_witness;
typedef struct {
 uint32_t address,bytes;
 rml_range point_region,window_region;
 unsigned gp_wrapped,pointer_provider_required;
 unsigned reset_copy_covers_window,reset_zero_covers_window;
} rml_witness_report;
rml_status rml_observe_witness(const rml_layout *,const rml_witness *,
 rml_witness_report *);
#ifdef __cplusplus
}
#endif
#endif
