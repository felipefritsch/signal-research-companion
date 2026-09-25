"""Execute notebooks with this Python, then export self-contained HTML previews."""
from pathlib import Path
import json
import os
import sys
import subprocess
import tempfile
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from traitlets.config import Config
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/notebooks'
OUT.mkdir(exist_ok=True,parents=True)
with tempfile.TemporaryDirectory() as tmp:
	kernel=Path(tmp)/'kernels/signal-study';kernel.mkdir(parents=True)
	(kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Signal study','language':'python'}))
	os.environ['JUPYTER_PATH']=tmp
	os.environ['IPYTHONDIR']=str(Path(tmp)/'ipython')
	os.environ['MPLCONFIGDIR']=str(Path(tmp)/'matplotlib')
	os.environ['JUPYTER_RUNTIME_DIR']=str(Path(tmp)/'runtime')
	if '--export-only' not in sys.argv:
		# Build the disposable font cache before the first notebook, so setup
		# progress is not saved as an alarming-looking notebook error output.
		subprocess.run([sys.executable,'-c','import matplotlib.font_manager'],check=True)
	for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
		nb=nbformat.read(path,as_version=4);nbformat.validate(nb)
		config=Config()
		config.KernelManager.transport='ipc'
		# These offline notebooks spawn no child jobs. Stop only their own kernel
		# after completed cells, avoiding macOS-wide process enumeration at shutdown.
		if '--export-only' not in sys.argv:
			NotebookClient(nb,timeout=120,kernel_name='signal-study',shutdown_kernel='immediate',config=config,resources={'metadata':{'path':str(ROOT)}}).execute()
			nbformat.write(nb,path)
		body,_=HTMLExporter().from_notebook_node(nb)
		soup=BeautifulSoup(body,'html.parser')
		style=soup.new_tag('style')
		style.string='.jp-CodeCell pre { white-space: pre-wrap !important; overflow-wrap: anywhere; }'
		soup.head.append(style)
		for link in soup.find_all('a',href=True):
			href=link['href']; parsed=urlsplit(href)
			if not parsed.scheme and parsed.path and not href.startswith('//'):
				target=(path.parent/unquote(parsed.path)).resolve()
				link['href']=os.path.relpath(target,OUT)+('#'+parsed.fragment if parsed.fragment else '')
		(OUT/(path.stem+'.html')).write_text(str(soup))
		print('Exported saved notebook:' if '--export-only' in sys.argv else 'Executed and exported:',path.name,flush=True)
