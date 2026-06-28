import pandas as pd
import sys

# Windows console encoding fix for printing vietnamese
sys.stdout.reconfigure(encoding='utf-8')

file_path = 'sakumoyu-0112-chiwa_019.xlsx'
df = pd.read_excel(file_path)

changes_made = 0

for idx, row in df.iterrows():
    if row.get('name') == 'ナハト':
        trans = str(row.get('trans'))
        original_trans = trans
        
        if 'lũ con người' not in trans:
            if 'với con người' in trans:
                trans = trans.replace('với con người', 'với lũ con người')
            if 'trước mặt mọi người' in trans:
                trans = trans.replace('trước mặt mọi người', 'trước mặt lũ con người')
            if 'con người là sinh vật' in trans:
                trans = trans.replace('con người là sinh vật', 'lũ con người là sinh vật')
        
        if trans != original_trans:
            df.at[idx, 'trans'] = trans
            print(f"Row {idx} changed:\nFrom: {original_trans}\nTo:   {trans}\n")
            changes_made += 1

if changes_made > 0:
    df.to_excel(file_path, index=False)
    print(f"Saved {changes_made} changes to {file_path}")
else:
    print("No changes were needed.")
