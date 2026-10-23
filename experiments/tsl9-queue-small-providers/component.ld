/* Nonphysical static component; never a firmware placement declaration. */
ENTRY(tsl9_queue_status_81aa)
SECTIONS
{
    . = 0;
    .text : {
        *(.text.tsl9_queue_status_81aa)
        *(.text.tsl9_queue_clear_820c)
    }
}
