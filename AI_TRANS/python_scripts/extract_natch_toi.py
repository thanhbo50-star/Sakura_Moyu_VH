import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = 'sakumoyu-0112-chiwa_019.xlsx'
df = pd.read_excel(file_path)

print("Extracting Natch's lines with 'tôi':")

with open('natch_toi_lines.txt', 'w', encoding='utf-8') as f:
    for idx, row in df.iterrows():
        # Soliloquy might belong to ナハト or have blank name but we can infer from surrounding context.
        # Let's just output any line translated with 'tôi' that belongs to Natch or is blank next to Natch.
        name = str(row.get('name'))
        trans = str(row.get('trans'))
        org = str(row.get('org'))
        
        # We will extract all Natch lines, plus lines with empty names just in case monologue has no name
        if name == 'ナハト' and 'tôi ' in trans or ' tôi' in trans or 'Tôi ' in trans:
            f.write(f"[{name}] Row {idx}\nOrg: {org}\nTrans: {trans}\n\n")

print("Done. Look at natch_toi_lines.txt")
