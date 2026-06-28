import pandas as pd

file_path = 'sakumoyu-0112-chiwa_019.xlsx'
df = pd.read_excel(file_path)

print("Unique names:")
print(df['name'].dropna().unique())

print("\nSample lines from Natch (assuming name contains Natch or ナッチ):")
natch_rows = df[df['name'].astype(str).str.contains('Natch|ナッチ|natch', case=False, na=False)]
for idx, row in natch_rows.head(10).iterrows():
    print(f"Row {idx}:")
    print(f"org: {row.get('org')}")
    print(f"mtl: {row.get('mtl')}")
    print(f"trans: {row.get('trans')}")
    print("-" * 20)
