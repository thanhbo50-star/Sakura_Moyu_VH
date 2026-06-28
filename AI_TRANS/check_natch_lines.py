import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('sakumoyu-0112-chiwa_019.xlsx')
for idx, r in df[df['name'] == 'ナハト'].iterrows():
    print(f"Row {idx} trans: {r['trans']}")
