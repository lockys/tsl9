// Execute only the pinned, extracted OTA module with synthetic input and offline stubs.
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const source=fs.readFileSync(process.argv[2]);
if(crypto.createHash('sha256').update(source).digest('hex')!=='c5eb7ae87e5edf310379f19743d720114c9717c3484b8abd30ad8b158affc017')throw Error('Original APK JS identity mismatch');
const moduleSource=source.subarray(0x181e8,0x19b20).toString('utf8');
const scenarios=['normal','readback','boot','nonzeroU','extraS','writeBad','startTimeout','writeTimeout','readMismatch','endTimeout','hw20'];
if(process.argv[3])scenarios.push('userRaw');
for(const name of scenarios){
  const actualRaw=name==='userRaw'?fs.readFileSync(process.argv[3]):null;
  if(actualRaw&&(actualRaw.length===0||actualRaw.length%1024||actualRaw.length>256*1024))throw Error('User RAW fixture must have whole 1024-byte pages');
  const pages=Array.from({length:actualRaw?actualRaw.length/1024:name==='readback'?2:1},(_,page)=>{const b=new Uint8Array(1026);b[0]=page>>>8;b[1]=page;for(let j=0;j<1024;j++)b[j+2]=actualRaw?actualRaw[page*1024+j]:((page*1024+j)*13)&255;return b;});
  let ota,failed=false,now=0,nextTimer=0;const timers=new Map(),trace=[];
  const uid=new Uint8Array(14).fill(7),buf=new Uint8Array(18);buf.set(uid,4);
  const update={deviceinfo:{buf,hw_ver:name==='hw20'?20:1,fw_ver:1,bt_ver:1},geturl:fun=>'fun='+fun};
  const app={isAdmin:()=>false,getUidUint8Array:b=>Array.from(b.slice(4,18)),modal:()=>{failed=true;},msg:()=>{},getjson:(q,cb)=>{if(!q.startsWith('fun=updateok'))throw Error('Unexpected network operation');cb({success:true,msg:'synthetic'});}};
  const transport={connIsOK:()=>true,tx:(cmd,data)=>trace.push({cmd,data:Array.from(data)})};
  const context={define:(id,factory)=>{const m={exports:{}};factory(id=>id.startsWith('@babel/')?(a=>Array.from(a)):transport,m,m.exports);ota=m.exports;},getApp:()=>app,wx:{showLoading:()=>{}},setInterval:(fn,ms)=>{const id=++nextTimer;timers.set(id,{fn,ms,at:now+ms});return id;},clearInterval:id=>timers.delete(id)};
  vm.runInNewContext(moduleSource,context,{timeout:1000,contextCodeGeneration:{strings:false,wasm:false}});
  ota.update=update;ota.is_app=1;ota.hexbuf=pages;ota.PageSize=1026;ota.prepare();
  const reply=(cmd,data)=>ota.rxCallback(cmd,new Uint8Array(data));
  const tick=()=>{let first;for(const [id,t] of timers)if(!first||t.at<first[1].at)first=[id,t];if(!first)throw Error('Missing OEM retry timer');now=first[1].at;first[1].at+=first[1].ms;first[1].fn();};
  const read=name==='readback'||name==='readMismatch'||name==='hw20';
  reply(0x55,[name==='boot'?1:name==='nonzeroU'?2:0]);if(ota.is_start)ota.Check(false,update);
  if(name==='startTimeout'){for(let i=0;i<12&&ota.updataIng;i++)tick();}
  else{
    reply(0x53,name==='extraS'?[1,1,0]:read?[1,1]:[1]);
    if(name==='writeTimeout'){for(let i=0;i<12&&ota.updataIng;i++)tick();}
    else{
      if(name==='writeBad'){reply(0x57,[1]);const corrupt=pages[0].slice();corrupt[10]^=1;reply(0x57,corrupt);}
      for(let i=0;i<pages.length;i++)reply(0x57,i===1?pages[i]:[0]);
      if(name==='readMismatch'){const corrupt=pages[0].slice();corrupt[10]^=1;for(let i=0;i<5;i++)reply(0x52,corrupt);}
      else{
        if(name==='readback'){for(const p of pages)reply(0x52,p);reply(0x52,[]);}
        if(name==='endTimeout'){for(let i=0;i<12&&ota.updataIng;i++)tick();}else reply(0x45,[]);
      }
    }
  }
  console.log('#state\t'+name+'\t'+(failed?'failed':'done'));
  for(const t of trace)console.log([name,t.cmd,t.data.length,crypto.createHash('sha256').update(Buffer.from(t.data)).digest('hex')].join('\t'));
}
