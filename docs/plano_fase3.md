# Planejamento Detalhado — Fase 3: Scripts em Python para Geração dos Gráficos

## Objetivo da Fase 3
Desenvolver o script [`generate_plots.py`](file:///e:/Faculdade/SistemasOperacionais/scripts/generate_plots.py) utilizando `pandas`, `numpy` e `matplotlib` para processar automaticamente os arquivos CSV em `e:\Faculdade\SistemasOperacionais\results\` e gerar todos os gráficos exigidos na **Seção 6 (Resumo dos gráficos)** do roteiro, com média, desvio padrão (barras de erro), anotações de destaque e alta resolução (`300 DPI`).

## Lista de Gráficos a Serem Gerados em `e:\Faculdade\SistemasOperacionais\plots\`

| Arquivo PNG | Pergunta do Roteiro | Tipo de Gráfico | Detalhes Visuais e Métricas |
|---|---|---|---|
| `01_individual_vs_coletivo.png` | **Pergunta 1:** Quão díspares são os tempos individuais vs. coletivo? | Barras com barras de erro (`±1 DP`) | Colunas para cada máquina individual + coluna para o cluster coletivo, com anotação de redução percentual de tempo. |
| `02_percentual_por_maquina.png` | **Pergunta 2:** Qual o percentual de compilação que cada máquina contribui? | Setores (Pizza / Donut) | Fatias proporcionais à média de arquivos `.c` compilados por cada servidor `distccd` no build coletivo. |
| `03_kernel_vs_sqlite.png` | **Pergunta 3:** Entre Kernel Linux e SQLite, a redução é significativa? | Barras agrupadas com barras de erro | Agrupado por projeto (`SQLite` vs. `Kernel Linux`), comparando `Solo` vs. `Distribuído` e destacando o *speedup* de cada um. |
| `04_velocidade_rede.png` | **Pergunta 4:** Quanto a velocidade de rede afeta? Em que ponto deixa de ser gargalo? | Linhas (Eixo X em escala logarítmica) | Banda (`1` a `1000 Mbit/s`) × Tempo de build, com marcação automática do **"joelho" da curva** (ponto onde a rede deixa de ser gargalo). |
| `05a_escala_maquinas.png` | **Pergunta 5A:** Número de máquinas × tempo, Speedup e Eficiência | Painel duplo de linhas | Subgráfico 1: Nº de máquinas (`1..4`) × Tempo (s). Subgráfico 2: *Speedup* medido vs. *Speedup* ideal linear e Lei de Amdahl + Eficiência ($S_n/n$). |
| `05b_processos_fundo.png` | **Pergunta 5B:** Processos de fundo competindo (`stress-ng`) | Barras + linha de tendência | Carga de CPU concorrente (`0%, 25%, 50%, 100%`) × Tempo de compilação (s) com barras de erro. |
| `05c_arquivos_vs_speedup.png` | **Pergunta 5C:** Nº de arquivos `.c` × paralelização | Linhas com marcadores | Quantidade de arquivos `.c` × *Speedup* ($T_{\text{solo}} / T_{\text{dist}}$), com linha de referência em `Speedup = 1.0x` (limiar onde distribuir compensa). |
| `06_energia_wh_edp.png` | **Pergunta 6:** Energia: 1 máquina potente vs. várias em paralelo | Painel duplo de linhas | Subgráfico 1: Tamanho da carga × Energia total (`Wh`). Subgráfico 2: Tamanho da carga × `EDP (Wh × s)`, marcando o **ponto de cruzamento (virada)** onde a compilação distribuída passa a compensar. |

## Plano de Testes da Fase 3 (Critérios de Aceite)
1. Executar `python3 scripts/generate_plots.py` sobre os CSVs reais gerados no teste da Fase 2.
2. Verificar se todos os 8 arquivos `.png` foram criados em `e:\Faculdade\SistemasOperacionais\plots\` com tamanho válido (`> 20 KB` cada) e sem erros de renderização.
3. Inspecionar visualmente amostras dos gráficos gerados para confirmar legibilidade, rótulos em português, legendas e barras de erro.
