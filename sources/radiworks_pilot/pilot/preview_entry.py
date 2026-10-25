from pathlib import Path
from radiworks.bootstrap import bootstrap_synthetic_catalog
from radiworks.main import create_app
import uvicorn
home=Path('/runtime')
if not (home/'data').exists(): bootstrap_synthetic_catalog(home)
app=create_app(base_dir=home,webapp_dir='/source/webapp')
uvicorn.run(app,uds='/socket/backend.sock',proxy_headers=False,log_level='warning')
