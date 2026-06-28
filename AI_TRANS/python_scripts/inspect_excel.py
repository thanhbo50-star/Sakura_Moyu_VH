import pandas as pd
import os

file_path = 'sakumoyu-0112-chiwa_019.xlsx'

try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    print("-" * 20)
    print("First 5 rows:")
    print(df.head())
    print("-" * 20)
    # Check for keywords to verify content
    print("Sample with 'Sol' or 'Chiwa':")
    # Assuming columns might be named 'Japanese', 'Vietnamese', or similar. 
    # If not, I'll see the columns in output.
except Exception as e:
    print(f"Error reading excel: {e}")
