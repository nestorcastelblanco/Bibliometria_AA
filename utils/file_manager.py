import pandas as pd
import os

def merge_and_clean(files, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    dfs = [pd.read_csv(f) for f in files]
    merged = pd.concat(dfs, ignore_index=True)

    merged.to_csv(os.path.join(output_folder, "with_duplicates.csv"), index=False)

    cleaned = merged.drop_duplicates(subset=["title"], keep="first")
    cleaned.to_csv(os.path.join(output_folder, "unified.csv"), index=False)
