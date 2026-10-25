
"""Local synthetic focus PNG bounds, persistent bytes and historical reference."""
import base64, hashlib, struct, zlib
from pathlib import Path
import pytest
from radiworks.api.routes import STATE

def chunk(kind,data):
 return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
def png(width=2,height=2,*,extra=b'',raw=None):
 header=struct.pack('>IIBBBBB',width,height,8,6,0,0,0)
 pixels=raw if raw is not None else (b'\x00'+b'\x10\x20\x30\xff'*width)*height
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',header)+extra+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b'')
def upload(home,data):
 return home.post('/context-images',json={'pngBase64':base64.b64encode(data).decode('ascii')})

def test_focus_image_upload_read_is_idempotent_and_named_by_content(home):
 data=png()
 first=upload(home,data)
 assert first.status_code==200,first.text
 expected={'sha256':hashlib.sha256(data).hexdigest(),'mediaType':'image/png','byteLength':len(data)}
 assert first.json()['image']==expected
 assert upload(home,data).json()==first.json()
 response=home.get('/context-images/'+expected['sha256'])
 assert response.status_code==200
 assert response.content==data
 assert response.headers['x-content-type-options']=='nosniff'
 assert response.headers['cache-control']=='no-store'
 assert len(list(STATE.state.case_store.cases_dir.rglob('*.png')))==1

@pytest.mark.parametrize('data',[
 b'<svg/>',png(extra=chunk(b'eXIf',b'secret')),png(extra=chunk(b'tEXt',b'Person\x00Name')),
 png(extra=chunk(b'acTL',struct.pack('>II',2,0))),
 png(width=1025,height=1),png(raw=b'\x00\x10'),png()+b'trailing',
 png()[:-1]+b'X',png(raw=b'\x05'+b'\x00'*8+b'\x00'+b'\x00'*8),
])
def test_invalid_focus_images_never_persist(home,data):
 response=upload(home,data)
 assert response.status_code==422,response.text
 assert list(STATE.state.case_store.cases_dir.rglob('*.png'))==[]

@pytest.mark.parametrize('body',[{'pngBase64':'!!!'},{'pngBase64':False},{'pngBase64':'','path':'../escape'},{'pngBase64':'YQ=='}])
def test_bad_upload_payload_has_controlled_error(home,body):
 assert home.post('/context-images',json=body).status_code==422

def test_focus_image_body_bounded(home):
 assert home.post('/context-images',content=b'x'*6_667_000,headers={'Content-Type':'application/json'}).status_code==413

def test_focus_image_reference_survives_read_and_later_context_edit(home):
 ref=upload(home,png()).json()['image']
 create=home.post('/cases',json={'name':'Synthetic Focus Image','personalContext':{'image':ref}})
 assert create.status_code==200
 analyzed=home.post('/analysis',json={'database':'HOMEOPATHY_Test','mode':'seeded','seed':42}).json()
 assert analyzed['draft']['contextSnapshot']['context']['personal']['image']==ref
 currentref=home.get('/cases/current/ref').json()['ref']
 edited=home.post('/cases/current/metadata',json={'expected_case_ref':currentref,'expected_context_version':1,'personalContext':{'image':None}})
 assert edited.status_code==200
 assert edited.json()['sessionList'][0]['contextSnapshot']['context']['personal']['image']==ref
 assert home.get('/context-images/'+ref['sha256']).status_code==200

@pytest.mark.parametrize('sha',['../elsewhere','G'*64,'a'*63,'a'*64])
def test_unavailable_or_invalid_image_never_falls_back(home,sha):
 assert home.get('/context-images/'+sha).status_code in (404,422)



def test_store_scope_isolation_and_fresh_instance_restore(tmp_path):
 from radiworks.core.context_images import ContextImageStore
 from radiworks.scope import ScopeContext
 base=tmp_path/'cases'
 base.mkdir()
 alpha=ScopeContext('tenant-a','client-a','job-a')
 beta=ScopeContext('tenant-b','client-a','job-a')
 first=ContextImageStore(base,alpha)
 reference=first.put(png())
 assert ContextImageStore(base,alpha).get(reference['sha256'])==png()
 with pytest.raises(FileNotFoundError):
  ContextImageStore(base,beta).get(reference['sha256'])
 assert ContextImageStore(base,beta).put(png())==reference
 assert len(list(base.rglob('*.png')))==2

def test_corrupted_store_content_rejected_without_overwrite(tmp_path):
 from radiworks.core.context_images import ContextImageStore,ContextImageError
 from radiworks.scope import ScopeContext
 base=tmp_path/'cases'
 base.mkdir()
 store=ContextImageStore(base,ScopeContext('tenant-a','client-a','job-a'))
 ref=store.put(png())
 target=next(base.rglob('*.png'))
 target.write_bytes(b'corrupt')
 with pytest.raises(ContextImageError): store.get(ref['sha256'])
 with pytest.raises(ContextImageError): store.put(png())
 assert target.read_bytes()==b'corrupt'

def test_png_decompression_bomb_is_bounded(home):
 assert upload(home,png(raw=b'\x00'*8_000_000)).status_code==422
 assert list(STATE.state.case_store.cases_dir.rglob('*.png'))==[]
