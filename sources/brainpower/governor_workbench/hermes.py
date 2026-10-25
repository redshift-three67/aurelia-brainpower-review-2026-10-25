"""Bounded Hermes availability probe, without launching an agent session."""
from pathlib import Path
import re
import subprocess
import json
import os
import tempfile
import time


class HermesAdapter:
    def prompt_limit(self, model):
        from .model_usage import HERMES_PROMPT_CHARS
        return HERMES_PROMPT_CHARS

    def __init__(self, path, workspace=None, codex_auth_path=None, timeout=120):
        self.path = Path(path)
        self.workspace = Path(workspace).resolve() if workspace else None
        self.codex_auth_path = Path(codex_auth_path).resolve() if codex_auth_path else None
        self.timeout = max(1, min(float(timeout), 120))

    def check(self):
        result = {'available': False, 'path': str(self.path), 'version': None,
                  'no_tools_review_supported': False,
                  'note': 'Version probe only. Isolated zero-tool reviews require an explicit workspace and authentication path.'}
        if not self.path.is_file():
            return result
        executable = self.path
        if executable.suffix.lower() in ('.cmd', '.bat'):
            # Resolve only the known sibling installation; never execute batch content through a shell.
            executable = self.path.parent.parent / 'hermes-agent' / 'venv' / 'Scripts' / 'hermes.exe'
        if not executable.is_file() or executable.suffix.lower() != '.exe':
            return result
        try:
            process = subprocess.run([str(executable), '--version'], capture_output=True, text=True,
                                     timeout=15, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            match = re.search(r'\b\d+\.\d+(?:\.\d+)?(?:[-+][\w.]+)?\b', process.stdout[:2000])
            result['available'] = process.returncode == 0
            result['version'] = match.group(0) if match else None
            if process.returncode:
                result['note'] = 'Hermes version probe failed; raw process output withheld.'
        except (OSError, subprocess.SubprocessError):
            result['note'] = 'Hermes version probe failed or timed out; raw process output withheld.'
        return result

    def review(self, prompt, model='gpt-5.6-terra', reasoning='medium', on_event=None, cancel_event=None, probe_only=False):
        from .routing_policy import validate_effort
        validate_effort(model, reasoning)
        if not self.workspace or not self.codex_auth_path:
            raise RuntimeError('Hermes review requires an explicit workspace and existing Codex auth path.')
        from .model_usage import check_prompt
        check_prompt(prompt, self, model)
        source = self.path.parent.parent / 'hermes-agent' if self.path.suffix.lower() in ('.cmd', '.bat') else self.path.parents[2]
        python = source / 'venv' / 'Scripts' / 'python.exe'
        if not python.is_file() or not (source / 'run_agent.py').is_file():
            raise RuntimeError('Hermes Python API installation is unavailable.')
        from .llm import ModelCancelled
        if cancel_event is not None and cancel_event.is_set():
            raise ModelCancelled('Hermes review cancelled.')
        if on_event:
            on_event({'type': 'model', 'model': model, 'message': 'Starting isolated zero-tool Hermes review'})
        runtime_dir = self.workspace / 'artifacts' / 'hermes-runs'
        runtime_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='review-', dir=runtime_dir) as temporary:
            home = Path(temporary)
            config = {'model': {'default': model, 'context_length': 128000}, 'toolsets': [],
                      'agent': {'disabled_toolsets': ['all'], 'environment_probe': False, 'api_max_retries': 1,
                                'intent_ack_continuation': False, 'stall_guards': False},
                      'plugins': {'enabled': []}, 'mcp_servers': {}, 'fallback_providers': [],
                      'compression': {'enabled': False}, 'memory': {'memory_enabled': False, 'user_profile_enabled': False}}
            (home / 'config.yaml').write_text(json.dumps(config), encoding='utf-8')
            env = {key: value for key, value in os.environ.items() if key.upper() in ('SYSTEMROOT', 'WINDIR', 'PATH', 'COMSPEC', 'PATHEXT')}
            env.update({'HERMES_HOME': str(home), 'HOME': str(home), 'USERPROFILE': str(home), 'TEMP': str(home), 'TMP': str(home),
                        'HERMES_SAFE_MODE': '1', 'HERMES_IGNORE_RULES': '1', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': 'utf-8'})
            request = {'home': str(home), 'source': str(source), 'codex_auth_path': str(self.codex_auth_path),
                       'model': model, 'reasoning': reasoning, 'prompt': prompt, 'probe_only': probe_only}
            process = subprocess.Popen([str(python), '-B', str(Path(__file__).with_name('hermes_runner.py'))],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, encoding='utf-8', cwd=home, env=env,
                                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            started = time.monotonic()
            sent = False
            try:
                while True:
                    if cancel_event is not None and cancel_event.is_set():
                        raise ModelCancelled('Hermes review cancelled; upstream inference may already have started.')
                    if time.monotonic() - started > self.timeout:
                        raise RuntimeError('Hermes isolated review timed out.')
                    try:
                        stdout, _ = process.communicate(json.dumps(request, ensure_ascii=False) if not sent else None, timeout=.2)
                        break
                    except subprocess.TimeoutExpired:
                        sent = True
                prefix = 'GOVERNOR_HERMES_RESULT='
                lines = [line[len(prefix):] for line in stdout.splitlines() if line.startswith(prefix)]
                if process.returncode or len(lines) != 1:
                    raise RuntimeError('Hermes helper failed; process output withheld.')
                result = json.loads(lines[0])
                if not result.get('success'):
                    raise RuntimeError(result.get('error', 'Hermes isolated review failed.'))
                return result
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate(timeout=5)
