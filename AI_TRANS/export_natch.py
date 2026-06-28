import pandas as pd
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
df = pd.read_excel('sakumoyu-0112-chiwa_019.xlsx')

data = []
for idx, row in df.iterrows():
    if row.get('name') == 'ナハト':
        trans = str(row.get('trans'))
        if trans != 'nan':
            data.append({
                "row": idx,
                "org": str(row.get('org')),
                "trans": trans
            })

with open('natch_spoken.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Exported {len(data)} lines to natch_spoken.json")
