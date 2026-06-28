import pandas as pd
import os
import glob

def check_encoding(directory):
    files = glob.glob(os.path.join(directory, '*.xlsx'))
    if not files:
        return

    file_path = files[0]
    try:
        df = pd.read_excel(file_path)
        # Save a sample to text file with utf-8 encoding
        sample = df[['org', 'trans']].dropna().head(10)
        with open('sample_output.txt', 'w', encoding='utf-8') as f:
            f.write(str(sample.to_string()))
        print("Sample written to sample_output.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    target_dir = r"c:/Users/tivac/Downloads/Compressed/drive-download-20251110T020358Z-1-001"
    check_encoding(target_dir)
