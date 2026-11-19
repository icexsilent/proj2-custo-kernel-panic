# Guia para Conectar a 2ª Máquina Física (Windows + WSL2 ou Linux Nativo)

Quando você for realizar os testes com uma segunda máquina física na mesma rede local (LAN), siga este checklist rápido:

## 1. Compatibilidade de Compilador (`gcc`)
- Nesta máquina principal (Cliente), a versão instalada no Ubuntu (WSL 2) é o **`gcc 15.2.0`** (`Ubuntu 26.04`).
- Na segunda máquina (Servidor `distccd`), instale a **mesma versão principal do `gcc`** (ou instale a versão correspondente lado a lado, ex.: `sudo apt install gcc-15` ou `gcc-14` em ambas as máquinas e chame `CC="distcc gcc-14"`).
- Confirme com `gcc --version` nas duas máquinas antes de iniciar a bateria de testes.

## 2. Configuração de Rede no Windows + WSL 2
Se a máquina (Cliente ou Servidor) estiver rodando Windows 11 + WSL 2:
1. O arquivo `C:\Users\<usuario>\.wslconfig` já foi preparado pelo script [`setup_network_windows.ps1`](file:///e:/Faculdade/SistemasOperacionais/scripts/setup_network_windows.ps1) com:
   ```ini
   [wsl2]
   networkingMode=mirrored
   firewall=true
   autoProxy=true
   ```
2. Reinicie o WSL no PowerShell:
   ```powershell
   wsl --shutdown
   ```
3. Abra o PowerShell **como Administrador** na máquina que rodará o `distccd` e libere a porta `3632`:
   ```powershell
   powershell -ExecutionPolicy Bypass -File e:\Faculdade\SistemasOperacionais\scripts\setup_network_windows.ps1 -ConfigureFirewall
   ```

## 3. Subindo o `distccd` na 2ª Máquina (Servidor)
Na segunda máquina (Linux nativo ou WSL 2), descubra a faixa de IP da sua rede local (ex.: `192.168.0.0/24` ou `192.168.1.0/24`) com `ip -4 addr` e inicie o daemon:
```bash
sudo apt update && sudo apt install -y build-essential distcc stress-ng
distccd --daemon --port 3632 --listen 0.0.0.0 --jobs $(nproc) \
  --allow 127.0.0.0/8 --allow 192.168.0.0/16 --allow 10.0.0.0/8 \
  --log-file /tmp/distccd_server.log --verbose
```

## 4. Testando a Conexão a partir do Cliente
Na máquina Cliente (esta máquina), teste se a porta `3632` da segunda máquina (`IP_DA_MAQUINA_2`) está acessível:
```bash
nc -zv IP_DA_MAQUINA_2 3632
```
Em seguida, basta passar o IP nos scripts de benchmark:
```bash
export DISTCC_HOSTS="localhost/8 IP_DA_MAQUINA_2/8"
```
