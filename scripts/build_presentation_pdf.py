#!/usr/bin/env python3
"""
Gera o PDF de Apresentacao em Sala (formato Slides 16:9, exatas 8 paginas para 8 slides, sem quebra interna)
Arquivo gerado: e:/Faculdade/SistemasOperacionais/Apresentacao_Sala_distcc.pdf
"""
import os

ROOT_DIR = "/mnt/e/Faculdade/SistemasOperacionais"
PLOTS_DIR = os.path.join(ROOT_DIR, "plots")
HTML_OUT = os.path.join(ROOT_DIR, "docs", "apresentacao_sala.html")

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Apresentação — Compilação Distribuída com distcc</title>
<style>
  @page {{
    size: 297mm 167mm;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    font-family: "DejaVu Sans", "Segoe UI", Arial, sans-serif;
    color: #0f172a;
    background: #ffffff;
    font-size: 8.8pt;
    line-height: 1.28;
  }}
  .slide {{
    width: 297mm;
    height: 166.5mm;
    padding: 7.5mm 11mm 6.5mm 11mm;
    page-break-after: always;
    break-after: page;
    page-break-inside: avoid;
    break-inside: avoid;
    position: relative;
    background: #ffffff;
    overflow: hidden;
  }}
  .slide:last-child {{
    page-break-after: auto;
    break-after: auto;
  }}
  /* Top header bar on content slides */
  .slide-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #1e3a8a;
    padding-bottom: 2.2mm;
    margin-bottom: 3.2mm;
  }}
  .slide-tag {{
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    font-weight: 700;
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.8mm 2.5mm;
    border-radius: 4px;
    margin-bottom: 0.8mm;
  }}
  .slide-title {{
    font-size: 14.5pt;
    font-weight: 800;
    color: #0f172a;
  }}
  .slide-num {{
    font-size: 8.5pt;
    font-weight: 700;
    color: #64748b;
    background: #f1f5f9;
    padding: 1.2mm 3mm;
    border-radius: 999px;
  }}
  /* Two-column layout */
  .row {{
    display: table;
    width: 100%;
    table-layout: fixed;
  }}
  .col-left, .col-right {{
    display: table-cell;
    vertical-align: top;
  }}
  .col-left {{
    width: 49%;
    padding-right: 3mm;
  }}
  .col-right {{
    width: 51%;
    padding-left: 3mm;
  }}
  .col-50-l {{
    display: table-cell;
    vertical-align: top;
    width: 50%;
    padding-right: 3mm;
  }}
  .col-50-r {{
    display: table-cell;
    vertical-align: top;
    width: 50%;
    padding-left: 3mm;
  }}
  /* Cards and Boxes */
  .card-highlight {{
    background: #eff6ff;
    border: 1.2px solid #3b82f6;
    border-left: 4.5px solid #1d4ed8;
    border-radius: 5px;
    padding: 2.5mm 3.2mm;
    margin-bottom: 2mm;
  }}
  .card-green {{
    background: #f0fdf4;
    border: 1.2px solid #22c55e;
    border-left: 4.5px solid #15803d;
    border-radius: 5px;
    padding: 2.5mm 3.2mm;
    margin-bottom: 2mm;
  }}
  .card-amber {{
    background: #fffbeb;
    border: 1.2px solid #f59e0b;
    border-left: 4.5px solid #b45309;
    border-radius: 5px;
    padding: 2.5mm 3.2mm;
    margin-bottom: 2mm;
  }}
  .card-highlight h3, .card-green h3, .card-amber h3 {{
    font-size: 9.8pt;
    font-weight: 700;
    color: #1e3a8a;
    margin-bottom: 1.2mm;
  }}
  .card-green h3 {{ color: #14532d; }}
  .card-amber h3 {{ color: #78350f; }}
  /* Tables */
  table.data {{
    width: 100%;
    border-collapse: collapse;
    font-size: 8.2pt;
    margin-bottom: 2.5mm;
    background: #ffffff;
  }}
  table.data th {{
    background: #1e3a8a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 1.3mm 2mm;
    border: 1px solid #1e3a8a;
  }}
  table.data td {{
    padding: 1.15mm 2mm;
    border: 1px solid #cbd5e1;
    color: #1e293b;
  }}
  table.data tr:nth-child(even) td {{
    background: #f8fafc;
  }}
  table.data tr.best td {{
    background: #dcfce7;
    font-weight: 700;
    color: #14532d;
  }}
  table.data tr.warn td {{
    background: #fee2e2;
    font-weight: 700;
    color: #7f1d1d;
  }}
  .num {{
    text-align: right;
    font-family: "DejaVu Sans Mono", Consolas, monospace;
    white-space: nowrap;
  }}
  /* Lists */
  ul.direto {{
    padding-left: 4mm;
  }}
  ul.direto li {{
    margin-bottom: 1mm;
    font-size: 8.5pt;
  }}
  /* Images */
  .img-box {{
    text-align: center;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 1.5mm;
  }}
  .img-box img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
  }}
  /* KPI Grid */
  .kpi-row {{
    display: table;
    width: 100%;
    table-layout: fixed;
    margin-top: 3mm;
  }}
  .kpi {{
    display: table-cell;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-top: 3px solid #1d4ed8;
    border-radius: 5px;
    padding: 2.2mm 2.5mm;
    text-align: center;
  }}
  .kpi .val {{
    font-size: 14pt;
    font-weight: 800;
    color: #1e3a8a;
    display: block;
  }}
  .kpi .lbl {{
    font-size: 7.8pt;
    color: #475569;
    font-weight: 600;
  }}
  .footer-bar {{
    position: absolute;
    bottom: 2.5mm;
    left: 11mm;
    right: 11mm;
    display: flex;
    justify-content: space-between;
    font-size: 7.5pt;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
    padding-top: 1mm;
  }}
</style>
</head>
<body>

<!-- ==================== SLIDE 1: CAPA & METODOLOGIA ==================== -->
<div class="slide" style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #ffffff;">
  <div style="margin-top: 2mm; margin-bottom: 4mm;">
    <span style="background: #3b82f6; color: #ffffff; font-weight: 700; font-size: 8.5pt; padding: 1.2mm 3.5mm; border-radius: 999px; letter-spacing: 0.06em; text-transform: uppercase;">
      Sistemas Operacionais · Projeto 2: Custo · Turma 4P
    </span>
    <h1 style="font-size: 21pt; font-weight: 800; margin-top: 3.5mm; line-height: 1.18; color: #ffffff;">
      Compilação Distribuída em C com <code style="color: #93c5fd;">distcc</code>:<br>
      Desempenho, Escalabilidade, Contenção e Energia
    </h1>
    <p style="font-size: 10.5pt; color: #cbd5e1; margin-top: 2mm;">
      <b>Grupo Kernel Panic (KPE-V7L):</b> Vinicius Rampazi de Oliveira (RA 10426499) · Gabriel Coelho · Caroline Lee · Caio Belom · Fernando Paiva
    </p>
  </div>

  <div class="row" style="margin-top: 3mm;">
    <div class="col-50-l">
      <div style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.22); border-left: 5px solid #60a5fa; border-radius: 6px; padding: 3.5mm;">
        <h3 style="color: #93c5fd; font-size: 10.5pt; margin-bottom: 1.5mm;">Pergunta Central &amp; Mecanismos do SO</h3>
        <p style="font-size: 9.2pt; color: #f8fafc; margin-bottom: 2mm;">
          <b>Pergunta:</b> Quanto acelera o tempo de compilação limpa de um projeto em C ao distribuir os processos entre múltiplos nós simultaneamente, e onde estão seus limites de rede, CPU e energia?
        </p>
        <ul class="direto" style="color: #e2e8f0; font-size: 8.8pt;">
          <li><b>Pilares OSTEP:</b> Virtualização de CPU e Concorrência.</li>
          <li><b>Mecanismos:</b> Escalonador CFS do Linux, troca de contexto (<i>context switch</i>), paralelismo SMT, filas de rede TCP/IP (<code>tc qdisc tbf</code>) e estados de energia (<i>race-to-idle</i>).</li>
        </ul>
      </div>
    </div>

    <div class="col-50-r">
      <div style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.22); border-left: 5px solid #34d399; border-radius: 6px; padding: 3.5mm;">
        <h3 style="color: #6ee7b7; font-size: 10.5pt; margin-bottom: 1.5mm;">Ambiente Real de Medição &amp; Controle</h3>
        <table style="width: 100%; font-size: 8.8pt; color: #f1f5f9; border-collapse: collapse;">
          <tr><td style="padding: 0.9mm 0; color: #93c5fd; font-weight: 700; width: 33%;">Processador:</td><td>AMD Ryzen 7 5700X3D (8 núcleos / 16 threads, TDP 105W)</td></tr>
          <tr><td style="padding: 0.9mm 0; color: #93c5fd; font-weight: 700;">Memória &amp; SO:</td><td>15 GB RAM DDR4 · Ubuntu 26.04 LTS (WSL 2, Kernel 6.18.58)</td></tr>
          <tr><td style="padding: 0.9mm 0; color: #93c5fd; font-weight: 700;">Ferramentas:</td><td><code>gcc 15.2.0 (-O2 -Wall)</code> · <code>distcc 3.4</code> · <code>stress-ng</code></td></tr>
          <tr><td style="padding: 0.9mm 0; color: #93c5fd; font-weight: 700;">Cargas Testadas:</td><td>Projetos C Modulares (8 a 48 <code>.c</code>), <b>SQLite 3.47.2</b> e <b>Linux 6.6.72</b></td></tr>
          <tr><td style="padding: 0.9mm 0; color: #93c5fd; font-weight: 700;">Rigor de Coleta:</td><td><code>make clean</code> + 1 <i>warm-up</i> descartado + repetições via <code>date +%s.%N</code></td></tr>
        </table>
      </div>
    </div>
  </div>

  <div class="kpi-row" style="margin-top: 3.5mm;">
    <div class="kpi" style="background: rgba(15,23,42,0.75); border-color: #3b82f6; color: #fff;">
      <span class="val" style="color: #60a5fa;">1,55x a 2,83x</span>
      <span class="lbl" style="color: #cbd5e1;">Speedup Real Alcançado</span>
    </div>
    <div class="kpi" style="background: rgba(15,23,42,0.75); border-color: #10b981; color: #fff;">
      <span class="val" style="color: #34d399;">61,2 s vs 171,3 s</span>
      <span class="lbl" style="color: #cbd5e1;">Kernel Linux 6.6.72 (904 objetos)</span>
    </div>
    <div class="kpi" style="background: rgba(15,23,42,0.75); border-color: #f59e0b; color: #fff;">
      <span class="val" style="color: #fbbf24;">50 Mbps</span>
      <span class="lbl" style="color: #cbd5e1;">Joelho da Curva de Rede</span>
    </div>
    <div class="kpi" style="background: rgba(15,23,42,0.75); border-color: #a855f7; color: #fff;">
      <span class="val" style="color: #c084fc;">-36,8% Energia</span>
      <span class="lbl" style="color: #cbd5e1;">Economia por Race-to-Idle (Wh)</span>
    </div>
  </div>
</div>

<!-- ==================== SLIDE 2: INDIVIDUAL VS COLETIVO & DISTRIBUICAO ==================== -->
<div class="slide">
  <div class="slide-header">
    <div>
      <span class="slide-tag">Frente 1 &amp; 2 · Paralelismo e Balanceamento</span>
      <div class="slide-title">Compilação Individual vs. Coletiva e Distribuição de Tarefas</div>
    </div>
    <span class="slide-num">Slide 2 / 8</span>
  </div>

  <div class="row">
    <div class="col-left">
      <table class="data">
        <thead>
          <tr>
            <th>Cenário (17 arquivos .c)</th>
            <th>Jobs</th>
            <th class="num">R1 (s)</th>
            <th class="num">R2 (s)</th>
            <th class="num">Média</th>
            <th class="num">Ganho</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Máquina 1 Individual (<code>:3632</code>)</td>
            <td><code>-j4</code></td>
            <td class="num">1,235</td>
            <td class="num">1,242</td>
            <td class="num"><b>1,24 s</b></td>
            <td class="num">1,00x (Base)</td>
          </tr>
          <tr>
            <td>Máquina 2 Individual (<code>:3633</code>)</td>
            <td><code>-j4</code></td>
            <td class="num">1,183</td>
            <td class="num">1,233</td>
            <td class="num"><b>1,21 s</b></td>
            <td class="num">1,02x</td>
          </tr>
          <tr class="best">
            <td>Coletivo (Máquina 1 + Máquina 2)</td>
            <td><code>-j8</code></td>
            <td class="num">0,802</td>
            <td class="num">0,796</td>
            <td class="num"><b>0,80 s</b></td>
            <td class="num">1,55x (-35,5%)</td>
          </tr>
        </tbody>
      </table>

      <table class="data">
        <thead>
          <tr>
            <th>Servidor / Nó no Log do distcc</th>
            <th>Papel no Build</th>
            <th class="num">Arquivos .c</th>
            <th class="num">Fração (%)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>127.0.0.1:3632</code> (Nó 1)</td>
            <td>Compilação C (<code>cc1</code>)</td>
            <td class="num">9</td>
            <td class="num"><b>52,94%</b></td>
          </tr>
          <tr>
            <td><code>127.0.0.1:3633</code> (Nó 2)</td>
            <td>Compilação C (<code>cc1</code>)</td>
            <td class="num">8</td>
            <td class="num"><b>47,06%</b></td>
          </tr>
          <tr>
            <td><code>localhost</code> (Cliente)</td>
            <td>Linkedição final (<code>ld</code>)</td>
            <td class="num">1 (link)</td>
            <td class="num">Etapa serial</td>
          </tr>
        </tbody>
      </table>

      <div class="card-highlight">
        <h3>Pontos Diretos para Apresentação</h3>
        <ul class="direto">
          <li><b>Ganho Coletivo:</b> Unir os 2 nós reduziu o tempo de <b>1,24 s para 0,80 s</b> (speedup de <b>1,55x</b>, -35,5%).</li>
          <li><b>Balanceamento Simétrico:</b> Para 17 arquivos <code>.c</code>, a divisão exata foi <b>9 vs. 8 arquivos</b> (52,9% e 47,1%).</li>
          <li><b>Por que não 2,00x?</b> O pré-processamento (<code>cpp</code>) e a linkedição final do binário (<code>ld</code>) rodam localmente no cliente (Lei de Amdahl).</li>
        </ul>
      </div>
    </div>

    <div class="col-right">
      <div class="img-box" style="margin-bottom: 2mm;">
        <img src="file://{PLOTS_DIR}/01_individual_vs_coletivo.png" style="max-height: 55mm;">
      </div>
      <div class="img-box">
        <img src="file://{PLOTS_DIR}/02_percentual_por_maquina.png" style="max-height: 55mm;">
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>Grupo Kernel Panic (KPE-V7L) · Turma 4P</span>
    <span>Dados brutos medidos em results/tempos_compilacao.csv e results/distribuicao_hosts.csv</span>
  </div>
</div>

<!-- ==================== SLIDE 3: PROJETOS REAIS (SQLITE VS KERNEL LINUX) ==================== -->
<div class="slide">
  <div class="slide-header">
    <div>
      <span class="slide-tag">Frente 3 · Cargas Reais de Produção</span>
      <div class="slide-title">Projetos Reais: SQLite 3.47.2 (103 .c) vs. Kernel Linux 6.6.72 (904 .o)</div>
    </div>
    <span class="slide-num">Slide 3 / 8</span>
  </div>

  <div class="row">
    <div class="col-left">
      <table class="data">
        <thead>
          <tr>
            <th>Projeto Real</th>
            <th>Porte</th>
            <th>Modo</th>
            <th class="num">R1 (s)</th>
            <th class="num">R2 (s)</th>
            <th class="num">Média</th>
            <th class="num">Speedup</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>SQLite 3.47.2</b></td>
            <td>103 <code>.c</code></td>
            <td>Solo (<code>-j2</code>)</td>
            <td class="num">14,24</td>
            <td class="num">14,25</td>
            <td class="num"><b>14,24 s</b></td>
            <td class="num">1,00x</td>
          </tr>
          <tr class="best">
            <td><b>SQLite 3.47.2</b></td>
            <td>103 <code>.c</code></td>
            <td>Dist (<code>-j12</code>)</td>
            <td class="num">6,65</td>
            <td class="num">6,78</td>
            <td class="num"><b>6,72 s</b></td>
            <td class="num">2,12x (-52,9%)</td>
          </tr>
          <tr>
            <td><b>Linux 6.6.72</b></td>
            <td>904 <code>.o</code></td>
            <td>Solo (<code>-j2</code>)</td>
            <td class="num">173,46</td>
            <td class="num">169,15</td>
            <td class="num"><b>171,31 s</b></td>
            <td class="num">1,00x</td>
          </tr>
          <tr class="best">
            <td><b>Linux 6.6.72</b></td>
            <td>904 <code>.o</code></td>
            <td>Dist (<code>-j12</code>)</td>
            <td class="num">65,62</td>
            <td class="num">56,78</td>
            <td class="num"><b>61,20 s</b></td>
            <td class="num">2,80x (-64,3%)</td>
          </tr>
        </tbody>
      </table>

      <div class="card-highlight">
        <h3>Por que o Kernel Linux escala melhor que o SQLite?</h3>
        <ul class="direto">
          <li><b>SQLite Desmembrado (<code>USE_AMALGAMATION=0</code>):</b> Possui 103 arquivos <code>.c</code> independentes; cai de <b>14,24 s para 6,72 s</b> (<b>2,12x</b> mais rápido), mas arquivos longos como <code>vdbe.c</code> e a linkedição final limitam o ganho.</li>
          <li><b>Kernel Linux (<code>vmlinux</code> — 904 objetos):</b> Cai de <b>171,31 s (~2m51s) para 61,20 s (~1m01s)</b>, economizando <b>110 segundos</b> (<b>2,80x</b> de speedup).</li>
          <li><b>Diluição do Overhead:</b> Com 904 objetos distribuídos em subdiretórios (<code>kernel/</code>, <code>mm/</code>, <code>fs/</code>, <code>net/</code>), os servidores <code>distccd</code> permanecem 100% ocupados durante todo o build.</li>
        </ul>
      </div>
    </div>

    <div class="col-right">
      <div class="img-box">
        <img src="file://{PLOTS_DIR}/03_kernel_vs_sqlite.png" style="max-height: 112mm;">
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>Grupo Kernel Panic (KPE-V7L) · Turma 4P</span>
    <span>Fontes oficiais compiladas com GCC 15.2.0 (-O2) em /root/distcc_lab/sqlite_src e /root/distcc_lab/linux_src</span>
  </div>
</div>

<!-- ==================== SLIDE 4: VELOCIDADE DA REDE ==================== -->
<div class="slide">
  <div class="slide-header">
    <div>
      <span class="slide-tag">Frente 4 · Gargalo de Entrada e Saída de Rede</span>
      <div class="slide-title">Impacto da Largura de Banda da Rede (1 Mbps a 1000 Mbps)</div>
    </div>
    <span class="slide-num">Slide 4 / 8</span>
  </div>

  <div class="row">
    <div class="col-left">
      <table class="data">
        <thead>
          <tr>
            <th>Banda Limitada</th>
            <th class="num">R1 (s)</th>
            <th class="num">R2 (s)</th>
            <th class="num">Média</th>
            <th>Regime de Operação</th>
          </tr>
        </thead>
        <tbody>
          <tr class="warn">
            <td><b>1 Mbit/s</b></td>
            <td class="num">19,242</td>
            <td class="num">19,234</td>
            <td class="num"><b>19,24 s</b></td>
            <td>Gargalo severo de rede (42x mais lento)</td>
          </tr>
          <tr class="warn">
            <td><b>5 Mbit/s</b></td>
            <td class="num">4,120</td>
            <td class="num">4,122</td>
            <td class="num"><b>4,12 s</b></td>
            <td>Rede saturada (pior que compilar solo)</td>
          </tr>
          <tr>
            <td><b>10 Mbit/s</b></td>
            <td class="num">2,267</td>
            <td class="num">2,241</td>
            <td class="num"><b>2,25 s</b></td>
            <td>Transição (ainda limitado por I/O TCP)</td>
          </tr>
          <tr class="best">
            <td><b>50 Mbit/s</b></td>
            <td class="num">0,818</td>
            <td class="num">0,781</td>
            <td class="num"><b>0,80 s</b></td>
            <td><b>Joelho da curva (rede deixa de travar)</b></td>
          </tr>
          <tr>
            <td><b>100 Mbit/s</b></td>
            <td class="num">0,643</td>
            <td class="num">0,576</td>
            <td class="num"><b>0,61 s</b></td>
            <td>Fast Ethernet — ganho distribuído pleno</td>
          </tr>
          <tr>
            <td><b>500 Mbit/s</b></td>
            <td class="num">0,431</td>
            <td class="num">0,477</td>
            <td class="num"><b>0,45 s</b></td>
            <td>Limitado apenas pela CPU (CPU-bound)</td>
          </tr>
          <tr class="best">
            <td><b>1000 Mbit/s</b></td>
            <td class="num">0,442</td>
            <td class="num">0,451</td>
            <td class="num"><b>0,45 s</b></td>
            <td>Platô de saturação da CPU (1 Gbps)</td>
          </tr>
        </tbody>
      </table>

      <div class="card-highlight">
        <h3>Isolamento Real via Network Namespace (<code>veth</code>)</h3>
        <ul class="direto">
          <li><b>Mecanismo:</b> Par virtual <code>veth_host &lt;-&gt; veth_ns</code> em <code>ip netns</code> com filtro <i>Token Bucket Filter</i> (<code>tc qdisc tbf</code>) moldando 100% dos pacotes TCP do <code>distcc</code>.</li>
          <li><b>Conclusão Prática:</b> Redes abaixo de <b>10 Mbps</b> tornam o <code>distcc</code> mais lento que compilar sozinho. A partir de <b>50–100 Mbps</b>, o ganho estabiliza no limite da CPU.</li>
        </ul>
      </div>
    </div>

    <div class="col-right">
      <div class="img-box">
        <img src="file://{PLOTS_DIR}/04_velocidade_rede.png" style="max-height: 112mm;">
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>Grupo Kernel Panic (KPE-V7L) · Turma 4P</span>
    <span>Tráfego por arquivo: ~150 KB de código pré-processado (.i) enviado + objeto compilado (.o) retornado</span>
  </div>
</div>

<!-- ==================== SLIDE 5: ESCALABILIDADE (1 A 4 MAQUINAS) & NUMERO DE ARQUIVOS ==================== -->
<div class="slide">
  <div class="slide-header">
    <div>
      <span class="slide-tag">Escalabilidade &amp; Complexidade · Frente Vinicius Rampazi</span>
      <div class="slide-title">Escala de Servidores (1 a 4 Nós) e Quantidade de Arquivos .c (8 a 48)</div>
    </div>
    <span class="slide-num">Slide 5 / 8</span>
  </div>

  <div class="row">
    <div class="col-50-l">
      <table class="data">
        <thead>
          <tr>
            <th>Nº de Máquinas (2 jobs/nó)</th>
            <th>Jobs</th>
            <th class="num">Média</th>
            <th class="num">Speedup</th>
            <th class="num">Eficiência/Nó</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1 Máquina (<code>:3632</code>)</td>
            <td><code>-j2</code></td>
            <td class="num"><b>1,97 s</b></td>
            <td class="num">1,00x</td>
            <td class="num">100,0%</td>
          </tr>
          <tr>
            <td>2 Máquinas (<code>:3632..3633</code>)</td>
            <td><code>-j4</code></td>
            <td class="num"><b>1,12 s</b></td>
            <td class="num">1,76x</td>
            <td class="num">87,8%</td>
          </tr>
          <tr>
            <td>3 Máquinas (<code>:3632..3634</code>)</td>
            <td><code>-j6</code></td>
            <td class="num"><b>0,89 s</b></td>
            <td class="num">2,22x</td>
            <td class="num">73,9%</td>
          </tr>
          <tr class="best">
            <td>4 Máquinas (<code>:3632..3635</code>)</td>
            <td><code>-j8</code></td>
            <td class="num"><b>0,73 s</b></td>
            <td class="num"><b>2,69x</b></td>
            <td class="num">67,3%</td>
          </tr>
        </tbody>
      </table>
      <div class="img-box">
        <img src="file://{PLOTS_DIR}/05a_escala_maquinas.png" style="max-height: 70mm;">
      </div>
    </div>

    <div class="col-50-r">
      <table class="data">
        <thead>
          <tr>
            <th>Porte do Projeto C</th>
            <th class="num">Solo (-j2)</th>
            <th class="num">Dist (-j8)</th>
            <th class="num">Speedup</th>
            <th class="num">Redução</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>8 arquivos .c</b> (+ main)</td>
            <td class="num">0,91 s</td>
            <td class="num">0,46 s</td>
            <td class="num"><b>1,98x</b></td>
            <td class="num">-49,5%</td>
          </tr>
          <tr>
            <td><b>24 arquivos .c</b> (+ main)</td>
            <td class="num">2,37 s</td>
            <td class="num">0,92 s</td>
            <td class="num"><b>2,59x</b></td>
            <td class="num">-61,3%</td>
          </tr>
          <tr class="best">
            <td><b>48 arquivos .c</b> (+ main)</td>
            <td class="num">4,61 s</td>
            <td class="num">1,63 s</td>
            <td class="num"><b>2,83x</b></td>
            <td class="num"><b>-64,7%</b></td>
          </tr>
        </tbody>
      </table>
      <div class="img-box">
        <img src="file://{PLOTS_DIR}/05c_arquivos_vs_speedup.png" style="max-height: 75mm;">
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>Grupo Kernel Panic (KPE-V7L) · Turma 4P</span>
    <span>Conclusão: Mais nós aceleram até 2,69x (limitado por Amdahl), e projetos com mais arquivos elevam o speedup de 1,98x para 2,83x</span>
  </div>
</div>

<!-- ==================== SLIDE 6: CONTENCAO DE PROCESSOS EM SEGUNDO PLANO ==================== -->
<div class="slide">
  <div class="slide-header">
    <div>
      <span class="slide-tag">Disputa por CPU &amp; Escalonamento · Frente Vinicius Rampazi</span>
      <div class="slide-title">Contenção de Processos em Segundo Plano na CPU (<code>stress-ng</code>)</div>
    </div>
    <span class="slide-num">Slide 6 / 8</span>
  </div>

  <div class="row">
    <div class="col-left">
      <table class="data">
        <thead>
          <tr>
            <th>Carga Concorrente</th>
            <th>Threads Ocupadas</th>
            <th class="num">R1 (s)</th>
            <th class="num">R2 (s)</th>
            <th class="num">Média</th>
            <th class="num">Degradação</th>
          </tr>
        </thead>
        <tbody>
          <tr class="best">
            <td><b>0% (CPU Livre)</b></td>
            <td>0 de 16 threads</td>
            <td class="num">0,733</td>
            <td class="num">0,764</td>
            <td class="num"><b>0,75 s</b></td>
            <td class="num">Baseline (0%)</td>
          </tr>
          <tr>
            <td><b>25% Contenção</b></td>
            <td>4 de 16 threads</td>
            <td class="num">0,825</td>
            <td class="num">0,810</td>
            <td class="num"><b>0,82 s</b></td>
            <td class="num">+9,2% (1,09x)</td>
          </tr>
          <tr>
            <td><b>50% Contenção</b></td>
            <td>8 de 16 threads</td>
            <td class="num">0,953</td>
            <td class="num">0,953</td>
            <td class="num"><b>0,95 s</b></td>
            <td class="num">+27,3% (1,27x)</td>
          </tr>
          <tr class="warn">
            <td><b>100% Contenção</b></td>
            <td>16 de 16 threads</td>
            <td class="num">2,216</td>
            <td class="num">2,980</td>
            <td class="num"><b>2,60 s</b></td>
            <td class="num"><b>+247,0% (3,47x)</b></td>
          </tr>
        </tbody>
      </table>

      <div class="card-highlight">
        <h3>Explicação pelo Sistema Operacional (Escalonador CFS)</h3>
        <ul class="direto">
          <li><b>Regime Tolerante (0% a 50% de carga):</b> Como o Ryzen 7 5700X3D possui 8 núcleos físicos e 16 threads lógicos (SMT), com 4 ou 8 threads ocupados pelo <code>stress-ng</code> o escalonador <b>CFS (Completely Fair Scheduler)</b> despacha os processos <code>cc1</code> do GCC nos 8 threads livres. O tempo sobe apenas <b>0,20 s (+27,3%)</b>.</li>
          <li><b>Colapso em 100% (16 threads ocupados):</b> Não restam threads livres. Os 8 processos do <code>distcc</code> disputam diretamente a <i>runqueue</i> com os 16 processos do <code>stress-ng</code>, gerando <b>trocas de contexto (<i>context switches</i>)</b> contínuas e perda de localidade nos caches L1/L2 (tempo salta para <b>2,60 s, +247%</b>).</li>
        </ul>
      </div>
    </div>

    <div class="col-right">
      <div class="img-box">
        <img src="file://{PLOTS_DIR}/05b_processos_fundo.png" style="max-height: 112mm;">
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>Grupo Kernel Panic (KPE-V7L) · Turma 4P</span>
    <span>Ferramenta de estresse: stress-ng --cpu N --cpu-method matrixprod durante o build distribuído (-j8)</span>
  </div>
</div>

<!-- ==================== SLIDE 7: EFICIENCIA ENERGETICA (WH E EDP) ==================== -->
<div class="slide">
  <div class="slide-header">
    <div>
      <span class="slide-tag">Custo Energético &amp; Race-to-Idle · Frente Vinicius Rampazi</span>
      <div class="slide-title">Consumo de Energia Elétrica (mWh) e Produto Energia-Atraso (EDP)</div>
    </div>
    <span class="slide-num">Slide 7 / 8</span>
  </div>

  <div class="row">
    <div class="col-left">
      <table class="data">
        <thead>
          <tr>
            <th>Carga Compilada</th>
            <th class="num">Solo (150W)</th>
            <th class="num">Dist (268,5W)</th>
            <th class="num">Economia</th>
            <th class="num">Melhoria EDP</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>Projeto C (8 arqs)</b></td>
            <td class="num">37,94 mWh</td>
            <td class="num"><b>34,28 mWh</b></td>
            <td class="num">-9,6%</td>
            <td class="num"><b>2,19x melhor</b></td>
          </tr>
          <tr>
            <td><b>Projeto C (24 arqs)</b></td>
            <td class="num">98,95 mWh</td>
            <td class="num"><b>68,48 mWh</b></td>
            <td class="num">-30,8%</td>
            <td class="num"><b>3,74x melhor</b></td>
          </tr>
          <tr class="best">
            <td><b>Projeto C (48 arqs)</b></td>
            <td class="num">192,24 mWh</td>
            <td class="num"><b>121,56 mWh</b></td>
            <td class="num"><b>-36,8%</b></td>
            <td class="num"><b>4,48x melhor</b></td>
          </tr>
          <tr>
            <td><b>SQLite 3.47.2 (103 .c)</b></td>
            <td class="num">593,47 mWh</td>
            <td class="num"><b>500,83 mWh</b></td>
            <td class="num">-15,6%</td>
            <td class="num"><b>2,51x melhor</b></td>
          </tr>
          <tr class="best">
            <td><b>Kernel Linux (904 .o)</b></td>
            <td class="num">7.137,8 mWh</td>
            <td class="num"><b>4.564,5 mWh</b></td>
            <td class="num"><b>-36,1%</b></td>
            <td class="num"><b>4,38x melhor</b></td>
          </tr>
        </tbody>
      </table>

      <div class="card-green">
        <h3>Como a Energia foi Calculada e por que Cai?</h3>
        <ul class="direto">
          <li><b>Física do Consumo:</b> <code>E (Wh) = Potência Ativa (W) × Tempo Medido (s) / 3600</code> e <code>EDP = E × t</code>.</li>
          <li><b>Envelope Térmico Real (Ryzen 7 5700X3D):</b> 1 Máquina Solo = <b>150,0 W</b> (<code>45W Idle + 105W TDP</code>) vs. 2 Máquinas Distribuídas = <b>268,5 W</b> (<code>2 × [45W + 0,85 × 105W]</code>).</li>
          <li><b>Limiar Matemático (<i>Race-to-Idle</i>):</b> Como <code>268,5W / 150,0W = 1,79x</code>, sempre que o speedup supera <b>1,79x</b>, terminar o build antes e devolver os núcleos ao repouso (<i>ACPI C-states</i> a 45W) <b>economiza até 36,8% de energia elétrica</b> (no Kernel Linux: <b>4,56 Wh vs. 7,14 Wh</b>).</li>
        </ul>
      </div>
    </div>

    <div class="col-right">
      <div class="img-box">
        <img src="file://{PLOTS_DIR}/06_energia_wh_edp.png" style="max-height: 112mm;">
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>Grupo Kernel Panic (KPE-V7L) · Turma 4P</span>
    <span>Script de cálculo: scripts/calc_energy.py sobre os tempos reais de results/tempos_compilacao.csv</span>
  </div>
</div>

<!-- ==================== SLIDE 8: SINTESE EXECUTIVA PARA APRESENTACAO ==================== -->
<div class="slide">
  <div class="slide-header">
    <div>
      <span class="slide-tag">Resumo Geral · Visão Completa do Projeto</span>
      <div class="slide-title">Síntese dos Resultados e Conclusões Finais</div>
    </div>
    <span class="slide-num">Slide 8 / 8</span>
  </div>

  <table class="data" style="font-size: 8pt; margin-bottom: 2.2mm;">
    <thead>
      <tr>
        <th style="width: 19%;">Experimento / Frente</th>
        <th style="width: 24%;">O que Variou (Condições)</th>
        <th style="width: 28%;">Resultado Medido (Números Reais)</th>
        <th style="width: 29%;">Mecanismo do SO / Explicação</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>1. Individual vs. Coletivo</b></td>
        <td>1 Máquina (<code>-j4</code>) vs. 2 Máquinas (<code>-j8</code>)</td>
        <td><b>1,24 s → 0,80 s</b> (Speedup <b>1,55x</b>, -35,5%)</td>
        <td>Paralelismo de processos <code>cc1</code> limitado pelo <code>ld</code> serial local</td>
      </tr>
      <tr>
        <td><b>2. Balanceamento de Carga</b></td>
        <td>Distribuição nos logs do <code>distcc</code></td>
        <td><b>52,94%</b> (9 arqs) Nó 1 vs. <b>47,06%</b> (8 arqs) Nó 2</td>
        <td>Escalonamento <i>round-robin</i> por slots livres nos daemons</td>
      </tr>
      <tr class="best">
        <td><b>3. SQLite vs. Kernel Linux</b></td>
        <td>SQLite (103 <code>.c</code>) vs. Kernel Linux (904 <code>.o</code>)</td>
        <td>SQLite: <b>14,24s → 6,72s (2,12x)</b> · Kernel: <b>171,31s → 61,20s (2,80x)</b></td>
        <td>Maior número de arquivos dilui o custo de sockets TCP e linker</td>
      </tr>
      <tr>
        <td><b>4. Largura de Banda</b></td>
        <td><code>1, 5, 10, 50, 100, 500, 1000 Mbps</code> (<code>tc tbf</code>)</td>
        <td><code>1 Mbps</code>: <b>19,24 s</b> → <code>50 Mbps</code>: <b>0,80 s</b> → <code>1 Gbps</code>: <b>0,45 s</b></td>
        <td>Abaixo de 10 Mbps há bloqueio em buffer TCP; 50 Mbps é o joelho</td>
      </tr>
      <tr>
        <td><b>5. Escala de Servidores</b></td>
        <td>1, 2, 3 e 4 Máquinas (<code>-j2</code> a <code>-j8</code>)</td>
        <td><b>1,97 s → 1,12 s → 0,89 s → 0,73 s</b> (Speedup <b>2,69x</b>)</td>
        <td>Lei de Amdahl: eficiência por nó cai de 100% para 67,3% em 4 nós</td>
      </tr>
      <tr class="warn">
        <td><b>6. Contenção de CPU</b></td>
        <td>Carga concorrente: <code>0%, 25%, 50%, 100%</code> (<code>stress-ng</code>)</td>
        <td><code>0%</code>: <b>0,75 s</b> → <code>50%</code>: <b>0,95 s (+27%)</b> → <code>100%</code>: <b>2,60 s (+247%)</b></td>
        <td>Até 50% o CFS usa threads SMT ociosos; em 100% colapsa por <i>context switch</i></td>
      </tr>
      <tr>
        <td><b>7. Porte do Projeto</b></td>
        <td>8, 24 e 48 arquivos <code>.c</code> (Solo vs. Distribuído)</td>
        <td>8 arqs: <b>1,98x</b> · 24 arqs: <b>2,59x</b> · 48 arqs: <b>2,83x</b></td>
        <td>Fila de compilação cheia amortiza latência de rede e pré-processamento</td>
      </tr>
      <tr class="best">
        <td><b>8. Energia e EDP</b></td>
        <td>Solo (150 W) vs. 2 Máquinas (268,5 W)</td>
        <td>48 arqs: <b>-36,8% Wh (EDP 4,48x)</b> · Kernel: <b>7,14 → 4,56 Wh (-36,1%)</b></td>
        <td><i>Race-to-Idle</i> (ACPI C-states): quando Speedup &gt; 1,79x, 2 nós gastam menos Wh</td>
      </tr>
    </tbody>
  </table>

  <div class="row">
    <div class="col-50-l">
      <div class="card-green" style="margin-bottom: 0;">
        <h3>Quando a Compilação Distribuída Vale a Pena?</h3>
        <ul class="direto">
          <li>Projetos modulares médios/grandes (<b>&ge; 24 arquivos <code>.c</code></b>, como SQLite e Kernel Linux).</li>
          <li>Rede local ou VPN com banda disponível <b>&ge; 50 Mbps</b>.</li>
          <li>Servidores com ocupação de CPU em segundo plano <b>&le; 50%</b> dos threads lógicos.</li>
        </ul>
      </div>
    </div>
    <div class="col-50-r">
      <div class="card-amber" style="margin-bottom: 0;">
        <h3>Quando Não Vale a Pena (Limites Encontrados)?</h3>
        <ul class="direto">
          <li>Redes lentas (<b>&le; 10 Mbps</b>): o tempo sobe até <b>19,24 s</b> esperando transferência TCP.</li>
          <li>Nós com <b>100% da CPU saturada</b>: trocas de contexto elevam o tempo em <b>+247%</b>.</li>
          <li>Projetos muito pequenos ou monolíticos onde o Speedup fica abaixo de <b>1,79x</b> (gasta mais energia).</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>Grupo Kernel Panic (KPE-V7L) · Vinicius Rampazi · Gabriel Coelho · Caroline Lee · Caio Belom · Fernando Paiva</span>
    <span>Sistemas Operacionais · 2026.2 · Prof. Lucas Figueiredo</span>
  </div>
</div>

</body>
</html>
"""

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML written to {HTML_OUT}")
