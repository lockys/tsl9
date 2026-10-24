/* Actual82A8 provider regions;all four roots retained forimplicit adjacency. */
SECTIONS {
 .state_read_code 0 : SUBALIGN(1) {
  *(.text.tsl9_feature_external_82a8)
  *(.text.tsl9_state_82c6)
  *(.text.tsl9_state_82ca)
  *(.text.tsl9_state_82cc)
 }
}
