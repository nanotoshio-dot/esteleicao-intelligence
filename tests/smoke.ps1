param([switch]$Packaged)
$ErrorActionPreference = 'Stop'
$env:ESTELEICAO_NO_BROWSER = '1'
$env:ESTELEICAO_PORT = '18501'
$env:LOCALAPPDATA = Join-Path $env:TEMP ('esteleicao-smoke-' + [guid]::NewGuid())
$process = $null
try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback,18501)
    try { $listener.Start() } finally { $listener.Stop() }
    if ($Packaged) {
        $process = Start-Process -FilePath 'dist\ESTELEICAO\ESTELEICAO.exe' -WindowStyle Hidden -PassThru
    } else {
        $process = Start-Process -FilePath (Get-Command python).Source -ArgumentList 'launcher.py' -WindowStyle Hidden -PassThru
    }
    $ok = $false
    for ($i = 0; $i -lt 90; $i++) {
        Start-Sleep -Seconds 1
        if ($process.HasExited) { throw "Application exited: $($process.ExitCode)" }
        try {
            $response = Invoke-WebRequest 'http://127.0.0.1:18501/_stcore/health' -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) { $ok = $true; break }
        } catch { Write-Verbose "Waiting for local HTTP server: $_" }
    }
    if (-not $ok) { throw 'Streamlit health endpoint did not return HTTP 200' }
    Write-Host 'Streamlit runtime smoke test: HTTP 200'
} finally {
    if ($process -and -not $process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
    $log = Join-Path $env:LOCALAPPDATA 'ESTELEICAO\logs\startup.log'
    if (Test-Path $log) { Get-Content $log -Tail 40 }
}
