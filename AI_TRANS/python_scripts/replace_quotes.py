import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'c:\Users\tivac\Downloads\Compressed\drive-download-20251110T020358Z-1-001\AI_TRANS\sakumoyu-0112-chiwa_019.xlsx'

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    sys.exit(1)

df = pd.read_excel(file_path)
changes = 0

for idx, row in df.iterrows():
    trans = str(row.get('trans'))
    if trans == 'nan' or pd.isna(row.get('trans')):
        continue
        
    new_trans = trans.replace('『', '"').replace('』', '"')
    
    if trans != new_trans:
        df.at[idx, 'trans'] = new_trans
        changes += 1

if changes > 0:
    df.to_excel(file_path, index=False)
    print(f"Replaced 『 and 』 with \" in {changes} rows.")
else:
    print("No changes needed.")
