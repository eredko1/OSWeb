#!/usr/bin/env bash
# Syntax-checks the inline script of index.html. Run before every commit.
set -e; cd "$(dirname "$0")/.."
python3 - <<'PY'
import re,sys,subprocess,tempfile
s=open('index.html',encoding='utf-8').read()
big=max(re.findall(r'<script>(.*?)</script>',s,flags=re.S),key=len)
f=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False); f.write(big); f.close()
r=subprocess.run(['node','--check',f.name],capture_output=True,text=True)
print('SYNTAX OK' if r.returncode==0 else r.stderr); sys.exit(r.returncode)
PY
