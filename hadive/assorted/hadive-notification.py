import os
import sys
import time
import psutil
import datetime
import psycopg2
import subprocess
import pandas as pd
from getpass import getpass
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText


def is_process_running(pid):
    """Check if process is running.
    Args:
        pid - process id to watch.
    Returns:
        (bool)"""

    try:
        os.getpgid(int(pid))
        return True
    except OSError:
        return False


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
         s.sendmail(msg['From'], recipients, msg.as_string())
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

    # Shoud quit if Popen fails.
    subprocess.call(cmd.split())
    for p in psutil.pids():
        if cmd.split()[1] in psutil.Process(p).cmdline():
            pid = p

    with open("./log.txt", "a") as f:
        f.write("{0}, {1}".format(pid, cmd))

    db_prev = day = 0
    while is_process_running(pid):
        # -- Get length of db.
        with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
            with conn.cursor() as cc:
                cc.execute("SELECT COUNT(*) FROM ped_count")
                db_now = cc.fetchall()[0][0]
        # -- (Active notif.) If db has grown, continue.
        if db_now > db_prev:
            db_prev = db_now
        else:
            break
        # -- (Passive notif.) Send a daily update.
        if day != datetime.datetime.now().day:
            day = datetime.datetime.now().day
            message = ("The HaDiVe script is currently running.\n"
                       "The database now has {} records.".format(db_prev))
            send_status_email(recipients, login, password, message)
        time.sleep(60 * 5)

    # -- While loop has broken, send notification.
    message = "The HaDiVe script has gone down."
    send_status_email(recipients, login, password, message)
    # -- Restart.
    main(cmd, recipients, login, password)


if __name__ == "__main__":
    cmd = raw_input("cmd to start ped-count script: ")
    recipients = raw_input("Email recipients (comma deliminated): ")
    login = raw_input("Sender (e-mail adress): ")
    password = getpass("Gmail password: ")

    main(cmd, recipients, login, password)
