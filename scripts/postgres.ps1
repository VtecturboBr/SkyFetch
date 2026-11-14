param([ValidateSet('start', 'stop', 'status')][string]$Action = 'status')
$ErrorActionPreference = 'Stop'
$pgRoot = Join-Path $env:LOCALAPPDATA 'SkyFetch\PostgreSQL17'
$pgCtl = Join-Path $pgRoot 'pgsql\bin\pg_ctl.exe'
$pgData = Join-Path $pgRoot 'data'
if (!(Test-Path -LiteralPath (Join-Path $pgData 'PG_VERSION'))) {
    throw 'Cluster PostgreSQL local nao encontrado. Consulte docs/AMBIENTE_LOCAL.md.'
}
if ($Action -eq 'status') {
    & $pgCtl -D $pgData status
    if ($LASTEXITCODE -notin @(0, 3)) { throw 'Nao foi possivel consultar o PostgreSQL.' }
    return
}
if ($Action -eq 'start') {
    & $pgCtl -D $pgData status *> $null
    if ($LASTEXITCODE -eq 0) { Write-Host 'PostgreSQL ja esta em execucao.'; return }
    if ($LASTEXITCODE -ne 3) { throw 'Falha ao verificar o cluster local.' }
    $pgLog = Join-Path $pgRoot 'postgres.log'
    $pgProcess = Start-Process -FilePath $pgCtl -ArgumentList @(
        '-D', "`"$pgData`"", '-l', "`"$pgLog`"", '-w', '-t', '20', 'start'
    ) -WindowStyle Hidden -PassThru
    # WaitForExit aguarda somente pg_ctl; -Wait aguardaria tambem o servidor filho.
    if (!$pgProcess.WaitForExit(25000)) { throw 'Tempo esgotado ao iniciar PostgreSQL.' }
    if ($pgProcess.ExitCode -ne 0) { throw "Falha ao iniciar PostgreSQL. Consulte $pgLog" }
    Write-Host 'PostgreSQL iniciado em 127.0.0.1:5432.'
    return
}
& $pgCtl -D $pgData status *> $null
if ($LASTEXITCODE -eq 3) { Write-Host 'PostgreSQL ja esta parado.'; return }
if ($LASTEXITCODE -ne 0) { throw 'Falha ao verificar o cluster local.' }
& $pgCtl -D $pgData -w -t 20 stop -m fast
if ($LASTEXITCODE -ne 0) { throw 'Falha ao parar PostgreSQL.' }
