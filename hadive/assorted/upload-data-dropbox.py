import os
import time
import dropbox
import psycopg2
import datetime
import argparse
import pandas as pd

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description="Input access token.")
    parser.add_argument("--token", dest="token", help="Dropbox app access tokent")
    return parser.parse_args()

class transfer_data:
    """Dropbox transfer class."""
    def __init__(self, access_token):
        """Initialize class with app access token."""
        self.access_token = access_token

    def delete_prev(self):
        """Delete current hadive_data.csv from dropbox."""
        dbx = dropbox.Dropbox(self.access_token)
        print dbx.files_delete("/hadive-data.csv")

    def upload_file(self, file_from, file_to):
        """Upload to dropbox.
        file_from - data to upload.
        file_to - where/how data will be uploaded."""

        dbx = dropbox.Dropbox(self.access_token)
        print "Opened dropbox connection."

        FILE_SIZE = os.path.getsize(file_from)
        CHUNK_SIZE = 100 * 1024 * 1024

        with open(file_from, 'rb') as f:
            upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
            cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=f.tell())
            commit = dropbox.files.CommitInfo(path=file_to)
            n = 1
            while f.tell() < FILE_SIZE:
                if ((FILE_SIZE - f.tell()) <= CHUNK_SIZE):
                    print dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
                else:
                    dbx.files_upload_session_append(f.read(CHUNK_SIZE), cursor.session_id, cursor.offset)
                    cursor.offset = f.tell()
                    print "Uploaded chunk: {}/{}".format(n, int((1. * FILE_SIZE / CHUNK_SIZE) + 0.5))
                    n += 1

def main():
    """Parse access token, prep data, and call upload class."""
    access_token = parse_args().token
    hadive_data = transfer_data(access_token)

    try:
        hadive_data.delete_prev()
        print "Deleted last upload."
    except:
        pass

    with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
        df = pd.read_sql_query(con=conn, sql="SELECT * FROM ped_count")
        print "Loaded data to df."
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
        print "Converted 'date' to datetime object."
        df = df[df["date"].dt.month == datetime.datetime.now().month - 1]
        df.to_csv("./hadive-data.csv", mode="w+")
        print "Wrote df to csv."
    hadive_data.upload_file("./hadive-data.csv", "/hadive-data.csv")

if __name__ == "__main__":
    month = datetime.datetime.now().month - 1
    while True == True:
        if month != datetime.datetime.now().month:
            month = datetime.datetime.now().month
            main()
        time.sleep(3600*24)
