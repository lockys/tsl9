// Executes only selected pinned OEM methods with synthetic data and offline stubs.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto'),assert=require('assert');
if(!process.argv[2])throw Error('Pass the locally extracted original app-service.js path.');
const bytes=fs.readFileSync(process.argv[2]);
assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),'c5eb7ae87e5edf310379f19743d720114c9717c3484b8abd30ad8b158affc017','OEM source identity');
const source=bytes.toString('utf8');
const bleName='BDB12361BD32C12FDBD74B66CADFC052.js';
function load(name,dependencies,app){
  const start=source.indexOf('define("'+name+'"');
  assert(start>=0,'OEM module exists: '+name);
  const next=source.indexOf('define("',start+10);
  const pageRequire=source.indexOf('require("'+name+'")',start);
  const end=pageRequire>=0&&(next<0||pageRequire<next)?pageRequire:next<0?source.length:next;
  let result;
  const context={define:(id,factory)=>{assert.equal(id,name);const module={exports:{}};factory(dependencies,module,module.exports);if(!result)result=module.exports;},
    getApp:()=>app,Page:page=>result=page,wx:{getStorageSync:()=>undefined},setTimeout:()=>0,setInterval:()=>0,clearInterval:()=>{}};
  vm.runInNewContext(source.slice(start,end),context,{timeout:1000,contextCodeGeneration:{strings:false,wasm:false}});
  return result;
}
const ble=load(bleName,id=>{assert(id.includes('defineProperty'));return (object,key,value)=>{object[key]=value;return object;};},{});
ble.txvar.mtu=20;ble.txCallback=()=>{}; // Do not execute wx BLE operations.
const traces=[];
const transport={tx:(command,payload)=>{ble.tx(command,payload);const frame=Buffer.concat(ble.txData.buf.map(chunk=>Buffer.from(chunk)));traces.push({command,payload:Buffer.from(payload||[]),frame});}};
function emit(name,packet,input){console.log([name,packet.command,packet.payload.toString('hex'),packet.frame.toString('hex'),input?input.toString('hex'):'-'].join('\t'));}
const index=load('pages/index/index.js',id=>id.includes('BDB12361')?transport:{},{modal:()=>{throw Error('Unexpected confirmation in synthetic direct event');}});
for(const [name,code] of [['lock',22],['unlock',23],['driver_left',26]]){
  const event={type:'touchstart',currentTarget:{dataset:{btn:code}}};
  if(name==='driver_left')index.SideControl(event);else index.controlBtn(event);
  emit(name,traces.at(-1));
}
index.SideControl({type:'touchend',currentTarget:{dataset:{btn:26}}});emit('seat_stop',traces.at(-1));
for(const hw of [3,5,6,8,19])for(const enabled of [0,1]){
  const baseline=new Uint8Array(76);baseline[0]=hw;baseline[1]=0x10;baseline[2]=0x41;baseline[3]=1;
  for(let i=4;i<18;i++)baseline[i]=i+7;for(let i=18;i<24;i++)baseline[i]=0x90+i;
  if(!enabled)baseline[30]=0x40;
  const app={getCheckData:()=>false,setCheckData:()=>{},isAdmin:()=>false,
    getItemIdx:(item,value)=>{const index=item.data.findIndex(entry=>entry.val===value);return index<0?0:index;},
    msg:()=>{throw Error('Unexpected OEM error');}};
  const update={deviceinfo:{hw_ver:hw,buf:baseline}};
  const page=load('pages/set/set.js',id=>id.includes('@babel')?(value=>Array.from(value)):id.includes('BDB12361')?transport:id.includes('7FE9D4A3')?update:{},app);
  page.setData=patch=>{for(const [key,value] of Object.entries(patch)){const keys=key.split('.');let object=page.data;for(const part of keys.slice(0,-1))object=object[part]||(object[part]={});object[keys.at(-1)]=value;}};
  // Canonicalize synthetic enum defaults through the OEM itself; all-zero
  // time/delay fields are not valid values in its setting lists.
  page.rx(160,baseline);page.tx(163);
  const input=Buffer.from(traces.at(-1).payload);
  for(let i=18;i<24;i++)input[i]=0x90+i;
  input[30]=(input[30]&~0x40)|(enabled?0:0x40);
  page.rx(160,new Uint8Array(input));
  // No B0 / gear / speed input exists in this OEM settings event.
  page.save({currentTarget:{dataset:{id:'blinkHighBeam'}},detail:{value:enabled}});
  const packet=traces.at(-1);assert.equal(packet.command,0xa3);assert.equal(packet.payload.length,76);
  assert.equal((packet.payload[30]>>>6)&1,enabled);assert(packet.payload.subarray(18,24).every(value=>value===0));
  emit('light_'+hw+'_'+enabled,packet,input);
}
