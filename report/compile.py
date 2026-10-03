# -*- coding: utf-8 -*-
import subprocess, io, os, sys

XELATEX = r'C:\Program Files\MiKTeX\miktex\bin\x64\xelatex.exe'
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

runs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
log = []
for i in range(runs):
    r = subprocess.run(
        [XELATEX, '-interaction=nonstopmode', '-halt-on-error',
         '--enable-installer', 'report.tex'],
        capture_output=True, timeout=600)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace')
    log.append(f'=== run {i+1} rc={r.returncode} ===\n{out}')
    if r.returncode != 0:
        break

with io.open(os.path.join(HERE, 'compile_log.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(log))

pdf = os.path.join(HERE, 'report.pdf')
print('pdf exists:', os.path.exists(pdf),
      'size:', os.path.getsize(pdf) if os.path.exists(pdf) else 0)
