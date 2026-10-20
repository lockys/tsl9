"""Loopback HTTP contract and strict-decoder tests. No vendor API requests."""
from pathlib import Path
import hashlib,http.server,json,shutil,subprocess,threading,urllib.parse,uuid
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT.parent
SCRIPT=ROOT/'download-tsl-firmware.ps1'
CATALOG=WORK/'firmware-downloads/legacy-options-2026-10-20/evidence/server-options-receipt.json'
if not CATALOG.is_file():
    CATALOG=WORK/'apk-analysis/tsl9-version-download-2026-10-20/legacy-normal-client/attempt-e6b363f19bf7412592f957d6b4a1057c/receipt.json'
PWSH=shutil.which('pwsh')
if not PWSH:raise RuntimeError('PowerShell 7.2+ required')
OUT=WORK/'apk-analysis/tsl9-download-script-2026-10-20/mock-tests'/uuid.uuid4().hex
OUT.mkdir(parents=True,exist_ok=False)
UID='00112233445566778899AABB';marker='接收OK'.encode('utf-8')
payload=bytes(range(256))*4;encoded=bytes(v^0xb7 for v in payload);line=encoded.hex().encode('ascii')
state={};requests=[]
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        n=int(self.headers.get('Content-Length','0'));raw=self.rfile.read(n)
        request=dict(path=self.path,fields=urllib.parse.parse_qs(raw.decode('ascii'),strict_parsing=True),content_type=self.headers.get('Content-Type'))
        requests.append(request)
        self.send_response(state.get('status',200))
        if state.get('redirect'):self.send_header('Location','http://127.0.0.1:'+str(self.server.server_port)+'/must-not-be-followed')
        body=state.get('body',b'');self.send_header('Content-Type','text/plain; charset=UTF-8')
        self.send_header('Content-Length',str(state.get('declared_length',len(body))));self.end_headers()
        try:self.wfile.write(body)
        except (BrokenPipeError,ConnectionResetError):pass
    def do_GET(self):
        requests.append(dict(unexpected_method='GET'));self.send_error(500)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url='http://127.0.0.1:'+str(server.server_port)+'/ffkj/user/'
cases=[
    ('valid_one_page',dict(body=line+marker),True,1,2966),
    ('valid_two_pages_trailing_CRLF',dict(body=line+b'\r\n'+line+b'\r\n'+marker),True,1,2966),
    ('redirect_stops',dict(status=302,redirect=True),False,1,2966),
    ('forbidden_stops',dict(status=403),False,1,2966),
    ('rate_limit_stops',dict(status=429),False,1,2966),
    ('invalid_hex_no_body_log',dict(body=b'not firmware '+UID.encode()+marker),False,1,2966),
    ('missing_marker',dict(body=line),False,1,2966),
    ('duplicate_marker',dict(body=line+marker+marker),False,1,2966),
    ('bare_lf_rejected',dict(body=line+b'\n'+line+marker),False,1,2966),
    ('short_page_rejected',dict(body=b'0000'+marker),False,1,2966),
    ('invalid_utf8',dict(body=b'\xff'+marker),False,1,2966),
    ('too_many_pages',dict(body=b'\r\n'.join([line]*97)+marker),False,1,2966),
    ('oversize_header',dict(body=b'',declared_length=262145),False,1,2966),
    ('unknown_ID_no_request',dict(body=line+marker),False,0,999999),
]
results=[]
try:
    for name,response,ok,count,fid in cases:
        state.clear();state.update(response);requests.clear();target=OUT/name
        command=[PWSH,'-NoProfile','-NonInteractive','-File',str(SCRIPT),'-FirmwareId',str(fid),'-OptionsReceipt',str(CATALOG),'-OutputRoot',str(target),'-MockUri',url]
        run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45,check=False)
        # Only fixed synthetic data is used; still enforce script output privacy.
        assert UID.encode() not in run.stdout+run.stderr,(name,'UID leaked')
        (OUT/(name+'.stdout.txt')).write_bytes(run.stdout);(OUT/(name+'.stderr.txt')).write_bytes(run.stderr)
        value=json.loads(run.stdout.decode('utf-8-sig').strip())
        assert (run.returncode==0)==ok,(name,run.returncode,value,run.stderr.decode('utf-8','replace'))
        assert len(requests)==count,(name,'unexpected attempts/redirect',len(requests))
        if count:
            request=requests[0];parsed=urllib.parse.urlsplit(request['path']);query=urllib.parse.parse_qs(parsed.query)
            assert parsed.path=='/ffkj/user/' and set(query)=={'Temp'} and 1<=int(query['Temp'][0])<=9999
            assert request['fields']==dict(action=['GetFirmware'],f_UID=[UID],f_FirmwareID=[str(fid)],ver=['30'])
            assert request['content_type'].startswith('application/x-www-form-urlencoded')
        if ok:
            folder=Path(value['directory']);pagecount=2 if name.startswith('valid_two') else 1
            assert Path(value['bin']).read_bytes()==payload*pagecount
            assert (folder/'server-encoded.dat').read_bytes()==encoded*pagecount
            assert (folder/'download.hex').read_bytes()==(line+b'\r\n')*pagecount
            assert (folder/'http-response.txt').read_bytes()==response['body']
            receipt=json.loads((folder/'receipt.json').read_text(encoding='utf-8'))
            assert receipt['mock'] and receipt['uid_stored'] is False and receipt['request_attempts']==1
            assert not receipt['target_ready'] and not receipt['ota_verified'] and not receipt['hardware_applicability_proved']
            assert UID not in (folder/'receipt.json').read_text(encoding='utf-8')
            for filename,seal in receipt['files'].items():
                b=(folder/filename).read_bytes();assert len(b)==seal['bytes'] and hashlib.sha256(b).hexdigest()==seal['sha256']
        else:
            assert value['status']=='stopped' and value['retries']==0
            assert not target.exists(),'Invalid reply must not be persisted'
        results.append(dict(case=name,passed=True,request_count=count,exit=run.returncode,status=value['status'],reason=value.get('reason')))
finally:server.shutdown();server.server_close()
report=dict(schema='download-script-loopback-contract-tests-v1',passed=True,cases=results,count=len(results),
    script_sha256=hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),catalog_sha256=hashlib.sha256(CATALOG.read_bytes()).hexdigest(),
    endpoint='literal loopback only',vendor_network_requests=0,real_UID_used=False,firmware_executed=False,hardware=False)
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=True,cases=len(results),vendor_network_requests=0,receipt=str(OUT/'verification.json'))))
