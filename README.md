# Projeto 2 de Sistemas Operacionais — Custo da Compilação Distribuída com `distcc` (WSL 2)

**Grupo:** Kernel Panic (`KPE-V7L` · Turma 4P — 2026.2 · Prof. Lucas Figueiredo)  
**Integrantes:** Gabriel Coelho · Caroline Lee · Vinicius Rampazi de Oliveira (RA 10426499) · Caio Belom · Fernando Paiva

Este repositório contém o **Relatório Final em PDF** ([`Relatorio_Projeto2_Kernel_Panic.pdf`](Relatorio_Projeto2_Kernel_Panic.pdf)), a página interativa do **Gráfico do Grupo** ([`grafico_grupo.html`](grafico_grupo.html)), os **dados brutos coletados** ([`dados/`](dados/)) e toda a infraestrutura de scripts, configurações de rede, automação de benchmarks e geração de gráficos para avaliar o **`distcc`** no Windows 11 + WSL 2 (Ubuntu 26.04 LTS, AMD Ryzen 7 5700X3D).

---

## Estrutura do Projeto

```text
e:\Faculdade\SistemasOperacionais\
├── Relatorio_Projeto2_Kernel_Panic.pdf  # Relatório final em PDF (9 seções da Ficha 4, 8 páginas)
├── Relatorio_Experimentos_distcc.pdf    # Cópia do relatório final em PDF
├── grafico_grupo.html                   # Gráfico interativo do grupo (HTML único com todas as condições e rodadas)
├── dados/                               # Dados brutos coletados nos experimentos (CSVs)
│   ├── hardware_specs.csv
│   ├── tempos_compilacao.csv
│   ├── distribuicao_hosts.csv
│   └── energia_estimada.csv
├── configs/
├── docs/
│   ├── relatorio_projeto2.html          # Código-fonte HTML do relatório em PDF
│   ├── grafico_grupo.html               # Cópia da página HTML do gráfico do grupo
│   ├── relatorio_experimentos.md        # Resumo analítico das 6 questões experimentais
│   └── guia_segunda_maquina.md          # Passo a passo para conectar um 2º PC (Windows/WSL2 ou Linux)
├── plots/                               # Gráficos gerados em alta resolução (300 DPI)
│   ├── 01_individual_vs_coletivo.png
│   ├── 02_percentual_por_maquina.png
│   ├── 03_kernel_vs_sqlite.png
│   ├── 04_velocidade_rede.png
│   ├── 05a_escala_maquinas.png
│   ├── 05b_processos_fundo.png
│   ├── 05c_arquivos_vs_speedup.png
│   └── 06_energia_wh_edp.png
├── results/                             # Cópia espelhada dos CSVs brutos gerados pelos scripts
└── scripts/
    ├── setup_network_windows.ps1        # Configura .wslconfig (mirrored), Firewall e PortProxy
    ├── manage_distccd.sh                # Inicia/para até 4 daemons distccd (portas 3632..3635)
    ├── setup_projects.sh                # Baixa e prepara SQLite 3.47.2 (103 .c) e Kernel Linux 6.6.72
    ├── bench_core.sh                    # Motor de coleta (warm-up + N repetições + logs)
    ├── parse_distcc_logs.py             # Contabiliza arquivos .c compilados por servidor
    ├── calc_energy.py                   # Calcula consumo em mWh/Wh e EDP (Energia × Tempo)
    ├── run_experiments.sh               # Orquestrador das 6 perguntas do roteiro (inclui veth + tc tbf)
    ├── generate_plots.py                # Gera todos os 8 gráficos com pandas/matplotlib
    └── test_fase1.sh                    # Teste automatizado da Fase 1
```

---

## Como Executar

### 1. Gerenciar os Daemons `distccd`
Dentro do WSL 2 (`wsl -d Ubuntu -u root`):
```bash
/mnt/e/Faculdade/SistemasOperacionais/scripts/manage_distccd.sh start 192.168.0.0/16 4 4
```

### 2. Preparar os Projetos Reais (SQLite Fonte Completo e Kernel Linux)
Os códigos-fonte são extraídos e compilados em `~/distcc_lab/` (sistema de arquivos `ext4` nativo do WSL 2) para evitar lentidão de I/O em `/mnt/`:
```bash
/mnt/e/Faculdade/SistemasOperacionais/scripts/setup_projects.sh tiny
```
> Para usar `defconfig` completo no Kernel Linux em vez do perfil enxuto, passe `defconfig` como argumento.

### 3. Rodar os Experimentos (Perguntas 1 a 6)
```bash
# Rodar todos os experimentos com 3 repetições cada (+1 rodada de warm-up descartada):
/mnt/e/Faculdade/SistemasOperacionais/scripts/run_experiments.sh all 3

# Ou rodar um experimento específico:
/mnt/e/Faculdade/SistemasOperacionais/scripts/run_experiments.sh exp3 3
```

> **Usando uma 2ª máquina física na rede:** defina os IPs antes de chamar o script:
> ```bash
> export NODE1_HOST="192.168.0.10:3632"
> export NODE2_HOST="192.168.0.11:3632"
> export NET_IFACE="eth0"
> /mnt/e/Faculdade/SistemasOperacionais/scripts/run_experiments.sh all 3
> ```

### 4. Gerar os Gráficos
```bash
python3 /mnt/e/Faculdade/SistemasOperacionais/scripts/generate_plots.py
```
