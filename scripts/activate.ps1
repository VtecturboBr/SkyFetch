# Execute com dot-source: . .\scripts\activate.ps1
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$venvActivate = Join-Path $projectRoot '.venv\Scripts\Activate.ps1'
$localEnv = Join-Path $projectRoot '.env'
if (!(Test-Path -LiteralPath $venvActivate)) { throw 'Ambiente .venv nao encontrado.' }
if (!(Test-Path -LiteralPath $localEnv)) { throw 'Arquivo .env local nao encontrado. Consulte docs/AMBIENTE_LOCAL.md.' }
$connections = @{}
foreach ($envLine in Get-Content -LiteralPath $localEnv) {
    if ($envLine -match '^\s*(#|$)') { continue }
    if ($envLine -notmatch '^(DATABASE_URL|SETUP_DATABASE_URL|TEST_DATABASE_URL)=(.+)$') {
        throw 'Formato inesperado no arquivo .env; valores nao foram exibidos.'
    }
    $connections[$Matches[1]] = $Matches[2]
}
foreach ($connectionName in @('DATABASE_URL', 'SETUP_DATABASE_URL', 'TEST_DATABASE_URL')) {
    if (!$connections.ContainsKey($connectionName)) { throw "Falta $connectionName no .env." }
}
. $venvActivate
foreach ($connectionName in $connections.Keys) {
    [Environment]::SetEnvironmentVariable($connectionName, $connections[$connectionName], 'Process')
}
$pgBin = Join-Path $env:LOCALAPPDATA 'SkyFetch\PostgreSQL17\pgsql\bin'
if (($env:Path -split ';') -notcontains $pgBin) { $env:Path = "$pgBin;$env:Path" }
Write-Host 'Python virtual e conexoes locais carregados; credenciais nao exibidas.'
