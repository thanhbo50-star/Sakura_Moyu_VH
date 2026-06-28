import pandas as pd
import re

file_path = 'sakumoyu-0112-chiwa_019.xlsx'
df = pd.read_excel(file_path)

natch_df = df[df['name'] == 'ナハト']

with open('natch_all_lines.txt', 'w', encoding='utf-8') as f:
    for idx, row in natch_df.iterrows():
        trans = str(row.get('trans'))
        # highlight lines with con người, người, họ, bọn họ
        if re.search(r'(con người|người|họ|bọn họ|chúng|kẻ)', trans, re.IGNORECASE):
            f.write(f"Row {idx} trans: {trans}\n")
            f.write(f"Row {idx} org: {row.get('org')}\n\n")

print("Finished extracting suspected lines.")
