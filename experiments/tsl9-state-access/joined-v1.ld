SECTIONS {
  .feature_graph : {
    KEEP(*(.feature_graph))
    KEEP(*(.text.tsl9_feature_external_82a8))
    KEEP(*(.text.tsl9_state_82c6))
    KEEP(*(.text.tsl9_state_82ca))
    KEEP(*(.text.tsl9_state_82cc))
    KEEP(*(.text.tsl9_callback_external_10032))
    KEEP(*(.text.tsl9_feature_external_10044))
    KEEP(*(.text.tsl9_state_10066))
    KEEP(*(.text.tsl9_state_1007c))
    KEEP(*(.text.tsl9_state_10088))
    KEEP(*(.text.tsl9_state_get_1008a))
    KEEP(*(.text.tsl9_feature_external_10096))
    KEEP(*(.text.tsl9_state_100ba))
    KEEP(*(.text.tsl9_state_100c6))
    KEEP(*(.text.tsl9_state_get_100c8))
    KEEP(*(.text.tsl9_feature_external_100d6))
    KEEP(*(.text.tsl9_state_100e8))
    KEEP(*(.text.tsl9_state_100f4))
    KEEP(*(.text.tsl9_state_get_100f6))
    KEEP(*(.text.tsl9_feature_external_10100))
    KEEP(*(.text.tsl9_state_10126))
    KEEP(*(.text.tsl9_state_1012e))
    KEEP(*(.text.tsl9_state_get_10130))
    KEEP(*(.text.tsl9_state_10140))
    KEEP(*(.text.tsl9_state_10154))
    tsl9_callback_external_9b36 = tsl9_queue_external_9b36;
  }
  .table_0 : { KEEP(*(.table_0)) }
  .table_1 : { KEEP(*(.table_1)) }
}
ASSERT(SIZEOF(.feature_graph) == 6038, "Exact parent plus state-access extent")
ASSERT(SIZEOF(.table_0) == 28, "Exact original outer relative table")
ASSERT(SIZEOF(.table_1) == 32, "Exact original nested relative table")
ASSERT(tsl9_callback_external_9b36 == tsl9_queue_external_9b36, "Alias binds actual existing original leaf")
