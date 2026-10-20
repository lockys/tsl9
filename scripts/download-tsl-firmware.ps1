#requires -Version 7.2
<#
.SYNOPSIS
POST-download one actually returned FirmwareID and decode its first-stage BIN.
.EXAMPLE
pwsh -NoProfile -File .\scripts\download-tsl-firmware.ps1 -FirmwareId 2966
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidateRange(1,2147483647)][int]$FirmwareId,
    [string]$OutputRoot = "$PSScriptRoot\..\firmware-downloads\manual",
    [string]$OptionsReceipt = "$PSScriptRoot\..\firmware-downloads\legacy-options-2026-10-20\evidence\server-options-receipt.json",
    # Test seam: HTTP literal loopback only; always uses a fixed synthetic UID.
    [Parameter(DontShow=$true)][uri]$MockUri
)
$ErrorActionPreference = 'Stop'
$stage='catalog'; $failure='catalog_invalid'; $attempts=0; $status=$null
$client=$null; $handler=$null; $request=$null; $response=$null; $cancel=$null
$stream=$null; $memory=$null; $uid=$null; $secureUid=$null; $pointer=[IntPtr]::Zero
function Digest([byte[]]$Bytes) {
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant()
}
try {
    $optionsPath=[IO.Path]::GetFullPath($OptionsReceipt)
    $catalogBytes=[IO.File]::ReadAllBytes($optionsPath)
    $catalog=[Text.Encoding]::UTF8.GetString($catalogBytes) | ConvertFrom-Json
    $matches=@($catalog.options | Where-Object { $_.FirmwareID -eq $FirmwareId })
    if($matches.Count -ne 1){$failure='firmware_id_not_in_returned_catalog';throw 'stop'}
    $labels=@($matches[0].version_labels | Where-Object { $_ -cmatch '^V[0-9]+\.[0-9]+\.[0-9]+$' })
    $label=if($labels.Count -eq 1){[string]$labels[0]}else{$null}
    $endpoint=[uri]'https://www.iffrc.com/ffkj/user/'
    $mock=$null -ne $MockUri
    $stage='identity'; $failure='invalid_uid'
    if($mock){
        $ip=$null
        if($MockUri.Scheme -ne 'http' -or -not [Net.IPAddress]::TryParse($MockUri.Host,[ref]$ip) -or
            -not [Net.IPAddress]::IsLoopback($ip) -or $MockUri.UserInfo -or $MockUri.Query -or $MockUri.Fragment){
            $failure='invalid_mock_uri';throw 'stop'
        }
        $endpoint=$MockUri
        $uid='00112233445566778899AABB'
    }else{
        $secureUid=Read-Host '輸入你自己裝置的24位十六進位UID（不顯示、不儲存）' -AsSecureString
        $pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureUid)
        try{$uid=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer).Trim().ToUpperInvariant()}
        finally{[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer);$pointer=[IntPtr]::Zero}
        if($uid -cnotmatch '^[0-9A-F]{24}$'){throw 'stop'}
    }
    $stage='request'; $failure='request_failed'
    $handler=[Net.Http.HttpClientHandler]::new();$handler.AllowAutoRedirect=$false
    if($mock){$handler.UseProxy=$false}
    $client=[Net.Http.HttpClient]::new($handler)
    $client.Timeout=[TimeSpan]::FromSeconds(30)
    $cancel=[Threading.CancellationTokenSource]::new([TimeSpan]::FromSeconds(30))
    $uri=[uri]($endpoint.AbsoluteUri+'?Temp='+(Get-Random -Minimum 1 -Maximum 10000))
    $request=[Net.Http.HttpRequestMessage]::new([Net.Http.HttpMethod]::Post,$uri)
    $fields=[Collections.Generic.Dictionary[string,string]]::new()
    $fields.Add('action','GetFirmware');$fields.Add('f_UID',$uid)
    $fields.Add('f_FirmwareID',[string]$FirmwareId);$fields.Add('ver','30')
    $request.Content=[Net.Http.FormUrlEncodedContent]::new($fields)
    $uid=$null;$fields.Clear();$secureUid=$null
    # Exactly one attempt: no redirect, retry, enumeration, login or completion call.
    $attempts=1
    $response=$client.SendAsync($request,[Net.Http.HttpCompletionOption]::ResponseHeadersRead,$cancel.Token).GetAwaiter().GetResult()
    $status=[int]$response.StatusCode
    if($status -ne 200){$failure='http_status_'+$status;throw 'stop'}
    $stage='response';$failure='response_too_large'
    $limit=262144
    if($response.Content.Headers.ContentLength -gt $limit){throw 'stop'}
    $stream=$response.Content.ReadAsStreamAsync($cancel.Token).GetAwaiter().GetResult()
    $memory=[IO.MemoryStream]::new();$buffer=[byte[]]::new(8192)
    while(($n=$stream.ReadAsync($buffer,0,$buffer.Length,$cancel.Token).GetAwaiter().GetResult()) -gt 0){
        if($memory.Length+$n -gt $limit){throw 'stop'}
        $memory.Write($buffer,0,$n)
    }
    $raw=$memory.ToArray();$failure='invalid_response_utf8'
    $utf8=[Text.UTF8Encoding]::new($false,$true);$text=$utf8.GetString($raw)
    $stage='decode';$failure='invalid_terminal_marker';$marker='接收OK'
    $first=$text.IndexOf($marker,[StringComparison]::Ordinal)
    if($first -lt 0 -or $first -ne $text.Length-$marker.Length -or
        $text.IndexOf($marker,$first+1,[StringComparison]::Ordinal) -ge 0){throw 'stop'}
    $hex=$text.Substring(0,$first)
    if($hex.EndsWith("`r`n",[StringComparison]::Ordinal)){$hex=$hex.Substring(0,$hex.Length-2)}
    $rows=$hex.Split(@("`r`n"),[StringSplitOptions]::None)
    $failure='invalid_hex_page_count'
    if($rows.Count -lt 1 -or $rows.Count -gt 96){throw 'stop'}
    $encoded=[byte[]]::new($rows.Count*1024);$page=0;$failure='invalid_hex_page'
    foreach($row in $rows){
        if($row -cnotmatch '^[0-9A-Fa-f]{2048}$'){throw 'stop'}
        $part=[Convert]::FromHexString($row)
        [Array]::Copy($part,0,$encoded,$page*1024,1024);$page++
    }
    $decoded=[byte[]]::new($encoded.Length)
    for($i=0;$i -lt $encoded.Length;$i++){$decoded[$i]=$encoded[$i] -bxor 0xB7}
    $normalized=$utf8.GetBytes(($rows -join "`r`n")+"`r`n")
    # Persist only after strict HEX validation: arbitrary server messages are never logged.
    $stage='save';$failure='local_save_failed'
    $root=[IO.Path]::GetFullPath($OutputRoot)
    $folder=Join-Path $root ('ID-'+$FirmwareId+'-'+[guid]::NewGuid().ToString('N'))
    if([IO.Directory]::Exists($folder)){throw 'stop'}
    [IO.Directory]::CreateDirectory($folder) | Out-Null
    $basename='ID-'+$FirmwareId+$(if($label){'-'+$label}else{''})
    $outputs=@{
        'http-response.txt'=$raw
        'download.hex'=$normalized
        'server-encoded.dat'=$encoded
        ($basename+'-decoded.bin')=$decoded
    }
    $files=[ordered]@{}
    foreach($name in ($outputs.Keys | Sort-Object)){
        $path=Join-Path $folder $name
        $file=[IO.File]::Open($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
        try{$file.Write($outputs[$name],0,$outputs[$name].Length)}finally{$file.Dispose()}
        $readback=[IO.File]::ReadAllBytes($path)
        if((Digest $readback) -ne (Digest $outputs[$name])){throw 'stop'}
        $files[$name]=@{bytes=$readback.Length;sha256=(Digest $readback)}
    }
    $receipt=[ordered]@{
        schema='TSL-one-returned-FirmwareID-download-v1';status='downloaded_and_verified';FirmwareID=$FirmwareId
        server_catalog_version_label=$label;catalog_sha256=(Digest $catalogBytes)
        endpoint=$endpoint.AbsoluteUri;action='GetFirmware';client_ver=30;http_status=$status
        request_attempts=$attempts;retries=0;redirects_followed=0;mock=$mock;uid_stored=$false
        pages=$rows.Count;page_bytes=1024;decoding='hex pairs then byte XOR 0xB7, first-stage candidate only'
        files=$files;firmware_executed=$false;hardware_applicability_proved=$false;target_ready=$false;ota_verified=$false
    }
    $receiptBytes=$utf8.GetBytes(($receipt | ConvertTo-Json -Depth 8))
    $receiptFile=[IO.File]::Open((Join-Path $folder 'receipt.json'),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try{$receiptFile.Write($receiptBytes,0,$receiptBytes.Length)}finally{$receiptFile.Dispose()}
    [ordered]@{status='downloaded_and_verified';FirmwareID=$FirmwareId;directory=$folder;bin=(Join-Path $folder ($basename+'-decoded.bin'));bytes=$decoded.Length;sha256=(Digest $decoded);mock=$mock;target_ready=$false;ota_verified=$false} | ConvertTo-Json -Compress
    exit 0
}catch{
    # Do not stringify exceptions, request bodies or arbitrary server replies.
    if($_.Exception.GetBaseException() -is [OperationCanceledException]){$failure='timeout_or_cancelled'}
    $errorType=$_.Exception.GetBaseException().GetType().FullName
    $errorCode=$_.Exception.GetBaseException().HResult
    $socketError=$null;$nativeSocketError=$null
    if($_.Exception.GetBaseException() -is [Net.Sockets.SocketException]){
        $socketError=$_.Exception.GetBaseException().SocketErrorCode.ToString()
        $nativeSocketError=$_.Exception.GetBaseException().NativeErrorCode
    }
    [ordered]@{status='stopped';stage=$stage;reason=$failure;error_type=$errorType;error_code=$errorCode;socket_error=$socketError;native_socket_error=$nativeSocketError;http_status=$status;request_attempts=$attempts;retries=0} | ConvertTo-Json -Compress
    exit 1
}finally{
    if($pointer -ne [IntPtr]::Zero){[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)}
    $uid=$null;$secureUid=$null
    foreach($resource in @($stream,$memory,$response,$request,$cancel,$client,$handler)){
        if($null -ne $resource){$resource.Dispose()}
    }
}
