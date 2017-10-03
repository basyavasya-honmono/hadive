import os
import time
import datetime
import psycopg2
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


if __name__ == "__main__":
    pid = raw_input("Process ID to watch: ")
    recipients = raw_input("Email recipients (comma deliminated): ")
    login = raw_input("Sender (e-mail adress): ")
    password = getpass("Gmail password: ")

    db_len = day = 0
    while is_process_running(pid):
        # -- Check that the database size has grown.
        with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
            with conn.cursor() as cc:
                cc.execute("SELECT COUNT(*) FROM ped_count")
                db_curr_len = cc.fetchal()[0][0]
        if db_curr_len > db_len:
            db_len = db_curr_len
        else:
            break

        # -- Send daily update.
        if day != datetime.datetime.now().day:
            send_status_email(recipient, login, password,
                              """The HaDiVe script is running as of {}.
                              The database currently has {} rows.""".format(
                              datetime.datetime.now().strftime("%Y-%m-%d"),
                              db_len))

            day = datetime.datetime.now().day

        time.sleep(60 * 5)

    for recipient in recipients.split(", "):
        send_status_email(recipient, login, password, "The HaDiVe script has gone down.")
