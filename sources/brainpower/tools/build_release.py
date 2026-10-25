"""Build an allowlisted source release without runtime data or credentials."""
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    root=Path(__file__).resolve().parents[1]
    import tomllib
    version=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    files=[]
    for directory in ('governor_workbench','tests','scripts','tools','docs'):
        for path in (root/directory).rglob('*'):
            if path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and path.suffix not in ('.pyc','.log'):
                files.append(path)
    for name in ('README.md','AGENTS.md','pyproject.toml','config.example.json','Start-Governor.cmd','Stop-Governor.cmd','Install-Governor.cmd'):
        files.append(root/name)
    for name in ('model_evaluation.json','model_evaluation_proposal_update.json','hybrid_review_evaluation.json','hermes_review_evaluation.json','hermes_hybrid_evaluation.json','supervisor_proposal_challenge.json'):
        path=root/'artifacts'/name
        if path.is_file(): files.append(path)
    target=root/'dist'/('GovernorWorkbench-'+version+'-Windows.zip'); target.parent.mkdir(exist_ok=True)
    manifest={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(files): archive.write(path,str(path.relative_to(root)).replace('\\','/'))
        archive.writestr('RELEASE_MANIFEST.json',json.dumps({'version':version,'files':manifest},indent=2))
    checksum=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(checksum+'  '+target.name+'\n',encoding='ascii')
    print(json.dumps({'archive':str(target),'bytes':target.stat().st_size,'files':len(files),'sha256':checksum}))


if __name__=='__main__': main()
