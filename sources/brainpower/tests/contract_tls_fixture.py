"""Ephemeral synthetic certificates; never installs trust or prints key bytes."""
import hashlib
import os
from pathlib import Path
import secrets
import ssl
import subprocess
import sys
import tempfile


def openssl_path():
    paths = {'win32': 'C:/Program Files/Git/usr/bin/openssl.exe', 'linux': '/usr/bin/openssl'}
    if sys.platform not in paths:
        raise RuntimeError('Unsupported certificate test platform')
    path = Path(paths[sys.platform])
    if not path.is_file():
        raise RuntimeError('Required test OpenSSL unavailable; not a passing skip')
    return path


class Certificates:
    def __init__(self):
        self.openssl = openssl_path()
        self.directory = tempfile.TemporaryDirectory(prefix='aurelia-t2-')
        self.root = Path(self.directory.name)
        self.config = self.root / 'openssl-test.cnf'
        self.config.write_text('[req]\ndistinguished_name=dn\n[dn]\n', encoding='ascii')
        try:
            self.run('req', '-x509', '-newkey', 'rsa:2048', '-noenc', '-days', '1',
                     '-subj', '/CN=Aurelia Synthetic Test CA', '-keyout', 'ca.key', '-out', 'ca.pem',
                     '-addext', 'basicConstraints=critical,CA:TRUE',
                     '-addext', 'keyUsage=critical,keyCertSign,cRLSign')
            for name, usage in [('server', 'serverAuth'), ('client', 'clientAuth'),
                                ('rotated', 'clientAuth'), ('denied', 'clientAuth')]:
                self.run('req', '-new', '-newkey', 'rsa:2048', '-noenc',
                         '-subj', '/CN=' + name, '-keyout', name + '.key', '-out', name + '.csr')
                extensions = 'basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\nextendedKeyUsage=' + usage + '\n'
                if name == 'server':
                    extensions += 'subjectAltName=DNS:localhost\n'
                (self.root / (name + '.ext')).write_text(extensions, encoding='ascii')
                self.run('x509', '-req', '-in', name + '.csr', '-CA', 'ca.pem', '-CAkey', 'ca.key',
                         '-set_serial', str(secrets.randbits(120) + 1), '-days', '1',
                         '-extfile', name + '.ext', '-out', name + '.pem')
            self.run('req', '-x509', '-newkey', 'rsa:2048', '-noenc', '-days', '1',
                     '-subj', '/CN=Untrusted Synthetic Client', '-keyout', 'foreign.key', '-out', 'foreign.pem')
        except BaseException:
            self.close()
            raise

    def run(self, *args):
        result = subprocess.run([str(self.openssl), *args], cwd=self.root,
                                env={**os.environ, 'OPENSSL_CONF': str(self.config)},
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if result.returncode:
            raise RuntimeError('Synthetic certificate command failed; no raw output emitted')

    def path(self, name):
        return str(self.root / name)

    def issue_window(self, name, role, start, end):
        """Absolute validity windows; does not change the system clock."""
        ca_config = self.root / 'window-ca.cnf'
        if not ca_config.exists():
            (self.root / 'index.txt').write_text('', encoding='ascii')
            (self.root / 'serial.txt').write_text('1000\n', encoding='ascii')
            ca_config.write_text(
                '[ca]\ndefault_ca=test_ca\n[test_ca]\n'
                'database=index.txt\nserial=serial.txt\nnew_certs_dir=.\n'
                'certificate=ca.pem\nprivate_key=ca.key\ndefault_md=sha256\n'
                'policy=names\nunique_subject=no\n[names]\ncommonName=supplied\n', encoding='ascii')
        self.run('ca', '-batch', '-notext', '-config', str(ca_config),
                 '-in', role + '.csr', '-out', name + '.pem', '-extfile', role + '.ext',
                 '-startdate', start, '-enddate', end)

    def fingerprint(self, name):
        der = ssl.PEM_cert_to_DER_cert((self.root / (name + '.pem')).read_text(encoding='ascii'))
        return hashlib.sha256(der).hexdigest()

    def close(self):
        self.directory.cleanup()
