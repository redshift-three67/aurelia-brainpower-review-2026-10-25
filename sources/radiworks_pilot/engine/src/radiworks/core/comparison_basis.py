"""Immutable source evidence for optional comparisons; no entropy or original mutation."""
from __future__ import annotations
import copy,hashlib,json,re
from pathlib import Path
from .. import copyguard
from ..persistence import document_digest
from ..scope import ScopeContext
from .rates import catalog_binding
from .personal_context import ContextSnapshot,ContextError
from .experimental_matrix import _catalog_payload,prepare_catalog_context,MatrixError,FORMULA_VERSION,WEIGHTS

MAX_SOURCE_BYTES=8*1024*1024
ID=re.compile(r'[0-9a-f]{32}\Z')
HASH=re.compile(r'[0-9a-f]{64}\Z')

class ComparisonBasisError(ValueError):
    pass


def capture_catalog(repository,selector,rates):
    """Do not change Original prefix rules; this experiment requires one exact file."""
    files=repository._selected_files(selector)
    if len(files)!=1:raise ComparisonBasisError('Vergleich benötigt genau einen belegten TXT-Katalog; Original-Präfixauswahl bleibt unverändert.')
    path=files[0]
    try:
        if path.is_symlink() or path.is_junction():raise ComparisonBasisError('Katalogverweise sind für den Vergleich ungeeignet.')
        raw=repository.release.read_verified(path) if repository.release else path.read_bytes()
        if len(raw)>4*1024*1024:raise ComparisonBasisError('Vergleichskatalog überschreitet 4 MiB; Original bleibt nutzbar.')
        text=raw.decode('utf-8')
        parsed=repository._parse_lines(path,text.splitlines())
        if catalog_binding(selector,parsed)!=catalog_binding(selector,rates):
            raise ComparisonBasisError('Katalog stimmt nicht mit den ursprünglich gelesenen Raten überein.')
        second=repository.release.read_verified(path) if repository.release else path.read_bytes()
        if raw!=second:raise ComparisonBasisError('Katalog wurde während der Aufnahme geändert.')
        return _catalog_payload({'name':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'content':text})
    except (OSError,UnicodeError,MatrixError) as exc:
        raise ComparisonBasisError('Katalogstand kann nicht sicher für den Vergleich aufgenommen werden.') from exc


def _checked_source(source):
    if type(source) is not dict or set(source)!={'schema','scope','caseId','sourceSessionId','contextSnapshot','catalog','baseline','passport','digest'}:
        raise ComparisonBasisError('Vergleichsquelle ist unvollständig.')
    frozen=copy.deepcopy(source)
    digest=frozen.pop('digest')
    if frozen['schema']!=1 or not isinstance(digest,str) or not HASH.fullmatch(digest) or document_digest(frozen)!=digest:
        raise ComparisonBasisError('Prüfsumme der Vergleichsquelle stimmt nicht.')
    if not isinstance(frozen['sourceSessionId'],str) or not ID.fullmatch(frozen['sourceSessionId']):raise ComparisonBasisError('Quellsitzung ist ungültig.')
    try:
        context=ContextSnapshot.from_payload(frozen['contextSnapshot']).payload()
        cat=_catalog_payload(frozen['catalog'])
    except (ContextError,MatrixError,TypeError,ValueError) as exc:raise ComparisonBasisError('Quellkontext oder Katalog ist ungültig.') from exc
    if context['caseId']!=frozen['caseId'] or context['scope']!=frozen['scope']:raise ComparisonBasisError('Quellidentität stimmt nicht.')
    baseline=frozen['baseline'];passport=frozen['passport']
    if type(baseline) is not dict or type(baseline.get('rateObjects')) is not list or not baseline['rateObjects'] or type(passport) is not dict:
        raise ComparisonBasisError('Originalgrundlage fehlt.')
    rows=baseline['rateObjects']
    if any(type(r) is not dict or type(r.get('nameOrRate')) is not str for r in rows):raise ComparisonBasisError('Originalraten sind ungültig.')
    if copyguard.digest(copyguard.visible_rate_texts(baseline))!=passport.get('copyguard_digest'):raise ComparisonBasisError('Original-CopyGuard-Bindung stimmt nicht.')
    frozen['digest']=digest
    return frozen


def make_source(session,catalog,scope):
    context=ContextSnapshot.from_payload(session['contextSnapshot']).payload()
    source={'schema':1,'scope':scope.to_dict(),'caseId':context['caseId'],'sourceSessionId':session['sessionId'],
        'contextSnapshot':context,'catalog':copy.deepcopy(catalog),'baseline':copy.deepcopy(session['analysisBaseline']),
        'passport':copy.deepcopy(session['passport'])}
    source['digest']=document_digest(source)
    checked=_checked_source(source)
    if len(json.dumps(checked,ensure_ascii=False).encode('utf-8'))>MAX_SOURCE_BYTES:raise ComparisonBasisError('Vergleichsquelle überschreitet die begrenzte Aufnahmegröße.')
    return checked


def source_reference(source):
    checked=_checked_source(source)
    return {'schema':1,'id':checked['sourceSessionId'],'digest':checked['digest']}


def read_source(directory,reference):
    if type(reference) is not dict or set(reference)!={'schema','id','digest'} or reference['schema']!=1 or type(reference['id']) is not str or not ID.fullmatch(reference['id']):
        raise ComparisonBasisError('Belegte Vergleichsquelle fehlt; bitte neue Originalanalyse starten.')
    root=Path(directory);path=root/(reference['id']+'.json')
    try:
        if root.is_symlink() or root.is_junction() or path.is_symlink() or path.is_junction() or not path.resolve().is_relative_to(root.resolve()):raise ComparisonBasisError('Vergleichsquelle besitzt einen unzulässigen Dateiverweis.')
        if path.stat().st_size>MAX_SOURCE_BYTES:raise ComparisonBasisError('Vergleichsquelle ist zu groß.')
        checked=_checked_source(json.loads(path.read_text(encoding='utf-8')))
    except (OSError,UnicodeError,ValueError,TypeError) as exc:
        if isinstance(exc,ComparisonBasisError):raise
        raise ComparisonBasisError('Vergleichsquelle kann nicht sicher gelesen werden.') from exc
    if source_reference(checked)!=reference:raise ComparisonBasisError('Vergleichsquelle passt nicht zur gespeicherten Sitzung.')
    return checked


def build_comparison_input(source,session,case,scope,*,page_start,weight,implementation_hash):
    source=_checked_source(source)
    if source_reference(source)!=session.get('comparisonBasis') or source['sourceSessionId']!=session.get('sessionId'):
        raise ComparisonBasisError('Quellsitzung und Vergleichsbeleg passen nicht zusammen.')
    if source['scope']!=scope.to_dict() or source['caseId']!=case.get('caseId') or source['contextSnapshot']!=session.get('contextSnapshot'):
        raise ComparisonBasisError('Fall-/Kontext-/Scope-Bindung stimmt nicht.')
    if source['baseline']!=session.get('analysisBaseline') or source['passport']!=session.get('passport'):
        raise ComparisonBasisError('Originalgrundlage wurde nachträglich geändert.')
    rows=source['baseline']['rateObjects']
    if type(page_start) is not int or page_start<0 or page_start%21 or page_start>=len(rows):raise ComparisonBasisError('Vergleich benötigt eine vorhandene 21er-Ergebnisseite.')
    if type(weight) is not str or weight not in WEIGHTS or type(implementation_hash) is not str or not HASH.fullmatch(implementation_hash):raise ComparisonBasisError('Vergleichsparameter sind ungültig.')
    try:prepare_catalog_context(source['contextSnapshot'],source['catalog'])
    except MatrixError as exc:raise ComparisonBasisError(str(exc)) from exc
    subset=copy.deepcopy(rows[page_start:page_start+21]);names=[r['nameOrRate'] for r in subset]
    catalogue={line.partition('\t')[0] for line in source['catalog']['content'].splitlines() if line.strip()}
    if any(not n.strip() or n not in catalogue for n in names):raise ComparisonBasisError('Originaltreffer fehlt im eingefrorenen Katalog.')
    return {'caseId':case['caseId'],'sourceSessionId':session['sessionId'],'contextSnapshot':copy.deepcopy(source['contextSnapshot']),
        'catalog':copy.deepcopy(source['catalog']),'rates':names,'originalSubset':subset,'originalProvenance':copy.deepcopy(source['passport']),
        'formulaVersion':FORMULA_VERSION,'implementationHash':implementation_hash,'weight':weight,'pageStart':page_start,'sourceDigest':source['digest']}
