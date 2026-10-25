# Sourced by run-ci.sh. Only the job-specific container can be removed.
cleanup_owned_container() {
  local remaining
  remaining=$(timeout 15s docker container ls --all --filter "name=^${name}$" --format '{{.ID}}') || return 1
  if [[ -n "$remaining" ]]; then
    timeout 20s docker rm -f "$name" >/dev/null || return 1
    remaining=$(timeout 15s docker container ls --all --filter "name=^${name}$" --format '{{.ID}}') || return 1
    [[ -z "$remaining" ]] || return 1
  fi
}
finish() {
  local status=$1
  trap - EXIT
  if ! cleanup_owned_container; then
    printf 'CP1 cleanup could not confirm removal of its own container.\n' >&2
    status=1
  fi
  exit "$status"
}
