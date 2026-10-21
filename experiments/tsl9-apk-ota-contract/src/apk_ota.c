#include "apk_ota.h"
#include <string.h>

void ak_rx_init(ak_rx *r) {
    memset(r,0,sizeof(*r));r->retained_length=1;
}
ak_feed_result ak_rx_feed(ak_rx *r,const uint8_t *p,size_t n,int64_t now,
                          ak_callback cb,void *ctx) {
    ak_feed_result result={0,0,AK_RETURNED};size_t i;
    if(n!=0 && p==NULL){result.effect=AK_EFFECT_UNKNOWN;return result;}
    /* Notification timeout is evaluated once, including an empty notify. */
    if(now>=r->notification_time &&
       (uint64_t)now-(uint64_t)r->notification_time>=500u)r->state=0;
    r->notification_time=now;
    for(i=0;i<n;++i){
        uint8_t b=p[i];result.consumed=i+1;
        if(r->state==0 && b==85)r->state=1;
        else if(r->state==1 && b==127){r->state=2;r->sum=0;}
        else if(r->state==2){r->state=3;r->type=b;r->sum=(uint8_t)(r->sum+b);}
        else if(r->state==3){r->state=4;r->declared=(uint16_t)((uint16_t)b<<8);r->sum=(uint8_t)(r->sum+b);}
        else if(r->state==4){
            r->index=0;r->declared=(uint16_t)(r->declared|b);
            if(r->declared==0)r->state=6;
            else if(r->declared<=4096){
                r->retained_length=r->declared;
                memset(r->retained,0,r->retained_length);r->state=5;
            }else r->state=0;
            r->sum=(uint8_t)(r->sum+b);
        }else if(r->state==5){
            /* Valid state produced by this parser always has index<len<=4096. */
            if(r->index>=r->declared || r->declared>4096){
                result.effect=AK_EFFECT_UNKNOWN;return result;
            }
            r->retained[r->index++]=b;
            if(r->index>=r->declared)r->state=6;
            r->sum=(uint8_t)(r->sum+b);
        }else if(r->state==6 && r->sum==b){
            ak_effect effect=AK_EFFECT_UNKNOWN;
            ++result.callbacks;
            if(cb!=NULL)effect=cb(ctx,r->type,r->retained,r->retained_length);
            if(effect!=AK_RETURNED){result.effect=effect;return result;}
            r->retained[0]=0;r->retained_length=1;r->state=0;
        }else r->state=0;
    }
    return result;
}
ak_truth ak_verify(const uint8_t *p,size_t n,const uint8_t *q,size_t qn) {
    size_t i;
    if(n==0)return AK_NO;
    if(p==NULL || q==NULL)return AK_UNKNOWN;
    for(i=0;i<n;++i)if(i>=qn || p[i]!=q[i])return AK_NO;
    return AK_YES;
}
ak_truth ak_w_accepts(const uint8_t *p,size_t n,const uint8_t *q,size_t qn,size_t pn) {
    if(n==1){if(p==NULL)return AK_UNKNOWN;if(p[0]==0)return AK_YES;}
    return n==pn ? ak_verify(p,n,q,qn) : AK_NO;
}
