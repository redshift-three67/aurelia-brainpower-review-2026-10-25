from __future__ import annotations

import base64
import struct
import unittest

from tools.server import lg2_preview_candidates as candidates


def _fake_ed25519_blob() -> bytes:
    key_type = b"ssh-ed25519"
    public = bytes(range(32))
    wire = struct.pack(">I", len(key_type)) + key_type + struct.pack(">I", len(public)) + public
    return base64.b64encode(wire)


SSH_CONFIG = (
    b"# keep this comment byte-for-byte \xff\r\n"
    b"PasswordAuthentication no\r\n"
    b"AllowTcpForwarding local\r\n"
    b"KbdInteractiveAuthentication no\r\n"
    b"X11Forwarding no\r\n"
    b"Subsystem sftp internal-sftp\r\n"
    b"AllowAgentForwarding no\r\n"
    b"PermitTunnel no\r\n"
)

SSH_ADDITIONS = (
    b"AllowStreamLocalForwarding no",
    b"PermitOpen 127.0.0.1:18112 127.0.0.1:18113",
    b"PermitListen none",
)

UFW_BEFORE = (
    b"# retained before.rules bytes \xff\n"
    b"*filter\n"
    b":ufw-before-input - [0:0]\n"
    b":ufw-before-output - [0:0]\n"
    b":ufw-before-forward - [0:0]\n"
    b"-A ufw-before-input -i lo -j ACCEPT\n"
    b"-A ufw-before-output -o lo -j ACCEPT\n"
    b"-A ufw-before-output -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT\n"
    b"-A ufw-before-output -j ufw-user-output\n"
    b"COMMIT\n"
    b"*nat\n"
    b":OUTPUT ACCEPT [0:0]\n"
    b"COMMIT\n"
)

UFW_JUMP = (
    b"-A ufw-before-output -d 127.0.0.1 -p tcp -m multiport "
    b"--dports 18112,18113 -j AURELIA_PREVIEW"
)

UFW_RULES = (
    b"-A AURELIA_PREVIEW -m owner --uid-owner 0 -j ACCEPT",
    b"-A AURELIA_PREVIEW -p tcp -m owner --uid-owner 1000 -m multiport --dports 18112 -j ACCEPT",
    b"-A AURELIA_PREVIEW -p tcp -m owner --uid-owner 1001 -m multiport --dports 18113 -j ACCEPT",
    b"-A AURELIA_PREVIEW -p tcp -j REJECT --reject-with tcp-reset",
)


class SSHConfigCandidateTests(unittest.TestCase):
    def test_adds_only_required_directives_and_preserves_original_bytes(self):
        result = candidates.ssh_security_config_candidate(SSH_CONFIG)

        self.assertTrue(result.startswith(SSH_CONFIG))
        active = [line.split(b"#", 1)[0].strip() for line in result.splitlines()]
        for directive in SSH_ADDITIONS:
            with self.subTest(directive=directive):
                self.assertEqual(active.count(directive), 1)
        self.assertEqual(candidates.ssh_security_config_candidate(result), result)

    def test_refuses_missing_duplicated_or_conflicting_security_directives(self):
        bad_configs = (
            SSH_CONFIG.replace(b"AllowTcpForwarding local", b"AllowTcpForwarding yes"),
            SSH_CONFIG + b"AllowTcpForwarding yes\n",
            SSH_CONFIG + b"PermitOpen any\n",
            SSH_CONFIG + b"ChallengeResponseAuthentication yes\n",
            SSH_CONFIG + b"Match User preview\n",
            SSH_CONFIG + b"Include /etc/ssh/sshd_config.d/*.conf\n",
        )
        for config in bad_configs:
            with self.subTest(config=config), self.assertRaises(ValueError):
                candidates.ssh_security_config_candidate(config)


class AuthorizedKeyCandidateTests(unittest.TestCase):
    def setUp(self):
        self.public_blob = _fake_ed25519_blob()
        self.suffix = b" ssh-ed25519 " + self.public_blob + b" synthetic role comment \xff\r\n"
        self.source = b"restrict" + self.suffix

    def test_adds_only_allowed_port_and_preserves_public_key_and_comment_bytes(self):
        for port in (18112, 18113):
            with self.subTest(port=port):
                result = candidates.project_authorized_key_candidate(self.source, port)
                prefix = f'restrict,port-forwarding,permitopen="127.0.0.1:{port}"'.encode("ascii")
                self.assertEqual(result, prefix + self.suffix)
                self.assertEqual(candidates.project_authorized_key_candidate(result, port), result)

    def test_rejects_unapproved_port_malformed_line_and_conflicting_options(self):
        bad_lines = (
            b"no-agent-forwarding" + self.suffix,
            b"restrict ssh-rsa " + self.public_blob + b" synthetic\n",
            b"restrict ssh-ed25519\n" + self.public_blob + b" synthetic\n",
            b"restrict ssh-ed25519 " + self.public_blob + b"\nextra\n",
        )
        with self.assertRaises(ValueError):
            candidates.project_authorized_key_candidate(self.source, 22)
        for line in bad_lines:
            with self.subTest(line=line), self.assertRaises(ValueError):
                candidates.project_authorized_key_candidate(line, 18112)

    def test_refuses_changing_an_already_bound_port(self):
        bound = candidates.project_authorized_key_candidate(self.source, 18112)
        with self.assertRaises(ValueError):
            candidates.project_authorized_key_candidate(bound, 18113)


class UFWBeforeRulesCandidateTests(unittest.TestCase):
    def test_declares_chain_jumps_before_loopback_and_preserves_other_tables(self):
        result = candidates.ufw_before_rules_candidate(UFW_BEFORE)
        lines = result.splitlines()
        declaration = lines.index(b":AURELIA_PREVIEW - [0:0]")
        jump = lines.index(UFW_JUMP)
        output_rules = [i for i, line in enumerate(lines) if line.startswith(b"-A ufw-before-output ")]
        loopback = lines.index(b"-A ufw-before-output -o lo -j ACCEPT")
        established = lines.index(b"-A ufw-before-output -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT")
        commit = lines.index(b"COMMIT")

        self.assertLess(declaration, jump)
        self.assertEqual(output_rules[0], jump)
        self.assertLess(jump, loopback)
        self.assertLess(jump, established)
        self.assertEqual(lines[commit - len(UFW_RULES):commit], list(UFW_RULES))
        self.assertEqual(candidates.normalize_ufw_before_rules(result), UFW_BEFORE)
        self.assertEqual(candidates.ufw_before_rules_candidate(result), result)

    def test_uid_specific_multiport_rules_declare_tcp_protocol(self):
        lines = candidates.ufw_before_rules_candidate(UFW_BEFORE).splitlines()
        for rule in UFW_RULES[1:3]:
            with self.subTest(rule=rule):
                self.assertIn(rule, lines)
                self.assertIn(b" -p tcp ", rule)

    def test_reject_tcp_reset_rule_declares_tcp_protocol(self):
        lines = candidates.ufw_before_rules_candidate(UFW_BEFORE).splitlines()
        reject_rule = UFW_RULES[-1]
        self.assertIn(reject_rule, lines)
        self.assertIn(b" -p tcp ", reject_rule)

    def test_refuses_foreign_partial_or_reordered_chain_ownership(self):
        foreign = UFW_BEFORE.replace(
            b":ufw-before-output - [0:0]\n",
            b":ufw-before-output - [0:0]\n:AURELIA_PREVIEW - [0:0]\n-A AURELIA_PREVIEW -j ACCEPT\n",
        )
        partial = UFW_BEFORE.replace(
            b":ufw-before-output - [0:0]\n",
            b":ufw-before-output - [0:0]\n:AURELIA_PREVIEW - [0:0]\n",
        )
        valid = candidates.ufw_before_rules_candidate(UFW_BEFORE)
        reordered = valid.replace(UFW_JUMP + b"\n", b"", 1) + UFW_JUMP + b"\n"
        for source in (foreign, partial, reordered):
            with self.subTest(source=source), self.assertRaises(ValueError):
                candidates.ufw_before_rules_candidate(source)

    def test_rejects_malformed_before_rules_and_normalizer_removes_only_exact_lines(self):
        for malformed in (
            UFW_BEFORE.replace(b":ufw-before-output - [0:0]\n", b""),
            UFW_BEFORE.replace(b"COMMIT\n", b"", 1),
            UFW_BEFORE.replace(b"*filter\n", b"*filter\n*filter\n", 1),
        ):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                candidates.ufw_before_rules_candidate(malformed)

        valid = candidates.ufw_before_rules_candidate(UFW_BEFORE)
        near_match = b"-A AURELIA_PREVIEW -j ACCEPT \n" + valid
        normalized = candidates.normalize_ufw_before_rules(near_match)
        self.assertTrue(normalized.startswith(b"-A AURELIA_PREVIEW -j ACCEPT \n"))
        self.assertEqual(normalized[len(b"-A AURELIA_PREVIEW -j ACCEPT \n"):], UFW_BEFORE)


if __name__ == "__main__":
    unittest.main()
