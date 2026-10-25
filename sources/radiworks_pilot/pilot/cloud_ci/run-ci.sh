#!/usr/bin/env bash
# Local candidate. Publish only the reviewed package; dispatch requires cost approval.
set -euo pipefail
umask 077
test "${GITHUB_REPOSITORY:-}" = redshift-three67/radiworks-pilot
test "${GITHUB_RUN_ATTEMPT:-}" = 1
[[ "${GITHUB_RUN_ID:-}" =~ ^[0-9]+$ ]]
test "$(uname -s)/$(uname -m)" = Linux/x86_64
control="$GITHUB_WORKSPACE/control/pilot/cloud_ci"
source_root="$GITHUB_WORKSPACE/source"
python3 -I -S -B "$control/guard.py" source "$source_root" "$control/SOURCE_LOCK.json"
node --version
docker version --format '{{.Client.Version}}/{{.Server.Version}}'
work=$(mktemp -d "$RUNNER_TEMP/rw-cp1.XXXXXXXX")
name="rw-cp1-${GITHUB_RUN_ID}"
image="rw-cp1:${GITHUB_RUN_ID}"
source "$control/cleanup.sh"
trap 'finish "$?"' EXIT
base='python@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258'
timeout --signal=TERM --kill-after=15s 180s docker pull --platform linux/amd64 "$base"
mkdir "$work/wheels"
chmod 777 "$work/wheels"
cp "$source_root/pilot/Dockerfile" "$work/Dockerfile"
cp "$source_root/pilot/requirements-linux-c3a.lock" "$work/requirements-linux-c3a.lock"
chmod 0444 "$work/requirements-linux-c3a.lock"
timeout --signal=TERM --kill-after=15s 300s docker run --name "$name" --rm --cpus=1 --memory=1g --memory-swap=1g --pids-limit=128 \
  --cap-drop=ALL --security-opt=no-new-privileges --read-only --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  --mount "type=bind,src=$work/wheels,dst=/wheels" \
  --mount "type=bind,src=$work/requirements-linux-c3a.lock,dst=/requirements.lock,readonly" \
  "$base" python -m pip download --disable-pip-version-check --no-cache-dir --no-deps --only-binary=:all: \
  --require-hashes --index-url=https://pypi.org/simple --dest=/wheels -r /requirements.lock
python3 -I -S -B "$control/guard.py" wheels "$work/wheels" "$source_root/pilot/dependencies.json"
# Base and all wheels are already present; Dockerfile is the original, unchanged one.
timeout --signal=TERM --kill-after=15s 900s docker build --network=none --pull=false --platform=linux/amd64 --tag "$image" "$work"
docker image inspect "$image" --format '{{.Id}}'
mkdir "$work/results"
chmod 777 "$work/results"
timeout --signal=TERM --kill-after=15s 360s docker run --name "$name" --rm --network=none \
  --cpus=1 --memory=1g --memory-swap=1g --pids-limit=128 --cap-drop=ALL --security-opt=no-new-privileges \
  --read-only --tmpfs /tmp:rw,nosuid,nodev,size=256m --workdir=/source/engine \
  --env PYTHONDONTWRITEBYTECODE=1 --env PYTHONPATH=/source/engine/src --env RADIOWORKS_HOME=/tmp/radiworks \
  --env HOME=/tmp --env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  --mount "type=bind,src=$source_root/engine,dst=/source/engine,readonly" \
  --mount "type=bind,src=$source_root/webapp,dst=/source/webapp,readonly" \
  --mount "type=bind,src=$work/results,dst=/results" \
  "$image" python -m pytest -p no:cacheprovider --basetemp=/tmp/pytest --maxfail=1 \
  --junitxml=/results/junit.xml tests/test_analysis.py tests/test_rates.py tests/test_gold_parity.py tests/test_bootstrap.py
python3 -I -S -B "$control/guard.py" junit "$work/results/junit.xml"
js_count=0
while IFS= read -r -d '' file; do
  timeout --signal=TERM --kill-after=2s 10s node --experimental-default-type=module --check "$file"
  js_count=$((js_count + 1))
done < <(find "$source_root/webapp" -type f \( -name '*.js' -o -name '*.mjs' \) -print0)
test "$js_count" -gt 0
printf 'JavaScript syntax files checked: %s\n' "$js_count"
python3 -I -S -B "$control/guard.py" source "$source_root" "$control/SOURCE_LOCK.json"
printf 'CP1 only: no SQLite fix, browser acceptance, VPS deployment or product approval.\n'
