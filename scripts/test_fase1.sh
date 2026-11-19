#!/usr/bin/env bash
# test_fase1.sh - Validacao completa da Fase 1 (Ambiente WSL2, Rede e distcc)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== 1. VERIFICACAO DE BINARIOS E VERSOES ==="
gcc --version | head -n 1
distcc --version | head -n 1
stress-ng --version | head -n 1
python3 -c 'import pandas, matplotlib, numpy; print("Python libs OK:", pandas.__version__, matplotlib.__version__, numpy.__version__)'
if which ccache >/dev/null 2>&1; then
    echo "AVISO: ccache encontrado"
else
    echo "ccache nao instalado (OK - sem interferencia de cache)"
fi

echo ""
echo "=== 2. INICIANDO DAEMONS DISTCCD (PORTAS 3632 E 3633) ==="
"$SCRIPT_DIR/manage_distccd.sh" start 192.168.0.0/16 4

echo ""
echo "=== 3. TESTE DE COMPILACAO DISTRIBUIDA (8 ARQUIVOS .C + MAIN.C) ==="
mkdir -p ~/distcc_lab/test_hello
cd ~/distcc_lab/test_hello
rm -f ./*.c ./*.o app Makefile /tmp/distcc-client.log

for i in $(seq 1 8); do
cat <<EOF > "part${i}.c"
#include <stdio.h>
int func_${i}(void) {
    int s = 0;
    for (int k = 0; k < 100000; k++) s += k * ${i};
    return s;
}
EOF
done

cat <<EOF > main.c
#include <stdio.h>
int func_1(void); int func_2(void); int func_3(void); int func_4(void);
int func_5(void); int func_6(void); int func_7(void); int func_8(void);
int main(void) {
    printf("Resultado soma distribuida = %d\n",
        func_1()+func_2()+func_3()+func_4()+func_5()+func_6()+func_7()+func_8());
    return 0;
}
EOF

cat << 'EOF' > Makefile
CC ?= gcc
CFLAGS = -O2 -Wall
SRCS = part1.c part2.c part3.c part4.c part5.c part6.c part7.c part8.c main.c
OBJS = $(SRCS:.c=.o)

all: app

app: $(OBJS)
	$(CC) $(CFLAGS) -o app $(OBJS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o app
EOF

export DISTCC_HOSTS="127.0.0.1:3632/2 127.0.0.1:3633/2"
export DISTCC_VERBOSE=1
export DISTCC_LOG="/tmp/distcc-client.log"
export DISTCC_FALLBACK=0
export DISTCC_POTENTIAL_HOSTS=""

make clean
make -j4 CC="distcc gcc"
./app

echo ""
echo "=== CONTAGEM DE COMPILACOES POR DAEMON NOS LOGS ==="
N1_CLIENT=$(grep -E "compile .* on 127\.0\.0\.1:3632.*completed ok" /tmp/distcc-client.log | wc -l)
N2_CLIENT=$(grep -E "compile .* on 127\.0\.0\.1:3633.*completed ok" /tmp/distcc-client.log | wc -l)
N1_DAEMON=$(grep -E "job complete" /tmp/distccd_node1.log | wc -l)
N2_DAEMON=$(grep -E "job complete" /tmp/distccd_node2.log | wc -l)
echo "  -> Node 1 (127.0.0.1:3632): cliente=${N1_CLIENT} arquivos | daemon=${N1_DAEMON} jobs"
echo "  -> Node 2 (127.0.0.1:3633): cliente=${N2_CLIENT} arquivos | daemon=${N2_DAEMON} jobs"
echo "  -> Total distribuido: $((N1_CLIENT + N2_CLIENT)) de 9 arquivos .c"

echo ""
echo "=== 4. TESTE DE TRAFFIC CONTROL (tc) NO KERNEL WSL2 ==="
if tc qdisc add dev eth0 root tbf rate 50mbit burst 32kbit latency 400ms 2>&1; then
    echo "Sucesso: tc tbf funciona nativamente na interface eth0 do WSL2!"
    tc qdisc show dev eth0
    tc qdisc del dev eth0 root
else
    echo "AVISO: kernel padrao do WSL2 nao tem modulo sch_tbf habilitado por padrao."
    zcat /proc/config.gz 2>/dev/null | grep -E "CONFIG_NET_SCH_(TBF|NETEM|HTB)" || true
fi
