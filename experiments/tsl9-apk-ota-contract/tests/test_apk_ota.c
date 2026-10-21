#include "apk_ota.h"
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(c) do { ++checks; if(!(c)) { \
    fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#c);return 1; } } while(0)
typedef struct {
    unsigned calls;
    uint8_t type, buf[4096];
    size_t n;
    ak_effect effect;
    int mutate;
} observation;
static ak_effect observe(void *ctx,uint8_t type,uint8_t *buf,size_t n) {
    observation *o=(observation *)ctx;
    ++o->calls;o->type=type;o->n=n;
    if(n<=sizeof(o->buf))memcpy(o->buf,buf,n);
    if(o->mutate && n!=0)buf[0]=238;
    return o->effect;
}
/* Synthetic, unaddressed reply frames only: no identity/control requests. */
static size_t frame(uint8_t *out,uint8_t type,const uint8_t *data,size_t n) {
    size_t i;uint8_t sum=type;
    out[0]=85;out[1]=127;out[2]=type;out[3]=(uint8_t)(n>>8);out[4]=(uint8_t)n;
    sum=(uint8_t)(sum+out[3]+out[4]);
    for(i=0;i<n;++i){out[5+i]=data[i];sum=(uint8_t)(sum+data[i]);}
    out[5+n]=sum;return n+6;
}
int main(void) {
    uint8_t page[1026],wire[4102],zero=0,bad=255;
    ak_rx r;observation o;ak_feed_result f;
    size_t i,n,split;
    for(i=0;i<sizeof(page);++i)page[i]=(uint8_t)(i*37u);
    page[0]=0;page[1]=42;
    CHECK(ak_verify(page,1,page,sizeof(page))==AK_YES);
    CHECK(ak_verify(page,2,page,sizeof(page))==AK_YES);
    CHECK(ak_verify(page,sizeof(page),page,sizeof(page))==AK_YES);
    CHECK(ak_verify(page,0,NULL,0)==AK_NO);
    CHECK(ak_verify(page,1,NULL,0)==AK_UNKNOWN);
    CHECK(ak_verify(page,3,page,2)==AK_NO);
    CHECK(ak_verify(&bad,1,page,sizeof(page))==AK_NO);
    CHECK(ak_w_accepts(&zero,1,NULL,0,1026)==AK_YES);
    CHECK(ak_w_accepts(NULL,0,page,sizeof(page),1026)==AK_NO);
    CHECK(ak_w_accepts(page,2,page,sizeof(page),1026)==AK_NO);
    CHECK(ak_w_accepts(page,sizeof(page),page,sizeof(page),1026)==AK_YES);
    CHECK(ak_w_accepts(page,2,page,sizeof(page),2)==AK_YES);
    CHECK(ak_w_accepts(&bad,1,page,sizeof(page),1026)==AK_NO);
    /* Every fragmentation boundary of a legitimate full W echo. */
    n=frame(wire,87,page,sizeof(page));
    for(split=0;split<=n;++split){
        memset(&o,0,sizeof(o));ak_rx_init(&r);
        f=ak_rx_feed(&r,wire,split,100,observe,&o);
        CHECK(f.effect==AK_RETURNED && f.consumed==split);
        f=ak_rx_feed(&r,wire+split,n-split,101,observe,&o);
        CHECK(f.effect==AK_RETURNED && o.calls==1 && o.type==87);
        CHECK(o.n==sizeof(page) && memcmp(o.buf,page,sizeof(page))==0);
        CHECK(r.state==0 && r.retained_length==1 && r.retained[0]==0);
    }
    /* Empty wire W success normalizes the clean buffer to one byte zero. */
    ak_rx_init(&r);memset(&o,0,sizeof(o));n=frame(wire,87,NULL,0);
    f=ak_rx_feed(&r,wire,n,100,observe,&o);
    CHECK(f.callbacks==1 && o.n==1 && o.buf[0]==0);
    CHECK(ak_w_accepts(o.buf,o.n,page,sizeof(page),1026)==AK_YES);
    /* Bad checksum retains its nonempty buffer for the next empty frame. */
    n=frame(wire,87,page,2);wire[n-1]^=1;
    memset(&o,0,sizeof(o));f=ak_rx_feed(&r,wire,n,110,observe,&o);
    CHECK(o.calls==0 && r.state==0 && r.retained_length==2);
    n=frame(wire,87,NULL,0);f=ak_rx_feed(&r,wire,n,111,observe,&o);
    CHECK(o.calls==1 && o.n==2 && memcmp(o.buf,page,2)==0);
    CHECK(ak_w_accepts(o.buf,o.n,page,sizeof(page),1026)==AK_NO);
    CHECK(ak_verify(o.buf,o.n,page,sizeof(page))==AK_YES);
    /* Timeout resets state only, preserving partially received allocation. */
    ak_rx_init(&r);memset(&o,0,sizeof(o));n=frame(wire,87,page,2);
    f=ak_rx_feed(&r,wire,6,100,observe,&o);
    CHECK(r.state==5 && r.index==1 && r.retained_length==2);
    n=frame(wire,87,NULL,0);f=ak_rx_feed(&r,wire,n,600,observe,&o);
    CHECK(o.calls==1 && o.n==2 && o.buf[0]==page[0] && o.buf[1]==0);
    /* Before 500ms, the same bytes continue the incomplete frame instead. */
    ak_rx_init(&r);memset(&o,0,sizeof(o));n=frame(wire,87,page,2);
    f=ak_rx_feed(&r,wire,6,100,observe,&o);
    n=frame(wire,87,NULL,0);f=ak_rx_feed(&r,wire,n,599,observe,&o);
    CHECK(o.calls==0);
    /* A successful empty R callback can pass Verify for pages < 256. */
    ak_rx_init(&r);memset(&o,0,sizeof(o));n=frame(wire,82,NULL,0);
    f=ak_rx_feed(&r,wire,n,100,observe,&o);
    CHECK(o.n==1 && ak_verify(o.buf,o.n,page,sizeof(page))==AK_YES);
    page[0]=1;CHECK(ak_verify(o.buf,o.n,page,sizeof(page))==AK_NO);page[0]=0;
    /* No try/finally in APK: a thrown callback prevents buffer/state reset. */
    ak_rx_init(&r);memset(&o,0,sizeof(o));o.effect=AK_THROWN;
    n=frame(wire,87,page,2);wire[n]=85;
    f=ak_rx_feed(&r,wire,n+1,100,observe,&o);
    CHECK(f.effect==AK_THROWN && f.consumed==n && f.callbacks==1);
    CHECK(r.state==6 && r.retained_length==2 && r.retained[1]==42);
    /* Unknown callback completion must not silently assume a normal return. */
    ak_rx_init(&r);n=frame(wire,87,NULL,0);
    f=ak_rx_feed(&r,wire,n,100,NULL,NULL);
    CHECK(f.effect==AK_EFFECT_UNKNOWN && f.consumed==n && r.state==6);
    /* Upper declared-length boundary and oversized rejection preserve buffer. */
    memset(page,255,sizeof(page));
    memset(&o,0,sizeof(o));ak_rx_init(&r);
    for(i=0;i<4096;++i)wire[5+i]=(uint8_t)i;
    wire[0]=85;wire[1]=127;wire[2]=82;wire[3]=16;wire[4]=0;wire[4101]=98;
    f=ak_rx_feed(&r,wire,4102,100,observe,&o);
    CHECK(f.callbacks==1 && o.n==4096 && o.buf[4095]==255);
    ak_rx_init(&r);r.retained[0]=9;
    wire[0]=85;wire[1]=127;wire[2]=87;wire[3]=16;wire[4]=1;
    f=ak_rx_feed(&r,wire,5,100,observe,&o);
    CHECK(r.state==0 && r.retained_length==1 && r.retained[0]==9);
    /* Callback mutation is synchronous borrowing, not JS array lifetime. */
    ak_rx_init(&r);memset(&o,0,sizeof(o));o.mutate=1;
    n=frame(wire,87,&zero,1);f=ak_rx_feed(&r,wire,n,100,observe,&o);
    CHECK(o.calls==1 && o.buf[0]==0 && f.effect==AK_RETURNED);
    CHECK(r.state==0 && r.retained_length==1 && r.retained[0]==0);
    /* Empty notifications update time; backwards Date does not trigger reset. */
    ak_rx_init(&r);memset(&o,0,sizeof(o));n=frame(wire,87,page,2);
    f=ak_rx_feed(&r,wire,6,100,observe,&o);
    f=ak_rx_feed(&r,NULL,0,50,observe,&o);
    CHECK(r.state==5 && r.notification_time==50 && f.callbacks==0);
    f=ak_rx_feed(&r,NULL,0,549,observe,&o);CHECK(r.state==5);
    f=ak_rx_feed(&r,NULL,0,550,observe,&o);CHECK(r.state==5);
    f=ak_rx_feed(&r,NULL,0,1050,observe,&o);
    CHECK(r.state==0 && r.retained_length==2 && f.consumed==0);
    /* All U8 data/checksum values exercise wrapping and checksum rejection. */
    for(i=0;i<256;++i){
        uint8_t value=(uint8_t)i;
        ak_rx_init(&r);memset(&o,0,sizeof(o));n=frame(wire,87,&value,1);
        f=ak_rx_feed(&r,wire,n,100,observe,&o);
        CHECK(o.calls==1 && o.n==1 && o.buf[0]==value && f.effect==AK_RETURNED);
        ak_rx_init(&r);memset(&o,0,sizeof(o));n=frame(wire,87,NULL,0);
        wire[n-1]=value;f=ak_rx_feed(&r,wire,n,100,observe,&o);
        CHECK(o.calls==(i==87 ? 1u : 0u) && r.state==0);
    }
    printf("{\"passed\":true,\"groups\":12,\"checks\":%u,\"synthetic_only\":true}\n",checks);
    return 0;
}
