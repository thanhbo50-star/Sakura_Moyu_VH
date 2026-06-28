"""
Merge translations (edit column, falling back to trans column) 
into the merge column, and save the final xlsx files to the viethoa/ directory.
For untranslated lines, falls back to the raw column to avoid blank lines in game.
"""
import os
import glob
import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = r'd:\sakura moyu\_trans'
EXCEL_DIR = os.path.join(BASE_DIR, 'script_excel')
VIETHOA_DIR = os.path.join(BASE_DIR, 'viethoa')

os.makedirs(VIETHOA_DIR, exist_ok=True)

def merge_files():
    files = sorted(glob.glob(os.path.join(EXCEL_DIR, '*.xlsx')))
    print(f"Found {len(files)} files to merge.")
    
    merged_count = 0
    for fpath in files:
        fname = os.path.basename(fpath)
        try:
            df = pd.read_excel(fpath)
            
            # Ensure columns exist
            for col in ['trans', 'edit', 'merge']:
                if col not in df.columns:
                    df[col] = None
            
            # Strip whitespace and convert empty strings to NaN
            for col in ['trans', 'edit']:
                df[col] = df[col].astype(str).str.strip().replace({'nan': None, '': None, 'None': None})
            
            # Populate merge column
            # Prioritize: edit -> trans -> raw
            df['merge'] = df['edit'].fillna(df['trans']).fillna(df['raw'])
            
            # Save to viethoa/
            out_path = os.path.join(VIETHOA_DIR, fname)
            df.to_excel(out_path, index=False)
            
            total = len(df)
            translated = df['edit'].fillna(df['trans']).notna().sum()
            print(f"Merged {fname}: {translated}/{total} lines translated.")
            merged_count += 1
        except Exception as e:
            print(f"Error merging {fname}: {e}")
            
    print(f"Done! Merged {merged_count} files into {VIETHOA_DIR}")

if __name__ == "__main__":
    merge_files()
