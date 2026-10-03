# -*- coding: utf-8 -*-
"""Отрисовка рисунков для отчёта программой graphviz."""
import subprocess
import io
import os

DOT = r'C:\Program Files\Graphviz\bin\dot.exe'
NEATO = r'C:\Program Files\Graphviz\bin\neato.exe'
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, 'fig'), exist_ok=True)

full_dot = '''graph G {
  node [shape=circle, fontname="Times New Roman", fontsize=14];
  edge [fontname="Times New Roman", fontsize=13];
  0 -- 1 [label="4"];
  0 -- 2 [label="2"];
  1 -- 2 [label="1"];
  1 -- 3 [label="5"];
  2 -- 3 [label="8"];
  2 -- 4 [label="10"];
  3 -- 4 [label="2"];
  3 -- 5 [label="6"];
  4 -- 5 [label="3"];
}
'''

def run(exe, args):
    r = subprocess.run([exe] + args, capture_output=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).decode('utf-8', 'replace')

full_path = os.path.join(HERE, 'fig', 'full_graph.dot')
with io.open(full_path, 'w', encoding='utf-8') as f:
    f.write(full_dot)

results = []

# Полный граф — neato (симметричная раскладка).
rc, msg = run(NEATO, ['-Tpng', '-Gdpi=150', full_path,
                      '-o', os.path.join(HERE, 'fig', 'fig_graph.png')])
results.append('full graph (neato) rc=%d %s' % (rc, msg))

# Остовное дерево — dot (дерево сверху вниз), из фактического вывода программы.
rc, msg = run(DOT, ['-Tpng', '-Gdpi=150',
                    os.path.join(HERE, '..', 'tests', 'test3.out'),
                    '-o', os.path.join(HERE, 'fig', 'fig_mst.png')])
results.append('mst (dot) rc=%d %s' % (rc, msg))

with io.open(os.path.join(HERE, 'fig', 'render_log.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
print('render done')
