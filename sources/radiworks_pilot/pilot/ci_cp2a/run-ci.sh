#!/usr/bin/env bash
# PREPARED ONLY. Publication and exactly one dispatch need concrete approval.
set -euo pipefail
umask 077
test "${GITHUB_REPOSITORY:-}" = redshift-three67/radiworks-pilot
test "${GITHUB_RUN_ATTEMPT:-}" = 1
[[ "${GITHUB_RUN_ID:-}" =~ ^[0-9]+$ ]]
test "$(uname -s)/$(uname -m)" = Linux/x86_64
control="$GITHUB_WORKSPACE/control/pilot/ci_cp2a"
source_root="$GITHUB_WORKSPACE/source"
python3 -I -S -B "$control/guard.py" source "$source_root" "$control/SOURCE_LOCK.json"
work=$(mktemp -d "$RUNNER_TEMP/rw-cp2a.XXXXXXXX")
export DOCKER_CONFIG="$work/docker-config"
mkdir "$DOCKER_CONFIG" "$work/runtime" "$work/results" "$work/compiler"
mkdir "$work/runtime/wheels"
chmod 777 "$work/runtime/wheels" "$work/results"
owner=$(basename "$work")
python3 -I -S -B - "$work" <<'PY'
import json,os,shutil,sys
p=sys.argv[1];free=shutil.disk_usage(p).free;inodes=os.statvfs(p).f_favail
print(json.dumps({'workspace_free_bytes':free,'free_inodes':inodes,'minimum_bytes':8589934592,'minimum_inodes':75000}))
if free < 8589934592 or inodes < 75000: raise SystemExit('insufficient isolated CI capacity')
PY
base='python@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258'
builder='python@sha256:edd0b3ec946cc68bd20e39480bd03929016d0fb6254cbf870cd3bc55ea25116d'
image="rw-cp2a-runtime:${GITHUB_RUN_ID}"
candidate="rw-cp2a-candidate:${GITHUB_RUN_ID}"
last_stage=none
D=(docker --host unix:///var/run/docker.sock)
run() {
  last_stage=$1; local seconds=$2; shift 2
  timeout --signal=TERM --kill-after=10s "${seconds}s" "$@" 2>&1 | python3 -I -S -B "$control/logcap.py" "$work/$last_stage.log"
}
cleanup_cmd() {
  local remaining=$((cleanup_deadline-SECONDS))
  ((remaining > 0)) || return 124
  ((remaining <= 20)) || remaining=20
  timeout --signal=TERM --kill-after=2s "${remaining}s" "${D[@]}" "$@"
}
finish() {
  local code=$?
  trap 'code=1' INT TERM
  trap - EXIT; set +e
  local cleanup_deadline=$((SECONDS+120)) ids count=0 label
  ids=$(cleanup_cmd container ls -aq --no-trunc --filter "label=aurelia.cp2a=$owner")
  if (( $? != 0 )); then code=1; printf 'OWN_CLEANUP=unconfirmed\n'; else
    for cid in $ids; do count=$((count+1)); done
    if (( count > 4 )); then code=1; printf 'OWN_CLEANUP=unexpected_count\n'; else
      for cid in $ids; do
        [[ "$cid" =~ ^[0-9a-f]{64}$ ]] || { code=1; continue; }
        label=$(cleanup_cmd container inspect --format '{{index .Config.Labels "aurelia.cp2a"}}' "$cid")
        if (( $? != 0 )) || test "$label" != "$owner"; then code=1; continue; fi
        cleanup_cmd container rm --force "$cid" >/dev/null || code=1
      done
      ids=$(cleanup_cmd container ls -aq --no-trunc --filter "label=aurelia.cp2a=$owner")
      if (( $? != 0 )) || test -n "$ids"; then code=1; printf 'OWN_CLEANUP=unconfirmed\n'; else printf 'OWN_CLEANUP=absent\n'; fi
    fi
  fi
  python3 -I -S -B "$control/guard.py" source "$source_root" "$control/SOURCE_LOCK.json" || code=1
  for report in baseline.json candidate.json; do
    if test -f "$work/results/$report"; then
      sha256sum "$work/results/$report"
      if test "$(stat -c %s "$work/results/$report")" -le 65536; then cat "$work/results/$report"; else code=1; printf 'REPORT=oversize\n'; fi
    fi
  done
  if ((code != 0)) && test -f "$work/$last_stage.log"; then tail -c 2000 "$work/$last_stage.log"; fi
  printf '\nCP2A_EXIT=%s; no full regression, artifact export or pilot activation.\n' "$code"
  exit "$code"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
run docker-version 20 "${D[@]}" version --format '{{.Client.Version}}/{{.Server.Version}}'
run base-pull 180 "${D[@]}" pull --platform=linux/amd64 "$base"
run builder-pull 180 "${D[@]}" pull --platform=linux/amd64 "$builder"
run source-download 120 python3 -I -S -B "$control/materials.py" download "$work/source.zip"
run source-extract 60 python3 -I -S -B "$control/materials.py" extract "$work/source.zip" --target "$work/source"
install -m 0444 "$source_root/pilot/requirements-linux-c3a.lock" "$work/runtime/requirements-linux-c3a.lock"
run wheels 300 "${D[@]}" run --rm --name "rw-cp2a-${GITHUB_RUN_ID}-wheels" --label "aurelia.cp2a=$owner" \
 --cpus=1 --memory=1g --memory-swap=1g --pids-limit=128 --user 65532:65532 --cap-drop=ALL --security-opt=no-new-privileges \
 --read-only --tmpfs /tmp:rw,nosuid,nodev,size=256m \
 --mount "type=bind,src=$work/runtime/wheels,dst=/wheels" --mount "type=bind,src=$work/runtime/requirements-linux-c3a.lock,dst=/requirements.lock,readonly" \
 "$base" python -m pip download --disable-pip-version-check --no-cache-dir --no-deps --only-binary=:all: --require-hashes --index-url=https://pypi.org/simple --dest=/wheels -r /requirements.lock
python3 -I -S -B "$control/guard.py" wheels "$work/runtime/wheels" "$source_root/pilot/dependencies.json"
install -m 0444 "$source_root/pilot/Dockerfile" "$work/runtime/Dockerfile"
run runtime-build 900 env DOCKER_BUILDKIT=0 "${D[@]}" build --network=none --pull=false --platform=linux/amd64 --tag "$image" "$work/runtime"
run sqlite-compile 900 "${D[@]}" run --rm --name "rw-cp2a-${GITHUB_RUN_ID}-compile" --label "aurelia.cp2a=$owner" \
 --network=none --cpus=1 --memory=2g --memory-swap=2g --pids-limit=256 --user "$(id -u):$(id -g)" --cap-drop=ALL --security-opt=no-new-privileges \
 --read-only --tmpfs /tmp:rw,nosuid,nodev,size=256m --workdir=/work \
 --mount "type=bind,src=$work/compiler,dst=/work" --mount "type=bind,src=$work/source/sqlite-src-3540100,dst=/source,readonly" \
 --mount "type=bind,src=$control/build-sqlite.sh,dst=/build-sqlite.sh,readonly" --mount "type=bind,src=$control/COMPILE_FLAGS.json,dst=/flags.json,readonly" \
 "$builder" bash /build-sqlite.sh
for proof in TOOLCHAIN.txt ELF_DYNAMIC.txt; do sha256sum "$work/compiler/output/$proof"; head -c 4000 "$work/compiler/output/$proof"; done
library_hash=$(sha256sum "$work/compiler/output/libsqlite3.so.0" | cut -d ' ' -f1)
# Create only bound candidate context, with the unchanged runtime as parent.
mkdir "$work/candidate" "$work/candidate/sqlite"
cp "$work/compiler/output/libsqlite3.so.0" "$work/compiler/output/LICENSE.md" "$work/candidate/sqlite/"
cp "$control/Dockerfile.candidate" "$work/candidate/Dockerfile"
python3 -I -S -B - "$work" "$library_hash" <<'PY'
import hashlib,json,sys
from pathlib import Path
work=Path(sys.argv[1]); data={'library_sha256':sys.argv[2], 'sqlite_source_sha256':'387e7f6cad4797b17848c07d453dc6606917bb356a6cfe5a3abafd38c240c71b', 'builder':'sha256:edd0b3ec946cc68bd20e39480bd03929016d0fb6254cbf870cd3bc55ea25116d', 'toolchain_sha256':hashlib.sha256((work/'compiler/output/TOOLCHAIN.txt').read_bytes()).hexdigest()}
(work/'candidate/sqlite/BUILD_PROVENANCE.json').write_text(json.dumps(data,indent=2)+'\n')
PY
chmod 0444 "$work/candidate/sqlite/libsqlite3.so.0" "$work/candidate/sqlite/LICENSE.md" "$work/candidate/sqlite/BUILD_PROVENANCE.json"
run candidate-build 120 env DOCKER_BUILDKIT=0 "${D[@]}" build --network=none --pull=false --build-arg "RUNTIME_IMAGE=$image" --tag "$candidate" "$work/candidate"
common=(--network=none --cpus=1 --memory=1g --memory-swap=1g --pids-limit=128 --cap-drop=ALL --security-opt=no-new-privileges --read-only --tmpfs /tmp:rw,nosuid,nodev,size=256m --mount "type=bind,src=$control/sqlite_probe.py,dst=/sqlite_probe.py,readonly" --mount "type=bind,src=$work/results,dst=/results")
run baseline-probe 120 "${D[@]}" run --rm --name "rw-cp2a-${GITHUB_RUN_ID}-baseline" --label "aurelia.cp2a=$owner" "${common[@]}" "$image" python -I -S -B /sqlite_probe.py --output /results/baseline.json
run candidate-probe 120 "${D[@]}" run --rm --name "rw-cp2a-${GITHUB_RUN_ID}-candidate" --label "aurelia.cp2a=$owner" "${common[@]}" "$candidate" python -I -S -B /sqlite_probe.py --baseline /results/baseline.json --expected-library-hash "$library_hash" --expected-source-id '2026-10-16 14:45:20 555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76' --output /results/candidate.json
"${D[@]}" image inspect "$image" "$candidate" --format '{{.Id}}'
printf 'CP2A native candidate proof complete. Not a product/live approval.\n'
