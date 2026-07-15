import os
import subprocess
import shutil
import tempfile
from pathlib import Path

root = Path(tempfile.mkdtemp(prefix='git-cherry-check-', dir='e:/Repos/release-validation-job'))
print(root)
subprocess.run(['git','init'], cwd=root, check=True, capture_output=True, text=True)
subprocess.run(['git','config','user.name','Test'], cwd=root, check=True)
subprocess.run(['git','config','user.email','test@example.com'], cwd=root, check=True)
(root/'f.txt').write_text('base\n', encoding='utf-8')
subprocess.run(['git','add','f.txt'], cwd=root, check=True)
subprocess.run(['git','commit','-m','initial'], cwd=root, check=True, capture_output=True, text=True)
subprocess.run(['git','branch','old-release'], cwd=root, check=True)
(root/'f.txt').write_text('base\nfeature\n', encoding='utf-8')
subprocess.run(['git','add','f.txt'], cwd=root, check=True)
subprocess.run(['git','commit','-m','feature'], cwd=root, check=True, capture_output=True, text=True)
sha = subprocess.run(['git','rev-parse','HEAD'], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
subprocess.run(['git','checkout','-b','current-release'], cwd=root, check=True, capture_output=True, text=True)
subprocess.run(['git','cherry-pick',sha], cwd=root, check=True, capture_output=True, text=True)
print('git cherry old current')
print(subprocess.run(['git','cherry','old-release','current-release'], cwd=root, capture_output=True, text=True).stdout)
print('git cherry current old')
print(subprocess.run(['git','cherry','current-release','old-release'], cwd=root, capture_output=True, text=True).stdout)
shutil.rmtree(root)
