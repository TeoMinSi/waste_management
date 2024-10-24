import pandas as pd
from datetime import datetime
import numpy as np

def data_generation():
    df_columns=["DateTime", "Main_Owner", "2nd_Owner","Bin_ID","Load(KG)","Full(Y/N)"]
    df = pd.read_csv('user1.csv', names=df_columns)
    bin2_df = df[["DateTime", "Main_Owner","2nd_Owner"]]
    bin3_df = df[["DateTime", "Main_Owner","2nd_Owner"]]

    bin2_df["Load(KG)"] = np.random.randint(0,100,size=(len(bin2_df)))
    bin3_df["Load(KG)"] = np.random.randint(0,100,size=(len(bin3_df)))

    loaded = ["Y","N"]

    bin2_df["Bin_ID"] = "bin2"
    bin3_df["Bin_ID"] = "bin3"

    bin2_df['Full(Y/N)'] = ['Y' if x > 60 else 'N' for x in bin2_df['Load(KG)']]
    bin3_df['Full(Y/N)'] = ['Y' if x > 60 else 'N' for x in bin3_df['Load(KG)']]
    new_df = pd.concat([bin2_df,bin3_df], ignore_index=True, sort=False)

    return new_df