"""Recheck literal source ranges through the original APK, without evaluating JS."""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
APK_SHA='10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee'
FIXTURE_SHA='adb37a96b215077525fe109990fcf8fde4ffc630b59e4c217365c98297ff8129'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def need(ok,message):
    if not ok:raise AssertionError(message)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apk',type=Path)
    args=parser.parse_args();apk=args.apk
    if apk is None:
        root=HERE.parents[1]
        for relative in ['publish-tsl9/artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk',
                         'artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk']:
            candidate=root/relative
            if candidate.is_file():apk=candidate;break
    need(apk is not None and apk.is_file(),'Original APK required locally; use --apk. No download attempted.')
    need(sha(apk.read_bytes())==APK_SHA,'Original APK identity')
    fixture=HERE/'source-map.json';raw=fixture.read_bytes()
    need(sha(raw)==FIXTURE_SHA,'Sealed literal-source fixture')
    source=json.loads(raw);need(len(source['sections'])==6,'Six source sections')
    member='assets/SaaA_embed/release_2_wx64f19032ca1ea79e.wxapkg'
    with zipfile.ZipFile(apk) as archive:pkg=archive.read(member)
    need(sha(pkg)=='6476a038c1861a431c5039b1644774cb60c338ce64ec64802955f069e19c37e3','Embedded package identity')
    need(pkg[0]==0xbe and pkg[13]==0xed,'Observed package header')
    index_bytes,body_bytes=struct.unpack_from('>II',pkg,5)
    count=struct.unpack_from('>I',pkg,14)[0];at=18;entries={}
    for _ in range(count):
        length=struct.unpack_from('>I',pkg,at)[0];at+=4
        name=pkg[at:at+length].decode('utf8');at+=length
        offset,size=struct.unpack_from('>II',pkg,at);at+=8
        need(name not in entries and offset>=14+index_bytes and offset+size<=len(pkg),'Bounded distinct package member')
        entries[name]=(offset,size)
    need(count==76 and at==14+index_bytes and 14+index_bytes+body_bytes==len(pkg),'Package index/body extent')
    offset,size=entries['/appservice.app.js'];appbytes=pkg[offset:offset+size]
    need(sha(appbytes)=='98d0959f26747f9ec867dab56efe32cb3dfaa2769dd6aa32fd48679c3870a188','Original appservice member')
    app=appbytes.decode('utf8');rows=[]
    for row in source['sections']:
        start,end=row['original_start_codepoint'],row['original_end_codepoint']
        text=app[start:end];data=text.encode('utf8')
        need(text==row['source_utf8'] and len(data)==row['source_bytes'] and sha(data)==row['sha256'],'Exact inert source range: '+row['name'])
        need(app.count('\n',0,start)+1==row['original_line'],'Original line anchor')
        rows.append(dict(name=row['name'],original_start_codepoint=start,original_end_codepoint=end,sha256=sha(data)))
    print(json.dumps(dict(passed=True,apk=str(apk.resolve()),apk_sha256=APK_SHA,
        source_fixture_sha256=FIXTURE_SHA,sections=rows,source_chain_verified=True,
        original_executed=False,emulation=False,network=False,hardware=False)))
if __name__=='__main__':main()
