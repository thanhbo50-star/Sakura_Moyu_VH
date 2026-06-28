import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = 'sakumoyu-0112-chiwa_019.xlsx'
df = pd.read_excel(file_path)

changes_made = 0

def replace_pronouns(text):
    if not isinstance(text, str) or text == 'nan':
        return text
    
    new_text = text
    # Replace We (Chúng tôi -> Chúng ta)
    new_text = re.sub(r'\bChúng tôi\b', 'Chúng ta', new_text)
    new_text = re.sub(r'\bchúng tôi\b', 'chúng ta', new_text)
    
    # Replace I (Tôi -> Ta)
    new_text = re.sub(r'\bTôi\b', 'Ta', new_text)
    new_text = re.sub(r'\btôi\b', 'ta', new_text)
    
    return new_text

for idx, row in df.iterrows():
    name = str(row.get('name'))
    
    # Apply to Natch (ナハト) spoken lines and all his narration/soliloquy (nan)
    if pd.isna(row.get('name')) or name == 'nan' or name == 'ナハト':
        trans = str(row.get('trans'))
        new_trans = replace_pronouns(trans)
        
        if trans != new_trans:
            df.at[idx, 'trans'] = new_trans
            print(f"Row {idx}:\nFrom: {trans}\nTo:   {new_trans}\n")
            changes_made += 1

if changes_made > 0:
    df.to_excel(file_path, index=False)
    print(f"Saved {changes_made} changes to {file_path}")
else:
    print("No changes made.")
