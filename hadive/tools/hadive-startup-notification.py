import os
import sys
import time
import json
import datetime
import psycopg2
from subprocess Popen, PIPE
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText


def send_status_email(recipients, login, password, message):
    """Send composed message to recipients from hadive email.
    Args:
        recipients (str) - email recipients.
        login (str) - sending email address.
        password (str) - senders passwords.
        message (str) - message to send."""

    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header('HaDiVe Status', 'utf-8')
    msg['From'] = login
    msg['To'] = recipients

    s = SMTP_SSL('smtp.gmail.com', 465, timeout=10)
    s.set_debuglevel(1)
    try:
         s.login(login, password)
         s.sendmail(msg['From'], recipients.split(", "), msg.as_string())
    finally:
        s.quit()


def main(cmd, recipients, login, password):
    """Start command, acquire pid, and monitor process. Send daily and failure
    notifications, and try to restart.
    Args:
        cmd (str): bash cmd
        recipients (str): notification recipients.
        login (str): email to send notifications.
        password (str): senders password."""

    # -- Write startup time and command to log.
    with open("./log.txt", "a") as f:
        f.write("{}, {}\n".format(datetime.datetime.now(), cmd))

    db_prev = day = 0 # -- Zero db length count and day of month value.
    # -- Run command as subprocess.
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)

    # -- While process is running continuously check status.
    while proc.poll() == None:
        # -- Get length of db.
        with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
            with conn.cursor() as cc:
                cc.execute("SELECT COUNT(*) FROM ped_count")
                db_now = cc.fetchall()[0][0]

        # -- If the db has grown set db length to current value.
        if db_now > db_prev:
            db_prev = db_now
        # -- If the database has not grown break the while loop.
        else:
            break

        # -- Send a daily update email.
        if day != datetime.datetime.now().day:
            day = datetime.datetime.now().day
            message = ("The HaDiVe script is currently running.\n"
                       "The database now has {} records.".format(db_prev))
            for recipient in recipients.split(", "):
                send_status_email(recipient, login, password, message)

        time.sleep(60 * 5) # -- Sleep for 5 minutes.

    # -- While loop has broken; the process has either died or 0 records have
    # -- been added to the database in the last 5 minutes.

    stdout, stderr = proc.communicate()
    with open("./log.txt", "a") as f:
        f.write("STDOUT\n")
        f.write("{}\n".format(stdout))
        f.write("STDERR\n")
        f.write(s"{}\n".format(stderr))

    del proc # -- Delete subprocesses object from memory to clear GPU.

    # -- Send alert that the process has died.
    message = "The HaDiVe script has gone down."
    send_status_email(recipients, login, password, message)

    # -- Restart.
    main(cmd, recipients, login, password)


if __name__ == "__main__":

    with open("./secrets.json", "r") as f:
        secrets = json.load(f)

    main(secrets["cmd"], secrets["recipients"], secrets["login"],
         secrets["password"])
