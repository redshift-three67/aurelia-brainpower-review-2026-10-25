#!/usr/bin/env bash
# Executed only inside the separately approved fixed builder container.
set -euo pipefail
umask 022
test "$(uname -s)/$(uname -m)" = Linux/x86_64
for tool in gcc make ld ldd readelf python3; do command -v "$tool" >/dev/null; done
mkdir /work/src /work/build /work/output
cp -R /source/. /work/src/
chmod -R u+w /work/src
{ gcc --version; make --version; ld --version; ldd --version; python3 --version; } > /work/output/TOOLCHAIN.txt
test "$(cat /work/src/VERSION)" = 3.54.1
test "$(cat /work/src/manifest.uuid)" = 555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76
CFLAGS=$(python3 -I -S -B -c 'import json; print(" ".join(json.load(open("/flags.json"))))')
export CFLAGS
cd /work/build
sh /work/src/configure --prefix=/opt/radiworks-sqlite --disable-tcl --disable-readline --enable-update-limit --enable-session --enable-fts3 --enable-fts4 --enable-fts5 --enable-rtree --enable-math
make -j1 sqlite3.c
# Full-source parser generation above is mandatory for UPDATE/DELETE LIMIT.
read -r -a flags <<< "$CFLAGS"
gcc -fPIC -shared -Wl,-soname,libsqlite3.so.0 -o /work/output/libsqlite3.so.0 "${flags[@]}" sqlite3.c -lm -ldl -lpthread
readelf -d /work/output/libsqlite3.so.0 > /work/output/ELF_DYNAMIC.txt
cp /work/src/LICENSE.md /work/output/LICENSE.md
sha256sum /work/output/libsqlite3.so.0
