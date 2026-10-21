"""Offline literal-source proof. Parses containers/text; never evaluates JavaScript."""
import argparse, hashlib, json, struct, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
APK='publish-tsl9/artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk'
APKSHA='10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee'
PKGSHA='6476a038c1861a431c5039b1644774cb60c338ce64ec64802955f069e19c37e3'
APPSHA='98d0959f26747f9ec867dab56efe32cb3dfaa2769dd6aa32fd48679c3870a188'
MODULES={'updater':'7686EA01BD32C12F10E0820688FFC052','ble':'BDB12361BD32C12FDBD74B66CADFC052','device':'7FE9D4A3BD32C12F198FBCA429EFC052'}
def sha(b):return hashlib.sha256(b).hexdigest()
def need(v,m):
    if not v:raise AssertionError(m)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def app_source():
    p=ROOT/APK;need(sha(p.read_bytes())==APKSHA,'APK identity')
    with zipfile.ZipFile(p) as z:b=z.read('assets/SaaA_embed/release_2_wx64f19032ca1ea79e.wxapkg')
    need(sha(b)==PKGSHA and b[0]==190 and b[13]==237,'package identity/header')
    ix,body=struct.unpack_from('>II',b,5);count=struct.unpack_from('>I',b,14)[0];at=18;entries={}
    for _ in range(count):
        n=struct.unpack_from('>I',b,at)[0];at+=4;name=b[at:at+n].decode('utf8');at+=n
        off,size=struct.unpack_from('>II',b,at);at+=8
        need(name not in entries and off>=14+ix and off+size<=len(b),'bounded unique entry');entries[name]=(off,size)
    need(count==76 and at==14+ix and 14+ix+body==len(b),'package extent')
    off,size=entries['/appservice.app.js'];a=b[off:off+size];need(sha(a)==APPSHA,'appservice identity');return a.decode('utf8')
def function_end(s,start):
    """Brace balancing for selected function literals; strings/comments are inert."""
    begin=s.index('{',start);depth=0;quote=None;i=begin
    while i<len(s):
        c=s[i]
        if quote:
            if c=='\\':i+=2;continue
            if c==quote:quote=None
        elif c in "\"'`":quote=c
        elif s[i:i+2]=='//':
            end=s.find('\n',i+2);i=len(s) if end<0 else end;continue
        elif s[i:i+2]=='/*':i=s.index('*/',i+2)+2;continue
        elif c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:return i+1
        i+=1
    raise AssertionError('unbalanced selected literal')
def make_sources():
    app=app_source();modules={};sections=[]
    for key,name in MODULES.items():
        p=ROOT/'apk-analysis/ota-static-scope'/(name+'.js');raw=p.read_bytes();s=raw.decode('utf8');base=app.find(s)
        need(base>=0 and app.count(s)==1,'exact retained module '+key)
        modules[key]={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(raw),'bytes':len(raw),'original_start_codepoint':base,'original_end_codepoint':base+len(s)}
    def add(name,key,token,endtoken=None):
        s=app if key=='app' else (ROOT/modules[key]['path']).read_text(encoding='utf8')
        start=s.index(token);end=s.index(endtoken,start) if endtoken else function_end(s,start)
        base=0 if key=='app' else modules[key]['original_start_codepoint'];text=s[start:end]
        sections.append(dict(name=name,module=key,module_start_codepoint=start,module_end_codepoint=end,
          original_start_codepoint=base+start,original_end_codepoint=base+end,original_line=app.count('\n',0,base+start)+1,
          source_bytes=len(text.encode('utf8')),sha256=sha(text.encode('utf8')),source_utf8=text))
    for name in ['TxSend','GetUidUint8Array','prepare','SendRead','UpgradeEnd','stop','start','Read','Write','ready']:
        add('updater.'+name,'updater',name+':function')
    for name in ['txvarinit','tx']:add('ble.'+name,'ble',name+':function')
    add('ble.initial-shared-state','ble','module.exports=(e(t={',',txvarinit:')
    add('ble.txData-definition','ble','"txData",',',e(t,"txCallback",')
    add('ble.txCallback-definition','ble','e(t,"txCallback",',',e(t,"connIsOK",')
    add('ble.connIsOK-definition','ble','e(t,"connIsOK",',',e(t,"init",')
    add('ble.init-and-MTU-and-Rx','ble','e(t,"init",',',e(t,"close",') if ',e(t,"close",' in (ROOT/modules['ble']['path']).read_text(encoding='utf8') else add('ble.init-and-MTU-and-Rx','ble','e(t,"init",')
    add('app.getUidUint8Array','app','getUidUint8Array:function')
    add('device.getinfo','device','getinfo:function')
    add('app.Hex2Dec','app','Hex2Dec:function',',getUidUint8Array:')
    add('babel.defineProperty','app','function _defineProperty(')
    return dict(schema='TSL9-APK-TX-SOURCE-v1',apk={'path':APK,'sha256':APKSHA},wxapkg_sha256=PKGSHA,appservice_sha256=APPSHA,offset_unit='Unicode codepoints; end exclusive',modules=modules,sections=sections)
def inspect(x):
    rows={r['name']:r['source_utf8'] for r in x['sections']}
    required={
      'ble.tx':['var r=this.txvar.mtu;r>244&&(r=244)','s=e?e.length:0,c=[85,127,t]','c.push(s>>>8),c.push(255&s)','for(a=2;a<c.length;a++)n+=c[a]','c.push(255&n)','c.splice(0,r)','v[i]=o[i]','this.txData.index=0,this.txData.buf=[]','this.txCallback(!0)'],
      'ble.txData-definition':['wx.writeBLECharacteristicValue','e.txData.index++,e.txCallback(!0)','e.txCallback(!1)','writeNoResponse?"writeNoResponse":"write"'],
      'ble.initial-shared-state':['txData:{buf:[],index:0,retryCount:0}','txvar:{mtu:20'],
      'babel.defineProperty':['Object.defineProperty(e,r,{value:t,enumerable:!0,configurable:!0,writable:!0})'],
      'ble.txCallback-definition':['this.txData.retryCount=0','this.txData.index<this.txData.buf.length','++this.txData.retryCount<10','this.txData(this.txData.buf[this.txData.index])'],
      'ble.init-and-MTU-and-Rx':['wx.onBLEMTUChange','a.txvar.mtu=t.mtu-3','mtu:247','wx.onBLECharacteristicValueChange'],
      'updater.TxSend':['e.connIsOK()?e.tx(t,i):(this.stop(),this.ErrInfo'],
      'app.getUidUint8Array':['t.length>=18?t.slice(4,18):new Uint8Array(14)'],
      'updater.GetUidUint8Array':['i.getUidUint8Array(this.update.deviceinfo.buf)'],
      'device.getinfo':['if(!(s.length<18))','this.deviceinfo.buf=s','this.deviceinfo.id=i.Dec2Hex(s.slice(4,16))','new Uint8Array(Object.values(this.deviceinfo.buf))'],
      'updater.Write':['++this.retryCount>=10','1200','this.TxSend(83','this.TxSend(87,e)'],
      'updater.Read':['++this.retryCount>=5','1e3','this.SendRead()'],
      'updater.SendRead':['this.TxSend(82','this.index>>>8&255,255&this.index'],
      'updater.prepare':['this.TxSend(85'], 'updater.UpgradeEnd':['this.TxSend(69']}
    for name,tokens in required.items():
        for token in tokens:need(token in rows[name],name+' exact source predicate '+token)
    for name in ['ble.tx','ble.txData-definition','ble.txCallback-definition','updater.TxSend']:
        need('Promise' not in rows[name] and 'setTimeout' not in rows[name] and 'setInterval' not in rows[name],name+' no promise/timer in selected function')
    return True
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');args=p.parse_args()
    actual=make_sources();inspect(actual);fixture=HERE/'exact-source.json'
    if args.write:dump(fixture,actual)
    else:need(json.loads(fixture.read_text(encoding='utf8'))==actual,'all exact source ranges/hash metadata')
    negatives=[]
    for name,old,new in [('prefix','c=[85,127,t]','c=[127,85,t]'),('length-endian','c.push(s>>>8),c.push(255&s)','c.push(255&s),c.push(s>>>8)'),('checksum-start','for(a=2;a<c.length;a++)','for(a=0;a<c.length;a++)'),('retry-threshold','++this.txData.retryCount<10','++this.txData.retryCount<11'),('UID-start','t.slice(4,18)','t.slice(3,18)'),('UID-end','t.slice(4,18)','t.slice(4,17)'),('MTU-cap','r>244&&(r=244)','r>247&&(r=247)'),('success-order','e.txData.index++,e.txCallback(!0)','e.txCallback(!0),e.txData.index++')]:
        mutated=json.loads(json.dumps(actual));changed=0
        for row in mutated['sections']:
            if old in row['source_utf8']:row['source_utf8']=row['source_utf8'].replace(old,new);changed+=1
        need(changed>0,'negative present '+name)
        try:inspect(mutated)
        except AssertionError as e:negatives.append({'case':name,'rejected':True,'reason':str(e)})
        else:raise AssertionError('accepted source mutant '+name)
    if args.check:
        seal=json.loads((HERE/'final-audit.json').read_text(encoding='utf8'))
        for row in seal['members']:
            b=(HERE/row['path']).read_bytes();need(len(b)==row['bytes'] and sha(b)==row['sha256'],'sealed member '+row['path'])
    print(json.dumps({'passed':True,'source_chain_verified':True,'sections':len(actual['sections']),'negative_fixtures':negatives,'javascript_executed':False,'network':False,'BLE':False,'hardware':False}))
if __name__=='__main__':main()
