import pandas as pd
import re
import sys
import os

# Fix console encoding for Vietnamese text output
sys.stdout.reconfigure(encoding='utf-8')

def get_unique_names(file_path: str) -> list[str]:
    """Get all unique character names in the translated Excel file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    df = pd.read_excel(file_path)
    return [str(name) for name in df['name'].dropna().unique()]

def extract_character_lines(file_path: str, character_name: str, keyword: str = "") -> list[dict]:
    """Extract lines spoken by a specific character, optionally filtered by a regex keyword."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    df = pd.read_excel(file_path)
    lines = []
    
    pattern = re.compile(keyword, re.IGNORECASE) if keyword else None
    
    for idx, row in df.iterrows():
        name = str(row.get('name'))
        is_character = (name == character_name) or (pd.isna(row.get('name')) and character_name == 'nan') or (name == 'nan' and character_name == 'nan')
        if is_character:
            trans = str(row.get('trans'))
            if not pattern or pattern.search(trans):
                lines.append({
                    "row": idx,
                    "name": name,
                    "org": str(row.get('org')),
                    "mtl": str(row.get('mtl')),
                    "trans": trans
                })
    return lines

def apply_text_replacement(file_path: str, character_name: str, target: str, replacement: str, include_nan: bool = True) -> dict:
    """Apply a simple text replacement to a character's translated lines."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    df = pd.read_excel(file_path)
    changes = 0
    changed_rows = []
    
    for idx, row in df.iterrows():
        name = str(row.get('name'))
        is_character = (name == character_name) or (include_nan and (pd.isna(row.get('name')) or name == 'nan'))
        if is_character:
            trans = str(row.get('trans'))
            if trans == 'nan' or pd.isna(row.get('trans')): continue
            
            new_trans = trans.replace(target, replacement)
            
            if trans != new_trans:
                df.at[idx, 'trans'] = new_trans
                changed_rows.append({"row": idx, "from": trans, "to": new_trans})
                changes += 1
                
    if changes > 0:
        df.to_excel(file_path, index=False)
        
    return {"changes_made": changes, "details": changed_rows}

def apply_regex_replacement(file_path: str, character_name: str, pattern: str, replacement: str, include_nan: bool = True) -> dict:
    """Apply a regex replacement to a character's translated lines."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    df = pd.read_excel(file_path)
    changes = 0
    changed_rows = []
    
    compiled_pattern = re.compile(pattern)
    
    for idx, row in df.iterrows():
        name = str(row.get('name'))
        is_character = (name == character_name) or (include_nan and (pd.isna(row.get('name')) or name == 'nan'))
        if is_character:
            trans = str(row.get('trans'))
            if trans == 'nan' or pd.isna(row.get('trans')): continue
            
            new_trans = compiled_pattern.sub(replacement, trans)
            
            if trans != new_trans:
                df.at[idx, 'trans'] = new_trans
                changed_rows.append({"row": idx, "from": trans, "to": new_trans})
                changes += 1
                
    if changes > 0:
        df.to_excel(file_path, index=False)
        
    return {"changes_made": changes, "details": changed_rows}
