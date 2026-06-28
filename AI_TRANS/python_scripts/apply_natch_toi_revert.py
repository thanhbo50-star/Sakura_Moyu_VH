import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = 'sakumoyu-0112-chiwa_019.xlsx'
df = pd.read_excel(file_path)

changes_made = 0

def revert_pronouns(text):
    if not isinstance(text, str) or text == 'nan':
        return text
    
    new_text = text
    
    # We want to change "Chúng ta" to "Chúng tôi" first
    new_text = re.sub(r'\bChúng ta\b', 'Chúng tôi', new_text)
    new_text = re.sub(r'\bchúng ta\b', 'chúng tôi', new_text)
    
    # Then "Ta" to "Tôi" and "ta" to "tôi"
    # To avoid changing "người ta", we can use a negative lookbehind, but in Vietnamese words are space separated.
    # so \bta\b matches whole word. If we want to avoid "người ta", we can just negative lookbehind space before 'ta'.
    # Actually just \bTa\b and \bta\b is fine, but let's exclude "người ta" explicitly if it exists.
    new_text = re.sub(r'(?<!người )\bta\b', 'tôi', new_text)
    new_text = re.sub(r'\bTa\b', 'Tôi', new_text)
    
    return new_text

for idx, row in df.iterrows():
    name = str(row.get('name'))
    
    # Apply to Natch (ナハト) spoken lines and his narration/soliloquy (nan)
    if pd.isna(row.get('name')) or name == 'nan' or name == 'ナハト':
        trans = str(row.get('trans'))
        new_trans = revert_pronouns(trans)
        
        if trans != new_trans:
            df.at[idx, 'trans'] = new_trans
            print(f"Row {idx}:\nFrom: {trans}\nTo:   {new_trans}\n")
            changes_made += 1

if changes_made > 0:
    df.to_excel(file_path, index=False)
    print(f"Saved {changes_made} changes to {file_path}")
else:
    print("No changes made.")
