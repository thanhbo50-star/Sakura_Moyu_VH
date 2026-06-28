"""
Sakura Moyu VH — MCP Translation Server
Tools for fast, token-efficient translation workflow.

Install: pip install mcp pandas openpyxl
Run: python MCP/server.py
"""

# ── Lightweight stdlib only at module level (fast startup) ──
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ─── Config ───────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
EXCEL_DIR   = BASE_DIR / "script_excel"
CONTEXT_DIR = BASE_DIR / "context"
CACHE_DIR   = BASE_DIR / "scripts" / "analysis_cache"

mcp = FastMCP("sakura-moyu-vh")

# ─── Lazy pandas import (cached after first call) ─────────
_pd = None

def _get_pd():
    global _pd
    if _pd is None:
        import pandas  # noqa: PLC0415
        _pd = pandas
    return _pd

# ─── Helpers ──────────────────────────────────────────────
def _get_arc(filename: str) -> str:
    m = re.search(r'sakumoyu-(\d+)-(\w+)', filename)
    if not m:
        return 'unknown'
    num  = int(m.group(1))
    part = m.group(2)
    if 'prologue' in part: return 'prologue'
    if num <= 52:           return 'common'
    if 'kuro_h'  in part:  return 'kuro_harem'
    if 'haru_h'  in part:  return 'haru_harem'
    if 'chiwa_h' in part:  return 'chiwa_harem'
    if 'hiori_h' in part:  return 'hiori_harem'
    if 'kuro'    in part:  return 'kuro'
    if 'haru'    in part:  return 'haru'
    if 'chiwa'   in part:  return 'chiwa'
    if 'hiori'   in part:  return 'hiori'
    return 'common'

def _load_df(filename: str):
    pd = _get_pd()
    path = EXCEL_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    return pd.read_excel(path)

def _save_df(df, filename: str):
    path = EXCEL_DIR / filename
    df.to_excel(path, index=False)

# ──────────────────────────────────────────────────────────
# TOOL 1: get_file_list
# ──────────────────────────────────────────────────────────
@mcp.tool()
def get_file_list(
    arc: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 30
) -> str:
    """
    Lấy danh sách file xlsx cần dịch.

    Args:
        arc: Lọc theo arc: prologue, common, kuro, haru, chiwa, hiori,
             kuro_harem, haru_harem, chiwa_harem, hiori_harem. None = tất cả.
        status: 'untranslated', 'partial', 'translated', 'needs_edit'. None = tất cả.
        limit: Số file tối đa (mặc định 30).
    """
    pd = _get_pd()
    files = sorted(EXCEL_DIR.glob("*.xlsx"))
    result = []

    for fpath in files:
        fname    = fpath.name
        file_arc = _get_arc(fname)
        if arc and file_arc != arc:
            continue
        try:
            df  = pd.read_excel(fpath)
            n   = len(df)
            nt  = int(df['trans'].notna().sum()) if 'trans' in df.columns else 0
            ne  = int(df['edit'].notna().sum())  if 'edit'  in df.columns else 0
            pct = round(nt / n * 100, 1) if n > 0 else 0.0

            file_status = (
                'untranslated' if pct == 0 else
                'translated'   if pct >= 95 else
                'partial'
            )
            if ne > 0 and nt > ne:
                file_status = 'needs_edit'

            if status and file_status != status:
                continue

            result.append({
                "file": fname, "arc": file_arc,
                "rows": n, "trans": nt, "edit": ne,
                "pct_trans": pct, "status": file_status,
            })
        except Exception as e:
            result.append({"file": fname, "arc": file_arc, "error": str(e)})

        if len(result) >= limit:
            break

    return json.dumps(result, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 2: get_rows_to_translate
# ──────────────────────────────────────────────────────────
@mcp.tool()
def get_rows_to_translate(
    filename: str,
    limit: int = 25,
    start_row: int = 0,
    include_context: bool = True
) -> str:
    """
    Lấy các dòng CHƯA DỊCH từ một file. Tool chính để lấy batch cần dịch.

    Args:
        filename: Tên file xlsx (vd: 'sakumoyu-0001-prologue_001.xlsx')
        limit: Số dòng tối đa (nên dùng 20-30)
        start_row: Offset để phân trang
        include_context: Nếu True, thêm 3 dòng trước để hiểu ngữ cảnh
    """
    pd = _get_pd()
    df = _load_df(filename)

    if 'trans' in df.columns:
        mask = df['trans'].isna() | (df['trans'].astype(str).str.strip().isin(['', 'nan']))
    else:
        mask = pd.Series([True] * len(df))

    untranslated_idx  = df[mask].index.tolist()
    total_untranslated = len(untranslated_idx)

    batch = untranslated_idx[start_row: start_row + limit]
    rows_out = []

    for idx in batch:
        row   = df.loc[idx]
        entry = {
            "index": int(idx),
            "name": str(row.get('name', '')).strip() if pd.notna(row.get('name')) else "",
            "org":  str(row.get('org',  '')).strip(),
            "raw":  str(row.get('raw',  '')).strip() if pd.notna(row.get('raw'))  else "",
        }
        if include_context:
            ctx_before = []
            for ci in range(max(0, idx - 3), idx):
                cr = df.loc[ci]
                t  = str(cr.get('edit', cr.get('trans', ''))).strip()
                if t and t != 'nan':
                    ctx_before.append({
                        "name": str(cr.get('name', '')).strip() if pd.notna(cr.get('name')) else "",
                        "text": t[:100]
                    })
            entry["context_before"] = ctx_before
        rows_out.append(entry)

    return json.dumps({
        "file": filename,
        "arc": _get_arc(filename),
        "total_untranslated": total_untranslated,
        "batch_start": start_row,
        "batch_size":  len(rows_out),
        "rows": rows_out
    }, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 3: get_translated_rows
# ──────────────────────────────────────────────────────────
@mcp.tool()
def get_translated_rows(
    filename: str,
    column: str = "edit",
    limit: int = 20,
    start_row: int = 0
) -> str:
    """
    Lấy các dòng ĐÃ DỊCH từ file để review hoặc tham khảo văn phong.

    Args:
        filename: Tên file xlsx
        column: 'edit' (đã tinh chỉnh) hoặc 'trans' (bản thảo)
        limit: Số dòng tối đa
        start_row: Offset
    """
    pd = _get_pd()
    df = _load_df(filename)

    if column not in df.columns:
        return json.dumps({"error": f"Column '{column}' not found"})

    mask       = df[column].notna() & ~df[column].astype(str).str.strip().isin(['', 'nan'])
    translated = df[mask].iloc[start_row: start_row + limit]
    rows_out   = []

    for idx, row in translated.iterrows():
        rows_out.append({
            "index": int(idx),
            "name":  str(row.get('name',  '')).strip() if pd.notna(row.get('name'))  else "",
            "org":   str(row.get('org',   '')).strip()[:150],
            "trans": str(row.get('trans', '')).strip()[:150] if pd.notna(row.get('trans')) else "",
            "edit":  str(row.get('edit',  '')).strip()[:150] if pd.notna(row.get('edit'))  else "",
        })

    return json.dumps({
        "file": filename, "column": column,
        "total_translated": int(mask.sum()),
        "rows": rows_out
    }, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 4: write_translations
# ──────────────────────────────────────────────────────────
@mcp.tool()
def write_translations(
    filename: str,
    translations: list,
    column: str = "trans"
) -> str:
    """
    Ghi kết quả dịch vào file xlsx.

    Args:
        filename: Tên file xlsx
        translations: List dict {index: int, text: str}
        column: 'trans' (bản thảo) hoặc 'edit' (đã tinh chỉnh)
    """
    df = _load_df(filename)
    if column not in df.columns:
        df[column] = None
    df[column] = df[column].astype(object)

    written, errors = 0, []
    for item in translations:
        try:
            idx  = int(item['index'])
            text = str(item['text']).strip()
            if idx in df.index:
                df.at[idx, column] = text
                written += 1
            else:
                errors.append(f"Index {idx} not found")
        except Exception as e:
            errors.append(str(e))

    _save_df(df, filename)
    return json.dumps({
        "status": "ok", "file": filename,
        "column": column, "written": written, "errors": errors
    }, ensure_ascii=False)


# ──────────────────────────────────────────────────────────
# TOOL 5: get_context_for_file
# ──────────────────────────────────────────────────────────
@mcp.tool()
def get_context_for_file(filename: str) -> str:
    """
    Lấy ngữ cảnh arc + danh sách nhân vật của file cụ thể.
    Tiết kiệm token: chỉ trả context của arc đó, không phải toàn bộ.

    Args:
        filename: Tên file xlsx
    """
    pd = _get_pd()
    arc = _get_arc(filename)
    arc_to_ctx = {
        'prologue':    'arc_common.md',  'common':      'arc_common.md',
        'kuro':        'arc_kuro.md',    'kuro_harem':  'arc_kuro.md',
        'haru':        'arc_haru.md',    'haru_harem':  'arc_haru.md',
        'chiwa':       'arc_chiwa.md',   'chiwa_harem': 'arc_chiwa.md',
        'hiori':       'arc_hiori.md',   'hiori_harem': 'arc_hiori.md',
    }
    ctx_file    = CONTEXT_DIR / arc_to_ctx.get(arc, 'arc_common.md')
    ctx_content = ctx_file.read_text(encoding='utf-8') if ctx_file.exists() else "Context not found."

    try:
        df    = _load_df(filename)
        chars = df['name'].dropna().unique().tolist() if 'name' in df.columns else []
        chars = [str(c) for c in chars if str(c) != 'nan']
    except Exception:
        chars = []

    return json.dumps({
        "file": filename, "arc": arc,
        "characters_in_file": chars,
        "arc_context": ctx_content[:3000]
    }, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 6: get_few_shot_examples
# ──────────────────────────────────────────────────────────
@mcp.tool()
def get_few_shot_examples(
    character: Optional[str] = None,
    arc: Optional[str] = None,
    limit: int = 8,
    only_edited: bool = True
) -> str:
    """
    Lấy ví dụ dịch tốt nhất (cột edit) làm few-shot examples cho prompt.
    Không load xlsx — chỉ đọc từ cache JSON (rất nhanh).

    Args:
        character: Tên nhân vật JP ('大雅', 'クロ', '千和'...). None = tất cả.
        arc: Lọc theo arc. None = tất cả.
        limit: Số ví dụ (nên dùng 5-10)
        only_edited: True = chỉ lấy dòng edit khác trans (chất lượng nhất)
    """
    cache_file = CACHE_DIR / 'char_examples.json'
    if not cache_file.exists():
        return json.dumps({"error": "Cache not found. Run scripts/analyze_project.py first."})

    with open(cache_file, encoding='utf-8') as f:
        all_examples = json.load(f)

    results = []
    for char, examples in all_examples.items():
        if character and char != character:
            continue
        if char == '__narrator__' and character and character != '__narrator__':
            continue
        for ex in examples:
            if only_edited and not ex.get('changed', False):
                continue
            if arc and _get_arc(ex.get('file', '')) != arc:
                continue
            results.append({
                "character": char,
                "org":  ex['org'],
                "trans": ex['trans'],
                "edit": ex['edit'],
                "file": ex.get('file', '')
            })
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break

    return json.dumps({"count": len(results), "examples": results}, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 7: get_translation_stats
# ──────────────────────────────────────────────────────────
@mcp.tool()
def get_translation_stats(arc: Optional[str] = None) -> str:
    """
    Xem tiến độ dịch realtime (đọc trực tiếp từ file xlsx).

    Args:
        arc: Lọc theo arc (None = tổng hợp tất cả).
    """
    pd       = _get_pd()
    arc_data = defaultdict(lambda: {'files': 0, 'rows': 0, 'trans': 0, 'edit': 0})

    for fpath in sorted(EXCEL_DIR.glob("*.xlsx")):
        file_arc = _get_arc(fpath.name)
        if arc and file_arc != arc:
            continue
        try:
            df = pd.read_excel(fpath)
            arc_data[file_arc]['files'] += 1
            arc_data[file_arc]['rows']  += len(df)
            if 'trans' in df.columns:
                arc_data[file_arc]['trans'] += int(df['trans'].notna().sum())
            if 'edit' in df.columns:
                arc_data[file_arc]['edit'] += int(df['edit'].notna().sum())
        except Exception:
            pass

    result = {}
    total  = {'files': 0, 'rows': 0, 'trans': 0, 'edit': 0}
    for a, s in arc_data.items():
        pct_t = round(s['trans'] / s['rows'] * 100, 1) if s['rows'] else 0
        pct_e = round(s['edit']  / s['rows'] * 100, 1) if s['rows'] else 0
        result[a] = {**s, 'pct_trans': pct_t, 'pct_edit': pct_e}
        for k in total: total[k] += s[k]

    total['pct_trans'] = round(total['trans'] / total['rows'] * 100, 1) if total['rows'] else 0
    total['pct_edit']  = round(total['edit']  / total['rows'] * 100, 1) if total['rows'] else 0
    result['__total__'] = total

    return json.dumps(result, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 8: search_translated
# ──────────────────────────────────────────────────────────
@mcp.tool()
def search_translated(
    query: str,
    search_in: str = "org",
    column: str = "edit",
    limit: int = 10
) -> str:
    """
    Tìm kiếm trong bản dịch để kiểm tra nhất quán thuật ngữ/xưng hô.

    Args:
        query: Từ/cụm từ cần tìm
        search_in: Tìm trong cột nào — 'org', 'trans', 'edit', 'name'
        column: Cột hiển thị kết quả — 'edit' hoặc 'trans'
        limit: Số kết quả tối đa
    """
    pd      = _get_pd()
    results = []

    for fpath in sorted(EXCEL_DIR.glob("*.xlsx")):
        if len(results) >= limit:
            break
        try:
            df = pd.read_excel(fpath)
            if search_in not in df.columns:
                continue
            mask    = df[search_in].astype(str).str.contains(query, na=False, regex=False)
            matches = df[mask]
            for idx, row in matches.iterrows():
                trans_text = str(row.get(column, '')).strip()
                if trans_text and trans_text != 'nan':
                    results.append({
                        "file": fpath.name, "index": int(idx),
                        "name": str(row.get('name', '')).strip() if pd.notna(row.get('name')) else "",
                        "org":  str(row.get('org',  '')).strip()[:120],
                        "translation": trans_text[:120],
                        "column_used": column
                    })
                if len(results) >= limit:
                    break
        except Exception:
            pass

    return json.dumps({
        "query": query, "search_in": search_in,
        "found": len(results), "results": results
    }, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 9: get_character_voice
# ──────────────────────────────────────────────────────────
@mcp.tool()
def get_character_voice(character: str) -> str:
    """
    Lấy thông tin xưng hô, giọng điệu, ví dụ dịch của một nhân vật.
    Dùng trước khi dịch cảnh có nhân vật đó để đảm bảo nhất quán.

    Args:
        character: Tên nhân vật JP ('大雅', 'クロ', '千和', 'ナハト', 'ハル'...)
    """
    chars_file = CONTEXT_DIR / 'characters.md'
    if not chars_file.exists():
        return json.dumps({"error": "characters.md not found. Run generate_all.py first."})

    content  = chars_file.read_text(encoding='utf-8')
    pattern  = rf'## {re.escape(character)}.*?(?=\n## |\Z)'
    match    = re.search(pattern, content, re.DOTALL)
    char_section = match.group(0) if match else f"Character '{character}' not found."

    cache_file   = CACHE_DIR / 'char_examples.json'
    examples_out = []
    if cache_file.exists():
        with open(cache_file, encoding='utf-8') as f:
            all_ex = json.load(f)
        for ex in all_ex.get(character, [])[:5]:
            examples_out.append({
                "org":     ex['org'][:100],
                "trans":   ex['trans'][:100],
                "edit":    ex['edit'][:100],
                "changed": ex.get('changed', False)
            })

    return json.dumps({
        "character": character,
        "profile":   char_section[:1500],
        "examples":  examples_out
    }, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 10: get_untranslated_count
# ──────────────────────────────────────────────────────────
@mcp.tool()
def get_untranslated_count(arc: Optional[str] = None) -> str:
    """
    Đếm nhanh số dòng chưa dịch theo arc (không load nội dung để tiết kiệm token).

    Args:
        arc: Arc cần kiểm tra. None = tất cả.
    """
    pd     = _get_pd()
    counts = defaultdict(lambda: {'untranslated': 0, 'total': 0, 'files': []})

    for fpath in sorted(EXCEL_DIR.glob("*.xlsx")):
        file_arc = _get_arc(fpath.name)
        if arc and file_arc != arc:
            continue
        try:
            df = pd.read_excel(fpath, usecols=lambda c: c == 'trans')
            n  = len(df)
            missing = int(df['trans'].isna().sum()) if 'trans' in df.columns else n
            counts[file_arc]['total']        += n
            counts[file_arc]['untranslated'] += missing
            if missing > 0:
                counts[file_arc]['files'].append({'file': fpath.name, 'missing': missing})
        except Exception:
            pass

    result = {}
    for a, d in counts.items():
        pct_done = round((d['total'] - d['untranslated']) / d['total'] * 100, 1) if d['total'] else 0
        result[a] = {
            'total': d['total'], 'untranslated': d['untranslated'],
            'pct_done': pct_done, 'files_with_gaps': d['files'][:10]
        }

    return json.dumps(result, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 11: batch_get_rows
# ──────────────────────────────────────────────────────────
@mcp.tool()
def batch_get_rows(filenames: list, rows_per_file: int = 10) -> str:
    """
    Lấy dòng chưa dịch từ NHIỀU FILE cùng lúc — siêu tiết kiệm token.

    Args:
        filenames: List tên file xlsx (tối đa 5)
        rows_per_file: Số dòng mỗi file (mặc định 10)
    """
    pd     = _get_pd()
    result = {}

    for fname in filenames[:5]:
        try:
            df   = _load_df(fname)
            mask = (
                df['trans'].isna() | df['trans'].astype(str).str.strip().isin(['', 'nan'])
                if 'trans' in df.columns
                else pd.Series([True] * len(df))
            )
            rows = []
            for idx, row in df[mask].head(rows_per_file).iterrows():
                rows.append({
                    "index": int(idx),
                    "name": str(row.get('name', '')).strip() if pd.notna(row.get('name')) else "",
                    "org":  str(row.get('org',  '')).strip()[:100]
                })
            result[fname] = {
                "arc": _get_arc(fname),
                "total_untrans": int(mask.sum()),
                "sample": rows
            }
        except Exception as e:
            result[fname] = {"error": str(e)}

    return json.dumps(result, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────
# TOOL 12: copy_trans_to_edit
# ──────────────────────────────────────────────────────────
@mcp.tool()
def copy_trans_to_edit(filename: str, indices: Optional[list] = None) -> str:
    """
    Copy cột trans → edit cho những dòng chưa có edit.
    Dùng khi bản trans đã đủ tốt, không cần tinh chỉnh thêm.

    Args:
        filename: Tên file xlsx
        indices: List index cụ thể (None = tất cả dòng có trans nhưng chưa có edit)
    """
    df = _load_df(filename)
    if 'trans' not in df.columns:
        return json.dumps({"error": "No 'trans' column found"})
    if 'edit' not in df.columns:
        df['edit'] = None

    if indices:
        mask = df.index.isin(indices)
    else:
        has_trans = df['trans'].notna() & ~df['trans'].astype(str).str.strip().isin(['', 'nan'])
        no_edit   = df['edit'].isna()   |  df['edit'].astype(str).str.strip().isin(['', 'nan'])
        mask      = has_trans & no_edit

    count = int(mask.sum())
    df.loc[mask, 'edit'] = df.loc[mask, 'trans']
    _save_df(df, filename)

    return json.dumps({"status": "ok", "copied": count, "file": filename}, ensure_ascii=False)


# ──────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
