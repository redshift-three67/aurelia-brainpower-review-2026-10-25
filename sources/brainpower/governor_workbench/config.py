"""Validated portable configuration; never exposes credential values."""
from copy import deepcopy
import json
import os
from pathlib import Path
import re
from urllib.parse import urlparse

SUPERVISORS = ('gpt-5.6-sol', 'gpt-6-astra')


def validate_dependencies(projects):
    ids = [p['id'] for p in projects]
    if len(ids) != len(set(ids)):
        raise ValueError('Projekt-IDs müssen eindeutig sein.')
    graph = {p['id']: p.get('depends_on', []) for p in projects}
    def visit(key, chain):
        if key in chain: raise ValueError('Zyklische Projektabhängigkeit.')
        if key not in graph: raise ValueError('Unbekannte Projektabhängigkeit: ' + key)
        for dep in graph[key]: visit(dep, chain | {key})
    for key in ids: visit(key, set())


def load_config(path):
    path = Path(path).resolve()
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if data.get('version') != 1: raise ValueError('Konfigurationsversion muss 1 sein.')
    defaults = dict(port=8787, data_dir='runtime', monitor_interval=15, git_interval=60,
                    auto_review_cooldown=900, auto_review_daily_limit=4,
                    router_url='http://127.0.0.1:3000/v1', router_api_key_env='GOVERNOR_ROUTER_API_KEY',
                    model_timeout=120, orchestrator='gpt-5.6-terra', supervisor='gpt-5.6-sol',
                    reasoning='medium', orchestrator_transport='hermes',hermes_path='', governor_dir='', snapshot_dir='',codex_auth_path='',live_views={},chrome_path='',vault_root='',legacy_review_egress_authorized=False)
    cfg = {**defaults, **data}
    from .routing_policy import validate_mode
    cfg['reasoning_mode'] = validate_mode(cfg.get('reasoning_mode', 'medium'))
    cfg.setdefault('staging_pilot_roots', [])
    cfg.setdefault('runtime_probe_port', 8794)
    if (type(cfg['runtime_probe_port']) is not int or not 1024 <= cfg['runtime_probe_port'] <= 65535
            or cfg['runtime_probe_port'] in (3000, cfg['port'])):
        raise ValueError('Laufzeittest benötigt einen eigenen lokalen Port.')
    def expand(value):
        value = re.sub(r'\$\{(\w+)\}', lambda m: os.environ.get(m[1], m[0]), value)
        return os.path.expandvars(value)
    for key in ('data_dir','hermes_path','governor_dir','snapshot_dir','codex_auth_path','chrome_path','vault_root'):
        if cfg[key]:
            resolved = Path(expand(cfg[key])).expanduser()
            cfg[key] = str((path.parent / resolved).resolve() if not resolved.is_absolute() else resolved.resolve())
    if (not isinstance(cfg['staging_pilot_roots'],list) or len(cfg['staging_pilot_roots'])>5
            or any(not isinstance(value,str) or not Path(expand(value)).is_absolute() for value in cfg['staging_pilot_roots'])):
        raise ValueError('Maximal fünf explizite absolute Pilotverzeichnisse erforderlich.')
    cfg['staging_pilot_roots']=[os.path.abspath(expand(value)) for value in cfg['staging_pilot_roots']]
    url = urlparse(cfg['router_url'])
    if type(cfg['legacy_review_egress_authorized']) is not bool:
        raise ValueError('Legacy-Modellfreigabe muss boolesch sein.')
    if url.scheme != 'http' or url.hostname not in ('127.0.0.1','localhost','::1') or url.username or url.password or url.query or url.fragment:
        raise ValueError('Router muss eine lokale HTTP-Adresse ohne Zugangsdaten sein.')
    for key,low,high in [('port',1024,65535),('monitor_interval',5,3600),('git_interval',15,3600),
                         ('auto_review_cooldown',300,86400),('auto_review_daily_limit',1,24),('model_timeout',15,300)]:
        if type(cfg[key]) is not int or not low <= cfg[key] <= high:
            raise ValueError('Ungültiger Wert: ' + key)
    if cfg['supervisor'] not in SUPERVISORS or cfg['orchestrator'] != 'gpt-5.6-terra' or cfg['reasoning'] != 'medium':
        raise ValueError('Nicht unterstützte Modellkombination.')
    if cfg['orchestrator_transport'] not in ('hermes','router'): raise ValueError('Transport muss hermes oder router sein.')
    if cfg['orchestrator_transport']=='hermes' and (url.port!=3000 or url.path.rstrip('/')!='/v1'):
        raise ValueError('Hermes-Isolation ist an den lokalen Router auf Port 3000/v1 gebunden.')
    projects = cfg.get('projects')
    if not isinstance(projects,list) or len(projects)>50: raise ValueError('Projekte müssen eine Liste mit maximal 50 Einträgen sein.')
    for p in projects:
        if not re.fullmatch(r'[a-z0-9_\-]{1,64}', p.get('id','')): raise ValueError('Ungültige Projekt-ID.')
        if not isinstance(p.get('name'),str) or not p['name'].strip(): raise ValueError('Projektname fehlt.')
        raw = expand(p.get('path',''))
        if not raw: raise ValueError('Existierendes Projekt benötigt einen Pfad.')
        target = Path(raw).expanduser()
        p['path'] = str((path.parent/target).resolve() if not target.is_absolute() else target.resolve())
        p.setdefault('kind','existing'); p.setdefault('gate','Nicht freigegeben')
        p.setdefault('status','Prüfung offen'); p.setdefault('next_step','Quellen und Gate prüfen.')
        p.setdefault('depends_on',[])
    validate_dependencies(projects)
    if not isinstance(cfg['live_views'],dict) or len(cfg['live_views'])>10: raise ValueError('Maximal zehn konfigurierte Live-Testziele.')
    used_ports = {}
    for key,value in cfg['live_views'].items():
        if (key not in [p['id'] for p in projects]+['governor'] or not isinstance(value,dict)
                or not {'url'} <= set(value) <= {'url', 'expected_openapi_title'}
                or not isinstance(value['url'], str)):
            raise ValueError('Ungültiges Live-Testziel.')
        title = value.get('expected_openapi_title')
        if title is not None and (not isinstance(title, str) or not title.strip() or len(title) > 120
                                  or any(ord(char) < 32 for char in title)):
            raise ValueError('Ungültiger OpenAPI-Titel für das Live-Testziel.')
        target=urlparse(value['url'])
        if target.scheme!='http' or target.hostname not in ('127.0.0.1','localhost','::1') or not target.port or target.port==3000 or target.username or target.password or target.fragment:
            raise ValueError('Live-Testziel muss ein lokaler HTTP-Testport sein; Router-Port 3000 ist ausgeschlossen.')
        if target.port in used_ports:
            raise ValueError(f'Live-Testziele benötigen eigene Ports: Port {target.port} gehört bereits zu {used_ports[target.port]}.')
        if key != 'governor' and target.port in (cfg['port'], cfg['runtime_probe_port']):
            raise ValueError(f'Live-Testziel {key} nutzt reservierten Port {target.port}.')
        used_ports[target.port] = key
    cfg['_config_path'] = str(path)
    return deepcopy(cfg)
