import sys, os
if "PRA_HOME" not in os.environ:
    print("Please set environment variable PRA_HOME before running.")
    sys.exit(1)

project_path = os.environ['PRA_HOME']

import pandas as pd
from pathlib import Path
import sys, argparse
from orchestration_utils import iter_data_directory

def merge(data_dir=f'{project_path}/data'):

    dirs, dtype_dicts = iter_data_directory(data_dir)
    print("Start merging files in directory:")
    for file_directory, dtype in zip(dirs, dtype_dicts):
        print(f"\t{file_directory.resolve()}")

        if not file_directory.exists():
            return

        for file in file_directory.glob("*_staging.csv"):
            archive_file = Path(str(file).replace("_staging", ""))
            if archive_file.exists():

                old_df = pd.read_csv(archive_file.resolve(), dtype=dtype, header=0)
                new_df = pd.read_csv(file.resolve(), dtype = dtype, header = 0)

                df = pd.concat([new_df, old_df], ignore_index = True)
                df.drop_duplicates(inplace=True)
                df.to_csv(path_or_buf= archive_file, index=False, header=True)

                file.unlink()
            else:
                file.rename(archive_file)

if __name__ == "__main__":
    
    ap = argparse.ArgumentParser(description="Script to merge staging and archive files.")
    ap.add_argument("-d","--data-directory", default=f'{project_path}/data' , help="Path to data directory.")

    args = vars(ap.parse_args())
    data_dir = args['data_directory']
    merge(data_dir)