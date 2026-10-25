"""Pinned release service with explicit isolated context and graceful file stop."""
from pathlib import Path
import argparse
import hashlib
import json
import logging
import os
import re
import sys
import threading
import time

FIELDS={'schema','sourceDir','manifestDigest','home','data','materia','port','tenant','client','job','keyFile','cpuDeps'}

def validate_config(config):
    if not isinstance(config,dict) or set(config)!=FIELDS or type(config['schema']) is not int or config['schema']!=1:raise ValueError('Invalid service schema')
    if type(config['port']) is not int or not 1024<=config['port']<=65535:raise ValueError('Invalid port')
    if not isinstance(config['manifestDigest'],str) or not re.fullmatch('[0-9a-f]{64}',config['manifestDigest']):raise ValueError('Invalid product digest')
    result=dict(config)
    for name in ['sourceDir','home','data','materia','keyFile','cpuDeps']:
        value=config[name]
        if value is None and name in ['keyFile','cpuDeps']:continue
        if not isinstance(value,str) or not Path(value).is_absolute():raise ValueError('Explicit absolute path required')
        path=Path(value)
        if path.is_symlink() or path.is_junction():raise ValueError('Linked service path refused')
        result[name]=str(path.resolve())
    source=Path(result['sourceDir']);home=Path(result['home'])
    if source==home or source in home.parents or home in source.parents:raise ValueError('Home and product must be separate')
    for name in ['tenant','client','job']:
        if not isinstance(config[name],str) or not re.fullmatch('[A-Za-z0-9._-]{1,128}',config[name]):raise ValueError('Invalid scope identifier')
    return result

def verify_product(config):
    source=Path(config['sourceDir']);raw=(source/'PRODUCT_MANIFEST.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=config['manifestDigest']:raise ValueError('Product manifest drift')
    manifest=json.loads(raw);files=manifest.get('files')
    if not isinstance(files,list) or not files or len(files)>10000:raise ValueError('Invalid product manifest')
    seen=set()
    for item in files:
        rel=Path(item['path'])
        if rel.is_absolute() or '..' in rel.parts or rel.as_posix() in seen:raise ValueError('Invalid product path')
        seen.add(rel.as_posix());p=source/rel
        if p.is_symlink() or p.is_junction() or source not in p.resolve().parents or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Pinned product drift')
    return len(files)

def check_start_boundary(config):
    if (Path(config['home'])/'service.stop').exists():raise ValueError('Operator stop remains set')
    if not Path(config['data']).is_dir():raise ValueError('Configured catalog unavailable')

def environment(config,inherited=None):
    env=dict(os.environ if inherited is None else inherited)
    for name in list(env):
        if name.startswith('RADIOWORKS_'):env.pop(name)
    env.update({'RADIOWORKS_HOME':config['home'],'RADIOWORKS_DATA_DIR':config['data'],'RADIOWORKS_SCOPE_MODE':'local','RADIOWORKS_LOCAL_TENANT_ID':config['tenant'],'RADIOWORKS_LOCAL_CLIENT_ID':config['client'],'RADIOWORKS_LOCAL_JOB_ID':config['job'],'PYTHONPATH':str(Path(config['sourceDir'])/'engine/src'),'PYTHONNOUSERSITE':'1'})
    if config['cpuDeps']:env['RADIOWORKS_EXP1_CPU_DEPS']=config['cpuDeps']
    if config['keyFile']:
        from cryptography.fernet import Fernet
        value=Path(config['keyFile']).read_bytes().strip();Fernet(value);env['RADIOWORKS_JOURNAL_KEY']=value.decode('ascii')
    return env

def reserve_port(port):
    import socket
    owned=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        if os.name=='nt':owned.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        owned.bind(('127.0.0.1',port));owned.listen(128);owned.setblocking(False)
        return owned
    except BaseException:
        owned.close();raise


def lifecycle_clean(server):
    life=getattr(server,'lifespan',None)
    return bool(server.started and life and not any(getattr(life,n,True) for n in ['startup_failed','shutdown_failed','error_occurred']) and not getattr(server,'force_exit',False))


def run(config):
    from contextlib import closing
    config=validate_config(config);verify_product(config);check_start_boundary(config)
    # Reserve and retain the exact socket BEFORE app construction/recovery.
    with closing(reserve_port(config['port'])) as owned_socket:
        configured_env=environment(config)
        os.environ.clear();os.environ.update(configured_env)
        source=Path(config['sourceDir']);home=Path(config['home'])
        sys.path.insert(0,str(source/'engine/src'))
        from radiworks.runtime_lease import runtime_home_lease
        with runtime_home_lease(home/'.release-service-owner'):
            _serve(config,source,home,owned_socket)


def _serve(config,source,home,owned_socket):
    from radiworks.main import create_app
    import radiworks.main
    if Path(radiworks.main.__file__).resolve().parent!=(source/'engine/src/radiworks').resolve():raise ValueError('Foreign product import')
    import uvicorn
    app=create_app(base_dir=home,data_dir=Path(config['data']),materia_dir=Path(config['materia']),webapp_dir=source/'webapp')
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=config['port'],access_log=False,log_level='warning',lifespan='on'))
    finished=threading.Event();recorded=threading.Event();watch_errors=[]
    identity={'pid':os.getpid(),'startedEpoch':time.time(),'port':config['port'],'home':str(home),'sourceDir':str(source),'manifestDigest':config['manifestDigest'],'scope':{'tenant':config['tenant'],'client':config['client'],'job':config['job']}}
    def watch():
        try:
            while not finished.wait(.1):
                if server.started and not recorded.is_set():
                    temp=home/'service-state.json.tmp';temp.write_text(json.dumps(identity),encoding='utf-8');temp.replace(home/'service-state.json');recorded.set()
                if (home/'service.stop').exists():server.should_exit=True;return
        except BaseException as exc:
            watch_errors.append(type(exc).__name__);server.should_exit=True
    watcher=threading.Thread(target=watch,name='owned-service-stop',daemon=True);watcher.start();returned=False;clean=False
    try:
        server.run(sockets=[owned_socket]);returned=True
    finally:
        finished.set();watcher.join()
        clean=bool(returned and recorded.is_set() and not watch_errors and lifecycle_clean(server))
        if recorded.is_set():
            identity['stoppedEpoch']=time.time();identity['exitClean']=clean
            (home/'service-state.json').write_text(json.dumps(identity),encoding='utf-8')
    if not clean:raise ValueError('Service startup/shutdown did not complete cleanly')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);args=parser.parse_args()
    cfg_path=Path(args.config).resolve();config=json.loads(cfg_path.read_text(encoding='utf-8-sig'));home=Path(config['home'])
    # Logs stay in the owned home; no personal payloads or recovery keys are logged.
    validate_config(config);home.mkdir(parents=True,exist_ok=True)
    log=(home/'release-service.log').open('a',encoding='utf-8',buffering=1);sys.stdout=sys.stderr=log;logging.basicConfig(stream=log,level=logging.WARNING)
    try:run(config)
    except Exception:
        logging.exception('Release service failed');return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
