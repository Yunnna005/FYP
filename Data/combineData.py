import pandas as pd
from pathlib import Path

FILE_1 = Path("/workspaces/python/FYP/Data/Other_Dataset/Transactions/Normalized/normalized_transactions.csv")
FILE_2 = Path("/workspaces/python/FYP/Data/Plaid_Dataset/Transactions/Normalized/normalized_transactions.csv")
FILE_3 = Path("/workspaces/python/FYP/Data/Real_Dataset/Transactions/Normalized/normalized_transactions.csv")
FILE_4 = Path("/workspaces/python/FYP/Data/Tink_Dataset/Transactions/Normalized/normalized_transactions.csv")

OUT_FILE = Path("transactions.csv")

OUT_DIR = Path("/workspaces/python/FYP/Data/Final")

def combine_files(file_1, file_2,file_3,file_4, out_file):
    df1 = pd.read_csv(file_1)
    df2 = pd.read_csv(file_2)
    df3 = pd.read_csv(file_3)
    df4 = pd.read_csv(file_4)

    combined_df = pd.concat([df1, df2,df3,df4], ignore_index=True)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(OUT_DIR / out_file, index=False)

combine_files(FILE_1, FILE_2, FILE_3, FILE_4, OUT_FILE)
