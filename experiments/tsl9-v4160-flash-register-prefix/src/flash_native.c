#include "flash_native.h"
#include "native_io.h"

/* Every site belongs to ID2966 SHA0ee64183..., not the older Runtime. */
#if !defined(FN_ONLY) || FN_ONLY==0x18e90
fn_word tsl9_flash_status_18e90(FN_CONTEXT fn_word status)
{
    fn_word base=FN_BASE5();
    FN_WRITE(0x18e94u,FN_ADD(base,FN_K(12u)),status);
    return FN_RET_STATUS(status,base);
}
#endif
#if !defined(FN_ONLY) || FN_ONLY==0x18e98
fn_word tsl9_flash_unlock_18e98(FN_CONTEXT fn_word incoming_a0)
{
    fn_word key1=FN_KEY1_HIGH(),key2,base=FN_BASE5();
    key1=FN_REG3(FN_ADD(key1,FN_K(0x123u)));
    key2=FN_KEY2_HIGH();
    FN_WRITE(0x18ea8u,FN_ADD(base,FN_K(4u)),key1);
    key2=FN_REG4(key2);
    key2=FN_REG4(FN_ADD(key2,FN_K(0xfffff9abu)));
    FN_WRITE(0x18eaeu,FN_ADD(base,FN_K(4u)),key2);
    FN_WRITE(0x18eb0u,FN_ADD(base,FN_K(36u)),key1);
    FN_WRITE(0x18eb2u,FN_ADD(base,FN_K(36u)),key2);
    return FN_RET_UNLOCK(incoming_a0,key1,key2,base);
}
#endif
#if !defined(FN_ONLY) || FN_ONLY==0x18eb6
fn_word tsl9_flash_lock_18eb6(FN_CONTEXT fn_word incoming_a0)
{
    fn_word base=FN_BASE4(),before,after,mask;
    FN_READ(0x18ebau,FN_ADD(base,FN_K(16u)),before);
    mask=FN_MASK3(0x8000u);
    after=FN_OR(before,mask);
    FN_WRITE(0x18ec0u,FN_ADD(base,FN_K(16u)),after);
    return FN_RET_UNLOCK(incoming_a0,mask,base,after);
}
#endif
#if !defined(FN_ONLY) || FN_ONLY==0x18ec4
fn_word tsl9_flash_erase_18ec4(FN_CONTEXT fn_word destination)
{
    fn_word base=FN_BASE5(),before,after,status,mask;
    FN_READ(0x18ec8u,FN_ADD(base,FN_K(16u)),before);
    before=FN_REG4(before);
    mask=FN_MASK3(0x20000u);
    destination=FN_ALIGN0(destination);
    after=FN_REG4(FN_OR(before,mask));
    FN_WRITE(0x18ed4u,FN_ADD(base,FN_K(16u)),after);
    FN_WRITE(0x18ed6u,FN_ADD(base,FN_K(20u)),destination);
    FN_READ(0x18ed8u,FN_ADD(base,FN_K(16u)),before);
    before=FN_REG4(before);
    after=FN_REG4(FN_OR(before,FN_K(64u)));
    FN_WRITE(0x18edeu,FN_ADD(base,FN_K(16u)),after);
    { FN_POLL_BEGIN;
      do { FN_POLL_STEP(0x18ee0u,1u);FN_READ(0x18ee0u,FN_ADD(base,FN_K(12u)),status);status=FN_REG4(FN_AND(status,FN_K(1u))); }
      while(FN_POLL_TRUE(0x18ee4u,status,1u));
      FN_CHECK_FLOW(); }
    FN_READ(0x18ee6u,FN_ADD(base,FN_K(16u)),before);
    mask=FN_MASK3(0xfffdffffu);
    after=FN_AND(before,mask);
    FN_WRITE(0x18eeeu,FN_ADD(base,FN_K(16u)),after);
    return FN_RET_ERASE(destination,mask,after,base);
}
#endif
#if !defined(FN_ONLY) || FN_ONLY==0x18ef2
fn_word tsl9_flash_program_18ef2(FN_CONTEXT fn_word destination,fn_word source)
{
    fn_word base=FN_BASE4(),before,after,status,last_word,mask,count;
    uint32_t offset;
    FN_READ(0x18ef6u,FN_ADD(base,FN_K(16u)),before);
    before=FN_REG5(before);
    mask=FN_MASK3(0x10000u);
    destination=FN_ALIGN0(destination);
    after=FN_REG5(FN_OR(before,mask));
    FN_WRITE(0x18f00u,FN_ADD(base,FN_K(16u)),after);
    { FN_POLL_BEGIN;
      do { FN_POLL_STEP(0x18f02u,1u);FN_READ(0x18f02u,FN_ADD(base,FN_K(12u)),status);status=FN_POLL5_AND(status,1u); }
      while(FN_POLL_TRUE(0x18f06u,status,1u));FN_CHECK_FLOW(); }
    base=FN_BASE4();
    { FN_POLL_BEGIN;
      do { FN_POLL_STEP(0x18f0cu,2u);FN_READ(0x18f0cu,FN_ADD(base,FN_K(12u)),status);status=FN_POLL5_AND(status,2u); }
      while(FN_POLL_TRUE(0x18f10u,status,2u));FN_CHECK_FLOW(); }
    base=FN_BASE4();
    count=FN_COUNT();offset=FN_OFFSET_VALUE(status);
    do {
        FN_READ(0x18f1eu,FN_SOURCE_ADDRESS(source,offset),last_word);
        FN_WRITE(0x18f26u,FN_DEST_ADDRESS(destination,offset),last_word);
        FN_WORD_DONE();
        { FN_POLL_BEGIN;
          do { FN_POLL_STEP(0x18f2au,2u);FN_READ(0x18f2au,FN_ADD(base,FN_K(12u)),status);status=FN_AND(status,FN_K(2u)); }
          while(FN_POLL_TRUE(0x18f2eu,status,2u));FN_CHECK_FLOW(); }
        offset+=4u;
    } while(offset!=FN_COUNT_VALUE(count));
    FN_READ(0x18f36u,FN_ADD(base,FN_K(16u)),before);
    before=FN_REG5(before);
    mask=FN_MASK3(0x200000u);
    after=FN_REG5(FN_OR(before,mask));
    FN_WRITE(0x18f3eu,FN_ADD(base,FN_K(16u)),after);
    base=FN_BASE5();
    { FN_POLL_BEGIN;
      do { FN_POLL_STEP(0x18f44u,1u);FN_READ(0x18f44u,FN_ADD(base,FN_K(12u)),status);status=FN_REG4(FN_AND(status,FN_K(1u))); }
      while(FN_POLL_TRUE(0x18f48u,status,1u));FN_CHECK_FLOW(); }
    FN_READ(0x18f4au,FN_ADD(base,FN_K(16u)),before);
    mask=FN_MASK3(0xfffeffffu);
    after=FN_AND(before,mask);
    FN_WRITE(0x18f52u,FN_ADD(base,FN_K(16u)),after);
    return FN_RET_PROGRAM(destination,source,count,mask,after,base,last_word);
}
#endif
#if !defined(FN_ONLY) || FN_ONLY==0x9c0a
fn_word tsl9_flash_quarter_9c0a(FN_CONTEXT fn_word destination,fn_word source)
{
    fn_word result;
    FN_FRAME_BEGIN(destination,source);
    destination=FN_DESTINATION(destination);
    FN_CSR_DECLARE;
    FN_CSR_CLEAR();
    result=FN_CALL_UNLOCK(destination);FN_CHECK_FLOW();
    result=FN_CALL_STATUS(FN_K(49u));FN_CHECK_FLOW();
    result=FN_CALL_ERASE(destination);FN_CHECK_FLOW();
    FN_FRAME_RELOAD(source);
    result=FN_CALL_PROGRAM(destination,source);FN_CHECK_FLOW();
    result=FN_CALL_LOCK(result);FN_CHECK_FLOW();
    FN_CSR_SET();
    FN_FRAME_END(result);
}
#endif
