import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('sakumoyu-0112-chiwa_019.xlsx')
for idx, row in df[df['name'] == 'ナハト'].iterrows():
    trans = str(row.get('trans'))
    org = str(row.get('org'))
    if trans != 'nan' and len(trans) > 5 and '……' not in org or len(org) > 8: 
        print(f"Row {idx}:\nOrg: {org}\nTrans: {trans}\n")
