function Get-ModelBuildInputHashes {
    param([string]$ModelRoot,[string[]]$Sources)
    $modelHashes=[ordered]@{}
    foreach($modelSource in $Sources){$modelHashes[$modelSource]=(Get-FileHash -LiteralPath (Join-Path $ModelRoot $modelSource) -Algorithm SHA256).Hash.ToLowerInvariant()}
    return $modelHashes
}
function Write-ModelBuildEvidence {
    param([string]$ModelRoot,[string]$Compiler,[string]$Executable,[string]$Mode,[string[]]$Sources,[System.Collections.IDictionary]$Before)
    $modelHashes=Get-ModelBuildInputHashes -ModelRoot $ModelRoot -Sources $Sources
    if($Before){
        if($Before.Count -ne $modelHashes.Count){throw 'Compile input manifest changed'}
        foreach($modelSource in $modelHashes.Keys){if($Before[$modelSource] -ne $modelHashes[$modelSource]){throw ('Source changed during compilation: '+$modelSource)}}
    }
    $modelEvidence=[ordered]@{mode=$Mode;executable=$Executable;executable_sha256=(Get-FileHash -LiteralPath $Executable -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$Compiler;compiler_sha256=(Get-FileHash -LiteralPath $Compiler -Algorithm SHA256).Hash.ToLowerInvariant();sources=$modelHashes;original_executed=$false;hardware=$false}
    if($Before){$modelEvidence['sources_before_compile']=$Before}
    Write-Output ('MODEL_BUILD '+($modelEvidence | ConvertTo-Json -Depth 6 -Compress))
}
