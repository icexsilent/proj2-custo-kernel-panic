#!/usr/bin/env python3
"""
parse_distcc_logs.py
Analisa o arquivo /tmp/distcc-client.log após uma compilação com distcc,
contabiliza quantos arquivos foram compilados com sucesso em cada host/porta
e adiciona o resultado em results/distribuicao_hosts.csv.
"""

import csv
import os
import re
import sys
from collections import Counter

COMPILE_OK_RE = re.compile(r"compile\s+(\S+)\s+on\s+(\S+)\s+completed\s+ok")


def main():
    if len(sys.argv) < 6:
        print(
            "Uso: parse_distcc_logs.py <log_file> <output_csv> <experimento> <projeto> <rotulo> <repeticao>",
            file=sys.stderr,
        )
        sys.exit(1)

    log_file = sys.argv[1]
    output_csv = sys.argv[2]
    experimento = sys.argv[3]
    projeto = sys.argv[4]
    rotulo = sys.argv[5]
    repeticao = sys.argv[6]

    counts = Counter()
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = COMPILE_OK_RE.search(line)
                if m:
                    host = m.group(2)
                    # Limpa sufixos de slots como /4 ou ,lzo se presentes no nome do host
                    host_clean = host.split("/")[0].split(",")[0]
                    counts[host_clean] += 1

    total = sum(counts.values())
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    file_exists = os.path.exists(output_csv) and os.path.getsize(output_csv) > 0

    with open(output_csv, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(
                [
                    "experimento",
                    "projeto",
                    "rotulo",
                    "repeticao",
                    "host",
                    "arquivos_compilados",
                    "total_arquivos",
                    "percentual",
                ]
            )
        if total > 0:
            for host, c in sorted(counts.items()):
                pct = round((c / total) * 100.0, 2)
                writer.writerow(
                    [experimento, projeto, rotulo, repeticao, host, c, total, pct]
                )
        else:
            writer.writerow(
                [experimento, projeto, rotulo, repeticao, "local_make", 0, 0, 100.0]
            )

    print(total)


if __name__ == "__main__":
    main()
