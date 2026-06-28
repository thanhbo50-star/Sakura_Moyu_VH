import pandas as pd

file_path = 'sakumoyu-0112-chiwa_019.xlsx'
df = pd.read_excel(file_path)

with open('names.txt', 'w', encoding='utf-8') as f:
    names = df['name'].dropna().unique()
    f.write("Unique names:\n")
    for name in names:
        f.write(f"{name}\n")

natch_rows = df[df['name'].astype(str).str.contains('Natch|ナッチ|natch|ナ', case=False, na=False)]
if len(natch_rows) == 0:
    # try mapping out all trans for the 4 names
    pass

with open('natch_samples.txt', 'w', encoding='utf-8') as f:
    for name in names:
        f.write(f"\n--- Samples for {name} ---\n")
        sample = df[df['name'] == name].head(5)
        for idx, row in sample.iterrows():
            f.write(f"Row {idx} org: {row.get('org')}\n")
            f.write(f"Row {idx} mtl: {row.get('mtl')}\n")
            f.write(f"Row {idx} trans: {row.get('trans')}\n")
