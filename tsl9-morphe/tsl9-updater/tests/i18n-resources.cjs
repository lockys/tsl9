'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const dirs=['values','values-b+zh+Hans','values-b+zh+Hant'];
const maps=dirs.map(dir=>{
 const xml=fs.readFileSync(path.join(root,'app/src/main/res',dir,'strings.xml'),'utf8');
 const entries=[...xml.matchAll(/<string name="([^"]+)">([\s\S]*?)<\/string>/g)].map(m=>[m[1],m[2]]);
 assert.equal(new Set(entries.map(x=>x[0])).size,entries.length,'duplicate resource '+dir);
 return new Map(entries);
});
let checks=0;const keys=[...maps[0].keys()].sort();
for(let i=1;i<maps.length;i++){
 assert.deepEqual([...maps[i].keys()].sort(),keys,'complete translation '+dirs[i]);checks++;
 for(const key of keys){
  const placeholders=s=>[...s.matchAll(/%\d+\$[a-z]/g)].map(x=>x[0]).sort();
  assert.deepEqual(placeholders(maps[i].get(key)),placeholders(maps[0].get(key)),key+' format arguments');checks++;
  assert(maps[i].get(key).trim(),key+' empty');checks++;
 }
}
const srcDir=path.join(root,'app/src/main/java/com/lockys/tsl9updater');
for(const file of ['OtaSession.java','FirmwareImage.java','HardwareCapture.java']){
 const source=fs.readFileSync(path.join(srcDir,file),'utf8');
 for(const m of source.matchAll(/\bm\("([^"]+)"/g)){assert(maps[0].has(m[1]),file+': '+m[1]);checks++;}
 assert(!/import android\./.test(source),'protocol has no Android dependency');checks++;
}
for(const file of ['MainActivity.java','BleClient.java']){
 const source=fs.readFileSync(path.join(srcDir,file),'utf8');
 const chinese=[...source.matchAll(/"(?:\\.|[^"\\])*"/g)].filter(m=>/[\u3400-\u9fff]/.test(m[0])).map(m=>m[0]);
 assert.deepEqual(chinese.filter(x=>!['"简体中文"','"繁體中文"'].includes(x)),[],file+' hardcoded UI text');checks++;
}
console.log('i18n resources passed: '+checks+' checks / '+keys.length+' keys x 3 locales');
