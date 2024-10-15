import pandas as pd
from datetime import datetime
import numpy as np

def data_generation():
    df_columns=["DateTime", "Main_Owner", "2nd_Owner","Bin_ID","Load(KG)","Full(Y/N)"]
    df = pd.read_csv('user1.csv', names=df_columns)
    new_df = df[["DateTime"]]

    new_df["Load(KG)"] = np.random.randint(0,100,size=(len(new_df)))

    users = ["user1","user2",'user3','user4']
    loaded = ["Y","N"]

    new_df["Bin_ID"] = "bin2"

    return new_df