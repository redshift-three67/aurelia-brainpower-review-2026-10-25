from __future__ import annotations

import re
import shlex
import subprocess
from typing import Any

MAX_DIAGNOSTIC_LINES = 20
MAX_DIAGNOSTIC_CHARS = 2000
_REDACTED = "[REDACTED]"
_PATH_BODY = (
    r"(?:"
    r"[^\r\n\"'<>]*?\.[a-z0-9]{1,16}(?=$|[\s,;:)\]}])"
    r"|[^\r\n\"'<>]+?(?=[\"'])"
    r"|[^\r\n\"'<>]+?(?=\s+(?:progress|status|phase|completed)\b)"
    r"|[^\r\n\"'<>]+)"
)
# Unquoted extensionless paths stop only at explicit diagnostic field labels.
# Otherwise the broad final alternative remains fail-closed.
_WINDOWS_PATH = re.compile(
    rf"(?i)\b[a-z]:[\\/]{_PATH_BODY}"
)
_POSIX_PATH = re.compile(
    rf"(?i)(?<![\w.-])/{_PATH_BODY}"
)
_UNC_PATH = re.compile(rf"(?i)(?<![\\])\\\\{_PATH_BODY}")
_WINDOWS_ABSOLUTE_PATH_TOKEN = re.compile(r"(?i)^(?:[a-z]:[\\/]|\\\\)")
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_SECRET_ASSIGNMENT = re.compile(
    r'''(?ix)(?P<key_quote>["']?)(?P<key>[a-z0-9_.-]+)(?P=key_quote)'''
    r'''\s*[:=]\s*(?P<value>'''
    r'''"(?:\\.|[^"\\\r\n])*"|'''
    r'''(?:'(?:\\.|[^'\\\r\n])*')|'''
    r'''[^,;\r\n]+?(?=[,;])|'''
    r'''[^\s,;"']+)'''
)
_CREDENTIAL_SUFFIXES = {
    "api_key",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "password",
}
_AUTHORIZATION = re.compile(r"(?i)\bauthorization\s*:\s*(?:bearer|basic)?\s*\S+")
_COOKIE = re.compile(r"(?i)\b(?:set-)?cookie\s*:\s*[^\r\n]+")
_LINE_SEPARATOR = re.compile(r"[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]")
_VALUE_FLAGS = {
    "--birth-date",
    "--birth-place",
    "--level",
    "--export",
    "--hardware-profile",
    "--k-total",
    "--top-k",
    "--synergy-combos",
    "--synergy-threshold",
    "--top-n",
    "--profile-template",
    "--entropy-mode",
    "--image",
    "--planet-type",
    "--focus",
}
_BOOLEAN_FLAGS = {"--synergy", "--adaptive-limits"}
_COMMAND_PREFIX = ("-m", "apps.cli.main", "scan", "top3-scan")
_COMMAND_ECHO = re.compile(r"^(?P<prefix>(?:argv|command)\s*:\s*)(?P<body>.*)$", re.I)


def _command_structure(snapshot: dict[str, Any]) -> tuple[list[str], set[int]]:
    command = snapshot.get("command")
    if (
        not isinstance(command, list)
        or any(not isinstance(item, str) for item in command)
        or len(command) < 5
        or tuple(command[1:5]) != _COMMAND_PREFIX
    ):
        return [], set()

    sensitive_indexes = set(range(5, min(7, len(command))))
    index = 7
    while index < len(command):
        token = command[index]
        if token in _VALUE_FLAGS:
            if index + 1 < len(command):
                sensitive_indexes.add(index + 1)
            index += 2
            continue
        index += 1
    return list(command), sensitive_indexes


def _sensitive_values(
    snapshot: dict[str, Any],
    command: list[str],
    sensitive_indexes: set[int],
) -> list[str]:
    values = {
        command[index]
        for index in sensitive_indexes
        if command[index]
    }
    for key in (
        "first_name", "last_name", "birth_date", "birth_place", "focus",
        "main_symptom", "image_path", "parallel_export_plan",
        "parallel_export_client_id", "owner_id", "tenant_id", "operator_id",
    ):
        value = snapshot.get(key)
        if value is not None and str(value).strip():
            values.add(str(value).strip())
    return sorted(values, key=len, reverse=True)


def _redact_command_echo(
    line: str,
    command: list[str],
    sensitive_indexes: set[int],
    echoed_command: list[str],
) -> str | None:
    if not command:
        return None
    match = _COMMAND_ECHO.fullmatch(line)
    if match is None:
        return None
    body = match.group("body")
    redacted = [
        _REDACTED
        if (
            index in sensitive_indexes
            or (
                index != 0
                and (
                    token.startswith("/")
                    or _WINDOWS_ABSOLUTE_PATH_TOKEN.match(token)
                )
            )
        )
        else token
        for index, token in enumerate(command)
    ]
    try:
        if shlex.split(body, posix=True) == echoed_command:
            return match.group("prefix") + shlex.join(redacted)
    except ValueError:
        pass
    if body == subprocess.list2cmdline(echoed_command):
        return match.group("prefix") + subprocess.list2cmdline(redacted)
    if all(
        not any(character.isspace() for character in token)
        for token in echoed_command
    ):
        if body.split() == echoed_command:
            return match.group("prefix") + " ".join(redacted)
    return None


def _redact_sensitive_tokens(line: str, sensitive: list[str]) -> str:
    for value in sensitive:
        left_boundaries = [r"(?<![A-Za-z0-9])"]
        right_boundaries = [r"(?![A-Za-z0-9])"]
        if value[0].isupper():
            left_boundaries.append(r"(?<=[a-z0-9])")
        if value[-1].islower():
            right_boundaries.append(r"(?=[A-Z])")
        token_pattern = re.compile(
            rf"(?:{'|'.join(left_boundaries)}){re.escape(value)}"
            rf"(?:{'|'.join(right_boundaries)})"
        )
        line = token_pattern.sub(_REDACTED, line)
    return line


def _redact_secret_assignment(match: re.Match[str]) -> str:
    key = match.group("key")
    normalized = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
    if not any(
        normalized == suffix or normalized.endswith(f"_{suffix}")
        for suffix in _CREDENTIAL_SUFFIXES
    ):
        return match.group(0)
    return f"{key}={_REDACTED}"


def safe_scan_diagnostics(snapshot: object) -> list[str]:
    """Return bounded useful worker diagnostics with authority and PII redacted."""
    if not isinstance(snapshot, dict):
        return []
    command, sensitive_indexes = _command_structure(snapshot)
    sensitive = _sensitive_values(snapshot, command, sensitive_indexes)
    pre_split_sensitive = [
        value for value in sensitive if _LINE_SEPARATOR.search(value)
    ]
    echoed_command = [
        _REDACTED
        if index in sensitive_indexes and _LINE_SEPARATOR.search(token)
        else token
        for index, token in enumerate(command)
    ]
    raw_lines: list[str] = []
    for key in ("stdout_tail", "stderr_tail"):
        value = snapshot.get(key)
        if isinstance(value, str):
            for private_value in pre_split_sensitive:
                value = value.replace(private_value, _REDACTED)
            raw_lines.extend(value.splitlines())
    result: list[str] = []
    used = 0
    for raw in raw_lines[-MAX_DIAGNOSTIC_LINES:]:
        line = raw.strip()
        if not line:
            continue
        command_echo = _redact_command_echo(
            line,
            command,
            sensitive_indexes,
            echoed_command,
        )
        line = (
            command_echo
            if command_echo is not None
            else _redact_sensitive_tokens(line, sensitive)
        )
        if command_echo is None:
            line = _UNC_PATH.sub(_REDACTED, line)
            line = _WINDOWS_PATH.sub(_REDACTED, line)
            line = _POSIX_PATH.sub(_REDACTED, line)
        line = _EMAIL.sub(_REDACTED, line)
        line = _AUTHORIZATION.sub(f"Authorization: {_REDACTED}", line)
        line = _COOKIE.sub(f"Cookie: {_REDACTED}", line)
        line = _SECRET_ASSIGNMENT.sub(_redact_secret_assignment, line)
        remaining = MAX_DIAGNOSTIC_CHARS - used
        if remaining <= 0:
            break
        line = line[:remaining]
        if line:
            result.append(line)
            used += len(line)
    return result
