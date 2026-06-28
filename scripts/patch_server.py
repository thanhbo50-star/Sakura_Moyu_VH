"""Patch server.py: add pd = _get_pd() to every @mcp.tool function that uses pd."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r'd:\sakura moyu\_trans\MCP\server.py'
with open(path, encoding='utf-8') as f:
    src = f.read()

# Split into lines for processing
lines = src.splitlines(keepends=True)
out = []
inside_tool = False
tool_body_start = False
added_pd = False

i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.rstrip()

    # Detect @mcp.tool() decorator
    if stripped.strip() == '@mcp.tool()':
        inside_tool = True
        tool_body_start = False
        added_pd = False
        out.append(line)
        i += 1
        continue

    # Detect function def after decorator
    if inside_tool and stripped.strip().startswith('def ') and not tool_body_start:
        tool_body_start = True
        out.append(line)
        i += 1
        continue

    # First line inside the tool function body (after the def)
    if inside_tool and tool_body_start and not added_pd:
        # Check if this line uses pd. anywhere in the rest of the function
        # We always add it (safe to call even if pandas already cached)
        if stripped.strip().startswith('"""') or stripped.strip().startswith("'''"):
            # It's a docstring — add pd= after the closing triple-quote
            out.append(line)
            # Continue until docstring closes
            if stripped.strip().count('"""') >= 2 or stripped.strip().count("'''") >= 2:
                # Single-line docstring
                indent = len(line) - len(line.lstrip())
                out.append(' ' * indent + 'pd = _get_pd()\n')
                added_pd = True
            else:
                # Multi-line docstring
                i += 1
                while i < len(lines):
                    out.append(lines[i])
                    if '"""' in lines[i] or "'''" in lines[i]:
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        out.append(' ' * (indent if indent else 4) + 'pd = _get_pd()\n')
                        added_pd = True
                        i += 1
                        break
                    i += 1
            i += 1
            continue
        else:
            # No docstring — add pd= before this line
            indent = len(line) - len(line.lstrip())
            out.append(' ' * (indent if indent else 4) + 'pd = _get_pd()\n')
            added_pd = True
            out.append(line)
            i += 1
            continue

    # Detect end of function (new def at top level resets state)
    if stripped and not stripped[0].isspace() and not stripped.startswith('@') and stripped.startswith('def ') and inside_tool:
        inside_tool = False
        tool_body_start = False
        added_pd = False

    out.append(line)
    i += 1

result = ''.join(out)
with open(path, 'w', encoding='utf-8') as f:
    f.write(result)
print("Patched. Verifying remaining bare pd. references in tool bodies...")

# Verify
with open(path, encoding='utf-8') as f:
    lines2 = f.readlines()
errors = []
for i, l in enumerate(lines2, 1):
    if 'pd.' in l and '_get_pd' not in l and 'import pandas' not in l:
        errors.append(f'L{i}: {l.rstrip()}')
if errors:
    print(f"Still found {len(errors)} bare pd. refs:")
    for e in errors: print(' ', e)
else:
    print("All pd. refs are now covered by local pd = _get_pd()")
