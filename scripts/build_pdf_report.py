#!/usr/bin/env python3
"""
build_pdf_report.py
Adiciona ao final do arquivo docs/relatorio_impressao.html todas as tabelas brutas
dos testes realizados (hardware_specs.csv, tempos_compilacao.csv, distribuicao_hosts.csv
e energia_estimada.csv) para geração do PDF completo.
"""

import os
import pandas as pd


def df_to_html_table(df: pd.DataFrame) -> str:
    cols = df.columns.tolist()
    out = ['<table class="appendix-table"><thead><tr>']
    for c in cols:
        out.append(f"<th>{c}</th>")
    out.append("</tr></thead><tbody>")
    for _, row in df.iterrows():
        out.append("<tr>")
        for c in cols:
            out.append(f"<td>{row[c]}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    html_path = os.path.join(root_dir, "docs", "relatorio_impressao.html")
    res_dir = os.path.join(root_dir, "results")

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Se já tiver o anexo de execuções anteriores, remove antes de regerar
    marker = "<!-- ANEXO_RESULTADOS_BRUTOS -->"
    if marker in html:
        html = html.split(marker)[0]
    else:
        html = html.replace("</body>\n</html>", "").replace("</body></html>", "")

    df_hw = pd.read_csv(os.path.join(res_dir, "hardware_specs.csv"))
    df_tempos = pd.read_csv(os.path.join(res_dir, "tempos_compilacao.csv"))
    df_hosts = pd.read_csv(os.path.join(res_dir, "distribuicao_hosts.csv"))
    df_energia = pd.read_csv(os.path.join(res_dir, "energia_estimada.csv"))

    appendix = f"""{marker}
<div class="page-break"></div>
<h2>Anexo — Todos os Resultados Brutos dos Testes Executados (CSVs Completos)</h2>
<p>Abaixo estão incluídos todos os registros brutos gerados pelos testes executados no computador (AMD Ryzen 7 5700X3D no WSL 2).</p>

<h3>A.1 Especificações de Hardware Coletadas (<code>hardware_specs.csv</code> — {len(df_hw)} linhas)</h3>
{df_to_html_table(df_hw)}

<h3>A.2 Todas as Medições de Tempo de Compilação (<code>tempos_compilacao.csv</code> — {len(df_tempos)} execuções)</h3>
{df_to_html_table(df_tempos)}

<div class="page-break"></div>
<h3>A.3 Todos os Registros de Distribuição por Servidor (<code>distribuicao_hosts.csv</code> — {len(df_hosts)} linhas)</h3>
{df_to_html_table(df_hosts)}

<h3>A.4 Todos os Cálculos de Energia e EDP sobre Tempos Reais (<code>energia_estimada.csv</code> — {len(df_energia)} linhas)</h3>
{df_to_html_table(df_energia)}

</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html + appendix)

    print(
        f"[OK] HTML atualizado com {len(df_tempos)} linhas de tempo e {len(df_hosts)} linhas de host."
    )


if __name__ == "__main__":
    main()
