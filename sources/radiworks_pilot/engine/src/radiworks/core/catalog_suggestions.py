"""Pure lexical catalog evidence; no numeric analysis, IO or semantic inference."""
from __future__ import annotations
import re
import unicodedata
from ..copyguard import check_text

RULE_VERSION = 'catalog-lexical-v1'
GROUPS = (
 ('HOMEOPATHY', 'Homeopathie'), ('BIOLOGICAL', 'Biologisch'),
 ('SYMBOLISM', 'Symbolik'), ('ESSENCES', 'Essenzen'), ('CHEMICAL', 'Chemie'),
 ('ENERGY', 'Energie'), ('AGRICULTURE', 'Agriculture'), ('ANALYSIS', 'Analyse-Raten'),
)
STOPWORDS = frozenset('der die das den dem des ein eine einer eines einem einen und oder aber mit ohne fur von zum zur aus auf bei nach vor uber unter durch ist sind sein als auch nur nicht sich im in am an zu es um the and or with without for from to of on at by is are be a an this that'.split())
WORDS = re.compile(r'[^\W\d_]+', re.UNICODE)

def _normalized(value: str) -> str:
 return ''.join(c for c in unicodedata.normalize('NFKD',value) if not unicodedata.combining(c)).casefold()

def _words(value: str) -> list[str]:
 return WORDS.findall(_normalized(value))

def _safe(value: str) -> bool:
 if any(unicodedata.category(c) in ('Cc','Cf','Cs') for c in value): return False
 return check_text(value)[0] == 'allow' and check_text(' '.join(_words(value)))[0] == 'allow'

def _term_set(value: str) -> set[str]:
 return {word for word in _words(value) if len(word)>=3 and word not in STOPWORDS}

def query_terms(focus: str, topics: str) -> list[str]:
 if any(type(value) is not str or len(value)>240 or not _safe(value) for value in (focus,topics)):
  raise ValueError('Suchbegriffe nicht nutzbar.')
 terms=list(dict.fromkeys(word for value in (focus,topics) for word in _words(value)
                          if len(word)>=3 and word not in STOPWORDS))
 if len(terms)>12: raise ValueError('Zu viele Suchbegriffe.')
 return terms

def rank_catalog(documents: list[dict], terms: list[str], limit: int = 8) -> dict:
 if type(limit) is not int or not 1<=limit<=8: raise ValueError('Ungültige Vorschlagsgrenze.')
 if type(terms) is not list or len(terms)>12 or any(type(t) is not str for t in terms):
  raise ValueError('Ungültige Suchbegriffe.')
 if not terms: return {'totalMatches':0,'suggestions':[]}
 results=[]
 for document in documents:
  name,text=document.get('name'),document.get('text')
  if type(name) is not str or type(text) is not str: raise ValueError('Ungültige Katalogquelle.')
  if not _safe(name): continue
  name_set=_term_set(name)
  group_set=set()
  for prefix,label in GROUPS:
   if name.startswith(prefix): group_set=_term_set(label);break
  rate_set=set();matched_lines=0
  for line in text.splitlines():
   rate=line.split('\t',1)[0].strip()
   if not rate or not _safe(rate): continue
   matches=_term_set(rate).intersection(terms)
   if matches: matched_lines+=1;rate_set.update(matches)
  name_terms=[word for word in terms if word in name_set]
  group_terms=[word for word in terms if word in group_set]
  rate_terms=[word for word in terms if word in rate_set]
  coverage=len(set(name_terms+group_terms+rate_terms))
  if not coverage: continue
  item={'name':name,'selector':name+'.txt','nameTerms':name_terms,'groupTerms':group_terms,
        'rateTerms':rate_terms,'matchedRateCount':matched_lines}
  results.append(((-coverage,-len(name_terms),-len(group_terms),-len(rate_terms),name.casefold(),name),item))
 results.sort(key=lambda pair:pair[0])
 return {'totalMatches':len(results),'suggestions':[item for _,item in results[:limit]]}
