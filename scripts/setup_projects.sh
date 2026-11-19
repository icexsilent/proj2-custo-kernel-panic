#!/usr/bin/env bash
# setup_projects.sh
# Fase 4: Baixa e prepara o código-fonte completo (não-amalgamation) do SQLite
# e a árvore do Kernel Linux dentro do filesystem nativo do WSL 2 (~/distcc_lab).
#
# Uso: ./setup_projects.sh [tiny|defconfig]

set -euo pipefail

KERNEL_CONFIG_MODE="${1:-tiny}"
LAB_DIR="$HOME/distcc_lab"
SQLITE_DIR="$LAB_DIR/sqlite_src"
LINUX_DIR="$LAB_DIR/linux_src"

mkdir -p "$LAB_DIR"

echo "================================================================="
echo " [1/2] Preparando SQLite (Codigo-Fonte Completo / Multi-Arquivos)"
echo "================================================================="
if [ ! -d "$LAB_DIR/sqlite_repo" ]; then
    rm -rf "$LAB_DIR/sqlite_repo"
    echo "  -> Clonando repositorio oficial sqlite/sqlite (branch version-3.47.2)..."
    git clone --depth 1 --branch version-3.47.2 https://github.com/sqlite/sqlite.git "$LAB_DIR/sqlite_repo"
fi

cd "$LAB_DIR/sqlite_repo"
if [ ! -d "tsrc" ]; then
    echo "  -> Executando ./configure && make .target_source sqlite3.h sqlite3ext.h shell.c..."
    ./configure --disable-tcl >/dev/null
    make .target_source sqlite3.h sqlite3ext.h shell.c >/dev/null
fi

mkdir -p "$SQLITE_DIR"
rm -f "$SQLITE_DIR"/*.c "$SQLITE_DIR"/*.h "$SQLITE_DIR"/*.o "$SQLITE_DIR"/Makefile

cp "$LAB_DIR/sqlite_repo/tsrc"/*.c "$LAB_DIR/sqlite_repo/tsrc"/*.h "$SQLITE_DIR/"
cp "$LAB_DIR/sqlite_repo"/sqlite3*.h "$LAB_DIR/sqlite_repo"/config.h "$LAB_DIR/sqlite_repo"/shell.c "$SQLITE_DIR/" 2>/dev/null || true

cd "$SQLITE_DIR"
SRCS_LIST="alter.c analyze.c attach.c auth.c backup.c bitvec.c btmutex.c btree.c build.c callback.c complete.c ctime.c date.c dbpage.c dbstat.c delete.c expr.c fault.c fkey.c fts3.c fts3_aux.c fts3_expr.c fts3_hash.c fts3_icu.c fts3_porter.c fts3_snippet.c fts3_tokenizer.c fts3_tokenizer1.c fts3_tokenize_vtab.c fts3_unicode.c fts3_unicode2.c fts3_write.c fts5.c func.c global.c hash.c icu.c insert.c json.c legacy.c loadext.c main.c malloc.c mem0.c mem1.c mem2.c mem3.c mem5.c memdb.c memjournal.c mutex.c mutex_noop.c mutex_unix.c mutex_w32.c notify.c opcodes.c os.c os_kv.c os_unix.c os_win.c pager.c parse.c pcache.c pcache1.c pragma.c prepare.c printf.c random.c resolve.c rowset.c rtree.c sqlite3session.c select.c sqlite3rbu.c status.c stmt.c table.c threads.c tokenize.c treeview.c trigger.c update.c userauth.c upsert.c util.c vacuum.c vdbe.c vdbeapi.c vdbeaux.c vdbeblob.c vdbemem.c vdbesort.c vdbetrace.c vdbevtab.c wal.c walker.c where.c wherecode.c whereexpr.c window.c utf.c vtab.c shell.c"
NUM_SQLITE_C=$(echo "$SRCS_LIST" | wc -w)
echo "  -> SQLite (USE_AMALGAMATION=0) preparado com $NUM_SQLITE_C arquivos .c independentes em $SQLITE_DIR"

cat <<EOF > "$SQLITE_DIR/Makefile"
CC ?= gcc
CFLAGS = -O2 -DSQLITE_PRIVATE= -DSQLITE_CORE=1 -DSQLITE_THREADSAFE=1 -DSQLITE_ENABLE_MATH_FUNCTIONS -D_HAVE_SQLITE_CONFIG_H -DBUILD_sqlite -I.
LDFLAGS = -lpthread -ldl -lm

SRCS = $SRCS_LIST
OBJS = \$(SRCS:.c=.o)

all: sqlite3

sqlite3: \$(OBJS)
	\$(CC) \$(CFLAGS) -o sqlite3 \$(OBJS) \$(LDFLAGS)

%.o: %.c
	\$(CC) \$(CFLAGS) -c \$< -o \$@

clean:
	rm -f *.o sqlite3
EOF

echo "================================================================="
echo " [2/2] Preparando Kernel Linux (linux-6.6.72)"
echo "================================================================="
TARBALL="$LAB_DIR/linux-6.6.72.tar.xz"
if [ ! -f "$TARBALL" ]; then
    echo "  -> Baixando linux-6.6.72.tar.xz de cdn.kernel.org..."
    curl -L --fail --retry 3 -o "$TARBALL" https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.6.72.tar.xz
fi

if [ ! -d "$LINUX_DIR" ] || [ ! -f "$LINUX_DIR/Makefile" ]; then
    echo "  -> Extraindo Kernel Linux em $LINUX_DIR..."
    rm -rf "$LINUX_DIR"
    mkdir -p "$LINUX_DIR"
    tar -xf "$TARBALL" -C "$LINUX_DIR" --strip-components=1
fi

cd "$LINUX_DIR"
make mrproper >/dev/null

if [ "$KERNEL_CONFIG_MODE" = "defconfig" ]; then
    echo "  -> Configurando Kernel com defconfig..."
    make defconfig >/dev/null
else
    echo "  -> Configurando Kernel com tinyconfig + subsistemas de SO (64-bit, Net, VFS, Ext4, Proc, ELF)..."
    make tinyconfig >/dev/null
    ./scripts/config \
        --enable 64BIT \
        --enable SMP \
        --enable MULTIUSER \
        --enable PRINTK \
        --enable BUG \
        --enable ELF_CORE \
        --enable BINFMT_ELF \
        --enable FILE_LOCKING \
        --enable BLOCK \
        --enable NET \
        --enable INET \
        --enable PACKET \
        --enable UNIX \
        --enable PROC_FS \
        --enable SYSFS \
        --enable TMPFS \
        --enable EXT4_FS \
        --enable FUTEX \
        --enable EPOLL \
        --enable SIGNALFD \
        --enable TIMERFD \
        --enable EVENTFD \
        --enable SHMEM \
        --enable AIO \
        --enable IO_URING \
        --disable WERROR
    make olddefconfig >/dev/null
fi

# Pre-compila scripts e headers gerados do kernel para que o benchmark meca apenas a compilacao dos .c do kernel
echo "  -> Executando 'make prepare scripts' no Kernel Linux..."
make -j"$(nproc)" prepare scripts >/dev/null

echo "[OK] Projetos SQLite ($NUM_SQLITE_C arquivos .c) e Kernel Linux prontos em $LAB_DIR!"
