param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Script = Join-Path $Root "reels_batch_downloader.py"

if (-not (Test-Path $Script)) {
    Write-Error "Unable to find reels_batch_downloader.py next to the scripts directory."
    exit 1
}

py -3 $Script @ScriptArgs
