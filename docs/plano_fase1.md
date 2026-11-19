# Planejamento do Projeto: Experimentos com `distcc` no WSL 2

## Diagnóstico Inicial da Máquina Local
- **Processador:** AMD Ryzen 7 5700X3D (8 núcleos / 16 threads)
- **RAM no WSL 2:** 15 GiB disponíveis
- **Sistema WSL 2:** Ubuntu (Kernel `6.18.58.1-microsoft-standard-WSL2`)
- **Rede atual do WSL 2:** NAT (`172.27.160.82/20` na `eth0`), sem `.wslconfig` configurado.
- **Ferramentas já presentes:** `python3`, `bc`, `tc` (`iproute2`).
- **Ferramentas pendentes de instalação:** `build-essential` (`gcc`, `make`), `distcc`, `stress-ng`, dependências de build do Kernel Linux (`flex`, `bison`, `libelf-dev`, `libssl-dev`) e do SQLite (`tcl`).

---

## Visão Geral das 4 Fases

```mermaid
flowchart LR
    F1["Fase 1: Ambiente WSL2, Rede e distcc"] --> T1["Teste 1: Compilação C distribuída via distccd"]
    T1 --> F2["Fase 2: Scripts de Benchmark, Rede (tc) e Stress"]
    F2 --> T2["Teste 2: Coleta CSV + Parse de Logs + tc/stress"]
    T2 --> F3["Fase 3: Scripts Python de Gráficos"]
    F3 --> T3["Teste 3: Geração de todos os gráficos"]
    T3 --> F4["Fase 4: SQLite (fonte completo) e Kernel Linux"]
    F4 --> T4["Teste 4: Build real solo vs. distcc"]
```

> [!IMPORTANT]
> Conforme solicitado, **cada fase terá seu planejamento apresentado antes do início** e será **integralmente testada e validada** antes de avançarmos para a próxima.

---

## Planejamento Detalhado — Fase 1: Configuração do Ambiente WSL 2 e `distcc`

### Objetivo da Fase 1
Preparar o WSL 2 para compilar projetos C/C++ com `distcc`, configurar a rede para que o ambiente funcione tanto **localmente (simulando múltiplos nós na mesma máquina)** quanto **em rede local (pronto para receber ou enviar jobs para uma 2ª máquina Windows ou Linux)**, e validar o funcionamento completo do cliente + daemon `distccd`.

### Etapas de Execução da Fase 1

1. **Estrutura de Diretórios:**
   - Criar em `e:\Faculdade\SistemasOperacionais` a estrutura organizada do projeto (scripts, configs, resultados, gráficos e guia de conexão para a 2ª máquina).
   - Criar dentro do filesystem nativo do WSL (`~/distcc_lab`) o diretório de compilação e builds para evitar o gargalo de I/O do `/mnt/e`.

2. **Instalação de Pacotes e Dependências no Ubuntu (WSL 2):**
   - Instalar compiladores e ferramentas de base: `gcc`, `g++`, `make`, `distcc`, `stress-ng`, `linux-tools-generic` / `iproute2` (para `tc`/`netem`), além das bibliotecas exigidas pelo SQLite e Kernel Linux (`flex`, `bison`, `libelf-dev`, `libssl-dev`, `tcl`, `bc`, `git`, `curl`, `xz-utils`).
   - Verificar se `ccache` está instalado/ativo e garantir que esteja desativado para não interferir nos experimentos.

3. **Configuração de Rede do WSL 2 (Preparação para 1 e N máquinas):**
   - Configurar `~/.wslconfig` no Windows com `networkingMode=mirrored` (e `firewall=true` / `autoProxy=true`), permitindo que o WSL 2 compartilhe o IP da placa de rede do Windows na LAN (essencial para quando a 2ª máquina entrar nos testes).
   - Criar um script auxiliar PowerShell (`setup_network_windows.ps1`) para abrir a porta `3632/TCP` (e portas de simulação `3633/TCP`) no Firewall do Windows e, caso necessário como fallback ao modo mirrored, configurar `netsh interface portproxy`.

4. **Configuração de Daemons `distccd` (Modo Real + Simulação Multi-Nó Local):**
   - Criar um script de gerenciamento (`manage_distccd.sh`) capaz de subir:
     - **Nó 1 (Porta 3632):** Daemon padrão `distccd` escutando na rede local e localhost, gravando log detalhado em `/tmp/distccd_node1.log`.
     - **Nó 2 Simulado (Porta 3633):** Um segundo daemon `distccd` na porta `3633` com log separado (`/tmp/distccd_node2.log`), permitindo testar **nesta única máquina** a distribuição entre múltiplos "servidores" (`127.0.0.1:3632` e `127.0.0.1:3633`) e validar a contagem de arquivos por host antes mesmo de conectar o segundo PC físico.

### Plano de Testes da Fase 1 (Critérios de Aceite)
Antes de iniciar a Fase 2, executaremos os seguintes testes automatizados:
1. **Verificação de versões e binários:** Confirmar `gcc --version`, `distcc --version`, `stress-ng --version` e suporte a `tc`.
2. **Teste dos Daemons (`distccd`):** Iniciar os daemons nas portas `3632` e `3633` e verificar se estão escutando (`ss -tlnp`).
3. **Teste de Compilação Distribuída e Logs:** Criar um mini-projeto de teste em C com 8 arquivos `.c` independentes em `~/distcc_lab/test_hello`, compilar com `make -j4 CC="distcc gcc"` distribuindo entre `127.0.0.1:3632/2` e `127.0.0.1:3633/2`, e verificar:
   - Se o binário final é gerado e executa corretamente;
   - Se os arquivos `/tmp/distcc-client.log`, `/tmp/distccd_node1.log` e `/tmp/distccd_node2.log` registram exatamente os arquivos `.c` compilados por cada instância.
4. **Teste de `tc` (Traffic Control) no WSL 2:** Testar a adição e remoção de uma regra `tc qdisc` na interface do WSL 2 para saber desde já se o kernel atual do WSL 2 suporta `tbf`/`netem` nativamente na interface `lo`/`eth0`.
