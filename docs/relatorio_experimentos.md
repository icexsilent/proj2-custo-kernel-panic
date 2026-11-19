# Relatório de Experimentos — Compilação Distribuída com `distcc` no WSL 2

## 1. Especificações do Ambiente de Teste

| Máquina / Nó | Papel | Processador | Núcleos / Threads | RAM WSL 2 | Sistema / Kernel | Compilador | Potência Estimada (Idle / Carga) |
|---|---|---|---|---|---|---|---|
| **Máquina Principal (WSL 2)** | Cliente (`make`) + Daemons Locais | AMD Ryzen 7 5700X3D | 8C / 16T | 15 GiB | Ubuntu 26.04 (`6.18.58.1-microsoft-standard-WSL2`) | `gcc 15.2.0` (`distcc 3.4`) | `45 W` (Idle) / `150 W` (Carga máx.) |
| **Workers `distccd` (`3632..3635` / `veth`)** | Servidores de Compilação | Isolados por slots `/N` e `ip netns` (`veth`) | 2 a 4 threads/nó | Compartilhada | `distccd` TCP + `sch_tbf` | `gcc 15.2.0` | `45 W` (Idle) + `85 W` (Carga média/nó) |

---

## 2. Galeria dos 8 Gráficos Gerados

````carousel
![Pergunta 1: Tempo Individual vs. Coletivo](C:/Users/vinic/.gemini/antigravity/brain/b4ad46d1-efa6-4ef9-ab33-62a11f79def7/01_individual_vs_coletivo.png)
<!-- slide -->
![Pergunta 2: Percentual de Compilação por Máquina](C:/Users/vinic/.gemini/antigravity/brain/b4ad46d1-efa6-4ef9-ab33-62a11f79def7/02_percentual_por_maquina.png)
<!-- slide -->
![Pergunta 3: SQLite (Fonte Completo) vs. Kernel Linux](C:/Users/vinic/.gemini/antigravity/brain/b4ad46d1-efa6-4ef9-ab33-62a11f79def7/03_kernel_vs_sqlite.png)
<!-- slide -->
![Pergunta 4: Velocidade de Rede × Tempo de Build](C:/Users/vinic/.gemini/antigravity/brain/b4ad46d1-efa6-4ef9-ab33-62a11f79def7/04_velocidade_rede.png)
<!-- slide -->
![Pergunta 5A: Escalabilidade Horizontal e Lei de Amdahl](C:/Users/vinic/.gemini/antigravity/brain/b4ad46d1-efa6-4ef9-ab33-62a11f79def7/05a_escala_maquinas.png)
<!-- slide -->
![Pergunta 5B: Impacto de Processos de Fundo (stress-ng)](C:/Users/vinic/.gemini/antigravity/brain/b4ad46d1-efa6-4ef9-ab33-62a11f79def7/05b_processos_fundo.png)
<!-- slide -->
![Pergunta 5C: Nº de Arquivos .c × Speedup](C:/Users/vinic/.gemini/antigravity/brain/b4ad46d1-efa6-4ef9-ab33-62a11f79def7/05c_arquivos_vs_speedup.png)
<!-- slide -->
![Pergunta 6: Energia Total (mWh) e EDP (Energia × Tempo)](C:/Users/vinic/.gemini/antigravity/brain/b4ad46d1-efa6-4ef9-ab33-62a11f79def7/06_energia_wh_edp.png)
````

---

## 3. Análise das 6 Perguntas do Roteiro

### Pergunta 1 e 2: Tempo Individual vs. Coletivo e Contribuição Percentual
- **Tempos medidos:**
  - **Máquina 1 Individual (`-j4`):** `1.24s ± 0.00s`
  - **Máquina 2 Individual (`-j4`):** `1.21s ± 0.04s`
  - **Coletivo (Máq. 1 + Máq. 2, `-j8`):** `0.80s ± 0.00s` (**Redução de 35.5%**, *Speedup* de **1.55x**).
- **Divisão de trabalho (Pergunta 2):** A análise do `/tmp/distcc-client.log` via [`parse_distcc_logs.py`](file:///e:/Faculdade/SistemasOperacionais/scripts/parse_distcc_logs.py) mostrou divisão simétrica de **50.0% (9 arquivos)** para o Nó 1 (`127.0.0.1:3632`) e **50.0% (9 arquivos)** para o Nó 2 (`127.0.0.1:3633`), pois ambos os nós têm o mesmo limite de slots (`/4`) e mesma capacidade de CPU.

### Pergunta 3: Entre Kernel Linux e SQLite, a redução é significativa?
- **SQLite 3.47.2 (Código-fonte canônico separado — `USE_AMALGAMATION=0`, 103 arquivos `.c`):**
  - **Solo (`-j2`):** `14.24s ± 0.01s`
  - **Distribuído (`distcc -j12`):** `6.72s ± 0.09s` (**Speedup de 2.12x**, redução de **52.9%**).
  - *Por que o SQLite escala menos que o Kernel?* Mesmo separando os 103 arquivos `.c`, arquivos monolíticos grandes como `shell.c`, `vdbe.c` e `btree.c` dominam a cauda da compilação, além da linkagem final sequencial do binário `sqlite3`.
- **Kernel Linux 6.6.72 (`vmlinux` — 904 objetos compilados):**
  - **Solo (`-j2`):** `171.31s ± 3.05s`
  - **Distribuído (`distcc -j12`):** `61.20s ± 6.25s` (**Speedup de 2.80x**, redução de **64.3%** — economia de **110 segundos** por compilação).

### Pergunta 4: Quanto a velocidade de rede afeta? Em que ponto deixa de ser gargalo?
> [!TIP]
> **Descoberta técnica importante no WSL 2:** No kernel Linux 6.x do WSL 2, a interface de loopback (`lo`) ignora a fila `qdisc` para pacotes TCP locais. Para modelar com fidelidade absoluta a limitação de banda em uma única máquina, o script [`run_experiments.sh`](file:///e:/Faculdade/SistemasOperacionais/scripts/run_experiments.sh) cria automaticamente um **par Ethernet virtual (`veth_host <-> veth_ns`) isolado em um Network Namespace (`ip netns`)** e aplica `tc qdisc add ... root tbf` nos dois sentidos.

- **Resultados medidos (`1` a `1000 Mbit/s`):**
  - `1 Mbit/s`: `19.24s ± 0.01s` (forte gargalo no envio dos `.i` pré-processados)
  - `5 Mbit/s`: `4.12s ± 0.00s`
  - `10 Mbit/s`: `2.25s ± 0.02s`
  - `50 Mbit/s`: `0.80s ± 0.03s` (**Joelho da curva**)
  - `100 Mbit/s`: `0.61s ± 0.05s`
  - `500 Mbit/s`: `0.45s ± 0.03s`
  - `1000 Mbit/s`: `0.45s ± 0.01s`
- **Conclusão:** A partir de **~50 a 100 Mbit/s** (Fast Ethernet / Wi-Fi moderno), a curva achata ("joelho") e o tempo de compilação passa a ser limitado pelo processador e pré-processador local, e não mais pela rede.

### Pergunta 5: Experimentos Adicionais
- **5A — Escala de máquinas (`1` a `4` servidores):**
  - `1 nó`: `1.97s` (`1.00x`, Eficiência `100%`)
  - `2 nós`: `1.12s` (`1.76x`, Eficiência `88%`)
  - `3 nós`: `0.89s` (`2.22x`, Eficiência `74%`)
  - `4 nós`: `0.73s` (`2.69x`, Eficiência `67%`)
  - A curva segue de perto a **Lei de Amdahl** com fração paralelizável $P \approx 88\%$ ($12\%$ sequencial devido ao pré-processamento `gcc -E` e linkagem final no cliente).
- **5B — Processos de fundo (`stress-ng`):**
  - `0% carga`: `0.75s` | `25% carga`: `0.82s (+9%)` | `50% carga`: `0.95s (+27%)` | `100% carga`: `2.60s (+247%)`. Quando os servidores atingem 100% de ocupação por processos concorrentes, o escalonador CFS divide o tempo de CPU com os workers do `distccd`, mais que triplicando o tempo de build.
- **5C — Nº de arquivos `.c` × paralelização:**
  - `8 arquivos`: `1.98x` (`0.91s` vs `0.46s`)
  - `24 arquivos`: `2.59x` (`2.37s` vs `0.92s`)
  - `48 arquivos`: `2.83x` (`4.61s` vs `1.63s`)

### Pergunta 6: Energia — 1 Máquina Potente vs. Várias em Paralelo
- **Energia Total (`Wh`):** Como cada máquina adicional ligada soma seu **consumo base ocioso ($P_{\text{idle}} \approx 45\text{ W}$)**, manter 2 máquinas ligadas (`260 W` combinados em carga) consome ligeiramente mais energia absoluta (`mWh`) em projetos pequenos devido à sobrecarga fixa de rede e de duas fontes/placas-mãe ativas.
- **Produto Energia-Atraso (`EDP = Wh × s`):** Quando avaliamos a eficiência conjunta energia × tempo (**EDP**), o **ponto de virada ocorre em ~75 arquivos `.c`**: acima dessa escala (como no SQLite com 103 arquivos e no Kernel Linux com 904 objetos), a redução quadrática do tempo supera o custo da potência base extra, tornando a compilação distribuída muito mais vantajosa em EDP.
