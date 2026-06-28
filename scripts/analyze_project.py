"""
Master analysis script for Sakura Moyu VH translation project.
Extracts: stats, character examples, glossary patterns, arc summaries.
Output: JSON data files for use in generating context/report files.
"""
import pandas as pd
import json
import os
import sys
import io
import re
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

XLSX_DIR = r'd:\sakura moyu\_trans\script_excel'
OUT_DIR  = r'd:\sakura moyu\_trans\scripts\analysis_cache'
os.makedirs(OUT_DIR, exist_ok=True)

# Arc mapping by filename prefix
ARC_MAP = {
    'prologue': ('Prologue', range(1, 14)),
    'common':   ('Common (Chung)', range(14, 93)),
    'kuro':     ('Arc Kuro', range(53, 75)),
    'haru':     ('Arc Haru', range(75, 94)),
    'chiwa':    ('Arc Chiwa', range(94, 118)),
    'hiori':    ('Arc Hiori', range(118, 148)),
    'kuro_h':   ('Harem Kuro', [140, 141]),
    'haru_h':   ('Harem Haru', [142, 143]),
    'chiwa_h':  ('Harem Chiwa', [144, 145]),
    'hiori_h':  ('Harem Hiori', [146, 147]),
}

def get_arc(filename):
    """Determine arc from filename."""
    m = re.search(r'sakumoyu-(\d+)-(\w+)', filename)
    if not m:
        return 'unknown'
    num = int(m.group(1))
    part = m.group(2)
    if 'prologue' in part: return 'prologue'
    if num <= 51: return 'common'
    if num == 52: return 'common'
    if 'kuro_h' in part: return 'kuro_harem'
    if 'haru_h' in part: return 'haru_harem'
    if 'chiwa_h' in part: return 'chiwa_harem'
    if 'hiori_h' in part: return 'hiori_harem'
    if 'kuro' in part: return 'kuro'
    if 'haru' in part: return 'haru'
    if 'chiwa' in part: return 'chiwa'
    if 'hiori' in part: return 'hiori'
    return 'common'

files = sorted([f for f in os.listdir(XLSX_DIR) if f.endswith('.xlsx')])
print(f"Processing {len(files)} files...")

# Accumulators
arc_stats = defaultdict(lambda: {'files': 0, 'rows': 0, 'trans': 0, 'edit': 0, 'file_list': []})
char_examples = defaultdict(list)  # char -> list of {org, trans, edit}
char_pov = defaultdict(set)       # char -> set of chars they speak with
all_glossary_pairs = []           # (org_word, vn_word) potential glossary
file_stats = []

for fname in files:
    fpath = os.path.join(XLSX_DIR, fname)
    arc = get_arc(fname)
    try:
        df = pd.read_excel(fpath)
        n_rows = len(df)
        n_trans = int(df['trans'].notna().sum()) if 'trans' in df.columns else 0
        n_edit  = int(df['edit'].notna().sum()) if 'edit' in df.columns else 0

        arc_stats[arc]['files'] += 1
        arc_stats[arc]['rows'] += n_rows
        arc_stats[arc]['trans'] += n_trans
        arc_stats[arc]['edit'] += n_edit
        arc_stats[arc]['file_list'].append(fname)

        file_stats.append({
            'file': fname,
            'arc': arc,
            'rows': n_rows,
            'trans': n_trans,
            'edit': n_edit,
            'pct_trans': round(n_trans/n_rows*100, 1) if n_rows > 0 else 0,
            'pct_edit': round(n_edit/n_rows*100, 1) if n_rows > 0 else 0,
        })

        # Extract character examples from rows where BOTH trans and edit exist
        if 'name' in df.columns and 'org' in df.columns and 'trans' in df.columns and 'edit' in df.columns:
            has_both = df[df['trans'].notna() & df['edit'].notna() & df['name'].notna()]
            for _, row in has_both.iterrows():
                char = str(row['name']).strip()
                if char and char != 'nan' and len(char_examples[char]) < 30:
                    org = str(row['org']).strip()
                    trans_txt = str(row['trans']).strip()
                    edit_txt = str(row['edit']).strip()
                    # Only add if edit differs from trans (shows real editing)
                    example = {
                        'org': org[:200],
                        'trans': trans_txt[:200],
                        'edit': edit_txt[:200],
                        'file': fname,
                        'changed': trans_txt != edit_txt
                    }
                    char_examples[char].append(example)

            # Collect narrator/no-name examples too
            no_name = df[df['name'].isna() & df['trans'].notna() & df['edit'].notna()]
            for _, row in no_name.iterrows():
                org = str(row['org']).strip()
                t = str(row['trans']).strip()
                e = str(row['edit']).strip()
                if t != e and len(char_examples['__narrator__']) < 20:
                    char_examples['__narrator__'].append({
                        'org': org[:200], 'trans': t[:200], 'edit': e[:200],
                        'file': fname, 'changed': True
                    })

    except Exception as ex:
        print(f"  ERROR {fname}: {ex}")

print("\n=== ARC STATS ===")
for arc, s in sorted(arc_stats.items()):
    pct = round(s['trans']/s['rows']*100,1) if s['rows'] > 0 else 0
    pct_e = round(s['edit']/s['rows']*100,1) if s['rows'] > 0 else 0
    print(f"  {arc:15s}: {s['files']} files, {s['rows']:5d} rows, trans={s['trans']:5d}({pct}%), edit={s['edit']:4d}({pct_e}%)")

print("\n=== CHARACTERS WITH EXAMPLES ===")
for char, examples in sorted(char_examples.items()):
    changed = [e for e in examples if e['changed']]
    print(f"  {char:10s}: {len(examples)} examples, {len(changed)} with edits")

# Save JSON data
with open(os.path.join(OUT_DIR, 'arc_stats.json'), 'w', encoding='utf-8') as f:
    json.dump(dict(arc_stats), f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT_DIR, 'char_examples.json'), 'w', encoding='utf-8') as f:
    json.dump(dict(char_examples), f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT_DIR, 'file_stats.json'), 'w', encoding='utf-8') as f:
    json.dump(file_stats, f, ensure_ascii=False, indent=2)

print(f"\nData saved to {OUT_DIR}")
print("DONE")
