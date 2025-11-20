import pandas as pd
import glob
import os

# Obtain directory path where all individual accolade csv files are located
dir_path = 'output/'

# Grab all csv's from designated directory path
accolade_csvs = glob.glob(os.path.join(dir_path, "*accolades*.csv"))

# Initialize empty list where we will append all DataFrames identifed from accolade csv files
accolade_list = []

# Iterate through all csv files
for csv in accolade_csvs:
    df = pd.read_csv(csv)
    accolade_list.append(df)

# Concatenate all DataFrames in accolade_list then save output as csv
final_df = pd.concat(accolade_list, ignore_index=True)
final_df.to_csv("../data/raw/ncaa_accolades_2004_to_2023.csv", index=False)



