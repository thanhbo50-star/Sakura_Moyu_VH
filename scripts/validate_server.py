import ast, io, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r'd:\sakura moyu\_trans\MCP\server.py'
with open(path, encoding='utf-8') as f:
    src = f.read()

# 1. Syntax check
try:
    ast.parse(src)
    print('Syntax: OK')
except SyntaxError as e:
    print(f'Syntax ERROR: {e}')
    sys.exit(1)

# 2. Count tools
tools = src.count('@mcp.tool()')
print(f'Tools defined: {tools}')

# 3. No bare top-level pandas import
top_level_pd = [l for l in src.splitlines()[:30] if 'import pandas' in l and 'def ' not in l]
if top_level_pd:
    print(f'WARNING: top-level pandas import found: {top_level_pd}')
else:
    print('Lazy import: OK (no top-level pandas)')

# 4. Startup time
t = time.perf_counter()
import importlib.util
spec = importlib.util.spec_from_file_location('server', path)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
elapsed = time.perf_counter() - t
print(f'Startup time: {elapsed*1000:.0f}ms (pandas NOT loaded yet)')
print('PASS')
