import argparse
import pandas as pd


def parse_args():
    """Parse input arguments.
    Returns:
        args (obj)"""
    parser = argparse.ArgumentParser(description="Path to .feather data file.")
    parser.add_argument("--path", dest="path", help="Path to .feather data file.")
    args = parser.parse_args()
    return args


def main(path):
    df = pd.read_feather(path)
    df = df.pivot_table(index="date", columns="cam_id", values="count") \
           .resample("5min").mean()
    df = df[df.index.weekday < 5]
    df = df.groupby(df.index.time).mean()
    df.index = map(lambda x: pd.to_datetime("01-01-2017 " + str(x)), df.index)
    df = df.stack().reset_index()
    df.columns = ["date", "cam", "count"]
    df.set_index("cam", inplace=True)
    df.to_csv("./weekdayavg.csv")

if __name__ == "__main__":
    args = parse_args()
    main(args.path)
    
