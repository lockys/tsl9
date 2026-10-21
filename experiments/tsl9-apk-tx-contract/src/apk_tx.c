#include "apk_tx.h"
#include <string.h>

#define AT_JS_EXACT_MAX UINT64_C(9007199254740991)

at_status at_encode(uint8_t command,const uint8_t *payload,size_t length,
                    uint8_t *out,size_t capacity,size_t *written) {
    size_t i; uint8_t sum;
    if(!out||!written||(!payload&&length)||length>UINT32_MAX||length>SIZE_MAX-6)
        return AT_DOMAIN;
    if(capacity<length+6) return AT_CAPACITY;
    out[0]=0x55; out[1]=0x7f; out[2]=command;
    out[3]=(uint8_t)(length>>8); out[4]=(uint8_t)length;
    sum=(uint8_t)(command+out[3]+out[4]);
    for(i=0;i<length;i++) { out[5+i]=payload[i]; sum=(uint8_t)(sum+payload[i]); }
    out[5+length]=sum; *written=length+6; return AT_OK;
}

void at_transport_init(at_sender *s,const char *device) {
    s->transport.mtu=20; s->transport.device_id=device?device:"";
    s->transport.service_id=""; s->transport.characteristic_id="";
    s->transport.notify=0; s->transport.write_no_response=0;
}

void at_init(at_sender *s,uint8_t *storage,size_t capacity) {
    memset(s,0,sizeof *s); s->wire=storage; s->capacity=capacity;
    at_transport_init(s,NULL);
}

static int connection_truthy(const at_sender *s) {
    const at_transport *t=&s->transport;
    return t->notify&&t->device_id&&t->device_id[0]&&t->service_id&&
        t->service_id[0]&&t->characteristic_id&&t->characteristic_id[0];
}

static at_observation observe(const at_sender *s,at_kind kind,at_status status) {
    at_observation o; memset(&o,0,sizeof o); o.kind=kind; o.status=status;
    if(s) {
        o.index=s->index; o.retry_count=s->retry_count;
        if(kind==AT_WRITE) {
            o.device_id=s->transport.device_id;
            o.service_id=s->transport.service_id;
            o.characteristic_id=s->transport.characteristic_id;
            o.write_no_response=!!s->transport.write_no_response;
            if(s->index<s->chunks) {
                size_t offset=(size_t)s->index*s->stride;
                o.value_defined=1; o.value=s->wire+offset;
                o.length=s->wire_length-offset;
                if(o.length>s->stride) o.length=s->stride;
            }
            /* Fail branch intentionally emits undefined value beyond buf.length.
             * The original SDK's treatment of that argument stays unmodelled. */
        }
    }
    return o;
}

static at_observation callback_true(at_sender *s) {
    if(!connection_truthy(s)) return observe(s,AT_DISCONNECTED,AT_OK);
    s->retry_count=0;
    return observe(s,s->index<s->chunks?AT_WRITE:AT_IDLE,AT_OK);
}

at_observation at_begin(at_sender *s,uint8_t command,const uint8_t *payload,
                        size_t length) {
    size_t n; int32_t mtu; at_status status;
    if(!s) return observe(s,AT_BOUNDARY,AT_DOMAIN);
    if(s->stalled) return observe(s,AT_BOUNDARY,AT_NO_PROGRESS);
    status=at_encode(command,payload,length,s->wire,s->capacity,&n);
    if(status!=AT_OK) return observe(s,AT_BOUNDARY,status);
    mtu=s->transport.mtu; if(mtu>244) mtu=244;
    s->index=0; s->chunks=0; s->initialized=1; s->wire_length=n;
    s->stride=mtu>0?(size_t)mtu:0;
    /* Original splice(0,mtu<=0) cannot reduce c.length and never reaches
     * txCallback(true). Stop observing that non-progress loop; no fake write. */
    if(mtu<=0) { s->stalled=1; return observe(s,AT_BOUNDARY,AT_NO_PROGRESS); }
    s->chunks=n/s->stride+(n%s->stride!=0);
    return callback_true(s);
}

at_observation at_success(at_sender *s) {
    if(!s||!s->initialized) return observe(s,AT_BOUNDARY,AT_DOMAIN);
    if(s->stalled) return observe(s,AT_BOUNDARY,AT_NO_PROGRESS);
    if(s->index>=AT_JS_EXACT_MAX) return observe(s,AT_BOUNDARY,AT_DOMAIN);
    ++s->index; /* success closure precedes connIsOK() and retry reset. */
    return callback_true(s);
}

at_observation at_failure(at_sender *s) {
    if(!s||!s->initialized) return observe(s,AT_BOUNDARY,AT_DOMAIN);
    if(s->stalled) return observe(s,AT_BOUNDARY,AT_NO_PROGRESS);
    if(!connection_truthy(s)) return observe(s,AT_DISCONNECTED,AT_OK);
    if(s->retry_count>=AT_JS_EXACT_MAX) return observe(s,AT_BOUNDARY,AT_DOMAIN);
    ++s->retry_count;
    return observe(s,s->retry_count<10?AT_WRITE:AT_IDLE,AT_OK);
}

at_status at_uid14(unsigned has_object,const uint8_t *input,size_t length,
                   uint8_t out[14]) {
    if(!has_object||!out||(!input&&length)) return AT_DOMAIN;
    if(length>=18) memcpy(out,input+4,14);
    else memset(out,0,14);
    return AT_OK;
}
