import pandas as pd
import os
import glob

def check_encoding_subdir(directory):
    subdir = os.path.join(directory, 'SakuraMoyuExcels')
    files = glob.glob(os.path.join(subdir, '*.xlsx'))
    if not files:
        print("No files in subdir")
        return

    # Sort to get the first one (prologue_001)
    files.sort()
    file_path = files[0]
    print(f"Reading {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        # Save a sample to text file with utf-8 encoding, include NaN to be sure
        sample = df[['org', 'trans']].head(20)
        with open('sample_output_subdir.txt', 'w', encoding='utf-8') as f:
            f.write(str(sample.to_string()))
        print("Sample written to sample_output_subdir.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    target_dir = r"c:/Users/tivac/Downloads/Compressed/drive-download-20251110T020358Z-1-001"
    check_encoding_subdir(target_dir)
