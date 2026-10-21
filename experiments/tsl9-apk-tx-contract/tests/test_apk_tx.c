#include "apk_tx.h"
#include "apk_ota.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned checks, groups;
#define T(x) do { ++checks; if (!(x)) { fprintf(stderr,"line %d: %s\n",__LINE__,#x); exit(1); } } while(0)
static void connected(at_sender *s) {
    s->transport.notify=1; s->transport.device_id="synthetic-device";
    s->transport.service_id="synthetic-service";
    s->transport.characteristic_id="synthetic-characteristic";
}
static void framing(void) {
    uint8_t b[64], p[]={0x00,0xff,0x80}; size_t n=99;
    const uint8_t empty[]={0x55,0x7f,0x45,0,0,0x45};
    const uint8_t filled[]={0x55,0x7f,0x57,0,3,0,0xff,0x80,0xd9};
    ++groups;
    T(at_encode(0x45,NULL,0,b,sizeof b,&n)==AT_OK); T(n==sizeof empty);
    T(!memcmp(b,empty,n));
    T(at_encode(0x57,p,sizeof p,b,sizeof b,&n)==AT_OK); T(n==sizeof filled);
    T(!memcmp(b,filled,n));
}
static void large_frames(void) {
    uint8_t *p=(uint8_t *)calloc(65536,1), *b=(uint8_t *)malloc(65542); size_t n;
    ++groups; T(p&&b);
    p[65535]=0xaa;
    T(at_encode(0x53,p,65535,b,65542,&n)==AT_OK); T(n==65541);
    T(b[3]==0xff&&b[4]==0xff&&b[n-1]==0x51);
    T(at_encode(0x53,p,65536,b,65542,&n)==AT_OK); T(n==65542);
    T(b[3]==0&&b[4]==0&&b[n-1]==0xfd); T(b[65540]==0xaa);
    free(b); free(p);
}
static void preflight(void) {
    uint8_t b[16],p[]={1,2}; size_t n=7; at_sender s; at_observation o;
    ++groups; memset(b,0xa5,sizeof b);
    T(at_encode(1,p,2,b,7,&n)==AT_CAPACITY); T(b[0]==0xa5&&b[15]==0xa5);
    T(at_encode(1,NULL,1,b,sizeof b,&n)==AT_DOMAIN);
    T(at_encode(1,p,2,NULL,16,&n)==AT_DOMAIN);
    T(at_encode(1,p,(size_t)UINT32_MAX+1,b,sizeof b,&n)==AT_DOMAIN);
    at_init(&s,b,7); connected(&s); s.index=3; s.retry_count=4;
    o=at_begin(&s,1,p,2); T(o.kind==AT_BOUNDARY&&o.status==AT_CAPACITY);
    T(s.index==3&&s.retry_count==4&&!s.initialized&&b[0]==0xa5);
    o=at_success(&s); T(o.status==AT_DOMAIN);
}
static void chain(void) {
    uint8_t b[80],p[37]; at_sender s; at_observation o;
    ++groups; memset(p,0x38,sizeof p); at_init(&s,b,sizeof b); connected(&s);
    o=at_begin(&s,0x57,p,sizeof p); T(o.kind==AT_WRITE&&o.length==20&&o.index==0);
    T(o.value_defined&&o.value==b&&s.chunks==3&&s.retry_count==0);
    o=at_success(&s); T(o.kind==AT_WRITE&&o.index==1&&o.length==20&&o.value==b+20);
    o=at_success(&s); T(o.kind==AT_WRITE&&o.index==2&&o.length==3&&o.value==b+40);
    o=at_success(&s); T(o.kind==AT_IDLE&&s.index==3&&s.retry_count==0);
}
static void retries(void) {
    uint8_t b[80],p[37]={0}; at_sender s; at_observation o; unsigned i;
    ++groups; at_init(&s,b,sizeof b); connected(&s); o=at_begin(&s,0x57,p,sizeof p);
    T(o.kind==AT_WRITE);
    for(i=1;i<10;i++) { o=at_failure(&s); T(o.kind==AT_WRITE&&o.index==0&&o.retry_count==i); }
    o=at_failure(&s); T(o.kind==AT_IDLE&&o.retry_count==10&&s.index==0);
    /* Another outstanding success can revive the shared chain after a drop. */
    o=at_success(&s); T(o.kind==AT_WRITE&&o.index==1&&o.retry_count==0);
    o=at_failure(&s); T(o.kind==AT_WRITE&&o.retry_count==1&&o.index==1);
}
static void disconnected(void) {
    uint8_t b[80],p[37]={0}; at_sender s; at_observation o;
    ++groups; at_init(&s,b,sizeof b);
    o=at_begin(&s,1,p,sizeof p); T(o.kind==AT_DISCONNECTED&&s.chunks==3&&s.index==0);
    connected(&s); o=at_begin(&s,1,p,sizeof p); T(o.kind==AT_WRITE);
    o=at_failure(&s); T(s.retry_count==1);
    s.transport.notify=0;
    o=at_success(&s); T(o.kind==AT_DISCONNECTED&&s.index==1&&s.retry_count==1);
    o=at_failure(&s); T(o.kind==AT_DISCONNECTED&&s.index==1&&s.retry_count==1);
    s.transport.notify=1; /* No implicit new write or reset. */
    T(s.index==1&&s.retry_count==1);
}
static void replacement(void) {
    uint8_t b[80],a[37],p[37],old[20]; at_sender s; at_observation o;
    ++groups; memset(a,0xa1,sizeof a); memset(p,0xb2,sizeof p);
    at_init(&s,b,sizeof b); connected(&s);
    o=at_begin(&s,0x57,a,sizeof a); memcpy(old,o.value,20);
    o=at_begin(&s,0x52,p,sizeof p); T(o.index==0&&o.value[2]==0x52);
    T(old[2]==0x57&&old[5]==0xa1);
    /* Old A success applies to B and skips B's still outstanding first chunk. */
    o=at_success(&s); T(o.index==1&&o.kind==AT_WRITE&&o.value[0]==0xb2);
    o=at_failure(&s); T(o.index==1&&o.retry_count==1&&o.value[0]==0xb2);
    /* Old B:first success and B:second success advance the same shared index. */
    o=at_success(&s); T(o.index==2&&o.kind==AT_WRITE);
    o=at_success(&s); T(o.index==3&&o.kind==AT_IDLE);
    /* An outstanding failure has NO index<length guard in the original. */
    o=at_failure(&s); T(o.kind==AT_WRITE&&!o.value_defined&&!o.value&&o.length==0);
    T(o.retry_count==1&&o.index==3);
}
static void live_transport(void) {
    uint8_t b[80],p[37]={0}; at_sender s; at_observation o;
    ++groups; at_init(&s,b,sizeof b); connected(&s);
    o=at_begin(&s,1,p,sizeof p); T(!strcmp(o.device_id,"synthetic-device"));
    T(!o.write_no_response);
    s.transport.device_id="synthetic-new"; s.transport.service_id="service-new";
    s.transport.characteristic_id="char-new"; s.transport.write_no_response=1;
    s.transport.mtu=1; /* Existing chunks keep the original MTU snapshot. */
    o=at_success(&s); T(o.length==20&&o.write_no_response);
    T(!strcmp(o.device_id,"synthetic-new")&&!strcmp(o.service_id,"service-new"));
    T(!strcmp(o.characteristic_id,"char-new"));
    s.transport.service_id=""; o=at_failure(&s); T(o.kind==AT_DISCONNECTED&&s.retry_count==0);
}
static void mtu(void) {
    uint8_t b[600],p[500]={0}; at_sender s; at_observation o;
    ++groups; at_init(&s,b,sizeof b); connected(&s); s.transport.mtu=1000;
    o=at_begin(&s,1,p,sizeof p); T(o.length==244&&s.chunks==3&&s.stride==244);
    s.transport.mtu=1; o=at_begin(&s,1,NULL,0); T(o.length==1&&s.chunks==6);
    T(o.value[0]==0x55); o=at_success(&s); T(o.value[0]==0x7f);
    s.retry_count=7; s.transport.mtu=0; o=at_begin(&s,1,NULL,0);
    T(o.kind==AT_BOUNDARY&&o.status==AT_NO_PROGRESS);
    T(s.index==0&&s.chunks==0&&s.retry_count==7);
    o=at_success(&s); T(o.status==AT_NO_PROGRESS&&s.index==0);
    o=at_failure(&s); T(o.status==AT_NO_PROGRESS&&s.retry_count==7);
    s.transport.mtu=20; o=at_begin(&s,2,NULL,0);
    T(o.status==AT_NO_PROGRESS&&s.wire[2]==1);
    at_init(&s,b,sizeof b); connected(&s);
    s.transport.mtu=-4; o=at_begin(&s,1,NULL,0); T(o.status==AT_NO_PROGRESS);
}
static void txvar_reset(void) {
    uint8_t b[80],p[37]={0}; at_sender s; at_observation o;
    ++groups; at_init(&s,b,sizeof b); connected(&s); s.transport.mtu=10;
    o=at_begin(&s,1,p,sizeof p); T(o.length==10);
    o=at_failure(&s); T(s.retry_count==1);
    at_transport_init(&s,"synthetic-other");
    T(s.transport.mtu==20&&!s.transport.notify&&s.chunks==5&&s.retry_count==1);
    T(s.transport.service_id[0]==0&&s.transport.characteristic_id[0]==0);
    o=at_success(&s); T(o.kind==AT_DISCONNECTED&&s.index==1&&s.retry_count==1);
}
static void snapshot(void) {
    uint8_t b[80],p[37]; at_sender s; at_observation o;
    ++groups; memset(p,0x91,sizeof p); at_init(&s,b,sizeof b); connected(&s);
    o=at_begin(&s,1,p,sizeof p); T(o.value[5]==0x91);
    memset(p,0x12,sizeof p); o=at_success(&s); T(o.value[0]==0x91);
    o=at_begin(&s,2,p,sizeof p); T(o.value[5]==0x12&&s.retry_count==0);
}
typedef struct { unsigned count; uint8_t type, data[128]; size_t length; } received;
static ak_effect receive(void *ctx,uint8_t type,uint8_t *p,size_t n) {
    received *r=(received *)ctx; T(n<=sizeof r->data);
    ++r->count; r->type=type; r->length=n; memcpy(r->data,p,n); return AK_RETURNED;
}
static void roundtrip(void) {
    uint8_t b[128],p[67]; at_sender s; at_observation o; ak_rx rx;
    ak_feed_result f; received r; size_t i; unsigned steps=0;
    ++groups; for(i=0;i<sizeof p;i++) p[i]=(uint8_t)(i+8);
    memset(&r,0,sizeof r); at_init(&s,b,sizeof b); connected(&s); s.transport.mtu=7;
    ak_rx_init(&rx); o=at_begin(&s,0x57,p,sizeof p);
    while(o.kind==AT_WRITE) {
        T(++steps<20&&o.value_defined);
        f=ak_rx_feed(&rx,o.value,o.length,1000,receive,&r);
        T(f.effect==AK_RETURNED&&f.consumed==o.length);
        o=at_success(&s);
    }
    T(steps==11&&r.count==1&&r.type==0x57&&r.length==sizeof p);
    T(!memcmp(r.data,p,sizeof p));
    b[s.wire_length-1]^=1; memset(&r,0,sizeof r); ak_rx_init(&rx);
    f=ak_rx_feed(&rx,b,s.wire_length,1000,receive,&r); T(r.count==0&&f.callbacks==0);
}
static void empty_receiver(void) {
    uint8_t b[6]; size_t n; ak_rx rx; ak_feed_result f; received r;
    ++groups; memset(&r,0,sizeof r); ak_rx_init(&rx);
    T(at_encode(0x57,NULL,0,b,sizeof b,&n)==AT_OK);
    f=ak_rx_feed(&rx,b,n,1000,receive,&r);
    T(f.callbacks==1&&r.count==1&&r.length==1&&r.data[0]==0);
    T(ak_w_accepts(r.data,r.length,NULL,0,1026)==AK_YES);
}
static void uid_helper(void) {
    uint8_t p[20],b[14]; size_t i;
    ++groups; for(i=0;i<sizeof p;i++) p[i]=(uint8_t)(0x60+i);
    T(at_uid14(1,p,sizeof p,b)==AT_OK); T(b[0]==0x64&&b[13]==0x71);
    memset(b,0xff,sizeof b); T(at_uid14(1,p,17,b)==AT_OK);
    for(i=0;i<sizeof b;i++) T(b[i]==0);
    memset(b,0xa5,sizeof b); T(at_uid14(0,NULL,0,b)==AT_DOMAIN&&b[0]==0xa5);
    T(at_uid14(1,NULL,18,b)==AT_DOMAIN&&b[0]==0xa5);
    T(at_uid14(1,NULL,0,b)==AT_OK&&b[13]==0);
}
static void exactness(void) {
    uint8_t b[16]; at_sender s; at_observation o;
    ++groups; at_init(&s,b,sizeof b); connected(&s); o=at_begin(&s,1,NULL,0);
    T(o.kind==AT_WRITE);
    s.index=UINT64_C(9007199254740991); o=at_success(&s);
    T(o.kind==AT_BOUNDARY&&o.status==AT_DOMAIN&&s.index==UINT64_C(9007199254740991));
    s.index=0; s.retry_count=UINT64_C(9007199254740991); o=at_failure(&s);
    T(o.status==AT_DOMAIN&&s.retry_count==UINT64_C(9007199254740991));
}
int main(void) {
    framing(); large_frames(); preflight(); chain(); retries(); disconnected();
    replacement(); live_transport(); mtu(); txvar_reset(); snapshot(); roundtrip();
    empty_receiver(); uid_helper(); exactness();
    printf("{\"passed\":true,\"groups\":%u,\"checks\":%u,\"BLE\":false,\"original_executed\":false}\n",groups,checks);
    return 0;
}
