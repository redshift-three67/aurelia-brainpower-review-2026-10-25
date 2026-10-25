"""Parse the NUL-delimited porcelain-v2 contract, with rename detection disabled."""
import json
import re


def parse_status(raw):
    if not raw.endswith('\0') or '\ufffd' in raw:
        raise ValueError('Git-Status ist unvollständig oder nicht eindeutig UTF-8.')
    head=None;branch=None;entries={};conflict=False
    for record in raw.split('\0')[:-1]:
        if record.startswith('# branch.oid '):
            if head is not None:raise ValueError('Mehrdeutiger Git-HEAD.')
            head=record[13:]
            if head=='(initial)':head=''
            elif not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}',head):raise ValueError('Ungültiger Git-HEAD.')
        elif record.startswith('# branch.head '):
            if branch is not None:raise ValueError('Mehrdeutiger Git-Zweig.')
            branch=record[14:];branch='' if branch=='(detached)' else branch
        elif record.startswith('# '):continue
        elif record.startswith(('1 ','u ')):
            fields=record.split(' ',8 if record.startswith('1 ') else 10)
            if len(fields)!=(9 if record.startswith('1 ') else 11):raise ValueError('Ungültiger Git-Eintrag.')
            xy,path=fields[1],fields[-1]
            if not re.fullmatch(r'[.MTADRCU]{2}',xy) or not path or path in entries:
                raise ValueError('Mehrdeutiger Git-Pfadstatus.')
            if path.startswith('/') or '\\' in path or '..' in path.split('/') or ':' in path:
                raise ValueError('Git-Pfad verlässt den Arbeitsbaum.')
            entries[path]=xy;conflict|=record.startswith('u ')
        else:raise ValueError('Nicht unterstützter Git-Statuseintrag.')
    if head is None or branch is None:raise ValueError('Git-Zweigmetadaten fehlen.')
    paths=sorted(entries)
    # Preserve a readable, header-free dirty-worktree indicator.
    status='\n'.join(entries[p].replace('.',' ')+' '+json.dumps(p,ensure_ascii=False) for p in paths)
    staged={p for p in paths if p.startswith('project_memories/') and entries[p][0]!='.'}
    return dict(head=head,branch=branch,status=status,names=paths,staged=staged,conflict=conflict)
