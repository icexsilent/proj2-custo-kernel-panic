# Relatório da Fase 1 e Planejamento da Fase 2

## Resultado dos Testes da Fase 1 (Concluída com Sucesso)
- **Ferramentas instaladas e validadas:** `gcc 15.2.0`, `distcc 3.4`, `stress-ng 0.20.01`, `pandas 2.3.3`, `matplotlib 3.10.7`, `numpy 2.3.5` (e `ccache` ausente para não viciar medições).
- **Daemons `distccd`:** Configurados via [`manage_distccd.sh`](file:///e:/Faculdade/SistemasOperacionais/scripts/manage_distccd.sh) nas portas `3632` (Node 1) e `3633` (Node 2 simulado).
- **Teste de Compilação Distribuída (`test_hello` com 9 arquivos `.c`):**
  - `127.0.0.1:3632` compilou **5 arquivos**;
  - `127.0.0.1:3633` compilou **4 arquivos**;
  - Linkagem final e execução do binário concluídas sem erros.
- **Traffic Control (`tc`) no WSL 2:** Testado e aprovado tanto na interface `eth0` (para 2+ máquinas físicas) quanto na interface `lo` (permitindo simular gargalo de rede mesmo em 1 máquina só!).

---

## Planejamento Detalhado — Fase 2: Scripts Automatizados de Benchmark

### Objetivo da Fase 2
Construir uma suíte modular de scripts em `e:\Faculdade\SistemasOperacionais\scripts\` que automatize **todas as 6 perguntas do roteiro**, gerando arquivos CSV padronizados em `e:\Faculdade\SistemasOperacionais\results\` prontos para os gráficos da Fase 3.

### Arquitetura dos Scripts a Serem Criados

1. **[`bench_core.sh`](file:///e:/Faculdade/SistemasOperacionais/scripts/bench_core.sh) — Motor Base de Coleta:**
   - Recebe: `<experimento>`, `<projeto>`, `<rotulo>`, `<modo: solo|distcc>`, `<hosts>`, `<jobs>`, `<repeticoes>`, `<warmup: 0|1>`, `<extra_col>`.
   - Executa 1 rodada de *warm-up* descartada (para aquecer cache de página do disco, conforme Seção 3 do roteiro).
   - Em cada repetição `1..REPS`:
     - Executa `make clean`, limpa `/tmp/distcc-client.log` e zera os logs dos daemons;
     - Mede o tempo de parede em segundos com precisão de milissegundos (`date +%s.%N`);
     - Registra no CSV principal (`results/tempos_compilacao.csv`):
       `experimento,projeto,rotulo,modo,hosts,jobs,extra,repeticao,tempo_s,arquivos_total`
     - Extrai automaticamente do `/tmp/distcc-client.log` quantos arquivos `.c` cada host compilou naquela rodada e salva em `results/distribuicao_hosts.csv`:
       `experimento,projeto,rotulo,repeticao,host,arquivos_compilados,percentual`

2. **[`parse_distcc_logs.py`](file:///e:/Faculdade/SistemasOperacionais/scripts/parse_distcc_logs.py) — Analisador de Logs do Cliente e Servidores:**
   - Script Python chamado automaticamente após cada build distribuído para contabilizar com exatidão as compilações concluídas (`compile ... on <host> completed ok`) no cliente e cruzar com os logs dos daemons (`/tmp/distccd_node*.log`).

3. **[`run_experiments.sh`](file:///e:/Faculdade/SistemasOperacionais/scripts/run_experiments.sh) — Orquestrador das 6 Perguntas do Roteiro:**
   Permite rodar todos os experimentos de uma vez (`./run_experiments.sh all`) ou individualmente por pergunta:
   - **`exp1_individual_vs_coletivo`**: Mede cada nó isoladamente (`Node1`, `Node2`) vs. `Coletivo (Node1 + Node2)` e registra a contribuição percentual de cada máquina (Perguntas 1 e 2).
   - **`exp3_projetos`**: Compara **Solo (`make -jN`) vs. Distribuído (`distcc`)** em dois projetos distintos (ex.: SQLite vs. Kernel Linux, ou perfis configuráveis) (Pergunta 3).
   - **`exp4_rede`**: Usa `tc qdisc add dev <iface> root tbf rate <X>mbit ...` variando a banda em `1, 5, 10, 50, 100, 500, 1000` Mbit/s (funciona tanto em `lo` para 1 máquina quanto em `eth0` para 2+ máquinas) e garante remoção do `qdisc` via `trap` mesmo se interrompido (Pergunta 4).
   - **`exp5_adicionais`**:
     - *Escala de máquinas (`exp5a_escala`)*: 1, 2, 3, 4 nós (`distccd` em portas `3632..3635` ou IPs reais) calculando *Speedup* e *Eficiência*;
     - *Processos de fundo (`exp5b_stress`)*: dispara `stress-ng --cpu <K>` correspondendo a `0%, 25%, 50%, 100%` dos núcleos lógicos durante a compilação;
     - *Nº de arquivos `.c` × paralelização (`exp5c_num_arquivos`)*: gera/compila cargas controladas com `10, 25, 50, 100, 200` arquivos `.c` independentes para medir o *speedup* em função do tamanho do projeto.
   - **`exp6_energia`**: Calcula e exporta para `results/energia_estimada.csv` o consumo em **Wh** e **EDP (Energy-Delay Product = Wh × s)** combinando potência base (*idle*) + TDP escalado pela carga × tempo medido para 1 máquina potente vs. N máquinas em paralelo, além da curva de cruzamento (ponto em que distribuir passa a compensar energeticamente).

### Plano de Testes da Fase 2 (Critérios de Aceite)
Antes de avançar para a Fase 3, vamos:
1. Criar um projeto sintético de validação rápida (`~/distcc_lab/ synthetic_bench` com 32 arquivos `.c`) para testar todos os módulos do [`run_experiments.sh`](file:///e:/Faculdade/SistemasOperacionais/scripts/run_experiments.sh) sem precisar esperar horas.
2. Executar um *dry-run / smoke test* real de **todos os 6 experimentos** (com `REPS=2` no projeto sintético) verificando:
   - Se o `tc` aplica e remove corretamente os limites de banda em `lo`;
   - Se o `stress-ng` inicia e encerra sem deixar processos órfãos;
   - Se os arquivos CSV (`tempos_compilacao.csv`, `distribuicao_hosts.csv`, `energia_estimada.csv`, `hardware_specs.csv`) são gerados com dados reais e sem linhas corrompidas.
