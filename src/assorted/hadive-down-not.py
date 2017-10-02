import os
import time
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


def send_status_email(recipients, login, password):
    """Send composed message to recipients from hadive email.
    Args:
        recipients (str) - email recipients.
        login - sending email address.
        password - senders passwords."""

    msg = MIMEText('The pedestrian count script has gone down.', 'plain', 'utf-8')
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

    while is_process_running(pid):
        time.sleep(30)

    send_status_email(recipients, login, password)
