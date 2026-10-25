"""Pure, byte-preserving candidate transformations for LG2 preview access."""
from __future__ import annotations

import base64
import binascii
import re


PREVIEW_PORTS = (18112, 18113)
PREVIEW_CHAIN = b"AURELIA_PREVIEW"

_SSH_REQUIRED = {
    b"allowtcpforwarding": (b"local",),
    b"allowagentforwarding": (b"no",),
    b"x11forwarding": (b"no",),
    b"permittunnel": (b"no",),
    b"passwordauthentication": (b"no",),
    b"kbdinteractiveauthentication": (b"no",),
}
_SSH_ADDITIONS = (
    (b"allowstreamlocalforwarding", b"AllowStreamLocalForwarding no", (b"no",)),
    (b"permitopen", b"PermitOpen 127.0.0.1:18112 127.0.0.1:18113",
     (b"127.0.0.1:18112", b"127.0.0.1:18113")),
    (b"permitlisten", b"PermitListen none", (b"none",)),
)
_SSH_BLOCKED_DIRECTIVES = {
    b"include", b"match", b"challengeresponseauthentication",
}
_SSH_BASE64_RE = re.compile(rb"^[A-Za-z0-9+/]+={0,2}$")

_UFW_CHAIN_DECL = b":AURELIA_PREVIEW - [0:0]"
_UFW_JUMP = (
    b"-A ufw-before-output -d 127.0.0.1 -p tcp -m multiport "
    b"--dports 18112,18113 -j AURELIA_PREVIEW"
)
_UFW_CHAIN_RULES = (
    b"-A AURELIA_PREVIEW -m owner --uid-owner 0 -j ACCEPT",
    b"-A AURELIA_PREVIEW -p tcp -m owner --uid-owner 1000 -m multiport --dports 18112 -j ACCEPT",
    b"-A AURELIA_PREVIEW -p tcp -m owner --uid-owner 1001 -m multiport --dports 18113 -j ACCEPT",
    b"-A AURELIA_PREVIEW -p tcp -j REJECT --reject-with tcp-reset",
)
_UFW_OWNED_LINES = frozenset((_UFW_CHAIN_DECL, _UFW_JUMP, *_UFW_CHAIN_RULES))


def _require_bytes(value: bytes, name: str) -> bytes:
    if not isinstance(value, bytes):
        raise TypeError(f"{name} must be bytes")
    return value


def _line_content(line: bytes) -> tuple[bytes, bytes]:
    if line.endswith(b"\r\n"):
        return line[:-2], b"\r\n"
    if line.endswith(b"\n"):
        return line[:-1], b"\n"
    return line, b""


def _ssh_directives(original: bytes) -> dict[bytes, list[tuple[bytes, ...]]]:
    directives: dict[bytes, list[tuple[bytes, ...]]] = {}
    for line in original.splitlines():
        active = line.lstrip()
        if not active or active.startswith(b"#"):
            continue
        active = active.split(b"#", 1)[0].strip()
        if not active:
            continue
        tokens = active.split()
        try:
            key = tokens[0].lower()
            values = tuple(token.lower() for token in tokens[1:])
            key.decode("ascii")
            for value in values:
                value.decode("ascii")
        except UnicodeDecodeError:
            raise ValueError("non-ASCII active SSH directive") from None
        if key in _SSH_BLOCKED_DIRECTIVES:
            raise ValueError("ambiguous SSH directive")
        if key == b"disableforwarding" and values != (b"no",):
            raise ValueError("conflicting SSH forwarding directive")
        if key == b"gatewayports" and values != (b"no",):
            raise ValueError("conflicting SSH gateway directive")
        directives.setdefault(key, []).append(values)
    return directives


def ssh_security_config_candidate(original: bytes) -> bytes:
    """Add the bounded local-forwarding policy without rewriting existing bytes."""
    original = _require_bytes(original, "original")
    directives = _ssh_directives(original)
    for key, expected in _SSH_REQUIRED.items():
        values = directives.get(key, [])
        if len(values) != 1 or values[0] != expected:
            raise ValueError(f"required SSH directive is missing or conflicting: {key.decode()}")

    additions = []
    for key, text, expected in _SSH_ADDITIONS:
        values = directives.get(key, [])
        if not values:
            additions.append(text)
        elif len(values) != 1 or values[0] != expected:
            raise ValueError(f"conflicting SSH directive: {key.decode()}")
    if not additions:
        return original

    newline = b"\r\n" if b"\r\n" in original else b"\n"
    prefix = original
    if prefix and not prefix.endswith((b"\n", b"\r")):
        prefix += newline
    return prefix + newline.join(additions) + newline


def _ssh_string(blob: bytes, offset: int) -> tuple[bytes, int]:
    if offset + 4 > len(blob):
        raise ValueError("malformed SSH public key blob")
    size = int.from_bytes(blob[offset:offset + 4], "big")
    start = offset + 4
    end = start + size
    if end > len(blob):
        raise ValueError("malformed SSH public key blob")
    return blob[start:end], end


def _validate_ed25519_public_blob(encoded: bytes) -> None:
    if not _SSH_BASE64_RE.fullmatch(encoded) or len(encoded) % 4 == 1:
        raise ValueError("malformed SSH public key encoding")
    padded = encoded + b"=" * (-len(encoded) % 4)
    try:
        blob = base64.b64decode(padded, validate=True)
        key_type, offset = _ssh_string(blob, 0)
        public, offset = _ssh_string(blob, offset)
    except (ValueError, binascii.Error):
        raise ValueError("malformed SSH public key blob") from None
    if key_type != b"ssh-ed25519" or len(public) != 32 or offset != len(blob):
        raise ValueError("expected one ssh-ed25519 public key")


def project_authorized_key_candidate(line: bytes, port: int) -> bytes:
    """Bind one restricted project key to exactly one approved loopback port."""
    line = _require_bytes(line, "line")
    if type(port) is not int or port not in PREVIEW_PORTS:
        raise ValueError("preview port is not allowed")

    content, ending = _line_content(line)
    if b"\n" in content or b"\r" in content:
        raise ValueError("authorized key must be a single line")
    old_prefix = b"restrict"
    new_prefix = f'restrict,port-forwarding,permitopen="127.0.0.1:{port}"'.encode("ascii")
    options, separator, key_fields = content.partition(b" ")
    if separator != b" " or not key_fields.startswith(b"ssh-ed25519 "):
        raise ValueError("authorized key must have the exact restricted ed25519 prefix")
    if options == old_prefix:
        output_prefix = new_prefix
    elif options == new_prefix:
        output_prefix = options
    else:
        raise ValueError("authorized key options conflict with the requested port")

    public_field = key_fields[len(b"ssh-ed25519 "):].split(None, 1)
    if not public_field:
        raise ValueError("authorized key is missing its public key")
    _validate_ed25519_public_blob(public_field[0])
    if output_prefix == options:
        return line
    return output_prefix + b" " + key_fields + ending


def normalize_ufw_before_rules(original: bytes) -> bytes:
    """Remove only complete, exact owned UFW lines for runtime comparison."""
    original = _require_bytes(original, "original")
    kept = []
    for line in original.splitlines(keepends=True):
        content, ending = _line_content(line)
        if ending in (b"\n", b"\r\n") and content in _UFW_OWNED_LINES:
            continue
        kept.append(line)
    return b"".join(kept)


def _filter_bounds(lines: list[bytes]) -> tuple[int, int]:
    contents = [_line_content(line)[0].strip() for line in lines]
    starts = [i for i, content in enumerate(contents) if content == b"*filter"]
    if len(starts) != 1:
        raise ValueError("before.rules must contain exactly one filter table")
    start = starts[0]
    end = None
    for i in range(start + 1, len(contents)):
        content = contents[i]
        if content == b"COMMIT":
            end = i
            break
        if content.startswith(b"*"):
            raise ValueError("filter table is missing COMMIT")
    if end is None:
        raise ValueError("filter table is missing COMMIT")
    return start, end


def _insert_ufw_rules(original: bytes) -> bytes:
    lines = original.splitlines(keepends=True)
    start, end = _filter_bounds(lines)
    contents = [_line_content(line)[0].strip() for line in lines]

    output_declarations = []
    declarations = []
    first_rule = None
    output_rules = []
    for i in range(start + 1, end):
        content = contents[i]
        if not content or content.startswith(b"#"):
            continue
        tokens = content.split()
        if tokens[0].startswith(b":"):
            declarations.append(i)
            if tokens[0] == b":ufw-before-output":
                output_declarations.append(i)
        if len(tokens) >= 2 and tokens[0] in (b"-A", b"-I"):
            if first_rule is None:
                first_rule = i
            if tokens[1] == b"ufw-before-output":
                if tokens[0] == b"-I":
                    raise ValueError("insert-style output rules are ambiguous")
                output_rules.append(i)

    if len(output_declarations) != 1:
        raise ValueError("before.rules must declare ufw-before-output exactly once")
    if contents[output_declarations[0]] != b":ufw-before-output - [0:0]":
        raise ValueError("ufw-before-output declaration is malformed")
    if declarations and first_rule is not None and max(declarations) > first_rule:
        raise ValueError("filter chain declarations must precede rules")

    newline = b"\r\n" if b"\r\n" in original else b"\n"
    declaration_at = first_rule if first_rule is not None else end
    jump_at = output_rules[0] if output_rules else declaration_at
    insertions: dict[int, list[bytes]] = {}
    insertions.setdefault(declaration_at, []).append(_UFW_CHAIN_DECL + newline)
    insertions.setdefault(jump_at, []).append(_UFW_JUMP + newline)
    insertions.setdefault(end, []).extend(rule + newline for rule in _UFW_CHAIN_RULES)

    result = []
    for i, line in enumerate(lines):
        result.extend(insertions.get(i, ()))
        result.append(line)
    return b"".join(result)


def _has_own_chain_reference(original: bytes) -> bool:
    return any(
        PREVIEW_CHAIN in _line_content(line)[0]
        for line in original.splitlines()
        if _line_content(line)[0].lstrip() and not _line_content(line)[0].lstrip().startswith(b"#")
    )


def ufw_before_rules_candidate(original: bytes) -> bytes:
    """Insert the exact preview owner policy, refusing partial or foreign reuse."""
    original = _require_bytes(original, "original")
    if not _has_own_chain_reference(original):
        return _insert_ufw_rules(original)

    normalized = normalize_ufw_before_rules(original)
    if normalized == original:
        raise ValueError("preview chain name is already occupied")
    expected = _insert_ufw_rules(normalized)
    if expected != original:
        raise ValueError("existing preview rules are partial, reordered, or conflicting")
    return original
