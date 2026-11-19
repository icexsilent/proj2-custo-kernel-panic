# Planejamento Detalhado — Fase 4: Projetos Reais (SQLite Fonte Completo e Kernel Linux)

## Objetivo da Fase 4
Baixar, configurar e testar dentro do filesystem nativo do WSL 2 (`~/distcc_lab`) os dois projetos reais exigidos na **Seção 4.3 do roteiro**:
1. **SQLite (Código-Fonte Completo / Canonical Source):** e **não** o *amalgamation* (`sqlite3.c` único), garantindo que a árvore possua dezenas de arquivos `.c` independentes (`src/*.c`) + geração prévia dos cabeçalhos (`make target_source` / arquivos gerados pelo `tclsh`) para medir paralelização real.
2. **Kernel Linux:** baixar uma árvore oficial enxuta (`linux-6.12.y` tarball oficial do `kernel.org`), configurar com `make tinyconfig` enriquecido (ou `defconfig` modularizado) para que tenha centenas de arquivos `.c` independentes e compile de forma limpa e reprodutível tanto no modo **Solo (`make -jN`)** quanto **Distribuído (`make -jM CC="distcc gcc" HOSTCC="distcc gcc"`)**.

## Etapas de Execução da Fase 4

1. **Script de Preparação [`setup_projects.sh`](file:///e:/Faculdade/SistemasOperacionais/scripts/setup_projects.sh):**
   - **SQLite Canonical Source (`~/distcc_lab/sqlite_src`):**
     - Baixa o tarball oficial *canonical source* (`sqlite-src-*.zip` / `tar.gz`) ou clona com `--depth 1` do espelho oficial `https://github.com/sqlite/sqlite.git`.
     - Executa `./configure` e pré-gera os arquivos de código/headers auxiliares (`parse.h`, `opcodes.h`, `keywordhash.h`) e configura um alvo no Makefile (`objs_only` / `libsqlite3.a`) que compila os **>100 arquivos `.c` separados de `src/`** individualmente (evitando que o Makefile padrão junte tudo num único `sqlite3.c`).
   - **Kernel Linux (`~/distcc_lab/linux_src`):**
     - Baixa o tarball oficial do Kernel Linux (`linux-6.6.72.tar.xz` de `cdn.kernel.org`).
     - Configura `.config` determinístico (`tinyconfig` + opções de kernel padrão habilitadas para gerar ~350 arquivos `.o` independentes, permitindo múltiplas repetições de benchmark em poucos minutos cada, ou `defconfig` completo quando desejado).

2. **Execução de Benchmark Real (Fase 4 — Validação Final):**
   - Rodar a bateria de experimentos com os projetos reais preparados (`SQLite` fonte separado vs. `Kernel Linux`), atualizar os arquivos CSV em `e:\Faculdade\SistemasOperacionais\results\` e regenerar todos os 8 gráficos finais em `e:\Faculdade\SistemasOperacionais\plots\`.
