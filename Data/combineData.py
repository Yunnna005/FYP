import pandas as pd
from pathlib import Path

FILE_1 = Path("//workspaces/python/FYP/Data/Real_Dataset/Transactions/Normalized/normalized_transactions_aib.csv")
FILE_2 = Path("/workspaces/python/FYP/Data/Real_Dataset/Transactions/Normalized/normalized_transactions_revolut.csv")

OUT_FILE = Path("normalized_transactions.csv")

OUT_DIR = Path("/workspaces/python/FYP/Data/Real_Dataset/Transactions/Normalized")

def combine_files(file_1, file_2, out_file):
    df1 = pd.read_csv(file_1)
    df2 = pd.read_csv(file_2)

    combined_df = pd.concat([df1, df2], ignore_index=True)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(OUT_DIR / out_file, index=False)

combine_files(FILE_1, FILE_2, OUT_FILE)
