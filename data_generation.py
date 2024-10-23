import pandas as pd
from datetime import datetime
import numpy as np

def data_generation():
    df_columns=["DateTime", "Main_Owner", "2nd_Owner","Bin_ID","Load(KG)","Full(Y/N)"]
    df = pd.read_csv('user1.csv', names=df_columns)
    bin2_df = df[["DateTime"]]
    bin3_df = df[["DateTime"]]

    bin2_df["Load(KG)"] = np.random.randint(0,100,size=(len(bin2_df)))
    bin3_df["Load(KG)"] = np.random.randint(0,100,size=(len(bin3_df)))

    users = ["user1","user2",'user3','user4']
    loaded = ["Y","N"]

    bin2_df["Bin_ID"] = "bin2"
    bin3_df["Bin_ID"] = "bin3"

    new_df = pd.concat([bin2_df,bin3_df], ignore_index=True, sort=False)

    return new_df