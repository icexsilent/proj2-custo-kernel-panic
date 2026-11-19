# setup_network_windows.ps1
# Configura o WSL 2 em modo Mirrored Networking e cria regras de Firewall no Windows
# para permitir trafego do distccd (portas 3632 e 3633) na rede local.
# Nota: Para abrir portas no Windows Firewall, execute este script como Administrador.

param(
    [switch]$ApplyWslConfig = $true,
    [switch]$ConfigureFirewall = $false,
    [switch]$SetupPortProxy = $false
)

$wslConfigPath = "$env:USERPROFILE\.wslconfig"

if ($ApplyWslConfig) {
    Write-Host "[1/3] Verificando configuracao $wslConfigPath..." -ForegroundColor Cyan
    $content = @"
[wsl2]
networkingMode=mirrored
firewall=true
autoProxy=true
"@
    if (-not (Test-Path $wslConfigPath)) {
        Set-Content -Path $wslConfigPath -Value $content -Encoding UTF8
        Write-Host "  -> Arquivo .wslconfig criado com networkingMode=mirrored." -ForegroundColor Green
        Write-Host "  -> Para aplicar a mudanca de rede entre maquinas fisicas, rode: wsl --shutdown" -ForegroundColor Yellow
    } else {
        Write-Host "  -> Arquivo .wslconfig ja existe. Conteudo atual:" -ForegroundColor Yellow
        Get-Content $wslConfigPath
    }
}

if ($ConfigureFirewall) {
    Write-Host "[2/3] Configurando regras de Firewall do Windows (Portas TCP 3632 e 3633)..." -ForegroundColor Cyan
    New-NetFirewallRule -DisplayName "distccd (WSL2) - TCP 3632-3633" `
        -Direction Inbound -Action Allow -Protocol TCP -LocalPort 3632,3633 `
        -Profile Private,Domain -ErrorAction SilentlyContinue
    Write-Host "  -> Regra de firewall configurada." -ForegroundColor Green
}

if ($SetupPortProxy) {
    Write-Host "[3/3] Configurando Port Forwarding (Fallback caso nao use Mirrored Mode)..." -ForegroundColor Cyan
    $wslIp = (wsl -d Ubuntu -- hostname -I).Trim().Split(" ")[0]
    Write-Host "  -> IP interno do WSL2 detectado: $wslIp"
    netsh interface portproxy add v4tov4 listenport=3632 listenaddress=0.0.0.0 connectport=3632 connectaddress=$wslIp
    netsh interface portproxy show all
}
