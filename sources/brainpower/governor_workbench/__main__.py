"""Portable CLI: initialize, diagnose, serve, stop and export local evidence."""
import argparse
from contextlib import contextmanager
from http.cookiejar import CookieJar
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import time
import urllib.request
from .config import load_config
from .evidence import Observer, now


@contextmanager
def instance_lock(folder):
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    stream=(folder/'instance.lock').open('a+b')
    stream.seek(0,2)
    if stream.tell()==0: stream.write(b'0'); stream.flush()
    stream.seek(0)
    try:
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except (OSError,BlockingIOError):
        stream.close(); raise RuntimeError('Governor für diesen Datenordner läuft bereits.')
    try: yield
    finally:
        stream.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
        stream.close()


def main(argv=None):
    parser=argparse.ArgumentParser(description='Lokale Governor Workbench')
    parser.add_argument('command',choices=['init','doctor','serve','stop','export'],nargs='?',default='serve')
    parser.add_argument('--config',default='config.local.json')
    parser.add_argument('--template',default='config.example.json')
    parser.add_argument('--output',default='artifacts/governor-evidence.json')
    args=parser.parse_args(argv)
    try:
        if args.command=='init':
            target=Path(args.config)
            if target.exists():
                print('Vorhandene Konfiguration beibehalten: '+str(target.resolve())); return 0
            shutil.copyfile(args.template,target)
            load_config(target)
            print('Konfiguration angelegt. Pfade auf diesem PC prüfen: '+str(target.resolve())); return 0
        cfg=load_config(args.config)
        if args.command=='doctor':
            from .hermes import HermesAdapter
            projects=[dict(id=p['id'],path=p['path'],exists=Path(p['path']).is_dir()) for p in cfg['projects']]
            with socket.socket() as sock:
                available=sock.connect_ex(('127.0.0.1',cfg['port']))!=0
            result=dict(time=now(),python=sys.version.split()[0],git=shutil.which('git'),
                        hermes=HermesAdapter(cfg['hermes_path']).check(),projects=projects,
                        port=cfg['port'],port_free=available,
                        codex_auth_file_present=bool(cfg.get('codex_auth_path')) and Path(cfg['codex_auth_path']).is_file(),
                        router_url=cfg['router_url'],note='Keine Inferenz oder Produktänderung durchgeführt.')
            print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['git'] and all(p['exists'] for p in projects) else 1
        if args.command=='stop':
            origin='http://127.0.0.1:'+str(cfg['port'])
            opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
            with opener.open(origin+'/api/state',timeout=5) as r: state=json.load(r)
            request=urllib.request.Request(origin+'/api/shutdown',data=b'{}',headers={
                'Content-Type':'application/json','Origin':origin,'X-CSRF-Token':state['csrf_token']})
            with opener.open(request,timeout=5) as r: r.read()
            for _ in range(120):
                # The server closes its socket before releasing this lock. A socket
                # timeout/WSAEWOULDBLOCK alone is not termination evidence on Windows.
                try:
                    with instance_lock(cfg['data_dir']): pass
                except RuntimeError: pass
                else:
                    print('Governor beendet.'); return 0
                time.sleep(.25)
            raise RuntimeError('Shutdown angefordert, aber Dienstport noch aktiv.')
        if args.command=='export':
            value=Observer(cfg).scan(force_git=True)
            target=Path(args.output); target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
            print(str(target.resolve())); return 0
        with instance_lock(cfg['data_dir']):
            from .server import make_server
            server=make_server(cfg)
            print('Governor Workbench: http://127.0.0.1:'+str(server.server_port),flush=True)
            try: server.serve_forever(poll_interval=.5)
            except KeyboardInterrupt: pass
            finally: server.app.close(); server.server_close()
        return 0
    except (OSError,ValueError,RuntimeError) as e:
        print('Governor: '+str(e),file=sys.stderr); return 1


if __name__=='__main__': raise SystemExit(main())
